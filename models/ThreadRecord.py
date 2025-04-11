from db import db
from sqlalchemy import func


class ThreadRecord(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  #user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
  topic = db.Column(db.String(150), nullable=False)
  thread_id = db.Column(db.String(64), nullable=True)  # AI resource.
  created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
  deleted = db.Column(db.Boolean, nullable=False, default=False)

  def to_dict(self):
    return {
        "id": self.id,
        "topic": self.topic,
        "thread_id": self.thread_id,
        #"user_id": self.user_id
    }
