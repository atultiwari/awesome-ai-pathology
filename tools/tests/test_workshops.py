"""Parsing the editor's teaching schedule out of an authored JS file.

The point of these is that the parser must never invent, never execute, and
never quietly produce nothing.
"""
from __future__ import annotations

import pytest

from lib.workshops import PUBLISHABLE, WorkshopsError, parse

SAMPLE = """
const OFFER_NOTE = 'Free for members';

const WORKSHOPS = [
  {
    id: 'ai-toolkit',
    title: 'AI Toolkit for Doctors',
    tagline: 'Two evenings with ChatGPT and Claude',
    status: 'open',
    level: 'Beginner',
    classes: 2,
    format: 'Live · hands-on',
    schedule: {
      label: 'Friday 7 & Saturday 8 August 2026',
      time: '8:30 PM IST',
      startISO: '2026-08-07T20:30:00+05:30',
    },
    price: { amount: 'See academy page', note: OFFER_NOTE },
    forWhom: 'Doctors who have not used these tools seriously.',
    cta: { label: 'Register', href: 'https://academy.example.org/ai-toolkit/' },
  },
  {
    id: 'members-only',
    title: 'Advanced Session',
    status: 'members',
    cta: { type: 'whatsapp', label: 'Ask us' },
  },
];
"""


def test_reads_the_fields_the_digest_prints():
    [workshop] = parse(SAMPLE)
    assert workshop["title"] == "AI Toolkit for Doctors"
    assert workshop["level"] == "Beginner"
    assert workshop["when"] == "Friday 7 & Saturday 8 August 2026"
    assert workshop["starts_at"] == "2026-08-07T20:30:00+05:30"
    assert workshop["url"] == "https://academy.example.org/ai-toolkit/"
    assert workshop["for_whom"].startswith("Doctors who")


def test_members_only_workshops_are_not_printed():
    """A reader cannot act on one, so listing it is advertising, not service."""
    assert [w["id"] for w in parse(SAMPLE)] == ["ai-toolkit"]


@pytest.mark.parametrize("status", PUBLISHABLE)
def test_every_publishable_status_survives(status):
    source = SAMPLE.replace("status: 'open',", f"status: '{status}',")
    assert parse(source)[0]["status"] == status


def test_a_todo_placeholder_never_reaches_print():
    source = SAMPLE.replace(
        "level: 'Beginner',", "level: 'Beginner', // TODO: confirm")
    assert parse(source)[0]["level"] is None


def test_braces_inside_prose_do_not_break_the_scan():
    source = SAMPLE.replace(
        "tagline: 'Two evenings with ChatGPT and Claude',",
        "tagline: 'Use a prompt like { this } and see',")
    assert parse(source)[0]["tagline"] == "Use a prompt like { this } and see"


def test_an_apostrophe_in_a_title_survives():
    source = SAMPLE.replace(
        "title: 'AI Toolkit for Doctors',", r"title: 'A Pathologist\'s Toolkit',")
    assert parse(source)[0]["title"] == "A Pathologist's Toolkit"


def test_a_missing_schedule_is_absent_not_invented():
    source = SAMPLE[:SAMPLE.index("schedule: {")] + SAMPLE[SAMPLE.index("price: {"):]
    assert parse(source)[0]["when"] is None


def test_nothing_publishable_raises_rather_than_printing_an_empty_section():
    source = SAMPLE.replace("status: 'open',", "status: 'members',")
    with pytest.raises(WorkshopsError):
        parse(source)


def test_a_changed_format_raises_rather_than_guessing():
    with pytest.raises(WorkshopsError):
        parse("const SOMETHING_ELSE = [];")


def test_the_parser_does_not_execute_the_source():
    """If this ever evaluated the file, a compromised host would own the CI."""
    hostile = SAMPLE.replace(
        "const WORKSHOPS = [",
        "throw new Error('executed'); const WORKSHOPS = [")
    assert parse(hostile)[0]["title"] == "AI Toolkit for Doctors"


def test_order_follows_the_site():
    source = SAMPLE.replace(
        "  {\n    id: 'members-only',\n    title: 'Advanced Session',\n    status: 'members',",
        "  {\n    id: 'second',\n    title: 'Second Workshop',\n    status: 'open',")
    assert [w["id"] for w in parse(source)] == ["ai-toolkit", "second"]
