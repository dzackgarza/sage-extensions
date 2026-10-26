r"""Orbifolds: spaces locally modelled on quotients of ``R^n`` by finite groups.

An ``n``-dimensional (smooth) orbifold is a paracompact Hausdorff space
``X`` with an orbifold atlas: an open cover by charts ``(U~, G, phi)``,
where ``U~`` is a connected open subset of ``R^n``, ``G`` a finite group of
diffeomorphisms of ``U~``, and ``phi: U~ -> X`` a ``G``-invariant map
inducing a homeomorphism of ``G\U~`` onto an open subset of ``X``, with
smooth embeddings of charts over inclusions of their images (Satake, "On a
generalization of the notion of manifold", 1956; Thurston, *The Geometry
and Topology of Three-Manifolds*, Ch. 13; Adem--Leida--Ruan, *Orbifolds and
Stringy Topology*, Ch. 1).  A smooth manifold is an orbifold whose charts
all have trivial group.  For a discrete group ``Gamma`` acting properly
discontinuously on a manifold ``M``, the orbit space ``Gamma\M`` is an
orbifold (Thurston, Ch. 13).
"""

from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.complex_analytic_spaces import ComplexAnalyticSpaces
from sage_extensions.categories.topological_spaces import TopologicalSpaces


class Orbifolds(OwnedCategory):
    r"""Smooth orbifolds (Satake 1956; Thurston, Ch. 13).

    The orbifold atlas is structure on the underlying paracompact Hausdorff
    space, and forgetting it is the functor to ``TopologicalSpaces()``.  A
    smooth manifold is the orbifold whose charts have trivial group, so
    ``SmoothManifolds()`` declares this category.
    """

    def super_categories(self):
        return [TopologicalSpaces()]

    @classmethod
    def _repr_object_names(cls):
        return "orbifolds"

    class ParentMethods:
        def orbifold_atlas(self):
            r"""The orbifold atlas: charts ``(U~, G, phi)`` with ``G\U~`` homeomorphic to an open of ``X``.

            For an orbit space ``Gamma\M`` the chart at the orbit of ``p`` is
            a ``Gamma_p``-invariant neighbourhood ``U~`` of ``p``, with the
            finite stabilizer ``Gamma_p`` and the restriction of the
            projection ``q``.
            """
            pass


class RiemannianOrbifolds(OwnedCategory):
    r"""Orbifolds with a Riemannian metric, invariant under every chart group.

    The metric is a ``G``-invariant Riemannian metric on each chart ``U~``,
    and the chart embeddings are isometries.  The metric is chosen data, so
    this is a data subcategory of ``Orbifolds()``.  A Riemannian manifold is
    a Riemannian orbifold whose charts have trivial group.  The orbit space
    ``Gamma\M`` of a Riemannian manifold ``M`` by a discrete group of
    isometries acting properly discontinuously is a Riemannian orbifold:
    the metric of ``M`` is ``Gamma``-invariant, so it is invariant under each
    stabilizer ``Gamma_p`` (Thurston, Ch. 13).
    """

    def super_categories(self):
        return [Orbifolds()]

    @classmethod
    def _repr_object_names(cls):
        return "Riemannian orbifolds"

    class ParentMethods:
        def riemannian_metric(self):
            r"""The chart-invariant metric: on ``Gamma\M``, the metric of ``M`` on each chart ``U~``."""
            pass


class ComplexOrbifolds(OwnedCategory):
    r"""Complex orbifolds: charts ``U~`` open in ``C^n``, finite groups of biholomorphisms.

    A holomorphic chart is a smooth chart, so a complex orbifold is an
    orbifold.  Its underlying space with the sheaf of ``G``-invariant
    holomorphic functions on the charts is a normal complex analytic space
    (H. Cartan, "Quotient d'un espace analytique par un groupe
    d'automorphismes", 1957).  Both forgetful functors send a complex
    orbifold to the same underlying topological space.  A complex manifold
    is a complex orbifold whose charts have trivial group.
    """

    def super_categories(self):
        return [Orbifolds(), ComplexAnalyticSpaces().Normal()]

    @classmethod
    def _repr_object_names(cls):
        return "complex orbifolds"

    class ParentMethods:
        def structure_sheaf(self):
            r"""``O_X``: the ``G``-invariant holomorphic functions on each chart ``U~``.

            On the orbit space ``Gamma\M`` it is ``V |-> O_M(q^{-1}V)^Gamma``.
            """
            pass


__all__ = ["ComplexOrbifolds", "Orbifolds", "RiemannianOrbifolds"]
