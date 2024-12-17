import uuid
from flask import Blueprint, request, jsonify, session
from models.book import Booking
from db_config import db
from square.client import Client
import requests

booking = Blueprint("booking", __name__)

# Initialize Square client with access_token
client = Client(
    access_token="EAAAl23ne7q020DpjHvkl4DkeJZ6QAUxbNbsKjwbxel5-5z1LKJLH_zATcVNZVht",
    environment="sandbox",  # Use 'production' for live environment
)

def convert_inr_to_usd(inr_amount):
    usd_amount = inr_amount / 81.85
    print(usd_amount, inr_amount)
    return round(usd_amount, 2)

@booking.route("/book", methods=["POST"])
def create_booking():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.json
    user_id = session["user_id"]
    place_id = data.get("place_id")
    place_name = data.get("place_name")
    check_in_date = data.get("check_in_date")
    check_out_date = data.get("check_out_date")
    
    # Convert total_price to float
    total_price = float(data.get("total_price"))  # Ensure it's a float
    source_id = data.get("source_id")
    
    # Convert INR to USD
    usd_amount = convert_inr_to_usd(total_price)
    if usd_amount > 4000:  # Define your max limit in USD
        return jsonify({"error": "Amount exceeds the maximum allowed limit."}), 400

    if not all([place_id, place_name, check_in_date, check_out_date, total_price, source_id]):
        return jsonify({"error": "Missing required booking or payment details"}), 400

    try:
        amount_in_cents = int(usd_amount * 100)  # Convert to cents
        result = client.payments.create_payment(
            body={
                "source_id": source_id,
                "amount_money": {"amount": amount_in_cents, "currency": "USD"},
                "idempotency_key": str(uuid.uuid4()),
            }
        )

        if result.is_success():
            new_booking = Booking(
                user_id=user_id,
                place_id=place_id,
                place_name=place_name,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                total_price=total_price,
                guests=data.get("guests", 1),
            )
            db.session.add(new_booking)
            db.session.commit()
            return jsonify({"message": "Booking successful"}), 201

        elif result.is_error():
            return jsonify({"error": result.errors}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Payment or booking failed: {str(e)}"}), 500

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