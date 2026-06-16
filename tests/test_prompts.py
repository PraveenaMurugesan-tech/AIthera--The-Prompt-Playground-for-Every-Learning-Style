def test_create_prompt(auth_client):
    payload = {"topic": "Photosynthesis", "learning_style": "visual", "difficulty": "beginner"}
    resp = auth_client.post("/prompts/", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["topic"] == payload["topic"]
    assert "id" in body
    request_id = body["id"]

    # cleanup: delete
    del_resp = auth_client.delete(f"/prompts/{request_id}")
    assert del_resp.status_code == 204


def test_list_prompts(auth_client):
    # create two prompts
    for i in range(2):
        auth_client.post("/prompts/", json={"topic": f"T{i}", "learning_style": "visual", "difficulty": "beginner"})

    resp = auth_client.get("/prompts/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_get_prompt(auth_client):
    create = auth_client.post("/prompts/", json={"topic": "UniqueTopic", "learning_style": "textual", "difficulty": "intermediate"})
    assert create.status_code == 201
    req = create.json()
    request_id = req["id"]

    resp = auth_client.get(f"/prompts/{request_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == request_id

    # cleanup
    auth_client.delete(f"/prompts/{request_id}")


def test_delete_prompt(auth_client):
    create = auth_client.post("/prompts/", json={"topic": "ToDelete", "learning_style": "visual", "difficulty": "beginner"})
    assert create.status_code == 201
    request_id = create.json()["id"]

    resp = auth_client.delete(f"/prompts/{request_id}")
    assert resp.status_code == 204

    # ensure 404 afterwards
    get = auth_client.get(f"/prompts/{request_id}")
    assert get.status_code == 404
