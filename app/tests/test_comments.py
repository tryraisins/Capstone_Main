import pytest



@pytest.mark.parametrize("payload, movie_id, expected_comment", [
    ({"comment": "Too much Drama"}, 1, "Too much Drama")
])
def test_create_comment(client, setup_database, payload, movie_id, expected_comment):
    # Signup

    user_data = {"username": "john_42", "email": "john42@gmail.com",
                 "full_name": "John Doe", "password": "qwertyuiop"}

    response = client.post(
        "/signup/", json=user_data)
    assert response.status_code == 201

    # Authenticate and get token
    response = client.post(
        "/login/", data={"username": "john_42",  "password": "qwertyuiop"})

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    token = response.json()["access_token"]

    # Create two movies

    movie_data = {"title": "Action Man", "genre": "Action",
                  "description": "One Man Army."}
    
    another_movie_data = {"title": "Tree", "genre": "Drama",
                          "description": "Grow like a tree."}
    
    response = client.post(
        '/movies',
        json=movie_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201

    response = client.post(
        '/movies',
        json=another_movie_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201

    # Test for authentication
    response = client.post(
        f'/movies/comments/{movie_id}',
        json=payload)

    assert response.status_code == 401

    # Test create comment
    response = client.post(
        f'/movies/comments/{movie_id}',
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["comment"] == expected_comment

  # Asserting that user_id is 1 because john_42 has id of 1 
    assert data["user_id"] == 1


def test_get_comments(client, setup_database):
    response = client.get("/movies/comments/")

    assert response.status_code == 200
    data = response.json()

    # Ensure each comment has a "comment" and "replies" field
    assert all("comment" in comment for comment in data)
    assert all("replies" in comment for comment in data)


@pytest.mark.parametrize("comment_id, wrong_id, expected_comment", [(1, 99, "A sweet movie")])
def test_get_comment_by_id(client, setup_database, comment_id, wrong_id, expected_comment):
    response = client.get(f"/movies/comments/{comment_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["Comment"]["comment"] == expected_comment

    response = client.get(f"/movies/comments/{wrong_id}")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "No comment found"}


@pytest.mark.parametrize("movie_id, wrong_id, expected_count, another_movie_id", [(1, 99, 1, 2)])
def test_get_comment_by_movie(client, setup_database, movie_id, wrong_id,expected_count, another_movie_id):
    response = client.get(f"/movies/comments/movie/{movie_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == expected_count

    response = client.get(f"/movies/comments/movie/{wrong_id}")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "No Movie results"}

    response = client.get(f"/movies/comments/movie/{another_movie_id}")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "No comments for this movie"}



@pytest.mark.parametrize("user_id, wrong_id, another_user_id", [(1, 99,2)])
def test_get_comment_by_user(client, setup_database, user_id, wrong_id, another_user_id):
    response = client.get(f"/movies/comments/user/{user_id}")

    assert response.status_code == 200
    

    response = client.get(f"/movies/comments/user/{wrong_id}")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "User not found"}

    # Create another user with no comment

    another_user_data = {"username": "sarah87", "email": "sarah87@msn.com",
                 "full_name": "Sarah Jane", "password": "qwertyuiop"}
    
    response = client.post(
        "/signup/", json=another_user_data)
    assert response.status_code == 201
    
    response = client.get(f"/movies/comments/user/{another_user_id}")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "No comments for this user"}


@pytest.mark.parametrize("comment_id, wrong_id, payload, expected_comment", [(1, 99, {"comment": "I love the movie too"}, "I love the movie too")])
def test_reply_comment(client, setup_database, comment_id, wrong_id, payload, expected_comment):
    
    # Authenticate and get token
    response = client.post(
        "/login/", data={"username": "sarah87",  "password": "qwertyuiop"})

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    token = response.json()["access_token"]

    # Test Authorization
    response = client.post(f"/movies/comments/reply_comment/{comment_id}")

    assert response.status_code == 401

    # Test reply comment with wrong comment id
    response = client.post(
        f'/movies/comments/reply_comment/{wrong_id}',
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "No comment found"}


    # Test reply comment 
    response = client.post(
        f'/movies/comments/reply_comment/{comment_id}',
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["comment"] == expected_comment
    

@pytest.mark.parametrize("comment_id, wrong_id, comment_without_reply_id", [(1, 99, 2)])
def test_get_replies_to_comment(client, setup_database, comment_id, wrong_id, comment_without_reply_id):
    response = client.get(f"/movies/comments/replies/{comment_id}")

    assert response.status_code == 200

    # Test for comment not in database
    response = client.get(f"/movies/comments/replies/{wrong_id}")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "Initial comment not found"}

    # Test for comment without replies
    response = client.get(f"/movies/comments/replies/{comment_without_reply_id}")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "No replies"}


@pytest.mark.parametrize("comment_id, wrong_id, payload, expected_comment, another_comment_id", [(1, 99, {"comment": "Updated comment"}, "Updated comment", 2)])
def test_update_comment(client, comment_id, wrong_id, payload, expected_comment, another_comment_id):
    
    # Test for Authentication
    response = client.put(
        f"/movies/comments/{comment_id}", json=payload)
    assert response.status_code == 401

    # Authenticate and login a user
    response = client.post(
        "/login/", data={"username": "avrg",  "password": "asdfghjkl"})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    token = response.json()["access_token"]

    # Test update a non_existing comment
    response = client.put(
        f"/movies/comments/{wrong_id}", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "No Comment"}

    # Test if authenticated user can update another user's comment
    response = client.put(
        f"/movies/comments/{another_comment_id}", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Unauthorized"}

    # Test Update comment
    response = client.put(
        f"/movies/comments/{comment_id}", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["comment"] == expected_comment

    
@pytest.mark.parametrize("username, password, comment_id, wrong_id, another_comment_id", [("sarah87", "qwertyuiop", 2, 99, 1)])
def test_delete_comment(client, setup_database, username, password, comment_id, wrong_id, another_comment_id):

    # Login to authenticate
    response = client.post(
        "/login/", data={"username": username,  "password": password})

    assert response.status_code == 200
    token = response.json()["access_token"]

    # Test for authentication
    response = client.delete(f"/movies/comments/{comment_id}")
    assert response.status_code == 401

    # Test to delete comment not in db
    response = client.delete(f"/movies/comments/{wrong_id}",
                             headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "No Comment"}

    # Test if authenticated user can delete another user comment
    response = client.delete(f"/movies/comments/{another_comment_id}",
                             headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Unauthorized"}

    # Test Authenticated user can delete comment
    response = client.delete(
        f"/movies/comments/{comment_id}", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data == {"message": "Success"}