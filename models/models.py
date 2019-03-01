import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    email_id = db.Column(db.String(120), unique=True, nullable=False)
    date_created = db.Column(
        db.TIMESTAMP(timezone=True), nullable=False, default=datetime.datetime.utcnow
    )
    last_login = db.Column(db.TIMESTAMP(timezone=True))
    status = db.Column(db.Integer, nullable=False)
    user_permissions = db.relationship("UserPermissions ", backref="user", lazy=True)

    def __repr__(self):
        return f"Username: {self.username}"


class Permissions(db.Model):
    perm_id = db.Column(db.Integer, primary_key=True)
    perm_name = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    date_created = db.Column(
        db.TIMESTAMP(timezone=True), nullable=False, default=datetime.datetime.utcnow
    )

    def __repr__(self):
        return f"Permission: {self.perm_name}"


class UserPermissions(db.Model):
    uperm_id = db.Column(db.Integer, primary_key=True)
    perm_id = db.Column(db.Integer, db.ForeignKey("permissions.perm_id"), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.uid"), nullable=False)
    access_granted_on = db.Column(
        db.TIMESTAMP(timezone=True), nullable=False, default=datetime.datetime.utcnow
    )

    def __repr__(self):
        return f"Permission{self.perm_id}, User={self.user_id}"
