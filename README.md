# ENEM Solicitação Spider

This repository contains a Scrapy spider used to retrieve ENEM results from the INEP portal.

## Environment variables

Create a `.env` file (use `.env_example` as a template) and define:

- `ENEM_LOGIN` – your login to the portal.
- `ENEM_PASSWORD` – the corresponding password.
- `ENEM_TARGET_REGISTRY` – optional enrollment number used for requests.
- `ENEM_YEAR` – optional year of the registry (e.g., `2015`).

## Running the spider

Install the required packages using `requirements.txt`:

```bash
pip install -r requirements.txt
```

Then execute the spider directly:

```bash
scrapy crawl enem
```

The spider will authenticate using the variables above and stores the retrieved result in memory (attribute `result_content`). No file is saved.

## REST API

You can also run the spider through a small API. Start the server:

```bash
uvicorn api:app --reload
```

Send a POST request to `/consulta` providing the credentials and optional parameters in JSON:

```json
{
  "login": "seu_login",
  "password": "sua_senha",
  "registry": "123456789012",
  "year": "2015"
}
```

Any parameter omitted will fall back to the value from the environment.

The API response will contain the text that would normally be saved to a file.

## REST API

You can also run the spider through a small API. Start the server:

```bash
uvicorn api:app --reload
```

Send a POST request to `/consulta` providing the credentials and optional parameters in JSON:

```json
{
  "login": "seu_login",
  "password": "sua_senha",
  "registry": "123456789012",
  "year": "2015"
}
```

Any parameter omitted will fall back to the value from the environment.


