"""Owned ringed-space structure used by the scheme hierarchy."""

from itertools import combinations

from sage.categories.category import Category
from sage.categories.morphism import Morphism
from sage.categories.category_with_axiom import all_axioms
from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.classcall_metaclass import typecall
from sage.structure.dynamic_class import DynamicMetaclass
from sage.structure.richcmp import op_EQ, op_NE
from sage.structure.sage_object import SageObject

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoryPacketMethods,
    CategoricalMor,
    FixedMorCategory,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.objects import (
    Objects,
    OwnedCategory,
    OwnedParameterizedCategory,
)
from sage_extensions.categories.abstract_categories.presheaves import (
    Coverage,
    CoveringFamilies,
    CoveringFamilyMorCategoryConstruction,
    CoveringFamilyMor,
    CoveringFamilyMorphism,
    DescentData,
)
from sage_extensions.categories.functors.core import Functor, IdentityFunctor
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import finite_indexed_family
from sage_extensions.categories.topological_spaces import TopologicalSpaces
from sage_extensions.logic import AtomicProposition, conjunction, negation
from sage_extensions.owned_category import _object_of, owned_category_join
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.validation import validator
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


if "Invertible" not in all_axioms:
    all_axioms.add("Invertible")
if "FiniteLocallyFree" not in all_axioms:
    all_axioms.add("FiniteLocallyFree")


class _SchemeTopologyData(SageObject):
    r"""The Zariski topology of a scheme ``X`` glued from affine charts.

    The open subsets of ``X`` are the subsets ``U`` whose preimage in every
    chart ``U_i = Spec A_i`` is open (Stacks, Lemma 26.14.1, Tag 01JB).  The topology is the
    subobject of the power set cut out by openness. A gluing realization
    supplies this topology through its topological colimit. Computing
    openness still requires the preimages to be represented at the chart
    topology owners. Without a selected gluing realization, only the empty
    set and whole space have a supplied openness decision here.
    """

    def open_subsets(self, space):
        if space.has_selected_finite_affine_atlas():
            return space.underlying_space().power_set().condition_set(
                lambda subset: self.is_open_subset(space, subset)
            )
        return space.power_set().condition_set(
            lambda subset: self.is_open_subset(space, subset)
        )

    def is_open_subset(self, space, subset) -> bool:
        if space.has_selected_finite_affine_atlas():
            from sage_extensions.categories.schemes.gluing import _AffineChartOpenSubobjects

            if subset in _AffineChartOpenSubobjects(space):
                return True
            return space.underlying_space().is_open_subset(subset)
        power = space.power_set()
        selected = power(subset)
        match selected:
            case _ if power.inclusion_order().le(selected, power.bottom()) is True:
                return True
            case _ if power.inclusion_order().le(power.top(), selected) is True:
                return True
            case _:
                assert False, (
                    f"whether {subset} is open in {space} is decided only for the empty set and "
                    f"the whole space; {space} is a scheme glued from affine charts"
                )


class _AffineSchemeTopologyData(SageObject):
    r"""The Zariski topology of ``X = Spec A``, read from the prime spectrum of ``A``.

    The points of ``Spec A`` are the prime ideals of ``A`` (Stacks, Definition
    10.17.1, Tag 00DZ), and the opens of ``X`` are the opens of that prime
    spectrum.
    """

    def __init__(self, coordinate_algebra) -> None:
        self._coordinate_algebra = coordinate_algebra

    def open_subsets(self, space):
        return self._coordinate_algebra.spectrum().open_subsets()

    def is_open_subset(self, space, subset) -> bool:
        return self._coordinate_algebra.spectrum().is_open_subset(subset)


class PresheafObjects(OwnedParameterizedCategory):
    r"""Presheaves on a topological space ``X``: the Grothendieck construction ``∫_{D in Cat} [Open(X)^op, D]``.

    An object is a pair ``(D, F)`` of a category ``D`` and a functor
    ``F: Open(X)^op -> D`` (Mathlib ``TopCat.Presheaf``, which fixes ``D``;
    here ``D`` varies).  A morphism ``(D, F) -> (D', F')`` is a pair
    ``(G, alpha)`` of a functor ``G: D -> D'`` and a natural transformation
    ``alpha: G F => F'``; composition is ``(G', alpha') (G, alpha) =
    (G' G, alpha' . G' alpha)``.  This is the Grothendieck construction of
    the functor ``Cat -> Cat``, ``D -> [Open(X)^op, D]``, ``G -> G_*``
    (Mathlib ``CategoryTheory.Grothendieck``).  The projection to
    ``Cat`` sends ``(D, F)`` to ``D``; its fibre over ``D`` is the functor
    category ``[Open(X)^op, D]`` (:meth:`with_values`), whose morphisms are
    the pairs ``(id_D, alpha)``.  The coslice ``Open(X)^op / Cat`` is the
    wide subcategory of the pairs ``(G, id)``, so it is no supercategory.

    No Grothendieck construction of a ``Cat``-valued functor is presented
    in the tree, so this category declares no supercategory.
    """

    def parameter_category(self):
        return TopologicalSpaces()

    def space(self):
        return self.base()

    def _repr_object_names(self):
        return f"presheaves on {self.space()}"

    def site(self) -> Category:
        r"""``Open(X)``, the poset category of the opens of ``X``."""
        return self.space().open_subsets_site()

    def super_categories(self):
        return []

    def with_values(self, value_category: Category) -> Category:
        r"""``[Open(X)^op, D]``, the fibre over ``D`` of the projection ``∫ [Open(X)^op, -] -> Cat``.

        Its objects are the presheaves on ``X`` with values in ``D``; its
        morphisms are the pairs ``(id_D, alpha)``, the natural
        transformations.
        """
        return self.site().presheaves(value_category)

    def value_change(self, value_functor: Functor) -> Functor:
        r"""``G_*: [Open(X)^op, D] -> [Open(X)^op, D']``, ``F -> G F``, for ``G: D -> D'``.

        The action on arrows of the functor whose Grothendieck construction
        this category is: the presheaf bifunctor on ``(id_{Open(X)}, G)``.
        """
        from sage_extensions.categories.abstract_categories.cat import Cat

        return Cat().presheaf_transport(IdentityFunctor(self.site()), value_functor)

    def morphism(self, source, target, value_functor: Functor, transformation):
        r"""``(G, alpha): (D, F) -> (D', F')`` for ``G: D -> D'`` and ``alpha: G F => F'``."""
        assert False, "morphism (G, alpha) of presheaves on PresheafObjects: not implemented"

    def presheaf_datum(self, presheaf: Functor):
        r"""The datum ``F: Open(X)^op -> D`` of an object ``(D, F)`` of this category."""
        assert presheaf.domain() is self.site().opposite(), (
            f"a presheaf on {self.space()} is a functor on Open(X)^op, but {presheaf} is a "
            f"functor on {presheaf.domain()}"
        )
        return {"open_sections_presheaf": presheaf}

    class ParentMethods:
        r"""A presheaf ``(D, F)`` on ``X``, with its functor ``F: Open(X)^op -> D``."""

        def __init__(self, open_sections_presheaf: Functor, **rest) -> None:
            self._open_sections_presheaf = open_sections_presheaf
            super().__init__(**rest)

        def open_sections_presheaf(self) -> Functor:
            r"""``F: Open(X)^op -> D``, ``U -> F(U)``, with the restriction maps."""
            return self._open_sections_presheaf

        def value_category(self) -> Category:
            r"""``D``, the image of ``(D, F)`` under the projection to ``Cat``."""
            return self._open_sections_presheaf.codomain()


class _UnpresentedSectionsPresheaf(Functor):
    r"""``F: Open(X)^op -> D`` of a sheaf whose sections on the opens of ``X`` are not presented.

    The sheaf is represented by a private realization on a basis or an atlas
    of ``X``; its values ``F(U)`` on the opens ``U`` of ``X`` are not computed.
    """

    def __init__(self, space, value_category: Category, sheaf_name: str) -> None:
        self._sheaf_name = sheaf_name
        Functor.__init__(self, space.open_subsets_site().opposite(), value_category)

    def _apply_object(self, opposite_object):
        assert False, f"sections of {self._sheaf_name} on {opposite_object}: not implemented"

    def _apply_morphism(self, opposite_arrow):
        assert False, f"restriction of {self._sheaf_name} along {opposite_arrow}: not implemented"

    def _repr_(self):
        return f"Sections presheaf of {self._sheaf_name}"


def _unpresented_sections_presheaf(space, sheaf_name: str, value_category: Category | None = None):
    r"""``F: Open(X)^op -> D`` of a sheaf whose sections on the opens of ``space`` are not presented.

    ``D`` defaults to ``Ab = Modules(ZZ)``, an abelian group being a
    ``ZZ``-module: the sections of a sheaf of ``O_X``-modules, or of a sheaf of
    abelian groups such as ``O_X^*``, form abelian groups.
    """
    from sage_extensions.categories.modules.pure.modules import Modules
    from sage_extensions.categories.rings.ring_foundation import _owned_integers

    values = Modules(_owned_integers()) if value_category is None else value_category
    return _UnpresentedSectionsPresheaf(space, values, sheaf_name)


def _unpresented_sheaf_placement(
    space, sheaf_name: str, mor_category: Category | None = None, value_category: Category | None = None
):
    r"""``Sh(Open(X), D)`` and its data for a sheaf whose sections on opens are not presented.

    An object ``(D, F)`` of ``∫ [Open(X)^op, -]`` lies in the fibre over ``D``
    of the projection to ``Cat``; a sheaf lies in the full subcategory
    ``Sh(Open(X), D)`` of that fibre, on ``F`` with its descent data for the
    open covers of ``X``.  The descent comparison on a cover is computed when
    a caller asks for it.  ``mor_category`` is the category whose morphisms
    the sheaf's arrows are, such as ``O_X``-linear maps; by default it is the
    fibre, whose morphisms are the natural transformations of the sections
    functors.
    """
    presheaf = _unpresented_sections_presheaf(space, sheaf_name, value_category)
    return _open_sheaf_placement(space, presheaf, mor_category)


def _is_empty_open(presheaf, opposite_object):
    r"""Recognize the canonical empty open of the presheaf's open site."""
    opens = presheaf.domain().base_category().object_set()
    return opposite_object.underlying_object().value() is opens.inclusion().codomain().bottom()


def _open_sheaf_placement(space, presheaf, mor_category=None):
    r"""Place a sections functor in the sheaves on the open site of its space."""
    from sage_extensions.categories.abstract_categories.presheaves import (
        OpenCoveringFamilies,
    )

    presheaves = PresheafObjects(space)
    coverage = OpenCoveringFamilies(space)
    sheaves = coverage.sheaves(presheaf.codomain())

    def inverse_for(equalizer):
        return equalizer.canonical_map().inverse()

    return sheaves, {
        **presheaves.presheaf_datum(presheaf),
        "descent_data": DescentData(coverage, presheaf, inverse_for),
        "fixed_mor_category": sheaves if mor_category is None else mor_category,
    }


class SheafObjects(OwnedParameterizedCategory):
    r"""Sheaves on a ringed space ``X``: the full subcategory of :class:`PresheafObjects` cut out by descent.

    An object ``(D, F)`` satisfies descent for the open coverings of ``X``
    (Mathlib ``TopCat.Sheaf``).  For one ``D`` these are the objects of
    :meth:`with_values`, ``Sh(Open(X), D)``.  Sections are computed on the basis
    opens that a sheaf's realization presents.
    """

    def parameter_category(self):
        return RingedSpaces()

    def space(self):
        return self.base()

    def _repr_object_names(self):
        return f"sheaves on {self.space()}"

    def super_categories(self):
        return [PresheafObjects(self.space())]

    def with_values(self, value_category: Category) -> Category:
        r"""``Sh(Open(X), D)``, the sheaves in the fibre over ``D`` of the projection to ``Cat``."""
        from sage_extensions.categories.abstract_categories.presheaves import (
            OpenCoveringFamilies,
        )

        return OpenCoveringFamilies(self.space()).sheaves(value_category)

    def an_object(self):
        return self.space().structure_sheaf()


class SheafedSpaces(OwnedCategory):
    r"""Sheafed spaces ``(X, F)``: a topological space ``X`` with a sheaf ``F`` on ``Open(X)``.

    Forgetting the sheaf is the functor to ``TopologicalSpaces``.  A sheafed
    space is therefore constructed on its own points and opens, and its
    underlying space is the image of that functor.
    """

    @classmethod
    def _repr_object_names(cls):
        return "sheafed spaces"

    def super_categories(self):
        return [TopologicalSpaces()]

    def an_object(self):
        return RingedSpaces().an_object()

    class ParentMethods:
        def underlying_space(self):
            r"""``|X|``, the image of ``(X, F)`` under the forgetful functor to ``TopologicalSpaces``.

            Forgetting the sheaf leaves the space ``X`` itself, with its own
            points and opens.
            """
            return self




class ModuleSheaves(OwnedParameterizedCategory):
    r"""Sheaves of ``O_X``-modules on one represented ringed space ``X``."""

    def scheme(self):
        return self.base()

    ringed_space = scheme

    def _repr_object_names(self):
        return f"module sheaves on {self.scheme()}"

    def super_categories(self):
        return [SheafObjects(self.scheme())]

    def an_object(self):
        return self.scheme().structure_sheaf()

    def tensor_product(self, factors):
        r"""Return the tensor product of represented module sheaves.

        The currently selected affine implementation is transported through
        the existing equivalence ``QCoh(Spec A) ~= Modules(A)``.  Moving this
        operation here records its mathematical owner: quasi-coherence adds a
        condition on a module sheaf; it does not define a second tensor
        product.
        """

        quasi_coherent = QuasiCoherentSheaves(self.scheme())
        modules = tuple(quasi_coherent.global_sections(factor) for factor in factors)
        return quasi_coherent.associated_sheaf(
            quasi_coherent.module_category().tensor_product(modules)
        )

    def kernel(self, sheaf_morphism):
        r"""Return the represented kernel in sheaves of ``O_X``-modules."""
        return sheaf_morphism.kernel()

    def cokernel(self, sheaf_morphism):
        r"""Return the represented cokernel in sheaves of ``O_X``-modules."""
        return sheaf_morphism.cokernel()

    def derived_global_sections(self):
        r"""``RΓ(X, -) : Mod(O_X) -> D(Γ(X, O_X))``, the right derived functor of global sections.

        Domain: sheaves of ``O_X``-modules on ``X``.  Codomain:
        ``DerivedCategory(Γ(X, O_X))``.  On an object, ``RΓ(X, F)`` is the
        class of ``Γ(X, I^•)`` for an injective resolution ``F -> I^•``,
        which exists because ``Mod(O_X)`` has enough injectives; its
        ``i``-th cohomology is ``H^i(X, F)``.
        """
        assert False, "derived_global_sections on ModuleSheaves: not implemented"

    class ParentMethods:
        def derived_global_sections(self):
            r"""``RΓ(X, F)``, an object of ``DerivedCategory(Γ(X, O_X))``.

            The image of this sheaf ``F`` under
            ``ModuleSheaves(X).derived_global_sections()``.  Computed for the
            standard line bundles ``O(d)`` on ``P^n_R``, ``n >= 1``, from
            Hartshorne, Theorem III.5.1, and for a quasi-coherent sheaf on an
            affine scheme from its one-chart Čech complex, which is acyclic
            (Stacks, Tag 01XB).
            """
            from sage_extensions.categories.schemes.geometric_cohomology import (
                _projective_space_line_bundle_derived_global_sections,
            )
            from sage_extensions.categories.schemes.schemes import ProjectiveSpaces, Schemes

            space = self.scheme()
            base = space.scheme_base_ring()
            match space:
                case _ if space in ProjectiveSpaces(base) and self in InvertibleSheavesWithChosenTrivialization(space):
                    return _projective_space_line_bundle_derived_global_sections(self)
                case _ if space in Schemes(base).Affine() and self in QuasiCoherentSheaves(space):
                    return self.geometric_cohomology_complex().derived_global_sections()
                case _:
                    assert False, "derived_global_sections on ModuleSheaves: not implemented"

        def sheaf_cohomology(self, degree):
            r"""``H^degree(X, F) = H^degree(RΓ(X, F))``, an object of ``Modules(Γ(X, O_X))``."""
            return self.derived_global_sections().cohomology(degree)

        def total_sheaf_cohomology(self):
            r"""``⊕_i H^i(X, F)``, an object of ``GradedModules(Γ(X, O_X))`` with ``H^i(X, F)`` in degree ``i``."""
            return self.derived_global_sections().graded_cohomology()


def _represented_sheaf_mor(domain, codomain):
    r"""The selected represented sheaf Mor shared by these endpoints.

    A pair built on one literal sheaf presentation uses that presentation's
    full-subcategory Mor.  The currently represented cross-presentation case
    is quasi-coherent sheaves, whose Mor owner compares affine and finite-atlas
    realizations.  A future non-quasi-coherent mixed presentation must supply
    its own common sheaf-arrow realization instead of being treated as a map
    merely because the endpoints are objects.
    """
    source_mor = getattr(domain, "_fixed_mor_category", None)
    target_mor = getattr(codomain, "_fixed_mor_category", None)
    if source_mor is not None and source_mor is target_mor:
        return source_mor.Mor(domain, codomain)
    scheme = domain.scheme()
    quasi_coherent = QuasiCoherentSheaves(scheme)
    if domain in quasi_coherent and codomain in quasi_coherent:
        return quasi_coherent.Mor(domain, codomain)
    raise TypeError(
        f"the sheaves {domain} and {codomain} have no selected common sheaf-morphism realization; "
        "their algebra-sheaf Hom exists mathematically, but this representation needs a common "
        "sheaf-arrow computation before an underlying arrow can be supplied"
    )


class AlgebraSheafMorphismMethods:
    r"""A morphism of ``O_X``-algebra sheaves on one represented ringed space.

    The underlying sheaf arrow is retained exactly.  Preservation of
    multiplication and unit are the defining arrow equations.  An arbitrary
    represented sheaf arrow states those equations as premises; constructions
    such as identity and composition derive them and record ``True``.
    """

    def __init__(self, parent, underlying_morphism, *, algebra_laws=None) -> None:
        underlying = _represented_sheaf_mor(parent.domain(), parent.codomain())(
            underlying_morphism
        )
        self._underlying_sheaf_morphism = underlying
        self._algebra_laws = algebra_laws
        super().__init__(parent)

    def underlying_sheaf_morphism(self):
        return self._underlying_sheaf_morphism

    def preserves_multiplication(self):
        if self._algebra_laws is True:
            return True
        return AtomicProposition("preserves_algebra_sheaf_multiplication", self)

    def preserves_unit(self):
        if self._algebra_laws is True:
            return True
        return AtomicProposition("preserves_algebra_sheaf_unit", self)

    def _richcmp_(self, other, op):
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if other not in self.parent():
            return op == op_NE
        equal = self.underlying_sheaf_morphism() == other.underlying_sheaf_morphism()
        return equal if op == op_EQ else negation(equal)

    def __eq__(self, other):
        return self._richcmp_(other, op_EQ)

    def __ne__(self, other):
        return self._richcmp_(other, op_NE)

    def __mul__(self, other):
        if other.codomain() is not self.domain() or other not in self.parent().mor_category().Mor(
            other.domain(), self.domain()
        ):
            return NotImplemented
        mor = self.parent().mor_category().Mor(other.domain(), self.codomain())
        return mor._from_known_algebra_map(
            self.underlying_sheaf_morphism() * other.underlying_sheaf_morphism()
        )


class AlgebraSheafMor(CategoricalMor):
    r"""``Hom_{O_X-Alg}(A,B)`` with its represented underlying sheaf arrow."""

    ElementMethods = AlgebraSheafMorphismMethods

    def _element_constructor_(self, underlying_morphism):
        if isinstance(underlying_morphism, AlgebraSheafMorphismMethods):
            if underlying_morphism.parent() is self:
                return underlying_morphism
            raise TypeError(f"{underlying_morphism} belongs to another Mor; apply the functor between the categories")
        return self.element_class(self, underlying_morphism)

    def _from_known_algebra_map(self, underlying_morphism):
        return self.element_class(self, underlying_morphism, algebra_laws=True)

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"there is no identity algebra-sheaf morphism {self.domain()} -> {self.codomain()}: "
                "the endpoints differ"
            )
        underlying = _represented_sheaf_mor(self.domain(), self.domain()).identity()
        return self._from_known_algebra_map(underlying)


class AlgebraSheafMorCategoryConstruction(MorCategoryConstruction):
    FixedCategoryClass = AlgebraSheafMor


class AlgebraSheaves(OwnedParameterizedCategory):
    r"""Sheaves of ``O_X``-algebras on one represented ringed space ``X``."""

    def scheme(self):
        return self.base()

    ringed_space = scheme

    def _repr_object_names(self):
        return f"algebra sheaves on {self.scheme()}"

    def super_categories(self):
        return [ModuleSheaves(self.scheme())]

    _MorCategory = AlgebraSheafMorCategoryConstruction

    def object(self, presheaf, *, categories=(), construction_data=None, _engine):
        r"""Construct an algebra sheaf from its sections on the open site."""
        fibre, presheaf_data = _open_sheaf_placement(self.scheme(), presheaf, self)
        return open_sections_presheaf._with_structure(
            (self, fibre, *tuple(categories)),
            {
                **presheaf_data,
                **dict(construction_data or {}),
            },
            engine=_engine,
        )

    def an_object(self):
        return self.scheme().structure_sheaf()


class _StructureSheafEngine:
    r"""The represented structure sheaf ``O_X`` of a ringed space ``X``."""

    def __init__(self, ringed_space, **rest) -> None:
        self._ringed_space = ringed_space
        self._restriction_maps = {}
        super().__init__(**rest)

    def presheaf(self):
        r"""The ring-valued sections functor underlying ``O_X`` on its open site."""
        return self.functor()

    @cached_method(key=lambda self, cover: id(cover))
    def module_descent_datum(self, cover):
        r"""The rank-one module descent presentation of ``O_X`` on ``cover``."""
        if cover.ambient_scheme() is not self.ringed_space():
            raise ValueError(
                f"the structure sheaf of {self.ringed_space()} can be described only on a cover of "
                f"{self.ringed_space()}, but {cover} is a cover of {cover.ambient_scheme()}"
            )
        from sage_extensions.categories.schemes.gluing import ModuleGluingData

        return ModuleGluingData(cover).an_object()

    def cech_sheaf(self, cover):
        r"""The canonical module-valued sheaf object on the finite Čech site of ``cover``."""
        return self.module_descent_datum(cover).sheaf()

    def ringed_space(self):
        return self._ringed_space

    scheme = ringed_space

    def global_sections(self):
        r"""Return ``Gamma(X,O_X)=O(X)``, the ring, for the represented affine scheme.

        ``O_X`` is a sheaf of commutative rings, so ``Gamma(X, O_X)`` is the
        ring ``O(X)``.  This representation builds ``O_X`` valued in
        ``Modules(O(X))``, where evaluation at ``id_X`` gives the regular
        module instead, so the ring answer stays here until ``O_X`` is built
        valued in commutative rings and this method retires into
        ``Sheaves.ParentMethods.global_sections``.
        """
        return self.ringed_space().coordinate_algebra()

    def sections_on_distinguished_open(self, distinguished_open):
        r"""Return ``O_X(D(f)) = O(D(f))`` for a represented distinguished open."""
        assert _is_distinguished_open_of(distinguished_open, self.ringed_space()), (
            f"the sections of the structure sheaf of {self.ringed_space()} are computed on its "
            f"distinguished opens D(f), but {distinguished_open} is not one of them"
        )
        return distinguished_open.coordinate_algebra()

    def restriction_map(self, source_open, target_open):
        r"""Return the represented restriction ``O(source_open) -> O(target_open)``.

        The active basis consists of the affine scheme itself and its represented
        distinguished opens.  If both opens are proper, the target is accepted
        exactly when every selected denominator inverted on the source becomes a
        unit on the target.  This is the localization universal property, rather
        than a separate containment heuristic on points.
        """

        ambient = self.ringed_space()
        key = (id(source_open), id(target_open))
        cached = self._restriction_maps.get(key)
        if cached is not None:
            cached_source, cached_target, restriction = cached
            if cached_source is source_open and cached_target is target_open:
                return restriction

        def remember(restriction):
            self._restriction_maps[key] = (source_open, target_open, restriction)
            return restriction

        if source_open is ambient:
            source_sections = self.global_sections()
        elif _is_distinguished_open_of(source_open, ambient):
            source_sections = self.sections_on_distinguished_open(source_open)
        else:
            raise ValueError(
                f"restriction of functions on {ambient} starts at the whole scheme or a "
                f"distinguished open D(f) of it, but {source_open} is neither"
            )

        if target_open is ambient:
            if source_open is not ambient:
                return remember(_localization_restriction_map(source_sections, self.global_sections()))
            return remember(source_sections.Mor(source_sections).identity())
        if not _is_distinguished_open_of(target_open, ambient):
            raise ValueError(
                f"restriction of functions on {ambient} ends at the whole scheme or a "
                f"distinguished open D(f) of it, but {target_open} is neither"
            )
        target_sections = self.sections_on_distinguished_open(target_open)

        if source_open is ambient:
            restriction = target_open.inclusion().coordinate_algebra_morphism()
            if restriction.domain() is not source_sections or restriction.codomain() is not target_sections:
                raise ArithmeticError(
                    f"the inclusion of {target_open} into {ambient} pulls back functions along a map "
                    f"{restriction.domain()} -> {restriction.codomain()}, not "
                    f"{source_sections} -> {target_sections}"
                )
            return remember(restriction)
        if source_open is target_open:


            return remember(source_sections.Mor(source_sections).identity())
        return remember(_localization_restriction_map(source_sections, target_sections))

    def associated_module_sheaf(self, module):
        r"""Return the represented affine sheaf ``M~`` on the distinguished-open basis."""

        return QuasiCoherentSheaves(self.ringed_space()).associated_sheaf(module)

    def stalk(self, point):
        r"""Return ``O_{X,p}`` for a represented affine prime point."""
        assert point.parent() is self.ringed_space().underlying_space(), (
            f"the stalk of the structure sheaf of {self.ringed_space()} is taken at a point of "
            f"its spectrum, but {point} is a point of {point.parent()}"
        )
        return point.local_ring()

    def _repr_(self) -> str:
        return f"Structure sheaf O_{{{self.scheme()}}}"


def _structure_sheaf(ringed_space):
    r"""Construct ``O_X`` from its ring-valued sections on the open site."""
    return AlgebraSheaves(ringed_space).object(
        _AffineOpenStructurePresheaf(ringed_space),
        categories=(
            QuasiCoherentSheaves(ringed_space),
            QuasiCoherentSheaves(ringed_space).Invertible(),
        ),
        construction_data={"ringed_space": ringed_space},
        _engine=_StructureSheafEngine,
    )


class _AffineStructurePresheaf(Functor):
    r"""``U -> Gamma(U,O_U)`` on the represented affine slice over an affine ``X``.

    Values are read as ``O(X)``-modules by restriction of scalars along the
    coordinate pullback ``O(X) -> O(U)``.  An arrow ``V -> U`` over ``X``
    acts by its affine coordinate pullback ``O(U) -> O(V)``, regarded as an
    ``O(X)``-linear map between those restricted modules.
    """

    def __init__(self, scheme) -> None:
        from sage_extensions.categories.modules.pure.modules import Modules
        from sage_extensions.categories.schemes.schemes import Schemes

        base = scheme.scheme_base_ring()
        assert scheme in Schemes(base).Affine(), (
            f"the structure presheaf on affine schemes over X is constructed only for affine X, "
            f"but {scheme} is in {scheme.category()}"
        )
        self._scheme = scheme
        self._scalar_ring = scheme.coordinate_algebra()
        site = distinguished_affine_coverage(scheme).site_category()
        Functor.__init__(self, site.opposite(), Modules(self._scalar_ring))

    def scheme(self):
        return self._scheme

    def scalar_ring(self):
        return self._scalar_ring

    def site_category(self):
        return self.domain().base_category()

    def _slice_object(self, opposite_object):
        return opposite_object.underlying_object()

    def _apply_object(self, opposite_object):
        slice_object = self._slice_object(opposite_object)
        affine = slice_object.arrow().domain()
        algebra = affine.coordinate_algebra()
        scalar_map = slice_object.arrow().coordinate_algebra_morphism()
        if affine is self.scheme():
            return self.scalar_ring().regular_module()
        return algebra.regular_module().restrict_scalars(scalar_map)

    def _apply_morphism(self, opposite_arrow):
        from sage_extensions.categories.modules.pure.modules import RestrictedScalarsModules

        source = self(opposite_arrow.domain())
        target = self(opposite_arrow.codomain())
        triangle = opposite_arrow.underlying_arrow()
        pullback = triangle.left().coordinate_algebra_morphism()
        restricted = RestrictedScalarsModules(self.scalar_ring())

        def image(element):
            source_element = source(element)
            match source:
                case _ if source in restricted:
                    underlying = source_element.underlying_element()
                case _:
                    underlying = source_element
            pulled_back = pullback(underlying)
            match target:
                case _ if target in restricted:
                    return target.wrap(pulled_back)
                case _:
                    return target(pulled_back)

        # Pullback along a morphism of algebras over the scalar ring is linear
        # over that ring, so the construction alone gives linearity.
        return source.module_category().Mor(source, target)._from_constructed_element_map(
            image
        )

    def _repr_(self):
        return f"Affine structure presheaf of {self.scheme()}"


@cached_function(key=lambda scheme: id(scheme))
def _affine_de_rham_complex(scheme):
    r"""``Ω^•_{X/R}`` on the distinguished affine basis of an affine ``X``.

    The presheaf ``U -> DR_R(O(U))`` composes the coordinate algebra with the
    de Rham functor ``DR_R : CAlg_R -> SCDGA_R``.  It is a sheaf on the basis:
    each ``Ω^p_{X/R}`` is quasi-coherent with ``Ω^p_{A_f/R} = (Ω^p_{A/R})_f``
    (Stacks, Tags 00RT and 01UM), and a sheaf on a basis determines the sheaf
    on ``X`` (Stacks, Tag 009O).
    """
    from sage_extensions.categories.functors.de_rham import _de_rham_functor

    coverage = distinguished_affine_coverage(scheme)
    presheaf = _AffineDeRhamPresheaf(scheme)

    def inverse_for(equalizer):
        return equalizer.canonical_map().inverse()

    descent = DescentData(coverage, presheaf, inverse_for)
    values = _de_rham_functor(scheme.scheme_base_ring()).codomain()
    return coverage.sheaves(values).object(
        presheaf,
        descent,
        categories=(SheafObjects(scheme),),
        construction_data=PresheafObjects(scheme).presheaf_datum(_AffineOpenDeRhamPresheaf(scheme)),
    )


class _AffineOpenDeRhamPresheaf(Functor):
    r"""``Ω^•_{X/R}: Open(X)^op -> SCDGA_R`` of an affine ``X = Spec A``, on the basis opens.

    ``U -> DR_R(O_X(U))``: the de Rham functor ``DR_R`` composed with the
    structure presheaf, so ``X -> DR_R(A)``, ``D(f) -> DR_R(A_f)``, and a
    restriction is ``DR_R`` of the localization map (Stacks, Tag 00RT:
    ``Ω_{S^{-1}A/R} = S^{-1} Ω_{A/R}``).  Sections over an open that is not a
    basis open are not computed.
    """

    def __init__(self, scheme) -> None:
        from sage_extensions.categories.functors.de_rham import _de_rham_functor

        self._scheme = scheme
        self._structure_presheaf = _AffineOpenStructurePresheaf(scheme)
        self._de_rham_functor = _de_rham_functor(scheme.scheme_base_ring())
        Functor.__init__(self, scheme.open_subsets_site().opposite(), self._de_rham_functor.codomain())

    def scheme(self):
        return self._scheme

    def _apply_object(self, opposite_object):
        return self._de_rham_functor(self._structure_presheaf(opposite_object))

    def _apply_morphism(self, opposite_arrow):
        return self._de_rham_functor(self._structure_presheaf(opposite_arrow))

    def _repr_(self):
        return f"De Rham presheaf of {self.scheme()} on its opens"


class _AffineDeRhamPresheaf(Functor):
    r"""``U -> DR_R(O(U))`` on the represented affine slice over an affine ``X``.

    An arrow ``V -> U`` over ``X`` acts by ``DR_R`` of its coordinate
    pullback ``O(U) -> O(V)``, an ``R``-algebra morphism.
    """

    def __init__(self, scheme) -> None:
        from sage_extensions.categories.functors.de_rham import _de_rham_functor
        from sage_extensions.categories.schemes.schemes import Schemes

        base = scheme.scheme_base_ring()
        assert scheme in Schemes(base).Affine(), (
            f"the de Rham presheaf on affine schemes over X is constructed only for affine X, "
            f"but {scheme} is in {scheme.category()}"
        )
        self._scheme = scheme
        self._de_rham_functor = _de_rham_functor(base)
        site = distinguished_affine_coverage(scheme).site_category()
        Functor.__init__(self, site.opposite(), self._de_rham_functor.codomain())

    def scheme(self):
        return self._scheme

    def _apply_object(self, opposite_object):
        affine = opposite_object.underlying_object().arrow().domain()
        return self._de_rham_functor(affine.coordinate_algebra())

    def _apply_morphism(self, opposite_arrow):
        triangle = opposite_arrow.underlying_arrow()
        return self._de_rham_functor(triangle.left().coordinate_algebra_morphism())

    def _repr_(self):
        return f"Affine de Rham presheaf of {self.scheme()}"


class _AffineOpenStructurePresheaf(Functor):
    r"""``O_X: Open(X)^op -> CRing`` of an affine ``X = Spec A``, on the basis opens.

    ``O_X(X) = A`` and ``O_X(D(f)) = A_f``; restriction ``X -> D(f)`` is the
    localization map ``A -> A_f`` and ``D(f) -> D(g)`` is the induced map of
    localizations (Hartshorne II.2.2).  Sections over an open that is not a
    basis open are not computed.
    """

    def __init__(self, scheme) -> None:
        from sage_extensions.categories.rings.ring_foundation import OwnedRings

        self._scheme = scheme
        Functor.__init__(self, scheme.open_subsets_site().opposite(), OwnedRings().Commutative())

    def scheme(self):
        return self._scheme

    def _apply_object(self, opposite_object):
        from sage_extensions.categories.rings.commutative_algebra import (
            DistinguishedOpenSubobjects,
        )

        subset = opposite_object.underlying_object().value()
        spectrum = self.scheme().underlying_space()
        match subset:
            case _ if _is_empty_open(self, opposite_object):
                ring = self.scheme().coordinate_algebra()
                return ring.localization(ring.zero())
            case _ if subset is spectrum.power_set().top():
                return self.scheme().coordinate_algebra()
            case _ if subset in DistinguishedOpenSubobjects(spectrum):
                return subset.coordinate_ring()
        assert False, (
            f"sections of O_{{{self.scheme()}}} on {subset}: not implemented; only the basis "
            "opens X and D(f) are computed"
        )

    def _apply_morphism(self, opposite_arrow):
        source = self(opposite_arrow.domain())
        target = self(opposite_arrow.codomain())
        if source is target:
            return source.Mor(target).identity()
        if source is self.scheme().coordinate_algebra():
            return target.localization_map()
        return _localization_restriction_map(source, target)

    def _repr_(self):
        return f"Structure presheaf of {self.scheme()} on its opens"


def _is_distinguished_open_of(open_subscheme, ambient) -> bool:
    from sage_extensions.categories.schemes.schemes import OpenImmersions

    return (
        open_subscheme in OpenImmersions(ambient)
        and open_subscheme.is_distinguished_open() is True
    )


def _localization_restriction_map(source, target):
    r"""Return ``S^{-1}A -> T^{-1}A`` when the target inverts every element of ``S``."""

    from sage_extensions.categories.rings.ring_foundation import (
    LocalizationRings,
    OwnedRings,
)

    if source is target:
        return source.Mor(source).identity()
    if source not in LocalizationRings():
        raise TypeError(
            f"restriction from D(f) to D(g) is computed between localizations of the coordinate "
            f"ring, but the rings are {source} and {target}"
        )
    if target is source.localization_source():
        target_unit = target.Mor(target).identity()
    elif target in LocalizationRings() and source.localization_source() is target.localization_source():
        target_unit = target.localization_map()
    else:
        raise ValueError(
            f"restriction from {source} to {target} requires the coordinate ring "
            f"{source.localization_source()} or a localization of that ring"
        )
    generators = tuple(source.localization_submonoid().monoid_generators())
    if any(not target_unit(generator).is_unit() for generator in generators):
        raise ValueError(
            f"there is no restriction from {source} to {target}: the target open is not "
            "contained in the source open, since some inverted element of the source is not a "
            "unit on the target"
        )

    def restrict(element):
        element = source(element)
        numerator = target_unit(element.numerator())
        denominator = target_unit(element.denominator())
        return numerator * denominator.inverse_of_unit()

    return source.Mor(target, category=OwnedRings())(restrict)


class DistinguishedAffineCoverRefinement(CoveringFamilyMorphism):
    r"""A refinement morphism between distinguished affine covers of one affine scheme.

    This is a morphism in :class:`DistinguishedAffineCovers`, hence already a
    morphism of :class:`CoveringFamilies` in ``AffSch_R/X``.  Its component on
    a fine chart is the corresponding inclusion in that slice; geometric
    consumers can recover the underlying scheme inclusion with
    :meth:`inclusion`.
    """

    def fine_cover(self):
        return self.domain()

    def coarse_cover(self):
        return self.codomain()

    def ambient_scheme(self):
        return self.fine_cover().ambient_scheme()

    def inclusion(self, fine_index):
        fine_index = self.fine_cover().chart_label(fine_index)
        return self.component(fine_index).left()

    chart_map = inclusion

    def geometric_cochain_map(self, sheaf):
        from sage_extensions.categories.schemes.geometric_cohomology import (
            _affine_cover_refinement_cochain_map,
        )

        return _affine_cover_refinement_cochain_map(self, sheaf)

    def geometric_cohomology_comparison(self, sheaf, degree):
        from sage_extensions.categories.schemes.geometric_cohomology import (
            _affine_cover_refinement_cohomology_map,
        )

        return _affine_cover_refinement_cohomology_map(self, sheaf, degree)


class DistinguishedAffineCoverMor(CoveringFamilyMor):
    r"""The refinement Mor between two distinguished affine covers."""

    Element = DistinguishedAffineCoverRefinement


class DistinguishedAffineCoverMorCategoryConstruction(
    CoveringFamilyMorCategoryConstruction
):
    r"""The Mor family of distinguished affine covers."""

    def fixed_category_class(self):
        return DistinguishedAffineCoverMor


class ZariskiCoveringFamilies(OwnedParameterizedCategory):
    r"""Finite covering families in the big Zariski site ``Sch_R/X``.

    For a scheme ``X`` over ``R`` the underlying site category is the slice
    ``Sch_R/X``.  This category is the represented Zariski coverage on that
    slice: its objects are finite covering families selected by Zariski-open
    cover constructions.  Specializations such as finite affine atlases build
    their objects here rather than using all covering families of the slice as
    though every family were a Zariski cover.

    The singleton identity family is the canonical specimen and is available
    for every scheme, affine or not::

        sage: from dzack_research.preamble.all import QQ, ProjectiveSpaces
        sage: line = ProjectiveSpaces(QQ)(1)
        sage: coverage = zariski_coverage(line)
        sage: coverage.site_category().base_object() is line
        True
        sage: identity_cover = coverage.an_object()
        sage: identity_cover in coverage
        True
        sage: identity_cover.target().arrow() == line.categorical_identity_morphism()
        True
    """

    def parameter_category(self):
        from sage_extensions.categories.schemes.schemes import Schemes

        return Schemes(self.scheme().scheme_base_ring())

    def scheme(self):
        return self.base()

    def site_category(self):
        from sage_extensions.categories.schemes.schemes import Schemes

        return Schemes(self.scheme().scheme_base_ring()).SliceOver(self.scheme())

    @cached_method
    def slice_target(self):
        r"""The terminal object ``id_X`` of ``Sch_R/X``."""
        return self.site_category().an_object()

    terminal_site_object = slice_target

    def super_categories(self):
        return [CoveringFamilies(self.site_category())]

    def an_object(self):
        target = self.slice_target()
        identity = self.site_category().Mor(target, target).identity()
        return self.family(target, (identity,), {})

    class ParentMethods:
        r"""A finite family admitted by the represented Zariski coverage."""

        def __init__(self, **rest) -> None:
            super().__init__(**rest)
            target_arrow = self.target().arrow()
            scheme = target_arrow.codomain()
            match target_arrow == scheme.categorical_identity_morphism():
                case True:
                    pass
                case False:
                    raise ValueError(
                        f"a Zariski cover of {scheme} must be a family of maps into {scheme} over "
                        f"the identity of {scheme}, but its target is {target_arrow}"
                    )
            embeddings = tuple(
                self.member(index).left()
                for index in self.index_set()
            )
            match all(
                embedding.is_open_immersion() is True
                for embedding in embeddings
            ):
                case True:
                    pass
                case False:
                    raise TypeError(
                        f"a Zariski cover of {scheme} must consist of open immersions, but one of "
                        f"the maps {embeddings} is not an open immersion"
                    )
            match scheme.is_covered_by_open_immersions(embeddings):
                case True:
                    pass
                case False:
                    raise ValueError(
                        f"the open immersions {embeddings} do not cover {scheme}"
                    )

    def _repr_object_names(self):
        return f"finite Zariski covering families of {self.scheme()}"


@cached_function(key=lambda scheme: id(scheme))
def zariski_coverage(scheme) -> Category:
    r"""The represented finite Zariski coverage of ``Sch_R/X``."""

    category = ZariskiCoveringFamilies(scheme)
    return Coverage(category.site_category(), category)


class DistinguishedAffineCovers(OwnedCategory):
    r"""Represented distinguished affine covering families.

    ``DistinguishedAffineCovers()`` is used for category membership without
    fixing the covered scheme. ``DistinguishedAffineCovers(X)`` fixes one
    affine scheme ``X`` and declares ``CoveringFamilies(AffSch_R/X)`` among
    its supercategories. Its objects are distinguished affine covers of
    ``X``. The ``an_object()`` method selects a specimen of the category.
    """

    _MorCategory = DistinguishedAffineCoverMorCategoryConstruction

    @staticmethod
    @cached_function(
        key=lambda cls, scheme=None: (
            cls,
            None if scheme is None else id(scheme),
        )
    )
    def __classcall__(cls, scheme=None):
        match cls:
            case DynamicMetaclass():
                return cls.__base__(scheme)
            case _:
                return typecall(cls, scheme)

    def __init__(self, scheme=None) -> None:
        self._scheme = scheme
        super().__init__()

    def scheme(self):
        return self._scheme

    def site_category(self):
        scheme = self.scheme()
        if scheme is None:
            raise ValueError(
                f"{self} is not attached to one scheme, so it has no single site of affine schemes over it"
            )
        from sage_extensions.categories.schemes.schemes import Schemes

        affine_schemes = Schemes(scheme.scheme_base_ring()).Affine()
        return affine_schemes.SliceOver(scheme)

    def coverage(self):
        scheme = self.scheme()
        if scheme is None:
            raise ValueError(
                f"{self} is not attached to one scheme, so it has no single Zariski coverage"
            )
        return distinguished_affine_coverage(scheme)

    @cached_method
    def slice_target(self):
        r"""The terminal slice object ``id_X`` shared by covers in this fibre."""
        return self.site_category().an_object()

    terminal_site_object = slice_target

    def super_categories(self):
        scheme = self.scheme()
        if scheme is None:
            return [Objects()]
        return [
            DistinguishedAffineCovers(),
            CoveringFamilies(self.site_category()),
        ]

    def an_object(self):
        scheme = self.scheme()
        if scheme is None:
            scheme = RingedSpaces().an_object()
        return scheme.distinguished_open_cover(scheme.coordinate_algebra().one())

    def _repr_object_names(self):
        scheme = self.scheme()
        if scheme is None:
            return "distinguished affine covers"
        return f"distinguished affine covering families of {scheme}"


    def _call_(self, elements):
        r"""Construct ``{D(f_i) -> X}`` through the covering-family entry."""
        scheme = self.scheme()
        assert scheme is not None, (
            f"a cover by distinguished opens D(f_i) is built on one scheme, but {self} is not "
            "attached to a scheme"
        )
        algebra = scheme.coordinate_algebra()
        values = tuple(algebra(element) for element in elements)
        assert values, (
            f"a cover of {scheme} by distinguished opens D(f_i) needs at least one f_i, but none were given"
        )
        assert algebra.ideal(*values).contains_ambient_element(algebra.one()), (
            f"the opens D(f_i) for f_i in {values} do not cover {scheme}: these elements do not "
            f"generate the unit ideal of {algebra}"
        )
        labels = finite_ordered_set(range(len(values)))
        defining_elements = finite_indexed_family(
            labels, lambda label: values[int(labels.ranking_map()(label))],
            name="Defining elements of the distinguished opens",
        )
        site = self.site_category()
        target = self.slice_target()
        opens = finite_indexed_family(
            labels, lambda label: scheme.distinguished_open(defining_elements[label]),
            name="Distinguished opens",
        )
        charts = finite_indexed_family(
            labels, lambda label: site.object(opens[label].inclusion()),
            name="Affine charts over the covered scheme",
        )
        members = finite_indexed_family(
            labels, lambda label: site.Mor(charts[label], target)(opens[label].inclusion()),
            name="Distinguished affine cover arrows",
        )

        def overlap_data(left, right):
            overlap = scheme.distinguished_open(defining_elements[left] * defining_elements[right])
            apex = site.object(overlap.inclusion())
            return site.span(
                site.Mor(apex, charts[left])(overlap.inclusion_into(opens[left])),
                site.Mor(apex, charts[right])(overlap.inclusion_into(opens[right])),
            )

        overlaps = {pair: overlap_data(*pair) for pair in combinations(tuple(labels), 2)}
        return self.family(target, members, overlaps, defining_elements=defining_elements)

    class ParentMethods:
        r"""A cover whose defining elements refine its already constructed family.

        The family owns its target, index set, arrows and overlap spans.
        This level adds only the elements defining its distinguished opens;
        their corresponding family has already been checked at the entry.
        """

        def __init__(self, defining_elements, **rest) -> None:
            self._defining_elements = defining_elements
            super().__init__(**rest)
            assert defining_elements.index_set() is self.index_set(), (
                f"the elements f_i defining the opens D(f_i) of {self.ambient_scheme()} are indexed by "
                f"{defining_elements.index_set()}, but the charts are indexed by {self.index_set()}"
            )

        def defining_data_decision(self):
            r"""Return the retained decision that the selected family is ``{D(f_i) -> X}``."""
            scheme = self.ambient_scheme()
            algebra = scheme.coordinate_algebra()
            return conjunction((
                self.target().arrow() == scheme.categorical_identity_morphism(),
                algebra.ideal(*self.defining_elements()).contains_ambient_element(algebra.one()),
                conjunction(
                    self.open(label)
                    is scheme.distinguished_open(self.defining_element(label))
                    for label in self.index_set()
                ),
            ))

        @validator
        def validate_defining_data(self):
            r"""Reject only a proved mismatch between the cover and its defining elements."""
            decision = self.defining_data_decision()
            if decision is False:
                raise ValueError(
                    f"{self} does not realize its retained distinguished-open data as a cover of "
                    f"{self.ambient_scheme()}"
                )
            return decision

        def _cache_key(self) -> int:
            return id(self)

        def ambient_scheme(self):
            r"""The affine scheme ``X`` this is a cover of."""
            return self.target().arrow().codomain()

        def defining_elements(self):
            return self._defining_elements

        def defining_element(self, index):
            r"""``f_i``, the element whose distinguished open is the chart at ``index``."""
            return self._defining_elements[self.chart_label(index)]

        def opens(self):
            return finite_indexed_family(
                self.atlas(),
                self.open,
                name="Distinguished affine opens",
            )

        def atlas(self):
            r"""The set the charts are indexed by, and the only source of chart labels."""
            return self.index_set()

        def chart_label(self, index):
            r"""Read ``index`` as a label of this cover's atlas."""
            return self.atlas()(index)

        def chart_position(self, index):
            r"""Where the chart at ``index`` sits in the atlas order."""
            return int(self.atlas().ranking_map()(self.chart_label(index)))

        def open(self, index):
            r"""``D(f_i)``, the chart at ``index``."""
            return self.member(self.chart_label(index)).domain().arrow().domain()

        def intersection_indices(self, *indices):
            r"""Read the stated chart labels, deduplicated and in the atlas order."""
            labels = {self.chart_label(index) for index in indices}
            assert labels, (
                f"an intersection of charts of {self} needs at least one chart, but none were named"
            )
            return finite_ordered_set(
                tuple(sorted(labels, key=self.atlas().ranking_map()))
            )

        def intersection(self, *indices):
            r"""Return ``D(prod_i f_i)``, the intersection of the selected charts."""
            return self._intersection_of_labels(self.intersection_indices(*indices))

        @cached_method
        def _intersection_of_labels(self, labels):
            match len(labels):
                case 1:
                    return self.open(labels[0])
                case _:
                    element = self.ambient_scheme().coordinate_algebra().one()
                    for label in labels:
                        element *= self.defining_element(label)
                    return self.ambient_scheme().distinguished_open(element)

        def overlap(self, left_index, right_index):
            return self.intersection(left_index, right_index)

        def structure_sheaf_restriction(self, chart_index, other_index):
            r"""``O(U_i) -> O(U_i cap U_j)``."""
            return self.ambient_scheme().structure_sheaf().restriction_map(
                self.open(chart_index),
                self.overlap(chart_index, other_index),
            )

        @cached_method
        def restrict_module(self, module, chart_index, *intersection_indices):
            r"""Return ``M_i|_{U_I}`` by scalar extension along ``O(U_i) -> O(U_I)``.

            A local algebra restricted as a module is the restricted algebra, so
            forgetting algebra structure does not construct a second scalar
            extension.
            """
            from sage_extensions.categories.algebras.algebras import Algebras

            chart = self.open(chart_index)
            chart_ring = chart.coordinate_algebra()
            assert module.base_ring() is chart_ring, (
                f"the module {module} on chart {chart_index} must be a module over its coordinate "
                f"ring {chart_ring}, but it is a module over {module.base_ring()}"
            )
            target = self.intersection(chart_index, *intersection_indices)
            match module:
                case _ if target is chart:
                    return module
                case _ if module in Algebras(chart_ring).Associative().Unital():
                    return self.restrict_algebra(module, chart_index, *intersection_indices)
                case _:
                    ring_map = self.ambient_scheme().structure_sheaf().restriction_map(chart, target)
                    restricted = module.base_change(ring_map)
                    assert restricted.base_ring() is target.coordinate_algebra(), (
                        f"the restriction of {module} to {target} is a module over "
                        f"{restricted.base_ring()}, not over {target.coordinate_algebra()}"
                    )
                    return restricted

        @cached_method
        def restrict_algebra(self, algebra, chart_index, *intersection_indices):
            r"""Return ``A_i|_{U_I}`` by algebra scalar extension along ``O(U_i) -> O(U_I)``."""
            from sage_extensions.categories.algebras.algebras import Algebras

            chart = self.open(chart_index)
            chart_ring = chart.coordinate_algebra()
            assert algebra in Algebras(chart_ring).Associative().Unital(), (
                f"the algebra {algebra} on chart {chart_index} must be an algebra over its "
                f"coordinate ring {chart_ring}, but it is in {algebra.category()}"
            )
            target = self.intersection(chart_index, *intersection_indices)
            if target is chart:
                return algebra
            ring_map = self.ambient_scheme().structure_sheaf().restriction_map(chart, target)
            restricted = Algebras(chart_ring).Associative().Unital().scalar_extension(ring_map)(algebra)
            assert restricted in Algebras(target.coordinate_algebra()).Associative().Unital(), (
                f"the restriction of {algebra} to {target} is not an algebra over "
                f"{target.coordinate_algebra()}; it is in {restricted.category()}"
            )
            return restricted

        def glue_modules(self, local_modules, transitions):
            r"""Return the glued module sheaf on this affine cover."""

            from sage_extensions.categories.schemes.gluing import ModuleGluingData

            return ModuleGluingData(self)(local_modules, transitions).sheaf()

        def glue_algebras(self, local_algebras, transitions):
            r"""Return the glued algebra sheaf on this affine cover."""
            from sage_extensions.categories.schemes.gluing import AlgebraGluingData

            return AlgebraGluingData(self)(local_algebras, transitions).sheaf()

        def common_refinement(self, other):
            r"""The span of refinements from ``{D(f_i g_j)}`` to these two covers.

            The returned object is a categorical span in this cover category.
            Its apex is the common refinement; its two legs are actual
            :class:`DistinguishedAffineCoverRefinement` morphisms.
            """
            assert other.ambient_scheme() is self.ambient_scheme(), (
                f"a common refinement needs two covers of one scheme, but {self} covers "
                f"{self.ambient_scheme()} and {other} covers {other.ambient_scheme()}"
            )
            category = self.category()
            index_pairs = tuple(
                (left, right)
                for left in self.atlas()
                for right in other.atlas()
            )
            fine = category(
                tuple(
                    self.defining_element(left) * other.defining_element(right)
                    for left, right in index_pairs
                )
            )
            site = self.site_category()

            def refinement_to(coarse, which):
                index_map = {
                    fine_index: index_pairs[fine.chart_position(fine_index)][which]
                    for fine_index in fine.atlas()
                }
                components = {}
                for fine_index in fine.atlas():
                    coarse_index = index_map[fine_index]
                    inclusion = fine.open(fine_index).inclusion_into(
                        coarse.open(coarse_index)
                    )
                    components[fine_index] = site.Mor(
                        fine.member(fine_index).domain(),
                        coarse.member(coarse_index).domain(),
                    )(inclusion)
                return category.Mor(fine, coarse)(index_map, components)

            return category.span(
                refinement_to(self, 0),
                refinement_to(other, 1),
            )

        def _repr_(self):
            return f"Distinguished affine cover of {self.ambient_scheme()} by {self.atlas().cardinality()} opens"


@cached_function(key=lambda scheme: id(scheme))
def distinguished_affine_coverage(scheme) -> Category:
    r"""The distinguished-open coverage in ``AffSch_R/X``."""

    category = DistinguishedAffineCovers(scheme)
    return Coverage(
        category.site_category(),
        category,
    )


class _AffineModuleSheafEngine:
    r"""The quasi-coherent sheaf ``M~`` on the represented distinguished-open basis."""

    def __init__(self, scheme, module, **rest) -> None:
        algebra = scheme.coordinate_algebra()
        if module.base_ring() is not algebra:
            raise ValueError(
                f"the sheaf M~ on {scheme} needs a module M over its coordinate ring {algebra}, but "
                f"{module} is a module over {module.base_ring()}"
            )
        self._scheme = scheme
        self._module = module
        self._local_sections = {}
        super().__init__(**rest)

    def ringed_space(self):
        return self._scheme

    scheme = ringed_space

    def module(self):
        return self._module

    def global_sections(self):
        return self.module()

    def geometric_cohomology_complex(self, cover=None):
        r"""Return the affine Čech complex computing this sheaf's cohomology."""
        from sage_extensions.categories.schemes.geometric_cohomology import (
            _affine_geometric_cohomology_complex,
        )

        return _affine_geometric_cohomology_complex(self, cover=cover)

    def geometric_scalar_cohomology_map(self, degree, scalar, *, cover=None):
        r"""Return the cohomology map induced by scalar multiplication."""
        from sage_extensions.categories.schemes.geometric_cohomology import (
            _affine_geometric_scalar_cohomology_map,
        )

        return _affine_geometric_scalar_cohomology_map(
            self,
            degree,
            scalar,
            cover=cover,
        )

    def stalk(self, point):
        r"""``M~_p = M_p``, the module localized at the prime of the point."""
        spectrum = self.scheme().underlying_space()
        assert point.parent() is spectrum, (
            f"the stalk of {self} is taken at a point of the spectrum of {self.scheme()}, but "
            f"{point} is a point of {point.parent()}"
        )
        return self.module().localize_at_prime(point.ideal())

    def sections_on_distinguished_open(self, distinguished_open):
        if not _is_distinguished_open_of(distinguished_open, self.scheme()):
            raise ValueError(
                f"the sections of {self} are computed on distinguished opens D(f) of {self.scheme()}, "
                f"but {distinguished_open} is not one of them"
            )
        key = id(distinguished_open)
        selected = self._local_sections.get(key)
        if selected is not None and selected.base_ring() is distinguished_open.coordinate_algebra():
            return selected
        section_ring = self.scheme().structure_sheaf().sections_on_distinguished_open(
            distinguished_open
        )
        selected = section_ring.localize_module(self.module())
        self._local_sections[key] = selected
        return selected

    def restriction_map(self, source_open, target_open):
        r"""Return the module restriction, linear over the structure-sheaf restriction."""


        ambient = self.scheme()
        structure_restriction = ambient.structure_sheaf().restriction_map(
            source_open,
            target_open,
        )
        source_sections = (
            self.global_sections()
            if source_open is ambient
            else self.sections_on_distinguished_open(source_open)
        )
        if target_open is ambient and source_open is ambient:
            return source_sections.module_category().Mor(source_sections, source_sections).identity()
        target_sections = (
            self.global_sections()
            if target_open is ambient
            else self.sections_on_distinguished_open(target_open)
        )

        if source_open is ambient:
            localization = target_sections.localization_functor()
            if localization.ring_map() is not structure_restriction:
                raise ArithmeticError(
                    f"restriction of {self} to {target_open} localizes along "
                    f"{localization.ring_map()}, but restriction of functions uses "
                    f"{structure_restriction}; they must agree"
                )
            return localization.unit(self.module(), localized=target_sections)
        if source_open is target_open:
            return source_sections.module_category().Mor(source_sections, source_sections).identity()

        restricted_target = target_sections.restrict_scalars(structure_restriction)
        source_ring = source_sections.base_ring()
        original_ring = source_ring.localization_source()

        def restrict(section):
            section = source_sections(section)
            inverse_denominator = structure_restriction(
                source_ring.fraction(original_ring.one(), section.denominator())
            )
            target_value = target_sections.scalar_multiple(
                inverse_denominator,
                section.numerator()
                if target_open is ambient
                else target_sections.fraction(section.numerator()),
            )
            return restricted_target.wrap(target_value)

        # The restriction of a localized module along the localization of its
        # ring is linear over the source ring, so the construction alone gives
        # linearity.
        return source_sections.module_category().Mor(
            source_sections, restricted_target
        )._from_constructed_element_map(restrict)

    def sheaf_category(self):
        r"""``QCoh(X)``, the category this sheaf is an object of."""
        return QuasiCoherentSheaves(self.scheme())

    def _repr_(self):
        return f"Affine module sheaf associated to {self.module()} on {self.scheme()}"


class _ModuleOpenPresheaf(Functor):
    r"""Additive sections computed by one represented module sheaf.

    The whole-space value uses its global sections. A basis realization
    supplies the other open schemes at which its restrictions are computed.
    """

    def __init__(self, scheme, sheaf) -> None:
        from sage_extensions.categories.group.magmas import AdditiveGroups

        self._scheme = scheme
        self._sheaf = sheaf
        super().__init__(
            scheme.open_subsets_site().opposite(),
            AdditiveGroups().AdditiveCommutative(),
        )

    def _open_scheme(self, opposite_object):
        subset = opposite_object.underlying_object().value()
        opens = self.domain().base_category().object_set()
        if subset is opens.inclusion().codomain().top():
            return self._scheme
        assert False, (
            f"sections of the module sheaf on {subset}: not implemented; "
            "the open's traces on its affine charts are not represented"
        )

    def _apply_object(self, opposite_object):
        if _is_empty_open(self, opposite_object):
            # A module sheaf has one empty-open section (Stacks, Tag 04B3).
            return self._scheme.scheme_base_ring().free_module(0).underlying_additive_group()
        open_scheme = self._open_scheme(opposite_object)
        sheaf = self._sheaf()
        module = (
            sheaf.global_sections()
            if open_scheme is self._scheme
            else sheaf.sections_on_distinguished_open(open_scheme)
        )
        return module.underlying_additive_group()

    def _apply_morphism(self, opposite_arrow):
        if _is_empty_open(self, opposite_arrow.domain()) or _is_empty_open(self, opposite_arrow.codomain()):
            return self.codomain().Mor(
                self(opposite_arrow.domain()), self(opposite_arrow.codomain()),
            ).zero()
        source_open = self._open_scheme(opposite_arrow.domain())
        target_open = self._open_scheme(opposite_arrow.codomain())
        if source_open is target_open:
            sections = self(opposite_arrow.domain())
            return self.codomain().Mor(sections, sections).identity()
        restriction = self._sheaf().restriction_map(
            source_open, target_open,
        )
        return restriction.domain().module_category().underlying_additive_group_functor()(
            restriction
        )


class _AffineModuleOpenPresheaf(_ModuleOpenPresheaf):
    r"""The additive sections of ``M~`` on ``Spec A`` and its basis opens.

    Values and restrictions use the associated sheaf's localization operations
    (Stacks, Tag 01I8). Forgetting scalars sends the restriction
    ``M -> Res(A_f, M_f)`` to its additive map ``M -> M_f``.
    """

    def _open_scheme(self, opposite_object):
        from sage_extensions.categories.rings.commutative_algebra import (
            DistinguishedOpenSubobjects,
        )

        subset = opposite_object.underlying_object().value()
        spectrum = self._scheme.underlying_space()
        if subset in DistinguishedOpenSubobjects(spectrum):
            return self._scheme.distinguished_open(subset.function())
        return super()._open_scheme(opposite_object)


class QuasiCoherentSheafMorphismMethods:
    r"""Operations defined on every represented quasi-coherent sheaf arrow."""

    def _kernel_quasi_coherent_sheaf(self):
        assert False, (
            f"the kernel of {self} is a quasi-coherent sheaf, but the current realization "
            f"{type(self).__name__} supplies no kernel computation"
        )

    def _cokernel_quasi_coherent_sheaf(self):
        assert False, (
            f"the cokernel of {self} is a quasi-coherent sheaf, but the current realization "
            f"{type(self).__name__} supplies no cokernel computation"
        )

    def kernel(self):
        return self._kernel_quasi_coherent_sheaf()

    def cokernel(self):
        return self._cokernel_quasi_coherent_sheaf()

    def projectivization_map(self):
        r"""Return the induced projectivization map on the quotient-surjectivity locus."""
        from sage_extensions.categories.schemes.relative_proj import (
            _projectivization_map,
        )

        return _projectivization_map(self)


class QuasiCoherentSheafMor(CategoricalMor):
    ElementMethods = QuasiCoherentSheafMorphismMethods


class AffineQuasiCoherentSheafMorphismMethods:
    r"""A morphism of affine quasi-coherent sheaves, represented by its module map."""

    def __init__(self, parent, module_morphism) -> None:
        source_module = parent.domain().module()
        target_module = parent.codomain().module()
        self._underlying_module_morphism = source_module.module_category().Mor(
            source_module,
            target_module,
        )(module_morphism)
        super().__init__(parent)

    def underlying_module_morphism(self):
        return self._underlying_module_morphism

    def _kernel_quasi_coherent_sheaf(self):
        category = QuasiCoherentSheaves(self.domain().scheme())
        return category.associated_sheaf(self.underlying_module_morphism().kernel())

    def _cokernel_quasi_coherent_sheaf(self):
        category = QuasiCoherentSheaves(self.domain().scheme())
        return category.associated_sheaf(self.underlying_module_morphism().cokernel())

    def _richcmp_(self, other, op):
        r"""Compare through the affine equivalence without collapsing unknown equality."""
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if not isinstance(other, AffineQuasiCoherentSheafMorphismMethods) or other.parent() is not self.parent():
            return op == op_NE
        equal = self.underlying_module_morphism() == other.underlying_module_morphism()
        return equal if op == op_EQ else negation(equal)

    def __eq__(self, other):
        return self._richcmp_(other, op_EQ)

    def __ne__(self, other):
        return self._richcmp_(other, op_NE)

    def __mul__(self, other):
        if not isinstance(other, AffineQuasiCoherentSheafMorphismMethods):
            return NotImplemented
        if other.codomain() is not self.domain():
            return NotImplemented
        return self.parent().mor_category().Mor(
            other.domain(),
            self.codomain(),
        )(
            self.underlying_module_morphism()
            * other.underlying_module_morphism()
        )


class AffineQuasiCoherentSheafMorphism(
    AffineQuasiCoherentSheafMorphismMethods,
    QuasiCoherentSheafMorphismMethods,
    Morphism,
):
    r"""Compatibility shell for private affine QCoh-arrow realizations."""


class AffineQuasiCoherentSheafMor(QuasiCoherentSheafMor):
    r"""``Hom_{O_X}(M~,N~)`` on affine ``X``, with sheaf endpoints."""

    ElementMethods = AffineQuasiCoherentSheafMorphismMethods

    def _element_constructor_(self, module_morphism):
        match module_morphism:
            case AffineQuasiCoherentSheafMorphismMethods() if module_morphism.parent() is self:
                return module_morphism
            case AffineQuasiCoherentSheafMorphismMethods():
                raise TypeError(f"{module_morphism} belongs to another Mor; apply the functor between the categories")
            case _:
                pass
        return self.element_class(self, module_morphism)

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"there is no identity morphism from {self.domain()} to the different sheaf "
                f"{self.codomain()}; the identity exists only when domain and codomain agree"
            )
        module = self.domain().module()
        return self(module.module_category().Mor(module, module).identity())


class QuasiCoherentSheafMorCategoryConstruction(MorCategoryConstruction):
    r"""Choose the represented Mor realization from the sheaves' defining presentations."""

    def fixed_category_class_for(self, domain, codomain):
        category = self.base_category()
        scheme = category.scheme()

        from sage_extensions.categories.schemes.relative_proj import (
            RelativeProjectivizationQuasiCoherentMor,
            RelativeProjectivizations,
        )

        match scheme in RelativeProjectivizations(scheme.scheme_base_ring()):
            case True:
                from sage_extensions.categories.schemes.gluing import (
                    _finite_atlas_sheaf_placement,
                )

                match (
                    _finite_atlas_sheaf_placement(domain),
                    _finite_atlas_sheaf_placement(codomain),
                ):
                    case (None, _) | (_, None):
                        return RelativeProjectivizationQuasiCoherentMor
                    case _:
                        pass
            case False:
                pass

        trivialized = category.Invertible().WithChosenTrivialization()
        match (domain in trivialized, codomain in trivialized):
            case (True, True):
                from sage_extensions.categories.divisors.invertible_sheaves import (
                    _ChosenTrivializationQuasiCoherentMor,
                )

                return _ChosenTrivializationQuasiCoherentMor
            case _:
                pass

        invertible = category.Invertible()
        match (domain in invertible, codomain in invertible):
            case (True, True):
                from sage_extensions.categories.divisors.invertible_sheaves import (
                    _PullbackLineBundleQuasiCoherentMor,
                )

                return _PullbackLineBundleQuasiCoherentMor
            case _:
                pass

        from sage_extensions.categories.schemes.schemes import Schemes

        affine = Schemes(scheme.scheme_base_ring()).Affine()
        match scheme in affine:
            case True:
                return AffineQuasiCoherentSheafMor
            case False:
                from sage_extensions.categories.schemes.gluing import (
                    FiniteAtlasModuleSheafMor,
                    _finite_atlas_of_sheaf_placement,
                    _finite_atlas_quasi_coherent_sheaves,
                )

                atlas = _finite_atlas_of_sheaf_placement(domain)
                represented = _finite_atlas_quasi_coherent_sheaves(atlas)
                assert domain.category().is_subcategory(represented), (
                    f"morphisms out of the sheaf {domain} on the non-affine scheme {scheme} are "
                    f"computed on the affine cover {atlas}, but {domain} is not given on that cover"
                )
                assert codomain.category().is_subcategory(represented), (
                    f"morphisms from {domain} to {codomain} are computed on the affine cover "
                    f"{atlas} of {scheme}, but {codomain} is not given on that cover"
                )
                return FiniteAtlasModuleSheafMor


class QuasiCoherentSheaves(CategoryPacketMethods, OwnedParameterizedCategory):
    r"""Quasi-coherent ``O_X``-modules on one scheme ``X``.

    On an affine ``X = Spec A`` the association ``M |-> M~`` is an equivalence
    onto this category, inverse to global sections (Stacks, Tag 01I8).  The
    represented affine operations are therefore read through ``Modules(A)``
    rather than defined a second time.  For the
    same reason a morphism of quasi-coherent sheaves on an affine scheme is
    determined by a morphism of the two modules.  The represented sheaf arrow
    retains the sheaves themselves as categorical endpoints and stores that
    module map as its affine realization.

    On a non-affine represented scheme, quasi-coherent sheaves are carried by
    the finite-atlas/descent objects in ``schemes.gluing``.  The affine
    equivalence methods below deliberately retain their affine assertion;
    placement in this category no longer means that every object has one
    global coordinate-algebra presentation.
    """

    def scheme(self):
        return self.base()

    def _repr_object_names(self):
        return f"quasi-coherent sheaves on {self.scheme()}"

    def super_categories(self):
        return [ModuleSheaves(self.scheme())]

    def an_object(self):
        return self.scheme().structure_sheaf()

    _MorCategory = QuasiCoherentSheafMorCategoryConstruction

    class ParentMethods:
        @cached_method
        def projectivization(self):
            r"""Return ``P_quot(F) = Proj_X(Sym(F))`` with its universal quotient."""
            from sage_extensions.categories.schemes.relative_proj import (
                _projectivization,
            )

            return _projectivization(self)

        def projectivization_base_change(self, ring_map):
            r"""Return the represented base-change comparison for ``P_quot(self)``."""
            return self.projectivization().arrow().domain().projectivization_base_change(
                ring_map
            )

    def object(self, *, categories=(), construction_data=None, _engine, open_sections_presheaf=None):
        r"""Construct one represented quasi-coherent sheaf through this owner.

        ``_engine`` is the private realization of the sheaf in the represented
        regime selected by the caller.  Stronger semantic placement is joined
        here so specializations do not initialize a second ``Parent`` shell.
        """
        if open_sections_presheaf is None:
            fibre, presheaf_data = _unpresented_sheaf_placement(
                self.scheme(), f"a quasi-coherent sheaf on {self.scheme()}", self
            )
        else:
            fibre, presheaf_data = _open_sheaf_placement(
                self.scheme(), open_sections_presheaf, self
            )
        return _object_of(
            owned_category_join((self, fibre, *tuple(categories))),
            _engine=(self, _engine, None),
            **presheaf_data,
            **dict(construction_data or {}),
        )

    class SubcategoryMethods:
        def Invertible(self):
            r"""Return the full subcategory of invertible ``O_X``-modules."""
            return self._with_axiom("Invertible")

        def FiniteLocallyFree(self):
            r"""Return the full subcategory of locally free ``O_X``-modules of finite rank.

            ``F`` is locally free of finite rank when ``X`` has an open cover by
            sets ``U`` with ``F|_U`` isomorphic to ``O_U^{n_U}``, ``n_U`` finite
            (Hartshorne, *Algebraic Geometry*, II.5).  These are the vector
            bundles on ``X``.
            """
            return self._with_axiom("FiniteLocallyFree")

    class FiniteLocallyFree(CategoryWithAxiom):
        r"""Locally free ``O_X``-modules of finite rank: the vector bundles on ``X``.

        Local freeness is a property of the sheaf; a trivializing cover is
        additional data.
        """

        def _repr_object_names(self):
            return f"vector bundles on {self.base_category().scheme()}"

    class Invertible(CategoryWithAxiom):
        r"""Invertible quasi-coherent sheaves on ``X``.

        Schemes are locally ringed spaces, so an invertible ``O_X``-module is
        equivalently a locally free ``O_X``-module of rank one (Stacks,
        Tag 0B8M).  A particular trivializing cover is additional data and is
        recorded separately by the line-bundle descent category.
        """

        def extra_super_categories(self):
            r"""An invertible ``O_X``-module is locally free of rank one (Stacks, Tag 0B8M)."""
            return [self.base_category().FiniteLocallyFree()]

        class ParentMethods:
            def is_invertible(self) -> bool:
                return True

        def WithChosenTrivialization(self):
            r"""Return invertible sheaves carrying one selected trivializing cover."""
            return InvertibleSheavesWithChosenTrivialization(self.base_category().scheme())

    def module_category(self):
        r"""``Modules(A)``: the category this one is equivalent to, for affine ``X``."""
        from sage_extensions.categories.modules.pure.modules import Modules
        from sage_extensions.categories.schemes.schemes import Schemes

        scheme = self.scheme()
        assert scheme in Schemes(scheme.scheme_base_ring()).Affine(), (
            f"quasi-coherent sheaves on X are equivalent to modules over one ring only for affine "
            f"X, but {scheme} is in {scheme.category()}"
        )
        return Modules(scheme.coordinate_algebra())

    @cached_method(key=lambda self, module: id(module))
    def associated_sheaf(self, module):
        r"""``M |-> M~``, the equivalence out of ``Modules(A)``."""
        assert module in self.module_category(), (
            f"the sheaf M~ on {self.scheme()} is defined for a module over its coordinate ring, "
            f"but {module} is in {module.category()}"
        )
        presheaf = _AffineModuleOpenPresheaf(self.scheme(), lambda: sheaf)
        sheaf = self.object(
            construction_data={"scheme": self.scheme(), "module": module},
            _engine=_AffineModuleSheafEngine,
            open_sections_presheaf=presheaf,
        )
        return sheaf

    def global_sections(self, sheaf):
        r"""``M~ |-> M``, the inverse equivalence."""
        assert sheaf in self, (
            f"{sheaf} is not a quasi-coherent sheaf on {self.scheme()}; it is in {sheaf.category()}"
        )
        return sheaf.global_sections()

    def local_presentation(self, sheaf):
        r"""``O_X^m -> O_X^n``, the presentation whose cokernel is ``F``.

        A finitely presented module has a chosen relation morphism between
        free modules, and the equivalence reads it as a morphism of free
        ``O_X``-modules; the hypothesis is exactly that chosen presentation,
        which is what makes the sheaf coherent on this affine chart.
        """
        from sage_extensions.categories.modules.pure.modules import (
            ModulesWithChosenFinitePresentation,
        )

        module = self.global_sections(sheaf)
        assert module in ModulesWithChosenFinitePresentation(module.base_ring()), (
            f"an exact sequence O^m -> O^n -> {sheaf} -> 0 needs the module of global sections to "
            f"be given by finitely many generators and relations, but {module} is in {module.category()}"
        )
        return module.presentation()


class InvertibleSheavesWithChosenTrivialization(OwnedParameterizedCategory):
    r"""Invertible sheaves on ``X`` with one selected trivializing affine cover.

    The choice of cover is structure on an invertible sheaf, not part of the
    invertibility property.  Forgetting that choice lands in
    ``QuasiCoherentSheaves(X).Invertible()``.
    """

    def scheme(self):
        return self.base()

    def super_categories(self):
        return [QuasiCoherentSheaves(self.scheme()).Invertible()]

    def _repr_object_names(self):
        return f"invertible sheaves on {self.scheme()} with a chosen trivialization"

    def _realize(self, engine, **construction_data):
        r"""Realize one represented trivialization through the quasi-coherent sheaf owner."""
        from sage_extensions.categories.divisors.invertible_sheaves import (
            _FiniteAtlasLineBundleOpenPresheaf,
        )

        presheaf = _FiniteAtlasLineBundleOpenPresheaf(self.scheme(), lambda: sheaf)
        sheaf = QuasiCoherentSheaves(self.scheme()).object(
            categories=(self,),
            construction_data=construction_data,
            _engine=engine,
            open_sections_presheaf=presheaf,
        )
        return sheaf

    def _call_(
        self,
        gluing_datum,
        transition_units=None,
        *,
        section_space=None,
        associated_divisor=None,
    ):
        r"""Construct an invertible sheaf from rank-one affine descent data.

        A distinguished-cover module descent datum already contains its
        transition isomorphisms.  A finite affine atlas supplies the equivalent
        rank-one datum by its transition units.
        """
        assert gluing_datum.scheme() is self.scheme(), (
            f"an invertible sheaf on {self.scheme()} must be glued on a cover of {self.scheme()}, "
            f"but the gluing data is on a cover of {gluing_datum.scheme()}"
        )
        match transition_units:
            case None:
                assert section_space is None and associated_divisor is None, (
                    "a space of global sections or an associated divisor can be given only with "
                    "transition units on a finite affine cover, but no transition units were given"
                )
                from sage_extensions.categories.divisors.invertible_sheaves import (
                    _DistinguishedCoverInvertibleSheafEngine,
                )

                return gluing_datum.sheaf(
                    categories=(self,),
                    construction_data={"gluing_datum": gluing_datum},
                    _engine=_DistinguishedCoverInvertibleSheafEngine,
                )
            case _:
                from sage_extensions.categories.divisors.invertible_sheaves import (
                    _FiniteAtlasInvertibleSheafEngine,
                )

                return self._realize(
                    _FiniteAtlasInvertibleSheafEngine,
                    gluing_datum=gluing_datum,
                    transition_units=transition_units,
                    section_space=section_space,
                    associated_divisor=associated_divisor,
                )

    def trivial(self, cover):
        r"""Return ``O_X`` with the selected distinguished affine trivialization ``cover``."""
        from sage_extensions.categories.schemes.gluing import ModuleGluingData

        assert cover.ambient_scheme() is self.scheme(), (
            f"the structure sheaf of {self.scheme()} is trivialized on a cover of it, but "
            f"{cover} is a cover of {cover.ambient_scheme()}"
        )
        return self(ModuleGluingData(cover).an_object())

    class ParentMethods:
        def trivializing_cover(self):
            r"""Return the selected affine cover on which this line bundle is trivialized."""
            return self.cover()


class RingedSpaces(CategoryPacketMethods, OwnedCategory):
    r"""Ringed spaces ``(X,O_X)``."""

    def an_object(self):
        r"""The affine ringed space ``Spec(ZZ)``."""
        from sage.rings.integer_ring import ZZ as SageZZ

        from sage_extensions.categories.rings.ring_foundation import (
            _own_ring,
            _owned_integers,
        )
        return (_owned_integers()).affine_spectrum()

    @classmethod
    def _repr_object_names(cls):
        return "ringed spaces"

    def super_categories(self):
        return [SheafedSpaces()]

    def LocallyRinged(self):
        return LocallyRingedSpaces()

    class ParentMethods:
        @cached_method
        def structure_sheaf(self):
            return _structure_sheaf(self)

        @cached_method
        def picard_group(self):
            r"""Return the Picard group of this ringed space.

            Mathematically ``Pic(X)`` is the abelian group of isomorphism
            classes of invertible ``O_X``-modules under tensor product, so the
            operation belongs to ringed spaces.  Descendant categories supply
            private computational specializations.
            """
            return self._picard_group()

        def _picard_group(self):
            r"""Invertible sheaf classes under tensor product (Hartshorne, II.6.12)."""
            from sage_extensions.categories.divisors.picard_groups import (
                _invertible_sheaf_class_group,
            )

            return _invertible_sheaf_class_group(self, self.structure_sheaf())

        @cached_method
        def cartier_divisor_sheaf(self):
            r"""Return the quotient sheaf ``K_X^*/O_X^*``.

            Here ``K_X`` is the sheaf of total quotient rings.  Cartier
            divisors are the global sections of this quotient sheaf (Stacks
            Project, Tag 02AQ).
            """
            from sage_extensions.categories.divisors.cartier_divisor_groups import (
                _cartier_divisor_quotient_sheaf,
            )

            return _cartier_divisor_quotient_sheaf(self)

        @cached_method
        def cartier_divisor_group(self):
            r"""Return ``CDiv(X)=Gamma(X,K_X^*/O_X^*)``."""
            return self.cartier_divisor_sheaf().global_sections()


class LocallyRingedMorCategoryConstruction(MorCategoryConstruction):
    r"""The Mor of locally ringed spaces, realized by the domain's presentation.

    An affine scheme is determined by its ring, and maps out of a glued
    scheme by compatible maps out of its charts (Stacks, Tags 01I1, 01JA).
    Those presentations choose the arrow engine, not another Mor object.
    """

    def fixed_category_class_for(self, domain, codomain):
        return domain._locally_ringed_mor_class()


class LocallyRingedSpaces(CategoryPacketMethods, OwnedCategory):
    r"""Ringed spaces whose stalks are local rings."""

    _MorCategory = LocallyRingedMorCategoryConstruction

    def an_object(self):
        r"""The locally ringed affine scheme ``Spec(ZZ)``."""
        return RingedSpaces().an_object()

    @classmethod
    def _repr_object_names(cls):
        return "locally ringed spaces"

    def super_categories(self):
        return [RingedSpaces()]

    class ParentMethods:
        def _locally_ringed_mor_class(self):
            r"""The arrow class of ``Mor(X, Y)`` in locally ringed spaces.

            A morphism of locally ringed spaces is a continuous map with a
            local map of sheaves of rings (Stacks, Tag 01HA).  A space whose
            presentation computes no such maps has the general Mor; a scheme
            refines this by its affine or gluing presentation.
            """
            return FixedMorCategory

        def stalk(self, point):
            return self.structure_sheaf().stalk(point)

        def covering_family(
            self,
            charts,
            embeddings,
            overlaps,
            *,
            ambient_chart_index,
        ):
            r"""Return the represented covering family in ``LRS/X``.

            The currently represented covering certificate contains this
            ambient space as one chart embedded by ``id_X``.  Non-affine
            overlaps remain slice objects with both overlap legs; they are not
            replaced by spectra of global sections.

            Unverified specimen: the overlap itself is the apex of the owned
            overlap span, not a private overlap record::

                sage: from dzack_research.preamble.all import QQ, AffineSpaces
                sage: plane = AffineSpaces(QQ)(2, names=("x", "y"))
                sage: x, y = plane.coordinate_algebra().algebra_generators()
                sage: punctured = plane.closed_subscheme(x, y).open_complement()
                sage: cover = plane.covering_family(
                ....:     {"whole": plane, "punctured": punctured},
                ....:     {"whole": plane.categorical_identity_morphism(), "punctured": punctured.inclusion()},
                ....:     {("whole", "punctured"): (punctured, punctured.inclusion(), punctured.categorical_identity_morphism())},
                ....:     ambient_chart_index="whole",
                ....: )
                sage: overlap = cover.overlap_span("whole", "punctured")
                sage: overlap.apex().arrow().domain() is punctured
                True
            """
            from sage_extensions.categories.schemes.covering_families import (
                _ringed_covering_family,
            )

            site = LocallyRingedSpaces().SliceOver(self)
            return _ringed_covering_family(
                self,
                site,
                charts,
                embeddings,
                overlaps,
                ambient_chart_index=ambient_chart_index,
            )


__all__ = [
    "AlgebraSheaves",
    "DistinguishedAffineCoverRefinement",
    "DistinguishedAffineCovers",
    "distinguished_affine_coverage",
    "LocallyRingedSpaces",
    "ModuleSheaves",
    "QuasiCoherentSheaves",
    "RingedSpaces",
    "SheafObjects",
    "SheafedSpaces",
    "ZariskiCoveringFamilies",
    "zariski_coverage",
]
