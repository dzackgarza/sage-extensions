r"""The setwise quotient action at an isotropic plane, and the plane row it feeds (#372).

The setwise stabilizer `P_I` of a primitive isotropic plane maps to `O(K_I)`,
`K_I = I^perp/I`, by the Levi quotient of Zemel, *The Structure of Integral
Parabolic Subgroups of Orthogonal Groups*, arXiv:1902.08264v2, section 1,
Lemma 1.1 (printed p. 5) and Proposition 1.6 (printed p. 10): the plane's own
action `GL(I)` and the class action `O(K_I)` are the two factors, and the kernel
is the unipotent radical extended by the plane actions that act trivially on
`K_I`.  The integral form of the two-factor structure is the block equation of
Dutour Sikirić--Hulek, arXiv:2302.01679v2, Theorem 4.9 (printed pp. 33--34):
`J = P_1 J Q_1^t` determines the complement's block from the plane action, the
third equation determines the class-mixing block, and the first is the linear
system for the remaining one whose integral solutions exist on a finite-index
subgroup of the plane actions only.

So a lift of a class action is a solution of that block system with `Q_3`
prescribed, and the kernel is the radical extended by the plane actions that
lift with a trivial class action.  This file drives both at Sterk's two plane
rows of `T_{En}` -- the split `P_1` and the non-split `P_2` -- and at a plane of
`T_{Co}`, and compares the plane-row count the class action feeds with card
`029J`'s `O` plane row, read by tag.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _second_representative(lattice):
    r"""Sterk's `P_2`: the plane that does not split off `T_{\mathrm{En}}`."""
    basis_elements = list(lattice.module_generators())
    first, second, third = basis_elements[0], basis_elements[1], basis_elements[2]
    w = basis_elements[4] + basis_elements[5]
    return lattice.primitive_isotropic_subobject(2 * first + 2 * second + w, third)


def _first_representative(lattice):
    r"""Sterk's `P_1`: the plane spanned by the first and third basis vectors."""
    basis_elements = tuple(lattice.module_generators())
    return lattice.primitive_isotropic_subobject(basis_elements[0], basis_elements[2])


def _coble_plane():
    r"""The plane of `T_{Co}` that #360 measured: `P = <ep + fp - sum a_i, 2h - (...)>`."""
    lattice = NamedLattices.Tco
    named = {
        str(label): lattice.module_generator(label)
        for label in lattice.module_generating_set()
    }
    first = named["ep"] + named["fp"] - sum(
        (named[f"a{index}"] for index in range(1, 9)), lattice.zero()
    )
    second = 2 * named["h"] - (
        named["a1"]
        + named["a2"]
        + sum((2 * named[f"a{index}"] for index in range(3, 8)), lattice.zero())
    )
    return lattice.primitive_isotropic_subobject(first, second)


def _check_the_setwise_action(plane):
    r"""Drive the image and the kernel at one plane, on computed values."""
    reduction = plane.isotropic_reduction()
    levi = reduction.levi_action()
    labels = tuple(reduction.module_generating_set())
    minus = reduction.O()({label: -reduction.module_generator(label) for label in labels})

    lift = levi.lift(minus)
    assert levi(lift) == minus
    assert lift in plane.parabolic_subgroup()
    assert all((~lift)(lift(vector)) == vector for vector in plane.ambient_lattice().module_generators())

    kernel = tuple(levi.kernel().group_generators())
    assert kernel != ()
    assert all(levi(generator) == levi.codomain().one() for generator in kernel)
    assert all(plane.acts_trivially_on_isotropic_reduction(generator) for generator in kernel)
    radical = tuple(plane.unipotent_radical_generators())
    assert all(generator in levi.kernel() for generator in radical)
    basis = plane.isotropic_basis()
    assert any(
        generator(vector) != vector for generator in kernel for vector in basis
    ), "the kernel of the class action is the pointwise radical, and no plane action lifts"
    return len(kernel), len(radical)


def test_the_setwise_action_returns_at_the_split_tenriques_plane() -> None:
    r"""`P_1` splits off `T_{\mathrm{En}}`: the class negation lifts, the kernel is generated."""
    plane = _first_representative(NamedLattices.TEn)
    _check_the_setwise_action(plane)


def test_the_setwise_action_returns_at_the_nonsplit_tenriques_plane() -> None:
    r"""`P_2` does not split: the same two answers come from the block equations alone."""
    plane = _second_representative(NamedLattices.TEn)
    assert plane.splitting_complement() is None
    _check_the_setwise_action(plane)


def test_the_setwise_action_returns_at_a_coble_plane() -> None:
    r"""The `T_{Co}` plane of #360: the same two answers, and the pointed part is not assumed."""
    plane = _coble_plane()
    assert plane.splitting_complement() is None
    _check_the_setwise_action(plane)


def test_the_tenriques_plane_row_is_the_card_row() -> None:
    r"""The plane row the class action feeds is card `029J`'s `O` plane row, read by tag.

    At a plane whose class stabilizer is filled by the plane's own stabilizer there
    is no extra factor between the `O(T_{\mathrm{En}})`-orbit of the plane and the
    orbit of its divided class set, so the hull of the class-set fibres is the
    plane row; the count is the public call's, and the value compared with it is
    the card's.
    """
    rows = tuple(NamedLattices.TEn.Aut().isotropic_orbit_representatives(2))
    assert cardinal(len(rows)) == card_plane_orbit_row("029J", "O")
