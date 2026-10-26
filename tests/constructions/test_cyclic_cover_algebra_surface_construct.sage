r"""A two-chart double-cover algebra exposes its local presentations, descent data, and deck maps."""

from sage_extensions.all import *  # noqa: F401,F403


def _double_cover_algebra():
    polynomials = QQ["x"]
    x = polynomials.algebra_generator("x")
    line = polynomials.affine_spectrum()
    cover = line.distinguished_open_cover(x, 1 - x)
    bundle = QuasiCoherentSheaves(line)(cover, {(0, 1): x})
    branch = bundle.tensor_power(2).section({0: 1, 1: x**2})
    return AlgebraSheaves(line).cyclic_cover(bundle, branch, 2), x


def test_double_cover_algebra_retains_branch_power_and_local_algebra_family() -> None:
    cyclic, x = _double_cover_algebra()
    locals_ = cyclic.local_algebras()

    assert cyclic.branch_power() == cyclic.line_bundle().tensor_power(2)
    assert cyclic.local_branch_coefficient(0) == 1
    assert cyclic.local_branch_coefficient(1) == x**2
    assert locals_[0] is cyclic.local_algebra(0)
    assert locals_[1] is cyclic.local_algebra(1)
    assert cyclic.local_underlying_module(0) is cyclic.local_algebra(0)
    assert cyclic.local_presentation(0) == cyclic.local_algebra(0).presentation()
    assert cyclic.local_multiplication(0) == cyclic.local_algebra(0).multiplication_morphism()


def test_double_cover_algebra_descent_surface_matches_its_gluing_datum() -> None:
    cyclic, x = _double_cover_algebra()
    gluing = cyclic.gluing_datum()
    transition = cyclic.transition(0, 1)
    source_z = transition.domain().algebra_generator("z")

    assert cyclic.sheaf() == gluing.sheaf()
    assert cyclic.underlying_module_datum() == gluing.underlying_module_datum()
    assert cyclic.sections() == gluing.compatible_sections()
    assert cyclic.restricted_algebra(0, 1) == gluing.restricted_algebra(0, 1)
    assert transition(source_z) == transition.codomain()(x) ** -1 * transition.codomain().algebra_generator("z")


def test_double_cover_algebra_relative_spectrum_and_deck_maps() -> None:
    cyclic, _x = _double_cover_algebra()
    projection = cyclic.relative_spectrum()
    global_deck = cyclic.deck_transformation(-1)
    local_deck = cyclic.local_deck_transformation(0, -1)
    local_z = cyclic.local_algebra(0).algebra_generator("z")
    local_action = cyclic.local_deck_group_scheme_action(0)

    assert projection.codomain() is cyclic.scheme()
    assert global_deck * global_deck == projection.domain().Mor(projection.domain()).identity()
    assert local_deck.coordinate_algebra_morphism()(local_z) == -local_z
    assert local_action.scheme() == cyclic.local_algebra(0).affine_spectrum()
