"""
Preprocessing Script
author: Robin Gutsche
last-update: 24-02-2023
"""
from multiprocessing import Process, Queue
from preprocessing.run_v2 import run_preprocessing
from preprocessing import settings
from preprocessing.helpers import worker_configurer

settings.init(project_name='TEMP_V2')

number_of_processes = 4

pids = sorted([x.name for x in settings.raw_path.joinpath(settings.project).glob('*') if not x.name.startswith('.')])

q = Queue(-1)

processes = []
i = 0
for pid in pids:
    p = Process(target=run_preprocessing, args=(pid, q, worker_configurer))
    processes.append(p)
    i += 1
    if i % number_of_processes == 0 or i == len(pids):
        for process in processes:
            process.start()

        for process in processes:
            process.join()

        processes = []
q.put_nowait(None)





