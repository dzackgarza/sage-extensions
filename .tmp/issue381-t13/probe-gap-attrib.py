r"""#381: what a 420 s window of the row contains, measured on the row itself.

The record attributes the walk's 166 s to the setwise action
``Set(List(x, y -> ImageElm(g, y)))``.  The plane route passes no ``point``, so
it takes the ``FactorCosetAction`` branch instead.  This probe prices every GAP
call the row makes and records **when** each first happens, so the fixed part of
a window can be separated from the split's own work.

No signal is used to stop it: the row's own cap does, because Sage's cysignals
owns ``SIGALRM`` and turns a private timer into a backtrace.
"""

import importlib.util
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
        object.__setattr__(self, "first_at", {})

    def __getattr__(self, name):
        attribute = getattr(self._wrapped, name)
        if name not in TRACKED or not callable(attribute):
            return attribute
        calls, seconds, first, first_at = (
            self.calls,
            self.seconds,
            self.first,
            self.first_at,
        )

        def timed(*args, **kwargs):
            start = time.perf_counter()
            try:
                return attribute(*args, **kwargs)
            finally:
                seconds[name] += time.perf_counter() - start
                calls[name] += 1
                if name not in first:
                    first_at[name] = start - START
                    first[name] = tuple(
                        len(argument) if isinstance(argument, (list, tuple)) else argument
                        for argument in args
                    )

        return timed


def report(proxy, yielded, note):
    log(f"---- {note} ----")
    log(f"planes yielded by the split: {yielded['planes']} (first at {yielded['first_at']:.1f} s)")
    for name in sorted(proxy.seconds, key=lambda key: -proxy.seconds[key]):
        per_call = proxy.seconds[name] / proxy.calls[name]
        log(
            f"{name:28s} {proxy.calls[name]:7d} calls {proxy.seconds[name]:9.2f} s "
            f"{per_call * 1000:9.3f} ms/call  first at {proxy.first_at[name]:7.1f} s  "
            f"first={proxy.first[name]!r}"
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

yielded = {"planes": 0, "first_at": float("nan")}
original_iter = oq._iter_transported_planes


def counting_iter(*args, **kwargs):
    for plane in original_iter(*args, **kwargs):
        if not yielded["planes"]:
            yielded["first_at"] = time.perf_counter() - START
        yielded["planes"] += 1
        yield plane


oq._iter_transported_planes = counting_iter
try:
    outcome = rows.run_row(lattice, subgroup, "Otilde", 420, "auto")
finally:
    oq.libgap = original
    oq._iter_transported_planes = original_iter
log(f"outcome: {outcome.report()}")
report(proxy, yielded, "at the row's own 420 s cap")
log("done")
