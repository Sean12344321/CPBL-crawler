# CPBL crawler

**API** - For fetching data from the database.
**Crawler** - For inserting data into the database.

## Installation

### Set Up chromedriver

If the chromedriver version does not match your installed Chrome version, visit the official [Chromedriver page](https://sites.google.com/chromium.org/driver/downloads/version-selection?authuser=0) for the correct version

Instructions:
Find the version that matches your Chrome version (e.g., 130.\* for Chrome version 130.x.xxxx).
Download and unzip the file.
Replace the old chromedriver.exe in your project or PATH with the new one.

### Install Poetry and Project Dependencies

```bash
 pipx install poetry
 poetry install
```

## Usage

go to api folder

```bash
python -m main
```

(if want to insert data into DB)
go to crawler folder

```bash
python -m main
```
