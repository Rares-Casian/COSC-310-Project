from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": "1",
    "title": "Hockey Sticks",
    "category": "sports",
    "tags": [
      "hockey",
      "equipment"
    ]
    }

def test_read_nonexistent_item():
    response = client.get("/items/8")
    assert response.status_code == 404
    assert response.json() == {'detail': "Item '8' not found"}


def test_create_item():
    response = client.post("/items/",json={"id": "10",
    "title": "Rares",
    "category": "School",
    "tags": [
      "class",
      "assigments"
    ]}
    )
    idnum = response.json()["id"]
    print(idnum)
    assert response.status_code == 201
    assert response.json() == {
    "id": idnum,
    "title": "Rares",
    "category": "School",
    "tags": [
      "class",
      "assigments"
    ]
  }














# from fastapi.testclient import TestClient
# from .main import app as a

# client = TestClient(a)

# def test_health():
#     r = client.get("/health")
#     assert r.status_code == 200
#     assert r.json() == {"status": "ok"}

#def test_get_item():
#   r = client.get("/data/items.json")