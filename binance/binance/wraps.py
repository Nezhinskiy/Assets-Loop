import time
from functools import wraps


def time_of_function(func):
    def wrapper():
        start_time = time.time()
        result = func()
        execution_time = round(time.time() - start_time, 1)
        return result, execution_time
    return wrapper
