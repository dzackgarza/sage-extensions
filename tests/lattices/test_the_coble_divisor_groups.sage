r"""The two Coble-divisor groups of #286's first paragraph, by their construction.

Dolgachev--Kond\=o, *Enriques surfaces and Borel--Weil--Bott type duality*, Izv.
Math. 77:3 (2013), p. 513, the sentence after prop. 3.2: ``delta`` is a
``(-2)``-vector of ``T_En`` with ``delta^\perp`` isometric to ``T_Co``, and the two
groups of the Coble divisor are the images in ``O(delta^\perp)`` of
``Stab_Gamma(delta)`` for ``Gamma = O(T_En)`` and ``Gamma = Gamma_{En,2}``, the
group of Alexeev--Engel--Garza--Schaffler, Nagoya Math. J. 259 (2025), Def. 2.6
(``029J``'s ``Gamma_{En,2}`` row).  Each is built by that construction -- the
stabilizer's image under the restriction to the perpendicular -- never from a
description of its image in ``O(q)``.

The research page (``prop:gamma-co-images``) states that the first of them is
all of ``O(T_Co)``; this test checks that claim by containment: both groups are
countably infinite, so the cardinalities agree trivially and the claim is the
containment of every generator of ``O(delta^\perp)`` in the image.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _delta_and_perpendicular():
    r"""``delta = e - f`` of ``T_En``'s hyperbolic plane, with ``q(delta) = -2``."""
    lattice = NamedLattices.TEn
    labels = tuple(lattice.module_generating_set())
    first = lattice.module_generator(labels[0])
    second = lattice.module_generator(labels[1])
    delta = first - second
    perp = lattice.subobject_on((delta,)).inclusion().orthogonal_complement()
    return lattice, delta, perp


def _gamma_en_2():
    r"""``Gamma_{En,2}``, the group #286 item 2 builds, at the degree-2 polarization."""
    invariant = Involutions.I_En.invariant_lattice()
    labels = tuple(invariant.module_generating_set())
    marks = []
    for left in labels:
        for right in labels:
            if left > right:
                continue
            left_vector = invariant.module_generator(left)
            right_vector = invariant.module_generator(right)
            if (
                invariant.q(left_vector) == ZZ.zero()
                and invariant.q(right_vector) == ZZ.zero()
                and invariant.b(left_vector, right_vector) != ZZ.zero()
            ):
                marks.append((left, right, invariant.b(left_vector, right_vector)))
    left, right, _pairing = next(entry for entry in marks if entry[2] == ZZ(2))
    h_invariant = invariant.module_generator(left) + invariant.module_generator(right)
    polarized = Involutions.I_En.polarized(invariant.inclusion()(h_invariant))
    return polarized.coinvariant_extension_subgroup()


def _restricted_isometries(perp, isometries):
    r"""The restrictions of isometries of ``T_En`` fixing ``delta`` to ``delta^\perp``."""
    inclusion = perp.inclusion()
    labels = tuple(perp.module_generating_set())
    return tuple(
        perp.O()(
            {
                label: inclusion.lift(
                    isometry(inclusion(perp.module_generator(label)))
                )
                for label in labels
            }
        )
        for isometry in isometries
    )


def test_the_coble_divisor_delta_has_perpendicular_isometric_to_tco() -> None:
    r"""``delta = e - f`` of ``T_En``: ``q(delta) = -2`` and ``delta^\perp`` is ``T_Co``."""
    lattice, delta, perp = _delta_and_perpendicular()
    assert delta.q() == ZZ(-2)
    assert perp.module_rank() == cardinal(11)
    assert perp.signature_pair().first() == cardinal(2)
    assert perp.signature_pair().second() == cardinal(9)
    assert perp.is_isometric(NamedLattices.Tco) is True


def test_the_first_coble_divisor_group_is_all_of_otco() -> None:
    r"""The image in ``O(delta^\perp)`` of ``Stab_{O(T_En)}(delta)`` contains all of ``O(T_Co)``.

    Both the image and ``O(delta^\perp)`` are countably infinite arithmetic
    groups, so the containment of every generator of ``O(delta^\perp)`` in the
    image is the check of the research page's claim
    (``prop:gamma-co-images``) that the first group is all of ``O(T_Co)``.
    """
    lattice, delta, perp = _delta_and_perpendicular()
    ambient = lattice.Aut()
    stabilizer = ambient.stabilizer(delta)
    generators = tuple(stabilizer.group_generators())
    image = perp.O().subgroup(_restricted_isometries(perp, generators))
    assert all(
        generator in image for generator in perp.O().group_generators()
    )
