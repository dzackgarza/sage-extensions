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
* every plane orbit has an edge -- a plane of the row contains isotropic
  lines, their orbits are line cusps of the row, and the flag it makes with
  each of them is one of the flags the route enumerates.  A line orbit is not
  required to carry one: a line vertex carries an edge exactly when the row's
  group carries a line of it into a plane cusp of the row, which is what an
  edge is, and a subgroup that fixes a plane has an orbit of lines outside it.
  The row's counts pin the line orbits anyway;
* the ``O(T_Co)`` incidence has one edge -- the ambient group is the whole of
  ``O(T_Co)``, so the left group of every double-coset computation is the
  parabolic's own image and each plane contributes its one transitive orbit
  of lines; that is the value ``main`` held at ``85284b8d18``.

The counts each row prints are the numbers the commit body of the push that
lands this file records.

**What a row reports.**  A row that does not return inside its per-call cap is
reported as undecided, never as failed: the cap is the caller's budget, not a
mathematical statement.  A row that returns an edge, or a relation over its
vertices, which fails its check is reported apart from that, as a contract
violation, because it is a statement about the library's answer and not about
the budget: each returned edge's line must lie in its plane and one subgroup
element must carry the line cusp representative into the plane cusp
representative, and the edges together must be a relation -- no two sharing
their line and plane cusp endpoints, and every vertex that can carry an edge
carrying one.  The relation is the input of the contract and not something the
contract reaches for, so the contract is asked of a relation the row returned.
A row step that raises is reported as an error, neither of the two: the
traceback is printed and the run ends on the error's own exit status.  The
driver's exit status says which happened -- 0 both rows decided as the decided
relation, 1 a row undecided or the whole-run budget spent, 2 a returned edge or
relation that breaks the contract, 3 a decided row whose counts are not the
decided relation, 4 a row step that raised -- and the statuses and those exit
statuses are the vocabulary of ``tests/coble_row_status.py``, shared with the
kernel-plane-rows driver.

    sage -python tests/coble_gamma_co_2_incidence_rows.py            # both rows
    sage -python tests/coble_gamma_co_2_incidence_rows.py --cap 10800
    sage -python tests/coble_gamma_co_2_incidence_rows.py --budget 28800
"""

import argparse
import signal
import sys
import time
import traceback
from dataclasses import dataclass

from sage_extensions.all import *  # noqa: F401,F403

from coble_row_status import RowStatus


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


def containment_violation(lattice, line, plane) -> str | None:
    r"""Why an edge whose line and plane these are breaks the row's contract, or ``None``.

    Both terms of an edge are subobjects of the row's lattice, and the line lies
    in the plane exactly when the line's retained generator is in the image of
    the plane's inclusion.
    """
    if line.inclusion().codomain() is not lattice or plane.inclusion().codomain() is not lattice:
        return "its line and plane are not subobjects of the row's lattice"
    domain = line.inclusion().domain()
    label = next(iter(domain.module_generating_set()))
    if plane.inclusion().is_in_image(line.inclusion()(domain.module_generator(label))):
        return None
    return "its line is not contained in its plane"


def transport_violation(lattice, subgroup, incidence) -> str | None:
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
    return containment_violation(lattice, moved, incidence.plane_cusp().representative())


def edge_violation(lattice, subgroup, incidence) -> str | None:
    r"""Why one returned edge breaks the row's contract, or ``None``."""
    violation = containment_violation(lattice, incidence.line(), incidence.plane())
    if violation is not None:
        return violation
    return transport_violation(lattice, subgroup, incidence)


def cusp_position(cusps, cusp) -> int | None:
    r"""The position of ``cusp`` among ``cusps``, or ``None`` when it is not one of them."""
    for position, candidate in enumerate(cusps):
        if candidate is cusp or candidate == cusp:
            return position
    return None


@dataclass(frozen=True)
class RowOutcome:
    r"""What one row of this driver did, and what it returned when it decided.

    ``status`` is the row's status, ``detail`` names the clause that broke, the
    cap that expired or the exception the row step raised -- the words one
    report of the row is made of -- and ``counts`` is the row's edge, line cusp
    and plane cusp count for a decided row, and ``None`` for a row that did not
    decide.
    """

    label: str
    status: RowStatus
    detail: str
    counts: tuple | None = None

    def report(self) -> str:
        r"""The one line that reports this outcome."""
        return f"[{self.label}] {self.status.words}: {self.detail}"


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


def row_contract(lattice, subgroup, label, lines, planes, incidences) -> RowOutcome:
    r"""What the row's returned relation says: a decided row, or the clause that broke.

    The clauses are the row's statement about the relation it returned.  Every
    edge joins a line that lies in its plane, and one element of the subgroup
    carries the line cusp representative into the plane cusp representative;
    each edge's two cusps are cusps of the row; no two edges share their line
    and plane cusp endpoints, so the relation is not a flag-orbit count; and
    every plane cusp carries an edge.  A plane cusp always does: a plane of the
    row contains isotropic lines, their orbits are line cusps of the row, and
    the flag each of them makes with the plane is one of the flags the route
    enumerates.  A line cusp is not required to carry one, because a line vertex
    carries an edge exactly when the row's group carries a line of it into a
    plane cusp of the row -- which is what an edge is -- and that is not every
    line: a subgroup that fixes a plane has an orbit of lines outside it, and a
    lattice with no isotropic plane has no edge at all.

    The returned relation is the input, so the contract is a statement about
    the library's answer and not about how the row was obtained.
    """
    for position, cusp in enumerate(lines):
        log(f"[{label}] line cusp {position}: {_coordinates(cusp.representative())}")
    for position, cusp in enumerate(planes):
        log(f"[{label}] plane cusp {position}: {_coordinates(cusp.representative())}")
    plane_vertices = set()
    retained_pairs = []
    for position, incidence in enumerate(incidences):
        line_id = cusp_position(lines, incidence.line_cusp())
        plane_id = cusp_position(planes, incidence.plane_cusp())
        if line_id is None or plane_id is None:
            which = "line" if line_id is None else "plane"
            return RowOutcome(
                label,
                RowStatus.CONTRACT_VIOLATION,
                f"edge {position} of {len(incidences)}: its {which} cusp is not a cusp of the row",
            )
        pair = (line_id, plane_id)
        violation = edge_violation(lattice, subgroup, incidence)
        if violation is None and pair in retained_pairs:
            violation = (
                f"two edges share the line and plane cusp endpoints L{line_id} and P{plane_id}"
            )
        if violation is not None:
            return RowOutcome(
                label,
                RowStatus.CONTRACT_VIOLATION,
                f"edge {position} of {len(incidences)}: {violation}",
            )
        retained_pairs.append(pair)
        plane_vertices.add(incidence.plane_cusp())
        log(
            f"[{label}] edge {position}: L{line_id} < P{plane_id}; "
            f"line={_coordinates(incidence.line())}; plane={_coordinates(incidence.plane())}"
        )
    for position, cusp in enumerate(planes):
        if cusp not in plane_vertices:
            return RowOutcome(
                label, RowStatus.CONTRACT_VIOLATION, f"plane cusp {position} carries no edge"
            )
    return RowOutcome(
        label,
        RowStatus.DECIDED,
        f"{len(incidences)} edges over {len(lines)} line cusps and {len(planes)} plane cusps",
        (len(incidences), len(lines), len(planes)),
    )


def run_row(lattice, subgroup, label, cap) -> RowOutcome:
    r"""What one incidence row of ``subgroup`` did, within its ``cap``.

    The row step is the public call ``tits_building_incidence()`` with the row's
    cusps, under the per-row cap, and then the row's contract on the relation
    the call returned.  The cap is the caller's budget: a cap of no seconds
    leaves no time for the call and the row is undecided without the call being
    made, and the alarm it sets reaches the call where Python holds control --
    a call that does not hand control back to Python is not interrupted by it,
    so the cap is the budget of a row and not a promise about where it stops.

    The row step raising is neither an undecided row nor a broken contract: the
    traceback is printed and the status says the step raised, so a failed call
    is not reported as a caller who ran out of time.
    """
    if cap <= 0:
        return RowOutcome(
            label, RowStatus.UNDECIDED, f"its cap of {cap:g} s is spent before the call"
        )
    start = time.monotonic()
    previous_handler = signal.signal(signal.SIGALRM, _alarm)
    try:
        signal.setitimer(signal.ITIMER_REAL, cap)
        try:
            incidences = tuple(subgroup.tits_building_incidence())
            lines = tuple(subgroup.cusps(1))
            planes = tuple(subgroup.cusps(2))
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        log(f"[{label}] the row's calls returned in {time.monotonic() - start:.1f} s")
        return row_contract(lattice, subgroup, label, lines, planes, incidences)
    except RowUndecided:
        return RowOutcome(
            label, RowStatus.UNDECIDED, f"the row did not return inside its {cap:g} s cap"
        )
    except Exception as error:
        traceback.print_exc()
        return RowOutcome(
            label, RowStatus.ERROR, f"the row step raised {type(error).__name__}: {error}"
        )
    finally:
        signal.signal(signal.SIGALRM, previous_handler)


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
    whole-run budget spent, ``2`` a returned edge or relation that breaks the
    contract, ``3`` a decided row whose counts are not the decided relation, and
    ``4`` a row step that raised.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cap", type=float, default=10800,
                        help="seconds one row may take before it is undecided; 0 leaves no time")
    parser.add_argument("--budget", type=int, default=28800,
                        help="seconds the whole run may take, 0 for no budget")
    arguments = parser.parse_args(argv)
    started = time.monotonic()
    lattice = NamedLattices.Tco
    log(f"the Coble period lattice {lattice} of rank {lattice.module_rank()}")
    counts = {}
    for label, subgroup in _rows(lattice):
        if arguments.budget and time.monotonic() - started > arguments.budget:
            log(f"[run] {RowStatus.UNDECIDED.words}: the whole-run budget is spent")
            return RowStatus.UNDECIDED.exit_status
        outcome = run_row(lattice, subgroup, label, arguments.cap)
        log(outcome.report())
        if outcome.status is not RowStatus.DECIDED:
            return outcome.status.exit_status
        counts[label] = outcome.counts
    if counts["O(T_Co)"][0] != 1:
        log("the O(T_Co) incidence through this route is not one edge")
        return RowStatus.COUNT_MISMATCH.exit_status
    if counts["Gamma_{Co,2}"] != (13, 4, 7):
        log("the Gamma_{Co,2} incidence is not the decided 13-edge relation over 4 line and 7 plane cusps")
        return RowStatus.COUNT_MISMATCH.exit_status
    log(
        f"the O(T_Co) incidence has {counts['O(T_Co)'][0]} edge; the Gamma_{{Co,2}} incidence has "
        f"{counts['Gamma_{Co,2}'][0]} edges over {counts['Gamma_{Co,2}'][1]} line orbits and "
        f"{counts['Gamma_{Co,2}'][2]} plane orbits"
    )
    return RowStatus.DECIDED.exit_status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
