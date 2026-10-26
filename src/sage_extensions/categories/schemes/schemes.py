r"""Owned categories and constructors for schemes over a base ring.

Every scheme a session receives is an object of its category, built by that
category's one entry (``CON-16``) and threaded through ``Schemes(R)`` down to
the owned root.  Each level stores only the datum it introduces:

* ``Schemes(R)`` the base ring ``R`` the scheme lies over, and the private
  Sage scheme realizing it when the construction has one;
* ``Schemes(R).Affine()`` the coordinate algebra ``A`` of ``Spec A``;
* ``AffineSpaces(R)`` and ``ProjectiveSpaces(R)`` nothing beyond the chosen
  coordinates their construction put into ``A`` or into the realization;
* a subobject category ``ClosedEmbeddings(X)`` or ``OpenImmersions(X)`` the
  codomain ``X`` and the defining datum of the inclusion into it, from which
  the inclusion arrow is built once the subobject exists;
* ``ClosedEmbeddings(X)`` the family of equations cutting the subscheme out;
* ``ProductSchemes(R)`` the indexed family of factors and the defining data
  of the projections; ``FiberProductSchemes(R)`` the selected pullback
  construction.

The Sage scheme that realizes a represented scheme is a private engine
(``OWN-06``).  It is computed by the construction that knows it -- ``Spec``
of the coordinate algebra's engine, Sage's projective space on the chosen
coordinates, the Sage subscheme cut out by the equations -- and passed as
construction data.  A scheme presented without one, a glued scheme, answers
everything its data determine and asserts that frontier where a native
computation is asked of it.

Membership is placement at construction (``CAT-23``).  A scheme over ``R'``
is a scheme over ``R`` only through the restriction-of-base functor along a
ring map ``R -> R'`` (``CAT-16``), which ``_scheme_mor_category`` applies
when an arrow joins schemes over two bases of one scalar tower.
"""

from itertools import combinations
from itertools import product as cartesian_product

from sage.categories.category import Category
from sage.categories.category_with_axiom import all_axioms
from sage.categories.morphism import Morphism
from sage.categories.rings import Rings as _SageRings
from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.integer import Integer as SageInteger
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.polynomial.multi_polynomial_ring_base import MPolynomialRing_base
from sage.rings.polynomial.polynomial_ring import PolynomialRing_generic
from sage.schemes.affine.affine_space import AffineSpace as _SageAffineSpace
from sage.schemes.generic.algebraic_scheme import (
    AlgebraicScheme_quasi as _SageAlgebraicSchemeQuasi,
)
from sage.schemes.generic.algebraic_scheme import (
    AlgebraicScheme_subscheme as _SageAlgebraicSchemeSubscheme,
)
from sage.schemes.generic.morphism import SchemeMorphism as _SageSchemeMorphism
from sage.schemes.generic.morphism import (
    SchemeMorphism_id as _SageSchemeMorphismIdentity,
)
from sage.schemes.generic.morphism import (
    SchemeMorphism_polynomial as _SageSchemeMorphismPolynomial,
)
from sage.schemes.generic.morphism import SchemeMorphism_spec as _SageSchemeMorphismSpec
from sage.schemes.generic.scheme import AffineScheme as _SageAffineScheme
from sage.schemes.product_projective.space import (
    ProductProjectiveSpaces as _SageProductProjectiveSpaces,
)
from sage.schemes.projective.projective_space import (
    ProjectiveSpace as _SageProjectiveSpace,
)
from sage.structure.element import parent as element_parent

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoricalMor,
    _MonoCategoryOf,
)
from sage_extensions.categories.abstract_categories.mor_foundation import (
    CategoricalArrow,
    object_level,
)
from sage_extensions.categories.abstract_categories.objects import (
    OwnedCategory,
    OwnedParameterizedCategory,
)
from sage_extensions.categories.abstract_categories.products import (
    _finite_factor_family,
)
from sage_extensions.categories.algebras.algebras import (
    Algebras,
    _engine_algebra_morphism,
)
from sage_extensions.categories.algebras.finitely_presented_algebras import (
    AlgebrasWithChosenFinitePresentation,
)
from sage_extensions.categories.algebras.free_algebras import (
    SymmetricAlgebras,
)
from sage_extensions.categories.modules.pure.modules import BilinearMap
from sage_extensions.categories.rings.commutative_algebra import (
    QuotientRings,
    _commutative_algebra_with_structure,
)
from sage_extensions.categories.rings.ring_foundation import (
    LocalizationRings,
    OwnedCategoryOverBaseRing,
    OwnedFields,
    OwnedIntegralDomains,
    OwnedPrincipalIdealDomains,
    OwnedRings,
    _engine_element,
    _engine_numeral,
    _engine_ring,
    _own_ring,
    _owned_complex_field,
    _owned_engine_element,
    _owned_integers,
    _owned_rationals,
    _owned_ring,
    _proper_restriction_base_ring,
    _ring_morphisms_equal,
    _selected_engine_ring_morphism,
)
from sage_extensions.categories.schemes.ringed_spaces import (
    LocallyRingedMorCategoryConstruction,
    LocallyRingedSpaces,
    PresheafObjects,
    QuasiCoherentSheaves,
)
from sage_extensions.categories.sets.finite_families import finite_family
from sage_extensions.categories.sets.indexed_families import (
    IndexedFamily,
    indexed_family,
)
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.lexicon.algebra import AlgebraHomomorphism
from sage_extensions.lexicon.category_theory import (
    ElementOfCategoryObject,
    ObjectOfCategory,
)
from sage_extensions.logic import AtomicProposition, conjunction, negation
from sage_extensions.owned_category import _object_of, owned_category_join
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.refine import RealizationHook

for _scheme_axiom in (
    "Affine",
    "QuasiAffine",
    "Projective",
    "Proper",
    "QuasiProjective",
    "Separated",
    "FiniteType",
    "LocallyNoetherian",
    "Integral",
    "Normal",
    "CalabiYau",
    "K3",
    "DelPezzo",
):
    if _scheme_axiom not in all_axioms:
        all_axioms.add(_scheme_axiom)


# ---------------------------------------------------------------------------
# Private engine adapters (OWN-06).
#
# Semantic operation: realize an owned scheme, scheme morphism or polynomial
# datum in Sage's scheme library and raise the results.  Owning callers: the
# scheme categories of this module.  Upstream operations: Sage's
# ``AffineScheme``, ``AffineSpace``, ``ProjectiveSpace``,
# ``ProductProjectiveSpaces``, ``AlgebraicScheme_subscheme`` and the scheme
# Mor objects of ``sage.schemes.generic.Mor``.  Every inspection of a Sage
# scheme or Sage morphism class is one of the functions in this block.
# ---------------------------------------------------------------------------


def _engine_scheme(scheme):
    r"""The private Sage scheme ``scheme`` computes in.

    It was computed from the owned datum by the construction that built
    ``scheme`` and stored at the ``Schemes(R)`` level; a scheme presented
    without a Sage realization asserts that frontier here.
    """
    return scheme._scheme_engine()


def _is_gluing_realization(realization) -> bool:
    r"""Whether the ``scheme_engine`` of a scheme is the realization of an affine gluing datum.

    The ``Schemes(R)`` level holds one private realization: a Sage scheme, or
    ``schemes.gluing``'s realization of a scheme glued from an affine gluing
    datum (Stacks, Tag 01JA).  Which of the two it is, is a representation
    question, answered here and nowhere else.
    """
    from sage_extensions.categories.schemes.gluing import _GluedScheme

    match realization:
        case _GluedScheme():
            return True
        case _:
            return False


def _native_scheme_mor(domain, codomain):
    r"""Sage's scheme Hom between the engines of two owned schemes."""
    return _engine_scheme(domain)._Hom_(_engine_scheme(codomain))


def _engine_scheme_morphism(morphism):
    r"""Lower one owned scheme morphism to its selected private Sage map.

    Protected scheme contract (OWN-05--OWN-07). The ordinary scheme API never
    returns this value. Callers are the scheme-owner adapters in this module
    plus the toric divisor-pullback adapter, which must invoke Sage on the
    represented native scheme. The input remains the owned morphism; the raw
    Sage map is consumed inside that computation and never becomes a public
    result or a defining datum of another mathematical subsystem.
    """
    return morphism._engine_morphism_crossing()


def _engine_defining_polynomials(native):
    r"""The coordinate polynomials of a Sage polynomial scheme morphism.

    Sage represents a morphism between affine or projective spaces by the
    polynomials giving its coordinates, and the identity as its own class
    carrying none; both are read here.
    """
    match native:
        case _SageSchemeMorphismIdentity():
            return tuple(native.domain().coordinate_ring().gens())
        case _SageSchemeMorphismPolynomial():
            return tuple(native.defining_polynomials())
        case _:
            assert False, (
                f"{native} is not represented by coordinate polynomials, so it has no "
                "homogeneous coordinate data to read"
            )


def _engine_coordinate_pullback_of(native, domain_algebra, codomain_algebra):
    r"""The owned pullback ``O(Y) -> O(X)`` of a Sage morphism ``X -> Y`` of affine engines.

    A morphism of affine schemes is its pullback on coordinate algebras.  Sage
    spells that map three ways: the identity, ``Spec`` of a ring morphism, and
    a polynomial map between affine spaces, whose pullback sends the
    coordinate of the target to the polynomial giving it.
    """
    match native:
        case _SageSchemeMorphismIdentity():
            return codomain_algebra.Mor(domain_algebra).identity()
        case _SageSchemeMorphismSpec():
            return codomain_algebra.Mor(domain_algebra)._from_engine_morphism(
                native.ring_homomorphism()
            )
        case _SageSchemeMorphismPolynomial():
            return codomain_algebra.Mor(domain_algebra)._from_engine_morphism(
                _engine_ring(codomain_algebra).hom(
                    list(native.defining_polynomials()),
                    _engine_ring(domain_algebra),
                )
            )
        case _:
            assert False, (
                f"{native} is not a Sage morphism of affine schemes with a readable pullback"
            )


@cached_function(
    key=lambda engine_polynomial_ring, base: (
        id(base),
        base,
        tuple(engine_polynomial_ring.variable_names()),
    )
)
def _engine_polynomial_algebra(engine_polynomial_ring, base):
    r"""The owned polynomial algebra over ``base`` whose engine is a Sage polynomial ring.

    Affine and projective spaces present their coordinates through Sage's
    polynomial rings; this is the one place such a ring is raised to the owned
    free, graded free and symmetric algebra it is.  Cache by the owned base
    identity and ordered variable names, rather than by the engine ring's
    equality: repeated adapters for the same coordinate presentation must
    retain one selected variable set and hence one symmetric-algebra parent.
    It is the symmetric algebra over the owned ``base`` itself: raising the
    engine's own base ring a second time would give a different scalar ring.
    """
    from sage_extensions.categories.algebras.free_algebras import (
        _polynomial_ring,
    )

    return _polynomial_ring(base, tuple(engine_polynomial_ring.variable_names()))


def _engine_affine_spectrum(algebra, base):
    r"""Sage's ``Spec A`` over ``Spec R`` for the engines of ``A`` and ``R``.

    ``Spec R`` over itself is the terminal ``R``-scheme.  Sage's schemes over
    ``R`` name ``Spec(R)`` over ``ZZ`` as their base scheme
    (``Scheme.base_scheme``, ``sage/schemes/generic/scheme.py``), so the
    terminal scheme computes in that object and the engine structure maps of
    ``R``-schemes land in it.
    """
    match algebra is base:
        case True:
            return _SageAffineScheme(_engine_ring(algebra))
        case False:
            return _SageAffineScheme(_engine_ring(algebra), _engine_ring(base))


def _engine_coercion_agreeing_on(pullback, determining):
    r"""The canonical Sage coercion realizing ``pullback``, checked on ``determining``.

    ``determining`` is a set of elements of the source on which ring maps out
    of the source are determined: the polynomial ring on them maps to the
    source by an epimorphism of rings.  So agreement there is agreement
    everywhere, so the coercion is an admissible realization exactly
    when it exists and matches the owned morphism there.
    """
    source = pullback.domain()
    target = pullback.codomain()
    engine_morphism = _engine_ring(target).coerce_map_from(_engine_ring(source))
    assert engine_morphism is not None, (
        f"cannot compute with the coordinate pullback {pullback} in Sage: Sage has no canonical "
        f"map from {source} to {target}, and {source} has no chosen finite set of algebra "
        "generators from which to build one"
    )
    assert all(
        engine_morphism(_engine_element(source, value))
        == _engine_element(target, pullback(value))
        for value in determining
    ), (
        f"cannot compute with the coordinate pullback {pullback} in Sage: Sage's canonical map "
        f"from {source} to {target} differs from it on elements that determine maps out of {source}"
    )
    return engine_morphism


def _engine_coordinate_pullback(pullback):
    r"""The private Sage ring map realizing one coordinate pullback.

    A framed source rebuilds the native map from the images of its algebra
    generators through the algebra bridge.  A localization has no algebra
    generating family, and a map out of ``S^{-1}A`` is determined by its
    restriction along ``A -> S^{-1}A``, so its realization is the canonical
    coercion checked on the family of the framed algebra at the foot of the
    localization tower.  Any other source supplies the realization its ring
    morphism selected when it was built.
    """
    source = pullback.domain()
    base = source.base_ring()
    # Declared engine adapter: a selected native ring map includes its own
    # coefficient map, which rebuilding an R-algebra map would erase.
    native = _selected_engine_ring_morphism(pullback)
    if native is not None:
        return native
    match source:
        case _ if source in LocalizationRings():
            determining = _elements_determining_maps_out_of(source, base)
            assert determining is not None, (
                f"cannot compute with the coordinate pullback {pullback} in Sage: no finite family of "
                f"elements determines the ring maps out of the localization {source} over {base}"
            )
            return _engine_coercion_agreeing_on(pullback, determining)
        case _ if source.is_framed_algebra():
            return _engine_algebra_morphism(pullback)
        case _:
            from sage_extensions.categories.functors.algebra_scalar_change import (
                _engine_ring_map,
            )

            return _engine_ring_map(pullback)


def _polynomial_exponents(exponent, variable_count: int) -> tuple[int, ...]:
    r"""Normalize a Sage polynomial dictionary exponent to one exponent per variable.

    Sage keys a univariate polynomial's dictionary by an integer and a
    multivariate one by an exponent tuple; both are read here.
    """
    match exponent:
        case int() | SageInteger():
            assert variable_count == 1, (
                f"cannot read the exponent {exponent} as one exponent per variable: an integer exponent "
                f"belongs to a polynomial in one variable, but this polynomial ring has {variable_count} variables"
            )
            return (int(exponent),)
        case _:
            return tuple(int(value) for value in exponent)


def _copy_polynomial_by_exponents(
    polynomial,
    target_ring,
    target_variables,
) -> ElementOfCategoryObject:
    r"""Copy a Sage polynomial onto name-independent variables by its exponent dictionary."""
    source = polynomial.parent()
    variable_count = len(source.gens())
    assert len(target_variables) == variable_count, (
        f"cannot copy the polynomial {polynomial} into {target_ring}: it is a polynomial in "
        f"{variable_count} variables, but {len(target_variables)} target variables were given"
    )
    result = target_ring.zero()
    for exponent, coefficient in polynomial.dict().items():
        term = target_ring(coefficient)
        for variable, power in zip(
            target_variables,
            _polynomial_exponents(exponent, variable_count),
            strict=True,
        ):
            term *= variable**power
        result += term
    return result


def _evaluate_owned_homogeneous_polynomial_on_coordinates(
    polynomial,
    polynomial_ring,
    coordinates,
    *,
    coefficient_map=None,
):
    r"""Evaluate one owned homogeneous polynomial on an owned coordinate family.

    The scalar coefficients are carried into the ring of the coordinates by
    its algebra structure morphism, so the substitution is an ``R``-algebra
    map and never reads a coefficient off the target engine.
    """
    polynomial = polynomial_ring(polynomial)
    labels = tuple(polynomial_ring.algebra_generating_set())
    coordinates = tuple(coordinates)
    assert len(coordinates) == len(labels), (
        f"cannot evaluate {polynomial} at the coordinates {coordinates}: {polynomial_ring} has "
        f"{len(labels)} variables, but {len(coordinates)} coordinates were given"
    )
    source_ring = coordinates[0].parent()
    assert all(coordinate.parent() is source_ring for coordinate in coordinates), (
        f"cannot evaluate {polynomial} at the coordinates {coordinates}: the coordinates do not "
        f"all lie in one ring (the first lies in {source_ring})"
    )
    base = polynomial_ring.base_ring()
    scalar_map = (
        _restriction_to_base(source_ring, base)
        if coefficient_map is None
        else coefficient_map
    )
    assert scalar_map.domain() is base and scalar_map.codomain() is source_ring, (
        f"cannot evaluate {polynomial} at the coordinates {coordinates}: the map on coefficients "
        f"{scalar_map} must be a ring map {base} -> {source_ring}, but it is "
        f"{scalar_map.domain()} -> {scalar_map.codomain()}"
    )
    engine = _engine_ring(polynomial_ring)
    engine_base = _engine_ring(base)
    backend = engine(_engine_element(polynomial_ring, polynomial))
    result = source_ring.zero()
    for exponent, coefficient in backend.monomial_coefficients().items():
        powers = _polynomial_exponents(exponent, len(labels))
        term = scalar_map(_owned_engine_element(base, engine_base(coefficient)))
        for coordinate, power in zip(coordinates, powers, strict=True):
            term *= coordinate**power
        result += term
    return source_ring(result)


def _evaluate_polynomial_in_algebra(
    polynomial,
    algebra,
) -> ElementOfCategoryObject:
    r"""Evaluate an engine polynomial on the chosen algebra generators of ``algebra``."""
    labels = tuple(algebra.algebra_generating_set())
    source = polynomial.parent()
    assert len(source.gens()) == len(labels), (
        f"cannot evaluate {polynomial} on the algebra generators of {algebra}: it is a polynomial "
        f"in {len(source.gens())} variables, but {algebra} has {len(labels)} chosen algebra generators"
    )
    base = algebra.base_ring()
    engine_base = _engine_ring(base)
    structure = algebra.algebra_structure_morphism()
    result = algebra.zero()
    for exponent, coefficient in polynomial.dict().items():
        powers = _polynomial_exponents(exponent, len(labels))
        term = structure(_owned_engine_element(base, engine_base(coefficient)))
        for label, power in zip(labels, powers, strict=True):
            term *= algebra.algebra_generator(label) ** power
        result += term
    return algebra(result)


# ---------------------------------------------------------------------------
# Maps out of algebras: the finite families on which two maps already agree.
# ---------------------------------------------------------------------------


def _localization_refines(finer, coarser) -> bool:
    r"""Whether every element ``coarser`` inverts is a unit in ``finer``.

    Both are localizations of one ring, so this is exactly the condition under
    which the canonical map ``coarser -> finer`` exists.
    """
    unit = finer.localization_map()
    return all(
        unit(generator).is_unit()
        for generator in coarser.localization_submonoid().monoid_generators()
    )


def _elements_determining_maps_out_of(algebra, base):
    r"""Elements of ``algebra`` on which two base-ring maps out of it already agree.

    A map out of a framed ``R``-algebra is fixed by the images of its algebra
    generators together with its restriction to ``R``.  When the represented
    scheme base is a smaller ring ``k``, that restriction is determined
    recursively by a finite family for ``R/k``, carried into the algebra by its
    structure morphism.  A map out of ``S^{-1}A`` is fixed by its restriction
    along ``A -> S^{-1}A``, so localization towers recurse to the framed
    algebra at their foot.  So the polynomial ring over ``base`` on the
    returned elements maps to ``algebra`` by an epimorphism of rings.  ``None``
    states that no such finite set of elements is represented.
    """
    if algebra is base:
        return ()
    match algebra:
        case _ if algebra.is_framed_algebra():
            algebra_base = algebra.base_ring()
            labels = algebra.algebra_generating_set()
            if not labels.cardinality().is_finite():
                return None
            generators = tuple(algebra.algebra_generator(label) for label in labels)
            if algebra_base is base:
                return generators
            scalar_generators = _elements_determining_maps_out_of(algebra_base, base)
            if scalar_generators is None:
                return None
            structure = algebra.algebra_structure_morphism()
            return generators + tuple(
                structure(element) for element in scalar_generators
            )
        case _ if algebra in LocalizationRings():
            if base in LocalizationRings():
                if algebra.localization_source() is base:
                    return ()
                if (
                    algebra.localization_source() is base.localization_source()
                    and _localization_refines(algebra, base)
                ):
                    return ()
            below = _elements_determining_maps_out_of(
                algebra.localization_source(), base
            )
            if below is None:
                return None
            localization_map = algebra.localization_map()
            return tuple(localization_map(element) for element in below)
        case _:
            return None


def _algebra_generator_label(algebra, generator):
    r"""The label of an element that is one of the algebra's chosen generators."""
    label = next(
        (
            label
            for label in algebra.algebra_generating_set()
            if algebra.algebra_generator(label) == generator
        ),
        None,
    )
    assert label is not None, (
        f"{generator} is not a chosen algebra generator of {algebra}"
    )
    return label


# ---------------------------------------------------------------------------
# Morphisms of schemes.
# ---------------------------------------------------------------------------


class SchemeConeMorphismConstruction:
    r"""The selected universal-cone target and legs defining an induced map.

    A map into a product or a fibre product is the factorization of a cone
    through its universal cone; the target and the legs are that cone, and
    composing the factorization with a projection returns the leg.
    """

    def __init__(self, target, legs, projections) -> None:
        self._target = target
        self._legs = legs
        self._projection_legs = tuple(zip(projections, legs, strict=True))

    def target(self):
        return self._target

    def legs(self):
        return self._legs

    def leg_of_projection(self, projection):
        r"""The leg of this particular universal cone at ``projection``.

        One scheme may carry both a product and a pullback construction.
        The projections, not its category membership, select the cone.
        """
        return next(
            (leg for arrow, leg in self._projection_legs if arrow is projection), None
        )

    def image_of(self, image):
        r"""Return ``image`` retaining this cone as the datum it was induced by."""
        return image.with_cone_construction(self)


class SchemeMorphismMethods:
    r"""A morphism of owned schemes, an element of the owned Mor of its endpoints.

    The defining datum is one of: the coordinate pullback ``O(Y) -> O(X)``
    between affine endpoints; homogeneous coordinates into a projective space
    (:class:`_ProjectiveCoordinateMorphism`); or a native Sage morphism
    between the engines of the endpoints.  The endpoints are always the owned
    schemes of the Mor, never read off the engine.  A morphism induced by a
    universal cone additionally retains that cone.

    Protected contract, used only by composition and equality inside this
    class family: :meth:`_represented_coordinate_pullback` returns the
    pullback datum or ``None``, and :meth:`_represented_point_coordinates`
    the selected point coordinates or ``None``.
    """

    _native_morphism = None
    _coordinate_pullback = None
    _scalar_pullback = None
    _cone_construction = None
    _point_coordinates = None
    _closed_complement = None
    _homogeneous_coordinates = None
    _coefficient_map = None
    _standard_projective_chart_embedding = False
    _multiprojective_chart_embedding = False
    _gluing_datum = None
    _gluing_chart_index = None
    _gluing_role = None
    _gluing_chart_map = None
    _finite_atlas = None
    _atlas_local_maps = None
    _glued_local_maps = None
    _relative_projectivization_source_sheaf = None
    _relative_projectivization_comparison = None
    _relative_projectivization_role = None
    _relative_projectivization_underlying_projection = None
    _relative_projectivization_sheaf_morphism = None
    _toric_lattice_morphism = None
    _toric_chart_targets = None
    _toric_chart_pullbacks = None
    _affine_quotient_base_change_datum = None

    def __init__(
        self,
        parent,
        native_morphism,
        *,
        mor,
        pullback=None,
        scalar_pullback=None,
        cone_construction=None,
        point_coordinates=None,
        closed_complement=None,
        homogeneous_coordinates=None,
        coefficient_map=None,
        standard_projective_chart_embedding=False,
        multiprojective_chart_embedding=False,
        gluing_datum=None,
        gluing_chart_index=None,
        gluing_role=None,
        gluing_chart_map=None,
        finite_atlas=None,
        atlas_local_maps=None,
        glued_local_maps=None,
        relative_projectivization_source_sheaf=None,
        relative_projectivization_comparison=None,
        relative_projectivization_role=None,
        relative_projectivization_underlying_projection=None,
        relative_projectivization_sheaf_morphism=None,
        toric_lattice_morphism=None,
        toric_chart_targets=None,
        toric_chart_pullbacks=None,
        affine_quotient_base_change_data=None,
    ) -> None:
        self._native_morphism = native_morphism
        self._coordinate_pullback = pullback
        self._scalar_pullback = scalar_pullback
        self._cone_construction = cone_construction
        self._point_coordinates = point_coordinates
        self._closed_complement = closed_complement
        self._homogeneous_coordinates = (
            None
            if homogeneous_coordinates is None
            else finite_family(
                tuple(homogeneous_coordinates), name="Homogeneous coordinates"
            )
        )
        self._coefficient_map = coefficient_map
        self._standard_projective_chart_embedding = standard_projective_chart_embedding
        self._multiprojective_chart_embedding = multiprojective_chart_embedding
        self._gluing_datum = gluing_datum
        self._gluing_chart_index = gluing_chart_index
        self._gluing_role = gluing_role
        self._gluing_chart_map = gluing_chart_map
        self._finite_atlas = finite_atlas
        self._atlas_local_maps = atlas_local_maps
        self._glued_local_maps = glued_local_maps
        self._relative_projectivization_source_sheaf = (
            relative_projectivization_source_sheaf
        )
        self._relative_projectivization_comparison = (
            relative_projectivization_comparison
        )
        self._relative_projectivization_role = relative_projectivization_role
        self._relative_projectivization_underlying_projection = (
            relative_projectivization_underlying_projection
        )
        self._relative_projectivization_sheaf_morphism = (
            relative_projectivization_sheaf_morphism
        )
        self._toric_lattice_morphism = toric_lattice_morphism
        self._toric_chart_targets = toric_chart_targets
        self._toric_chart_pullbacks = toric_chart_pullbacks
        self._affine_quotient_base_change_datum = affine_quotient_base_change_data
        # A morphism of locally ringed spaces is a pair (f, f^#); its continuous
        # map f is the point map this arrow defines in ``_call_`` (contraction of
        # primes along the coordinate pullback). The set map is lazy: it stores
        # the callable and evaluates nothing at construction.
        super().__init__(
            parent,
            Sets().Mor(parent.domain(), parent.codomain())(lambda point: self(point)),
        )

    def with_cone_construction(self, construction):
        r"""This morphism, retaining the universal cone it was induced by."""
        return self.parent().element_class(
            self.parent(),
            self._native_morphism,
            mor=self.parent(),
            pullback=self._coordinate_pullback,
            scalar_pullback=self._scalar_pullback,
            cone_construction=construction,
            point_coordinates=self._point_coordinates,
            closed_complement=self._closed_complement,
            homogeneous_coordinates=self._homogeneous_coordinates,
            coefficient_map=self._coefficient_map,
            standard_projective_chart_embedding=self._standard_projective_chart_embedding,
            multiprojective_chart_embedding=self._multiprojective_chart_embedding,
            gluing_datum=self._gluing_datum,
            gluing_chart_index=self._gluing_chart_index,
            gluing_role=self._gluing_role,
            gluing_chart_map=self._gluing_chart_map,
            finite_atlas=self._finite_atlas,
            atlas_local_maps=self._atlas_local_maps,
            glued_local_maps=self._glued_local_maps,
            relative_projectivization_source_sheaf=self._relative_projectivization_source_sheaf,
            relative_projectivization_comparison=self._relative_projectivization_comparison,
            relative_projectivization_role=self._relative_projectivization_role,
            relative_projectivization_underlying_projection=self._relative_projectivization_underlying_projection,
            relative_projectivization_sheaf_morphism=self._relative_projectivization_sheaf_morphism,
            toric_lattice_morphism=self._toric_lattice_morphism,
            toric_chart_targets=self._toric_chart_targets,
            toric_chart_pullbacks=self._toric_chart_pullbacks,
            affine_quotient_base_change_data=self._affine_quotient_base_change_datum,
        )

    def gluing_datum(self):
        if self._gluing_datum is None:
            raise AttributeError(f"{self} is not defined by a selected scheme gluing")
        return self._gluing_datum

    def chart_index(self):
        if self._gluing_chart_index is None:
            raise AttributeError(f"{self} has no selected gluing chart")
        return self._gluing_chart_index

    def open_image(self):
        if self._gluing_role != "chart_embedding":
            raise AttributeError(f"{self} is not a chart embedding")
        return self.gluing_datum().chart_image(self.chart_index())

    def chart_isomorphism(self):
        if self._gluing_role != "chart_embedding":
            raise AttributeError(f"{self} is not a chart embedding")
        return self.gluing_datum().chart_isomorphism(self.chart_index())

    def open_inclusion(self):
        return self.open_image().inclusion()

    def chart_embedding(self):
        if self._gluing_role != "chart_map":
            raise AttributeError(f"{self} is not a map through a selected gluing chart")
        return self.gluing_datum().chart_embedding(self.chart_index())

    def chart_map(self):
        if self._gluing_role != "chart_map":
            raise AttributeError(
                f"{self} is not represented by a map through a selected gluing chart"
            )
        return self._gluing_chart_map

    def atlas(self):
        if self._gluing_role != "finite_atlas":
            raise AttributeError(
                f"{self} is not represented on a selected finite affine atlas"
            )
        return self._finite_atlas

    def local_maps(self):
        if self._gluing_role != "finite_atlas":
            raise AttributeError(
                f"{self} is not represented by local maps on a finite atlas"
            )
        return self._atlas_local_maps

    def local_map(self, index):
        if self._toric_lattice_morphism is not None:
            target_embedding = (
                self.codomain().gluing_datum().chart_embedding(self.chart_target(index))
            )
            return target_embedding * self.chart_morphism(index)
        return self.local_maps()[self.atlas().normalize_chart_index(index)]

    def glued_local_maps(self):
        if self._gluing_role != "glued_domain":
            raise AttributeError(
                f"{self} is not represented by local maps on a glued domain"
            )
        return self._glued_local_maps

    def glued_local_map(self, index):
        return self.glued_local_maps()[self.gluing_datum().normalize_chart_index(index)]

    def source_sheaf(self):
        if self._relative_projectivization_source_sheaf is None:
            raise AttributeError(
                f"{self} is not a relative-projectivization projection"
            )
        return self._relative_projectivization_source_sheaf

    def comparison(self):
        if self._relative_projectivization_comparison is None:
            raise AttributeError(
                f"{self} is not defined by a relative-projectivization comparison"
            )
        return self._relative_projectivization_comparison

    def underlying_projection(self):
        if self._relative_projectivization_underlying_projection is None:
            raise AttributeError(f"{self} has no selected underlying base projection")
        return self._relative_projectivization_underlying_projection

    def sheaf_morphism(self):
        if self._relative_projectivization_sheaf_morphism is None:
            raise AttributeError(
                f"{self} is not defined by a relative-projectivization sheaf morphism"
            )
        return self._relative_projectivization_sheaf_morphism

    def lattice_morphism(self):
        if self._toric_lattice_morphism is None:
            raise AttributeError(f"{self} is not a represented toric morphism")
        return self._toric_lattice_morphism

    def chart_target(self, source_cone):
        if self._toric_chart_targets is None:
            raise AttributeError(f"{self} has no toric chart targets")
        return self._toric_chart_targets.value(source_cone)

    def chart_pullback(self, source_cone):
        if self._toric_chart_pullbacks is None:
            raise AttributeError(f"{self} has no toric chart pullbacks")
        return self._toric_chart_pullbacks.value(source_cone)

    def chart_morphism(self, source_cone):
        source_chart = self.domain().affine_chart(source_cone)
        target_chart = self.codomain().affine_chart(self.chart_target(source_cone))
        return source_chart.Mor(target_chart)(self.chart_pullback(source_cone))

    def _affine_quotient_base_change_data(self):
        if self._affine_quotient_base_change_datum is None:
            raise AttributeError(
                f"{self} is not an invariant-quotient base-change comparison"
            )
        return self._affine_quotient_base_change_datum

    def source_acted_scheme(self):
        return self._affine_quotient_base_change_data()["acted_scheme"]

    def ring_map(self):
        return self._affine_quotient_base_change_data()["ring_map"]

    def base_changed_acted_scheme(self):
        return self._affine_quotient_base_change_data()["changed_acted_scheme"]

    def quotient_after_base_change(self):
        return self.base_changed_acted_scheme().affine_quotient()

    def base_change_after_quotient(self):
        return self._affine_quotient_base_change_data()["base_changed_old_quotient"]

    def comparison_morphism(self):
        return self

    def reynolds_hypothesis_holds(self) -> bool:
        from sage_extensions.categories.rings.ring_foundation import (
            OwnedFields,
            _owned_ring,
        )

        source = _owned_ring(self.ring_map().domain())
        target = _owned_ring(self.ring_map().codomain())
        if source not in OwnedFields() or target not in OwnedFields():
            return False
        group = self.base_changed_acted_scheme().acting_group()
        return group.is_finite() is True and group.order_is_invertible_in(target)

    @cached_method
    def reynolds_isomorphism(self):
        from sage_extensions.categories.rings.ring_foundation import (
            _engine_element,
            _engine_ring,
        )
        from sage_extensions.categories.schemes.quotients import (
            _evaluate_polynomial_in_algebra,
        )

        assert self.reynolds_hypothesis_holds() is True, (
            f"the comparison X_(k')/G -> (X/G)_(k') for {self.source_acted_scheme()} along "
            f"{self.ring_map()} is proved an isomorphism only when the acting group "
            f"{self.base_changed_acted_scheme().acting_group()} is finite and its order is invertible "
            "in the target field (Reynolds operator)"
        )
        forward = self.comparison_morphism()
        source_quotient = self.quotient_after_base_change()
        target_quotient = self.base_change_after_quotient()
        changed_acted = self.base_changed_acted_scheme()
        changed_source_algebra = changed_acted.coordinate_algebra()
        changed_invariants = source_quotient.coordinate_algebra()
        changed_old_invariants = target_quotient.coordinate_algebra()
        comparison_pullback = forward.coordinate_algebra_morphism()
        invariant_inclusion = changed_acted.invariant_algebra_inclusion()
        engine_source = _engine_ring(changed_source_algebra)
        old_generator_images = tuple(
            engine_source(
                _engine_element(
                    changed_source_algebra,
                    invariant_inclusion(
                        comparison_pullback(
                            changed_old_invariants.algebra_generator(label)
                        )
                    ),
                )
            )
            for label in changed_old_invariants.algebra_generating_set()
        )
        inverse_images = {}
        for label in changed_invariants.algebra_generating_set():
            invariant = invariant_inclusion(changed_invariants.algebra_generator(label))
            engine_invariant = engine_source(
                _engine_element(changed_source_algebra, invariant)
            )
            certificate = engine_invariant.in_subalgebra(
                old_generator_images, algorithm="groebner", certificate="invariant"
            )
            if certificate is None:
                raise ArithmeticError(
                    f"the Reynolds operator makes the comparison along {self.ring_map()} an "
                    f"isomorphism, but the invariant {invariant} of the base-changed ring could not "
                    "be written as a polynomial in the base changes of the original invariants"
                )
            inverse_images[label] = _evaluate_polynomial_in_algebra(
                certificate, changed_old_invariants
            )
        inverse_pullback = changed_invariants.Mor(changed_old_invariants)(
            inverse_images
        )
        from sage_extensions.categories.schemes.schemes import (
            _affine_morphism_from_pullback,
        )

        inverse = _affine_morphism_from_pullback(
            target_quotient, source_quotient, inverse_pullback
        )
        return (
            Schemes(source_quotient.scheme_base_ring())
            .Core()
            .Mor(source_quotient, target_quotient)(forward, inverse)
        )

    def pullback_divisor(self, divisor):
        if self._toric_lattice_morphism is None:
            raise AttributeError(f"{self} is not a represented toric morphism")
        from sage_extensions.categories.schemes.toric.toric_schemes import _integers

        codomain = self.codomain()
        target_group = codomain.weil_divisor_group()
        divisor = target_group(divisor)
        assert codomain.is_cartier(divisor), (
            f"the pullback along {self} is defined for Cartier divisors, but {divisor} is not "
            f"Cartier on {codomain}"
        )
        target_rays = codomain.fan().cones(1)
        target_coordinates = divisor.to_vector()
        engine_divisor = _engine_scheme(codomain).divisor(
            [int(target_coordinates(ray)) for ray in target_rays]
        )
        pulled = _engine_scheme_morphism(self).pullback_divisor(engine_divisor)
        source = self.domain()
        source_group = source.weil_divisor_group()
        source_rays = source.fan().cones(1)
        return source_group.linear_combination(
            {
                ray: _integers()(pulled.coefficient(position))
                for position, ray in enumerate(source_rays)
                if pulled.coefficient(position)
            }
        )

    def pullback_line_bundle(self, bundle):
        if self._toric_lattice_morphism is None:
            raise AttributeError(f"{self} is not a represented toric morphism")
        assert bundle.scheme() is self.codomain(), (
            f"cannot pull back {bundle} along {self}: it is a line bundle on {bundle.scheme()}, "
            f"not on the codomain {self.codomain()}"
        )
        return self.domain().invertible_sheaf_of_divisor(
            self.pullback_divisor(bundle.associated_divisor())
        )

    def cone_construction(self):
        r"""Return the selected universal-cone datum defining this map, or ``None``."""
        return self._cone_construction

    def closed_complement(self):
        r"""Return the selected closed complement when this is its open inclusion."""
        if self._closed_complement is None:
            raise AttributeError(f"{self} has no selected closed complement")
        return self._closed_complement

    def _in_mor(self, mor):
        r"""Re-site this representation in a Mor with the same endpoints.

        Protected arrow-engine contract of ``SchemeMorCategory``.  Its
        constructor checks endpoints and any added scalar condition first;
        a representation without a native morphism supplies its own copy of
        the same defining data.  In particular chart maps never need a native
        realization merely to forget the relative-base condition.
        """
        gluing_chart_map = self._gluing_chart_map
        if self._gluing_role == "chart_map":
            gluing_chart_map = mor.mor_category().Mor(
                self.domain(), self.chart_embedding().domain()
            )(self.chart_map())
        glued_local_maps = self._glued_local_maps
        if self._gluing_role == "glued_domain":
            datum = self.gluing_datum()
            glued_local_maps = finite_indexed_family(
                datum.chart_index_set(),
                lambda index: mor.mor_category().Mor(
                    datum.chart(index), self.codomain()
                )(self.glued_local_map(index)),
                name="Re-sited glued-domain local maps",
            )
        return mor.element_class(
            mor,
            self._native_morphism,
            mor=mor,
            pullback=self._coordinate_pullback,
            scalar_pullback=self._scalar_pullback,
            cone_construction=self.cone_construction(),
            point_coordinates=self._represented_point_coordinates(),
            closed_complement=self._closed_complement,
            homogeneous_coordinates=self._homogeneous_coordinates,
            coefficient_map=self._coefficient_map,
            standard_projective_chart_embedding=self._standard_projective_chart_embedding,
            multiprojective_chart_embedding=self._multiprojective_chart_embedding,
            gluing_datum=self._gluing_datum,
            gluing_chart_index=self._gluing_chart_index,
            gluing_role=self._gluing_role,
            gluing_chart_map=gluing_chart_map,
            finite_atlas=self._finite_atlas,
            atlas_local_maps=(
                None
                if self._atlas_local_maps is None
                else finite_indexed_family(
                    self._finite_atlas.chart_index_set(),
                    lambda index: mor.mor_category().Mor(
                        self._finite_atlas.chart(index), self.codomain()
                    )(self._atlas_local_maps[index]),
                    name="Re-sited finite-atlas local maps",
                )
            ),
            glued_local_maps=glued_local_maps,
            relative_projectivization_source_sheaf=self._relative_projectivization_source_sheaf,
            relative_projectivization_comparison=self._relative_projectivization_comparison,
            relative_projectivization_role=self._relative_projectivization_role,
            relative_projectivization_underlying_projection=self._relative_projectivization_underlying_projection,
            relative_projectivization_sheaf_morphism=self._relative_projectivization_sheaf_morphism,
            toric_lattice_morphism=self._toric_lattice_morphism,
            toric_chart_targets=self._toric_chart_targets,
            toric_chart_pullbacks=self._toric_chart_pullbacks,
            affine_quotient_base_change_data=self._affine_quotient_base_change_datum,
        )

    def _transport_initialization_to_mor(self, mor):
        r"""Retain this scheme-map representation while adding stronger arrow structure."""
        return (
            (self._native_morphism,),
            {
                "mor": mor,
                "pullback": self._coordinate_pullback,
                "scalar_pullback": self._scalar_pullback,
                "cone_construction": self.cone_construction(),
                "point_coordinates": self._represented_point_coordinates(),
                "closed_complement": self._closed_complement,
                "homogeneous_coordinates": self._homogeneous_coordinates,
                "coefficient_map": self._coefficient_map,
                "standard_projective_chart_embedding": self._standard_projective_chart_embedding,
                "multiprojective_chart_embedding": self._multiprojective_chart_embedding,
                "gluing_datum": self._gluing_datum,
                "gluing_chart_index": self._gluing_chart_index,
                "gluing_role": self._gluing_role,
                "gluing_chart_map": self._gluing_chart_map,
                "finite_atlas": self._finite_atlas,
                "atlas_local_maps": self._atlas_local_maps,
                "glued_local_maps": self._glued_local_maps,
                "relative_projectivization_source_sheaf": self._relative_projectivization_source_sheaf,
                "relative_projectivization_comparison": self._relative_projectivization_comparison,
                "relative_projectivization_role": self._relative_projectivization_role,
                "relative_projectivization_underlying_projection": self._relative_projectivization_underlying_projection,
                "relative_projectivization_sheaf_morphism": self._relative_projectivization_sheaf_morphism,
                "toric_lattice_morphism": self._toric_lattice_morphism,
                "toric_chart_targets": self._toric_chart_targets,
                "toric_chart_pullbacks": self._toric_chart_pullbacks,
                "affine_quotient_base_change_data": self._affine_quotient_base_change_datum,
            },
        )

    def _represented_coordinate_pullback(self):
        return self._coordinate_pullback

    def _represented_point_coordinates(self):
        return self._point_coordinates

    def homogeneous_coordinates(self):
        if self._homogeneous_coordinates is None:
            raise AttributeError(
                f"{self} is not represented by homogeneous coordinates"
            )
        return self._homogeneous_coordinates

    def coefficient_map(self):
        if self._coefficient_map is None:
            raise AttributeError(f"{self} has no selected coefficient map")
        return self._coefficient_map

    def _projective_coordinate_data(self):
        return self._homogeneous_coordinates is not None

    def _projective_engine_morphism(self):
        ring = self.coefficient_map().codomain()
        base = self.coefficient_map().domain()
        # The engine realizes the coordinates over its own scalars, so the
        # selected coefficient map must be the structure map R -> A of the
        # coordinate algebra, the map the engine applies to scalars.
        natural = ring.algebra_structure_morphism()
        assert (
            natural.domain() is base
            and _ring_morphisms_equal(self.coefficient_map(), natural) is True
        ), (
            f"the selected coefficient map of {self} is not the structure map {base} -> {ring}"
        )
        return _native_scheme_mor(self.domain(), self.codomain())(
            [_engine_element(ring, value) for value in self.homogeneous_coordinates()],
            check=False,
        )

    def __mul__(self, other):
        if self._relative_projectivization_role == "base_projection":
            if (
                other
                is self.comparison()
                .changed_projectivization()
                .arrow()
                .domain()
                .projectivization_projection()
            ):
                return self.comparison().square_composite()
            return self.underlying_projection() * other
        if self._relative_projectivization_role == "base_change_base":
            if (
                other
                is self.comparison()
                .changed_projectivization()
                .arrow()
                .domain()
                .projectivization_projection()
            ):
                return self.comparison().square_composite()
            return super().__mul__(other)
        if self._gluing_role == "glued_domain":
            if (
                not isinstance(other, SchemeMorphismMethods)
                or other.codomain() is not self.domain()
            ):
                return NotImplemented
            if self._is_the_identity():
                return other
            if other._is_the_identity():
                return self
            return other._postcompose_with(self)
        if self._gluing_role == "finite_atlas":
            if (
                not isinstance(other, SchemeMorphismMethods)
                or other.codomain() is not self.domain()
            ):
                return NotImplemented
            if self._is_the_identity():
                return other
            if other._is_the_identity():
                return self
            return other._postcompose_with(self)
        if self._gluing_role == "open_inclusion":
            datum = self.gluing_datum()
            chart = datum.chart_isomorphism(self.chart_index())
            return datum.chart_embedding(self.chart_index()) * (chart.inverse() * other)
        if self._gluing_role == "chart_embedding":
            if other.codomain() is not self.domain():
                return NotImplemented
            from sage_extensions.categories.schemes.gluing import (
                _glued_scheme_chart_map,
                _scheme_composition_mor,
            )

            return _glued_scheme_chart_map(
                _scheme_composition_mor(self, other),
                self,
                other,
            )
        if self._gluing_role == "chart_map":
            composite = self.chart_map() * other
            if composite is NotImplemented:
                return NotImplemented
            from sage_extensions.categories.schemes.gluing import (
                _glued_scheme_chart_map,
                _scheme_composition_mor,
            )

            return _glued_scheme_chart_map(
                _scheme_composition_mor(self, other),
                self.chart_embedding(),
                composite,
            )
        if self._multiprojective_chart_embedding:
            if other.codomain() is not self.domain():
                return NotImplemented
            return _projective_coordinate_morphism(self) * other
        if self._homogeneous_coordinates is None:
            return super().__mul__(other)
        assert other.codomain() is self.domain(), (
            f"{self} and {other} are not composable"
        )
        cone_leg = self._projected_cone_leg(other)
        if cone_leg is not None:
            return cone_leg
        if other._is_the_identity():
            return self
        mor = _scheme_composition_mor(self, other)
        if self.domain() in Schemes(self.domain().scheme_base_ring()).Affine():
            pullback = other.coordinate_algebra_morphism()
            return _ProjectiveCoordinateMorphism(
                mor,
                tuple(pullback(value) for value in self.homogeneous_coordinates()),
                coefficient_map=OwnedRings()
                .Mor(self.coefficient_map().domain(), pullback.codomain())
                .elementwise(lambda value: pullback(self.coefficient_map()(value))),
            )
        if other.domain()._is_glued_from_affine_atlas():
            return other._postcompose_with(self)
        before = _projective_coordinate_morphism(other)
        source_ring = self.coefficient_map().codomain()

        def substitute(polynomial):
            return _evaluate_owned_homogeneous_polynomial_on_coordinates(
                polynomial,
                source_ring,
                tuple(before.homogeneous_coordinates()),
                coefficient_map=before.coefficient_map(),
            )

        coefficients = (
            OwnedRings()
            .Mor(self.coefficient_map().domain(), before.coefficient_map().codomain())
            .elementwise(lambda value: substitute(self.coefficient_map()(value)))
        )
        values = tuple(substitute(value) for value in self.homogeneous_coordinates())
        point_values = (
            finite_family(values, name="Point coordinates")
            if before._represented_point_coordinates() is not None
            else None
        )
        return _ProjectiveCoordinateMorphism(
            mor, values, coefficient_map=coefficients, point_coordinates=point_values
        )

    def _postcompose_with(self, after):
        if self._toric_lattice_morphism is not None:
            datum = self.domain().gluing_datum()
            return _scheme_composition_mor(after, self)(
                finite_indexed_family(
                    datum.chart_index_set(),
                    lambda index: after * self.local_map(index),
                )
            )
        if self._relative_projectivization_role == "base_change_total":
            if (
                after
                is self.comparison().projectivization().projectivization_projection()
            ):
                return self.comparison().square_composite()
            return None
        if self._relative_projectivization_source_sheaf is not None:
            if after is self.codomain().structure_morphism():
                return self.domain().structure_morphism()
            return None
        if self._gluing_role == "glued_domain":
            if after.domain() is not self.codomain():
                return NotImplemented
            from sage_extensions.categories.schemes.gluing import _glued_scheme_morphism

            datum = self.gluing_datum()
            return _glued_scheme_morphism(
                _scheme_composition_mor(after, self),
                tuple(
                    after * self.glued_local_map(index)
                    for index in datum.chart_indices()
                ),
            )
        if self._gluing_role == "finite_atlas":
            if after.domain() is not self.codomain():
                return NotImplemented
            from sage_extensions.categories.schemes.gluing import (
                _finite_atlas_scheme_morphism,
            )

            return _finite_atlas_scheme_morphism(
                self.domain(),
                after.codomain(),
                self.atlas(),
                self.local_maps().map(lambda local_map: after * local_map),
            )
        if self._gluing_role == "open_inclusion":
            chart = self.gluing_datum().chart_isomorphism(self.chart_index())
            return after.local_map(self.chart_index()) * chart.inverse().forward()
        if self._gluing_role == "chart_embedding":
            if after.domain() is not self.codomain():
                return NotImplemented
            return after.local_map(self.chart_index())
        if self._gluing_role == "chart_map":
            if after.domain() is not self.codomain():
                return NotImplemented
            return after.local_map(self.chart_index()) * self.chart_map()
        return NotImplemented

    def __eq__(self, other):
        if self._toric_lattice_morphism is not None:
            return (
                isinstance(other, SchemeMorphismMethods)
                and other._toric_lattice_morphism is not None
                and other.domain() is self.domain()
                and other.codomain() is self.codomain()
                and other.lattice_morphism() == self.lattice_morphism()
            )
        if self._relative_projectivization_role == "surjectivity_open_inclusion":
            return (
                isinstance(other, SchemeMorphismMethods)
                and other._relative_projectivization_role
                == "surjectivity_open_inclusion"
                and other.domain() is self.domain()
                and other.codomain() is self.codomain()
                and other.sheaf_morphism() is self.sheaf_morphism()
            )
        if self._relative_projectivization_role == "surjectivity_induced_morphism":
            return (
                isinstance(other, SchemeMorphismMethods)
                and other._relative_projectivization_role
                == "surjectivity_induced_morphism"
                and other.domain() is self.domain()
                and other.codomain() is self.codomain()
                and other.sheaf_morphism() is self.sheaf_morphism()
            )
        if self._relative_projectivization_role == "base_projection":
            if other is self.underlying_projection():
                return True
            if (
                isinstance(other, SchemeMorphismMethods)
                and other._relative_projectivization_role == "base_projection"
            ):
                return (
                    other.domain() is self.domain()
                    and other.codomain() is self.codomain()
                    and other.underlying_projection() == self.underlying_projection()
                )
            return self.underlying_projection() == other
        if self._relative_projectivization_role == "base_change_composite":
            return (
                isinstance(other, SchemeMorphismMethods)
                and other._relative_projectivization_role == "base_change_composite"
                and other.domain() is self.domain()
                and other.codomain() is self.codomain()
                and other.comparison() is self.comparison()
            )
        if self._relative_projectivization_role == "base_change_total":
            return (
                isinstance(other, SchemeMorphismMethods)
                and other._relative_projectivization_role == "base_change_total"
                and other.domain() is self.domain()
                and other.codomain() is self.codomain()
                and other.comparison() is self.comparison()
            )
        if self._relative_projectivization_source_sheaf is not None:
            return (
                isinstance(other, SchemeMorphismMethods)
                and other._relative_projectivization_source_sheaf
                is self._relative_projectivization_source_sheaf
                and other.domain() is self.domain()
                and other.codomain() is self.codomain()
            )
        if self._gluing_role == "glued_domain":
            return (
                isinstance(other, SchemeMorphismMethods)
                and other._gluing_role == "glued_domain"
                and other.domain() is self.domain()
                and other.codomain() is self.codomain()
                and other.gluing_datum() is self.gluing_datum()
                and all(
                    self.glued_local_map(index) == other.glued_local_map(index)
                    for index in self.gluing_datum().chart_indices()
                )
            )
        if self._gluing_role == "finite_atlas":
            if (
                not isinstance(other, SchemeMorphismMethods)
                or other.domain() is not self.domain()
                or other.codomain() is not self.codomain()
            ):
                return False
            if other._gluing_role == "finite_atlas" and other.atlas() is self.atlas():
                return all(
                    self.local_map(index) == other.local_map(index)
                    for index in self.atlas().chart_indices()
                )
            if other._is_the_identity():
                return all(
                    self.local_map(index) == self.atlas().chart_embedding(index)
                    for index in self.atlas().chart_indices()
                )
            return all(
                self.local_map(index) == other * self.atlas().chart_embedding(index)
                for index in self.atlas().chart_indices()
            )
        if self._gluing_role == "chart_map":
            if (
                not isinstance(other, SchemeMorphismMethods)
                or other.codomain() is not self.codomain()
            ):
                return False
            if other._gluing_role == "chart_embedding":
                return (
                    other.gluing_datum() is self.gluing_datum()
                    and other.chart_index() == self.chart_index()
                    and self.chart_map()
                    == other.domain().categorical_identity_morphism()
                )
            if other._gluing_role != "chart_map":
                return False
            if self.chart_index() == other.chart_index():
                return self.chart_map() == other.chart_map()
            datum = self.gluing_datum()
            if other.gluing_datum() is not datum:
                return False
            from sage_extensions.categories.schemes.gluing import (
                _lands_in_distinguished_open,
            )

            left_overlap = datum.overlap(self.chart_index(), other.chart_index())
            right_overlap = datum.overlap(other.chart_index(), self.chart_index())
            if not _lands_in_distinguished_open(self.chart_map(), left_overlap):
                return False
            if not _lands_in_distinguished_open(other.chart_map(), right_overlap):
                return False
            left = left_overlap.corestriction(self.chart_map())
            right = right_overlap.corestriction(other.chart_map())
            transition = datum.transition_between(
                self.chart_index(), other.chart_index()
            ).forward()
            return transition * left == right
        if self._gluing_role == "chart_embedding":
            if getattr(other, "_gluing_role", None) == "chart_map":
                return (
                    other.codomain() is self.codomain()
                    and other.gluing_datum() is self.gluing_datum()
                    and other.chart_index() == self.chart_index()
                    and other.chart_map()
                    == self.domain().categorical_identity_morphism()
                )
            return (
                isinstance(other, SchemeMorphismMethods)
                and other._gluing_role == "chart_embedding"
                and other.gluing_datum() is self.gluing_datum()
                and other.chart_index() == self.chart_index()
            )
        if (
            self._gluing_role == "open_inclusion"
            or getattr(other, "_gluing_role", None) == "open_inclusion"
        ):
            return (
                isinstance(other, SchemeMorphismMethods)
                and self._gluing_role == other._gluing_role == "open_inclusion"
                and self.gluing_datum() is other.gluing_datum()
                and self.chart_index() == other.chart_index()
                and self.domain() is other.domain()
                and self.codomain() is other.codomain()
            )
        if self._homogeneous_coordinates is None:
            return super().__eq__(other)
        if self is other:
            return True
        if (
            not isinstance(other, SchemeMorphismMethods)
            or other.domain() is not self.domain()
            or other.codomain() is not self.codomain()
        ):
            return False
        other = _projective_coordinate_morphism(other)
        ring = self.coefficient_map().codomain()
        restriction = _projective_section_restriction(self.domain(), ring)
        mor = OwnedRings().Mor(self.coefficient_map().domain(), restriction.codomain())
        coefficients_equal = _ring_morphisms_equal(
            mor.elementwise(lambda scalar: restriction(self.coefficient_map()(scalar))),
            mor.elementwise(
                lambda scalar: restriction(ring(other.coefficient_map()(scalar)))
            ),
        )
        if coefficients_equal is False:
            return False
        left, right = (
            tuple(self.homogeneous_coordinates()),
            tuple(ring(value) for value in other.homogeneous_coordinates()),
        )
        offset = 0
        for width in _projective_coordinate_blocks(self.codomain()):
            if any(
                not restriction(left[i] * right[j] - left[j] * right[i]).is_zero()
                for i, j in combinations(range(offset, offset + width), 2)
            ):
                return False
            offset += width
        return coefficients_equal

    def _engine_morphism_crossing(self):
        r"""The Sage morphism between the engines this morphism computes in."""
        if self._toric_lattice_morphism is not None:
            assert self._native_morphism is not None, (
                f"cannot compute with {self} in Sage: the toric morphism was constructed from its "
                "fan-compatible lattice map without a Sage morphism over this base ring"
            )
            return self._native_morphism
        if self._gluing_role == "open_inclusion":
            raise NotImplementedError(
                "a glued open inclusion is represented by its gluing datum"
            )
        if self._homogeneous_coordinates is not None:
            return self._projective_engine_morphism()
        if self._scalar_pullback is not None:
            base_arrow = LocallyRingedSpaces().Mor(
                self.domain().base_scheme(), self.codomain()
            )(self._scalar_pullback)
            return _engine_scheme_morphism(base_arrow) * _engine_scheme_morphism(
                self.domain().structure_morphism()
            )
        if self._coordinate_pullback is not None:
            if self._is_the_identity():
                return _engine_scheme(self.domain()).identity_morphism()
            return _native_scheme_mor(self.domain(), self.codomain())(
                _engine_coordinate_pullback(self._coordinate_pullback),
                check=False,
            )
        assert self._native_morphism is not None, (
            f"cannot compute with {self} in Sage: it was constructed from its coordinate data without "
            "a Sage scheme morphism"
        )
        return self._native_morphism

    def point_coordinates(self):
        r"""Return the selected owned coordinate family of this represented point."""
        assert self._point_coordinates is not None, (
            f"{self} has no point coordinates: it was not constructed as a point from a family of "
            "coordinates"
        )
        return self._point_coordinates

    def _call_(self, point):
        if self._gluing_role in ("open_inclusion", "chart_embedding"):
            from sage_extensions.categories.rings.commutative_algebra import (
                PrimeSpectra,
            )

            if element_parent(point) in PrimeSpectra():
                if element_parent(point) is not self.domain().underlying_space():
                    raise ValueError(
                        f"{point} is not a prime point of the chart {self.domain()}"
                    )
                return self.codomain()._glued_chart_point_map(self.chart_index())(point)
        r"""Evaluate a prime point or compose a scheme-valued point.

        On affine prime points, ``Spec(f)`` acts by contraction along ``f``.
        A scheme-valued point ``T -> X`` maps to its composite ``T -> Y``.
        The prime-point construction is the contravariant spectrum functor,
        not a choice of a residue-field-valued point.

        Unexecuted affine open-inclusion specimen (localization prime
        correspondence, Atiyah--Macdonald, Proposition 3.11)::

            sage: from dzack_research.preamble.all import *
            sage: A = QQ['x']; x = A.algebra_generator('x')
            sage: X = AffineSchemes(QQ)(A)
            sage: U = X.distinguished_open(x)
            sage: B = U.coordinate_algebra()
            sage: p = U(B.ideal(B(x - A.one())))
            sage: U.inclusion()(p) == X(A.ideal(x - A.one()))
            True
            sage: U.inclusion().evaluate_at(p) == U.inclusion()(p)
            True
        """
        from sage_extensions.categories.rings.commutative_algebra import PrimeSpectra

        if element_parent(point) in PrimeSpectra():
            source = self.domain()
            target = self.codomain()
            if element_parent(point) is not source.underlying_space():
                raise ValueError(f"{point} is not a prime point of the domain {source}")
            if target.has_selected_finite_affine_atlas():
                atlas = target.selected_finite_affine_atlas()
                for index in atlas.chart_indices():
                    embedding = atlas.chart_embedding(index)
                    if self is embedding or (
                        source is embedding.domain() and (self == embedding) is True
                    ):
                        return target._glued_chart_point_map(index)(point)
            match source, target:
                case _ if (
                    source in Schemes(source.scheme_base_ring()).Affine()
                    and target in Schemes(target.scheme_base_ring()).Affine()
                ):
                    ring_map = self.coordinate_algebra_morphism()
                    spectrum = OwnedRings().Commutative().prime_spectrum_functor()
                    opposite = spectrum.domain()
                    arrow = opposite.Mor(
                        opposite(ring_map.codomain()), opposite(ring_map.domain())
                    )(ring_map)
                    return spectrum.on_morphism(arrow)(point)
                case _:
                    assert False, (
                        f"the image of {point} along {self} requires the prime-point map "
                        "of the glued scheme realization"
                    )
        return self.compose(point)

    def _projected_cone_leg(self, before):
        r"""Reduce a projection after the factorization through its own cone."""
        construction = before.cone_construction()
        if construction is not None and construction.target() is self.domain():
            return construction.leg_of_projection(self)
        return None

    def __mul__(self, other):
        r"""``self o other``, composition of scheme morphisms.

        The identity is a two-sided unit; ``Spec R`` is terminal in ``Sch/R``,
        so a composite landing there is the structure morphism of its domain;
        a projection composed with a cone factorization is the leg.  Otherwise
        affine composites compose their pullbacks and the remaining ones
        compose their realizations.
        """
        assert other.codomain() is self.domain(), (
            f"{self} and {other} are not composable: the codomain of the second is not the domain of the first"
        )
        if self._is_the_identity():
            return other
        if other._is_the_identity():
            return self
        relative = Schemes(self.codomain().scheme_base_ring())
        if (
            self.parent().mor_category().is_subcategory(relative)
            and other.parent().mor_category().is_subcategory(relative)
            and self.codomain() is other.domain().base_scheme()
        ):
            return other.domain().structure_morphism()

        cone_leg = self._projected_cone_leg(other)
        if cone_leg is not None:
            return cone_leg

        mor = _scheme_composition_mor(self, other)
        point_coordinates = self._represented_point_coordinates()
        if (
            point_coordinates is not None
            and other.codomain() is other.domain().base_scheme()
            and other == other.domain().structure_morphism()
            and self.codomain()
            in Schemes(self.codomain().scheme_base_ring()).Projective()
        ):
            # The constant map T -> Spec R -> X at an R-point: its homogeneous
            # coordinates are the point's coordinates, read as sections on T.
            return _ProjectiveCoordinateMorphism(
                mor,
                tuple(
                    _constant_sections_ring(other.domain())(value)
                    for value in point_coordinates
                ),
            )
        left_pullback = self._represented_coordinate_pullback()
        right_pullback = other._represented_coordinate_pullback()
        left_scalar_pullback = self._scalar_pullback
        right_scalar_pullback = other._scalar_pullback
        if left_scalar_pullback is not None or right_scalar_pullback is not None:
            if left_scalar_pullback is None or right_scalar_pullback is None:
                return False
            equal = _ring_morphisms_equal(left_scalar_pullback, right_scalar_pullback)
            if equal is True or self.domain() in ProjectiveSpaces(
                self.domain().scheme_base_ring()
            ):
                return equal
            return AtomicProposition("equal", self, other)
        if left_pullback is not None and right_pullback is not None:
            return mor(right_pullback * left_pullback)
        if (
            left_pullback is not None
            and self.codomain() is Schemes(left_pullback.domain()).base_scheme()
            and other.codomain() is other.domain().base_scheme()
            and other.parent()
            .mor_category()
            .is_subcategory(Schemes(other.domain().scheme_base_ring()))
        ):
            assert left_pullback.codomain() is mor.domain().scheme_base_ring(), (
                f"cannot compose the structure morphism of {mor.domain()} with Spec of {left_pullback}: "
                f"the ring map must land in the base ring {mor.domain().scheme_base_ring()} of {mor.domain()}, "
                f"but it lands in {left_pullback.codomain()}"
            )
            assert mor.codomain() is Schemes(left_pullback.domain()).base_scheme(), (
                f"the composite lands in Spec {left_pullback.domain()}, but the requested codomain is {mor.codomain()}"
            )
            return mor.element_class(mor, None, mor=mor, scalar_pullback=left_pullback)
        structured = other._postcompose_with(self)
        if structured is not None:
            return structured
        return mor.element_class(
            mor,
            _engine_scheme_morphism(self) * _engine_scheme_morphism(other),
            mor=mor,
        )

    def _is_the_identity(self) -> bool:
        r"""Whether this morphism is its Mor object's selected identity."""
        return self.domain() is self.codomain() and self is self.parent().identity()

    def _postcompose_with(self, after):
        r"""``after o self`` for a representation with its own composite, else ``None``."""
        return

    def compose(self, before):
        return self * before

    def then(self, after):
        return after * self

    def evaluate_at(self, point):
        r"""The image of a represented point under this morphism.

        A projection out of a product of projective spaces sends a point given
        by its homogeneous coordinate blocks to the block of its factor; every
        other represented morphism composes with the point.
        """
        from sage_extensions.categories.rings.commutative_algebra import PrimeSpectra

        if element_parent(point) in PrimeSpectra():
            return self._call_(point)
        domain = self.domain()
        base = domain.scheme_base_ring()
        coordinates = point._represented_point_coordinates()
        if domain in ProductProjectiveSpaces(base) and coordinates is not None:
            factors = domain.factors()
            values = tuple(coordinates)
            offset = 0
            for label in factors.index_set():
                width = int(factors[label].relative_dimension()) + 1
                block = values[offset : offset + width]
                offset += width
                if self is domain.projection(label):
                    return factors[label].point_morphism(block)
        return self * point

    def coordinate_algebra_morphism(self):
        r"""``f^#: O(Y) -> O(X)``, the pullback representing a morphism of affine schemes."""
        pullback = self._represented_coordinate_pullback()
        assert pullback is not None, (
            f"{self} has no coordinate algebra morphism: only a morphism between affine schemes is a "
            f"pullback of coordinate algebras, and {self.domain()} or {self.codomain()} is not affine"
        )
        return pullback

    pullback_on_coordinate_algebras = coordinate_algebra_morphism

    @cached_method
    def graph_morphism(self):
        r"""``Gamma_f = (id, f): X -> X x_S Y``."""
        identity = self.domain().categorical_identity_morphism()
        return _scheme_product(self.domain(), self.codomain()).from_product_cone(
            (identity, self)
        )

    @cached_method
    def graph_subscheme(self):
        r"""The closed subscheme ``Gamma_f <= X x_S Y`` cut out by ``1 tensor b - f^#(b) tensor 1``.

        The graph is the inverse image of the diagonal of ``Y`` under
        ``f x id``, so it is closed whenever ``Y`` is separated; affine ``Y``
        is.  The graph morphism factors through it as an isomorphism.
        """
        base = self.codomain().scheme_base_ring()
        assert self.codomain() in Schemes(base).Affine(), (
            f"cannot form the graph of {self} as a closed subscheme: the codomain {self.codomain()} "
            f"must be an affine scheme over {base}, but it is an object of {self.codomain().category()}"
        )
        product = _scheme_product(self.domain(), self.codomain())
        to_domain = product.projection(0).coordinate_algebra_morphism()
        to_codomain = product.projection(1).coordinate_algebra_morphism()
        pullback = self.coordinate_algebra_morphism()
        algebra = self.codomain().coordinate_algebra()
        equations = tuple(
            to_codomain(algebra.algebra_generator(label))
            - to_domain(pullback(algebra.algebra_generator(label)))
            for label in algebra.algebra_generating_set()
        )
        return product.closed_subscheme(equations)

    def base_change(self, ring_map):
        r"""``f_{R'}: X_{R'} -> Y_{R'}``, the morphism the base-change functor induces.

        The square with the two projections commutes, so an automorphism of
        ``X`` over ``R`` becomes an automorphism of ``X_{R'}`` over ``R'``.
        """
        return self.domain().scheme_category().base_change_functor(ring_map)(self)

    def slice_base_change_adjunction(self):
        r"""Return ``Sigma_self -| self^*`` between the two scheme slice categories."""
        from sage_extensions.categories.schemes.base_change import (
            _slice_base_change_adjunction,
        )

        return _slice_base_change_adjunction(self)

    def inverse_image(self, subscheme):
        r"""``f^{-1}(Z) = X x_Y Z`` as a closed or open subscheme of ``X``.

        For ``Z = V(I) <= Spec B`` and ``f: Spec A -> Spec B`` this is
        ``V(f^#(I) A)``.  For an open ``U = D(g) <= Spec B`` it is the open
        ``D(f^# g) <= X``: a point ``p`` maps into ``D(g)`` exactly when
        ``g`` does not vanish at ``f(p)``, that is when ``f^# g`` does not
        vanish at ``p``.  On ``X`` glued from affine charts ``U_i`` this is
        ``D((f iota_i)^# g) <= U_i`` on each chart, glued along the atlas
        of ``X``.  An open immersion is a monomorphism, and a morphism
        ``T -> X`` whose composite with ``f`` lands in ``U`` factors through
        ``f^{-1}(U)``, so ``f^{-1}(U)`` with its inclusion and ``f``
        restricted is the fibre product ``X x_Y U``.
        """
        assert subscheme.inclusion().codomain() is self.codomain(), (
            f"cannot form the inverse image of {subscheme} under {self}: it is a "
            f"subscheme of {subscheme.inclusion().codomain()}, not of the codomain {self.codomain()}"
        )
        domain = self.domain()
        base = domain.scheme_base_ring()
        match subscheme:
            case _ if subscheme in OpenImmersions(self.codomain()):
                assert subscheme.is_distinguished_open() is True, (
                    f"cannot form the inverse image of {subscheme} under {self}: it is computed here for a "
                    f"distinguished open D(g) of an affine scheme, and {subscheme} is not known to be one"
                )
                element = self.codomain().coordinate_algebra()(
                    subscheme.distinguished_open_element()
                )
                if domain._is_glued_from_affine_atlas():
                    from sage_extensions.categories.schemes.gluing import (
                        _glued_chartwise_distinguished_open,
                    )

                    datum = domain.gluing_datum()
                    labels = tuple(datum.chart_indices())
                    return _glued_chartwise_distinguished_open(
                        datum,
                        labels,
                        {label: label for label in labels},
                        {
                            label: datum.chart(label).distinguished_open(
                                (
                                    self * datum.chart_embedding(label)
                                ).coordinate_algebra_morphism()(element)
                            )
                            for label in labels
                        },
                        name=f"Inverse image of {subscheme} under {self}",
                    )
                assert domain in Schemes(base).Affine(), (
                    f"cannot form the inverse image of {subscheme} under {self}: the domain must be affine "
                    f"or glued from affine charts, but it is an object of {domain.category()}"
                )
                return domain.distinguished_open(
                    self.coordinate_algebra_morphism()(element)
                )
            case _:
                assert (
                    domain in Schemes(base).Affine()
                    and self.codomain() in Schemes(base).Affine()
                ), (
                    f"cannot form the inverse image of {subscheme} under {self}: this computation "
                    f"requires affine schemes over {base}, but the domain is an object of "
                    f"{domain.category()} and the codomain an object of {self.codomain().category()}"
                )
                pullback = self.coordinate_algebra_morphism()
                equations = tuple(
                    pullback(equation) for equation in subscheme.defining_equations()
                )
                return domain.closed_subscheme(equations)

    def fixed_subscheme(self):
        r"""``X^f = Eq(f, id_X)``, the fixed subscheme of an endomorphism.

        On a product of projective spaces a retained product-cone map
        ``f=(f_i)`` is fixed exactly when ``f_i(x)=pi_i(x)`` in every factor.
        Equality of two projective points is cut out by the ``2 x 2`` minors of
        their homogeneous coordinate pairs, so these minors give the
        scheme-theoretic equalizer without choosing affine charts.
        """
        assert self.domain() is self.codomain(), (
            f"{self} has no fixed subscheme: it is a morphism {self.domain()} -> {self.codomain()}, "
            "not an endomorphism"
        )
        domain = self.domain()
        base = domain.scheme_base_ring()
        construction = self.cone_construction()
        if (
            domain in ProductProjectiveSpaces(base)
            and construction is not None
            and construction.target() is domain
        ):
            legs = construction.legs()
            equations = []
            for label in domain.factors().index_set():
                moved_values = _engine_defining_polynomials(
                    _engine_scheme_morphism(legs[label])
                )
                fixed_values = _engine_defining_polynomials(
                    _engine_scheme_morphism(domain.projection(label))
                )
                assert len(moved_values) == len(fixed_values), (
                    f"cannot form the fixed subscheme of {self}: in the factor {label} the map has "
                    f"{len(moved_values)} homogeneous coordinates, but the projection has {len(fixed_values)}"
                )
                equations.extend(
                    moved_values[left] * fixed_values[right]
                    - moved_values[right] * fixed_values[left]
                    for left, right in combinations(range(len(moved_values)), 2)
                )
            return domain.closed_subscheme(tuple(equations))
        return Schemes(base).equalizer(self, domain.categorical_identity_morphism())

    def _engine_pullback_with_trivial_base_map(self):
        r"""The pullback ``B -> A`` realized in the engine over one coefficient ring.

        Sage computes kernels and surjectivity of a ring map by Groebner
        elimination on its graph ideal, which it refuses for a map stated with
        a separate base map.  Both coordinate algebras here lie over one scalar
        ring, so the map is restated on the generators alone.
        """
        pullback = self.coordinate_algebra_morphism()
        source_algebra = pullback.domain()
        target_algebra = pullback.codomain()
        assert source_algebra.is_framed_algebra(), (
            f"cannot compute with the pullback {pullback} of {self} in Sage: {source_algebra} must have "
            f"a chosen set of algebra generators, but it is an object of {source_algebra.category()}"
        )
        target_engine = _engine_ring(target_algebra)
        return _engine_ring(source_algebra).hom(
            [
                target_engine(
                    _engine_element(
                        target_algebra,
                        pullback(source_algebra.algebra_generator(label)),
                    )
                )
                for label in source_algebra.algebra_generating_set()
            ],
            target_engine,
        )

    @cached_method
    def scheme_theoretic_image(self):
        r"""The closed subscheme ``V(ker f^#) <= Y`` for affine ``f: Spec A -> Spec B``.

        The scheme-theoretic image is the smallest closed subscheme through
        which ``f`` factors; for affine ``f`` its ideal sheaf is the kernel of
        ``f^#`` (Stacks, Tag 01R7).  The kernel is computed by the engine's
        elimination on the graph ideal.
        """
        base = self.domain().scheme_base_ring()
        assert (
            self.domain() in Schemes(base).Affine()
            and self.codomain() in Schemes(base).Affine()
        ), (
            f"cannot form the scheme-theoretic image of {self}: this computation requires affine "
            f"schemes over {base}, but the domain is an object of {self.domain().category()} and the "
            f"codomain an object of {self.codomain().category()}"
        )
        kernel = self._engine_pullback_with_trivial_base_map().kernel()
        algebra = self.codomain().coordinate_algebra()
        equations = tuple(
            _owned_engine_element(algebra, generator) for generator in kernel.gens()
        )
        return self.codomain().closed_subscheme(equations)

    @cached_method
    def quasi_coherent_adjunction(self):
        r"""Return the affine adjunction ``f^* -| f_*`` on represented quasi-coherent sheaves."""
        from sage_extensions.categories.schemes.sheaf_functors import (
            _affine_quasi_coherent_adjunction,
        )

        return _affine_quasi_coherent_adjunction(self)

    def module_pullback_functor(self):
        r"""Return ``f^* : QCoh(Y) -> QCoh(X)`` for this affine morphism."""
        return self.quasi_coherent_adjunction().pullback_functor()

    def direct_image_functor(self):
        r"""Return ``f_* : QCoh(X) -> QCoh(Y)`` for this affine morphism."""
        return self.quasi_coherent_adjunction().direct_image_functor()

    def direct_image(self, sheaf):
        r"""``f_* N~ = (Res_{f^#} N)~`` for affine ``f: Spec B -> Spec A`` (Stacks, Tag 01I9)."""
        return self.direct_image_functor().on_object(sheaf)

    @cached_method(key=lambda self, sheaf: id(sheaf))
    def module_pullback(self, sheaf):
        r"""Return the represented object ``f^*F``.

        For affine ``f : Spec B -> Spec A`` this is ``(M tensor_A B)~``
        (Stacks, Tag 01I9), through the affine pullback functor.  For a
        represented closed immersion ``i : Z -> P`` into projective space, the
        standard twists ``O_P(d)`` have their object pullback represented
        directly.  In every other represented non-affine case the exact object
        ``f^*F`` retains ``f`` and ``F`` without claiming a chartwise
        computation or a morphism action.
        """
        base = self.domain().scheme_base_ring()
        match (
            self.domain() in ClosedEmbeddings(self.codomain()),
            self.codomain() in ProjectiveSpaces(base),
        ):
            case (True, True):
                from sage_extensions.categories.schemes.sheaf_functors import (
                    _projective_closed_immersion_module_pullback,
                )

                return _projective_closed_immersion_module_pullback(self, sheaf)
            case _:
                pass
        match (
            self.domain() in Schemes(self.domain().scheme_base_ring()).Affine(),
            self.codomain() in Schemes(self.codomain().scheme_base_ring()).Affine(),
        ):
            case (True, True):
                return self.module_pullback_functor().on_object(sheaf)
            case _:
                from sage_extensions.categories.schemes.sheaf_functors import (
                    _exact_quasi_coherent_pullback,
                )

                return _exact_quasi_coherent_pullback(self, sheaf)

    def is_open_immersion(self) -> bool:
        r"""Whether this arrow is the inclusion of an open subscheme of its codomain.

        An open immersion is an isomorphism onto an open subscheme followed by
        its inclusion (Stacks, Tag 01IN); here the open subscheme is placed in
        ``OpenImmersions(Y)`` at its construction and this arrow is its
        inclusion.  A representation whose arrows factor that way by their
        construction states it by overriding this method.  The open inclusion
        of a selected closed complement, a standard or multiprojective chart
        embedding, a gluing chart embedding, and the open inclusion of a
        relative projectivization are open immersions by their construction.
        """
        if (
            self._closed_complement is not None
            or self._standard_projective_chart_embedding
            or self._multiprojective_chart_embedding
            or self._gluing_role in ("open_inclusion", "chart_embedding")
            or self._relative_projectivization_role == "surjectivity_open_inclusion"
        ):
            return True
        if self._is_the_identity():
            return True
        source = self.domain()
        if source in FiberProductSchemes(source.scheme_base_ring()):
            # Open immersions are stable under base change (Stacks, 01JY).
            left, right = source.fiber_product_cospan()
            if self is source.right_projection() and left.is_open_immersion() is True:
                return True
            if self is source.left_projection() and right.is_open_immersion() is True:
                return True
        return source in OpenImmersions(self.codomain()) and self is source.inclusion()

    def is_closed_immersion(self) -> bool:
        r"""Whether ``f^#`` is surjective, for affine ``f`` (Stacks, Tag 0H2N, Lemma 37.81.1)."""
        base = self.domain().scheme_base_ring()
        assert (
            self.domain() in Schemes(base).Affine()
            and self.codomain() in Schemes(base).Affine()
        ), (
            f"cannot decide whether {self} is a closed immersion: this is decided here only for "
            f"morphisms of affine schemes over {base}, but the domain is an object of "
            f"{self.domain().category()} and the codomain an object of {self.codomain().category()}"
        )
        return bool(self._engine_pullback_with_trivial_base_map().is_surjective())

    def de_rham_cohomology(self, degree):
        r"""``H^k_dR(X/S) = R^k f_*(Omega^*_{X/S})`` for this arrow ``f: X -> S``.

        The ``k``-th hyperdirect image of the relative de Rham complex, with
        ``k`` equal to ``degree``.  Its value is an object of
        ``QuasiCoherentSheaves(S)``.  When ``f`` is smooth and proper over a
        base of characteristic zero it is a locally free coherent
        ``O_S``-module (Katz, *Nilpotent connections and the monodromy
        theorem*, Publ. Math. IHES 39 (1970), introduction and (3.0)).
        """
        return _relative_de_rham_cohomology(self, degree, ())

    def gauss_manin_connection(self, degree):
        r"""``(H^k_dR(X/S), nabla_GM)`` for a smooth proper ``f: X -> S``.

        ``H^k_dR(X/S)`` is ``f.de_rham_cohomology(k)``, a locally free coherent
        ``O_S``-module, and the Gauss-Manin connection is an integrable
        connection on it relative to the base of ``S`` (Katz, *Nilpotent
        connections and the monodromy theorem*, Publ. Math. IHES 39 (1970),
        introduction and (3.0)).  The value is an object of
        ``VectorBundlesWithConnection(S).Integrable()`` whose underlying
        locally free module is ``f.de_rham_cohomology(k)``.  The caller
        supplies a smooth proper ``f``.
        """
        from sage_extensions.categories.modules.connections import (
            VectorBundlesWithConnection,
            _GaussManinConnection,
        )

        category = VectorBundlesWithConnection(self.codomain()).Integrable()
        bundles = QuasiCoherentSheaves(self.codomain()).FiniteLocallyFree()
        bundle = _relative_de_rham_cohomology(self, degree, (bundles,))
        # Forgetting nabla returns E, so (E, nabla) is the presheaf of sections of E,
        # an object of the fibre [Open(S)^op, D] that holds E.
        presheaves = PresheafObjects(self.codomain())
        fibre = presheaves.with_values(bundle.value_category())
        return _object_of(
            owned_category_join((category, fibre)),
            _engine=(category, _GaussManinConnection, None),
            family_morphism=self,
            degree=degree,
            underlying_vector_bundle=bundle,
            fixed_mor_category=category,
            functor=bundle.open_sections_presheaf(),
            **presheaves.presheaf_datum(bundle.open_sections_presheaf()),
        )

    def __eq__(self, other) -> bool:
        r"""Decide equality on represented pullbacks, else on the native realizations.

        Two affine morphisms are equal when their pullbacks agree on a set of
        elements on which maps out of the codomain algebra are determined; a
        finite set of algebra generators, or the one at the foot of a
        localization tower, supplies it.
        """
        if self is other:
            return True
        if not isinstance(other, SchemeMorphismMethods):
            return False
        if (
            self.domain() is not other.domain()
            or self.codomain() is not other.codomain()
        ):
            return False
        if self._closed_complement is not None or other._closed_complement is not None:
            return (
                self._closed_complement is not None
                and self._closed_complement is other._closed_complement
            )
        left_pullback = self._represented_coordinate_pullback()
        right_pullback = other._represented_coordinate_pullback()
        if left_pullback is not None and right_pullback is not None:
            base = self.codomain().scheme_base_ring()
            determining = _elements_determining_maps_out_of(
                self.codomain().coordinate_algebra(), base
            )
            relative = Schemes(base)
            if (
                determining is not None
                and self.parent().mor_category().is_subcategory(relative)
                and other.parent().mor_category().is_subcategory(relative)
            ):
                return conjunction(
                    left_pullback(element) == right_pullback(element)
                    for element in determining
                )
            return _ring_morphisms_equal(left_pullback, right_pullback)
        return bool(_engine_scheme_morphism(self) == _engine_scheme_morphism(other))

    def __ne__(self, other):
        return negation(self == other)

    def __hash__(self) -> int:
        if (
            self._toric_lattice_morphism is not None
            or self._relative_projectivization_role
            in (
                "base_change_composite",
                "base_change_total",
                "base_change_base",
                "base_projection",
                "surjectivity_open_inclusion",
                "surjectivity_induced_morphism",
            )
        ):
            raise TypeError(f"unhashable type: {type(self).__name__}")
        if self._relative_projectivization_source_sheaf is not None:
            raise TypeError(f"unhashable type: {type(self).__name__}")
        if self._gluing_role in ("chart_map", "finite_atlas", "glued_domain"):
            raise TypeError(f"unhashable type: {type(self).__name__}")
        if self._gluing_role == "open_inclusion":
            position = (
                self.gluing_datum().chart_index_set().ranking_map()(self.chart_index())
            )
            return hash((id(self.gluing_datum()), int(position), "open-image"))
        return hash((id(self.domain()), id(self.codomain())))

    def _repr_(self) -> str:
        if self._gluing_role == "open_inclusion":
            return f"Open inclusion {self.domain()} -> {self.codomain()}"
        if self._gluing_role == "chart_embedding":
            return f"Open chart embedding {self.domain()} -> {self.codomain()} (chart {self.chart_index()})"
        if self._gluing_role == "chart_map":
            return f"Scheme morphism into glued chart {self.chart_index()}: {self.domain()} -> {self.codomain()}"
        if self._gluing_role == "finite_atlas":
            return f"Scheme morphism from finite atlas: {self.domain()} -> {self.codomain()}"
        if self._gluing_role == "glued_domain":
            return f"Scheme morphism from glued charts: {self.domain()} -> {self.codomain()}"
        if self._relative_projectivization_role == "base_change_composite":
            return f"Relative-Proj base-change composite {self.domain()} -> {self.codomain()}"
        if self._relative_projectivization_role == "base_change_total":
            return f"Relative-Proj base-change total map {self.domain()} -> {self.codomain()}"
        if self._relative_projectivization_role == "base_change_base":
            return f"Relative-Proj base-change base map {self.domain()} -> {self.codomain()}"
        if self._relative_projectivization_role == "base_projection":
            return f"Relative-Proj selected base projection {self.domain()} -> {self.codomain()}"
        if self._relative_projectivization_role == "surjectivity_open_inclusion":
            return f"Relative-Proj surjectivity-locus inclusion {self.domain()} -> {self.codomain()}"
        if self._relative_projectivization_role == "surjectivity_induced_morphism":
            return f"Relative-Proj induced map on surjectivity locus {self.domain()} -> {self.codomain()}"
        if self._toric_lattice_morphism is not None:
            return f"Toric scheme morphism {self.domain()} -> {self.codomain()} induced by {self.lattice_morphism()}"
        if self._affine_quotient_base_change_datum is not None:
            return (
                f"Invariant-quotient base-change morphism along {self.ring_map()} "
                f"for {self.source_acted_scheme()}"
            )
        if self._closed_complement is not None:
            return f"Open immersion {self.domain()} -> {self.codomain()} complementing {self._closed_complement}"
        if self._homogeneous_coordinates is not None:
            return f"Projective morphism from {self.domain()} to {self.codomain()} defined by {tuple(self._homogeneous_coordinates)}"
        return f"Scheme morphism: {self.domain()} -> {self.codomain()}"

    def scalar_pullback(self):
        if self._scalar_pullback is None:
            raise AttributeError(f"{self} is not represented by a scalar pullback")
        return self._scalar_pullback


SchemeMorphism = SchemeMorphismMethods


def _open_complement_inclusion(closed_complement):
    r"""The arrow realization rule ``Mor -> (X - Z -> X)`` for the closed complement ``Z``."""

    def realize(mor):
        return mor.element_class(
            mor, None, mor=mor, closed_complement=closed_complement
        )

    return realize


def _projective_coordinate_blocks(scheme):
    r"""The homogeneous coordinate blocks of a projective presentation."""
    base = scheme.scheme_base_ring()
    match scheme:
        case _ if scheme in ProductProjectiveSpaces(base):
            return tuple(
                int(factor.relative_dimension()) + 1 for factor in scheme.factors()
            )
        case _ if scheme in ProjectiveSpaces(base):
            return (int(scheme.relative_dimension()) + 1,)
        case _:
            return _projective_coordinate_blocks(scheme.inclusion().codomain())


def _projective_coordinate_morphism(morphism):
    r"""Read an existing polynomial morphism in its owned coordinate presentation.

    Engine adapter (OWN-06): native polynomial morphisms use the canonical
    map on coefficients.  An already owned coordinate map keeps its stated
    coefficient map instead, including a noncanonical scalar base change.
    """
    if morphism._projective_coordinate_data():
        return morphism
    coordinates = morphism._represented_point_coordinates()
    if coordinates is not None:
        return _ProjectiveCoordinateMorphism(
            morphism.parent(),
            tuple(coordinates),
            point_coordinates=coordinates,
        )
    ring = _constant_sections_ring(morphism.domain())
    if (
        morphism._is_the_identity()
        and morphism.domain()
        not in Schemes(morphism.domain().scheme_base_ring()).Affine()
    ):
        # id_X on a projective X is given by the homogeneous coordinates themselves.
        return _ProjectiveCoordinateMorphism(
            morphism.parent(),
            tuple(
                ring.algebra_generator(name) for name in ring.algebra_generating_set()
            ),
        )
    native = _engine_scheme_morphism(morphism)
    engine = _engine_ring(ring)
    values = tuple(
        _owned_engine_element(ring, engine(value))
        for value in _engine_defining_polynomials(native)
    )
    return _ProjectiveCoordinateMorphism(morphism.parent(), values)


def _constant_sections_ring(source):
    r"""The ring in which coordinate sections on ``source`` are written.

    For affine ``source`` it is the coordinate algebra; for a projective
    ``source`` it is the homogeneous coordinate ring of its ambient
    projective space, read modulo the equations by
    :func:`_projective_section_restriction`.
    """
    base = source.scheme_base_ring()
    if source in Schemes(base).Affine():
        return source.coordinate_algebra()
    ambient, _ = _engine_projective_ambient(_engine_scheme(source))
    return _engine_polynomial_algebra(ambient.coordinate_ring(), base)


@cached_function(key=lambda scheme, ring: (id(scheme), id(ring)))
def _projective_section_restriction(scheme, ring):
    r"""Read coordinate polynomials modulo the equations on the stated source.

    Engine adapter of the scheme-morphism owner.  On ``Proj(P/I)`` a
    homogeneous section vanishes exactly when it vanishes on every standard
    open, hence when it belongs to ``I:B^infinity`` (Stacks, Tag 01M7).
    For a product the standard opens invert one coordinate from each block,
    so ``B`` is the product of the block ideals.  On ``X - V(J)`` the further
    saturation by ``J`` expresses restriction to that open, with nilpotents
    retained.  Saturation is computed by the existing ideal owner, not by a
    finite test of points.  The quotient here represents equality of
    homogeneous sections; it is not advertised as ``Gamma(X, O_X)``.
    """
    if scheme in Schemes(scheme.scheme_base_ring()).Affine():
        algebra = scheme.coordinate_algebra()
        return OwnedRings().Mor(ring, algebra).elementwise(algebra)
    native = _engine_scheme(scheme)
    ambient, equations = _engine_projective_ambient(native)
    engine = _engine_ring(ring)
    variables = tuple(engine.gens())

    def owned(polynomial):
        return _owned_engine_element(
            ring, _copy_polynomial_by_exponents(polynomial, engine, variables)
        )

    ideal = ring.ideal(*(owned(equation) for equation in equations))
    owned_variables = tuple(
        _owned_engine_element(ring, variable) for variable in variables
    )
    blocks = []
    offset = 0
    for width in _projective_coordinate_blocks(scheme):
        blocks.append(owned_variables[offset : offset + width])
        offset += width
    assert offset == len(variables), (
        f"cannot restrict homogeneous polynomials to {scheme}: the homogeneous coordinate ring "
        f"{ring} has {len(variables)} variables, but the projective factors of {scheme} have "
        f"{offset} homogeneous coordinates"
    )
    from sage.misc.misc_c import prod

    irrelevant = ring.ideal(
        *(prod(choice, ring.one()) for choice in cartesian_product(*blocks))
    )
    ideal = ideal.ideal_saturation(irrelevant)
    match native:
        case _SageAlgebraicSchemeQuasi():
            excluded = ring.ideal(
                *(owned(equation) for equation in native.Y().defining_polynomials())
            )
            ideal = ideal.ideal_saturation(excluded)
    return ring.quotient_ring(ideal).quotient_map()


def _scalar_maps_equal_on_scheme(scheme, left, right):
    r"""Compare scalar maps after restricting their images to this scheme."""
    if scheme._is_glued_from_affine_atlas():
        decisions = tuple(
            _scalar_maps_equal_on_scheme(chart, left, right)
            for chart in scheme.gluing_datum().charts()
        )
        return conjunction(decisions)
    base = scheme.scheme_base_ring()
    if scheme in Schemes(base).Affine():
        restriction = scheme.structure_morphism().coordinate_algebra_morphism()
    else:
        ambient, _ = _engine_projective_ambient(_engine_scheme(scheme))
        ring = _engine_polynomial_algebra(ambient.coordinate_ring(), base)
        restriction = _projective_section_restriction(
            scheme, ring
        ) * _restriction_to_base(ring, base)
    mor = OwnedRings().Mor(left.domain(), restriction.codomain())
    return _ring_morphisms_equal(
        mor.elementwise(lambda scalar: restriction(left(scalar))),
        mor.elementwise(lambda scalar: restriction(right(scalar))),
    )


def _ProjectiveCoordinateMorphism(
    mor,
    coordinates,
    *,
    coefficient_map=None,
    cone_construction=None,
    point_coordinates=None,
    standard_projective_chart_embedding=False,
):
    r"""Construct a projective-coordinate arrow in its actual SchemeMor parent.

    The homogeneous sections and coefficient map are defining data of the
    generated ``SchemeMorphismMethods`` element; this factory is not an arrow
    class and cannot create a parallel morphism host.
    """
    coordinates = tuple(coordinates)
    assert coordinates, (
        f"cannot build a morphism {mor.domain()} -> {mor.codomain()} from homogeneous coordinates: no coordinates were given"
    )
    ring = coordinates[0].parent()
    assert all(value.parent() is ring for value in coordinates), (
        f"the homogeneous coordinates {coordinates} do not all lie in the same ring {ring}"
    )
    target_base = mor.codomain().scheme_base_ring()
    if coefficient_map is None:
        coefficient_map = _restriction_to_base(ring, target_base)
    assert (
        coefficient_map.domain() is target_base and coefficient_map.codomain() is ring
    ), f"the coefficient map {coefficient_map} must have parent {target_base} -> {ring}"
    assert sum(_projective_coordinate_blocks(mor.codomain())) == len(coordinates), (
        f"{mor.codomain()} needs {sum(_projective_coordinate_blocks(mor.codomain()))} homogeneous coordinates, "
        f"but {len(coordinates)} were given"
    )
    return mor.element_class(
        mor,
        None,
        mor=mor,
        homogeneous_coordinates=coordinates,
        coefficient_map=coefficient_map,
        cone_construction=cone_construction,
        point_coordinates=point_coordinates,
        standard_projective_chart_embedding=standard_projective_chart_embedding,
    )


def _StandardProjectiveChartEmbedding(
    mor,
    coordinates,
    *,
    coefficient_map=None,
    cone_construction=None,
    point_coordinates=None,
):
    r"""Construct a standard projective chart inclusion as a generated Mor element."""
    return _ProjectiveCoordinateMorphism(
        mor,
        coordinates,
        coefficient_map=coefficient_map,
        cone_construction=cone_construction,
        point_coordinates=point_coordinates,
        standard_projective_chart_embedding=True,
    )


def _StandardMultiprojectiveChartEmbedding(
    native_morphism, *, mor, cone_construction=None, point_coordinates=None
):
    r"""Construct a product-chart inclusion as an element of its actual SchemeMor."""
    return mor.element_class(
        mor,
        native_morphism,
        mor=mor,
        cone_construction=cone_construction,
        point_coordinates=point_coordinates,
        multiprojective_chart_embedding=True,
    )


class SchemeMorCategory(CategoricalMor):
    r"""The owned category \(\mathrm{Mor}_{\mathbf{Sch}/R}(X, Y)\).

    Its objects are the scheme morphisms \(X\to Y\) over ``R``.  An arrow is
    constructed from its defining datum (``CON-16``):

    * an owned scheme morphism with these endpoints, returned, or re-sited
      between affine endpoints through its pullback;
    * an owned ring morphism ``O(Y) -> O(X)`` when both endpoints are affine;
    * a native Sage scheme morphism between the engines of the endpoints;
    * an arrow realization rule, a callable ``Mor -> morphism`` returning an
      element parented by this Mor.  The rule is the datum of arrows whose
      representation class belongs to another construction owner -- the open
      inclusions of a glued scheme, the complement of a projective closed
      subscheme -- and of the inclusion of a subobject, which cannot be built
      before the subobject it starts at.

    Sage's scheme Hom between the two engines stays underneath as the
    computation engine for native realizations; it is built when first asked
    for, so a Mor whose endpoint has no engine still constructs.
    """

    ElementMethods = SchemeMorphismMethods

    def __init__(self, mor_family, domain, codomain) -> None:
        CategoricalMor.__init__(self, mor_family, domain, codomain)

    @cached_method
    def _engine_mor_crossing(self):
        r"""Return the private Sage Mor object these morphisms are computed in."""
        return _native_scheme_mor(self.domain(), self.codomain())

    def _from_engine_morphism(self, datum):
        r"""Raise a selected native scheme computation at its exact owned endpoints.

        Protected engine crossing for the scheme structure and native
        realization owners; public construction takes coordinate pullbacks
        or the construction's defining data.
        """
        domain, codomain = self.domain(), self.codomain()
        assert datum.domain() is _engine_scheme(
            domain
        ) and datum.codomain() is _engine_scheme(codomain)
        if (
            domain in Schemes(domain.scheme_base_ring()).Affine()
            and codomain in Schemes(codomain.scheme_base_ring()).Affine()
        ):
            return self(
                _engine_coordinate_pullback_of(
                    datum, domain.coordinate_algebra(), codomain.coordinate_algebra()
                )
            )
        return self.element_class(self, datum, mor=self)

    def _element_constructor_(self, datum):
        domain = self.domain()
        codomain = self.codomain()
        base = codomain.scheme_base_ring()
        affine_endpoints = (
            domain in Schemes(domain.scheme_base_ring()).Affine()
            and codomain in Schemes(base).Affine()
        )
        match datum:
            case SchemeMorphismMethods() if datum.parent() is self:
                return datum
            case SchemeMorphismMethods() if affine_endpoints:
                raise TypeError(
                    f"{datum} belongs to another Mor; apply the functor between the categories"
                )
            case SchemeMorphismMethods():
                raise TypeError(
                    f"{datum} belongs to another Mor; apply the functor between the categories"
                )
            case _SageSchemeMorphism():
                raise TypeError(
                    "a native scheme arrow is private engine output, not scheme-morphism defining data"
                )
            case Morphism() | CategoricalArrow():
                assert affine_endpoints, (
                    f"cannot make the ring morphism {datum} a morphism {domain} -> {codomain}: a ring morphism "
                    f"defines a morphism of schemes only between affine schemes, and {domain} or {codomain} "
                    "is not affine"
                )
                assert (
                    datum.domain() is codomain.coordinate_algebra()
                    and datum.codomain() is domain.coordinate_algebra()
                ), (
                    f"the pullback {datum} does not join the coordinate algebras of {codomain} and {domain}"
                )
                relative = Schemes(domain.scheme_base_ring())
                if self.mor_category().is_subcategory(relative):
                    ring = relative.base_ring()
                    target_algebra = domain.coordinate_algebra()
                    source_structure = (
                        codomain.structure_morphism().coordinate_algebra_morphism()
                    )
                    target_structure = (
                        domain.structure_morphism().coordinate_algebra_morphism()
                    )
                    ring_mor = OwnedRings().Mor(ring, target_algebra)
                    composed = ring_mor.elementwise(
                        lambda scalar: datum(source_structure(scalar))
                    )
                    structural = ring_mor.elementwise(target_structure)
                    assert _ring_morphisms_equal(composed, structural) is not False, (
                        f"cannot make the pullback {datum} a morphism {domain} -> {codomain} over {ring}: it does "
                        f"not commute with the structure maps from {ring} into the coordinate algebras "
                        f"{codomain.coordinate_algebra()} and {domain.coordinate_algebra()}"
                    )
                return self.element_class(self, None, mor=self, pullback=datum)
            case _ if callable(datum):
                realized = datum(self)
                assert realized.parent() is self, (
                    f"cannot make a morphism {domain} -> {codomain} from the construction rule {datum}: it "
                    f"returned {realized}, a morphism in {realized.parent()}, not in {self}"
                )
                return realized
            case _:
                assert False, (
                    f"{datum} is not a defining datum of a morphism {domain} -> {codomain}"
                )

    @object_level
    @cached_method
    def identity(self):
        r"""``id_X``: the identity pullback on an affine scheme, else the engine identity."""
        assert self.domain() is self.codomain(), (
            f"{self} has no identity: its domain {self.domain()} is not its codomain {self.codomain()}"
        )
        scheme = self.domain()
        match scheme:
            case _ if scheme in Schemes(scheme.scheme_base_ring()).Affine():
                algebra = scheme.coordinate_algebra()
                return self.element_class(
                    self, None, mor=self, pullback=algebra.Mor(algebra).identity()
                )
            case _ if scheme._scheme_engine_realization is None:
                return self.element_class(self, None, mor=self)
            case _:
                return self.element_class(
                    self, _engine_scheme(scheme).identity_morphism(), mor=self
                )


def _restriction_to_base(ring, base_ring):
    r"""The composite ring morphism ``base_ring -> ring`` along the scalar tower of ``ring``.

    ``ring`` is an algebra over its own base, that base over its base, and so
    on down to ``ZZ``; ``base_ring`` is one of the rings of that tower.  The
    composite of the structure morphisms is the structure morphism of
    ``ring`` as a ``base_ring``-algebra, which is the defining datum of the
    restriction of base along ``Spec ring -> Spec base_ring``.
    """
    if ring is base_ring:
        return ring.Mor(ring).identity()
    below = _proper_restriction_base_ring(ring)
    assert below is not None, f"{base_ring} is not a ring of the scalar tower of {ring}"
    match ring.base_ring():
        case _ if ring.base_ring() is below:
            step = ring.algebra_structure_morphism()
        case _:
            # ``below`` is the initial ring, and the ring map out of it is unique.
            step = below.Mor(ring)(lambda integer: ring(integer))
    return step * _restriction_to_base(below, base_ring)


def _scheme_mor_category(domain, codomain, *, category=None):
    r"""The chosen Mor of two schemes, without changing either scalar structure.

    Two schemes with the same stated base use the Mor over that base.
    Across bases an arrow is a morphism of their locally ringed spaces;
    its coordinate pullback retains the actual scalar map.  In particular
    two evaluations of a parameter at different values do not mutate one
    cached spectrum into two incompatible structures (Stacks, Tag 01I1).
    """
    match category:
        case None:
            base = codomain.scheme_base_ring()
            match domain.scheme_base_ring() is base:
                case True:
                    category = Schemes(base)
                case False:
                    category = LocallyRingedSpaces()
    return category.Mor(domain, codomain)


def _scheme_composition_mor(after, before):
    r"""The Mor of a composite, retaining a common base only when both arrows do."""
    category = after.parent().mor_category()
    match before.parent().mor_category().is_subcategory(category):
        case True:
            return category.Mor(before.domain(), after.codomain())
        case False:
            return LocallyRingedSpaces().Mor(before.domain(), after.codomain())


def _affine_structure_morphism_to_base(scheme, base_ring):
    r"""Return ``scheme -> Spec(base_ring)`` in ``Sch/base_ring``.

    Over its own base this is the structure morphism.  Over a coarser base of
    its scalar tower it is ``Spec`` of the composite scalar map, a morphism of
    the scheme restricted to that base.
    """
    base_ring = _own_ring(base_ring)
    own_base = scheme.scheme_base_ring()
    assert scheme in Schemes(own_base).Affine(), (
        f"cannot form the structure morphism {scheme} -> Spec {base_ring}: this construction "
        f"requires an affine scheme, but {scheme} is an object of {scheme.category()}"
    )
    if own_base is base_ring:
        return scheme.structure_morphism()
    scalar_map = (
        scheme.structure_morphism().coordinate_algebra_morphism()
        * _restriction_to_base(own_base, base_ring)
    )
    return _scheme_mor_category(scheme, Schemes(base_ring).base_scheme())(scalar_map)


def _scheme_isomorphism(forward, inverse):
    r"""Return the selected inverse pair in the core of the scheme category.

    A chart overlap can carry distinct open-subobject placements on its two
    sides.  Those placements strengthen the objects, not the category in which
    their transition is an isomorphism: chart changes are arrows in ``Sch/R``.
    """
    assert (
        forward.domain() is inverse.codomain()
        and forward.codomain() is inverse.domain()
    ), (
        f"{forward} and {inverse} are not mutually inverse: {forward} is "
        f"{forward.domain()} -> {forward.codomain()}, but {inverse} is "
        f"{inverse.domain()} -> {inverse.codomain()}"
    )
    schemes = Schemes(forward.codomain().scheme_base_ring())
    return schemes.Core().Mor(forward.domain(), forward.codomain())(forward, inverse)


def _scheme_with_structure(
    scheme,
    category,
    *,
    _engine=None,
    construction_data=None,
):
    r"""Rebuild ``scheme`` once in a stronger scheme category carrying selected data.

    This is the owner-side route for structures whose underlying mathematical
    object is still the same represented scheme, such as a chosen boundary
    divisor.  The private realization is retained verbatim; consumers outside
    the scheme owner never inspect it.  The stronger category must already
    declare ``Schemes(R)`` through its supercategory chain.
    """

    base = scheme.scheme_base_ring()
    assert category.is_subcategory(Schemes(base)), (
        f"cannot make {scheme} an object of {category}: {category} is not a subcategory of the "
        f"schemes over {base}"
    )
    realization = scheme._scheme_engine_realization
    data = dict(construction_data or {})
    return _object_of(
        category,
        _engine=None if _engine is None else (category, _engine, None),
        scheme_base_ring=base,
        scheme_engine=realization,
        **data,
    )


def _affine_morphism_from_pullback(domain, codomain, pullback):
    r"""The affine morphism ``domain -> codomain`` defined by its coordinate pullback."""
    return _scheme_mor_category(domain, codomain)(pullback)


def _affine_spec_morphism(algebra_morphism):
    r"""``Spec(phi): Spec B -> Spec A`` for an algebra morphism ``phi: A -> B``."""
    source_algebra = algebra_morphism.domain()
    target_algebra = algebra_morphism.codomain()
    assert (
        source_algebra
        in Algebras(source_algebra.base_ring()).Associative().Unital().Commutative()
    ), (
        f"cannot apply Spec to {algebra_morphism}: its domain {source_algebra} must be a "
        f"commutative algebra over {source_algebra.base_ring()}, but it is an object of "
        f"{source_algebra.category()}"
    )
    assert (
        target_algebra
        in Algebras(target_algebra.base_ring()).Associative().Unital().Commutative()
    ), (
        f"cannot apply Spec to {algebra_morphism}: its codomain {target_algebra} must be a "
        f"commutative algebra over {target_algebra.base_ring()}, but it is an object of "
        f"{target_algebra.category()}"
    )
    return _affine_morphism_from_pullback(
        target_algebra.affine_spectrum(),
        source_algebra.affine_spectrum(),
        algebra_morphism,
    )


# ---------------------------------------------------------------------------
# The category of schemes over a base ring and its axioms.
# ---------------------------------------------------------------------------


def _etale_comparison_embedding(scheme, invariant):
    r"""The embedding ``sigma: k -> CC`` along which the etale ``invariant`` of ``scheme`` is computed.

    Artin's comparison theorem (Freitag--Kiehl [FK88], Ch. I, Thm. 11.6)
    computes etale cohomology of ``X_{kbar}`` as singular cohomology of
    ``X(CC)`` when ``char k = 0``.  The embedding constructed here is the
    unique one ``QQ -> CC``; any other base is a stated gap.
    """
    from sage.rings.rational_field import QQ as SageQQ

    from sage_extensions.categories.schemes.geometric_cohomology import (
        _rational_complex_embedding,
    )

    base = scheme.scheme_base_ring()
    assert base in OwnedFields(), (
        f"the etale invariant {invariant} of {scheme} is defined through X_kbar for X over a "
        f"field k, but {scheme} is over {base}, which is not a field"
    )
    match base:
        case _ if _engine_ring(base) is SageQQ:
            return _rational_complex_embedding()
        case _ if base.characteristic() == 0:
            assert False, (
                f"the etale invariant {invariant} of {scheme} is computed by comparison along an "
                f"embedding {base} -> CC, and such an embedding is constructed only for QQ"
            )
        case _:
            assert False, (
                f"the etale invariant {invariant} of {scheme} over {base}, of characteristic "
                f"{base.characteristic()}, has no comparison with a complex realization, and "
                "etale cohomology in positive characteristic is not computed"
            )


def _normal_placement(base_ring) -> bool:
    r"""Whether \(\mathbb{A}^n_R\) and \(\mathbb{P}^n_R\) over ``base_ring`` are placed as normal.

    A scheme is normal when its local rings are integrally closed domains.
    Affine ``n``-space over ``R`` is covered by the single polynomial ring
    ``R[x_1,...,x_n]``, and projective ``n``-space by the degree-zero parts of
    its graded localizations, which are again polynomial rings on ``n``
    variables.  A polynomial ring over an integrally closed domain is
    integrally closed, and so is every localization of one, so both spaces are
    normal exactly when ``R`` is.

    The hypothesis stated here is that ``R`` is a principal ideal domain, hence
    a unique factorization domain, hence integrally closed; that covers
    \(\mathbb{Z}\), every field, and every polynomial ring in one variable over
    a field.  Normality is not placed over a base outside that hypothesis.
    """
    return base_ring in OwnedPrincipalIdealDomains()


def _integral_placement(ring) -> bool:
    r"""Whether ``Spec`` of ``ring`` is integral: ``ring`` is placed as an integral domain.

    ``Spec A`` is integral exactly when ``A`` is a domain (Stacks, Tag 01OK);
    the placement of ``A`` is read, and no primality is decided here.
    """
    return ring in OwnedIntegralDomains()


def _function_field_on_atlas(atlas, equations):
    r"""``K(X) = Frac(A)`` for the first nonempty open ``Spec A = X cap U_i`` over the charts of ``atlas``.

    ``X`` is integral, and meets the chart ``U_i -> Y`` of ``atlas`` in the
    closed subscheme of ``U_i`` cut out by the pullbacks of ``equations``
    along the chart's homogeneous coordinates; no equations means ``X = Y``.
    That intersection is empty exactly when the pulled-back equations
    generate the unit ideal.  A nonempty open of an integral scheme is
    integral (Mathlib ``AlgebraicGeometry.isIntegral_of_isOpenImmersion``),
    so its coordinate ring is a domain (Stacks, Tag 01OK) whose fraction
    field is ``K(X)`` (Mathlib
    ``AlgebraicGeometry.functionField_isFractionRing_of_isAffineOpen``).
    """
    from sage_extensions.categories.algebras.free_algebras import (
        _quotient_by_algebra_elements_backend,
    )

    for label in atlas.chart_index_set():
        algebra = atlas.chart(label).coordinate_algebra()
        coordinates = tuple(
            _projective_coordinate_morphism(
                atlas.member(label).domain().arrow()
            ).homogeneous_coordinates()
        )
        local_equations = tuple(
            _evaluate_owned_homogeneous_polynomial_on_coordinates(
                equation, equation.parent(), coordinates
            )
            for equation in equations
        )
        match local_equations:
            case () if algebra in OwnedIntegralDomains():
                return algebra.fraction_field()
            case ():
                empty = algebra.one() == algebra.zero()
            case _:
                empty = algebra.ideal(*local_equations).contains_ambient_element(
                    algebra.one()
                )
        if empty is True:
            continue
        domain, _quotient_map = _quotient_by_algebra_elements_backend(
            algebra, local_equations, extra_categories=(OwnedIntegralDomains(),)
        )
        return domain.fraction_field()
    assert False, (
        f"an integral scheme has a nonempty affine open, but its pullback to every chart of {atlas} "
        "is empty"
    )


def _affine_scheme(algebra, base, placements=(), **level_data):
    r"""Construct ``Spec A`` over ``Spec R`` in ``Schemes(R).Affine()`` joined with ``placements``.

    This is the construction behind the entry ``Schemes(R).Affine()(A)``;
    specialized affine constructions -- a distinguished open, an affine closed
    subscheme, an affine product, an acted scheme -- reach it with their own
    placement and the level data those placements declare.  The placements
    implied by ``A`` are stated here once: a framed algebra is of finite type,
    hence quasi-projective (Stacks, Tag 01VW for affine morphisms of finite
    type); ``Spec R`` is smooth over itself; a domain gives an integral scheme.
    """
    schemes = Schemes(base)
    categories = [schemes.Affine()]
    match algebra in OwnedRings().Noetherian():
        case True:
            categories.append(schemes.LocallyNoetherian())
        case False:
            pass
    if algebra is base or (
        algebra.is_framed_algebra()
        and algebra.algebra_generating_set().cardinality().is_finite()
    ):
        categories.extend((schemes.FiniteType(), schemes.QuasiProjective()))
    if algebra is base:
        categories.append(schemes.Smooth())
        if _normal_placement(base):
            categories.append(schemes.Normal())
    if _integral_placement(algebra):
        categories.append(schemes.Integral())
    return _object_of(
        owned_category_join((*categories, *placements)),
        scheme_base_ring=base,
        scheme_engine=_engine_affine_spectrum(algebra, base),
        coordinate_algebra=algebra,
        **level_data,
    )


@cached_function(key=lambda algebra, base: (id(algebra), id(base)))
def _affine_spectrum_over(algebra, base):
    r"""The selected ``Spec A`` over ``Spec R``, one object for each ``(A, R)``."""
    return _affine_scheme(algebra, base)


def _affine_spectrum(ring_or_algebra, base_ring=None):
    r"""Return the affine scheme ``Spec(A)`` over its scalar base.

    If ``A`` is an owned commutative ``R``-algebra, the result lies in
    ``Schemes(R)`` and its structure morphism is ``Spec`` of ``R -> A``.  A
    ring stated as its own base, ``Spec(R, base_ring=R)``, is the terminal
    affine ``R``-scheme.  Omitting the base retains the algebra's own base; a
    ring whose base is itself, or whose base has the same engine, is over
    itself.
    """
    algebra = _own_ring(ring_or_algebra)
    match base_ring:
        case None:
            declared = algebra.base_ring()
            base = (
                algebra
                if declared is None or _engine_ring(declared) is _engine_ring(algebra)
                else _own_ring(declared)
            )
        case _:
            base = _own_ring(base_ring)
    return Schemes(base).Affine()(algebra)


class SchemeMorCategoryConstruction(LocallyRingedMorCategoryConstruction):
    r"""Morphisms commuting with the chosen structure maps to ``Spec R``.

    Unlike an axiom on an R-scheme, specifying R restricts the morphisms:
    its Mor is not the unrestricted locally ringed-space Mor.
    """

    def _inherits_morphisms_from(self, supercategory, domain, codomain):
        return supercategory.is_subcategory(Schemes(self.base_category().base_ring()))


class Schemes(OwnedCategoryOverBaseRing):
    r"""Schemes over ``Spec(R)`` for the represented base ring ``R``.

    Objects are schemes ``X`` with a structure morphism ``X -> Spec R``;
    morphisms are morphisms over ``Spec R``.  The level datum is ``R`` itself
    and the private Sage scheme realizing ``X``, or ``None`` for a scheme
    presented without one.
    """

    def parameter_category(self):
        r"""Classical ``Spec(R)`` requires a commutative unital base ring."""
        return OwnedRings().Commutative()

    def an_object(self):
        r"""The affine line over the base ring."""
        return AffineSpaces(self.base_ring())(1)

    def _repr_object_names(self):
        return f"schemes over {self.base_ring()}"

    def super_categories(self):
        r"""A scheme is a locally ringed space.

        Restriction along ``Spec R -> Spec R_0`` is a functor obtained from
        this category, never a supercategory declaration: Sage applies every
        axiom along a declared edge, and finite type, smoothness and
        projectivity do not descend that composite.
        """
        return [LocallyRingedSpaces()]

    _MorCategory = SchemeMorCategoryConstruction

    @property
    def _SliceCategory(self):
        r"""Supply the scheme realization of ``Sch/R`` over ``Y``: families over ``Y``, with their fibres."""
        from sage_extensions.categories.schemes.families import _SchemeSlice

        return _SchemeSlice

    def Mor(self, domain, codomain):
        r"""``Mor_{Sch/R}(X, Y)``, the single Mor selected by its category family."""
        return self.MorCategory().Of(domain, codomain)

    _MonoCategory = None  # set below, once SchemeMonomorphisms is defined

    class SubcategoryMethods:
        def base_change_functor(self, ring_map):
            r"""Return ``- x_{Spec R} Spec R' : Sch/R -> Sch/R'`` along ``R -> R'``."""
            from sage_extensions.categories.schemes.base_change import (
                _scheme_base_change_functor,
            )

            assert _owned_ring(ring_map.domain()) is self.base_ring(), (
                f"cannot form the base change of {self} along {ring_map}: the ring map must start at the "
                f"base ring {self.base_ring()}, but it starts at {ring_map.domain()}"
            )
            return _scheme_base_change_functor(ring_map)

        @cached_method
        def picard_functor(self):
            r"""``Pic : C^op -> Mod_ZZ`` on this category ``C`` of schemes.

            ``op(X)`` goes to the Picard group ``Pic(X)`` of isomorphism
            classes of invertible ``O_X``-modules, an abelian group and so a
            ``ZZ``-module, and ``op(f)`` for ``f: X -> Y`` goes to the pullback
            ``f^* : Pic(Y) -> Pic(X)`` (Hartshorne, *Algebraic Geometry*,
            II.6).
            """
            from sage_extensions.categories.divisors.picard_groups import _PicardFunctor

            return _PicardFunctor(self)

        def product(self, factors):
            r"""Return $\prod_{i \in I} X_i$ for an indexed family of schemes.

            The product is taken over the index set: the coordinates of every
            factor sit side by side in the one product, so the projection to
            the factor at $i$ is an arrow out of that product rather than a
            composite through nested binary products.
            """
            return self._categorical_product_construction(factors).object()

        def _categorical_product_construction(self, factors):
            r"""Return the selected finite scheme product with its universal cone."""
            from sage_extensions.categories.abstract_categories.products import (
                SelectedLimitConstruction,
                _discrete_diagram,
            )

            family = _finite_factor_family(factors, name="Product factors")
            if any(factor not in self for factor in family):
                raise TypeError(
                    f"cannot form the product in {self} of {family}: every factor must be an object of "
                    f"{self}, and {next(factor for factor in family if factor not in self)} is not"
                )
            labels = tuple(family.index_set())
            match len(labels):
                case 0:
                    product = Schemes(self.base_ring()).base_scheme()
                case 1:
                    product = family[labels[0]]
                case _:
                    product = _selected_scheme_product(family)
            diagram = _discrete_diagram(family, self)

            def projection(index):
                label = index.value()
                match len(labels):
                    case 1:
                        return product.categorical_identity_morphism()
                    case _:
                        return product.projection(label)

            universal_cone = diagram.ProductCones().cone(product, projection)

            def factorizer(cone):
                match len(labels):
                    case 0:
                        apex_map = self.Mor(cone.apex(), product)(
                            cone.apex().structure_morphism()
                        )
                    case 1:
                        apex_map = cone.structure_morphism(diagram.domain()(labels[0]))
                    case _:
                        legs = indexed_family(
                            family.index_set(),
                            lambda label: cone.structure_morphism(
                                diagram.domain()(label)
                            ),
                            name="Scheme product cone legs",
                        )
                        apex_map = product.from_product_cone(legs)
                return (
                    diagram.Cones()
                    .Mor(cone, universal_cone)
                    ._from_commuting_apex_map(apex_map)
                )

            return SelectedLimitConstruction(diagram, universal_cone, factorizer)

        def _categorical_product(self, left, right):
            return self._categorical_product_construction((left, right)).object()

        def fiber_product(self, left_leg, right_leg):
            r"""Return the fiber product of the cospan these two legs form."""
            assert left_leg.codomain() is right_leg.codomain(), (
                f"{left_leg} and {right_leg} do not form a cospan: their codomains "
                f"{left_leg.codomain()} and {right_leg.codomain()} differ"
            )
            return self._categorical_pullback(left_leg, right_leg)

        def _categorical_pullback(self, left_morphism, right_morphism):
            return _scheme_fiber_product(left_morphism, right_morphism)

        def equalizer(self, left, right):
            r"""Return the equalizer ``Eq(f, g) -> X`` of two parallel morphisms."""
            assert (
                left.domain() is right.domain() and left.codomain() is right.codomain()
            ), (
                f"cannot form the equalizer of {left} and {right}: they are not parallel; they are "
                f"{left.domain()} -> {left.codomain()} and {right.domain()} -> {right.codomain()}"
            )
            return self._categorical_equalizer(left, right)

        def _categorical_equalizer(self, left, right):
            r"""``Eq(f, g)`` for affine ``f, g: Spec A -> Spec B``.

            The equalizer is the closed subscheme cut out by the ideal
            ``(f^#(b) - g^#(b) : b in B)``; a chosen generating set of ``B``
            generates that ideal because both pullbacks are ``R``-algebra maps.
            Its universal property is that of the closed immersion: ``h: T -> X``
            factors through it exactly when ``h^#`` kills the ideal, which is
            ``f h = g h`` (Stacks, Tag 01JR).
            """
            source = left.domain()
            target = left.codomain()
            base = source.scheme_base_ring()
            assert (
                source in Schemes(base).Affine() and target in Schemes(base).Affine()
            ), (
                f"cannot form the equalizer of {left} and {right}: this computation requires affine "
                f"schemes over {base}, but the domain {source} is an object of {source.category()} and "
                f"the codomain {target} an object of {target.category()}"
            )
            target_algebra = target.coordinate_algebra()
            assert target_algebra.is_framed_algebra(), (
                f"cannot form the equalizer of {left} and {right}: the coordinate algebra "
                f"{target_algebra} of the codomain must have a chosen set of algebra generators, but it "
                f"is an object of {target_algebra.category()}"
            )
            left_pullback = left.coordinate_algebra_morphism()
            right_pullback = right.coordinate_algebra_morphism()
            equations = tuple(
                left_pullback(target_algebra.algebra_generator(label))
                - right_pullback(target_algebra.algebra_generator(label))
                for label in target_algebra.algebra_generating_set()
            )
            equalizer = source.closed_subscheme(equations)
            assert left * equalizer.inclusion() == right * equalizer.inclusion(), (
                f"the closed subscheme {equalizer} of {source} does not equalize {left} and {right}: the "
                "two composites with its inclusion differ"
            )
            return equalizer

        def Affine(self):
            r"""Return this category with the axiom that its objects are affine."""
            return self._with_axiom("Affine")

        def QuasiAffine(self):
            r"""Return this category with the axiom that its objects are quasi-affine."""
            return self._with_axiom("QuasiAffine")

        def Projective(self):
            r"""Return this category with the axiom that its objects are projective over the base."""
            return self._with_axiom("Projective")

        def QuasiProjective(self):
            r"""Return this category with the axiom that its objects are quasi-projective over the base."""
            return self._with_axiom("QuasiProjective")

        def Separated(self):
            r"""Return this category with the axiom that its objects are separated."""
            return self._with_axiom("Separated")

        def FiniteType(self):
            r"""Return this category with the axiom that its objects are of finite type over the base."""
            return self._with_axiom("FiniteType")

        def Proper(self):
            r"""Return this category with the axiom that its objects are proper over the base."""
            return self._with_axiom("Proper")

        def CalabiYau(self):
            r"""Return this category with the axiom that its objects are Calabi--Yau over the base."""
            return self._with_axiom("CalabiYau")

        def LocallyNoetherian(self):
            r"""Return this category with the axiom that its objects are locally Noetherian."""
            return self._with_axiom("LocallyNoetherian")

        def Integral(self):
            r"""Return this category with the axiom that its objects are integral."""
            return self._with_axiom("Integral")

        def Normal(self):
            r"""Return this category with the axiom that its objects are normal."""
            return self._with_axiom("Normal")

        def Smooth(self):
            r"""Return this category with the axiom that its objects are smooth over the base."""
            return self._with_axiom("Smooth")

    @cached_method
    def base_scheme(self):
        r"""``Spec R``, the terminal object of ``Sch/R``."""
        return self.Affine()(self.base_ring())

    @cached_method
    def slice_category(self):
        return self.SliceOver(self.base_scheme())

    def as_slice_object(self, scheme):
        assert scheme in self, f"{scheme} is not an object of {self}"
        return self.slice_category()(scheme.structure_morphism())

    @cached_method
    def coslice_category(self):
        r"""``Spec R / Sch_R``, where the pointed ``R``-schemes live.

        An object is a morphism ``Spec R -> X`` and a morphism is a triangle
        under ``Spec R``.  A family ``X -> S`` is an object of the slice and a
        point of ``X`` is an object of the coslice; the two constructions are
        opposite and neither stands in for the other.
        """
        return self.CosliceUnder(self.base_scheme())

    def as_coslice_object(self, point):
        r"""Read a morphism ``Spec R -> X`` as a pointed ``R``-scheme."""
        assert point.domain() is self.base_scheme(), (
            f"cannot read {point} as a pointed scheme over {self.base_ring()}: its domain must be "
            f"{self.base_scheme()}, but it is {point.domain()}"
        )
        assert point.codomain() in self, (
            f"cannot read {point} as a pointed scheme over {self.base_ring()}: its codomain "
            f"{point.codomain()} is not an object of {self}"
        )
        return self.coslice_category()(point)

    def glue_affine_charts(self, left_chart, right_chart, transition):
        r"""Glue two affine charts along the represented open isomorphism ``transition``."""
        from sage_extensions.categories.schemes.gluing import (
            _TwoChartSchemeGluingDatum,
        )

        return _TwoChartSchemeGluingDatum(
            self, left_chart, right_chart, transition
        ).scheme()

    def glue_affine_atlas(self, charts, transitions, placements=(), **level_data):
        r"""Glue a finite affine atlas with represented distinguished-open transitions.

        ``placements`` are further categories the glued scheme is an object of
        by its construction, with the level data they declare: the open
        complement of a closed subscheme is glued as an object of
        ``OpenImmersions(X)``, a mixed product as an object of
        ``ProductSchemes(R)``.
        """
        from sage_extensions.categories.schemes.gluing import (
            _FiniteSchemeGluingDatum,
        )

        return _FiniteSchemeGluingDatum(
            self,
            charts,
            transitions,
            placements=placements,
            level_data=level_data,
        ).scheme()

    class ParentMethods:
        _derived_construction_parameters = frozenset({"topology_data"})

        def __contains__(self, point) -> bool:
            if self.has_selected_finite_affine_atlas():
                return point in self.underlying_space()
            return element_parent(point) is self

        def _element_constructor_(self, point):
            if self.has_selected_finite_affine_atlas():
                return self.underlying_space()(point)
            match element_parent(point) is self:
                case True:
                    return point
                case False:
                    assert False, (
                        f"{point} is not a point of {self}: points of a scheme glued from affine "
                        "charts are constructed only from points of its charts"
                    )

        def underlying_space(self):
            r"""The topological space retained by this scheme's construction."""
            if self._is_glued_from_affine_atlas():
                return self._scheme_engine_realization.underlying_space()
            if self.has_selected_finite_affine_atlas():
                return (
                    self.selected_finite_affine_atlas()
                    .presentation()
                    .scheme()
                    .underlying_space()
                )
            return self

        @cached_method
        def structure_sheaf(self):
            r"""``O_X`` from the affine presentation or selected affine atlas.

            On an affine scheme use its coordinate algebra. On an atlas,
            global functions are compatible chart functions, and basis
            restrictions use the retained overlap maps (Hartshorne, II.1.22).
            """
            if self in Schemes(self.scheme_base_ring()).Affine():
                from sage_extensions.categories.schemes.ringed_spaces import (
                    _structure_sheaf,
                )

                return _structure_sheaf(self)
            from sage_extensions.categories.schemes.gluing import (
                _finite_atlas_structure_sheaf,
            )

            atlas = self.selected_finite_affine_atlas()
            functions = atlas.global_function_algebra()
            restrictions = indexed_family(
                atlas.chart_index_set(),
                atlas.global_function_restriction,
                name="Restrictions of compatible global functions to affine charts",
            )
            return _finite_atlas_structure_sheaf(atlas, functions, restrictions)

        def _glued_chart_point_map(self, index):
            r"""Supply a selected chart's continuous map to the glued point space.

            Protected scheme-realization operation. Its callers are the chart
            embedding and chart-image inclusion realizations in ``gluing``.
            """
            assert self.has_selected_finite_affine_atlas(), (
                f"{self} has no selected affine gluing presentation"
            )
            if self._is_glued_from_affine_atlas():
                return self._scheme_engine_realization.chart_point_map(index)
            return (
                self.selected_finite_affine_atlas()
                .presentation()
                .scheme()
                ._glued_chart_point_map(index)
            )

        def _glued_chart_image_subset(self, index):
            r"""Supply the point-space subset for a selected affine chart image.

            Protected realization operation consumed by
            ``OpenImmersions.ParentMethods.open_subset``.
            """
            assert self._is_glued_from_affine_atlas(), (
                f"{self} has no selected affine gluing presentation"
            )
            return self._scheme_engine_realization.chart_image_subset(index)

        def __init__(
            self, scheme_base_ring, scheme_engine=None, topology_data=None, **rest
        ) -> None:
            r"""``R``, the Zariski topology of ``X``, and the private Sage scheme realizing ``X``.

            The realization is private computation state, not a mathematical
            datum: a scheme glued from charts is presented without one, and
            omits it.  The Zariski topology is the topology of the space ``X``
            itself, supplied to the topological-space level.  An affine scheme
            ``Spec A`` supplies the topology of the prime spectrum of ``A``; a
            scheme glued from charts has the glued topology.
            """
            from sage_extensions.categories.schemes.ringed_spaces import (
                _SchemeTopologyData,
            )

            self._scheme_base_ring = scheme_base_ring
            self._scheme_engine_realization = scheme_engine
            match topology_data:
                case None:
                    zariski_topology = _SchemeTopologyData()
                case _:
                    zariski_topology = topology_data
            super().__init__(
                base=scheme_base_ring, topology_data=zariski_topology, **rest
            )

        def _scheme_engine(self):
            r"""The private Sage scheme realizing this scheme (``OWN-06``)."""
            assert self._scheme_engine_realization is not None, (
                f"cannot compute with {self} in Sage: it was constructed without a Sage scheme (for "
                "instance by gluing affine charts)"
            )
            match self._is_glued_from_affine_atlas():
                case True:
                    return self._scheme_engine_realization._native_realization_for_scheme_adapter()
                case False:
                    return self._scheme_engine_realization

        def _is_glued_from_affine_atlas(self) -> bool:
            r"""Whether this scheme is realized by the affine gluing datum it was glued from."""
            return _is_gluing_realization(self._scheme_engine_realization)

        def _repr_(self) -> str:
            r"""A glued scheme by its base and charts; otherwise the Sage scheme realizing it."""
            match self._is_glued_from_affine_atlas():
                case True:
                    return (
                        f"Scheme over {self.scheme_base_ring()} glued from the affine charts "
                        f"{self.gluing_datum().charts()}"
                    )
                case False:
                    match self._scheme_engine_realization:
                        case None:
                            return f"Scheme over {self.scheme_base_ring()}"
                        case engine:
                            return repr(engine)

        def gluing_datum(self):
            r"""The affine gluing datum this scheme was glued from (Stacks, Tag 01JA).

            Charts ``U_i``, overlaps ``U_ij <= U_i`` and transition isomorphisms
            satisfying the cocycle condition: the chosen presentation of a
            scheme built by :meth:`Schemes.glue_affine_atlas` or
            :meth:`Schemes.glue_affine_charts`, whose charts, overlaps and
            chart embeddings are read from it.
            """
            assert self._is_glued_from_affine_atlas(), (
                f"{self} was not glued from an affine gluing datum"
            )
            return self._scheme_engine_realization.gluing_datum()

        @cached_method
        def finite_affine_atlas(self):
            r"""Return the finite affine atlas selected when this scheme was glued.

            The gluing datum remains the private transition/cocycle engine;
            the public atlas is the object of ``FiniteAffineAtlases(X)`` whose
            chart arrows are this glued scheme's represented open embeddings.
            """
            assert self._is_glued_from_affine_atlas(), (
                f"{self} has no finite affine atlas from its construction: it was not glued from affine "
                "charts"
            )
            from sage_extensions.categories.schemes.gluing import (
                FiniteAffineAtlases,
            )

            return FiniteAffineAtlases(self)._from_gluing_presentation(
                self.gluing_datum(),
            )

        def selected_finite_affine_atlas(self):
            r"""Return this scheme's construction-selected finite affine atlas.

            Glued schemes retain the atlas used to construct them.  Projective
            and multiprojective spaces retain their standard affine atlases.
            Other represented schemes do not acquire an atlas merely because a
            finite affine cover may exist abstractly.
            """
            base = self.scheme_base_ring()
            match self:
                case _ if self._is_glued_from_affine_atlas():
                    return self.finite_affine_atlas()
                case _ if self in ProjectiveSpaces(base):
                    return self.standard_affine_atlas()
                case _ if self in ProductProjectiveSpaces(base):
                    return self.standard_affine_atlas()
                case _ if self in ClosedSubschemes(base) and (
                    self.inclusion().codomain() in ProjectiveSpaces(base)
                    or self.inclusion().codomain() in ProductProjectiveSpaces(base)
                ):
                    return self.standard_affine_atlas()
                case _:
                    raise TypeError(
                        f"{self} has no finite affine atlas chosen at its construction: it was not glued from "
                        "affine charts and is not a projective space or a product of projective spaces; it is an "
                        f"object of {self.category()}"
                    )

        def has_selected_finite_affine_atlas(self) -> bool:
            r"""Whether construction selected a concrete finite affine atlas for this scheme."""
            base = self.scheme_base_ring()
            match self:
                case _ if self._is_glued_from_affine_atlas():
                    return True
                case _ if self in ProjectiveSpaces(base):
                    return True
                case _ if self in ProductProjectiveSpaces(base):
                    return True
                case _ if self in ClosedSubschemes(base) and (
                    self.inclusion().codomain() in ProjectiveSpaces(base)
                    or self.inclusion().codomain() in ProductProjectiveSpaces(base)
                ):
                    return True
                case _:
                    return False

        def is_covered_by_open_immersions(self, embeddings) -> bool:
            r"""Decide joint coverage for the represented open-cover regimes owned here.

            The input maps are open immersions ``U_i -> X``.  Joint coverage is
            exact in the regimes represented by the scheme construction itself:
            an identity member, the selected affine-gluing atlas, and a family of
            distinguished opens of an affine scheme.  Projective and product-
            projective standard atlases are additional theorem-backed cases of
            this same scheme-level coverage operation.

            This is the admission decision used by the represented Zariski
            coverage; an unrepresented cover is rejected rather than silently
            acquiring a coverage placement.
            """
            family = finite_family(
                tuple(embeddings),
                name="Open immersions proposed as a Zariski cover",
            )
            identity = self.categorical_identity_morphism()
            match any(embedding == identity for embedding in family):
                case True:
                    return True
                case False:
                    pass

            # A base-changed Zariski cover is a cover (Stacks, Tag 00VI).
            # Read its original arrows from the retained pullback cospans.
            original_embeddings = []
            base_changes = []
            for embedding in family:
                chart = embedding.domain()
                if chart not in FiberProductSchemes(chart.scheme_base_ring()):
                    break
                left, right = chart.fiber_product_cospan()
                if embedding is chart.right_projection():
                    original_embeddings.append(left)
                    base_changes.append(right)
                elif embedding is chart.left_projection():
                    original_embeddings.append(right)
                    base_changes.append(left)
                else:
                    break
            else:
                if base_changes and all(
                    (base_change == base_changes[0]) is True
                    for base_change in base_changes
                ):
                    return (
                        base_changes[0]
                        .codomain()
                        .is_covered_by_open_immersions(original_embeddings)
                    )

            match self._is_glued_from_affine_atlas():
                case True:
                    selected = self.gluing_datum()
                    match all(
                        any(
                            embedding == selected.chart_embedding(index)
                            for embedding in family
                        )
                        for index in selected.chart_indices()
                    ):
                        case True:
                            return True
                        case False:
                            pass
                case False:
                    pass

            base = self.scheme_base_ring()
            match self:
                case _ if self in ProjectiveSpaces(base):
                    standard = finite_family(
                        tuple(
                            self.standard_affine_chart_embedding(index)
                            for index in range(int(self.relative_dimension()) + 1)
                        ),
                        name="Standard projective affine cover embeddings",
                    )
                    match all(
                        any(embedding == standard_embedding for embedding in family)
                        for standard_embedding in standard
                    ):
                        case True:
                            return True
                        case False:
                            pass
                case _ if self in ProductProjectiveSpaces(base):
                    _choices, _charts, standard_embeddings = (
                        self._standard_affine_cover_charts_and_embeddings()
                    )
                    match all(
                        any(embedding == standard_embedding for embedding in family)
                        for standard_embedding in standard_embeddings.values()
                    ):
                        case True:
                            return True
                        case False:
                            pass
                case _:
                    pass

            match self in Schemes(base).Affine():
                case True:
                    match all(
                        embedding.domain() in OpenImmersions(self)
                        and (embedding == embedding.domain().inclusion()) is True
                        and embedding.domain().is_distinguished_open() is True
                        for embedding in family
                    ):
                        case True:
                            algebra = self.coordinate_algebra()
                            elements = tuple(
                                embedding.domain().distinguished_open_element()
                                for embedding in family
                            )
                            return bool(
                                algebra.ideal(*elements).contains_ambient_element(
                                    algebra.one()
                                )
                            )
                        case False:
                            pass
                case False:
                    pass

            raise ValueError(
                f"cannot decide whether the open immersions {family} cover {self}: the family is not the "
                f"identity, does not contain the affine charts {self} was glued from or its selected standard "
                "projective charts, and is not a family of distinguished open subschemes of an affine scheme"
            )

        def chartwise_closed_subscheme(
            self,
            local_closed_subschemes,
            *,
            name="Chartwise closed subscheme",
            placements=(),
            _engine=None,
            construction_data=None,
        ):
            r"""The closed subscheme glued from closed subschemes ``Z_i <= U_i`` that agree on the overlaps."""
            assert self._is_glued_from_affine_atlas(), (
                f"cannot glue closed subschemes of the charts of {self}: it was not glued from affine charts"
            )
            return self._scheme_engine_realization.chartwise_closed_subscheme(
                local_closed_subschemes,
                name=name,
                placements=placements,
                _engine=_engine,
                construction_data=construction_data,
            )

        def chartwise_fixed_subscheme(self, local_automorphisms):
            r"""The fixed subscheme of an automorphism preserving each chart, glued from the charts' fixed subschemes."""
            assert self._is_glued_from_affine_atlas(), (
                f"cannot glue fixed subschemes of the charts of {self}: it was not glued from affine charts"
            )
            return self._scheme_engine_realization.chartwise_fixed_subscheme(
                local_automorphisms
            )

        def c2_chartwise_invariant_quotient(
            self,
            acting_group,
            local_actions,
            *,
            _engine=None,
            construction_data=None,
        ):
            r"""This scheme modulo a ``C_2`` action preserving each chart, glued from the charts' invariant quotients."""
            assert self._is_glued_from_affine_atlas(), (
                f"cannot glue invariant quotients of the charts of {self}: it was not glued from affine "
                "charts"
            )
            return self._scheme_engine_realization.c2_chartwise_invariant_quotient(
                self,
                acting_group,
                local_actions,
                _engine=_engine,
                construction_data=construction_data,
            )

        def _locally_ringed_mor_class(self):
            r"""The arrow engine for this scheme's affine/native or gluing presentation."""
            match self._is_glued_from_affine_atlas():
                case True:
                    return self._scheme_engine_realization.scheme_mor_class()
                case False:
                    return SchemeMorCategory

        def Mor(self, codomain, category=None):
            return _scheme_mor_category(self, codomain, category=category)

        def morphism_from_finite_atlas(self, codomain, local_maps, *, atlas=None):
            r"""Glue a morphism from compatible maps on one selected finite affine atlas."""
            match atlas:
                case None:
                    atlas = self.selected_finite_affine_atlas()
                case _:
                    pass
            from sage_extensions.categories.schemes.gluing import (
                _finite_atlas_scheme_morphism,
            )

            return _finite_atlas_scheme_morphism(
                self,
                codomain,
                atlas,
                local_maps,
            )

        def scheme_base_ring(self):
            return self._scheme_base_ring

        def scheme_category(self):
            return Schemes(self.scheme_base_ring())

        def log_pair(self, boundary_divisor):
            r"""Return the log pair ``(self, boundary_divisor)``."""
            from sage_extensions.categories.schemes.log_pairs import _log_pair

            return _log_pair(self, boundary_divisor)

        def base_scheme(self):
            return self.scheme_category().base_scheme()

        @cached_method
        def structure_morphism(self):
            r"""``X -> Spec R``: ``Spec`` of the algebra structure for affine ``X``, glued from the charts' for a glued ``X``, else the realization's."""
            base_scheme = self.base_scheme()
            base = self.scheme_base_ring()
            match self:
                case _ if self is base_scheme:
                    return self.categorical_identity_morphism()
                case _ if self._is_glued_from_affine_atlas():
                    return self._scheme_engine_realization.structure_morphism(self)
                case _ if self in Schemes(base).Affine():
                    algebra = self.coordinate_algebra()
                    pullback = _restriction_to_base(algebra, base)
                    mor = _scheme_mor_category(self, base_scheme)
                    return mor.element_class(mor, None, mor=mor, pullback=pullback)
                case _ if self._scheme_engine_realization is None:
                    mor = _scheme_mor_category(self, base_scheme)
                    return mor.element_class(mor, None, mor=mor)
                case _:
                    return _scheme_mor_category(
                        self, base_scheme
                    )._from_engine_morphism(_engine_scheme(self).base_morphism())

        def dimension(self):
            r"""The Krull dimension of ``Spec A`` for affine ``X``, else the realization's."""
            match self:
                case _ if self in Schemes(self.scheme_base_ring()).Affine():
                    return self.coordinate_algebra().krull_dimension()
                case _:
                    return _owned_engine_element(
                        SageZZ,
                        SageZZ(_engine_scheme(self).dimension()),
                    )

        def relative_dimension(self):
            r"""The relative dimension of ``X -> Spec R``.

            Zero for ``Spec R``; the number of coordinates of an affine space;
            ``dim A - dim R`` for another affine scheme, the relative dimension
            of an equidimensional scheme of finite type and flat over an
            integral base; the sum over the factors of a product; otherwise the
            realization's.
            """
            base = self.scheme_base_ring()
            match self:
                case _ if self is self.base_scheme():
                    return _owned_engine_element(SageZZ, SageZZ.zero())
                case _ if self in AffineSpaces(base):
                    return (
                        self.coordinate_algebra().algebra_generating_set().cardinality()
                    )
                case _ if self in ProductSchemes(base):
                    return _owned_engine_element(
                        SageZZ,
                        SageZZ(
                            sum(
                                int(factor.relative_dimension())
                                for factor in self.factors()
                            )
                        ),
                    )
                case _ if self in Schemes(base).Affine():
                    return self.dimension() - base.krull_dimension()
                case _ if base in OwnedFields():
                    return self.dimension()
                case _:
                    return _owned_engine_element(
                        SageZZ,
                        SageZZ(_engine_scheme(self).dimension_relative()),
                    )

        def is_affine(self):
            r"""Whether the structure morphism to ``Spec R`` is affine.

            Since the base is affine, this is equivalent to this scheme
            being affine (Stacks, Definition 29.11.1). It is independent
            of any additional Dynkin type or other chosen structure.
            An affine placement decides it; a selected construction supplies
            its decision otherwise. A scheme given without that computation
            retains the exact proposition. Having a native scheme model
            alone does not supply an affineness algorithm.
            """
            match self:
                case _ if self in Schemes(self.scheme_base_ring()).Affine():
                    return True
                case _:
                    return self._affineness_decision()

        @RealizationHook
        def _affineness_decision(self):
            r"""Supply the affineness proposition from retained construction data.

            Protected scheme computation contract. The public predicate
            calls this supplier; a toric fan or a retained underlying scheme
            can decide it without requiring a native engine. The default
            retains the proposition when no algorithm has been selected.
            """
            return AtomicProposition("is_affine", self)

        def is_smooth(self) -> bool:
            r"""Whether ``X -> Spec R`` is smooth: by placement, else by the realization's Jacobian criterion."""
            match self:
                case _ if self in Schemes(self.scheme_base_ring()).Smooth():
                    return True
                case _:
                    return bool(_engine_scheme(self).is_smooth())

        def is_calabi_yau(self) -> bool:
            r"""Whether ``X`` is smooth and proper with ``omega_X ~= O_X``.

            The definition is the one :class:`Schemes.CalabiYau` states
            [Huy05, §6.1].  Placement answers first.  Otherwise the
            canonical bundle decides, through the realization of its
            category:

            - a projective complete intersection has ``omega_X = O_X(d)``
              through its adjunction isomorphism.  In positive dimension
              ``O_X(d)`` is trivial exactly when ``d = 0``: were
              ``O_X(d) ~= O_X`` with ``d != 0``, the ample ``O_X(1)`` would make
              ``O_X`` ample, so ``X`` would be quasi-affine and proper, hence
              finite;
            - a smooth toric scheme has ``Pic(X) = Cl(X)`` (Cox--Little--Schenck,
              Prop. 4.2.6), so ``omega_X = O_X(K_X)`` is trivial exactly when the
              class of ``K_X = -sum_rho D_rho`` in ``Cl(X)`` is zero; it is
              complete, that is proper, exactly when its fan is complete
              (CLS Thm. 3.4.1).
            """
            from sage_extensions.categories.schemes.complete_intersections import (
                ProjectiveCompleteIntersections,
            )
            from sage_extensions.categories.schemes.toric.toric_schemes import (
                ToricSchemes,
            )

            base = self.scheme_base_ring()
            match self:
                case _ if self in Schemes(base).CalabiYau():
                    return True
                case _ if self in ToricSchemes(base):
                    if not (self.is_smooth() and self.is_complete()):
                        return False
                    return bool(self.divisor_class(self.canonical_divisor()).is_zero())
                case _ if self in ProjectiveCompleteIntersections(base):
                    assert int(self.dimension()) >= 1, (
                        f"the canonical-bundle criterion for {self} needs positive dimension, so that "
                        "O_X(1) is ample on a positive-dimensional scheme"
                    )
                    if not self.is_smooth():
                        return False
                    return int(self.canonical_line_bundle().degree()) == 0
                case _:
                    assert False, (
                        f"whether {self} is Calabi--Yau is decided from its canonical bundle, which the "
                        "preamble decides to be trivial only for toric schemes and projective complete "
                        "intersections"
                    )

        def base_change(self, ring_map):
            r"""``X_{R'} = X x_{Spec R} Spec R'`` along a scalar morphism ``R -> R'``.

            The functor is applied to this object; the result is constructed
            as the fibre product of ``X -> Spec R <- Spec R'``, so its two
            projections and the universal factorization are available on it.
            """
            return self.scheme_category().base_change_functor(ring_map)(self)

        def as_slice_object(self):
            return self.scheme_category().as_slice_object(self)

        def fiber(self, base_morphism):
            r"""``X x_{Spec R} T``, the fibre of ``X -> Spec R`` over a morphism ``T -> Spec R``."""
            assert base_morphism.codomain() is self.base_scheme(), (
                f"cannot take the fibre of {self} over {base_morphism}: it must be a morphism into the "
                f"base scheme {self.base_scheme()}, but its codomain is {base_morphism.codomain()}"
            )
            return self.scheme_category().fiber_product(
                self.structure_morphism(), base_morphism
            )

        def fiber_over_ideal(self, ideal):
            r"""The fibre over the closed subscheme ``V(I) <= Spec R`` of an ideal ``I`` of ``R``."""
            return self.fiber(
                self.base_scheme()
                .closed_subscheme(tuple(ideal.ideal_generators()))
                .inclusion()
            )

        @cached_method
        def diagonal_morphism(self):
            r"""``Delta: X -> X x_S X``, the cone map with both legs the identity."""
            identity = self.categorical_identity_morphism()
            return _scheme_product(self, self).from_product_cone((identity, identity))

        def point_morphism(self, coordinates):
            r"""The ``R``-point ``Spec R -> X`` with the stated coordinates.

            On an affine scheme with chosen algebra generators the point is
            the algebra map sending each generator to its coordinate.  On a
            product of projective spaces the coordinates are the concatenated
            homogeneous blocks of the factors; on another realized scheme they
            are its native point coordinates.

            For a represented projective plane, the native realization's
            point homset supplies only the private computational point::

                sage: from dzack_research.preamble.all import QQ, ProjectiveSpaces
                sage: plane = ProjectiveSpaces(QQ)(2)
                sage: point = plane.point_morphism((QQ.one(), QQ.one(), QQ.one()))
                sage: point.domain() is plane.base_scheme() and point.codomain() is plane
                True
            """
            base = self.scheme_base_ring()
            owned_coordinates = tuple(base(coordinate) for coordinate in coordinates)
            selected = finite_family(
                owned_coordinates, name=f"Selected coordinates of point on {self}"
            )
            mor = Schemes(base).Mor(self.base_scheme(), self)
            match self:
                case _ if self in Schemes(base).Affine():
                    algebra = self.coordinate_algebra()
                    assert algebra.is_framed_algebra(), (
                        f"cannot form the {base}-point of {self} with coordinates {owned_coordinates}: the "
                        f"coordinate algebra {algebra} must have a chosen set of algebra generators, but it is an "
                        f"object of {algebra.category()}"
                    )
                    labels = tuple(algebra.algebra_generating_set())
                    assert len(labels) == len(owned_coordinates), (
                        f"cannot form the {base}-point of {self} with coordinates {owned_coordinates}: {algebra} "
                        f"has {len(labels)} chosen algebra generators, but {len(owned_coordinates)} coordinates "
                        "were given"
                    )
                    pullback = algebra.Mor(base)(
                        dict(zip(labels, owned_coordinates, strict=True))
                    )
                    return mor.element_class(
                        mor,
                        None,
                        mor=mor,
                        pullback=pullback,
                        point_coordinates=selected,
                    )
                case _ if self in ProductProjectiveSpaces(base):
                    engine_coordinates = tuple(
                        _engine_element(base, coordinate)
                        for coordinate in owned_coordinates
                    )
                    factor_points = []
                    offset = 0
                    for factor in self.factors():
                        width = int(factor.relative_dimension()) + 1
                        block = engine_coordinates[offset : offset + width]
                        assert len(block) == width, (
                            f"cannot form the {base}-point of {self} with coordinates {owned_coordinates}: the factor "
                            f"{factor} needs {width} homogeneous coordinates, but only {len(block)} remain"
                        )
                        factor_engine = _engine_scheme(factor)
                        factor_points.append(
                            factor_engine._point(
                                factor_engine.point_homset(), block, check=False
                            )
                        )
                        offset += width
                    assert offset == len(engine_coordinates), (
                        f"cannot form the {base}-point of {self} with coordinates {owned_coordinates}: the factors "
                        f"need {offset} homogeneous coordinates in total, but {len(engine_coordinates)} were given"
                    )
                    engine = _engine_scheme(self)
                    native = engine._point(
                        engine.point_homset(), factor_points, check=False
                    )
                    return mor.element_class(
                        mor, native, mor=mor, point_coordinates=selected
                    )
                case _:
                    engine = _engine_scheme(self)
                    native = engine._point(
                        engine.point_homset(),
                        [
                            _engine_element(base, coordinate)
                            for coordinate in owned_coordinates
                        ],
                        check=False,
                    )
                    return mor.element_class(
                        mor, native, mor=mor, point_coordinates=selected
                    )

        def projective_morphism_from_coordinates(self, target, coordinates):
            r"""Return the projective morphism defined by a basepoint-free coordinate family.

            ``coordinates`` are owned homogeneous sections on the projective
            presentation.  The caller has selected this exact source as a
            domain on which they have no common zero; retaining that open domain
            and the coordinate family is the complete defining datum of the
            morphism.  No larger rational-map domain is substituted.
            """
            base = self.scheme_base_ring()
            assert target in ProjectiveSpaces(base), (
                f"cannot build a morphism {self} -> {target} from homogeneous coordinates: {target} must "
                f"be a projective space over {base}, but it is an object of {target.category()}"
            )
            coordinates = tuple(coordinates)
            assert len(coordinates) == int(target.relative_dimension()) + 1, (
                f"cannot build a morphism {self} -> {target} from the homogeneous coordinates "
                f"{coordinates}: {target} needs {int(target.relative_dimension()) + 1} homogeneous "
                f"coordinates, but {len(coordinates)} were given"
            )
            return _ProjectiveCoordinateMorphism(
                _scheme_mor_category(self, target), coordinates
            )

        def categorical_identity_morphism(self):
            r"""``id_X``, the identity of this scheme's endomorphism Mor."""
            return _scheme_mor_category(self, self).identity()

        def product_with(self, other):
            r"""Return ``X x_S Y``, the product asked of the two objects.

            One argument is distinguished, so this is the operator spelling of
            the binary case.  A product over an index set that is part of the
            mathematics is named and taken over that set with
            ``Schemes(R).product(family)`` (`CON-14`).
            """
            schemes = self.scheme_category()
            assert other in schemes, (
                f"cannot form the product of {self} and {other} over {self.scheme_base_ring()}: {other} "
                f"is not an object of {schemes}"
            )
            factors = (self, other)
            return schemes.product(
                indexed_family(Sets.Δ[1], lambda index: factors[int(index)])
            )

        def point_counts(self, extension_degree):
            r"""Return ``(#X(F_q),...,#X(F_{q^n}))`` for a finite base field."""
            degree = int(extension_degree)
            assert degree >= 1, (
                f"cannot count the points of {self} over the extensions of degree 1 to {degree}: the "
                "extension degree must be at least 1"
            )
            base = self.scheme_base_ring()
            match base:
                case _ if base in OwnedFields() and base.cardinality().is_finite():
                    return finite_family(
                        tuple(
                            _owned_engine_element(SageZZ, SageZZ(value))
                            for value in _engine_scheme(self).count_points(degree)
                        ),
                        name="Point counts",
                    )
                case _:
                    assert False, (
                        f"point counts of {self} are defined after choosing finite residue/extension fields, but the "
                        f"current preamble computes them only when the base ring {base} is itself a finite field"
                    )

        def point_count(self, extension_degree=1):
            r"""Return ``#X(F_{q^n})`` for the stated extension degree ``n``."""
            degree = int(extension_degree)
            return self.point_counts(degree)[degree - 1]

    class Separated(CategoryWithAxiom):
        r"""Schemes whose diagonal is a closed immersion."""

        class ParentMethods:
            def is_separated(self):
                return True

            def point_blowup(self, point):
                r"""Return the blowup of ``self`` along the closed image of the ``R``-point ``point``.

                A section ``Spec R -> X`` of a separated ``R``-scheme is a
                closed immersion, so its image is a closed center and the
                blowup is defined (Stacks, Tags 024T and 0806).  The current
                represented computation is the projective-plane case; other
                separated schemes retain the operation at this owner and state
                the missing Rees-algebra computation explicitly.
                """
                base = self.scheme_base_ring()
                assert (
                    point.domain() is self.base_scheme() and point.codomain() is self
                ), (
                    f"cannot blow up {self} at {point}: the center must be an {base}-point "
                    f"Spec {base} -> {self}"
                )
                match self:
                    case _ if (
                        self in ProjectiveSpaces(base)
                        and base in OwnedFields()
                        and int(self.relative_dimension()) == 2
                    ):
                        from sage_extensions.categories.schemes.blowups import (
                            _projective_point_blowup,
                        )

                        return _projective_point_blowup(self, point)
                    case _:
                        raise AssertionError(
                            f"the blowup of the separated scheme {self} at the closed point {point} is defined "
                            "as the relative Proj of the Rees algebra of its point ideal, but this realization "
                            "does not supply that Rees-algebra construction"
                        )

        def an_object(self):
            r"""The affine line, separated because it is affine."""
            return AffineSpaces(self.base_ring())(1)

    class FiniteType(CategoryWithAxiom):
        r"""Schemes of finite type over the base."""

        def extra_super_categories(self):
            base = self.base_ring()
            match base in OwnedRings().Noetherian():
                case True:
                    return [Schemes(base).LocallyNoetherian()]
                case False:
                    return []

        class ParentMethods:
            def is_finite_type(self):
                return True

            @cached_method
            def hodge_structure(self):
                r"""The mixed Hodge structure on ``H^*(X(CC); ZZ)``.

                The complex realization uses the embedding of the base
                retained by the represented computation. For a smooth
                proper complex variety each ``H^k`` is pure of weight ``k``
                (Deligne, Theorie de Hodge II, (2.1.1), (2.3.1)).
                """
                return self._hodge_structure()

            def _hodge_structure(self):
                assert False, (
                    f"Hodge realization of {self}: not implemented; "
                    "an embedding into CC and its cohomological realization are required"
                )

            def complex_realization(self, scalar_embedding):
                r"""``X(CC)`` along ``sigma: k -> CC``, an object of :class:`TopologicalSpaces`.

                The points are the ``CC``-points of the base change
                ``X x_{k, sigma} CC``, and the topology is the analytic one:
                on each affine chart ``X_i <= A^r``, the topology induced by
                the Euclidean topology of ``CC^r``.  Finite type is the
                hypothesis that makes each chart a closed subset of some
                ``CC^r``.  The space depends on ``sigma``, so the embedding is
                part of the input.  Dimca [Dim92], Ch. 1, (6.10): ``X(CC)``
                has the homotopy type of a finite CW complex.
                """
                from sage_extensions.categories.schemes.geometric_cohomology import (
                    _complex_realization,
                )

                assert scalar_embedding.domain() is self.scheme_base_ring(), (
                    f"the complex points of {self} are taken along an embedding of its base "
                    f"{self.scheme_base_ring()} into CC, but {scalar_embedding} has domain "
                    f"{scalar_embedding.domain()}"
                )
                assert scalar_embedding.codomain() is _owned_complex_field(), (
                    f"the complex points of {self} are taken along an embedding into CC, but "
                    f"{scalar_embedding} has codomain {scalar_embedding.codomain()}"
                )
                return _complex_realization(self, scalar_embedding)

            def betti_number(self, degree):
                r"""``b_k(X) = dim_{Q_l} H^k_et(X_{kbar}, Q_l)`` for a prime ``l != char k``.

                Freitag--Kiehl, *Etale Cohomology and the Weil Conjecture*
                [FK88], Ch. I, §12: ``H^k(X, Q_l) = H^k(X, Z_l) (x) Q_l`` with
                ``H^k(X, Z_l) = lim_n H^k(X, Z/l^n)``.  When ``char k = 0`` and
                ``sigma: k -> CC`` is an embedding, Artin's comparison theorem
                ([FK88], Ch. I, Thm. 11.6, for ``X x_{k, sigma} CC -> Spec CC``)
                identifies ``H^k_et(X_{kbar}, Z/l^n)`` with
                ``H^k(X(CC), Z/l^n)``.  Passing to the limit and tensoring
                with ``Q_l`` gives ``b_k(X) = b_k(X(CC))``, the Betti number
                of :meth:`complex_realization`.
                """
                return self.complex_realization(
                    _etale_comparison_embedding(self, f"b_{degree}")
                ).betti_number(degree)

            def euler_characteristic(self):
                r"""``chi(X) = sum_k (-1)^k b_k(X)``, with ``b_k`` the etale Betti numbers.

                By :meth:`betti_number`, each ``b_k(X)`` equals
                ``b_k(X(CC))`` along ``sigma: k -> CC``, so the alternating
                sum is the Euler characteristic of the complex realization,
                which :class:`TopologicalSpaces` computes as the contraction
                of the Betti vector with ``((-1)^k)``.
                """
                return self.complex_realization(
                    _etale_comparison_embedding(self, "chi")
                ).euler_characteristic()

            @cached_method
            def zeta_function(self):
                r"""Return the Hasse--Weil zeta function over a finite base field.

                For a finite-type scheme ``X/F_q`` this is

                ``Z(X,T) = exp(sum_{n >= 1} #X(F_{q^n}) T^n / n)``.

                The operation belongs to finite-type schemes; represented
                families supply computational cases through ``_zeta_function``.
                """
                base = self.scheme_base_ring()
                assert base in OwnedFields() and base.cardinality().is_finite(), (
                    f"the Hasse--Weil zeta function of {self} is represented here only over a finite field, "
                    f"but its base ring is {base}"
                )
                return self._zeta_function()

            def _zeta_function(self):
                raise AssertionError(
                    f"the Hasse--Weil zeta function of the finite-type scheme {self} is defined by its point "
                    "counts over finite extensions, but this realization has no selected zeta-function algorithm"
                )

        def an_object(self):
            r"""The affine line, of finite type over the base ring."""
            return AffineSpaces(self.base_ring())(1)

    class LocallyNoetherian(CategoryWithAxiom):
        r"""Schemes locally covered by spectra of Noetherian rings (Stacks, Tag 01OV)."""

        class ParentMethods:
            def is_locally_noetherian(self):
                return True

            def cycle_group(self, cycle_dimension):
                r"""Return ``Z_k(X)``, the group of locally finite ``k``-cycles on ``X``.

                The mathematical group is generated by the integral closed
                subschemes of dimension ``k``, with locally finite support.  A
                represented affine Noetherian scheme supplies the current
                sparse computation; other locally Noetherian schemes retain
                the operation and state that computational frontier.
                """
                return self._cycle_group(cycle_dimension)

            def _cycle_group(self, cycle_dimension):
                raise AssertionError(
                    f"the algebraic cycle group Z_{cycle_dimension}({self}) is defined by locally finite "
                    "formal sums of integral closed subschemes of the stated dimension, but this realization "
                    "does not supply a represented family of those prime cycles"
                )

        def an_object(self):
            r"""The affine line when the selected base is Noetherian."""
            base = self.base_ring()
            assert base in OwnedRings().Noetherian(), (
                f"the canonical locally Noetherian scheme over {base} used here is A^1_{base}, "
                f"but {base} is not known to be Noetherian"
            )
            return AffineSpaces(base)(1)

        class Integral(CategoryWithAxiom):
            r"""Locally Noetherian integral schemes, where Weil divisor classes are defined."""

            class ParentMethods:
                def weil_cycle_isomorphism(self):
                    r"""Identify Weil divisors with codimension-one cycles on ``X``."""
                    return self._weil_cycle_isomorphism()

                def _weil_cycle_isomorphism(self):
                    raise AssertionError(
                        f"the Weil divisors of {self} and its codimension-one cycles have the same prime "
                        "generators, but this realization does not supply compatible represented groups from "
                        "which to construct that canonical isomorphism"
                    )

                def full_weil_divisor_group(self):
                    r"""Return ``Div(X)``, the Weil divisor group (Stacks, Tag 0BE2)."""
                    return self._full_weil_divisor_group()

                def _full_weil_divisor_group(self):
                    raise AssertionError(
                        f"the Weil divisor group of the locally Noetherian integral scheme {self} is defined "
                        "on its codimension-one prime divisors, but this realization does not supply a "
                        "represented prime-divisor family and order-of-vanishing algorithm"
                    )

                @cached_method
                def class_group(self):
                    r"""Return ``Cl(X) = Div(X) / Prin(X)`` (Stacks, Tag 0BE4)."""
                    return self._class_group()

                def _class_group(self):
                    raise AssertionError(
                        f"the Weil divisor class group Cl({self}) is defined as Div({self}) modulo principal "
                        "Weil divisors, but this realization does not supply a represented quotient presentation"
                    )

                @cached_method
                def picard_to_class_group_morphism(
                    self,
                    base_picard_group=None,
                    base_class_group=None,
                    base_picard_to_class=None,
                ):
                    r"""Return the canonical comparison ``Pic(X) -> Cl(X)``.

                    On a locally Noetherian integral scheme an invertible sheaf
                    determines a Weil divisor class, hence this map belongs here.
                    Represented descendants supply the computation from their
                    Cartier/Weil or divisor-presentation data.
                    """
                    return self._picard_to_class_group_morphism(
                        base_picard_group=base_picard_group,
                        base_class_group=base_class_group,
                        base_picard_to_class=base_picard_to_class,
                    )

                def _picard_to_class_group_morphism(
                    self,
                    base_picard_group=None,
                    base_class_group=None,
                    base_picard_to_class=None,
                ):
                    raise AssertionError(
                        f"the canonical map Pic({self}) -> Cl({self}) is defined by sending an invertible "
                        "sheaf to its Weil divisor class, but this realization does not supply a represented "
                        "Cartier-to-Weil divisor comparison algorithm"
                    )

            def an_object(self):
                r"""The affine line when the base is a Noetherian domain."""
                base = self.base_ring()
                assert (
                    base in OwnedRings().Noetherian() and base in OwnedIntegralDomains()
                ), (
                    f"the canonical locally Noetherian integral scheme over {base} used here is A^1_{base}, "
                    "which requires the base to be a Noetherian integral domain"
                )
                return AffineSpaces(base)(1)

    class Proper(CategoryWithAxiom):
        r"""Schemes proper over the base.

        ``X -> Spec R`` is proper when it is separated, of finite type and
        universally closed (Stacks, Tag 01W0, Definition 29.42.1).  The two
        immediate supercategories are the first two conditions; universal
        closedness is the datum this axiom adds.
        """

        def extra_super_categories(self):
            return [
                Schemes(self.base_ring()).Separated(),
                Schemes(self.base_ring()).FiniteType(),
            ]

        class ParentMethods:
            def is_proper(self):
                return True

        def an_object(self):
            r"""The projective line, proper because it is projective (Stacks, Tag 01WC)."""
            return ProjectiveSpaces(self.base_ring())(1)

        class Smooth(CategoryWithAxiom):
            r"""Smooth proper schemes over the base.

            Over a field ``k`` these are the schemes whose Hodge numbers
            ``h^{p,q} = dim_k H^q(X, Omega^p_{X/k})`` are defined: the
            cohomology of a coherent sheaf on a proper scheme over a field is
            finite-dimensional, and smoothness makes ``Omega^p_{X/k}``
            locally free.
            """

            def an_object(self):
                r"""The projective line, smooth and proper over the base."""
                return ProjectiveSpaces(self.base_ring())(1)

            class ParentMethods:
                def hodge_number(self, p, q):
                    r"""``h^{p,q}(X) = dim_k H^q(X, Omega^p_{X/k})``.

                    Huybrechts, *Complex Geometry* [Huy05], Def. 2.2.23,
                    states it for a compact complex manifold.  The routed
                    categories are those whose pure Hodge structure the
                    preamble constructs; each realization cites the theorem
                    it computes the dimension by.
                    """
                    from sage_extensions.categories.schemes.complete_intersections import (
                        ProjectiveCompleteIntersections,
                    )
                    from sage_extensions.categories.schemes.toric.toric_schemes import (
                        ToricSchemes,
                    )

                    base = self.scheme_base_ring()
                    assert base in OwnedFields(), (
                        f"the Hodge number h^({p},{q}) = dim H^{q}(X, Omega^{p}) is a dimension over "
                        f"the base field, but {self} is over {base}, which is not a field"
                    )
                    match self:
                        case _ if self in ToricSchemes(base):
                            return self.hodge_structure().hodge_number(p, q)
                        case _ if self in ProjectiveCompleteIntersections(base):
                            return self.hodge_structure().hodge_number(p, q)
                        case _:
                            assert False, (
                                f"h^({p},{q})({self}) is computed only for smooth complete toric "
                                "varieties over QQ and smooth quartic K3 surfaces over QQ"
                            )

    class Integral(CategoryWithAxiom):
        r"""Schemes that are reduced and irreducible."""

        class ParentMethods:
            def is_integral(self):
                return True

            @cached_method
            def function_field(self):
                r"""The function field ``K(X) = O_{X,eta}``, the local ring at the generic point.

                Domain: an integral scheme ``X`` over ``R``.  Codomain: a field,
                an ``R``-algebra through ``R -> O_{X,eta}`` (Hartshorne,
                *Algebraic Geometry*, II, Ex. 3.6).  For every nonempty affine
                open ``U = Spec A`` of ``X``, ``K(X) = Frac(A)`` (Mathlib
                ``AlgebraicGeometry.functionField_isFractionRing_of_isAffineOpen``).
                The open is read from the scheme's own construction: an affine
                scheme is its own open; a scheme with a selected finite affine
                atlas, such as ``P^n_k`` with its standard charts, uses a chart of
                that atlas; a projective closed subscheme ``Z = V_+(f_1, ..., f_k)``
                of such a scheme ``Y`` meets the chart ``U_i -> Y`` in
                ``V(f_1|U_i, ..., f_k|U_i) <= U_i``, the pullbacks of the
                equations along the chart's homogeneous coordinates (Stacks,
                Tag 01M3).  So ``K(P^n_k) = k(x_1/x_0, ..., x_n/x_0)``, and the
                plane cubic ``V_+(x_0^3 + x_1^3 + x_2^3)`` has the function field
                ``Frac(k[a, b]/(1 + a^3 + b^3))`` of its chart ``x_0 != 0``.
                """
                base = self.scheme_base_ring()
                match self:
                    case _ if self in Schemes(base).Affine():
                        return self.coordinate_algebra().fraction_field()
                    case _ if self.has_selected_finite_affine_atlas():
                        return _function_field_on_atlas(
                            self.selected_finite_affine_atlas(), ()
                        )
                    case _ if (
                        self in ClosedSubschemes(base)
                        and self in Schemes(base).Projective()
                        and self.inclusion()
                        .codomain()
                        .has_selected_finite_affine_atlas()
                    ):
                        return _function_field_on_atlas(
                            self.inclusion().codomain().selected_finite_affine_atlas(),
                            tuple(self.defining_equations()),
                        )
                    case _:
                        assert False, (
                            f"function_field on the integral schemes over {base} with neither an affine "
                            f"presentation nor a selected affine atlas, such as {self}: not implemented"
                        )

        def an_object(self):
            r"""The affine line, integral because ``R[x]`` is a domain when ``R`` is."""
            base = self.base_ring()
            assert _integral_placement(base), (
                f"the affine line over {base} is integral exactly when {base} is a domain"
            )
            return AffineSpaces(base)(1)

    class Normal(CategoryWithAxiom):
        r"""Schemes whose local rings are integrally closed domains."""

        class ParentMethods:
            def is_normal(self):
                return True

        def an_object(self):
            r"""The affine line, normal because ``R[x]`` is integrally closed when ``R`` is."""
            base = self.base_ring()
            assert _normal_placement(base), (
                f"the affine line over {base} is normal exactly when {base} is, and the "
                "criterion available here is that the base is a principal ideal domain"
            )
            return AffineSpaces(base)(1)

    class Smooth(CategoryWithAxiom):
        r"""Schemes smooth over the base."""

        class ParentMethods:
            def is_smooth(self):
                return True

            @cached_method
            def canonical_line_bundle(self):
                r"""Return the relative canonical line bundle ``omega_{X/R}`` in a represented smooth case.

                For a smooth morphism of constant relative dimension ``d`` the
                mathematical owner is this category: ``omega_{X/R} =
                det(Omega^1_{X/R})``.  Descendant categories supply private
                computational specializations; other smooth schemes retain the
                operation at its owner and state the missing determinant
                algorithm rather than losing the operation by lower placement.
                """
                return self._canonical_line_bundle()

            def _canonical_line_bundle(self):
                raise AssertionError(
                    f"the canonical line bundle of the smooth scheme {self} is "
                    "det(Omega^1), but a represented determinant of its relative "
                    "cotangent sheaf is not computed here"
                )

            def canonical_bundle(self, *args, **kwargs):
                return self.canonical_line_bundle(*args, **kwargs)

            @cached_method
            def anticanonical_line_bundle(self):
                r"""Return ``omega_{X/R}^{-1}`` in every represented canonical-bundle case."""
                return self.canonical_line_bundle().dual_sheaf()

            def anticanonical_bundle(self, *args, **kwargs):
                return self.anticanonical_line_bundle(*args, **kwargs)

            def de_rham_complex(self):
                r"""``Ω^•_{X/R}``, the algebraic de Rham complex of this smooth scheme.

                An object of ``Sheaves(zariski_coverage(X),
                DifferentialGradedAlgebras(R).Supercommutative().Alternating())``:
                a sheaf of supercommutative differential graded ``R``-algebras
                whose sections over an affine open ``Spec A`` are
                ``DeRhamAlgebras(R)(A) = DR_R(A)``.  Its differential is
                ``R``-linear but not ``O_X``-linear.  For affine ``X`` it is
                constructed on the distinguished affine basis
                ``distinguished_affine_coverage(X)``, which determines the
                sheaf on ``X`` (Stacks, Tag 009O).
                """
                from sage_extensions.categories.schemes.ringed_spaces import (
                    _affine_de_rham_complex,
                )

                base = self.scheme_base_ring()
                match self:
                    case _ if self in Schemes(base).Affine():
                        return _affine_de_rham_complex(self)
                    case _:
                        assert False, (
                            "de_rham_complex on Schemes.Smooth: not implemented"
                        )

            def de_rham_hypercohomology(self):
                r"""``RΓ(X, Ω^•_{X/R})``, an object of ``DerivedCategory(R)``.

                The hypercohomology of the de Rham complex: the class of the
                total complex of ``Γ(X, I^{•,•})`` for a Cartan--Eilenberg
                injective resolution of ``Ω^•_{X/R}`` by sheaves of
                ``R``-modules.  Computed for projective spaces ``P^n_R`` from
                Stacks Project, Tag 0FMJ.
                """
                from sage_extensions.categories.schemes.geometric_cohomology import (
                    _projective_space_de_rham_hypercohomology,
                )

                base = self.scheme_base_ring()
                match self:
                    case _ if self in ProjectiveSpaces(base):
                        return _projective_space_de_rham_hypercohomology(self)
                    case _:
                        assert False, (
                            "de_rham_hypercohomology on Schemes.Smooth: not implemented"
                        )

            def de_rham_cohomology(self, degree):
                r"""``H^degree_dR(X/R) = H^degree(RΓ(X, Ω^•_{X/R}))``, an object of ``Modules(R)``."""
                return self.de_rham_hypercohomology().cohomology(degree)

            def de_rham_cohomology_algebra(self):
                r"""``H^*_dR(X/R)``, an object of ``GradedAlgebras(R).Supercommutative()``.

                The graded module ``⊕_k H^k_dR(X/R)`` with the cup product
                induced by the wedge product of ``Ω^•_{X/R}``; it needs a
                multiplicative model of ``RΓ(X, Ω^•_{X/R})``, which the
                derived category alone does not supply.
                """
                assert False, (
                    "de_rham_cohomology_algebra on Schemes.Smooth: not implemented"
                )

        def an_object(self):
            r"""The affine line, which is smooth over the base ring."""
            return AffineSpaces(self.base_ring())(1)

        def de_rham_cohomology(self, degree):
            r"""Return ``H^degree_dR(-/R) : Sm_R^op -> Mod_R``."""
            from sage_extensions.categories.functors.de_rham import (
                _smooth_scheme_de_rham_cohomology_functor,
            )

            return _smooth_scheme_de_rham_cohomology_functor(self.base_ring(), degree)

        def de_rham_cohomology_algebra(self):
            r"""Return ``H^*_dR(-/R) : Sm_R^op -> GradedAlgebras(R).Supercommutative()``."""
            from sage_extensions.categories.functors.de_rham import (
                _smooth_scheme_de_rham_cohomology_algebra_functor,
            )

            return _smooth_scheme_de_rham_cohomology_algebra_functor(self.base_ring())

    class CalabiYau(CategoryWithAxiom):
        r"""Calabi--Yau schemes: smooth and proper, with trivial canonical bundle.

        Huybrechts, *Complex Geometry* [Huy05], §6.1 (before Prop. 6.1.11):
        a Calabi--Yau manifold is a compact Kahler manifold ``X`` of
        dimension ``n`` whose canonical bundle ``K_X = Lambda^n Omega_X`` is
        trivial.  Over a base field the algebraic statement is a smooth
        proper scheme ``X`` with ``omega_{X/k} ~= O_X``.  Smoothness and
        properness are the immediate supercategories; triviality of the
        canonical bundle is the property this axiom adds.  Membership is
        decided from the canonical bundle by :meth:`Schemes.ParentMethods.is_calabi_yau`.
        """

        def extra_super_categories(self):
            return [
                Schemes(self.base_ring()).Smooth(),
                Schemes(self.base_ring()).Proper(),
            ]

        class ParentMethods:
            def is_calabi_yau(self):
                return True

    class Affine(CategoryWithAxiom):
        r"""Schemes isomorphic to ``Spec A``.

        The level datum is the coordinate algebra ``A``; ``Spec`` is an
        equivalence ``CAlg_R^op -> AffSch_R`` (Stacks, Tag 01I1), so ``A``
        determines the scheme and is no choice.
        """

        def an_object(self):
            r"""The affine line over the base ring."""
            return AffineSpaces(self.base_ring())(1)

        def _call_(self, algebra):
            r"""``Spec A`` over this category's base, one object for each algebra."""
            return _affine_spectrum_over(_own_ring(algebra), self.base_ring())

        def extra_super_categories(self):
            # Quasi-affine as well: a scheme is an open subscheme of itself.
            return [Schemes(self.base_ring()).QuasiAffine()]

        class ParentMethods:
            @cached_method
            def diagonal_subscheme(self):
                r"""Closed diagonal of an affine scheme via its coordinate algebra."""
                product = _scheme_product(self, self)
                left = product.projection(0).coordinate_algebra_morphism()
                right = product.projection(1).coordinate_algebra_morphism()
                algebra = self.coordinate_algebra()
                equations = tuple(
                    left(algebra.algebra_generator(label))
                    - right(algebra.algebra_generator(label))
                    for label in algebra.algebra_generating_set()
                )
                return product.closed_subscheme(equations)

            _derived_construction_parameters = frozenset({"topology_data"})

            def __init__(self, coordinate_algebra, **rest) -> None:
                from sage_extensions.categories.schemes.ringed_spaces import (
                    _AffineSchemeTopologyData,
                )

                self._coordinate_algebra = coordinate_algebra
                super().__init__(
                    topology_data=_AffineSchemeTopologyData(coordinate_algebra), **rest
                )

            def coordinate_algebra(self):
                r"""``A = Gamma(X, O_X)``, the coordinate algebra of ``X = Spec A``."""
                return self._coordinate_algebra

            def coordinate_ring(self):
                r"""The coordinate algebra, under the name the ring layer uses."""
                return self.coordinate_algebra()

            @cached_method
            def underlying_space(self):
                r"""The prime spectrum ``Spec A`` underlying the affine scheme ``Spec A``."""
                return self.coordinate_algebra().spectrum()

            def _repr_(self) -> str:
                r"""``Spec A``; a closed subscheme ``V(f_1, ..., f_k)`` is named by its codomain and equations."""
                match self:
                    case _ if self in ClosedSubschemes(self.scheme_base_ring()):
                        return (
                            f"Closed subscheme of {self.inclusion().codomain()} defined by "
                            f"{', '.join(str(equation) for equation in self.defining_equations())}"
                        )
                    case _:
                        return f"Spectrum of {self.coordinate_algebra()}"

            def __contains__(self, point) -> bool:
                r"""Whether ``point`` is a point of ``Spec A``, a prime ideal of ``A``."""
                return point in self.underlying_space()

            def _element_constructor_(self, datum):
                r"""The point of ``Spec A`` that ``datum`` names, a prime ideal of ``A``."""
                return self.underlying_space()(datum)

            def _prime_point(self, point):
                r"""``point`` as an element of ``Spec A``: a prime point, or the prime it is given by."""
                spectrum = self.underlying_space()
                match point.parent():
                    case _ if point.parent() is spectrum:
                        return point
                    case _:
                        return spectrum(point)

            def is_regular_at(self, point) -> bool:
                r"""Return whether ``O_{X,p}`` is a regular local ring."""
                return bool(self._prime_point(point).is_regular())

            def is_singular_at(self, point) -> bool:
                r"""Return the negation of local regularity at ``p``."""
                return not self.is_regular_at(point)

            def is_locally_factorial_at(self, point):
                r"""Return local factoriality at ``p`` in the supported regular regime."""
                return self._prime_point(point).is_locally_factorial()

            def _cycle_group(self, cycle_dimension):
                r"""Compute ``Z_k(self)`` from the represented Noetherian affine spectrum."""
                from sage_extensions.categories.divisors.chow_groups import (
                    _affine_cycle_group,
                )

                return _affine_cycle_group(self, cycle_dimension)

            def _full_weil_divisor_group(self):
                r"""Return the full height-one Weil divisor group in the represented affine-normal case."""
                base = self.scheme_base_ring()
                match self in Schemes(base).Normal():
                    case True:
                        from sage_extensions.categories.divisors.general_divisors import (
                            _affine_normal_weil_divisor_group,
                        )

                        return _affine_normal_weil_divisor_group(self)
                    case False:
                        raise AssertionError(
                            f"the Weil divisor group Div({self}) is defined because {self} is locally "
                            "Noetherian and integral, but the represented affine computation available "
                            "here requires normality in order to compute height-one valuations"
                        )

            def _weil_cycle_isomorphism(self):
                r"""Compute the Weil/cycle identification from the common affine prime spectrum."""
                from sage_extensions.categories.divisors.chow_groups import (
                    _affine_weil_cycle_isomorphism,
                )

                return _affine_weil_cycle_isomorphism(self)

            def closed_subscheme(
                self, *equations, placements=(), _quotient_data=None, **level_data
            ):
                r"""``V(f_1, ..., f_k) = Spec A/(f_1, ..., f_k)``, with its closed immersion.

                The equations are given one by one or as a single finite family.
                The inclusion is ``Spec`` of the quotient map ``A -> A/I``.  A
                construction whose closed subscheme is also an object of further
                categories states them in ``placements``, with their level data.
                """
                equations = _equation_family(equations)
                algebra = self.coordinate_algebra()
                base = self.scheme_base_ring()
                match _quotient_data:
                    case None:
                        quotient, quotient_map = algebra._quotient_by_algebra_elements(
                            tuple(equations)
                        )
                    case (quotient, quotient_map):
                        assert (
                            quotient_map.domain() is algebra
                            and quotient_map.codomain() is quotient
                        ), (
                            f"cannot form the closed subscheme of {self} cut out by {equations}: the quotient map "
                            f"{quotient_map} must be {algebra} -> {quotient}, but it is "
                            f"{quotient_map.domain()} -> {quotient_map.codomain()}"
                        )
                return _affine_scheme(
                    quotient,
                    base,
                    (ClosedEmbeddings(self), ClosedSubschemes(base), *placements),
                    inclusion_codomain=self,
                    inclusion_datum=quotient_map,
                    defining_equations=equations,
                    **level_data,
                )

            @cached_method
            def relative_differentials(self):
                r"""Return the affine module of relative Kähler differentials."""
                return self.coordinate_algebra().kahler_differentials()

            def is_flat(self) -> bool:
                r"""Return whether this represented affine scheme is flat over its base."""
                return bool(self.coordinate_algebra().is_flat())

            def differential_rank_drop_subscheme(self, rank):
                r"""Return the closed Fitting stratum ``V(Fitt_rank(Omega^1_{X/S}))``."""
                ideal = self.relative_differentials().fitting_ideal(int(rank))
                return self.closed_subscheme(tuple(ideal.ideal_generators()))

            def singular_subscheme(self):
                r"""Return the nonsmooth closed subscheme in the supported equidimensional field case.

                This uses ``Fitt_d(Omega^1_{X/k})`` when the affine morphism is
                flat and finitely presented with equidimensional fibres of
                dimension ``d``.  The base is a field, so flatness is automatic;
                the chosen finite algebra presentation and the minimal
                components of its defining ideal verify the remaining
                hypotheses.
                """
                base = self.scheme_base_ring()
                assert base in OwnedFields(), (
                    f"cannot form the singular locus of {self}: this computation requires a field as base "
                    f"ring, but the base ring is {base}"
                )
                algebra = self.coordinate_algebra()
                assert algebra in AlgebrasWithChosenFinitePresentation(base), (
                    f"cannot form the singular locus of {self}: its coordinate algebra {algebra} must be given "
                    f"by finitely many generators and relations, but it is an object of {algebra.category()}"
                )
                dimension = int(algebra.krull_dimension())
                minimal_components = (
                    _engine_ring(algebra).defining_ideal().minimal_associated_primes()
                )
                assert all(
                    int(component.dimension()) == dimension
                    for component in minimal_components
                ), (
                    f"cannot form the singular locus of {self}: the Fitting ideal criterion requires {self} to "
                    f"be equidimensional, but not all its irreducible components have dimension {dimension}"
                )
                return self.differential_rank_drop_subscheme(dimension)

            def relative_nonsmooth_subscheme(self):
                r"""Return the relative nonsmooth locus in the supported flat hypersurface regime.

                For a flat morphism locally of finite presentation, smoothness at
                a point is smoothness of the fibre there (Stacks, Tags 01V8 and
                01V9).  For a primitive hypersurface over a univariate polynomial
                ring over a perfect field, every fibre is a hypersurface of the
                same dimension and the Jacobian criterion is detected by the
                corresponding Fitting ideal of relative differentials.
                """
                assert self.is_flat(), (
                    f"cannot form the relative non-smooth locus of {self} over {self.scheme_base_ring()}: the "
                    f"Fitting ideal criterion requires {self} to be flat over its base, and flatness is not "
                    "established"
                )
                base = self.scheme_base_ring()
                algebra = self.coordinate_algebra()
                assert algebra in AlgebrasWithChosenFinitePresentation(base), (
                    f"cannot form the relative non-smooth locus of {self}: its coordinate algebra {algebra} "
                    f"must be given by finitely many generators and relations, but it is an object of "
                    f"{algebra.category()}"
                )
                coefficient_field = base.base_ring()
                assert (
                    coefficient_field in OwnedFields()
                    and base in SymmetricAlgebras(coefficient_field)
                    and base.algebra_generating_set().cardinality() == 1
                    and bool(_engine_ring(coefficient_field).is_perfect())
                ), (
                    f"cannot form the relative non-smooth locus of {self}: the criterion is available only "
                    f"over a base k[t] with k a perfect field, but the base ring is {base}"
                )
                relative_dimension = (
                    algebra._represented_primitive_hypersurface_relative_dimension()
                )
                return self.differential_rank_drop_subscheme(relative_dimension)

            @cached_method
            def distinguished_open(self, element):
                r"""Return \(D(f)\subseteq X\), the open locus where ``element`` is a unit.

                \(D(f)=\operatorname{Spec}A[1/f]\), and the localization map
                \(A\to A[1/f]\) is the pullback of the open immersion.  For a
                scheme over \(R\), \(A[1/f]\) is an \(R\)-algebra through
                \(R\to A\to A[1/f]\), so the localization map is a morphism
                of \(R\)-algebras, as every morphism of
                affine \(R\)-schemes is on coordinate algebras.
                """
                algebra = self.coordinate_algebra()
                element = algebra(element)
                localized = algebra.localization(element)
                base = self.scheme_base_ring()
                return _affine_scheme(
                    localized,
                    base,
                    (OpenImmersions(self),),
                    inclusion_codomain=self,
                    # The canonical R-algebra map is a |-> a/1. The
                    # localization's scalar action is R -> A -> S^-1 A,
                    # so this formula preserves scalars, product and unit.
                    inclusion_datum=Algebras(base)
                    .Associative()
                    .Unital()
                    .Commutative()
                    .Mor(algebra, localized)
                    ._from_constructed_element_map(
                        lambda element: localized.fraction(element)
                    ),
                )

            def basic_open(self, element):
                r"""Archived spelling for the distinguished open ``D(element)``."""
                return self.distinguished_open(element)

            def distinguished_open_cover(self, *elements):
                r"""Return the finite cover by ``D(f_i)`` when the ``f_i`` generate the unit ideal."""
                from sage_extensions.categories.schemes.ringed_spaces import (
                    DistinguishedAffineCovers,
                )

                return DistinguishedAffineCovers(self)(
                    tuple(_equation_family(elements))
                )

            def associated_module_sheaf(self, module):
                r"""Return the quasi-coherent sheaf ``M~`` of an ``A``-module ``M``."""

                return self.structure_sheaf().associated_module_sheaf(module)

            def relative_spectrum(self, algebra_structure):
                r"""``Spec_X(B~) -> X`` for the ``O_X``-algebra given by ``A -> B`` (Stacks, Tag 01LQ).

                On affine ``X = Spec A`` a quasi-coherent ``O_X``-algebra is an
                ``A``-algebra, stated as the ``R``-algebra morphism ``A -> B``;
                its relative spectrum is ``Spec B`` with the structure morphism
                ``Spec`` of that map, an object of ``Sch/X``.
                """
                assert algebra_structure.domain() is self.coordinate_algebra(), (
                    f"cannot form the relative spectrum over {self} of {algebra_structure}: it must be an "
                    f"algebra map out of the coordinate algebra {self.coordinate_algebra()}, but it starts at "
                    f"{algebra_structure.domain()}"
                )
                structure_morphism = _affine_morphism_from_pullback(
                    algebra_structure.codomain().affine_spectrum(),
                    self,
                    algebra_structure,
                )
                return self.scheme_category().SliceOver(self)(structure_morphism)

    class QuasiAffine(CategoryWithAxiom):
        r"""Schemes that are open subschemes of an affine scheme."""

        def an_object(self):
            r"""The affine line, which is affine."""
            return AffineSpaces(self.base_ring())(1)

        def extra_super_categories(self):
            return [Schemes(self.base_ring()).Separated()]

        class ParentMethods:
            def is_quasi_affine(self):
                return True

        class FiniteType(CategoryWithAxiom):
            r"""Quasi-affine schemes of finite type over the base.

            A quasi-affine morphism of finite type is quasi-projective (Stacks,
            Tag 0B3H, Lemma 29.41.7), so this join declares quasi-projectivity.
            Neither hypothesis alone gives it.
            """

            def an_object(self):
                r"""The affine line, which is affine and of finite type."""
                return AffineSpaces(self.base_ring())(1)

            def extra_super_categories(self):
                return [Schemes(self.base_ring()).QuasiProjective()]

    class QuasiProjective(CategoryWithAxiom):
        r"""Schemes quasi-projective over the base."""

        def an_object(self):
            r"""The projective line, which is projective."""
            return ProjectiveSpaces(self.base_ring())(1)

        def extra_super_categories(self):
            return [Schemes(self.base_ring()).Separated()]

        class ParentMethods:
            def is_quasi_projective(self):
                return True

    class Projective(CategoryWithAxiom):
        r"""Schemes projective over the base."""

        def an_object(self):
            r"""The projective line."""
            return ProjectiveSpaces(self.base_ring())(1)

        def extra_super_categories(self):
            r"""Projective schemes are quasi-projective and proper.

            A projective morphism is locally projective, with the one-member
            cover of the base (Stacks, Tag 01W8, Definition 29.44.1), and a
            locally projective morphism is proper (Stacks, Tag 01WC,
            Lemma 29.44.5); finite type is reached through properness.
            """
            return [
                Schemes(self.base_ring()).QuasiProjective(),
                Schemes(self.base_ring()).Proper(),
            ]

        class ParentMethods:
            def is_projective(self):
                return True

            def closed_subscheme(
                self,
                *equations,
                placements=(),
                _object_engine=None,
                construction_data=None,
                **level_data,
            ):
                r"""``V_+(f_1, ..., f_k)``, cut out by homogeneous equations.

                The equations are owned homogeneous polynomials, or elements of
                the realization's coordinate ring, which are raised into the
                owned ring of that engine before they are retained.  The Sage
                subscheme they cut out is the realization, and its embedding is
                the inclusion.  A construction whose closed subscheme is also an
                object of further categories -- a complete intersection, a blowup
                -- states them in ``placements``, with their level data.
                """
                return _projective_closed_subscheme(
                    self,
                    equations,
                    placements=placements,
                    _object_engine=_object_engine,
                    construction_data=construction_data,
                    **level_data,
                )


def _projective_closed_subscheme(
    ambient,
    equations,
    placements=(),
    *,
    _engine=None,
    _object_engine=None,
    construction_data=None,
    **level_data,
):
    r"""The one projective closed-subscheme construction, with its inclusion.

    The private engine argument is used by a construction that must decide
    a property of the defining ideal before placing its resulting scheme,
    such as the complete-intersection criterion.  No owned provisional
    scheme is allocated to make that decision.
    """
    equations = _projective_equation_family(_equation_family(equations))
    base = ambient.scheme_base_ring()
    engine = (
        _engine_projective_subscheme(_engine_scheme(ambient), equations)
        if _engine is None
        else _engine
    )
    category = owned_category_join(
        (
            Schemes(base).Projective(),
            ClosedEmbeddings(ambient),
            ClosedSubschemes(base),
            *placements,
        )
    )
    data = dict(construction_data or {})
    match _object_engine:
        case None:
            object_realization = None
        case _:
            object_realization = (Schemes(base), _object_engine, None)
    return _object_of(
        category,
        _engine=object_realization,
        scheme_base_ring=base,
        scheme_engine=engine,
        inclusion_codomain=ambient,
        inclusion_datum=_native_embedding_rule,
        defining_equations=equations,
        **data,
        **level_data,
    )


def AffineSchemes(base_ring):
    r"""``Schemes(R).Affine()``, under the name the session catalogue uses."""
    return Schemes(base_ring).Affine()


def ProjectiveSchemes(base_ring):
    r"""``Schemes(R).Projective()``, under the name the session catalogue uses."""
    return Schemes(base_ring).Projective()


def IntegralSchemes(base_ring):
    r"""``Schemes(R).Integral()``, under the name the session catalogue uses."""
    return Schemes(base_ring).Integral()


def NormalSchemes(base_ring):
    r"""``Schemes(R).Normal()``, under the name the session catalogue uses."""
    return Schemes(base_ring).Normal()


def SmoothSchemes(base_ring):
    r"""``Schemes(R).Smooth()``, under the name the session catalogue uses."""
    return Schemes(base_ring).Smooth()


def _family_ingress(arguments):
    r"""Read arguments given one by one, or as one finite family, as that family.

    This is syntax ingress for calls such as ``closed_subscheme(f)``,
    ``closed_subscheme(f, g)`` and ``closed_subscheme((f, g))``: a single
    argument that is a Python sequence or an indexed family is the family
    itself.
    """
    match arguments:
        case ((tuple() | list() | IndexedFamily()) as family,):
            return family
        case _:
            return arguments


def _equation_family(equations):
    r"""The finite family of equations given one by one or as one family."""
    return finite_family(tuple(_family_ingress(equations)), name="Defining equations")


def _projective_equation_family(equations):
    r"""Raise engine-ring equations into the owned ring of that engine; keep owned ones.

    A homogeneous equation already in an owned polynomial ring is retained as
    it is.  One given in a Sage polynomial ring is the same polynomial seen
    through the private realization, and it is raised through the owned ring
    of that engine so every retained equation is owned mathematics.
    """
    raised = []
    for equation in equations:
        parent = equation.parent()
        match parent:
            case PolynomialRing_generic() | MPolynomialRing_base():
                # Homogeneous polynomial equations retain their selected
                # coefficient ring and ordered variable names; reconstruct
                # that polynomial ring rather than adopting this engine parent.
                owned = _own_ring(parent.base_ring()).polynomial_ring(
                    tuple(parent.variable_names())
                )
                raised.append(_owned_engine_element(owned, equation))
            case _ if parent in _SageRings():
                owned = _own_ring(parent)
                raised.append(_owned_engine_element(owned, equation))
            case _:
                raised.append(equation)
    assert all(equation.is_homogeneous() for equation in raised), (
        f"cannot form a closed subscheme of a projective scheme from the equations "
        f"{tuple(raised)}: the equations must be homogeneous, and "
        f"{next(equation for equation in raised if not equation.is_homogeneous())} is not"
    )
    return finite_family(tuple(raised), name="Homogeneous defining equations")


def _engine_projective_ambient(engine):
    r"""The Sage projective or multiprojective space a realization lies in, with its equations.

    Engine adapter (``OWN-06``): the one place the class of a Sage projective
    realization is inspected, for the projective closed-subscheme construction.
    A Sage subscheme records its ambient space and defining polynomials, and a
    closed subscheme of it is cut out in that ambient space by those
    polynomials together with the new equations; an ambient space is its own,
    with none.
    """
    match engine:
        case _SageAlgebraicSchemeQuasi():
            return engine.ambient_space(), tuple(engine.X().defining_polynomials())
        case _SageAlgebraicSchemeSubscheme():
            return engine.ambient_space(), tuple(engine.defining_polynomials())
        case _:
            return engine, ()


def _engine_projective_subscheme(engine, equations):
    r"""The Sage subscheme of the realization ``engine`` cut out by owned homogeneous equations.

    Each equation is copied by its exponent dictionary onto the coordinates of
    the ambient space, so the owned ring it was written in need not share the
    realization's variable names.
    """
    ambient, ambient_equations = _engine_projective_ambient(engine)
    ambient_ring = ambient.coordinate_ring()
    ambient_variables = tuple(ambient_ring.gens())
    return ambient.subscheme(
        ambient_equations
        + tuple(
            _copy_polynomial_by_exponents(
                _engine_element(equation.parent(), equation),
                ambient_ring,
                ambient_variables,
            )
            for equation in equations
        )
    )


def _native_embedding_rule(mor):
    r"""The arrow realization rule for the inclusion of a realized closed subscheme into its codomain.

    Both realizations lie in one ambient space, and the inclusion keeps every
    homogeneous coordinate.
    """
    ambient, _ambient_equations = _engine_projective_ambient(
        _engine_scheme(mor.codomain())
    )
    return mor.element_class(
        mor,
        _native_scheme_mor(mor.domain(), mor.codomain())(
            list(ambient.coordinate_ring().gens()), check=False
        ),
        mor=mor,
    )


class AffineGSchemes(OwnedCategory):
    r"""Represented affine schemes with a chosen action of one group.

    This is the affine specialization of ``GObjects(G, Schemes(R))`` and the
    construction owner for represented affine actions.  An object is ``Spec A``
    with the chosen left action ``rho: G -> Aut(Spec A)``; the scheme the
    action was stated on is retained as the constructor's input and returned
    by :meth:`unacted_scheme`.
    """

    @staticmethod
    def __classcall__(cls, group, base_ring):
        from sage_extensions.categories.group.groups import _owned_group

        base_ring = _own_ring(base_ring)
        assert base_ring in OwnedRings().Commutative(), (
            f"affine G-schemes here are actions on classical schemes over Spec(R), "
            f"so their base ring must be commutative, but {base_ring} is in {base_ring.category()}"
        )
        return Category.__classcall__(cls, _owned_group(group), base_ring)

    def __init__(self, group, base_ring) -> None:
        self._group = group
        self._base_ring = base_ring
        OwnedCategory.__init__(self)

    def acting_group(self):
        return self._group

    def base_ring(self):
        return self._base_ring

    def super_categories(self):
        from sage_extensions.categories.group.g_objects import GObjects

        return [
            GObjects(self.acting_group(), Schemes(self.base_ring())),
            Schemes(self.base_ring()).Affine(),
        ]

    def _repr_object_names(self):
        return f"affine {self.acting_group()}-schemes over {self.base_ring()}"

    def an_object(self):
        scheme = AffineSpaces(self.base_ring())(1)
        identity = scheme.categorical_identity_morphism()
        return self(scheme, lambda _group_element: identity)

    def global_sections_functor(self):
        r"""Return ``Gamma(-, O): AffGSch_G^op -> Modules(R[G])``.

        For a left action on ``X``, the induced left action on sections is
        ``g . s = (g^{-1})^* s``; the inverse is forced by pullback
        contravariance.
        """
        from sage_extensions.categories.schemes.quotients import (
            _AffineSectionModuleFunctor,
        )

        return _AffineSectionModuleFunctor(self.acting_group(), self.base_ring())

    def _call_(self, scheme, action):
        r"""``Spec A`` with the left action ``g |-> action(g)`` of this group.

        The result is a new affine scheme on the coordinate algebra of
        ``scheme``, constructed in this category; the action datum it receives
        is the coordinate pullback of each action morphism, which is the datum
        a morphism of affine schemes is.
        """
        base = self.base_ring()
        assert scheme in Schemes(base).Affine(), (
            f"cannot make {scheme} an object of {self}: it must be an affine scheme over {base}, but "
            f"it is an object of {scheme.category()}"
        )
        source_endomorphisms = Schemes(base).Mor(scheme, scheme)

        def action_pullback(group_element):
            return source_endomorphisms(
                action(group_element)
            ).coordinate_algebra_morphism()

        acted = _affine_scheme(
            scheme.coordinate_algebra(),
            base,
            (self,),
            acting_group=self.acting_group(),
            action=action_pullback,
            underlying_category=Schemes(base),
            unacted_scheme=scheme,
        )
        acted.validate_action(check=False)
        return acted

    class ParentMethods:
        def __init__(self, unacted_scheme, **rest) -> None:
            self._unacted_scheme = unacted_scheme
            super().__init__(**rest)

        def nontrivial_stabilizer_subscheme(self):
            r"""Scheme-theoretic union of nonidentity fixed loci for a finite action.

            The computation uses the group's selected finite iteration.  A
            finite cardinal alone supplies no such data, and an undecided
            comparison with the identity cannot select a union component.
            """
            group = self.acting_group()
            assert group.is_finite() is True, (
                f"a represented nontrivial stabilizer subscheme requires a finite group, not {group}"
            )
            try:
                elements = iter(group)
            except TypeError, NotImplementedError:
                assert False, (
                    f"the nontrivial stabilizer subscheme of {self} requires a selected "
                    f"finite enumeration of {group}"
                )
            ideal = None
            identity = group.one()
            for element in elements:
                is_identity = element == identity
                if is_identity is True:
                    continue
                assert is_identity is False, (
                    f"the nontrivial stabilizer subscheme of {self} requires deciding "
                    f"whether {element} is the identity of {group}; that comparison is undecided"
                )
                fixed = self._cyclic_restriction(element).fixed_ideal()
                ideal = fixed if ideal is None else ideal.intersection(fixed)
            if ideal is None:
                algebra = self.coordinate_algebra()
                ideal = algebra.ideal(algebra.one())
            return self.closed_subscheme(tuple(ideal.ideal_generators()))

        def unacted_scheme(self):
            r"""Return the affine scheme the action was stated on."""
            return self._unacted_scheme

        @cached_method
        def fixed_ideal(self):
            r"""Return the ideal defining the common fixed subscheme ``X^G``.

            For ``X = Spec(A)`` and chosen generators ``s`` of ``G``, the fixed
            ideal is generated by ``s^*(a) - a`` on a chosen algebra generating
            family of ``A``.  Those equations generate the full equalizer ideal
            because every ``s^*`` is an ``R``-algebra map: modulo them each
            ``s^*`` fixes the scalar image and every algebra generator, hence is
            the identity; since the ``s`` generate ``G``, so is every element.
            """
            group = self.acting_group()
            assert (
                group.has_selected_group_resolution()
                and group.group_generating_set().cardinality().is_finite() is True
            ), (
                f"cannot form the ideal of the fixed locus of {group} on {self}: the group must have a "
                f"chosen finite set of group generators, but it is an object of {group.category()}"
            )
            algebra = self.coordinate_algebra()
            assert algebra.is_framed_algebra(), (
                f"cannot form the ideal of the fixed locus of {group} on {self}: the coordinate algebra "
                f"{algebra} must have a chosen set of algebra generators, but it is an object of "
                f"{algebra.category()}"
            )
            labels = algebra.algebra_generating_set()
            assert labels.cardinality().is_finite() is True, (
                f"cannot form the ideal of the fixed locus of {group} on {self}: the coordinate algebra "
                f"{algebra} must have finitely many chosen algebra generators, but it has "
                f"{labels.cardinality()}"
            )
            equations = []
            for group_generator in group.group_generators():
                pullback = self.action_of(group_generator).coordinate_algebra_morphism()
                assert (
                    pullback.domain() is algebra and pullback.codomain() is algebra
                ), (
                    f"cannot form the ideal of the fixed locus of {group} on {self}: the pullback {pullback} "
                    f"of the group generator {group_generator} must be an endomorphism of {algebra}, but it is "
                    f"{pullback.domain()} -> {pullback.codomain()}"
                )
                equations.extend(
                    pullback(algebra.algebra_generator(label))
                    - algebra.algebra_generator(label)
                    for label in labels
                )
            return algebra.ideal(*equations)

        @cached_method
        def fixed_subscheme(self):
            r"""Return the common fixed subscheme ``X^G`` of this affine action."""
            return self.closed_subscheme(tuple(self.fixed_ideal().ideal_generators()))

        @cached_method
        def _invariant_algebra_data(
            self,
        ) -> tuple[
            ObjectOfCategory,
            AlgebraHomomorphism,
            tuple[ElementOfCategoryObject, ...],
        ]:
            r"""Return the selected ``(A^G, A^G -> A, engine invariants)``."""
            return _affine_linear_invariant_algebra_data(self)

        def _invariant_algebra_element(self, element) -> ElementOfCategoryObject:
            r"""Express one invariant element of ``A`` in ``A^G``.

            The invariant-ring computation used by the affine quotient returns a
            polynomial certificate in its selected invariant generators; the
            certificate is evaluated in the owned invariant algebra.
            """
            source_algebra = self.coordinate_algebra()
            element = source_algebra(element)
            # Select the finite polynomial supplier before traversing its
            # determining family.  Unknown invariance is not a refutation;
            # an exact subalgebra certificate below can prove the lift.
            invariant_algebra, inclusion, engine_invariants = (
                self._invariant_algebra_data()
            )
            for group_generator in self.acting_group().group_generators():
                image = self.action_of(group_generator).coordinate_algebra_morphism()(
                    element
                )
                if (image == element) is False:
                    raise ValueError(
                        f"cannot express {element} in the invariant algebra of {self}: "
                        f"the action of {group_generator} does not fix it"
                    )
            if not engine_invariants:
                return invariant_algebra(element)
            engine_source = _engine_ring(source_algebra)
            certificate = engine_source(
                _engine_element(source_algebra, element)
            ).in_subalgebra(
                engine_invariants,
                algorithm="groebner",
                certificate="invariant",
            )
            assert certificate is not None, (
                f"cannot express the invariant element {element} of {source_algebra} in the chosen "
                f"generators of the invariant algebra {invariant_algebra}: Sage's subalgebra membership "
                "test found no expression"
            )
            result = _evaluate_polynomial_in_algebra(certificate, invariant_algebra)
            image = inclusion(result)
            assert (image == element) is not False, (
                f"the expression of {element} in the invariant algebra {invariant_algebra} is wrong: its "
                f"image in {source_algebra} is {image}, not {element}"
            )
            # The selected polynomial realization checks the certificate
            # exactly even when the public equality diagnostic is undecided.
            assert engine_source(
                _engine_element(source_algebra, image)
            ) == engine_source(_engine_element(source_algebra, element)), (
                f"the polynomial certificate for {element} in {invariant_algebra} has the wrong image"
            )
            return result

        def _factor_through_affine_quotient(self, morphism):
            r"""Factor one invariant affine morphism uniquely through ``Spec(A^G)``.

            If ``f : Spec(A) -> Spec(C)`` is invariant, every selected
            generator of ``C`` pulls back to an element of ``A^G``, and the
            subalgebra-membership certificate expresses that pullback in the
            selected invariant generators.  These expressions define
            ``C -> A^G`` and hence the factor ``Spec(A^G) -> Spec(C)``.
            Uniqueness follows because the selected presentation of ``A^G`` was
            obtained from the kernel of the map from the polynomial algebra on
            those invariant generators to ``A``; its inclusion is injective.
            """
            assert morphism.domain() is self, (
                f"cannot factor {morphism} through the quotient of {self} by {self.acting_group()}: its "
                f"domain is {morphism.domain()}, not {self}"
            )
            target = morphism.codomain()
            base = self.scheme_base_ring()
            assert target in Schemes(base).Affine(), (
                f"cannot factor {morphism} through the affine quotient of {self}: the codomain {target} "
                f"must be an affine scheme over {base}, but it is an object of {target.category()}"
            )
            target_algebra = target.coordinate_algebra()
            assert target_algebra.is_framed_algebra(), (
                f"cannot factor {morphism} through the affine quotient of {self}: the coordinate algebra "
                f"{target_algebra} of {target} must have a chosen set of algebra generators, but it is an "
                f"object of {target_algebra.category()}"
            )
            labels = target_algebra.algebra_generating_set()
            assert labels.cardinality().is_finite() is True, (
                f"cannot factor {morphism} through the affine quotient of {self}: the coordinate algebra "
                f"{target_algebra} of {target} must have finitely many chosen algebra generators, but it "
                f"has {labels.cardinality()}"
            )
            pullback = morphism.coordinate_algebra_morphism()
            invariant_algebra, inclusion, _engine_invariants = (
                self._invariant_algebra_data()
            )
            factor_pullback = target_algebra.Mor(invariant_algebra)(
                {
                    label: self.invariant_algebra_element(
                        pullback(target_algebra.algebra_generator(label))
                    )
                    for label in labels
                }
            )
            factor = _affine_morphism_from_pullback(
                self.affine_quotient(), target, factor_pullback
            )
            # The exact lifts of the chosen algebra generators prove this
            # triangle.  Preserve an undecided general map comparison while
            # still refusing an explicitly refuted triangle.
            assert (factor * self.quotient_morphism() == morphism) is not False, (
                f"the factorization {factor} of {morphism} through the quotient of {self} is wrong: its "
                f"composite with the quotient map {self} -> {self.affine_quotient()} is not {morphism}"
            )
            return factor


def _affine_linear_invariant_algebra_data(
    scheme,
) -> tuple[
    ObjectOfCategory,
    AlgebraHomomorphism,
    tuple[ElementOfCategoryObject, ...],
]:
    r"""Return a finite presentation of ``A^G`` and its inclusion into ``A``.

    Private computation boundary (``OWN-06``) for the supported affine quotient
    regime: ``A`` is a polynomial algebra over a field, ``G`` is finite with
    chosen generators, and the pullbacks are linear on the chosen polynomial
    generators.  Sage's matrix-group ``invariant_generators`` routes invariant
    generation to Singular; Sage's elimination ideal computes the kernel of the
    polynomial map on the returned invariant generators.
    """
    from sage.groups.matrix_gps.finitely_generated import MatrixGroup
    from sage.matrix.constructor import matrix as sage_matrix
    from sage.rings.polynomial.polynomial_ring_constructor import (
        PolynomialRing as SagePolynomialRing,
    )

    group = scheme.acting_group()
    assert (
        group.is_finite() is True
        and group.has_selected_group_resolution()
        and group.group_generating_set().cardinality().is_finite() is True
    ), (
        f"cannot compute the invariant algebra of {group} acting on {scheme}: the group must be "
        f"finite with a chosen finite set of group generators, but it is an object of "
        f"{group.category()}"
    )
    algebra = scheme.coordinate_algebra()
    base = scheme.scheme_base_ring()
    assert algebra in SymmetricAlgebras(base) and algebra.is_framed_algebra(), (
        f"cannot compute the invariant algebra of {group} acting on {scheme}: the coordinate "
        f"algebra {algebra} must be a polynomial algebra with chosen variables, but it is an "
        f"object of {algebra.category()}"
    )
    assert algebra.algebra_generating_set().cardinality().is_finite() is True, (
        f"cannot compute the invariant algebra of {group} acting on {scheme}: the coordinate "
        f"algebra {algebra} must be a polynomial algebra in finitely many variables"
    )
    assert base in OwnedFields(), (
        f"cannot compute the invariant algebra of {group} acting on {scheme}: the base ring "
        f"{base} must be a field"
    )
    labels = tuple(algebra.algebra_generating_set())
    engine_algebra = _engine_ring(algebra)
    variables = tuple(engine_algebra.gens())
    assert len(variables) == len(labels), (
        f"cannot compute the invariant algebra of {group} acting on {scheme}: {algebra} has "
        f"{len(labels)} chosen variables, but its Sage polynomial ring has {len(variables)}"
    )
    engine_base = _engine_ring(base)

    # The polynomial algebra on no generators is the scalar field itself, which
    # every automorphism over the base fixes pointwise.
    if not variables:
        return algebra, algebra.Mor(algebra).identity(), ()
    group_generators = tuple(group.group_generators())
    if not group_generators:
        return algebra, algebra.Mor(algebra).identity(), variables

    backend_matrices = []
    pullbacks = []
    for group_generator in group_generators:
        pullback = scheme.action_of(group_generator).coordinate_algebra_morphism()
        pullbacks.append(pullback)
        rows = []
        for label in labels:
            image = engine_algebra(
                _engine_element(algebra, pullback(algebra.algebra_generator(label)))
            )
            row = [
                engine_base(image.monomial_coefficient(variable))
                for variable in variables
            ]
            linear_part = sum(
                (
                    coefficient * variable
                    for coefficient, variable in zip(row, variables, strict=True)
                ),
                engine_algebra.zero(),
            )
            assert image == linear_part, (
                f"cannot compute the invariant algebra of {group} acting on {scheme}: the action must be "
                f"linear in the variables, but {group_generator} sends the variable {label} to {image}"
            )
            # Sage/Singular's matrix-group invariant convention acts on the
            # coordinate variables by the transpose of the supplied matrix, so
            # the rows are the actual pullback images of the chosen variables.
            rows.append(row)
        backend_matrices.append(sage_matrix(engine_base, rows))

    backend_invariants = tuple(MatrixGroup(backend_matrices).invariant_generators())
    assert backend_invariants, (
        f"Sage's invariant ring computation returned no generators for the invariant algebra of "
        f"{group} acting on {scheme}, whose coordinate algebra has {len(variables)} variables"
    )
    engine_invariants = tuple(
        _copy_polynomial_by_exponents(invariant, engine_algebra, variables)
        for invariant in backend_invariants
    )
    invariant_elements = tuple(
        _owned_engine_element(algebra, invariant) for invariant in engine_invariants
    )
    for pullback in pullbacks:
        for invariant, engine_invariant in zip(
            invariant_elements, engine_invariants, strict=True
        ):
            image = pullback(invariant)
            assert (image == invariant) is not False, (
                f"Sage's generator {invariant} of the invariant ring of {group} acting on {scheme} "
                f"is not fixed by {pullback}"
            )
            assert (
                engine_algebra(_engine_element(algebra, image)) == engine_invariant
            ), (
                f"the polynomial realization of Sage's invariant {invariant} is not fixed by {pullback}"
            )

    invariant_labels = tuple(
        f"invariant_{index}" for index in range(len(engine_invariants))
    )
    presentation = base.free_module(invariant_labels).symmetric_algebra()
    presentation_engine = _engine_ring(presentation)
    ambient_count = len(variables)
    invariant_count = len(engine_invariants)
    combined = SagePolynomialRing(
        engine_base,
        ambient_count + invariant_count,
        names=tuple(f"ambient_{index}" for index in range(ambient_count))
        + tuple(f"invariant_{index}" for index in range(invariant_count)),
    )
    ambient_variables = tuple(combined.gens()[:ambient_count])
    invariant_variables = tuple(combined.gens()[ambient_count:])
    graph_ideal = combined.ideal(
        tuple(
            invariant_variables[index]
            - _copy_polynomial_by_exponents(invariant, combined, ambient_variables)
            for index, invariant in enumerate(engine_invariants)
        )
    )
    kernel = graph_ideal.elimination_ideal(ambient_variables)
    relations = []
    for relation in kernel.gens():
        if relation == combined.zero():
            continue
        relation_terms = {}
        for exponent, coefficient in relation.dict().items():
            powers = _polynomial_exponents(exponent, ambient_count + invariant_count)
            assert not any(powers[:ambient_count]), (
                f"Sage's elimination of the variables of {algebra} from the relations among the "
                f"invariants of {group} returned {relation}, which still contains those variables"
            )
            relation_terms[powers[ambient_count:]] = coefficient
        relations.append(
            _owned_engine_element(presentation, presentation_engine(relation_terms))
        )
    invariant_algebra = (
        presentation
        if not relations
        else presentation.quotient_by_relations(tuple(relations))
    )
    invariant_labels = tuple(invariant_algebra.algebra_generating_set())
    inclusion = invariant_algebra.Mor(algebra)(
        {
            label: invariant_elements[index]
            for index, label in enumerate(invariant_labels)
        }
    )
    return invariant_algebra, inclusion, engine_invariants


# ---------------------------------------------------------------------------
# Affine and projective spaces, with their chosen coordinates.
# ---------------------------------------------------------------------------


def _normalized_space_names(names):
    r"""Coordinate names as Sage's space constructors read them: ``None``, a string, or a tuple."""
    match names:
        case None | str():
            return names
        case _:
            return tuple(str(name) for name in names)


def _space_placements(base, dimension):
    r"""The theorem-backed placements of ``A^n_R`` and ``P^n_R`` read at construction."""
    schemes = Schemes(base)
    placements = [
        category
        for category, holds in (
            (schemes.Integral(), _integral_placement(base)),
            (schemes.Normal(), _normal_placement(base)),
        )
        if holds
    ]
    if _integral_placement(base):
        from sage_extensions.categories.schemes.varieties import (
            Curves,
            Surfaces,
            Varieties,
        )

        dimension = int(dimension)
        placements.append(Varieties(base))
        match dimension:
            case 1:
                placements.append(Curves(base))
            case 2:
                placements.append(Surfaces(base))
    return tuple(placements)


def _affine_space_coordinates(base, dimension, names):
    r"""Sage's affine ``n``-space on the chosen names, and its owned polynomial coordinate algebra.

    The coordinate algebra is the owned polynomial algebra on the coordinate
    names, which is the free, graded free and symmetric algebra on them.
    """
    engine = _SageAffineSpace(
        int(dimension), _engine_ring(base), names=_normalized_space_names(names)
    )
    return engine, _engine_polynomial_algebra(engine.coordinate_ring(), base)


def _affine_space(base, coordinates, placements=(), **level_data):
    r"""Construct ``A^n_R = Spec R[x_1, ..., x_n]`` from :func:`_affine_space_coordinates`.

    ``placements`` and ``level_data`` are those of a specialized construction
    -- a product of affine spaces, a scalar base change -- whose object is also
    an affine space.
    """
    engine, algebra = coordinates
    dimension = int(algebra.algebra_generating_set().cardinality())
    if dimension == 0:
        # A^0_R = Spec R is the identity over Spec R, hence projective.
        placements = (Schemes(base).Projective(), *placements)
    return _object_of(
        owned_category_join(
            (
                AffineSpaces(base),
                *_space_placements(base, dimension),
                *placements,
            )
        ),
        scheme_base_ring=base,
        scheme_engine=engine,
        coordinate_algebra=algebra,
        **level_data,
    )


@cached_function(key=lambda base, dimension, names: (id(base), int(dimension), names))
def _canonical_affine_space(base, dimension, names):
    r"""The selected ordinary ``A^n_R`` for one coordinate datum."""
    return _affine_space(base, _affine_space_coordinates(base, dimension, names))


class AffineSpaces(OwnedCategoryOverBaseRing):
    r"""Affine spaces ``A^n_R`` with chosen coordinates ``x_1, ..., x_n``.

    The chosen coordinates are the free generators of the coordinate algebra,
    so an object is ``Spec`` of a polynomial algebra with its generators; the
    same scheme with another coordinate system is another object.
    """

    def analytification(self, scalar_embedding):
        r"""Return affine-space analytification along this base embedding."""
        assert _owned_ring(scalar_embedding.domain()) is self.base_ring(), (
            f"cannot analytify the affine spaces over {self.base_ring()} along {scalar_embedding}: the "
            f"embedding must start at {self.base_ring()}, but it starts at {scalar_embedding.domain()}"
        )
        from sage_extensions.categories.schemes.analytic_families import (
            _affine_space_analytification_functor,
        )

        return _affine_space_analytification_functor(scalar_embedding)

    def an_object(self):
        r"""The affine line over the base ring."""
        return self(1)

    def _call_(self, dimension, names=None):
        r"""Construct ``A^n_R`` on the chosen coordinate names, one object for each datum."""
        return _canonical_affine_space(
            self.base_ring(),
            int(_engine_numeral(SageZZ, dimension)),
            _normalized_space_names(names),
        )

    def _repr_object_names(self):
        return f"affine spaces over {self.base_ring()}"

    def super_categories(self):
        return [Schemes(self.base_ring()).Affine().FiniteType().Smooth()]

    class ParentMethods:
        def hypersurface(self, f):
            r"""The hypersurface ``V(f) = Spec k[x_1, ..., x_n]/(f)`` with its closed immersion into ``A^n_k``.

            Domain: a nonconstant polynomial ``f`` of the coordinate algebra
            ``k[x_1, ..., x_n]`` of this affine space (Hartshorne, *Algebraic
            Geometry*, I.1).  Codomain: a closed subscheme of ``A^n_k``, a
            scheme over ``k`` whose inclusion ``V(f) -> A^n_k`` is ``Spec`` of
            the quotient map ``k[x_1, ..., x_n] -> k[x_1, ..., x_n]/(f)``.
            """
            assert f in self.coordinate_algebra(), (
                f"a hypersurface of {self} is cut out by an element of its coordinate algebra "
                f"{self.coordinate_algebra()}, but {f} is not one"
            )
            return self.closed_subscheme(f)

        @cached_method
        def _picard_group(self):
            r"""Return ``Pic(A^n_k) = 0`` over a field."""
            base = self.scheme_base_ring()
            assert base in OwnedFields(), (
                f"cannot compute the Picard group of {self}: Pic(A^n) = 0 is used here only over a field, "
                f"but the base ring is {base}"
            )
            from sage_extensions.categories.divisors.picard_groups import PicardGroups

            return PicardGroups().trivial(self)

        @cached_method
        def _class_group(self):
            r"""Return ``Cl(A^n_k) = 0`` over a field."""
            base = self.scheme_base_ring()
            assert base in OwnedFields(), (
                f"cannot compute the class group of {self}: Cl(A^n) = 0 is used here only over a field, "
                f"but the base ring is {base}"
            )
            from sage_extensions.categories.divisors.class_groups import ClassGroups

            return ClassGroups().trivial(self)

        def _zeta_function(self):
            r"""Return ``Z(A^d/F_q, T) = 1/(1 - q^d T)``."""
            base = self.scheme_base_ring()
            rational_functions, T = _rational_functions_in_T()
            q = int(base.cardinality().finite_value())
            d = int(self.relative_dimension())
            return rational_functions.one() / (rational_functions.one() - q**d * T)


def _rational_functions_in_T():
    r"""The owned rational function field ``QQ(T)`` and its variable ``T``."""

    rationals = _owned_rationals()
    polynomial = rationals.polynomial_ring("T")
    rational_functions = _commutative_algebra_with_structure(
        polynomial.fraction_field(), rationals, ("T",)
    )
    return rational_functions, rational_functions.algebra_generator("T")


def _projective_space(base, dimension, names, placements=(), **level_data):
    r"""Construct ``P^n_R = Proj R[x_0, ..., x_n]`` on the chosen homogeneous coordinates.

    The realization is Sage's projective space on the same names; the chosen
    coordinates are the data it is built from.
    """
    dimension = int(dimension)
    engine = _SageProjectiveSpace(
        dimension, _engine_ring(base), names=_normalized_space_names(names)
    )
    decided = list(_space_placements(base, dimension))
    match dimension:
        case 0:
            # Proj R[x_0] = D_+(x_0) = Spec R: the degree-zero part of
            # R[x_0,x_0^-1] is R. Retain its affine algebra datum.
            decided.append(Schemes(base).Affine())
            level_data = {"coordinate_algebra": base, **level_data}
        case _:
            pass
    match (base in OwnedFields(), dimension):
        case (True, 2):
            from sage_extensions.categories.schemes.varieties import Surfaces

            decided.append(Surfaces(base).Projective())
        case _:
            pass
    return _object_of(
        owned_category_join((ProjectiveSpaces(base), *decided, *placements)),
        scheme_base_ring=base,
        scheme_engine=engine,
        **level_data,
    )


@cached_function(key=lambda base, dimension, names: (id(base), int(dimension), names))
def _canonical_projective_space(base, dimension, names):
    r"""The selected ordinary ``P^n_R`` for one coordinate datum."""
    return _projective_space(base, dimension, names)


class ProjectiveSpaces(OwnedCategoryOverBaseRing):
    r"""Projective spaces ``P^n_R`` with chosen homogeneous coordinates ``x_0, ..., x_n``."""

    def an_object(self):
        r"""The projective line over the base ring."""
        return self(1)

    def _call_(self, dimension, names=None):
        r"""Construct ``P^n_R`` on the chosen coordinate names, one object for each datum."""
        return _canonical_projective_space(
            self.base_ring(),
            int(_engine_numeral(SageZZ, dimension)),
            _normalized_space_names(names),
        )

    def _repr_object_names(self):
        return f"projective spaces over {self.base_ring()}"

    def analytification(self, scalar_embedding):
        r"""The analytification functor ``P^n_K |-> CP^n`` along an embedding ``sigma: K -> CC``.

        Domain: the projective spaces over ``K``.  Codomain: compact complex
        manifolds (Serre, GAGA, Sec. 2); ``P^n_K`` goes to ``CP^n`` with its
        standard atlas.
        """
        assert _owned_ring(scalar_embedding.domain()) is self.base_ring(), (
            f"cannot analytify the projective spaces over {self.base_ring()} along {scalar_embedding}: "
            f"the embedding must start at {self.base_ring()}, but it starts at {scalar_embedding.domain()}"
        )
        from sage_extensions.categories.schemes.analytic_families import (
            _projective_space_analytification_functor,
        )

        return _projective_space_analytification_functor(scalar_embedding)

    def super_categories(self):
        return [Schemes(self.base_ring()).Projective().Smooth()]

    class ParentMethods:
        def _repr_(self) -> str:
            return (
                f"Projective Space of dimension {self.relative_dimension()} over "
                f"{self.scheme_base_ring()}"
            )

        def variable_names(self):
            r"""The names of the chosen homogeneous coordinates ``x_0, ..., x_n``."""
            return tuple(str(name) for name in _engine_scheme(self).variable_names())

        @cached_method
        def fan(self):
            r"""Return the owned standard fan of ``P^n``."""
            from sage_extensions.categories.schemes.toric.fans import (
                RationalPolyhedralFans,
            )

            lattice = _owned_integers().free_module(int(self.relative_dimension()))
            return RationalPolyhedralFans(lattice).projective_space_fan()

        @cached_method
        def _picard_to_class_group_morphism(
            self,
            base_picard_group=None,
            base_class_group=None,
            base_picard_to_class=None,
        ):
            r"""Return the projective-bundle comparison ``Pic(P^n_S) -> Cl(P^n_S)``.

            Over a nonfield base the base Picard group, base class group and
            their comparison are the data of the projective-bundle formula and
            are supplied together; over a field they are the trivial groups of
            ``Spec k``.
            """
            from sage_extensions.categories.divisors.general_divisors import (
                _projective_space_over_field_picard_to_class_group_morphism,
                _projective_space_picard_to_class_group_morphism,
            )

            supplied = (base_picard_group, base_class_group, base_picard_to_class)
            match supplied:
                case (None, None, None):
                    base = self.scheme_base_ring()
                    assert base in OwnedFields(), (
                        f"cannot compare the Picard and class groups of {self}: over the base ring {base}, which "
                        f"is not a field, the Picard group and class group of Spec {base} and the map between "
                        "them must be given"
                    )
                    return _projective_space_over_field_picard_to_class_group_morphism(
                        self
                    )
                case _:
                    assert all(value is not None for value in supplied), (
                        f"cannot compare the Picard and class groups of {self}: the Picard group, the class "
                        "group of the base and the map between them must be given together, but only some of "
                        "them were given"
                    )
                    return _projective_space_picard_to_class_group_morphism(
                        self, *supplied
                    )

        def _picard_group(self):
            r"""Return ``Pic(P^n_k) = ZZ[O(1)]`` over a field."""
            base = self.scheme_base_ring()
            assert base in OwnedFields(), (
                f"the represented computation of Pic({self}) uses a field base, but the base is {base}; "
                "construct the projective-bundle decomposition from Pic(S) at PicardGroups().projective_bundle"
            )
            return self.picard_to_class_group_morphism().domain()

        def hyperplane_class(self):
            r"""``[O(1)]``, the module generator of ``Pic(P^n_k) = ZZ[O(1)]`` over a field ``k``.

            Hartshorne, *Algebraic Geometry*, II.6.4 and II.6.17.
            """
            return self.picard_group().module_generator("O(1)")

        def integral_singular_cohomology(self, degree):
            r"""``H^degree(P^n(CC); ZZ)``, the cohomology of the complex realization along ``QQ -> CC``."""
            from sage_extensions.categories.schemes.geometric_cohomology import (
                _integral_singular_cohomology_over_rationals,
            )

            return _integral_singular_cohomology_over_rationals(self, degree)

        def _hodge_structure(self):
            r"""``H^*(P^n(CC); ZZ) = direct_sum_p ZZ(-p)`` along ``QQ -> CC``.

            The class of a codimension-p linear subspace spans H^{2p} and
            has Hodge type (p,p); odd cohomology vanishes. See Example 2.2.3,
            https://sites.math.duke.edu/~robles/hw_HT.pdf .
            """
            from sage_extensions.categories.modules.hodge_structures import (
                _split_mixed_hodge_structure,
            )

            assert self.scheme_base_ring() is _owned_rationals(), (
                f"Hodge realization of {self}: not implemented for this base; "
                "the represented embedding is QQ -> CC"
            )
            return _split_mixed_hodge_structure(
                _owned_integers(),
                tuple(range(0, 2 * int(self.relative_dimension()) + 1, 2)),
                name=f"H^*({self}(CC); ZZ)",
            )

        @cached_method
        def _picard_intersection_pairing(self):
            r"""The form ``[O(1)]^2 = 1`` on ``Pic(P^2)``."""
            assert int(self.relative_dimension()) == 2, (
                f"the projective-space surface pairing applies to P^2, but {self} has relative "
                f"dimension {self.relative_dimension()}"
            )
            picard = self.picard_group()
            labels = picard.module_generating_set()
            assert int(labels.cardinality()) == 1, (
                f"Pic(P^2) over a field should have one generator [O(1)], but {picard} has "
                f"{labels.cardinality()} generators"
            )
            integers = _owned_integers()
            return BilinearMap(
                picard,
                picard,
                integers.regular_module(),
                lambda _left, _right: integers.one(),
            )

        def _del_pezzo_degree(self):
            r"""``(-K_{P^2})^2 = (3H)^2 = 9``."""
            assert int(self.relative_dimension()) == 2, (
                f"the projective-space Del Pezzo degree applies to P^2, but {self} has relative "
                f"dimension {self.relative_dimension()}"
            )
            return _owned_integers()(9)

        def _is_del_pezzo(self) -> bool:
            r"""``P^2`` is Del Pezzo because ``-K = O(3)`` is ample."""
            assert int(self.relative_dimension()) == 2, (
                f"the projective-space Del Pezzo predicate applies to P^2, but {self} has relative "
                f"dimension {self.relative_dimension()}"
            )
            return bool(self.anticanonical_line_bundle().is_ample())

        def _class_group(self):
            return self.picard_to_class_group_morphism().codomain()

        def homogeneous_coordinate_ring(self):
            r"""The homogeneous coordinate ring ``S = k[x_0, ..., x_n]`` of ``P^n_k = Proj S``.

            Domain: this projective space.  Codomain: the polynomial
            ``k``-algebra on the homogeneous coordinates ``x_0, ..., x_n``,
            graded by total degree, with ``S_d = H^0(P^n_k, O(d))`` for
            ``d >= 0`` (Hartshorne, *Algebraic Geometry*, II.2 and II.5.13).
            It is the ring of the global sections of ``O(1)``, so its degree-1
            part is ``H^0(P^n_k, O(1))``.
            """
            return self.O(1).global_sections().homogeneous_coordinate_ring()

        def homogeneous_coordinate_generators(self):
            r"""Return the chosen homogeneous coordinate generators of this projective space."""
            return self.homogeneous_coordinate_ring().algebra_generators()

        def hyperplane(self, index=0):
            r"""The coordinate hyperplane ``V_+(x_index)``, the hypersurface of the degree-1 form ``x_index``."""
            return self.hypersurface(
                tuple(self.homogeneous_coordinate_generators())[int(index)]
            )

        def hypersurface(self, f, placements=()):
            r"""The hypersurface ``V_+(f) = Proj k[x_0, ..., x_n]/(f)`` with its closed immersion into ``P^n_k``.

            Domain: a nonconstant homogeneous polynomial ``f`` of the
            homogeneous coordinate ring ``k[x_0, ..., x_n]`` of this projective
            space (Hartshorne, *Algebraic Geometry*, I.2).  Codomain: a closed
            subscheme of ``P^n_k``, a projective scheme over ``k`` whose
            inclusion ``V_+(f) -> P^n_k`` is induced by the graded quotient map
            ``k[x_0, ..., x_n] -> k[x_0, ..., x_n]/(f)``.  The projective
            closed-subscheme construction asserts that ``f`` is homogeneous.  A caller
            that knows ``f`` irreducible states ``Schemes(k).Integral()`` in
            ``placements``: then ``(f)`` is a homogeneous prime and ``V_+(f)`` is
            integral.

            ``V_+(f)`` is an effective Cartier divisor: on the chart ``D_+(x_i)``
            it is cut out by the single nonzerodivisor ``f / x_i^e``, with ``e``
            the degree of ``f``, so its ideal sheaf is ``O(-e)`` and its Picard
            class is ``[O(e)] = e [O(1)]`` (Hartshorne, Proposition II.6.4 and
            Corollary II.6.17).
            """
            degree = self.homogeneous_coordinate_ring().homogeneous_degree(f)
            hyperplane_class = next(iter(self.picard_group().module_generators()))
            return self.closed_subscheme(
                f,
                placements=(EffectiveCartierDivisors(self), *placements),
                effective_cartier_ideal_sheaf=self.O(-degree),
                effective_cartier_picard_class=degree * hyperplane_class,
            )

        def basic_open(self, homogeneous_element):
            r"""Return ``D_+(homogeneous_element)`` as the complement of its zero locus."""
            return self.closed_subscheme(homogeneous_element).open_complement()

        def _standard_chart_coordinate_name(self, chart_index, numerator_index):
            r"""The name of the coordinate ``x_k / x_i`` on the ``i``-th standard chart."""
            return f"x{int(numerator_index)}_over_x{int(chart_index)}"

        def _standard_chart_coordinate(self, chart_index, numerator_index):
            r"""``x_k / x_i`` as a generator of the ``i``-th chart's coordinate algebra."""
            algebra = self.standard_affine_chart(chart_index).coordinate_algebra()
            return algebra.algebra_generator(
                self._standard_chart_coordinate_name(chart_index, numerator_index)
            )

        @cached_method
        def standard_affine_charts(self):
            r"""The family ``(U_0, ..., U_n)`` of standard affine charts of ``P^n_R``.

            ``U_i = D_+(x_i)`` is the spectrum of the degree-zero part of the
            graded localization at ``x_i``, the polynomial ring on the ``n``
            ratios ``x_k/x_i`` with ``k`` other than ``i``; each chart is affine
            ``n``-space and its coordinate names record which ratio each
            variable is (Stacks, Tag 01M3).
            """
            dimension = int(self.relative_dimension())
            base = self.scheme_base_ring()
            charts = tuple(
                AffineSpaces(base)(
                    dimension,
                    names=tuple(
                        self._standard_chart_coordinate_name(index, numerator)
                        for numerator in range(dimension + 1)
                        if numerator != index
                    ),
                )
                for index in range(dimension + 1)
            )
            return finite_family(charts, name="Standard affine charts")

        def standard_affine_chart(self, index):
            r"""``U_i = D_+(x_i)``, the ``i``-th standard affine chart."""
            return self.standard_affine_charts()[int(index)]

        @cached_method
        def standard_affine_chart_embedding(self, index):
            r"""The standard open immersion ``U_i = D_+(x_i) -> P^n_R``."""
            return _standard_projective_chart_embedding(self, int(index))

        def standard_chart_overlap(self, chart_index, other_index):
            r"""``U_i cap U_j = D(x_j/x_i)``, an open of the ``i``-th chart."""
            chart = self.standard_affine_chart(chart_index)
            return chart.distinguished_open(
                self._standard_chart_coordinate(chart_index, other_index)
            )

        def _standard_chart_change(self, source_index, target_index):
            r"""``U_i cap U_j -> U_j cap U_i``, read on coordinates."""
            source_index = int(source_index)
            target_index = int(target_index)
            assert source_index != target_index, (
                f"there is no chart change from the standard chart {source_index} of {self} to itself: a "
                "chart change joins two distinct standard charts"
            )
            dimension = int(self.relative_dimension())
            source_overlap = self.standard_chart_overlap(source_index, target_index)
            target_overlap = self.standard_chart_overlap(target_index, source_index)
            target_chart = self.standard_affine_chart(target_index)
            restriction = source_overlap.inclusion().coordinate_algebra_morphism()
            inverse_ratio = restriction(
                self._standard_chart_coordinate(source_index, target_index)
            ).inverse_of_unit()
            images = {
                self._standard_chart_coordinate_name(target_index, numerator): (
                    inverse_ratio
                    if numerator == source_index
                    else restriction(
                        self._standard_chart_coordinate(source_index, numerator)
                    )
                    * inverse_ratio
                )
                for numerator in range(dimension + 1)
                if numerator != target_index
            }
            # The overlap algebra is a localization, not a symmetric algebra:
            # the map is an arrow of commutative R-algebras, fixed by the
            # images of the free generators of the chart.
            into_target_chart = _scheme_mor_category(source_overlap, target_chart)(
                Algebras(self.scheme_base_ring())
                .Associative()
                .Unital()
                .Commutative()
                .Mor(
                    target_chart.coordinate_algebra(),
                    source_overlap.coordinate_algebra(),
                )(images)
            )
            return target_overlap.corestriction(into_target_chart)

        def standard_chart_transition(self, source_index, target_index):
            r"""``phi_{ji}: U_i cap U_j -> U_j cap U_i``, the chart change and its inverse.

            On coordinates ``x_k/x_j = (x_k/x_i)(x_j/x_i)^{-1}`` and
            ``x_i/x_j = (x_j/x_i)^{-1}``, defined because ``x_j/x_i`` is
            invertible on the overlap (Stacks, Tag 01MM).
            """
            return _scheme_isomorphism(
                self._standard_chart_change(source_index, target_index),
                self._standard_chart_change(target_index, source_index),
            )

        @cached_method
        def O(self, degree):
            r"""Return the standard invertible sheaf ``O(d)`` on this projective space, for any integer ``d``.

            Its global sections are the degree-``d`` piece ``S_d`` of
            ``S = R[x_0..x_n]``, a free ``R``-module framed by the degree-``d``
            monomials, and zero for ``d < 0`` (Hartshorne, Proposition II.5.13).
            """
            from sage_extensions.categories.divisors.invertible_sheaves import (
                _projective_o,
            )

            return _projective_o(self, degree)

        def coordinate_hyperplane_section_restriction(self, degree, coordinate_index):
            r"""Restrict ``O(degree)`` sections to the selected coordinate hyperplane."""
            from sage_extensions.categories.divisors.linear_systems import (
                _coordinate_hyperplane_section_restriction,
            )

            return _coordinate_hyperplane_section_restriction(
                self, degree, coordinate_index
            )

        def coordinate_point_jet_evaluation(self, degree, coordinate_index, jet_order):
            r"""Evaluate ``O(degree)`` jets at the selected coordinate point."""
            from sage_extensions.categories.divisors.linear_systems import (
                _coordinate_point_jet_evaluation,
            )

            return _coordinate_point_jet_evaluation(
                self, degree, coordinate_index, jet_order
            )

        def sections_vanishing_to_order(
            self, degree, coordinate_index, vanishing_order
        ):
            r"""Return ``O(degree)`` sections vanishing to the stated order."""
            return self.coordinate_point_jet_evaluation(
                degree, coordinate_index, vanishing_order
            ).kernel()

        def imposed_multiplicity_linear_system(
            self, degree, coordinate_index, vanishing_order
        ):
            r"""Projectivize sections satisfying a coordinate-point multiplicity condition."""
            from sage_extensions.categories.divisors.linear_systems import (
                _coordinate_imposed_multiplicity_linear_system,
            )

            return _coordinate_imposed_multiplicity_linear_system(
                self, degree, coordinate_index, vanishing_order
            )

        @cached_method
        def _canonical_line_bundle(self):
            r"""Compute ``omega_{P^n_R} = O(-n-1)`` for the smooth-owner operation."""
            return self.O(-int(self.relative_dimension()) - 1)

        @cached_method
        def structure_sheaf(self):
            r"""``O_X`` on ``Open(|P^n_R|)``, glued from the standard affine charts ``D_+(x_i)``.

            Its global sections are ``Gamma(P^n_R, O) = S_0 = R`` for
            ``S = R[x_0..x_n]`` (Hartshorne, Proposition II.5.13).
            """
            from sage_extensions.categories.schemes.gluing import (
                _finite_atlas_structure_sheaf,
            )

            atlas = self.standard_affine_atlas()
            restrictions = indexed_family(
                atlas.chart_index_set(),
                lambda index: (
                    atlas.chart(index).coordinate_algebra().algebra_structure_morphism()
                ),
                name="Projective global-function restrictions",
            )
            return _finite_atlas_structure_sheaf(
                atlas, self.scheme_base_ring(), restrictions
            )

        @cached_method
        def standard_affine_atlas(self):
            r"""Return the verified standard affine atlas on this exact projective space."""
            from sage_extensions.categories.schemes.gluing import (
                FiniteAffineAtlases,
            )

            indices = tuple(range(int(self.relative_dimension()) + 1))
            return FiniteAffineAtlases(self)(
                tuple(self.standard_affine_chart(index) for index in indices),
                tuple(
                    self.standard_chart_transition(left, right)
                    for left, right in combinations(indices, 2)
                ),
                tuple(self.standard_affine_chart_embedding(index) for index in indices),
            )

        def glued_from_standard_charts(self):
            r"""``P^n_R`` presented as the gluing of its standard affine charts.

            The atlas verifies the inverse and triple-cocycle conditions on the
            overlaps, so this is the scheme those charts and transitions
            determine (Stacks, Tag 01JA), as opposed to the realized space this
            method is called on.
            """
            indices = range(int(self.relative_dimension()) + 1)
            return Schemes(self.scheme_base_ring()).glue_affine_atlas(
                tuple(self.standard_affine_chart(index) for index in indices),
                tuple(
                    self.standard_chart_transition(left, right)
                    for left, right in combinations(indices, 2)
                ),
            )

        def _zeta_function(self):
            r"""Return ``Z(P^d/F_q, T) = prod_{i=0}^d (1 - q^i T)^{-1}``."""
            base = self.scheme_base_ring()
            rational_functions, T = _rational_functions_in_T()
            q = int(base.cardinality().finite_value())
            d = int(self.relative_dimension())
            result = rational_functions.one()
            for i in range(d + 1):
                result *= rational_functions.one() / (
                    rational_functions.one() - q**i * T
                )
            return result


def _standard_projective_chart_embedding(projective, chart_index):
    r"""Return the standard open-chart morphism ``U_i -> P^n``.

    The affine chart has coordinates ``x_k/x_i``; its map to projective space
    is the homogeneous family with coordinate ``i`` equal to one and every
    other coordinate the corresponding ratio.
    """
    chart_index = int(chart_index)
    chart = projective.standard_affine_chart(chart_index)
    algebra = chart.coordinate_algebra()
    coordinates = tuple(
        algebra.one()
        if numerator == chart_index
        else projective._standard_chart_coordinate(chart_index, numerator)
        for numerator in range(int(projective.relative_dimension()) + 1)
    )
    return _StandardProjectiveChartEmbedding(
        _scheme_mor_category(chart, projective),
        coordinates,
    )


# ---------------------------------------------------------------------------
# Products.
# ---------------------------------------------------------------------------


class ProductSchemes(OwnedCategoryOverBaseRing):
    r"""Products ``prod_{i in I} X_i`` of schemes, with their indexed factors and projections.

    The level data are the indexed family of factors and, over the same index
    set, the defining datum of each projection in ``Mor(X, X_i)``; the
    projection arrows are built from those data once the product exists.
    """

    def an_object(self):
        r"""The affine plane as a product of two affine lines."""
        line = AffineSpaces(self.base_ring())(1)
        return _scheme_product(line, line)

    def _repr_object_names(self):
        return f"scheme products over {self.base_ring()}"

    def super_categories(self):
        return [Schemes(self.base_ring())]

    class ParentMethods:
        def __init__(self, factors, projection_data, **rest) -> None:
            self._product_factors = factors
            self._projection_data = projection_data
            super().__init__(**rest)

        def factors(self):
            r"""Return the exact indexed family whose product this is."""
            return self._product_factors

        def number_of_factors(self):
            return self.factors().cardinality()

        @cached_method
        def projection(self, index):
            r"""Return the projection to the factor at ``index``."""
            return _scheme_mor_category(self, self.factors()[index])(
                self._projection_data[index]
            )

        @cached_method
        def projections(self):
            r"""Return the projections, indexed by the same set as :meth:`factors`."""
            return indexed_family(
                self.factors().index_set(),
                self.projection,
                name="Scheme product projections",
            )

        def projection_label(self, projection):
            r"""Return the factor label selected by one of this product's projections."""
            assert projection.domain() is self, (
                f"{projection} is not a projection of the product {self}: its domain is "
                f"{projection.domain()}"
            )
            label = next(
                (
                    label
                    for label in self.factors().index_set()
                    if projection is self.projection(label)
                ),
                None,
            )
            assert label is not None, (
                f"{projection} is not a projection of the product {self}: it is not the projection onto "
                "any factor"
            )
            return label

        def from_product_cone(self, legs):
            r"""Return the unique represented map into this product.

            The cone carries the index set of the factor family.  An affine
            product factors through the coordinate-algebra coproduct; a product
            of projective spaces concatenates the homogeneous coordinates of
            its legs on Sage's multiprojective realization.  A glued mixed
            product has its projections but no represented map into it.
            """
            factors = self.factors()
            factor_indices = factors.index_set()
            factor_labels = tuple(factor_indices)
            legs = _finite_factor_family(legs, name="Product cone legs")
            assert legs.index_set().cardinality() == factor_indices.cardinality(), (
                f"cannot form the map into the product {self} from the cone {legs}: the product has "
                f"{factor_indices.cardinality()} factors, but the cone has {legs.index_set().cardinality()} legs"
            )
            source = legs[factor_labels[0]].domain()
            assert all(legs[label].domain() is source for label in factor_labels), (
                f"cannot form the map into the product {self} from the cone {legs}: its legs do not all "
                f"start at one scheme (the first starts at {source})"
            )
            assert all(
                legs[label].codomain() is factors[label] for label in factor_labels
            ), (
                f"cannot form the map into the product {self} from the cone {legs}: each leg must land in "
                f"its factor, and the leg at "
                f"{next(label for label in factor_labels if legs[label].codomain() is not factors[label])} "
                "does not"
            )

            base = self.scheme_base_ring()
            match self:
                case _ if self in Schemes(base).Affine():
                    assert source in Schemes(base).Affine(), (
                        f"cannot form the map into the affine product {self} from the cone {legs}: its common "
                        f"domain {source} must be an affine scheme over {base}, but it is an object of "
                        f"{source.category()}"
                    )
                    product_algebra = self.coordinate_algebra()
                    images = {}
                    for factor_label in factor_labels:
                        leg = legs[factor_label]
                        factor_algebra = factors[factor_label].coordinate_algebra()
                        if factor_algebra is base:
                            assert leg == source.structure_morphism(), (
                                f"cannot form the map into the product {self} from the cone {legs}: the leg {leg} to the "
                                f"base scheme must be the structure morphism of {source}"
                            )
                            continue
                        projection_pullback = self.projection(
                            factor_label
                        ).coordinate_algebra_morphism()
                        leg_pullback = leg.coordinate_algebra_morphism()
                        for generator_label in factor_algebra.algebra_generating_set():
                            generator = factor_algebra.algebra_generator(
                                generator_label
                            )
                            images[
                                _algebra_generator_label(
                                    product_algebra, projection_pullback(generator)
                                )
                            ] = leg_pullback(generator)
                    pullback = (
                        source.structure_morphism().coordinate_algebra_morphism()
                        if product_algebra is base
                        else product_algebra.Mor(source.coordinate_algebra())(images)
                    )
                    cone = _affine_morphism_from_pullback(source, self, pullback)
                case _ if self in ProductProjectiveSpaces(base):
                    coordinate_legs = tuple(
                        _projective_coordinate_morphism(legs[label])
                        for label in factor_labels
                    )
                    coefficients = coordinate_legs[0].coefficient_map()
                    assert all(
                        _ring_morphisms_equal(coefficients, leg.coefficient_map())
                        is True
                        for leg in coordinate_legs
                    ), (
                        f"cannot form the map into the product of projective spaces {self} from the cone {legs}: "
                        f"the legs must all use the same map {coefficients} on coefficients, and they do not"
                    )
                    coordinates = tuple(
                        value
                        for leg in coordinate_legs
                        for value in leg.homogeneous_coordinates()
                    )
                    cone = _ProjectiveCoordinateMorphism(
                        LocallyRingedSpaces().Mor(source, self),
                        coordinates,
                        coefficient_map=coefficients,
                    )
                case _:
                    assert False, (
                        f"cannot form the map into the product {self} from the cone {legs}: maps into a product "
                        f"glued from affine charts are not computed here; {self} is an object of {self.category()}"
                    )

            cone = SchemeConeMorphismConstruction(
                self,
                legs,
                (self.projection(index) for index in factors.index_set()),
            ).image_of(cone)
            assert all(
                self.projection(label) * cone == legs[label] for label in factor_labels
            ), (
                f"the map {cone} into the product {self} is wrong: its composites with the projections "
                f"are not the legs {legs}"
            )
            return cone


def _projective_projection_rule(offset, width, scalar_map=None):
    r"""The arrow realization rule for the projection of a multiprojective space to one factor.

    The projection sends a point to the block of homogeneous coordinates
    ``x_offset, ..., x_{offset + width - 1}``; it is realized on Sage's
    multiprojective space by those coordinates.
    """

    def realize(mor):
        source = mor.domain()
        ambient, _ = _engine_projective_ambient(_engine_scheme(source))
        ring = _engine_polynomial_algebra(
            ambient.coordinate_ring(), source.scheme_base_ring()
        )
        coordinates = tuple(
            _owned_engine_element(ring, value)
            for value in ambient.coordinate_ring().gens()[offset : offset + width]
        )
        coefficient_map = None
        if scalar_map is not None:
            structure = _restriction_to_base(ring, scalar_map.codomain())
            coefficient_map = (
                OwnedRings()
                .Mor(scalar_map.domain(), ring)
                .elementwise(lambda value: structure(scalar_map(value)))
            )
        return _ProjectiveCoordinateMorphism(
            mor, coordinates, coefficient_map=coefficient_map
        )

    return realize


class ProductProjectiveSpaces(OwnedCategoryOverBaseRing):
    r"""Finite products of projective spaces over one base ring, on Sage's multiprojective realization."""

    def an_object(self):
        r"""The product of two projective lines."""
        line = ProjectiveSpaces(self.base_ring())(1)
        return _scheme_product(line, line)

    def _repr_object_names(self):
        return f"products of projective spaces over {self.base_ring()}"

    def super_categories(self):
        return [
            ProductSchemes(self.base_ring()),
            Schemes(self.base_ring()).Projective().Smooth(),
        ]

    class ParentMethods:
        def c2_diagonal_sign_action(self, group=None):
            r"""Return the diagonal sign action on every projective-line factor."""
            from sage_extensions.categories.divisors.linearizations import (
                _c2_diagonal_product_projective_action,
            )

            return _c2_diagonal_product_projective_action(self, group)

        @cached_method
        def _standard_affine_cover_charts_and_embeddings(self):
            r"""The charts and open immersions of the standard multiprojective cover."""
            factors = self.factors()
            factor_indices = factors.index_set()
            factor_labels = tuple(factor_indices)
            positions = {
                label: position for position, label in enumerate(factor_labels)
            }
            choices = tuple(
                cartesian_product(
                    *(
                        range(int(factors[label].relative_dimension()) + 1)
                        for label in factor_labels
                    )
                )
            )
            charts = {}
            embeddings = {}
            for choice in choices:
                chart = _scheme_product(
                    indexed_family(
                        factor_indices,
                        lambda label, choice=choice: factors[
                            label
                        ].standard_affine_chart(choice[positions[label]]),
                        name="Standard affine factors of a multiprojective chart",
                    )
                )
                charts[choice] = chart
                chart_algebra = chart.coordinate_algebra()
                engine_coordinates = []
                for label in factor_labels:
                    factor = factors[label]
                    selected = choice[positions[label]]
                    pullback = chart.projection(label).coordinate_algebra_morphism()
                    engine_coordinates.extend(
                        _engine_element(
                            chart_algebra,
                            chart_algebra.one()
                            if coordinate == selected
                            else pullback(
                                factor._standard_chart_coordinate(selected, coordinate)
                            ),
                        )
                        for coordinate in range(int(factor.relative_dimension()) + 1)
                    )
                embeddings[choice] = _StandardMultiprojectiveChartEmbedding(
                    _native_scheme_mor(chart, self)(engine_coordinates, check=False),
                    mor=_scheme_mor_category(chart, self),
                )

            return choices, charts, embeddings

        @cached_method
        def standard_affine_atlas(self):
            r"""Return the product of the factors' standard affine atlases."""
            from sage_extensions.categories.schemes.gluing import (
                FiniteAffineAtlases,
            )

            factors = self.factors()
            factor_indices = factors.index_set()
            factor_labels = tuple(factor_indices)
            positions = {
                label: position for position, label in enumerate(factor_labels)
            }
            choices, charts, embeddings = (
                self._standard_affine_cover_charts_and_embeddings()
            )

            @cached_function
            def overlap(source_choice, target_choice):
                chart = charts[source_choice]
                element = chart.coordinate_algebra().one()
                for label in factor_labels:
                    source_index = source_choice[positions[label]]
                    target_index = target_choice[positions[label]]
                    if source_index != target_index:
                        pullback = chart.projection(label).coordinate_algebra_morphism()
                        element *= pullback(
                            factors[label]._standard_chart_coordinate(
                                source_index, target_index
                            )
                        )
                return chart.distinguished_open(element)

            def transition(source_choice, target_choice):
                source_chart = charts[source_choice]
                inclusion = overlap(source_choice, target_choice).inclusion()

                def leg(label):
                    factor = factors[label]
                    source_index = source_choice[positions[label]]
                    target_index = target_choice[positions[label]]
                    local_projection = source_chart.projection(label) * inclusion
                    if source_index == target_index:
                        return local_projection
                    into_factor_overlap = factor.standard_chart_overlap(
                        source_index, target_index
                    ).corestriction(local_projection)
                    changed = (
                        factor._standard_chart_change(source_index, target_index)
                        * into_factor_overlap
                    )
                    return (
                        factor.standard_chart_overlap(
                            target_index, source_index
                        ).inclusion()
                        * changed
                    )

                into_target = charts[target_choice].from_product_cone(
                    indexed_family(
                        factor_indices,
                        leg,
                        name="Coordinatewise multiprojective chart transition legs",
                    )
                )
                return overlap(target_choice, source_choice).corestriction(into_target)

            transitions = {
                (left, right): _scheme_isomorphism(
                    transition(left, right), transition(right, left)
                )
                for left, right in combinations(choices, 2)
            }
            return FiniteAffineAtlases(self)(
                charts,
                transitions,
                embeddings,
            )

        def O(self, *degrees):
            r"""Return ``O(d_1, ..., d_r)`` on this product of projective spaces."""
            from sage_extensions.categories.divisors.invertible_sheaves import (
                _product_projective_o,
            )

            return _product_projective_o(self, _family_ingress(degrees))

        @cached_method
        def _canonical_line_bundle(self):
            return self.O(
                *(-int(factor.relative_dimension()) - 1 for factor in self.factors())
            )


def _scheme_product_cache_key(factors):
    return (
        id(factors.index_set()),
        tuple(id(factor) for factor in factors),
    )


@cached_function(key=_scheme_product_cache_key)
def _selected_scheme_product(factors):
    r"""Return the selected ordinary product of one finite indexed scheme family."""
    return _scheme_product(factors)


def _scheme_product(*schemes, placements=(), **level_data):
    r"""Return the categorical product in the supported scheme regimes.

    The defining datum is an indexed family.  Positional arguments and one
    sequence are syntactic ingress for the family on the canonical finite
    ordinal; an explicit :class:`IndexedFamily` keeps its exact index set, so
    repeated factors still have distinct roles.

    Affine spaces use ``A^m x A^n = A^{m+n}``; affine factors use the
    coproduct of their coordinate algebras; projective spaces use Sage's
    multiprojective realization; finite mixtures of affine schemes and
    projective spaces are glued from products of their affine charts.  Every
    route constructs the product with its indexed factors and the data of its
    projections.
    """
    factors = _finite_factor_family(_family_ingress(schemes), name="Product factors")
    index_set = factors.index_set()
    assert index_set.cardinality() >= 2, (
        f"cannot form the product of {factors} by this construction: it needs at least two "
        f"factors, but {index_set.cardinality()} were given"
    )
    scheme_values = tuple(factors[label] for label in index_set)
    base = scheme_values[0].scheme_base_ring()
    assert all(
        scheme in Schemes(base) and scheme.scheme_base_ring() is base
        for scheme in scheme_values
    ), (
        f"cannot form the product of {factors}: every factor must be a scheme over the base ring "
        f"{base} of the first factor, and "
        f"{next(scheme for scheme in scheme_values if not (scheme in Schemes(base) and scheme.scheme_base_ring() is base))} "
        "is not"
    )
    rank = index_set.ranking_map()

    def projection_family(values):
        r"""The projection data, indexed by the factor index set in its order."""
        return indexed_family(
            index_set,
            lambda label: values[int(rank(label))],
            name="Scheme product projection data",
        )

    match scheme_values:
        case _ if all(scheme in AffineSpaces(base) for scheme in scheme_values):
            dimensions = tuple(
                int(scheme.relative_dimension()) for scheme in scheme_values
            )
            names = tuple(
                f"x{factor}_{coordinate}"
                for factor, dimension in enumerate(dimensions)
                for coordinate in range(dimension)
            )
            coordinates = _affine_space_coordinates(base, sum(dimensions), names)
            product_algebra = coordinates[1]
            product_labels = tuple(product_algebra.algebra_generating_set())
            pullbacks = []
            offset = 0
            for factor, dimension in zip(scheme_values, dimensions, strict=True):
                factor_algebra = factor.coordinate_algebra()
                pullbacks.append(
                    factor_algebra.Mor(product_algebra)(
                        {
                            label: product_algebra.algebra_generator(
                                product_labels[offset + position]
                            )
                            for position, label in enumerate(
                                factor_algebra.algebra_generating_set()
                            )
                        }
                    )
                )
                offset += dimension
            return _affine_space(
                base,
                coordinates,
                (ProductSchemes(base), *placements),
                factors=factors,
                projection_data=projection_family(pullbacks),
                **level_data,
            )
        case _ if all(scheme in ProjectiveSpaces(base) for scheme in scheme_values):
            widths = tuple(
                int(scheme.relative_dimension()) + 1 for scheme in scheme_values
            )
            dimension = sum(width - 1 for width in widths)
            projective_surface_placement = ()
            if base in OwnedFields() and dimension == 2:
                from sage_extensions.categories.schemes.varieties import Surfaces

                projective_surface_placement = (Surfaces(base).Projective(),)
            names = tuple(
                f"x{factor}_{coordinate}"
                for factor, width in enumerate(widths)
                for coordinate in range(width)
            )
            engine = _SageProductProjectiveSpaces(
                [width - 1 for width in widths],
                _engine_ring(base),
                names=names,
            )
            offsets = tuple(sum(widths[:position]) for position in range(len(widths)))
            return _object_of(
                owned_category_join(
                    (
                        ProductProjectiveSpaces(base),
                        *_space_placements(base, dimension),
                        *projective_surface_placement,
                        *placements,
                    )
                ),
                scheme_base_ring=base,
                scheme_engine=engine,
                factors=factors,
                projection_data=projection_family(
                    tuple(
                        _projective_projection_rule(offset, width)
                        for offset, width in zip(offsets, widths, strict=True)
                    )
                ),
                **level_data,
            )
        case _ if all(scheme in Schemes(base).Affine() for scheme in scheme_values):
            return _affine_scheme_product(
                factors, scheme_values, base, projection_family, placements, level_data
            )
        case _ if all(
            scheme in Schemes(base).Affine() or scheme in ProjectiveSpaces(base)
            for scheme in scheme_values
        ):
            return _mixed_affine_projective_product(
                factors, base, placements, level_data
            )
        case _:
            assert False, (
                f"cannot form the product of {factors}: products are computed here only for affine "
                f"schemes, projective spaces over {base}, and finite products mixing the two"
            )


def _affine_scheme_product(
    factors, scheme_values, base, projection_family, placements, level_data
):
    r"""``Spec(A_1 tensor_R ... tensor_R A_n)`` with the coproduct injections as projection pullbacks.

    ``Spec R`` is terminal in ``Sch/R``: a terminal factor contributes nothing
    to the coordinate algebra and its projection is the structure morphism,
    whose pullback is the algebra structure morphism.
    """
    base_scheme = Schemes(base).base_scheme()
    nonterminal_positions = tuple(
        position
        for position, scheme in enumerate(scheme_values)
        if scheme is not base_scheme
    )
    commutative_algebras = Algebras(base).Associative().Unital().Commutative()
    match len(nonterminal_positions):
        case 0:
            algebra = base
            maps = []
        case 1:
            algebra = scheme_values[nonterminal_positions[0]].coordinate_algebra()
            maps = [algebra.Mor(algebra).identity()]
        case _:
            algebras = tuple(
                scheme_values[position].coordinate_algebra()
                for position in nonterminal_positions
            )
            algebra = commutative_algebras.coproduct((algebras[0], algebras[1]))
            maps = list(algebra.coproduct_injections())
            for next_algebra in algebras[2:]:
                extended = commutative_algebras.coproduct((algebra, next_algebra))
                left_map, right_map = extended.coproduct_injections()
                maps = [left_map * factor_map for factor_map in maps] + [right_map]
                algebra = extended
    injection_at = dict(zip(nonterminal_positions, maps, strict=True))
    structure_pullback = (
        base.Mor(base).identity()
        if algebra is base
        else algebra.algebra_structure_morphism()
    )
    pullbacks = tuple(
        injection_at[position] if position in injection_at else structure_pullback
        for position in range(len(scheme_values))
    )
    return _affine_scheme(
        algebra,
        base,
        (ProductSchemes(base), *placements),
        factors=factors,
        projection_data=projection_family(pullbacks),
        **level_data,
    )


def _mixed_affine_projective_product(factors, base, placements, level_data):
    r"""Glue a finite product containing affine and projective factors.

    For each projective factor choose one standard affine chart.  The product
    of those charts with all affine factors is affine.  Two such product charts
    overlap where every changed homogeneous coordinate ratio is a unit, hence
    on one distinguished open, the product of those ratios.  Coordinatewise
    projective chart changes and identities on the affine factors give the
    finite gluing.  The local factor projections agree on overlaps, so they
    glue to the categorical projections, which are constructed from those
    local maps as the product is glued.
    """
    factors = _finite_factor_family(factors, name="Product factors")
    schemes = tuple(factors)
    projective_positions = tuple(
        position
        for position, scheme in enumerate(schemes)
        if scheme in ProjectiveSpaces(base)
    )
    chart_labels = tuple(
        cartesian_product(
            *(
                range(int(schemes[position].relative_dimension()) + 1)
                for position in projective_positions
            )
        )
    )
    projective_slot = {
        position: slot for slot, position in enumerate(projective_positions)
    }
    charts = {
        label: _scheme_product(
            tuple(
                scheme.standard_affine_chart(label[projective_slot[position]])
                if position in projective_slot
                else scheme
                for position, scheme in enumerate(schemes)
            )
        )
        for label in chart_labels
    }

    @cached_function
    def overlap(source_label, target_label):
        chart = charts[source_label]
        element = chart.coordinate_algebra().one()
        for position in projective_positions:
            slot = projective_slot[position]
            if source_label[slot] != target_label[slot]:
                pullback = chart.projection(position).coordinate_algebra_morphism()
                element *= pullback(
                    schemes[position]._standard_chart_coordinate(
                        source_label[slot], target_label[slot]
                    )
                )
        return chart.distinguished_open(element)

    def transition(source_label, target_label):
        source_chart = charts[source_label]
        inclusion = overlap(source_label, target_label).inclusion()
        legs = []
        for position, scheme in enumerate(schemes):
            local_projection = source_chart.projection(position) * inclusion
            if (
                position not in projective_slot
                or source_label[projective_slot[position]]
                == target_label[projective_slot[position]]
            ):
                legs.append(local_projection)
                continue
            source_index = source_label[projective_slot[position]]
            target_index = target_label[projective_slot[position]]
            into_factor_overlap = scheme.standard_chart_overlap(
                source_index, target_index
            ).corestriction(local_projection)
            changed = (
                scheme._standard_chart_change(source_index, target_index)
                * into_factor_overlap
            )
            legs.append(
                scheme.standard_chart_overlap(target_index, source_index).inclusion()
                * changed
            )
        into_target_chart = charts[target_label].from_product_cone(tuple(legs))
        return overlap(target_label, source_label).corestriction(into_target_chart)

    transitions = tuple(
        _scheme_isomorphism(transition(left, right), transition(right, left))
        for left, right in combinations(chart_labels, 2)
    )
    # The projection to a factor is given chartwise, in the order of the charts
    # of the gluing; on a chart the local projection lands in the factor, or in
    # its standard chart followed by that chart's embedding.
    local_projection_families = tuple(
        tuple(
            _standard_projective_chart_embedding(
                factor, label[projective_slot[position]]
            )
            * charts[label].projection(position)
            if position in projective_slot
            else charts[label].projection(position)
            for label in chart_labels
        )
        for position, factor in enumerate(schemes)
    )

    schemes_over_base = Schemes(base)
    placements = [ProductSchemes(base), *placements]
    placements.extend(
        placement
        for placement in (
            schemes_over_base.Separated(),
            schemes_over_base.FiniteType(),
            schemes_over_base.Smooth(),
        )
        if all(factor in placement for factor in schemes)
    )
    # A finite-type affine scheme is quasi-projective and projective spaces are
    # projective, so the product of those is quasi-projective.
    if all(
        factor in schemes_over_base.QuasiProjective()
        or (
            factor in schemes_over_base.Affine()
            and factor in schemes_over_base.FiniteType()
        )
        for factor in schemes
    ):
        placements.append(schemes_over_base.QuasiProjective())
    # For products of the standard spaces the charts are polynomial rings over
    # the base, so integral and normal placements are read from the base.
    if all(
        factor in AffineSpaces(base) or factor in ProjectiveSpaces(base)
        for factor in schemes
    ):
        placements.extend(
            _space_placements(
                base,
                sum(int(factor.relative_dimension()) for factor in schemes),
            )
        )
        # An affine zero-space is Spec(R), the terminal factor over the base.
        # Its presence does not destroy projectivity of the other factors.
        if all(
            factor in ProjectiveSpaces(base)
            or (factor in AffineSpaces(base) and int(factor.relative_dimension()) == 0)
            for factor in schemes
        ):
            placements.append(schemes_over_base.Projective())
            dimension = sum(int(factor.relative_dimension()) for factor in schemes)
            if base in OwnedFields() and dimension == 2:
                from sage_extensions.categories.schemes.varieties import Surfaces

                placements.append(Surfaces(base).Projective())
    return schemes_over_base.glue_affine_atlas(
        tuple(charts[label] for label in chart_labels),
        transitions,
        placements=tuple(placements),
        factors=factors,
        projection_data=indexed_family(
            factors.index_set(),
            lambda label: local_projection_families[
                int(factors.index_set().ranking_map()(label))
            ],
            name="Glued product projection data",
        ),
        **level_data,
    )


# ---------------------------------------------------------------------------
# Fibre products.
# ---------------------------------------------------------------------------


class SchemeFiberProductConstruction:
    r"""The selected cospan, projection data, and universal factorization of one pullback.

    ``X x_S Y`` is the limit of the cospan ``X -> S <- Y``.  The construction
    retains the cospan, the defining data of the two projections in
    ``Mor(X x_S Y, X)`` and ``Mor(X x_S Y, Y)``, and the realization of the
    universal factorization: the coordinate-algebra pushout, a factorization
    of pushout cocones, or a factorization of scheme cones.
    """

    def __init__(
        self,
        cospan,
        projection_data,
        *,
        algebra_pushout=None,
        scheme_factorization=None,
        cocone_factorization=None,
    ) -> None:
        left_leg, right_leg = cospan
        assert left_leg.codomain() is right_leg.codomain(), (
            f"{left_leg} and {right_leg} do not form a cospan: their codomains "
            f"{left_leg.codomain()} and {right_leg.codomain()} differ"
        )
        self._cospan = (left_leg, right_leg)
        self._projection_data = tuple(projection_data)
        assert len(self._projection_data) == 2, (
            f"a fibre product of {left_leg} and {right_leg} has two projections, but "
            f"{len(self._projection_data)} were given"
        )
        self._algebra_pushout = algebra_pushout
        self._scheme_factorization = scheme_factorization
        self._cocone_factorization = cocone_factorization

    def cospan(self):
        return self._cospan

    def projection_data(self):
        return self._projection_data

    def algebra_pushout(self):
        return self._algebra_pushout

    def scheme_factorization(self):
        return self._scheme_factorization

    def cocone_factorization(self):
        return self._cocone_factorization


class FiberProductSchemes(OwnedCategoryOverBaseRing):
    r"""Schemes constructed as the selected pullback of one cospan.

    The level datum is the :class:`SchemeFiberProductConstruction`.
    """

    def an_object(self):
        r"""``A^1 x_{Spec R} A^1``, the affine plane as a fiber product."""
        line = AffineSpaces(self.base_ring())(1)
        return _scheme_fiber_product(
            line.structure_morphism(), line.structure_morphism()
        )

    def _repr_object_names(self):
        return f"fiber products of schemes over {self.base_ring()}"

    def super_categories(self):
        return [Schemes(self.base_ring())]

    class ParentMethods:
        def __init__(self, fiber_product_construction, **rest) -> None:
            self._fiber_product_construction = fiber_product_construction
            super().__init__(**rest)

        def fiber_product_construction(self):
            r"""Return the selected pullback construction defining this scheme."""
            return self._fiber_product_construction

        def fiber_product_cospan(self):
            return self.fiber_product_construction().cospan()

        def fiber_product_base(self):
            return self.fiber_product_cospan()[0].codomain()

        @cached_method
        def fiber_product_projections(self):
            r"""``(X x_S Y -> X, X x_S Y -> Y)``, built from their defining data."""
            left_leg, right_leg = self.fiber_product_cospan()
            left_datum, right_datum = (
                self.fiber_product_construction().projection_data()
            )
            relative = Schemes(self.scheme_base_ring())
            category = (
                relative
                if all(
                    leg.parent().mor_category().is_subcategory(relative)
                    for leg in (left_leg, right_leg)
                )
                else LocallyRingedSpaces()
            )
            return (
                category.Mor(self, left_leg.domain())(left_datum),
                category.Mor(self, right_leg.domain())(right_datum),
            )

        def left_projection(self):
            return self.fiber_product_projections()[0]

        def right_projection(self):
            return self.fiber_product_projections()[1]

        def from_pullback_cone(self, left_map, right_map):
            r"""Return the factorization of a cone through this pullback."""
            assert left_map.domain() is right_map.domain(), (
                f"{left_map} and {right_map} do not form a cone over the cospan of the fibre product "
                f"{self}: their domains {left_map.domain()} and {right_map.domain()} differ"
            )
            left_projection, right_projection = self.fiber_product_projections()
            assert left_map.codomain() is left_projection.codomain(), (
                f"cannot factor the cone ({left_map}, {right_map}) through the fibre product {self}: the "
                f"first map must land in {left_projection.codomain()}, but it lands in {left_map.codomain()}"
            )
            assert right_map.codomain() is right_projection.codomain(), (
                f"cannot factor the cone ({left_map}, {right_map}) through the fibre product {self}: the "
                f"second map must land in {right_projection.codomain()}, but it lands in "
                f"{right_map.codomain()}"
            )
            construction = self.fiber_product_construction()
            left_leg, right_leg = construction.cospan()
            assert left_leg * left_map == right_leg * right_map, (
                f"cannot factor the cone ({left_map}, {right_map}) through the fibre product {self}: its "
                f"two composites to {left_leg.codomain()} differ"
            )
            scheme_factorization = construction.scheme_factorization()
            cocone_factorization = construction.cocone_factorization()
            match construction:
                case _ if scheme_factorization is not None:
                    factorization = scheme_factorization(left_map, right_map)
                case _ if cocone_factorization is not None:
                    factorization = _affine_morphism_from_pullback(
                        left_map.domain(),
                        self,
                        cocone_factorization(
                            left_map.coordinate_algebra_morphism(),
                            right_map.coordinate_algebra_morphism(),
                        ),
                    )
                case _:
                    algebra_pushout = construction.algebra_pushout()
                    assert algebra_pushout is not None, (
                        f"cannot factor the cone ({left_map}, {right_map}) through the fibre product {self}: it "
                        "was built without a pushout of coordinate algebras or another universal factorization"
                    )
                    factorization = _affine_morphism_from_pullback(
                        left_map.domain(),
                        self,
                        algebra_pushout.from_pushout_cocone(
                            left_map.coordinate_algebra_morphism(),
                            right_map.coordinate_algebra_morphism(),
                        ),
                    )
            return SchemeConeMorphismConstruction(
                self,
                (left_map, right_map),
                (left_projection, right_projection),
            ).image_of(factorization)


def _structure_morphism_rule(mor):
    r"""The arrow realization rule for the structure morphism of the Mor's domain."""
    return mor(mor.domain().structure_morphism())


class _RelativeDeRhamCohomologySheafEngine:
    r"""``R^k f_*(Omega^*_{X/S})``, the ``k``-th hyperdirect image of the relative de Rham complex.

    The defining data are the arrow ``f: X -> S`` and the degree ``k``.  The
    sheaf is the one associated to the presheaf ``V |-> H^k(f^{-1}(V),
    Omega^*_{X/S})`` of hypercohomology groups (Katz, *Nilpotent connections
    and the monodromy theorem*, Publ. Math. IHES 39 (1970), (3.0)).
    """

    def __init__(self, family_morphism, degree, **rest) -> None:
        self._family_morphism = family_morphism
        self._degree = degree
        super().__init__(**rest)

    def family_morphism(self):
        r"""The arrow ``f: X -> S``."""
        return self._family_morphism

    def degree(self):
        r"""The cohomological degree ``k``."""
        return self._degree

    def ringed_space(self):
        return self.family_morphism().codomain()

    scheme = ringed_space

    def global_sections(self):
        r"""``H^k_dR(X/S)(S)``; for affine ``S`` it is the hypercohomology ``H^k(X, Omega^*_{X/S})``.

        For affine ``S``, ``R^k f_*`` of a complex of quasi-coherent sheaves
        has global sections the hypercohomology of the complex on ``X``
        (Hartshorne, *Algebraic Geometry*, III.8.5, for each sheaf of the
        complex).  This needs the relative de Rham complex of ``X`` over
        ``S`` and its Cech hypercohomology on an affine cover of ``X``.
        """
        assert False, (
            "global_sections on relative de Rham cohomology sheaves: not implemented"
        )

    def sheaf_category(self):
        r"""``QCoh(S)``, the category this sheaf is an object of."""
        return QuasiCoherentSheaves(self.scheme())

    def _repr_(self):
        f = self.family_morphism()
        return f"R^{self.degree()} f_*(Omega^*_(X/S)) for f: {f.domain()} -> {f.codomain()}"


@cached_function(
    key=lambda family, degree, categories: (id(family), degree, categories)
)
def _relative_de_rham_cohomology(family, degree, categories):
    r"""``H^k_dR(X/S) = R^k f_*(Omega^*_{X/S})`` in ``QCoh(S)`` joined with ``categories``.

    ``categories`` states a placement the caller's hypotheses establish: for
    a smooth proper ``f`` over a base of characteristic zero the sheaf is
    locally free of finite rank (Katz, *Nilpotent connections and the
    monodromy theorem*, Publ. Math. IHES 39 (1970), (3.0)).
    """
    return QuasiCoherentSheaves(family.codomain()).object(
        categories=categories,
        construction_data={"family_morphism": family, "degree": degree},
        _engine=_RelativeDeRhamCohomologySheafEngine,
    )


def _localization_base_change_pushout(left_pullback, right_pullback):
    r"""Realize ``B tensor_A S^{-1}A`` as ``B[phi(S)^{-1}]`` for the localization map ``rho: A -> S^{-1}A``.

    Let ``phi: A -> B`` be the other leg and ``lambda: B -> B[phi(S)^{-1}]``
    the localization map.  The map ``lambda phi`` sends ``S`` to units, so it
    induces ``phi': S^{-1}A -> B[phi(S)^{-1}]`` with ``phi' rho = lambda phi``,
    and ``(lambda, phi')`` is a cocone.  It is universal: for a cocone
    ``(u: B -> T, v: S^{-1}A -> T)``, ``u phi = v rho`` sends ``S`` to units,
    so ``u`` factors uniquely through ``lambda`` by the universal property of
    localization, and the factorization agrees with ``v`` on ``S^{-1}A``
    because both composites with ``rho`` are ``u phi`` and ``rho`` is an
    epimorphism of rings.  On spectra this is the preimage
    ``f^{-1}(D(s)) = D(f^# s)`` of a distinguished open (Hartshorne,
    *Algebraic Geometry*, II.3.3, step 3).  The localization leg is
    recognized as the localization map of its codomain by its values on the
    chosen algebra generators of ``A``, which determine a map out of ``A``.
    ``None`` states that the span is not of this shape.
    """
    base = left_pullback.domain()
    assert right_pullback.domain() is base, (
        f"cannot form the pushout of {left_pullback} and {right_pullback}: they must start at one "
        f"ring, but they start at {base} and {right_pullback.domain()}"
    )

    def is_localization_map(leg):
        localized = leg.codomain()
        match localized:
            case _ if (
                localized in LocalizationRings()
                and localized.localization_source() is base
                and base.is_framed_algebra()
            ):
                canonical = localized.localization_map()
                return all(
                    leg(generator) == canonical(generator)
                    for generator in base.finite_algebra_generators()
                )
            case _:
                return False

    def realize(other_pullback, localization_pullback, localization_on_right):
        if not is_localization_map(localization_pullback):
            return None
        other = other_pullback.codomain()
        localized = localization_pullback.codomain()
        scalars = other.base_ring()
        algebras = Algebras(scalars).Associative().Unital().Commutative()
        pushout = other.localization(
            *(other_pullback(element) for element in localized.inverted_elements())
        )
        other_to_pushout = algebras.Mor(other, pushout)(pushout.localization_map())
        localized_to_pushout = algebras.Mor(localized, pushout)(
            localized.induced_morphism(pushout.localization_map() * other_pullback)
        )
        maps = (
            (other_to_pushout, localized_to_pushout)
            if localization_on_right
            else (localized_to_pushout, other_to_pushout)
        )

        def factor(left_to_target, right_to_target):
            assert left_to_target.codomain() is right_to_target.codomain(), (
                f"cannot factor through the pushout {pushout}: the maps {left_to_target} and "
                f"{right_to_target} must land in one ring, but they land in {left_to_target.codomain()} "
                f"and {right_to_target.codomain()}"
            )
            other_to_target = (
                left_to_target if localization_on_right else right_to_target
            )
            return algebras.Mor(pushout, other_to_target.codomain())(
                pushout.induced_morphism(other_to_target)
            )

        return pushout, maps[0], maps[1], factor

    represented = realize(left_pullback, right_pullback, True)
    return (
        represented
        if represented is not None
        else realize(right_pullback, left_pullback, False)
    )


def _quotient_base_change_pushout(left_pullback, right_pullback):
    r"""Realize ``A tensor_T Q`` as ``A/IA`` for a surjection ``T -> Q`` with kernel ``I``.

    This is the affine algebra realization for base change along a quotient of
    the scalar ring, used when the general algebra pushout does not own the
    span because ``Q`` has no selected algebra framing.  Two surjections have a
    represented kernel: the quotient map ``T -> T/I``, and an ``R``-point
    ``e: T -> R`` of an ``R``-algebra ``T`` with finitely many chosen algebra
    generators ``t``.  The kernel of ``e`` is generated by the ``t - e(t)``:
    they lie in it, and ``T/(t - e(t))`` is generated as an ``R``-algebra by
    the images of the ``t``, which are scalars, so ``R -> T/(t - e(t))`` is
    surjective and ``e`` is its inverse.  Then ``A tensor_T T/I = A/IA``,
    since ``A tensor_T -`` is right exact on ``I -> T -> T/I -> 0``.  The
    presentation of ``A/IA`` supplies the pushout object, its two canonical
    maps, and the universal cocone factorization.  ``None`` states that the
    span is not of this shape.
    """
    base = left_pullback.domain()
    assert right_pullback.domain() is base, (
        f"cannot form the pushout of {left_pullback} and {right_pullback}: they must start at one "
        f"ring, but they start at {base} and {right_pullback.domain()}"
    )

    def kernel_generators(quotient_pullback):
        quotient = quotient_pullback.codomain()
        match quotient:
            case _ if (
                quotient in QuotientRings() and quotient.quotient_source() is base
            ):
                return tuple(quotient.defining_ideal().ideal_generators())
            case _ if quotient is base.base_ring() and base.is_framed_algebra():
                return tuple(
                    generator - base(quotient_pullback(generator))
                    for generator in base.finite_algebra_generators()
                )
            case _:
                return None

    def realize(other_pullback, quotient_pullback, quotient_on_right):
        other = other_pullback.codomain()
        quotient = quotient_pullback.codomain()
        kernel = kernel_generators(quotient_pullback)
        if kernel is None:
            return None
        if other not in AlgebrasWithChosenFinitePresentation(other.base_ring()):
            return None
        equations = tuple(other_pullback(generator) for generator in kernel)
        pushout, other_to_pushout = other._quotient_by_algebra_elements(equations)
        engine_quotient_to_pushout = _engine_ring(pushout).coerce_map_from(
            _engine_ring(quotient)
        )
        assert engine_quotient_to_pushout is not None, (
            f"cannot form the pushout {pushout} of {quotient} and {other}: Sage has no canonical map "
            f"from {quotient} to {pushout}"
        )
        quotient_to_pushout = quotient.Mor(pushout)._from_engine_morphism(
            engine_quotient_to_pushout
        )
        maps = (
            (other_to_pushout, quotient_to_pushout)
            if quotient_on_right
            else (quotient_to_pushout, other_to_pushout)
        )

        def factor(left_to_target, right_to_target):
            assert left_to_target.codomain() is right_to_target.codomain(), (
                f"cannot factor through the pushout {pushout}: the maps {left_to_target} and "
                f"{right_to_target} must land in one ring, but they land in {left_to_target.codomain()} "
                f"and {right_to_target.codomain()}"
            )
            other_to_target = left_to_target if quotient_on_right else right_to_target
            return pushout.Mor(other_to_target.codomain())(
                {
                    label: other_to_target(other.algebra_generator(label))
                    for label in pushout.algebra_generating_set()
                }
            )

        return pushout, maps[0], maps[1], factor

    represented = realize(left_pullback, right_pullback, True)
    return (
        represented
        if represented is not None
        else realize(right_pullback, left_pullback, False)
    )


def _projective_base_change_factorization(changed, projective_map, scalar_map):
    r"""The map to the changed projective presentation defined by both cone legs.

    The coordinate sections come from the map to the original presentation;
    coefficients act through the specified map to the changed scalar base.
    On a glued apex the construction is applied on its affine charts.
    """
    source = projective_map.domain()
    if source._is_glued_from_affine_atlas():
        datum = source.gluing_datum()
        return LocallyRingedSpaces().Mor(source, changed)(
            indexed_family(
                datum.chart_index_set(),
                lambda index: _projective_base_change_factorization(
                    changed,
                    projective_map * datum.chart_embedding(index),
                    scalar_map * datum.chart_embedding(index),
                ),
                name="Local projective base-change factorizations",
            )
        )
    coordinates = _projective_coordinate_morphism(projective_map)
    ring = coordinates.coefficient_map().codomain()
    if source in Schemes(source.scheme_base_ring()).Affine():
        coefficients = scalar_map.coordinate_algebra_morphism()
    else:
        assert scalar_map == source.structure_morphism(), (
            f"cannot form the map from {source} to the base change {changed}: {source} is not "
            f"affine, so its map to the new base must be its structure morphism, but it is {scalar_map}"
        )
        coefficients = _restriction_to_base(ring, changed.scheme_base_ring())
    return _ProjectiveCoordinateMorphism(
        LocallyRingedSpaces().Mor(source, changed),
        tuple(coordinates.homogeneous_coordinates()),
        coefficient_map=coefficients,
    )


def _projective_space_scalar_base_change(left_map, right_map):
    r"""Realize the pullback of ``P^n_R`` along ``Spec R' -> Spec R``.

    ``None`` states that the cospan is not this specialization.  The result is
    projective space over ``R'`` on the same coordinates, constructed as the
    fibre product with its projection to ``P^n_R``, its structure morphism to
    ``Spec R'``, and a factorization of cones.
    """
    base_scheme = left_map.codomain()
    if right_map.codomain() is not base_scheme:
        return None
    for projective_leg, scalar_leg, projective_on_left in (
        (left_map, right_map, True),
        (right_map, left_map, False),
    ):
        projective = projective_leg.domain()
        scalar_scheme = scalar_leg.domain()
        source_base = projective.scheme_base_ring()
        if (
            projective not in ProjectiveSpaces(source_base)
            or base_scheme is not projective.base_scheme()
            or projective_leg != projective.structure_morphism()
        ):
            continue
        if scalar_scheme is not scalar_scheme.base_scheme():
            continue
        target_base = scalar_scheme.scheme_base_ring()
        width = int(projective.relative_dimension()) + 1
        projective_projection = _projective_projection_rule(
            0, width, scalar_leg.coordinate_algebra_morphism()
        )
        projection_data = (
            (projective_projection, _structure_morphism_rule)
            if projective_on_left
            else (_structure_morphism_rule, projective_projection)
        )

        def factor(
            left_cone_map, right_cone_map, projective_on_left=projective_on_left
        ):
            projective_cone_map = (
                left_cone_map if projective_on_left else right_cone_map
            )
            scalar_cone_map = right_cone_map if projective_on_left else left_cone_map
            return _projective_base_change_factorization(
                changed, projective_cone_map, scalar_cone_map
            )

        changed = _projective_space(
            target_base,
            width - 1,
            projective.variable_names(),
            (FiberProductSchemes(target_base),),
            fiber_product_construction=SchemeFiberProductConstruction(
                (left_map, right_map),
                projection_data,
                scheme_factorization=factor,
            ),
        )
        # The projection retains the scalar leg, even for an endomorphism
        # of the same scalar ring; neither projective space is mutated.
        return changed
    return None


def _multiprojective_closed_fibre(left_map, right_map):
    r"""``X x_{P^m} Spec R`` for ``X <= P = prod P^{n_i}`` over the factor ``P^m`` and an ``R``-point.

    Let ``f = pr_j o i: X -> P^{n_j}`` with ``i: X -> P`` closed and
    ``a: Spec R -> P^{n_j}`` the point with coordinates ``a``.  Pasting
    pullbacks, ``X x_{P^{n_j}} Spec R = X x_P (P x_{P^{n_j}} Spec R)``, and
    ``P x_{P^{n_j}} Spec R = Q``, the product of the other factors, mapping
    to ``P`` by ``(id_Q, a)``.  So the fibre is ``V(F(x, a)) <= Q``, the
    closed subscheme cut out by the equations of ``X`` with the ``j``-th
    block set to ``a`` (Hartshorne, *Algebraic Geometry*, II.3, the fibre
    ``X_y``).  A cone ``(S -> X, S -> Spec R)`` factors through it by the
    other blocks of ``S -> X -> P``.  Returns ``None`` outside this regime.
    """
    for family, point, family_on_left in (
        (left_map, right_map, True),
        (right_map, left_map, False),
    ):
        source = family.domain()
        base = source.scheme_base_ring()
        coordinates = point._represented_point_coordinates()
        residue = point.domain()
        if (
            coordinates is None
            or residue is not residue.base_scheme()
            or source not in ClosedSubschemes(base)
        ):
            continue
        ambient = source.inclusion().codomain()
        if ambient not in ProductProjectiveSpaces(base):
            continue
        factors = ambient.factors()
        labels = tuple(factors.index_set())
        selected = next(
            (
                label
                for label in labels
                if factors[label] is family.codomain()
                and family == ambient.projection(label) * source.inclusion()
            ),
            None,
        )
        if selected is None:
            continue
        others = tuple(label for label in labels if label != selected)
        remaining = (
            factors[others[0]]
            if len(others) == 1
            else Schemes(base).product(tuple(factors[label] for label in others))
        )
        equations = tuple(source.defining_equations())
        ambient_ring = equations[0].parent()
        remaining_ring = _constant_sections_ring(remaining)
        remaining_variables = iter(
            tuple(
                remaining_ring.algebra_generator(name)
                for name in remaining_ring.algebra_generating_set()
            )
        )
        point_values = iter(tuple(coordinates))
        ambient_variables = iter(tuple(ambient_ring.algebra_generating_set()))
        images = {}
        for label in labels:
            for _ in range(int(factors[label].relative_dimension()) + 1):
                images[next(ambient_variables)] = (
                    remaining_ring(next(point_values))
                    if label == selected
                    else next(remaining_variables)
                )
        substitution = ambient_ring.Mor(remaining_ring)(images)

        def to_ambient(scheme, remaining_map, scalar_map):
            r"""``S -> P`` with the remaining blocks from ``S -> Q`` and the ``j``-th from ``a``."""
            legs = {label: point * scalar_map for label in (selected,)}
            match len(others):
                case 1:
                    legs[others[0]] = remaining_map
                case _:
                    for position, label in enumerate(others):
                        legs[label] = remaining.projection(position) * remaining_map
            return ambient.from_product_cone(
                indexed_family(
                    ambient.factors().index_set(),
                    lambda label: legs[label],
                    name=f"Map from {scheme} to {ambient}",
                )
            )

        def to_source(mor):
            fibre = mor.domain()
            return mor(
                source.corestriction(
                    to_ambient(fibre, fibre.inclusion(), fibre.structure_morphism())
                )
            )

        def factor(left_cone_map, right_cone_map, family_on_left=family_on_left):
            to_family = left_cone_map if family_on_left else right_cone_map
            through_ambient = source.inclusion() * to_family
            match len(others):
                case 1:
                    to_remaining = ambient.projection(others[0]) * through_ambient
                case _:
                    to_remaining = remaining.from_product_cone(
                        indexed_family(
                            remaining.factors().index_set(),
                            lambda position: (
                                ambient.projection(others[position]) * through_ambient
                            ),
                            name="Remaining blocks of a cone into a fibre",
                        )
                    )
            return fibre.corestriction(to_remaining)

        fibre = remaining.closed_subscheme(
            *(substitution(equation) for equation in equations),
            placements=(FiberProductSchemes(base),),
            fiber_product_construction=SchemeFiberProductConstruction(
                (left_map, right_map),
                (to_source, _structure_morphism_rule)
                if family_on_left
                else (_structure_morphism_rule, to_source),
                scheme_factorization=factor,
            ),
        )
        return fibre
    return None


def _projective_closed_affine_pullback(left_map, right_map):
    r"""Pull a projective closed immersion back to an affine scheme.

    The inverse image is cut out by the pulled homogeneous equations
    (Stacks, Definition 26.17.7 and Lemma 26.17.6). Its quotient algebra
    gives the universal factorization; both scheme projections are retained.

    Unexecuted conic chart pullback::

        sage: from dzack_research.preamble.all import *
        sage: P = ProjectiveSpaces(QQ)(2)
        sage: S = P.O(1).global_sections().homogeneous_coordinate_ring()
        sage: x0, x1, x2 = tuple(S.algebra_generators())
        sage: Z = P.closed_subscheme(x0*x2-x1*x1)
        sage: chart = P.standard_affine_chart_embedding(0)
        sage: product = Schemes(QQ).fiber_product(Z.inclusion(), chart)
        sage: product.left_projection().codomain() is Z
        True
        sage: product.right_projection().codomain() is chart.domain()
        True
        sage: product.left_projection().is_open_immersion()
        True
        sage: Z.inclusion()*product.left_projection() == chart*product.right_projection()
        True
        sage: product.from_pullback_cone(product.left_projection(), product.right_projection()) == product.categorical_identity_morphism()
        True
    """
    for closed_map, affine_map, closed_on_left in (
        (left_map, right_map, True),
        (right_map, left_map, False),
    ):
        closed = closed_map.domain()
        affine = affine_map.domain()
        ambient = closed_map.codomain()
        base = affine.scheme_base_ring()
        if not (
            closed in ClosedSubschemes(base)
            and (closed_map == closed.inclusion()) is True
            and affine in Schemes(base).Affine()
            and (
                ambient in ProjectiveSpaces(base)
                or ambient in ProductProjectiveSpaces(base)
            )
        ):
            continue
        coordinate_map = _projective_coordinate_morphism(affine_map)
        coordinates = tuple(coordinate_map.homogeneous_coordinates())
        ring = affine.coordinate_algebra()
        if ambient in ProjectiveSpaces(base):
            homogeneous_ring = (
                ambient.O(1).global_sections().homogeneous_coordinate_ring()
            )
            equations = tuple(closed.homogeneous_defining_equations(homogeneous_ring))
        else:
            equations = tuple(closed.defining_equations())
        local_equations = tuple(
            ring(
                _evaluate_owned_homogeneous_polynomial_on_coordinates(
                    equation, equation.parent(), coordinates
                )
            )
            for equation in equations
        )
        quotient, quotient_map = ring._quotient_by_algebra_elements(local_equations)
        local_coordinates = tuple(
            quotient_map(ring(coordinate)) for coordinate in coordinates
        )

        def closed_projection(mor):
            return _ProjectiveCoordinateMorphism(
                mor,
                local_coordinates,
                coefficient_map=quotient_map * coordinate_map.coefficient_map(),
            )

        projection_data = (
            (closed_projection, quotient_map)
            if closed_on_left
            else (quotient_map, closed_projection)
        )

        def factor(left_cone_map, right_cone_map):
            return product.corestriction(
                right_cone_map if closed_on_left else left_cone_map
            )

        product = affine.closed_subscheme(
            local_equations,
            placements=(FiberProductSchemes(base),),
            _quotient_data=(quotient, quotient_map),
            fiber_product_construction=SchemeFiberProductConstruction(
                (left_map, right_map),
                projection_data,
                scheme_factorization=factor,
            ),
        )
        return product
    return None


def _scheme_fiber_product(left_map, right_map):
    r"""Return ``X x_S Y`` in the represented affine and scalar-projective regimes."""
    assert left_map.codomain() is right_map.codomain(), (
        f"{left_map} and {right_map} do not form a cospan: their codomains "
        f"{left_map.codomain()} and {right_map.codomain()} differ"
    )
    projective_base_change = _projective_space_scalar_base_change(left_map, right_map)
    if projective_base_change is not None:
        return projective_base_change
    closed_affine_pullback = _projective_closed_affine_pullback(left_map, right_map)
    if closed_affine_pullback is not None:
        return closed_affine_pullback
    multiprojective_fibre = _multiprojective_closed_fibre(left_map, right_map)
    if multiprojective_fibre is not None:
        return multiprojective_fibre

    left = left_map.domain()
    right = right_map.domain()
    base_scheme = left_map.codomain()
    affine_over_base = Schemes(left.scheme_base_ring()).Affine()
    if (
        left._is_glued_from_affine_atlas()
        and right in affine_over_base
        and base_scheme in affine_over_base
    ):
        from sage_extensions.categories.schemes.gluing import (
            _glued_fiber_product_over_affine_base,
        )

        return _glued_fiber_product_over_affine_base(left_map, right_map)
    # Scalar base change includes noncanonical maps and endomorphisms of R.
    # Choose it before the coproduct shortcut for two R-linear structure maps.
    for scheme_leg, scalar_leg, on_left in (
        (left_map, right_map, True),
        (right_map, left_map, False),
    ):
        scheme = scheme_leg.domain()
        scalar_scheme = scalar_leg.domain()
        if (
            scheme in Schemes(scheme.scheme_base_ring()).Affine()
            and scheme_leg.codomain() is scheme.base_scheme()
            and scalar_scheme is scalar_scheme.base_scheme()
            and scheme_leg == scheme.structure_morphism()
        ):
            functor = Schemes(scheme.scheme_base_ring()).base_change_functor(
                scalar_leg.coordinate_algebra_morphism()
            )
            return functor._affine_object(
                scheme, cospan=(left_map, right_map), scheme_on_left=on_left
            )
    base_ring = left.scheme_base_ring()
    affine = Schemes(base_ring).Affine()
    assert left in affine and right in affine and base_scheme in affine, (
        f"cannot form the fibre product of {left_map} and {right_map}: this computation requires "
        f"affine schemes over {base_ring}, but {left}, {right} and {base_scheme} are objects of "
        f"{left.category()}, {right.category()} and {base_scheme.category()}"
    )
    left_pullback = left_map.coordinate_algebra_morphism()
    right_pullback = right_map.coordinate_algebra_morphism()
    commutative_algebras = Algebras(base_ring).Associative().Unital().Commutative()
    match base_scheme:
        case _ if (
            base_scheme is left.base_scheme()
            and left_map.parent().mor_category().is_subcategory(Schemes(base_ring))
            and right_map.parent().mor_category().is_subcategory(Schemes(base_ring))
        ):
            # Spec R is terminal in Sch/R, so both legs are structure morphisms
            # and the span sits under R, the initial object of CAlg_R: the
            # pushout is the coproduct A tensor_R B with its own factorization.
            algebra_pushout = commutative_algebras.coproduct(
                (left.coordinate_algebra(), right.coordinate_algebra())
            )
            left_pushout_map, right_pushout_map = algebra_pushout.coproduct_injections()
            cocone_factorization = algebra_pushout.from_cocone
        case _:
            quotient_base_change = _localization_base_change_pushout(
                left_pullback, right_pullback
            )
            if quotient_base_change is None:
                quotient_base_change = _quotient_base_change_pushout(
                    left_pullback, right_pullback
                )
            match quotient_base_change:
                case None:
                    algebra_pushout = commutative_algebras.pushout(
                        left_pullback, right_pullback
                    )
                    left_pushout_map = algebra_pushout.left_pushout_map()
                    right_pushout_map = algebra_pushout.right_pushout_map()
                    cocone_factorization = None
                case _:
                    (
                        algebra_pushout,
                        left_pushout_map,
                        right_pushout_map,
                        cocone_factorization,
                    ) = quotient_base_change
    return _affine_scheme(
        algebra_pushout,
        base_ring,
        (FiberProductSchemes(base_ring),),
        fiber_product_construction=SchemeFiberProductConstruction(
            (left_map, right_map),
            (left_pushout_map, right_pushout_map),
            algebra_pushout=algebra_pushout,
            cocone_factorization=cocone_factorization,
        ),
    )


# ---------------------------------------------------------------------------
# Subobjects of a scheme.
# ---------------------------------------------------------------------------


class _SchemeSubobjectsOf(OwnedParameterizedCategory):
    r"""Subobjects of one scheme ``X``, by the kind of immersion they carry.

    A subobject is the pair ``(Z, i: Z -> X)``.  The level data are the
    codomain ``X`` and the defining datum of ``i`` in ``Mor(Z, X)``; ``i`` is
    built from them once ``Z`` exists, because an arrow cannot be constructed
    before its domain.
    """

    def base_object(self):
        r"""Return the scheme these subobjects are subobjects of."""
        return self.base()

    def _repr_object_names(self) -> str:
        return f"{self.immersion_name} into {self.base_object()}"

    def super_categories(self):
        return [
            Schemes(self.base_object().scheme_base_ring()).SubobjectCategory(
                self.base_object()
            )
        ]

    class ParentMethods:
        def __init__(self, inclusion_codomain, inclusion_datum, **rest) -> None:
            self._inclusion_codomain = inclusion_codomain
            self._inclusion_datum = inclusion_datum
            super().__init__(**rest)

        @cached_method
        def inclusion(self):
            r"""Return the chosen monomorphism ``i: Z -> X`` representing this subobject.

            The scheme it sits inside is ``i.codomain()`` and is never separate
            data.
            """
            return _scheme_mor_category(self, self._inclusion_codomain)(
                self._inclusion_datum
            )


def _distinguished_overlap_transition(
    left_chart, left_element, right_chart, right_element
):
    r"""The isomorphism ``D_i(f_j) -> D_j(f_i)`` of the two presentations of ``D(f_i f_j)``.

    For ``left_chart = D(f_i)`` and ``right_chart = D(f_j)`` inside one affine
    scheme, the overlap is the locus where both elements are units.  It is
    presented once over each chart, and the two presentations are compared by
    the universal property alone: a map into ``D(f_j)`` is a map into ``X``
    inverting ``f_j``, so each direction is the corestriction of one overlap's
    inclusion through the other chart and then through the other overlap.
    """
    left_overlap = left_chart.distinguished_open(right_element)
    right_overlap = right_chart.distinguished_open(left_element)
    return _scheme_isomorphism(
        right_overlap.corestriction(
            right_chart.corestriction(left_chart.inclusion() * left_overlap.inclusion())
        ),
        left_overlap.corestriction(
            left_chart.corestriction(
                right_chart.inclusion() * right_overlap.inclusion()
            )
        ),
    )


class ClosedEmbeddings(_SchemeSubobjectsOf):
    r"""Subobjects of ``X`` whose inclusion is a closed immersion.

    For affine \(X=\operatorname{Spec}A\) this is
    \(\operatorname{Spec}(A/I)\hookrightarrow X\), induced by the quotient
    \(A\twoheadrightarrow A/I\).  The level datum is the finite family of
    equations cutting the subscheme out.
    """

    immersion_name = "closed embeddings"

    def an_object(self):
        r"""The coordinate axis, cut out by the first coordinate of ``X``."""
        base_object = self.base_object()
        first = next(iter(base_object.coordinate_algebra().algebra_generators()))
        return base_object.closed_subscheme(first)


class _LogarithmicDifferentialsSheafEngine:
    r"""``Omega^p_X(log D)`` for an effective Cartier divisor ``i: D -> X``.

    The defining data are the divisor ``D`` and the degree ``p``.  For ``X``
    smooth over the base and ``D`` smooth with local equation ``t``, the sheaf
    is the ``O_X``-submodule of ``j_* Omega^p_U``, ``j: U = X - D -> X``,
    generated locally by ``Omega^p_X`` and ``Omega^{p-1}_X wedge dt/t``
    (Deligne, *Theorie de Hodge II*, Publ. Math. IHES 40 (1971), §3.1).
    """

    def __init__(self, divisor, degree, **rest) -> None:
        self._divisor = divisor
        self._degree = degree
        super().__init__(**rest)

    def divisor(self):
        r"""The effective Cartier divisor ``i: D -> X``."""
        return self._divisor

    def degree(self):
        r"""The form degree ``p``."""
        return self._degree

    def ringed_space(self):
        return self.divisor().inclusion().codomain()

    scheme = ringed_space

    def top_degree_twist(self):
        r"""The twist ``e - n - 1`` with ``Omega^n_X(log D) = O(e - n - 1)`` on ``X = P^n``.

        In top degree ``n`` the local generator is ``dx_1 wedge ... wedge
        dx_{n-1} wedge dt/t``, so ``Omega^n_X(log D) = Omega^n_X tensor O_X(D)``.
        On ``P^n`` one has ``Omega^n = O(-n-1)`` (Hartshorne, *Algebraic
        Geometry*, Example II.8.20.1), and ``O_X(D) = I_D^vee = O(e)`` for the
        divisor's ideal sheaf ``I_D = O(-e)``.  A section ``g`` of
        ``O(e - n - 1)`` is the form ``g Omega / f``, with ``f`` the degree-``e``
        equation of ``D`` and ``Omega`` the Euler form (Griffiths, *On the periods
        of certain rational integrals I*, Ann. of Math. 90 (1969)).
        """
        X = self.scheme()
        n = X.dimension()
        assert X in ProjectiveSpaces(X.scheme_base_ring()) and self.degree() == n, (
            f"Omega^{self.degree()}_X(log D) on {X} is a twist of O_X only in top degree on a "
            f"projective space; here p = {self.degree()} and X has dimension {n}"
        )
        return -self.divisor().ideal_sheaf().degree() - n - 1

    def global_sections(self):
        r"""``H^0(X, Omega^p_X(log D))``.

        For ``X = P^n`` and ``p = n`` it is ``H^0(P^n, O(e - n - 1))``, the
        forms ``g Omega / f`` with ``g`` of degree ``e - n - 1``
        (:meth:`top_degree_twist`).  Every other case needs the logarithmic
        de Rham complex on an affine cover of ``X`` and its Cech cohomology.
        """
        X = self.scheme()
        match self.degree():
            case p if (
                X in ProjectiveSpaces(X.scheme_base_ring()) and p == X.dimension()
            ):
                return X.O(self.top_degree_twist()).global_sections()
            case _:
                assert False, (
                    "global_sections on logarithmic differentials: not implemented outside top "
                    "degree on a projective space"
                )

    def sheaf_category(self):
        r"""``QCoh(X)``, the category this sheaf is an object of."""
        return QuasiCoherentSheaves(self.scheme())

    def _repr_(self):
        return f"Omega^{self.degree()}_X(log D) for D = {self.divisor()} on X = {self.scheme()}"


class EffectiveCartierDivisors(_SchemeSubobjectsOf):
    r"""Effective Cartier divisors ``D -> X`` as closed subobjects of one scheme.

    An effective Cartier divisor is a closed subscheme whose ideal sheaf is
    invertible.  This is structure on the closed subobject, not on one
    particular divisor realization.  A represented construction may retain a
    Picard-class realization; the class itself is mathematically ``[O_X(D)]``.
    """

    immersion_name = "effective Cartier divisors"

    def super_categories(self):
        ambient = self.base_object()
        return [
            ClosedEmbeddings(ambient),
            ClosedSubschemes(ambient.scheme_base_ring()),
        ]

    def an_object(self):
        r"""Return the empty effective Cartier divisor in the represented affine case."""
        ambient = self.base_object()
        base = ambient.scheme_base_ring()
        match ambient:
            case _ if ambient in Schemes(base).Affine():
                return ambient.closed_subscheme(
                    ambient.coordinate_algebra().one(),
                    placements=(self,),
                    effective_cartier_ideal_sheaf=ambient.structure_sheaf(),
                )
            case _:
                raise AssertionError(
                    f"the empty closed subscheme is an effective Cartier divisor on {ambient}, but this "
                    "category currently constructs that specimen only from an affine presentation"
                )

    class ParentMethods:
        def __init__(
            self,
            effective_cartier_ideal_sheaf,
            effective_cartier_picard_class=None,
            **rest,
        ) -> None:
            self._effective_cartier_picard_class = effective_cartier_picard_class
            super().__init__(
                closed_embedding_ideal_sheaf=effective_cartier_ideal_sheaf,
                **rest,
            )
            ambient = self.inclusion().codomain()
            assert self.ideal_sheaf() in QuasiCoherentSheaves(ambient).Invertible(), (
                f"the defining ideal sheaf of the effective Cartier divisor {self} on {ambient} must be "
                f"an invertible O_X-module on {ambient}, but {self.ideal_sheaf()} is an object of "
                f"{self.ideal_sheaf().category()}"
            )

        def is_effective_cartier_divisor(self) -> bool:
            return True

        def picard_class(self):
            r"""Return the represented class ``[O_X(D)] = [I_D^vee]`` in ``Pic(X)``."""
            match self._effective_cartier_picard_class:
                case None:
                    raise AssertionError(
                        f"{self} is an effective Cartier divisor on {self.inclusion().codomain()}, so it "
                        "defines the Picard class [O(D)], but this closed-subscheme realization does not "
                        "supply a represented class"
                    )
                case picard_class:
                    return picard_class

        def logarithmic_differentials(self, degree):
            r"""``Omega^p_X(log D)``, the ``p``-forms on ``X`` with logarithmic poles along ``D``.

            For ``X`` smooth over the base and ``D`` a smooth divisor with local
            equation ``t``, it is the ``O_X``-submodule of ``j_* Omega^p_U``,
            ``j: U = X - D -> X``, generated locally by ``Omega^p_X`` and
            ``Omega^{p-1}_X wedge dt/t``; it is locally free and an object of
            ``QuasiCoherentSheaves(X)`` (Deligne, *Theorie de Hodge II*, Publ.
            Math. IHES 40 (1971), §3.1).  Here ``p`` is ``degree``.
            """
            ambient = self.inclusion().codomain()
            return QuasiCoherentSheaves(ambient).object(
                categories=(QuasiCoherentSheaves(ambient).FiniteLocallyFree(),),
                construction_data={"divisor": self, "degree": degree},
                _engine=_LogarithmicDifferentialsSheafEngine,
            )

        def residue(self, degree):
            r"""The Poincare residue ``Res: H^0(X, Omega^p_X(log D)) -> H^0(D, Omega^{p-1}_D)``.

            Here ``i: D -> X`` is ``self.inclusion()``, and ``X`` and ``D`` are
            smooth over the base; ``p`` is ``degree``.  The sheaf map
            ``Omega^p_X(log D) -> i_* Omega^{p-1}_D`` is locally
            ``alpha wedge dt/t |-> alpha|_D`` for a local equation ``t`` of
            ``D``; it identifies ``Gr^W_1 Omega^*_X(log D)`` with
            ``i_* Omega^*_D[-1]`` (Deligne, op. cit., (3.1.5.2), the case of
            one component).  This method returns its map on global sections.

            For ``X = P^n`` with ``n >= 2``, ``p = n`` and ``D = V(f)`` of degree
            ``e``, the domain is ``H^0(P^n, O(e - n - 1))`` by ``g |-> g Omega / f``
            (:meth:`logarithmic_differentials`).  Adjunction gives
            ``Omega^{n-1}_D = O_D(e - n - 1)`` (Hartshorne, *Algebraic Geometry*,
            Example II.8.20.3), and under it the residue of ``g Omega / f`` is
            ``g|_D`` (Griffiths, *On the periods of certain rational integrals I*,
            Ann. of Math. 90 (1969)).  The restriction
            ``H^0(P^n, O(e - n - 1)) -> H^0(D, O_D(e - n - 1))`` is surjective,
            because ``H^1(P^n, O(-n - 1)) = 0`` for ``n >= 2`` (Hartshorne, III.5.1),
            so its image is all of ``H^0(D, Omega^{n-1}_D)``.
            """
            ambient = self.inclusion().codomain()
            n = ambient.dimension()
            match degree:
                case p if (
                    ambient in ProjectiveSpaces(ambient.scheme_base_ring())
                    and p == n
                    and n >= 2
                ):
                    twist = self.logarithmic_differentials(p).top_degree_twist()
                    return ambient.O(twist).restriction_map(self)
                case _:
                    assert False, (
                        "residue on EffectiveCartierDivisors: not implemented outside top degree on "
                        "a projective space of dimension at least 2"
                    )


class ClosedSubschemes(OwnedCategoryOverBaseRing):
    r"""Closed subschemes of schemes over ``R``: a scheme with its closed immersion.

    ``ClosedEmbeddings(X)`` is the fibre of this category over one scheme
    ``X``; this category collects those fibres over all ``R``-schemes so that
    being a closed subscheme is a placement a session can ask without naming
    the codomain of the immersion.  Its objects are constructed in both.
    """

    def an_object(self):
        r"""The origin of the affine line."""
        line = AffineSpaces(self.base_ring())(1)
        return line.closed_subscheme(
            next(iter(line.coordinate_algebra().algebra_generators()))
        )

    def _repr_object_names(self):
        return f"closed subschemes of schemes over {self.base_ring()}"

    def super_categories(self):
        return [Schemes(self.base_ring())]

    class ParentMethods:
        @cached_method
        def standard_affine_atlas(self):
            r"""The inverse images of the ambient standard projective charts.

            Each chart is the actual pullback of the closed immersion and
            retains its map to this subscheme. Chart overlaps and transitions
            are their base changes (Stacks, Tags 01JR and 01JY).

            Unexecuted conic chart and structure-sheaf assertions::

                sage: from dzack_research.preamble.all import *
                sage: P = ProjectiveSpaces(QQ)(2)
                sage: S = P.O(1).global_sections().homogeneous_coordinate_ring()
                sage: x0, x1, x2 = tuple(S.algebra_generators())
                sage: Z = P.closed_subscheme(x0*x2-x1*x1)
                sage: atlas = Z.standard_affine_atlas()
                sage: atlas.scheme() is Z
                True
                sage: Z.selected_finite_affine_atlas() is atlas
                True
                sage: local = atlas.chart(0)
                sage: local.right_projection().codomain() is Z
                True
                sage: Z.inclusion()*atlas.chart_embedding(0) == P.standard_affine_chart_embedding(0)*local.left_projection()
                True
                sage: site = Z.open_subsets_site()
                sage: basic = site(atlas.chart_open_subset(0))
                sage: Z.structure_sheaf().sections(basic) is local.coordinate_algebra()
                True
            """
            ambient = self.inclusion().codomain()
            base = self.scheme_base_ring()
            assert ambient in ProjectiveSpaces(
                base
            ) or ambient in ProductProjectiveSpaces(base), (
                "a standard closed-subscheme atlas requires a projective-space ambient atlas"
            )
            return ambient.standard_affine_atlas().pullback(self.inclusion())

        def __init__(
            self,
            defining_equations=None,
            closed_embedding_ideal_sheaf=None,
            **rest,
        ) -> None:
            self._defining_equations = defining_equations
            self._closed_embedding_ideal_sheaf = closed_embedding_ideal_sheaf
            super().__init__(**rest)

        def defining_equations(self):
            r"""The supplied global equation family; chartwise presentations keep their local ideals."""
            assert self._defining_equations is not None, (
                f"{self} has no global defining equations: it was glued from closed subschemes of affine "
                "charts, and only their local equations are known"
            )
            return self._defining_equations

        def codimension(self):
            r"""``dim X - dim Z``; for affine ``X`` the codimension of the defining ideal."""
            codomain = self.inclusion().codomain()
            match codomain:
                case _ if codomain in Schemes(codomain.scheme_base_ring()).Affine():
                    coordinate_algebra = codomain.coordinate_algebra()
                    quotient = self.defining_ideal_owned().quotient_ring()
                    return (
                        coordinate_algebra.krull_dimension()
                        - quotient.krull_dimension()
                    )
                case _:
                    return codomain.dimension() - self.dimension()

        def homogeneous_defining_equations(self, coordinate_ring):
            r"""Raise projective defining equations into a selected owned coordinate algebra."""
            codomain = self.inclusion().codomain()
            base = codomain.scheme_base_ring()
            assert codomain in ProjectiveSpaces(base), (
                f"cannot write homogeneous defining equations of {self}: it must be a closed subscheme of "
                f"a projective space over {base}, but it is a closed subscheme of {codomain}, an object of "
                f"{codomain.category()}"
            )
            assert coordinate_ring.base_ring() is base, (
                f"cannot write the homogeneous defining equations of {self} in {coordinate_ring}: that "
                f"ring must have base ring {base}, but its base ring is {coordinate_ring.base_ring()}"
            )
            engine_target = _engine_ring(coordinate_ring)
            target_variables = tuple(engine_target.gens())
            return finite_family(
                tuple(
                    _owned_engine_element(
                        coordinate_ring,
                        _copy_polynomial_by_exponents(
                            _engine_element(equation.parent(), equation),
                            engine_target,
                            target_variables,
                        ),
                    )
                    for equation in self.defining_equations()
                ),
                name=f"Homogeneous defining equations of {self}",
            )

        @cached_method
        def defining_ideal_owned(self):
            r"""Return the ideal generated by the equations cutting this subscheme out.

            For affine ``X = Spec A`` it is an ideal of ``A``; for a projective
            ``X`` it is the homogeneous ideal the equations generate in the
            ring they are written in.  The ideal is derived from the equations
            when asked for: its module presentation is a separate question.
            """
            codomain = self.inclusion().codomain()
            equations = tuple(self.defining_equations())
            match codomain:
                case _ if codomain in Schemes(codomain.scheme_base_ring()).Affine():
                    return codomain.coordinate_algebra().ideal(*equations)
                case _:
                    return equations[0].parent().ideal(*equations)

        def is_empty(self) -> bool:
            r"""Return whether this closed subscheme is empty."""
            codomain = self.inclusion().codomain()
            base = codomain.scheme_base_ring()
            match codomain:
                case _ if codomain in Schemes(base).Affine():
                    return self.defining_ideal_owned().contains_ambient_element(
                        codomain.coordinate_algebra().one()
                    )
                case _ if codomain in Schemes(base).Projective():
                    # Sage's projective dimension is -1 exactly for the empty Proj.
                    return int(self.dimension()) < 0
                case _:
                    assert False, (
                        f"cannot decide whether {self} is empty: this is decided here only for closed subschemes "
                        f"of affine or projective schemes, but it lies in {codomain}, an object of "
                        f"{codomain.category()}"
                    )

        def corestriction(self, morphism):
            r"""The factorization ``T -> Z`` of a morphism ``T -> X`` landing in ``Z``.

            In the affine case the factor is induced by the quotient coordinate
            algebra.  For a homogeneous-coordinate morphism into projective
            space, the coordinates factor through ``Z`` exactly when every
            homogeneous defining equation vanishes on them, and the factor
            retains those coordinates in ``Mor(T, Z)``.
            """
            codomain = self.inclusion().codomain()
            assert morphism.codomain() is codomain, (
                f"cannot factor {morphism} through {self}: it must be a morphism into {codomain}, but its "
                f"codomain is {morphism.codomain()}"
            )
            source = morphism.domain()
            base = source.scheme_base_ring()
            match source:
                case _ if (
                    source in Schemes(base).Affine() and self in Schemes(base).Affine()
                ):
                    pullback = morphism.coordinate_algebra_morphism()
                    assert all(
                        pullback(equation) == source.coordinate_algebra().zero()
                        for equation in self.defining_equations()
                    ), (
                        f"{morphism} does not factor through {self}: its pullback does not kill the defining equations"
                    )
                    algebra = self.coordinate_algebra()
                    factor = _scheme_mor_category(source, self)(
                        algebra.Mor(source.coordinate_algebra())(
                            {
                                label: pullback(
                                    codomain.coordinate_algebra().algebra_generator(
                                        label
                                    )
                                )
                                for label in algebra.algebra_generating_set()
                            }
                        )
                    )
                    assert self.inclusion() * factor == morphism, (
                        f"the factorization {factor} of {morphism} through {self} is wrong: its composite with the "
                        f"inclusion of {self} into {codomain} is not {morphism}"
                    )
                    return factor
                case _ if codomain in ProjectiveSpaces(
                    base
                ) or codomain in ProductProjectiveSpaces(base):
                    # A section on T vanishes when it does modulo the equations of T.
                    coordinates = tuple(
                        _projective_coordinate_morphism(
                            morphism
                        ).homogeneous_coordinates()
                    )
                    if codomain in ProjectiveSpaces(base):
                        target_ring = (
                            codomain.O(1)
                            .global_sections()
                            .homogeneous_coordinate_ring()
                        )
                        equations = tuple(
                            self.homogeneous_defining_equations(target_ring)
                        )
                    else:
                        equations = tuple(self.defining_equations())
                        target_ring = equations[0].parent()
                    on_source = _projective_section_restriction(
                        source, coordinates[0].parent()
                    )
                    assert all(
                        on_source(
                            _evaluate_owned_homogeneous_polynomial_on_coordinates(
                                equation, target_ring, coordinates
                            )
                        ).is_zero()
                        for equation in equations
                    ), (
                        f"{morphism} does not factor through {self}: a homogeneous defining equation does not vanish"
                    )
                    return _ProjectiveCoordinateMorphism(
                        _scheme_mor_category(source, self), coordinates
                    )
                case _:
                    assert False, (
                        f"cannot factor {morphism} through {self}: this is computed here only for morphisms of "
                        "affine schemes and for morphisms into projective space given by homogeneous coordinates; "
                        f"{source} is an object of {source.category()} and {codomain} of {codomain.category()}"
                    )

        def intersection(self, other):
            r"""``Z cap W = V(I + J)``, the scheme-theoretic intersection in ``X``.

            It is the fibre product ``Z x_X W`` (Stacks, Tag 0C4H): a morphism
            into ``X`` factors through it exactly when its pullback kills both
            ideals.
            """
            codomain = self.inclusion().codomain()
            assert other.inclusion().codomain() is codomain, (
                f"cannot intersect {self} and {other}: they are closed subschemes of different schemes, "
                f"{codomain} and {other.inclusion().codomain()}"
            )
            return codomain.closed_subscheme(
                (*self.defining_equations(), *other.defining_equations())
            )

        @cached_method
        def O(self, degree):
            r"""Return ``O_Z(d) = i^* O_P(d)`` for a closed subscheme of projective space."""
            codomain = self.inclusion().codomain()
            assert codomain in ProjectiveSpaces(self.scheme_base_ring()), (
                f"cannot form O(d) on {self}: this requires a closed subscheme of a projective space, but "
                f"{self} is a closed subscheme of {codomain}, an object of {codomain.category()}"
            )
            return codomain.O(degree).restrict_to(self)

        def _picard_group(self):
            r"""Invertible sheaf classes, with ``O_Z(0)`` as projective tensor unit."""
            codomain = self.inclusion().codomain()
            if codomain in ProjectiveSpaces(self.scheme_base_ring()):
                from sage_extensions.categories.divisors.picard_groups import (
                    _invertible_sheaf_class_group,
                )

                return _invertible_sheaf_class_group(self, self.O(0))
            return super()._picard_group()

        def fundamental_cycle(self):
            r"""Return this closed subscheme's cycle with generic local multiplicities."""
            from sage_extensions.categories.divisors.chow_groups import (
                _fundamental_cycle,
            )

            return _fundamental_cycle(self)

        def proper_pushforward_cycle(self, cycle):
            r"""Push ``cycle`` forward along this closed immersion."""
            from sage_extensions.categories.divisors.chow_groups import (
                _closed_immersion_cycle_pushforward,
            )

            return _closed_immersion_cycle_pushforward(self, cycle)

        def serre_intersection(self, other, point):
            r"""Return the local Tor intersection with ``other`` at ``point``."""
            from sage_extensions.categories.divisors.chow_groups import (
                _serre_intersection,
            )

            return _serre_intersection(self, other, point)

        def serre_intersection_multiplicity(self, other, point):
            r"""Return Serre's alternating Tor-length intersection multiplicity."""
            return self.serre_intersection(other, point).multiplicity()

        def intersection_multiplicity(self, other, point):
            r"""``i(p; Z . W)``, the multiplicity of the intersection at ``p``.

            For two effective hypersurfaces meeting properly in a smooth affine
            surface over a field, this is ``length_{O_{X,p}} O_{X,p}/(f,g)``.
            The polynomial realization computes a primary decomposition of
            ``(f,g)``; the component whose radical is the maximal ideal of ``p``
            is the local Artinian factor ``Q_p``, and
            ``dim_k(P/Q_p) = length(P_p/Q_p P_p) [kappa(p):k]``, so dividing by
            the residue degree returns the composition length even at a
            nonrational closed point.  Outside the proper hypersurface case the
            intersection product is Serre's alternating Tor length.
            """
            codomain = self.inclusion().codomain()
            assert other.inclusion().codomain() is codomain, (
                f"cannot form the intersection multiplicity of {self} and {other}: they are closed "
                f"subschemes of different schemes, {codomain} and {other.inclusion().codomain()}"
            )
            base = codomain.scheme_base_ring()
            assert base in OwnedFields(), (
                f"cannot form the intersection multiplicity of {self} and {other} at {point}: the length "
                f"formula requires a field as base ring, but the base ring is {base}"
            )
            assert (
                codomain in AffineSpaces(base)
                and int(codomain.relative_dimension()) == 2
            ), (
                f"cannot form the intersection multiplicity of {self} and {other} at {point}: the length "
                f"formula requires them to lie in the affine plane over {base}, but they lie in {codomain}"
            )
            assert self.codimension() == other.codimension() == 1, (
                f"cannot form the intersection multiplicity of {self} and {other} at {point}: the length "
                "formula requires both to be hypersurfaces, of codimension 1"
            )
            assert (
                self.defining_equations().cardinality() == 1
                and other.defining_equations().cardinality() == 1
            ), (
                f"cannot form the intersection multiplicity of {self} and {other} at {point}: each "
                f"hypersurface must be given by one equation, but they are given by "
                f"{self.defining_equations().cardinality()} and {other.defining_equations().cardinality()}"
            )
            spectrum = codomain.underlying_space()
            match point.parent():
                case _ if point.parent() is spectrum:
                    pass
                case _:
                    point = spectrum(point)
            point_ideal = point.ideal()
            assert point_ideal.is_maximal(), (
                f"cannot form the intersection multiplicity of {self} and {other} at {point}: the point "
                f"must be a closed point, but its ideal {point_ideal} is not maximal"
            )
            meeting = self.intersection(other).defining_ideal_owned()
            return point.local_length(meeting)

        def ideal_sheaf(self):
            r"""Return the quasi-coherent ideal sheaf ``I_Z`` of this closed subscheme.

            Constructions that already represent ``I_Z`` retain that exact sheaf
            as defining data.  Otherwise the affine presentation realizes it as
            ``I~`` from the defining ideal when asked for.
            """
            match self._closed_embedding_ideal_sheaf:
                case None:
                    pass
                case ideal_sheaf:
                    return ideal_sheaf
            codomain = self.inclusion().codomain()
            assert codomain in Schemes(codomain.scheme_base_ring()).Affine(), (
                f"cannot form the ideal sheaf of {self}: this requires a closed subscheme of an affine "
                f"scheme, but {codomain} is an object of {codomain.category()}"
            )
            return codomain.associated_module_sheaf(self.defining_ideal_owned())

        def open_complement(self):
            r"""``X - Z``, the open subscheme on which the ideal of ``Z`` is the unit ideal.

            A prime of ``X = Spec A`` lies outside ``Z = V(I)`` exactly when it
            fails to contain some ``f in I``, so the complement is the union of
            the ``D(f_i)`` for the equations ``f_i`` cutting ``Z`` out.  A single
            equation gives the affine ``D(f)``; several give the scheme glued
            from the ``D(f_i)`` along ``D(f_i f_j)``, whose inclusion is given
            chartwise by the inclusions of the ``D(f_i)``.

            For a projective ``X`` the complement is Sage's quasi-projective
            subscheme ``X - Z``, and its inclusion is defined by ``Z``.
            """
            codomain = self.inclusion().codomain()
            base = codomain.scheme_base_ring()
            match codomain:
                case _ if codomain in Schemes(base).Projective():
                    return _object_of(
                        owned_category_join(
                            (OpenImmersions(codomain), Schemes(base).QuasiProjective())
                        ),
                        scheme_base_ring=base,
                        scheme_engine=_SageAlgebraicSchemeSubscheme.complement(
                            _engine_scheme(self), _engine_scheme(codomain)
                        ),
                        inclusion_codomain=codomain,
                        inclusion_datum=_open_complement_inclusion(self),
                    )
                case _ if codomain in Schemes(base).Affine():
                    equations = self.defining_equations()
                    indices = equations.index_set()
                    charts = {
                        index: codomain.distinguished_open(equations[index])
                        for index in indices
                    }
                    match equations.cardinality():
                        case 0:
                            return codomain.distinguished_open(
                                codomain.coordinate_algebra().zero()
                            )
                        case 1:
                            return charts[next(iter(indices))]
                        case _:
                            return Schemes(base).glue_affine_atlas(
                                charts,
                                {
                                    (left, right): _distinguished_overlap_transition(
                                        charts[left],
                                        equations[left],
                                        charts[right],
                                        equations[right],
                                    )
                                    for left, right in combinations(tuple(indices), 2)
                                },
                                placements=(OpenImmersions(codomain),),
                                inclusion_codomain=codomain,
                                inclusion_datum={
                                    index: chart.inclusion()
                                    for index, chart in charts.items()
                                },
                            )
                case _:
                    assert False, (
                        f"cannot form the open complement of {self}: this is computed here only in affine or "
                        f"projective schemes, but {codomain} is an object of {codomain.category()}"
                    )


class OpenImmersions(_SchemeSubobjectsOf):
    r"""Subobjects of ``X`` whose inclusion is an open immersion.

    ``X.distinguished_open(f)`` builds ``D(f) = Spec A_f`` here, included by
    ``Spec`` of the localization map ``A -> A_f``.  The element ``f`` is not a
    function of the open subscheme (``D(f) = D(uf) = D(f^2)``); it is the
    localization datum the coordinate algebra ``A_f`` retains, and the
    operations below that need it read it there.
    """

    immersion_name = "open immersions"

    def an_object(self):
        r"""\(D(f)\) for ``f`` the first coordinate of ``X``."""
        base_object = self.base_object()
        return base_object.distinguished_open(
            next(iter(base_object.coordinate_algebra().algebra_generators()))
        )

    class ParentMethods:
        @cached_method
        def open_subset(self):
            r"""The image of this open subscheme in its ambient point space.

            Distinguished opens retain their defining function. Selected
            affine chart images retain the image of their continuous chart
            map, which is open by the gluing theorem.
            """
            ambient = self.inclusion().codomain()
            if ambient._is_glued_from_affine_atlas():
                datum = ambient.gluing_datum()
                for index in datum.chart_indices():
                    if self is datum.chart_image(index):
                        return ambient._glued_chart_image_subset(index)
            if self.is_distinguished_open() is True:
                return ambient.underlying_space().distinguished_open(
                    self.distinguished_open_element()
                )
            assert False, (
                f"the point-space image of {self} requires an open-immersion image "
                "construction beyond distinguished opens and selected affine chart images"
            )

        def flat_pullback_cycle(self, cycle):
            r"""Restrict a cycle to this open subscheme, preserving multiplicities.

            Integral cycle components restrict to their intersection with
            the open; an empty intersection contributes zero. This is valid
            for every open immersion, not merely a principal localization.
            """
            return self._flat_pullback_cycle(cycle)

        def _flat_pullback_cycle(self, cycle):
            raise NotImplementedError(
                f"the flat pullback of {cycle} along {self.inclusion()} requires "
                "a represented restriction of prime cycles through this open's atlas"
            )

        def is_distinguished_open(self):
            r"""Whether this open is ``D(f)`` for an element ``f`` of the coordinate algebra of its affine codomain.

            An affine open whose coordinate algebra is the localization of the
            codomain's coordinate algebra at one element is that element's
            ``D(f)``.  Whether an open presented otherwise equals some ``D(f)``
            is whether its closed complement is ``V(f)`` up to radical, which is
            not decided here, and the answer is then the proposition
            ``is_distinguished_open(U)``.
            """
            codomain = self.inclusion().codomain()
            affine = Schemes(codomain.scheme_base_ring()).Affine()
            match self:
                case _ if (
                    codomain in affine
                    and self in affine
                    and self.coordinate_algebra() in LocalizationRings()
                    and self.coordinate_algebra().localization_source()
                    is codomain.coordinate_algebra()
                    and self.coordinate_algebra().inverted_elements().cardinality() == 1
                ):
                    return True
                case _:
                    return AtomicProposition("is_distinguished_open", self)

        def distinguished_open_element(self):
            r"""The element ``f`` with this open equal to ``D(f)``, read from its coordinate algebra ``A_f``."""
            assert self.is_distinguished_open() is True, (
                f"{self} has no chosen element f with {self} = D(f): it is not known to be a "
                f"distinguished open subscheme of {self.inclusion().codomain()}"
            )
            return self.coordinate_algebra().inverted_element()

        def contains_image_of(self, morphism):
            r"""Whether ``g: T -> X`` lands in this open ``U <= X``, that is, factors through ``U``.

            An open immersion ``U -> X`` is a monomorphism, and ``g`` factors
            through it exactly when the image of ``g`` lies in ``U``.  For
            ``U = D(f)`` and ``T`` affine that is ``g^#(f)`` being a unit of
            ``O(T)``, by the universal property of ``A_f`` (Stacks, Tag 01HR);
            that is the case decided here.
            """
            codomain = self.inclusion().codomain()
            assert morphism.codomain() is codomain, (
                f"cannot decide whether {morphism} lands in the open subscheme {self} of {codomain}: its "
                f"codomain is {morphism.codomain()}, not {codomain}"
            )
            source = morphism.domain()
            assert (
                self.is_distinguished_open() is True
                and source in Schemes(source.scheme_base_ring()).Affine()
            ), (
                f"cannot decide whether {morphism} lands in {self}: this is decided here only when {self} "
                f"is a distinguished open D(f) and the domain is affine; the domain {source} is an object "
                f"of {source.category()}"
            )
            defining_element = codomain.coordinate_algebra()(
                self.distinguished_open_element()
            )
            return source.coordinate_algebra()(
                morphism.coordinate_algebra_morphism()(defining_element)
            ).is_unit()

        def corestriction(self, morphism):
            r"""The factorization ``T -> U`` of a morphism ``g: T -> X`` landing in this open ``U``.

            It exists exactly when :meth:`contains_image_of` holds, and it is
            unique because the inclusion is a monomorphism.  For ``U = D(f)``
            the universal property of ``A_f`` sends ``a/f^k`` to
            ``g^#(a) g^#(f)^{-k}`` (Stacks, Tag 01HR).
            """
            assert self.contains_image_of(morphism), (
                "the morphism does not land in this open: it does not send the defining element to a unit"
            )
            source = morphism.domain()
            return _scheme_mor_category(source, self)(
                self.coordinate_algebra().induced_morphism(
                    morphism.coordinate_algebra_morphism()
                )
            )

        def inclusion_into(self, larger_open):
            r"""The open immersion ``D(g) -> D(f)`` when ``D(g) <= D(f)`` in one affine scheme.

            Its pullback is the map ``A_f -> A_g`` the universal property of
            the localization gives, which exists exactly when ``f`` is a unit on
            ``D(g)``; it is the restriction of the structure sheaf, and composed
            with the inclusion of ``D(f)`` it is the inclusion of ``D(g)``.
            """
            from sage_extensions.categories.schemes.ringed_spaces import (
                _localization_restriction_map,
            )

            codomain = self.inclusion().codomain()
            assert larger_open.inclusion().codomain() is codomain, (
                f"cannot include {self} into {larger_open}: they are open subschemes of different schemes, "
                f"{codomain} and {larger_open.inclusion().codomain()}"
            )
            restriction = _localization_restriction_map(
                larger_open.coordinate_algebra(), self.coordinate_algebra()
            )
            inclusion = _scheme_mor_category(self, larger_open)(restriction)
            assert larger_open.inclusion() * inclusion == self.inclusion(), (
                f"the map {inclusion} from {self} to {larger_open} is wrong: its composite with the "
                f"inclusion of {larger_open} is not the inclusion of {self} into {codomain}"
            )
            return inclusion


class DistinguishedOpenImmersions(_SchemeSubobjectsOf):
    r"""Open immersions represented by a distinguished localization ``D(f)``."""

    immersion_name = "distinguished open immersions"

    def super_categories(self):
        return [OpenImmersions(self.base_object())]

    def an_object(self):
        return self(
            self.base_object().distinguished_open(
                next(iter(self.base_object().coordinate_algebra().algebra_generators()))
            )
        )

    def _call_(self, opened):
        from sage_extensions.refine import refine

        if (
            opened not in OpenImmersions(self.base_object())
            or opened.is_distinguished_open() is not True
        ):
            raise ValueError(
                "the localization-based pullback requires a distinguished open D(f)"
            )
        return refine(opened, self)

    class ParentMethods:
        def _flat_pullback_cycle(self, cycle):
            r"""Pull back a cycle through the selected localization ``D(f)``."""
            from sage_extensions.categories.divisors.chow_groups import (
                _distinguished_open_cycle_pullback,
            )

            return _distinguished_open_cycle_pullback(self, cycle)


class SchemeMonomorphisms(_MonoCategoryOf):
    r"""Monomorphisms of schemes.

    A closed immersion and an open immersion are monomorphisms.  Which of the
    two an inclusion is, is placed where the subobject is constructed, and
    this reads that placement; a glued chart embedding is a monomorphism
    because it factors as an isomorphism onto an open subscheme followed by its
    inclusion.  Injectivity on points is neither necessary nor sufficient for a
    scheme monomorphism.
    """

    def accepts(self, arrow) -> bool:
        codomain = arrow.codomain()
        source = arrow.domain()
        match source:
            case _ if source in ClosedEmbeddings(codomain):
                return arrow is source.inclusion()
            case _:
                return arrow.is_open_immersion()


class ProjectiveLines(OwnedCategoryOverBaseRing):
    r"""Projective spaces of relative dimension one with chosen coordinates."""

    def super_categories(self):
        return [ProjectiveSpaces(self.base_ring())]

    def an_object(self):
        return self(ProjectiveSpaces(self.base_ring())(1))

    def _call_(self, line):
        from sage_extensions.refine import refine

        if (
            line not in ProjectiveSpaces(self.base_ring())
            or int(line.relative_dimension()) != 1
        ):
            raise ValueError(
                "a projective line must be P^1 over the specified base ring"
            )
        return refine(line, self)

    class ParentMethods:
        def coordinate_swap_action(self, group=None):
            r"""The involution swapping the two homogeneous coordinates of P^1."""
            from sage_extensions.categories.divisors.linearizations import (
                _projective_line_coordinate_swap_action,
            )

            return _projective_line_coordinate_swap_action(self, group)


class SchemesOverIntegralDomains(OwnedCategoryOverBaseRing):
    r"""Schemes over an integral domain ``R``, with their generic fibre.

    The generic fibre of ``X -> Spec R`` is the base change along
    ``R -> Frac(R)``.  That ``R`` is an integral domain is the category of
    the parameter, refused at the boundary.
    """

    def parameter_category(self):
        return OwnedIntegralDomains()

    def super_categories(self):
        return [Schemes(self.base_ring())]

    def an_object(self):
        return self(Schemes(self.base_ring()).an_object())

    def _call_(self, scheme):
        from sage_extensions.refine import refine

        base = self.base_ring()
        assert scheme in Schemes(base), (
            f"only a scheme over {base} is placed in {self}, but {scheme} is in {scheme.category()}"
        )
        return refine(scheme, self)

    class ParentMethods:
        def generic_fiber(self):
            r"""Base change to the function field of the integral base."""
            return self.base_change(self.scheme_base_ring().fraction_field_map())


class SchemesOverLocalRings(OwnedCategoryOverBaseRing):
    r"""Schemes over a local ring ``R``, with their special fibre.

    The special fibre of ``X -> Spec R`` is the base change along the residue
    map ``R -> R/m`` at the closed point.  That ``R`` is local is the category
    of the parameter, refused at the boundary.
    """

    def parameter_category(self):
        return OwnedRings().Local()

    def super_categories(self):
        return [Schemes(self.base_ring())]

    def an_object(self):
        return self(Schemes(self.base_ring()).an_object())

    def _call_(self, scheme):
        from sage_extensions.refine import refine

        base = self.base_ring()
        assert scheme in Schemes(base), (
            f"only a scheme over {base} is placed in {self}, but {scheme} is in {scheme.category()}"
        )
        return refine(scheme, self)

    class ParentMethods:
        def special_fiber(self):
            return self.base_change(self.scheme_base_ring().residue_map())

        def base_change_to_completion(self):
            base = self.scheme_base_ring()
            return self.base_change(
                base.adic_completion(base.maximal_ideal()).completion_map()
            )

        def special_fiber_comparison(self):
            from sage_extensions.categories.schemes.families import (
                _special_fiber_comparison,
            )

            return _special_fiber_comparison(self)


__all__ = [
    "AffineSchemes",
    "AffineSpaces",
    "ClosedEmbeddings",
    "ClosedSubschemes",
    "DistinguishedOpenImmersions",
    "EffectiveCartierDivisors",
    "FiberProductSchemes",
    "IntegralSchemes",
    "NormalSchemes",
    "OpenImmersions",
    "ProductProjectiveSpaces",
    "ProductSchemes",
    "ProjectiveLines",
    "ProjectiveSchemes",
    "ProjectiveSpaces",
    "SchemeMonomorphisms",
    "SchemeMorphism",
    "Schemes",
    "SchemesOverIntegralDomains",
    "SchemesOverLocalRings",
    "SmoothSchemes",
]

Schemes._MonoCategory = SchemeMonomorphisms
