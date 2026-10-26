r"""The session namespace, as ``sage.all`` is Sage's: importing it makes a scope a session.

``from sage_extensions.all import *`` enters the closed preamble
mathematical universe.  The module is not a superset of ``sage.all`` and does
not publish Sage's constructor namespace.  Sage is an implementation service
used by private adapters; every public name bound here is owned mathematics or
an ordinary Python support object deliberately selected by the preamble.
"""

import sys as _sys
from importlib import import_module as _import_module
from importlib.util import find_spec as _find_spec
from pathlib import Path as _Path
from typing import cast as _cast

# The session's numeric vocabulary and its parser are one contract: decimal
# literals remain explicit MPFR approximations even though ``RealNumber`` now
# names an exact element of ``RR``.
import sageparse.preparser.research  # noqa: F401
from sage.misc.lazy_import import lazy_import as _lazy_import
from sage.repl.load import load as _sage_load

from sage_extensions import language_runtime as _language_runtime
from sage_extensions.categories.abstract_categories import (  # noqa: F401
    Cat,
    CategoricalIsomorphism,
    CommutativeSquare,
    Coverage,
    CoveringFamilies,
    DescentData,
    DescentDataOnCover,
    DescentEqualizer,
    DescentEqualizerComparison,
    DirectedSystem,
    DirectSumObjects,
    FiniteOrdinalCategory,
    InverseSystem,
    MorCategories,
    NaturalTransformationMorphism,
    OpenCoveringFamilies,
    OppositeMorphism,
    PosetCategory,
    ProductMorphism,
    ResolutionMorphism,
    Resolutions,
    Sheaves,
    SubobjectMor,
    SubobjectMorphism,
    TrivialCoveringFamilies,
    trivial_coverage,
)
from sage_extensions.categories.abstract_categories.functors import (  # noqa: F401
    DiscreteCategories,
    DiscreteCategory,
    ObjectSetFunctor,
)
from sage_extensions.categories.algebras.algebras import (
    MatrixAlgebras as MatrixAlgebras,
)
from sage_extensions.categories.cell_complexes import (  # noqa: F401
    CellComplexes,
    DeltaComplexes,
    PolytopalComplexes,
    SimplicialComplexes,
    SimplicialSets,
)
from sage_extensions.categories.chamber_systems import (  # noqa: F401
    ChamberSystems,
)
from sage_extensions.categories.complex_affine_spaces import (  # noqa: F401
    ComplexAffineSpaces,
    ComplexVectorSpaces,
)
from sage_extensions.categories.complex_analytic_spaces import (  # noqa: F401
    ComplexAnalyticSpaces,
)
from sage_extensions.categories.coxeter_diagrams import (
    CoxeterDiagrams as CoxeterDiagrams,
)
from sage_extensions.categories.divisors import (  # noqa: F401
    AlgebraicCycleGroups,
    CartierDivisorGroups,
    ChowGroups,
    ClassGroups,
    CompleteLinearSystems,
    CoxRings,
    DivisorGroups,
    FormalDivisorGroups,
    HomogeneousPolynomialSectionSpaces,
    ImposedMultiplicityLinearSystems,
    LineBundleCohomologySpaces,
    PicardGroups,
    ProjectiveJetSpaces,
    ProjectiveLinearSystems,
    SectionRings,
    TorusInvariantCycleGroups,
    WeilDivisorGroups,
)
from sage_extensions.categories.functions import (  # noqa: F401
    C,
    GradedLebesgueAlgebra,
    GradedLebesgueModule,
    GradedTensorProductModules,
    GradedTensorSquare,
    LebesgueConvolution,
    LebesgueConvolutionAlgebra,
    LebesgueConvolutionModule,
    LebesgueGradedModules,
    Lp,
    ell,
    graded_lebesgue_algebra,
    lebesgue_convolution_algebra,
)

# Explicit redundant aliases below are public session exports, not private imports.
from sage_extensions.categories.functors.core import (
    Adjunction as Adjunction,
)
from sage_extensions.categories.functors.core import (
    Functor as Functor,
)
from sage_extensions.categories.functors.core import (
    IdentityFunctor as IdentityFunctor,
)
from sage_extensions.categories.functors.core import (
    NaturalTransformation as NaturalTransformation,
)
from sage_extensions.categories.graph_categories import (  # noqa: F401
    Digraphs,
    Graphs,
    LabelledDigraphs,
    LabelledGraphs,
)
from sage_extensions.categories.group.groups import (  # noqa: F401
    LieGroups,
    TopologicalGroups,
)
from sage_extensions.categories.holomorphic_atlases import (  # noqa: F401
    HolomorphicAtlases,
)
from sage_extensions.categories.hyperbolic_geometry import (  # noqa: F401
    HyperbolicPolyhedra,
    HyperbolicRationalPoints,
    HyperbolicSpaces,
    PositiveConeComponents,
)
from sage_extensions.categories.hyperbolic_lattices import (  # noqa: F401
    HyperbolicLattices,
)
from sage_extensions.categories.integral_affine_atlases import (  # noqa: F401
    IntegralAffineAtlases,
)
from sage_extensions.categories.integral_affine_collars import (  # noqa: F401
    IntegralAffineCollars,
)
from sage_extensions.categories.integral_affine_manifolds import (  # noqa: F401
    IntegralAffineManifolds,
    IntegralAffineManifoldsWithBoundary,
    IntegralAffineManifoldsWithCorners,
    SingularIntegralAffineLocalModels,
    SingularIntegralAffineSpaces,
)
from sage_extensions.categories.integral_affine_stratified_atlases import (  # noqa: F401
    IntegralAffineBoundaryAtlases,
    IntegralAffineCornerAtlases,
)
from sage_extensions.categories.isotropic_orbits import (  # noqa: F401
    FlagType,
    IsotropicFlag,
)
from sage_extensions.categories.isotropic_parabolics import (  # noqa: F401
    PrimitiveIsotropicSubobjects,
)
from sage_extensions.categories.lattice_centralizers import (  # noqa: F401
    IsometryPrimitiveExtension,
)
from sage_extensions.categories.lattice_morphisms import (  # noqa: F401
    LatticeEmbedding,
    LatticeIsometry,
    LatticeMor,
    LatticeMorphism,
)
from sage_extensions.categories.lattices import (  # noqa: F401  # noqa: F401
    DefiniteLattices,
    EvenLattices,
    EvenTwoElementaryLattices,
    FiniteRankLattices,
    IsotropicReductions,
    Lattices,
    NoncrystallographicRootLattices,
    NondegenerateLattices,
    NotPrimitiveError,
    RootLattices,
    nikulin_invariants,
    signature_pair,
    signature_pairs,
)
from sage_extensions.categories.manifold_dimension_strata import (  # noqa: F401
    ManifoldsOfDimensionAtMost,
    PureDimensionalManifolds,
)
from sage_extensions.categories.manifolds import (  # noqa: F401
    ComplexManifolds,
    DifferentiableManifolds,
    RiemannianManifolds,
    SmoothManifolds,
    TopologicalManifolds,
)
from sage_extensions.categories.manifolds_with_boundary import (  # noqa: F401
    RealCkManifoldsWithBoundary,
    RealCkManifoldsWithCorners,
    SmoothManifoldsWithBoundary,
    SmoothManifoldsWithCorners,
    TopologicalManifoldsWithBoundary,
    TopologicalManifoldsWithCorners,
)
from sage_extensions.categories.metric_affine_spaces import (  # noqa: F401
    EuclideanSpaces,
    SphericalSpaces,
)
from sage_extensions.categories.modules.hodge_structures import (  # noqa: F401
    FilteredModules,
    HodgeStructures,
    MixedHodgeStructures,
    PolarizedHodgeStructures,
)
from sage_extensions.categories.modules.pure.modules import (  # noqa: F401
    MatrixEndomorphismSpaces,
    MatrixSpaces,
)
from sage_extensions.categories.orbifolds import (  # noqa: F401
    ComplexOrbifolds,
    Orbifolds,
    RiemannianOrbifolds,
)
from sage_extensions.categories.rational_integral_stabilizers import (  # noqa: F401
    FiniteCommensurabilityQuotient,
    IntegralStructureAction,
)
from sage_extensions.categories.real_affine_spaces import (  # noqa: F401
    AffineSpacesWithLattice,
    RealAffineSpaces,
    RealVectorSpaces,
)
from sage_extensions.categories.real_ck_atlases import (  # noqa: F401
    RealCkAtlases,
)
from sage_extensions.categories.real_ck_manifolds import (  # noqa: F401
    RealCkManifolds,
)
from sage_extensions.categories.satake_diagrams import (
    SatakeDiagrams as SatakeDiagrams,
)
from sage_extensions.categories.schemes.degeneration_central_fibers import (  # noqa: F401
    DegenerationCentralFibers,
)
from sage_extensions.categories.sets.finite_graded_posets import (  # noqa: F401
    FiniteGradedPosets,
)
from sage_extensions.categories.stratified_atlases import (  # noqa: F401
    RealCkBoundaryAtlases,
    RealCkCornerAtlases,
    TopologicalBoundaryAtlases,
    TopologicalCornerAtlases,
)
from sage_extensions.categories.topological_atlases import (  # noqa: F401
    TopologicalAtlases,
)
from sage_extensions.categories.triangulations import (  # noqa: F401
    ChosenTriangulations,
)

_lazy_import(
    "sage_extensions.schemes",
    (
        "ADELogPairs",
        "AlgebraSheaves",
        "AffineGroupSchemeActions",
        "AffineGroupSchemes",
        "AffineGSchemes",
        "AffineInvariantQuotientBaseChangeComparison",
        "AffineSchemes",
        "AffineSpaces",
        "AbstractPolytopes",
        "ConvexPolytopesIn",
        "AnalyticDiscFamily",
        "Blowups",
        "ClosedEmbeddings",
        "ClosedSubschemes",
        "ConvexPolygons",
        "ConvexPolytopes",
        "EuclideanPolytopesIn",
        "HyperbolicGeodesicPolytopesIn",
        "LatticePolytopesIn",
        "CurveLocalDeltaContribution",
        "Curves",
        "CyclicCoverBaseChangeComparison",
        "DistinguishedAffineCoverRefinement",
        "DistinguishedAffineCovers",
        "EffectiveCartierDivisors",
        "FiberProductSchemes",
        "FiniteGluedInvariantQuotient",
        "HesseBertiniFamily",
        "HorikawaEnriquesSurface",
        "HorikawaK3Family",
        "IntegralSchemes",
        "IsolatedHypersurfaceSingularity",
        "LatticePolygons",
        "LatticePolytopes",
        "LegendreMonodromyFamily",
        "LocallyRingedSpaces",
        "LogPairs",
        "ModuleSheaves",
        "NodalCubic",
        "NodalCubicIntegralTopology",
        "NodalCubicNormalization",
        "NormalSchemes",
        "OpenImmersions",
        "DistinguishedOpenImmersions",
        "PGL2IntegralTopology",
        "PointedAnalyticFundamentalGroup",
        "ProductProjectiveSpaces",
        "ProductSchemes",
        "ProjectiveCompleteIntersections",
        "ProjectiveGeneralLinearGroup2",
        "ProjectivePointBlowups",
        "ProjectiveSchemes",
        "ProjectiveSpaces",
        "ProjectiveLines",
        "QuasiCoherentSheaves",
        "RationalPolyhedralFans",
        "RegularPolytopes",
        "SphericalGeodesicPolytopesIn",
        "RelativeCyclicCoverLift",
        "RelativeProjectivizations",
        "RingedSpaces",
        "SchemeMonomorphisms",
        "SchemeMorphism",
        "Schemes",
        "SchemesOverIntegralDomains",
        "SchemesOverLocalRings",
        "PresheafObjects",
        "SheafObjects",
        "SheafedSpaces",
        "SideDecoration",
        "SmoothSchemes",
        "Surfaces",
        "ToricFixedPointBlowups",
        "ToricGeometricLineBundleCohomologySpaces",
        "ToricLogPairs",
        "ToricSchemes",
        "ToricProjectiveSpaces",
        "GorensteinToricSchemes",
        "SmoothCompleteRationalToricSchemes",
        "ToricWeightCohomologyComplexes",
        "Varieties",
        "ZariskiCoveringFamilies",
        "distinguished_affine_coverage",
        "rational_quintic_with_nonrational_node_normalization",
        "rational_quintic_with_two_nodes_normalization",
        "zariski_coverage",
    ),
)
_lazy_import(
    "sage_extensions.categories.schemes.cyclic_covers",
    "CyclicCovers",
)
from sage_extensions.categories.algebras.graded_lie_algebras import (  # noqa: F401
    GradedLieAlgebras,
)
from sage_extensions.categories.algebras.graded_nonassociative_algebras import (  # noqa: F401
    GradedNonassociativeAlgebras,
)
from sage_extensions.categories.fundamental_groupoids import (  # noqa: F401
    FundamentalGroupoid,
    FundamentalGroupoids,
)
from sage_extensions.categories.pointed_topological_spaces import (  # noqa: F401
    TopologicalSpaceCoslices,
)
from sage_extensions.categories.rings.ring_foundation import (
    _OwnedRingParent,
)
from sage_extensions.categories.sets import (  # noqa: F401
    NN,
    AugmentedSimplexCategory,
    CardinalComparison,
    Cardinalities,
    CartesianProductsOfSets,
    CoproductsOfSets,
    CountableSets,
    CountablyInfiniteSets,
    DisjointUnionsOfSets,
    EnumeratedByIntegers,
    EnumeratedByNaturals,
    EnumeratedSets,
    FinitelySupportedFunctionSets,
    FinitePowerSets,
    FiniteSets,
    FourierCharacters,
    FunctionEnumeratedSets,
    HermitePolynomials,
    InfiniteSets,
    LaurentMonomials,
    ObjectSetsOfDiscreteCategories,
    Ord,
    Ordinals,
    PartiallyOrderedSets,
    PowerSets,
    Set,
    SetInjection,
    Sets,
    SetSurjection,
    SincTranslates,
    TotallyOrderedSets,
    UncountableSets,
    WellOrderedSets,
    aleph,
    aleph0,
    cardinal,
    continuum,
    finite_ordered_set,
    omega,
    omega0,
    ordinal,
)
from sage_extensions.categories.topological_spaces import (  # noqa: F401
    ContinuousMap,
    TopologicalSpaceMor,
    TopologicalSpaces,
)
from sage_extensions.categories.vector_orbits import (  # noqa: F401
    VectorPrimitiveExtension,
)
from sage_extensions.categories.vinberg_invariants import (  # noqa: F401
    VinbergInvariantMatrices,
    reflection_cosines,
)
from sage_extensions.logic import Predicate, Propositions, Unknown, ask  # noqa: F401
from sage_extensions.rings import (  # noqa: F401
    CC,
    RR,
    AdicallyCompleteRings,
    AdicCompletions,
    ArtinianRings,
    CommutativeIdeals,
    CommutativeRings,
    CompleteLocalRings,
    DistinguishedOpenSubobjects,
    DivisionRings,
    ExactComplexField,
    ExactComplexNumber,
    ExactRealField,
    ExactRealNumber,
    Fields,
    FormalPowerSeriesRings,
    I,
    IntegralDomains,
    LocalRings,
    NoetherianRings,
    NonNegativeReals,
    NumberFieldsWithChosenPrimitiveElement,
    OrderedRings,
    Orders,
    OwnedCategoryOverBaseRing,
    OwnedDivisionRings,
    OwnedFields,
    OwnedNumberFields,
    OwnedOrders,
    OwnedRings,
    OwnedRngs,
    OwnedSemirings,
    PredicateSubrings,
    PrimeFields,
    PrimeSpectra,
    PrincipalIdealDomains,
    RealApproximation,
    Rings,
    UnitInterval,
    ZariskiClosedSubobjects,
    _restore_session_ring_bindings,
    binomial,
    cos,
    cosh,
    e,
    exp,
    log,
    pi,
    sech,
    sgn,
    sin,
    sinh,
    sqrt,
    tan,
    tanh,
    zeta,
)
from sage_extensions.rings import (
    session_ring_objects as _session_ring_objects,
)
from sage_extensions.tensors import Tensor, TensorModule, tensor  # noqa: F401
from sage_extensions.utilities import (
    lmap as lmap,
)
from sage_extensions.utilities import (
    lzip as lzip,
)
from sage_extensions.utilities import (
    to_var_names as to_var_names,
)
from sage_extensions.utilities import (
    zipsum as zipsum,
)
from sage_extensions.validation import strict_checking  # noqa: F401


def load(filename: str, globals: dict | None = None, attach: bool = False) -> None:
    r"""Load a Sage file through its canonical module when it is importable.

    Package sources must not be executed into an ad-hoc namespace: that creates
    a second population of category and module classes beside the ordinary
    import population.  Resolve an importable source path to its dotted module
    name and let the installed ``sageparse`` finder own compilation and module
    identity.  Arbitrary session scripts, which have no importable module name,
    retain Sage's traditional namespace-loading behavior.
    """
    scope = _sys._getframe(1).f_globals if globals is None else globals
    source = _Path(filename).expanduser().resolve()
    module_name = None
    module_depth = -1
    conflicting_source = None
    unresolved_package_source = None
    for entry in _sys.path:
        root = _Path(entry or ".").resolve()
        try:
            relative = source.relative_to(root)
        except ValueError:
            continue
        # Canonicalize package sources in either source format.  An ordinary
        # top-level Sage script still uses Sage's execute-into-scope loader,
        # even though sageparse also makes top-level .sage files importable.
        if relative.suffix not in (".py", ".sage"):
            continue
        root_is_package = (root / "__init__.py").is_file() or (
            root / "__init__.sage"
        ).is_file()
        if root_is_package and relative.name not in ("__init__.py", "__init__.sage"):
            # This sys.path entry is itself a package directory. Names derived
            # relative to it omit that package's qualified prefix; probing
            # them with find_spec can import the same source under a second
            # top-level alias before a broader sys.path root is considered.
            # Let a broader root resolve the source without executing this
            # short alias. If none exists, fail closed below.
            parts = list(relative.with_suffix("").parts)
            if parts and all(part.isidentifier() for part in parts):
                candidate = ".".join(parts)
                if (
                    unresolved_package_source is None
                    or len(parts) > unresolved_package_source[1]
                ):
                    unresolved_package_source = (candidate, len(parts))
            continue
        if len(relative.parts) == 1 and relative.name not in (
            "__init__.py",
            "__init__.sage",
        ):
            # A source at the root of a package directory is a package module,
            # but this sys.path entry alone omits the package's parent name.
            # Do not import it under a short top-level alias. A broader import
            # root may still provide the canonical qualified name later in the
            # loop; if none does, the unresolved-package check fails closed.
            if (root / "__init__.py").is_file() or (root / "__init__.sage").is_file():
                unresolved_package_source = (source.stem, 1)
            continue
        parts = list(relative.with_suffix("").parts)
        if parts and parts[-1] == "__init__":
            parts.pop()
        if not parts or not all(part.isidentifier() for part in parts):
            continue
        candidate = ".".join(parts)
        package_parent = (
            relative.name in ("__init__.py", "__init__.sage")
            or (root / "__init__.py").is_file()
            or (root / "__init__.sage").is_file()
            or any(
                (root.joinpath(*relative.parts[:index]) / "__init__.py").is_file()
                or (root.joinpath(*relative.parts[:index]) / "__init__.sage").is_file()
                for index in range(1, len(relative.parts))
            )
        )
        if not package_parent:
            # A dotted-looking path below sys.path is not itself a package
            # contract: Sage scripts are often kept in subdirectories without
            # package initializers. Keep those on Sage's normal load route;
            # only package-owned sources must share import-module identity.
            continue
        # Only delegate when the installed sageparse finder chooses this exact
        # source; package directories may have their own loader.
        try:
            spec = _find_spec(candidate)
        except (ImportError, ModuleNotFoundError, ValueError):
            # find_spec for a dotted name may import its parent package. If
            # that package fails to initialize, do not treat the exception as
            # proof that this package source is non-importable and fall back to
            # Sage's independent exec route. Preserve the most-qualified failed
            # package candidate so the failure is reported below.
            if package_parent and (
                unresolved_package_source is None
                or len(parts) > unresolved_package_source[1]
            ):
                unresolved_package_source = (candidate, len(parts))
            continue
        if spec is None or spec.origin is None:
            # This sys.path entry did not make the source importable under the
            # candidate name (a nested path entry may be only a partial name).
            # It is not evidence of a competing canonical module.
            if package_parent and (
                unresolved_package_source is None
                or len(parts) > unresolved_package_source[1]
            ):
                unresolved_package_source = (candidate, len(parts))
            continue
        if _Path(spec.origin).resolve() == source:
            # Overlapping sys.path entries can make one file importable under
            # both its full package name and a shorter alias (for example,
            # ``pkg.mod`` and ``mod``).  The package-qualified route is the
            # canonical population; choosing the first matching path entry
            # would make identity depend on sys.path insertion order.
            if len(parts) > module_depth:
                module_name = candidate
                module_depth = len(parts)
        else:
            resolved_source = _Path(spec.origin).resolve()
            # The sageparse finder deliberately prefers a generated .py beside
            # its .sage source. Canonicalize through that selected module rather
            # than rejecting the source or executing it into a second scope.
            same_compiled_source = (
                resolved_source.parent == source.parent
                and resolved_source.stem == source.stem
                and source.suffix == ".sage"
                and resolved_source.suffix == ".py"
            )
            if same_compiled_source:
                if len(parts) > module_depth:
                    module_name = candidate
                    module_depth = len(parts)
            else:
                # A shallow alias conflict must not hide a more-qualified
                # package conflict discovered through another sys.path root.
                # Prefer the strongest ownership evidence, then name depth.
                conflict = (candidate, resolved_source, package_parent, len(parts))
                if (
                    conflicting_source is None
                    or (package_parent and not conflicting_source[2])
                    or (
                        package_parent == conflicting_source[2]
                        and len(parts) > conflicting_source[3]
                    )
                ):
                    conflicting_source = conflict
    if module_name is not None:
        # The importer is the sole owner of module execution and identity.
        # Reloading here would recreate classes in the same module object while
        # already-imported consumers retain references to the old classes,
        # reintroducing the split population this route exists to prevent.
        imported = _import_module(module_name)
    elif conflicting_source is not None and (
        conflicting_source[2]
        or (
            conflicting_source[1].parent == source.parent
            and conflicting_source[1].stem == source.stem
        )
    ):
        # Normal import resolution selected a different source for a module
        # name that this package source would otherwise claim. Falling back to
        # exec-into-scope here would create a second class population. A bare
        # session script that happens to share a dotted candidate with some
        # unrelated import keeps the traditional Sage loading behavior.
        raise ImportError(
            f"{source} is under an import root but is not the canonical source "
            f"for {conflicting_source[0]!r}; import the module selected by sageparse instead"
        )
    elif unresolved_package_source is not None:
        raise ImportError(
            f"{source} belongs to package source {unresolved_package_source[0]!r}, "
            "but the canonical importer could not resolve it; refusing duplicate execution"
        )
    if module_name is not None:
        imported = _sys.modules[module_name]
        if attach:
            from sage.repl.attach import add_attached_file as _add_attached_file

            _add_attached_file(source)
        scope.update(
            (name, value)
            for name, value in vars(imported).items()
            if not (name.startswith("__") and name.endswith("__"))
        )
    else:
        _sage_load(filename, scope, attach)
    _restore_session_ring_bindings(scope)
    scope["GradedLebesgueAlgebra"] = GradedLebesgueAlgebra
    scope["LebesgueConvolutionAlgebra"] = LebesgueConvolutionAlgebra
    scope["load"] = load


# This is deliberately last.  Internal modules may import backend names while
# they load; the public session receives only owned scalar objects, owned
# constructors, and the owned runtime names emitted by the research dialect.
_restore_session_ring_bindings(globals())
_session_rings = _session_ring_objects()
ZZ: _OwnedRingParent = _cast(_OwnedRingParent, _session_rings["ZZ"])
QQ: _OwnedRingParent = _cast(_OwnedRingParent, _session_rings["QQ"])
Integer = _language_runtime.Integer
RealNumber = _language_runtime.RealNumber
ComplexNumber = _language_runtime.ComplexNumber
matrix = _language_runtime.matrix
factorial = _language_runtime.factorial
ellipsis_range = _language_runtime.ellipsis_range
ellipsis_iter = _language_runtime.ellipsis_iter


# The catalogue constructs named lattices at import time, so it is imported
# last, after every name it uses exists.
_lazy_import(
    "sage_extensions.catalogue",
    (
        "Embeddings",
        "Involutions",
        "NamedLattices",
        "NegativeDefTwoElementary",
        "TwoElementary",
        "signature_orthogonal_sums",
        "two_elementary_orthogonal_sums",
    ),
)
_lazy_import("sage_extensions.coble", "Coble")
_lazy_import("sage_extensions.sterk", "Sterk")


_language_runtime.install(globals())
