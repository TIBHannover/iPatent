import os
import logging

from typing import List, Dict, Any

from torch.utils.data import DataLoader

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointIdsList, Batch,
    Filter, FieldCondition, MatchValue
)

from tqdm import tqdm

os.environ.pop('SSL_CERT_FILE', None)

logging.basicConfig(
    filename='logs/index.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    filemode='w'
)

logger = logging.getLogger(__name__)

class QdrantIndex:
    def __init__(self, host: str = 'localhost', port: int = 8181):
        self.client = QdrantClient(
            host=host, port=port, https=False
        )

    def check_connection(self):
        """Check QDrant connection"""
        try:
            self.client.api_version()
            logger.info("Connection to Qdrant established successfully!")
            return True
        except Exception as e:
            logger.fatal(f"Failed to connect to Qdrant: {e}")

    def collection_exits(self, collection_name):
        if self.client.collection_exists(collection_name):
            return True
        return False
        
    def create_collection(
        self, collection_name: str, vector_size: int, distance: str = 'Cosine'
    ):
        """Create a new collection in Qdrant."""
    
        distance_map = {
            'Cosine': Distance.COSINE,
            'Euclid': Distance.EUCLID,
            'Dot': Distance.DOT,
        }

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size, distance=distance_map[distance]
            ),
        )

    def add_points(self, collection_name: str, model, batch):
        """Add points to the specified collection."""
        
        total_added = 0
        
        try:
            ids, payloads, _, tensors = batch
            vectors = model.encode_images(tensors).cpu().numpy()
            
            self.client.upsert(
                collection_name=collection_name,
                points=Batch(ids=ids, vectors=vectors, payloads=payloads)
            )
            
            total_added += len(ids)
        
        except Exception as e:
            logger.error(f"Error adding batch to collection '{collection_name}': {str(e)}")
        
        return total_added

    def delete_points(self, collection_name: str, point_ids: List[int]):
        """Delete points from the specified collection."""
        self.client.delete(
            collection_name=collection_name,
            points_selector=PointIdsList(points=point_ids),
        )
        logger.info(f"{len(point_ids)} points deleted from collection '{collection_name}'.")

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about the specified collection."""
        return self.client.get_collection(
            collection_name=collection_name
        )

    def list_collections(self) -> List[str]:
        """List all collections in the Qdrant instance."""
        return [
            collection.name
            for collection in self.client.get_collections().collections
        ]

    def delete_collection(self, collection_name: str):
        """Delete the specified collection."""
        self.client.delete_collection(collection_name=collection_name)
        return True

    def dict_to_filter(self, filter_dict: Dict[str, Any]) -> Filter:
        """
        Convert a dictionary into a Qdrant `Filter` object.
        
        Args:
            filter_dict (Dict[str, Any]): A dictionary specifying filter conditions.

        Returns:
            Filter: A Qdrant filter object.
        """
        must_conditions = []
        
        for key, value in filter_dict.items():
            must_conditions.append(
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
            )
        
        return Filter(must=must_conditions)
    
    def search(
        self, 
        collection_name: str, 
        query_vector: List[float], 
        limit: int = 10, 
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform a vector search in the specified collection with optional filtering.

        Args:
            collection_name (str): The name of the collection to search.
            query_vector (List[float]): The query vector for similarity search.
            limit (int): Maximum number of results to return.
            filters (Dict[str, Any], optional): A dictionary of filters to apply. Defaults to None.

        Returns:
            List[Dict[str, Any]]: A list of search results with id, score, and payload.
        """
        # Convert filters dictionary to a Qdrant Filter object if provided
        filter_obj = self.dict_to_filter(filters) if filters else None

        # Perform the query
        results = self.client.query_points(
            collection_name=collection_name,
            query=query_vector.tolist()[0],
            query_filter=filter_obj,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )

        return [
            {
                'id': hit.id,
                'score': hit.score,
                'payload': hit.payload
            }
            for hit in results.points
        ]
    
    def get_vector_by_id(self, collection_name: str, point_id: int) -> List[float]:
        """
        Retrieve the vector corresponding to a specific point ID.

        Args:
            collection_name (str): The name of the collection.
            point_id (int): The ID of the point.

        Returns:
            List[float]: The vector associated with the given point ID.
        """
        result = self.client.retrieve(
            collection_name=collection_name,
            ids=[point_id],
            with_vectors=True,  # Include vectors in the result
        )
        if result:
            return result[0].vector  # Return the vector of the first (and only) result
        else:
            raise ValueError(f"Point with ID {point_id} not found in collection '{collection_name}'.")
    
    def get_vectors_by_ids(self, collection_name: str, point_ids: List[int]) -> Dict[int, List[float]]:
        """
        Retrieve vectors corresponding to a list of point IDs.

        Args:
            collection_name (str): The name of the collection.
            point_ids (List[int]): A list of point IDs.

        Returns:
            Dict[int, List[float]]: A dictionary mapping each point ID to its vector.
        """
        results = self.client.retrieve(
            collection_name=collection_name,
            ids=point_ids,
            with_vectors=True,  # Include vectors in the result
        )
        return {result.id: result.vector for result in results}