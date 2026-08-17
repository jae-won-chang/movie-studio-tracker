# Movie Studio Tracker

Type in the name of a movie studio and get back a table of every movie that studio produced —
with the release year, budget, and box office — plus a chart of how many movies they put out
each year.

All of this information is public, but it is spread across a lot of different movie websites,
and each one shows you only one movie at a time. This program collects it into one place.

The data comes from [Wikidata](https://www.wikidata.org/), the structured database behind
Wikipedia. **No API key is required**, so anyone can run this without signing up for anything.

## Setup

Clone the repo to download it from GitHub. Perhaps onto the Desktop.

Navigate to the repo using the command line.

```sh
cd ~/Desktop/movie-studio-tracker
```

Create a virtual environment:

```sh
conda create -n movies-env python=3.11
```

Activate the virtual environment:

```sh
conda activate movies-env
```

Install package dependencies:

```sh
pip install -r requirements.txt
```

## Configuration

**There is nothing to configure.** This program uses Wikidata, which needs no API key, no
account, and no payment. There are no credentials to store, so there is no ".env" file to
set up.

A ".env" file is still listed in the ".gitignore" file, so that if this project ever does
need a secret value, it cannot be committed to version control by accident.

## Usage

Run the program:

```sh
python -m app.movies
```

It will ask you for a studio name. Press enter to use A24, or type another one:

```
Please choose a movie studio (or press enter for A24): Blumhouse Productions
```

The program then:

1. prints how many movies it found, and how many of them actually have box office data
2. lists the ten most recent releases
3. names the studio's biggest box office hit
4. saves every movie to a CSV file, like `a24_movies.csv`
5. opens a bar chart in your browser showing movies released per year

### Example output

```
Please choose a movie studio (or press enter for A24): 

Looking up A24...

Found 54 movies produced by A24.
11 of them have a box office figure (20%).

Most recent releases:

  2028  Elden Ring                                 box office: N/A
  2026  Primetime                                  box office: N/A
  2025  The Legend of Ochi                         box office: N/A
  2025  André Is an Idiot                          box office: N/A
  2025  Highest 2 Lowest                           box office: N/A
  2025  Bring Her Back                             box office: N/A
  2025  Death of a Unicorn                         box office: N/A
  2025  Eddington                                  box office: N/A
  2024  Love Lies Bleeding                         box office: N/A
  2024  MaXXXine                                   box office: N/A

Biggest box office: Hereditary ($79,275,328)

Saved all 54 movies to a24_movies.csv
```

### Studios to try

`A24`, `Blumhouse Productions`, `Pixar`, `Ghibli`, `Legendary Entertainment`

If a studio name isn't found, the program says so and suggests trying a different spelling.

## Testing

Run the tests:

```sh
pytest
```

Most of the tests use fake data instead of calling Wikidata, so they run instantly and still
pass even if Wikidata is down. One test (`test_fetch_movies`) does make a real request, to
check that the Wikidata query itself still works.

The tests cover:

- formatting money, including movies that have no box office figure
- combining the duplicate rows Wikidata returns for each movie
- making sure missing data stays missing instead of turning into zero
- what happens when a studio name matches nothing
- counting movies per year
- building the chart

Tests also run automatically on GitHub Actions every time new code is pushed.

## Notes on the data

A few things I found out while building this, which are worth knowing before trusting the
numbers:

- **This only shows movies a studio *produced*, not ones it only distributed.** Wikidata's
  "production company" property is what links a film to a studio, so films that A24 released
  but did not make — like *Spring Breakers* — do not show up.
- **Only about a fifth of movies have a box office figure**, because Wikidata only knows what
  someone added to Wikipedia. The program prints this percentage so the numbers aren't mistaken
  for the whole picture, and movies with no data are kept in the table rather than deleted.
- **Box office figures may only cover one country.** Some are US-only totals rather than
  worldwide.
- **Films that haven't come out yet are included**, so the chart may show future years.
- Nothing here is adjusted for inflation, so old and new movies aren't directly comparable.

## License

[MIT](LICENSE)
