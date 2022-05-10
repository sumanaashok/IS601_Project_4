import csv

from flask import url_for
from flask_login import current_user

from app import db
from app.db.models import User, Transaction


def test_transaction_csv_upload(client):
    """This tests the functionality of uploading a csv file of transactions, and checking the processed records"""
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
        },
                                     follow_redirects=True)

        assert login_response.status_code == 200

        form_data = {
            "file": open('testing_resources/transactions.csv', 'rb')
        }

        # This makes a call to upload the csv of transactions which will be processed.
        transaction_csv_upload_response = client.post(
            "/transactions/upload",
            data=form_data,
            follow_redirects=True)

        user_object = User.query.filter_by(email='testuser1@test.com').first()
        transactions = Transaction.query.filter_by(user_id=user_object.id)

        assert user_object is not None
        assert transaction_csv_upload_response.status_code == 200
        assert transactions.count() > 10
        assert transactions.first().user_id == user_object.id

        # This makes a call to browse the transactions uploaded
        browse_transactions_response = client.get("/transactions")
        test_header = f"Browse: Transactions"
        test_transaction_content = f"CREDIT"
        header_content = bytes(test_header, 'utf-8')
        transactions_content = bytes(test_transaction_content, 'utf-8')
        assert browse_transactions_response.status_code == 200
        assert header_content in browse_transactions_response.data
        assert transactions_content in browse_transactions_response.data


def test_transactions_csv_upload_access_denied(client):
    """This tests the csv file upload denial"""
    with client:
        # checking if access to transactions upload page without login is redirecting to login page
        response = client.get("/transactions/upload")
        assert response.status_code == 302
        # checking if the redirect is working properly
        response_following_redirects = client.get("/transactions/upload", follow_redirects=True)
        assert response_following_redirects.request.path == url_for('auth.login')
        assert response_following_redirects.status_code == 200


def test_balance_calculation(client):
    """This tests is the balance calculated is correct"""
    with client:
        register_response = client.post("/register", data={
            "email": "testuser123@test.com",
            "password": "test123!test",
            "confirm": "test123!test"
        },
                                        follow_redirects=True)
        login_response = client.post("/login", data={
            "email": "testuser123@test.com",
            "password": "test123!test"
        },
                                     follow_redirects=True)

        assert login_response.status_code == 200

        form_data = {
            "file": open('testing_resources/transactions.csv', 'rb')
        }

        balance_before_transaction = User.query.get(current_user.id).balance
        # balance before any transaction
        assert balance_before_transaction == 0
        # This makes a call to upload the csv of transactions which will be processed.
        transaction_csv_upload_response = client.post(
            "/transactions/upload",
            data=form_data,
            follow_redirects=True)

        assert transaction_csv_upload_response.status_code == 200
        # balance after transaction
        balance_after_transaction = User.query.get(current_user.id).balance
        assert balance_after_transaction == 10601



