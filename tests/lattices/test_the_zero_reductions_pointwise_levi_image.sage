r"""The pointwise Levi image at a null line with zero reduction is trivial.

On `U(2)`, the first basis vector is primitive isotropic of divisibility two and
`K_I = I^perp/I = 0`.  The pointwise Levi image `M_I^1` is therefore the trivial
subgroup of `O(0)`.  Asking for its order is the first finite-group step in the
parabolic presentation; the zero rank must not be sent to the definite-group
matrix normalizer, whose Gram normalization divides by the zero matrix's gcd.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_zero_reduction_has_a_trivial_pointwise_levi_image() -> None:
    lattice = Lattices(ZZ)([[0, 2], [2, 0]])
    labels = tuple(lattice.module_generating_set())
    vector = lattice.module_generator(labels[0])
    reduction = lattice.primitive_isotropic_subobject(vector).isotropic_reduction()

    assert vector.q() == ZZ(0)
    assert vector.is_primitive() is True
    assert vector.div() == ZZ(2)
    assert reduction.quotient_lattice().module_rank() == NN(0)
    assert reduction.pointwise_levi_image().cardinality() == cardinal(1)
    assert tuple(reduction.pointwise_levi_image().group_generators()) == ()
    assert tuple(lattice.Aut().stabilizer(vector).group_generators()) == ()
