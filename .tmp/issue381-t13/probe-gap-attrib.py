r"""#381: which GAP call a plane's cost is in -- measured on the row, not modelled.

The record attributes the walk's 166 s to the setwise action
``Set(List(x, y -> ImageElm(g, y)))``.  The plane route passes no ``point``, so
it takes the ``FactorCosetAction`` branch instead.  This probe prices every GAP
call that branch makes, on the row itself, and it dumps its table on an alarm so
a kill cannot take the numbers with it.

Two counts matter and they are different numbers: ``_from_image`` *invocations*
(one ``FactorCosetAction`` each) and the lifts it yields (one generator resume
each).  ``FactorCosetAction``'s count is the first.
"""

import importlib.util
import os
import signal
import sys
import time
from collections import defaultdict

sys.path.insert(0, "tests")
START = time.perf_counter()


def log(message):
    print(f"[{time.perf_counter() - START:8.2f}s] {message}", flush=True)


import sage_extensions.categories.orthogonal_quotients as oq

TRACKED = (
    "IsomorphismPermGroup",
    "Range",
    "Subgroup",
    "Image",
    "FactorCosetAction",
    "Index",
    "GeneratorsOfGroup",
    "TrivialSubgroup",
    "ClosureGroup",
    "Order",
    "Orbits",
    "PreImagesRepresentative",
    "LetterRepAssocWord",
    "FreeGroup",
    "GroupHomomorphismByImagesNC",
    "One",
    "Set",
    "function_factory",
)


class TimedGap:
    """Forwards to ``libgap`` and times every call it makes in ``TRACKED``."""

    def __init__(self, wrapped):
        object.__setattr__(self, "_wrapped", wrapped)
        object.__setattr__(self, "calls", defaultdict(int))
        object.__setattr__(self, "seconds", defaultdict(float))
        object.__setattr__(self, "first", {})

    def __getattr__(self, name):
        attribute = getattr(self._wrapped, name)
        if name not in TRACKED or not callable(attribute):
            return attribute
        calls, seconds, first = self.calls, self.seconds, self.first

        def timed(*args, **kwargs):
            start = time.perf_counter()
            try:
                return attribute(*args, **kwargs)
            finally:
                seconds[name] += time.perf_counter() - start
                calls[name] += 1
                if name not in first:
                    first[name] = tuple(
                        len(argument) if isinstance(argument, (list, tuple)) else argument
                        for argument in args
                    )

        return timed


def report(proxy, note):
    log(f"---- {note} ----")
    for name in sorted(proxy.seconds, key=lambda key: -proxy.seconds[key]):
        per_call = proxy.seconds[name] / proxy.calls[name]
        log(
            f"{name:30s} {proxy.calls[name]:7d} calls {proxy.seconds[name]:9.2f} s "
            f"{per_call * 1000:9.3f} ms/call  first={proxy.first[name]!r}"
        )


spec = importlib.util.spec_from_file_location("rows", "tests/coble_gamma_co_2_incidence_rows.py")
rows = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rows)

lattice = rows._lattice_by_name("Tco")
log(f"lattice: rank {lattice.module_rank()}, signature {lattice.signature()}")
subgroup = rows._row_subgroup(lattice, "Otilde")
log(f"subgroup: {subgroup}")

original = oq.libgap
proxy = TimedGap(original)
oq.libgap = proxy

# The planes the split yields, counted where they are yielded: the walk's own
# resumes are not a count of them, because one invocation yields many.
yielded = {"planes": 0}
original_iter = oq._iter_transported_planes


def counting_iter(*args, **kwargs):
    for plane in original_iter(*args, **kwargs):
        yielded["planes"] += 1
        yield plane


oq._iter_transported_planes = counting_iter


def dump(_signum, _frame):
    oq.libgap = original
    log(f"planes yielded by the split: {yielded['planes']}")
    report(proxy, "at the alarm")
    log("done")
    os._exit(0)


signal.signal(signal.SIGALRM, dump)
signal.setitimer(signal.ITIMER_REAL, 700.0)
try:
    outcome = rows.run_row(lattice, subgroup, "Otilde", 1200, "auto")
    signal.setitimer(signal.ITIMER_REAL, 0.0)
finally:
    oq.libgap = original
log(f"outcome: {outcome.report()}")
report(proxy, "after the row")
log("done")
