def test_create_consensus_result(auth_client):
    create = auth_client.post("/prompts/", json={"topic": "ConsensusTopic", "learning_style": "visual", "difficulty": "beginner"})
    request_id = create.json()["id"]

    payload = {"request_id": request_id, "final_prompt": "Final", "quality_score": 0.9}
    resp = auth_client.post("/consensus-results/", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["request_id"] == request_id


def test_get_consensus_result(auth_client):
    create = auth_client.post("/prompts/", json={"topic": "ConsensusTopic2", "learning_style": "visual", "difficulty": "beginner"})
    request_id = create.json()["id"]

    payload = {"request_id": request_id, "final_prompt": "Final2"}
    auth_client.post("/consensus-results/", json=payload)

    resp = auth_client.get(f"/consensus-results/{request_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["request_id"] == request_id
