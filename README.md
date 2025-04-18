[![Backend CI](https://github.com/jefferyharrell/Captioner/actions/workflows/backend-ci.yml/badge.svg?branch=main)](https://github.com/jefferyharrell/Captioner/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/jefferyharrell/Captioner/actions/workflows/frontend-ci.yml/badge.svg?branch=main)](https://github.com/jefferyharrell/Captioner/actions/workflows/frontend-ci.yml)
[![E2E CI](https://github.com/jefferyharrell/Captioner/actions/workflows/e2e-ci.yml/badge.svg?branch=main)](https://github.com/jefferyharrell/Captioner/actions/workflows/e2e-ci.yml)

# Captioner

Captioner is a private web application for viewing and captioning photographs. It features a React frontend and a FastAPI backend, storing images on the local filesystem and captions in a SQLite database. 

---

## Project Status (April 2025)

- **Monorepo:** FastAPI backend (Python 3.12, SQLite, robust logging, thumbnail endpoint, /rescan endpoint, TDD enforced) and Next.js 14 frontend (TypeScript, Tailwind v4, shadcn/ui).
- **Single-Photo UX:** The frontend fetches and displays a random photo with editable caption (real-time save, no gallery/grid view).
- **Testing:**
  - Backend: Pytest + pytest-cov (≥90% coverage), Black, Pyright. All endpoints and features are covered by tests.
  - Frontend: Jest/React Testing Library for unit tests, Playwright for E2E (caption editing, random photo fetch).
  - Test-driven development is strictly enforced: all features are implemented via TDD, and CI blocks merges below 90% coverage.
- **CI/CD:** GitHub Actions runs on PRs and direct pushes to main. Pre-commit hooks run Black and Pyright. Manual CI trigger enabled.
- **Logging:** All backend events (startup, scans, errors) logged to stdout and rotating file. Syslog optional. Robustly tested.
- **Image Support:** JPEG, PNG, TIFF, WEBP. Thumbnails served as JPEG. HEIC is not supported (see below).
- **API:** All endpoints use SHA-256 hash as photo identifier. /rescan endpoint is implemented and available. Error responses use FastAPI's default format.

---

**Supported image formats:** JPEG, PNG, TIFF, and WEBP. Unsupported formats (including HEIC) are ignored or rejected. Thumbnails are always served as browser-compatible JPEGs.

Designed for simplicity and extensibility, Captioner makes managing your photo collection and their captions straightforward, with a clean, organized codebase ready for future enhancements.

---

## Why We Dropped HEIC Support

HEIC image support was removed due to persistent compatibility and stability issues with the pyheif/libheif toolchain. Version mismatches, CFFI binding errors, and inconsistent behavior across platforms made HEIC more trouble than it’s worth for a private photo app. Captioner now focuses on reliability and browser compatibility: JPEG, PNG, TIFF, and WEBP are fully supported. If you need to view HEICs, convert them to a standard format first—your sanity will thank you.

## Backend Logging

The backend logs all major events—including app startup, image scans, and file monitoring—to both stdout and a rotating log file (`logs/server.log` by default). This makes debugging and monitoring easy.

- **Log file location:** By default, logs are written to `backend/logs/server.log`. To change this, set the `LOG_DIR` environment variable before starting the backend.
- **Log level:** Set the `LOG_LEVEL` environment variable to `DEBUG`, `INFO`, etc. (default: `INFO`).
- **Syslog:** To enable syslog logging, set `SYSLOG_ENABLE=1` in the environment.

Example:
```bash
LOG_LEVEL=DEBUG LOG_DIR=/tmp/logs SYSLOG_ENABLE=1 venv/bin/uvicorn app.main:app
```

All image discovery (startup scan, folder monitoring) and errors are logged. See the log file for details if something goes sideways.
