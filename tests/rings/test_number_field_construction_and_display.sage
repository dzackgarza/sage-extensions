r"""A quadratic field constructs, and its lattices display without an ordering.

`QuadraticField(2, "a")` used to fail during construction: the self-module
membership installed at the end of `Parent.__init__` hashes the ring, the
number-field branch of the ring's `_repr_` reads `defining_polynomial`, and that
method arrives with the placement the algebra constructor installs only after
the first initialization.  Number fields are identity-bearing parents, like the
orders that already hashed by identity for the same reason.

These cases pin the construction contract and then run the three original
specimens of research issue 614 — a rank-two lattice over `QuadraticField(2,
"a")`, over its maximal order, and over `QuadraticField(-1, "i")`'s maximal
order — through both `repr` and `latex`.
"""

from sage.all import latex

from sage_extensions.all import Lattices, OwnedNumberFields, QuadraticField, ZZ


def test_the_quadratic_field_constructs_before_its_placement_is_installed() -> None:
    field = QuadraticField(2, "a")

    generator = field.algebra_generator("a")
    two = ZZ.one() + ZZ.one()
    assert str(field.defining_polynomial()) == "a^2 - 2"
    assert field in OwnedNumberFields()
    assert generator * generator == field(two)
    assert repr(field)
    assert hash(field) == hash(field)
    assert field == field


def test_the_field_and_its_maximal_order_carry_lattices_that_display() -> None:
    field = QuadraticField(2, "a")
    order = field.maximal_order()
    imaginary_order = QuadraticField(-1, "i").maximal_order()

    specimens = {
        "over QQ(sqrt 2)": Lattices(field)(field**2),
        "over its maximal order": Lattices(order)(order**2),
        "over Z[i]": Lattices(imaginary_order)(imaginary_order**2),
    }
    for name, lattice in specimens.items():
        assert repr(lattice), name

        text = latex(lattice)
        assert "rk}(L) = 2" in text, name
        assert "disc}(L)" in text, name
        assert "sig}(L)" not in text, name

        # The explicit ordering guard is untouched: these fraction fields are
        # not represented as ordered, so an index of inertia is not available.
        try:
            lattice.signature_pair()
        except AssertionError as error:
            assert "chosen ordering" in str(error), name
        else:
            raise AssertionError(f"{name}: signature_pair answered without a chosen ordering")


def test_the_rational_display_and_its_signature_are_unchanged() -> None:
    plane = Lattices(ZZ)([[0, 1], [1, 0]])

    text = latex(plane)
    assert "sig}(L) = (1, 1)" in text
    assert plane.signature_pair() is not None
