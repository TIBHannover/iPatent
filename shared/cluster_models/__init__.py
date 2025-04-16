import os
import importlib

current_dir = os.path.dirname(__file__)
for filename in os.listdir(current_dir):
    if filename.endswith('_cluster_model.py') and filename not in ['__init__.py']:
        module_name = f'shared.cluster_models.{filename[:-3]}' 
        importlib.import_module(module_name)
