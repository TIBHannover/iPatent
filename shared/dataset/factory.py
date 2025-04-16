from shared.dataset.registry import DatasetRegistry

class DatasetFactory:
    @staticmethod
    def get_dataset(dataset_name, **kwargs):
        return DatasetRegistry.get_dataset(dataset_name, **kwargs)

    @staticmethod
    def list_available_datasets():
        return DatasetRegistry.list_datasets()
