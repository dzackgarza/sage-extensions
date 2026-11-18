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


def delta_and_perpendicular(lattice):
    r"""`delta = e - f` of `T_En` and its perpendicular, which is `T_Co`."""
    labels = tuple(lattice.module_generating_set())
    delta = lattice.module_generator(labels[0]) - lattice.module_generator(labels[1])
    perp = lattice.subobject_on((delta,)).inclusion().orthogonal_complement()
    return delta, perp


def gamma_en_2(lattice):
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


def run(lattice, cap):
    r"""What the construction returned, inside `cap` seconds, and what it says."""
    started = time.monotonic()
    delta, perp = delta_and_perpendicular(lattice)
    log(f"[R] delta: q = {delta.q()}, perp rank {perp.module_rank()}, "
        f"isometric to T_Co: {perp.is_isometric(NamedLattices.Tco)}")
    if not perp.is_isometric(NamedLattices.Tco):
        log("[R] the perpendicular is not T_Co: the row is about another lattice")
        return 2
    gamma = gamma_en_2(lattice)
    log(f"[R] Gamma_En,2 built: characters complete {gamma.character_data_is_complete()}, "
        f"contains a character kernel {gamma.contains_character_kernel()}")
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cap", type=float, default=10800, help="seconds the row may take")
    parser.add_argument("--lattice", default="TEn", choices=("TEn",),
                        help="the lattice the (-2)-vector is taken in")
    arguments = parser.parse_args(argv)
    previous = signal.signal(signal.SIGALRM, _alarm)
    try:
        return run(NamedLattices.TEn, arguments.cap)
    finally:
        signal.signal(signal.SIGALRM, previous)


if __name__ == "__main__":
    sys.exit(main())
