r"""The ([3,5,3]) lattice retains its selected real place for Vinberg enumeration."""

from sage_extensions.all import *  # noqa: F401,F403


def test_golden_integer_lattice_number_field_vinberg_finds_four_simple_roots() -> None:
    field = QuadraticField(5, "s")
    s = field.primitive_element()
    order = field.maximal_order()
    phi = (1 + s) / 2
    lattice = Lattices(order)(
        [
            [2, -1, 0, 0],
            [-1, 2, -phi, 0],
            [0, -phi, 2, -1],
            [0, 0, -1, 2],
        ]
    )
    place = next(embedding for embedding in field.embeddings(AA) if embedding(s) > 0)
    vinberg = lattice.number_field_vinberg(place)
    complete, roots = vinberg.vinberg_simple_roots(count=4)

    assert complete
    assert roots.cardinality() == cardinal(4)
