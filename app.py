import streamlit as st
from elasticsearch import ApiError, Elasticsearch, TransportError
from sentence_transformers import SentenceTransformer

from elasticsearch_client import create_elasticsearch_client
from indexMapping import INDEX_NAME


@st.cache_resource
def load_model() -> SentenceTransformer:
    return SentenceTransformer("all-mpnet-base-v2")


def search(es: Elasticsearch, input_keyword: str) -> list[dict]:
    vector = load_model().encode(input_keyword).tolist()
    query = {
        "field": "DescriptionVector",
        "query_vector": vector,
        "k": 10,
        "num_candidates": 500,
    }
    response = es.knn_search(
        index=INDEX_NAME,
        knn=query,
        source=["ProductName", "Description"],
    )
    return response["hits"]["hits"]


def main():
    st.title("Search Myntra Fashion Products")

    try:
        es = create_elasticsearch_client()
        if not es.ping():
            st.error(
                "Could not connect to Elasticsearch. Check your connection settings."
            )
            st.stop()
    except (ApiError, TransportError, OSError, ValueError) as error:
        st.error(f"Could not connect to Elasticsearch: {error}")
        st.stop()

    search_query = st.text_input("Enter your search query")

    if st.button("Search"):
        if not search_query.strip():
            st.warning("Enter a search query.")
            return

        try:
            results = search(search_query)
        except (ApiError, TransportError, OSError, ValueError) as error:
            st.error(f"Search failed: {error}")
            return

        if not results:
            st.info("No matching products found.")
            return

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
