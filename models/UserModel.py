from flask.ext.login import UserMixin


class User(UserMixin):
    def __init__(self,user_tuple):
        self.id = user_tuple[0]
        self.password = user_tuple[1]

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False