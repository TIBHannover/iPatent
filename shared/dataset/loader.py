import uuid
import numpy as np
import webdataset as wds

class DataLoader:

    @staticmethod
    def get_dataloader(dataset, transforms, batch_size=32, num_workers=4):
        
        def collate_fn(batch):
            ids, metadata, images, tensors = [], [], [], []

            for sample in batch:
                ids.append(str(uuid.uuid4()))
                meta = {k: v for k, v in sample.items() if k not in ['image.png']}
                metadata.append(meta)
                images.append(sample['image.png'])
                tensors.append(transforms(sample['image.png'], tensors=True))

            return np.array(ids), metadata, images, tensors
        
        return wds.WebLoader(
            dataset,
            batch_size=batch_size,
            num_workers=num_workers,
            collate_fn=collate_fn
        )