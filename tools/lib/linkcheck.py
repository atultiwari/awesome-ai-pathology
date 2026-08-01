"""Link liveness checking.

Distinguishes ROT (a link that is genuinely broken and must be fixed) from
TRANSIENT trouble (rate limiting, anti-bot walls, slow hosts). Only rot fails
the build — otherwise a busy CDN turns every PR red and the check gets ignored,
which is worse than not having it.
"""
from __future__ import annotations

import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Iterable, Literal
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

# A conventional browser token. An identifying "compatible; ...bot...; +url"
# string is politer in principle, but several sites we must check — notably
# accessdata.fda.gov, which holds our regulatory references — answer such a UA
# with a misleading 404. That turns every FDA citation into a false broken-link
# report, which is far worse than sending an ordinary UA. Volume here is tiny
# (a few hundred requests, weekly) and every request is a plain read.
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
TIMEOUT_S = 25
MAX_WORKERS = 4
PER_HOST_DELAY_S = 0.6

# Rate limiting, service overload and gateway hiccups are not link rot.
TRANSIENT_CODES = frozenset({408, 429, 500, 502, 503, 504})
# Servers that dislike HEAD or bots, but the URL itself is fine.
RETRY_WITH_GET_CODES = frozenset({403, 405, 406, 501})

# Hosts that serve a deliberate 403/404 to non-browser agents. A failure here
# cannot be distinguished from real rot, so it is downgraded to a warning that
# explicitly asks for a human to look. Verified by hand with a browser UA:
# Kaggle returns 200 for competition URLs that this checker sees as 404.
BOT_HOSTILE_HOSTS = frozenset({
    "www.kaggle.com", "kaggle.com",
    "doi.org", "dx.doi.org",
    "linkinghub.elsevier.com", "www.sciencedirect.com",
    "onlinelibrary.wiley.com", "www.nature.com",
    "ieeexplore.ieee.org", "pubs.rsna.org", "ascopubs.org",
})

Severity = Literal["error", "warning"]


@dataclass(frozen=True)
class LinkResult:
    severity: Severity
    where: str
    url: str
    detail: str

    def __str__(self) -> str:
        return f"{self.where}: {self.url} → {self.detail}"


def check_urls(pairs: Iterable[tuple[str, str]]) -> tuple[list[LinkResult], list[LinkResult]]:
    """Check every (source, url). Returns (errors, warnings)."""
    by_host: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for where, url in pairs:
        by_host[urlparse(url).netloc].append((where, url))

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        batches = pool.map(_check_host_batch, by_host.values())

    results = [r for batch in batches for r in batch]
    return (
        sorted((r for r in results if r.severity == "error"), key=str),
        sorted((r for r in results if r.severity == "warning"), key=str),
    )


def _check_host_batch(pairs: list[tuple[str, str]]) -> list[LinkResult]:
    """Check one host's URLs serially, spaced out, so we don't trigger throttling."""
    out: list[LinkResult] = []
    for index, (where, url) in enumerate(pairs):
        if index:
            time.sleep(PER_HOST_DELAY_S)
        result = _check_one(where, url)
        if result is not None:
            out.append(result)
    return out


def _check_one(where: str, url: str) -> LinkResult | None:
    outcome = _request(url, method="HEAD")

    if isinstance(outcome, int) and outcome in RETRY_WITH_GET_CODES:
        outcome = _request(url, method="GET")
    if isinstance(outcome, int) and outcome in TRANSIENT_CODES:
        time.sleep(2.0)
        outcome = _request(url, method="GET")

    if outcome == "ok":
        return None

    host = urlparse(url).netloc
    if isinstance(outcome, int):
        if outcome in TRANSIENT_CODES:
            return LinkResult("warning", where, url, f"HTTP {outcome} (transient — not treated as rot)")
        if outcome in RETRY_WITH_GET_CODES or host in BOT_HOSTILE_HOSTS:
            return LinkResult("warning", where, url, f"HTTP {outcome} (bot-blocked — verify by hand)")
        return LinkResult("error", where, url, f"HTTP {outcome}")

    # Network-level failure: DNS, TLS, refused, timeout.
    if "timed out" in outcome:
        return LinkResult("warning", where, url, "timed out — verify by hand")
    return LinkResult("error", where, url, outcome)


def _request(url: str, method: str) -> Literal["ok"] | int | str:
    request = Request(url, method=method, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=TIMEOUT_S) as response:
            return "ok" if response.status < 400 else response.status
    except HTTPError as exc:
        return exc.code
    except (URLError, OSError, ValueError) as exc:
        reason = getattr(exc, "reason", exc)
        return f"{type(exc).__name__}: {reason}"
