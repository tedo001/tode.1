# Third-Party Licenses

This project bundles and depends on the following third-party software. Each is
the property of its respective owners and licensed under the terms below.

## Direct Python dependencies

| Package | Version | License | Notes |
|---|---|---|---|
| [PySide6](https://doc.qt.io/qtforpython/) | ≥ 6.6.0 | **LGPL-3.0** | Qt for Python — the official Qt binding. LGPL permits use in closed-source/commercial apps as long as the Qt libraries remain replaceable (dynamically linked, as bundled). |
| [torch](https://github.com/pytorch/pytorch) | ≥ 2.2.0 | BSD-3-Clause | Permissive. RT-DETR runtime. |
| [torchvision](https://github.com/pytorch/vision) | ≥ 0.17.0 | BSD-3-Clause | Permissive. |
| [transformers](https://github.com/huggingface/transformers) | ≥ 4.48.0 | Apache-2.0 | Permissive. Provides RT-DETR / RT-DETRv2. |
| [supervision](https://github.com/roboflow/supervision) | ≥ 0.22.0 | MIT | Permissive. Detection post-processing / NMS. |
| [opencv-python](https://github.com/opencv/opencv-python) | ≥ 4.8.0 | Apache-2.0 | Permissive. |
| [Pillow](https://github.com/python-pillow/Pillow) | ≥ 10.0.0 | MIT-CMU (HPND) | Permissive. |
| [numpy](https://github.com/numpy/numpy) | ≥ 1.24.0 | BSD-3-Clause | Permissive. |
| [requests](https://github.com/psf/requests) | ≥ 2.28.0 | Apache-2.0 | Permissive. |

### Web server (optional, `requirements-server.txt`)

| Package | License |
|---|---|
| [fastapi](https://github.com/tiangolo/fastapi) | MIT |
| [uvicorn](https://github.com/encode/uvicorn) | BSD-3-Clause |
| [gunicorn](https://github.com/benoitc/gunicorn) | MIT |
| [python-multipart](https://github.com/Kludex/python-multipart) | Apache-2.0 |
| [aiofiles](https://github.com/Tinche/aiofiles) | Apache-2.0 |

## Model weights

| Software | Source | License | Notes |
|---|---|---|---|
| RT-DETR pretrained weights (`PekingU/rtdetr_*`) | downloaded from the [HuggingFace Hub](https://huggingface.co/PekingU) at runtime | Apache-2.0 | Trained on **COCO** ([cocodataset.org](https://cocodataset.org), CC-BY-4.0). Predictions inherit dataset attribution requirements. Weights are not bundled — they download on first use. |

## User-supplied content

- **Annotated images** — the user retains all rights to images and labels they
  create with this tool. Exported datasets are the user's property.

## Why MIT for this project

Every dependency tode ships is permissively licensed, so tode itself can be
**MIT** — usable in private, commercial, and closed-source products:

- Detection: RT-DETR / `transformers` (Apache-2.0), `supervision` (MIT),
  torch/torchvision (BSD). No AGPL dependency (the previous Ultralytics YOLO
  engine was removed).
- GUI: **PySide6 is LGPL-3.0** — unlike GPL PyQt6, LGPL allows use in
  closed-source apps provided the Qt libraries stay dynamically linked and
  replaceable, which the standard PyInstaller/installer layout satisfies (Qt
  ships as separate DLLs).

**LGPL obligation when redistributing:** keep the bundled Qt/PySide6 libraries
replaceable (don't statically link them) and retain their license notices. That
is the only copyleft-style condition; tode's own source is unrestricted MIT.
