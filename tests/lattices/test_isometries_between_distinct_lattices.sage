r"""Isometries between distinct integral lattice objects, and their transport.

``L.Isom(L_prime)`` constructs the isometry homset between two lattice objects.
Distinct isometric endpoints with nontrivial discriminant construct, invert, and
induce mutually inverse isometries of their discriminant modules; that transport
between orbit lattices is what the exact finite discriminant image of #310
composes.

The specimen is two distinct parents with the same form, ``U + <-2>`` and its Gram
tensor, so the construction runs with a nontrivial discriminant group and without
any cached-parent shortcut.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _isometric_pair():
    r"""``U + <-2>`` twice, as two distinct objects of ``Lattices(ZZ)``.

    The second is given by its Gram tensor rather than by the same sum, so the two
    are distinct parents and not one cached construction.
    """
    first = Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])
    second = Lattices(ZZ)([[0, 1, 0], [1, 0, 0], [0, 0, -2]])
    return first, second


def test_distinct_isometric_lattices_construct_an_invertible_isometry() -> None:
    r"""``Isom`` between distinct endpoints: form-preserving, invertible, discriminant-inverse."""

    first, second = _isometric_pair()
    assert first is not second
    assert first.module_rank() == second.module_rank()
    assert first.discriminant_group().cardinality() == cardinal(2)
    assert second.discriminant_group().cardinality() == cardinal(2)

    homset = first.Isom(second)
    labels = tuple(first.module_generating_set())
    targets = tuple(second.module_generating_set())
    isometry = homset(
        {
            label: second.module_generator(target)
            for label, target in zip(labels, targets, strict=True)
        }
    )
    assert isometry.domain() is first
    assert isometry.codomain() is second

    inverse = isometry.inverse()
    assert inverse.domain() is second
    assert inverse.codomain() is first
    for label in labels:
        generator = first.module_generator(label)
        assert inverse(isometry(generator)) == generator

    forward = isometry.discriminant_isometry()
    backward = inverse.discriminant_isometry()
    assert forward.domain() is first.discriminant_group()
    assert forward.codomain() is second.discriminant_group()
    for element in first.discriminant_group():
        assert backward(forward(element)) == element
    for element in second.discriminant_group():
        assert forward(backward(element)) == element
