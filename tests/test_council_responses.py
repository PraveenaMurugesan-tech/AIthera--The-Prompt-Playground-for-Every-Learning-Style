def test_create_council_response(auth_client):
    create = auth_client.post("/prompts/", json={"topic": "CouncilTopic", "learning_style": "visual", "difficulty": "beginner"})
    request_id = create.json()["id"]

    payload = {
        "request_id": request_id,
        "model": "test-model",
        "role": "expert",
        "prompt": "Answer this",
        "reasoning": "Because",
        "strengths": ["clear", "concise"],
        "metadata": {"foo": "bar"},
    }

    resp = auth_client.post("/council-responses/", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["request_id"] == request_id
    assert body["model"] == "test-model"


def test_get_council_responses(auth_client):
    create = auth_client.post("/prompts/", json={"topic": "CRTopic", "learning_style": "visual", "difficulty": "beginner"})
    request_id = create.json()["id"]

    payload = {
        "request_id": request_id,
        "model": "test-model",
        "role": "expert",
        "prompt": "Answer this",
        "reasoning": "Because",
        "strengths": ["clear"],
    }

    auth_client.post("/council-responses/", json=payload)

    resp = auth_client.get(f"/council-responses/{request_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
