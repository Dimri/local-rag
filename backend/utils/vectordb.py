import os
from typing import Any

import weaviate
from dotenv import load_dotenv
from tqdm import tqdm
from weaviate.classes.init import AdditionalConfig, Auth, Timeout
from weaviate.classes.query import MetadataQuery

from .embeddings import load_embedding_model

load_dotenv()
embedding_model = load_embedding_model()


def vectordb_client() -> weaviate.client.Client:
    weaviate_url = os.getenv("WEAVIATE_URL")
    weaviate_api_key = os.getenv("WEAVIATE_API_KEY")

    # Connect to Weaviate Cloud
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=weaviate_url,
        auth_credentials=Auth.api_key(weaviate_api_key),
        additional_config=AdditionalConfig(
            timeout=Timeout(init=30, query=60, insert=120)  # Values in seconds
        ),
    )
    print(f"{client.is_ready() = }")
    return client


def upload_documents(
    documents, collection: weaviate.collections.Collection
) -> list[str]:
    data_objects = []
    for doc in tqdm(documents):
        # metadata_with_only_headers = {k: v for k, v in doc.metadata.items() if k.startswith("header")}
        # Add each document to the batch
        properties = {
            "text": doc.page_content,
            "page_number": doc.metadata["page_number"],
        }
        data_object = weaviate.classes.data.DataObject(
            properties=properties,
            vector=doc.metadata["embedding"].tolist(),
        )
        data_objects.append(data_object)

    collection.data.insert_many(data_objects)
    print("Upload completed.")


def search_collection(
    query: str, collection: weaviate.collections.Collection, k: int = 5
) -> list[dict[str, Any]]:
    query_vector = embedding_model.encode(query)
    response = collection.query.hybrid(
        query=query,
        vector=query_vector,
        limit=k,
        return_metadata=MetadataQuery(distance=True),
    )
    result = [o.properties for o in response.objects]
    return result
