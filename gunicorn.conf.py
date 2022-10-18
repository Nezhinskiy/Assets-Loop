from multiprocessing import cpu_count


def max_workers():
    return cpu_count() * 2 + 1


TIMEOUT = 600
workers = max_workers()

