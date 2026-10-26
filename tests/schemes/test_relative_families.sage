from sage_extensions.all import *


def test_xy_equals_t_family_retains_morphism_special_fiber_and_nonsmooth_locus() -> None:
    parameter = QQ.polynomial_ring("t")
    t = parameter.algebra_generator("t")
    family = parameter.affine_equation_family(
        ("x", "y"),
        lambda presentation: (
            presentation.algebra_generator("x")
            * presentation.algebra_generator("y")
            - presentation(t),
        ),
    )

    assert family.structure_morphism().domain() is family
    assert family.structure_morphism().codomain() is family.base_scheme()
    assert family.as_slice_object().arrow() is family.structure_morphism()
    assert family.is_flat()

    special = family.fiber_over_ideal(parameter.ideal(t))
    special_algebra = special.coordinate_algebra()
    assert special_algebra.algebra_generator("x") * special_algebra.algebra_generator("y") == special_algebra.zero()

    nonsmooth = family.relative_nonsmooth_subscheme()
    xbar = family.coordinate_algebra().algebra_generator("x")
    ybar = family.coordinate_algebra().algebra_generator("y")
    assert nonsmooth.defining_ideal_owned() == family.coordinate_algebra().ideal(xbar, ybar)
