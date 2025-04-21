import io

import logging

from minio import Minio
from minio.error import S3Error

from concurrent.futures import ThreadPoolExecutor, as_completed

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
        self, bucket_name, ids
    ):
        """
        Concurrently fetch images from MinIO bucket as BytesIO objects.
        """
        images = [None] * len(ids)

        if not self.client.bucket_exists(bucket_name):
            raise ValueError(f"Bucket '{bucket_name}' does not exist.")

        def fetch(index, object_id):
            try:
                response = self.client.get_object(bucket_name, object_id)
                image_data = io.BytesIO(response.data)
                image_data.seek(0)
                return index, image_data
            except S3Error as e:
                logger.error(f"Retrieval failed for {object_id}: {e}")
                return index, None
            finally:
                try:
                    response.close()
                    response.release_conn()
                except Exception:
                    pass

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(fetch, i, obj_id) for i, obj_id in enumerate(ids)]
            for future in as_completed(futures):
                index, image = future.result()
                images[index] = image

        return [img for img in images if img is not None]