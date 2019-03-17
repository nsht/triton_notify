import os
import tempfile

import pytest

from app import app

@pytest.fixture
def client():
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    client = app.test_client()

    yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])



def test_empty_db(client):
    """Start with a blank database."""
    response = client.get('/')
    assert b'ok' in response.data

def test_unauthorized_healthcheck_access(client):
    """Send request without auth"""
    response = client.get('/healthcheck')
    assert(response.status_code == 401)

def test_unauthorized_message_send(client):
    """Send message send request without auth"""
    response = client.post('/message/telegram')
    assert(response.status_code == 401)