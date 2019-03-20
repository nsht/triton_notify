import os
import tempfile
import json

import pytest

import triton_notify, pdb
from triton_notify.models import models
import bcrypt


@pytest.fixture(scope="session")
def client():
    # Create in memory db
    triton_notify.app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///:memory:"
    models.db.create_all()
    triton_notify.app.config["TESTING"] = True
    client = triton_notify.app.test_client()

    # create test password hash
    test_pasword = "correct horse battery staple".encode()
    test_password_hash = bcrypt.hashpw(test_pasword, bcrypt.gensalt())
    # Create User object
    test_user = models.User(
        username="test",
        password=test_password_hash,
        user_type="test_user",
        email_id="test@example.com",
        status=1,
    )
    models.db.session.add(test_user)
    models.db.session.commit()
    yield client


def test_index(client):
    response = client.get("/")
    assert b"ok" in response.data


def test_unauthorized_healthcheck_access(client):
    """Send request without auth"""
    response = client.get("/healthcheck")
    assert response.status_code == 401


def test_unauthorized_message_send(client):
    """Send message send request without auth"""
    response = client.post("/message/telegram")
    assert response.status_code == 401


def test_successfull_login(client):
    """Test login """
    test_password = "correct horse battery staple"
    response = client.post(
        "/login",
        data=json.dumps({"username": "test", "password": test_password}),
        content_type="application/json",
    )
    assert response.status_code == 200


def test_unsuccessfull_login(client):
    """Test Failed login conditions"""
    test_password = "incorrect horse battery staple"
    response = client.post(
        "/login",
        data=json.dumps({"username": "test", "password": test_password}),
        content_type="application/json",
    )
    assert response.status_code == 401
