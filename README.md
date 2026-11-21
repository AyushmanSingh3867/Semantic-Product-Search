# Semantic Product Search

A semantic search demo for fashion product descriptions. It creates text embeddings with the `all-mpnet-base-v2` Sentence Transformers model, stores the vectors in Elasticsearch, and lets you search products from a Streamlit app using natural-language queries.

## How it works

1. The notebook reads the product catalog and encodes each description as a 768-dimensional vector.
2. Elasticsearch stores the product fields and description vectors in the `all_products` index.
3. The Streamlit app embeds a search query and retrieves the 10 nearest product descriptions.

## Project files

| File | Purpose |
| --- | --- |
| `searchApp.py` | Streamlit search interface |
| `indexData.ipynb` | Loads, embeds, and indexes catalog products |
| `indexMapping.py` | Elasticsearch mapping, including the vector field |
| `myntra_products_catalog.csv` | Product catalog used by the notebook |
| `requirements.txt` | Python dependencies |

## Requirements

- Python 3.9 or newer
- Elasticsearch 8.x, running locally or at a URL you can access
- A compatible Elasticsearch CA certificate when using HTTPS with a private/self-signed certificate

## Setup

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

In macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

Start Elasticsearch and set its connection details in the same terminal where you will run the app. In PowerShell:

```powershell
$env:ELASTICSEARCH_URL = "https://localhost:9200"
$env:ELASTICSEARCH_USERNAME = "elastic"
$env:ELASTICSEARCH_PASSWORD = "<your-elasticsearch-password>"
$env:ELASTICSEARCH_CA_CERTS = "C:\path\to\http_ca.crt"
```

`ELASTICSEARCH_CA_CERTS` can be omitted if your Elasticsearch endpoint uses a certificate trusted by your system. Do not put real passwords, certificates, or private keys in the repository.

## Index the catalog

The app searches an existing `all_products` index; it does not create or populate the index. To build it:

1. Start Jupyter from the project directory with `jupyter notebook`.
2. Open `indexData.ipynb` and run the cells in order.
3. The notebook reads the first 500 catalog rows, creates description embeddings, creates the Elasticsearch index, and indexes the records.

The notebook creates the index, so if it already exists, remove or rename it in Elasticsearch before running the indexing cells again.

## Run the search app

With Elasticsearch running and the index populated, start Streamlit:

```bash
python -m streamlit run searchApp.py
```

Open the local URL printed by Streamlit, enter a product query such as `blue running shoes`, and select **Search**.

## Configuration

| Environment variable | Default | Description |
| --- | --- | --- |
| `ELASTICSEARCH_URL` | `https://localhost:9200` | Elasticsearch endpoint |
| `ELASTICSEARCH_USERNAME` | `elastic` | Elasticsearch username |
| `ELASTICSEARCH_PASSWORD` | Empty | Elasticsearch password |
| `ELASTICSEARCH_CA_CERTS` | Unset | Path to the Elasticsearch CA certificate |

Set the same variables before running the notebook and the app.

## Data and usage

The included CSV contains third-party product catalog information. Check the dataset's source and redistribution terms before publishing or reusing it. Product names and descriptions are provided as sample data; this project is not affiliated with or endorsed by Myntra or the listed brands.

The Elasticsearch credentials and certificate paths are supplied through environment variables. If credentials previously used with this project were real, rotate them before publishing.
