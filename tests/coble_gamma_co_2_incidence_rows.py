r"""The Tits-building incidence rows on the Coble lattice, through the public call.

This is the acceptance entry point of #391 and of #381's last step: the
incidence between the line orbits and the plane orbits of ``T_Co`` under each
of the four groups whose rows return -- ``O(T_Co)``, ``Gamma_{Co,2}``,
``Otilde(T_Co) = ker rho`` and ``Otilde+(T_Co) = ker(rho, sn_RR)``.  It is not
collected by pytest (its file name does not begin with ``test_``), because
these rows are measured in minutes and share one subgroup/orbit/cusp cache;
they belong in the dedicated CI job, not repeated throughout the per-test
gate.  The two rows of #391 fit the runtime's 6144 MiB guard: the measured
two-row run peaked at 3718 MiB tree RSS.  The two kernel rows of #381 are the
rows of ``coble_kernel_plane_rows.py`` read at their planes, so they are the
row selection ``--rows Otilde,Otilde+``, not the default.

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

**The kernel rows.**  ``Otilde`` and ``Otilde+`` cut the discriminant image
instead of forcing it: ``chi(Otilde)`` is trivial and ``chi(Otilde+)`` is
trivial, so the double cosets at a plane are the plain cosets of
``chi(Stab P)`` in ``chi(O(L))``, and the incidence call reads them by the
same parabolic covering.  Their plane rows are 189720 planes each (#390), so
the incidence of those two rows is dispatched as its own job, and each row's
edges are recorded per group; no count is typed, because the two rows have no
card (lattice-database#7).

**What is asserted.**  The decided Gamma relation has 13 edges over four line
cusps and seven plane cusps.  No lattice-database card holds a ``T_Co`` value
(lattice-database#7); this acceptance value is checked against representatives
from both the pinned and the image's indefinite-port checkouts.  In addition,
the cited construction guarantees for every output of the incidence call on
any lattice whose rows return through this route:

* each edge joins a line that lies in its plane -- the edge's line term is
  contained in its plane term, and one subgroup element carries the selected
  line cusp representative into the selected plane cusp representative;
* the incidence is a relation, not a flag-orbit count -- no two retained edges
  have the same line and plane cusp endpoints;
* every plane orbit has an edge -- a plane of the row contains isotropic
  lines, their orbits are line cusps of the row, and the flag it makes with
  each of them is one of the flags the route enumerates;
* every line orbit has an edge as soon as the row has a plane orbit -- a
  totally isotropic subspace extends to a maximal one, all maximal ones have
  the dimension of the Witt index (``witt_index``, after O'Meara,
  *Introduction to Quadratic Forms*, Section 42F), and a row with a plane orbit
  has Witt index at least two; the saturation of the plane the line spans is
  then a primitive isotropic plane of the lattice, and the flag the two make is
  one the route enumerates, so its edge has the line's cusp as its line vertex
  (D. Dutour Sikiri\'c and K. Hulek, arXiv:2302.01679v2, printed p. 5: the
  edges are the inclusion relation between the two kinds of vertex).  A row
  without a plane orbit -- ``U + <-2>`` has signature ``(1, 2)`` -- has line
  vertices only, and a line vertex there is decided with no edge because there
  is no plane vertex for it to be incident with;
* the ``O(T_Co)`` incidence has one edge -- the ambient group is the whole of
  ``O(T_Co)``, so the left group of every double-coset computation is the
  parabolic's own image and each plane contributes its one transitive orbit
  of lines; that is the value ``main`` held at ``85284b8d18``.

For the two kernel rows the same construction guarantees, and this driver
checks, the first three clauses too -- their counts are recorded and not
compared with anything, and the one comparison that does hold is between the
two rows: ``Otilde+`` is a subgroup of ``Otilde``, so its line and plane rows
have at least as many cusps as ``Otilde``'s.  The edge count of a kernel row
is *not* monotone in the group: a finer group has more vertices, so a coarser
group's edge is not one of its edges.

**The small-lattice check.**  ``--lattice`` reads the same driver on a lattice
whose rows the gate can afford, so the code that the dispatched job runs is
exercised in minutes:
``--lattice 6JRS=U+U+<-2>`` has ``|O(A_L)| = 1``, hence ``Otilde = O(L)`` and
``Otilde+ = O^+(L)``, and the driver's rows must equal the ambient rows; on
``U+U(2)+<-2>`` the discriminant image is non-trivial (``|O(A_L)| = 2``) and
the kernel rows split into three line cusps and two plane cusps of their own.
``tests/lattices/test_the_kernel_incidence_rows.sage`` gates the same two
lattices on the same guarantees, and additionally on the subgroup's own flag
row, which is the relation read through a different public call.

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
their line and plane cusp endpoints, every plane vertex carrying an edge, and
every line vertex carrying one whenever the row has a plane vertex.  The
relation is the input of the contract and not something the contract reaches
for, so the contract is asked of a relation the row returned.
A row step that raises is reported as an error, neither of the two: the
traceback is printed and the run ends on the error's own exit status.  The
driver's exit status says which happened -- 0 both rows decided as the decided
relation, 1 a row undecided or the whole-run budget spent, 2 a returned edge or
relation that breaks the contract, 3 a decided row whose counts are not the
decided relation, 4 a row step that raised -- and the statuses and those exit
statuses are the vocabulary of ``tests/coble_row_status.py``, shared with the
kernel-plane-rows driver.

    sage -python tests/coble_gamma_co_2_incidence_rows.py            # the two #391 rows
    sage -python tests/coble_gamma_co_2_incidence_rows.py --cap 10800
    sage -python tests/coble_gamma_co_2_incidence_rows.py --budget 28800
    sage -python tests/coble_gamma_co_2_incidence_rows.py \
        --rows 'Otilde,Otilde+' --lattice Tco                     # the #381 rows
    sage -python tests/coble_gamma_co_2_incidence_rows.py \
        --rows 'Otilde,Otilde+' --lattice 6JRS                    # the small-lattice check
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


def cusp_positions(cusps):
    r"""The position of every cusp of a row, by identity, for the relation to be read in one pass.

    The relation of a kernel row has one edge per plane, and each edge names its
    two vertices; scanning the vertex rows for each of them is one comparison
    per vertex of the row at every edge, which a row of 189720 planes cannot
    pay.  The cusps an edge names are the row's own retained objects, so
    identity answers; a cusp that is not one of them is compared by the cusp's
    own equivalence, which is a witness question and stays the slow path.
    """
    ordering = {id(cusp): position for position, cusp in enumerate(cusps)}
    retained = tuple(cusps)

    def position(cusp) -> int | None:
        by_identity = ordering.get(id(cusp))
        if by_identity is not None:
            return by_identity
        for candidate_position, candidate in enumerate(retained):
            if candidate == cusp:
                return candidate_position
        return None

    return position


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
    and plane cusp endpoints, so the relation is not a flag-orbit count; every
    plane cusp carries an edge; and, when the row has a plane cusp, every line
    cusp carries one too.

    A plane cusp always carries an edge: a plane of the row contains isotropic
    lines, their orbits are line cusps of the row, and the flag each of them
    makes with the plane is one of the flags the route enumerates.  A line cusp
    carries one exactly when the row has a plane cusp: a totally isotropic
    subspace extends to a maximal one, all maximal ones have the dimension of
    the Witt index (``witt_index``, after O'Meara, *Introduction to Quadratic
    Forms*, Section 42F), a row with a plane cusp has Witt index at least two,
    and the saturation of the plane a line spans is then a primitive isotropic
    plane of the lattice; the flag the line and that plane make is one the
    route enumerates, and its edge has the line's cusp as its line vertex
    (Dutour Sikiri\'c--Hulek, arXiv:2302.01679v2, printed p. 5: the edges are
    the inclusion relation between the two kinds of vertex).  A row without a
    plane cusp has line vertices only, and a line vertex is then decided with no
    edge, because there is no plane vertex to be incident with -- ``U + <-2>``
    has signature ``(1, 2)`` and is the smallest such row.

    The returned relation is the input, so the contract is a statement about
    the library's answer and not about how the row was obtained.
    """
    for position, cusp in enumerate(lines):
        log(f"[{label}] line cusp {position}: {_coordinates(cusp.representative())}")
    for position, cusp in enumerate(planes):
        log(f"[{label}] plane cusp {position}: {_coordinates(cusp.representative())}")
    line_vertices = set()
    plane_vertices = set()
    retained_pairs = set()
    line_position = cusp_positions(lines)
    plane_position = cusp_positions(planes)
    for position, incidence in enumerate(incidences):
        line_id = line_position(incidence.line_cusp())
        plane_id = plane_position(incidence.plane_cusp())
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
        retained_pairs.add(pair)
        line_vertices.add(line_id)
        plane_vertices.add(plane_id)
        log(
            f"[{label}] edge {position}: L{line_id} < P{plane_id}; "
            f"line={_coordinates(incidence.line())}; plane={_coordinates(incidence.plane())}"
        )
    for position in range(len(planes)):
        if position not in plane_vertices:
            return RowOutcome(
                label, RowStatus.CONTRACT_VIOLATION, f"plane cusp {position} carries no edge"
            )
    if planes:
        for position in range(len(lines)):
            if position not in line_vertices:
                return RowOutcome(
                    label, RowStatus.CONTRACT_VIOLATION, f"line cusp {position} carries no edge"
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


ROW_LABELS = ("O", "Gamma_{Co,2}", "Otilde", "Otilde+")

# A label may carry a comma of its own, so a specification is read against the
# labels and never split on commas blindly; the longest label that starts the
# rest is the row it names.
_LABELS_LONGEST_FIRST = tuple(sorted(ROW_LABELS, key=len, reverse=True))


def selected_rows(specification) -> tuple[tuple[str, ...], str | None]:
    r"""The rows a comma-separated specification names, and the rest it cannot read.

    ``Gamma_{Co,2}`` carries a comma, so ``--rows O,Gamma_{Co,2}`` has three
    comma-separated pieces and two rows.  The specification is therefore read
    against ``ROW_LABELS`` from the longest label down: the longest label that
    starts the unread rest is the row it names, a comma after it separates the
    next name, and a rest that starts with no label is returned as the text the
    run reports as not a row of this driver.
    """
    names = []
    remaining = specification.strip()
    while remaining:
        label = next(
            (
                candidate for candidate in _LABELS_LONGEST_FIRST
                if remaining.startswith(candidate)
            ),
            None,
        )
        if label is None:
            return tuple(names), remaining
        names.append(label)
        remaining = remaining[len(label):].lstrip()
        if remaining.startswith(","):
            remaining = remaining[1:].lstrip()
    return tuple(names), None


def _row_subgroup(lattice, label):
    r"""The subgroup of one row, built when the row runs.

    The Gamma_{Co,2} subgroup is the image-preimage stabilizer of A_{U(2)} in the
    discriminant group, and building it costs far more than the first row's
    subgroup does; a row's subgroup is therefore built when that row runs, so the
    first row starts without waiting on the second.  The two kernel rows are
    ``Otilde = ker rho`` and ``Otilde+ = ker(rho, sn_RR)``, the rows of #390.
    """
    match label:
        case "O":
            return lattice.Aut()
        case "Gamma_{Co,2}":
            return lattice.Aut().discriminant_point_stabilizer(_decomposition(lattice))
        case "Otilde":
            return lattice.stable_orthogonal_group()
        case "Otilde+":
            return lattice.stable_orthogonal_group().intersection(lattice.O_plus())
    raise ValueError(f"{label} is not a row of the incidence driver, which has {ROW_LABELS}")


def _lattice_by_name(name):
    r"""The lattice one driver run is about: the Coble lattice, or a specimen the gate can afford.

    ``Tco`` is the object of the dispatched job.  The others exist so that the
    code this job runs is exercised on a lattice whose rows return in seconds:
    ``6JRS = U + U + <-2>`` has ``|O(A_L)| = 1``, hence ``Otilde = O(L)``, and
    ``U+U(2)+<-2>`` has ``|O(A_L)| = 2``, so each kernel row there is a
    genuinely smaller group than its ambient row's.  Both are gate lattices of
    the kernel plane rows (``test_the_stable_plane_rows_...``).
    """
    match name:
        case "Tco":
            return NamedLattices.Tco
        case "6JRS":
            return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])
        case "U+U+<-4>":
            return Lattices(ZZ)("U") + Lattices(ZZ)("U") + Lattices(ZZ)([[-4]])
        case "U+U(2)+<-4>":
            return (
                Lattices(ZZ)("U")
                + Lattices(ZZ)([[0, 2], [2, 0]])
                + Lattices(ZZ)([[-4]])
            )
        case "U+U(2)+<-2>":
            return (
                Lattices(ZZ)("U")
                + Lattices(ZZ)([[0, 2], [2, 0]])
                + Lattices(ZZ)([[-2]])
            )
        case "6JRX":
            return _scattone(1)
        case "6JRY":
            return _scattone(2)
    raise ValueError(f"{name} is not a lattice of this driver")


def _scattone(k):
    r"""``Lambda_{2k} = U^2 + E8(-1)^2 + <-2k>``, the rank-21 cards 6JRX and 6JRY."""
    return (
        Lattices(ZZ)("U")
        + Lattices(ZZ)("U")
        + Lattices(ZZ)("E8")
        + Lattices(ZZ)("E8")
        + Lattices(ZZ)([[-2 * k]])
    )


LATTICE_NAMES = ("Tco", "6JRS", "U+U+<-4>", "U+U(2)+<-2>", "U+U(2)+<-4>", "6JRX", "6JRY")


def _trivial_image_row_agreement(lattice, rows):
    r"""Why a kernel row differs from its ambient row where ``rho`` is trivial, or ``None``.

    ``Otilde`` is the kernel of the discriminant representation, so where
    ``|O(A_L)| = 1`` it *is* ``O(L)``; the sign condition that cuts ``Otilde+``
    out of ``Otilde`` is then the whole of the index-two subgroup
    ``lattice.O_plus()``, so both kernel rows are the ambient rows and their
    counts are not free -- they are the ambient counts, computed here through
    the ambient group objects.  That is the one place the driver compares a
    counted number with another, and it makes the small-lattice run
    self-checking; on a lattice with a non-trivial discriminant image the
    function returns ``None`` -- there is nothing to compare, and the rows are
    recorded only.
    """
    target = lattice.discriminant_group().orthogonal_group()
    if target.cardinality() != cardinal(1):
        return None
    log(
        f"the discriminant image of {lattice} is trivial, so each kernel row is its "
        "ambient row's; comparing the counts"
    )
    ambient = lattice.Aut()
    for label, other in (("Otilde", ambient), ("Otilde+", lattice.O_plus())):
        if label not in rows:
            continue
        edges, line_count, plane_count = rows[label]
        other_lines = int(other.cusps(1).cardinality())
        other_planes = int(other.cusps(2).cardinality())
        if (line_count, plane_count) != (other_lines, other_planes):
            return (
                f"the {label} row has {line_count} line and {plane_count} plane cusps, "
                f"but the discriminant image of {lattice} is trivial, so its rows are "
                f"the ambient ones: {other_lines} line and {other_planes} plane cusps"
            )
        other_edges = int(other.tits_building_incidence().cardinality())
        if edges != other_edges:
            return (
                f"the {label} row has {edges} edges, but the discriminant image of "
                f"{lattice} is trivial, so its incidence is the ambient one's, "
                f"which has {other_edges}"
            )
    log(f"each kernel row agrees with the ambient row of {lattice}")
    return None


def main(argv):
    r"""Run the selected incidence rows and report each row's outcome as an exit status.

    The statuses and exit statuses are ``tests/coble_row_status.py``'s: ``0``
    every selected row decided as the decided relation, ``1`` a row undecided or
    the whole-run budget spent, ``2`` a returned edge or relation that breaks the
    contract, ``3`` a decided row whose counts are not the decided relation, and
    ``4`` a row step that raised.  On ``T_Co`` the decided relation is ``O``: one
    edge, and ``Gamma_{Co,2}``: 13 edges over 4 line and 7 plane cusps (#391);
    on a lattice whose discriminant image is trivial the kernel rows are decided
    by their ambient rows instead (:func:`_trivial_image_row_agreement`), and on
    any other lattice the rows are recorded, with ``Otilde+``'s two vertex counts
    at least ``Otilde``'s.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cap", type=float, default=10800,
                        help="seconds one row may take before it is undecided; 0 leaves no time")
    parser.add_argument("--budget", type=int, default=28800,
                        help="seconds the whole run may take, 0 for no budget")
    parser.add_argument("--rows", default="O,Gamma_{Co,2}",
                        help=f"comma-separated rows to run, from {ROW_LABELS}")
    parser.add_argument("--lattice", default="Tco",
                        help=f"the lattice to run on, from {LATTICE_NAMES}")
    arguments = parser.parse_args(argv)
    selected, unread = selected_rows(arguments.rows)
    if unread is not None:
        log(f"[run] {RowStatus.ERROR.words}: {unread} is not a row of this driver, which has {ROW_LABELS}")
        return RowStatus.ERROR.exit_status
    started = time.monotonic()
    lattice = _lattice_by_name(arguments.lattice)
    log(f"the lattice {lattice} of rank {lattice.module_rank()}")
    log(f"the rows {selected}")
    counts = {}
    for label in selected:
        if arguments.budget and time.monotonic() - started > arguments.budget:
            log(f"[run] {RowStatus.UNDECIDED.words}: the whole-run budget is spent")
            return RowStatus.UNDECIDED.exit_status
        outcome = run_row(lattice, _row_subgroup(lattice, label), label, arguments.cap)
        log(outcome.report())
        if outcome.status is not RowStatus.DECIDED:
            return outcome.status.exit_status
        counts[label] = outcome.counts
    if lattice is NamedLattices.Tco:
        if "O" in counts and counts["O"][0] != 1:
            log("the O(T_Co) incidence through this route is not one edge")
            return RowStatus.COUNT_MISMATCH.exit_status
        if "Gamma_{Co,2}" in counts and counts["Gamma_{Co,2}"] != (13, 4, 7):
            log("the Gamma_{Co,2} incidence is not the decided 13-edge relation over 4 line and 7 plane cusps")
            return RowStatus.COUNT_MISMATCH.exit_status
    disagreement = _trivial_image_row_agreement(lattice, counts)
    if disagreement is not None:
        log(f"[run] {RowStatus.COUNT_MISMATCH.words}: {disagreement}")
        return RowStatus.COUNT_MISMATCH.exit_status
    if "Otilde" in counts and "Otilde+" in counts:
        coarse, fine = counts["Otilde"], counts["Otilde+"]
        if fine[1] < coarse[1] or fine[2] < coarse[2]:
            log(
                f"the Otilde+ row has {fine[1]} line and {fine[2]} plane cusps against "
                f"Otilde's {coarse[1]} and {coarse[2]}, but Otilde+ is a subgroup of "
                "Otilde, so its vertex rows cannot be smaller"
            )
            return RowStatus.COUNT_MISMATCH.exit_status
    log(
        "recorded counts: "
        + "; ".join(
            f"{label} {row[0]} edges over {row[1]} line and {row[2]} plane cusps"
            for label, row in counts.items()
        )
    )
    return RowStatus.DECIDED.exit_status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
