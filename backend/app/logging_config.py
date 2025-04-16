import logging
import logging.handlers
import os
from pathlib import Path

def setup_logging(log_dir=None, syslog_enable=False):
    """
    Configure logging for the backend. Logs to stdout and a rotating file.
    Optionally logs to syslog if syslog_enable is True.
    """
    # Allow override via environment variable for testability
    env_log_dir = os.environ.get("LOG_DIR")
    if env_log_dir:
        log_dir = Path(env_log_dir)
    else:
        log_dir = log_dir or Path(__file__).parent.parent / "logs"
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "server.log"
    # Truncate the log file at startup
    try:
        with open(log_file, "w", encoding="utf-8"):
            pass  # This empties the file
    except Exception as e:
        # If truncation fails, log to stdout only
        print(f"WARNING: Could not truncate log file {log_file}: {e}")

    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove ALL handlers (not just default) so re-calling works in tests
    while root_logger.handlers:
        root_logger.removeHandler(root_logger.handlers[0])

    # StreamHandler (stdout)
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    root_logger.addHandler(sh)

    # RotatingFileHandler
    fh = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8"
    )
    fh.setFormatter(formatter)
    root_logger.addHandler(fh)

    # Syslog (optional)
    if syslog_enable or os.environ.get("SYSLOG_ENABLE", "0") == "1":
        try:
            syslog_address = "/dev/log" if os.name != "nt" else ("localhost", 514)
            syslog_handler = logging.handlers.SysLogHandler(address=syslog_address)
            syslog_handler.setFormatter(formatter)
            root_logger.addHandler(syslog_handler)
        except Exception as e:
            root_logger.warning(f"Syslog handler could not be attached: {e}")

    root_logger.info(f"Logging initialized. Level: {log_level}, Log file: {log_file}")
