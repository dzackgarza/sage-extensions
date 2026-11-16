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

**What is asserted.**  The decided Gamma relation has 13 edges over four line
cusps and seven plane cusps.  No lattice-database card holds a ``T_Co`` value
(lattice-database#7); this acceptance value is checked against representatives
from both the pinned and the image's indefinite-port checkouts.  In addition,
the cited construction guarantees for every output:

* each edge joins a line that lies in its plane -- the edge's line term is
  contained in its plane term, and one subgroup element carries the selected
  line cusp representative into the selected plane cusp representative;
* the incidence is a relation, not a flag-orbit count -- no two retained edges
  have the same line and plane cusp endpoints;
* every line orbit and every plane orbit has an edge -- each cusp of the
  line row and of the plane row appears as a vertex of some edge;
* the ``O(T_Co)`` incidence has one edge -- the ambient group is the whole of
  ``O(T_Co)``, so the left group of every double-coset computation is the
  parabolic's own image and each plane contributes its one transitive orbit
  of lines; that is the value ``main`` held at ``85284b8d18``.

The counts each row prints are the numbers the commit body of the push that
lands this file records.  A row that does not return inside its per-call cap
is reported as undecided, never as failed: the cap is the caller's budget,
not a mathematical statement.  A row that returns an edge which fails its
check is reported apart from that, as a contract violation, because it is a
statement about the library's answer and not about the budget: each returned
edge's line must lie in its plane and one subgroup element must carry the line
cusp representative into the plane cusp representative, and the edges together
must be a relation -- no two sharing their line and plane cusp endpoints, and
no cusp of either row left without an edge.  The driver's exit status says
which happened -- 0 both rows decided as the decided relation, 1 a row
undecided or the whole-run budget spent, 2 a returned edge that breaks the
contract, 3 a decided row whose counts are not the decided relation -- and the
statuses and those exit statuses are the vocabulary of
``tests/coble_row_status.py``, shared with the kernel-plane-rows driver.

    sage -python tests/coble_gamma_co_2_incidence_rows.py            # both rows
    sage -python tests/coble_gamma_co_2_incidence_rows.py --cap 10800
    sage -python tests/coble_gamma_co_2_incidence_rows.py --budget 28800
"""

import argparse
import signal
import sys
import time

from sage_extensions.all import *  # noqa: F401,F403

from coble_row_status import (
    EXIT_COUNT_MISMATCH,
    EXIT_DECIDED,
    EXIT_UNDECIDED,
    RowStatus,
    exit_status,
)


class RowUndecided(Exception):
    """A call did not return inside the per-call cap."""


def _alarm(signum, frame):
    raise RowUndecided


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


def containment_violation(line, plane) -> str | None:
    r"""Why an edge whose line and plane these are breaks the row's contract, or ``None``.

    The line term of the edge must lie in its plane term: the line's retained
    generator is a vector of the lattice, and it lies in the plane exactly when
    it is in the image of the plane's inclusion.
    """
    domain = line.inclusion().domain()
    label = next(iter(domain.module_generating_set()))
    if plane.inclusion().is_in_image(line.inclusion()(domain.module_generator(label))):
        return None
    return "its line is not contained in its plane"


def transport_violation(subgroup, incidence) -> str | None:
    r"""Why no subgroup element carries the edge's line cusp into its plane cusp, or ``None``.

    The witness ``plane_transporter * line_transporter^-1`` carries the selected
    line cusp's representative into the selected plane cusp's representative.
    It must be an element of the subgroup the row is taken under, and what it
    carries that line to must lie in that plane.
    """
    witness = incidence.plane_transporter() * ~incidence.line_transporter()
    if witness not in subgroup:
        return (
            "no element of the subgroup carries the line cusp representative "
            "into the plane cusp representative"
        )
    moved = witness.transport_isotropic_object(incidence.line_cusp().representative())
    return containment_violation(moved, incidence.plane_cusp().representative())


def edge_violation(subgroup, incidence) -> str | None:
    r"""Why one returned edge breaks the row's contract, or ``None``."""
    violation = containment_violation(incidence.line(), incidence.plane())
    if violation is not None:
        return violation
    return transport_violation(subgroup, incidence)


def cusp_position(cusps, cusp) -> int | None:
    r"""The position of ``cusp`` among ``cusps``, or ``None`` when it is not one of them."""
    for position, candidate in enumerate(cusps):
        if candidate is cusp or candidate == cusp:
            return position
    return None


def report_row_outcome(label, status, detail):
    r"""Report one row's outcome in one line and return ``(None, status)``.

    The one place a row's outcome is worded.  The status names which fact about
    the run it is, and the detail names the clause that broke or the cap that
    expired; a row that did not decide returns no counts.
    """
    log(f"[{label}] {status.value}: {detail}")
    return None, status


def _coordinates(term):
    r"""The integral coordinates of a subobject's retained basis in its ambient lattice."""
    inclusion = term.inclusion()
    domain = inclusion.domain()
    lattice = inclusion.codomain()
    labels = tuple(lattice.module_generating_set())
    return tuple(
        tuple(
            int(inclusion(domain.module_generator(label)).to_vector()(other))
            for other in labels
        )
        for label in domain.module_generating_set()
    )


def run_row(lattice, subgroup, label, cap):
    r"""Return ``(counts, status)`` for one incidence row of ``subgroup``.

    The row step is the public call ``tits_building_incidence()`` under the
    per-row cap: the alarm's ``RowUndecided`` makes the row undecided, never
    failed, because the cap is the caller's budget and not a mathematical
    statement.  The cap is the row's own signal for the length of that call, so
    the handler is installed here and given back when the call ends.

    Every edge the call returns is checked against the row's contract -- its
    line lies in its plane, and one element of the subgroup carries the line
    cusp representative into the plane cusp representative -- and the edges
    together are checked as a relation: each edge's two cusps are cusps of the
    row, no two edges share their line and plane cusp endpoints, and every line
    cusp and every plane cusp is a vertex of an edge.
    A returned edge or set of edges that breaks the contract is a different
    ``RowStatus`` from an undecided row, and the report names the clause and the
    edge.  ``counts`` is the edge, line cusp and plane cusp count of a decided
    row, and ``None`` for a row that did not decide.
    """
    start = time.monotonic()
    previous_handler = signal.signal(signal.SIGALRM, _alarm)
    try:
        signal.setitimer(signal.ITIMER_REAL, cap)
        incidences = tuple(subgroup.tits_building_incidence())
    except RowUndecided:
        return report_row_outcome(
            label, RowStatus.UNDECIDED, f"the row did not return inside its {cap:g} s cap"
        )
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)
    elapsed = time.monotonic() - start
    lines = tuple(subgroup.cusps(1))
    planes = tuple(subgroup.cusps(2))
    for position, cusp in enumerate(lines):
        log(f"[{label}] line cusp {position}: {_coordinates(cusp.representative())}")
    for position, cusp in enumerate(planes):
        log(f"[{label}] plane cusp {position}: {_coordinates(cusp.representative())}")
    line_vertices = set()
    plane_vertices = set()
    retained_pairs = []
    for position, incidence in enumerate(incidences):
        line_id = cusp_position(lines, incidence.line_cusp())
        plane_id = cusp_position(planes, incidence.plane_cusp())
        if line_id is None or plane_id is None:
            which = "line" if line_id is None else "plane"
            return report_row_outcome(
                label,
                RowStatus.CONTRACT_VIOLATION,
                f"edge {position} of {len(incidences)}: its {which} cusp is not a cusp of the row",
            )
        pair = (line_id, plane_id)
        violation = edge_violation(subgroup, incidence)
        if violation is None and pair in retained_pairs:
            violation = (
                f"two edges share the line and plane cusp endpoints L{line_id} and P{plane_id}"
            )
        if violation is not None:
            return report_row_outcome(
                label,
                RowStatus.CONTRACT_VIOLATION,
                f"edge {position} of {len(incidences)}: {violation}",
            )
        retained_pairs.append(pair)
        line_vertices.add(incidence.line_cusp())
        plane_vertices.add(incidence.plane_cusp())
        log(
            f"[{label}] edge {position}: L{line_id} < P{plane_id}; "
            f"line={_coordinates(incidence.line())}; plane={_coordinates(incidence.plane())}"
        )
    for position, cusp in enumerate(lines):
        if cusp not in line_vertices:
            return report_row_outcome(
                label, RowStatus.CONTRACT_VIOLATION, f"line cusp {position} carries no edge"
            )
    for position, cusp in enumerate(planes):
        if cusp not in plane_vertices:
            return report_row_outcome(
                label, RowStatus.CONTRACT_VIOLATION, f"plane cusp {position} carries no edge"
            )
    log(
        f"[{label}] {len(incidences)} edges over {len(lines)} line cusps and "
        f"{len(planes)} plane cusps in {elapsed:.1f} s"
    )
    return (len(incidences), len(lines), len(planes)), RowStatus.DECIDED


def _rows(lattice):
    r"""Yield each row's label with its subgroup, built when the row is taken.

    The Gamma_{Co,2} subgroup is the image-preimage stabilizer of A_{U(2)} in the
    discriminant group, and building it costs far more than the first row's
    subgroup does; a row's subgroup is therefore built when that row runs, so the
    first row starts without waiting on the second.
    """
    yield "O(T_Co)", lattice.Aut()
    yield "Gamma_{Co,2}", lattice.Aut().discriminant_point_stabilizer(_decomposition(lattice))


def main(argv):
    r"""Run both incidence rows and report each row's outcome as an exit status.

    The statuses and exit statuses are ``tests/coble_row_status.py``'s: ``0``
    both rows decided as the decided relation, ``1`` a row undecided or the
    whole-run budget spent, ``2`` a returned edge that breaks the contract, and
    ``3`` a decided row whose counts are not the decided relation.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cap", type=float, default=10800,
                        help="seconds one row call may take before it is undecided")
    parser.add_argument("--budget", type=int, default=28800,
                        help="seconds the whole run may take, 0 for no budget")
    arguments = parser.parse_args(argv)
    started = time.monotonic()
    lattice = NamedLattices.Tco
    log(f"the Coble period lattice {lattice} of rank {lattice.module_rank()}")
    rows = {}
    for label, subgroup in _rows(lattice):
        if arguments.budget and time.monotonic() - started > arguments.budget:
            log("the whole-run budget is spent")
            return EXIT_UNDECIDED
        counts, status = run_row(lattice, subgroup, label, arguments.cap)
        if status is not RowStatus.DECIDED:
            return exit_status(status)
        rows[label] = counts
    if rows["O(T_Co)"][0] != 1:
        log("the O(T_Co) incidence through this route is not one edge")
        return EXIT_COUNT_MISMATCH
    if rows["Gamma_{Co,2}"] != (13, 4, 7):
        log("the Gamma_{Co,2} incidence is not the decided 13-edge relation over 4 line and 7 plane cusps")
        return EXIT_COUNT_MISMATCH
    log(
        f"the O(T_Co) incidence has {rows['O(T_Co)'][0]} edge; the Gamma_{{Co,2}} incidence has "
        f"{rows['Gamma_{Co,2}'][0]} edges over {rows['Gamma_{Co,2}'][1]} line orbits and "
        f"{rows['Gamma_{Co,2}'][2]} plane orbits"
    )
    return EXIT_DECIDED


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
