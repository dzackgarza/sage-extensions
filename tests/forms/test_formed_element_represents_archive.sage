r"""Which integers the positive definite lattice ``<2> + <3>`` represents."""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_lattice_2_plus_3_represents_2_3_5_and_not_1_or_4() -> None:
    r"""``2a^2 + 3b^2``: norm 2 at ``(+-1, 0)``, 3 at ``(0, +-1)``, 5 at ``(+-1, +-1)``; never 1 or 4.

    ``2a^2 + 3b^2 = 4`` forces ``b = 0``, ``a^2 = 2``, or ``|b| = 1``, ``2a^2 = 1``.
    """
    lattice = Lattices(ZZ)([[2, 0], [0, 3]])
    e, f = lattice.basis()

    assert lattice.vectors_of_square(1).cardinality() == 0
    assert lattice.vectors_of_square(2).cardinality() == 2
    assert lattice.vectors_of_square(3).cardinality() == 2
    assert lattice.vectors_of_square(4).cardinality() == 0
    assert lattice.vectors_of_square(5).cardinality() == 4
    assert (e + f).represents(5)
    assert not (e + f).represents(4)
    assert lattice.minimum() == 2
