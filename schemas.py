from .init import ma
from .models import Movie, Review, User

class MovieSchema(ma.SQLAlchemyAutoSchema):
    average_rating = ma.Method("get_average_rating")
    class Meta:
        model = Movie
    def get_average_rating(self, obj):
        return obj.average_rating()

class ReviewSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Review

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
