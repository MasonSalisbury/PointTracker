from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_add_transaction():
    data = '{ "payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z" }'
    response = client.post("/transactions", data=data)
    assert response.status_code == 200
    assert response.json()["payer"] == "DANNON"

def test_get_transactions():
    data = '{ "payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z" }'
    _ = client.post("/transactions", data=data)
    response = client.get("/balances")
    response_data = response.json()
    assert len(response_data) > 0
    assert "MILLER COORS" in response_data
    assert response_data["MILLER COORS"] == 10000

def test_example_scenario():
    _ = client.delete("/clear_db")

    reqs = [
        '{ "payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z" }',
        '{ "payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z" }',
        '{ "payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z" }',
        '{ "payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z" }',
        '{ "payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z" }'
    ]
    for req in reqs:
        _ = client.post("/transactions", data=req)

    data = { "points": 5000 }
    response = client.patch("/spend", json=data)
    response_data = response.json()
    
    expected_payer_to_points = {
        "DANNON": -100,
        "UNILEVER": -200,
        "MILLER COORS": -4700
    }
    for actual in response_data:
        assert expected_payer_to_points[actual["payer"]] == actual["points"]

    response2 = client.get("/balances")
    data2 = response2.json()
    assert data2["DANNON"] == 1000
    assert data2["UNILEVER"] == 0
    assert data2["MILLER COORS"] == 5300

def test_multi_spend():
    _ = client.delete("/clear_db")

    reqs = [
        '{ "payer": "Apple", "points": -500, "timestamp": "2021-11-13T14:00:00Z" }',
        '{"payer":"Boeing","points":200,"timestamp":"2021-11-14T14:00:00Z"}',
        '{"payer":"Google","points":300,"timestamp":"2021-11-12T14:00:00Z"}',
        '{"payer":"Apple","points":1000,"timestamp":"2021-11-11T14:00:00Z"}'
    ]
    for req in reqs:
        client.post("/transactions", data=req)

    # Spend 1: 800 points
    spend_data = {"points": 800}
    spend_response = client.patch("/spend", json=spend_data).json()

    expected_payer_to_points = {
        "Apple": -500,
        "Google": -300
    }
    for actual in spend_response:
        assert expected_payer_to_points[actual["payer"]] == actual["points"]

    balances_response = client.get("/balances").json()
    assert balances_response["Apple"] == 0
    assert balances_response["Google"] == 0
    assert balances_response["Boeing"] == 200

    # Spend 2: 150 points
    spend_data2 = {"points": 150}
    spend_response2 = client.patch("/spend", json=spend_data2).json()

    expected_payer_to_points = {
        "Boeing": -150
    }
    for actual in spend_response2:
        assert expected_payer_to_points[actual["payer"]] == actual["points"]

    balances_response2 = client.get("/balances").json()
    assert balances_response2["Apple"] == 0
    assert balances_response2["Google"] == 0
    assert balances_response2["Boeing"] == 50

def test_over_spend():
    _ = client.delete("/clear_db")

    client.post("/transactions", data='{"payer":"Boeing","points":200,"timestamp":"2021-11-14T14:00:00Z"}')

    spend_data = {"points": 1000}
    spend_response = client.patch("/spend", json=spend_data)

    assert spend_response.status_code == 400
