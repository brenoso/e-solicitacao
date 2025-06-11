# ENEM Solicitação Spider

This repository contains a Scrapy spider used to retrieve ENEM results from the INEP portal.

## Environment variables

Create a `.env` file (use `.env_example` as a template) and define:

- `ENEM_LOGIN` – your login to the portal.
- `ENEM_PASSWORD` – the corresponding password.
- `ENEM_TARGET_REGISTRY` – optional enrollment number used for requests.
- `ENEM_YEAR` – optional year of the registry (e.g., `2015`).

## Running

Install the required packages, for example:

```bash
pip install scrapy python-dotenv
```

Then execute the spider:

```bash
scrapy crawl enem
```

The spider will authenticate using the variables above and will download the most recent result file, saving it as `resultado_registry_<number>_<year>.txt` (or `.csv`, depending on the portal).


