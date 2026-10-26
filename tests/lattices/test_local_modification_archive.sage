r"""Archived p-primary local lattice modification on the live overlattice owner.

The archived integral-lattice API distinguished an arbitrary overlattice from
a local modification at a chosen prime: the glue classes must lie in the
p-primary part of the discriminant form.  For ``U(2)`` either individual
discriminant generator is an order-two quadratic-isotropic class, and gluing
it produces the even unimodular hyperbolic plane with index two.
"""


from sage_extensions.all import *


def test_archived_u2_two_primary_modification_is_the_index_two_even_overlattice() -> None:
    lattice = Lattices(ZZ)([[0, 2], [2, 0]])
    discriminant = lattice.discriminant_group()
    glue_class = discriminant.module_generators()[0]

    assert glue_class.additive_order() == 2
    assert discriminant.q(glue_class) == discriminant.quadratic_value_module().zero()

    inclusion = lattice.local_modification(2, glue_class)
    enlarged = inclusion.codomain()

    assert inclusion.domain() is lattice
    assert inclusion.index() == 2
    assert enlarged.is_even()
    assert enlarged.is_unimodular()
    assert abs(enlarged.determinant()) == 1
    assert enlarged.is_isometric(Lattices(ZZ)("U")) is True
