from db_config import db
from datetime import datetime


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    place_id = db.Column(db.Integer, nullable=False)
    place_name = db.Column(db.String(255), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    guests = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "place_id": self.place_id,
            "place_name": self.place_name,
            "booking_date": self.booking_date,
            "check_in_date": self.check_in_date,
            "check_out_date": self.check_out_date,
            "total_price": self.total_price,
            "guests": self.guests,
        }
