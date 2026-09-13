# Docker images

Two image variants are provided; pick the one that matches your runtime.

| Tag        | Base                                       | Size (approx) | Detection      | Use case                                |
|------------|--------------------------------------------|---------------|----------------|-----------------------------------------|
| `tode:cpu` | `python:3.12-slim` + CPU torch             | ~2–3 GB       | RT-DETR (CPU)  | CI, headless batch, dataset export      |
| `tode:gpu` | `pytorch/pytorch:2.4.0-cuda12.4-cudnn9`    | ~7 GB         | RT-DETR (CUDA) | GPU-accelerated batch / GUI build       |

The repository root also contains a `Dockerfile` — its default stage builds the
GUI-capable image (`docker-compose.yml`) and its `web` stage builds the FastAPI
server (`docker-compose.server.yml`). RT-DETR weights download from the
HuggingFace Hub on first use; they are not baked into any image.

## Build

All commands are run from the repository root.

```bash
docker build -f docker/Dockerfile-cpu -t tode:cpu .
docker build -f docker/Dockerfile-gpu -t tode:gpu .
```

## License notes

- tode is **MIT-licensed**; every dependency is permissive.
- The detection stack (RT-DETR / `transformers` Apache-2.0, `supervision` MIT,
  torch BSD) and the **PySide6** GUI (LGPL-3.0) all allow closed-source and
  commercial use. See `THIRD_PARTY_LICENSES.md` for the full breakdown.
