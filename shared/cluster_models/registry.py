class ClusterModelsRegistry:
    _cluster_models = {}

    @classmethod
    def register(cls, name):
        def inner_wrapper(wrapped_class):
            if name in cls._cluster_models:
                raise ValueError(f"Cluster model '{name}' already exists")
            cls._cluster_models[name] = wrapped_class
            return wrapped_class
        return inner_wrapper

    @classmethod
    def get_cluster_model(cls, name):
        if name not in cls._cluster_models:
            raise ValueError(f"Cluster model '{name}' not found")
        return cls._cluster_models[name]

    @classmethod
    def list_cluster_models(cls):
        return list(cls._cluster_models.keys())
