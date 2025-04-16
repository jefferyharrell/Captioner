# Captioner – Project Specification (Prose Edition)

Captioner is a private web application designed to make viewing and captioning photographs as painless as possible. The system is split into a React frontend and a FastAPI backend, with images stored on the backend's filesystem and captions tracked in a SQLite database. The application is intended for use on macOS and Linux, and is designed to be easily extensible for future enhancements.

When the user opens the gallery, they are greeted by a grid of image thumbnails, each displaying its current caption if one exists. Clicking a thumbnail brings up a detail view, showing the image at full size and providing a text area for editing its caption. Thumbnails are generated on-the-fly and cached in memory, with a default maximum cache size of 100 megabytes—this limit can be adjusted via configuration. The cache is managed to avoid filling up RAM, but otherwise aims to be invisible to the user.

Images are discovered by scanning a designated folder on the backend. This scan happens automatically at startup, but the user can also trigger a rescan manually via a button in the frontend, which calls a dedicated API endpoint. The rescan endpoint returns immediately with a simple acknowledgment, and the frontend is responsible for refreshing the gallery after a short delay to reflect any new images.

Each image is uniquely identified by its SHA-256 hash. If two files have identical contents (regardless of filename), only one entry is created in the database and duplicate uploads are rejected. The database schema uses the hash as the primary key; filename is stored as metadata and can be non-unique. The schema is designed to be extensible for future metadata fields.

Captions are stored as plain Unicode text and can be any length. The API for updating captions expects a JSON object in the request body (for example, {"caption": "A nice day at the beach"}). If a caption update is attempted for an image that doesn't exist, the backend responds with a standardized FastAPI error object, such as {"detail": "Photo not found."}. All errors returned by the API follow this structure, making them easy to handle programmatically.

The frontend is designed to be responsive and usable on all modern browsers, but there's no requirement for strict accessibility compliance—just basic common sense to avoid egregious usability blunders. For images, the alt text is set to the caption if present, falls back to the filename if not, and is left blank if both are missing, so screen readers aren't forced to read out something pointless.

No upload or deletion functionality is provided in the initial version; images are added manually to the folder. The backend is robust against missing files and gracefully handles database or filesystem errors. The project is developed using test-driven development, with Pytest for the backend and React Testing Library for the frontend.

While the current focus is on simplicity, the entire architecture is intentionally extensible. Future enhancements, such as image upload, deletion, search, or even automatic captioning using machine learning models, can be added without major rework. Nothing in the design should preclude bolting on an image-to-text model for auto-generating captions if the urge ever strikes.

Finally, the project name "Captioner" is just a placeholder—feel free to change it later, and avoid hard-coding it anywhere that would make renaming a pain.
