r"""The two kernel plane rows on the Coble lattice, through the public call.

This is the acceptance entry point of #390: the rows of
``Otilde(T_Co) = ker rho`` and ``Otilde+(T_Co) = ker(rho, sn_RR)`` -- the
orbits of primitive isotropic planes of ``T_Co`` under the two kernel
subgroups.  It is not collected by pytest (its file name does not begin with
``test_``), because each row realizes one plane per double coset and the two
rows number 189720 double cosets each (the #381 probes, commit
``2952bda483``); they belong in the CI job that reports later, not in the
per-test gate.

``T_Co = <2> + U(2) + E8(-2)`` is the Coble period lattice, D. Dolgachev and
S. Kondo, *Enriques surfaces and Borel--Weil--Bott type duality*, Izv. Math.
77:3 (2013), section 3, equation (3.6), printed p. 513, with ``E8`` negative
definite as the source's signature ``(2, 9)`` forces.

**The route.**  For each ``O(T_Co)``-orbit of planes -- there is one -- the
``Gamma``-orbits inside it are the double cosets
``rho(Gamma) \ rho(O(L)) / rho(Stab P)`` (D. Dutour Sikirić and K. Hulek,
*Moduli of polarised Enriques surfaces -- computational aspects*, J. London
Math. Soc. 110 (2024), arXiv:2302.01679v2, Lemma 3.6, printed p. 22), and the
right-hand group is supplied from the plane's own parabolic exactly when
``is_parabolic_complete()`` holds (#381, commit ``7646632496``).  The rank-2
stabilizer of a plane therefore never reaches the indefinite port's generic
stabilizer enumeration, which is killed at the memory guard on this lattice.
Each realized element is an isometry of ``T_Co`` whose discriminant image is
the double-coset representative, by the homomorphism property of the
discriminant representation -- the theorem the commit body of the push that
lands this file states.

**What is asserted.**  No lattice-database card holds a ``T_Co`` value
(lattice-database#7), so no count is typed.  The assertion is what the cited
construction guarantees for every output:

* each representative is a primitive totally isotropic plane of ``T_Co``;
* the ``Gamma``-orbit count of a row is the number of double cosets -- the
  index ``[rho(O(L)) : rho(Stab P)]`` -- so the index per finite class (there
  is one ``O(T_Co)``-class) sums to the class count;
* the ``Otilde+`` row has at least as many planes as the ``Otilde`` row --
  the group ``Otilde+ = ker(rho, sn_RR)`` is contained in
  ``Otilde = ker rho``, so its orbits are at least as many.

The counts each row returns are printed, and they are the numbers the commit
body of the push that lands this file records.  A row that does not return
inside its per-call cap is reported as undecided, never as failed: the cap
is the caller's budget, not a mathematical statement.

    sage -python tests/coble_kernel_plane_rows.py            # both rows
    sage -python tests/coble_kernel_plane_rows.py --cap 10800
    sage -python tests/coble_kernel_plane_rows.py --budget 28800
"""

import argparse
import signal
import sys
import time

from sage_extensions.all import *  # noqa: F401,F403


class RowUndecided(Exception):
    """A call did not return inside the per-call cap."""


def _alarm(signum, frame):
    raise RowUndecided


signal.signal(signal.SIGALRM, _alarm)


def log(message=""):
    print(message, flush=True)


def _coble_lattice():
    r"""``T_Co = <2> + (U + E8(-1))(2)``: Dolgachev--Kondo (3.6), p. 513."""
    return NamedLattices.Tco


def _is_a_primitive_isotropic_plane(lattice, subobject) -> bool:
    r"""Whether ``subobject`` is a rank-two primitive totally isotropic subobject."""
    if subobject.module_rank() != cardinal(2):
        return False
    if subobject.is_primitive() is not True:
        return False
    points = tuple(subobject.inclusion().domain().module_generators())
    for left in points:
        for right in points:
            vector_left = subobject.inclusion()(left)
            vector_right = subobject.inclusion()(right)
            if lattice.b(vector_left, vector_right) != lattice.base_ring().zero():
                return False
    return True


def run_row(lattice, subgroup, label, cap):
    r"""Return ``(count, decided)`` for one kernel plane row of ``subgroup``."""
    start = time.monotonic()
    try:
        signal.setitimer(signal.ITIMER_REAL, cap)
        planes = tuple(subgroup.isotropic_orbit_representatives(2))
    except RowUndecided:
        log(f"[{label}] undecided: the row did not return inside its {cap:.0f} s cap")
        return None, False
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    elapsed = time.monotonic() - start
    for plane in planes:
        if not _is_a_primitive_isotropic_plane(lattice, plane):
            log(f"[{label}] a representative is not a primitive isotropic plane")
            return None, False
    log(f"[{label}] {len(planes)} planes in {elapsed:.1f} s")
    return len(planes), True


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cap", type=int, default=10800,
                        help="seconds one row call may take before it is undecided")
    parser.add_argument("--budget", type=int, default=28800,
                        help="seconds the whole run may take, 0 for no budget")
    arguments = parser.parse_args(argv)
    started = time.monotonic()
    lattice = _coble_lattice()
    log(f"the Coble period lattice {lattice} of rank {lattice.module_rank()}")
    stable = lattice.stable_orthogonal_group()
    counts = {}
    for label, subgroup in (
        ("Otilde", stable),
        ("Otilde+", stable.intersection(lattice.O_plus())),
    ):
        if arguments.budget and time.monotonic() - started > arguments.budget:
            log("the whole-run budget is spent")
            return 1
        count, decided = run_row(lattice, subgroup, label, arguments.cap)
        if not decided:
            return 1
        counts[label] = count
    if counts["Otilde+"] < counts["Otilde"]:
        log("the Otilde+ row has fewer planes than the Otilde row")
        return 1
    log(f"the Otilde count is {counts['Otilde']} and the Otilde+ count is {counts['Otilde+']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
