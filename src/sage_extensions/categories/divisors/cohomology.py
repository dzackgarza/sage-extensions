r"""Owned coherent cohomology spaces for represented line bundles."""

from sage_extensions.categories.modules.pure.modules import VectorSpaces
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
)
from sage_extensions.categories.sets.set_categories import finite_ordinal_set


class LineBundleCohomologySpaces(OwnedCategoryOverBaseRing):
    r"""Vector spaces represented as \(H^i(X, \mathcal{O}_X(D))\) for one divisor.

    An object is a finite free module over the base field together with the
    scheme \(X\), the divisor \(D\) and the degree \(i\) it represents.  The
    free-module level consumes the framing; this level adds \(X\), \(D\) and
    \(i\).
    """

    def _repr_object_names(self):
        return f"line-bundle cohomology spaces over {self.base_ring()}"

    def an_object(self):
        r"""A toric H^0(O(1)) witness over the stated base ring."""
        from sage_extensions.categories.schemes.geometric_cohomology import (
            ToricGeometricLineBundleCohomologySpaces,
        )

        return ToricGeometricLineBundleCohomologySpaces(self.base_ring()).an_object()

    def super_categories(self):
        return [VectorSpaces(self.base_ring())]

    def _call_(self, scheme, divisor, degree, dimension):
        r"""The represented \(H^{\mathrm{degree}}(X, \mathcal{O}_X(D))\) of the stated dimension."""
        degree = int(degree)
        dimension = int(dimension)
        assert degree >= 0, (
            f"there is no cohomology group H^{degree}(X, O_X(D)) of {scheme}: the "
            f"cohomological degree must be nonnegative"
        )
        assert dimension >= 0, (
            f"cannot form H^{degree}(X, O_X({divisor})) of dimension {dimension}: a vector "
            f"space dimension must be nonnegative"
        )
        assert scheme.scheme_base_ring() is self.base_ring(), (
            f"cannot form H^{degree}(X, O_X({divisor})) as a {self.base_ring()}-vector space: "
            f"{scheme} is a scheme over {scheme.scheme_base_ring()}, not over {self.base_ring()}"
        )
        return self.base_ring()._fresh_free_module_on(
            finite_ordinal_set(dimension),
            _extra_categories=(self,),
            _extra_construction_data={
                "cohomology_scheme": scheme,
                "cohomology_divisor": divisor,
                "cohomological_degree": degree,
            },
        )

    class ParentMethods:
        def __init__(
            self,
            cohomology_scheme,
            cohomology_divisor,
            cohomological_degree,
            **rest,
        ) -> None:
            self._cohomology_scheme = cohomology_scheme
            self._cohomology_divisor = cohomology_divisor
            self._cohomological_degree = int(cohomological_degree)
            super().__init__(**rest)

        def cohomology_scheme(self):
            r"""The scheme \(X\) of \(H^i(X, \mathcal{O}_X(D))\)."""
            return self._cohomology_scheme

        def cohomology_divisor(self):
            r"""The divisor \(D\) of \(H^i(X, \mathcal{O}_X(D))\)."""
            return self._cohomology_divisor

        def cohomological_degree(self):
            r"""The degree \(i\) of \(H^i(X, \mathcal{O}_X(D))\)."""
            return self._cohomological_degree


__all__ = ["LineBundleCohomologySpaces"]
