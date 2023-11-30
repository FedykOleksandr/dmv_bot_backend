from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    is_notificated = db.Column(db.Boolean, default=False, nullable=False)
    branch_id = db.Column(db.String(120), nullable=True)

    def __repr__(self):
        return f'<Appointment {self.date} {self.time} {self.email} {self.is_notificated} {self.branch_id}>'
