r"""The tensor layer reads an element's coordinates, and its constructors take components.

An element of a framed module is not component data.  Its coordinates are the
coefficients of $v=\sum_i a_i e_i$ in the module's chosen framing $(e_i)$, a
convention of the tensor package and not a choice at each call site, and the
operation that states it is `tensor.coordinates(element)`: the type-$(1,0)$
tensor of those coefficients, read once from the element's retained coefficient
family and positioned by the framing's labels.

`tensor.vector(R, components)` and `tensor.covector(R, components)` take
component data.  An element handed to them is not one: it would supply its
components by being iterated, which is the module's coordinate order chosen at
the constructor, and `tensor.coordinates` is the operation that names the
element's framing instead.

Reading a tensor over another ring is the same kind of statement: it exists
exactly when every component lies in that ring, so the ring change decides it
and names the component that does not, with the position it stands at.  Left to
the conversion of one entry, a component outside the ring surfaces as a rational
that does not convert, and the caller that needs the decision is left to make it
one component at a time.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def _control():
    r"""`U + A2` over `ZZ`, in the framing $(e, f, a_1, a_2)$: $e$ isotropic, $b(e,f)=1$.

    The elements below are sparse in that framing -- $e$ is supported at the
    first label, $f$ at the second and $a_1$ at the third -- so a reading
    positioned by the framing's labels and not by the support's own order gives
    the zero components as well as the nonzero ones.
    """
    lattice = Lattices(ZZ)("U") + Lattices(ZZ)("A2")
    labels = tuple(lattice.module_generating_set())
    return (
        lattice,
        lattice.module_generator(labels[0]),
        lattice.module_generator(labels[1]),
        lattice.module_generator(labels[2]),
    )


def test_the_coordinates_of_an_element_are_its_coefficients_in_the_framing() -> None:
    r"""$e \mapsto (1,0,0,0)$, $f \mapsto (0,1,0,0)$, $a_1 \mapsto (0,0,1,0)$, $0 \mapsto (0,0,0,0)$.

    The last and the zero vector are the ones a reading off the support alone
    would get wrong: a sparse element holds no component for a basis vector it
    does not use, and the coordinate vector has to have one per label of the
    framing anyway.
    """
    lattice, isotropic, partner, orthogonal = _control()
    assert tensor.coordinates(isotropic) == tensor.vector(ZZ, (1, 0, 0, 0))
    assert tensor.coordinates(partner) == tensor.vector(ZZ, (0, 1, 0, 0))
    assert tensor.coordinates(orthogonal) == tensor.vector(ZZ, (0, 0, 1, 0))
    assert tensor.coordinates(lattice.zero()) == tensor.vector(ZZ, (0, 0, 0, 0))
    assert tuple(int(entry) for entry in tensor.coordinates(isotropic).tensor_valence()) == (1, 0)
    assert tensor.coordinates(isotropic).base_ring() == lattice.base_ring()


def test_the_coordinates_can_be_read_over_another_ring() -> None:
    r"""The transvection states its update over the fraction field, so $f \mapsto (0,1,0,0)$ there.

    Reading an element's coordinates and reading them over a larger ring are
    two operations: the coordinate vector is the element's, over the ring it
    lives on, and `change_ring` moves the coefficients.
    """
    _lattice, isotropic, partner, _orthogonal = _control()
    assert tensor.coordinates(isotropic).change_ring(QQ) == tensor.vector(
        QQ, (1, 0, 0, 0)
    )
    assert tensor.coordinates(partner).change_ring(QQ) == tensor.vector(
        QQ, (0, 1, 0, 0)
    )


def test_the_component_constructors_refuse_an_element() -> None:
    r"""`tensor.vector` and `tensor.covector` take components; `e` has a coordinate vector instead.

    A tensor built from the element by iterating it is the module's coordinate
    order reaching the constructor, which is what `tensor.coordinates` states.
    """
    _lattice, isotropic, _partner, _orthogonal = _control()
    with pytest.raises(TypeError):
        tensor.vector(ZZ, isotropic)
    with pytest.raises(TypeError):
        tensor.covector(ZZ, isotropic)
    assert tensor.coordinates(isotropic) == tensor.vector(ZZ, (1, 0, 0, 0))


def test_a_change_of_ring_names_the_component_that_leaves_it() -> None:
    r"""$(1, \tfrac12)$ is not integral: the ring change names $\tfrac12$ and its position.

    A change of coefficients is a statement about the tensor and the ring, and it
    holds exactly when every component lies in the ring.  The decision is the ring
    change's: a component outside the ring is refused by it, with the component
    and the position it stands at, and not by the conversion of that one entry,
    which names a rational and no position -- so a caller that needs the decision
    has to make it itself, one component at a time.
    """
    half = QQ(1) / QQ(2)
    coordinates = tensor.vector(QQ, (1, half))
    assert coordinates.component_outside(ZZ) == ((1,), half)
    with pytest.raises(ValueError):
        coordinates.change_ring(ZZ)
    integral = tensor.vector(QQ, (1, QQ(2)))
    assert integral.component_outside(ZZ) is None
    assert integral.change_ring(ZZ) == tensor.vector(ZZ, (1, 2))
