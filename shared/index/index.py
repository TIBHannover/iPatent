import logging

from shared.index.qdrant_index import QdrantIndex
from shared.index.minio_index import MinIOIndex
from shared.dataset.factory import DatasetFactory
from shared.dataset.loader import DataLoader
from shared.encoders.factory import EncoderFactory

from shared.utils.common import load_config
from shared.utils.image import preprocess

logging.basicConfig(
    filename='logs/index.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    filemode='w'
)

logger = logging.getLogger(__name__)

def index():
    
    config = load_config()

    model = EncoderFactory.get_encoder(config['encoder']['name'])

    qdrant_index = QdrantIndex(
        host=config['qdrant']['host'], port=config['qdrant']['port']
    )
    
    minio_index = MinIOIndex(
        endpoint=config['minio']['endpoint'],
        access_key=config['minio']['access_key'],
        secret_key=config['minio']['secret_key'],
        secure=False
    )

    collection_name = config['qdrant']['collection_name']
    bucket_name=config['minio']['bucket_name']
    dataset_name = config['dataset']['dataset_name']
    
    # for collection_name in qdrant_index.list_collections():
    #     qdrant_index.delete_collection(collection_name=collection_name)
    
    if not qdrant_index.collection_exits(collection_name=collection_name):

        qdrant_index.create_collection(collection_name, vector_size=config['qdrant']['dim'])
        logger.info(f"Collection '{collection_name}' created successfully.")

        if not minio_index.bucket_exists(bucket_name=bucket_name):
            minio_index.create_bucket(bucket_name=bucket_name)
            logger.info(f"Bucket '{bucket_name}' created successfully.")

        dataset = DatasetFactory.get_dataset(
            dataset_name, shards_url=config['dataset']['dataset_urls'][0]
        )

        dataloader = DataLoader.get_dataloader(
            dataset, preprocess,
            batch_size=config['dataset']['batch_size'], num_workers=config['dataset']['num_workers']
        )

        total_added_vectors, total_added_images = 0, 0

        for batch in dataloader:
            total_added_vectors += qdrant_index.add_points(
                config['qdrant']['collection_name'], model, batch
            )
            total_added_images += minio_index.bulk_upload(
                config['minio']['bucket_name'], batch
            )

        assert total_added_vectors == total_added_images, logger.error(f'{total_added_vectors}/{total_added_images}')

        logger.info(f"Total {total_added_vectors} vectors/images added to collection '{collection_name}'.")

    else:
        logger.info(f'Collection "{collection_name}" already exists. Skipping indexing.')
    
    collection_info = qdrant_index.get_collection_info(collection_name=collection_name)
    logger.info(collection_info)
    
index()
