r"""The category of elements of the Picard functor, polarized varieties, the Lefschetz operator and primitive cohomology."""

from sage.categories.category_with_axiom import all_axioms
from sage.structure.element import Element

from sage_extensions.categories.abstract_categories.categories_of_elements import (
    _CategoryOfElements,
    _object_of_elements,
)
from sage_extensions.lexicon.category_theory import ObjectOfCategory
from sage_extensions.owned_category_bases import CategoryWithAxiom

if "Ample" not in all_axioms:
    all_axioms.add("Ample")


class _PicardCategoryOfElements(_CategoryOfElements):
    r"""``int Pic`` over a category ``C`` of schemes.

    ``Pic : C^op -> Mod_ZZ`` is read through the forgetful functor to
    ``Sets``.  An object is a pair ``(X, L)`` with ``X`` an object of ``C`` and
    ``L`` a class in ``Pic(X)``; a morphism ``(X, L) -> (Y, M)`` is
    ``f: X -> Y`` with ``f^* M = L``.  Whether ``L`` is ample is a property of
    the element, so the pairs with ``L`` ample are the full subcategory
    ``Ample()`` (``CAT-30``).
    """

    class SubcategoryMethods:
        def Ample(self):
            r"""The full subcategory on the pairs ``(X, L)`` with ``L`` ample."""
            return self._with_axiom("Ample")

    class Ample(CategoryWithAxiom):
        r"""The full subcategory of ``int Pic`` on the pairs ``(X, L)`` with ``L`` ample.

        Over a category ``C`` of projective varieties over a field ``k``
        these are the polarized varieties: a projective variety ``X`` with
        the class of an ample line bundle ``L``.  A morphism
        ``(X, L) -> (Y, M)`` is ``f: X -> Y`` with ``f^* M = L``.  A variety
        over ``k`` with an ample line bundle is projective, because a power
        of ``L`` is very ample (Hartshorne, *Algebraic Geometry*, II.7.6).
        """

        def object(self, underlying_object: ObjectOfCategory, element: Element) -> ObjectOfCategory:
            r"""The pair ``(X, L)`` of an object ``X`` of ``C`` and an ample class ``L`` in ``Pic(X)``.

            Ampleness of ``L`` is the caller's datum; construction stores
            the pair and does not decide it.  When ``X`` was constructed as
            an object of ``C.Smooth()``, the pair is constructed in
            ``Smooth()``, the polarized pairs with ``X`` smooth.
            """
            schemes = self.base_category().projection_functor().codomain()
            match underlying_object:
                case _ if underlying_object in schemes.Smooth():
                    return self.Smooth().object(underlying_object, element)
                case _:
                    return _object_of_elements(self, self.base_category(), underlying_object, element)

        __call__ = object

        def an_object(self) -> ObjectOfCategory:
            r"""``(P^1, [O(1)])`` over the base ring of ``C``; ``O(1)`` is very ample on ``P^n`` (Hartshorne, II.7)."""
            from sage_extensions.categories.schemes.schemes import ProjectiveSpaces

            schemes = self.base_category().projection_functor().codomain()
            line = ProjectiveSpaces(schemes.base_ring())(1)
            assert line in schemes, (
                f"the witness (P^1, [O(1)]) of {self} needs P^1 to be an object of {schemes}, but it is not"
            )
            return self(line, line.hyperplane_class())

        class ParentMethods:
            r"""An object ``X`` of ``C`` with its chosen ample class ``L``."""

            def polarization(self) -> Element:
                r"""The ample class ``L`` in ``Pic(X)`` of the pair ``(X, L)``."""
                return self.element()

            def polarization_class(self):
                r"""``h = c_1(L) in H^2(X(CC); ZZ)`` for ``k`` embedded in ``CC``.

                The first Chern class of ``L`` in the integral singular
                cohomology of the analytification ``X(CC)`` (Voisin, *Hodge
                Theory and Complex Algebraic Geometry I*, §7.1).  It is the
                image of the unit ``1 in H^0`` under ``L_h``, since
                ``h cup 1 = h``.
                """
                variety = self.underlying_object()
                unit_degree = variety.integral_singular_cohomology(0)
                unit = next(iter(unit_degree.module_generating_set()))
                return _lefschetz_component(variety, self.polarization(), 0, 1)(
                    unit_degree.module_generator(unit)
                )

        class Smooth(CategoryWithAxiom):
            r"""The polarized pairs ``(X, L)`` with ``X`` smooth."""

            def object(self, underlying_object: ObjectOfCategory, element: Element) -> ObjectOfCategory:
                r"""The pair ``(X, L)`` of a smooth object ``X`` of ``C`` and an ample class ``L`` in ``Pic(X)``."""
                elements = self.base_category().base_category()
                schemes = elements.projection_functor().codomain()
                assert underlying_object in schemes.Smooth(), (
                    f"cannot form the smooth polarized pair ({underlying_object}, {element}): "
                    f"{underlying_object} is not an object of {schemes.Smooth()}"
                )
                return _object_of_elements(self, elements, underlying_object, element)

            __call__ = object

            class ParentMethods:
                r"""A smooth projective variety ``X`` with its chosen ample class ``L``."""

                def lefschetz_operator(self, degree, power=1):
                    r"""``L_h^power = h^power cup (-) : H^degree(X(CC); ZZ) -> H^{degree+2 power}(X(CC); ZZ)``.

                    Cup product with the ``power``-th power of the
                    polarization class ``h = c_1(L)``, the component in
                    degree ``degree`` of the degree-2 endomorphism ``L_h`` of
                    the graded ``ZZ``-module ``H^*(X(CC); ZZ)``.  For ``X``
                    smooth of dimension ``n`` the hard Lefschetz theorem
                    states that ``L_h^{n-k} : H^k -> H^{2n-k}`` becomes an
                    isomorphism after ``QQ tensor_ZZ (-)`` for ``k <= n``
                    (Voisin, op. cit., §6.2).
                    """
                    return _lefschetz_component(
                        self.underlying_object(), self.polarization(), degree, power
                    )

                def primitive_cohomology(self, k):
                    r"""``H^k_prim = ker(L_h^{n-k+1} : H^k -> H^{2n-k+2})`` for ``0 <= k <= n = dim X``.

                    The kernel of ``L_h^{n-k+1}`` on ``H^k(X(CC); ZZ)``, a
                    subobject with its inclusion.  ``QQ`` is flat over
                    ``ZZ``, so ``QQ tensor_ZZ H^k_prim`` is the rational
                    primitive cohomology, and the Lefschetz decomposition is
                    ``H^k(X(CC); QQ) = sum_r L_h^r H^{k-2r}_prim``
                    (Voisin, op. cit., §6.2).
                    """
                    variety = self.underlying_object()
                    dimension = int(variety.dimension())
                    assert 0 <= int(k) <= dimension, (
                        f"primitive cohomology H^{k}_prim of {variety} is defined for 0 <= k <= dim X = "
                        f"{dimension}"
                    )
                    return self.lefschetz_operator(k, dimension - int(k) + 1).kernel()


def _polarization_multiple(variety, polarization):
    r"""The integer ``m`` with ``L = m [O(1)]``, for ``X`` a projective space or a projective complete intersection.

    On ``P^n_k`` over a field, ``Pic(P^n_k) = ZZ [O(1)]`` (Hartshorne,
    *Algebraic Geometry*, II.6.17), and ``m`` is the coordinate of ``L`` on the
    hyperplane summand.  On a complete intersection ``X`` the represented
    class is ``[O_X(m)] = i^* [O_P(m)]``, and ``m`` is the twist of the
    ambient line bundle it is pulled back from.
    """
    from sage_extensions.categories.rings.ring_foundation import OwnedFields
    from sage_extensions.categories.schemes.complete_intersections import (
        ProjectiveCompleteIntersections,
    )
    from sage_extensions.categories.schemes.schemes import ProjectiveSpaces

    base = variety.scheme_base_ring()
    match variety:
        case _ if variety in ProjectiveSpaces(base):
            assert base in OwnedFields(), (
                f"c_1 of a class in Pic({variety}) is read from Pic(P^n_k) = ZZ [O(1)], which needs a "
                f"field base, but the base is {base}"
            )
            return variety.picard_group().dual_basis()["O(1)"](polarization)
        case _ if variety in ProjectiveCompleteIntersections(base):
            return polarization.underlying_element().representative().ambient_line_bundle().degree()
        case _:
            assert False, (
                f"c_1 of a class in Pic({variety}) is computed only for projective spaces and projective "
                f"complete intersections, and {variety} is in {variety.category()}"
            )


def _lefschetz_component(variety, polarization, degree, power):
    r"""``h^power cup (-) : H^degree(X(CC); ZZ) -> H^{degree + 2 power}(X(CC); ZZ)`` for ``h = c_1(L)``.

    ``L = m [O(1)]`` and ``h = m i^* alpha`` for the generator ``alpha`` of
    ``H^2(P^N; ZZ)``.  Every nonzero cohomology group met here is free of
    rank one with its given generator ``g_k``:

    - ``X = P^n``: ``g_{2j} = alpha^j`` and ``alpha^j cup alpha^r =
      alpha^{j+r}`` (Hatcher, *Algebraic Topology*, Thm. 3.19), so ``g_k``
      goes to ``m^power g_{k + 2 power}``.
    - ``X`` a smooth complete intersection of dimension ``n`` and degree
      ``d``: by the Lefschetz hyperplane theorem ``g_k = i^* alpha^{k/2}`` for
      even ``k < n``, and by Poincare duality ``g_k`` for even ``k > n`` is
      dual to the generator of ``H_{2n-k}(X) = H_{2n-k}(P^N)`` (Dimca,
      *Singularities and Topology of Hypersurfaces*, Ch. 5, §3; Lazarsfeld,
      *Positivity I*, 3.1.17).  The projection formula makes cup with
      ``i^* alpha`` the identity on these generators away from the middle
      degree, and ``(i^* alpha)^n = d g_{2n}``.  So ``g_k`` goes to
      ``m^power g_{k + 2 power}`` when ``k`` and ``k + 2 power`` lie on one
      side of ``n``, and to ``d m^power g_{k + 2 power}`` when ``k < n <
      k + 2 power``.

    A group of rank zero at either end gives the zero map.  The middle group
    ``H^n`` of an even-dimensional complete intersection has a basis that no
    represented class identifies with ``i^* alpha^{n/2}``, so a map into or
    out of it is not constructed.
    """
    from sage_extensions.categories.schemes.complete_intersections import (
        ProjectiveCompleteIntersections,
    )
    from sage_extensions.categories.schemes.schemes import ProjectiveSpaces

    degree = int(degree)
    power = int(power)
    assert power >= 0, f"L_h^{power} is defined for a nonnegative power, not {power}"
    target_degree = degree + 2 * power
    source = variety.integral_singular_cohomology(degree)
    target = variety.integral_singular_cohomology(target_degree)
    source_labels = source.module_generating_set()
    target_labels = target.module_generating_set()
    match (int(source.module_rank()), int(target.module_rank())):
        case (0, _) | (_, 0):
            return source.Mor(target)({label: target.zero() for label in source_labels})
        case (1, 1):
            pass
        case ranks:
            assert False, (
                f"h^{power} cup (-) : H^{degree} -> H^{target_degree} of {variety} is constructed between groups "
                f"of rank one, but the ranks are {ranks}: the cup product on the middle cohomology of an "
                "unmarked complete intersection is not constructed"
            )
    base = variety.scheme_base_ring()
    multiple = _polarization_multiple(variety, polarization)
    factor = multiple**power
    match variety:
        case _ if variety in ProjectiveSpaces(base):
            pass
        case _ if variety in ProjectiveCompleteIntersections(base).Smooth():
            dimension = int(variety.dimension())
            assert dimension not in (degree, target_degree), (
                f"h^{power} cup (-) : H^{degree} -> H^{target_degree} of {variety} meets the middle degree "
                f"{dimension}: the cup product on the middle cohomology of an unmarked complete "
                "intersection is not constructed"
            )
            match degree < dimension < target_degree:
                case True:
                    factor = factor * variety.projective_degree()
                case False:
                    pass
        case _:
            assert False, (
                f"h cup (-) on H^*({variety}(CC); ZZ) is computed only for projective spaces and smooth "
                f"projective complete intersections, and {variety} is in {variety.category()}"
            )
    target_generator = target.module_generator(next(iter(target_labels)))
    return source.Mor(target)({label: factor * target_generator for label in source_labels})
