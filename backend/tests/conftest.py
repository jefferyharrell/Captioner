import sys
import os
import pytest
from fastapi.testclient import TestClient

# Ensure the backend directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def cleanup_files():
    files = []
    def register(file_path):
        files.append(file_path)
    yield register
    for file_path in files:
        try:
            if hasattr(file_path, 'exists') and file_path.exists():
                file_path.unlink()
            elif isinstance(file_path, str):
                import os
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception:
            pass
