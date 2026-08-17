# this is the "test/movies_test.py" file...

import pandas as pd

from app.movies import (format_usd, clean_movies, count_by_year,
                        make_chart, fetch_movies)


# Some fake Wikidata results to test with. Using fake data means most of
# these tests run without making any network requests, so they are fast
# and they don't depend on Wikidata being up.
FAKE_RESULTS = pd.DataFrame([
    # this movie appears twice, because Wikidata stores box office per country
    {"filmLabel": "Moonlight", "date": "2016-09-02T00:00:00Z",
     "boxoffice": "27854932", "cost": "1500000"},
    {"filmLabel": "Moonlight", "date": "2016-10-21T00:00:00Z",
     "boxoffice": "65300000", "cost": "1500000"},
    # this one has no box office and no budget
    {"filmLabel": "Into the Forest", "date": "2015-01-01T00:00:00Z",
     "boxoffice": None, "cost": None},
])


def test_format_usd():
    assert format_usd(1500000) == "$1,500,000"
    assert format_usd(0) == "$0"
    assert format_usd(27854932.0) == "$27,854,932"


def test_format_usd_handles_missing_amounts():
    # movies with no box office should say "N/A" instead of crashing
    assert format_usd(None) == "N/A"
    assert format_usd(float("nan")) == "N/A"


def test_clean_movies():
    movies = clean_movies(FAKE_RESULTS)

    # the two Moonlight rows should be combined into one
    assert len(movies) == 2
    assert list(movies.columns) == ["title", "year", "box_office", "budget"]

    moonlight = movies[movies["title"] == "Moonlight"].iloc[0]
    assert moonlight["year"] == "2016"
    assert moonlight["box_office"] == 65300000    # keeps the larger figure
    assert moonlight["budget"] == 1500000


def test_clean_movies_keeps_missing_data_missing():
    # a movie with no box office should stay blank, NOT become zero,
    # otherwise it would drag down any average
    movies = clean_movies(FAKE_RESULTS)

    forest = movies[movies["title"] == "Into the Forest"].iloc[0]
    assert pd.isna(forest["box_office"])
    assert pd.isna(forest["budget"])


def test_clean_movies_with_no_results():
    # if a studio name matches nothing, the program should return an empty
    # table rather than crash
    movies = clean_movies(pd.DataFrame())

    assert len(movies) == 0
    assert list(movies.columns) == ["title", "year", "box_office", "budget"]


def test_count_by_year():
    movies = pd.DataFrame({
        "title": ["A", "B", "C", "D"],
        "year": ["2020", "2021", "2021", None],
        "box_office": [None, None, None, None],
        "budget": [None, None, None, None],
    })

    counts = count_by_year(movies)

    assert list(counts["year"]) == ["2020", "2021"]
    assert list(counts["movies"]) == [1, 2]


def test_make_chart():
    figure = make_chart(clean_movies(FAKE_RESULTS), "A24")

    assert figure.layout.title.text == "A24: Movies Released per Year"


def test_fetch_movies():
    # this is the only test that uses the internet, to check that the
    # Wikidata query still works
    raw = fetch_movies("A24")

    assert isinstance(raw, pd.DataFrame)
    assert len(raw) > 0
    assert "filmLabel" in raw.columns
