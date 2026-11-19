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

**Two routes, one relation.**  Two public calls decide that relation.
``tits_building_incidence()`` carries a covering of the plane's lines to each
plane as flags, and keeps one certificate per endpoint pair -- the flag, the
two cusps and one transporter to each.  A carried flag is a constructed parent,
and this library retains every constructed parent for the process, so that
route's records cost a flag and two transporters a plane: 249 016 B and 13.68
ms a plane on ``T_Co``'s ``Otilde`` row.
``tits_building_incidence_by_divided_classes()`` decides the same edges from
the divided class of each carried line; its records are
``DividedClassCuspIncidence`` -- two cusps and the ``rho(Gamma)``-orbit that
named the line vertex, no flag, no subobject, no transporter -- at 1 427 B and
1.65 ms a plane on the same row.  ``--route`` chooses between them:
``divided-class``, ``certificate``, or ``auto`` (the default), which takes the
class route wherever it applies and the certificate route only where the class
route states it cannot decide the row -- a subgroup cutting no discriminant
condition, and a subgroup that is not invariant under conjugation -- and logs
which route it took and why at every row.  The two are one relation and not two
answers: ``tests/lattices/test_the_incidence_decided_by_divided_classes.sage``
compares both routes' relations, as endpoint pairs, with the subgroup's own
flag row, which is a third computation of it.

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
  line cusp representative into the selected plane cusp representative.  This
  is the certificate route's clause, and the only route whose records carry
  those terms: a ``DividedClassCuspIncidence`` has no line term and no
  transporter, so the clause its own record carries is that the edge's
  divided-class orbit is the one its line cusp is indexed by, read here from
  the row's cusps and not from the datum; containment for a class route's edge
  is the statement the gate makes where the two routes are compared;
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
the budget: each returned edge carries the clause its route's record can state
-- on the certificate route, that its line lies in its plane and that one
subgroup element carries the line cusp representative into the plane cusp
representative; on the class route, that the divided-class orbit it names is
the orbit its line cusp is indexed by -- and the edges together must be a
relation -- no two sharing their line and plane cusp endpoints, every plane
vertex carrying an edge, and every line vertex carrying one whenever the row
has a plane vertex.  The
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
    sage -python tests/coble_gamma_co_2_incidence_rows.py \
        --rows 'Otilde,Otilde+' --lattice Tco --route certificate # the flag-carrying route
"""

import argparse
import hashlib
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


INTEGRAL_ARCHIVE = (
    "the 569160-edge integral archive of #286's table (research Actions 44170494099)"
)
PAGE_UNPOLARIZED = "the page's thm:unpolarized-cusps, one orbit of each kind"
PREVIOUS_ROW = "the Γ_{Co,2} row decided in #391"


RECORDED_COMPARISONS = []


def record_comparison(label, statement, computed, recorded, source) -> bool:
    r"""Record a computed value beside the value a source states, and never gate on it.

    A row's job is to report what it returned.  A number a page or an archive
    states is a comparison for the reader, not a condition the row has to meet:
    making it a condition turns the run's green into a restatement of the number
    rather than an independent computation, and it turns a disagreement -- which
    #286 files on research the same day, naming the class where they differ --
    into a failed job.  So the computed value is printed with the source that
    states the recorded one and with the word ``agrees`` or ``DIFFERS``, and the
    agreement is returned for a caller that keeps the tally.  Nothing calls the
    row's status with it.
    """
    agrees = computed == recorded
    RECORDED_COMPARISONS.append((label, statement, computed, recorded, agrees))
    log(
        f"[{label}] {statement}: computed {computed}; {source} states {recorded} — "
        f"{'agrees' if agrees else 'DIFFERS'}"
    )
    return agrees


def record_plane_class_indices(label, subgroup, planes, limit=8) -> tuple:
    r"""Record `[Stab_{O(q)}(J) : rho(Stab_Gamma(P))]` at the row's first `limit` plane classes.

    `J = [P/2]` is the order-four totally isotropic subgroup a plane's divided
    classes span, and the index is the plane analogue of the line row's
    `[Stab_{O(q)}(v̄) : ρ(Stab_Γ(v))]`: the number of the subgroup's plane orbits
    inside one class `J`.

    **Every row records it**, and the route is the row's own:

    * a subgroup cut out by characters reads it from the finite image
      (`OrthogonalCharacterQuotient.plane_class_index`: the meet
      `chi(Gamma) cap chi(Pi)` against the stabilizer of the class set);
    * the ambient `O(L)`, which retains no character quotient, reads it from the
      plane's own parabolic (`stabilizer_discriminant_image_orders`: the
      stabilizer of the class set against the image of the certified parabolic's
      generators).  That is the pair `#360` measures at a `T_Co` plane as
      `(1981808640, 247726080)`, index 8.

    Two finite orders a class, and no new integral computation.  A row of `T_Co`
    has 189720 plane cusps over 23715 classes, so a bounded number of classes is
    what one command records, and the bound is stated with the answer.

    The answer is the pairs `(classes, index)` recorded, so a caller compares
    them and no value here is a condition on the row.
    """
    characteristic = getattr(subgroup, "finite_character_quotient", None)
    quotient = characteristic() if characteristic is not None else None
    route = "the finite character image" if quotient is not None else "the plane's parabolic"
    log(f"[{label}] the plane class index is read by {route}")
    recorded = []
    seen = set()
    for plane_cusp in planes:
        if len(recorded) >= limit:
            break
        plane = plane_cusp.representative()
        if quotient is not None:
            classes, stabilizer_order, image_order, index = quotient.plane_class_index(plane)
            lattice = quotient.lattice
        else:
            lattice = subgroup.domain()
            classes = _plane_class_set(lattice, plane)
            stabilizer_order, image_order = plane.stabilizer_discriminant_image_orders()
            index = stabilizer_order // image_order
        key = frozenset(classes)
        if key in seen:
            continue
        seen.add(key)
        recorded.append((tuple(classes), index))
        log(
            f"[{label}] plane class {len(recorded)} of J = [P/2]: "
            f"|Stab_{{O(q)}}(J)| = {stabilizer_order}, "
            f"|rho(Stab_Gamma(P))| = {image_order}, index {index}"
        )
    indices = {index for _classes, index in recorded}
    log(
        f"[{label}] the plane class index over {len(recorded)} of the row's distinct classes J "
        f"(bounded at {limit}; the row has {len(planes)} plane cusps): "
        f"{len(indices)} distinct value{'s' if len(indices) != 1 else ''}"
    )
    if recorded:
        stabilizer_order = (
            quotient.plane_class_index(planes[0].representative())[1]
            if quotient is not None
            else planes[0].representative().stabilizer_discriminant_image_orders()[0]
        )
        log(
            f"[{label}] the liftable classes J number |O(q)| / |Stab(J)| = "
            f"{int(lattice.discriminant_group().O().cardinality()) // stabilizer_order} "
            f"at this row's first class"
        )
    return tuple(recorded)


def _plane_class_set(lattice, plane):
    r"""`J = [P/2]` for a plane, as the span of its divided classes.

    The three nonzero cosets of `P/2P` carry every divided class of the plane on
    a lattice whose discriminant group has exponent two, so the span of the
    classes of the plane's two generators and of their sum is the whole class
    set -- the same set the quotient reads, built here from the lattice's own
    `divided_discriminant_class`.
    """
    form = lattice.discriminant_group()
    inclusion = plane.inclusion()
    domain = inclusion.domain()
    basis = tuple(
        inclusion(domain.module_generator(label))
        for label in domain.module_generating_set()
    )
    closure = {form.zero()}
    for vector in (basis[0], basis[1], basis[0] + basis[1]):
        generator = lattice.divided_discriminant_class(vector)
        closure |= {element + generator for element in closure}
    return frozenset(closure)


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


def edge_violation(lattice, subgroup, incidence, *, include_coordinates=False):
    r"""Audit an edge, retaining coordinates only for a requested log sample.

    The full kernel relation contains 569160 edges.  Computing the coordinates
    of every certified flag is unnecessary to test its exact containment and
    subgroup transporters; only sampled flags need those coordinates printed.
    The complete mathematical checks and release of each flag are unchanged.
    """
    try:
        line, plane = incidence.flag().terms()
        line_coordinates = _coordinates(line) if include_coordinates else None
        plane_coordinates = _coordinates(plane) if include_coordinates else None
        violation = containment_violation(lattice, line, plane)
        if violation is not None:
            return violation, line_coordinates, plane_coordinates
        return transport_violation(lattice, subgroup, incidence), line_coordinates, plane_coordinates
    finally:
        # A certificate that reconstructs its flag from a retained basis
        # releases the reconstruction here; inspecting all 569160 Coble
        # kernel edges must not retain one rebuilt flag/subobject-parent
        # graph per inspected edge.  A certificate that holds the flag it was
        # built with (`CuspIncidence`, the ambient group's) has nothing to
        # release and keeps it.
        release = getattr(incidence, "release_flag", None)
        if release is not None:
            release()


def line_datum_key(quotient, cusp):
    r"""The divided-class datum the row indexes one of its line cusps by.

    This is the invariant the class route decides an edge with, read here from
    the cusp's own representative: the ``rho(Gamma)``-orbit of the divided
    class pair ``{c, -c}`` of a primitive isotropic line, which an element of
    the subgroup carries to the pair of the image line (Dutour Sikirić--Hulek,
    arXiv:2302.01679v2, Lemma 3.6, printed p. 22).  Two lines share it exactly
    when they lie in one orbit of the row's subgroup, which is what makes it
    the row's own index.
    """
    from sage_extensions.categories.orthogonal_quotients import (
        _isotropic_line_image_key,
    )

    return _isotropic_line_image_key(quotient, cusp.representative())


def divided_class_violation(incidence, keys) -> str | None:
    r"""Why a class route's edge breaks its own clause, or ``None``.

    A ``DividedClassCuspIncidence`` retains no flag, no subobject and no
    transporter: what it states is that its line vertex is the cusp whose
    divided-class orbit is the one it carries.  The clause is therefore read
    against the row's cusps -- each cusp's own key, computed here and not taken
    from the record -- so a record whose datum is not its line cusp's is a
    relation the class data does not state.
    """
    cusp = id(incidence.line_cusp())
    if cusp not in keys:
        return "its line cusp carries no divided-class datum of the row"
    if keys[cusp] != incidence.divided_classes():
        return (
            "its divided-class orbit is not the orbit its line cusp is indexed by, so the "
            "class data does not state this edge"
        )
    return None


ROW_ROUTES = ("auto", "divided-class", "certificate")


def chosen_route(subgroup, route):
    r"""The incidence route one row takes, and why when ``auto`` chose it.

    ``divided-class`` and ``certificate`` are the caller's own choice and carry
    no reason of ours.  ``auto`` prefers the class route and takes the
    certificate route exactly where the class route states it cannot decide the
    row: a group that retains no character quotient at all -- the ambient
    ``O(L)``, which the class route is not defined for -- a subgroup that cuts
    no discriminant condition, whose lines carry no class datum naming a cusp,
    and a subgroup that is not invariant under conjugation, which has no one
    covering to carry from plane to plane.  Each is the class route's own
    refusal, read here from the same fact, so the route a row takes is the
    driver's decision and is logged before the row runs.
    """
    if route != "auto":
        return route, ""
    characteristic = getattr(subgroup, "finite_character_quotient", None)
    if characteristic is None:
        return "certificate", (
            "it is the ambient orthogonal group, which retains no character quotient and so "
            "carries no divided-class datum"
        )
    quotient = characteristic()
    if not quotient.discriminant_preimages:
        return "certificate", (
            "it cuts no discriminant condition, so a line carries no class datum that names its cusp"
        )
    if not quotient.preserves_conjugation():
        return "certificate", (
            "it is not invariant under conjugation, so every plane's covering would have to be "
            "computed at that plane"
        )
    return "divided-class", (
        "its lines carry divided classes and its covering is carried from one plane to the others"
    )


def row_relation(subgroup, route):
    r"""The relation one row's route computes, from the call that route names."""
    if route == "divided-class":
        return subgroup.tits_building_incidence_by_divided_classes()
    return subgroup.tits_building_incidence()


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


def row_contract(lattice, subgroup, label, lines, planes, incidences, route) -> RowOutcome:
    r"""What the row's returned relation says: a decided row, or the clause that broke.

    The clauses are the row's statement about the relation it returned, and the
    first of them is the one its route's records carry.  The certificate route's
    edge joins a line that lies in its plane, and one element of the subgroup
    carries the line cusp representative into the plane cusp representative; a
    class route's edge has no line term and no transporter, and its clause is
    that the divided-class orbit it names is the orbit its line cusp is indexed
    by.  Containment for a class route's edge is the gate's statement, made
    where the two routes' relations are compared with the subgroup's own flag
    row.

    What both routes' edges state is read here: each edge's two cusps are cusps
    of the row; no two edges share their line and plane cusp endpoints, so the
    relation is not a flag-orbit count; every plane cusp carries an edge; and,
    when the row has a plane cusp, every line cusp carries one too.

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
    # The complete Coble relation has 569160 edges and 189720 plane cusps.
    # Printing every record can exhaust the Actions log before the mathematical
    # verdict.  Audit every record, but print bounded endpoint samples and a
    # deterministic digest of the entire ordered edge relation.
    for name, cusps in (("line", lines), ("plane", planes)):
        for position in sorted(set(range(min(3, len(cusps)))) |
                               set(range(max(3, len(cusps) - 3), len(cusps)))):
            log(f"[{label}] {name} cusp {position}: {_coordinates(cusps[position].representative())}")
    keys = {}
    if route == "divided-class":
        quotient = subgroup.finite_character_quotient()
        keys = {id(cusp): line_datum_key(quotient, cusp) for cusp in lines}
    line_vertices = set()
    plane_vertices = set()
    line_degrees = [0] * len(lines)
    plane_degrees = [0] * len(planes)
    retained_pairs = set()
    edge_digest = hashlib.sha256()
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
        if route == "divided-class":
            violation = divided_class_violation(incidence, keys)
        else:
            violation, line_coordinates, plane_coordinates = edge_violation(
                lattice, subgroup, incidence,
                include_coordinates=(position < 3 or position >= len(incidences) - 3),
            )
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
        edge_digest.update(f"{line_id}:{plane_id}\n".encode("ascii"))
        line_vertices.add(line_id)
        plane_vertices.add(plane_id)
        line_degrees[line_id] += 1
        plane_degrees[plane_id] += 1
        if position < 3 or position >= len(incidences) - 3:
            if route == "divided-class":
                log(f"[{label}] edge {position}: L{line_id} < P{plane_id}")
            else:
                log(
                    f"[{label}] edge {position}: L{line_id} < P{plane_id}; "
                    f"line={line_coordinates}; plane={plane_coordinates}"
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
    log(
        f"[{label}] the degree sequence of the relation: line cusps "
        f"{sorted(set(line_degrees))} over {len(line_degrees)}, plane cusps "
        f"{sorted(set(plane_degrees))} over {len(plane_degrees)}"
    )
    if lattice is NamedLattices.Tco and label in ("Otilde", "Otilde+"):
        # What the independent 569160-flag integral archive states about these
        # two rows: 527 line classes each incident with 1080 plane classes, and
        # 189720 plane classes each incident with three line classes.  Both are
        # *recorded* against it, not required of the row: cardinalities alone
        # would not detect an incorrect incidence graph with the same edge
        # count, so the degree sequence is reported for the reader to compare.
        record_comparison(
            label,
            "the Coble kernel line cusps' degrees",
            tuple(sorted(set(line_degrees))),
            (1080,),
            INTEGRAL_ARCHIVE,
        )
        record_comparison(
            label,
            "the Coble kernel plane cusps' degrees",
            tuple(sorted(set(plane_degrees))),
            (3,),
            INTEGRAL_ARCHIVE,
        )
    log(f"[{label}] audited {len(incidences)} distinct edges; ordered endpoint SHA-256: {edge_digest.hexdigest()}")
    return RowOutcome(
        label,
        RowStatus.DECIDED,
        f"{len(incidences)} edges over {len(lines)} line cusps and {len(planes)} plane cusps",
        (len(incidences), len(lines), len(planes)),
    )


def run_row(lattice, subgroup, label, cap, route="auto") -> RowOutcome:
    r"""What one incidence row of ``subgroup`` did, within its ``cap``.

    The row step is the public call the row's route names --
    ``tits_building_incidence_by_divided_classes()`` or
    ``tits_building_incidence()``, resolved by :func:`chosen_route` and logged
    with the reason before the call -- with the row's cusps, under the per-row
    cap, and then the row's contract on the relation the call returned.  The
    cap is the caller's budget: a cap of no seconds leaves no time for the call
    and the row is undecided without the call being made, and the alarm it sets
    reaches the call where Python holds control -- a call that does not hand
    control back to Python is not interrupted by it, so the cap is the budget
    of a row and not a promise about where it stops.

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
        deciding = time.monotonic()
        taken, reason = chosen_route(subgroup, route)
        log(
            f"[{label}] the row's route: {taken}"
            + (f", taken because {reason}" if reason else ", as the run asked")
            + f" (decided in {time.monotonic() - deciding:.1f} s)"
        )
        signal.setitimer(signal.ITIMER_REAL, cap)
        try:
            incidences = tuple(row_relation(subgroup, taken))
            lines = tuple(subgroup.cusps(1))
            planes = tuple(subgroup.cusps(2))
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        log(f"[{label}] the row's calls returned in {time.monotonic() - start:.1f} s")
        if getattr(subgroup, "finite_character_quotient", None) is not None:
            log(
                f"[{label}] the quotient retains "
                f"{subgroup.finite_character_quotient().retained_isotropic_transport_count()} "
                "carried-object transport datums: one for each carried isotropic object still "
                "registered, keyed by its span, each holding the object, its source and the "
                "isometry that placed it -- not the row's coverings and not its planes' lifts, "
                "which are retained separately"
            )
        return row_contract(lattice, subgroup, label, lines, planes, incidences, taken)
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
            return lattice.stable_positive_orthogonal_group()
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


def _trivial_image_row_agreement(lattice, rows, route="auto"):
    r"""Why a kernel row differs from its ambient row where ``rho`` is trivial, or ``None``.

    ``Otilde`` is the kernel of the discriminant representation, so where
    ``|O(A_L)| = 1`` it *is* ``O(L)``; the sign condition that cuts ``Otilde+``
    out of ``Otilde`` is then the whole of the index-two subgroup
    ``lattice.O_plus()``, so both kernel rows are the ambient rows and their
    counts are not free -- they are the ambient counts, computed here through
    the ambient group objects, on the route the row itself took where the
    ambient group takes it (``rho`` trivial cuts no discriminant condition, so
    ``auto`` gives the ambient rows the certificate route).  That is the one
    place the driver compares a counted number with another, and it makes the
    small-lattice run self-checking; on a lattice with a non-trivial
    discriminant image the function returns ``None`` -- there is nothing to
    compare, and the rows are recorded only.
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
        other_edges = int(row_relation(other, chosen_route(other, route)[0]).cardinality())
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

    ``--route`` chooses the call each row makes (:func:`chosen_route`): the
    divided-class route, the certificate route, or ``auto``, which prefers the
    class route and takes the certificate route only where the class route
    states it cannot decide the row.  Every row logs the route it took and the
    reason, so a run's relation is never one whose route is unstated.
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
    parser.add_argument("--plane-class-index", type=int, default=8,
                        help="how many of the row's distinct plane classes J = [P/2] to record "
                             "the index [Stab_O(q)(J) : rho(Stab_Gamma(P))] at; 0 records none")
    parser.add_argument("--route", default="auto", choices=ROW_ROUTES,
                        help="the incidence route: 'divided-class' (the class route), "
                             "'certificate' (the flag-carrying route), or 'auto' (the class "
                             "route wherever it applies, the certificate route where it does not)")
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
        subgroup = _row_subgroup(lattice, label)
        outcome = run_row(lattice, subgroup, label, arguments.cap, arguments.route)
        log(outcome.report())
        if outcome.status is not RowStatus.DECIDED:
            return outcome.status.exit_status
        counts[label] = outcome.counts
        # The plane class index is a quotient of two orders of the finite
        # character image, so it is asked only of a row that has one: the
        # ambient O(L) row is the label without a quotient, and the driver's
        # route decision reads the same fact.
        if (
            arguments.plane_class_index
            and getattr(subgroup, "finite_character_quotient", None) is not None
        ):
            record_plane_class_indices(
                label, subgroup, tuple(subgroup.cusps(2)), arguments.plane_class_index
            )
    if lattice is NamedLattices.Tco:
        if "O" in counts:
            record_comparison(
                "O", "the ambient row's counts (edges, lines, planes)",
                counts["O"], (1, 1, 1), PAGE_UNPOLARIZED,
            )
        if "Gamma_{Co,2}" in counts:
            record_comparison(
                "Gamma_{Co,2}", "the Gamma_{Co,2} row's counts (edges, lines, planes)",
                counts["Gamma_{Co,2}"], (13, 4, 7), PREVIOUS_ROW,
            )
        # The independent integral flag certificate of research#667 proves
        # 527 line cusps, 23715 * 8 plane cusps and three distinct flag
        # classes above each plane.  The counts of both kernel rows are
        # recorded against it and are not conditions on the row: a relation
        # with the same edge count and another shape is a disagreement the
        # reader sees, and #286 files a disagreement on research.
        for kernel_label in ("Otilde", "Otilde+"):
            if kernel_label in counts:
                record_comparison(
                    kernel_label, "the kernel row's counts (edges, lines, planes)",
                    counts[kernel_label], (569160, 527, 189720), INTEGRAL_ARCHIVE,
                )
    disagreement = _trivial_image_row_agreement(lattice, counts, arguments.route)
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
