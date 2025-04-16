import io

import webdataset as wds
from braceexpand import braceexpand

from shared.dataset.registry import DatasetRegistry

@DatasetRegistry.register('epo')
class EPODataset(wds.WebDataset):

    def __init__(self, shards_url):

        wds.WebDataset.__init__(self, urls=shards_url)
        self.shards_url = shards_url
        self.shards = braceexpand(self.shards_url)
        self.output_dict = {
            '__key__': lambda x: x,
            'image.png': lambda x: x,
            'hashcode.txt': lambda x: x.decode('utf-8'),
            'name.txt': lambda x: x.decode('utf-8'),
            'class.txt': lambda x: x.decode('utf-8'),
            'desc.txt': lambda x: x.decode('utf-8'),
            'labels.txt': lambda x: x.decode('utf-8'),
            'title.txt': lambda x: x.decode('utf-8')
        }
    
    def __iter__(self):

        for shard in self.shards:
            dataset = (
                wds.WebDataset(shard, shardshuffle=0, empty_check=False)
                .shuffle(0)
                .to_tuple(*self.output_dict.keys())
                .map_tuple(
                    *[
                        self.output_dict[key]
                        for key in self.output_dict.keys()
                    ]
                )
                .map(lambda x: dict(zip(self.output_dict.keys(), x)))
            )

            for sample in dataset:
                yield sample