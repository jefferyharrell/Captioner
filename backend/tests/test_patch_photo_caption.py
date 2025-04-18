from pathlib import Path
import hashlib
import uuid
from sqlalchemy import text


def test_patch_photo_caption(test_app, temp_photos_dir):
    filename = f"caption_{uuid.uuid4().hex}.jpeg"
    fake_image = uuid.uuid4().bytes
    test_hash = hashlib.sha256(fake_image).hexdigest()
    ext = Path(filename).suffix
    hashed_filename = f"{test_hash}{ext}"
    file_path = temp_photos_dir / hashed_filename
    # Upload
    resp = test_app.post(
        "/photos", files={"file": (filename, fake_image, "image/jpeg")}
    )
    assert resp.status_code == 201
    data = resp.json()
    # PATCH caption
    new_caption = "A very cool caption!"
    resp2 = test_app.patch(
        f"/photos/{data['hash']}/caption", json={"caption": new_caption}
    )
    assert resp2.status_code == 200
    patched = resp2.json()
    assert patched["hash"] == data["hash"]
    assert patched["filename"] == filename
    assert patched["caption"] == new_caption
    # GET to verify
    resp3 = test_app.get(f"/photos/{data['hash']}")
    assert resp3.status_code == 200
    body = resp3.json()
    assert body["caption"] == new_caption
    # PATCH with fake hash/filename
    resp4 = test_app.patch(
        "/photos/badhash/doesnotexist.jpg/caption", json={"caption": "nope"}
    )
    assert resp4.status_code == 404
    data4 = resp4.json()
    assert set(data4.keys()) == {"detail"}
