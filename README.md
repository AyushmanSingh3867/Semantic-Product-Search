# Semantic Product Search

A semantic search demo for fashion products. Product descriptions are embedded with the `all-mpnet-base-v2` Sentence Transformers model, indexed as 768-dimensional vectors in Elasticsearch, and searched through a Streamlit app.

## Project structure

```text
Semantic-Product-Search/
├── app.py
├── indexData.py
├── elasticsearch_client.py
├── indexMapping.py
├── requirements.txt
├── .env.example
└── data/
    └── myntra_products_catalog.csv
```

## Requirements

- Python 3.9 or newer
- Elasticsearch 8.x
- A compatible CA certificate when using HTTPS with a private or self-signed certificate

## Setup

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

On macOS or Linux, activate the virtual environment and copy the example file with:

```bash
source .venv/bin/activate
cp .env.example .env
```

Edit `.env` with your Elasticsearch URL, username, password, and CA certificate path. The app and indexing script load these settings automatically. If your Elasticsearch server does not require authentication, leave both username and password unset. Do not commit `.env`, passwords, or certificate files.

## Build the Elasticsearch index

Start Elasticsearch, then run:

```bash
python indexData.py
```

The script reads the entire catalog, fills missing values, generates description embeddings in batches, creates the `all_products` index, and bulk-indexes the products. The model is downloaded the first time it runs.

The script will not overwrite an existing index. If you need to re-index, remove the existing `all_products` index from Elasticsearch first.

## Run the app

```bash
python -m streamlit run app.py
```

Open the local URL printed by Streamlit and search for products with a natural-language query, such as `blue running shoes`. Streamlit caches the embedding model so it is not reloaded on each search.

## Configuration

| Variable | Description |
| --- | --- |
| `ELASTICSEARCH_URL` | Elasticsearch endpoint (default: `https://localhost:9200`) |
| `ELASTICSEARCH_USERNAME` | Elasticsearch username |
| `ELASTICSEARCH_PASSWORD` | Elasticsearch password |
| `ELASTICSEARCH_CA_CERTS` | Path to the Elasticsearch CA certificate; omit for system-trusted certificates |

Set both username and password, or leave both unset.

## Data and usage

The included CSV contains third-party product catalog information. Verify its source and redistribution terms before publishing or reusing it. Product names and descriptions are provided as sample data; this project is not affiliated with or endorsed by Myntra or the listed brands.

If any Elasticsearch credentials previously used with this project were real, rotate them.
