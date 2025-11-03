from marshmallow import Schema, fields

class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str(required=True)
    year = fields.Str(allow_none=True)
    imdb_id = fields.Str(allow_none=True)
    created_at = fields.DateTime()

class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    is_admin = fields.Boolean()
    created_at = fields.DateTime()

class ActivitySchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    action = fields.Str()
    details = fields.Str()
    timestamp = fields.DateTime()
    # optional nested user
    user = fields.Nested(UserSchema, dump_only=True)
