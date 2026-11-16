r"""A stabilizer states its clause when it is read, from the objects it stabilizes.

In U the general linear group stabilizes the flag Ze exactly when it maps e to
+-e; the shear (e, f) -> (e, e + f) does and the exchange of e and f does not.
The setwise stabilizer of the isotropic line Ze in O(U) is named by the image
of its inclusion.
"""

from sage_extensions.all import *
from sage_extensions.categories.group.groups import _named_by_its_own_words


def test_the_flag_stabilizer_of_a_line_in_u_contains_the_shear_and_not_the_exchange():
    hyperbolic = Lattices(ZZ)("U")
    e, f = tuple(hyperbolic.module_generators())
    labels = tuple(hyperbolic.module_generating_set())
    line = e.sublattice()
    general_linear = hyperbolic.general_linear_group()
    stabilizer = general_linear.flag_stabilizer((line,))
    shear = general_linear(dict(zip(labels, (e, e + f), strict=True)))
    exchange = general_linear(dict(zip(labels, (f, e), strict=True)))
    assert shear in stabilizer
    assert exchange not in stabilizer


def test_the_setwise_stabilizer_of_an_isotropic_line_names_the_image_of_its_inclusion():
    hyperbolic = Lattices(ZZ)("U")
    embedding = hyperbolic.basis_vector(0).sublattice().inclusion()
    setwise = hyperbolic.O().setwise_stabilizer(embedding)
    name = _named_by_its_own_words(embedding)
    assert setwise._predicate_clause() == f"g(im({name}))=im({name})"
