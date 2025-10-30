from flask import Blueprint, request, jsonify
from .models import Movie, User, Review, db
from .schemas import MovieSchema, ReviewSchema, UserSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

movie_bp = Blueprint('movie_bp', __name__)
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
user_schema = UserSchema()
review_schema = ReviewSchema()
reviews_schema = ReviewSchema(many=True)

# ----------------- User Authentication -----------------
@movie_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"msg":"Username already exists"}),400
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)

@movie_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token)
    return jsonify({"msg": "Invalid credentials"}), 401

# ----------------- Movies -----------------
@movie_bp.route('/movies', methods=['POST'])
@jwt_required()
def add_movie():
    data = request.json
    new_movie = Movie(title=data['title'], description=data.get('description'), release_year=data.get('release_year'))
    db.session.add(new_movie)
    db.session.commit()
    return movie_schema.jsonify(new_movie)

@movie_bp.route('/movies', methods=['GET'])
def get_movies():
    movies = Movie.query.all()
    return movies_schema.jsonify(movies)

@movie_bp.route('/movies/<int:movie_id>', methods=['PUT'])
@jwt_required()
def update_movie(movie_id):
    data = request.json
    movie = Movie.query.get_or_404(movie_id)
    movie.title = data.get('title', movie.title)
    movie.description = data.get('description', movie.description)
    movie.release_year = data.get('release_year', movie.release_year)
    db.session.commit()
    return movie_schema.jsonify(movie)

@movie_bp.route('/movies/<int:movie_id>', methods=['DELETE'])
@jwt_required()
def delete_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return jsonify({"msg":"Movie deleted"})

# ----------------- Reviews -----------------
@movie_bp.route('/movies/<int:movie_id>/reviews', methods=['POST'])
@jwt_required()
def add_review(movie_id):
    data = request.json
    user_id = get_jwt_identity()
    movie = Movie.query.get_or_404(movie_id)
    review = Review(movie_id=movie.id, user_id=user_id, rating=data['rating'], comment=data['comment'])
    db.session.add(review)
    db.session.commit()
    return jsonify({"msg": "Review added!"})

@movie_bp.route('/movies/<int:movie_id>/reviews', methods=['GET'])
def get_reviews(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    reviews = Review.query.filter_by(movie_id=movie.id).all()
    return reviews_schema.jsonify(reviews)

# ----------------- Search / Filter / Sort -----------------
@movie_bp.route('/movies/search', methods=['GET'])
def search_movies():
    query = request.args.get('q','')
    movies = Movie.query.filter(Movie.title.ilike(f'%{query}%')).all()
    return movies_schema.jsonify(movies)

@movie_bp.route('/movies/filter', methods=['GET'])
def filter_movies():
    year = request.args.get('year')
    movies = Movie.query.filter_by(release_year=year).all()
    return movies_schema.jsonify(movies)

@movie_bp.route('/movies/sort', methods=['GET'])
def sort_movies():
    sort_by = request.args.get('by','title')
    if sort_by=='rating':
        movies = Movie.query.all()
        movies.sort(key=lambda m: m.average_rating(), reverse=True)
    elif sort_by=='year':
        movies = Movie.query.order_by(Movie.release_year.desc()).all()
    else:
        movies = Movie.query.order_by(Movie.title).all()
    return movies_schema.jsonify(movies)

# ----------------- Pagination -----------------
@movie_bp.route('/movies/page/<int:page>', methods=['GET'])
def paginated_movies(page):
    per_page = request.args.get('per_page',5,type=int)
    movies = Movie.query.paginate(page=page, per_page=per_page)
    return movies_schema.jsonify(movies.items)
