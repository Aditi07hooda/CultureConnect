from flask import Flask, request, render_template
from flask_paginate import Pagination, get_page_parameter
import pandas as pd

# Flask app
app = Flask(__name__)

# Load dataset
places_df = pd.read_csv("Tourist_Places_India.csv")


# Helper function to filter recommendations
def recommend_places(location=None, place_type=None, activity=None, season=None):
    filtered_df = (
        places_df.copy()
    )  # Use a copy to avoid modifying the original DataFrame

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
            filtered_df["Activities"].str.contains(
                activity.strip(), case=False, na=False
            )
        ]
    if season:
        filtered_df = filtered_df[
            filtered_df["Best Season"].str.contains(
                season.strip(), case=False, na=False
            )
        ]

    return filtered_df


# Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    recommendations = pd.DataFrame()
    pagination = None
    location = place_type = activity = season = None

    if request.method == "POST":
        # Get form data
        location = request.form.get("location")
        place_type = request.form.get("place_type")
        activity = request.form.get("activity")
        season = request.form.get("season")

        # Check if at least one field is provided
        if not (location or place_type or activity or season):
            message = "Please provide at least one filter (location, type, activity, or season)."
            return render_template("index.html", message=message)

        # Get recommendations
        recommendations = recommend_places(
            location=location, place_type=place_type, activity=activity, season=season
        )

    elif request.method == "GET":
        # Retain query parameters for pagination
        location = request.args.get("location")
        place_type = request.args.get("place_type")
        activity = request.args.get("activity")
        season = request.args.get("season")

        # Fetch recommendations again
        recommendations = recommend_places(
            location=location, place_type=place_type, activity=activity, season=season
        )

    # Pagination setup
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10  # Number of results per page
    offset = (page - 1) * per_page
    total = len(recommendations)

    # Paginated data
    paginated_recommendations = recommendations.iloc[offset : offset + per_page]
    pagination = Pagination(
        page=page,
        total=total,
        per_page=per_page,
        css_framework="bootstrap5",
        record_name="places",
        format_total=True,
        format_number=True,
    )

    # Convert paginated data to dictionary
    recommendation_list = paginated_recommendations.to_dict(orient="records")

    return render_template(
        "index.html",
        recommendations=recommendation_list,
        pagination=pagination,
        location=location,
        place_type=place_type,
        activity=activity,
        season=season,
    )


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
