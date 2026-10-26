r"""Filtered modules, mixed Hodge structures and pure Hodge structures.

The definitions are Deligne's (*Théorie de Hodge II*, Publ. Math. IHES 40
(1971)).  Let ``R`` be a subring of the real numbers such that ``R tensor QQ``
is a field (``ZZ``, ``QQ`` or ``RR``; Deligne II (2.3.1)).

- A *mixed Hodge structure* over ``R`` is a finitely generated ``R``-module
  ``V``, an increasing filtration ``W`` (the weight filtration) of
  ``V tensor_R QQ`` and a decreasing filtration ``F`` (the Hodge filtration)
  of ``V tensor_R CC``, such that ``F`` induces on each ``Gr^W_n tensor CC``
  a Hodge structure of weight ``n`` (II (2.3.1)).
- A *Hodge structure of weight* ``n`` is a mixed Hodge structure with
  ``Gr^W_m = 0`` for ``m != n``.  Equivalently ``V tensor CC`` is the direct
  sum of ``V^{p,q} = F^p cap conj(F^q)`` over ``p + q = n``, with
  ``conj(V^{p,q}) = V^{q,p}`` (II (2.1.1), (2.1.10)).
- A *polarization* of a Hodge structure of weight ``n`` is an ``R``-bilinear
  ``Q: V tensor V -> R(-n)`` that is ``(-1)^n``-symmetric and satisfies the
  Hodge–Riemann relations (II (2.1.15)).

Morphisms are ``R``-linear maps whose scalar extensions preserve ``W`` and
``F``; such morphisms are strictly compatible with both filtrations
(II (2.3.5)), which makes the categories abelian.
"""

from functools import partial

from sage.categories.category import Category
from sage.categories.category_with_axiom import all_axioms
from sage.misc.cachefunc import cached_method

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    MorCategoryConstruction,
)
from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
    _initialize_module_mor_parent,
    _ModuleMorCommonMethods,
)
from sage_extensions.categories.modules.pure.modules import Modules
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    _owned_integers,
)
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.set_categories import NN
from sage_extensions.logic import AtomicProposition
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.validation import validator

# ``Polarizable`` is the property that a pure Hodge structure admits a
# polarization; the chosen polarization is the data of
# :class:`PolarizedHodgeStructures`.
if "Polarizable" not in all_axioms:
    all_axioms.add("Polarizable")


class FilteredModules(OwnedCategoryOverBaseRing):
    r"""Modules over ``R`` with a finite decreasing filtration by submodules.

    An object is ``(M, F^•)`` with ``F^p M`` a submodule of ``M``,
    ``F^{p+1} M subseteq F^p M``, ``F^p M = M`` for ``p << 0`` and
    ``F^p M = 0`` for ``p >> 0``.  An increasing filtration ``W_•`` is the
    decreasing filtration ``W^{-n} := W_n`` (Deligne II (1.1.2)).  A morphism
    is an ``R``-linear map ``f`` with ``f(F^p M) subseteq F^p N``.
    """

    def _repr_object_names(self) -> str:
        return f"filtered modules over {self.base()}"

    def super_categories(self):
        return [Modules(self.base_ring())]

    class ParentMethods:
        def filtration_stage(self, p):
            r"""The inclusion ``F^p M -> M``, an arrow of ``Modules(R)``."""
            assert False, "filtration_stage on FilteredModules(R): not implemented"

        def graded_piece(self, p):
            r"""``Gr_F^p M = F^p M / F^{p+1} M``, an object of ``Modules(R)``."""
            assert False, "graded_piece on FilteredModules(R): not implemented"


def _hodge_tate_number_table(weights):
    r"""``h^{p,p}`` is the number of basis vectors of weight ``2p``; the other numbers vanish.

    A Hodge–Tate summand of weight ``2p`` is a sum of copies of ``R(-p)``,
    of type ``(p, p)``.
    """
    counts = {}
    for weight in weights:
        assert int(weight) % 2 == 0, (
            f"a Hodge–Tate structure has even weights, but a summand of weight {weight} was given"
        )
        bidegree = (int(weight) // 2, int(weight) // 2)
        counts[bidegree] = counts.get(bidegree, 0) + 1
    return {bidegree: NN(count) for bidegree, count in counts.items()}


def _convolved_hodge_numbers(left, right):
    r"""``h^{p,q}(V tensor V') = sum_{a+a'=p, b+b'=q} h^{a,b}(V) h^{a',b'}(V')``."""
    table = {}
    for (a, b), value in left.items():
        for (other_a, other_b), other_value in right.items():
            bidegree = (a + other_a, b + other_b)
            table[bidegree] = table.get(bidegree, NN(0)) + value * other_value
    return table


def _split_mixed_hodge_structure(
    base_ring,
    weights,
    *,
    hodge_number_table=None,
    polarizable_weights=None,
    name=None,
):
    r"""The mixed Hodge structure on ``R^r`` whose ``i``-th basis vector has weight ``weights[i]``.

    ``W_n`` is the span of the basis vectors of weight at most ``n``, so ``W``
    splits.  With no ``hodge_number_table`` the structure is Hodge–Tate: the
    summand of weight ``2p`` is a sum of copies of ``R(-p)`` and ``F^p`` is the
    span of the basis vectors of weight at least ``2p``.  Otherwise
    ``hodge_number_table`` is a function returning ``dim Gr_F^p Gr^W_{p+q}``
    for the Hodge filtration that the caller's object determines.  A
    Hodge–Tate summand is polarized by a positive definite form, so every
    Hodge–Tate weight is polarizable.  An object with one weight ``n`` is an
    object of ``HodgeStructures(R, n)``.
    """
    from sage_extensions.categories.modules.framed.framed_free_modules import (
        _fresh_free_module_on,
    )

    integers = _owned_integers()
    weights = tuple(integers(weight) for weight in weights)
    if hodge_number_table is None:
        polarizable = frozenset(weights)
        hodge_number_table = partial(_hodge_tate_number_table, weights)
    else:
        polarizable = frozenset() if polarizable_weights is None else frozenset(polarizable_weights)
    support = frozenset(weights)
    match int(len(support)):
        case 1:
            (weight,) = support
            pure = HodgeStructures(base_ring, weight)
            category = pure.Polarizable() if weight in polarizable else pure
        case _:
            category = MixedHodgeStructures(base_ring)
    structure = _fresh_free_module_on(
        base_ring,
        len(weights),
        _extra_categories=(category,),
        _extra_construction_data={
            "hodge_weights": weights,
            "hodge_number_table": hodge_number_table,
            "polarizable_weights": polarizable,
        },
    )
    if name is None:
        listed = ", ".join(str(weight) for weight in sorted(support))
        name = f"Mixed Hodge structure of rank {len(weights)} over {base_ring} with weights {{{listed}}}"
    # The framed free modules precede the Hodge structures in the joined
    # category, so their ``_repr_`` is found first; Sage's ``rename`` names it.
    structure.rename(name)
    return structure


class MixedHodgeStructureMorphismMethods:
    r"""An ``R``-linear map of mixed Hodge structures.

    Its scalar extensions preserve ``W`` and ``F``.  On split ``W`` a basis
    vector of weight ``m`` maps into ``W_m``; on Hodge–Tate endpoints ``F^p``
    is the span of the weights at least ``2p``, so it maps into the weights at
    least ``m`` as well.
    """

    @cached_method
    def filtration_preservation_decision(self):
        r"""Decide on the basis whether ``W`` and ``F`` are preserved, else the proposition."""
        domain, codomain = self.domain(), self.codomain()
        target_labels = tuple(codomain.module_generating_set())
        hodge_tate = domain.is_hodge_tate() and codomain.is_hodge_tate()
        for label in domain.module_generating_set():
            weight = domain.weight_of_module_generator(label)
            image = self(domain.module_generator(label)).to_vector()
            for target in target_labels:
                if not image(target):
                    continue
                target_weight = codomain.weight_of_module_generator(target)
                if target_weight > weight:
                    return False
                if hodge_tate and target_weight < weight:
                    return False
        if hodge_tate:
            return True
        return AtomicProposition("preserves_hodge_filtration", self)

    @validator
    def validate_filtration_preservation(self) -> None:
        r"""Raise ``ValueError`` when this map is decided not to preserve ``W`` or ``F`` (``OWN-22``)."""
        if self.filtration_preservation_decision() is False:
            raise ValueError(
                f"the map {self.domain()} -> {self.codomain()} does not preserve the weight and "
                "Hodge filtrations"
            )


class MixedHodgeStructureMor(_ModuleMorCommonMethods, CategoricalMor):
    r"""The morphisms ``V -> V'`` of mixed Hodge structures, an ``R``-submodule of ``Hom_R(V, V')``."""

    ElementMethods = MixedHodgeStructureMorphismMethods

    def __init__(self, mor_family, domain, codomain) -> None:
        _initialize_module_mor_parent(self, mor_family, domain, codomain, full_linear_mor=False)

    def __call__(self, images):
        r"""Construct a morphism of mixed Hodge structures without Sage coercion discovery."""
        return self._element_constructor_(images)

    def _element_constructor_(self, images, *, check=False):
        r"""Construct the linear map; ``check=True`` runs its validators (``OWN-22``)."""
        morphism = super()._element_constructor_(images, check=check)
        morphism.validate_filtration_preservation(check=check)
        return morphism

    def _repr_(self):
        return f"Mor({self.domain()}, {self.codomain()}) in mixed Hodge structures over {self.base_ring()}"


class MixedHodgeStructureMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return MixedHodgeStructureMor


class MixedHodgeStructures(OwnedCategoryOverBaseRing):
    r"""Mixed Hodge structures over ``R`` (Deligne II (2.3.1)).

    The underlying ``R``-module ``V`` is finitely generated, so the
    supercategory is ``Modules(R).FinitelyGenerated()``.  The filtrations live
    on ``V tensor QQ`` and ``V tensor CC``, not on ``V``, so
    :class:`FilteredModules` is not a supercategory; each filtration is a
    value in ``FilteredModules`` of the extended base.
    """

    def _repr_object_names(self) -> str:
        return f"mixed Hodge structures over {self.base()}"

    def super_categories(self):
        return [Modules(self.base_ring()).FinitelyGenerated()]

    _MorCategory = MixedHodgeStructureMorCategoryConstruction

    def an_object(self):
        r"""The Tate structure ``R(1)``, pure of weight ``-2`` and type ``(-1, -1)`` (Deligne II (2.1.13))."""
        return self.tate_structure(1)

    def tate_structure(self, n):
        r"""The Tate structure ``R(n)``: ``R`` of weight ``-2n`` and type ``(-n, -n)``.

        The object is pure of weight
        ``-2n``, so it lies in ``HodgeStructures(R, -2n)``.
        """
        return _split_mixed_hodge_structure(
            self.base_ring(), (-2 * _owned_integers()(n),), name=f"Tate structure R({n}) over {self.base()}"
        )

    def _call_(self, module, weight_filtration, hodge_filtration):
        r"""The mixed Hodge structure ``(V, W, F)``.

        ``weight_filtration`` is an object of ``FilteredModules(R tensor QQ)``
        on ``V tensor QQ`` in the reindexed form ``W^{-n} = W_n``;
        ``hodge_filtration`` is an object of ``FilteredModules(CC)`` on
        ``V tensor CC``.
        """
        assert False, "construction on MixedHodgeStructures(R): not implemented"

    def weight_graded_functor(self, weight):
        r"""``Gr^W_n: MixedHodgeStructures(R) -> HodgeStructures(R, n)``.

        Exact, since morphisms are strictly compatible with ``W``
        (Deligne II (2.3.5)).
        """
        assert False, "weight_graded_functor on MixedHodgeStructures(R): not implemented"

    class ParentMethods:
        def __init__(
            self,
            hodge_weights=None,
            hodge_number_table=None,
            polarizable_weights=frozenset(),
            **rest,
        ) -> None:
            self._hodge_weights = hodge_weights
            self._hodge_number_table_supplier = hodge_number_table
            self._polarizable_weights = polarizable_weights
            super().__init__(**rest)

        def weight_of_module_generator(self, label):
            r"""The weight ``n`` of the summand ``Gr^W_n`` that the basis vector ``label`` spans in."""
            return self._hodge_weights[int(label)]

        def weight_support(self):
            r"""The finite set of ``n`` with ``Gr^W_n V != 0``."""
            return finite_ordered_set(tuple(sorted(frozenset(self._hodge_weights))))

        def is_pure(self) -> bool:
            r"""``Gr^W_m V = 0`` for every weight ``m`` but at most one."""
            return int(self.weight_support().cardinality()) <= 1

        @cached_method
        def _hodge_number_table(self):
            return self._hodge_number_table_supplier()

        def hodge_number(self, p, q):
            r"""``h^{p,q} = dim_CC Gr_F^p Gr^W_{p+q} (V tensor CC)``, a natural number."""
            return self._hodge_number_table().get((int(p), int(q)), NN(0))

        def is_hodge_tate(self) -> bool:
            r"""``h^{p,q} = 0`` for ``p != q``: each ``Gr^W_{2p}`` is a sum of copies of ``R(-p)``."""
            return all(p == q for p, q in self._hodge_number_table())

        def weight_filtration(self):
            r"""``W`` on ``V tensor QQ``, an object of ``FilteredModules(R tensor QQ)``."""
            assert False, "weight_filtration on MixedHodgeStructures(R): not implemented"

        def hodge_filtration(self):
            r"""``F`` on ``V tensor CC``, an object of ``FilteredModules(CC)``."""
            assert False, "hodge_filtration on MixedHodgeStructures(R): not implemented"

        def weight_graded_piece(self, weight):
            r"""``Gr^W_n V``, an object of ``HodgeStructures(R, n)``.

            ``W`` is split, so ``Gr^W_n V`` is the span of the basis vectors of
            weight ``n``, with the Hodge numbers of ``V`` in bidegrees
            ``p + q = n``.
            """
            weight = _owned_integers()(weight)
            table = self._hodge_number_table()
            count = sum(1 for own in self._hodge_weights if own == weight)
            name = f"Gr^W_{weight} of {self}"
            return _split_mixed_hodge_structure(
                self.base_ring(),
                (weight,) * count,
                hodge_number_table=lambda: {
                    bidegree: value for bidegree, value in table.items() if sum(bidegree) == int(weight)
                },
                polarizable_weights=self._polarizable_weights & frozenset((weight,)),
                name=name,
            )

        def tate_twist(self, n):
            r"""``V(n) = V tensor R(n)``: weights drop by ``2n`` and ``h^{p,q}(V(n)) = h^{p+n,q+n}(V)``."""
            n = int(n)
            table = self._hodge_number_table()
            return _split_mixed_hodge_structure(
                self.base_ring(),
                tuple(weight - 2 * n for weight in self._hodge_weights),
                hodge_number_table=lambda: {(p - n, q - n): value for (p, q), value in table.items()},
                polarizable_weights=frozenset(weight - 2 * n for weight in self._polarizable_weights),
            )

        def tensor_product(self, other):
            r"""``V tensor_R V'`` with the convolution filtrations.

            ``W_n(V tensor V') = sum_{a+b=n} W_a V tensor W_b V'`` and
            ``F^p = sum_{a+b=p} F^a tensor F^b``, so
            ``h^{p,q} = sum h^{a,b}(V) h^{p-a,q-b}(V')``.
            """
            assert other in MixedHodgeStructures(self.base_ring()), (
                f"the tensor product of mixed Hodge structures needs {other} in "
                f"{MixedHodgeStructures(self.base_ring())}"
            )
            left, right = self._hodge_number_table(), other._hodge_number_table()
            pairs = tuple(
                (weight, other_weight)
                for weight in self._hodge_weights
                for other_weight in other._hodge_weights
            )
            # ``Gr^W_n`` of the product is ``sum_{a+b=n} Gr^W_a tensor Gr^W_b``,
            # polarized by the products of polarizations when every factor is.
            unpolarizable = frozenset(
                weight + other_weight
                for weight, other_weight in pairs
                if weight not in self._polarizable_weights
                or other_weight not in other._polarizable_weights
            )
            weights = tuple(weight + other_weight for weight, other_weight in pairs)
            return _split_mixed_hodge_structure(
                self.base_ring(),
                weights,
                hodge_number_table=lambda: _convolved_hodge_numbers(left, right),
                polarizable_weights=frozenset(weights) - unpolarizable,
            )

        def dual_hodge_structure(self):
            r"""``V^vee = Hom_R(V, R)`` with ``W_k(V^vee) = (V / W_{-k-1})^vee``.

            The basis dual to a basis of weight ``n`` vectors has weight
            ``-n``, and ``h^{p,q}(V^vee) = h^{-p,-q}(V)``.
            """
            table = self._hodge_number_table()
            return _split_mixed_hodge_structure(
                self.base_ring(),
                tuple(-weight for weight in self._hodge_weights),
                hodge_number_table=lambda: {(-p, -q): value for (p, q), value in table.items()},
                polarizable_weights=frozenset(-weight for weight in self._polarizable_weights),
            )

        def Mor(self, codomain, category=None):
            r"""The ``R``-linear maps whose scalar extensions preserve ``W`` and ``F``."""
            if category is None:
                return MixedHodgeStructures(self.base_ring()).Mor(self, codomain)
            return category.Mor(self, codomain)


class HodgeStructures(OwnedCategoryOverBaseRing):
    r"""Hodge structures of weight ``n`` over ``R`` (Deligne II (2.1.1)).

    The full subcategory of ``MixedHodgeStructures(R)`` with ``Gr^W_m = 0`` for
    ``m != n``.  The condition depends on the integer ``n``, so it is a
    parameter of the category and not a parameterless axiom.
    """

    @staticmethod
    def __classcall__(cls, base_ring, weight):
        return OwnedCategoryOverBaseRing.__classcall__(
            cls, base_ring, _owned_integers()(weight)
        )

    def __init__(self, base_ring, weight) -> None:
        self._weight = weight
        super().__init__(base_ring)

    def weight(self):
        r"""The weight ``n``, an element of ``ZZ``."""
        return self._weight

    def _repr_object_names(self) -> str:
        return f"Hodge structures of weight {self.weight()} over {self.base()}"

    def _make_named_class_key(self, name):
        return (super()._make_named_class_key(name), self.weight())

    def super_categories(self):
        return [MixedHodgeStructures(self.base_ring())]

    def an_object(self):
        r"""A polarizable Hodge structure of weight ``n``.

        For even ``n = 2m`` it is the Tate structure ``R(-m)`` (Deligne II
        (2.1.13)).  For odd ``n = 2m + 1`` it is ``R^2`` of type
        ``(m + 1, m) + (m, m + 1)``, the type of ``H^1`` of an elliptic curve
        twisted by ``R(-m)``, polarized as that curve's cup product.
        """
        weight = self.weight()
        half = weight // 2
        match int(weight % 2):
            case 0:
                return MixedHodgeStructures(self.base_ring()).tate_structure(-half)
            case 1:
                return _split_mixed_hodge_structure(
                    self.base_ring(),
                    (weight, weight),
                    hodge_number_table=lambda: {
                        (int(half) + 1, int(half)): NN(1),
                        (int(half), int(half) + 1): NN(1),
                    },
                    polarizable_weights=frozenset((weight,)),
                    name=f"Hodge structure of type ({half + 1}, {half}) + ({half}, {half + 1}) over {self.base()}",
                )

    class SubcategoryMethods:
        def Polarizable(self) -> Category:
            r"""Hodge structures that admit a polarization (Deligne II (2.1.15))."""
            return self._with_axiom("Polarizable")

    class ParentMethods:
        def hodge_decomposition(self):
            r"""``V tensor CC = ⊕_{p+q=n} V^{p,q}``, an object of ``GradedModules(CC, ZZ)``.

            The piece of degree ``p`` is ``V^{p,n-p} = F^p cap conj(F^{n-p})``.
            """
            assert False, "hodge_decomposition on HodgeStructures(R, n): not implemented"

        def weil_operator(self):
            r"""``C`` acting by ``i^{p-q}`` on ``V^{p,q}``, an endomorphism of ``V tensor RR``."""
            assert False, "weil_operator on HodgeStructures(R, n): not implemented"

    class Polarizable(CategoryWithAxiom):
        r"""Polarizable Hodge structures of weight ``n``.

        Full: a morphism of Hodge structures between polarizable ones is a
        morphism here; a chosen polarization is the data of
        :class:`PolarizedHodgeStructures`.
        """

        def _repr_object_names(self) -> str:
            return f"polarizable {self.base_category()._repr_object_names()}"


HodgeStructures.__dict__["Polarizable"]._base_category_class_and_axiom = (
    HodgeStructures,
    "Polarizable",
)


class PolarizedHodgeStructures(OwnedCategoryOverBaseRing):
    r"""Hodge structures of weight ``n`` with a chosen polarization.

    An object is ``(V, Q)`` with ``Q: V tensor V -> R(-n)`` ``(-1)^n``-symmetric,
    ``Q(V^{p,q}, V^{p',q'}) = 0`` unless ``p = q'``, and
    ``Q(Cx, conj(x)) > 0`` for ``x != 0`` (Deligne II (2.1.15)).  A morphism
    preserves ``Q``, so this data subcategory is not full.
    """

    @staticmethod
    def __classcall__(cls, base_ring, weight):
        return OwnedCategoryOverBaseRing.__classcall__(
            cls, base_ring, _owned_integers()(weight)
        )

    def __init__(self, base_ring, weight) -> None:
        self._weight = weight
        super().__init__(base_ring)

    def weight(self):
        r"""The weight ``n``, an element of ``ZZ``."""
        return self._weight

    def _repr_object_names(self) -> str:
        return f"polarized Hodge structures of weight {self.weight()} over {self.base()}"

    def _make_named_class_key(self, name):
        return (super()._make_named_class_key(name), self.weight())

    def super_categories(self):
        return [HodgeStructures(self.base_ring(), self.weight()).Polarizable()]

    class ParentMethods:
        def polarization(self):
            r"""The chosen ``Q: V tensor V -> R(-n)``, an arrow of ``Modules(R)``."""
            assert False, "polarization on PolarizedHodgeStructures(R, n): not implemented"
