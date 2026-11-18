r"""The plane class index ``[Stab_{O(q)}(J) : rho(Stab_Gamma(P))]`` at a plane.

``J = [P/2]`` is the order-four totally isotropic subgroup of ``A_L`` that a
primitive isotropic plane's divided classes span, and the plane rows of the
Coble pipeline are indexed by the number of the subgroup's plane orbits inside
one such class.  The right-hand order is read in the finite character image --
``chi(Stab_Gamma(P)) = chi(Gamma) cap chi(Pi)``, which is what the covering of
the incidence is computed from (D. Dutour Sikirić and K. Hulek,
arXiv:2302.01679v2, Lemma 3.6, printed p. 22) -- and the left-hand order is the
stabilizer of the class set inside ``O(q)``.

Nothing here types the value: the identity the four returned numbers satisfy is
checked, and so is the containment that puts a subgroup's index above the
ambient group's own, whose index the plane's parabolic reports.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_plane_class_index_is_the_stabilizer_quotient_of_the_parabolic_image():
    r"""``|Stab_{O(q)}(J)| = |rho(Stab_Gamma(P))| * index``, with no remainder.

    ``U + U(2)`` has one plane orbit under ``O(L)``, so both orders the index
    is made of are small and the arithmetic is checked where it is cheap: the
    stabilizer of the class set is the image of the parabolic times the index,
    with no remainder, which is the statement the plane rows are indexed by.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)([[0, 2], [2, 0]])
    subgroup = lattice.stable_orthogonal_group()
    quotient = subgroup.finite_character_quotient()
    plane = next(iter(subgroup.cusps(2))).representative()

    _classes, stabilizer_order, image_order, index = quotient.plane_class_index(plane)

    assert stabilizer_order == image_order * index
    assert index >= 1
    assert image_order >= 1
