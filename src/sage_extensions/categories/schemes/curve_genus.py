r"""Projective curve normalizations and residue-weighted genus defects.

For a reduced integral projective curve ``C`` with finite normalization
``nu:C^nu -> C``, the normalization sequence

``0 -> O_C -> nu_* O_Cnu -> Q -> 0``

has ``Q`` supported at the nonnormal closed points.  Stacks Project, Tag
``0C1R``, identifies the stalk length with the local delta invariant.  Taking
Euler characteristics gives

``p_a(C) = g(C^nu) + sum_p delta_p [kappa(p):k]``

for the represented geometrically integral curves below.  The residue degree is
part of each contribution, so a nonrational closed point is not split into
geometric points and then counted as if each were rational.

The two supplied plane quintics have explicit normalization maps from ``P^1``.
Their local delta invariants are computed independently by Singular
``normal.lib::deltaLoc`` through :class:`IsolatedHypersurfaceSingularity`; the
global genus relation only checks that these local contributions exhaust the
normalization defect.
"""

from sage.misc.cachefunc import cached_method
from sage.rings.rational_field import QQ as SageQQ
from sage.structure.sage_object import SageObject

from sage_extensions.categories.rings.ring_foundation import (
    _own_ring,
    _owned_rationals,
)
from sage_extensions.categories.schemes.schemes import (
    ProjectiveSpaces,
    Schemes,
)
from sage_extensions.categories.schemes.singularities import (
    IsolatedHypersurfaceSingularity,
)
from sage_extensions.categories.schemes.varieties import Curves
from sage_extensions.categories.sets.finite_families import finite_family

_RATIONALS = _owned_rationals()


class CurveLocalDeltaContribution(SageObject):
    r"""One closed singular point with its local delta and residue degree."""

    def __init__(self, singularity, point, *, projective_support=None) -> None:
        assert point.parent().ring() is singularity.polynomial_ring(), (
            f"the point {point} is not a point of the plane of the singularity {singularity}: "
            f"its coordinates lie in {point.parent().ring()}, not in {singularity.polynomial_ring()}"
        )
        self._singularity = singularity
        self._point = point
        self._projective_support = projective_support

    def singularity(self):
        return self._singularity

    def local_point(self):
        return self._point

    def projective_support(self):
        return self._projective_support

    @cached_method
    def delta_invariant(self):
        return self.singularity().delta_invariant_at(self.local_point())

    @cached_method
    def residue_degree(self):
        return self.local_point().residue_degree()

    @cached_method
    def weighted_contribution(self):
        return self.singularity().delta_contribution_over_base(self.local_point())

    def _repr_(self):
        return (
            f"delta={self.delta_invariant()} at {self.projective_support()!r} "
            f"with residue degree {self.residue_degree()}"
        )


class _CurveGenusComparison(SageObject):
    r"""The normalization-sequence equality between arithmetic and geometric genus."""

    def __init__(self, curve) -> None:
        self._curve = curve
        assert self.arithmetic_genus() == self.geometric_genus() + self.total_delta_contribution(), (
            f"the genus formula p_a = g + sum of delta invariants fails for {curve}: "
            f"arithmetic genus {self.arithmetic_genus()}, geometric genus {self.geometric_genus()}, "
            f"total delta {self.total_delta_contribution()}; some singular point is missing or "
            "has the wrong delta invariant"
        )

    def normalization_data(self):
        return self._curve

    def arithmetic_genus(self):
        return self.normalization_data().arithmetic_genus()

    def geometric_genus(self):
        return self.normalization_data().normalization_curve().arithmetic_genus()

    def total_delta_contribution(self):
        return self.normalization_data().total_delta_contribution()

    def holds(self) -> bool:
        return True

    def _repr_(self) -> str:
        return f"Genus comparison: p_a={self.arithmetic_genus()}, g={self.geometric_genus()}, delta={self.total_delta_contribution()}"





def _quintic_with_chosen_normalization(equation, plane, coordinate_formula, local_delta_contributions):
    r"""The plane quintic ``V(equation)`` constructed with the normalization ``[s:t] |-> formula(s, t)``."""
    base = plane.scheme_base_ring()
    normalization = ProjectiveSpaces(base)(1, names=("s", "t"))
    ring = normalization.O(5).global_sections().homogeneous_coordinate_ring()
    coordinates = coordinate_formula(ring.algebra_generator("s"), ring.algebra_generator("t"))
    return Curves(base).from_equation(
        equation,
        plane,
        normalization_curve=normalization,
        normalization_coordinates=finite_family(tuple(coordinates), name="Homogeneous coordinates of the normalization"),
        local_delta_contributions=finite_family(tuple(local_delta_contributions), name="Local delta contributions"),
    )


def _origin_contribution(equation, *, projective_support):
    plane = equation.parent()
    singularity = IsolatedHypersurfaceSingularity(plane, equation)
    point = plane.spectrum()(plane.ideal(*tuple(plane.algebra_generators())))
    return CurveLocalDeltaContribution(
        singularity,
        point,
        projective_support=projective_support,
    )


def rational_quintic_with_two_nodes_normalization():
    r"""Return a rational quintic with two affine nodes and one point at infinity.

    ``C: Y^2 Z^3 = X(X-Z)^2(X-4Z)^2`` has the normalization

    ``[s:t] |-> [s^2 t^3 : s(s^2-t^2)(s^2-4t^2) : t^5]``.
    """
    plane = ProjectiveSpaces(_RATIONALS)(2, names=("X", "Y", "Z"))
    ring = plane.O(5).global_sections().homogeneous_coordinate_ring()
    X = ring.algebra_generator("X")
    Y = ring.algebra_generator("Y")
    Z = ring.algebra_generator("Z")

    local = _RATIONALS.polynomial_ring(("u", "v"))
    u, v = tuple(local.algebra_generators())
    first = _origin_contribution(
        v**2 - (u + 1) * u**2 * (u - 3) ** 2,
        projective_support=(1, 0, 1),
    )
    second = _origin_contribution(
        v**2 - (u + 4) * (u + 3) ** 2 * u**2,
        projective_support=(4, 0, 1),
    )
    infinity = _origin_contribution(
        v**3 - u * (u - v) ** 2 * (u - 4 * v) ** 2,
        projective_support=(0, 1, 0),
    )
    curve = _quintic_with_chosen_normalization(
        Y**2 * Z**3 - X * (X - Z) ** 2 * (X - 4 * Z) ** 2,
        plane,
        lambda s, t: (
            s**2 * t**3,
            s * (s**2 - t**2) * (s**2 - 4 * t**2),
            t**5,
        ),
        (first, second, infinity),
    )
    return curve.normalization_data()


def rational_quintic_with_nonrational_node_normalization():
    r"""Return a rational quintic with one degree-two singular closed point.

    ``C: Y^2 Z^3 = X(X^2+Z^2)^2`` is normalized by

    ``[s:t] |-> [s^2 t^3 : s(s^4+t^4) : t^5]``.

    On ``Z=1`` the singular prime ``(x^2+1,y)`` has residue degree two.  Its
    local delta is one at each conjugate geometric point, so the one closed
    point contributes ``2`` over ``QQ``; it is never expanded into two entries.
    """
    plane = ProjectiveSpaces(_RATIONALS)(2, names=("X", "Y", "Z"))
    ring = plane.O(5).global_sections().homogeneous_coordinate_ring()
    X = ring.algebra_generator("X")
    Y = ring.algebra_generator("Y")
    Z = ring.algebra_generator("Z")

    affine = _RATIONALS.polynomial_ring(("x", "y"))
    x, y = tuple(affine.algebra_generators())
    affine_singularity = IsolatedHypersurfaceSingularity(
        affine,
        y**2 - x * (x**2 + 1) ** 2,
    )
    nonrational_point = affine.spectrum()(affine.ideal(x**2 + 1, y))
    nonrational = CurveLocalDeltaContribution(
        affine_singularity,
        nonrational_point,
        projective_support="V(X^2+Z^2,Y) on Z != 0",
    )

    infinity_ring = _RATIONALS.polynomial_ring(("x", "z"))
    x_inf, z_inf = tuple(infinity_ring.algebra_generators())
    infinity = _origin_contribution(
        z_inf**3 - x_inf * (x_inf**2 + z_inf**2) ** 2,
        projective_support=(0, 1, 0),
    )
    curve = _quintic_with_chosen_normalization(
        Y**2 * Z**3 - X * (X**2 + Z**2) ** 2,
        plane,
        lambda s, t: (
            s**2 * t**3,
            s * (s**4 + t**4),
            t**5,
        ),
        (nonrational, infinity),
    )
    return curve.normalization_data()


__all__ = [
    "CurveLocalDeltaContribution",
    "rational_quintic_with_nonrational_node_normalization",
    "rational_quintic_with_two_nodes_normalization",
]
