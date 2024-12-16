from flask import Blueprint, request, jsonify, session
from models.book import Booking
from db_config import db

booking = Blueprint("booking", __name__)


@booking.route("/book", methods=["POST"])
def create_booking():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.json
    user_id = session["user_id"]
    place_id = data.get("place_id")
    place_name = data.get("place_name")

    if not all(
        [
            place_id,
            place_name,
            data.get("check_in_date"),
            data.get("check_out_date"),
            data.get("total_price"),
            data.get("guests"),
        ]
    ):
        return jsonify({"error": "Missing required booking details"}), 400

    try:
        new_booking = Booking(
            user_id=user_id,
            place_id=place_id,
            place_name=place_name,
            check_in_date=data["check_in_date"],
            check_out_date=data["check_out_date"],
            total_price=data["total_price"],
            guests=data["guests"],
        )
        db.session.add(new_booking)
        db.session.commit()
        return jsonify({"message": "Booking successful"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to book: {str(e)}"}), 500


@booking.route("/bookings", methods=["GET"])
def get_user_bookings():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]
    bookings = Booking.query.filter_by(user_id=user_id).all()
    bookings_list = [
        {
            "place_name": booking.place_name,
            "check_in_date": booking.check_in_date,
            "check_out_date": booking.check_out_date,
            "guests": booking.guests,
            "total_price": booking.total_price,
        }
        for booking in bookings
    ]
    return jsonify(bookings_list)



@booking.route("/bookings/<int:booking_id>", methods=["GET"])
def get_booking(booking_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    return jsonify(booking.to_dict()), 200
