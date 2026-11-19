r"""The Coble point the incidence driver stabilizes is a summand no isometry swaps.

`Gamma_{Co,2}` is `R_{Gamma_{En,2}}`, and the driver builds it as `rho^{-1}` of
the setwise stabilizer of `A_{U(2)} = <[ep/2],[fp/2]>` in `O(q_{T_Co})`.  The
identification of that point stabilizer with the stabilizer of the
*decomposition* `[h/2]^perp = A_{U(2)} + A_{E_8(2)}` -- which is what
`prop:gamma-co-images` (3) evaluates -- turns on two facts:

* the complement of `A_{U(2)}` inside `[h/2]^perp` is a summand, so an isometry
  preserving `[h/2]^perp` and `A_{U(2)}` preserves the complement too; and
* no isometry carries `A_{U(2)}` onto that complement, because an isometry is a
  bijection of the classes and the two have different orders (`4` against
  `det E_8(2) = 2^8 = 256`).

The second fact is a hypothesis and not a tautology: on a module whose two
summands have the same order an isometry does swap them, and there the
stabilizer of the point is properly contained in the stabilizer of the
decomposition.  Both sides are asserted here, so the file says which fact makes
the Coble identification hold.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _classes(lattice):
    r"""One class of `A_L` per named module generator: the primitive dual's class."""
    return {
        label: lattice.discriminant_class(lattice.primitive_dual(lattice.module_generator(label)))
        for label in lattice.module_generating_set()
    }


def _blocks(lattice):
    r"""The named generators of the three blocks of `T_Co = <h> + U(2) + E_8(-2)`.

    `T_Co` is built as the orthogonal sum of its three blocks, and each block's
    generators are named: `h` for `<h>`, `ep` and `fp` for `U(2)`, and `a1` to
    `a8` for `E_8(-2)`.  The first test reads the decomposition of `A_{T_Co}`
    off those three blocks; nothing else here assumes the names.
    """
    labels = tuple(lattice.module_generating_set())
    named = ("h", "ep", "fp")
    return named, tuple(label for label in labels if label not in named)


def test_the_coble_point_and_its_complement_have_different_orders_so_no_isometry_swaps_them():
    r"""`[h/2]^perp` splits as an order-four and an order-256 summand; `4 != 256`.

    `T_Co = <h> + E_10(2)` with `E_10(2) = U(2) + E_8(-2)`, so
    `A_{T_Co} = <[h/2]> + A_{U(2)} + A_{E_8(2)}` is an orthogonal decomposition
    and `[h/2]^perp = A_{E_10(2)} = A_{U(2)} + A_{E_8(2)}`.  The driver's point
    is `A_{U(2)}`, its orthogonal complement in `[h/2]^perp` is `A_{E_8(2)}`,
    and the two orders differ -- so no isometry of `O(A_{T_Co})` carries one
    onto the other, which is what makes the point stabilizer the stabilizer of
    the decomposition `prop:gamma-co-images` (3) evaluates.
    """
    lattice = NamedLattices.Tco
    form = lattice.discriminant_group()
    classes = _classes(lattice)
    _named, e8_labels = _blocks(lattice)
    e8_classes = tuple(classes[label] for label in e8_labels)

    point = form.subobject_on((classes["ep"], classes["fp"]))
    e8 = form.subobject_on(e8_classes)
    characteristic = form.subobject_on((classes["h"],))
    ten = form.subobject_on((classes["ep"], classes["fp"]) + e8_classes)

    assert characteristic.cardinality() == cardinal(2)
    assert point.cardinality() == cardinal(4)
    assert e8.cardinality() == cardinal(256)
    assert ten.cardinality() == cardinal(1024)
    assert characteristic.cardinality() * ten.cardinality() == form.cardinality()
    assert point.cardinality() * e8.cardinality() == ten.cardinality()
    assert point.cardinality() != e8.cardinality()
    # The zero of the form's value ring, read off an isotropic class rather
    # than named: `[ep/2]` is isotropic, so its pairing with itself is zero.
    zero = form.b(classes["ep"], classes["ep"])
    assert all(
        form.b(classes[label], member) == zero
        for label in ("h", "ep", "fp")
        for member in e8_classes
    )


def test_two_isometric_summands_are_swapped_so_the_point_stabilizer_is_proper():
    r"""On `A1 + A1` the summands have equal order and an isometry exchanges them.

    The same construction with two summands of order two: the lattice isometry
    exchanging the two `A1`s swaps their classes in `A`, so the setwise
    stabilizer of one summand is a proper subgroup of `O(q)` -- where in the
    Coble case it is the whole stabilizer of the decomposition.  An order
    hypothesis is what the Coble identification uses, and this is the case where
    it fails.
    """
    lattice = Lattices(ZZ)("A1") + Lattices(ZZ)("A1")
    form = lattice.discriminant_group()
    classes = _classes(lattice)
    labels = tuple(lattice.module_generating_set())
    first, second = classes[labels[0]], classes[labels[1]]
    point = form.subobject_on((first,))
    other = form.subobject_on((second,))
    swap = lattice.O()(
        {
            labels[0]: lattice.module_generator(labels[1]),
            labels[1]: lattice.module_generator(labels[0]),
        }
    )

    assert point.cardinality() == other.cardinality()
    assert swap(lattice.module_generator(labels[0])) == lattice.module_generator(labels[1])
    assert (
        form.discriminant_class(lattice.primitive_dual(swap(lattice.module_generator(labels[0]))))
        == second
    )
    stabilizer = form.O().stabilizer_of_classes((first,))
    swapped = form.O().stabilizer_of_classes((second,))
    assert stabilizer.cardinality() == swapped.cardinality()
    assert form.O().cardinality() > stabilizer.cardinality()
