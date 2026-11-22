r"""The plane stabilizer includes generators of its whole congruence Levi projection.

The split plane below has block data $H=0$, $J=\operatorname{diag}(1,5)$ and
$A=(-2)$.  Dutour Sikirić--Hulek, Theorem 4.9 (arXiv:2302.01679v2, printed
pp. 33--34), gives $P_1=JQ_1^{-t}J^{-1}$ for a lift with trivial quotient action.
The lower shear of level five is therefore induced by an element of $P_I$, and
a constructive generating family must cover that direction.  The old finite list
of candidate shears had levels $1,2,3,4,6$ and constructed no lift of this one.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _the_level_five_split_plane():
    r"""Return the plane in the block basis $(U\mid P\mid K)$ with $J=\operatorname{diag}(1,5)$."""
    lattice = Lattices(ZZ)(
        [
            [0, 0, 1, 0, 0],
            [0, 0, 0, 5, 0],
            [1, 0, 0, 0, 0],
            [0, 5, 0, 0, 0],
            [0, 0, 0, 0, -2],
        ]
    )
    basis = tuple(lattice.module_generators())
    return lattice, lattice.primitive_isotropic_subobject(basis[2], basis[3])


def _plane_action(plane, generator):
    r"""The induced column-coordinate action of ``generator`` on the plane's basis."""
    inclusion = plane.inclusion()
    domain = inclusion.domain()
    labels = tuple(domain.module_generating_set())
    images = [
        generator(inclusion(domain.module_generator(label)))
        for label in labels
    ]
    return matrix([
        [inclusion.lift(image).to_vector()(label) for image in images]
        for label in labels
    ])


def test_the_public_stabilizer_contains_the_level_five_levi_shear() -> None:
    r"""The real public call returns a generator acting by the missing level-five shear."""
    lattice, plane = _the_level_five_split_plane()
    family = lattice.Aut().stabilizer(plane, action="setwise").group_generators()
    actions = tuple(_plane_action(plane, generator) for generator in family)
    assert matrix([[1, 5], [0, 1]]) in actions
    assert plane.levi_plane_action_projection_index() == cardinal(6)
    assert plane.levi_plane_action_index(trivial_on_quotient=True) == cardinal(6)
