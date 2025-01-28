from . import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    archived = db.Column(db.Boolean, default=False)
    archived_at = db.Column(db.DateTime)
    points = db.Column(db.Integer, default=0)
    task_type = db.Column(db.String(10), default='regular')  # 'mit' or 'regular'
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DailyXP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    xp_earned = db.Column(db.Integer, default=0)
    
    @classmethod
    def add_xp(cls, points, date=None):
        if date is None:
            date = datetime.utcnow().date()
        daily_xp = cls.query.filter_by(date=date).first()
        if daily_xp:
            daily_xp.xp_earned += points
        else:
            daily_xp = cls(date=date, xp_earned=points)
            db.session.add(daily_xp)
        db.session.commit()
        return daily_xp
