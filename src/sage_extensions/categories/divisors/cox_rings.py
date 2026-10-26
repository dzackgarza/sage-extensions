r"""Cox rings of represented toric schemes, with their divisor-class grading."""

from sage_extensions.categories.abstract_categories.objects import (
    OwnedParameterizedCategory,
)
from sage_extensions.categories.algebras.graded_algebras import GradedAlgebras
from sage_extensions.categories.rings.ring_foundation import _engine_element
from sage_extensions.categories.schemes.toric.toric_schemes import (
    ToricSchemes,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
)


class CoxRings(OwnedParameterizedCategory):
    r"""Cox rings graded by the represented divisor class group of one toric scheme.

    An object is \(k[x_\rho \mid \rho \in \Sigma(1)]\) graded by
    \(\deg x_\rho = [D_\rho] \in \operatorname{Cl}(X)\).  The polynomial algebra
    level consumes the presentation; this level adds the toric scheme \(X\).
    """

    @staticmethod
    def __classcall__(cls, scheme):
        return OwnedParameterizedCategory.__classcall__(cls, scheme)

    def __init__(self, scheme) -> None:
        OwnedParameterizedCategory.__init__(self, scheme)

    def parameter_category(self):
        r"""The toric schemes over the parameter's own base."""
        return ToricSchemes(self.parameter().scheme_base_ring())

    def scheme(self):
        return self.base()

    def grading_group(self):
        from sage_extensions.categories.schemes.schemes import Schemes

        scheme = self.scheme()
        base = scheme.scheme_base_ring()
        assert scheme in Schemes(base).LocallyNoetherian().Integral(), (
            f"cannot grade the Cox ring of {scheme} by Cl({scheme}): the scheme-level divisor class group "
            "is owned by locally Noetherian integral schemes"
        )
        return scheme.class_group()

    def an_object(self):
        r"""The Cox ring of the parameter toric scheme."""
        return self.scheme().cox_ring()

    def super_categories(self):
        return [
            GradedAlgebras(
                self.scheme().scheme_base_ring(),
                self.grading_group(),
            )
        ]

    def _repr_object_names(self):
        return f"Cox rings of {self.scheme()}"

    class ParentMethods:
        def __init__(self, cox_scheme, **rest) -> None:
            self._cox_scheme = cox_scheme
            super().__init__(**rest)

        def cox_scheme(self):
            r"""The toric scheme whose Cox ring this is."""
            return self._cox_scheme

        def cox_rays(self):
            rays = self.cox_scheme().fan().cones(1)
            labels = self.algebra_generating_set()
            return finite_indexed_family(
                labels,
                lambda label: rays[int(labels.ranking_map()(label))],
                name="Cox generator rays",
            )

        def generator_degree(self, label):
            labels = self.algebra_generating_set()
            label = labels(label)
            ray = self.cox_rays()[label]
            return self.cox_scheme().divisor_class(
                self.cox_scheme().torus_invariant_prime_divisor(ray)
            )

        def homogeneous_degree(self, element):
            r"""Return the class-group degree of a nonzero homogeneous Cox polynomial."""
            element = self(element)
            assert element != self.zero(), (
                f"the zero element of {self} has no degree in the class group: every "
                f"homogeneous component contains 0, so its degree is not defined"
            )
            backend = _engine_element(self, element)
            degrees = []
            labels = tuple(self.algebra_generating_set())
            grading = self.grading_monoid()
            for exponents, coefficient in backend.dict().items():
                if not coefficient:
                    continue
                degree = grading.zero()
                for position, exponent in enumerate(exponents):
                    if exponent:
                        generator_degree = self.generator_degree(labels[position])
                        degree = degree + grading.scalar_multiple(
                            grading.base_ring()(int(exponent)),
                            generator_degree,
                        )
                degrees.append(degree)
            selected = degrees[0]
            assert all(degree == selected for degree in degrees[1:]), (
                f"{element} in {self} has no class-group degree: it is not homogeneous, since "
                f"its monomials have the different degrees {degrees}"
            )
            return selected


def _cox_ring(scheme):
    r"""Return ``k[x_rho | rho in Sigma(1)]`` with ``deg(x_rho)=[D_rho]``."""
    rays = scheme.fan().cones(1)
    names = tuple(f"x{position}" for position in range(int(rays.cardinality())))
    presentation = scheme.scheme_base_ring().polynomial_ring(names)
    return presentation.quotient_by_relations(
        (),
        _extra_categories=(CoxRings(scheme),),
        _extra_construction_data=(("cox_scheme", scheme),),
    )


__all__ = ["CoxRings"]
