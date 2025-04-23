import streamlit as st
from shared.index.qdrant_index import QdrantIndex
from shared.index.minio_index import MinIOIndex
from shared.utils.common import load_config

config = load_config()

class IndexService:

    def __init__(self):
        self.qdrant_index = QdrantIndex(
        host=config['qdrant']['host'], port=config['qdrant']['port']
        )
        self.minio_index = MinIOIndex(
            endpoint=config['minio']['endpoint'],
            access_key=config['minio']['access_key'],
            secret_key=config['minio']['secret_key'],
            secure=False
        )
        self.collection_name = config['qdrant']['collection_name']

    def get_fused_results(self, text_results, image_results, text_weight=0.5, limit=10):

        text_results_dict = {result['id']: result['score'] for result in text_results}
        image_results_dict = {result['id']: result['score'] for result in image_results}

        fused_results = []
        all_ids = set(text_results_dict.keys()).union(image_results_dict.keys())

        for result_id in all_ids:
            text_score = text_results_dict.get(result_id, 0)
            image_score = image_results_dict.get(result_id, 0)

            combined_score = (text_weight * text_score) + ((1 - text_weight) * image_score)

            payload = next(
                (res['payload'] for res in (text_results + image_results) if res['id'] == result_id),
                {}
            )

            fused_results.append({
                'id': result_id,
                'score': combined_score,
                'payload': payload,
            })

        fused_results.sort(key=lambda x: x['score'], reverse=True)

        return fused_results[:limit]
    
    def get_search_results(self, query_vector, filters=None, limit=10):
        return self.qdrant_index.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            filters=filters
        )

    def get_vectors_by_ids(self, image_ids):
        return self.qdrant_index.get_vectors_by_ids(
            collection_name=self.collection_name,
            point_ids=image_ids
        )

    def get_images_by_ids(self, image_ids):
        return self.minio_index.fetch_all(
            bucket_name=config['minio']['bucket_name'],
            ids=image_ids
        )
