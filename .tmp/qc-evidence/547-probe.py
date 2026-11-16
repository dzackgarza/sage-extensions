import time
from sage_extensions.all import *
import sage_extensions.categories.sets.set_categories as sc


def big(n, *, key=None, record=None):
    """A finite ordered set of n naturals reached through its map, as a locus is."""
    indices = Sets.Δ[n - 1]

    def point(index):
        if record is not None:
            record.append(int(index))
        return ZZ(int(index))

    def position(value):
        number = ZZ(value)
        return number if indices.is_parent_of(number) is True else None

    return FiniteOrderedSets().from_indexed(indices, point, index_of=position, key=key)


def timed(fn):
    start = time.perf_counter()
    result = fn()
    return result, time.perf_counter() - start


point = Sets.Δ[0]
print("tree:", sc.__file__)
print(f"{'n':>7} {'declared: product':>18} {'points read':>12} | {'keyless: product':>17} {'points read':>12}")
for n in (2048, 8192, 32768, 131072):
    record = []
    factor = big(n, key=("locus", n), record=record)
    record.clear()
    _, t_declared = timed(lambda: Sets().product((factor, point)))
    declared_reads = tuple(record)

    plain_record = []
    plain = big(n, record=plain_record)
    plain_record.clear()
    _, t_plain = timed(lambda: Sets().product((plain, point)))
    plain_reads = tuple(plain_record)
    print(f"{n:7d} {t_declared*1e3:16.2f}ms {len(declared_reads):12d} | {t_plain*1e3:15.1f}ms {len(plain_reads):12d}")

# the second declaration of one datum
n = 32768
record = []
first = big(n, key=("locus", n), record=record)
record.clear()
_, t_again = timed(lambda: big(n, key=("locus", n), record=record))
print(f"second declaration of the same datum at n={n}: {t_again*1e3:.2f}ms, points read {len(record)}")
