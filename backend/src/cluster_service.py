from collections import defaultdict

import torch

from shared.cluster_models.factory import ClusterModelFactory
from backend.src.index_service import IndexService

from shared.utils.common import load_config

config = load_config()

class ClusterService:

    def __init__(self):
        self.index_service = IndexService()
    
    def set_cluster_model(self, model_name, n_clusters):
        self.model = ClusterModelFactory.get_cluster_model(
            model_name=model_name, n_clusters=n_clusters
        )
    
    def get_cluster_groups(self, image_ids, sample_dict, image_dict):
        
        assert self.model != None, 'Cluster model not set!'

        id_vector_dict = self.index_service.get_vectors_by_ids(image_ids)
        vectors = [
            torch.tensor(v) if not isinstance(v, torch.Tensor) else v
            for v in id_vector_dict.values()
        ]

        cluster_labels = self.model.cluster(torch.stack(vectors))
        
        clustered_id_groups = defaultdict(list)
        for image_id, label in zip(id_vector_dict.keys(), cluster_labels):
            clustered_id_groups[label].append(image_id)

        clustered_results = {}

        for cluster_id, group in clustered_id_groups.items():

            results_in_cluster = []
            all_labels = []
            
            for image_id in group:

                sample = sample_dict[image_id]
                image = image_dict[image_id]

                labels_str = sample['metadata'].get('labels.txt', '')
                labels = labels_str.split('__SEP__') if labels_str else []
                all_labels.extend(label.strip() for label in labels if label.strip())

                results_in_cluster.append({
                    'id': image_id,
                    'image': image,
                    'patent': ''.join(sample['metadata']['__key__'].split('_')[:-2]),
                    'metadata': sample['metadata']
                })
            
            clustered_results[cluster_id] = {
                "results": results_in_cluster,
                "labels": list(set(all_labels))
            }
        
        return clustered_results