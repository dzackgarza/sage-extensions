r"""Weil divisor class groups."""

from sage.rings.integer_ring import ZZ as SageZZ

from sage_extensions.categories.divisors.divisor_groups import (
    _affine_line_over_rationals,
    _cokernel_in_category,
    _free_presentation,
    _integers,
)
from sage_extensions.categories.modules.pure.modules import (
    Modules,
)
from sage_extensions.categories.rings.ring_foundation import (
    OwnedFields,
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.owned_category_bases import Category


class ClassGroups(Category):
    r"""The abelian groups isomorphic to the Weil divisor class group \(\operatorname{Cl}(X)\) of some scheme \(X\).

    This is the full subcategory of ``Modules(ZZ)`` cut out by that condition
    on objects; its morphisms are all group homomorphisms.  Every abelian group
    satisfies the condition: every abelian group is the ideal class group of a
    Dedekind domain \(A\) (Claborn, "Every abelian group is a class group",
    Pacific J. Math. 18 (1966), no. 2, 219--222), and the prime divisors of
    \(\operatorname{Spec} A\) are its nonzero primes, so
    \(\operatorname{Cl}(\operatorname{Spec} A)\) is the ideal class group of \(A\).

    The value \(\operatorname{Cl}(X)\) is constructed with its scheme \(X\),
    which this level stores and ``class_group_scheme()`` returns: as
    \(\operatorname{coker}(\rho)\) of a principal-divisor morphism
    \(\rho\colon P \to \operatorname{Div}(X)\), as the biproduct
    \(\operatorname{Cl}(S) \oplus \mathbb{Z}[H]\) of the projective bundle
    formula, or, over a field, as the free module on the hyperplane class
    \(\{H\}\) of \(\mathbb{P}^n_k\).  A group placed here by the condition alone
    has no chosen scheme.
    """

    def an_object(self):
        r"""The zero class group of \(\mathbb{A}^1_{\mathbb{Q}}\)."""
        return self.trivial(_affine_line_over_rationals())

    @classmethod
    def _repr_object_names(cls):
        return "class groups"

    def super_categories(self):
        return [Modules(_owned_integers())]

    def _call_(self, group):
        r"""The abelian group ``group``, placed in ``ClassGroups()`` by Claborn's theorem."""
        from sage_extensions.refine import refine

        abelian_groups = Modules(_owned_integers())
        assert group in abelian_groups, (
            f"{group} is not a class group: an object of {self} is an abelian group, "
            f"and {group} is not an object of {abelian_groups}"
        )
        return refine(group, self)

    def cokernel_of_principal_divisors(self, scheme, principal_divisors):
        r"""\(\operatorname{Cl}(X) = \operatorname{Div}(X)/\operatorname{im}(\rho)\) for the principal-divisor morphism ``principal_divisors`` \(\rho\colon P \to \operatorname{Div}(X)\).

        The result is the cokernel, with ``scheme`` as its scheme and \(\rho\)
        as its retained principal-divisor morphism.
        """
        return _cokernel_in_category(
            principal_divisors,
            self,
            class_group_scheme=scheme,
            principal_to_weil=principal_divisors,
        )

    def free(self, scheme, generators):
        r"""The free abelian group on the set ``generators`` of divisor classes of ``scheme``, presented by \(0 \to \mathbb{Z}^{(S)}\).

        This is an explicit construction for a scheme whose class group is
        already known to be free on these classes; it does not assert or
        decide that theorem.
        """
        return _cokernel_in_category(
            _free_presentation(generators),
            self,
            class_group_scheme=scheme,
            principal_to_weil=None,
        )

    def trivial(self, scheme):
        r"""The zero class group of ``scheme``, the free group on no classes."""
        return self.free(scheme, finite_ordered_set(()))

    def projective_space_over_field(self, projective_space):
        r"""\(\operatorname{Cl}(\mathbb{P}^n_k) = \mathbb{Z}[H]\) for a field \(k\), free on the hyperplane class.

        A divisor of degree \(d\) is linearly equivalent to \(dH\), and degree
        is an isomorphism \(\operatorname{Cl}(\mathbb{P}^n_k) \to \mathbb{Z}\)
        (Hartshorne, II.6.4).  The result is the free module on \(\{H\}\),
        placed here with ``projective_space`` as its scheme.
        """
        base = projective_space.scheme_base_ring()
        assert base in OwnedFields(), (
            f"cannot apply Cl(P^n_k) = Z[H] to {projective_space}: the base ring {base} is not a field, "
            "so Cl(P^n_S) = Cl(S) + Z[H] needs the class group of the base, through projective_bundle"
        )
        return _integers()._fresh_free_module_on(
            finite_ordered_set(("H",)),
            _extra_categories=(self,),
            _extra_construction_data={
                "class_group_scheme": projective_space,
                "principal_to_weil": None,
            },
        )

    def projective_bundle(self, projective_space, base_class_group):
        r"""\(\operatorname{Cl}(\mathbb{P}^n_S) = \operatorname{Cl}(S) \oplus \mathbb{Z}[H]\).

        The base class group is required input, so a nontrivial base
        contribution is never replaced by zero.  The result is the biproduct
        itself, placed here with ``projective_space`` as its scheme; its
        injections are the pullback of base classes and the hyperplane class.
        """
        assert base_class_group in self, (
            f"cannot apply Cl(P^n_S) = Cl(S) + Z[H] to {base_class_group}: the second "
            f"argument must be the class group Cl(S) of the base, but it is not a class group"
        )
        assert base_class_group.class_group_scheme() is projective_space.base_scheme(), (
            f"cannot apply Cl(P^n_S) = Cl(S) + Z[H] to {projective_space}: the given class "
            f"group is Cl({base_class_group.class_group_scheme()}), not the class group of "
            f"the base {projective_space.base_scheme()}"
        )
        integers = _integers()
        hyperplane = integers.free_module(finite_ordered_set(("H",)))
        return Modules(integers).biproduct(
            (base_class_group, hyperplane),
            extra_categories=(self,),
            extra_construction_data={
                "class_group_scheme": projective_space,
                "principal_to_weil": None,
            },
        )

    class ParentMethods:
        # The value Cl(X) is constructed with X; a group placed by the
        # defining condition alone has neither X nor a principal-divisor map.
        _class_group_scheme = None
        _principal_to_weil = None

        def __init__(self, class_group_scheme, principal_to_weil=None, **rest) -> None:
            self._class_group_scheme = class_group_scheme
            self._principal_to_weil = principal_to_weil
            super().__init__(**rest)

        def class_group_scheme(self):
            r"""The scheme whose divisor classes this group presents."""
            assert self._class_group_scheme is not None, (
                f"class_group_scheme on class groups: {self} was placed by Claborn's theorem, and the "
                "construction of a Dedekind domain A with Cl(A) isomorphic to it is not implemented"
            )
            return self._class_group_scheme

        def principal_to_weil_morphism(self):
            r"""The principal-divisor morphism \(\rho_W\colon P \to \operatorname{Div}\) with \(\operatorname{Cl}(X) = \operatorname{coker}\rho_W\).

            This is the defining morphism the presented-module level retains
            for this cokernel; a class group built by the projective bundle
            formula is a biproduct and has none.
            """
            if self._principal_to_weil is None:
                raise ValueError(
                    f"{self} has no selected principal-divisor morphism: this class group was constructed "
                    "from a known abstract presentation rather than as the cokernel of P -> Div(X)"
                )
            return self._principal_to_weil


__all__ = ["ClassGroups"]
