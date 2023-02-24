"""
Configuration script. Define global paths that won't change.
"""
from pathlib import Path


def init(run_from='btupc09', project_name=''):
    """
    Set global paths
    :param run_from: 'btupc09' (default). 'cluster', 'local'
    :param project_name: str representing your project dir name with the raw data
    :return:
    """
    global project
    global raw_path
    global intermediate_path
    global processed_path

    project = project_name
    if run_from == 'btupc09':
        raw_path = Path('/data/btu-ai/data/raw')
        intermediate_path = Path('/data/btu-ai/data/intermediate')
        processed_path = Path('/data/btu-ai/data/processed')
    elif run_from == 'cluster':
        raw_path = Path('/home/BTU-AI/data/raw')
        intermediate_path = Path('/home/BTU-AI/data/intermediate')
        processed_path = Path('/home/BTU-AI/data/processed')
    elif run_from == 'local':
        raw_path = Path('/Volumes/btu-ai/data/raw')
        intermediate_path = Path('/Volumes/btu-ai/data/intermediate')
        processed_path = Path('/Volumes/btu-ai/data/processed')
    else:
        raise Exception('Define machine for preprocessing')

