from shared.cluster_models.registry import ClusterModelsRegistry

class ClusterModelFactory:
    @staticmethod
    def get_cluster_model(model_name, n_clusters):
        model_class = ClusterModelsRegistry.get_cluster_model(name=model_name)
        return model_class(n_clusters)

    @staticmethod
    def list_available_cluster_models():
        return ClusterModelsRegistry.list_cluster_models()
