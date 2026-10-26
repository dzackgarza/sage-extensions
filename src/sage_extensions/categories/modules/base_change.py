r"""Scalar-extension helpers shared by owned module constructions."""

from sage_extensions.categories.rings.ring_foundation import (
    OwnedRings,
    _owned_ring,
)


def _base_change_codomain(module, ring_map):
    r"""Validate ``R -> S`` against ``module`` and return the owned ring ``S``."""
    target = _owned_ring(ring_map.codomain())
    module.base_ring().Mor(target, category=OwnedRings())(ring_map)
    return target


def _base_change_scalar(ring_map, scalar):
    r"""Apply ``R -> S`` and return the resulting element of the owned ring ``S``."""
    source = _owned_ring(ring_map.domain())
    target = _owned_ring(ring_map.codomain())
    return source.Mor(target, category=OwnedRings())(ring_map)(scalar)


def _base_change_element(module, changed_module, ring_map, element):
    r"""Apply the represented scalar-extension unit to one framed-module element."""
    coordinates = module.framing_morphism().lift(module(element))
    return changed_module.linear_combination(
        {
            label: _base_change_scalar(ring_map, coefficient)
            for label, coefficient in coordinates.parent()._selected_module_coefficients(coordinates).items()
        }
    )
