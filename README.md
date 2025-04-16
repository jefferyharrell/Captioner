# Captioner

Captioner is a private web application for viewing and captioning photographs. It features a React frontend and a FastAPI backend, storing images on the local filesystem and captions in a SQLite database. Designed for simplicity and extensibility, Captioner makes managing your photo collection and their captions straightforward, with a clean, organized codebase ready for future enhancements.

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
