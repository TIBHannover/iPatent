import re
from collections import (
    defaultdict, Counter, OrderedDict
)

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
    
    def select_cluster_terms(self, terms, max_terms=5):
        
        filtered_terms = [
            term for term in terms if bool(re.search(r'[a-zA-Z]', term))
        ]
        term_counts = Counter(filtered_terms)

        repeated_terms = [term for term, count in term_counts.items() if count > 1]

        if repeated_terms:
            selected = repeated_terms[:max_terms]
        else:
            selected = list(term_counts.keys())[:max_terms]

        return selected
    
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
            all_terms = []
            scores = []
            
            for image_id in group:

                sample = sample_dict[image_id]
                image = image_dict[image_id]

                terms_str = sample['metadata'].get('labels.txt', '')
                terms = terms_str.split('__SEP__') if terms_str else []
                all_terms.extend(term.strip() for term in terms if term.strip())

                scores.append(sample.get('score', 0.0))

                results_in_cluster.append({
                    'id': image_id,
                    'image': image,
                    'patent': ''.join(sample['metadata']['__key__'].split('_')[:-2]),
                    'metadata': sample['metadata'],
                    'score': sample.get('score', 0.0)
                })
            
            avg_score = sum(scores) / len(scores) if scores else 0.0

            clustered_results[cluster_id] = {
                'results': results_in_cluster,
                'terms': self.select_cluster_terms(all_terms),
                'avg_score': avg_score
            }
        
        return OrderedDict(
            sorted(
                clustered_results.items(),
                key=lambda x: x[1]['avg_score'],
                reverse=True
            )
        )