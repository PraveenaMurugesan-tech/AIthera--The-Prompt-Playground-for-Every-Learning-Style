def test_run_workflow(auth_client):
    create = auth_client.post("/prompts/", json={"topic": "WorkflowTopic", "learning_style": "visual", "difficulty": "beginner"})
    request_id = create.json()["id"]

    resp = auth_client.post(f"/workflow/{request_id}/run")
    assert resp.status_code == 200
    body = resp.json()
    # verify required fields
    assert body.get("request_id") == request_id
    assert "prompt_request" in body
    assert "council_responses" in body
    assert "consensus_result" in body
    assert "explanation" in body
