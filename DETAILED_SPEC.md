# Captioner – Detailed Project Specification

## Overview
Captioner is a private web application for viewing and captioning photographs. It is designed for extensibility, test-driven development, and minimal user frustration (no guarantees). The system consists of a React frontend and a FastAPI backend, with SQLite for metadata and the filesystem for image storage. All code is written with TDD in mind, and the project is structured for easy future enhancements.

---

## Architecture
- **Frontend:** Next.js 14 (TypeScript), Tailwind v4, shadcn/ui. Single-photo random UX with real-time caption editing (no gallery/grid view, no rescan button).
- **Backend:** FastAPI (Python 3), SQLite, SQLAlchemy ORM
- **Image Storage:** Filesystem on backend
- **Supported image formats:** JPEG, PNG, TIFF, and WEBP. Unsupported formats (including HEIC) are ignored or rejected. Thumbnails are always served as browser-compatible JPEGs.
- **Test Frameworks:** Pytest (backend), Jest/React Testing Library and Playwright (frontend)
- **OS Target:** macOS and Linux

---

## Backend (FastAPI)

### Data Model
- **Photo**
  - `hash` (SHA-256, str): Primary key (unique)
  - `filename` (str): Original filename (metadata only)
  - `caption` (text, nullable): Unicode, unlimited length
  - *Extensible*: Table allows for future metadata fields

### Endpoints
- `POST /login` – Simple password authentication. Reads `PASSWORD` env var at request time. Returns `{ "success": true }` or `{ "success": false }`.
- `POST /photos` – Upload a photo. Stores file as `<sha256><ext>`, checks for duplicate (by hash only), saves metadata in DB. Returns photo metadata.
- `GET /photos` – List all photo records (hash, filename, caption).
- `GET /photos/{hash}` – Get metadata for a specific photo.
- `PATCH /photos/{hash}/caption` – Update caption. Request body: `{ "caption": "..." }`. Returns updated photo record.
- `GET /photos/{hash}/image` – Serve the image file for the given hash.
- `POST /rescan` – Manual trigger for backend to rescan images folder; returns immediate ack. Fully implemented and tested.

### Error Handling
- All errors are returned as {"detail": ...} format:
  ```json
  { "detail": <HumanReadableMessage> }
  ```
  - 404 → `{ "detail": "Photo not found." }`
  - 409 → `{ "detail": "Photo with this hash already exists." }`

### Image Discovery
- At startup, backend scans the images folder and adds any new photos to the DB.
- Backend should also detect new images placed in the folder and add them to the DB. (Implementation may use polling, inotify, or similar.)
- Manual rescan is triggered via `/rescan` endpoint.

### Thumbnail Caching
- Thumbnails are generated on-the-fly and served as JPEGs.
- Thumbnails are cached in memory using a robust, tested LRU cache (default 100MB, configurable via environment variable).
- Cache eviction, error handling (404 for missing, 500 for corrupt), and all logic are robustly tested with Pytest.

### Security
- Password for `/login` endpoint is read from the `PASSWORD` environment variable at request time (not at module load).
- No upload/delete endpoints in initial version; images are added manually to the folder.
- Backend is robust against missing files and handles DB/filesystem errors gracefully.
- CORS is enabled for local frontend development.

### Testing
- All backend features are tested with Pytest and pytest-cov (minimum 90% coverage enforced).
- Static analysis (Pyright) and formatting (Black) are enforced via pre-commit hooks and CI.
- Tests ensure DB/filesystem isolation and clean up after themselves.
- Test-driven development is strictly enforced: tests are written before code, and all code is covered by tests before merging.

---

## Frontend (Next.js)

### Features
- **Single-Photo UX:** Fetches and displays a random photo from the backend, with an editable caption field below the image. Caption edits are saved in real time (debounced) via the API.
- **No Gallery/Grid:** There is no gallery or grid view; the user always sees a single random photo, as per the latest UX direction.
- **No Rescan Button:** Manual rescanning is not exposed in the UI.
- **Responsive Design:** Usable on all modern browsers, with basic accessibility (alt text = caption > filename > blank).
- **No upload/delete UI:** Images are uniquely identified by their SHA-256 hash.

### API Integration
- All API calls expect and handle standardized error responses.
- Frontend and backend communicate only via HTTP and must support different domains.

### Testing
- Uses Jest and React Testing Library for unit/component tests.
- Uses Playwright for E2E tests (e.g., caption editing, random photo fetch).
- Test-driven development is strictly enforced: all features are implemented via TDD, and all code is covered by tests before merging.

---

## Extensibility & Future Enhancements
- **Easy to add:** Upload, delete, search, or ML-based auto-captioning endpoints.
- **Photo model and API are designed to accept new metadata fields and features with minimal rework. The photo's `hash` is the primary key; `filename` is metadata.
- **Nothing is hard-coded to the name "Captioner"; renaming is painless.

---

## Project Structure
- `/backend/app/` – FastAPI app and models
- `/backend/images/` – Original images
- `/backend/thumbnails/` – Cached thumbnails
- `/backend/photos.db` – SQLite database
- `/backend/tests/` – Pytest tests
- `/frontend/src/` – React source code
- `/frontend/public/` – Static files
- `/frontend/package.json` – Frontend dependencies

---

## Development Practices
- Test-driven development is strictly followed.
- All new features require corresponding tests before code is written.
- Tests must pass before code is considered complete.
- Code is concise, maintainable, and written with a healthy dose of skepticism about your own abilities.

---

## Known Gaps / TODOs
- Thumbnail cache logic (in-memory, LRU, configurable)
- Automated detection of new images placed in the folder (beyond startup scan)

---

## Philosophy
- Simplicity, extensibility, and testability are paramount.
- If you’re not writing tests first, you’re doing it wrong.
- If you’re not refactoring after the tests pass, you’re probably still doing it wrong.
- The codebase is your enemy; treat it with suspicion and demand proof (in the form of passing tests) before trusting anything.
