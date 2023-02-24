"""
Configuration script. Define global paths that won't change.
"""
from pathlib import Path


def init(project_name=''):
    """
    Set global paths
    :param project_name: str representing your project dir name with the raw data
    :return:
    """
    global project
    global raw_path
    global intermediate_path
    global processed_path

    project = project_name
    raw_path = Path('/data/btu-ai/data/raw')
    intermediate_path = Path('/data/btu-ai/data/intermediate')
    processed_path = Path('/data/btu-ai/data/processed')


