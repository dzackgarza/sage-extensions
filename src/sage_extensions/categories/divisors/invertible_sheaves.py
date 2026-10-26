r"""Invertible sheaves represented by rank-one affine module descent data."""

from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
)
from sage_extensions.categories.modules.pure.modules import (
    FinitelyGeneratedFreeModules,
    Modules,
)
from sage_extensions.categories.functors.core import Functor
from sage_extensions.categories.rings.ring_foundation import (
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.schemes.gluing import (
    FiniteAffineAtlases,
    ModuleGluingData,
    _ModuleGluingSheafEngine,
    _AffineChartOpenSubobjects,
)
from sage_extensions.validation import validator
from sage_extensions.logic import conjunction, negation
from sage_extensions.categories.schemes.ringed_spaces import (
    InvertibleSheavesWithChosenTrivialization,
    QuasiCoherentSheafMor,
    QuasiCoherentSheaves,
    _is_empty_open,
)
from sage_extensions.categories.abstract_categories.mor_foundation import object_level


def _homogeneous_section_identity_comparison(sections):
    """The identity in the core Mor of an owned section module."""
    identity = sections.module_category().Mor(sections, sections).identity()
    return sections.module_category().Core().Mor(sections, sections)(identity, identity)


def _rank_one_generator(module):
    labels = module.module_generating_set()
    if not labels.cardinality().is_finite() or int(labels.cardinality()) != 1:
        raise TypeError(
            f"{module} is not free of rank one: an invertible sheaf is locally free of rank one, "
            f"but this local module has a generating set of cardinality {labels.cardinality()}"
        )
    return module.module_generator(next(iter(labels)))


def _rank_one_transition(source, target, unit):
    unit = target.base_ring()(unit)
    if not unit.is_unit():
        raise ValueError(
            f"the transition scalar {unit} from {source} to {target} is not a unit of "
            f"{target.base_ring()}: transition functions of an invertible sheaf must be units"
        )
    source_generator = _rank_one_generator(source)
    target_generator = _rank_one_generator(target)
    forward = source.module_category().Mor(source, target)(
        lambda _label: target.scalar_multiple(unit, target_generator)
    )
    inverse_unit = source.base_ring()(unit.inverse_of_unit())
    inverse = target.module_category().Mor(target, source)(
        lambda _label: source.scalar_multiple(inverse_unit, source_generator)
    )
    return source.module_category().Core().Mor(source, target)(forward, inverse)


def _invertible_sheaf(gluing_datum):
    r"""Construct a rank-one distinguished-cover descent object through its sheaf owner."""
    return InvertibleSheavesWithChosenTrivialization(gluing_datum.scheme())(
        gluing_datum
    )


def _finite_atlas_invertible_sheaf(
    gluing_datum,
    transition_units,
    *,
    section_space=None,
    associated_divisor=None,
):
    r"""Construct finite-atlas rank-one descent through its sheaf owner."""
    return InvertibleSheavesWithChosenTrivialization(gluing_datum.scheme())(
        gluing_datum,
        transition_units,
        section_space=section_space,
        associated_divisor=associated_divisor,
    )


class _DistinguishedCoverInvertibleSheafEngine(_ModuleGluingSheafEngine):
    r"""A line bundle represented by rank-one free descent on one affine cover."""

    def __init__(self, gluing_datum, module_gluing_datum, **rest) -> None:
        match module_gluing_datum is gluing_datum:
            case True:
                pass
            case False:
                raise ValueError(
                    f"the gluing data {gluing_datum} and {module_gluing_datum} differ: an invertible "
                    "sheaf and its underlying sheaf of modules must be glued from the same descent data"
                )
        assert gluing_datum in ModuleGluingData(gluing_datum.cover()), (
            f"{gluing_datum} is not descent data for modules on the affine cover "
            f"{gluing_datum.cover()}: an invertible sheaf is glued from modules on an affine cover"
        )
        self._gluing_datum = gluing_datum
        self._transition_units = {}
        for module in gluing_datum.local_modules():
            ring = module.base_ring()
            if module not in FinitelyGeneratedFreeModules(ring) or int(module.module_rank()) != 1:
                raise TypeError(
                    f"the chart module {module} over {ring} is not free of rank one: an invertible "
                    "sheaf is locally free of rank one on every chart"
                )
        chart_count = int(gluing_datum.local_modules().cardinality())
        for left in range(chart_count):
            for right in range(left + 1, chart_count):
                self._transition_units[left, right] = self._extract_transition_unit(
                    left,
                    right,
                )
        super().__init__(module_gluing_datum=module_gluing_datum, **rest)

    def gluing_datum(self):
        return self._gluing_datum

    def cover(self):
        return self.gluing_datum().cover()

    def scheme(self):
        return self.gluing_datum().scheme()

    ringed_space = scheme

    def sheaf(self):
        return self

    def local_module(self, index):
        return self.gluing_datum().local_module(index)

    def local_trivialization(self, index):
        r"""Return the literal rank-one free chart module trivializing this sheaf."""

        module = self.local_module(index)
        identity = module.module_category().Mor(module, module).identity()
        return module.module_category().Core().Mor(module, module)(identity, identity)

    def _extract_transition_unit(self, source_index, target_index):
        transition = self.gluing_datum().transition(source_index, target_index).forward()
        source = transition.domain()
        target = transition.codomain()
        source_generator = _rank_one_generator(source)
        target_labels = target.module_generating_set()
        target_label = next(iter(target_labels))
        unit = target.framing_morphism().lift(transition(source_generator))(target_label)
        if not unit.is_unit():
            raise ValueError(
                f"the transition map {transition} sends the basis vector of {source} to "
                f"{unit} times the basis vector of {target}, and {unit} is not a unit: the transition "
                "maps of an invertible sheaf must be isomorphisms"
            )
        return unit

    def transition_unit(self, source_index, target_index):
        r"""Return the unit ``u_ij`` with ``e_i |-> u_ij e_j`` on the overlap."""

        source_index = int(source_index)
        target_index = int(target_index)
        if source_index == target_index:
            raise ValueError(
                f"chart indices {source_index} and {target_index} coincide: a transition function "
                "is defined on the overlap of two distinct charts"
            )
        if source_index < target_index:
            return self._transition_units[source_index, target_index]
        return self._transition_units[target_index, source_index].inverse_of_unit()

    def global_sections(self):
        return self.gluing_datum().compatible_sections()

    def morphism_to(self, target, local_maps):
        r"""Return the sheaf morphism represented by the supplied chart maps."""
        return QuasiCoherentSheaves(self.scheme()).Mor(self, target)(local_maps)

    @classmethod
    def _from_transition_units(cls, cover, transition_units):
        local_modules = tuple(
            open_subscheme.coordinate_algebra().free_module(1)
            for open_subscheme in cover.opens()
        )
        transitions = {}
        for left in range(len(local_modules)):
            for right in range(left + 1, len(local_modules)):
                source = cover.restrict_module(local_modules[left], left, right)
                target = cover.restrict_module(local_modules[right], right, left)
                transitions[left, right] = _rank_one_transition(
                    source,
                    target,
                    transition_units[left, right],
                )
        datum = ModuleGluingData(cover)(local_modules, transitions)
        return _invertible_sheaf(datum)

    @classmethod
    def trivial(cls, cover):
        r"""Return ``O_X`` represented as the rank-one trivial bundle on ``cover``."""

        units = {
            (left, right): cover.overlap(left, right).coordinate_algebra().one()
            for left in range(len(cover.opens()))
            for right in range(left + 1, len(cover.opens()))
        }
        return cls._from_transition_units(cover, units)

    def tensor_product(self, other):
        r"""Tensor two line bundles by multiplying their transition units."""
        if other not in InvertibleSheavesWithChosenTrivialization(self.scheme()):
            raise TypeError(
                f"cannot tensor {self} with {other}: {other} is not an invertible sheaf on "
                f"{self.scheme()} with a chosen trivialization"
            )
        if other.cover() is not self.cover():
            raise ValueError(
                f"cannot tensor {self} with {other}: they are trivialized on different affine covers, "
                "and this tensor product multiplies transition functions on one common cover"
            )
        units = {
            (left, right): self.transition_unit(left, right)
            * other.transition_unit(left, right)
            for left in range(len(self.cover().opens()))
            for right in range(left + 1, len(self.cover().opens()))
        }
        return self._from_transition_units(self.cover(), units)

    @cached_method
    def tensor_power(self, exponent):
        r"""Return ``self^tensor exponent`` using powers of the transition units."""

        exponent = int(exponent)
        units = {}
        for left in range(len(self.cover().opens())):
            for right in range(left + 1, len(self.cover().opens())):
                unit = self.transition_unit(left, right)
                units[left, right] = (
                    unit**exponent
                    if exponent >= 0
                    else unit.inverse_of_unit() ** (-exponent)
                )
        return self._from_transition_units(self.cover(), units)

    def dual_sheaf(self):
        r"""Return the dual line bundle, with transition units ``u_ij^{-1}``."""

        return self.tensor_power(-1)

    def _repr_(self):
        return f"Invertible sheaf on {self.scheme()} trivialized by {self.cover()}"


class _FiniteAtlasLineBundleOpenPresheaf(Functor):
    r"""Sections of a finite-atlas line bundle as modules over the scheme base.

    Global sections retain their selected realization. Basis sections use
    the actual module descent datum, and global restriction uses the chosen
    trivialization's chart component (Hartshorne, II.5.13). The empty-cover
    condition gives the zero module on the empty open (Stacks, Tag 04B3).
    """

    def __init__(self, scheme, line_bundle):
        self._scheme = scheme
        self._line_bundle = line_bundle
        Functor.__init__(self, scheme.open_subsets_site().opposite(), Modules(scheme.scheme_base_ring()))

    def _is_whole(self, open_object):
        opens = self.domain().base_category().object_set()
        return open_object.underlying_object().value() is opens.inclusion().codomain().top()

    def _basis(self, open_object):
        subset = open_object.underlying_object().value()
        atlas = self._line_bundle().gluing_datum()
        assert (
            subset in _AffineChartOpenSubobjects(self._scheme)
            and subset.gluing_datum() is atlas.presentation()
        ), f"sections on {subset} require a basis open of the line bundle's selected atlas"
        return subset.chart_index(), subset.chart_open()

    @cached_method
    def _whole_module(self):
        bundle = self._line_bundle()
        sections = bundle.global_sections()
        if sections.base_ring() is self._scheme.scheme_base_ring():
            return sections
        return sections.restrict_scalars(bundle.gluing_datum().global_function_algebra().algebra_structure_morphism())

    def _apply_object(self, open_object):
        if _is_empty_open(self, open_object):
            return self.codomain().base_ring().free_module(0)
        if self._is_whole(open_object):
            return self._whole_module()
        bundle = self._line_bundle()
        index, chart_open = self._basis(open_object)
        chart = bundle.gluing_datum().chart(index)
        scalar_map = chart.coordinate_algebra().algebra_structure_morphism()
        if chart_open is not chart:
            scalar_map = chart_open.inclusion().coordinate_algebra_morphism() * scalar_map
        module = bundle.module_descent_datum().basis_module(index, chart_open)
        return module.restrict_scalars(scalar_map)

    @cached_method(key=lambda self, open_object: id(open_object))
    def _whole_to_basis(self, open_object):
        bundle = self._line_bundle()
        source = self._whole_module()
        target = self(open_object)
        index, chart_open = self._basis(open_object)
        datum = bundle.module_descent_datum()

        def restrict(section):
            if source is not bundle.global_sections():
                section = source(section).underlying_element()
            local = bundle.section_on_chart(section, index)
            return target.wrap(datum.basis_restriction(
                index, bundle.gluing_datum().chart(index), index, chart_open, local,
            ))

        return self.codomain().Mor(source, target)._from_constructed_element_map(restrict)

    def _apply_morphism(self, arrow):
        source = self(arrow.domain())
        target = self(arrow.codomain())
        if _is_empty_open(self, arrow.domain()) or _is_empty_open(self, arrow.codomain()):
            return self.codomain().Mor(source, target).zero()
        if arrow.domain() is arrow.codomain() or (self._is_whole(arrow.domain()) and self._is_whole(arrow.codomain())):
            return self.codomain().Mor(source, target).identity()
        if self._is_whole(arrow.domain()):
            return self._whole_to_basis(arrow.codomain())
        if self._is_whole(arrow.codomain()):
            # Such an inclusion identifies this basis open with the whole space.
            return self._whole_to_basis(arrow.domain()).inverse()
        source_index, source_open = self._basis(arrow.domain())
        target_index, target_open = self._basis(arrow.codomain())
        datum = self._line_bundle().module_descent_datum()
        return self.codomain().Mor(source, target)._from_constructed_element_map(
            lambda section: target.wrap(datum.basis_restriction(
                source_index, source_open, target_index, target_open,
                source(section).underlying_element(),
            ))
        )


class _FiniteAtlasLineBundleSections:
    r"""Sections from rank-one modules and their retained atlas transitions."""

    def global_sections(self):
        r"""Return the chosen section space or the module of compatible sections."""
        match self._section_space:
            case None:
                return self.compatible_sections()
            case section_space:
                return section_space

    @cached_method
    def module_descent_datum(self):
        r"""The rank-one chart modules with their semilinear descent maps."""
        from sage_extensions.categories.schemes.gluing import (
            _finite_atlas_line_bundle_module_datum,
        )

        return _finite_atlas_line_bundle_module_datum(self)

    @cached_method
    def module_sheaf(self):
        return self.module_descent_datum().sheaf()

    @cached_method
    def compatible_sections(self):
        return self.module_sheaf().global_sections()

    def section_on_chart(self, section, index):
        r"""The chart component of a global section in this trivialization."""
        assert self._section_space is None, (
            "a selected framed space of global sections needs its chart-component comparison"
        )
        return self.module_descent_datum().compatible_section_component(section, index)

    def compatible_section(self, section):
        r"""The compatible chart family represented by this global section."""
        atlas = self.gluing_datum()
        components = {index: self.section_on_chart(section, index) for index in atlas.chart_indices()}
        return self.module_descent_datum().compatible_section(components)

    def sheaf(self):
        return self


class _FiniteAtlasInvertibleSheafEngine(_FiniteAtlasLineBundleSections):
    r"""A line bundle on a finite glued affine atlas via transition functions.

    Unlike the distinguished-cover realization, whose descent datum lives on one affine
    scheme's distinguished-open cover and hence has a literal common overlap
    ring, a finite glued atlas has two isomorphic presentations of every
    overlap.  A transition unit ``u_ij`` therefore lives on the source-side
    overlap, and the triple cocycle is

    ``u_ik = u_ij * phi_ij^*(u_jk)``

    after restriction to the source-side triple overlap.  The scheme gluing
    datum already owns ``phi_ij`` and its restrictions, so this class only
    adds the rank-one descent data rather than duplicating scheme descent.
    """

    def __init__(
        self,
        gluing_datum,
        transition_units,
        *,
        section_space=None,
        associated_divisor=None,
        base_change_image=None,
        **rest,
    ) -> None:
        if gluing_datum not in FiniteAffineAtlases(gluing_datum.scheme()):
            raise TypeError(
                f"{gluing_datum} is not a finite affine atlas of {gluing_datum.scheme()}: a line bundle "
                "is glued here from transition functions on a finite affine atlas"
            )
        self._finite_gluing_datum = gluing_datum
        self._section_space = section_space
        self._associated_divisor = associated_divisor
        self._base_change_image = base_change_image
        self._local_modules = {
            index: gluing_datum.chart(index).coordinate_algebra().free_module(1)
            for index in gluing_datum.chart_indices()
        }
        expected = set(gluing_datum.transition_index_set())
        supplied = dict(transition_units)
        if set(supplied) != expected:
            raise ValueError(
                f"transition functions were given on the chart pairs {sorted(supplied, key=str)}, but the "
                f"atlas {gluing_datum} has the pairs {sorted(expected, key=str)}: a line bundle needs "
                "exactly one transition function for each pair of charts"
            )
        self._transition_units = {
            (source_index, target_index): gluing_datum.overlap(source_index, target_index).coordinate_algebra()(
                supplied[source_index, target_index]
            )
            for source_index, target_index in expected
        }
        super().__init__(**rest)
        self.validate_transition_units(check=False)

    @validator
    def validate_transition_units(self) -> None:
        r"""Check that every transition function is a unit of its overlap ring (``OWN-22``)."""
        for (source_index, target_index), unit in self._transition_units.items():
            if unit.is_unit() is False:
                raise ValueError(
                    f"the transition function {unit} on the overlap of charts {source_index} and "
                    f"{target_index} is not a unit of {unit.parent()}: line-bundle transition functions "
                    "must be units"
                )

    def gluing_datum(self):
        return self._finite_gluing_datum

    def cover(self):
        return self.gluing_datum()

    def scheme(self):
        return self.gluing_datum().scheme()

    ringed_space = scheme

    def chart_indices(self):
        return self.gluing_datum().chart_indices()

    def local_module(self, index):
        index = self.gluing_datum().normalize_chart_index(index)
        return self._local_modules[index]

    def local_trivialization(self, index):
        module = self.local_module(index)
        identity = module.module_category().Mor(module, module).identity()
        return module.module_category().Core().Mor(module, module)(identity, identity)

    def associated_divisor(self):
        if self._associated_divisor is None:
            raise TypeError(
                f"{self} was not constructed as O(D) of a divisor D, so it has no associated divisor"
            )
        return self._associated_divisor

    def _selected_base_change_image(self):
        r"""Return the selected scalar-base-change datum, or None.

        Protected finite-atlas line-bundle construction contract. The
        base-change source/projection/section operations and tensor-power
        transport in this module are its callers; they must not read the
        realization's storage directly.
        """
        return self._base_change_image

    def _stored_pair(self, source_index, target_index):
        datum = self.gluing_datum()
        source_index = datum.normalize_chart_index(source_index)
        target_index = datum.normalize_chart_index(target_index)
        if source_index == target_index:
            raise ValueError(
                f"chart indices {source_index} and {target_index} coincide: a transition function "
                "is defined on the overlap of two distinct charts"
            )
        ranking = datum.chart_index_set().ranking_map()
        return (
            (source_index, target_index)
            if ranking(source_index) < ranking(target_index)
            else (target_index, source_index)
        )

    def transition_unit(self, source_index, target_index):
        datum = self.gluing_datum()
        source_index = datum.normalize_chart_index(source_index)
        target_index = datum.normalize_chart_index(target_index)
        pair = self._stored_pair(source_index, target_index)
        unit = self._transition_units[pair]
        if pair == (source_index, target_index):
            return unit
        reverse_transition = datum.transition_between(source_index, target_index).forward()
        return reverse_transition.coordinate_algebra_morphism()(
            unit.inverse_of_unit()
        )

    def _restrict_pair_unit_to_triple(
        self,
        source_index,
        target_index,
        third_index,
        unit,
    ):
        datum = self.gluing_datum()
        pair_overlap = datum.overlap(source_index, target_index)
        triple = datum.triple_overlap(source_index, target_index, third_index)
        into_pair = pair_overlap.corestriction(triple.inclusion())
        return into_pair.coordinate_algebra_morphism()(unit)

    def satisfies_cocycle_condition(self) -> bool:
        r"""Whether ``g_ik = g_ij g_jk`` on every triple overlap of the atlas.

        A line bundle constructed from a divisor or a global object has transition
        functions that satisfy this by construction; this is the statement a test or
        a caller supplying transition functions by hand asks for.
        """
        from itertools import combinations

        datum = self.gluing_datum()

        def holds(left, middle, right):
            left_middle = self._restrict_pair_unit_to_triple(left, middle, right, self.transition_unit(left, middle))
            middle_right = self._restrict_pair_unit_to_triple(middle, right, left, self.transition_unit(middle, right))
            pullback = datum.transition_on_triple(left, middle, right).coordinate_algebra_morphism()
            left_right = self._restrict_pair_unit_to_triple(left, right, middle, self.transition_unit(left, right))
            return left_middle * pullback(middle_right) == left_right

        return all(holds(*triple) for triple in combinations(tuple(datum.chart_indices()), 3))

    @classmethod
    def _from_transition_units(cls, cover, transition_units):
        return _finite_atlas_invertible_sheaf(cover, transition_units)

    @classmethod
    def trivial(cls, atlas):
        units = {
            pair: atlas.overlap(*pair).coordinate_algebra().one()
            for pair in atlas.transition_index_set()
        }
        return _finite_atlas_invertible_sheaf(atlas, units)

    def tensor_product(self, other):
        if other not in InvertibleSheavesWithChosenTrivialization(self.scheme()):
            raise TypeError(
                f"cannot tensor {self} with {other}: {other} is not an invertible sheaf on "
                f"{self.scheme()} with a chosen trivialization"
            )
        if other.gluing_datum() is not self.gluing_datum():
            raise ValueError(
                f"cannot tensor {self} with {other}: they are trivialized on different affine atlases, "
                "and this tensor product multiplies transition functions on one common atlas"
            )
        units = {
            pair: self.transition_unit(*pair) * other.transition_unit(*pair)
            for pair in self.gluing_datum().transition_index_set()
        }
        return _finite_atlas_invertible_sheaf(self.gluing_datum(), units)

    @cached_method
    def tensor_power(self, exponent):
        exponent = int(exponent)
        units = {}
        for pair in self.gluing_datum().transition_index_set():
            unit = self.transition_unit(*pair)
            units[pair] = (
                unit**exponent
                if exponent >= 0
                else unit.inverse_of_unit() ** (-exponent)
            )
        return _finite_atlas_invertible_sheaf(self.gluing_datum(), units)

    def dual_sheaf(self):
        return self.tensor_power(-1)

    def _repr_(self):
        return f"Invertible sheaf on finite affine atlas of {self.scheme()}"


class _LineBundleBaseChangeImage:
    r"""The chosen preimage of a line bundle under scalar base change along a ring map.

    For \(f\colon R \to S\) and a bundle \(L\) on \(X\), the base-changed
    bundle \(f^* L\) on \(X_S\) retains \(L\) and \(f\).  Two later operations
    read this preimage: ``base_change_source_bundle`` and
    ``section_base_change_comparison``, the isomorphism
    \(H^0(X, L) \otimes_R S \cong H^0(X_S, f^* L)\) of polynomial section spaces.
    The changed bundle owns it from construction time.
    """

    def __init__(self, source_bundle, ring_map) -> None:
        self._source_bundle = source_bundle
        self._ring_map = ring_map

    def source_bundle(self):
        return self._source_bundle

    def ring_map(self):
        return self._ring_map

    def projection(self, changed_bundle):
        return changed_bundle.scheme().left_projection()

    def compatible_section(self, changed_bundle, section):
        r"""Pull a compatible section back in the standard local trivializations.

        The selected basis of each standard O(d) chart pulls back to the
        selected basis of the corresponding changed chart.  Thus a section
        a_i e_i pulls back to p_i^#(a_i) e_i'.  The transition equations are
        preserved by these ring maps; the target descent constructor checks
        them without retaining an unrelated homogeneous presentation.
        """
        from sage_extensions.categories.sets.indexed_families import (
            finite_indexed_family,
        )

        source = self.source_bundle()
        source_sections = source.compatible_sections()
        if section.parent() is not source_sections:
            raise ValueError(
                f"{section} is not a global section of {source}: its parent is {section.parent()}"
            )
        source_atlas = source.gluing_datum()
        source_module_datum = source.module_sheaf().gluing_datum()
        target_atlas = changed_bundle.gluing_datum()
        target_module_datum = changed_bundle.module_sheaf().gluing_datum()
        projection = self.projection(changed_bundle)

        def component(index):
            source_index = source_atlas.normalize_chart_index(index)
            target_index = target_atlas.normalize_chart_index(index)
            chart_projection = source_atlas.chart(source_index).corestriction(
                projection * target_atlas.chart_embedding(target_index)
            )
            pullback = chart_projection.coordinate_algebra_morphism()
            source_module = source.local_module(source_index)
            target_module = changed_bundle.local_module(target_index)
            label = next(iter(source_module.module_generating_set()))
            coefficient = source_module.framing_morphism().lift(
                source_module_datum.compatible_section_component(section, source_index)
            )(label)
            return target_module.scalar_multiple(
                pullback(coefficient), _rank_one_generator(target_module)
            )

        return target_module_datum.compatible_section(
            finite_indexed_family(target_atlas.chart_index_set(), component)
        )

    def section_comparison(self, changed_bundle):
        return _section_base_change_comparison(
            self.source_bundle().global_sections(),
            changed_bundle.global_sections(),
            self.ring_map(),
        )


def _section_base_change_comparison(source_sections, target_sections, ring_map):
    r"""Compare scalar extension of two polynomial section spaces monomial by monomial."""
    changed_source = source_sections.base_change(ring_map)
    source_by_exponents = {
        source_sections.monomial_exponents(label): label
        for label in source_sections.module_generating_set()
    }
    target_by_exponents = {
        target_sections.monomial_exponents(label): label
        for label in target_sections.module_generating_set()
    }
    forward = changed_source.module_category().Mor(changed_source, target_sections)(
        lambda label: target_sections.module_generator(
            target_by_exponents[source_sections.monomial_exponents(label)]
        )
    )
    inverse = target_sections.module_category().Mor(target_sections, changed_source)(
        lambda label: changed_source.module_generator(
            source_by_exponents[target_sections.monomial_exponents(label)]
        )
    )
    return changed_source.module_category().Core().Mor(changed_source, target_sections)(
        forward, inverse
    )


def _base_change_image(bundle):
    image = bundle._selected_base_change_image()
    assert image is not None, (
        f"{bundle} was not constructed by base change of scalars, so it has no source bundle "
        "or base-change projection"
    )
    return image


def _base_change_source_bundle(bundle):
    return _base_change_image(bundle).source_bundle()


def _base_change_projection(bundle):
    return _base_change_image(bundle).projection(bundle)


def _section_base_change_comparison_of(bundle):
    return _base_change_image(bundle).section_comparison(bundle)


def _tensor_power_base_change_image(bundle, exponent):
    r"""Return the scalar-change provenance inherited by one tensor power."""
    match bundle._selected_base_change_image():
        case None:
            return None
        case image:
            return _LineBundleBaseChangeImage(
                image.source_bundle().tensor_power(exponent),
                image.ring_map(),
            )


def _chosen_trivialization_object(
    scheme,
    engine,
    *,
    placements=(),
    **construction_data,
):
    r"""Realize one line-bundle engine in the chosen-trivialization owner."""
    category = InvertibleSheavesWithChosenTrivialization(scheme)
    presheaf = _FiniteAtlasLineBundleOpenPresheaf(scheme, lambda: sheaf)
    sheaf = QuasiCoherentSheaves(scheme).object(
        categories=(category, *placements),
        construction_data=construction_data,
        _engine=engine,
        open_sections_presheaf=presheaf,
    )
    return sheaf


def _invertible_sheaf_object(
    scheme,
    engine,
    *,
    placements=(),
    **construction_data,
):
    r"""Realize one line-bundle engine directly in ``QCoh(scheme).Invertible()``."""
    category = QuasiCoherentSheaves(scheme).Invertible()
    presheaf = _FiniteAtlasLineBundleOpenPresheaf(scheme, lambda: sheaf)
    sheaf = QuasiCoherentSheaves(scheme).object(
        categories=(category, *placements),
        construction_data=construction_data,
        _engine=engine,
        open_sections_presheaf=presheaf,
    )
    return sheaf


class _ProjectiveSpaceLineBundleEngine(_FiniteAtlasInvertibleSheafEngine):
    r"""The standard ``O(d)`` on one represented projective space.

    This is a specialization of finite-atlas invertible-sheaf descent.  Its
    local basis on ``U_i`` has transition ``(x_j/x_i)^d`` to ``U_j``; tensor
    product therefore adds degrees and duality negates them.

    Unexecuted sections specimens (Hartshorne, Proposition II.5.13)::

        sage: from dzack_research.preamble.all import *
        sage: line = ProjectiveSpaces(QQ)(1)
        sage: bundle = line.O(2)
        sage: whole = bundle.descent_data().coverage().whole_open()
        sage: bundle.sections(whole).module_rank() == 3
        True
        sage: negative = line.O(-1)
        sage: negative.sections(whole).is_zero()
        True
        sage: atlas = line.standard_affine_atlas()
        sage: site = line.open_subsets_site()
        sage: chart = site(atlas.chart_open_subset(1))
        sage: negative.sections(chart).module_over_extension().module_rank() == 1
        True
        sage: forms = bundle.global_sections()
        sage: S = forms.homogeneous_coordinate_ring()
        sage: x0 = S.algebra_generator(line.variable_names()[0])
        sage: section = forms.section_from_homogeneous_polynomial(x0*x0)
        sage: opposite = site.opposite()
        sage: arrow = opposite.Mor(opposite(whole), opposite(chart))(site.Mor(chart, whole)())
        sage: restriction = bundle.open_sections_presheaf().on_morphism(arrow)
        sage: y = next(iter(atlas.chart(1).coordinate_algebra().algebra_generators()))
        sage: local = bundle.local_module(1)
        sage: generator = local.module_generator(next(iter(local.module_generating_set())))
        sage: restriction(section).underlying_element() == local.scalar_multiple(y*y, generator)
        True
        sage: first = site(atlas.chart_open_subset(0))
        sage: overlap = site(atlas.chart_open_subset(0, atlas.overlap(0, 1)))
        sage: F = bundle.open_sections_presheaf()
        sage: first_arrow = opposite.Mor(opposite(whole), opposite(first))(site.Mor(first, whole)())
        sage: first_overlap = opposite.Mor(opposite(first), opposite(overlap))(site.Mor(overlap, first)())
        sage: second_overlap = opposite.Mor(opposite(chart), opposite(overlap))(site.Mor(overlap, chart)())
        sage: F.on_morphism(first_overlap)(F.on_morphism(first_arrow)(section)) == F.on_morphism(second_overlap)(restriction(section))
        True
    """

    # The standard atlas and the transition units are computed here from the
    # projective space and the degree.
    _derived_construction_parameters = frozenset({"gluing_datum", "transition_units"})

    def __init__(
        self,
        projective_space,
        degree,
        *,
        base_change_image=None,
        **rest,
    ) -> None:
        from sage_extensions.categories.divisors.linear_systems import (
            _homogeneous_polynomial_section_space,
        )
        from sage_extensions.categories.schemes.schemes import (
            ProjectiveSpaces,
        )

        base = projective_space.scheme_base_ring()
        if projective_space not in ProjectiveSpaces(base):
            raise TypeError(
                f"cannot construct O({degree}) on {projective_space}: it is not a projective space "
                f"over {base}"
            )
        self._projective_space = projective_space
        self._degree = _owned_integers()(degree)
        atlas = projective_space.standard_affine_atlas()
        units = {}
        for source_index, target_index in atlas.transition_index_set():
            overlap = atlas.overlap(source_index, target_index)
            restriction = overlap.inclusion().coordinate_algebra_morphism()
            ratio = restriction(
                projective_space._standard_chart_coordinate(
                    source_index,
                    target_index,
                )
            )
            units[source_index, target_index] = (
                ratio ** int(self._degree)
                if self._degree >= 0
                else ratio.inverse_of_unit() ** int(-self._degree)
            )
        # Gamma(P^n_R, O(d)) is the degree-d piece S_d of S = R[x_0..x_n] for
        # every integer d, and S_d = 0 for d < 0 (Hartshorne, Proposition II.5.13).
        section_space = _homogeneous_polynomial_section_space(
            projective_space,
            self._degree,
            coordinate_names=projective_space.variable_names(),
        )
        super().__init__(
            atlas,
            units,
            section_space=section_space,
            base_change_image=base_change_image,
            **rest,
        )

    def projective_space(self):
        return self._projective_space

    def degree(self):
        return self._degree

    def tensor_product(self, other):
        match other:
            case _ProjectiveSpaceLineBundleEngine() if other.projective_space() is self.projective_space():
                return _projective_o(
                    self.projective_space(),
                    self.degree() + other.degree(),
                )
            case _ProjectiveSpaceLineBundleEngine():
                raise ValueError(
                    f"cannot tensor {self} with {other}: they are line bundles on different projective "
                    "spaces"
                )
            case _:
                return super().tensor_product(other)

    @cached_method
    def tensor_power(self, exponent):
        exponent = _owned_integers()(exponent)
        match exponent == 1:
            case True:
                return self
            case False:
                return _projective_o(
                    self.projective_space(),
                    exponent * self.degree(),
                    base_change_image=_tensor_power_base_change_image(self, exponent),
                )

    def dual_sheaf(self):
        return _projective_o(self.projective_space(), -self.degree())

    def is_ample(self) -> bool:
        return int(self.projective_space().relative_dimension()) == 0 or self.degree() > 0

    def is_basepoint_free(self) -> bool:
        return self.degree() >= 0

    is_globally_generated = is_basepoint_free

    def restriction_map(self, closed_subscheme):
        from sage_extensions.categories.divisors.linear_systems import (
            _projective_section_restriction,
        )

        return _projective_section_restriction(self, closed_subscheme)

    def restrict_to(self, closed_subscheme):
        r"""Return the pullback of O(d) along a represented projective closed immersion."""
        return closed_subscheme.inclusion().module_pullback(self)

    def pullback(self, morphism):
        r"""Return ``f^*O(d)`` for a represented projective-product projection.

        For the projection ``pi_i : prod_j P_j -> P_i``, the pullback is the
        multiprojective line bundle with degree ``d`` in the selected factor
        and degree zero in every other factor.  The retained projection label,
        rather than equality of repeated factors, selects that role.
        """
        from sage_extensions.categories.schemes.schemes import (
            ProductProjectiveSpaces,
        )

        if morphism.codomain() is not self.projective_space():
            raise ValueError(
                f"cannot pull back {self} along {morphism}: its codomain {morphism.codomain()} is not "
                f"the projective space {self.projective_space()}"
            )
        source = morphism.domain()
        base = source.scheme_base_ring()
        assert source in ProductProjectiveSpaces(base), (
            f"cannot pull back {self} along {morphism}: pullback is computed here only along a "
            f"projection from a product of projective spaces, and {source} is not a product of "
            f"projective spaces over {base}"
        )
        label = source.projection_label(morphism)
        labels = tuple(source.factors().index_set())
        label = source.factors().index_set()(label)
        return source.O(
            tuple(self.degree() if factor_label == label else 0 for factor_label in labels)
        )

    def linearize(self, scheme_action_functor, character):
        from sage_extensions.categories.divisors.linearizations import (
            _line_bundle_linearization,
        )

        return _line_bundle_linearization(self, scheme_action_functor, character)

    def c2_coordinate_swap_linearization(self, twist=1):
        r"""Linearize this ``O(d)`` for coordinate swap with the selected C2 character."""
        from sage_extensions.categories.group.groups import OwnedGroups

        base = self.projective_space().scheme_base_ring()
        group = OwnedGroups().C(2)
        scalar = base(twist)
        match scalar in (base.one(), -base.one()):
            case False:
                raise ValueError(
                    f"the twist {twist} is not +1 or -1: a character of C2 over {base} takes the "
                    "generator to +1 or -1"
                )
            case True:
                pass
        action = self.projective_space().coordinate_swap_action(group)

        def character(element):
            match group(element) == group.one():
                case True:
                    return base.one()
                case False:
                    return scalar

        return self.linearize(action, character)

    def linear_system(self, sections=None):
        from sage_extensions.categories.divisors.linear_systems import (
            _projective_linear_system,
        )

        selected = (
            tuple(self.global_sections().module_generators())
            if sections is None
            else tuple(sections)
        )
        return _projective_linear_system(self, selected)

    def jet_evaluation(self, point, order):
        from sage_extensions.categories.divisors.linear_systems import (
            _projective_point_jet_evaluation,
        )

        return _projective_point_jet_evaluation(self, point, order)

    def sections_vanishing_to_order(self, point, order):
        return self.jet_evaluation(point, order).kernel()

    def imposed_multiplicity_linear_system(self, point, order):
        from sage_extensions.categories.divisors.linear_systems import (
            _imposed_point_multiplicity_linear_system,
        )

        return _imposed_point_multiplicity_linear_system(self, point, order)

    def section_on_chart(self, section, index):
        r"""Dehomogenize a degree-d form in the trivialization by ``x_i^d``.

        Each monomial becomes the product of affine ratios away from its
        selected coordinate (Hartshorne, Proposition II.5.13).
        """
        sections = self.global_sections()
        coordinates = sections.framing_morphism().lift(sections(section))
        atlas = self.gluing_datum()
        index = atlas.normalize_chart_index(index)
        ring = atlas.chart(index).coordinate_algebra()
        scalar_map = ring.algebra_structure_morphism()
        coefficient = ring.zero()
        for monomial in coordinates.support().domain():
            term = scalar_map(coordinates(monomial))
            for coordinate, exponent in enumerate(sections.monomial_exponents(monomial)):
                if exponent and coordinate != int(index):
                    term *= self.projective_space()._standard_chart_coordinate(int(index), coordinate) ** int(exponent)
            coefficient += term
        module = self.local_module(index)
        return module.scalar_multiple(coefficient, _rank_one_generator(module))

    def homogeneous_polynomial_sections(self):
        return self.global_sections()

    def homogeneous_polynomial_comparison(self):
        return _homogeneous_section_identity_comparison(self.global_sections())

    def section_multiplication(self, other):
        from sage_extensions.categories.modules.pure.modules import BilinearMap

        match other:
            case _ProjectiveSpaceLineBundleEngine() if other.projective_space() is self.projective_space():
                pass
            case _ProjectiveSpaceLineBundleEngine():
                raise ValueError(
                    f"cannot multiply sections of {self} and {other}: they are line bundles on different "
                    "projective spaces"
                )
            case _:
                raise TypeError(
                    f"cannot multiply sections of {self} and {other}: {other} is not O(d) on a "
                    "projective space"
                )
        target_bundle = self.tensor_product(other)
        left = self.global_sections()
        right = other.global_sections()
        target = target_bundle.global_sections()
        target_by_exponents = {
            target.monomial_exponents(monomial): monomial
            for monomial in target.module_generating_set()
        }

        def product(left_monomial, right_monomial):
            exponents = tuple(
                left_power + right_power
                for left_power, right_power in zip(
                    left.monomial_exponents(left_monomial),
                    right.monomial_exponents(right_monomial),
                    strict=True,
                )
            )
            return target.module_generator(target_by_exponents[exponents])

        return BilinearMap(left, right, target, product)

    @cached_method
    def section_ring(self):
        from sage_extensions.categories.divisors.section_rings import SectionRings

        return SectionRings(self.scheme().scheme_base_ring())(self)

    def base_change(self, ring_map):
        return _projective_o(
            self.projective_space().base_change(ring_map),
            self.degree(),
            base_change_image=_LineBundleBaseChangeImage(self, ring_map),
        )

    def base_change_source_bundle(self):
        return _base_change_source_bundle(self)

    def base_change_projection(self):
        return _base_change_projection(self)

    def section_base_change_comparison(self):
        return _section_base_change_comparison_of(self)

    def pullback_compatible_section(self, section):
        r"""Pull a section of the source bundle back along this base change."""
        return _base_change_image(self).compatible_section(self, section)

    def _repr_(self):
        return f"O({self.degree()}) on {self.projective_space()}"



class _RestrictedLineBundleDescent(_FiniteAtlasLineBundleSections):
    r"""Pullback of line-bundle transition functions on the inverse-image atlas.

    If the ambient frames have transition ``u_ij``, their pulled frames have
    transition ``i^#(u_ij)`` (Hartshorne, II.5.12). Computation is lazy, so
    the object retains the specified pullback morphism before chart comparisons
    are requested.
    """

    def __init__(self, **rest):
        self._section_space = None
        super().__init__(**rest)

    @cached_method
    def gluing_datum(self):
        return self.ambient_line_bundle().gluing_datum().pullback(self.pullback_morphism())

    @cached_method
    def local_module(self, index):
        return self.gluing_datum().chart(index).coordinate_algebra().free_module(1)

    @cached_method
    def transition_unit(self, source_index, target_index):
        atlas = self.gluing_datum()
        ambient = self.ambient_line_bundle()
        overlap = atlas.overlap(source_index, target_index)
        into_ambient_chart = atlas.chart(source_index).left_projection() * overlap.inclusion()
        ambient_overlap = ambient.gluing_datum().overlap(source_index, target_index)
        into_ambient_overlap = ambient_overlap.corestriction(into_ambient_chart)
        return into_ambient_overlap.coordinate_algebra_morphism()(ambient.transition_unit(source_index, target_index))


class _ProjectiveSubschemeLineBundleEngine(_RestrictedLineBundleDescent):
    r"""The pullback ``i^* O_P(d)`` along a projective closed immersion.

    The defining datum is the actual closed immersion together with the
    ambient projective line bundle. Its chart modules and transitions are
    pulled back on the actual inverse-image atlas. Global sections are the
    module of compatible chart sections. The image-valued restriction map
    retains its own section-image operation.

    Unexecuted conic sections (Hartshorne, II.5.12)::

        sage: from dzack_research.preamble.all import *
        sage: P = ProjectiveSpaces(QQ)(2)
        sage: S = P.O(1).global_sections().homogeneous_coordinate_ring()
        sage: x0, x1, x2 = tuple(S.algebra_generators())
        sage: Z = P.closed_subscheme(x0*x2-x1*x1)
        sage: L = Z.inclusion().module_pullback(P.O(1))
        sage: atlas = Z.standard_affine_atlas()
        sage: L.gluing_datum() is atlas
        True
        sage: site = Z.open_subsets_site()
        sage: chart = site(atlas.chart_open_subset(0))
        sage: sections = L.sections(chart).module_over_extension()
        sage: sections is L.local_module(0)
        True
        sage: sections.base_ring() is atlas.chart(0).coordinate_algebra()
        True
        sage: first = P.standard_affine_chart(0).coordinate_algebra()
        sage: ratio = first.algebra_generator('x1_over_x0')
        sage: restriction = atlas.overlap(0, 1).inclusion().coordinate_algebra_morphism() * atlas.chart(0).left_projection().coordinate_algebra_morphism()
        sage: L.transition_unit(0, 1) == restriction(ratio)
        True
        sage: trivial = Z.inclusion().module_pullback(P.O(0))
        sage: datum = trivial.module_descent_datum()
        sage: unit = datum.compatible_section({i: trivial.local_module(i).module_generator(0) for i in atlas.chart_indices()})
        sage: trivial.section_on_chart(unit, 0) == trivial.local_module(0).module_generator(0)
        True
    """

    def __init__(
        self,
        closed_subscheme,
        ambient_line_bundle,
        *,
        pullback_morphism=None,
        **rest,
    ) -> None:
        from sage_extensions.categories.schemes.schemes import (
            ClosedSubschemes,
            ProjectiveSpaces,
        )

        base = closed_subscheme.scheme_base_ring()
        if closed_subscheme not in ClosedSubschemes(base):
            raise TypeError(
                f"cannot restrict {ambient_line_bundle} to {closed_subscheme}: it is not a closed "
                f"subscheme over {base}"
            )
        ambient = closed_subscheme.inclusion().codomain()
        if ambient not in ProjectiveSpaces(base):
            raise TypeError(
                f"cannot form O_X(d) on {closed_subscheme}: it is a closed subscheme of {ambient}, "
                f"which is not a projective space over {base}"
            )
        match ambient_line_bundle:
            case _ProjectiveSpaceLineBundleEngine() if ambient_line_bundle.projective_space() is ambient:
                pass
            case _ProjectiveSpaceLineBundleEngine():
                raise ValueError(
                    f"cannot restrict {ambient_line_bundle} to {closed_subscheme}: the bundle lives on "
                    f"{ambient_line_bundle.projective_space()}, but the subscheme lies in {ambient}"
                )
            case _:
                raise TypeError(
                    f"cannot restrict {ambient_line_bundle} to {closed_subscheme}: it is not a line "
                    f"bundle O(d) on the projective space {ambient}"
                )
        match pullback_morphism:
            case None:
                selected_pullback = closed_subscheme.inclusion()
            case _:
                selected_pullback = pullback_morphism
        match (
            selected_pullback.domain() is closed_subscheme,
            selected_pullback.codomain() is ambient,
        ):
            case (True, True):
                pass
            case _:
                raise ValueError(
                    f"{selected_pullback} is not a morphism from {closed_subscheme} to {ambient}, so it "
                    "cannot be the closed immersion along which the line bundle is pulled back"
                )
        self._scheme = closed_subscheme
        self._ambient_line_bundle = ambient_line_bundle
        self._pullback_morphism = selected_pullback
        super().__init__(**rest)

    def scheme(self):
        return self._scheme

    def pullback_morphism(self):
        return self._pullback_morphism

    inclusion = pullback_morphism

    def ambient_line_bundle(self):
        return self._ambient_line_bundle

    def degree(self):
        return self.ambient_line_bundle().degree()

    def tensor_product(self, other):
        match other:
            case _ProjectiveSubschemeLineBundleEngine() if other.scheme() is self.scheme():
                pass
            case _ProjectiveSubschemeLineBundleEngine():
                raise ValueError(
                    f"cannot tensor {self} with {other}: they are line bundles on different schemes"
                )
            case _:
                raise TypeError(
                    f"cannot tensor {self} with {other}: {other} is not the restriction of O(d) from a "
                    "projective space"
                )
        return self.pullback_morphism().module_pullback(
            self.ambient_line_bundle().tensor_product(other.ambient_line_bundle())
        )

    def tensor_power(self, exponent):
        exponent = _owned_integers()(exponent)
        if exponent == 1:
            return self
        return self.pullback_morphism().module_pullback(
            self.ambient_line_bundle().tensor_power(exponent)
        )

    def dual_sheaf(self):
        return self.pullback_morphism().module_pullback(
            self.ambient_line_bundle().dual_sheaf()
        )

    def is_ample(self) -> bool:
        r"""Decide ampleness for restrictions of ``O(d)`` to projective subschemes."""
        if int(self.scheme().dimension()) == 0:
            return True
        return self.degree() > 0

    def section_restriction_map(self):
        return self.ambient_line_bundle().restriction_map(self.scheme())

    def represented_global_section_image(self):
        return self.section_restriction_map().codomain()

    def canonical_isomorphism_to(self, target):
        r"""Return the canonical comparison with an equal-degree presentation on this scheme."""
        match target:
            case _ProjectiveSubschemeLineBundleEngine() if target.scheme() is self.scheme():
                pass
            case _ProjectiveSubschemeLineBundleEngine():
                raise ValueError(
                    f"no isomorphism from {self} to {target}: they are line bundles on different schemes"
                )
            case _:
                raise TypeError(
                    f"cannot compare {self} with {target}: {target} is not the restriction of O(d) from a "
                    "projective space"
                )
        if self.degree() != target.degree():
            raise ValueError(
                f"no canonical isomorphism from {self} to {target}: their degrees {self.degree()} and "
                f"{target.degree()} differ"
            )
        ambient = _chosen_trivialization_isomorphism(
            self.ambient_line_bundle(),
            target.ambient_line_bundle(),
        )
        sheaves = QuasiCoherentSheaves(self.scheme())
        forward = sheaves.Mor(self, target)(ambient.forward())
        inverse = sheaves.Mor(target, self)(ambient.inverse().forward())
        return sheaves.Core().Mor(self, target)(forward, inverse)

    def _repr_(self):
        return f"O({self.degree()}) restricted to {self.scheme()}"


def _projective_o(projective_space, degree, *, base_change_image=None):
    r"""Return the standard line bundle ``O(d)`` on ``P^n``."""
    return _chosen_trivialization_object(
        projective_space,
        _ProjectiveSpaceLineBundleEngine,
        projective_space=projective_space,
        degree=degree,
        base_change_image=base_change_image,
    )


def _projective_subscheme_line_bundle(
    closed_subscheme,
    ambient_line_bundle,
    *,
    pullback_morphism=None,
):
    r"""Return the invertible pullback of ``ambient_line_bundle`` to ``closed_subscheme``."""
    return _invertible_sheaf_object(
        closed_subscheme,
        _ProjectiveSubschemeLineBundleEngine,
        closed_subscheme=closed_subscheme,
        ambient_line_bundle=ambient_line_bundle,
        pullback_morphism=pullback_morphism,
    )


class _ProductProjectiveLineBundleEngine(_FiniteAtlasInvertibleSheafEngine):
    r"""The standard ``O(d_1,...,d_r)`` on a product of projective spaces."""

    # The product's standard affine atlas and its transition units are
    # determined by the product and the selected multidegree, not independent
    # constructor inputs to a chosen trivialization.
    _derived_construction_parameters = frozenset({"gluing_datum", "transition_units"})

    def __init__(
        self,
        projective_product,
        degrees,
        *,
        base_change_image=None,
        **rest,
    ) -> None:
        from sage_extensions.categories.divisors.linear_systems import (
            _multihomogeneous_polynomial_section_space,
        )
        from sage_extensions.categories.schemes.schemes import (
            ProductProjectiveSpaces,
        )
        from sage_extensions.categories.sets.indexed_families import (
            IndexedFamily,
            finite_indexed_family,
        )

        base = projective_product.scheme_base_ring()
        if projective_product not in ProductProjectiveSpaces(base):
            raise TypeError(
                f"cannot construct O{degrees} on {projective_product}: it is not a product of "
                f"projective spaces over {base}"
            )
        factors = projective_product.factors()
        factor_indices = factors.index_set()
        factor_labels = tuple(factor_indices)
        match degrees:
            case IndexedFamily():
                if degrees.index_set() is not factor_indices:
                    raise ValueError(
                        f"the multidegree {degrees} is indexed by {degrees.index_set()}, but the factors of "
                        f"{projective_product} are indexed by {factor_indices}"
                    )
                degree_values = tuple(
                    _owned_integers()(degrees[label]) for label in factor_labels
                )
            case _:
                degree_values = tuple(_owned_integers()(degree) for degree in degrees)
                if len(degree_values) != len(factor_labels):
                    raise ValueError(
                        f"the multidegree {degree_values} has {len(degree_values)} entries, but "
                        f"{projective_product} has {len(factor_labels)} projective factors: a multidegree "
                        "has one degree per factor"
                    )
        self._projective_product = projective_product
        self._multidegree = finite_indexed_family(
            factor_indices,
            lambda label: degree_values[
                next(
                    position
                    for position, known_label in enumerate(factor_labels)
                    if known_label == label
                )
            ],
            name="Line-bundle multidegree",
        )
        atlas = projective_product.standard_affine_atlas()
        positions = {label: position for position, label in enumerate(factor_labels)}
        units = {}
        for source_choice, target_choice in atlas.transition_index_set():
            overlap = atlas.overlap(source_choice, target_choice)
            overlap_restriction = overlap.inclusion().coordinate_algebra_morphism()
            chart = atlas.chart(source_choice)
            unit = overlap.coordinate_algebra().one()
            for label in factor_labels:
                position = positions[label]
                source_index = source_choice[position]
                target_index = target_choice[position]
                if source_index == target_index:
                    continue
                factor = factors[label]
                chart_pullback = chart.projection(label).coordinate_algebra_morphism()
                ratio = overlap_restriction(
                    chart_pullback(
                        factor._standard_chart_coordinate(source_index, target_index)
                    )
                )
                degree = self.multidegree()[label]
                unit *= (
                    ratio ** int(degree)
                    if degree >= 0
                    else ratio.inverse_of_unit() ** int(-degree)
                )
            units[source_choice, target_choice] = unit
        section_space = _multihomogeneous_polynomial_section_space(
            projective_product,
            self.multidegree(),
        )
        super().__init__(
            atlas,
            units,
            section_space=section_space,
            base_change_image=base_change_image,
            **rest,
        )

    def projective_product(self):
        return self._projective_product

    def multidegree(self):
        return self._multidegree

    def tensor_product(self, other):
        match other:
            case _ProductProjectiveLineBundleEngine() if other.projective_product() is self.projective_product():
                labels = tuple(self.multidegree().index_set())
                return _product_projective_o(
                    self.projective_product(),
                    tuple(
                        self.multidegree()[label] + other.multidegree()[label]
                        for label in labels
                    ),
                )
            case _ProductProjectiveLineBundleEngine():
                raise ValueError(
                    f"cannot tensor {self} with {other}: they are line bundles on different products of "
                    "projective spaces"
                )
            case _:
                return super().tensor_product(other)

    @cached_method
    def tensor_power(self, exponent):
        exponent = _owned_integers()(exponent)
        match exponent == 1:
            case True:
                return self
            case False:
                return _product_projective_o(
                    self.projective_product(),
                    tuple(
                        exponent * self.multidegree()[label]
                        for label in self.multidegree().index_set()
                    ),
                    base_change_image=_tensor_power_base_change_image(self, exponent),
                )

    def dual_sheaf(self):
        return self.tensor_power(-1)

    def is_ample(self) -> bool:
        factors = self.projective_product().factors()
        return all(
            int(factors[label].relative_dimension()) == 0
            or self.multidegree()[label] > 0
            for label in factors.index_set()
        )

    def is_basepoint_free(self) -> bool:
        return all(
            self.multidegree()[label] >= 0
            for label in self.multidegree().index_set()
        )

    is_globally_generated = is_basepoint_free

    def restrict_to(self, closed_subscheme):
        r"""Return the restricted multiprojective line bundle on ``closed_subscheme``."""
        return _product_projective_subscheme_line_bundle(closed_subscheme, self)

    def linearize(self, scheme_action_functor, character):
        from sage_extensions.categories.divisors.linearizations import (
            _line_bundle_linearization,
        )

        return _line_bundle_linearization(self, scheme_action_functor, character)

    def c2_diagonal_sign_linearization(self, twist=1):
        r"""Linearize this multidegree for the diagonal sign action and selected C2 character."""
        from sage_extensions.categories.group.groups import OwnedGroups

        base = self.projective_product().scheme_base_ring()
        group = OwnedGroups().C(2)
        scalar = base(twist)
        match scalar in (base.one(), -base.one()):
            case False:
                raise ValueError(
                    f"the twist {twist} is not +1 or -1: a character of C2 over {base} takes the "
                    "generator to +1 or -1"
                )
            case True:
                pass
        action = self.projective_product().c2_diagonal_sign_action(group)

        def character(element):
            match group(element) == group.one():
                case True:
                    return base.one()
                case False:
                    return scalar

        return self.linearize(action, character)

    def homogeneous_polynomial_sections(self):
        return self.global_sections()

    def homogeneous_polynomial_comparison(self):
        return _homogeneous_section_identity_comparison(self.global_sections())

    def section_multiplication(self, other):
        from sage_extensions.categories.modules.pure.modules import BilinearMap

        match other:
            case _ProductProjectiveLineBundleEngine() if other.projective_product() is self.projective_product():
                pass
            case _ProductProjectiveLineBundleEngine():
                raise ValueError(
                    f"cannot multiply sections of {self} and {other}: they are line bundles on different "
                    "products of projective spaces"
                )
            case _:
                raise TypeError(
                    f"cannot multiply sections of {self} and {other}: {other} is not a line bundle "
                    "O(d_1,...,d_r) on a product of projective spaces"
                )
        target_bundle = self.tensor_product(other)
        left = self.global_sections()
        right = other.global_sections()
        target = target_bundle.global_sections()
        target_by_exponents = {
            target.monomial_exponents(monomial): monomial
            for monomial in target.module_generating_set()
        }

        def product(left_monomial, right_monomial):
            exponents = tuple(
                tuple(a + b for a, b in zip(left_block, right_block, strict=True))
                for left_block, right_block in zip(
                    left.monomial_exponents(left_monomial),
                    right.monomial_exponents(right_monomial),
                    strict=True,
                )
            )
            return target.module_generator(target_by_exponents[exponents])

        return BilinearMap(left, right, target, product)

    def section_on_chart(self, section, choice):
        r"""Dehomogenize one global section on the standard affine atlas.

        On the chart where homogeneous coordinate ``x_{i,j_i}`` of each
        factor is nonzero, ``O(d_i)`` is trivialized by ``x_{i,j_i}^{d_i}``.
        Dividing a multihomogeneous monomial by those selected powers therefore
        replaces every selected coordinate by ``1`` and every other coordinate
        by the corresponding affine ratio. The result lies in the selected
        chart's rank-one module.
        """
        sections = self.global_sections()
        section = sections(section)
        coordinates = sections.framing_morphism().lift(section)
        atlas = self.gluing_datum()
        choice = atlas.normalize_chart_index(choice)
        factors = self.projective_product().factors()
        factor_labels = tuple(factors.index_set())
        positions = {label: position for position, label in enumerate(factor_labels)}
        chart = atlas.chart(choice)
        chart_ring = chart.coordinate_algebra()
        scalar_map = chart_ring.algebra_structure_morphism()
        local_coefficient = chart_ring.zero()
        for monomial in coordinates.support().domain():
            term = scalar_map(coordinates(monomial))
            blocks = sections.monomial_exponents(monomial)
            for label, block in zip(factor_labels, blocks, strict=True):
                selected = choice[positions[label]]
                factor = factors[label]
                projection = chart.projection(label).coordinate_algebra_morphism()
                for coordinate, exponent in enumerate(block):
                    if not exponent or coordinate == selected:
                        continue
                    term *= projection(factor._standard_chart_coordinate(selected, coordinate)) ** int(exponent)
            local_coefficient += term
        module = self.local_module(choice)
        return module.scalar_multiple(local_coefficient, _rank_one_generator(module))

    @cached_method
    def section_ring(self):
        from sage_extensions.categories.divisors.section_rings import SectionRings

        return SectionRings(self.scheme().scheme_base_ring())(self)

    def base_change(self, ring_map):
        return _product_projective_o(
            self.projective_product().base_change(ring_map),
            tuple(
                self.multidegree()[label]
                for label in self.multidegree().index_set()
            ),
            base_change_image=_LineBundleBaseChangeImage(self, ring_map),
        )

    def base_change_source_bundle(self):
        return _base_change_source_bundle(self)

    def base_change_projection(self):
        return _base_change_projection(self)

    def section_base_change_comparison(self):
        return _section_base_change_comparison_of(self)

    def pullback_compatible_section(self, section):
        r"""Pull a section of the source bundle back along this base change."""
        return _base_change_image(self).compatible_section(self, section)

    def _repr_(self):
        degrees = tuple(self.multidegree()[label] for label in self.multidegree().index_set())
        return f"O{degrees} on {self.projective_product()}"



class _ProductProjectiveSubschemeLineBundleEngine(_RestrictedLineBundleDescent):
    r"""The pullback of ``O(d_1,...,d_r)`` to a closed multiprojective subscheme."""

    def __init__(self, closed_subscheme, ambient_line_bundle, **rest) -> None:
        from sage_extensions.categories.schemes.schemes import (
            ClosedSubschemes,
            ProductProjectiveSpaces,
        )

        base = closed_subscheme.scheme_base_ring()
        if closed_subscheme not in ClosedSubschemes(base):
            raise TypeError(
                f"cannot restrict {ambient_line_bundle} to {closed_subscheme}: it is not a closed "
                f"subscheme over {base}"
            )
        ambient = closed_subscheme.inclusion().codomain()
        if ambient not in ProductProjectiveSpaces(base):
            raise TypeError(
                f"cannot form O_X(d_1,...,d_r) on {closed_subscheme}: it is a closed subscheme of "
                f"{ambient}, which is not a product of projective spaces over {base}"
            )
        match ambient_line_bundle:
            case _ProductProjectiveLineBundleEngine() if ambient_line_bundle.projective_product() is ambient:
                pass
            case _ProductProjectiveLineBundleEngine():
                raise ValueError(
                    f"cannot restrict {ambient_line_bundle} to {closed_subscheme}: the bundle lives on "
                    f"{ambient_line_bundle.projective_product()}, but the subscheme lies in {ambient}"
                )
            case _:
                raise TypeError(
                    f"cannot restrict {ambient_line_bundle} to {closed_subscheme}: it is not a line "
                    f"bundle O(d_1,...,d_r) on the product of projective spaces {ambient}"
                )
        self._scheme = closed_subscheme
        self._ambient_line_bundle = ambient_line_bundle
        self._pullback_morphism = closed_subscheme.inclusion()
        super().__init__(**rest)

    def scheme(self):
        return self._scheme

    def pullback_morphism(self):
        return self._pullback_morphism

    inclusion = pullback_morphism

    def ambient_line_bundle(self):
        return self._ambient_line_bundle

    def multidegree(self):
        return self.ambient_line_bundle().multidegree()

    def tensor_product(self, other):
        match other:
            case _ProductProjectiveSubschemeLineBundleEngine() if other.scheme() is self.scheme():
                pass
            case _ProductProjectiveSubschemeLineBundleEngine():
                raise ValueError(
                    f"cannot tensor {self} with {other}: they are line bundles on different schemes"
                )
            case _:
                raise TypeError(
                    f"cannot tensor {self} with {other}: {other} is not the restriction of "
                    "O(d_1,...,d_r) from a product of projective spaces"
                )
        return _product_projective_subscheme_line_bundle(
            self.scheme(),
            self.ambient_line_bundle().tensor_product(other.ambient_line_bundle()),
        )

    def tensor_power(self, exponent):
        exponent = _owned_integers()(exponent)
        if exponent == 1:
            return self
        return _product_projective_subscheme_line_bundle(
            self.scheme(),
            self.ambient_line_bundle().tensor_power(exponent),
        )

    def dual_sheaf(self):
        return _product_projective_subscheme_line_bundle(
            self.scheme(),
            self.ambient_line_bundle().dual_sheaf(),
        )

    def is_ample(self) -> bool:
        r"""Return a theorem-backed positive ampleness decision from the ambient product."""
        assert self.ambient_line_bundle().is_ample(), (
            f"cannot decide whether {self} is ample: ampleness is decided here only for restrictions "
            f"of an ample bundle, and {self.ambient_line_bundle()} is not ample"
        )
        return True

    def canonical_isomorphism_to(self, target):
        r"""Return the canonical comparison with an equal-multidegree presentation on this scheme."""
        match target:
            case _ProductProjectiveSubschemeLineBundleEngine() if target.scheme() is self.scheme():
                pass
            case _ProductProjectiveSubschemeLineBundleEngine():
                raise ValueError(
                    f"no isomorphism from {self} to {target}: they are line bundles on different schemes"
                )
            case _:
                raise TypeError(
                    f"cannot compare {self} with {target}: {target} is not the restriction of "
                    "O(d_1,...,d_r) from a product of projective spaces"
                )
        source_degrees = self.multidegree()
        target_degrees = target.multidegree()
        if source_degrees.index_set() is not target_degrees.index_set():
            raise ValueError(
                f"no canonical isomorphism from {self} to {target}: their multidegrees are indexed by "
                f"different factor sets {source_degrees.index_set()} and {target_degrees.index_set()}"
            )
        if any(
            source_degrees[label] != target_degrees[label]
            for label in source_degrees.index_set()
        ):
            raise ValueError(
                f"no canonical isomorphism from {self} to {target}: their multidegrees {source_degrees} "
                f"and {target_degrees} differ"
            )
        ambient = _chosen_trivialization_isomorphism(
            self.ambient_line_bundle(),
            target.ambient_line_bundle(),
        )
        sheaves = QuasiCoherentSheaves(self.scheme())
        forward = sheaves.Mor(self, target)(ambient.forward())
        inverse = sheaves.Mor(target, self)(ambient.inverse().forward())
        return sheaves.Core().Mor(self, target)(forward, inverse)

    def _repr_(self):
        degrees = tuple(
            self.multidegree()[label] for label in self.multidegree().index_set()
        )
        return f"O{degrees} restricted to {self.scheme()}"


def _line_bundle_identity_local_maps(source, target):
    r"""Return the chartwise basis identifications of two line bundles on one trivialization."""
    if source.gluing_datum() is not target.gluing_datum():
        raise ValueError(
            f"cannot identify {source} with {target} chart by chart: they are trivialized on "
            "different covers"
        )
    return {
        index: source.local_module(index).module_category().Mor(
            source.local_module(index),
            target.local_module(index),
        )(
            {
                next(iter(source.local_module(index).module_generating_set())):
                    _rank_one_generator(target.local_module(index))
            }
        )
        for index in source.gluing_datum().chart_index_set()
    }


def _line_bundle_compatible_section_map(source_datum, target_datum, local_map):
    r"""The map of compatible-section modules induced by chartwise linear maps."""
    source_sections = source_datum.compatible_sections()
    target_sections = target_datum.compatible_sections()
    charts = source_datum.chart_index_set()

    def image(section):
        return target_datum.compatible_section(
            {
                index: local_map(index)(source_datum.compatible_section_component(section, index))
                for index in charts
            }
        )

    return source_sections.module_category().Mor(source_sections, target_sections)._from_constructed_element_map(
        image, premises=tuple(local_map(index) for index in charts),
    )


class _ChosenTrivializationQuasiCoherentMorphismMethods:
    r"""A line-bundle sheaf morphism represented by compatible maps in one trivialization."""

    def __init__(self, parent, local_maps) -> None:
        source = parent.domain()
        target = parent.codomain()
        if source.gluing_datum() is not target.gluing_datum():
            raise ValueError(
                f"cannot build a morphism {source} -> {target} from local maps: the two line bundles "
                "are trivialized on different covers"
            )
        match (source, target):
            case (_DistinguishedCoverInvertibleSheafEngine(), _DistinguishedCoverInvertibleSheafEngine()):
                self._descent_morphism = source.gluing_datum().Mor(
                    target.gluing_datum()
                )(local_maps)
            case (_FiniteAtlasInvertibleSheafEngine(), _FiniteAtlasInvertibleSheafEngine()):
                source_sheaf = source.module_sheaf()
                target_sheaf = target.module_sheaf()
                self._descent_morphism = QuasiCoherentSheaves(source.scheme()).Mor(
                    source_sheaf,
                    target_sheaf,
                )(local_maps)
            case _:
                raise TypeError(
                    f"cannot build a morphism {source} -> {target} from local maps: the two line bundles "
                    "are not both glued on a distinguished affine cover or both on a finite affine atlas"
                )
        super().__init__(parent)

    def descent_morphism(self):
        return self._descent_morphism

    def local_map(self, index):
        return self.descent_morphism().local_map(index)

    @cached_method
    def global_sections_map(self):
        r"""Return the induced map on the compatible-section modules of the trivializations."""
        match self.domain():
            case _DistinguishedCoverInvertibleSheafEngine():
                source_datum = self.domain().gluing_datum()
                target_datum = self.codomain().gluing_datum()
            case _FiniteAtlasInvertibleSheafEngine():
                source_datum = self.domain().module_sheaf().gluing_datum()
                target_datum = self.codomain().module_sheaf().gluing_datum()
            case _:
                raise TypeError(
                    f"cannot compute the map on global sections induced by {self}: {self.domain()} is "
                    "not glued on a distinguished affine cover or a finite affine atlas"
                )
        return _line_bundle_compatible_section_map(source_datum, target_datum, self.local_map)

    def _richcmp_(self, other, op):
        r"""Compare the chart maps, preserving undecided equalities."""
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if not isinstance(other, _ChosenTrivializationQuasiCoherentMorphismMethods):
            return NotImplemented
        if self.domain() is not other.domain() or self.codomain() is not other.codomain():
            return op == op_NE
        decision = conjunction(
            self.local_map(index) == other.local_map(index)
            for index in self.domain().gluing_datum().chart_index_set()
        )
        return decision if op == op_EQ else negation(decision)

    __hash__ = None

    def __mul__(self, other):
        match other:
            case _ChosenTrivializationQuasiCoherentMorphismMethods():
                pass
            case _:
                return NotImplemented
        if other.codomain() is not self.domain():
            return NotImplemented
        return self.parent().mor_category().Mor(
            other.domain(),
            self.codomain(),
        )(
            {
                index: self.local_map(index) * other.local_map(index)
                for index in other.domain().gluing_datum().chart_index_set()
            }
        )


class _ChosenTrivializationQuasiCoherentMor(QuasiCoherentSheafMor):
    r"""The QCoh Mor of line bundles carrying one represented trivializing cover."""

    ElementMethods = _ChosenTrivializationQuasiCoherentMorphismMethods

    def _element_constructor_(self, local_maps):
        match local_maps:
            case _ChosenTrivializationQuasiCoherentMorphismMethods() if local_maps.parent() is self:
                return local_maps
            case _ChosenTrivializationQuasiCoherentMorphismMethods():
                raise TypeError(f"{local_maps} belongs to another Mor; apply the functor between the categories")
            case _:
                pass
        return self.element_class(self, local_maps)

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"no identity morphism from {self.domain()} to {self.codomain()}: the domain and "
                "codomain differ"
            )
        return self(_line_bundle_identity_local_maps(self.domain(), self.domain()))


def _chosen_trivialization_isomorphism(source, target):
    r"""Return the basis-preserving isomorphism of equal represented line-bundle trivializations."""
    sheaves = QuasiCoherentSheaves(source.scheme())
    forward = sheaves.Mor(source, target)(_line_bundle_identity_local_maps(source, target))
    inverse = sheaves.Mor(target, source)(_line_bundle_identity_local_maps(target, source))
    return sheaves.Core().Mor(source, target)(forward, inverse)


class _PullbackLineBundleQuasiCoherentMorphismMethods:
    r"""The pullback of an ambient line-bundle arrow along a closed immersion.

    Unexecuted vanishing along a coordinate hyperplane (Hartshorne, II.5.12)::

        sage: from dzack_research.preamble.all import *
        sage: P = ProjectiveSpaces(QQ)(1)
        sage: source = P.O(0); target = P.O(1)
        sage: forms = target.global_sections(); S = forms.homogeneous_coordinate_ring()
        sage: x0 = S.algebra_generator(P.variable_names()[0])
        sage: section = forms.section_from_homogeneous_polynomial(x0)
        sage: atlas = P.standard_affine_atlas()
        sage: local_maps = {i: source.local_module(i).Mor(target.local_module(i))({0: target.section_on_chart(section, i)}) for i in atlas.chart_indices()}
        sage: zero_maps = {i: source.local_module(i).Mor(target.local_module(i)).zero() for i in atlas.chart_indices()}
        sage: ambient = QuasiCoherentSheaves(P).Mor(source, target)
        sage: nonzero = ambient(local_maps); zero = ambient(zero_maps)
        sage: nonzero.local_map(0)(source.local_module(0).module_generator(0)) != target.local_module(0).zero()
        True
        sage: Z = P.closed_subscheme(x0)
        sage: pulled_source = Z.inclusion().module_pullback(source)
        sage: pulled_target = Z.inclusion().module_pullback(target)
        sage: hom = QuasiCoherentSheaves(Z).Mor(pulled_source, pulled_target)
        sage: restricted = hom(nonzero)
        sage: restricted == hom(zero)
        True
        sage: restricted.local_map(1)(pulled_source.local_module(1).module_generator(0)) == pulled_target.local_module(1).zero()
        True
        sage: datum = pulled_source.module_descent_datum()
        sage: unit = datum.compatible_section({i: pulled_source.local_module(i).module_generator(0) for i in datum.chart_indices()})
        sage: restricted.global_sections_map()(unit) == pulled_target.global_sections().zero()
        True
    """

    def __init__(self, parent, ambient_morphism) -> None:
        source = parent.domain()
        target = parent.codomain()
        if source.pullback_morphism() is not target.pullback_morphism():
            raise ValueError(
                f"cannot pull back a morphism to {source} -> {target}: the two line bundles are "
                f"pulled back along different morphisms {source.pullback_morphism()} and "
                f"{target.pullback_morphism()}"
            )
        ambient_source = source.ambient_line_bundle()
        ambient_target = target.ambient_line_bundle()
        ambient_sheaves = QuasiCoherentSheaves(ambient_source.scheme())
        self._ambient_morphism = ambient_sheaves.Mor(
            ambient_source,
            ambient_target,
        )(ambient_morphism)
        super().__init__(parent)

    def ambient_morphism(self):
        return self._ambient_morphism

    @cached_method
    def local_map(self, index):
        r"""The scalar extension of the ambient arrow on a restricted chart."""
        from sage_extensions.categories.schemes.gluing import FiniteAtlasModuleGluingMorphism

        source = self.domain()
        target = self.codomain()
        chart = source.gluing_datum().chart(index)
        return FiniteAtlasModuleGluingMorphism._base_changed_map(
            self.ambient_morphism().local_map(index),
            chart.left_projection().coordinate_algebra_morphism(),
            source.local_module(index), target.local_module(index),
        )

    @cached_method
    def descent_morphism(self):
        source = self.domain().module_descent_datum()
        target = self.codomain().module_descent_datum()
        return source.Mor(target)({index: self.local_map(index) for index in source.chart_indices()})

    @cached_method
    def global_sections_map(self):
        r"""The map on global sections induced by the restricted chart maps."""
        return _line_bundle_compatible_section_map(
            self.domain().module_descent_datum(),
            self.codomain().module_descent_datum(),
            self.local_map,
        )

    def _richcmp_(self, other, op):
        r"""Equality of restricted arrows is equality on the affine cover.

        Pullback need not be faithful: a nonzero ambient map may vanish on
        the closed subscheme. Compare the actual scalar-extended local maps
        (Hartshorne, II.5.12), retaining undecided equalities.
        """
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if not isinstance(other, _PullbackLineBundleQuasiCoherentMorphismMethods):
            return NotImplemented
        if self.domain() is not other.domain() or self.codomain() is not other.codomain():
            return op == op_NE
        decision = conjunction(
            self.local_map(index) == other.local_map(index)
            for index in self.domain().gluing_datum().chart_indices()
        )
        return decision if op == op_EQ else negation(decision)

    __hash__ = None

    def __mul__(self, other):
        match other:
            case _PullbackLineBundleQuasiCoherentMorphismMethods():
                pass
            case _:
                return NotImplemented
        if other.codomain() is not self.domain():
            return NotImplemented
        return self.parent().mor_category().Mor(
            other.domain(),
            self.codomain(),
        )(self.ambient_morphism() * other.ambient_morphism())


class _PullbackLineBundleQuasiCoherentMor(QuasiCoherentSheafMor):
    r"""The QCoh Mor represented by pullback from ambient line-bundle morphisms."""

    ElementMethods = _PullbackLineBundleQuasiCoherentMorphismMethods

    def _element_constructor_(self, ambient_morphism):
        match ambient_morphism:
            case _PullbackLineBundleQuasiCoherentMorphismMethods() if ambient_morphism.parent() is self:
                return ambient_morphism
            case _PullbackLineBundleQuasiCoherentMorphismMethods():
                raise TypeError(f"{ambient_morphism} belongs to another Mor; apply the functor between the categories")
            case _:
                pass
        return self.element_class(self, ambient_morphism)

    @object_level
    @cached_method
    def identity(self):
        if self.domain() is not self.codomain():
            raise ValueError(
                f"no identity morphism from {self.domain()} to {self.codomain()}: the domain and "
                "codomain differ"
            )
        ambient = self.domain().ambient_line_bundle()
        return self(QuasiCoherentSheaves(ambient.scheme()).Mor(ambient, ambient).identity())


def _product_projective_o_key(projective_product, degrees, base_change_image=None):
    from sage_extensions.categories.sets.indexed_families import IndexedFamily

    match degrees:
        case IndexedFamily():
            indices = id(degrees.index_set())
        case _:
            indices = None
    return (
        id(projective_product),
        indices,
        tuple(int(degree) for degree in degrees),
        id(base_change_image),
    )


@cached_function(key=_product_projective_o_key)
def _product_projective_o(projective_product, degrees, *, base_change_image=None):
    r"""Return ``O(degrees)`` on one represented product of projective spaces."""
    return _chosen_trivialization_object(
        projective_product,
        _ProductProjectiveLineBundleEngine,
        projective_product=projective_product,
        degrees=degrees,
        base_change_image=base_change_image,
    )


def _product_projective_subscheme_line_bundle(closed_subscheme, ambient_line_bundle):
    r"""Return the invertible pullback of a multiprojective line bundle."""
    return _invertible_sheaf_object(
        closed_subscheme,
        _ProductProjectiveSubschemeLineBundleEngine,
        closed_subscheme=closed_subscheme,
        ambient_line_bundle=ambient_line_bundle,
    )


__all__ = [
    # Realization engines are intentionally private; public objects are placed
    # through the quasi-coherent/invertible sheaf owners.
]
