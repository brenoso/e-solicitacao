# ENEM Solicitação Spider

This repository contains a Scrapy spider used to retrieve ENEM results from the INEP portal.

## Environment variables

Create a `.env` file (use `.env_example` as a template) and define:

- `ENEM_LOGIN` – your login to the portal.
- `ENEM_PASSWORD` – the corresponding password.
- `ENEM_TARGET_REGISTRY` – optional enrollment number used for requests.
- `ENEM_TARGET_CPF` – optional CPF used for requests.
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

## API

This project also exposes a small FastAPI application that executes the spider
in a subprocess and returns the retrieved file content. Install the additional dependency
`fastapi` (and an ASGI server such as `uvicorn`) and run:

```bash
uvicorn api:app
```

Once running you can request the result with either a registry or a CPF and the year as query
parameters:

```bash
curl "http://localhost:8000/consulta?registry=151000163729&year=2015"

# ou utilizando CPF
curl "http://localhost:8000/consulta?cpf=12345678900&year=2015"
```

The endpoint will return the contents of the generated file directly as the
response body.


