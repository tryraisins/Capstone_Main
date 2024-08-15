## TOOLS

- **Programming Language**: Python
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Authentication**: JWT (JSON Web Tokens)
- **ORM**: SQLAlchemy
- **Password Management**: Passlib
- **Hosting Platform**: Render
- **Testing Framework**: Pytest
- **API Documentation**: OpenAPI/Swagger
- **Environment Configuration**: python-dotenv

## Key Features

- **Secure Authentication**: Allows users to log in and register using JWT, with restricted actions based on authentication status.
- **Full CRUD Functionality**: Supports creating, reading, updating, and deleting movies, users, ratings, and comments.
- **Movie Management**: Users can add new movies, search for them by various criteria, and view detailed movie information.
- **Ratings and Reviews**: Users can rate and comment on movies, enhancing community interaction.
- **Efficient Querying**: The API supports advanced filtering, pagination, and searching to handle large amounts of data effectively.
- **Modular Design**: Leverages FastAPI’s dependency injection for a modular and maintainable codebase.
- **Comprehensive Logging**: Includes detailed logging and error handling to ensure smooth operation and easy troubleshooting.

## Applications

- **Movie Discovery Platforms**: Perfect for creating movie databases or platforms where users can explore and find movies.
- **Review Aggregators**: Ideal for services that compile and manage movie reviews and ratings.
- **Content Management Systems (CMS)**: Suitable for CMS applications focused on media content, particularly movies.

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

    Create a PostgreSQL database and set up the connection in the `.env` file:

    ```
    DATABASE_URL=your_database_url  # Replace with your database URL
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

## Project Directory

```
MOVIE_API/
├── .pytest_cache/
├── alembic/
├── app/
│   ├── __pycache__/
│   ├── routers/
│   ├── tests/
│   ├── config.py
│   ├── crud.py
│   ├── database.py
│   ├── logger.py
│   ├── main.py
│   ├── models.py
│   ├── auth.py
│   ├── schemas.py
│   ├── text.txt
│   ├── utils.py
├── .env
├── .gitignore
├── alembic.ini
├── README.md
├── requirements.txt
```
