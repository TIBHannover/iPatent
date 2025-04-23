import copy

from backend.src import (
    index_service, encoder_service,
    cluster_service,
    lvlm_service
)

from shared.utils.common import load_config

config = load_config()

class Server:

    def __init__(self):
        self.index_service = index_service.IndexService()
        self.encoder_service = encoder_service.EncoderService()
        self.cluster_service = cluster_service.ClusterService()
        self.lvlm_service = lvlm_service.LVLMService(
            host_url=config['lvlm']['host_url'],
            model_name=config['lvlm']['model_name'],
            max_images=config['lvlm']['max_images']
        )
    
    def text_search(self, query, filters=None, limit=10):
        query_vector = self.encoder_service.get_encoded_text(query)
        return self.index_service.get_search_results(
                query_vector, filters, limit
            )

    def image_search(self, query, filters=None, limit=10):
        query_vector = self.encoder_service.get_encoded_image(query)
        return self.index_service.get_search_results(
                query_vector, filters, limit
            )

    def search(
        self, text_query=None, image_query=None,
        filters=None, limit=10, text_weight=0.5
    ):

        text_results, image_results = None, None

        if text_query:
            text_results = self.text_search(
                query=text_query, filters=filters, limit=limit
            )

        if image_query:
            image_results = self.image_search(
                query=image_query, filters=filters, limit=limit
            )

        if text_results and image_results:
            results = self.index_service.get_fused_results(
                text_results, image_results, text_weight, limit
            )
        else:
            results = text_results if text_results else image_results

        images = self.index_service.get_images_by_ids(
            image_ids=[sample['id'] for sample in results]
        )

        return [{
            'id': sample['id'],
            'rank': rank,
            'image': image,
            'patent': ''.join(sample['payload']['__key__'].split('_')[:-2]),
            'metadata': sample['payload'],
            'score': sample['score']
        } for rank, (image, sample) in enumerate(zip(images, results), start=1)]

    def cluster(self, results, model_name, n_clusters, top_k=10):
        
        top_k_results = results[:top_k]

        self.cluster_service.set_cluster_model(model_name, n_clusters)
        
        image_ids = [sample['id'] for sample in top_k_results]
        id_to_sample = {sample['id']: sample for sample in top_k_results}
        
        images = self.index_service.get_images_by_ids(
            image_ids=[sample['id'] for sample in top_k_results]
        )
        id_to_image = dict(zip(image_ids, images))

        clustered_results = self.cluster_service.get_cluster_groups(
            image_ids=image_ids, sample_dict=id_to_sample, image_dict=id_to_image
        )

        return clustered_results

    def generate_titles_and_desrciptions(self, clustered_results):
        
        cluster_contents = {}

        for cluster_id, cluster_group in clustered_results.items():

            cluster_contents[cluster_id] = self.lvlm_service.generate_cluster_content(
                cluster_samples=cluster_group['results']
            )
        
        return cluster_contents
