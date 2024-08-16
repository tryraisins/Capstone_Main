## Overview

The goal of this project is to develop a movie listing API using FastAPI. The API will allow users to list movies, view listed movies, rate them, and add comments. The application will be secured using JWT (JSON Web Tokens), ensuring that only the user who listed a movie can edit it.

## Tools

- **Framework**: FastAPI
- **Programming Language**: Python
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **ORM**: SQLAlchemy
- **Hosting Platform**: Render
- **Testing Framework**: Pytest
- **Environment Configuration**: python-dotenv

## Setup Instructions

### Prerequisites

- Python 3.12.1
- PostgreSQL
- Better Stack # Optional, for logging purposes

### API Documentation

Once the server is up and running, access the interactive API documentation at the provided URL.

### Installation Steps

1.  **Clone the repository**:

    ```
    git clone https://github.com/tryraisins/Capstone_Main.git
    ```

2.  **Install dependencies**:

    ```
    pip install -r requirements.txt
    ```

3.  **Configure the database**:

    Create a PostgreSQL database and set up the connection in the `.env` file\
    Add your SECRET_KEY value in the `.env` file\
    Add DATABASE_URL=your_database_url # Replace with your database URL\
    Then add the following

    ```
    ALGORITHM = HS256
    ACCESS_TOKEN_EXPIRES_MINUTES = 30
    ```

4.  **Add BetterStack Source**:

    Create a new python source and add the source token in the `.env` file:

    ```
    BETTER_STACK_TOKEN =your_BETTER_STACK_TOKEN  # Replace with your Better Stack Token
    ```

5.  **Apply database migrations**:

    ```
    alembic init alembic

    alembic upgrade head
    ```

6.  **Run the application**:

    ```
    uvicorn app.main:app --reload
    ```

### Testing the API

To ensure the API works as expected, run the tests using `pytest`:

1.  **Install `pytest`**:

    ```
    pip install pytest
    ```

2.  **Execute the tests**:

    ```
    set PYTHONPATH=%cd%
    pytest
    ```

## Directory

```
MOVIE_API/
├── app/
│   ├── routers/
│   ├── tests/
│   ├── auth.py
│   ├── crud.py
│   ├── database.py
│   ├── logger.py
│   ├── main.py
│   ├── middleware.py
│   ├── models.py
│   ├── schemas.py
├── .env
├── .gitignore
├── README.md
├── requirements.txt
```

## Live Testing

https://capstone-main-nwii.onrender.com/docs#/
