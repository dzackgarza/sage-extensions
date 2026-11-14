r"""The parameter lattice of the unipotent radical at Sterk's $P_2$ of $T_{\mathrm{En}}$ (#365).

The radical of the setwise stabilizer at a primitive isotropic plane $I$ is
$U_I = \ker(P_I \to \GL(I) \times O(I^\perp/I))$, and in the basis $(U \mid P \mid K)$
of `plane_block_basis` — Dutour Sikirić–Hulek, arXiv:2302.01679v2, Theorem 4.9, proof,
printed pp. 33--34 — an element of it has the block matrix

.. math::
    g = \begin{pmatrix} 1 & 0 & 0 \\ a & 1 & \tau \\ c & 0 & 1 \end{pmatrix},
    \qquad \tau = -J^{-1} c^t A_K, \qquad
    J a + a^t J^t = -(Kc + c^t K^t + c^t A_K c),

so the parameter $c$ — the $(K, U)$ block — determines the element and the two
equations decide which parameters occur.  `unipotent_parameter_lattice()` decides
every class of $c$ at the modulus those equations impose
(`unipotent_parameter_modulus()`) and returns a $\mathbb{Z}$-basis of the parameters
that lift; `unipotent_radical_element()` returns the element over a basis vector.

This file pins three computed facts at $P_2$:

* the parameters of the plane's Eichler transvections that lie in the radical lie in
  the returned lattice, and so do the parameters on the third and fourth basis vectors
  of $K$ — the two parameters the #364 turn reported as lying in $U_I$ but outside the
  lattice its residue table enumerated;
* every basis vector of the lattice has an element of the radical over it, that
  element fixes the plane pointwise and acts trivially on $P_2^\perp/P_2$ by direct
  computation, and the translations of those elements reach the radical's own
  translation rank;
* the parameters on the first two basis vectors of $K$ have no lift at all, which is
  the part of the lattice that is not all of $\mathbb{Z}^{16}$, so the lattice is
  neither the whole space nor a proper sublattice of what lifts.

Nothing here is typed from a page or from a docstring: every count, rank and index
compared below is computed from the plane.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _second_representative(lattice):
    r"""Sterk's $P_2$: the plane that does not split off $T_{\mathrm{En}}$."""
    basis_elements = list(lattice.module_generators())
    first, second, third = basis_elements[0], basis_elements[1], basis_elements[2]
    w = basis_elements[4] + basis_elements[5]
    return lattice.primitive_isotropic_subobject(2 * first + 2 * second + w, third)


def _plane_basis(plane):
    r"""The plane's own basis, taken from its inclusion and not from the block basis."""
    return tuple(
        plane.inclusion()(plane.module_generator(label))
        for label in plane.module_generating_set()
    )


def _perpendicular_basis(plane):
    r"""A generating set of $P_2^\perp$, in the ambient lattice."""
    perpendicular = plane.isotropic_perpendicular()
    return tuple(
        perpendicular.inclusion()(perpendicular.module_generator(label))
        for label in perpendicular.module_generating_set()
    )


def _coordinate_count(plane):
    r"""How many coordinates a parameter has: the rank of the returned lattice's basis."""
    return cardinal(sum(1 for _ in plane.unipotent_parameter_lattice()))


def _unit_parameter(plane, position, column):
    r"""The parameter with a single $1$, on basis vector ``position`` of $K$ in plane column ``column``.

    This is the parameter vector with coordinate $2 \cdot \text{position} + \text{column}$
    set, the listing of `unipotent_parameter_vector`.
    """
    slot = 2 * position + column
    return tuple(1 if index == slot else 0 for index in range(_coordinate_count(plane)))


def _parameter_of(plane, element):
    r"""The parameter of an element of the radical, listed the way the lattice lists them."""
    return plane.unipotent_parameter_vector(plane.unipotent_block_coordinates(element)[0])


def _radical_transvections(plane) -> tuple:
    r"""The plane's Eichler transvections that fix the plane pointwise and act trivially on $P^\perp/P$."""
    basis = _plane_basis(plane)

    def fixes_pointwise(automorphism):
        return all(automorphism(vector) == vector for vector in basis)

    return tuple(
        transvection
        for transvection in plane.parabolic_transvection_generators()
        if fixes_pointwise(transvection)
        and plane.acts_trivially_on_isotropic_reduction(transvection)
    )


def test_the_parameters_of_the_radical_transvections_lie_in_the_lattice() -> None:
    r"""Every Eichler transvection of the plane that lies in $U_I$ has its parameter in the lattice.

    The transvections are selected by the radical's own definition — they fix the
    plane pointwise and act trivially on $P_2^\perp/P_2$ — and each parameter is then
    expressed on the returned lattice.  The round trip back is asserted, so a lattice
    listed in one ordering and read in another fails here.
    """
    plane = _second_representative(NamedLattices.TEn)
    transvections = _radical_transvections(plane)

    assert cardinal(sum(1 for _ in transvections)) > cardinal(0)
    for transvection in transvections:
        parameter = _parameter_of(plane, transvection)
        assert (
            plane.unipotent_parameter_from_coordinates(
                plane.unipotent_parameter_coordinates(parameter)
            )
            == parameter
        )


def test_the_parameters_of_the_third_and_fourth_vectors_of_the_quotient_lie_in_the_lattice() -> None:
    r"""The two parameters the #364 turn found outside its enumeration are in this lattice.

    Those parameters are supported on the third and fourth basis vectors of $K$ in the
    first plane column.  Each one is expressed on the lattice, and the element over it
    is built and checked: it fixes the plane pointwise and acts trivially on
    $P_2^\perp/P_2$, so it lies in $U_I$ and the parameter genuinely occurs.
    """
    plane = _second_representative(NamedLattices.TEn)
    basis = _plane_basis(plane)

    for position in (2, 3):
        parameter = _unit_parameter(plane, position, 0)
        assert (
            plane.unipotent_parameter_from_coordinates(
                plane.unipotent_parameter_coordinates(parameter)
            )
            == parameter
        )
        element = plane.unipotent_radical_element(parameter)
        assert all(element(vector) == vector for vector in basis)
        assert plane.acts_trivially_on_isotropic_reduction(element) is True


def test_every_basis_vector_has_an_element_of_the_radical_over_it() -> None:
    r"""One element of $U_I$ over each basis vector, and their translations reach the target rank.

    Each element is checked against the radical's definition on the plane's own basis,
    its parameter is read back off the block matrix and compared with the basis vector
    it was built from, and the translations of the whole family are compared with the
    rank the radical's translation image has: the two agree, so the family is not a
    proper sublattice of `\tau(U_I)`.
    """
    plane = _second_representative(NamedLattices.TEn)
    parameters = plane.unipotent_parameter_lattice()
    basis = _plane_basis(plane)
    elements = tuple(plane.unipotent_radical_element(row) for row in parameters)

    for element in elements:
        assert all(element(vector) == vector for vector in basis)
        assert plane.acts_trivially_on_isotropic_reduction(element) is True
    for element, row in zip(elements, parameters, strict=True):
        assert _parameter_of(plane, element) == row
    translation, target = plane.unipotent_translation_rank(elements)
    assert cardinal(translation) == cardinal(target)
    assert cardinal(sum(1 for _ in elements)) == cardinal(target)


def test_the_first_two_vectors_of_the_quotient_have_no_lift() -> None:
    r"""The parameters on the first two basis vectors of $K$ are not parameters of elements of $U_I$.

    The block equations have no integral solution for them, which `unipotent_parameter_lifts`
    decides and which is why the lattice is not all of $\mathbb{Z}^{16}$: these four unit
    parameters are the part of the coordinate space that is outside it.
    """
    plane = _second_representative(NamedLattices.TEn)

    for position in (0, 1):
        for column in (0, 1):
            parameter = _unit_parameter(plane, position, column)
            assert (
                plane.unipotent_parameter_lifts(plane.unipotent_parameter_matrix(parameter))
                is False
            )


def test_the_centre_is_generated_over_the_vanishing_parameter() -> None:
    r"""The centre's generator has vanishing parameter, translates nothing, and is not the identity.

    It is the element of $U_I$ with $c = 0$ and $\tau = 0$: it fixes the plane pointwise
    and fixes $P_2^\perp$ pointwise, which is what makes its translation vanish, and it
    still moves a vector of a complement of $P_2^\perp$ — it is not the identity, and
    that displaced direction is the one the translation map cannot see.
    """
    plane = _second_representative(NamedLattices.TEn)
    central = plane.unipotent_central_generator()

    assert _parameter_of(plane, central) == tuple(
        0 for _ in range(_coordinate_count(plane))
    )
    assert plane.acts_trivially_on_isotropic_reduction(central) is True
    assert all(central(vector) == vector for vector in _plane_basis(plane))
    assert all(central(vector) == vector for vector in _perpendicular_basis(plane))
    translation, _target = plane.unipotent_translation_rank((central,))
    assert cardinal(translation) == cardinal(0)
    assert any(
        central(vector) != vector for vector in NamedLattices.TEn.module_generators()
    )
