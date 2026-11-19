r"""The public pointed family at an odd lattice whose vector has divisibility above one.

The stabilizer of a primitive isotropic vector `v` sits in

    1 -> U_I -> P_I^1 -> M_I -> 1,

and the two constructions that answer it are the split section, whose
splitting forces divisibility one, and the residue action, which builds a
rational group out of one lift of each generator of `O(K_I)` and cuts the
integral stabilizer out of it over a finite module.  The residue action itself
needs no parity: what it needs is that its rational group contain the radical,
which the pointwise Levi kernel supplies at every divisibility and which the
perpendicular kernel does not -- an isometry fixing `I` and `I^\perp` pointwise
is the identity.

The specimens are Gram matrices: `U(2) + <3>` is odd of divisibility two and
`U(3) + <3>` is odd of divisibility three, so the divisibility-two lattice of
the earlier rows is covered in its odd form too.  The assertions are the
public surface's own: the family is non-empty, every member fixes the marked
vector, and every member preserves the form.  Nothing about the *group* the
family generates is asserted here: the witness that would decide it -- asking
whether a generator of the radical lies in the residue action's stabilizer --
is not available through the library, because an integral isometry is not
coerced into the action's rational group, and the question answers `False`
both before and after the kernel is added, even for an element that is a
generator of that group.
"""

from sage_extensions.all import *  # noqa: F401,F403

ODD_DIVISIBILITY_TWO = [[0, 2, 0], [2, 0, 0], [0, 0, 3]]
ODD_DIVISIBILITY_THREE = [[0, 3, 0], [3, 0, 0], [0, 0, 3]]


def _assert_the_public_family_answers(gram, divisibility) -> None:
    r"""The public family is non-empty, fixes the marked vector, and consists of isometries."""
    lattice = Lattices(ZZ)(gram)
    labels = tuple(lattice.module_generating_set())
    vector = lattice.module_generator(labels[0])

    assert lattice.is_even() is False
    assert vector.q() == ZZ(0)
    assert vector.is_primitive() is True
    assert vector.div() == ZZ(divisibility)

    family = tuple(lattice.Aut().stabilizer(vector).group_generators())

    assert family
    assert all(isometry(vector) == vector for isometry in family)
    assert all(
        lattice.b(isometry(left), isometry(right)) == lattice.b(left, right)
        for isometry in family
        for left in lattice.module_generators()
        for right in lattice.module_generators()
    )


def test_the_public_pointed_family_of_an_odd_divisibility_two_line_answers() -> None:
    r"""`U(2) + <3>`: `K_I = <3>`, divisibility two, and the family fixes its vector."""
    _assert_the_public_family_answers(ODD_DIVISIBILITY_TWO, 2)


def test_the_public_pointed_family_of_an_odd_divisibility_three_line_answers() -> None:
    r"""`U(3) + <3>`: divisibility three, so the answer is not a divisibility-two accident."""
    _assert_the_public_family_answers(ODD_DIVISIBILITY_THREE, 3)
