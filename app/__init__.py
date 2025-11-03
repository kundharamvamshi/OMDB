import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# create extensions
db = SQLAlchemy()
migrate = Migrate()




def create_app(config_object=None):
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'), static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))


# Basic config - override by environment or pass config_object
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///omdb.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# init extensions
    db.init_app(app)
    migrate.init_app(app, db)


# register blueprints
    from .routes import movie_bp
    app.register_blueprint(movie_bp)


# create DB if not exists
    with app.app_context():
        db.create_all()


    return app