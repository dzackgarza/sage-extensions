r"""Topological spaces under a fixed space, and the homotopy groups of pointed spaces."""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.abstract_categories.arrow_categories import CosliceCategory


class TopologicalSpaceCoslices(CosliceCategory):
    r"""``X/Top``: topological spaces ``B`` with a chosen continuous map ``i: X -> B``.

    For ``X`` the one-point space this is the category ``*/Top`` of pointed
    spaces: an object is a space ``B`` with the base point ``b = i(*)``, and a
    morphism is a continuous map preserving base points (Hatcher, *Algebraic
    Topology*, §4.1).  ``CosliceUnder(X)`` on ``TopologicalSpaces()`` selects
    this class through the ``Coslices`` declaration of that category.
    """

    def homotopy_groups_functor(self):
        r"""``pi_* : */Top -> [Disc(ZZ_{>=1}), Groups]``.

        The value at ``(B, b)`` is the family ``n |-> pi_n(B, b) = [(S^n, s), (B, b)]_*``
        of pointed homotopy classes, a functor from the discrete category on
        the positive integers into groups; ``pi_n`` is abelian for ``n >= 2``.
        ``pi_0`` is a pointed set, not a group, so degree 0 is not indexed.
        A pointed map induces the family of homomorphisms ``f_*`` (Hatcher,
        op. cit., §4.1).  The functor is defined on ``*/Top``, so the fixed
        space of this coslice must be the one-point space.
        """
        assert False, "homotopy_groups_functor on TopologicalSpaceCoslices: not implemented"

    class ParentMethods(CosliceCategory.ParentMethods):
        r"""A space ``B`` with its chosen map from the fixed space; for ``*/Top``, a pointed space."""

        def homotopy_groups(self):
            r"""``pi_*(B, b)``: the value of ``homotopy_groups_functor()`` at this pointed space.

            An object of ``[Disc(ZZ_{>=1}), Groups]`` whose degree-``n`` value is
            ``pi_n(B, b)``, with ``pi_1`` at degree 1.  Defined when the fixed
            space of the coslice is the one-point space.
            """
            assert False, "homotopy_groups on TopologicalSpaceCoslices: not implemented"

        def base_point(self):
            r"""``b = i(*)``, the image of the point of the one-point space under the chosen arrow ``i: * -> B``."""
            arrow = self.arrow()
            source = arrow.domain()
            assert source.cardinality() == 1, (
                f"{self} has no base point: its chosen arrow starts at {source}, not at the one-point space"
            )
            return arrow(source.an_element())

        def _repr_(self) -> str:
            arrow = self.arrow()
            if arrow.domain().cardinality() == 1:
                return f"Pointed space ({arrow.codomain()}, {self.base_point()})"
            return f"Space under {arrow.domain()}: ({arrow.domain()} -> {arrow.codomain()})"

        def fundamental_group(self):
            r"""``pi_1(B, b)``, an object of ``Groups``: the degree-0 part of :meth:`homotopy_lie_algebra` as a group."""
            return self.arrow().codomain()._fundamental_group_at(self.base_point())

        @cached_method
        def homotopy_lie_algebra(self):
            r"""``pi_*(B, b)`` under the Whitehead product, an object of ``GradedLieAlgebras(ZZ)``.

            The grading is the shifted one: degree ``n >= 0`` holds
            ``pi_{n+1}(B, b)``, and negative degrees are zero, so the Whitehead
            product ``pi_p x pi_q -> pi_{p+q-1}`` has degree zero (Felix,
            Halperin and Thomas, *Rational Homotopy Theory*, GTM 205, §21).
            The bracket of ``a in pi_p`` and ``b in pi_q`` is
            ``(-1)^p [a, b]_W``.  The Whitehead product is graded symmetric,
            ``[b, a]_W = (-1)^{pq} [a, b]_W`` (Hatcher, *Algebraic Topology*,
            Example 4.52), and the sign ``(-1)^p`` turns this into the Koszul
            rule ``[x, y] = -(-1)^{|x||y|} [y, x]`` for ``|x| = p - 1`` and
            ``|y| = q - 1``.  Degree 0 is ``pi_1(B, b)``, a ``ZZ``-module only
            when it is abelian; as a group it is :meth:`fundamental_group`.
            """
            from sage_extensions.categories.algebras.graded_algebras import (
                _graded_multiplication_from_components,
            )
            from sage_extensions.categories.algebras.graded_lie_algebras import GradedLieAlgebras
            from sage_extensions.categories.modules.graded_modules import GradedModules
            from sage_extensions.categories.rings.ring_foundation import _owned_integers
            from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
            from sage_extensions.categories.sets.indexed_families import indexed_family

            space = self.arrow().codomain()
            point = self.base_point()
            integers = _owned_integers()

            def piece(degree):
                match degree >= 0:
                    case True:
                        return space._homotopy_group_module(point, degree + 1)
                    case False:
                        return integers.free_module(finite_ordered_set(()))

            module = GradedModules(integers)(
                indexed_family(integers, piece, name=f"Homotopy groups pi_(*+1) of {self}")
            )

            def bracket_on_components(s, x, t, y):
                pairing = space._whitehead_pairing(point, s + 1, t + 1)
                return integers(-1) ** (s + 1) * pairing(pairing.domain().pure_tensor(x, y))

            bracket = _graded_multiplication_from_components(module, bracket_on_components)
            algebra = GradedLieAlgebras(integers)(module, bracket)
            # The direct-sum parent class defines ``_repr_`` and precedes its
            # category's ``ParentMethods``; Sage's ``rename`` names it.
            algebra.rename(f"Homotopy Lie algebra pi_*(B, b) of {space} under the Whitehead product")
            return algebra

        def whitehead_product(self, alpha, beta):
            r"""``[alpha, beta]_W in pi_{p+q-1}(B, b)`` for ``alpha in pi_p``, ``beta in pi_q``, ``p, q >= 1``.

            The class of ``S^{p+q-1} -> S^p v S^q -> B``, the attaching map of the
            top cell of ``S^p x S^q`` followed by ``alpha v beta`` (Whitehead,
            Ann. of Math. 42 (1941); Hatcher, op. cit., Example 4.52).  For
            ``p = q = 1`` it is the commutator in ``pi_1``.  ``alpha`` and
            ``beta`` are elements of the homotopy Lie algebra: a class of ``pi_p`` is
            an element of degree ``p - 1`` of :meth:`homotopy_lie_algebra`, and the
            product extends bilinearly.
            """
            algebra = self.homotopy_lie_algebra()
            integers = algebra.base_ring()
            beta = algebra(beta)
            return sum(
                (
                    integers(-1) ** (degree + 1) * (algebra.from_component(degree, component) * beta)
                    for degree, component in algebra(alpha).homogeneous_components().items()
                ),
                algebra.zero(),
            )

        def rational_homotopy_lie_algebra(self):
            r"""``pi_{*+1}(B, b) tensor QQ`` under the Whitehead product, an object of ``GradedLieAlgebras(QQ)``.

            Degree ``n`` holds ``pi_{n+1}(B, b) tensor QQ``; the shift makes the
            Whitehead product a degree-zero graded Lie bracket, isomorphic to
            the Samelson bracket on ``pi_*(Omega B) tensor QQ`` up to sign.
            Hypothesis: ``B`` is simply connected, so every ``pi_{n+1}`` with
            ``n >= 1`` is abelian (Felix, Halperin and Thomas, *Rational
            Homotopy Theory*, GTM 205, §21).
            """
            assert False, "rational_homotopy_lie_algebra on TopologicalSpaceCoslices: not implemented"


__all__ = ["TopologicalSpaceCoslices"]
