"""This tests login , registration and dashboard authentication"""
from flask import url_for


def test_register(client):
    """This tests for successful registration"""
    with client:
        register_response = client.post("/register", data={
            "email": "testuser1@test.com",
            "password": "test123!test",
            "confirm": "test123!test"
        },
                                        follow_redirects=True)
        # After successful registration,redirected to login page
        assert register_response.status_code == 200
        assert register_response.request.path == url_for('auth.login')


def test_login(client):
    """This tests for successful login"""
    with client:
        register_response = client.post("/register", data={
            "email": "testuser1@test.com",
            "password": "test123!test",
            "confirm": "test123!test"
        },
                                        follow_redirects=True)

        assert register_response.status_code == 200
        assert register_response.request.path == url_for('auth.login')

        login_response = client.post("/login", data={
            "email": "testuser1@test.com",
            "password": "test123!test"
        },
                                     follow_redirects=True)
        # After successful login ,redirected to dashboard
        assert login_response.request.path == url_for('auth.dashboard')
        assert login_response.status_code == 200


def test_dashboard_access(client):
    """This tests for successful access to dashboard after login"""
    with client:
        register_response = client.post("/register", data={
            "email": "testuser1@test.com",
            "password": "test123!test",
            "confirm": "test123!test"
        },
                                        follow_redirects=True)

        login_response = client.post("/login", data={
            "email": "testuser1@test.com",
            "password": "test123!test"
        }, follow_redirects=True)
        assert login_response.request.path == url_for('auth.dashboard')
        assert login_response.status_code == 200


def test_dashboard_access_denied(client):
    """This tests for unsuccessful access to dashboard after login"""
    with client:
        register_response = client.post("/register", data={
            "email": "testuser1@test.com",
            "password": "test123!test",
            "confirm": "test123!test"
        },
                                        follow_redirects=True)

        assert register_response.status_code == 200
        assert register_response.request.path == url_for('auth.login')

        login_response = client.post("/login", data={
            "email": "testuser1@test.com",
            "password": "test1234!test"
        },
                                     follow_redirects=True)
        assert login_response.request.path == url_for('auth.login')
        assert login_response.status_code == 200





