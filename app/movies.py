# this is the "app/movies.py" file...

import requests
import pandas as pd
import plotly.express as px

WIKIDATA_URL = "https://query.wikidata.org/sparql"

# Wikidata asks that programs identify themselves when making requests
HEADERS = {"User-Agent": "movie-studio-tracker/1.0 (student project)"}

# The Wikidata properties this program uses:
#   P272  = production company (which studio made the film)
#   P577  = publication date
#   P2142 = box office
#   P2130 = cost (the budget)
QUERY_TEMPLATE = """
SELECT ?filmLabel ?date ?boxoffice ?cost WHERE {
  ?company rdfs:label "STUDIO_NAME_HERE"@en .
  ?film wdt:P272 ?company .
  OPTIONAL { ?film wdt:P577 ?date . }
  OPTIONAL { ?film wdt:P2142 ?boxoffice . }
  OPTIONAL { ?film wdt:P2130 ?cost . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""


def format_usd(amount):
    """Formats a number as US dollars.

    Params:
        amount (float) like 1500000, or None if we don't have the number

    Returns a string like "$1,500,000", or "N/A" if there was no amount.
    """
    if amount is None or pd.isna(amount):
        return "N/A"
    return f"${amount:,.0f}"


def fetch_movies(studio):
    """Fetches a studio's movies from Wikidata.

    Params:
        studio (str) the name of a movie studio, like "A24"

    Returns a pandas DataFrame of the raw results, which may contain
    more than one row per movie.
    """
    # Take out any quote marks, because they would break the query
    safe_name = studio.replace('"', "")
    query = QUERY_TEMPLATE.replace("STUDIO_NAME_HERE", safe_name)

    response = requests.get(WIKIDATA_URL,
                            params={"query": query, "format": "json"},
                            headers=HEADERS,
                            timeout=60)
    response.raise_for_status()
    rows = response.json()["results"]["bindings"]

    # Wikidata wraps every value in a small dictionary, so unwrap them
    return pd.DataFrame([{key: value["value"] for key, value in row.items()}
                         for row in rows])


def clean_movies(raw):
    """Turns the raw Wikidata results into one tidy row per movie.

    A movie can appear on several rows, because Wikidata stores a separate
    release date and box office figure for each country. This keeps the
    earliest year and the largest money figures.

    Params:
        raw (DataFrame) the results from fetch_movies

    Returns a DataFrame with the columns: title, year, box_office, budget.
    """
    columns = ["title", "year", "box_office", "budget"]
    if len(raw) == 0:
        return pd.DataFrame(columns=columns)

    movies = raw.copy()

    # If no movie had a value, Wikidata leaves the column out completely
    for column in ["date", "boxoffice", "cost"]:
        if column not in movies.columns:
            movies[column] = None

    movies["boxoffice"] = pd.to_numeric(movies["boxoffice"], errors="coerce")
    movies["cost"] = pd.to_numeric(movies["cost"], errors="coerce")
    movies["year"] = movies["date"].str[:4]

    movies = (movies.groupby("filmLabel", as_index=False)
              .agg(year=("year", "min"),
                   box_office=("boxoffice", "max"),
                   budget=("cost", "max"))
              .rename(columns={"filmLabel": "title"})
              .sort_values("year", ascending=False))

    return movies[columns].reset_index(drop=True)


def get_studio_movies(studio):
    """Fetches and cleans a studio's movies in one step.

    Params:
        studio (str) the name of a movie studio, like "A24"

    Returns a tidy DataFrame with the columns: title, year, box_office, budget.
    """
    return clean_movies(fetch_movies(studio))


def count_by_year(movies):
    """Counts how many movies came out in each year.

    Params:
        movies (DataFrame) a tidy DataFrame from clean_movies

    Returns a DataFrame with the columns: year, movies.
    """
    counts = movies["year"].dropna().value_counts().sort_index()
    return pd.DataFrame({"year": counts.index, "movies": counts.values})


def summarize(movies, studio):
    """Prints a short summary of a studio's movies.

    Params:
        movies (DataFrame) a tidy DataFrame from clean_movies
        studio (str) the studio's name, used in the headings
    """
    total = len(movies)
    print(f"\nFound {total} movies produced by {studio}.")

    # Say how much of the data is actually filled in, so the numbers below
    # aren't mistaken for the whole picture
    have_money = movies["box_office"].notna().sum()
    print(f"{have_money} of them have a box office figure "
          f"({100 * have_money // total}%).")

    print("\nMost recent releases:\n")
    for _, movie in movies.head(10).iterrows():
        # some movies have no release date at all, so show a placeholder
        year = movie["year"] if pd.notna(movie["year"]) else "????"
        print(f"  {year}  {movie['title'][:40]:42} "
              f"box office: {format_usd(movie['box_office'])}")

    if have_money > 0:
        biggest = movies.loc[movies["box_office"].idxmax()]
        print(f"\nBiggest box office: {biggest['title']} "
              f"({format_usd(biggest['box_office'])})")


def make_chart(movies, studio):
    """Builds a bar chart of how many movies came out each year.

    Params:
        movies (DataFrame) a tidy DataFrame from clean_movies
        studio (str) the studio's name, used in the chart title

    Returns a plotly figure.
    """
    counts = count_by_year(movies)
    return px.bar(counts, x="year", y="movies",
                  title=f"{studio}: Movies Released per Year",
                  labels={"year": "Year", "movies": "Number of movies"},
                  height=450)


if __name__ == "__main__":

    studio = input("Please choose a movie studio (or press enter for A24): ")
    if not studio:
        studio = "A24"

    print(f"\nLooking up {studio}...")

    try:
        movies = get_studio_movies(studio)
    except requests.exceptions.RequestException:
        print("\nSorry, couldn't reach Wikidata. Please check your internet "
              "connection and try again.")
        raise SystemExit

    if len(movies) == 0:
        print(f"\nSorry, no movies found for {studio}.")
        print("Check the spelling, or try a studio like A24, Blumhouse "
              "Productions, or Pixar.")
        raise SystemExit

    summarize(movies, studio)

    filename = studio.lower().replace(" ", "_") + "_movies.csv"
    movies.to_csv(filename, index=False)
    print(f"\nSaved all {len(movies)} movies to {filename}")

    make_chart(movies, studio).show()
