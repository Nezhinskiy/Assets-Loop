from multiprocessing import cpu_count


def max_workers():
    return cpu_count()


TIMEOUT = 300
workers = max_workers()
