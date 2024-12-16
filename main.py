from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from flask_paginate import Pagination, get_page_parameter
import pandas as pd

from auth import auth
from db_config import init_db

# Flask app
app = Flask(__name__)
app.secret_key = "qwertyuioplkjhgfdsazxcvbnm"
init_db(app)

app.register_blueprint(auth, url_prefix='/auth')

# Load dataset
places_df = pd.read_csv("Tourist_Places_India.csv")
places_df = places_df.dropna(subset=["Rating"])  # Ensure no NaN values in 'Rating'
places_df["Rating"] = pd.to_numeric(places_df["Rating"], errors="coerce")  # Ensure numeric ratings


# Helper function to filter recommendations
def recommend_places(location=None, place_type=None, activity=None, season=None):
    filtered_df = places_df.copy()

    # Clean the data by stripping whitespace
    for column in ["Location", "Type", "Activities", "Best Season"]:
        if column in filtered_df:
            filtered_df[column] = filtered_df[column].str.strip()

    # Apply filters based on user input
    if location:
        filtered_df = filtered_df[
            filtered_df["Location"].str.contains(location.strip(), case=False, na=False)
        ]
    if place_type:
        filtered_df = filtered_df[
            filtered_df["Type"].str.contains(place_type.strip(), case=False, na=False)
        ]
    if activity:
        filtered_df = filtered_df[
            filtered_df["Activities"].str.contains(activity.strip(), case=False, na=False)
        ]
    if season:
        filtered_df = filtered_df[
            filtered_df["Best Season"].str.contains(season.strip(), case=False, na=False)
        ]

    return filtered_df


# Routes
@app.route("/")
def index():
    print(session)
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    trending_places = places_df.nlargest(10, "Rating").to_dict(orient="records")  # Top 10 by rating
    message = "Trending tourist places:"
    return render_template("index.html", recommendations=trending_places, message=message)


@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    recommendations = pd.DataFrame()
    pagination = None
    location = place_type = activity = season = None
    message = ""

    if request.method == "POST":
        # Get form data
        location = request.form.get("location")
        place_type = request.form.get("place_type")
        activity = request.form.get("activity")
        season = request.form.get("season")

        # If no input provided, show top 10 trending places
        if not (location or place_type or activity or season):
            recommendations = places_df.nlargest(10, "Rating")
            message = "Trending tourist places:"
        else:
            # Get recommendations
            recommendations = recommend_places(
                location=location,
                place_type=place_type,
                activity=activity,
                season=season,
            )

            # If no recommendations found, fallback to 10 random related places
            if recommendations.empty:
                recommendations = places_df.sample(5)
                message = "No exact matches found. But you may like:"
    else:
        # For GET requests, show trending places by default
        recommendations = places_df.nlargest(10, "Rating")
        message = "Trending tourist places:"

    # Pagination setup
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10  # Number of results per page
    offset = (page - 1) * per_page
    total = len(recommendations)

    # Paginated data
    paginated_recommendations = recommendations.iloc[offset : offset + per_page].to_dict(orient="records")
    pagination = Pagination(
        page=page,
        total=total,
        per_page=per_page,
        css_framework="bootstrap5",
        record_name="places",
        format_total=True,
        format_number=True,
    )

    return render_template(
        "index.html",
        recommendations=paginated_recommendations,
        pagination=pagination,
        location=location,
        place_type=place_type,
        activity=activity,
        season=season,
        message=message,
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)