# CMTStat: CMT Statistics Tool

[![CI workflow](https://github.com/fabianhe/cmt_statistics_tool/actions/workflows/test.yaml/badge.svg)](https://github.com/fabianhe/cmt_statistics_tool/actions/workflows/test.yaml)
[![Tokei](https://tokei.rs/b1/github/fabianhe/cmt_statistics_tool)](https://tokei.rs)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

The conference management tool [CMT](https://cmt3.research.microsoft.com/), hosted by Microsoft Research, is a popular tool to manage submissions, the reviewing process, and camrea-ready-copy preparation for scientific conferences. CMT provides various CSV and XLS export capabilities about papers, reviewers, authors, etc.

The CMT Statistics Tool is a Python application and PostgreSQL database for importing such CMT data, deriving and plotting various statistics and running utility queries.
By harmonizing CMT exports into a common schema, it enables deep analysis of conference submissions.
Common use cases, such as viewing submissions by date, country, affiliation, or finding differences in acceptance rates over time are included.
The easiest way to get started using the CMT Statistics Tool for your conference is by forking this repository and going through the Setup below.

This repository is based on initial work by Anna and [Magda Balazinska](https://www.cs.washington.edu/people/faculty/magda) for [PVLDB](http://vldb.org/pvldb/) volume 13 and [VLDB 2020](https://vldb2020.org/).
It was extended and refined at [HPI](https://hpi.de/) for PVLDB volume 14 and [VLDB 2021](https://vldb.org/2021/). Its current form is intended to be as general as possible, but as each conference is different, slight adaptations will be necessary.

## Getting started

1. Fork this repository
2. Clone your repository
3. [Setup](#setup) your environment
4. [Customize your insert logic and table schema](#schema)
5. Import the [required data](#required-data)
6. Run the [statistics](#statistics) or utilities you are interested in

## Organization

The project is structured into tables, insert, statistics and utility.

- The [`tables`](cmt_statistics_tool/tables) files are an ORM definition of the database tables.
- The [`insert`](cmt_statistics_tool/insert) files contain the logic of importing the CMT exports.
- The [`statistics`](cmt_statistics_tool/statistics) files derive statistics as tables and plots from the data.
- The [`utility`](cmt_statistics_tool/utility) files contain other helpful queries.

### Required Data

Please export the following Excel data from CMT:

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
   - Expertise Level vs. Rating: [`s01_01.py`](cmt_statistics_tool/statistics/s01_01.py)
   - Acceptance Rate over Time: [`s01_02.py`](cmt_statistics_tool/statistics/s01_02.py)
   - Number of Submissions/Revisions over time: [`s01_03.py`](cmt_statistics_tool/statistics/s01_03.py)
   - Fraction of accepted or to be revised Papers per Paper Category: [`s01_04.py`](cmt_statistics_tool/statistics/s01_04.py)
2. Paper status
   - Status of papers per category: [`s02_01.py`](cmt_statistics_tool/statistics/s02_01.py)
   - Status of papers: [`s02_02.py`](cmt_statistics_tool/statistics/s02_02.py)
   - Status of papers per primary subject area: [`s02_03.py`](cmt_statistics_tool/statistics/s02_03.py)
   - Status of papers per number of authors: [`s02_04.py`](cmt_statistics_tool/statistics/s02_04.py)
3. Other
   - Number of papers per distinct affiliations (email domains): [`s03_01.py`](cmt_statistics_tool/statistics/s03_01.py)
   - Number of papers per country/region: [`s03_02.py`](cmt_statistics_tool/statistics/s03_02.py)
   - Number of accepted papers per email domain: [`s03_03.py`](cmt_statistics_tool/statistics/s03_03.py)
   - Number of papers per country/region (pie): [`s03_04.py`](cmt_statistics_tool/statistics/s03_04.py)

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

## Schema

If your export columns are named differently than the schema, you must change the [insert logic](cmt_statistics_tool/insert).
If you have additional columns or do not have some columns in your export, you must change the [insert logic](cmt_statistics_tool/insert) as well as the [table schema](cmt_statistics_tool/tables).
For each of the following files, a script dealing with the insert is in the [insert directory](cmt_statistics_tool/insert).
Currently, the schema of the required data is as follows:

- People: TSV file
  - First Name
  - Middle Initial (optional)
  - Last Name
  - E-mail
  - Organization
  - Country
  - Google Scholar
  - URL
  - Semantic Scholar URL
  - DBLP URL
  - Domain Conflicts
- Papers: XLSX file with multiple sheets. Sheet names correspond to track names, revision tracks have the Suffix "Revision".
  - Paper ID
  - Created
  - Last Modified
  - Paper Title
  - Abstract
  - Primary Contact Author Name
  - Primary Contact Author Email
  - Authors
  - Author Names
  - Author Emails
  - Track Name
  - Primary Subject Area
  - Secondary Subject Areas
  - Conflicts
  - Domains
  - Assigned
  - Completed
  - % Completed
  - Bids
  - Discussion
  - Status
  - Requested For Author Feedback
  - Author Feedback Submitted?
  - Requested For Camera Ready
  - Camera Ready Submitted?
  - Requested For Presentation
  - Files
  - Number of Files
  - Supplementary Files
  - Number of Supplementary Files
  - Reviewers
  - Reviewer Emails
  - MetaReviewers
  - MetaReviewer Emails
  - SeniorMetaReviewers
  - SeniorMetaReviewerEmails
  - Q1 (PVLDB does not allow papers previously rejected from PVLDB to be resubmitted within 12 months of the original submission date.)
  - Q3 (Conflict)
  - Q4 (Special category)
  - Q7 (Authors)
  - Q8 (Availability and Reproducibility)
- Reviews: XLSX file with multiple sheets. Sheet names correspond to track names, revision tracks have the Suffix "Revision".
  - Paper ID
  - Paper Title
  - Reviewer Name
  - Reviewer Email
  - Q1 (Overall Rating)
  - Q1 (Overall Rating - Value)
  - Q2 (Relevant for PVLDB)
  - Q3 (Are there specific revisions that could raise your overall rating?)
  - Q4 (Flavor of Regular Research Paper. Please indicate which flavor or flavors best describe the paper.)
  - Q5 (Summary of the paper (what is being proposed and in what context) and a brief justification of your overall recommendation. One solid paragraph.)
  - Q6 (Three (or more) strong points about the paper. Please be precise and explicit; clearly explain the value and nature of the contribution.)
  - Q7 (Three (or more) weak points about the paper. Please clearly indicate whether the paper has any mistakes, missing related work, or results that cannot be considered a contribution; write it so that the authors can understand what is seen as negative.)
  - Q8 (Novelty. Please give a high novelty ranking to papers on new topics, opening new fields, or proposing truly new ideas; assign medium ratings to delta papers and papers on well-known topics but still with some valuable contribution.)
  - Q9 (Significance)
  - Q10 (Technical Depth and Quality of Content)
  - Q11 (Experiments)
  - Q12 (Presentation)
  - Q13 (Detailed Evaluation (Contribution, Pros/Cons, Errors); please number each point and please provide as constructive feedback as possible.)
  - Q14 (Reproducibility. If the authors have provided supplemental material (data, code, etc.), is the information likely to be sufficient to understand and to reproduce the experiments? Otherwise, do the authors provide sufficient technical details in the paper to support reproducibility? Note that we do not expect actual reproducibility experiments, but rather a verification that the material is reasonable in scope and content.)
  - Q15 (Revision. If revision is required, list specific required revisions you seek from the authors. Please number each point.)
  - Q16 (Rate your confidence in this review.)
  - Q16 (Rate your confidence in this review. - Value)
  - Q17 (Confidential comments for the PC Chairs. Please add any information that may help us reach a decision.)
  - Q18 (Name and affiliation of external expert (!) reviewer (if applicable).)
  - Q19 (I understand that I am allowed to discuss a paper submission with a trainee for the purpose of teaching them how to review papers. I understand that (a) I am responsible to ensure that there is no COI according to the rules published at PVLDB.org between the trainee and any of the authors of the paper. (b) I have informed the trainee about the confidentiality of the content of the paper. (c) I am solely responsible for the final review. [If the trainee contributed significantly to the paper review, please list them above as external reviewer].)
- Metareviews: XLSX file with multiple sheets. Sheet names correspond to track names, revision tracks have the Suffix "Revision".
  - Paper ID
  - Paper Title
  - Meta-Reviewer Name
  - Meta-Reviewer Email
  - Q1 (Overall Rating)
  - Q1 (Overall Rating - Value)
  - Q2 (Summary Comments)
- Seniormetareviews: XLSX file with multiple sheets. Sheet names correspond to track names, revision tracks have the Suffix "Revision".
  - currently not used
- Mapping: XLSX file
  - Revision ID
  - OriginalSubmission ID
  - Revision Title
