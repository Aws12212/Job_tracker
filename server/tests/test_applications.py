def create_application(client, headers, **fields):
    data = {"company": "Acme", "role": "Backend Dev", **fields}
    res = client.post("/applications", json=data, headers=headers)
    assert res.status_code == 201
    return res.json()


def test_create_application(client, auth):
    res = client.post("/applications", json={"company": "Acme", "role": "Backend Dev"}, headers=auth)

    assert res.status_code == 201
    body = res.json()
    assert body["company"] == "Acme"
    assert body["status"] == "wishlist"
    assert "id" in body


def test_list_applications(client, auth):
    create_application(client, auth, company="Acme")
    create_application(client, auth, company="Globex")

    res = client.get("/applications", headers=auth)

    assert res.status_code == 200
    assert {a["company"] for a in res.json()} == {"Acme", "Globex"}


def test_filter_by_status(client, auth):
    create_application(client, auth, company="Acme", status="applied")
    create_application(client, auth, company="Globex", status="wishlist")

    res = client.get("/applications", params={"status": "applied"}, headers=auth)

    assert [a["company"] for a in res.json()] == ["Acme"]


def test_search_matches_company_or_role(client, auth):
    create_application(client, auth, company="Acme", role="Backend Dev")
    create_application(client, auth, company="Globex", role="Data Engineer")

    by_company = client.get("/applications", params={"q": "glob"}, headers=auth).json()
    by_role = client.get("/applications", params={"q": "backend"}, headers=auth).json()

    assert [a["company"] for a in by_company] == ["Globex"]
    assert [a["company"] for a in by_role] == ["Acme"]


def test_get_application(client, auth):
    created = create_application(client, auth)

    res = client.get(f"/applications/{created['id']}", headers=auth)

    assert res.status_code == 200
    assert res.json()["id"] == created["id"]


def test_patch_updates_only_sent_fields(client, auth):
    created = create_application(client, auth, notes="Referral from Sam")

    res = client.patch(f"/applications/{created['id']}", json={"status": "interview"}, headers=auth)

    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "interview"
    assert body["company"] == "Acme"
    assert body["notes"] == "Referral from Sam"


def test_patch_rejects_invalid_status(client, auth):
    created = create_application(client, auth)

    res = client.patch(f"/applications/{created['id']}", json={"status": "nope"}, headers=auth)

    assert res.status_code == 422


def test_delete_application(client, auth):
    created = create_application(client, auth)

    res = client.delete(f"/applications/{created['id']}", headers=auth)

    assert res.status_code == 204
    assert client.get(f"/applications/{created['id']}", headers=auth).status_code == 404


def test_users_cannot_see_each_others_applications(client, make_user):
    alice = make_user("alice@example.com")
    bob = make_user("bob@example.com")
    created = create_application(client, alice)
    url = f"/applications/{created['id']}"

    assert client.get("/applications", headers=bob).json() == []
    assert client.get(url, headers=bob).status_code == 404
    assert client.patch(url, json={"status": "offer"}, headers=bob).status_code == 404
    assert client.delete(url, headers=bob).status_code == 404


def test_requires_login(client):
    assert client.get("/applications").status_code == 401
    assert client.post("/applications", json={"company": "Acme", "role": "Dev"}).status_code == 401
