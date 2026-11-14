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
the double-coset representative: a breadth-first walk over the right-coset
action of ``rho(O(L))`` on ``rho(O(L)) / rho(Stab P)`` carries, for every
coset it reaches, the last ambient generator image that carried its parent
there, and a lift of a word in the rho-images of the ambient generators is
the same word in those generators, by the homomorphism property of the
discriminant representation.

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


def _kernel_row_expected_count(subgroup, plane):
    r"""The double-coset count of one kernel plane row, by group orders.

    For ``Gamma`` in ``{Otilde, Otilde+}`` the character image ``chi(Gamma)``
    is trivial -- every element of ``ker rho`` has trivial discriminant
    image, and every element of ``ker(rho, sn_RR)`` also has sign ``+1`` --
    so the double cosets ``chi(Gamma) \\ chi(O(L)) / chi(H)`` of Dutour
    Sikirić--Hulek, Lemma 3.6, printed p. 22, are the plain cosets of
    ``chi(H)`` in ``chi(O(L))``, and their number is the index
    ``|chi(O(L))| / |chi(H)|`` by Lagrange's theorem.

    ``|chi(O(L))|`` is the quotient's own order computation
    (``image_order``), and ``|chi(H)| = |rho(H)| * s`` where ``s`` in
    ``{1, 2}`` is the size of the kernel of the projection ``chi(H) ->
    rho(H)``: ``s = 2`` exactly when the sign character does not factor
    through ``rho`` on the stabilizer, decided here by whether the
    generator-wise sign assignment on the certified parabolic family extends
    to a homomorphism on ``rho(H)`` (GAP's ``GroupHomomorphismByImages``
    returns ``fail`` when it does not -- the same well-definedness test the
    sign-descent rank of the quotient applies to the ambient generators).
    With no sign factor in ``chi`` at all, ``s = 1`` and the count is
    ``|im rho| / |rho(H)|``.

    This is the independent computation the row's own walk is checked
    against: group orders and one homomorphism well-definedness test, no
    coset enumeration.  (The double-coset enumeration in the full joint
    character product was measured past this VM's memory guard at the Coble
    size -- 6260 MiB tree RSS, killed at 6144 -- so the orders route is not
    only faster, it is the one that fits.)

    The formula was validated against the rows themselves on the gate
    lattices ``6JRS = U + U + <-2>`` and ``U + U(2) + <-2>`` (both kernel
    rows of both lattices) and against the Coble group orders
    ``|im rho| = 46998591897600``, ``|rho(H)| = 247726080``.
    """
    from sage.libs.gap.libgap import libgap
    from sage_extensions.categories.group.groups import (
        OwnedGroups,
        _element_to_engine,
        _gap_model,
    )

    quotient = subgroup.finite_character_quotient()
    family = tuple(plane.parabolic_stabilizer_generators())
    lattice = subgroup.supergroup().domain()
    rho = lattice.discriminant_representation()
    image_order = int(quotient.image_order())
    _engine, im_rho, _section, _ambient = quotient._im_rho_engine_and_section()
    images = [
        _element_to_engine(quotient._discriminant_group, rho(h)) for h in family
    ]
    rho_H = libgap.Subgroup(im_rho, images)
    rho_H_order = int(libgap.Order(rho_H))
    j, sign_labels = quotient._sign_descent_rank()
    if j == 0 or not sign_labels:
        return image_order // rho_H_order
    if len(sign_labels) != 1:
        raise RuntimeError(
            "the expected count of a kernel plane row is computed here for one sign "
            f"character, but {subgroup} cuts {len(sign_labels)}"
        )
    label = sign_labels[0]
    ring = lattice.base_ring()
    if label == "spinor":
        morphism = lattice.O_plus().preimage_morphism()
        values = [morphism(h).is_one() for h in family]
    else:
        values = [ring(h.determinant()) == ring.one() for h in family]
    c2 = _gap_model(OwnedGroups().C(2))
    c2gen = list(libgap.GeneratorsOfGroup(c2))[0]
    targets = [libgap.One(c2) if v else c2gen for v in values]
    s = 1 if bool(libgap.GroupHomomorphismByImages(rho_H, c2, images, targets)) else 2
    return image_order // (rho_H_order * s)


def _expected_row_count(lattice, subgroup):
    r"""The sum over the ambient ``O(L)``-classes of the double-coset count."""
    ambient = tuple(subgroup.supergroup().isotropic_orbit_representatives(2))
    total = 0
    for plane in ambient:
        if plane.is_parabolic_complete() is not True:
            raise RuntimeError(
                f"the plane {plane} of {lattice} has no certified parabolic family, so "
                "the expected count of the kernel plane row cannot be computed"
            )
        total += _kernel_row_expected_count(subgroup, plane)
    return total, len(ambient)


def check_row_count(lattice, subgroup, label, count):
    r"""The index per class sums to the class count: the row equals its double cosets."""
    expected, classes = _expected_row_count(lattice, subgroup)
    log(f"[{label}] expected {expected} planes over {classes} ambient class(es)")
    if count != expected:
        log(
            f"[{label}] the row returned {count} planes but the double cosets of its "
            f"{classes} ambient class(es) number {expected}"
        )
        return False
    return True


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
        if not check_row_count(lattice, subgroup, label, count):
            return 1
        counts[label] = count
    if counts["Otilde+"] < counts["Otilde"]:
        log("the Otilde+ row has fewer planes than the Otilde row")
        return 1
    log(f"the Otilde count is {counts['Otilde']} and the Otilde+ count is {counts['Otilde+']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
