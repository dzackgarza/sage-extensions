r"""Research issue 614, cells 18 and 21: the multiplication forms over an order.

The notebook's other committed regressions for these cells state the *display*
of the lattices over `ZZ[sqrt 2]` and `ZZ[i]`.  The multiplication identities —
which are what the cells assert — were verified only by probes, so they are
stated here with the notebook's own objects and its unchanged assertions:

* cell 13 then 18: ``K = QuadraticField(2, "a")``, ``a = K.algebra_generator("a")``,
  ``O = K.maximal_order()``, ``L = Lattices(O)([[2, a], [a, 2]])`` with
  ``u*u = 2``, ``u*v = a``, ``v*v = 2``, and the Gram tensor retained;
* cell 16: ``Lattices(O)(O**2)`` with the standard identities ``e*e = 1``,
  ``e*f = 0``, ``f*f = 1``;
* cell 20 then 21: ``Oi = QuadraticField(-1, "i").maximal_order()``,
  ``Lattices(Oi)(Oi**2)`` with ``ei*ei = 1``, ``ei*fi = 0``, ``fi*fi = 1``.

Nothing here is a display assertion, and nothing wider than these cells is
claimed.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_cell_18_the_hyperbolic_form_over_the_maximal_order_of_q_sqrt_two() -> None:
    r"""``Lattices(O)([[2, a], [a, 2]])``: ``u*u = 2``, ``u*v = a``, ``v*v = 2``.

    ``O`` is the maximal order of ``QQ(sqrt 2)`` and ``a`` its generator, so the
    Gram matrix of this form has entries in ``O`` and its diagonal is the
    rational ``2``.  The three products are the cell's own assertions.
    """
    field = QuadraticField(2, "a")
    a = field.algebra_generator("a")
    order = field.maximal_order()
    lattice = Lattices(order)([[2, a], [a, 2]])
    basis = lattice.module_generators()
    assert basis.cardinality() == 2
    u, v = tuple(basis)

    assert u * u == 2
    assert u * v == a
    assert v * v == 2
    gram = lattice.gram_tensor()
    # The Gram tensor's displayed type: contravariant twice, as the cell prints.
    valence = gram.tensor_valence()
    assert (valence[0], valence[1]) == (0, 2)


def test_cell_16_the_standard_form_over_the_maximal_order_of_q_sqrt_two() -> None:
    r"""``Lattices(O)(O**2)``: ``e*e = 1``, ``e*f = 0``, ``f*f = 1``.

    The identity form over the same order: the notebook asserts these for the
    rational and the Gaussian cases, and this is the remaining member of the
    family, whose display the committed regression already states.
    """
    field = QuadraticField(2, "a")
    order = field.maximal_order()
    lattice = Lattices(order)(order**2)
    e, f = tuple(lattice.module_generators())

    assert e * e == 1
    assert e * f == 0
    assert f * f == 1


def test_cell_7_the_identity_lattice_over_the_integers() -> None:
    r"""``Lattices(ZZ)(ZZ**2)``: ``e*e = 1``, ``e*f = 0``, ``f*f = 1``.

    The notebook also states the chosen frame of the same lattice —
    ``linear_combination({0: 1}) = e`` and ``linear_combination({1: 1}) = f`` —
    which is what makes the three products statements about those two vectors.
    """
    lattice = Lattices(ZZ)(ZZ**2)
    e, f = tuple(lattice.module_generators())

    assert lattice.linear_combination({0: 1}) == e
    assert lattice.linear_combination({1: 1}) == f
    assert e * e == 1
    assert e * f == 0
    assert f * f == 1


def test_cell_11_the_identity_lattice_over_the_rationals() -> None:
    r"""``Lattices(QQ)(QQ**2)``: ``eQ*eQ = 1``, ``eQ*fQ = 0``, ``fQ*fQ = 1``."""
    lattice = Lattices(QQ)(QQ**2)
    e, f = tuple(lattice.module_generators())

    assert e * e == 1
    assert e * f == 0
    assert f * f == 1


def test_cell_14_the_identity_lattice_over_q_sqrt_two() -> None:
    r"""``Lattices(K)(K**2)``: ``eK*eK = 1``, ``eK*fK = 0``, ``fK*fK = 1``."""
    field = QuadraticField(2, "a")
    lattice = Lattices(field)(field**2)
    e, f = tuple(lattice.module_generators())

    assert e * e == 1
    assert e * f == 0
    assert f * f == 1


def test_cell_21_the_identity_form_over_the_gaussian_integers() -> None:
    r"""``Lattices(Oi)(Oi**2)``: ``ei*ei = 1``, ``ei*fi = 0``, ``fi*fi = 1``.

    ``Oi = ZZ[i]`` is the maximal order of ``QQ(i)``; the products are the
    cell's own assertions, unchanged.
    """
    order = QuadraticField(-1, "i").maximal_order()
    lattice = Lattices(order)(order**2)
    ei, fi = tuple(lattice.module_generators())

    assert ei * ei == 1
    assert ei * fi == 0
    assert fi * fi == 1
