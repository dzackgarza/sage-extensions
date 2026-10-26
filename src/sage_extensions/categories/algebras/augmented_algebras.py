"""Algebras equipped with an augmentation morphism to the base ring."""

from sage.categories.map import Map
from sage.categories.morphism import Morphism
from sage.misc.cachefunc import cached_method

from sage_extensions.categories.abstract_categories.mor_foundation import CategoricalArrow
from sage_extensions.categories.abstract_categories.arrow_categories import (
    CommutativeSquare, SliceCategory, SliceMorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.abstract_categories.mor_categories import CategoricalMor

from sage_extensions.categories.algebras.algebras import (
    Algebras,
    MultiplicativeAlgebraMorphism,
    UnitalMultiplicativeAlgebraMor,
    UnitalMultiplicativeAlgebraMorphism,
    _algebra_on_module,
    _root_algebra_law_decisions,
    _scalar_module,
)
from sage_extensions.categories.algebras.free_algebras import (
    AlternatingAlgebras,
    DividedPowerAlgebras,
    FreeAlgebras,
    GradedFreeAlgebras,
    SymmetricAlgebras,
    TensorAlgebras,
)
from sage_extensions.categories.algebras.graded_algebras import (
    GradedAlgebraMor, GradedAlgebras,
)
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedRings,
    _owned_ring,
)
from sage_extensions.logic import conjunction
from sage_extensions.validation import validator
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


def AugmentedAlgebras(base_ring):
    r"""Return the canonical slice of associative unital ``R``-algebras over ``R``.

    An object retains its algebra and chosen augmentation ``epsilon: A -> R``.
    A morphism ``f: A -> B`` is an algebra morphism satisfying
    ``epsilon_B*f = epsilon_A``. This is the existing slice construction,
    with its scalar-algebra implementation; both entries retain one category.
    """
    ring = _owned_ring(base_ring)
    if ring not in OwnedRings().Commutative():
        raise TypeError(f"augmented R-algebras require a commutative R, but got {ring}")
    ordinary = Algebras(ring).Associative().Unital()
    return SliceCategory(ordinary, _scalar_module(ring))


class _AugmentedAlgebraMorphism:
    r"""An actual algebra arrow with its retained augmentation triangle.

    The existing algebra Mor constructs the lower arrow on the same
    structured endpoints. Its cooperative constructor supplies every lower
    arrow operation. The extra datum is an existing ArrowMor square, whose
    right edge is the identity of the scalar algebra.
    """

    def __init__(self, parent, datum, *, augmentation_square=None, **options):
        underlying = parent.underlying_mor()
        # Reading a stronger arrow in C preserves it literally. Here the
        # defining square needs the existing C implementation, so enter its
        # actual constructor on the retained whole-map datum. This prevents
        # an augmented edge from recursively composing its own square.
        if isinstance(datum, (Morphism, CategoricalArrow)) and datum.parent() is underlying:
            arrow = datum
        elif (
            isinstance(underlying, UnitalMultiplicativeAlgebraMor)
            and isinstance(datum, UnitalMultiplicativeAlgebraMorphism)
            and datum.domain() is parent.domain()
            and datum.codomain() is parent.codomain()
        ):
            # The common unframed constructor otherwise forgets f to U(f)
            # before its unital provider sees it. This existing exact-map
            # transport keeps f's three law decisions independently.
            arrow = underlying._from_constructed_element_map(
                datum, transported_morphism=datum,
            )
        else:
            # In particular the graded constructor retains the actual
            # source map and its independent degree-preservation datum.
            arrow = underlying._element_constructor_(datum)
        self._augmentation_underlying_morphism = arrow
        if augmentation_square is None:
            augmentation_square = parent._square_of(arrow)
        elif (
            augmentation_square.parent() is not parent._augmentation_square_mor()
            or augmentation_square.left() is not datum
        ):
            raise ValueError("the augmentation triangle must retain this exact defining algebra arrow")
        elif arrow is not datum:
            augmentation_square = parent._augmentation_square_mor()._from_commuting_edges(
                arrow, augmentation_square.right(),
                commutativity_premises=(augmentation_square,),
            )
        self._augmentation_square = augmentation_square
        args, transported_options = arrow._transport_initialization_to_mor(parent)
        super().__init__(*args, **transported_options, **options)
        self.validate_augmentation_preservation(check=False)

    def _elementwise_linearity_derivation(self):
        return self._augmentation_underlying_morphism.linearity_decision()

    def _multiplicativity_derivation(self):
        return self._augmentation_underlying_morphism.is_multiplicative()

    def _unit_preservation_derivation(self):
        return self._augmentation_underlying_morphism.preserves_unit()

    def underlying_arrow(self):
        r"""The retained arrow after forgetting augmentation preservation."""
        return self._augmentation_underlying_morphism

    def augmentation_square(self):
        r"""The defining square with left edge ``f`` and right edge ``id_R``."""
        return self._augmentation_square

    def left(self):
        r"""The free edge of this slice morphism, on its structured endpoints."""
        return self.augmentation_square().left()

    def right(self):
        r"""The retained edge at the fixed scalar object."""
        return self.augmentation_square().right()

    @cached_method
    def preserves_augmentation(self):
        r"""The augmentation equation, retaining undecided morphism equality."""
        square = self.augmentation_square()
        scalar = square.right().domain()
        ordinary = Algebras(self.domain().algebra_base_ring()).Associative().Unital()
        identity = ordinary.Mor(scalar, scalar).identity()
        return conjunction((square.commutativity_decision(), square.right() == identity))

    commutativity_decision = preserves_augmentation

    @validator
    def validate_augmentation_preservation(self):
        r"""Check the defining triangle when requested, following ``OWN-22``."""
        decision = self.preserves_augmentation()
        if decision is False:
            raise ValueError(f"{self.underlying_arrow()} does not preserve the chosen augmentations")
        assert decision is True, (
            "no selected algebra-morphism equality computation decides this augmentation triangle"
        )

    def __mul__(self, other):
        if not isinstance(other, _AugmentedAlgebraMorphism):
            return MultiplicativeAlgebraMorphism.__mul__(self, other)
        if other.codomain() is not self.domain():
            return NotImplemented
        if self.domain() is self.codomain() and self is self.parent().identity():
            return other
        if other.domain() is other.codomain() and other is other.parent().identity():
            return self
        category = Cat().join((self.parent().mor_category(), other.parent().mor_category()))
        square = self.augmentation_square() * other.augmentation_square()
        return category.Mor(other.domain(), self.codomain())._from_augmentation_square(
            square, degree_preservation_premises=(self, other),
        )


class _AugmentedAlgebraMor(CategoricalMor):
    r"""The existing scalar-slice Mor, with the actual algebra-arrow provider."""

    ElementMethods = _AugmentedAlgebraMorphism

    def underlying_mor(self):
        ordinary = Algebras(self.domain().algebra_base_ring()).Associative().Unital()
        return ordinary.Mor(self.domain(), self.codomain())

    @cached_method
    def _augmentation_square_mor(self):
        ordinary = Algebras(self.domain().algebra_base_ring()).Associative().Unital()
        arrows = ordinary.ArrowCategory()
        source = arrows(self.domain().augmentation())
        target = arrows(self.codomain().augmentation())
        return arrows.Mor(source, target)

    def _square_of(self, arrow):
        scalar = self.domain().augmentation().codomain()
        ordinary = Algebras(self.domain().algebra_base_ring()).Associative().Unital()
        return self._augmentation_square_mor()(arrow, ordinary.Mor(scalar, scalar).identity())

    def _element_constructor_(self, datum, *, check=False):
        if isinstance(datum, CommutativeSquare):
            morphism = self._from_augmentation_square(datum)
        else:
            morphism = self.element_class(self, datum)
        morphism.validate_augmentation_preservation(check=check)
        return morphism

    def _from_augmentation_square(self, square, *, degree_preservation_premises=None):
        square = self._augmentation_square_mor()(square)
        return self.element_class(self, square.left(), augmentation_square=square)

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError("the identity in an augmented-algebra Mor requires equal endpoints")
        return self._from_augmentation_square(self._augmentation_square_mor().identity())


class _GradedAugmentedAlgebraMor(_AugmentedAlgebraMor, GradedAlgebraMor):
    r"""Algebra arrows retaining both the selected grading and augmentation."""

    def __init__(self, mor_family, domain, codomain):
        GradedAlgebraMor.__init__(self, mor_family, domain, codomain)

    def underlying_mor(self):
        graded = GradedAlgebras(self.domain().algebra_base_ring(), self.grading_monoid())
        return graded.Mor(self.domain(), self.codomain())

    def _from_augmentation_square(self, square, *, degree_preservation_premises=None):
        r"""Retain the composite's actual graded arrows as sufficient premises."""
        square = self._augmentation_square_mor()(square)
        return self.element_class(
            self, square.left(), augmentation_square=square,
            degree_preservation_premises=degree_preservation_premises,
        )

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError("the identity in a graded augmented Mor requires equal endpoints")
        square = self._augmentation_square_mor().identity()
        return self.element_class(
            self, square.left(), augmentation_square=square,
            degree_preservation_premises=(),
        )


class _AugmentedAlgebraSlice(SliceCategory):
    r"""The scalar-slice implementation of ``AugmentedAlgebras(R)``.

    This is selected by the existing SliceCategory cache, not a second
    category. The original algebra and its one chosen map are retained by
    the slice; the algebra owner constructs the structured domain on the
    original module, multiplication and unit.
    """

    _SliceMor = _AugmentedAlgebraMor

    @staticmethod
    def __classcall__(cls, base_category, base_object):
        return SliceCategory(base_category, base_object)

    @classmethod
    def _slice_category_class_for(cls, base_category, base_object):
        return cls if base_object is _scalar_module(base_category.base_ring()) else None

    def base_ring(self):
        return self.base_category().base_ring()

    def object(self, augmentation, *, categories=(), construction_data=None, _engine=None):
        r"""Admit the exact scalar map, then use the canonical slice cache."""
        if not isinstance(augmentation, Map):
            raise TypeError("an augmented algebra is supplied by an algebra map to its scalar algebra")
        domain = augmentation.domain()
        if domain not in self.base_category() or domain.algebra_base_ring() is not self.base_ring():
            raise ValueError("the augmentation must retain the requested coefficient ring")
        if augmentation.codomain() is not self.base_object():
            raise ValueError("the augmentation must end at the exact canonical scalar algebra")
        selected = self.base_category().Mor(domain, self.base_object())(augmentation)
        return SliceCategory.object(
            self, selected, categories=categories,
            construction_data=construction_data, _engine=_engine,
        )

    __call__ = object

    def _construct_on(self, arrow, categories, engine, construction_data):
        return _augmented_algebra(
            arrow, category=self, categories=categories,
            construction_data=construction_data, engine=engine,
        )

    def an_object(self):
        ring = self.base_ring()
        polynomials = ring.free_module(("x",)).symmetric_algebra()
        label = next(iter(polynomials.algebra_generating_set()))
        return self(polynomials.Mor(self.base_object())({label: self.base_object().zero()}))

    class ParentMethods:
        def is_augmented(self):
            r"""This object retains a chosen augmentation, its scalar-slice datum."""
            return True

        @cached_method
        def augmentation(self):
            r"""The chosen augmentation on this exact structured endpoint.

            The wrapper retains the original module, multiplication and unit,
            so each law is transported from the selected arrow independently.
            """
            from sage_extensions.categories.algebras.comparison_maps import (
                _constructed_algebra_morphism,
            )

            category = AugmentedAlgebras(self.algebra_base_ring())
            selected = category.arrow(self)
            source = self.unformed_module()
            return _constructed_algebra_morphism(
                self, selected.codomain(),
                lambda element: selected(source(element)),
                transported_morphism=selected,
            )

class GradedAugmentedAlgebras(OwnedCategoryOverBaseRing):
    r"""Associative unital algebras with a chosen grading and augmentation.

    These are independent data over the same commutative ``R``. A morphism
    preserves both. No projection to the unit-degree piece, centrality of
    that piece, connectedness, or grading law for the augmentation is stated.
    """

    _MorCategory = SliceMorCategoryConstruction
    _SliceMor = _GradedAugmentedAlgebraMor

    @classmethod
    def parameter_category(cls):
        return OwnedRings().Commutative()

    def an_object(self):
        r"""The scalar algebra, concentrated in the grading's identity degree."""
        from sage_extensions.categories.algebras.comparison_maps import (
            _constructed_algebra_morphism,
        )
        ring = self.base_ring()
        algebra = GradedAlgebras(ring, self.grading_monoid()).an_object()
        label = next(iter(algebra.module_generating_set()))
        scalar = _scalar_module(ring)
        augmentation = _constructed_algebra_morphism(
            algebra, scalar,
            lambda element: scalar(algebra(element).to_vector()(label)),
        )
        return AugmentedAlgebras(ring)(augmentation)

    @staticmethod
    def __classcall__(cls, base_ring, grading_monoid=None):
        graded = GradedAlgebras(base_ring, grading_monoid)
        return OwnedCategoryOverBaseRing.__classcall__(
            cls, graded.base_ring(), graded.grading_monoid()
        )

    def __init__(self, base_ring, grading_monoid) -> None:
        self._grading_monoid = grading_monoid
        super().__init__(base_ring)

    def grading_monoid(self):
        return self._grading_monoid

    def _repr_object_names(self) -> str:
        return f"graded augmented algebras over {self.base()}"

    def _make_named_class_key(self, name):
        return (super()._make_named_class_key(name), self.grading_monoid())

    def super_categories(self):
        return [
            GradedAlgebras(self.base_ring(), self.grading_monoid()),
            AugmentedAlgebras(self.base_ring()),
        ]

    class ParentMethods:
        def ground_ring_augmentation(self):
            r"""The actual chosen ``A -> R`` map, without an unchosen factorization."""
            return self.augmentation()


def _augmentation_codomain_is_allowed(domain, base, codomain) -> bool:
    r"""An augmentation lands in the base with its canonical scalar structure.

    A ring such as ``QQ[t]`` may already carry a different coefficient base.
    Its canonical algebra over itself is the existing ``_scalar_module``
    realization, not a change of the augmentation's mathematical target.
    """
    _ = domain
    return codomain is _scalar_module(base)


def _declared_graded_algebra_category(domain):
    for category in domain.category().all_super_categories(proper=False):
        if isinstance(category, GradedAlgebras):
            return category
    return None


def _graded_algebra_placement(domain, base):

    placement = []
    algebras = Algebras(base)
    match domain in algebras.Commutative():
        case True:
            placement.append(algebras.Commutative())
        case False:
            pass
    graded = _declared_graded_algebra_category(domain)
    if graded is None:
        return placement
    monoid = graded.grading_monoid()
    placement.append(GradedAlgebras(base, monoid))
    placement.append(GradedAugmentedAlgebras(base, monoid))
    if domain in FreeAlgebras(base):
        placement.append(FreeAlgebras(base))
    if domain in GradedFreeAlgebras(base):
        placement.append(GradedFreeAlgebras(base))
    if domain in SymmetricAlgebras(base):
        placement.append(SymmetricAlgebras(base))
    if domain in TensorAlgebras(base):
        placement.append(TensorAlgebras(base))
    if domain in AlternatingAlgebras(base):
        placement.append(AlternatingAlgebras(base))
    if domain in DividedPowerAlgebras(base):
        placement.append(DividedPowerAlgebras(base))
    return placement


def _augmented_algebra(
    augmentation, *, category=None, categories=(), construction_data=None, engine=None,
    constructing_category=None,
):
    r"""Return the domain of ``augmentation``, as an augmented algebra.

    The selected scalar slice retains this exact map and the algebra owner
    retains its domain as the structured algebra's underlying module. A
    grading, when present, is independent data; it supplies no map to ``A_u``.
    The module owner selects the actual finite, free or general realization;
    its existing same-data construction has no additional engine parameter.
    The result is an object of ``category``, its ambient category
    (``ARC-07``), unless a canonical power producer names its power
    category as ``constructing_category``.
    """
    match isinstance(augmentation, Map):
        case True:
            pass
        case False:
            raise TypeError(
                f"an augmentation is an algebra morphism A -> R, but {augmentation!r} is not a map"
            )
    domain = augmentation.domain()
    if category is None:
        category = AugmentedAlgebras(domain.algebra_base_ring())
    base = category.base_ring()
    algebras = Algebras(base).Associative().Unital()
    if domain.algebra_base_ring() is not base:
        raise ValueError("the augmentation must have the requested literal coefficient ring")
    assert engine is None, (
        "this scalar slice retains the original algebra's exact module data; "
        "the module owner's existing same-data construction selects its "
        "realization and has no supplied composition with another private "
        "slice engine"
    )
    match domain in algebras:
        case True:
            pass
        case False:
            raise TypeError(
                f"an augmentation {augmentation} needs its domain {domain} to be an algebra over {base}, but it is not"
            )
    aug_codomain = _owned_ring(augmentation.codomain())
    match _augmentation_codomain_is_allowed(domain, base, aug_codomain):
        case True:
            pass
        case False:
            raise TypeError(
                f"an augmentation of {domain} is a morphism to {base}, but {augmentation} ends at "
                f"{augmentation.codomain()}"
            )
    selected = algebras.Mor(domain, aug_codomain)(augmentation)
    placement = _graded_algebra_placement(domain, base)
    law_decisions = _root_algebra_law_decisions(domain)
    if _declared_graded_algebra_category(domain) is not None:
        law_decisions["grading"] = domain.grading_compatibility_decision()
    data = dict(construction_data or {})
    data["_constructing_category"] = (
        category if constructing_category is None else constructing_category
    )
    arrows = dict(data.pop("slice_arrows", {}))
    if category in arrows and arrows[category] is not selected:
        raise ValueError("one scalar slice cannot retain two different augmentations")
    arrows[category] = selected
    data["slice_arrows"] = arrows
    # A power algebra's defining input is M, not its whole graded module.
    # Pass that exact datum through construction before cooperative init;
    # the direct-sum realization retains the same graded-piece family.
    if domain in AlternatingAlgebras(base):
        data["generating_module"] = domain.generating_module()
        data["power_flavor"] = "alternating"
    elif domain in DividedPowerAlgebras(base):
        data["generating_module"] = domain.generating_module()
        data["power_flavor"] = "divided"
    elif domain in SymmetricAlgebras(base) or domain in TensorAlgebras(base):
        data["generating_module"] = domain.generating_module()
    if domain.is_framed_algebra():
        framing_owner = domain.algebra_framing_owner()
        data["algebra_generating_family"] = domain.algebra_generators()
        data["algebra_framing_source"] = domain.algebra_framing_source()
        data["algebra_framing_owner"] = framing_owner
    return _algebra_on_module(
        domain,
        domain.multiplication_morphism(),
        placement=(category, *tuple(placement)),
        categories=categories,
        unit=domain.one(),
        construction_data=data,
        law_decisions=law_decisions,
    )
