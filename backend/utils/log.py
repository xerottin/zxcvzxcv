import time


def timeit(method):
    def timed(*args, **kwargs):
        ts = time.time()
        result = method(*args, **kwargs)
        te = time.time()
        print(f"{method.__name__} took: {te - ts} sec")
        return result

    return timed
