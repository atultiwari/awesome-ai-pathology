# Awesome AI in Pathology

<p align='center'>
  <a href='https://github.com/sindresorhus/awesome'><img src='https://awesome.re/badge.svg' alt='Awesome'></a>
  <img src='https://img.shields.io/badge/entries-39-blue.svg' alt='entries'>
  <a href='LICENSE'><img src='https://img.shields.io/badge/content-CC%20BY%204.0-lightgrey.svg' alt='content licence'></a>
  <a href='LICENSE-CODE'><img src='https://img.shields.io/badge/code-MIT-lightgrey.svg' alt='code licence'></a>
</p>

**Everything in AI for pathology — from the paper to the plugin to the product — with an honest note on whether you are allowed to use it on a patient.**

Curated by a practising pathologist, for **pathologists and researchers alike**. Every entry records what it costs, what hardware it needs, whether it works offline, whether it uploads your slides, and where it stands with regulators.

> **Not medical advice or a substitute for validation.** Inclusion is not endorsement. Regulatory clearance in one country says nothing about another. See [DISCLAIMER.md](DISCLAIMER.md).

---

## Browse by

**I am a…**  [🩺 Pathologists](browse/audience/clinician.md) · [🔬 Researchers](browse/audience/researcher.md) · [💻 Developers](browse/audience/developer.md) · [🎓 Educators](browse/audience/educator.md)

**I want to…**  [Annotate slides](browse/task/annotation.md) · [Segment nuclei](browse/task/nuclei-segmentation.md) · [Detect and count cells](browse/task/cell-detection.md) · [Segment tissue regions](browse/task/tissue-segmentation.md) · [Grade tumours](browse/task/grading.md) · [Quantify IHC](browse/task/ihc-quantification.md) · [Check slide quality and artefacts](browse/task/quality-control.md) · [Classify slides or patches](browse/task/classification.md) · [Write or structure reports](browse/task/report-writing.md) · [Predict molecular status from morphology](browse/task/molecular-prediction.md)

**Constraints**  [💻 Runs on a laptop](browse/setting/runs-on-laptop.md) · [🔌 Works offline](browse/setting/works-offline.md) · [📷 No scanner needed](browse/setting/no-scanner-needed.md) · [🌍 Low-resource ready](browse/setting/low-resource.md)

**Regulatory status**  [Not applicable](browse/regulatory/not-applicable.md) · [Research use only](browse/regulatory/ruo.md)

[**See everything →**](browse/all.md)

---

## Contents

- [Foundation Models](#foundation-models) (5)
- [Vision-Language Models](#vision-language-models) (3)
- [Task-Specific Models](#task-specific-models) (4)
- [Software — Viewers & Platforms](#software--viewers--platforms) (5)
- [QuPath Extensions & Scripts](#qupath-extensions--scripts) (4)
- [Developer Libraries & Frameworks](#developer-libraries--frameworks) (7)
- [Datasets](#datasets) (6)
- [Benchmarks & Challenges](#benchmarks--challenges) (2)
- [Standards & Interoperability](#standards--interoperability) (1)
- [Education & Training](#education--training) (1)
- [Meta — Other Lists & Community](#meta--other-lists--community) (1)

---

## Foundation Models

🧠 Tile-level and slide-level vision encoders pretrained on large pathology corpora, used as frozen feature extractors or fine-tuning backbones.

| Name | What it does | Status | Cost / Hardware | Tasks | Links |
| --- | --- | --- | --- | --- | --- |
| **Phikon-v2** | Openly licensed pathology tile encoder trained on public cohorts. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · consumer gpu · 🌍 | [`Classify slides or patches`](browse/task/classification.md) [`Train or fine-tune models`](browse/task/model-training.md) | [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://arxiv.org/abs/2409.09173) [![Model](https://img.shields.io/badge/Model-link-orange)](https://huggingface.co/owkin/phikon-v2) |
| **[Prov-GigaPath](https://github.com/prov-gigapath/prov-gigapath)** | Slide-level foundation model with a tile encoder and long-context aggregator. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free for academic · workstation gpu | [`Classify slides or patches`](browse/task/classification.md) [`Predict molecular status from morphology`](browse/task/molecular-prediction.md) [`Train or fine-tune models`](browse/task/model-training.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/prov-gigapath/prov-gigapath) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://doi.org/10.1038/s41586-024-07441-w) [![Model](https://img.shields.io/badge/Model-link-orange)](https://huggingface.co/prov-gigapath/prov-gigapath) |
| **[TITAN](https://github.com/mahmoodlab/TITAN)** | Multimodal whole-slide foundation model producing slide-level embeddings. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free for academic · workstation gpu | [`Classify slides or patches`](browse/task/classification.md) [`Search and retrieve similar images`](browse/task/retrieval-search.md) [`Write or structure reports`](browse/task/report-writing.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/mahmoodlab/TITAN) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://doi.org/10.1038/s41591-025-03982-3) [![Model](https://img.shields.io/badge/Model-link-orange)](https://huggingface.co/MahmoodLab/TITAN) |
| **[UNI](https://github.com/mahmoodlab/UNI)** | Self-supervised vision foundation model for pathology tile encoding. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free for academic · consumer gpu · 🌍 | [`Classify slides or patches`](browse/task/classification.md) [`Train or fine-tune models`](browse/task/model-training.md) [`Search and retrieve similar images`](browse/task/retrieval-search.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/mahmoodlab/UNI) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://doi.org/10.1038/s41591-024-02857-3) [![Model](https://img.shields.io/badge/Model-link-orange)](https://huggingface.co/MahmoodLab/UNI) |
| **Virchow2** | Large pathology vision foundation model trained on a very large slide corpus. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free for academic · workstation gpu | [`Classify slides or patches`](browse/task/classification.md) [`Train or fine-tune models`](browse/task/model-training.md) | [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://arxiv.org/abs/2408.00738) [![Model](https://img.shields.io/badge/Model-link-orange)](https://huggingface.co/paige-ai/Virchow2) |

[Browse all Foundation Models →](browse/category/foundation-model.md)

## Vision-Language Models

💬 Models aligning pathology images with text — contrastive encoders, instruction-tuned assistants, reasoning models, and agentic systems.

| Name | What it does | Status | Cost / Hardware | Tasks | Links |
| --- | --- | --- | --- | --- | --- |
| **[CONCH](https://github.com/mahmoodlab/CONCH)** | Vision-language foundation model for pathology image-text tasks. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free for academic · consumer gpu · 🌍 | [`Classify slides or patches`](browse/task/classification.md) [`Search and retrieve similar images`](browse/task/retrieval-search.md) [`Ask questions about an image`](browse/task/vqa.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/mahmoodlab/CONCH) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://doi.org/10.1038/s41591-024-02856-4) |
| **[PLIP](https://github.com/PathologyFoundation/plip)** | Pathology CLIP model trained on image-text pairs mined from social media. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · cpu · 🌍 | [`Classify slides or patches`](browse/task/classification.md) [`Search and retrieve similar images`](browse/task/retrieval-search.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/PathologyFoundation/plip) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://doi.org/10.1038/s41591-023-02504-3) [![Demo](https://img.shields.io/badge/Demo-link-ff69b4)](https://huggingface.co/spaces/vinid/webplip) |
| **[Quilt-LLaVA](https://quilt-llava.github.io/)** | Instruction-tuned pathology assistant trained from educational video narration. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · consumer gpu · 🌍 | [`Ask questions about an image`](browse/task/vqa.md) [`Teach and learn`](browse/task/education.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/aldraus/quilt-llava) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://arxiv.org/abs/2312.04746) [![Site](https://img.shields.io/badge/Site-link-ffb6c1)](https://quilt-llava.github.io/) |

[Browse all Vision-Language Models →](browse/category/vision-language-model.md)

## Task-Specific Models

🎯 Models solving one well-defined pathology task: nuclei segmentation, mitosis detection, grading, biomarker scoring, quality control.

| Name | What it does | Status | Cost / Hardware | Tasks | Links |
| --- | --- | --- | --- | --- | --- |
| **[CellViT](https://github.com/TIO-IKIM/CellViT)** | Vision-transformer nucleus segmentation and classification. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · consumer gpu · 🌍 | [`Segment nuclei`](browse/task/nuclei-segmentation.md) [`Detect and count cells`](browse/task/cell-detection.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/TIO-IKIM/CellViT) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://doi.org/10.1016/j.media.2024.103143) |
| **[HistoQC](https://github.com/choosehappy/HistoQC)** | Automated quality control for whole-slide images. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · cpu | [`Check slide quality and artefacts`](browse/task/quality-control.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/choosehappy/HistoQC) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://doi.org/10.1200/CCI.18.00157) |
| **[HoVer-Net](https://github.com/vqdang/hover_net)** | Simultaneous nucleus segmentation and classification in histology. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · consumer gpu · 🌍 | [`Segment nuclei`](browse/task/nuclei-segmentation.md) [`Detect and count cells`](browse/task/cell-detection.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/vqdang/hover_net) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://doi.org/10.1016/j.media.2019.101563) |
| **[StarDist](https://github.com/stardist/stardist)** | Star-convex polygon nucleus detection. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · cpu · 🌍 | [`Segment nuclei`](browse/task/nuclei-segmentation.md) [`Detect and count cells`](browse/task/cell-detection.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/stardist/stardist) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://arxiv.org/abs/1806.03535) |

[Browse all Task-Specific Models →](browse/category/task-specific-model.md)

## Software — Viewers & Platforms

🖥️ Desktop and server applications for viewing, annotating, managing and analysing whole-slide images.

| Name | What it does | Status | Cost / Hardware | Tasks | Links |
| --- | --- | --- | --- | --- | --- |
| **[ASAP](https://github.com/computationalpathologygroup/ASAP)** | Fast whole-slide image viewer with annotation support. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · cpu | [`Annotate slides`](browse/task/annotation.md) [`Manage slides and metadata`](browse/task/data-management.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/computationalpathologygroup/ASAP) |
| **[Cytomine](https://cytomine.org/)** | Web-based collaborative platform for annotating and analysing whole-slide images. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · workstation gpu | [`Annotate slides`](browse/task/annotation.md) [`Manage slides and metadata`](browse/task/data-management.md) [`Teach and learn`](browse/task/education.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/cytomine) [![Site](https://img.shields.io/badge/Site-link-ffb6c1)](https://cytomine.org/) |
| **[Digital Slide Archive](https://digitalslidearchive.github.io/digital_slide_archive/)** | Server platform for managing, annotating and analysing large slide collections. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · workstation gpu | [`Annotate slides`](browse/task/annotation.md) [`Manage slides and metadata`](browse/task/data-management.md) [`Segment tissue regions`](browse/task/tissue-segmentation.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/DigitalSlideArchive/digital_slide_archive) [![Site](https://img.shields.io/badge/Site-link-ffb6c1)](https://digitalslidearchive.github.io/digital_slide_archive/) |
| **[OMERO](https://www.openmicroscopy.org/omero/)** | Image data management server for microscopy, including whole-slide images. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · workstation gpu | [`Manage slides and metadata`](browse/task/data-management.md) [`Annotate slides`](browse/task/annotation.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/ome/openmicroscopy) [![Site](https://img.shields.io/badge/Site-link-ffb6c1)](https://www.openmicroscopy.org/omero/) |
| **[QuPath](https://qupath.github.io/)** | Open-source desktop software for whole-slide image analysis and annotation. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · cpu · 🌍 | [`Annotate slides`](browse/task/annotation.md) [`Detect and count cells`](browse/task/cell-detection.md) [`Quantify IHC`](browse/task/ihc-quantification.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/qupath/qupath) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://doi.org/10.1038/s41598-017-17204-5) [![Docs](https://img.shields.io/badge/Docs-link-6A5ACD)](https://qupath.readthedocs.io/) [![Site](https://img.shields.io/badge/Site-link-ffb6c1)](https://qupath.github.io/) |

[Browse all Software — Viewers & Platforms →](browse/category/software-viewer.md)

## QuPath Extensions & Scripts

🧩 Extensions, plugins and script collections that add capability to QuPath.

| Name | What it does | Status | Cost / Hardware | Tasks | Links |
| --- | --- | --- | --- | --- | --- |
| **[QuPath Cellpose Extension](https://github.com/BIOP/qupath-extension-cellpose)** | Brings Cellpose and Omnipose segmentation into QuPath. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · consumer gpu · 🌍 | [`Segment nuclei`](browse/task/nuclei-segmentation.md) [`Detect and count cells`](browse/task/cell-detection.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/BIOP/qupath-extension-cellpose) |
| **[QuPath InstanSeg Extension](https://github.com/qupath/qupath-extension-instanseg)** | InstanSeg nucleus and cell segmentation inside QuPath. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · cpu · 🌍 | [`Segment nuclei`](browse/task/nuclei-segmentation.md) [`Detect and count cells`](browse/task/cell-detection.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/qupath/qupath-extension-instanseg) |
| **[QuPath StarDist Extension](https://github.com/qupath/qupath-extension-stardist)** | Runs StarDist star-convex nucleus detection inside QuPath. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · cpu · 🌍 | [`Segment nuclei`](browse/task/nuclei-segmentation.md) [`Detect and count cells`](browse/task/cell-detection.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/qupath/qupath-extension-stardist) [![Docs](https://img.shields.io/badge/Docs-link-6A5ACD)](https://qupath.readthedocs.io/en/stable/docs/deep/stardist.html) |
| **[WSInfer](https://github.com/SBU-BMI/wsinfer)** | Runs pretrained patch classification models across whole slides, with a QuPath front end. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · consumer gpu | [`Classify slides or patches`](browse/task/classification.md) [`Segment tissue regions`](browse/task/tissue-segmentation.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/SBU-BMI/wsinfer) [![Docs](https://img.shields.io/badge/Docs-link-6A5ACD)](https://wsinfer.readthedocs.io/) |

[Browse all QuPath Extensions & Scripts →](browse/category/qupath-extension.md)

## Developer Libraries & Frameworks

📦 Programming libraries for whole-slide I/O, preprocessing, multiple-instance learning, and end-to-end computational pathology pipelines.

| Name | What it does | Status | Cost / Hardware | Tasks | Links |
| --- | --- | --- | --- | --- | --- |
| **[CLAM](https://github.com/mahmoodlab/CLAM)** | Attention-based multiple-instance learning for weakly supervised whole-slide classification. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · workstation gpu | [`Classify slides or patches`](browse/task/classification.md) [`Train or fine-tune models`](browse/task/model-training.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/mahmoodlab/CLAM) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://doi.org/10.1038/s41551-020-00682-w) |
| **[HistomicsTK](https://github.com/DigitalSlideArchive/HistomicsTK)** | Python toolkit for histology image analysis and feature extraction. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · cpu · 🌍 | [`Segment nuclei`](browse/task/nuclei-segmentation.md) [`Normalise or deconvolve stains`](browse/task/stain-normalisation.md) [`Quantify IHC`](browse/task/ihc-quantification.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/DigitalSlideArchive/HistomicsTK) [![Docs](https://img.shields.io/badge/Docs-link-6A5ACD)](https://digitalslidearchive.github.io/HistomicsTK/) |
| **[OpenSlide](https://openslide.org/)** | C library with Python bindings for reading proprietary whole-slide formats. | [![Not applicable](https://img.shields.io/badge/Status-N%2FA-lightgrey)](browse/regulatory/not-applicable.md) | free · cpu | [`Read and convert slide formats`](browse/task/wsi-io.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/openslide/openslide) [![Site](https://img.shields.io/badge/Site-link-ffb6c1)](https://openslide.org/) |
| **[PathML](https://github.com/Dana-Farber-AIOS/pathml)** | Python library for computational pathology preprocessing and modelling. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · consumer gpu | [`Read and convert slide formats`](browse/task/wsi-io.md) [`Segment nuclei`](browse/task/nuclei-segmentation.md) [`Normalise or deconvolve stains`](browse/task/stain-normalisation.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/Dana-Farber-AIOS/pathml) [![Docs](https://img.shields.io/badge/Docs-link-6A5ACD)](https://pathml.readthedocs.io/) |
| **[Slideflow](https://github.com/slideflow/slideflow)** | End-to-end deep learning pipeline for whole-slide images. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · workstation gpu | [`Classify slides or patches`](browse/task/classification.md) [`Train or fine-tune models`](browse/task/model-training.md) [`Predict prognosis and survival`](browse/task/survival-prediction.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/slideflow/slideflow) [![Docs](https://img.shields.io/badge/Docs-link-6A5ACD)](https://slideflow.dev/) |
| **[TIAToolbox](https://github.com/TissueImageAnalytics/tiatoolbox)** | Python toolbox for computational pathology pipelines. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · consumer gpu | [`Read and convert slide formats`](browse/task/wsi-io.md) [`Segment tissue regions`](browse/task/tissue-segmentation.md) [`Segment nuclei`](browse/task/nuclei-segmentation.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/TissueImageAnalytics/tiatoolbox) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://doi.org/10.1038/s43856-022-00186-5) [![Docs](https://img.shields.io/badge/Docs-link-6A5ACD)](https://tia-toolbox.readthedocs.io/) |
| **[TRIDENT](https://github.com/mahmoodlab/TRIDENT)** | Toolkit for whole-slide preprocessing and foundation-model feature extraction. | [![Research use only](https://img.shields.io/badge/Status-RUO-grey)](browse/regulatory/ruo.md) | free · workstation gpu | [`Read and convert slide formats`](browse/task/wsi-io.md) [`Train or fine-tune models`](browse/task/model-training.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/mahmoodlab/TRIDENT) |

[Browse all Developer Libraries & Frameworks →](browse/category/library-framework.md)

## Datasets

🗂️ Public or request-access image, image-text, and multimodal pathology datasets.

| Name | What it does | Status | Cost / Hardware | Tasks | Links |
| --- | --- | --- | --- | --- | --- |
| **[CAMELYON16](https://camelyon16.grand-challenge.org/)** | Lymph node metastasis detection challenge dataset. | [![Not applicable](https://img.shields.io/badge/Status-N%2FA-lightgrey)](browse/regulatory/not-applicable.md) | free · cpu | [`Classify slides or patches`](browse/task/classification.md) [`Segment tissue regions`](browse/task/tissue-segmentation.md) [`Train or fine-tune models`](browse/task/model-training.md) | [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://doi.org/10.1001/jama.2017.14585) [![Site](https://img.shields.io/badge/Site-link-ffb6c1)](https://camelyon16.grand-challenge.org/) |
| **NCT-CRC-HE-100K** | Colorectal tissue-type patch classification dataset. | [![Not applicable](https://img.shields.io/badge/Status-N%2FA-lightgrey)](browse/regulatory/not-applicable.md) | free · cpu · 🌍 | [`Classify slides or patches`](browse/task/classification.md) [`Train or fine-tune models`](browse/task/model-training.md) [`Teach and learn`](browse/task/education.md) | [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://doi.org/10.1371/journal.pmed.1002730) [![Data](https://img.shields.io/badge/Data-link-orange)](https://zenodo.org/records/1214456) |
| **[PANDA](https://www.kaggle.com/competitions/prostate-cancer-grade-assessment)** | Prostate biopsy Gleason grading challenge dataset. | [![Not applicable](https://img.shields.io/badge/Status-N%2FA-lightgrey)](browse/regulatory/not-applicable.md) | free · cpu | [`Grade tumours`](browse/task/grading.md) [`Classify slides or patches`](browse/task/classification.md) [`Train or fine-tune models`](browse/task/model-training.md) | [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://doi.org/10.1038/s41591-021-01620-2) [![Site](https://img.shields.io/badge/Site-link-ffb6c1)](https://www.kaggle.com/competitions/prostate-cancer-grade-assessment) |
| **[PanNuke](https://warwick.ac.uk/fac/cross_fac/tia/data/pannuke)** | Pan-cancer nucleus instance segmentation and classification dataset. | [![Not applicable](https://img.shields.io/badge/Status-N%2FA-lightgrey)](browse/regulatory/not-applicable.md) | free · cpu · 🌍 | [`Segment nuclei`](browse/task/nuclei-segmentation.md) [`Detect and count cells`](browse/task/cell-detection.md) [`Train or fine-tune models`](browse/task/model-training.md) | [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://arxiv.org/abs/2003.10778) [![Site](https://img.shields.io/badge/Site-link-ffb6c1)](https://warwick.ac.uk/fac/cross_fac/tia/data/pannuke) |
| **[Quilt-1M](https://github.com/wisdomikezogwo/quilt1m)** | Histopathology image-text pairs mined from educational videos. | [![Not applicable](https://img.shields.io/badge/Status-N%2FA-lightgrey)](browse/regulatory/not-applicable.md) | free · cpu · 🌍 | [`Train or fine-tune models`](browse/task/model-training.md) [`Search and retrieve similar images`](browse/task/retrieval-search.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/wisdomikezogwo/quilt1m) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://arxiv.org/abs/2306.11207) [![Data](https://img.shields.io/badge/Data-link-orange)](https://zenodo.org/records/8239942) |
| **[TCGA](https://www.cancer.gov/ccg/research/genome-sequencing/tcga)** | Pan-cancer whole-slide and molecular data archive. | [![Not applicable](https://img.shields.io/badge/Status-N%2FA-lightgrey)](browse/regulatory/not-applicable.md) | free · cpu | [`Train or fine-tune models`](browse/task/model-training.md) [`Predict molecular status from morphology`](browse/task/molecular-prediction.md) [`Predict prognosis and survival`](browse/task/survival-prediction.md) | [![Data](https://img.shields.io/badge/Data-link-orange)](https://portal.gdc.cancer.gov/) [![Site](https://img.shields.io/badge/Site-link-ffb6c1)](https://www.cancer.gov/ccg/research/genome-sequencing/tcga) |

[Browse all Datasets →](browse/category/dataset.md)

## Benchmarks & Challenges

📊 Evaluation suites, leaderboards and grand challenges for comparing methods on common tasks.

| Name | What it does | Status | Cost / Hardware | Tasks | Links |
| --- | --- | --- | --- | --- | --- |
| **[HEST-1k / HEST-Bench](https://github.com/mahmoodlab/HEST)** | Paired histology and spatial transcriptomics dataset and benchmark. | [![Not applicable](https://img.shields.io/badge/Status-N%2FA-lightgrey)](browse/regulatory/not-applicable.md) | free · consumer gpu · 🌍 | [`Work with spatial transcriptomics`](browse/task/spatial-transcriptomics.md) [`Train or fine-tune models`](browse/task/model-training.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/mahmoodlab/HEST) [![Paper](https://img.shields.io/badge/Paper-link-1f77b4)](https://arxiv.org/abs/2406.16192) [![Docs](https://img.shields.io/badge/Docs-link-6A5ACD)](https://hest.readthedocs.io/) [![Data](https://img.shields.io/badge/Data-link-orange)](https://huggingface.co/datasets/MahmoodLab/hest) |
| **[Patho-Bench](https://github.com/mahmoodlab/Patho-Bench)** | Standardised evaluation suite for pathology slide-level foundation models. | [![Not applicable](https://img.shields.io/badge/Status-N%2FA-lightgrey)](browse/regulatory/not-applicable.md) | free · workstation gpu | [`Classify slides or patches`](browse/task/classification.md) [`Train or fine-tune models`](browse/task/model-training.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/mahmoodlab/Patho-Bench) |

[Browse all Benchmarks & Challenges →](browse/category/benchmark.md)

## Standards & Interoperability

🔌 DICOM, FHIR, SNOMED CT, LOINC, CAP protocols and the plumbing that turns a demo into a deployed system.

| Name | What it does | Status | Cost / Hardware | Tasks | Links |
| --- | --- | --- | --- | --- | --- |
| **[DICOM for Whole Slide Imaging](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.32.8.html)** | The vendor-neutral standard for storing and exchanging pathology slides. | [![Not applicable](https://img.shields.io/badge/Status-N%2FA-lightgrey)](browse/regulatory/not-applicable.md) | free · cpu · 🌍 | [`Read and convert slide formats`](browse/task/wsi-io.md) [`Manage slides and metadata`](browse/task/data-management.md) [`Consult remotely`](browse/task/telepathology.md) | [![Docs](https://img.shields.io/badge/Docs-link-6A5ACD)](https://dicom.nema.org/) [![Site](https://img.shields.io/badge/Site-link-ffb6c1)](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_A.32.8.html) |

[Browse all Standards & Interoperability →](browse/category/standard-interop.md)

## Education & Training

🎓 Courses, tutorials, atlases, slide boxes, societies and conferences for learning pathology AI.

| Name | What it does | Status | Cost / Hardware | Tasks | Links |
| --- | --- | --- | --- | --- | --- |
| **[PathologyOutlines](https://www.pathologyoutlines.com/)** | Free comprehensive online pathology reference. | [![Not applicable](https://img.shields.io/badge/Status-N%2FA-lightgrey)](browse/regulatory/not-applicable.md) | free · cpu | [`Teach and learn`](browse/task/education.md) | [![Site](https://img.shields.io/badge/Site-link-ffb6c1)](https://www.pathologyoutlines.com/) |

[Browse all Education & Training →](browse/category/education.md)

## Meta — Other Lists & Community

🔗 Other curated lists, newsletters, research groups and community resources.

| Name | What it does | Status | Cost / Hardware | Tasks | Links |
| --- | --- | --- | --- | --- | --- |
| **[Awesome-Pathology-VLMs](https://github.com/wenhaozhang0066/Awesome-Pathology-VLMs)** | Curated list of pathology vision-language models, datasets and benchmarks. | [![Not applicable](https://img.shields.io/badge/Status-N%2FA-lightgrey)](browse/regulatory/not-applicable.md) | free · cpu | [`Teach and learn`](browse/task/education.md) | [![Code](https://img.shields.io/badge/Code-link-green)](https://github.com/wenhaozhang0066/Awesome-Pathology-VLMs) |

[Browse all Meta — Other Lists & Community →](browse/category/meta.md)

---

## About

**Curated by Dr. Atul Tiwari**  
Associate Professor, Department of Pathology, Government Medical College, Chittorgarh, Rajasthan, India  
Additional Nodal Officer (AI/ML), Department of Medical Education, Government of Rajasthan, India
  
ORCID: [0000-0002-8048-9541](https://orcid.org/0000-0002-8048-9541)

*No commercial affiliations. No sponsored placements. No affiliate links.*

> This is a personal project. It is not an official publication of Government Medical College Chittorgarh or the Government of Rajasthan, and inclusion of any product does not constitute endorsement by any institution.

## Contributing

Suggestions are very welcome via [Issues](https://github.com/atultiwari/awesome-ai-pathology/issues/new/choose). Pull requests open once the taxonomy settles — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

Content [CC BY 4.0](LICENSE) · code [MIT](LICENSE-CODE).

<sub>README, browse pages and the JSON API are generated from `data/entries/*.yaml`. Do not edit them by hand.</sub>
