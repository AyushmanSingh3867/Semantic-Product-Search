import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()


def create_elasticsearch_client() -> Elasticsearch:
    username = os.getenv("ELASTICSEARCH_USERNAME")
    password = os.getenv("ELASTICSEARCH_PASSWORD")
    if bool(username) != bool(password):
        raise ValueError(
            "Set both ELASTICSEARCH_USERNAME and ELASTICSEARCH_PASSWORD, or neither."
        )

    return Elasticsearch(
        os.getenv("ELASTICSEARCH_URL", "https://localhost:9200"),
        basic_auth=(username, password) if username and password else None,
        ca_certs=os.getenv("ELASTICSEARCH_CA_CERTS"),
    )
