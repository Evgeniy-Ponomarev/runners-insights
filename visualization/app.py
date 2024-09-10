"""
Athlete Dashboard Application

This script creates a Dash web application for visualizing athlete data based on age group and year.
It includes a dropdown to filter by year and age group, a bar chart, and a data table.
"""

import pandas as pd
import dash
from dash import Dash, Input, Output, dcc, html, dash_table
import warnings
import sqlite3

# Ignore future warnings
warnings.simplefilter(action="ignore", category=FutureWarning)
import plotly.express as px


# Load the dataset
conn = sqlite3.connect("../webparser/runners_db.db")
df = pd.read_sql_query("SELECT * FROM runners", conn)
conn.close()


def set_age_group(age):
    """
    Categorize athletes into age groups based on their age.

    Args:
        age (int): The age of the athlete.

    Returns:
        str: The age group the athlete falls into.
    """
    if age <= 20:
        return "0-20"
    elif 20 < age <= 30:
        return "20-30"
    elif 30 < age <= 40:
        return "30-40"
    elif 40 < age <= 50:
        return "40-50"
    else:
        return "50+"


# Calculate the age and age group for each athlete
df["age"] = df["run_year"] - df["Age_year"]
df["age_group"] = df["age"].apply(set_age_group)

# Aggregate data for the bar chart
df2 = df.groupby(["run_year", "age_group"]).size().reset_index(name="Count athletes")

# Columns to display in the data table
columns_to_display = [
    "Category",
    "Rang",
    "Fullname",
    "Age_year",
    "Location",
    "total_time",
    "run_link",
    "run_year",
]

# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the Dash app
app.layout = html.Div(
    [
        html.Div(children="Athletes"),
        # Dropdowns for selecting year and age group
        html.Div(
            [
                html.Label("Select Year(s):"),
                dcc.Dropdown(
                    id="year-dropdown",
                    options=[
                        {"label": str(year), "value": str(year)}
                        for year in df["run_year"].unique()
                    ],
                    multi=True,
                    placeholder="Select year(s)",
                ),
            ]
        ),
        html.Div(
            [
                html.Label("Select Age Group(s):"),
                dcc.Dropdown(
                    id="age-dropdown",
                    options=[
                        {"label": age_group, "value": age_group}
                        for age_group in df["age_group"].unique()
                    ],
                    multi=True,
                    placeholder="Select age group(s)",
                ),
            ]
        ),
        # Bar chart to display athletes per age group
        dcc.Graph(id="bar-chart"),
        # Data table to display filtered results
        dash_table.DataTable(
            id="table-data",
            columns=[{"name": col, "id": col} for col in columns_to_display],
            data=df.to_dict("records"),
            style_table={"overflowX": "scroll"},
            css=[{"selector": "tr:first-child", "rule": "display: none"}],
        ),
        html.Div(id="table-output"),
    ],
    style={"textAlign": "center", "margin": "5%"},
)


@app.callback(
    [Output("bar-chart", "figure"), Output("table-data", "data")],
    [Input("year-dropdown", "value"), Input("age-dropdown", "value")],
)
def update_chart_and_table(selected_years, selected_age_groups):
    """
    Update both the bar chart and the filtered data table based on selected year(s) and age group(s).

    Args:
        selected_years (list): List of selected years.
        selected_age_groups (list): List of selected age groups.

    Returns:
        tuple: A Plotly bar chart and a filtered table in dictionary format.
    """
    # Make copies of the data for filtering
    filtered_data = df.copy()
    filtered_bar_data = df2.copy()

    # Filter by selected years
    if selected_years:
        filtered_data = filtered_data[
            filtered_data["run_year"].astype(str).isin(selected_years)
        ]
        filtered_bar_data = filtered_bar_data[
            filtered_bar_data["run_year"].astype(str).isin(selected_years)
        ]

    # Filter by selected age groups
    if selected_age_groups:
        filtered_data = filtered_data[
            filtered_data["age_group"].isin(selected_age_groups)
        ]
        filtered_bar_data = filtered_bar_data[
            filtered_bar_data["age_group"].isin(selected_age_groups)
        ]

    # Create a bar chart with the filtered data
    bar_chart = px.bar(
        filtered_bar_data,
        x="run_year",
        y="Count athletes",
        color="age_group",
        title="Athletes per Age Group",
    )

    # Return the bar chart and the filtered table data
    return bar_chart, filtered_data.to_dict("records")


if __name__ == "__main__":
    app.run_server(debug=True)
    # app.run_server(host="0.0.0.0", port=8050)
