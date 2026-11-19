r"""The pointed family where the quotient is a nonreflective Lorentzian lattice.

`L = U + K` with `K` the Bogachev--Kolpakov nonreflective Lorentzian lattice
(arXiv:2112.14642v4, section 6.1, printed p. 8: the form
`3x_0^2 + 14x_0x_1 + 98x_0x_2 + 49x_2^2`, of which the paper says "Then `L` is
nonreflective").  The pointed vector is the `U` summand's first generator,
primitive isotropic of divisibility one, and `K_I` is `K` itself -- rank three,
signature `(1, 2)`, discriminant `-2401`.

Why this file exists beside the pointed family's own.  At divisibility one the
pointwise Levi map is onto `O(K_I)`: the congruence lemma's lift reads
`c_i = b(w, kappa_i - tau^sharp kappa_i)`, an integer because the divisibility
is one, so `M_I = O(K_I)` and the family is one lift per generator together
with the radical's.  What is *not* available here is a library-owned family for
`O(K_I)`: the library's chamber route needs a completed fundamental chamber,
and a nonreflective Lorentzian lattice has none, while its reflections lie in
the maximal reflection subgroup, which has infinite index by the paper's
definition of reflectivity on printed p. 2 -- so no finite family of reflections
generates `O(K_I)` however many walls are taken.  `O(K_I)`'s generators
therefore come from `sage_indefinite_port`, whose generating claim the library
does not certify (`_computed_group_generators` says so).  This file pins what
the pointed call answers *given* that family; it does not certify the family,
and the pointed family here is complete only relative to it.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _specimen():
    r"""`U + K` and its `U` generator, for `K` the nonreflective Lorentzian lattice."""
    lattice = Lattices(ZZ)("U") + NamedLattices.BogachevKolpakovNonReflective
    labels = tuple(lattice.module_generating_set())
    vector = lattice.module_generator(labels[0])
    subobject = lattice.primitive_isotropic_subobject(vector)
    return lattice, vector, subobject, subobject.isotropic_reduction()


def test_the_pointed_family_answers_at_a_nonreflective_quotient() -> None:
    r"""The call returns, its members fix the vector, and `M_I` is the whole quotient.

    `L` is odd (the paper's form is odd and `U` is even), of signature `(2, 3)`
    and discriminant `-2401`; the pointed vector is isotropic, primitive and of
    divisibility one.  Every certified generator of `O(K_I)` has a pointwise
    lift, which is the divisibility-one case of the congruence lemma, so the
    family is its two factors and not a coset graph with more than one class.
    """
    lattice, vector, subobject, reduction = _specimen()
    quotient = reduction.quotient_lattice()
    image = reduction.pointwise_levi_image()

    assert vector.q() == ZZ(0)
    assert vector.is_primitive() is True
    assert vector.div() == ZZ(1)
    assert lattice.is_even() is False
    assert lattice.signature().first() == 2
    assert lattice.signature().second() == 3
    assert quotient.module_rank() == NN(3)
    assert quotient.discriminant() == ZZ(-2401)

    for generator in quotient.O().group_generators():
        assert generator in image

    family = subobject.pointed_stabilizer_generators()
    assert family
    assert all(generator(vector) == vector for generator in family)
