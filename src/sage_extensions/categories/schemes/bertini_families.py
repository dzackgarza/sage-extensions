r"""A Bertini application with an actual smooth locus and exceptional member.

The Hesse pencil on ``P^2`` is spanned by

``x^3+y^3+z^3`` and ``xyz``.

On the affine parameter line ``A^1_QQ = Spec QQ[t]`` the family is
``x^3+y^3+z^3-3txyz=0``.  In characteristic zero the Jacobian equations have a
projective solution exactly when ``t^3=1``.  Thus the theorem's conclusion is
the represented open ``D(t^3-1)`` in the parameter line, not a claim that
every member is smooth.  The fibre ``t=0`` is the Fermat cubic and is smooth;
``t=1`` is an explicit singular member of the same family.

The family is an object of the slice ``Sch_QQ/A^1_QQ``: the closed subscheme
``X = V(x^3+y^3+z^3-3txyz) <= P^2_QQ x A^1_QQ`` with the second projection
``f: X -> A^1_QQ``.  Its fibre over the rational point ``t = a`` is the
fibre product ``X x_{A^1} Spec QQ``.

The pencil has base points.  One rational base point ``[1:-1:0]`` is retained
with its actual value and first-jet evaluation maps, so the application keeps
the base-locus hypothesis visible rather than silently treating the pencil as
basepoint free.
"""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.rings.ring_foundation import _owned_rationals
from sage_extensions.categories.schemes.complete_intersections import (
    ProjectiveCompleteIntersections,
)
from sage_extensions.categories.schemes.families import _projective_hypersurface_family
from sage_extensions.categories.schemes.schemes import (
    AffineSpaces,
    ProjectiveSpaces,
    Schemes,
    _evaluate_owned_homogeneous_polynomial_on_coordinates,
)
from sage_extensions.validation import validator


class _HessePencil:
    r"""Private realization of the Hesse family as an object of ``Sch_QQ/A^1_QQ``.

    The slice object itself retains the family ``f: X -> A^1_QQ``.  This
    engine adds the plane ``P^2_QQ``, the equation of ``X`` in
    ``QQ[t][x,y,z]``, and the pencil on ``P^2_QQ`` with its selected base
    point.
    """

    def __init__(
        self,
        *,
        base_field,
        parameter,
        plane,
        equation,
        line_bundle,
        linear_system,
        fermat_section,
        product_section,
        basepoint,
        **rest,
    ) -> None:
        self._base_field = base_field
        self._parameter = parameter
        self._plane = plane
        self._equation = equation
        self._line_bundle = line_bundle
        self._linear_system = linear_system
        self._fermat_section = fermat_section
        self._product_section = product_section
        self._basepoint = basepoint
        super().__init__(**rest)

    def base_field(self):
        return self._base_field

    def parameter_ring(self):
        return self.parameter_scheme().coordinate_algebra()

    def parameter(self):
        return self._parameter

    def parameter_scheme(self):
        return self.arrow().codomain()

    def family(self):
        r"""The family as an object of ``Sch_QQ/A^1_QQ``; its morphism ``X -> A^1_QQ`` is :meth:`arrow`."""
        return self

    def linear_system(self):
        return self._linear_system

    def base_locus(self):
        return self.linear_system().base_locus()

    def basepoint(self):
        return self._basepoint

    @cached_method
    def base_locus_point(self):
        return self.base_locus().corestriction(self.basepoint())

    @cached_method
    def basepoint_value_evaluation(self):
        return self._line_bundle.jet_evaluation(self.basepoint(), 1)

    @cached_method
    def basepoint_first_jet_evaluation(self):
        return self._line_bundle.jet_evaluation(self.basepoint(), 2)

    @validator
    def validate_basepoint(self) -> None:
        r"""Check that ``[1:-1:0]`` is a base point: both spanning sections vanish there."""
        evaluation = self.basepoint_value_evaluation()
        for section in (self._fermat_section, self._product_section):
            if evaluation(section) != evaluation.codomain().zero():
                raise ValueError(
                    f"the point {self.basepoint()} of {self.basepoint().codomain()} is not a base "
                    f"point of the Hesse pencil: the section {section} does not vanish there"
                )

    def discriminant(self):
        t = self.parameter()
        return t**3 - self.parameter_ring().one()

    @cached_method
    def good_parameter_locus(self):
        r"""Return ``D(t^3-1)``, exactly the smooth-fibre locus on this chart."""
        return self.parameter_scheme().distinguished_open(self.discriminant())

    @cached_method
    def exceptional_parameter_locus(self):
        r"""Return ``V(t^3-1)``, the singular-fibre locus on this chart."""
        return self.parameter_scheme().closed_subscheme(self.discriminant())

    def parameter_is_good(self, value) -> bool:
        value = self.base_field()(value)
        return value**3 != self.base_field().one()

    def member(self, value):
        r"""The plane cubic ``V(x^3+y^3+z^3-3a xyz) <= P^2_QQ`` for ``a = value``.

        It is the equation of ``X`` with ``t`` specialized to ``a``, as an
        object of ``ProjectiveCompleteIntersections(QQ)``.  The fibre
        :meth:`fibre` over the point ``t = a`` is the same curve presented as
        a fibre product.
        """
        value = self.base_field()(value)
        plane = self._plane
        ring = self._line_bundle.global_sections().homogeneous_coordinate_ring()
        specialization = self.parameter_ring().Mor(self.base_field())({"t": value})
        specialized = _evaluate_owned_homogeneous_polynomial_on_coordinates(
            self._equation,
            self._equation.parent(),
            tuple(ring.algebra_generator(name) for name in ("x", "y", "z")),
            coefficient_map=ring.algebra_structure_morphism() * specialization,
        )
        return ProjectiveCompleteIntersections(self.base_field())(plane, specialized)

    @cached_method
    def general_member(self):
        return self.member(self.base_field().zero())

    @cached_method
    def exceptional_member(self):
        return self.member(self.base_field().one())

    @cached_method
    def restriction_to_good_locus(self):
        r"""The restriction ``f^{-1}(U) -> U -> A^1_QQ`` of the family to ``U = D(t^3-1)``.

        ``f^{-1}(U) <= X`` is the fibre product ``X x_{A^1} U``, an object of
        ``Sch_QQ/A^1_QQ`` through ``f`` restricted to it.
        """
        preimage = self.arrow().inverse_image(self.good_parameter_locus())
        return self.category().object(self.arrow() * preimage.inclusion())

    @cached_method
    def projective_pencil(self):
        r"""The pencil over its whole parameter line, as an object of ``Sch_QQ/P^1_QQ``.

        The members of ``<x^3+y^3+z^3, xyz>`` are ``s(x^3+y^3+z^3) - 3t xyz``
        for ``[s:t] in P^1_QQ`` (Artebani--Dolgachev, *The Hesse pencil of
        plane cubic curves*, arXiv:math/0611590, section 2).  The total space
        is the closed subscheme ``V(s(x^3+y^3+z^3) - 3t xyz) <= P^2_QQ x P^1_QQ``
        of bidegree ``(3, 1)``, and the family is its second projection.  Over
        the chart ``s != 0`` it is the affine family :meth:`arrow`; the
        member ``[0:1]`` is the triangle ``xyz = 0``.
        """
        base = self.base_field()
        line = ProjectiveSpaces(base)(1, names=("s", "t"))
        product = Schemes(base).product((self._plane, line))
        ring = product.O(3, 1).global_sections().homogeneous_coordinate_ring()
        x, y, z, s, t = (ring.algebra_generator(name) for name in ("x0_0", "x0_1", "x0_2", "x1_0", "x1_1"))
        total = product.closed_subscheme(s * (x**3 + y**3 + z**3) - ring(3) * t * x * y * z)
        return Schemes(base).SliceOver(line).object(product.projection(1) * total.inclusion())

    def good_locus_restriction_map(self):
        r"""The inclusion ``f^{-1}(U) -> X`` as a morphism of ``Sch_QQ/A^1_QQ``."""
        restricted = self.restriction_to_good_locus()
        preimage = restricted.arrow().domain()
        return self.category().Mor(restricted, self)(preimage.inclusion())

    def theorem_hypotheses(self) -> bool:
        r"""The selected Hesse/Bertini calculation uses characteristic zero."""
        return int(self.base_field().characteristic()) == 0

    def theorem_conclusion_is_exact(self) -> bool:
        r"""Record the computed conclusion without upgrading it to every fibre."""
        return (
            self.theorem_hypotheses()
            and self.parameter_is_good(self.base_field().zero())
            and not self.parameter_is_good(self.base_field().one())
        )

    def _repr_(self) -> str:
        return f"Hesse-Bertini family over {self.parameter_scheme()} with good locus {self.good_parameter_locus()}"


def HesseBertiniFamily(check=False):
    r"""Return the Hesse cubic pencil as an object of ``Sch_QQ/A^1_QQ``.

    The object is ``X = V(x^3+y^3+z^3-3txyz) <= P^2_QQ x A^1_QQ`` with the
    second projection ``f: X -> A^1_QQ``, together with the pencil
    ``<x^3+y^3+z^3, xyz> <= H^0(P^2_QQ, O(3))`` and its base point
    ``[1:-1:0]``.
    """
    base = _owned_rationals()
    line = AffineSpaces(base)(1, names=("t",))
    parameter = line.coordinate_algebra()
    t = parameter.algebra_generator("t")
    plane = ProjectiveSpaces(base)(2, names=("x", "y", "z"))
    relative_ring = parameter.polynomial_ring(("x", "y", "z"))
    x = relative_ring.algebra_generator("x")
    y = relative_ring.algebra_generator("y")
    z = relative_ring.algebra_generator("z")
    scalar = relative_ring.algebra_structure_morphism()
    equation = x**3 + y**3 + z**3 - scalar(parameter(3) * t) * x * y * z
    family = _projective_hypersurface_family(plane, line, equation, name="Hesse pencil")

    bundle = plane.O(3)
    sections = bundle.global_sections()
    ring = sections.homogeneous_coordinate_ring()
    rx = ring.algebra_generator("x")
    ry = ring.algebra_generator("y")
    rz = ring.algebra_generator("z")
    fermat = sections.section_from_homogeneous_polynomial(rx**3 + ry**3 + rz**3)
    product = sections.section_from_homogeneous_polynomial(rx * ry * rz)

    pencil = Schemes(base).SliceOver(line).object(
        family,
        _engine=_HessePencil,
        construction_data={
            "base_field": base,
            "parameter": t,
            "plane": plane,
            "equation": equation,
            "line_bundle": bundle,
            "linear_system": bundle.linear_system((fermat, product)),
            "fermat_section": fermat,
            "product_section": product,
            "basepoint": plane.point_morphism((base.one(), -base.one(), base.zero())),
        },
    )
    pencil.validate_basepoint(check=check)
    return pencil


__all__ = ["HesseBertiniFamily"]
