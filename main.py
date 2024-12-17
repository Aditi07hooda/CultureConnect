from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from flask_paginate import Pagination, get_page_parameter
import pandas as pd

from auth import auth
from book import booking
from db_config import init_db

app = Flask(__name__)
app.secret_key = "qwertyuioplkjhgfdsazxcvbnm"
init_db(app)

app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(booking, url_prefix="/")

# Load dataset
places_df = pd.read_csv("Tourist_Places_India.csv")
places_df = places_df.dropna(subset=["Rating"])
places_df["Rating"] = pd.to_numeric(places_df["Rating"], errors="coerce")


# Helper function to filter recommendations
def recommend_places(
    site_name, place, location, activity, price, place_type, season, festival, ratings
):
    filtered_df = places_df.copy()

    # Clean the data by stripping whitespace
    for column in [
        "Location",
        "Type",
        "Activities",
        "Best Season",
        "name",
        "place",
        "festival",
    ]:
        if column in filtered_df:
            filtered_df[column] = filtered_df[column].str.strip()

    # Apply filters based on user input
    if site_name:
        filtered_df = filtered_df[
            filtered_df["name"].str.contains(site_name, case=False, na=False)
        ]
    if place:
        filtered_df = filtered_df[
            filtered_df["place"].str.contains(place, case=False, na=False)
        ]
    if location:
        filtered_df = filtered_df[
            filtered_df["Location"].str.contains(location, case=False, na=False)
        ]
    if activity:
        filtered_df = filtered_df[
            filtered_df["Activities"].str.contains(activity, case=False, na=False)
        ]
    if place_type:
        filtered_df = filtered_df[
            filtered_df["Type"].str.contains(place_type, case=False, na=False)
        ]
    if season:
        filtered_df = filtered_df[
            filtered_df["Best Season"].str.contains(season, case=False, na=False)
        ]
    if festival:
        filtered_df = filtered_df[
            filtered_df["festival"].str.contains(festival, case=False, na=False)
        ]
    if ratings:
        filtered_df = filtered_df[filtered_df["Rating"] >= float(ratings)]
    if price:
        filtered_df = filtered_df[
            filtered_df["price per night"] <= float(price)
        ]  # Changed to allow searching under budget

    return filtered_df


# Routes
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    trending_places = places_df.nlargest(10, "Rating").to_dict(orient="records")
    message = "Trending tourist places:"
    return render_template(
        "index.html", recommendations=trending_places, message=message
    )


@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    message = ""
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10

    if request.method == "POST":
        site_name = request.form.get("site_name")
        place = request.form.get("place")
        location = request.form.get("location")
        activity = request.form.get("activity")
        price = request.form.get("price")
        place_type = request.form.get("place_type")
        season = request.form.get("season")
        festival = request.form.get("festival")
        ratings = request.form.get("ratings")

        recommendations = recommend_places(
            site_name=site_name,
            place=place,
            location=location,
            activity=activity,
            price=price,
            place_type=place_type,
            season=season,
            festival=festival,
            ratings=ratings,
        )

        # Store only IDs in session for large data
        session["recommendation_ids"] = recommendations["place_id"].tolist()
        session["recommendation_message"] = "Results filtered successfully."

    recommendation_ids = session.get("recommendation_ids", [])
    message = session.get("recommendation_message", "")

    # Paginate based on stored IDs
    paginated_ids = recommendation_ids[(page - 1) * per_page : page * per_page]
    paginated_recommendations = places_df[
        places_df["place_id"].isin(paginated_ids)
    ].to_dict(orient="records")

    pagination = Pagination(
        page=page,
        total=len(recommendation_ids),
        per_page=per_page,
        css_framework="bootstrap5",
        record_name="places",
    )

    return render_template(
        "index.html",
        recommendations=paginated_recommendations,
        pagination=pagination,
        message=message,
    )


@app.route("/about")
def about():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("about.html")


@app.route("/contact")
def contact():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("contact.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/place/<int:place_id>")
def page_detail(place_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    place = places_df.loc[places_df["place_id"] == place_id].iloc[0]

    similar_places = (
        places_df[
            (places_df["Type"] == place["Type"]) & (places_df["place_id"] != place_id)
        ]
        .nlargest(4, "Rating")
        .to_dict(orient="records")
    )
    return render_template(
        "place_detail.html", place=place, similar_places=similar_places
    )


if __name__ == "__main__":
    app.run(debug=True)
