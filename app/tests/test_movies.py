import pytest



@pytest.mark.parametrize("payload, expected_title", [
    ({"title": "Frozen", "genre": "Animation",
     "description": "Children musical."}, "New Movie")
])
def test_list_movie(client, setup_database, payload, expected_title):
    # Signup
    response = client.post(
        "/signup/", json={"username": "john_42", "email": "john42@gmail.com", "full_name": "John Doe", "password": "qwertyuiop"})
    assert response.status_code == 201

    # Authenticate and get token
    response = client.post(
        "/login/", data={"username": "john_42",  "password": "qwertyuiop"})


    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    token = response.json()["access_token"]

    # Test for authentication
    response = client.post(
        '/movies',
        json=payload)
    
    assert response.status_code == 401

    # Test create movie
    response = client.post(
        '/movies',
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == expected_title
    

def test_get_movies(client, setup_database):
    response = client.get("/movies")

    assert response.status_code == 200
    data = response.json()
   
    # Ensure each movie has a "title" and "genre" field
    assert all("title" in movie for movie in data)
    assert all("genre" in movie for movie in data)


@pytest.mark.parametrize("movie_id, wrong_id, expected_title", [(1, 99, "New Movie")])
def test_get_movie_by_id(client, setup_database, movie_id, wrong_id, expected_title):
    response = client.get(f"/movies/{movie_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == expected_title
    
    response = client.get(f"/movies/{wrong_id}")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "No Movie Found"}



@pytest.mark.parametrize("genre, wrong_genre, expected_movie_count", [("Drama", "Fiction", 1)])
def test_get_movie_by_genre(client, setup_database, genre, wrong_genre, expected_movie_count):
    response = client.get(f"/movies/genre/{genre}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == expected_movie_count
    
    response = client.get(f"/movies/genre/{wrong_genre}")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "No Movie Found"}

@pytest.mark.parametrize("movie_title, expected_title, wrong_title", [("New Movie", "New Movie", "Wrong Title")])
def test_get_movie_by_title(client, setup_database, movie_title, expected_title, wrong_title):
    response = client.get(f"/movies/title/{movie_title}")

    assert response.status_code == 200
    data = response.json()
    assert all(movie["title"] == expected_title for movie in data)
    
    response = client.get(f"/movies/title/{wrong_title}")
    assert response.status_code == 404
    data = response.json()
    assert data == {"detail": "No Movie Found"}




@pytest.mark.parametrize("username, password, movie_id, user_id, update_payload, expected_title, wrong_id", [
    ("john_42", "qwertyuiop", 1, 1, {"title": "Updated Movie Title"}, "Updated Movie Title", 99)
])
def test_update_movie(client, setup_database, username, password, movie_id, user_id, update_payload, expected_title, wrong_id):
# Check if movie exists
  response = client.get(f"/movies/{movie_id}")

  assert response.status_code == 200

  # Check if not movie
  response = client.get(f"/movies/{wrong_id}")

  assert response.status_code == 404

  # Login to authenticate
  response = client.post(
      "/login/", data={"username": username,  "password": password})

  assert response.status_code == 200
  data = response.json()

  assert "access_token" in data
  assert data["token_type"] == "bearer"

  token = response.json()["access_token"]

  # Check authentication
  response = client.put(f"/movies/{movie_id}", json=update_payload)
  assert response.status_code == 401

  response = client.put(f"/movies/{user_id}", json=update_payload,
                        headers={"Authorization": f"Bearer {token}"})

  assert response.status_code == 200
  data = response.json()
  assert data["title"] == expected_title
  

  # Test for authenticated user updating another user's movie
  response = client.post(
      "/signup/", json={"username": "sarah87", "email": "sarah87@msn.com",
                 "full_name": "Sarah Jane", "password": "qwertyuiop"})

  # Login to authenticate
  response = client.post(
        "/login/", data={"username": "sarah87",  "password": "qwertyuiop"})
      
  
  assert response.status_code == 200
  data = response.json()

  assert "access_token" in data
  assert data["token_type"] == "bearer"

  token = response.json()["access_token"]

  response = client.put(f"/movies/{movie_id}", json=update_payload,
                        headers={"Authorization": f"Bearer {token}"})

  assert response.status_code == 401
  data = response.json()
  assert data == {"detail": "Unauthorized"}


@pytest.mark.parametrize("username, password, movie_id, wrong_id, username2, password2", [("john_42", "qwertyuiop", 1, 99, "sarah87", "qwertyuiop")])
def test_delete_movie(client, setup_database, username, password, movie_id, wrong_id, username2, password2):


    # Check for authentication
    response = client.delete(f"/movies/{movie_id}")
    assert response.status_code == 401

   
    # Check if authenticated user can delete another user"s movie
    response = client.post(
      "/login/", data={"username": username2,  "password": password2})

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"

    token = response.json()["access_token"]

    response = client.delete(f"/movies/{movie_id}",
                        headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    data = response.json()
    assert data == {"detail": "Unauthorized"}

    # Check if movie not in db
    response = client.get(f"/movies/{wrong_id}",
                          headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    data = response.json()
    assert data == {"detail":"No Movie Found"}

    # Login to authenticate
    response = client.post(
        "/login/", data={"username": username,  "password": password})

    assert response.status_code == 200
    
    token = response.json()["access_token"]

    response = client.delete(f"/movies/{movie_id}",
                             headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data == {"message": "Successf"}
    