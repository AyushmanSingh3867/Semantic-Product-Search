import os

import streamlit as st
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

indexName = "all_products"
elasticsearch_username = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
elasticsearch_password = os.getenv("ELASTICSEARCH_PASSWORD")

es = Elasticsearch(
    os.getenv("ELASTICSEARCH_URL", "https://localhost:9200"),
    basic_auth=(elasticsearch_username, elasticsearch_password)
    if elasticsearch_password
    else None,
    ca_certs=os.getenv("ELASTICSEARCH_CA_CERTS"),
)

if not es.ping():
    st.error("Could not connect to Elasticsearch. Check your connection settings.")
    st.stop()


def search(input_keyword):
    model = SentenceTransformer("all-mpnet-base-v2")
    vector_of_input_keyword = model.encode(input_keyword)

    query = {
        "field": "DescriptionVector",
        "query_vector": vector_of_input_keyword,
        "k": 10,
        "num_candidates": 500,
    }
    res = es.knn_search(
        index=indexName,
        knn=query,
        source=["ProductName", "Description"],
    )
    return res["hits"]["hits"]


def main():
    st.title("Search Myntra Fashion Products")
    search_query = st.text_input("Enter your search query")

    if st.button("Search"):
        if search_query:
            results = search(search_query)
            st.subheader("Search Results")
            for result in results:
                with st.container():
                    product = result.get("_source", {})
                    if product.get("ProductName"):
                        st.header(product["ProductName"])
                    if product.get("Description"):
                        st.write(f"Description: {product['Description']}")
                    st.divider()


if __name__ == "__main__":
    main()
