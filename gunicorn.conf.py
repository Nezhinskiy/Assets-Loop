from multiprocessing import cpu_count


def max_workers():
    return cpu_count()


TIMEOUT = 300
workers = max_workers()
max_requests = 1000
worker_class = 'gevent'
