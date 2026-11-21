from pathlib import Path
from typing import Iterator

import pandas as pd
from elasticsearch import ApiError, Elasticsearch, TransportError, helpers
from sentence_transformers import SentenceTransformer

from elasticsearch_client import create_elasticsearch_client
from indexMapping import INDEX_NAME, indexMapping

DATA_PATH = Path(__file__).parent / "data" / "myntra_products_catalog.csv"
BATCH_SIZE = 128
BULK_CHUNK_SIZE = 500
MODEL_NAME = "all-mpnet-base-v2"


def load_products(csv_path: Path = DATA_PATH) -> pd.DataFrame:
    products = pd.read_csv(csv_path).fillna("None")
    if products.empty:
        raise ValueError(f"No products found in {csv_path}.")
    if "ProductID" not in products or "Description" not in products:
        raise ValueError("The catalog must include ProductID and Description columns.")
    if products["ProductID"].duplicated().any():
        raise ValueError("ProductID values must be unique for indexing.")
    return products


def iter_bulk_actions(
    products: pd.DataFrame,
    model: SentenceTransformer,
    batch_size: int = BATCH_SIZE,
) -> Iterator[dict]:
    for start in range(0, len(products), batch_size):
        batch = products.iloc[start : start + batch_size]
        descriptions = batch["Description"].astype(str).tolist()
        vectors = model.encode(
            descriptions,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
        ).tolist()
        if len(vectors) != len(batch):
            raise ValueError(
                "The embedding model returned an unexpected number of vectors."
            )

        for record, vector in zip(batch.to_dict("records"), vectors):
            record["DescriptionVector"] = vector
            yield {
                "_op_type": "index",
                "_index": INDEX_NAME,
                "_id": str(record["ProductID"]),
                "_source": record,
            }


def index_catalog(es: Elasticsearch, csv_path: Path = DATA_PATH) -> int:
    products = load_products(csv_path)
    if es.indices.exists(index=INDEX_NAME):
        raise ValueError(
            f"Index {INDEX_NAME!r} already exists. Delete it before re-indexing."
        )

    model = SentenceTransformer(MODEL_NAME)
    es.indices.create(index=INDEX_NAME, mappings=indexMapping)
    indexed_count, _ = helpers.bulk(
        es,
        iter_bulk_actions(products, model),
        chunk_size=BULK_CHUNK_SIZE,
    )
    return indexed_count


def main() -> None:
    try:
        es = create_elasticsearch_client()
        if not es.ping():
            raise ConnectionError(
                "Could not connect to Elasticsearch. Check your connection settings."
            )
        indexed_count = index_catalog(es)
    except helpers.BulkIndexError as error:
        raise SystemExit(
            f"Indexing failed for {len(error.errors)} product(s). "
            "Inspect the Elasticsearch bulk errors before retrying."
        ) from error
    except (ApiError, TransportError, OSError, ValueError) as error:
        raise SystemExit(f"Indexing failed: {error}") from error
    finally:
        if "es" in locals():
            es.close()

    print(f"Indexed {indexed_count} products into {INDEX_NAME!r}.")


if __name__ == "__main__":
    main()
