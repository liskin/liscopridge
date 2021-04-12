from contextlib import contextmanager
from time import perf_counter


@contextmanager
def timeit():
    t = None
    start = perf_counter()
    yield lambda: t
    t = perf_counter() - start


@contextmanager
def timeit_print(text="timeit"):
    start = perf_counter()
    yield
    print(f"{text}: {perf_counter() - start:.3f} sec")
