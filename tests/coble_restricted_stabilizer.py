r"""The restricted-stabilizer row of `#286`: `R_{Gamma_{En,2}}` by its construction.

`Gamma_{Co,2}` is `R_{Gamma_{En,2}}`, the image in `O(delta^perp)` of
`Stab_{Gamma_{En,2}}(delta)` for `delta` the `(-2)`-vector of `T_En` whose
perpendicular is `T_Co` (Dolgachev--Kondo, Izv. Math. 77:3 (2013), p. 513, the
sentence after Prop. 3.2).  This script builds it that way -- the stabilizer,
its generators, their restriction to the perpendicular -- and compares what it
gets with the group the incidence driver uses for its `Gamma_{Co,2}` row,
`rho^{-1}` of the stabilizer of `A_{U(2)}` in `O(A_{T_Co})`.

It is not collected by pytest: the stabilizer of a non-isotropic vector is the
indefinite port's marked-diagram decision, whose cost at rank 12 is minutes to
hours (see `results/issue286-the-restricted-stabilizer-cost.md`), so the row
belongs in the image job that reports later.

Exit status: 0 the row decided and agreed with the preimage group; 1 the row
did not return inside its cap; 2 the row returned and *differs* from the
preimage group (a disagreement, to be reported and filed, never hidden).
"""

import argparse
import signal
import sys
import time

from sage_extensions.all import *  # noqa: F401,F403


class RowUndecided(Exception):
    r"""The row did not return inside its cap."""


def _alarm(signum, frame):
    raise RowUndecided


def log(message=""):
    print(message, flush=True)


def delta_and_perpendicular(subgroup, select=None):
    r"""The `(-2)`-vector `delta` of the subgroup's own lattice, and its perpendicular.

    `delta` must be an element of the lattice the subgroup acts on, and that is
    the subgroup's supergroup's -- the coinvariant extension's lattice for
    `Gamma_{En,2}`, which is an equal but distinct copy of `T_En`.  A `delta`
    taken from the catalogue object is a vector of a lattice none of this
    subgroup's isometries is an isometry of, and the stabilizer call then treats
    it as a family rather than as an element.

    `select` names the vector in the lattice it is handed; the default is
    `e - f` of the first two generators, which is `T_En`'s `(-2)`-vector
    (Dolgachev--Kondō, Izv. Math. 77:3 (2013), p. 513).
    """
    lattice = subgroup.supergroup().domain()
    delta = (select or _difference_of_the_first_two)(lattice)
    if delta.parent() is not lattice:
        raise ArithmeticError(
            f"delta = {delta} is not an element of {lattice}, the lattice {subgroup} acts on"
        )
    if delta.q() != ZZ(-2):
        raise ArithmeticError(f"delta = {delta} has q = {delta.q()}, not -2")
    perp = lattice.subobject_on((delta,)).inclusion().orthogonal_complement()
    return delta, perp


def _difference_of_the_first_two(lattice):
    r"""`e - f` of the lattice's first two named generators."""
    labels = tuple(lattice.module_generating_set())
    return lattice.module_generator(labels[0]) - lattice.module_generator(labels[1])


def _minus_two_generator(lattice):
    r"""The lattice's first named generator of square `-2`."""
    for label in lattice.module_generating_set():
        vector = lattice.module_generator(label)
        if lattice.q(vector) == ZZ(-2):
            return vector
    raise ArithmeticError(f"{lattice} names no generator of square -2")


def gamma_en_2():
    r"""`Gamma_{En,2}`, the group of Alexeev--Engel--Garza--Schaffler, Def. 2.6."""
    invariant = Involutions.I_En.invariant_lattice()
    labels = tuple(invariant.module_generating_set())
    for left in labels:
        for right in labels:
            if left > right:
                continue
            a = invariant.module_generator(left)
            b = invariant.module_generator(right)
            if (
                invariant.q(a) == ZZ.zero()
                and invariant.q(b) == ZZ.zero()
                and invariant.b(a, b) == ZZ(2)
            ):
                polarized = Involutions.I_En.polarized(invariant.inclusion()(a + b))
                return polarized.coinvariant_extension_subgroup()
    raise ArithmeticError("the invariant lattice of I_En has no isotropic pair of pairing two")


def restricted(perp, isometries):
    r"""The restrictions of isometries fixing `delta` to `delta^perp`."""
    inclusion = perp.inclusion()
    labels = tuple(perp.module_generating_set())
    return tuple(
        perp.O()(
            {
                label: inclusion.lift(isometry(inclusion(perp.module_generator(label))))
                for label in labels
            }
        )
        for isometry in isometries
    )


def run(cap):
    r"""What the construction returned, inside `cap` seconds, and what it says."""
    started = time.monotonic()
    gamma = gamma_en_2()
    log(f"[R] Gamma_En,2 built: characters complete {gamma.character_data_is_complete()}, "
        f"contains a character kernel {gamma.contains_character_kernel()}")
    delta, perp = delta_and_perpendicular(gamma)
    log(f"[R] delta: q = {delta.q()}, perp rank {perp.module_rank()}, "
        f"isometric to T_Co: {perp.is_isometric(NamedLattices.Tco)}")
    if not perp.is_isometric(NamedLattices.Tco):
        log("[R] the perpendicular is not T_Co: the row is about another lattice")
        return 2
    signal.setitimer(signal.ITIMER_REAL, cap)
    try:
        stabilizer = gamma.stabilizer(delta)
        generators = tuple(stabilizer.group_generators())
    except RowUndecided:
        log(f"[R] undecided: the stabilizer's generators did not return in {cap:g} s")
        return 1
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    log(f"[R] Stab_Gamma(delta): {len(generators)} generators in {time.monotonic() - started:.1f} s")
    image = perp.O().subgroup(restricted(perp, generators))
    log(f"[R] the restricted image, as a subgroup of O(T_Co)")
    tco = NamedLattices.Tco
    rho = tco.discriminant_representation()
    restricted_generators = restricted(perp, generators)
    image_order = tco.discriminant_group().O().subgroup(
        tuple(rho(generator) for generator in restricted_generators)
    ).cardinality()
    spinor = tco.O_plus().preimage_morphism()
    signs = tuple(1 if spinor(generator).is_one() else -1 for generator in restricted_generators)
    log(f"[R] |rho(R)| = {image_order}; spinor signs {signs.count(1)} of +1, {signs.count(-1)} of -1")
    form = tco.discriminant_group()

    def span(family):
        closure = {form.zero()}
        for generator in family:
            closure |= {element + generator for element in closure}
        return frozenset(closure)

    classes = {
        label: tco.discriminant_class(tco.primitive_dual(tco.module_generator(label)))
        for label in tco.module_generating_set()
    }
    point = span((classes["ep"], classes["fp"]))
    preimage_order = form.O().stabilizer_of_classes(point).cardinality()
    log(f"[R] the driver's group is rho^-1(Stab(J)) with |Stab(J)| = {preimage_order}")
    agrees = image_order == preimage_order and signs.count(-1) > 0
    log(f"[R] {'agrees' if agrees else 'DIFFERS'}: the restricted image "
        f"{'is' if agrees else 'is not'} the preimage group's discriminant image "
        f"with both spinor signs")
    log(f"[R] the row returned in {time.monotonic() - started:.1f} s")
    return 0 if agrees else 2


SMALL_SPECIMEN = "U + U(2) + <-2>"


def small_specimen():
    r"""`L = U + U(2) + <-2>`, whose `(-2)`-vector has `U + U(2)` as its perpendicular.

    The smallest lattice pair that carries the shape of the Coble statement: a
    `(-2)`-vector `delta` whose perpendicular `M` is a smaller lattice, a
    discriminant preimage on `L` playing `Gamma_{En,2}`'s role, and the same
    preimage on `M` playing the incidence driver's.  The construction and the
    comparison are the row's, at a size one command reaches.
    """
    U = Lattices(ZZ)("U")
    U2 = Lattices(ZZ)([[0, 2], [2, 0]])
    return U + U2 + Lattices(ZZ)([[-2]])


def _u2_labels(block):
    r"""The two labels of an isotropic pair of pairing two — the `U(2)` block's."""
    labels = tuple(block.module_generating_set())
    for left in labels:
        for right in labels:
            if left >= right:
                continue
            a, b = block.module_generator(left), block.module_generator(right)
            if block.q(a) == ZZ.zero() and block.q(b) == ZZ.zero() and block.b(a, b) == ZZ(2):
                return (left, right)
    raise ArithmeticError(f"{block} has no isotropic pair of pairing two")


def _class_set(block, labels):
    r"""The span in `A_block` of the classes of `labels`, as a set of classes."""
    form = block.discriminant_group()
    closure = {form.zero()}
    for label in labels:
        generator = form.discriminant_class(
            block.primitive_dual(block.module_generator(label))
        )
        closure |= {element + generator for element in closure}
    return frozenset(closure)


def run_small(cap):
    r"""The same construction and comparison at rank five, where one command reaches it."""
    started = time.monotonic()
    lattice = small_specimen()
    point = _class_set(lattice, _u2_labels(lattice))
    gamma = lattice.Aut().discriminant_point_stabilizer(point)
    log(f"[R-small] {SMALL_SPECIMEN}: the subgroup on L, as a discriminant preimage")
    delta, perp = delta_and_perpendicular(gamma, _minus_two_generator)
    log(f"[R-small] delta q = {delta.q()}, perp rank "
        f"{perp.module_rank()}, isometric to U + U(2): {perp.is_isometric(small_perpendicular())}")
    if not perp.is_isometric(small_perpendicular()):
        log("[R-small] the perpendicular is not U + U(2)")
        return 2
    signal.setitimer(signal.ITIMER_REAL, cap)
    try:
        generators = tuple(gamma.group_generators())
        restrictions = restricted(perp, tuple(gamma.stabilizer(delta).group_generators()))
    except RowUndecided:
        log(f"[R-small] undecided: the stabilizer did not return in {cap:g} s")
        return 1
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    log(f"[R-small] {len(generators)} generators of the subgroup, "
        f"{len(restrictions)} restrictions to the perpendicular")
    rho = perp.discriminant_representation()
    image_order = perp.discriminant_group().O().subgroup(
        tuple(rho(generator) for generator in restrictions)
    ).cardinality()
    spinor = perp.O_plus().preimage_morphism()
    signs = tuple(1 if spinor(generator).is_one() else -1 for generator in restrictions)
    stabilizer_order = perp.discriminant_group().O().stabilizer_of_classes(
        _class_set(perp, _u2_labels(perp))
    ).cardinality()
    log(f"[R-small] |rho(R)| = {image_order}; the driver's |Stab(J)| = {stabilizer_order}; "
        f"spinor signs {signs.count(1)} of +1, {signs.count(-1)} of -1")
    agrees = image_order == stabilizer_order
    log(f"[R-small] {'agrees' if agrees else 'DIFFERS'}: the two descriptions "
        f"{'have' if agrees else 'do not have'} the same discriminant image")
    log(f"[R-small] the row returned in {time.monotonic() - started:.1f} s")
    return 0 if agrees else 2


def small_perpendicular():
    r"""`U + U(2)`, the perpendicular of the `(-2)`-vector of the small specimen."""
    return Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cap", type=float, default=10800, help="seconds the row may take")
    parser.add_argument("--lattice", default="TEn", choices=("TEn", "small"),
                        help="the lattice pair the row is about: 'TEn' is the Coble one "
                             "(`delta^perp` is `T_Co`), 'small' is `U + U(2) + <-2>`")
    arguments = parser.parse_args(argv)
    previous = signal.signal(signal.SIGALRM, _alarm)
    try:
        if arguments.lattice == "small":
            return run_small(arguments.cap)
        return run(arguments.cap)
    finally:
        signal.signal(signal.SIGALRM, previous)


if __name__ == "__main__":
    sys.exit(main())
