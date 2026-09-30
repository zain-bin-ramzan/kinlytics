import pytest
from fastapi.testclient import TestClient
from store import store

@pytest.fixture
def client():
    store.reset()
    from main import app
    with TestClient(app) as c:
        yield c