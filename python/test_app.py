import pytest
from app import app, is_file_exists


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_is_file_exists_false():
    assert is_file_exists('/tmp/__pytest_nonexistent__') is False


def test_is_file_exists_true():
    assert is_file_exists('/tmp') is True


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
