r"""#381: do the two kernel rows have the same cusp lists, or only the same counts?

The walk's data -- the coset space `im rho / rho(Stab)`, the breadth-first
transversal, and the lifts spelled from the lattice's ambient generators -- does
not mention the subgroup.  What the subgroup enters through is the character
image `A = chi(Gamma)`, which is trivial for both kernel rows, and the sign
sheet, which `Otilde` does not have (`j = 0`) and `Otilde+` suppresses because
its stabilizer presents the sign coset.  So the two rows should yield the *same*
planes in the *same* order, not merely equally many.  This probe compares the
cusp lists themselves on the lattices the gate can afford.
"""

import importlib.util
import sys
import time

sys.path.insert(0, "tests")
START = time.perf_counter()


def log(message):
    print(f"[{time.perf_counter() - START:8.2f}s] {message}", flush=True)


spec = importlib.util.spec_from_file_location("rows", "tests/coble_gamma_co_2_incidence_rows.py")
rows = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rows)

for name in ("U+U(2)+<-2>", "6JRS"):
    lattice = rows._lattice_by_name(name)
    log(f"=== {name}: rank {lattice.module_rank()}, signature {lattice.signature()} ===")
    for rank in (1, 2):
        lists = {}
        for label in ("Otilde", "Otilde+"):
            subgroup = rows._row_subgroup(lattice, label)
            cusps = tuple(subgroup.cusps(rank))
            lists[label] = tuple(
                rows._coordinates(cusp.representative()) for cusp in cusps
            )
            log(f"  {label} rank {rank}: {len(cusps)} cusps")
        same_list = lists["Otilde"] == lists["Otilde+"]
        same_set = set(lists["Otilde"]) == set(lists["Otilde+"])
        log(f"  rank {rank}: lists equal {same_list}; sets equal {same_set}")
        if not same_list:
            for position, (left, right) in enumerate(
                zip(lists["Otilde"], lists["Otilde+"], strict=False)
            ):
                if left != right:
                    log(f"  first difference at position {position}: {left} vs {right}")
                    break
log("done")
