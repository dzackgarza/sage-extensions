r"""The category ``PicardGroups()`` and the Picard functor ``Pic : C^op -> PicardGroups()``.

For a scheme ``X`` the Picard group ``Pic(X)`` is the abelian group of
isomorphism classes of invertible ``O_X``-modules under tensor product, and a
morphism ``f: X -> Y`` induces the pullback ``f^* : Pic(Y) -> Pic(X)``,
``[L] |-> [f^* L]`` (Hartshorne, *Algebraic Geometry*, II.6).  An abelian group
is a ``ZZ``-module, and the abelian groups isomorphic to some ``Pic(X)`` form
the full subcategory ``PicardGroups()`` of ``Modules(ZZ)``, in which ``Pic``
takes its values.  The value at one scheme is that scheme's ``picard_group()``.
"""

from sage.categories.map import Map
from sage.misc.cachefunc import cached_function, cached_method
from sage.structure.element import parent as element_parent
from sage.structure.parent import Parent
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.divisors.divisor_groups import (
    _affine_line_over_rationals,
    _cokernel_in_category,
    _integers,
)
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.modules.pure.modules import BiproductModules, Modules
from sage_extensions.categories.rings.ring_foundation import OwnedFields, _owned_integers
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.lexicon.category_theory import ObjectOfCategory
from sage_extensions.logic import AtomicProposition, negation
from sage_extensions.owned_category import _object_of, owned_category_join
from sage_extensions.owned_category_bases import Category


class PicardGroups(Category):
    r"""The abelian groups isomorphic to ``Pic(X)`` for some scheme ``X``.

    This is the full subcategory of ``Modules(ZZ)`` cut out by that condition
    on objects; its morphisms are all group homomorphisms.  Every abelian group
    satisfies the condition: every abelian group ``G`` is the ideal class group
    of a Dedekind domain ``A`` (Claborn, "Every abelian group is a class group",
    Pacific J. Math. 18 (1966), no. 2, 219--222), and ``Pic(Spec A) = Cl(A)``
    because ``Spec A`` is Noetherian, integral, separated and regular, hence
    locally factorial (Hartshorne, *Algebraic Geometry*, II.6.16).

    The value ``Pic(X)`` of the Picard functor is constructed with its scheme
    ``X``, which this level stores and ``picard_scheme()`` returns.  A group
    placed here by the condition alone has no chosen scheme.
    """

    def an_object(self):
        r"""``Pic(A^1_QQ) = 0``."""
        return self.trivial(_affine_line_over_rationals())

    @classmethod
    def _repr_object_names(cls):
        return "Picard groups"

    def super_categories(self):
        return [Modules(_owned_integers())]

    def _call_(self, group):
        r"""The abelian group ``group``, placed in ``PicardGroups()`` by Claborn's theorem."""
        from sage_extensions.refine import refine

        abelian_groups = Modules(_owned_integers())
        assert group in abelian_groups, (
            f"{group} is not a Picard group: an object of {self} is an abelian group, "
            f"and {group} is not an object of {abelian_groups}"
        )
        return refine(group, self)

    def cokernel_of_principal_divisors(self, scheme, principal_divisors):
        r"""``Pic(X) = CDiv(X)/im(rho)`` for the principal Cartier divisor morphism ``rho: P -> CDiv(X)``.

        For an integral scheme ``X`` the Cartier divisor class group is
        isomorphic to ``Pic(X)`` (Hartshorne, II.6.15).  The result is the
        cokernel, with ``scheme`` as its Picard scheme.
        """
        return _cokernel_in_category(principal_divisors, self, picard_scheme=scheme)

    def trivial(self, scheme):
        r"""``Pic(X) = 0`` for a scheme ``X`` whose invertible sheaves are all trivial.

        The free ``ZZ``-module on no classes, with ``scheme`` as its Picard
        scheme.  Examples: ``Spec A`` for a unique factorization domain ``A``
        (Hartshorne, II.6.2 and II.6.16), so ``Spec k``, ``A^n_k`` and
        ``Spec ZZ``.
        """
        return _integers()._fresh_free_module_on(
            finite_ordered_set(()),
            _extra_categories=(self,),
            _extra_construction_data={"picard_scheme": scheme},
        )

    def projective_space_over_field(self, projective_space):
        r"""``Pic(P^n_k) = ZZ[O(1)]`` for a field ``k``, free on the class of ``O(1)``.

        Hartshorne, II.6.4 and II.6.17.  The result has ``projective_space``
        as its Picard scheme.
        """
        base = projective_space.scheme_base_ring()
        assert base in OwnedFields(), (
            f"cannot apply Pic(P^n_k) = ZZ[O(1)] to {projective_space}: the base ring {base} is not a field, "
            "so Pic(P^n_S) = Pic(S) + ZZ[O(1)] needs the Picard group of the base, through projective_bundle"
        )
        return _integers()._fresh_free_module_on(
            finite_ordered_set(("O(1)",)),
            _extra_categories=(self,),
            _extra_construction_data={"picard_scheme": projective_space},
        )

    def projective_bundle(self, projective_space, base_picard_group):
        r"""``Pic(P^n_S) = Pic(S) + ZZ[O(1)]``, the biproduct of the base Picard group and the hyperplane summand.

        Hartshorne, II.6.17 and II, Exercise 6.1.  The first injection is the
        pullback ``pi^* : Pic(S) -> Pic(P^n_S)`` along the structure morphism
        ``pi: P^n_S -> S``; the second sends ``O(1)`` to the hyperplane class.
        The base Picard group is required input, so a nontrivial base
        contribution is never replaced by zero.
        """
        assert base_picard_group in self, (
            f"cannot apply Pic(P^n_S) = Pic(S) + ZZ[O(1)] to {base_picard_group}: the second argument "
            f"must be the Picard group Pic(S) of the base, but it is not an object of {self}"
        )
        assert base_picard_group.picard_scheme() is projective_space.base_scheme(), (
            f"cannot apply Pic(P^n_S) = Pic(S) + ZZ[O(1)] to {projective_space}: the given group is "
            f"Pic({base_picard_group.picard_scheme()}), not the Picard group of the base "
            f"{projective_space.base_scheme()}"
        )
        integers = _integers()
        hyperplane = integers.free_module(finite_ordered_set(("O(1)",)))
        return Modules(integers).biproduct(
            (base_picard_group, hyperplane),
            extra_categories=(self,),
            extra_construction_data={"picard_scheme": projective_space},
        )

    class ParentMethods:
        # The value Pic(X) of the Picard functor is constructed with X; a
        # group placed by the defining condition alone has none.
        _picard_scheme = None

        def __init__(self, picard_scheme, **rest) -> None:
            self._picard_scheme = picard_scheme
            super().__init__(**rest)

        def picard_scheme(self):
            r"""The scheme ``X`` of which this group is the value ``Pic(X)``."""
            assert self._picard_scheme is not None, (
                f"picard_scheme on Picard groups: {self} was placed by Claborn's theorem, and the "
                "construction of a Dedekind domain A with Cl(A) isomorphic to it is not implemented"
            )
            return self._picard_scheme

        def _assert_projective_bundle_decomposition(self):
            r"""Assert that this is ``Pic(P^n_S)`` constructed as the biproduct ``Pic(S) + ZZ[O(1)]``."""
            from sage_extensions.categories.schemes.schemes import ProjectiveSpaces

            scheme = self.picard_scheme()
            base = scheme.scheme_base_ring()
            assert scheme in ProjectiveSpaces(base), (
                f"{self} has no projective-bundle decomposition: it is Pic({scheme}), and {scheme} "
                f"is not a projective space over {base}"
            )
            assert self in BiproductModules(_integers()), (
                f"{self} has no chosen decomposition Pic(S) + ZZ[O(1)]: it was not constructed as that "
                "biproduct by PicardGroups().projective_bundle"
            )

        def projective_base_picard_group(self):
            r"""The summand ``Pic(S)`` of ``Pic(P^n_S) = Pic(S) + ZZ[O(1)]``."""
            self._assert_projective_bundle_decomposition()
            return self.biproduct_factor(0)

        def projective_hyperplane_factor(self):
            r"""The summand ``ZZ[O(1)]`` of ``Pic(P^n_S) = Pic(S) + ZZ[O(1)]``."""
            self._assert_projective_bundle_decomposition()
            return self.biproduct_factor(1)

        def base_picard_inclusion(self):
            r"""The pullback ``pi^* : Pic(S) -> Pic(P^n_S)``, the injection of the base summand."""
            self._assert_projective_bundle_decomposition()
            return self.injection(0)

        def hyperplane_class(self):
            r"""The class ``[O(1)]`` in ``Pic(P^n_S)``.

            In ``Pic(S) + ZZ[O(1)]`` it is the image of the hyperplane
            summand's module generator; in ``Pic(P^n_k) = ZZ[O(1)]`` over a
            field ``k`` it is the module generator itself (Hartshorne, II.6.4
            and II.6.17).
            """
            from sage_extensions.categories.schemes.schemes import ProjectiveSpaces

            scheme = self.picard_scheme()
            base = scheme.scheme_base_ring()
            assert scheme in ProjectiveSpaces(base), (
                f"{self} has no hyperplane class: it is Pic({scheme}), and {scheme} is not a projective "
                f"space over {base}"
            )
            match self:
                case _ if self in BiproductModules(_integers()):
                    factor = self.projective_hyperplane_factor()
                    return self.injection(1)(factor.module_generator("O(1)"))
                case _:
                    assert base in OwnedFields(), (
                        f"{self} has no hyperplane class: Pic({scheme}) over the base ring {base}, which is "
                        "not a field, is constructed as Pic(S) + ZZ[O(1)] by PicardGroups().projective_bundle"
                    )
                    return self.module_generator("O(1)")


class _PicardFunctor(Functor):
    r"""``Pic : C^op -> PicardGroups()`` on a category ``C`` of schemes over a base ring.

    ``op(X) |-> Pic(X)``, the group of isomorphism classes of invertible
    ``O_X``-modules under tensor product, and ``op(f) |-> f^*`` for
    ``f: X -> Y`` (Hartshorne, *Algebraic Geometry*, II.6).  Pullback
    preserves tensor products, so ``f^*`` is a group homomorphism, and
    ``(g f)^* = f^* g^*``, so ``Pic`` is contravariant.  ``PicardGroups()``
    is a full subcategory of ``Modules(ZZ)``, so ``f^*`` is a morphism of
    abelian groups between two of its objects.
    """

    def __init__(self, scheme_category: Category) -> None:
        self._scheme_category = scheme_category
        super().__init__(scheme_category.opposite(), PicardGroups())

    def _apply_object(self, opposite_scheme: ObjectOfCategory) -> Parent:
        r"""``Pic(X)`` for the object ``op(X)`` of ``C^op``."""
        return opposite_scheme.underlying_object().picard_group()

    def _apply_morphism(self, morphism: Map) -> Map:
        r"""``f^* : Pic(Y) -> Pic(X)``, ``[L] |-> [f^* L]``, for the arrow ``op(f): op(Y) -> op(X)`` of ``f: X -> Y``.

        ``f^*`` is a group homomorphism, so it is fixed by the images of
        module generators of ``Pic(Y)``.  For ``Y = P^n_k`` over a field,
        ``Pic(Y) = ZZ[O(1)]`` (Hartshorne, II.6.4 and II.6.17), and its one
        module generator ``[O(1)]`` goes to ``[f^* O(1)]``.
        """
        from sage_extensions.categories.schemes.schemes import ProjectiveSpaces

        arrow = morphism.underlying_arrow()
        target_scheme = arrow.codomain()
        source = self(morphism.domain())
        target = self(morphism.codomain())
        base = target_scheme.scheme_base_ring()
        assert target_scheme in ProjectiveSpaces(base), (
            f"cannot pull back Pic({target_scheme}) along {arrow}: f^* is computed on the module generators "
            f"of Pic(P^n_k), and {target_scheme} is not a projective space over {base}"
        )
        pulled_hyperplane = target(target.underlying_set()(arrow.module_pullback(target_scheme.O(1))))
        return source.module_category().Mor(source, target)(
            {label: pulled_hyperplane for label in source.module_generating_set()}
        )

    @cached_method
    def category_of_elements(self):
        r"""``int Pic`` over ``C``: the pairs ``(X, L)`` with ``L`` in ``Pic(X)``.

        ``Pic`` is a presheaf on ``C``, so a morphism ``(X, L) -> (Y, M)`` is
        ``f: X -> Y`` with ``f^* M = L``.
        """
        from sage_extensions.categories.schemes.polarized_varieties import (
            _PicardCategoryOfElements,
        )

        return _PicardCategoryOfElements(self, self._scheme_category)

    def _repr_(self) -> str:
        return "Pic"


class _InvertibleSheafClass:
    r"""The isomorphism class ``[L]`` of one invertible ``O_X``-module ``L``."""

    def __init__(self, parent, representative) -> None:
        self._representative = representative
        super().__init__(parent)

    def representative(self):
        r"""The invertible sheaf ``L`` that represents this class."""
        return self._representative

    def _richcmp_(self, other, op):
        match op in (op_EQ, op_NE):
            case False:
                return NotImplemented
            case True:
                pass
        match element_parent(other) is self.parent():
            case False:
                return op == op_NE
            case True:
                pass
        decision = self.parent().equal(self, other)
        return decision if op == op_EQ else negation(decision)

    __hash__ = None

    def _repr_(self):
        return f"[{self.representative()}]"


class _InvertibleSheafClasses:
    r"""The set of isomorphism classes of invertible ``O_X``-modules.

    The group law is the tensor product, ``[L] + [M] = [L tensor M]``; the
    inverse is the dual sheaf, ``-[L] = [L^vee]``, because
    ``L tensor L^vee = O_X`` for ``L`` invertible; and the unit is ``[O_X]``
    (Hartshorne, *Algebraic Geometry*, II.6.12).  Two represented sheaves
    that are the same object give the same class; any other identification
    is the proposition ``isomorphic(L, M)``.
    """

    def __init__(self, scheme, unit_sheaf, **rest) -> None:
        self._scheme = scheme
        self._unit_sheaf = unit_sheaf
        super().__init__(**rest)

    def scheme(self):
        return self._scheme

    def __contains__(self, value):
        return element_parent(value) is self

    def __call__(self, value):
        r"""The class of ``value``: an element of this set, or an invertible sheaf on ``X``."""
        from sage_extensions.categories.schemes.ringed_spaces import QuasiCoherentSheaves

        match element_parent(value) is self:
            case True:
                return value
            case False:
                invertible = QuasiCoherentSheaves(self.scheme()).Invertible()
                assert value in invertible, (
                    f"{value} has no class in Pic({self.scheme()}): it is not an object of {invertible}"
                )
                return self.element_class(self, value)

    @cached_method
    def zero(self):
        r"""``[O_X]``, the class of the structure sheaf."""
        return self.element_class(self, self._unit_sheaf)

    def add(self, left, right):
        left = self(left)
        right = self(right)
        match (left.representative() is self._unit_sheaf, right.representative() is self._unit_sheaf):
            case (True, _):
                return right
            case (_, True):
                return left
            case _:
                return self(left.representative().tensor_product(right.representative()))

    def negate(self, value):
        value = self(value)
        match value.representative() is self._unit_sheaf:
            case True:
                return value
            case False:
                return self(value.representative().dual_sheaf())

    def scale(self, scalar, value):
        exponent = _integers()(scalar)
        value = self(value)
        match exponent == 0:
            case True:
                return self.zero()
            case False:
                return self(value.representative().tensor_power(exponent))

    def equal(self, left, right):
        r"""Decide ``[L] = [M]`` when ``L`` and ``M`` are one sheaf, else return ``isomorphic(L, M)``."""
        left = self(left)
        right = self(right)
        match left.representative() is right.representative():
            case True:
                return True
            case False:
                return AtomicProposition("isomorphic", left.representative(), right.representative())

    def _repr_(self):
        return f"Isomorphism classes of invertible sheaves on {self.scheme()}"


class _PicardGroupEngine:
    r"""``Pic(X)`` as a ``ZZ``-module on the isomorphism classes of invertible sheaves."""

    def _repr_(self):
        return f"Pic({self.picard_scheme()})"


@cached_function(key=lambda scheme, unit_sheaf: id(scheme))
def _invertible_sheaf_class_group(scheme, unit_sheaf):
    r"""``Pic(X)``, the isomorphism classes of invertible ``O_X``-modules under tensor product.

    ``unit_sheaf`` is the represented invertible sheaf ``O_X``, the unit of
    the tensor product.  An abelian group is a ``ZZ``-module, with ``n [L]``
    the class of ``L^{tensor n}``.
    """
    from sage_extensions.categories.modules.general_modules import GeneralModules
    from sage_extensions.categories.sets.set_categories import Sets

    classes = _object_of(
        Sets(),
        _engine=(Sets(), _InvertibleSheafClasses, _InvertibleSheafClass),
        scheme=scheme,
        unit_sheaf=unit_sheaf,
    )
    integers = _integers()
    return _object_of(
        owned_category_join((GeneralModules(integers), PicardGroups())),
        _engine=(GeneralModules(integers), _PicardGroupEngine, None),
        picard_scheme=scheme,
        base_ring=integers,
        underlying_set=classes,
        addition=classes.add,
        zero=classes.zero(),
        negation=classes.negate,
        scalar_action=classes.scale,
    )


__all__ = ["PicardGroups"]
