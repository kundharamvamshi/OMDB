import os

class Config:
    # Secret & basic
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///omdb.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OMDB API (optional) - if you want to fetch details from OMDb API
    OMDB_API_KEY = os.getenv('OMDB_API_KEY', '596e3184')
  # set this in your env if you use OMDb
    OMDB_API_URL = "http://www.omdbapi.com/"

    # Pagination defaults
    DEFAULT_PER_PAGE = int(os.environ.get("PER_PAGE", 10))
