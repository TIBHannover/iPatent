import umap
import torch

from backend.src.index_service import IndexService

class ProjectionService:

    def __init__(self, n_components=3, random_state=1337):
        self.index_service = IndexService()
        self.reducer = umap.UMAP(n_components=n_components, random_state=random_state)
    
    def project(self, clustered_results):
        
        all_ids = []
        all_vectors = []
        all_cluster_ids = []
        all_images = []
        all_patents = []

        for cluster_id, cluster_data in clustered_results.items():
            for result in cluster_data["results"]:
                all_ids.append(result["id"])
                all_images.append(result["image"])
                all_patents.append(result["patent"])
                all_cluster_ids.append(cluster_id)

        id_vector_dict = self.index_service.get_vectors_by_ids(all_ids)

        for image_id in all_ids:
            vector = id_vector_dict[image_id]
            vector = vector if isinstance(vector, torch.Tensor) else torch.tensor(vector)
            all_vectors.append(vector)

        all_vectors = torch.stack(all_vectors).numpy()
        embedding = self.reducer.fit_transform(all_vectors)

        projected_points = []
        for i, (x, y, z) in enumerate(embedding):
            projected_points.append({
                "id": all_ids[i],
                "image": all_images[i],
                "patent": all_patents[i],
                "x": x,
                "y": y,
                "z": z,
                "cluster": all_cluster_ids[i]
            })

        return projected_points