r"""#381: what the __doc__ read in _copy_operation_metadata costs per realized word."""

import time

from sage_extensions.all import Lattices, ZZ
from sage_extensions.categories.abstract_categories import mor_foundation

lattice = Lattices(ZZ)("U") + Lattices(ZZ)("A2")
group = lattice.Aut()
generator = tuple(group.group_generators())[0]


def time_it(label, function, count):
    start = time.perf_counter()
    for _ in range(count):
        function()
    elapsed = time.perf_counter() - start
    print(f"{label:28} {count} calls  {elapsed:7.3f}s  {elapsed / count * 1e3:7.3f} ms each")


def realize():
    group.one()
    ~generator


time_it("warm-up", realize, 3)
time_it("current", realize, 60)

original = mor_foundation._copy_operation_metadata


def fast(operation, reading):
    operation.__wrapped__ = reading
    for name in mor_foundation.WRAPPER_ASSIGNMENTS:
        if name == "__doc__":
            continue
        try:
            value = getattr(reading, name)
        except AttributeError:
            continue
        setattr(operation, name, value)


mor_foundation._copy_operation_metadata = fast
time_it("without the __doc__ read", realize, 60)
mor_foundation._copy_operation_metadata = original

start = time.perf_counter()
from sage.misc import sageinspect
for _ in range(20):
    try:
        sageinspect.sage_getsourcelines(type(generator))
    except Exception:
        pass
elapsed = time.perf_counter() - start
print(f"sage_getsourcelines         20 calls  {elapsed:7.3f}s  {elapsed / 20 * 1e3:7.3f} ms each")
