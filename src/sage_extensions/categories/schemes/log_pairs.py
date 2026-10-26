r"""Log pairs \((X,\Delta)\) and the toric log pairs among them.

A log pair is a variety together with a chosen effective boundary divisor.
The pair is the object: neither the variety nor the divisor alone answers the
questions a log pair is asked, and the log canonical class \(K_X+\Delta\) is
the first of them.

For a toric variety the boundary is the sum of the torus-invariant prime
divisors, one for each ray of the fan, and Cox--Little--Schenck,
*Toric Varieties*, Thm. 8.2.3 gives \(K_X=-\sum_{\rho}D_\rho\).  The toric
boundary is therefore anticanonical, and \((X,\Delta_{\mathrm{toric}})\) is
log Calabi--Yau -- a statement this layer computes rather than asserts.
"""

from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
)
from sage_extensions.categories.schemes.schemes import Schemes, _scheme_with_structure
from sage_extensions.refine import RealizationHook


class LogPairs(OwnedCategoryOverBaseRing):
    r"""Pairs ``(X, Delta)`` of a variety and a chosen boundary divisor."""

    def an_object(self):
        r"""The projective line with its toric boundary, the two torus-fixed points: a log Calabi--Yau pair."""
        from sage.rings.integer_ring import ZZ as SageZZ

        from sage_extensions.categories.rings.ring_foundation import (
            _own_ring,
            _owned_integers,
        )
        from sage_extensions.categories.schemes.toric.fans import (
            RationalPolyhedralFans,
        )

        cocharacters = _owned_integers().free_module(1)
        line = RationalPolyhedralFans(cocharacters).projective_space_fan().toric_variety(
            self.base_ring()
        )
        return line.log_pair()

    def _call_(self, log_scheme, boundary_divisor):
        r"""The log pair ``(X, Delta)`` of a scheme over this base and a divisor on it."""
        assert log_scheme.scheme_base_ring() == self.base_ring(), (
            f"{log_scheme} cannot be the scheme of a log pair in {self}: it lies over "
            f"{log_scheme.scheme_base_ring()}, not over {self.base_ring()}"
        )
        return _scheme_with_structure(
            log_scheme,
            self,
            construction_data={
                "log_scheme": log_scheme,
                "boundary_divisor": boundary_divisor,
            },
        )

    def _repr_object_names(self):
        return f"log pairs over {self.base_ring()}"

    def super_categories(self):
        return [Schemes(self.base_ring())]

    class ParentMethods:
        def __init__(self, log_scheme, boundary_divisor, **rest) -> None:
            self._log_scheme = log_scheme
            self._boundary_divisor = boundary_divisor
            super().__init__(**rest)

        def log_scheme(self):
            r"""The variety ``X`` of the pair."""
            return self._log_scheme

        @RealizationHook
        def _affineness_decision(self):
            r"""The chosen boundary does not change affineness of its scheme."""
            return self.log_scheme().is_affine()

        def scheme(self):
            r"""Return the underlying scheme ``X`` of this log pair."""
            return self.log_scheme()

        def boundary_divisor(self):
            r"""The boundary ``Delta``."""
            return self._boundary_divisor

        def boundary_divisor_group(self):
            r"""The divisor group ``Delta`` is an element of."""
            return self.boundary_divisor().parent()

        def canonical_divisor(self):
            r"""The canonical divisor ``K_X``, asked of the variety."""
            return self.log_scheme().canonical_divisor()

        def log_canonical_divisor(self):
            r"""``K_X + Delta``, the class whose vanishing is log Calabi--Yau."""
            return self.canonical_divisor() + self.boundary_divisor()

        def is_log_calabi_yau(self) -> bool:
            r"""Whether ``K_X + Delta`` is the zero divisor."""
            return (
                self.log_canonical_divisor()
                == self.boundary_divisor_group().zero()
            )

        def _repr_(self) -> str:
            return f"Log pair ({self.log_scheme()}, {self.boundary_divisor()})"


class ToricLogPairs(OwnedCategoryOverBaseRing):
    r"""Log pairs whose variety is toric and whose boundary is torus-invariant."""

    def an_object(self):
        r"""The projective line with the sum of its two torus-fixed points."""
        return LogPairs(self.base_ring()).an_object()

    def _call_(
        self,
        toric_variety,
        boundary_divisor,
        *,
        _engine=None,
        construction_data=None,
    ):
        r"""The toric log pair of a toric variety and a torus-invariant boundary."""
        assert toric_variety.scheme_base_ring() == self.base_ring(), (
            f"{toric_variety} cannot be the variety of a toric log pair in {self}: it lies over "
            f"{toric_variety.scheme_base_ring()}, not over {self.base_ring()}"
        )
        assert boundary_divisor.parent() is toric_variety.torus_invariant_divisor_group(), (
            f"the boundary {boundary_divisor} of a toric log pair on {toric_variety} must be a "
            f"torus-invariant divisor on it, but it lies in {boundary_divisor.parent()}"
        )
        data = {
            "log_scheme": toric_variety,
            "boundary_divisor": boundary_divisor,
            **dict(construction_data or {}),
        }
        return _scheme_with_structure(
            toric_variety,
            self,
            _engine=_engine,
            construction_data=data,
        )

    def _repr_object_names(self):
        return f"toric log pairs over {self.base_ring()}"

    def super_categories(self):
        return [LogPairs(self.base_ring())]

    class ParentMethods:
        def fan(self):
            r"""The fan of the variety of the pair."""
            return self.log_scheme().fan()

        def toric_scheme(self):
            r"""Return the underlying toric scheme of this toric log pair."""
            return self.log_scheme()

        def codimension_in_toric_scheme(self):
            r"""Zero: this pair's scheme is its retained toric ambient scheme."""
            from sage.rings.integer_ring import ZZ as SageZZ

            from sage_extensions.categories.rings.ring_foundation import (
                _own_ring,
                _owned_integers,
            )

            return _owned_integers().zero()

        def is_toric_boundary(self) -> bool:
            r"""Whether ``Delta`` is the full toric boundary ``sum_rho D_rho``."""
            return self.boundary_divisor() == self.log_scheme().toric_boundary_divisor()


def _log_pair(log_scheme, boundary_divisor):
    r"""The log pair of a variety and a chosen boundary divisor on it."""
    return LogPairs(log_scheme.scheme_base_ring())(log_scheme, boundary_divisor)


def _toric_log_pair(toric_variety, boundary_divisor):
    r"""The toric log pair of a toric variety and a torus-invariant boundary."""
    return ToricLogPairs(toric_variety.scheme_base_ring())(toric_variety, boundary_divisor)


__all__ = ["LogPairs", "ToricLogPairs"]
