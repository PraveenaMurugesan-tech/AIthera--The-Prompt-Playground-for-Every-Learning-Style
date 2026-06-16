def test_create_explanation(auth_client):
    # create prompt
    create = auth_client.post("/prompts/", json={"topic": "ExplainX", "learning_style": "visual", "difficulty": "beginner"})
    assert create.status_code == 201
    request_id = create.json()["id"]

    resp = auth_client.post(f"/explanations/{request_id}/generate")
    assert resp.status_code == 201
    data = resp.json()
    assert data["request_id"] == request_id
    assert "content" in data


def test_get_explanation(auth_client):
    create = auth_client.post("/prompts/", json={"topic": "ExplainY", "learning_style": "visual", "difficulty": "beginner"})
    request_id = create.json()["id"]

    # generate explanation
    auth_client.post(f"/explanations/{request_id}/generate")

    resp = auth_client.get(f"/explanations/{request_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["request_id"] == request_id
