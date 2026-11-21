import importlib
import sys
import types
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd


class FakeModel:
    def __init__(self):
        self.batch_lengths = []

    def encode(self, texts, **kwargs):
        self.batch_lengths.append(len(texts))
        return np.ones((len(texts), 768), dtype=np.float32)


class IndexDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        elasticsearch = types.ModuleType("elasticsearch")
        elasticsearch.Elasticsearch = type("Elasticsearch", (), {})
        elasticsearch.ApiError = type("ApiError", (Exception,), {})
        elasticsearch.TransportError = type("TransportError", (Exception,), {})
        elasticsearch.helpers = types.SimpleNamespace(
            BulkIndexError=type("BulkIndexError", (Exception,), {})
        )

        sentence_transformers = types.ModuleType("sentence_transformers")
        sentence_transformers.SentenceTransformer = type(
            "SentenceTransformer", (), {}
        )

        dotenv = types.ModuleType("dotenv")
        dotenv.load_dotenv = lambda: None

        with patch.dict(
            sys.modules,
            {
                "elasticsearch": elasticsearch,
                "sentence_transformers": sentence_transformers,
                "dotenv": dotenv,
            },
        ):
            sys.modules.pop("elasticsearch_client", None)
            sys.modules.pop("indexData", None)
            cls.index_data = importlib.import_module("indexData")

    def test_bulk_actions_encode_every_record_across_batches(self):
        products = pd.DataFrame(
            {
                "ProductID": [11, 12, 13],
                "Description": ["first", "second", "third"],
            }
        )
        model = FakeModel()

        actions = list(
            self.index_data.iter_bulk_actions(products, model, batch_size=2)
        )

        self.assertEqual([action["_id"] for action in actions], ["11", "12", "13"])
        self.assertEqual(model.batch_lengths, [2, 1])
        self.assertTrue(
            all(
                len(action["_source"]["DescriptionVector"]) == 768
                for action in actions
            )
        )

    def test_load_products_reads_full_catalog_and_fills_missing_values(self):
        products = self.index_data.load_products()
        expected_row_count = len(pd.read_csv(self.index_data.DATA_PATH))

        self.assertEqual(len(products), expected_row_count)
        self.assertFalse(products.isna().any().any())
        self.assertEqual(products["ProductID"].nunique(), len(products))


if __name__ == "__main__":
    unittest.main()
