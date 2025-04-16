import io

import logging

from minio import Minio
from minio.error import S3Error

from torch.utils.data import DataLoader

from tqdm import tqdm

logging.basicConfig(
    filename='logs/index.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    filemode='w'
)

logger = logging.getLogger(__name__)

class MinIOIndex:

    def __init__(
        self,
        endpoint,
        access_key,
        secret_key,
        secure=True
    ):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
    
    def bucket_exists(self, bucket_name):
        return True if self.client.bucket_exists(bucket_name) else False
    
    def create_bucket(self, bucket_name):
        try:
            self.client.make_bucket(bucket_name)
        except S3Error as e:
            logger.error(f'Failed to create bucket: {e}')

    def bulk_upload(
        self, bucket_name, batch
    ):

        total_added = 0 
        try:      
            ids, _, images, _ = batch
            try:
                for id, image_bytes in zip(ids, images):

                    data_stream = io.BytesIO(image_bytes)
                    data_stream.seek(0)

                    self.client.put_object(
                        bucket_name=bucket_name,
                        object_name=id,
                        data=data_stream,
                        length=len(image_bytes)
                    )
                    total_added += 1
            except S3Error as e:
                logger.error(f'Upload failed: {e}')
        except S3Error as e:
            logger.error(f'Error initializing bucket or client: {e}')
            return False

        return total_added
    
    def fetch_all(
        self,
        bucket_name,
        ids
    ):
        images = []

        try:
            if not self.client.bucket_exists(bucket_name):
                raise ValueError(f"Bucket '{bucket_name}' does not exist.")

            for id in ids:
                try:
                    response = self.client.get_object(bucket_name, id)
                    image = io.BytesIO(response.data)
                    image.seek(0)
                    images.append(image)
                except S3Error as e:
                    logger.error(f"Retrieval failed for {id}: {e}")
                finally:
                    response.close()
                    response.release_conn()
        except S3Error as e:
            logger.error(f"Error accessing bucket or client: {e}")
        return images