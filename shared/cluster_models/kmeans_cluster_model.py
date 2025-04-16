from sklearn.cluster import KMeans

from shared.cluster_models.base import BaseCluserModel
from shared.cluster_models.registry import ClusterModelsRegistry

@ClusterModelsRegistry.register('KMeans')
class KMeansClusterModel(BaseCluserModel):

    def __init__(self, k):
        super().__init__()
        self.k = k
        self.model = KMeans(
            n_clusters=self.k, random_state=1337, n_init='auto'
        )
    
    def cluster(self, image_vectors):
        return self.model.fit_predict(image_vectors)
