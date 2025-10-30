from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta

# ---------------------------------
# App Configuration
# ---------------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key_here'
db = SQLAlchemy(app)
jwt = JWTManager(app)

# ---------------------------------
# Database Models
# ---------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100))
    year = db.Column(db.String(10))
    description = db.Column(db.Text)
    reviews = db.relationship('Review', backref='movie', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------------------------
# Routes
# ---------------------------------
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Online Movie Database API"}), 200


# ---------- USER AUTH ----------
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    hashed_pw = generate_password_hash(data['password'])
    new_user = User(username=data['username'], email=data['email'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401
    access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=2))
    return jsonify({"access_token": access_token}), 200


# ---------- MOVIE CRUD ----------
@app.route('/movies', methods=['POST'])
@jwt_required()
def add_movie():
    data = request.get_json()
    new_movie = Movie(
        title=data['title'],
        genre=data.get('genre'),
        year=data.get('year'),
        description=data.get('description')
    )
    db.session.add(new_movie)
    db.session.commit()
    return jsonify({"message": "Movie added successfully"}), 201


@app.route('/movies', methods=['GET'])
def get_movies():
    movies = Movie.query.all()
    movie_list = [{
        "id": m.id,
        "title": m.title,
        "genre": m.genre,
        "year": m.year,
        "description": m.description
    } for m in movies]
    return jsonify(movie_list), 200


@app.route('/movies/<int:id>', methods=['PUT'])
@jwt_required()
def update_movie(id):
    movie = Movie.query.get_or_404(id)
    data = request.get_json()
    movie.title = data.get('title', movie.title)
    movie.genre = data.get('genre', movie.genre)
    movie.year = data.get('year', movie.year)
    movie.description = data.get('description', movie.description)
    db.session.commit()
    return jsonify({"message": "Movie updated successfully"}), 200


@app.route('/movies/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_movie(id):
    movie = Movie.query.get_or_404(id)
    db.session.delete(movie)
    db.session.commit()
    return jsonify({"message": "Movie deleted successfully"}), 200


# ---------- REVIEWS ----------
@app.route('/movies/<int:movie_id>/reviews', methods=['POST'])
@jwt_required()
def add_review(movie_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    review = Review(
        content=data['content'],
        rating=data['rating'],
        user_id=user_id,
        movie_id=movie_id
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({"message": "Review added successfully"}), 201


@app.route('/movies/<int:movie_id>/reviews', methods=['GET'])
def get_reviews(movie_id):
    reviews = Review.query.filter_by(movie_id=movie_id).all()
    return jsonify([{
        "id": r.id,
        "content": r.content,
        "rating": r.rating,
        "user_id": r.user_id,
        "date_posted": r.date_posted
    } for r in reviews]), 200


@app.route('/reviews/<int:id>', methods=['PUT'])
@jwt_required()
def update_review(id):
    review = Review.query.get_or_404(id)
    data = request.get_json()
    review.content = data.get('content', review.content)
    review.rating = data.get('rating', review.rating)
    db.session.commit()
    return jsonify({"message": "Review updated successfully"}), 200


@app.route('/reviews/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_review(id):
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted successfully"}), 200


# ---------------------------------
# Run Server
# ---------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)