from flask import url_for

from app.db.models import User, Song


def test_songs_csv_upload(client):
    """This tests the functionality of uploading a csv file of songs, and checking the processed records"""
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
            "file": open('testing_resources/music.csv', 'rb')
        }

        # This makes a call to upload the csv of songs which will be processed.
        songs_csv_upload_response = client.post(
            "/songs/upload",
            data=form_data,
            follow_redirects=True)

        user_object = User.query.filter_by(email='testuser1@test.com').first()
        songs = Song.query.filter_by(user_id=user_object.id)

        assert user_object is not None
        assert songs_csv_upload_response.status_code == 200
        assert songs.count() > 10
        assert songs.first().user_id == user_object.id

        # This makes a call to browse the songs uploaded
        browse_songs_response = client.get("/songs")
        test_header = f"Browse: Songs"
        test_songs_content = f"Crazy (feat. Joie Tan) [Radio Mix]"
        header_content = bytes(test_header, 'utf-8')
        songs_content = bytes(test_songs_content, 'utf-8')
        assert browse_songs_response.status_code == 200
        assert header_content in browse_songs_response.data
        assert songs_content in browse_songs_response.data


def test_songs_csv_upload_access_denied(client):
    """This tests the csv file upload denial"""
    with client:
        # checking if access to songs upload page without login is redirecting to login page
        response = client.get("/songs/upload")
        assert response.status_code == 302
        # checking if the redirect is working properly
        response_following_redirects = client.get("/songs/upload", follow_redirects=True)
        assert response_following_redirects.request.path == url_for('auth.login')
        assert response_following_redirects.status_code == 200
