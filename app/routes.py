from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, current_app
from . import db
from .models import User, Movie, Activity
import hashlib


movie_bp = Blueprint('movie', __name__)


### FRONTEND ROUTES (render HTML) ###
@movie_bp.route('/')
def home():
    return render_template('index.html')


@movie_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template('login.html')
    # POST -> authenticate
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return render_template('login.html', error='Provide username and password')
    hashed = hashlib.sha256(password.encode()).hexdigest()
    user = User.query.filter_by(username=username, password=hashed).first()
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
    # record activity
        db.session.add(Activity(user_id=user.id, action='login', details='User logged in'))
        db.session.commit()
        return redirect(url_for('movie.home'))
    return render_template('login.html', error='Invalid credentials')


@movie_bp.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'GET':
        return render_template('signup.html')
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return render_template('signup.html', error='Provide username and password')
    if User.query.filter_by(username=username).first():
        return render_template('signup.html', error='Username taken')
    hashed = hashlib.sha256(password.encode()).hexdigest()
    user = User(username=username, password=hashed, is_admin=False)
    db.session.add(user)
    db.session.commit()
    db.session.add(Activity(user_id=user.id, action='signup', details='User signed up'))
    db.session.commit()
    session['user_id'] = user.id
    session['username'] = user.username
    session['is_admin'] = user.is_admin
    return redirect(url_for('movie.home'))


@movie_bp.route('/logout')
def logout():
    user_id = session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    if user_id:
        db.session.add(Activity(user_id=user_id, action='logout', details='User logged out'))
        db.session.commit()
    return redirect(url_for('movie.home'))


@movie_bp.route('/admin')
def admin_page():
# simple guard
    if not session.get('is_admin'):
        return redirect(url_for('movie.login_page'))
    users = User.query.order_by(User.created_at.desc()).all()
    activities = Activity.query.order_by(Activity.timestamp.desc()).limit(200).all()
    return render_template('admin.html', users=users, activities=activities)




### API routes (JSON) ###
@movie_bp.route("/api/movies/search")
def search_movies_api():
    import requests
    from flask import request, jsonify
    from config import Config

    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Missing query"}), 400

    url = f"http://www.omdbapi.com/?s={query}&apikey={Config.OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "Search" not in data:
        return jsonify({"error": data.get("Error", "No results found")}), 404

    movies = []
    for item in data["Search"]:
        imdb_id = item.get("imdbID")
        # Fetch detailed info for each movie
        detail_url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={Config.OMDB_API_KEY}"
        detail_res = requests.get(detail_url)
        detail_data = detail_res.json()

        movies.append({
            "title": detail_data.get("Title"),
            "year": detail_data.get("Year"),
            "imdb_rating": detail_data.get("imdbRating"),
            "plot": detail_data.get("Plot"),
            "actors": detail_data.get("Actors"),
            "poster": detail_data.get("Poster"),
            "imdb_id": imdb_id
        })

    return jsonify({"items": movies})




@movie_bp.route('/api/movies', methods=['GET'])
def api_list_movies():
    movies = Movie.query.limit(100).all()
    return jsonify([{'id': m.id, 'title': m.title, 'year': m.year, 'imdb_id': m.imdb_id} for m in movies])


# endpoint to add movie to DB (admin or special usage)
@movie_bp.route('/api/movies', methods=['POST'])
def api_add_movie():
    data = request.json or {}
    title = data.get('title')
    imdb_id = data.get('imdb_id')
    if not title:
        return jsonify({'error': 'title required'}), 400
    movie = Movie(title=title, year=data.get('year'), imdb_id=imdb_id)
    db.session.add(movie)
    db.session.commit()
    return jsonify({'id': movie.id, 'title': movie.title}), 201


# -------------------- FRONTEND MOVIE SEARCH PAGE --------------------

import requests
from config import Config  # make sure config.py exists and has OMDB_API_KEY

@movie_bp.route('/search', methods=['GET', 'POST'])
def search_movies():
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if not query:
            return render_template('search.html', error='Please enter a movie name')

        # Fetch from OMDb API
        api_key = Config.OMDB_API_KEY
        url = f'https://www.omdbapi.com/?apikey={api_key}&s={query}'
        response = requests.get(url)

        if response.status_code != 200:
            return render_template('search.html', error='Failed to connect to movie API')

        data = response.json()
        if data.get('Response') == 'True':
            movies = data.get('Search', [])
            return render_template('search.html', movies=movies, query=query)
        else:
            return render_template('search.html', error='No movies found for your search.')

    return render_template('search.html')
