import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import string
import re
import sqlite3


def scrape_runners_data(years):
    """
    Scrape runners' data from the given URLs, process it into a DataFrame, and clean the data.

    The function iterates over the provided years and letters to build URLs dynamically, fetches
    the HTML content, and extracts runners' data. It organizes the data into a Pandas DataFrame,
    processes the age and year values, and performs cleaning on the dataset.

    Args:
        years (list): list of years to parse for.

    Returns:
        pd.DataFrame: A cleaned DataFrame with the runners' data.
    """
    columns = [
        "Category",
        "Rang",
        "Fullname",
        "Age_year",
        "Location",
        "total_time",
        "run_link",
        "run_year",
    ]
    df = pd.DataFrame(columns=columns)
    letters = list(string.ascii_lowercase)

    for year in years:
        for letter in letters:
            url = f"https://services.datasport.com/{year}/lauf/zuerich/alfa{letter}.htm"
            try:
                # Try making a GET request to the URL
                page = requests.get(url, timeout=10)
                page.raise_for_status()  # Raise HTTPError for bad responses (4xx, 5xx)
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err} - URL: {url}")
                continue  # Skip to the next URL in case of HTTP errors
            except requests.exceptions.ConnectionError as conn_err:
                print(f"Connection error occurred: {conn_err} - URL: {url}")
                continue  # Skip to the next URL in case of connection errors
            except requests.exceptions.Timeout as timeout_err:
                print(f"Timeout error occurred: {timeout_err} - URL: {url}")
                continue  # Skip to the next URL in case of timeouts
            except requests.exceptions.RequestException as req_err:
                print(f"General error occurred: {req_err} - URL: {url}")
                continue  # Skip to the next URL in case of any other request exceptions
            soup = BeautifulSoup(page.text, "html.parser")
            runners = [
                data.get_text()
                for data in soup.select("font")
                if 'font size="2"' in str(data)
            ]

            for runner in runners:
                try:
                    row = re.match(
                        r"(?P<Category>[^ ]+) +(?P<Rang>\d+|DNF|DSQ|OUT)\.? +(?P<Fullname>[^\d]+?) +(?P<Age_year>\d{4}|\?{4}) +"
                        r"(?P<Location>.*?) +(?P<total_time>[\d:.,]+)? +.*?[^ ] +\(\d+\)",
                        runner,
                    ).groupdict()
                except:
                    continue

                new_row = pd.DataFrame(
                    {
                        "Category": row["Category"],
                        "Rang": row["Rang"],
                        "Fullname": row["Fullname"],
                        "Age_year": row["Age_year"],
                        "Location": row["Location"],
                        "total_time": row["total_time"],
                        "run_link": url,
                        "run_year": int(year),
                    },
                    index=[0],
                )

                df = pd.concat([new_row, df.loc[:]]).reset_index(drop=True)

    return df


def clean_runners_data(df):
    """
    Clean the DataFrame by processing age data and filtering out invalid entries.

    Args:
        df (pd.DataFrame): The original DataFrame with runners' data.

    Returns:
        pd.DataFrame: A cleaned DataFrame with valid age data and unnecessary columns removed.
    """
    df["Age_year"] = pd.to_numeric(df["Age_year"], errors="coerce")
    df["Age_year"] = df["Age_year"].astype("Int64")
    df["run_year"] = df["run_year"].astype("Int64")

    # Calculate runners' age and filter out invalid age entries
    df["age"] = df["run_year"] - df["Age_year"]
    df = df[df["age"].notna() & (df["age"] > 0)]

    # Drop unnecessary columns and reset the index
    df = df.drop(columns=["age"]).reset_index(drop=True)

    return df


def save_to_csv(df, filename):
    """
    Save the cleaned DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): The cleaned DataFrame with runners' data.
        filename (str): The name of the CSV file.
    """
    df.to_csv(filename, index=False)


def save_to_sqlite(df, db_name, table_name):
    """
    Save the cleaned DataFrame to an SQLite database.

    Args:
        df (pd.DataFrame): The cleaned DataFrame with runners' data.
        db_name (str): The name of the SQLite database.
        table_name (str): The name of the table in the SQLite database.
    """
    conn = sqlite3.connect(db_name)

    # Create the table if it doesn't exist
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            Id INTEGER PRIMARY KEY,
            Category TEXT,
            Rang TEXT,
            Fullname TEXT,
            Age_year INTEGER,
            Location TEXT,
            total_time TEXT,
            run_link TEXT,
            run_year INTEGER
        );
    """
    )

    # Save the DataFrame to the SQLite table
    df.to_sql(table_name, conn, if_exists="replace", index=True, index_label="Id")
    conn.close()


def main():
    """
    Main function to orchestrate the data scraping, cleaning, and saving processes.

    It scrapes runners' data, cleans the dataset, and saves the results to both CSV and SQLite database.
    """
    years = ["2014", "2015", "2016", "2017", "2018"]
    # Scrape the data
    df = scrape_runners_data(years)

    # Clean the data
    df_cleaned = clean_runners_data(df)

    # Save to CSV and SQLite database
    save_to_csv(df_cleaned, "results.csv")
    save_to_sqlite(df_cleaned, "runners_db.db", "runners")


if __name__ == "__main__":
    main()
