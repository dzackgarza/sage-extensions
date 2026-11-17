r"""A basis adapted to a null flag is a basis of the plane it is adapted in.

The null plane ``<e_0, e_2>`` of ``U + U(2) + <-6>`` carries the zero form, so
every vector in it is isotropic and every primitive one of them spans a null
line there.  In the plane's own basis the line ``Z(2 e_0 + e_1)`` is the
coordinate row ``(2, 1)``.  Over the integers that row is primitive and
completes to the basis ``((2, 1), (1, 0))`` of determinant ``-1``; the Smith form
of a row taken in the fraction field instead has the unimodular factor
``((1, -1/2), (0, 1))``, whose inverse is not a basis change of the integer
plane, and the rows it rebases have determinant ``2``.  The adapted basis is
therefore not a basis, and the stabilizer cannot invert the basis change it
conjugates its generators by.

What is asserted is the mathematics of the adapted basis: it inverts, and it
carries the flag's first block onto the flag's own first term.
"""

from sage_extensions.all import *


def _null_plane():
    r"""The rank-two zero-form plane ``<e_0, e_2>`` of ``U + U(2) + <-6>``."""
    lattice = (
        Lattices(ZZ)("U")
        + Lattices(ZZ)(((0, 2), (2, 0)))
        + Lattices(ZZ)(((-6,),))
    )
    e_0, _e_1, e_2, _e_3, _e_4 = tuple(lattice.module_generators())
    return lattice.primitive_isotropic_subobject(e_0, e_2).inclusion().domain()


def _plane_basis(plane):
    r"""The plane's own two basis vectors, in the order its generating set labels them."""
    return tuple(plane.module_generator(label) for label in plane.module_generating_set())


def test_the_basis_adapted_to_a_null_line_in_a_null_plane_inverts():
    r"""``Z(2 e_0 + e_1)`` in the null plane: the adapted basis is a basis of the plane."""
    plane = _null_plane()
    first, second = _plane_basis(plane)
    generator_of_the_line = 2 * first + second
    line = plane.primitive_isotropic_subobject(generator_of_the_line)
    general_linear = plane.general_linear_group()
    stabilizer = general_linear.flag_stabilizer((line,))
    change = stabilizer.basis_change()
    assert change * ~change == general_linear.one()
    assert line.inclusion().is_in_image(change(first))
    assert not line.inclusion().is_in_image(change(second))
    for generator in stabilizer.group_generators():
        assert line.inclusion().is_in_image(generator(generator_of_the_line))


def test_the_basis_adapted_to_a_null_plane_inverts():
    r"""The empty flag of the null plane: a basis adapted to it is still a basis of the plane."""
    plane = _null_plane()
    first, second = _plane_basis(plane)
    general_linear = plane.general_linear_group()
    change = general_linear.flag_stabilizer(()).basis_change()
    assert change * ~change == general_linear.one()
    assert (~change)(change(first)) == first
    assert (~change)(change(second)) == second
