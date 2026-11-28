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




import sageparse.preparser.research
from sage.misc.lazy_import import lazy_import as _lazy_import
from sage.repl.load import load as _sage_load

from sage_extensions import language_runtime as _language_runtime














from sage_extensions.categories.abstract_categories import *
from sage_extensions.categories.algebras import *
from sage_extensions.categories.divisors import *
from sage_extensions.categories.forms import *
from sage_extensions.categories.functions import *
from sage_extensions.categories.group.profinite import *
from sage_extensions.categories.modules import *
from sage_extensions.categories.modules.framed import *
from sage_extensions.categories.modules.framed.finitely_generated import *
from sage_extensions.categories.modules.framed.formed import *
from sage_extensions.categories.modules.group_modules import *
from sage_extensions.categories.modules.pure import *
from sage_extensions.categories.modules.pure.finitely_generated import *
from sage_extensions.categories.schemes.toric import *
from sage_extensions.categories.sets import *
from sage_extensions.categories.sets.enumerated import *
from sage_extensions.groups import *
from sage_extensions.lexicon import *
from sage_extensions.rings import *
from sage_extensions.schemes import *
from sage_extensions.static_types import *
from sage_extensions.tensors import *
from sage_extensions.categories.abstract_categories.functors import (
    DiscreteCategories,
    DiscreteCategory,
    ObjectSetFunctor,
)
from sage_extensions.categories.algebras.algebras import (
    MatrixAlgebras,
)
from sage_extensions.categories.cell_complexes import (
    CellComplexes,
    DeltaComplexes,
    PolytopalComplexes,
    SimplicialComplexes,
    SimplicialSets,
)
from sage_extensions.categories.chamber_systems import (
    ChamberSystems,
)
from sage_extensions.categories.complex_affine_spaces import (
    ComplexAffineSpaces,
    ComplexVectorSpaces,
)
from sage_extensions.categories.complex_analytic_spaces import (
    ComplexAnalyticSpaces,
)
from sage_extensions.categories.coxeter_diagrams import (
    CoxeterDiagrams as CoxeterDiagrams,
)


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
from sage_extensions.categories.graph_categories import (
    Digraphs,
    Graphs,
    LabelledDigraphs,
    LabelledGraphs,
)
from sage_extensions.categories.group.groups import (
    LieGroups,
    TopologicalGroups,
)
from sage_extensions.categories.holomorphic_atlases import (
    HolomorphicAtlases,
)
from sage_extensions.categories.hyperbolic_geometry import (
    HyperbolicPolyhedra,
    HyperbolicRationalPoints,
    HyperbolicSpaces,
    PositiveConeComponents,
)
from sage_extensions.categories.hyperbolic_lattices import (
    HyperbolicLattices,
)
from sage_extensions.categories.integral_affine_atlases import (
    IntegralAffineAtlases,
)
from sage_extensions.categories.integral_affine_collars import (
    IntegralAffineCollars,
)
from sage_extensions.categories.integral_affine_manifolds import (
    IntegralAffineManifolds,
    IntegralAffineManifoldsWithBoundary,
    IntegralAffineManifoldsWithCorners,
    SingularIntegralAffineLocalModels,
    SingularIntegralAffineSpaces,
)
from sage_extensions.categories.integral_affine_stratified_atlases import (
    IntegralAffineBoundaryAtlases,
    IntegralAffineCornerAtlases,
)
from sage_extensions.categories.isotropic_orbits import (
    DividedClassCuspIncidence,
    FlagType,
    IsotropicFlag,
    OrientedIsotropicFlag,
    RationalIsotropicFlagComplex,
)
from sage_extensions.categories.isotropic_parabolics import (
    LeviQuotientLiftAbsent,
    PrimitiveIsotropicSubobjects,
    right_coset_action,
)
from sage_extensions.categories.orthogonal_quotients import (
    general_image_certificate,
)
from sage_extensions.lattice_database import (
    card_arithmetic_group,
    card_arithmetic_group_row,
    card_arithmetic_group_tags,
    card_lattice,
    card_line_orbit_lengths,
    card_line_orbit_row,
    card_plane_orbit_lengths,
    card_plane_orbit_row,
    card_polarization_degrees,
    card_polarization_lattice,
    card_polarization_row,
    card_provenance,
)
from sage_extensions.categories.lattice_centralizers import (
    IsometryPrimitiveExtension,
)
from sage_extensions.categories.lattice_morphisms import (
    LatticeEmbedding,
    LatticeIsometry,
    LatticeMor,
    LatticeMorphism,
)
from sage_extensions.categories.definite_lattices import (
    definite_indecomposable_summands,
)
from sage_extensions.categories.lattices import (
    DefiniteLattices,
    EvenLattices,
    EvenTwoElementaryLattices,
    FiniteRankLattices,
    IsotropicReductions,
    Lattices,
    OrientedIsotropicFlags,
    NoncrystallographicRootLattices,
    NondegenerateLattices,
    NotPrimitiveError,
    RootLattices,
    TransvectionOutsideTheLattice,
    nikulin_invariants,
    signature_pair,
    signature_pairs,
)
from sage_extensions.categories.manifold_dimension_strata import (
    ManifoldsOfDimensionAtMost,
    PureDimensionalManifolds,
)
from sage_extensions.categories.manifolds import (
    ComplexManifolds,
    CoverageUndecided,
    DifferentiableManifolds,
    RiemannianManifolds,
    SmoothManifolds,
    TopologicalManifolds,
)
from sage_extensions.categories.vector_bundles import (
    SmoothVectorBundles,
)
from sage_extensions.categories.manifolds_with_boundary import (
    RealCkManifoldsWithBoundary,
    RealCkManifoldsWithCorners,
    SmoothManifoldsWithBoundary,
    SmoothManifoldsWithCorners,
    TopologicalManifoldsWithBoundary,
    TopologicalManifoldsWithCorners,
)
from sage_extensions.categories.metric_affine_spaces import (
    EuclideanSpaces,
    SphericalSpaces,
)
from sage_extensions.categories.modules.hodge_structures import (
    FilteredModules,
    HodgeStructures,
    MixedHodgeStructures,
    PolarizedHodgeStructures,
)
from sage_extensions.categories.modules.pure.modules import (
    MatrixEndomorphismSpaces,
    MatrixSpaces,
)
from sage_extensions.categories.orbifolds import (
    ComplexOrbifolds,
    Orbifolds,
    RiemannianOrbifolds,
)
from sage_extensions.categories.polyhedral_cones import (
    RationalPolyhedralCones,
)
from sage_extensions.categories.rational_integral_stabilizers import (
    FiniteCommensurabilityQuotient,
    IntegralStructureAction,
)
from sage_extensions.categories.real_affine_spaces import (
    AffineSpacesWithLattice,
    RealAffineSpaces,
    RealVectorSpaces,
)
from sage_extensions.categories.real_ck_atlases import (
    RealCkAtlases,
)
from sage_extensions.categories.real_ck_manifolds import (
    RealCkManifolds,
)
from sage_extensions.categories.satake_diagrams import (
    SatakeDiagrams as SatakeDiagrams,
)
from sage_extensions.categories.schemes.degeneration_central_fibers import (
    DegenerationCentralFibers,
)
from sage_extensions.categories.sets.finite_graded_posets import (
    FiniteGradedPosets,
)
from sage_extensions.categories.stratified_atlases import (
    RealCkBoundaryAtlases,
    RealCkCornerAtlases,
    TopologicalBoundaryAtlases,
    TopologicalCornerAtlases,
)
from sage_extensions.categories.topological_atlases import (
    TopologicalAtlases,
)
from sage_extensions.categories.triangulations import (
    ChosenTriangulations,
)

_lazy_import(
    "sage_extensions.categories.schemes.cyclic_covers",
    "CyclicCovers",
)
from sage_extensions.categories.algebras.subalgebras import (
    GeneratedSubalgebras,
)
from sage_extensions.categories.algebras.algebra_ideals import (
    GeneratedAlgebraIdeals,
)
from sage_extensions.categories.algebras.graded_lie_algebras import (
    GradedLieAlgebras,
)
from sage_extensions.categories.algebras.graded_nonassociative_algebras import (
    GradedNonassociativeAlgebras,
)
from sage_extensions.categories.fundamental_groupoids import (
    FundamentalGroupoid,
    FundamentalGroupoids,
)
from sage_extensions.categories.pointed_topological_spaces import (
    TopologicalSpaceCoslices,
)
from sage_extensions.categories.topological_spaces import (
    ContinuousMap,
    TopologicalSpaceMor,
    TopologicalSpaces,
)
from sage_extensions.categories.vector_orbits import (
    VectorPrimitiveExtension,
)
from sage_extensions.categories.vinberg_invariants import (
    VinbergInvariantMatrices,
    reflection_cosines,
)
from sage_extensions.logic import (
    AtomicProposition,
    Predicate,
    Propositions,
    Unknown,
    ask,
)
from sage_extensions.rings import (
    _restore_session_ring_bindings,
)
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
from sage_extensions.validation import strict_checking


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



        if relative.suffix not in (".py", ".sage"):
            continue
        root_is_package = (root / "__init__.py").is_file() or (
            root / "__init__.sage"
        ).is_file()
        if root_is_package and relative.name not in ("__init__.py", "__init__.sage"):






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




            continue


        try:
            spec = _find_spec(candidate)
        except (ImportError, ModuleNotFoundError, ValueError):





            if package_parent and (
                unresolved_package_source is None
                or len(parts) > unresolved_package_source[1]
            ):
                unresolved_package_source = (candidate, len(parts))
            continue
        if spec is None or spec.origin is None:



            if package_parent and (
                unresolved_package_source is None
                or len(parts) > unresolved_package_source[1]
            ):
                unresolved_package_source = (candidate, len(parts))
            continue
        if _Path(spec.origin).resolve() == source:





            if len(parts) > module_depth:
                module_name = candidate
                module_depth = len(parts)
        else:
            resolved_source = _Path(spec.origin).resolve()



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




        imported = _import_module(module_name)
    elif conflicting_source is not None and (
        conflicting_source[2]
        or (
            conflicting_source[1].parent == source.parent
            and conflicting_source[1].stem == source.stem
        )
    ):





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






FormulaFunction = _language_runtime.FormulaFunction
Integer = _language_runtime.Integer
RealNumber = _language_runtime.RealNumber
ComplexNumber = _language_runtime.ComplexNumber
matrix = _language_runtime.matrix
factorial = _language_runtime.factorial
ellipsis_range = _language_runtime.ellipsis_range
ellipsis_iter = _language_runtime.ellipsis_iter




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








__all__ = tuple(sorted(name for name in globals() if not name.startswith("_")))
_language_runtime.register_session_names(__all__)
