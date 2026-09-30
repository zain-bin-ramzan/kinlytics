def create_round(client, date="2026-09-29", min_participants=3):
    r = client.post("/rounds", json={"date": date, "min_participants": min_participants})
    assert r.status_code == 200
    return r.json()["round_id"]

def contribute(client, rid, client_id, total, apps=None, date="2026-09-29"):
    return client.post(f"/rounds/{rid}/contributions", json={
        "client_id": client_id,
        "date": date,
        "total_screen_time_minutes": total,
        "app_usage_minutes": apps or {},
    })

# --- round lifecycle ---

def test_create_round(client):
    rid = create_round(client)
    assert rid

def test_get_unknown_round_404(client):
    assert client.get("/rounds/nope").status_code == 404

def test_close_round(client):
    rid = create_round(client)
    assert client.post(f"/rounds/{rid}/close").status_code == 200
    # submit after close -> 409
    r = contribute(client, rid, "c1", 100)
    assert r.status_code == 409
    assert r.json()["detail"] == "round_closed"

# --- contribution validation ---

def test_duplicate_client_rejected(client):
    rid = create_round(client)
    assert contribute(client, rid, "c1", 100).status_code == 200
    r = contribute(client, rid, "c1", 200)
    assert r.status_code == 409
    assert r.json()["detail"] == "duplicate"

def test_wrong_date_rejected(client):
    rid = create_round(client, date="2026-09-29")
    r = contribute(client, rid, "c1", 100, date="2026-09-28")
    assert r.status_code == 400
    assert r.json()["detail"] == "date_mismatch"

def test_status_counts_participants(client):
    rid = create_round(client)
    contribute(client, rid, "c1", 100)
    contribute(client, rid, "c2", 200)
    body = client.get(f"/rounds/{rid}").json()
    assert body["received"] == 2
    assert set(body["valid_clients"]) == {"c1", "c2"}

# --- aggregation ---

def test_result_gated_by_min_participants(client):
    rid = create_round(client, min_participants=3)
    contribute(client, rid, "c1", 100)
    contribute(client, rid, "c2", 200)
    body = client.get(f"/rounds/{rid}/result").json()
    assert body["released"] is False
    assert body["participants_used"] == 2

def test_result_average_and_ranking(client):
    rid = create_round(client, min_participants=3)
    contribute(client, rid, "c1", 240, {"chat": 80, "video": 60})
    contribute(client, rid, "c2", 180, {"chat": 40, "video": 100})
    contribute(client, rid, "c3", 300, {"chat": 50})

    body = client.get(f"/rounds/{rid}/result").json()
    assert body["released"] is True
    assert body["participants_used"] == 3
    assert body["average_screen_time_minutes"] == 240.0  # (240+180+300)/3

    ranking = {a["app_id"]: a["total_minutes"] for a in body["app_ranking"]}
    assert ranking == {"chat": 170, "video": 160}

    # ordering: chat first
    assert body["app_ranking"][0]["app_id"] == "chat"

def test_offline_client_not_counted_as_zero(client):
    rid = create_round(client, min_participants=2)
    contribute(client, rid, "c1", 200)
    contribute(client, rid, "c2", 400)
    # c3 never submits
    body = client.get(f"/rounds/{rid}/result").json()
    assert body["participants_used"] == 2
    assert body["average_screen_time_minutes"] == 300.0 