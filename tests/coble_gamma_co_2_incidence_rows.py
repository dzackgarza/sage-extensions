r"""The Tits-building incidence rows on the Coble lattice, through the public call.

This is the acceptance entry point of #391: the incidence between the
``Gamma_{Co,2}``-orbits of primitive isotropic lines and planes of ``T_Co``,
and the ``O(T_Co)`` incidence through the same route.  It is not collected by
pytest (its file name does not begin with ``test_``), because these two rows
are measured in minutes and share one subgroup/orbit/cusp cache; they belong
in the dedicated CI job, not repeated throughout the per-test gate.  The final
route fits the runtime's 6144 MiB guard: the measured two-row run peaked at
3718 MiB tree RSS.

``T_Co = <2> + U(2) + E8(-2)`` is the Coble period lattice, D. Dolgachev and
S. Kondo, *Enriques surfaces and Borel--Weil--Bott type duality*, Izv. Math.
77:3 (2013), section 3, equation (3.6), printed p. 513, with ``E8`` negative
definite as the source's signature ``(2, 9)`` forces.

**The route.**  The edges at the orbit of a plane ``P`` are the
``Stab_{Gamma}(P)``-orbits of the isotropic lines of ``P``: the lines of a
totally isotropic plane are isotropic, and two flags over the same plane are
``Gamma``-equivalent exactly when their lines lie in one
``Stab_{Gamma}(P)``-orbit.  The lines of ``P`` decompose into orbits of the
plane's parabolic ``Pi = Stab_{O(T_Co)}(P)`` -- the divisibility of a line of
``P`` is preserved by ``Pi`` -- and those orbits are the ambient flag orbits
read at ``P``.  Within one such orbit the ``Stab_{Gamma}(P)``-orbits are the
double cosets ``K \ Pi / (Pi cap Stab(ell_0))`` with
``K = Stab_{Gamma}(P)``; because ``Gamma`` is the full preimage of its own
discriminant image, ``K`` contains the kernel of ``rho`` on ``Pi``, so the
double cosets descend to the finite image (D. Dutour Sikiri\'c and K. Hulek,
*Moduli of polarised Enriques surfaces -- computational aspects*, J. London
Math. Soc. 110 (2024), arXiv:2302.01679v2, Lemma 3.6, printed p. 22).  The
parabolic's family is certified complete (``is_parabolic_complete``, #331,
#366), so the stabilizer never reaches the indefinite port's generic
enumeration, which is killed at the memory guard on this lattice.

**What is asserted.**  No lattice-database card holds a ``T_Co`` value
(lattice-database#7), so no count is typed.  The assertion is what the cited
construction guarantees for every output:

* each edge joins a line that lies in its plane -- the edge's line term is
  contained in its plane term;
* every line orbit and every plane orbit has an edge -- each cusp of the
  line row and of the plane row appears as a vertex of some edge;
* the ``O(T_Co)`` incidence has one edge -- the ambient group is the whole of
  ``O(T_Co)``, so the left group of every double-coset computation is the
  parabolic's own image and each plane contributes its one transitive orbit
  of lines; that is the value ``main`` held at ``85284b8d18``.

The counts each row prints are the numbers the commit body of the push that
lands this file records.  A row that does not return inside its per-call cap
is reported as undecided, never as failed: the cap is the caller's budget,
not a mathematical statement.

    sage -python tests/coble_gamma_co_2_incidence_rows.py            # both rows
    sage -python tests/coble_gamma_co_2_incidence_rows.py --cap 10800
    sage -python tests/coble_gamma_co_2_incidence_rows.py --budget 28800
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


def _span(form, family):
    r"""The span of a finite family of classes of `A_L` over `ZZ/2ZZ`, as a set."""
    closure = {form.zero()}
    for generator in family:
        closure |= {element + generator for element in closure}
    return frozenset(closure)


def _classes(lattice):
    r"""One class of `A_L` per named module generator: the primitive dual's class."""
    return {
        label: lattice.discriminant_class(lattice.primitive_dual(lattice.module_generator(label)))
        for label in lattice.module_generating_set()
    }


def _decomposition(lattice):
    r"""`A_{U(2)}`, the span of the `U(2)`-generators' classes in `A_{T_Co}`."""
    form = lattice.discriminant_group()
    classes = _classes(lattice)
    return _span(form, (classes["ep"], classes["fp"]))


def _assert_line_in_plane(line, plane) -> None:
    r"""The line term of an edge lies in the plane term of the same edge."""
    domain = line.inclusion().domain()
    label = next(iter(domain.module_generating_set()))
    assert plane.inclusion().is_in_image(line.inclusion()(domain.module_generator(label)))


def run_row(lattice, subgroup, label, cap):
    r"""Return ``(edge count, line cusps, plane cusps, decided)`` for one incidence row."""
    start = time.monotonic()
    try:
        signal.setitimer(signal.ITIMER_REAL, cap)
        incidences = tuple(subgroup.tits_building_incidence())
    except RowUndecided:
        log(f"[{label}] undecided: the row did not return inside its {cap:.0f} s cap")
        return None, None, None, False
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    elapsed = time.monotonic() - start
    lines = tuple(subgroup.cusps(1))
    planes = tuple(subgroup.cusps(2))
    line_vertices = {incidence.line_cusp() for incidence in incidences}
    plane_vertices = {incidence.plane_cusp() for incidence in incidences}
    for incidence in incidences:
        _assert_line_in_plane(incidence.line(), incidence.plane())
        assert incidence.line_cusp() in lines
        assert incidence.plane_cusp() in planes
    for cusp in lines:
        assert cusp in line_vertices, f"a line cusp of {label} carries no edge"
    for cusp in planes:
        assert cusp in plane_vertices, f"a plane cusp of {label} carries no edge"
    log(
        f"[{label}] {len(incidences)} edges over {len(lines)} line cusps and "
        f"{len(planes)} plane cusps in {elapsed:.1f} s"
    )
    return len(incidences), len(lines), len(planes), True


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cap", type=int, default=10800,
                        help="seconds one row call may take before it is undecided")
    parser.add_argument("--budget", type=int, default=28800,
                        help="seconds the whole run may take, 0 for no budget")
    arguments = parser.parse_args(argv)
    started = time.monotonic()
    lattice = NamedLattices.Tco
    log(f"the Coble period lattice {lattice} of rank {lattice.module_rank()}")
    rows = {}
    for label, subgroup in (
        ("O(T_Co)", lattice.Aut()),
        ("Gamma_{Co,2}", lattice.Aut().discriminant_point_stabilizer(_decomposition(lattice))),
    ):
        if arguments.budget and time.monotonic() - started > arguments.budget:
            log("the whole-run budget is spent")
            return 1
        count, line_count, plane_count, decided = run_row(lattice, subgroup, label, arguments.cap)
        if not decided:
            return 1
        rows[label] = (count, line_count, plane_count)
    if rows["O(T_Co)"][0] != 1:
        log("the O(T_Co) incidence through this route is not one edge")
        return 1
    log(
        f"the O(T_Co) incidence has {rows['O(T_Co)'][0]} edge; the Gamma_{{Co,2}} incidence has "
        f"{rows['Gamma_{Co,2}'][0]} edges over {rows['Gamma_{Co,2}'][1]} line orbits and "
        f"{rows['Gamma_{Co,2}'][2]} plane orbits"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
