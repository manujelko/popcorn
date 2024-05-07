import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.dependencies import get_session
from app.main import create_app
from app.models import Movie


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app = create_app(enable_rate_limiter=False)
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_movie(client: TestClient):
    response = client.post(
        "/v1/movies", json={"title": "Moana", "year": 2016, "runtime": 107}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == 1
    assert data["title"] == "Moana"
    assert data["year"] == 2016
    assert data["runtime"] == 107


def test_create_movie_incomplete(client: TestClient):
    response = client.post("/v1/movies", json={"title": "Moana"})
    assert response.status_code == 422


def test_read_movies(session: Session, client: TestClient):
    movie_1 = Movie(title="Moana", year=2016, runtime=107)
    movie_2 = Movie(title="The Martian", year=2015, runtime=151)
    session.add(movie_1)
    session.add(movie_2)
    session.commit()

    response = client.get("/v1/movies")
    data = response.json()

    assert response.status_code == 200

    assert len(data) == 2
    assert data[0]["title"] == "Moana"
    assert data[0]["year"] == 2016
    assert data[0]["runtime"] == 107
    assert data[0]["id"] == movie_1.id
    assert data[1]["title"] == "The Martian"
    assert data[1]["year"] == 2015
    assert data[1]["runtime"] == 151
    assert data[1]["id"] == 2


def test_read_movie(session: Session, client: TestClient):
    movie = Movie(title="Moana", year=2016, runtime=107)
    session.add(movie)
    session.commit()

    response = client.get(f"/v1/movies/{movie.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == "Moana"
    assert data["year"] == 2016
    assert data["runtime"] == 107
    assert data["id"] == movie.id


def test_update_movie(session: Session, client: TestClient):
    movie = Movie(title="Moana", year=2015, runtime=107)
    session.add(movie)
    session.commit()

    response = client.patch(f"/v1/movies/{movie.id}", json={"year": 2016})
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == "Moana"
    assert data["year"] == 2016
    assert data["runtime"] == 107
    assert data["id"] == movie.id


def test_delete_movie(session: Session, client: TestClient):
    movie = Movie(title="Moana", year=2015, runtime=107)
    session.add(movie)
    session.commit()

    response = client.delete(f"/v1/movies/{movie.id}")

    movie_in_db = session.get(Movie, movie.id)

    assert response.status_code == 200
    assert movie_in_db is None
