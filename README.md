# VLDB Statistics Tool

[![Tokei](https://tokei.rs/b1/github/fabianhe/vldb)](https://tokei.rs)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This repository is based on initial work by Anna and [Magda Balazinska](https://www.cs.washington.edu/people/faculty/magda) for [VLDB 2020](https://vldb2020.org/).

## Organization

The project is structured into tables, insert, statistics and utility.

- The `tables` files are an ORM definition of the database tables.
- The `insert` files contain the logic of importing the CMT exports.
- The `statistics` files derive statistics as tables and plots from the data.
- The `utility` files contain other helpful queries.

### Required Data

Please export the following data:

- `people`: A single file containing all people participating
- `papers`: A single file containing all research tracks and revisions
- `reviews` A single file containing all reviews on all tracks and revisions
- `metareviews` A single file containing all metareviews on all tracks and revisions (if applicable)
- `seniormetareviews` A single file containing all seniormetareviews on all tracks and revisions (if applicable)
- `mapping` A single file containing special mappings from original submissions to revisions (if applicable)

Note that CMT exports `.xls` files.
Please convert them to `.xlsx` beforehand, for example by using Excel's "Save As ..." function.

### Statistics

1. Reviewers and ratings
   - Expertise Level vs Rating: `s01_01.py`
   - Acceptance Rate over Time: `s01_02.py`
   - Number of Submissions/Revisions over time: `s01_03.py`
   - Fraction of accepted or to be revised Papers per Paper Category: `s01_04.py`
2. Paper status
   - Status of papers per category: `s02_01.py`
   - Status of papers: `s02_02.py`
   - Status of papers per primary subject area: `s02_03.py`
   - Status of papers per number of authors: `s02_04.py`
3. Other
   - Number of papers per distinct affiliations (email domains): `s03_01.py`
   - Number of papers per country/region: `s03_02.py`
   - Number of accepted papers per email domain: `s03_03.py`
   - Number of papers per country/region (pie): `s03_04.py`

## Setup

This project uses Python version `3.9.1`.
We recommend using [`pyenv`](https://github.com/pyenv/pyenv) to manage your Python versions.

```bash
pyenv install 3.9.1
cd to-this-repo
pyenv local 3.9.1
exec "$SHELL"
python --version
# Python 3.9.1
python -m pip install --upgrade pip
```

For managing the Python environment, we use [Pipenv](https://github.com/pypa/pipenv).
Install it as follows:

```bash
python -m pip install --upgrade pipenv
```

Initialize your Pipenv environment:

```bash
python -m pipenv --python 3.9.1
```

Then, install the required python packages:

```bash
pipenv sync --dev
```

Additionally, we use [Black](https://github.com/psf/black) as a formatter ([nb-black](https://github.com/dnanhkhoa/nb_black) for notebooks), [Flake8](https://github.com/PyCQA/flake8) as a linter, and [Mypy](https://github.com/python/mypy) for static typing.
Please note that, depending on whether you use Jupyter Notebooks or Jupyter lab, nb-black requires either `%load_ext nb_black` or `%load_ext lab_black`.

For the PostgreSQL instance, you're free to connect any instance you already have in the `tables/__init__.py` connection string.
If you wish to setup PostgreSQL from scratch, we recommend a [Docker setup](https://hub.docker.com/_/postgres/).
