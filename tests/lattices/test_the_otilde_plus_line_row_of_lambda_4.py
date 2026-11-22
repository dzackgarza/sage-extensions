r"""The line row of ``Lambda_4`` under ``Otilde+`` returns the card's one orbit.

Card ``6JRY`` of ``dzackgarza/lattice-database`` records one orbit of primitive
isotropic lines under $\widetilde O^+(\Lambda_4) = \ker \rho \cap O^+(\Lambda_4)$
(J. Scattone, *On the compactification of moduli spaces for algebraic K3
surfaces*, Mem. Amer. Math. Soc. 374 (1987), Theorem 4.0.1), and that is the row
this test asks the public orbit call of #286 for.

It is red at this commit, and the failure is the defect: the call asks for the
selected generating family of the ambient orthogonal group, whose computation on
this lattice grows without bound
(``results/issue618-the-ambient-family-is-the-cost.md``).  The row runs in a child
with an address-space bound and an alarm, so the growth is this row's outcome and
never the suite's, and the parent asserts the count the card states.
"""

#: The child stops itself when its resident set passes this bound, which the
#: lattice, the group and the finite character quotient together (306 MiB and one
#: second) are far below and the family's computation is not; the alarm bounds the
#: same growth in time.  An address-space limit cannot be used: Sage's import maps
#: more address space than the row ever needs resident.
_MEMORY_BYTES = 700 * 1024 * 1024
_ALARM_SECONDS = 180

_SOURCE = """
import os
import threading
import time

def _stop_at_the_bound(bound):
    while True:
        time.sleep(0.5)
        with open("/proc/self/status") as status:
            resident = [line for line in status if line.startswith("VmRSS:")][0]
        if int(resident.split()[1]) * 1024 > bound:
            print("stopped_at_memory_bound", flush=True)
            os._exit(3)

threading.Thread(target=_stop_at_the_bound, args=(BOUND,), daemon=True).start()

lattice = (
    Lattices(ZZ)("U")
    + Lattices(ZZ)("U")
    + Lattices(ZZ)("E8")
    + Lattices(ZZ)("E8")
    + Lattices(ZZ)([[-4]])
)
group = lattice.stable_orthogonal_group().intersection(lattice.O_plus())
print("count", group.isotropic_orbit_representatives(1).cardinality())
"""


def test_the_line_row_of_lambda_4_returns_the_cards_one_orbit() -> None:
    r"""The row's count is the card's one, inside a 700 MiB child and three minutes."""
    status, counts, stderr = counts_in_bounded_child(
        _SOURCE.replace("BOUND", f"{_MEMORY_BYTES}"), 0, _ALARM_SECONDS
    )
    assert counts == ["1"], (
        f"the child exited {status} and reported {counts}; stderr ends {stderr}"
    )
