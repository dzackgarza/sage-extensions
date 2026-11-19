r"""The pointed stabilizer of a primitive non-isotropic vector on an odd lattice.

For `v` primitive with `b(v,v) != 0`, put `K = v^perp \cap L` and
`L_0 = Z v \perp K`.  `L_0` has finite index in `L` -- `|b(v,v)|/d` with `d`
the divisibility of the functional `b(-,v)`, so not `|b(v,v)|` itself -- and
with `H = L/L_0` read as a subgroup of `A_{L_0}`, an isometry of `K` extends
to `L` fixing `v` exactly when it preserves `H`.  Nothing in that statement
reads `q` as anything but the norm, so no parity hypothesis is available or
needed: the extreme points are that `(1 \oplus \sigma)` preserves `L_0^\#`
because it preserves `L_0`, and that `L = \pi^{-1}(H)` is the definition of
`H`, not an appeal to overlattice theory.

The specimens are Gram matrices, and each asserts the property that makes it
the specimen it is:

* `U + <3>` at its norm-three vector is odd, indefinite, and its complement is
  the unimodular `U`, so the gluing is trivial and the pointed stabilizer is
  all of `O(U)` -- infinite, so nothing is asserted about its order.
* `<x, k>` with Gram `[[1,-1],[-1,-2]]` at `v = 2x - k` is odd, indefinite, of
  discriminant three, with `b(v,v) = 6`, `K = <k> = <-2>` and `Zv + K` of index
  two in `L`, so the gluing is nontrivial and the stabilizer is the order-two
  group `{+-1}` on `K`.  That order is the oracle: it is what the extension
  gives, and it is read from the returned family rather than typed into the
  answer.
"""

from sage_extensions.all import *  # noqa: F401,F403

UNIMODULAR_COMPLEMENT = [[0, 1, 0], [1, 0, 0], [0, 0, 3]]
GLUED_COMPLEMENT = [[1, -1], [-1, -2]]


def _pointed_generators(lattice, vector):
    r"""The library's generators of the stabilizer of ``vector`` in ``O(L)``."""
    return tuple(lattice.Aut().stabilizer(vector).group_generators())


def test_the_odd_lattice_with_a_unimodular_complement_is_answered() -> None:
    r"""`U + <3>` at its norm-three vector: odd, indefinite, and the family fixes it."""
    lattice = Lattices(ZZ)(UNIMODULAR_COMPLEMENT)
    labels = tuple(lattice.module_generating_set())
    x, _f, k = tuple(lattice.module_generators())
    vector = k

    assert lattice.is_even() is False
    assert lattice.is_definite() is False
    assert lattice.b(vector, vector) == ZZ(3)
    assert vector.is_primitive() is True

    family = _pointed_generators(lattice, vector)

    assert family
    assert all(generator(vector) == vector for generator in family)
    assert all(
        lattice.b(generator(left), generator(right)) == lattice.b(left, right)
        for generator in family
        for left in lattice.module_generators()
        for right in lattice.module_generators()
    )
    assert lattice.b(x, vector) == ZZ(0)


def test_the_odd_lattice_with_a_nontrivial_gluing_is_answered() -> None:
    r"""The disc-three specimen at `v = 2x - k`: the stabilizer is the order-two `{+-1}` on `K`.

    `v` has square six and its complement is `<k>` of square minus two, so
    `Zv + K` has index two in `L` and the gluing is the nontrivial one; the
    extension of `-1` on `K` preserves it, and the returned family generates
    the order-two group that is the whole stabilizer there.
    """
    lattice = Lattices(ZZ)(GLUED_COMPLEMENT)
    labels = tuple(lattice.module_generating_set())
    x, k = tuple(lattice.module_generators())
    vector = 2 * x - k

    assert lattice.is_even() is False
    assert lattice.is_definite() is False
    assert lattice.discriminant() == ZZ(3)
    assert lattice.b(vector, vector) == ZZ(6)
    assert vector.is_primitive() is True
    assert lattice.b(vector, k) == ZZ(0)
    assert lattice.b(k, k) == ZZ(-2)

    family = _pointed_generators(lattice, vector)

    assert family
    assert all(generator(vector) == vector for generator in family)
    assert lattice.Aut().subgroup(family).cardinality() == cardinal(2)
