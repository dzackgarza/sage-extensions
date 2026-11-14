r"""Orthogonal scalar extension preserves explicit actions and inverse pairs."""

from sage_extensions.all import *


def test_orthogonal_scalar_extension_preserves_the_explicit_action_and_inverse_pairs():
    r"""Sigma and tau extend with their group law over QQ and finite prime fields."""
    lattice = Lattices(ZZ)([[0, 1, 0], [1, 0, 0], [0, 0, 2]])
    e, f, h = tuple(lattice.module_generators())
    sigma = lattice.Aut()((-f, -e, h))
    tau = lattice.Aut()((e, -e + f - h, -2 * e - h))
    for ring_map in (ZZ.fraction_field_map(), PrimeFields()(2).quotient_map(), PrimeFields()(5).quotient_map()):
        changed = lattice.base_change(ring_map)
        a, b, c = tuple(changed.module_generators())
        extension = lattice.orthogonal_group_base_change(ring_map)
        sigma_image = extension(sigma)
        tau_image = extension(tau)
        assert sigma_image.domain() is changed and sigma_image.codomain() is changed
        assert sigma_image(a) == -b and sigma_image(b) == -a and sigma_image(c) == c
        assert tau_image(a) == a
        assert tau_image(b) == -a + b - c and tau_image(c) == -2 * a - c
        product_image = extension(sigma * tau)
        inverse_image = extension(~tau)
        for point in (a, b, c):
            assert product_image(point) == sigma_image(tau_image(point))
            assert inverse_image(tau_image(point)) == point
