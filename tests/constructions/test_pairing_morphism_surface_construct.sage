r"""A pairing morphism retains its two factor modules and coordinate values."""

from sage_extensions.all import *  # noqa: F401,F403


def _rectangular_pairing():
    left = ZZ.free_module(2)
    right = ZZ.free_module(3)
    pairing = left.pairings_with(right, ZZ)([[1, 0, 2], [0, 1, 0]])
    return left, right, pairing


def test_pairing_morphism_retains_distinct_left_and_right_modules() -> None:
    left, right, pairing = _rectangular_pairing()

    assert pairing.left_module() is left
    assert pairing.right_module() is right
    assert pairing.domain().tensor_factor(0) is left
    assert pairing.domain().tensor_factor(1) is right


def test_pairing_morphism_coordinate_values_match_basis_pairing() -> None:
    left, right, pairing = _rectangular_pairing()
    coordinates = pairing.coordinate_values()
    labels = pairing.domain().module_generating_set()
    pair = labels[0]

    assert coordinates.index_set() is labels
    assert coordinates[pair] == pairing(
        left.module_generator(pair.component(0)),
        right.module_generator(pair.component(1)),
    )


def test_pairing_morphism_evaluates_bilinearly_on_nonbasis_elements() -> None:
    left, right, pairing = _rectangular_pairing()
    x = left.module_generator(0) + left.module_generator(1)
    y = right.module_generator(1) + right.module_generator(2)

    assert pairing(x, y) == ZZ(3)
