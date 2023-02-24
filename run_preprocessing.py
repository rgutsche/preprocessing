"""
Preprocessing Script
author: Robin Gutsche
last-update: 26-08-2021, 22:17
"""

from multiprocessing import Process, Queue
from preprocessing.run import run_preprocessing
from preprocessing import settings
from preprocessing.helpers import listener_process, listener_configurer, worker_configurer

# if __name__ == '__main__':
settings.init(run_from='btupc09', project_name='CETEG_PROGNOSE_PART2')
number_of_processes = 9
pids = sorted([x.name for x in settings.raw_path.joinpath(settings.project).glob('*') if not x.name.startswith('.')])

q = Queue(-1)
listener = Process(target=listener_process, args=(q, listener_configurer))
listener.start()
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
listener.join()





