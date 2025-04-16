def test_login_success(test_app, monkeypatch):
    test_password = "super_secret_test_pw"
    monkeypatch.setenv("PASSWORD", test_password)
    resp = test_app.post("/login", json={"password": test_password})
    assert resp.status_code == 200
    data = resp.json()
    assert data == {"success": True}


def test_login_failure(test_app, monkeypatch):
    test_password = "super_secret_test_pw"
    monkeypatch.setenv("PASSWORD", test_password)
    resp = test_app.post("/login", json={"password": "wrong_pw"})
    assert resp.status_code == 200
    data = resp.json()
    assert data == {"success": False}
