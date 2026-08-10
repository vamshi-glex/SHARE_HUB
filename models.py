from extensions import db


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    text = db.Column(db.Text, default="")
    edit_locked = db.Column(db.Boolean, default=False)