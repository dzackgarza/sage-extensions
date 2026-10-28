r"""Lattices.

Sage does not define a category of (quadratic-form) lattices.  Sage's
:func:`~sage.modules.free_quadratic_module_integer_symmetric.IntegralLattice`
constructs a free quadratic module; the order-theoretic category is
:class:`~sage.categories.lattice_posets.LatticePosets`.  This module
owns the missing category, following Sage's category primer
(``super_categories``, ``ParentMethods``, ``ElementMethods``) and the
``Category_over_base_ring`` parameterization.  A lattice is a free
`R`-module with a symmetric form, built through ``FormModules(R)``: it is
the module, all the way down to its underlying set, and holds no second
module.  The classcall is the category over a ring.  Objects are
constructed by calling that category.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Hashable, Mapping, Sequence
from dataclasses import dataclass
from functools import cache
from typing import TYPE_CHECKING, overload
from sage_extensions.categories.abstract_categories.mor_foundation import object_level

if TYPE_CHECKING:
    from sage.categories.category import Category

    from sage_extensions.owned_category import ConstructionData

from sage.arith.misc import gcd
from sage.categories.category_with_axiom import all_axioms
from sage.misc.abstract_method import abstract_method
from sage.combinat.root_system.cartan_type import CartanType
from sage.misc.cachefunc import cached_function, cached_method
from sage.misc.latex import latex
from sage.misc.repr import repr_lincomb
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.element import RingElement
from sage.structure.element import parent as element_parent
from sage.structure.parent import Parent

from sage_extensions.categories import lattice_engines
from sage_extensions.categories._lattice import (
    _block_offsets,
    _block_position,
    _colimit_lattice,
    _discriminant_of_gram,
    _generating_set_for,
    _gram_is_even,
    _IdentityGram,
    _lattice,
    _lattice_from_gram_tensor,
    _lattice_latex,
    _lattice_object,
    _lattice_on_gram,
    _nested_gram_tensor,
    _normalized_lattice_names,
    _orthogonal_sum,
    _signature_pair_of_gram,
    _tensor_product_lattice,
    signature_pair,
)
from sage_extensions.categories._lattice import (
    signature_pairs as signature_pairs,
)
from sage_extensions.categories.abstract_categories.direct_sum_objects import (
    DirectSumObjects,
)
from sage_extensions.categories.abstract_categories.mor_categories import (
    IsoCategoryConstruction,
    MonoCategoryConstruction,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.objects import OwnedCategory
from sage_extensions.categories.group.magmas import Monoids
from sage_extensions.categories.abstract_categories.arrow_categories import (
    CosliceCategory,
    _WalkingArrowFunctorCategory,
)
from sage_extensions.categories.abstract_categories.products import _FiniteSequenceFunctorCategory
from sage_extensions.categories.definite_lattices import (
    _babai,
    _bkz_reduction,
    _center_density,
    _close_vectors,
    _closest_vector,
    _contact_polytope,
    _covering_radius,
    _exact_cvp_engine,
    _first_unrepresented_value,
    _gaussian_heuristic,
    _hadamard_ratio,
    _hermite_invariant,
    _hkz_reduction,
    _kissing_number,
    _lll_reduction,
    _minimum,
    _norm_two_root_types,
    _packing_density,
    _packing_radius,
    _reflective_root_system_components,
    _root_sublattice,
    _roots,
    _roots_of_square,
    _shortest_vectors,
    _square_coordinate_bound,
    _successive_minima,
    _theta_series,
    _vectors_of_square,
    _vectors_of_square_and_divisibility,
    _voronoi_cell,
    _voronoi_facets,
    _voronoi_relevant_vectors,
)
from sage_extensions.categories.group.groups import (
    Groups,
    OwnedGroups,
    _engine_group,
)
from sage_extensions.categories.group.predicate_subgroups import (
    PredicateSubgroups,
    PreimageSubgroups,
)
from sage_extensions.categories.isotropic_orbits import (
    IsotropicFlag,
    _isotropic_flag_locus,
    _isotropic_sublattice_locus,
    _primitive_isotropic_sublattice_locus,
)
from sage_extensions.categories.lattice_morphisms import (
    LatticeEmbeddingMor,
    LatticeIsometryMethods,
    LatticeIsometryMor,
    LatticeMor,
    _LatticeCore,
    _lattice_embedding_mor,
    _lattice_isometry_mor,
    _lattice_mor,
    _number_field_spinor_norm_representative,
    _rational_spinor_norm_representative,
)
from sage_extensions.categories.modules.base_change import (
    _base_change_element,
)
from sage_extensions.categories.modules.framed.formed.discriminant_modules import (
    DiscriminantBilinearModules,
    DiscriminantQuadraticModules,
    _discriminant_module,
)
from sage_extensions.categories.modules.framed.formed.form_modules import (
    BilinearFormModules,
    FormModules,
    FreeFormModules,
)
from sage_extensions.categories.modules.framed.formed.torsion_form_modules import (
    _even_lattice_genus_gram,
    _form_gram_on,
    _relations_among_generators,
    _torsion_form_isometry,
    _torsion_form_modules,
)
from sage_extensions.categories.modules.framed.framed_free_modules import (
    _module_subobject_constructor_data,
    _span_basis_elements,
)
from sage_extensions.categories.modules.module_morphisms.module_morphisms import (
    _solve_preimage_integrally,
)
from sage_extensions.categories.modules.pure.modules import (
    Modules,
    ModulesOverIntegralDomains,
    ModuleSubobjectConstruction,
    ModuleSubobjects,
    TensorProductModules,
)
from sage_extensions.categories.rings.ring_foundation import (
    CommutativeRings,
    OwnedCategoryOverBaseRing,
    OwnedRings,
    PrimeFields,
    _engine_element,
    _engine_ring,
    _own_ring,
    _owned_engine_element,
    _OwnedRingParent,
    _owned_integers,
    _owned_rationals,
)
from sage_extensions.categories.sets.cardinals import Cardinal, cardinal
from sage_extensions.categories.sets.finite_families import finite_family
from sage_extensions.categories.sets.finite_ordered_sets import (
    FiniteOrderedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    IndexedFamily,
    finite_indexed_family,
    finite_indexed_family_from_values,
    indexed_family,
)
from sage_extensions.categories.sets.set_categories import (
    NN,
    FiniteSets,
    Sets,
)
from sage_extensions.categories.vector_orbits import (
    VectorPrimitiveExtension,
    _definite_complement_extensions,
    _gluing_route_discriminant_classes,
    _stable_complement_root_reflections,
)
from sage_extensions.logic import AtomicProposition, Predicate, negation
from sage_extensions.owned_category_bases import CategoryWithAxiom
from sage_extensions.refine import refine
from sage_extensions.tensors.tensor import (
    Tensor,
    _engine_component_matrix,
    tensor,
)


def nikulin_invariants(rank, discriminant_length, delta):
    r"""Return \((r,a,\delta)\) as a point of \(\mathbb N^3\)."""

    return (NN**3)((int(rank), int(discriminant_length), int(delta)))


_Rings = OwnedRings()

for _lattice_property_axiom in ("Indecomposable", "Twisted", "Untwisted"):
    if _lattice_property_axiom not in all_axioms:
        all_axioms.add(_lattice_property_axiom)


@dataclass(frozen=True)
class LatticeConstruction:
    r"""One expression in an unbounded lattice construction enumeration.

    ``factors`` identify the input expressions and ``witness`` retains the
    inclusion for an overlattice. Equal lattices may occur by different paths.
    """

    lattice: object
    operation: str
    factors: tuple["LatticeConstruction", ...] = ()
    witness: object | None = None


_INDECOMPOSABLE_NAMES = {}


# This fixed integral presentation was published in Sage's named-lattice
# catalogue (poeschko/sage@3014850b7c, special_lattices.py, Leech entry). Hecke's
# `leech_lattice()` remains the independent maintained oracle: it constructs
# the same lattice by the Conway--Sloane holy construction.
_LEECH_GRAM_ROWS = (
    (8, 4, 4, 4, 4, 4, 4, 2, 4, 4, 4, 2, 4, 2, 2, 2, 4, 2, 2, 2, 0, 0, 0, -3),
    (4, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 1, 1, 2, 1, 0, 0, -1),
    (4, 2, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 1, 2, 2, 1, 1, 1, 0, 0, -1),
    (4, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 1, 2, 1, 1, 0, 0, -1),
    (4, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, -1),
    (4, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 1, 2, 2, 1, 1, 2, 1, 2, 1, 0, 0, 0, -1),
    (4, 2, 2, 2, 2, 2, 4, 2, 2, 2, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 0, 0, 0, -1),
    (2, 2, 2, 2, 2, 2, 2, 4, 1, 1, 1, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 0, 0, 1),
    (4, 2, 2, 2, 2, 2, 2, 1, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, -1),
    (4, 2, 2, 2, 2, 2, 2, 1, 2, 4, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 0, 1, 0, -1),
    (4, 2, 2, 2, 2, 2, 2, 1, 2, 2, 4, 2, 2, 1, 2, 1, 2, 1, 2, 1, 0, 0, 1, -1),
    (2, 2, 2, 2, 1, 1, 1, 2, 2, 2, 2, 4, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1, 1, 1),
    (4, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 1, 4, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, -1),
    (2, 2, 1, 1, 2, 2, 1, 2, 2, 2, 1, 2, 2, 4, 2, 2, 1, 2, 2, 2, 2, 2, 1, 1),
    (2, 1, 2, 1, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 4, 2, 1, 2, 2, 2, 2, 1, 2, 1),
    (2, 1, 1, 2, 2, 1, 1, 2, 2, 1, 1, 2, 2, 2, 2, 4, 1, 2, 2, 2, 2, 1, 1, 1),
    (4, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 1, 1, 1, 4, 2, 2, 2, 1, 1, 1, -1),
    (2, 1, 2, 1, 2, 1, 1, 2, 2, 2, 1, 2, 1, 2, 2, 2, 2, 4, 2, 2, 2, 2, 1, 1),
    (2, 1, 1, 2, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2, 2, 2, 2, 2, 4, 2, 2, 1, 2, 1),
    (2, 2, 1, 1, 2, 1, 2, 2, 2, 1, 1, 2, 1, 2, 2, 2, 2, 2, 2, 4, 2, 1, 1, 1),
    (0, 1, 1, 1, 1, 0, 0, 2, 1, 0, 0, 2, 1, 2, 2, 2, 1, 2, 2, 2, 4, 2, 2, 2),
    (0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 4, 2, 2),
    (0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 2, 4, 2),
    (-3, -1, -1, -1, -1, -1, -1, 1, -1, -1, -1, 1, -1, 1, 1, 1, -1, 1, 1, 1, 2, 2, 2, 4),
)


class LatticeMorCategoryConstruction(MorCategoryConstruction):
    r"""The strict form-preserving Mor categories of lattices."""

    def fixed_category_class(self):
        return LatticeMor


class LatticeMonoCategoryConstruction(MonoCategoryConstruction):
    r"""The form-preserving monomorphisms of lattices."""

    def fixed_category_class(self):
        return LatticeEmbeddingMor


class LatticeIsoCategoryConstruction(IsoCategoryConstruction):
    r"""The isometries of lattices."""

    def fixed_category_class(self):
        return LatticeIsometryMor


def _gram_key(gram):
    rank = int(gram.tensor_shape()[0])
    return tuple(
        tuple(int(gram[row, column]) for column in range(rank)) for row in range(rank)
    )


def _register_indecomposable_gram(name, gram):
    r"""Register an exact Gram matrix under its indecomposable display name."""
    _INDECOMPOSABLE_NAMES.setdefault(_gram_key(gram), str(name))


def _register_indecomposable_gram_rows(name, rows):
    r"""Register integral Gram rows without constructing the lattice or its tensor."""
    _INDECOMPOSABLE_NAMES.setdefault(
        tuple(tuple(int(entry) for entry in row) for row in rows),
        str(name),
    )


def _register_indecomposable(name, lattice):
    r"""Register an indecomposable live lattice by exact Gram equality."""
    if lattice.is_decomposable():
        raise ValueError(
            f"cannot register {lattice!r} under the name {name!r}: only an indecomposable lattice names a single Gram block, and this lattice decomposes as an orthogonal sum"
        )
    _register_indecomposable_gram(name, lattice.gram_tensor())


def _indecomposable_name(lattice):
    r"""Return the registered exact or scalar-twist name, if one exists."""
    gram = lattice.gram_tensor().change_ring(_owned_integers())
    exact = _INDECOMPOSABLE_NAMES.get(_gram_key(gram))
    if exact is not None:
        return exact
    rank = int(gram.tensor_shape()[0])
    content = gcd(gram[row, column] for row in range(rank) for column in range(rank))
    for scale in (content, -content):
        if scale in (0, 1, -1):
            continue

        rank = gram.tensor_shape()[0]
        integers = gram.base_ring()
        divisor = int(scale)
        untwisted = tensor(
            integers,
            (),
            (rank, rank),
            [
                [integers(int(gram[i, j]) // divisor) for j in range(rank)]
                for i in range(rank)
            ],
        )
        name = _INDECOMPOSABLE_NAMES.get(_gram_key(untwisted))
        if name is not None:
            return f"{name}({scale})"
    return None


def _overlattice_inclusions(form):
    r"""Return the overlattice inclusions glued along the isotropic subgroups of ``form``.

    Nikulin's correspondence is a bijection, so the inclusions are indexed
    by the isotropic subgroups, and each is built once, when it is asked for.
    An inclusion is a member exactly when this set built it: an overlattice
    built elsewhere has another codomain object, so it is another arrow.
    """
    isotropic = form.isotropic_subgroups()
    glue = isotropic.enumeration()
    positions = {}

    @cache
    def element_at(index):
        inclusion = form.overlattice_from_isotropic_subobject(glue(index))
        positions[id(inclusion)] = index
        return inclusion

    def index_of(inclusion):
        return positions.get(id(inclusion))

    return FiniteOrderedSets().from_indexed(
        isotropic.index_set(),
        element_at,
        index_of=index_of,
        contains=lambda inclusion: index_of(inclusion) is not None,
        name=f"overlattice inclusions of {form.source_lattice()}",
    )


@cached_function(
    key=lambda module, basis, root_system_type_name=None: (
        id(module),
        basis,
        root_system_type_name,
    )
)
def _lattice_subobject_spanning(module, basis, root_system_type_name=None):
    r"""Return the canonical lattice subobject on a finite span basis.

    The subobject is the lattice on the free module framed by the span basis,
    with the restricted Gram \(b(v_i,v_j)\), built in one construction that
    retains its inclusion into ``module``.  A ``root_system_type_name`` places
    it in ``RootLattices`` with that name of the type of the root system as its
    datum.
    """
    match root_system_type_name:
        case None:
            return _lattice_subobject_on_basis(module, basis, (), {})
        case _:
            return _lattice_subobject_on_basis(
                module, basis, (RootLattices(),), {"root_system_type_name": root_system_type_name}
            )


def _lattice_subobject_on_basis(module, basis, extra_categories, construction_data):
    r"""The lattice subobject framed by ``basis``, placed also in ``extra_categories``.

    ``construction_data`` is the datum each extra category introduces, passed
    to its constructor: a root-system type name for ``RootLattices``.
    """
    ring = module.base_ring()
    basis_elements = tuple(basis)
    rank = len(basis_elements)
    labels, embedded, lift = _module_subobject_constructor_data(module, basis)
    source_module = ring._fresh_free_module_on(labels)
    match rank:
        case 0:
            gram = _IdentityGram(source_module)
        case _:
            gram = tensor(
                ring,
                (),
                (rank, rank),
                (
                    module.b(left, right)
                    for left in basis_elements
                    for right in basis_elements
                ),
            )

    def inclusion_factory(source):
        # The inclusion is built from its generator images in its own Mor (``CON-17``).
        return source.Emb(module)(embedded)

    return _lattice_object(
        Lattices(ring),
        source_module,
        gram,
        extra_categories=extra_categories,
        construction_data=construction_data,
        subobject_construction=ModuleSubobjectConstruction(
            ambient=module,
            generator_images=embedded,
            lift=lift,
            inclusion_factory=inclusion_factory,
        ),
    )


class LocalGenusSymbol:
    r"""The Conway--Sloane Jordan-block invariants at one finite prime.

    For odd ``p`` each block is ``(m,n,d)``.  At ``p=2`` each block is
    ``(m,n,s,d,o)``.  These integer tuples are the mathematical local-symbol
    data; Sage's ``Genus_Symbol_p_adic_ring`` is reconstructed privately when
    one of its exact algorithms is used.
    """

    def __init__(self, prime, jordan_blocks) -> None:
        integers = _owned_integers()
        self._prime = integers(prime)
        if not self._prime.is_prime():
            raise ValueError(
                f"cannot form a local genus symbol at {prime!r}: a local genus symbol is taken at a prime p, and {prime!r} is not prime"
            )
        self._jordan_blocks = tuple(
            tuple(integers(entry) for entry in block) for block in jordan_blocks
        )

    def prime(self):
        return self._prime

    def jordan_blocks(self):
        return self._jordan_blocks

    symbol = jordan_blocks

    @cached_method
    def _engine(self):
        from sage.quadratic_forms.genera.genus import Genus_Symbol_p_adic_ring

        integers = self.prime().parent()
        return Genus_Symbol_p_adic_ring(
            _engine_element(integers, self.prime()),
            [
                [_engine_element(integers, entry) for entry in block]
                for block in self.jordan_blocks()
            ],
        )

    def excess(self):
        integers = self.prime().parent()
        return _owned_engine_element(integers, SageZZ(self._engine().excess()))

    def level(self):
        integers = self.prime().parent()
        return _owned_engine_element(integers, SageZZ(self._engine().level()))

    def norm(self):
        integers = self.prime().parent()
        return _owned_engine_element(integers, SageZZ(self._engine().norm()))

    def number_of_blocks(self):
        return self.prime().parent()(len(self.jordan_blocks()))

    @cached_method
    def canonical_symbol(self):
        r"""Return the canonical Conway--Sloane symbol of this local genus.

        For odd ``p`` the Jordan symbol is already canonical.  At ``p = 2``
        oddity fusion and sign walking reduce it to the canonical symbol, and
        ``ZZ_p``-equivalence is equality of the canonical ``p``-adic symbols
        [CS10, Ch. 15, §7.6].
        """
        integers = self.prime().parent()
        return tuple(
            tuple(_owned_engine_element(integers, SageZZ(entry)) for entry in block)
            for block in self._engine().canonical_symbol()
        )

    def __eq__(self, other):
        return (
            isinstance(other, LocalGenusSymbol)
            and self.prime() == other.prime()
            and self.jordan_blocks() == other.jordan_blocks()
        )

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return (
            f"Local genus at {self.prime()} with Jordan blocks {self.jordan_blocks()}"
        )


class NotPrimitiveError(ValueError):
    r"""Raised when an operation requiring a primitive lattice vector is given a nonprimitive one."""


class _Genus(Sets().ObjectType):
    r"""The genus of a nondegenerate integral lattice ``L`` of finite rank.

    The genus of ``L`` is the set of isometry classes of lattices ``L'``
    with ``L'_v`` isometric to ``L_v`` at every place ``v`` [PS24, Def.
    1.9.1].  ``lean-categories`` states it as the fibre of
    ``isometryClassToGenus`` over the genus of ``L``
    (``LeanCategories/Lattices/Valued/LocalGlobal.lean``: ``SameGenus``,
    ``IntegralLatticeGenus``, ``isometryClassToGenus``).  The set is finite
    [PS24, Cor. 1.10.4]; ``lean-categories`` proves the finiteness for
    positive definite lattices only (``genus_finite``).  Each point is
    represented by a lattice in its class, the cardinality is the class
    number [PS24, Def. 1.10.5], and the determinant and the parity are the
    same for every member [PS24, Prop. 1.9.2].

    An engine realizing objects of ``FiniteSets()`` (`CAT-28`): the datum is
    ``L``, construction stores it, and the representatives of the classes
    are computed on the first request.
    """

    def __init__(self, lattice) -> None:
        self._lattice = lattice
        super().__init__(category=FiniteSets(), facade=True)

    def representative(self):
        r"""Return the lattice whose genus this is."""
        return self._lattice

    def signature_pair(self):
        r"""Return the signature pair ``(t_+, t_-)`` shared by every member."""
        return self._lattice.signature_pair()

    def determinant(self):
        r"""Return the determinant shared by every member [PS24, Prop. 1.9.2]."""
        return self._lattice.determinant()

    def is_even(self) -> bool:
        r"""Return whether the members are even; parity is the same for every member [PS24, Prop. 1.9.2]."""
        return bool(self._lattice.is_even())

    def is_odd(self) -> bool:
        r"""Return whether the members are odd."""
        return not self.is_even()

    def discriminant_form(self):
        r"""Return the discriminant form of a member: quadratic for an even genus, bilinear for an odd one."""
        return self._lattice.discriminant_group()

    def exists(self) -> bool:
        r"""Return ``True``: a genus contains the class of the lattice it is the genus of.

        ``lean-categories``: ``isometryClassToGenus_surjective``
        (``LeanCategories/Lattices/Valued/LocalGlobal.lean``).
        """
        return True

    @cached_method
    def _engine(self):
        r"""Sage's global genus symbol of the representative, private computation data."""
        from sage.quadratic_forms.genera.genus import Genus as SageGenus

        return SageGenus(
            _engine_component_matrix(self._lattice.gram_tensor()).change_ring(SageZZ)
        )

    @cached_method
    def local_symbol(self, prime):
        r"""Return the canonical ``ZZ_p`` genus symbol of the members at ``prime``."""
        integers = _owned_integers()
        prime = integers(prime)
        symbol = self._engine().local_symbol(_engine_element(integers, prime))
        return LocalGenusSymbol(
            prime,
            tuple(
                tuple(_owned_engine_element(integers, SageZZ(entry)) for entry in block)
                for block in symbol.canonical_symbol()
            ),
        )

    def excess(self, prime):
        return self.local_symbol(prime).excess()

    def level(self, prime):
        return self.local_symbol(prime).level()

    @cached_method
    def mass(self):
        r"""Return the Smith--Minkowski--Siegel mass of a definite genus.

        The mass is ``sum_i 1/|O(L_i)|`` over the classes of the genus
        [Conway--Sloane, *Low-dimensional lattices IV*, eq. (1);
        ``references/literature/lattice-research/conway1988mass.md`` l.13-16].
        Sage's ``GenusSymbol_global_ring.mass`` (read in the ``sage-stubs``
        source checkout, ``genus.py:3175``) restricts only to definite genera
        and special-cases rank 1, so rank 2 is computed by the same formula.
        """
        from sage.rings.rational_field import QQ as SageQQ

        signature = self.signature_pair()
        positive, negative = signature.first(), signature.second()
        positive_is_zero = (positive == cardinal(0)) is True
        negative_is_zero = (negative == cardinal(0)) is True
        if not positive_is_zero and not negative_is_zero:
            raise ValueError(
                f"the Smith--Minkowski--Siegel mass of {self!r} is not defined: the mass is a finite sum only for a definite genus, and this genus has signature ({positive}, {negative})"
            )
        return _owned_engine_element(_owned_rationals(), SageQQ(self._engine().mass()))

    @cached_method
    def spinor_genus_count(self):
        r"""Return the number of improper spinor genera in this genus, a power of 2 [CS99, Ch. 15, §9.1].

        Defined here for rank at least 3 [CS99, Ch. 15, §3.5, l.11778]; Sage's
        ``spinor_generators(proper=False)`` on the genus symbol computes it.
        """
        integers = _owned_integers()
        rank = int(self._lattice.module_rank())
        assert rank >= 3, (
            f"the spinor-genus count of {self!r} is taken here in rank at least three, and the rank is {rank}"
        )
        return integers(2 ** len(self._engine().spinor_generators(proper=False)))

    def theta_series(self, precision=20, variable="q"):
        r"""Return the theta series of this definite genus.

        It is the average of the theta series of the classes weighted by the
        reciprocal orders of their orthogonal groups,
        ``theta_gen = (sum_i theta_{L_i} / |O(L_i)|) / (sum_i 1 / |O(L_i)|)``
        over one lattice ``L_i`` from each class, each ``theta_{L_i}`` with the
        exponent ``b(x, x)`` of a lattice's ``theta_series``.  Its coefficients
        are rational.  By the Siegel--Weil formula it is the Eisenstein
        component of the theta series of every member.
        """
        signature = self.signature_pair()
        positive_is_zero = (signature.first() == cardinal(0)) is True
        negative_is_zero = (signature.second() == cardinal(0)) is True
        assert positive_is_zero or negative_is_zero, (
            f"the theta series of {self!r} is a power series only for a definite genus, and this genus has signature ({signature.first()}, {signature.second()})"
        )
        rationals = self._lattice.base_ring().fraction_field()
        series_ring = rationals.power_series_ring(variable)
        weights = indexed_family(
            self.representatives(),
            lambda member: (
                rationals.one()
                / rationals(int(member.orthogonal_group().cardinality()))
            ),
        )
        weighted = sum(
            (
                weight
                * series_ring(
                    member.theta_series(precision=precision, variable=variable)
                )
                for member, weight in weights.items()
            ),
            series_ring.zero(),
        )
        return weighted * (rationals.one() / sum(weights.values(), rationals.zero()))

    def local_density(self, prime, value):
        r"""Return the local density ``beta_p(L, m)`` of a member ``L`` at ``prime`` for ``value``.

        ``beta_p(L, m) = lim_k p^{k(1-n)} #{x in L/p^k L : b(x, x) = m mod p^k}``
        in rank ``n``; it depends only on ``L tensor ZZ_p``, so on the genus.
        """
        from sage.rings.rational_field import QQ as SageQQ

        integers = _owned_integers()
        density = _local_density(
            self._engine_form(),
            _engine_element(integers, integers(prime)),
            _engine_element(integers, integers(value)),
        )
        return _owned_engine_element(_owned_rationals(), SageQQ(density))

    def siegel_eisenstein_coefficient(self, value):
        r"""Return Siegel's product ``a_E(m)`` of the local densities of this definite genus at ``value``.

        For a definite member ``L`` of rank ``n >= 2``, ``Q(x) = b(x, x)``
        taken positive (``-b`` on a negative definite genus) and ``D`` the
        determinant of ``Q``'s Gram matrix, the product is computed in four
        steps.

        1. The real density is ``beta_oo(m) = n w_n D^{-1/2} m^{(n-2)/2} / 2``
           with ``w_n = pi^{n/2} / Gamma(n/2 + 1)`` the volume of the unit
           ``n``-ball: Siegel, Ann. of Math. (2) 36 (1935), Hilfssatz 26,
           pp. 554--555, as stated in Hanke, *Local densities and explicit
           bounds for representability by a quadratic form*, Duke Math. J.
           124 (2004), (5.5).  Section and equation numbers of Hanke are
           those of his preprint, web.math.princeton.edu/~jonhanke/Web-02/
           Local-Densities.
        2. At a prime ``p`` not dividing ``2 m D`` the density is
           ``beta_p(m) = p^{1-n} #{x mod p : Q(x) = m mod p}``, and Hanke,
           Lemma 9.1 counts the solutions: ``1 - chi(p) p^{-n/2}`` with
           ``chi`` the character of ``(-1)^{n/2} D`` for even ``n``, and
           ``1 + chi(p) p^{(1-n)/2}`` with ``chi`` the character of
           ``(-1)^{(n-1)/2} m D`` for odd ``n``.  With ``k = n/2``,
           respectively ``k = (n-1)/2``, and ``S`` the primes dividing
           ``2 m D``, the product over ``p`` not in ``S`` is
           ``1 / L^S(k, chi)`` for even ``n`` and
           ``L^S(k, chi) / zeta^S(2k)`` for odd ``n``, since
           ``1 + x = (1 - x^2) / (1 - x)``; ``L^S`` and ``zeta^S`` omit the
           Euler factors at ``S``.  The ``L``-values are exact through
           ``sage.quadratic_forms.special_values``, which evaluates
           Iwasawa, *Lectures on p-adic L-functions* (1972), pp. 16--17.
        3. At each ``p`` in ``S`` the density is :meth:`local_density`,
           the limit of Hanke, (5.2).
        4. Siegel's Hauptsatz (Siegel 1935; Hanke, (5.3) for ``n >= 3``)
           equates the product of all densities with the coefficient of
           ``q^m`` of :meth:`theta_series`, and halves the product when
           ``n = 2``.  Rank 1 is outside the theorem, which requires the
           number of variables to exceed 1.

        The value is rational: the powers of ``pi`` and the square roots
        of steps 1 and 2 cancel.
        """
        from sage.arith.misc import (
            fundamental_discriminant,
            kronecker_symbol,
            prime_divisors,
        )
        from sage.functions.gamma import gamma
        from sage.misc.misc_c import prod
        from sage.quadratic_forms.special_values import (
            quadratic_L_function__exact,
            zeta__exact,
        )
        from sage.rings.rational_field import QQ as SageQQ
        from sage.symbolic.constants import pi
        from sage.symbolic.ring import SR

        signature = self.signature_pair()
        positive, negative = int(signature.first()), int(signature.second())
        assert positive == 0 or negative == 0, (
            f"the Siegel product of {self!r} is the Eisenstein coefficient of a definite genus, and this genus has signature ({positive}, {negative})"
        )
        rank = positive + negative
        assert rank >= 2, (
            f"Siegel's Hauptsatz for {self!r} requires at least 2 variables, and this genus has rank {rank}"
        )
        sign = 1 if negative == 0 else -1
        integers = _owned_integers()
        rationals = _owned_rationals()
        m = _engine_element(integers, integers(value))
        assert m >= 1, (
            f"the Siegel product of {self!r} is taken at a positive integer, not at {m}"
        )
        determinant = abs(_engine_element(integers, integers(self.determinant())))
        exceptional = prime_divisors(2 * m * determinant)

        # Step 1: the real density, Siegel's Hilfssatz 26 (Hanke (5.5)).
        half_rank = SageQQ(rank) / 2
        unit_ball_volume = pi**half_rank / gamma(half_rank + 1)
        real_density = (
            rank
            * unit_ball_volume
            / 2
            * SR(determinant) ** (-SageQQ.one() / 2)
            * SR(m) ** (half_rank - 1)
        )

        # Step 2: the primes outside S, by Hanke's Lemma 9.1 as L-values.
        match rank % 2:
            case 0:
                k = rank // 2
                character = fundamental_discriminant((-1) ** k * determinant)
                partial_l_value = quadratic_L_function__exact(k, character) * prod(
                    1 - SageQQ(kronecker_symbol(character, p)) / p**k
                    for p in exceptional
                )
                generic_density = 1 / partial_l_value
            case _:
                k = (rank - 1) // 2
                character = fundamental_discriminant((-1) ** k * m * determinant)
                partial_l_value = quadratic_L_function__exact(k, character) * prod(
                    1 - SageQQ(kronecker_symbol(character, p)) / p**k
                    for p in exceptional
                )
                partial_zeta_value = zeta__exact(2 * k) * prod(
                    1 - SageQQ.one() / p ** (2 * k) for p in exceptional
                )
                generic_density = partial_l_value / partial_zeta_value

        # Step 3: the primes in S, as local densities of the positive form.
        positive_value = _owned_engine_element(integers, sign * m)
        exceptional_density = prod(
            _engine_element(
                rationals,
                self.local_density(_owned_engine_element(integers, p), positive_value),
            )
            for p in exceptional
        )

        # Step 4: Siegel's Hauptsatz, with its factor 1/2 in two variables.
        hauptsatz_factor = SageQQ.one() / 2 if rank == 2 else SageQQ.one()
        coefficient = (
            hauptsatz_factor * real_density * generic_density * exceptional_density
        )
        # The product is an exact real; reading it in QQ decides that it is rational.
        from sage_extensions.rings.real import RR

        return rationals(RR(SR(coefficient)))

    def siegel_eisenstein_series(self, precision=20, variable="q"):
        r"""Return ``1 + sum_{0 < m < precision} a_E(m) q^m`` for this definite genus.

        Each coefficient is :meth:`siegel_eisenstein_coefficient`, so the
        series is computed from local densities alone, independently of
        the classes of the genus.  The constant term is 1, the zero vector
        of every member.  By Siegel's Hauptsatz the series equals
        :meth:`theta_series` to the same precision.
        """
        rationals = self._lattice.base_ring().fraction_field()
        series_ring = rationals.power_series_ring(variable)
        coefficients = [rationals.one()] + [
            self.siegel_eisenstein_coefficient(m) for m in range(1, int(precision))
        ]
        engine = _engine_ring(series_ring)
        series = engine(
            [_engine_element(rationals, coefficient) for coefficient in coefficients]
        ).add_bigoh(int(precision))
        return _owned_engine_element(series_ring, series)

    @cached_method
    def anisotropic_primes(self):
        r"""Return the set of primes ``p`` at which ``L tensor QQ_p`` is anisotropic, for a member ``L``.

        The real place is not a member; the signature decides it.  In rank
        at least 3 a form unimodular at ``p`` is isotropic over ``QQ_p``
        (Serre, *A Course in Arithmetic*, Ch. IV, 1.7, Prop. 4 for the
        reduction, Ch. II, 2.2, Cor. 2 of Thm. 1 for the lift), so the set
        is the finite set of such primes dividing ``2 det L``.  In rank 1 it
        is every prime.  In rank 2 it is the set of ``p`` at which
        ``-det L`` is not a square in ``QQ_p`` (Serre, Ch. IV, 2.2, Thm. 6
        i)), infinite unless ``-det L`` is a rational square; it is the set
        of primes of ``ZZ`` cut out by that criterion, decided at each
        prime.
        """
        integers = _owned_integers()
        form = self._engine_form()
        match int(self._lattice.module_rank()):
            case rank if rank >= 3:
                return finite_ordered_set(
                    tuple(
                        _owned_engine_element(integers, SageZZ(prime))
                        for prime in form.anisotropic_primes()
                        if prime > 0
                    )
                )
            case _:
                return integers.condition_set(
                    lambda number: (
                        number.is_prime()
                        and form.is_anisotropic(_engine_element(integers, number))
                    )
                )

    @cached_method
    def local_representations(self):
        r"""Return the values ``b(x, x)`` of the localizations of a member, at the primes where they are not every ``p``-adic integer.

        The family is indexed by the primes ``p`` at which ``L tensor ZZ_p``
        does not represent every nonzero ``p``-adic integer.  Its value at
        ``p`` is indexed by the square classes of ``QQ_p^x`` that
        ``L tensor ZZ_p`` represents, each by its representative (``1, 3, 5,
        7, 2, 6, 10, 14`` for ``p = 2``; ``1, u, p, u p`` for odd ``p``, with
        ``u`` the least quadratic nonresidue), and takes the least valuation
        ``v`` at which the class is represented; ``L tensor ZZ_p`` represents
        an element of the class exactly when its valuation is ``v + 2j``,
        ``j >= 0``.

        In rank at least 3 every such prime divides ``2 det L``, and the
        index set is that finite set.  In rank 1 every prime is a member,
        and in rank 2 every prime at which the form is anisotropic and
        unimodular is one; there the index set is the set of primes of
        ``ZZ`` cut out by the definition, decided at each prime by
        :func:`_least_represented_valuations`.
        """
        integers = _owned_integers()
        form = self._engine_form()
        conditions = form.local_representation_conditions()

        def least(prime):
            return _least_represented_valuations(
                form, conditions, _engine_element(integers, prime)
            )

        match int(self._lattice.module_rank()):
            case rank if rank >= 3:
                primes = finite_ordered_set(
                    tuple(
                        _owned_engine_element(integers, SageZZ(prime))
                        for prime in conditions.exceptional_primes[1:]
                    )
                )
            case _:
                primes = integers.condition_set(
                    lambda number: (
                        number.is_prime()
                        and not _represents_every_integer(
                            conditions, _engine_element(integers, number), least(number)
                        )
                    )
                )
        return indexed_family(primes, lambda prime: _square_class_family(least(prime)))

    @cached_method
    def _engine_form(self):
        r"""Sage's integral quadratic form ``x |-> b(x, x)`` of the representative, private computation data."""
        from sage.quadratic_forms.quadratic_form import QuadraticForm

        return QuadraticForm(
            SageZZ,
            2
            * _engine_component_matrix(self._lattice.gram_tensor()).change_ring(SageZZ),
        )

    @cached_method
    def representatives(self):
        r"""Return one lattice from each isometry class of this genus.

        The classes of the improper spinor genus of the representative come
        first.
        """
        integers = _owned_integers()
        gram = _engine_component_matrix(self._lattice.gram_tensor()).change_ring(SageZZ)
        gram.set_immutable()
        return finite_ordered_set(
            tuple(
                Lattices(integers)(
                    [
                        [_owned_engine_element(integers, entry) for entry in row]
                        for row in found.rows()
                    ]
                )
                for spinor_genus in _genus_classes(gram)
                for found in spinor_genus
            )
        )

    def __iter__(self):
        return iter(self.representatives())

    def _cardinality_decision(self):
        r"""Supply the cardinality through the computed finite class representatives.

        The genus is the fibre of ``isometryClassToGenus`` in
        ``Lattices/Valued/LocalGlobal.lean``. Its chosen representatives give
        a bijection with that fibre, so Sets' cardinality owner reads the
        cardinality of this finite enumeration.
        """
        return self.representatives().cardinality()

    def class_number(self):
        r"""Return the number of isometry classes in this genus [PS24, Def. 1.10.5]."""
        return _owned_integers()(int(self.cardinality()))

    def __contains__(self, lattice) -> bool:
        r"""Return whether ``lattice`` is a lattice whose class lies in this genus."""
        return (
            lattice in Lattices(self._lattice.base_ring())
            and lattice.module_rank().is_finite()
            and bool(lattice.is_nondegenerate())
            and lattice.genus() == self
        )

    def __eq__(self, other) -> bool:
        r"""Two genera are equal when their signatures, determinants and canonical local symbols agree.

        Two forms are in one genus when they are equivalent over ``RR`` and
        over ``ZZ_p`` for every prime [CS10, Ch. 15, §7], and
        ``ZZ_p``-equivalence is equality of the canonical ``p``-adic symbols
        [CS10, Ch. 15, §7.6].  At a prime not dividing ``2 det`` the local
        lattice is unimodular and fixed by the rank and the determinant.
        """
        match other:
            case _ if other is self:
                return True
            case _ if other in _integral_lattice_genera():
                integers = _owned_integers()
                return (
                    self.signature_pair() == other.signature_pair()
                    and self.determinant() == other.determinant()
                    and all(
                        self.local_symbol(prime) == other.local_symbol(prime)
                        for prime in (
                            _owned_engine_element(integers, SageZZ(symbol.prime()))
                            for symbol in self._engine().local_symbols()
                        )
                    )
                )
            case _:
                return False

    def __ne__(self, other) -> bool:
        return not self == other

    def __hash__(self) -> int:
        signature = self.signature_pair()
        return hash(
            (int(signature.first()), int(signature.second()), int(self.determinant()))
        )

    def _repr_(self) -> str:
        signature = self.signature_pair()
        parity = "even" if self.is_even() else "odd"
        return f"Genus of {parity} integral lattices of signature ({signature.first()}, {signature.second()}) and determinant {self.determinant()}"


class _IntegralLatticeGenera(Sets().ObjectType):
    r"""The set of genera of integral lattices.

    ``lean-categories``: ``IntegralLatticeGenus``, the quotient of the
    isometry classes by ``SameGenus``
    (``LeanCategories/Lattices/Valued/LocalGlobal.lean``).  ``L.genus()`` is
    the quotient map.  The set is infinite: the rank-one lattices ``<n>``
    lie in distinct genera.
    """

    def __init__(self) -> None:
        super().__init__(category=Sets().Infinite(), facade=True)

    def __contains__(self, genus) -> bool:
        return isinstance(genus, _Genus)

    def _repr_(self) -> str:
        return "Set of genera of integral lattices"


@cached_function
def _integral_lattice_genera():
    return _IntegralLatticeGenera()


@cached_function
def _genus_classes(gram):
    r"""Private computation of the isometry classes of the genus of ``gram``.

    ``gram`` is an immutable Gram matrix over Sage's ``ZZ`` of a
    nondegenerate integral lattice of finite rank.  Returns the Gram matrices
    of one lattice from each isometry class of its genus, grouped by improper
    spinor genus, the spinor genus of ``gram`` first.

    In rank at most ``1`` the genus is one class.  In rank ``2`` the classes
    are the reduced binary forms of discriminant ``-4 det`` in the genus;
    an indefinite class has several reduced forms, so those are compared
    under improper equivalence.  In rank at least ``3`` one seed per
    improper spinor genus is a chain of ``p``-neighbours along a subset of
    Sage's spinor generators. Hanke's one-class-per-spinor-genus theorem for
    nondegenerate indefinite integral forms of rank at least three does not
    require rational isotropy [Hanke, *Quadratic Forms and Automorphic Forms*,
    revised 2009 notes, §3.5, Thm. 3.5.1, p. 52; Cassels (1978), Thm. 7.1,
    p. 186]. The weaker isotropic formulation in [CS10, Ch. 15, §9.1,
    Thm. 14, p. 388] is sufficient for the isotropic witness but not the
    strongest available theorem used here.
    A definite
    spinor genus is enumerated by ``p``-neighbours at a prime ``p`` not
    dividing the determinant, with ``p`` in the improper spinor kernel so
    that neighbours stay in the spinor genus.  The masses of all enumerated
    classes, including explicitly inserted seeds, must add up exactly to the
    mass of the genus; this is the completeness check after enumeration.
    """
    from itertools import combinations

    from sage.quadratic_forms.binary_qf import BinaryQF
    from sage.quadratic_forms.genera.genus import Genus as SageGenus
    from sage.quadratic_forms.quadratic_form import QuadraticForm
    from sage.quadratic_forms.quadratic_form__neighbors import neighbor_iteration
    from sage.rings.infinity import Infinity
    from sage.rings.rational_field import QQ as SageQQ
    from sage.sets.primes import Primes

    genus = SageGenus(gram)
    positive, negative = genus.signature_pair()
    indefinite = positive != 0 and negative != 0
    match gram.nrows():
        case rank if rank <= 1:
            return ((gram,),)
        case 2:
            classes = []
            for found in genus.representatives(backend="sage"):
                form = BinaryQF(found[0, 0], 2 * found[0, 1], found[1, 1])
                if not (
                    indefinite
                    and any(
                        form.is_equivalent(other, proper=False) for _, other in classes
                    )
                ):
                    classes.append((found, form))
            return (tuple(found for found, _ in classes),)

    scale = (SageZZ.one() if genus.is_even() else SageZZ(2)) * (
        -SageZZ.one() if positive == 0 else SageZZ.one()
    )
    form = QuadraticForm(SageZZ, scale * gram)
    spinor_primes = genus.spinor_generators(proper=False)
    spinor_operators, kernel = genus._improper_spinor_kernel()
    spinor_classes = spinor_operators.quotient(kernel)
    generated = spinor_classes.subgroup([])
    for spinor_prime in spinor_primes:
        assert spinor_prime.is_prime() and not spinor_prime.divides(genus.determinant()), (
            f"the improper spinor generator {spinor_prime} is not a prime coprime to the determinant {genus.determinant()}"
        )
        prime_class = spinor_classes(spinor_operators.delta(spinor_prime))
        assert prime_class.order() == 2, (
            f"the improper spinor generator {spinor_prime} does not define a nontrivial 2-torsion class"
        )
        previous_order = generated.order()
        generated = spinor_classes.subgroup((prime_class,) + generated.gens())
        assert generated.order() == 2 * previous_order, (
            f"the improper spinor generator {spinor_prime} does not enlarge the accumulated subgroup"
        )
    assert generated.order() == spinor_classes.order(), (
        f"the improper spinor generators {spinor_primes} do not span the quotient of order {spinor_classes.order()}"
    )
    # Build the Boolean-lattice orbit recursively. Every nonempty subset has
    # one canonical parent (remove its last prime), so each quotient element
    # costs exactly one p-neighbour step instead of recomputing its entire
    # chain from the original form.
    seed_by_subset = {(): form}
    for size in range(1, len(spinor_primes) + 1):
        for chosen in combinations(spinor_primes, size):
            parent = chosen[:-1]
            spinor_prime = chosen[-1]
            parent_seed = seed_by_subset[parent]
            vector = parent_seed.find_primitive_p_divisible_vector__next(
                spinor_prime
            )
            assert vector is not None, (
                f"the form {parent_seed} has no primitive vector of norm divisible by {spinor_prime}"
            )
            seed_by_subset[chosen] = parent_seed.find_p_neighbor_from_vec(
                spinor_prime, vector
            )
    seeds = [seed_by_subset[()]] + [
        seed_by_subset[chosen]
        for size in range(1, len(spinor_primes) + 1)
        for chosen in combinations(spinor_primes, size)
    ]
    assert len(seeds) == spinor_classes.order(), (
        f"constructed {len(seeds)} spinor-genus seeds for an improper quotient of order {spinor_classes.order()}"
    )
    assert all(seed.det() == form.det() for seed in seeds), (
        f"a p-neighbour spinor-genus seed changed the determinant of {form}"
    )
    for index, seed in enumerate(seeds):
        assert all(
            not seed.is_globally_equivalent_to(other)
            for other in seeds[index + 1 :]
        ), (
            f"the p-neighbour construction produced duplicate isometry-class seeds for the genus of {gram}"
        )

    def grams(forms):
        return tuple(
            (found.Hessian_matrix() / scale).change_ring(SageZZ) for found in forms
        )

    if indefinite:
        return tuple(grams((seed,)) for seed in seeds)

    # A ``p``-neighbour ``M`` of ``L`` with ``p`` prime to ``2 det`` has
    # ``[L : L cap M] = [M : L cap M] = p``, so its spinor genus is that of
    # ``L`` moved by the spinor operator of ``p`` [CS10, Ch. 15, §9.2,
    # Thm. 15]; at a prime whose operator lies in the improper spinor kernel
    # the neighbours stay in their spinor genus. Start at the odd prime ``3``
    # so the cited theorem's coprimality hypothesis with ``2 * det`` always
    # applies, including to even lattices of odd determinant.
    prime = SageZZ(3)
    while prime.divides(genus.determinant()) or (
        spinor_primes and not spinor_classes(spinor_operators.delta(prime)).is_one()
    ):
        prime = Primes().next(prime)
    total = form.conway_mass()
    found_mass = SageQQ.zero()
    classes = []
    for seed in seeds:
        # Do not use ``neighbor_iteration``'s mass stopping condition here:
        # it measures only discovered neighbours and excludes traversal seeds,
        # whereas ``found_mass`` below counts each spinor genus including its
        # seed. Completeness is checked against the full genus mass afterward.
        spinor_genus = neighbor_iteration(
            [seed],
            prime,
            algorithm="orbits",
            # The definite genus is finite, and the full mass equality below
            # is the completeness criterion. An arbitrary class-count cap
            # would reject otherwise supported genera with more than 10^6
            # classes rather than enumerate them completely.
            max_classes=Infinity,
        )
        # ``neighbor_iteration`` uses its seeds only as traversal roots; its
        # returned class list starts empty and therefore need not contain a
        # seed at all. Include the seed class explicitly, deduplicating it if
        # a neighbour equivalent to the seed was discovered during traversal.
        seed_position = next(
            (
                index
                for index, found in enumerate(spinor_genus)
                if seed.is_globally_equivalent_to(found)
            ),
            None,
        )
        if seed_position is None:
            spinor_genus.insert(0, seed)
        else:
            spinor_genus.insert(0, spinor_genus.pop(seed_position))
        found_mass += sum(
            SageQQ.one() / found.number_of_automorphisms() for found in spinor_genus
        )
        classes.append(grams(spinor_genus))
    assert found_mass == total, (
        f"the classes found in the genus of {gram} have mass {found_mass}, but the genus has mass {total}"
    )
    return tuple(classes)


def _local_density(form, prime, value):
    r"""Private computation of ``beta_p(Q, m)`` for Sage's integral quadratic form ``Q``.

    For ``Q = p^v f`` with ``f`` primitive at ``p``,
    ``beta_p(Q, m) = p^v beta_p(f, m / p^v)``; Sage's ``local_density``
    returns ``beta_p(f, m / p^v)`` without the factor ``p^v`` (``TRAPS.md``).
    """
    content = gcd(form.coefficients())
    return prime ** content.valuation(prime) * form.local_density(prime, value)


def _least_represented_valuations(form, conditions, prime):
    r"""Private computation of the least valuation at which ``L tensor ZZ_p`` represents each square class of ``QQ_p^x``.

    ``form`` is Sage's integral form ``Q(x) = b(x, x)`` of ``L``,
    ``conditions`` its local representation conditions and ``prime`` a
    prime ``p`` of Sage's ``ZZ``.  Returns, for Sage's representative ``r``
    of each square class (``conditions.squareclass_vector(p)``) of which
    ``L tensor ZZ_p`` represents an element, the least valuation of such an
    element.

    - Rank 1, ``Q = c X^2``: the values are ``c u^2 p^{2k}``, so the one
      class is that of ``c``, from ``v_p(c)``.
    - Rank 2 at a prime where Sage records no condition and ``p`` does not
      divide the level of ``Q``: ``L tensor ZZ_p`` is unimodular and ``p``
      odd.  Over ``F_p`` the reduction of a form of rank 2 represents every
      nonzero element (Serre, *A Course in Arithmetic*, Ch. IV, 1.7,
      Prop. 4), and a primitive solution of ``Q(x) = a mod p`` lifts to a
      solution in ``ZZ_p`` (Ch. II, 2.2, Cor. 2 of Thm. 1).  If ``Q`` is
      isotropic over ``QQ_p`` the reduction is isotropic (Ch. IV, 2.2,
      proof of Thm. 6 i), over ``F_p``), so every ``a`` in ``ZZ_p`` is
      represented.  If ``Q`` is anisotropic, a primitive ``x`` with
      ``p | Q(x)`` would be a zero of the reduction and lift to a zero over
      ``QQ_p``, so the represented elements are those of even valuation:
      the classes ``1`` and ``u`` from valuation 0.  Sage writes the
      second answer at every such prime (``TRAPS.md``).
    - Rank 2 at a prime dividing the level where Sage records no
      condition: Sage found each class at its least possible valuation and
      omitted the prime, so every class is represented from ``v_p(r)``.
    - Otherwise Sage stores, for each class, the least ``e`` with
      ``r p^{2e}`` represented, or ``+Infinity``; the least represented
      valuation is ``v_p(r) + 2e`` (``TRAPS.md``).
    """
    from sage.rings.infinity import infinity
    from sage.rings.rational_field import QQ as SageQQ

    classes = tuple(
        SageZZ(representative)
        for representative in conditions.squareclass_vector(prime)
    )
    recorded = prime in conditions.exceptional_primes
    match int(form.dim()):
        case 1:
            coefficient = SageZZ(form[0, 0])
            return {
                representative: coefficient.valuation(prime)
                for representative in classes
                if (SageQQ(coefficient) / representative).is_padic_square(prime)
            }
        case 2 if (
            not recorded
            and not prime.divides(form.level())
            and form.is_anisotropic(prime)
        ):
            return {
                representative: SageZZ.zero()
                for representative in classes
                if representative.valuation(prime) == 0
            }
        case 2 if not recorded:
            return {
                representative: representative.valuation(prime)
                for representative in classes
            }
        case _:
            steps = conditions.local_conditions_vector_for_prime(prime)[1:]
            return {
                representative: representative.valuation(prime) + 2 * step
                for representative, step in zip(classes, steps, strict=False)
                if step != infinity
            }


def _represents_every_integer(conditions, prime, least):
    r"""Whether ``least`` represents every square class from its least possible valuation ``v_p(r)``, so every nonzero ``p``-adic integer."""
    return least == {
        SageZZ(representative): SageZZ(representative).valuation(prime)
        for representative in conditions.squareclass_vector(prime)
    }


def _square_class_family(least):
    r"""Private raising of the least represented valuations: the family on the represented square classes, valued in those valuations."""
    integers = _owned_integers()
    classes = finite_ordered_set(
        tuple(
            _owned_engine_element(integers, representative) for representative in least
        )
    )
    return indexed_family(
        classes,
        lambda representative: _owned_engine_element(
            integers, SageZZ(least[_engine_element(integers, representative)])
        ),
    )


def _locally_represented(local_representations, value) -> bool:
    r"""Private computation: whether every ``L tensor ZZ_p`` represents the nonzero integer ``value``.

    ``local_representations`` is :meth:`_Genus.local_representations`: it is
    indexed by the primes ``p`` at which ``L tensor ZZ_p`` misses some
    nonzero ``p``-adic integer, so every other ``L tensor ZZ_p`` represents
    ``value``.  At an index ``p`` its value is indexed by the represented
    square classes of ``QQ_p^x``, each valued in the least valuation of a
    represented element of the class; the represented elements of a class
    are those of that valuation and above, in steps of 2, so ``value`` is
    represented exactly when its class ``r`` (``value / r`` a square in
    ``QQ_p``) is an index and ``v_p(value)`` is at least the value at ``r``.
    """
    from sage.rings.rational_field import QQ as SageQQ

    integers = _owned_integers()
    numerator = SageQQ(_engine_element(integers, value))

    def represented_at(prime) -> bool:
        classes = local_representations.value(prime)
        engine_prime = _engine_element(integers, prime)
        return any(
            (numerator / _engine_element(integers, representative)).is_padic_square(
                engine_prime
            )
            and value.valuation(prime) >= classes.value(representative)
            for representative in classes.index_set()
        )

    return all(represented_at(prime) for prime in local_representations.index_set())


def _indefinite_binary_representation(lattice, value):
    r"""Private computation: a vector ``x`` of the indefinite ``ZZ``-lattice ``L`` of rank 2 with ``b(x, x) = value != 0``, or ``None``.

    With ``L tensor QQ`` anisotropic, PARI's ``qfbsolve`` lists a
    representative of each solution class
    (:func:`lattice_engines._binary_special_orthogonal_representatives`).
    With ``L tensor QQ`` isotropic, let ``e`` be a primitive isotropic vector
    and ``f`` its Bezout partner, ``b(e, f) = d = div(e)``.  The kernel of
    ``b(e, -)`` on ``L`` is ``QQ e cap L = ZZ e``, so ``b(e, -)`` maps ``L``
    onto ``d ZZ`` and ``{e, f}`` is a basis of ``L``.  Then
    ``b(x e + y f, x e + y f) = y (2 d x + c y)`` with ``c = b(f, f)``, so a
    solution has ``y`` a divisor of ``value`` and ``2 d x = value / y - c y``,
    a finite search over the divisors of ``value``.
    """
    isotropic = lattice_engines._isotropic_vector_witness(lattice)
    if isotropic is None:
        found = lattice_engines._binary_special_orthogonal_representatives(
            lattice, value
        )
        return found[0] if found else None
    partner = isotropic.bezout_partner()
    divisibility = isotropic.div()
    partner_square = partner.q()
    for positive in value.divisors():
        for second in (positive, -positive):
            first, remainder = (value // second - partner_square * second).quo_rem(
                2 * divisibility
            )
            if remainder == value.parent().zero():
                return lattice.scalar_multiple(
                    first, isotropic
                ) + lattice.scalar_multiple(second, partner)
    return None


def _isometry_class_representatives(lattices, grams):
    r"""Private computation of ``Lattices.isometry_classes``.

    ``lattices`` are nondegenerate lattices over ``ZZ`` of finite rank and
    ``grams`` their Gram matrices over Sage's ``ZZ``.  Returns, for each
    position, the position of the first lattice isometric to it.

    Positions are grouped by invariants of the isometry class, in turn:
    rank, determinant and signature; for a definite form the numbers
    ``N_1, ..., N_4`` of vectors of norm ``1, ..., 4``, which the lattice
    determines [CS10, Ch. 2, §2.3]; the genus.  Inside a group two lattices
    are compared by the one decision ``Isom(L, M).is_empty()``
    (``LatticeIsometryMor._isometry_decision``), which constructs no
    isometry.  TRAPS.md records the wall times that order the steps.
    """

    from sage.libs.pari import pari
    from sage.quadratic_forms.genera.genus import signature_pair_of_matrix

    signatures = tuple(signature_pair_of_matrix(gram) for gram in grams)

    def numerical_invariants(position):
        return (grams[position].nrows(), grams[position].det(), signatures[position])

    def short_vector_counts(position):
        # ``qfrep`` counts the pairs ``±v``.
        if 0 not in signatures[position]:
            return ()
        sign = 1 if signatures[position][1] == 0 else -1
        return tuple(pari(sign * grams[position]).qfrep(4, 0))

    def genus(position):
        return lattices[position].genus()

    blocks = [tuple(range(len(grams)))]
    for invariant in (numerical_invariants, short_vector_counts, genus):
        refined = []
        for block in blocks:
            parts = {}
            for position in block:
                parts.setdefault(invariant(position), []).append(position)
            refined.extend(part for part in parts.values() if len(part) > 1)
        blocks = refined

    def isometric(found, position):
        empty = lattices[found].Isom(lattices[position]).is_empty()
        assert empty is True or empty is False, (
            f"cannot decide whether {lattices[found]!r} and {lattices[position]!r} are isometric, so their isometry classes cannot be separated"
        )
        return not empty

    representative = list(range(len(grams)))
    for block in blocks:
        classes = []
        for position in block:
            match next((found for found in classes if isometric(found, position)), None):
                case None:
                    classes.append(position)
                case found:
                    representative[position] = found
    return tuple(representative)


_BLACKBOARD_RING_NAMES = {
    "Z": "ZZ",
    "Q": "QQ",
    "R": "RR",
    "C": "CC",
    "N": "NN",
}


def _ring_notation(ring):
    r"""Session name and latex for a base ring.

    Sage typesets `\ZZ`, `\QQ`, `\RR`, `\CC`, and the rest of that
    family as ``\Bold{Z}``, ``\Bold{Q}``, \ldots .  The session names
    are ``ZZ``, ``QQ``, ``RR``, ``CC``; the latex is ``\mathbb{Z}``
    and so on, not Sage's ``\Bold``.
    """
    raw = str(latex(ring))
    prefix = r"\Bold{"
    if raw.startswith(prefix) and raw.endswith("}") and raw.count("{") == 1:
        letter = raw[len(prefix) : -1]
        name = _BLACKBOARD_RING_NAMES.get(letter)
        if name is not None:
            return name, rf"\mathbb{{{letter}}}"
    return str(ring), raw


def _postcomposed(automorphism, leg):
    r"""The arrow ``g o leg`` for an automorphism ``g`` of the codomain of ``leg``, in the Mor of ``leg``.

    ``g`` is an automorphism of ``B = leg.codomain()``, so ``g o leg`` has the
    endpoints of ``leg`` and is constructed in its Mor on its generator images.
    """
    source = leg.domain()
    return leg.parent()(lambda label: automorphism(leg(source.module_generator(label))))


def _assert_monic_leg(category, marked, leg):
    r"""State the hypothesis that a marking of ``Ar(Lattices)`` or ``Fun([n], Lattices)`` is a monomorphism."""
    assert leg.is_injective() is True, (
        f"{marked} is an object of {category} whose leg {leg} into its apex is not known to be "
        f"injective: the automorphisms of the apex carrying a marking onto itself are the setwise "
        f"stabilizer of its image only when the marking is a monomorphism"
    )


class _MarkedLatticeMethods:
    r"""Operations of the categories of marked lattices: ``<n>/Lattices``, ``Ar(Lattices)``, ``Fun([2], Lattices)``.

    A marked lattice is a diagram of lattices ending at a lattice ``L``, its
    apex (``sage-indefinite-port`` ``references/port-design.md``, *Marked
    lattices*).  ``O(L)`` acts on the marked lattices with apex ``L`` by
    postcomposing the legs into the apex, and an isomorphism of marked
    lattices with apex component ``g in O(L)`` exists from ``m`` to ``m'``
    exactly when ``g . m`` and ``m'`` are isomorphic with identity apex
    component.  Each marking category states the two operations of this
    action: :meth:`apex_action` and :meth:`apex_stabilizer`.
    """

    @abstract_method
    def apex_action(self, automorphism, marked):
        r"""Return ``g . marked``: the marking of the apex ``L`` postcomposed with ``g = automorphism`` in ``O(L)``."""

    @abstract_method
    def apex_stabilizer(self, marked):
        r"""Return the subgroup of ``O(L)`` of apex components of the automorphisms of ``marked``.

        It is ``{g in O(L) : g . marked is isomorphic to marked by an
        isomorphism with apex component g}``, so the stabilizer of
        ``g . marked`` is ``g S g^{-1}`` for ``S`` the stabilizer of
        ``marked``.
        """

    def primitive_marking_classes(self, source: Parent, lattice: Parent) -> Parent:
        r"""One marked lattice per isomorphism class of primitive markings of ``lattice`` of shape ``source``.

        ``source`` is the shape of the marking: ``<n>`` for a pointed lattice,
        a totally isotropic lattice for a sublattice, a chain for a flag.  The
        classes are decided by ``sage_indefinite_port`` (#403).
        """
        from sage_indefinite_port.indefinite.marked_lattices import primitive_marking_classes

        return primitive_marking_classes(self, source, lattice)


class Lattices(OwnedCategoryOverBaseRing):
    r"""
    The category of lattices over a base ring, and the constructor for
    its objects.

    Sage's ``IntegralLattice`` factory constructs finite nondegenerate
    integral forms but does not provide the mathematical category used here.
    ``Lattices(R)`` owns the broader category of free `R`-modules with an
    `R`-valued symmetric form; finite rank and nondegeneracy are refinements,
    not hidden constructor assumptions.      Named descriptors (``U``, a finite
    simply-laced Cartan type, a Euclidean rank) are owned Gram tensors.

    Sage's meet/join lattices are :class:`LatticePosets`, a different
    mathematical object.

    EXAMPLES::

        sage: from sage_extensions.categories.lattices import Lattices
        sage: Lattices(ZZ)
        Lattices(ZZ)
        sage: Lattices(ZZ).super_categories()
        [Category of framed free modules,
         Category of modules with a symmetric bilinear form,
         Category of formed modules]

        sage: C = Lattices(ZZ)
        sage: L = C("U")
        sage: L
        Integral lattice of rank 2 and signature (1, 1)
        sage: L in C
        True
        sage: C("A2")
        Integral lattice of rank 2 and signature (0, 2)
        sage: latex(L)
        \begin{gathered}
        L \in \mathrm{Lattices}(\mathbb{Z}), \quad \mathrm{rk}(L) = 2, \quad \mathrm{sig}(L) = (1, 1), \quad \mathrm{disc}(L) = 1 \\
        L = U \\
        G_L = \left(\begin{array}{rr}
        \cdot & 1 \\
        1 & \cdot
        \end{array}\right) \\
        \end{gathered}
        sage: latex(Lattices(ZZ))
        \mathrm{Lattices}(\mathbb{Z}) \in \mathrm{Cat}
    """

    @staticmethod
    def __classcall_private__(cls, *args):
        r"""Return the category of lattices over a ring.

        This is not a lattice constructor.  An object is
        ``Lattices(R)(data)``.
        """
        if len(args) != 1:
            raise TypeError(
                f"Lattices(R) takes exactly one argument, a ring R, but received {len(args)} arguments {args!r}; a lattice itself is constructed as Lattices(R)(data)"
            )
        ring = _own_ring(args[0])
        assert ring in _Rings, (
            f"Lattices(R) takes a ring R, but {args[0]!r} is not a ring; a lattice itself is constructed as Lattices(R)(data)"
        )
        from sage_extensions.categories.modules.pure.modules import (
            _is_group_algebra,
        )

        if cls is Lattices and _is_group_algebra(ring):
            # Lattices(R[G]): lattices over R with a form-preserving G-action.
            from sage_extensions.categories.modules.group_modules.group_lattices import (
                LatticesOverGroupAlgebra,
            )

            return LatticesOverGroupAlgebra(ring)
        return super().__classcall__(cls, ring)

    class Coslices(_MarkedLatticeMethods, CosliceCategory):
        r"""``X/Lattices``: lattices marked by a map from ``X``, the coslice construction on ``Lattices``."""

        def apex_action(self, automorphism, marked):
            r"""``(L, g o i)`` for the object ``(L, i: X -> L)`` and ``g`` in ``O(L)``."""
            return self.object(_postcomposed(automorphism, self.arrow(marked)))

        def apex_stabilizer(self, marked):
            r"""``{g in O(L) : g o i = i}``: an isomorphism of ``X/Lattices`` is the identity on ``X``.

            The marking ``i`` is fixed, not movable, so the stabilizer fixes
            the image of every generator of ``X``; ``i`` need not be injective
            (the zero vector is a marking of ``<0> -> L``).
            """
            arrow = self.arrow(marked)
            return arrow.codomain().O().pointwise_stabilizer(arrow)

    class ArrowDiagrams(_MarkedLatticeMethods, _WalkingArrowFunctorCategory):
        r"""``Ar(Lattices) = [[1], Lattices]``: lattices marked by a sublattice."""

        def apex_action(self, automorphism, marked):
            r"""``(L, g o i)`` for the marking ``i: I -> L`` and ``g`` in ``O(L)``."""
            return self.object(_postcomposed(automorphism, marked.arrow()))

        def apex_stabilizer(self, marked):
            r"""``{g in O(L) : g(i(I)) = i(I)}`` for a monic marking ``i: I -> L``.

            An isomorphism of ``Ar(Lattices)`` is a square ``(alpha, g)`` with
            ``g i = i alpha``; for monic ``i`` such an ``alpha`` exists exactly
            when ``g`` carries the image of ``i`` onto itself.
            """
            arrow = marked.arrow()
            _assert_monic_leg(self, marked, arrow)
            return arrow.codomain().O().setwise_stabilizer(arrow)

    class SequenceDiagrams(_MarkedLatticeMethods, _FiniteSequenceFunctorCategory):
        r"""``[[n], Lattices]``: lattices marked by a chain of sublattices, such as a flag."""

        def apex_action(self, automorphism, marked):
            r"""The chain ``I_0 -> ... -> I_{n-1} -> L`` with its last arrow postcomposed with ``g``.

            Every leg into the apex ``L`` factors through the last arrow, so
            postcomposing it postcomposes each leg.
            """
            transitions = tuple(marked.arrows())
            return self((*transitions[:-1], _postcomposed(automorphism, transitions[-1])))

        def apex_stabilizer(self, marked):
            r"""``{g in O(L) : g(F(j -> top)(F(j))) = F(j -> top)(F(j)) for every j}``, for a chain of monomorphisms.

            An isomorphism of chains is a natural isomorphism; with monic legs
            ``F(j -> top)`` into the apex its component at ``j`` exists exactly
            when ``g`` carries the image of that leg onto itself, so the
            stabilizer is the intersection of the setwise stabilizers of the
            images of the legs.
            """
            functor = marked.functor()
            shape = functor.domain()
            top = shape(int(shape.object_set().cardinality()) - 1)
            orthogonal_group = functor(top).O()
            legs = tuple(
                functor(shape.Mor(vertex, top).unique())
                for vertex in shape.objects()
                if vertex is not top
            )
            for leg in legs:
                _assert_monic_leg(self, marked, leg)
            stabilizer = orthogonal_group.intersection(
                *(orthogonal_group.setwise_stabilizer(leg) for leg in legs)
            )
            return stabilizer.select_group_generators(
                lambda: orthogonal_group._marking_stabilizer_generators(self, marked, stabilizer)
            )

    @cached_method
    def Core(self):
        r"""The core groupoid of lattices: the isometry Mors ``Isom(L, M)``, with ``O(L)`` its vertex groups."""
        return _LatticeCore(self)

    def _core_isomorphism_witness(self, core_mor):
        r"""Implementer side of ``CoreMor``'s core contract for lattices: one isometry, or ``None``."""
        return None if core_mor.is_empty() is True else core_mor.an_element()

    def _core_automorphism_generators(self, core_mor):
        r"""Implementer side of ``CoreMor``'s core contract for lattices: generators of ``O(L)``.

        ``CoreMor.group_generators`` reads a selected resolution first and
        asks this only without one.  The generators are those of the
        lattice realization: Sage's for definite ``L``, and for indefinite
        ``L`` the port's ``automorphism_group_generators`` (#403), the
        port's own algorithm for ``O(L)`` (``_computed_group_generators``).
        """
        lattice = core_mor.domain()
        assert lattice.module_rank().is_finite(), (
            f"generators of O({lattice}) are computed only for a lattice of finite rank, and {lattice} has "
            f"rank {lattice.module_rank()}"
        )
        return core_mor._computed_group_generators()

    def _marked_isometry(self, diagram_category, source, target):
        r"""Implementer side of ``_FunctorCategory``'s protected marked-diagram contract.

        The apex isometry of an isomorphism of marked lattices, or ``None``,
        from ``sage-indefinite-port``'s marked-lattice entry (#403).  The
        answer is untrusted engine output.
        """
        from sage_indefinite_port.indefinite.marked_lattices import isometry

        return isometry(diagram_category, source, target)

    def _marked_automorphism_generators(self, diagram_category, marked):
        r"""Implementer side of the marked-diagram contract: apex isometries generating ``Aut`` of the marking (#403).

        Callers: ``CoreMor`` through the marking category, as declared at
        ``_FunctorCategory``, and ``LatticeIsometryMor``, whose orbit
        splitting and vector stabilizers read the apex image of ``Aut`` of
        a marking of an indefinite lattice.
        """
        from sage_indefinite_port.indefinite.marked_lattices import (
            automorphism_group_generators,
        )

        return automorphism_group_generators(diagram_category, marked)

    def _marking_component(self, source_marking, target_marking, apex):
        r"""Implementer side of the marked-diagram contract: ``alpha`` with ``kappa alpha = g iota``.

        ``iota = source_marking`` and ``kappa = target_marking`` are
        embeddings and ``g = apex`` an isometry carrying ``iota`` onto
        ``kappa``; ``alpha`` is read on the generators of the source of
        ``iota`` by lifting along the monomorphism ``kappa``.
        """
        domain = source_marking.domain()
        return domain.Isom(target_marking.domain())(
            lambda label: target_marking.lift(apex(source_marking(domain.module_generator(label))))
        )

    def twist_functor(self, scale):
        r"""Return the integral-lattice endofunctor ``L |-> L(scale)``."""
        if _engine_ring(self.base_ring()) is not SageZZ:
            raise TypeError(
                f"the twist functor L |-> L({scale}) is defined here only for lattices over ZZ, but {self} has base ring {self.base_ring()}"
            )
        from sage_extensions.categories.functors.twist import TwistFunctor

        return TwistFunctor(scale)

    def isometry_classes(self, lattices):
        r"""Return the partition of a finite family of lattices into isometry classes.

        ``lattices`` is a finite indexed family `(L_i)_{i \in I}` of
        nondegenerate lattices of finite rank in this category.  The result
        is the family of blocks of `I` under `L_i \cong L_j`, indexed by the
        quotient `I/\cong`; each block is the finite ordered set of its
        indices in the order of `I`, and the blocks are in the order of
        their first indices.  No isometry is constructed.

        EXAMPLES::

            sage: from sage_extensions.categories.lattices import Lattices
            sage: from sage_extensions.categories.sets.finite_families import finite_family
            sage: C = Lattices(ZZ)
            sage: family = finite_family((C([[2, -1], [-1, 2]]), C("U"), C([[2, 1], [1, 2]])))
            sage: classes = C.isometry_classes(family)
            sage: classes.cardinality()
            2
            sage: [tuple(int(index) for index in block) for block in classes]
            [(0, 2), (1,)]
        """
        assert _engine_ring(self.base_ring()) is SageZZ, (
            f"isometry classes are implemented for lattices over ZZ, but {self} has base ring {self.base_ring()}"
        )
        indices = tuple(lattices.index_set())
        family_members = tuple(lattices.value(index) for index in indices)
        representatives = _isometry_class_representatives(
            family_members,
            tuple(
                _engine_component_matrix(member.gram_tensor()).change_ring(SageZZ)
                for member in family_members
            ),
        )
        blocks = {}
        for index, representative in zip(indices, representatives, strict=True):
            blocks.setdefault(representative, []).append(index)
        members = tuple(tuple(block) for block in blocks.values())
        return indexed_family(
            Sets.Δ[len(members) - 1],
            lambda label: FiniteOrderedSets().from_indexed(
                Sets.Δ[len(members[int(label)]) - 1],
                lambda position: members[int(label)][int(position)],
            ),
            name="Isometry classes",
        )

    def genus(self, signature, discriminant_quadratic_form):
        r"""Return the genus of the even lattices with ``signature`` and ``discriminant_quadratic_form``.

        The signature and the discriminant quadratic form determine the genus
        of an even lattice [nikulin1979integral, Cor. 1.9.4]; ``signature``
        is an object of ``signature_pairs()``.  An even lattice with these
        invariants exists exactly when
        ``discriminant_quadratic_form.is_discriminant_form_of_even_lattice(signature)``
        [nikulin1979integral, Thm. 1.10.1], and otherwise there is no genus
        to return.
        """
        integers = self.base_ring()
        assert _engine_ring(integers) is SageZZ, (
            f"the genus of even lattices with given signature and discriminant form is implemented for lattices over ZZ, but {self} has base ring {integers}"
        )
        if not discriminant_quadratic_form.is_discriminant_form_of_even_lattice(
            signature
        ):
            raise ValueError(
                f"no even lattice of signature ({signature.first()}, {signature.second()}) has discriminant quadratic form {discriminant_quadratic_form!r} [nikulin1979integral, Thm. 1.10.1]"
            )
        gram = _even_lattice_genus_gram(discriminant_quadratic_form, signature)
        return self(
            [
                [_owned_engine_element(integers, entry) for entry in row]
                for row in gram.rows()
            ]
        ).genus()

    @overload  # type: ignore[override]  # the stub promises a SageObject; the object type of this category is its provider class
    def __call__(
        self, data: str | Sequence[Sequence[object]], *args: object, **options: object
    ) -> Lattices.ParentMethods: ...

    @overload
    def __call__(
        self, data: object, *args: object, **options: object
    ) -> Lattices.ParentMethods: ...

    def __call__(
        self, data: object, *args: object, **options: object
    ) -> Lattices.ParentMethods:
        r"""Return the lattice that ``data`` presents; a lattice in this category is returned as is.

        A named form or a Gram given by rows has finite rank.

        EXAMPLES::

            sage: from sage_extensions.categories.lattices import Lattices
            sage: L = Lattices(ZZ)("U")
            sage: Lattices(ZZ)(L) is L
            True
        """
        return super().__call__(data, *args, **options)

    def _call_(  # type: ignore[override]  # the stub promises a SageObject; the object type of this category is its provider class
        self,
        data: object,
        basis: None = None,
        names: str | Sequence[str] | None = None,
        form: Tensor | None = None,
        module_generators: Sequence[Hashable] | Parent | None = None,
    ) -> Lattices.ParentMethods:
        r"""Construct a lattice in this category.

        This is Sage's category constructor: ``C(x)`` for ``C`` a
        category.  ``Lattices(ZZ)("U")`` is the hyperbolic plane over
        `\ZZ`.  ``Lattices(R)(R^n)`` is the standard Euclidean lattice
        of rank `n`; ``Lattices(R)(R^{\mathbb N})`` is its colimit.
        A pairing Gram is a lattice: ``C((R^NN).diagonal_gram({0: -1}))``.
        ``module_generators=`` is the generating set of the underlying
        free module; when omitted, its labels are the natural-number ordinal
        of the rank. The symbols \(e_i\) only print basis vectors.
        The result is an owned lattice.

        EXAMPLES::

            sage: from sage_extensions.categories.lattices import Lattices
            sage: A2 = Lattices(ZZ)([[2, 1], [1, 2]])
            sage: F = A2.unformed_module()
            sage: tuple(int(key) for key in F.module_generating_set())
            (0, 1)
            sage: F.module_generator(0) != F.module_generator(1)
            True
            sage: Lattices(ZZ)("U")
            Integral lattice of rank 2 and signature (1, 1)
            sage: I2 = Lattices(ZZ)(ZZ^2)
            sage: I2
            Integral lattice of rank 2 and signature (2, 0)
            sage: I2.gram_tensor().tensor_valence()
            (0, 2)
            sage: e = I2.basis_vector(0)
            sage: e
            e_0
            sage: e.to_vector()
            e_0
            sage: e*e, e.b(I2.basis_vector(1))
            (1, 0)
            sage: I2((1, 0))
            e_0
            sage: Linf = Lattices(ZZ)(ZZ^NN)
            sage: Linf
            Integral lattice of rank +Infinity and signature (+Infinity, 0)
            sage: Linf((1, 0, 0, 1))
            e_0 + e_3
            sage: Lattices(ZZ)((ZZ^NN).diagonal_gram({0: -1}))
            Integral lattice of rank +Infinity and signature (+Infinity, 1)
        """

        return _lattice(
            data,
            basis,
            names=names,
            form=form,
            module_generators=module_generators,
            category=self,
        )

    def _specialize_existing_lattice(
        self,
        lattice,
        *,
        extra_categories=(),
        construction_data=(),
        unformed_module=None,
    ):
        r"""Build a lattice carrying added structure on the data of ``lattice``.

        Protected construction contract of ``Lattices(R)`` (``OWN-05``).  Its
        callers are the entries of categories whose structure is stated on an
        existing lattice and which have no Gram presentation of their own to
        supply, such as ``Lattices(R[G])(L, action)``.  It takes the lattice,
        the categories the structure adds, the data those categories declare
        (a mapping, or a family of name-value pairs), and the module the
        structure is stated on: ``lattice`` itself when the structure is
        stated on the lattice, as for a group action, and otherwise the
        module ``lattice`` is built on.

        It computes the datum of the one lattice construction and calls it:
        the Gram presentation of ``lattice`` stated on that module, together
        with the structure ``lattice`` already carries by its placement -- its
        subobject inclusion, its biproduct or tensor-product factors and its
        root framing.  The result is a new lattice on the same data, and it
        answers ``unformed_module()`` with the module the structure was
        stated on.
        """
        ring = self.base_ring()
        assert lattice in self, (
            f"cannot specialize {lattice!r} in {self}: it is not a lattice of {self}"
        )
        stated_on = (
            lattice.unformed_module() if unformed_module is None else unformed_module
        )
        carried_categories = []
        carried_data = {}
        match lattice in OrthogonalSumLattices(ring):
            case True:
                carried_categories.append(OrthogonalSumLattices(ring))
                carried_data["biproduct_factors"] = lattice.biproduct_factors()
        match lattice in TensorProductModules(ring):
            case True:
                carried_categories.append(TensorProductModules(ring))
                carried_data["tensor_factors"] = lattice.tensor_factors()
        match lattice in RootLattices():
            case True:
                carried_categories.append(RootLattices())
                carried_data["root_system_type_name"] = lattice.root_system_type_name()
        match lattice in NoncrystallographicRootLattices(ring):
            case True:
                carried_categories.append(NoncrystallographicRootLattices(ring))
                carried_data["coxeter_type"] = lattice.coxeter_type()
        match lattice in ModuleSubobjects(ring):
            case True:
                subobject_construction = lattice.module_subobject_construction()
            case False:
                subobject_construction = None
        carried_data.update(dict(construction_data))
        return _lattice_object(
            self,
            stated_on,
            lattice.gram_tensor(),
            extra_categories=(*carried_categories, *tuple(extra_categories)),
            construction_data=carried_data,
            subobject_construction=subobject_construction,
        )

    def colimit(self, stage, *, row_support=None):
        r"""Return \(\operatorname{colim}_n \mathrm{stage}(n)\) along \(x\mapsto(x,0)\).

        ``stage(n)`` is a rank-\(n\) lattice in this category.  The
        resulting form is evaluated in a finite stage containing the supports
        of the vectors being paired.  The stage callback alone does not prove
        an infinite signature, nondegeneracy or unimodularity; those predicates
        remain undecided unless the represented Gram rule supplies the missing
        global information.

        EXAMPLES::

            sage: from sage_extensions.categories.lattices import Lattices
            sage: C = Lattices(ZZ)
            sage: L = C.colimit(lambda n: C(ZZ^n))
            sage: L.basis_vector(3) * L.basis_vector(3)
            1
        """

        return _colimit_lattice(stage, category=self, row_support=row_support)

    def orthogonal_direct_sum_bifunctor(self):
        r"""Return the orthogonal direct-sum bifunctor on lattices over this ring."""
        from sage_extensions.categories.functors.linear_constructions import (
            _orthogonal_direct_sum_bifunctor,
        )

        return _orthogonal_direct_sum_bifunctor(self.base_ring())

    def an_object(self):
        r"""The hyperbolic plane U."""
        return self("U")

    def standard_objects(self):
        r"""Iterate familiar integral lattices through the ordinary constructors.

        This is a selected catalogue, not an enumeration of all lattices.
        Non-simply-laced root types use their integral symmetrized Cartan
        forms as supplied by :meth:`root_lattice`.
        """
        if self.base_ring() is not _owned_integers():
            raise NotImplementedError("standard specimens are currently integral")
        rank = 1
        while True:
            if rank == 1:
                yield self([[1]])
                yield self([[-1]])
            if rank == 2:
                yield self("U")
            for kind in ("A", "B", "C", "D", "E", "F", "G"):
                valid = (
                    kind == "A"
                    or kind in {"B", "C"} and rank >= 2
                    or kind == "D" and rank >= 4
                    or kind == "E" and rank in (6, 7, 8)
                    or kind == "F" and rank == 4
                    or kind == "G" and rank == 2
                )
                if valid:
                    yield self.root_lattice(kind, rank)
            for positive in range(rank + 1):
                negative = rank - positive
                yield self.IPQ(positive, negative)
                if positive > 0 and negative > 0 and (positive - negative) % 8 == 0:
                    yield self.IIPQ(positive, negative)
            if rank == 24:
                yield self.leech_lattice()
            rank += 1

    @staticmethod
    def root_lattice(kind, rank, names=None):
        r"""Return the exact negative-definite root lattice of the selected finite type."""
        kind = str(kind)
        rank = int(rank)
        if kind == "H":
            if rank not in (3, 4):
                raise ValueError(
                    f"there is no root system H{rank}: the finite noncrystallographic root systems of type H are H3 and H4"
                )
            from sage_extensions.categories.rings.number_fields import (
                QuadraticField,
            )

            field = QuadraticField(5, "sqrt5")
            order = field.ring_of_integers()
            phi = order((field.one() + field.primitive_element()) / field(2))
            bonds = (phi, *([order.one()] * (rank - 2)))
            gram = _nested_gram_tensor(
                tuple(
                    tuple(
                        -order(2)
                        if row == column
                        else bonds[min(row, column)]
                        if abs(row - column) == 1
                        else order.zero()
                        for column in range(rank)
                    )
                    for row in range(rank)
                ),
                order,
            )
            selected_names = _normalized_lattice_names(names, cardinal(rank))
            module = order.free_module(
                _generating_set_for(cardinal(rank), None, selected_names)
            )
            return _lattice_object(
                Lattices(order),
                module,
                gram,
                names=selected_names,
                extra_categories=(NoncrystallographicRootLattices(order),),
                construction_data={"coxeter_type": (kind, rank)},
            )
        if kind not in {"A", "B", "C", "D", "E", "F", "G"}:
            raise ValueError(f"unknown finite root family {kind!r}")
        return Lattices(_owned_integers())(f"{kind}{rank}", names=names)

    @staticmethod
    def IPQ(positive, negative):
        r"""Return the odd unimodular lattice ``I_(positive,negative)``."""
        positive = int(positive)
        negative = int(negative)
        if positive < 0 or negative < 0 or positive + negative == 0:
            raise ValueError(
                f"I_({positive},{negative}) is not defined: the odd unimodular lattice I_(p,q) requires p, q >= 0 and p + q > 0"
            )
        diagonal = [1] * positive + [-1] * negative
        gram = [
            [entry if row == column else 0 for column, entry in enumerate(diagonal)]
            for row in range(len(diagonal))
        ]
        return Lattices(_owned_integers())(gram)

    @staticmethod
    def IIPQ(positive, negative):
        r"""Return the indefinite even unimodular lattice ``II_(positive,negative)``.

        Such a lattice exists exactly when both inertia indices are positive and
        ``positive-negative`` is divisible by eight.  With the repository's
        negative-definite ``E8`` convention it is the orthogonal sum of
        hyperbolic planes and the required signed ``E8`` blocks.
        """
        positive = int(positive)
        negative = int(negative)
        if positive < 1 or negative < 1:
            raise ValueError(
                f"II_({positive},{negative}) is not defined here: II_(p,q) denotes an indefinite even unimodular lattice, which requires p >= 1 and q >= 1"
            )
        if (positive - negative) % 8:
            raise ValueError(
                f"no even unimodular lattice II_({positive},{negative}) exists: the signature p - q = {positive - negative} of an even unimodular lattice is divisible by eight"
            )
        integers = _owned_integers()
        category = Lattices(integers)
        summands = [category("U") for _ in range(min(positive, negative))]
        if negative > positive:
            summands.extend(category("E8") for _ in range((negative - positive) // 8))
        elif positive > negative:
            positive_e8 = category("E8").twist(-1)
            summands.extend(positive_e8 for _ in range((positive - negative) // 8))
        return _orthogonal_sum(tuple(summands))

    @staticmethod
    def rank_one_negative(scale):
        r"""Return the rank-one lattice ``<-2 scale>``."""
        integers = _owned_integers()
        return Lattices(integers)(1).twist(integers(-2 * int(scale)))

    @staticmethod
    def LK3_2d(degree):
        r"""Return ``<-2d> + U^2 + E8^2``, the degree-``2d`` K3 complement lattice."""
        degree = int(degree)
        if degree < 1:
            raise ValueError(
                f"no K3 lattice of degree 2d with d = {degree}: a polarization has positive degree, so d >= 1"
            )
        integers = _owned_integers()
        category = Lattices(integers)
        return _orthogonal_sum(
            (
                Lattices.rank_one_negative(degree),
                category("U"),
                category("U"),
                category("E8"),
                category("E8"),
            )
        )

    @staticmethod
    def hyperkaehler_lattice(deformation_type, n=2):
        r"""Return the Beauville--Bogomolov--Fujiki lattice of a standard deformation type.

        ``K3`` means ``K3^[n]`` and ``Kum`` the generalized Kummer series;
        ``OG6`` and ``OG10`` are the two O'Grady types.  The formulas are the
        standard integral BBF lattices and use the existing owned ``U``, ``E8``
        and ``A2`` constructors rather than a second lattice representation.
        """
        deformation_type = str(deformation_type)
        n = int(n)
        if deformation_type not in {"K3", "Kum", "OG6", "OG10"}:
            raise ValueError(
                f"unknown hyperkähler deformation type {deformation_type!r}"
            )
        integers = _owned_integers()
        category = Lattices(integers)
        hyperbolic = (category("U"), category("U"), category("U"))
        if deformation_type == "K3":
            if n < 2:
                raise ValueError(
                    f"no BBF lattice of K3^[{n}]-type: the K3^[n] series requires n >= 2"
                )
            return _orthogonal_sum(
                (
                    *hyperbolic,
                    category("E8"),
                    category("E8"),
                    category(1).twist(2 - 2 * n),
                )
            )
        if deformation_type == "Kum":
            if n < 2:
                raise ValueError(
                    f"no BBF lattice of generalized Kummer type Kum_{n}: the series requires n >= 2"
                )
            return _orthogonal_sum((*hyperbolic, category(1).twist(-2 - 2 * n)))
        if deformation_type == "OG6":
            minus_two = category(1).twist(-2)
            return _orthogonal_sum((*hyperbolic, minus_two, minus_two))
        return _orthogonal_sum(
            (*hyperbolic, category("E8"), category("E8"), category("A2"))
        )

    @staticmethod
    @cached_function
    def leech_lattice():
        r"""Return the negative-definite Leech lattice in its fixed integral presentation.

        The named object has no input-dependent computation.  Its Gram
        presentation is retained locally so constructing it does not cold-load
        OSCAR; Hecke's ``leech_lattice()`` is the independent oracle from which
        this presentation is checked.
        """
        integers = _owned_integers()
        entries = {entry for row in _LEECH_GRAM_ROWS for entry in row}
        coefficients = {entry: integers(-entry) for entry in entries}
        rows = tuple(
            tuple(coefficients[entry] for entry in row)
            for row in _LEECH_GRAM_ROWS
        )
        category = Lattices(integers)
        leech = _lattice_from_gram_tensor(
            _nested_gram_tensor(rows, integers),
            integers,
            None,
            None,
            category,
            axiom_categories=(
                category.FinitelyGenerated(),
                category.Nondegenerate(),
                category.Unimodular(),
                category.Even(),
            ),
        )
        lattice_engines.validate_even_unimodular_gram(
            leech.gram_tensor(), check=False
        )
        return leech

    @cached_method
    def super_categories(self):
        r"""
        Return the immediate super categories of ``self``.

        A lattice is a free `R`-module with a symmetric `R`-valued form.
        Immediate supers only, as required by the Sage category primer.

        EXAMPLES::

            sage: from sage_extensions.categories.lattices import Lattices
            sage: Lattices(ZZ).super_categories()
            [Category of free form modules,
             Category of modules with a symmetric bilinear form]
        """

        return [
            FreeFormModules(self.base_ring()),
            BilinearFormModules(self.base_ring()).Symmetric(),
        ]

    _MorCategory = LatticeMorCategoryConstruction
    _MonoCategory = LatticeMonoCategoryConstruction
    _IsoCategory = LatticeIsoCategoryConstruction

    class Indecomposable(CategoryWithAxiom):
        r"""Full property subcategory of lattices with no nontrivial orthogonal sum.

        ``known_objects`` offers examples; it does not enumerate this category.
        """

        _certifying_predicate = "is_indecomposable"

        def __contains__(self, lattice):
            if lattice not in Lattices(self.base_ring()):
                return False
            answer = lattice.is_indecomposable()
            if isinstance(answer, bool):
                return answer
            if super().__contains__(lattice):
                return True
            raise NotImplementedError(
                f"orthogonal indecomposability of {lattice!r} is not decided"
            )

        def an_object(self):
            return Lattices(self.base_ring())("U")

    class Twisted(CategoryWithAxiom):
        r"""Integral lattices with a nonunit integral factor in the form."""

        _certifying_predicate = "is_twisted"

        def __contains__(self, lattice):
            if lattice not in Lattices(self.base_ring()):
                return False
            answer = lattice.is_twisted()
            if isinstance(answer, bool):
                return answer
            if super().__contains__(lattice):
                return True
            raise NotImplementedError(f"twistedness of {lattice!r} is not decided")

        def an_object(self):
            return Lattices(self.base_ring())("U").twist(2)

    class Untwisted(CategoryWithAxiom):
        r"""Integral lattices whose Gram entries generate the unit ideal."""

        _certifying_predicate = "is_untwisted"

        def __contains__(self, lattice):
            if lattice not in Lattices(self.base_ring()):
                return False
            answer = lattice.is_untwisted()
            if isinstance(answer, bool):
                return answer
            if super().__contains__(lattice):
                return True
            raise NotImplementedError(f"untwistedness of {lattice!r} is not decided")

        def an_object(self):
            return Lattices(self.base_ring())("U")

    class SubcategoryMethods:
        def known_objects(self, max_rank=None):
            r"""Return known integral specimens satisfying this lattice category."""
            ring = self._super_categories[0].base_ring()
            if ring is not _owned_integers():
                raise NotImplementedError("known lattice specimens are currently integral")
            bound = 8 if max_rank is None else max_rank
            if bound < 0:
                raise ValueError("max_rank must be nonnegative")
            axioms = self.axioms()
            known = []
            for lattice in Lattices(ring).standard_objects():
                if int(lattice.module_rank()) > bound:
                    break
                if "Indecomposable" in axioms and lattice.is_indecomposable() is not True:
                    continue
                if "Untwisted" in axioms and lattice.is_untwisted() is not True:
                    continue
                if "Twisted" in axioms and lattice.is_twisted() is not True:
                    continue
                known.append(lattice)
            return finite_family(known, name="Known objects of this lattice category")

        def Indecomposable(self):
            r"""The full subcategory of orthogonally indecomposable lattices."""
            return self._with_axiom("Indecomposable")

        def Twisted(self):
            r"""The property subcategory of lattices with a nonunit form factor."""
            return self._with_axiom("Twisted")

        def Untwisted(self):
            r"""The property subcategory of primitive integral forms."""
            return self._with_axiom("Untwisted")

        def construction_enumeration(self, seeds):
            r"""Enumerate integral-lattice construction expressions fairly.

            The seed at position ``i`` has weight ``i + 1``, so even a
            supplied infinite sequence is visited fairly. A proper overlattice adds
            one, a twist by a nonunit integer ``n`` adds ``1 + abs(n)``, and a
            binary operation adds one to the
            sum of its inputs' weights. Every finite expression over the
            supplied seeds therefore occurs at a finite weight. Distinct
            expressions remain distinct even when their lattices are isometric.
            The supplied set is sorted by its displayed Gram data; other
            iterables retain their given order. The enumeration has no bound.
            """
            if self.base_ring() is not _owned_integers():
                raise NotImplementedError("integer twist enumeration requires integral lattices")
            if isinstance(seeds, (set, frozenset)):
                seeds = sorted(
                    seeds,
                    key=lambda lattice: (
                        int(lattice.module_rank()),
                        tuple(str(lattice.gram_tensor()[i, j])
                              for i in range(int(lattice.module_rank()))
                              for j in range(int(lattice.module_rank()))),
                    ),
                )
            seed_iterator = iter(seeds)
            levels = {}
            exhausted = False
            weight = 1
            while True:
                current = []
                if not exhausted:
                    try:
                        lattice = next(seed_iterator)
                    except StopIteration:
                        exhausted = True
                    else:
                        if lattice not in self:
                            raise TypeError(f"{lattice!r} is not an object of {self!r}")
                        if not lattice.module_rank().is_finite():
                            raise ValueError("construction enumeration requires finite-rank seeds")
                        current.append(LatticeConstruction(lattice, "seed"))
                if weight > 1:
                    for source in levels[weight - 1]:
                        lattice = source.lattice
                        if lattice.is_nondegenerate() is True:
                            for inclusion in lattice.integral_overlattice_inclusions():
                                if inclusion.index() == 1:
                                    continue
                                current.append(LatticeConstruction(inclusion.codomain(), "overlattice", (source,), inclusion))
                for source_weight in range(1, weight - 2):
                    magnitude = weight - source_weight - 1
                    for source in levels[source_weight]:
                        for scalar in (magnitude, -magnitude):
                            current.append(LatticeConstruction(
                                source.lattice.twist(self.base_ring()(scalar)), "twist", (source,),
                            ))
                for left_weight in range(1, weight - 1):
                    right_weight = weight - left_weight - 1
                    for left in levels[left_weight]:
                        for right in levels[right_weight]:
                            current.append(LatticeConstruction(
                                self.orthogonal_sum((left.lattice, right.lattice)),
                                "orthogonal_sum", (left, right),
                            ))
                            current.append(LatticeConstruction(
                                self.tensor_product((left.lattice, right.lattice)),
                                "tensor_product", (left, right),
                            ))
                levels[weight] = tuple(current)
                yield from levels[weight]
                if exhausted and not any(levels.values()):
                    return
                weight += 1

        def object_enumeration(self, seeds):
            r"""Yield the lattices of :meth:`construction_enumeration` in order."""
            for construction in self.construction_enumeration(seeds):
                yield construction.lattice

        def tensor_product(self, factors):
            r"""Return the tensor product lattice with the product pairing."""
            return _tensor_product_lattice(factors)

        def _categorical_tensor_product(self, left, right):
            return self.tensor_product((left, right))

        def orthogonal_sum(self, summands):
            r"""Return the orthogonal sum, retaining its module biproduct.

            A lattice is a module with a form, so their orthogonal sum is
            the biproduct of the underlying modules carrying the orthogonal
            sum of the forms.  It is taken over the index set: the summand at
            each index has its own block of coordinates, so three summands are
            three and not a two-summand sum whose first summand is a sum.

            ``L + M`` is the two-index case, and ``L ** n`` the constant
            family over an $n$-element index set.

            The empty family gives the zero lattice over this category's
            base ring and retains its empty summand family.
            Supplied nondegenerate placements of all summands are retained
            by the sum, including the empty family, without a new
            determinant or scalar zero decision.

            EXAMPLES::

                sage: Z = Lattices(ZZ).orthogonal_sum(())
                sage: assert Z.base_ring() is ZZ and Z.module_rank() == cardinal(0)
                sage: assert Z.biproduct_factors().cardinality() == cardinal(0)
                sage: W = Lattices(QQ).orthogonal_sum(())
                sage: assert W.base_ring() is QQ and W is not Z
                sage: U = Lattices(ZZ)("U")
                sage: into = Z.from_product_cone((), domain=U)
                sage: out = Z.from_coproduct_cocone((), codomain=U)
                sage: assert all(into(v) == Z.zero() for v in U.module_generators())
                sage: assert out(Z.zero()) == U.zero()
                sage: assert Z.orthogonal_decomposition(()).codomain().module_rank() == cardinal(0)
                sage: from sage_extensions.categories.modules.framed.formed.form_modules import FormModules
                sage: from sage_extensions.categories.sets.set_categories import NN, Sets
                sage: a = Sets().Mor(NN, QQ)(lambda n: QQ(1) + QQ(1)/QQ(2)**int(n))
                sage: x = RR.of_cauchy(a)
                sage: P = Lattices(RR).Nondegenerate()([[x]])
                sage: N = Lattices(RR).Nondegenerate()([[-x]])
                sage: S = Lattices(RR).orthogonal_sum((P, N))
                sage: assert S in FormModules(RR).Nondegenerate()
                sage: assert S.is_nondegenerate() is True
                sage: assert S.witt_index() == ZZ(1)
                sage: assert Lattices(RR).orthogonal_sum(()) in FormModules(RR).Nondegenerate()
            """
            return _orthogonal_sum(summands, self.base_ring())

        def biproduct(self, summands):
            r"""Request a categorical biproduct for form-preserving maps."""
            raise NotImplementedError(
                "orthogonal sums do not supply categorical biproducts for form-preserving maps"
            )

        def _categorical_biproduct(self, left, right):
            raise NotImplementedError(
                "orthogonal sums do not supply categorical biproducts for form-preserving maps"
            )

        def product(self, summands):
            r"""Request a categorical product for form-preserving maps."""
            return self.product_construction(summands).object()

        def coproduct(self, summands):
            r"""Request a categorical coproduct for form-preserving maps."""
            return self.coproduct_construction(summands).object()

        def _categorical_product(self, left, right):
            return self.product((left, right))

        def _categorical_coproduct(self, left, right):
            return self.coproduct((left, right))

        def _categorical_product_construction(self, factors):
            r"""Do not use module-product projections as form-preserving maps."""
            raise NotImplementedError(
                "a categorical lattice product is not supplied by the orthogonal-sum construction"
            )

        def _categorical_coproduct_construction(self, factors):
            r"""Do not use module-coproduct maps as form-preserving maps."""
            raise NotImplementedError(
                "a categorical lattice coproduct is not supplied by the orthogonal-sum construction"
            )

        def coordinate_diagonal_embeddings(self, lattices):
            r"""Return the diagonal embeddings among a finite family of framed lattices.

            For a framed target ``T``, decompose its selected basis into the
            connected components of the graph with an edge ``i--j`` when
            ``b(e_i,e_j) != 0``. Equal Gram blocks occur in groups. A part of
            size ``k`` in one such group gives the diagonal embedding
            ``M(k) -> M^k``. For a collection of parts, divide their sizes by
            their common gcd ``g``; whenever an input source has exactly the
            resulting multiset of Gram blocks, return the represented embedding
            ``source(g) -> T``.

            Each result is ``(source, target, g, embedding, parts)``. ``source``
            and ``target`` are the original objects from ``lattices``;
            ``embedding`` is a live lattice embedding with domain ``source(g)``;
            ``parts`` numbers the target coordinate blocks from zero. The
            identity embedding is omitted.
            """
            from sage.combinat.partition import Partitions

            values = tuple(lattices)
            if any(lattice not in self for lattice in values):
                raise TypeError(
                    f"coordinate diagonal embeddings in {self} require every object to be a lattice of this category"
                )

            def coordinate_blocks(lattice):
                rank = int(lattice.module_rank())
                gram = lattice.gram_tensor()
                cuts = tuple(int(cut) for cut in gram.gram_connected_component_cuts())
                bounds = (0, *cuts, rank)
                return tuple(
                    (
                        tuple(range(start, stop)),
                        tuple(
                            tuple(gram[i, j] for j in range(start, stop))
                            for i in range(start, stop)
                        ),
                    )
                    for start, stop in zip(bounds, bounds[1:])
                )

            def profile(blocks):
                return frozenset(Counter(block for _indices, block in blocks).items())

            blocks_by_lattice = {
                lattice: coordinate_blocks(lattice) for lattice in values
            }
            by_profile = {}
            for lattice in values:
                by_profile.setdefault(profile(blocks_by_lattice[lattice]), []).append(
                    lattice
                )

            def partitions_through(size):
                return tuple(
                    tuple(int(part) for part in partition)
                    for total in range(size + 1)
                    for partition in Partitions(total)
                )

            def choices(groups):
                match groups:
                    case ():
                        return ((),)
                    case (first, *rest):
                        tail = choices(tuple(rest))
                        result = []
                        for partition in partitions_through(len(first)):
                            parts = []
                            start = 0
                            for size in partition:
                                parts.append(tuple(first[start : start + size]))
                                start += size
                            result.extend((tuple(parts) + others) for others in tail)
                        return tuple(result)

            result = []
            for target in values:
                target_blocks = blocks_by_lattice[target]
                groups = {}
                for position, (_indices, block) in enumerate(target_blocks):
                    groups.setdefault(block, []).append(position)
                for parts in choices(tuple(tuple(group) for group in groups.values())):
                    if not parts:
                        continue
                    if len(parts) == len(target_blocks) and all(
                        len(part) == 1 for part in parts
                    ):
                        continue
                    sizes = tuple(len(part) for part in parts)
                    scale = sizes[0]
                    for size in sizes[1:]:
                        scale = gcd(scale, size)
                    wanted_blocks = tuple(
                        tuple(
                            tuple((len(part) // scale) * entry for entry in row)
                            for row in target_blocks[part[0]][1]
                        )
                        for part in parts
                    )
                    wanted_profile = frozenset(Counter(wanted_blocks).items())
                    for source in by_profile.get(wanted_profile, ()):
                        source_blocks = blocks_by_lattice[source]
                        free = Counter(range(len(parts)))
                        images = [None] * int(source.module_rank())
                        ordered_parts = []
                        target_labels = tuple(target.module_generating_set())
                        for indices, block in source_blocks:
                            chosen = next(
                                position
                                for position in free
                                if free[position] and wanted_blocks[position] == block
                            )
                            free[chosen] -= 1
                            part = parts[chosen]
                            ordered_parts.append(part)
                            for local, source_position in enumerate(indices):
                                image = target.zero()
                                for block_position in part:
                                    target_index = target_blocks[block_position][0][
                                        local
                                    ]
                                    image += target.module_generator(
                                        target_labels[target_index]
                                    )
                                images[source_position] = image
                        if any(image is None for image in images):
                            raise RuntimeError(
                                f"failed to construct every basis image of the diagonal embedding {source} -> {target}"
                            )
                        twisted = source.twist(scale)
                        embedding = twisted.Emb(target)(tuple(images))
                        result.append(
                            (
                                source,
                                target,
                                int(scale),
                                embedding,
                                tuple(ordered_parts),
                            )
                        )
            return tuple(result)

    def _repr_(self):
        r"""Return ``Lattices(R)`` with the session name of the base ring.

        This is the cell's text/plain output.  The notebook typesets
        :meth:`_latex_` when it can; both must say ``Lattices(R)``, not
        Sage's "Category of lattices over Integer Ring".

        EXAMPLES::

            sage: from sage_extensions.categories.lattices import Lattices
            sage: Lattices(ZZ)
            Lattices(ZZ)
            sage: Lattices(QQ)
            Lattices(QQ)
        """
        name, _tex = _ring_notation(self.base_ring())
        return f"Lattices({name})"

    def _latex_(self):
        r"""Return ``Lattices(R) \in Cat``, with blackboard bold for `\ZZ`, `\QQ`, `\RR`, `\CC`.

        EXAMPLES::

            sage: from sage_extensions.categories.lattices import Lattices
            sage: latex(Lattices(ZZ))
            \mathrm{Lattices}(\mathbb{Z}) \in \mathrm{Cat}
            sage: latex(Lattices(QQ))
            \mathrm{Lattices}(\mathbb{Q}) \in \mathrm{Cat}
        """
        _name, tex = _ring_notation(self.base_ring())
        return rf"\mathrm{{Lattices}}({tex}) \in \mathrm{{Cat}}"

    def integral_representative_coefficient_bound(
        self, rank: Cardinal | int, determinant: RingElement | int
    ) -> RingElement:
        r"""Bound representative coefficients from the rank and determinant alone.

        Every nondegenerate integral form with these invariants has an
        integral basis with all absolute Gram coefficients at most the
        returned integer. The rank is finite and the determinant is
        nonzero. In rank zero the empty form has coefficient bound zero.
        This computes a bound, not a representative or a basis change.

        Using the invariants alone is essential when enumerating possible
        complementary forms: no complement need already be constructed.
        See the corresponding lattice method and the full proof in
        ``docs/theory/hyperbolic-index.md``.
        """
        integers = _owned_integers()
        assert self.base_ring() is integers, (
            f"integral representative coefficient bounds require Lattices(ZZ), not {self}"
        )
        dimension = cardinal(rank)
        assert dimension.is_finite(), (
            f"an integral representative coefficient bound requires finite rank, not {dimension}"
        )
        n = int(dimension)
        determinant = abs(integers(determinant))
        assert determinant > integers.zero(), (
            "an integral representative coefficient bound requires a nonzero determinant"
        )
        if n == 0:
            return integers.zero()
        if n == 1:
            return determinant
        size = integers(n)
        definite_bound = integers(2)**(n*(n - 1)//2) * determinant
        if n == 2:
            return definite_bound
        epsilon_inverse = (integers(4) * size**3 * integers(6)**n)**(n*n) * (size**3 + size)
        independent_length = integers(2) * size**n * epsilon_inverse**(n - 1)
        basis_length = independent_length**(n*n + 1) + integers.one()
        indefinite_bound = size * basis_length**2 * determinant
        return max(definite_bound, indefinite_bound)

    def integral_isometry_coefficient_bound(
        self, rank: Cardinal | int, first_height: RingElement | int,
        second_height: RingElement | int,
    ) -> RingElement:
        r"""Bound some integral isometry from dimension and Gram heights.

        For nondegenerate symmetric integral matrices A,B of common rank
        n >= 3 and maximum absolute entries at most first_height and
        second_height, integral equivalence implies the existence of a
        unimodular U with U.transpose()*A*U == B and every entry bounded
        by this integer. This computes neither existence nor U.

        Calderon, arXiv:2202.10257v2, Theorem 4.1 and Appendix F supply
        the indefinite estimate. The theory note makes its remaining
        spherical-function and Haar-volume factors explicit and includes
        the separate S={infinity} volume factor. In the definite case
        inverse-Gram Cauchy--Schwarz gives a smaller bound. All powers
        here are integers; fractional exponents are rounded upward.
        """
        from math import factorial

        integers = _owned_integers()
        assert self.base_ring() is integers, "integral isometry bounds require ZZ"
        dimension = cardinal(rank)
        assert dimension.is_finite(), "an integral isometry bound needs finite rank"
        n = int(dimension)
        assert n >= 3, "this uniform integral isometry bound requires rank at least three"
        first_height, second_height = integers(first_height), integers(second_height)
        assert first_height > 0 and second_height > 0, "Gram heights must be positive"
        size, two, three = integers(n), integers(2), integers(3)
        fact = integers(factorial(n))
        bump = integers(10)**(n*n) * size**(((n + 2)**2 + 3)//4)
        smooth = three * (three * size**2 * fact)**((n*(n - 1) + 7)//4) * bump
        dynamics = integers(12) * two**(3*n*n*(n - 1)) * size**2 * integers(15)**6 * smooth**12
        transverse_dimension = n*(n + 1)//2 - 1
        lattice_volume = two**(2*n**3 + 1)
        orbit_volume = (
            two**(2*n**6)
            * (two**(2*n**3 + 5) * three**(4*n**4) * size**(6*n**3 + 1))**transverse_dimension
            * lattice_volume
        )
        coefficient = (
            two**(6*n**3) * size**(4*n**3) * fact**(2*n*n + 1)
            * dynamics * orbit_volume**6
        )
        return coefficient * (integers(4) * first_height * second_height)**(2*n**3)

    class ParentMethods:
        r"""Operations generic to every lattice.

        The datum this level introduces is the Gram presentation of the form
        in the framing of the module the form is stated on.  The form itself
        and that module are the datum of ``FormModules(R)``, which the
        construction computes from the presentation.
        """

        def _pairing_value_module(self):
            r"""The lattice pairing has scalar values, independent of their module realization."""
            return self.base_ring()

        if TYPE_CHECKING:

            def linear_combination(
                self,
                coefficients: Mapping[Hashable, RingElement | int],
            ) -> Lattices.ElementMethods: ...

        def base_ring(self) -> _OwnedRingParent:
            return super().base_ring()

        def __init__(self, gram_tensor, **rest) -> None:
            self._preamble_gram_tensor = gram_tensor
            super().__init__(**rest)

        def _added_structure(self, construction_data: dict[str, ConstructionData]) -> tuple[tuple[Category, ...], dict[str, ConstructionData]]:
            r"""The Gram tensor this level adds, kept when the lattice is constructed again (``OWN-05``; see ``Objects``)."""
            categories, data = super()._added_structure(construction_data)
            return categories, {"gram_tensor": self.gram_tensor(), **data}

        def _first_ngens(self, n):
            r"""Return the first ``n`` module generators, for Sage's ``L.<e,f> =`` naming syntax."""
            labels = self.module_generating_set()
            return tuple(
                self.module_generator(labels[position]) for position in range(int(n))
            )

        def lattice_category(self):
            r"""Return the base-ring lattice category owning this object."""
            return Lattices(self.base_ring())

        def subobject_on(self, module_generating_set):
            r"""Return the span with the restricted lattice form."""

            basis = _span_basis_elements(self, module_generating_set)
            return _lattice_subobject_spanning(self, basis)

        def sublattice_from(self, vectors, *, saturate=False):
            r"""Return the lattice subobject spanned by ``vectors``.

            When ``saturate`` is true, first take the primitive closure of the
            underlying module inclusion and then rebuild the restricted form on
            that saturated embedded basis.  Thus the result is still a lattice
            subobject of ``self`` rather than a bare saturated module.
            """
            span = self.subobject_on(vectors)
            if not saturate:
                return span
            saturated_module = span.inclusion().saturation()
            embedded_basis = tuple(
                saturated_module.inclusion()(generator)
                for generator in saturated_module.module_generators()
            )
            return self.subobject_on(embedded_basis)

        def primitive_sublattice_from(self, vectors):
            r"""Return the saturated lattice subobject generated by ``vectors``."""
            return self.sublattice_from(vectors, saturate=True)

        def ambient_lattice(self):
            r"""Return the ambient lattice of a represented lattice subobject."""
            if self not in ModuleSubobjects(self.base_ring()):
                raise TypeError(
                    f"{self!r} is not included in a larger lattice: it is not a sublattice with an inclusion into a lattice, only an object of {self.category()}"
                )
            return self.inclusion().codomain()

        def lattice_basis(self):
            r"""Return the selected lattice basis as actual lattice elements."""
            return self.module_generators()

        def rank(self):
            r"""Return the lattice rank."""
            return self.module_rank()

        def saturation(self):
            r"""Return the primitive closure as a lattice subobject of the same ambient lattice."""
            if self not in ModuleSubobjects(self.base_ring()):
                raise TypeError(
                    f"cannot saturate {self!r}: saturation is taken of a sublattice with an inclusion into a lattice, but {self!r} is only an object of {self.category()}"
                )
            ambient = self.inclusion().codomain()
            saturated_module = self.inclusion().saturation()
            embedded_basis = tuple(
                saturated_module.inclusion()(generator)
                for generator in saturated_module.module_generators()
            )
            return ambient.subobject_on(embedded_basis)

        def orthogonal_complement(self, sublattice=None):
            r"""Return an orthogonal lattice subobject.

            ``L.orthogonal_complement(I)`` computes ``I^perp`` in ``L``.  On a
            lattice that is itself represented as a subobject, omitting ``I``
            retains the existing ``I.orthogonal_complement()`` convention.
            """
            if sublattice is None:
                if self not in ModuleSubobjects(self.base_ring()):
                    raise TypeError(
                        f"{self!r}.orthogonal_complement() with no argument needs {self!r} to be a sublattice with an inclusion into a lattice, but it is only an object of {self.category()}; pass the sublattice whose orthogonal complement is wanted"
                    )
                return self.inclusion().orthogonal_complement()
            if sublattice not in ModuleSubobjects(self.base_ring()):
                raise TypeError(
                    f"cannot take the orthogonal complement of {sublattice!r} in {self!r}: it is not a sublattice with an inclusion into a lattice"
                )
            inclusion = sublattice.inclusion()
            if inclusion.codomain() is not self:
                raise ValueError(
                    f"cannot take the orthogonal complement of {sublattice!r} in {self!r}: it is a sublattice of {inclusion.codomain()!r}, not of {self!r}"
                )
            return inclusion.orthogonal_complement()

        def integral_isometry(self, morphism, *, source=None):
            r"""Descend a rational isometry onto this integral lattice.

            A formed scalar extension retains its defining source lattice.
            That source supplies the integral model even when the rational
            endpoints differ. A rational space presented without an integral
            model requires ``source`` explicitly. Both directions must
            preserve the stated lattices; raise ``ValueError`` otherwise.

            EXAMPLES::

                sage: L = Lattices(ZZ)("U")
                sage: V = L.vector_space()
                sage: phi = V.Isom(V)(lambda label: -V.module_generator(label))
                sage: g = L.integral_isometry(phi)
                sage: all(g(x) == -x for x in L.module_generators())
                True
                sage: labels = tuple(V.module_generating_set())
                sage: e, f = V.module_generator(labels[0]), V.module_generator(labels[1])
                sage: dilation = V.Isom(V)(lambda j: V.scalar_multiple(QQ(2), e) if j == labels[0] else V.scalar_multiple(QQ(1)/QQ(2), f))
                sage: L.integral_isometry(dilation)
                Traceback (most recent call last):
                ...
                ValueError: the rational isometry does not map the source integral lattice onto the target
            """
            if source is None:
                from sage_extensions.categories.modules.framed.formed.form_modules import (
                    FormBaseChanges,
                )

                rational_source = morphism.domain()
                if rational_source in FormBaseChanges(rational_source.base_ring()):
                    source = rational_source.base_change_source()
                    if (
                        rational_source.base_change_ring_map()
                        != self.base_ring().fraction_field_map()
                    ):
                        raise ValueError(
                            "the rational source must retain scalar extension from the target integral ring"
                        )
                elif rational_source is self.vector_space():
                    source = self
                else:
                    raise ValueError(
                        "the source integral lattice must be supplied for distinct rational endpoints"
                    )
            isometry = morphism.integral_restriction(source, self)
            if isometry is None:
                raise ValueError(
                    "the rational isometry does not map the source integral lattice onto the target"
                )
            return isometry

        def orthogonal_decomposition(self, embeddings):
            r"""Return ``self -> direct_sum(S_i)`` for chosen orthogonal embeddings.

            The embeddings must have codomain ``self`` and assemble to an
            isometry from their orthogonal biproduct. Form preservation is
            a hypothesis on these data; the inverse computation requires
            invertibility, so an orthogonal finite-index sublattice is not
            a decomposition.
            The result retains all summands, injections and projections.
            """
            embeddings = tuple(embeddings)
            if any(embedding.codomain() is not self for embedding in embeddings):
                raise ValueError(
                    "orthogonal summand embeddings must end in the ambient lattice"
                )
            normal = Lattices(self.base_ring()).orthogonal_sum(
                tuple(embedding.domain() for embedding in embeddings)
            )
            assembled = normal.from_coproduct_cocone(embeddings, codomain=self)
            return normal.Isom(self)(
                lambda label: assembled(normal.module_generator(label))
            ).inverse()

        def perp(self, sublattice=None):
            r"""Synonym for :meth:`orthogonal_complement`."""
            return self.orthogonal_complement(sublattice)

        def _root_subobject_on(self, simple_roots, root_system_type_name):
            r"""Return the root sublattice framed by its simple roots, with its root-system label.

            A simple system is a basis of the root lattice it spans (Humphreys,
            *Introduction to Lie Algebras and Representation Theory*, §10.1), so
            the simple roots frame the sublattice and its
            :meth:`simple_roots` returns them.
            """
            return _lattice_subobject_spanning(
                self,
                tuple(simple_roots),
                root_system_type_name=root_system_type_name,
            )


        def _Hom_(self, codomain, category=None):
            lattices = Lattices(self.base_ring())
            if codomain in lattices and (
                category is None or category.is_subcategory(lattices)
            ):
                return _lattice_mor(self, codomain)
            return super()._Hom_(codomain, category)

        def Emb(self, codomain):
            r"""Return the set of form-preserving embeddings into ``codomain``."""

            return _lattice_embedding_mor(self, codomain)

        def Isom(self, codomain):
            r"""Return the set of isometries to ``codomain``."""

            return _lattice_isometry_mor(self, codomain)

        @object_level
        def Aut(self):
            r"""Return ``Isom(L,L)``, the orthogonal automorphism Mor."""
            return self.Isom(self)

        def orthogonal_group(self):
            r"""Return ``O(L,b)=Aut(L,b)`` as the owned isometry group."""
            return self.Aut()

        O = orthogonal_group

        def bilinear_orthogonal_group(self):
            r"""Return ``O(L,b)``; explicit name for the lattice pairing."""
            return self.Aut()

        def quadratic_orthogonal_group(self):
            r"""Return ``O(L,q)`` for ``q(x)=b(x,x)``.

            On a free integral lattice, preserving the symmetric bilinear form
            and preserving its diagonal quadratic form are equivalent, so this
            is the same represented group as ``O(L,b)``.
            """
            return self.Aut()

        @cached_method
        def discriminant_representation(self):
            r"""Return ``rho_L:O(L)->O(A_L)`` by functoriality of discriminants."""
            source = self.Aut()
            target = self.discriminant_group().orthogonal_group()
            return OwnedGroups().Mor(source, target)(lambda isometry: isometry.discriminant_morphism())

        @cached_method
        def discriminant_image(self):
            r"""Return the computed image of ``rho_L`` when ``O(L)`` generators are known.

            EXAMPLES::

                sage: L = Lattices(ZZ)("A2")
                sage: rho = L.discriminant_representation()
                sage: Q = L.discriminant_group().orthogonal_group()
                sage: H = rho.preimage_subgroup(Q.subgroup(tuple(Q.group_generators())))
                sage: all(g in H for g in H.schreier_generators())
                True
                sage: H.image_under(rho).cardinality() == Q.cardinality() == 2
                True
            """
            return self.Aut().discriminant_image()

        @cached_method
        def discriminant_representation_is_surjective(self) -> bool:
            r"""Return whether the computed discriminant image equals ``O(A_L)``."""
            image = self.discriminant_image()
            return (
                image.cardinality()
                == self.discriminant_group().orthogonal_group().cardinality()
            )

        @cached_method
        def stable_orthogonal_group(self):
            r"""Return \(\tilde O(L)=\ker(O(L)\to O(A_L))\), the stable orthogonal group.

            It is the kernel of the discriminant reduction morphism
            :meth:`discriminant_representation`, the first term of
            :meth:`discriminant_reduction_sequence` (Gritsenko--Hulek--Sankaran,
            *Abelianisation of orthogonal groups*, arXiv:0810.1614, §1).

            EXAMPLES::

                sage: L = Lattices(ZZ)("A2")
                sage: stable = L.stable_orthogonal_group()
                sage: generators = stable.schreier_generators()
                sage: all(g in stable for g in generators)
                True
                sage: stable.image_under(L.discriminant_representation()).cardinality() == 1
                True
                sage: L = Lattices(ZZ)([[0,2],[2,0]])
                sage: O = L.Aut()
                sage: exchange = O([[0,1],[1,0]])
                sage: minus_id = O([[-1,0],[0,-1]])
                sage: generators = L.stable_orthogonal_group().schreier_generators(generators=(exchange, minus_id))
                sage: rho = L.discriminant_representation()
                sage: all(rho(g) == rho.codomain().one() for g in generators)
                True
                sage: L.stable_orthogonal_group().image_under(rho, ambient_generators=(exchange, minus_id)).cardinality() == 1
                True
            """
            target = self.discriminant_group().orthogonal_group()
            trivial = target.subgroup_on(())
            return self.Aut().discriminant_preimage(trivial)

        @cached_method
        def discriminant_reduction_sequence(self):
            r"""Return \(1\to\tilde O(L)\to O(L)\xrightarrow{f}O(A_L)\to C_L\to 1\).

            ``f`` is :meth:`discriminant_representation`, its kernel is
            :meth:`stable_orthogonal_group`, and \(C_L=O(A_L)/f(O(L))\).
            """
            return DiscriminantReductionSequence(self)

        def discriminant_sequence_data(self):
            r"""Return the finite discriminant-action/coset data used by catalogue certification."""
            from sage_extensions.categories.lattice_orbit_invariants import (
                discriminant_sequence_data,
            )

            return discriminant_sequence_data(self)

        def primitive_orbit_series(self, bound=4):
            r"""Return the bounded primitive-vector orbit series for the standard orthogonal subgroups."""
            from sage_extensions.categories.lattice_orbit_invariants import (
                primitive_orbit_series,
            )

            return primitive_orbit_series(self, bound=bound)

        def discriminant_orbit_series(self, bound=4):
            r"""Return the bounded discriminant-form orbit series used under the Eichler ``U^2`` hypothesis."""
            from sage_extensions.categories.lattice_orbit_invariants import (
                discriminant_orbit_series,
            )

            return discriminant_orbit_series(self, bound=bound)

        @cached_method
        def special_orthogonal_group(self):
            r"""Return ``SO(L)=ker(det:O(L)->{+-1})`` as a predicate subgroup."""

            orthogonal = self.Aut()
            special = orthogonal.predicate_subgroup(
                lambda automorphism: automorphism.determinant() == 1,
                "det(g)=1",
                character_data={"determinant_kernel": True},
            )

            def generators():
                from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

                signs = Groups.C(2)
                determinant = orthogonal.Mor(signs).elementwise(
                    lambda isometry: signs.one() if isometry.determinant() == 1 else signs.group_generators()[0]
                )
                return finite_ordered_set(tuple(determinant.kernel().group_generators()))

            special.select_group_generators(generators)
            return special

        def SO(self, *args, **kwargs):
            return self.special_orthogonal_group(*args, **kwargs)

        @cached_method(key=lambda self, ring_map: id(ring_map))
        def base_change(self, ring_map) -> Lattices.ParentMethods:
            r"""Return \(L\otimes_R S\) along ``ring_map`` \(\varphi\colon R\to S\), a lattice over \(S\).

            The scalar extension of the underlying free module is the free
            \(S\)-module on the same framing, and the form extends
            \(S\)-bilinearly, so its Gram presentation is \(\varphi(G_L)\).  The
            result is constructed in ``Lattices(S)`` on those data and keeps
            the framing labels of \(L\).  Along the identity of \(R\) it is
            \(L\).  Along \(R\to\operatorname{Frac}(R)\) it is the quadratic
            space \(L_K=L\otimes_R K\) that :meth:`vector_space` returns.

            In finite rank, supplied unimodularity survives every base
            change. Supplied nondegeneracy survives known injective maps
            between integral domains. Neither is inferred from an
            arbitrary nonflat base change.

            EXAMPLES::

                sage: from sage_extensions.categories.modules.framed.formed.form_modules import FormModules
                sage: L = Lattices(ZZ).Nondegenerate()([[2]])
                sage: V = L.base_change(ZZ.fraction_field_map())
                sage: assert V in FormModules(QQ).Nondegenerate()
                sage: assert V.base_change_source() is L
                sage: S = ZZ.quotient_ring(ZZ.ideal(2))
                sage: reduced = L.base_change(S.quotient_map())
                sage: assert reduced.gram_tensor()[0, 0] == S.zero()
                sage: assert reduced not in FormModules(S).Nondegenerate()
                sage: U = Lattices(ZZ).Unimodular()("U")
                sage: assert U.base_change(S.quotient_map()) in FormModules(S).Unimodular()
            """
            from sage_extensions.categories.modules.framed.formed.form_modules import (
                FormBaseChanges,
            )

            return FormBaseChanges(ring_map.codomain())(self, ring_map)

        def orthogonal_group_base_change(self, ring_map):
            r"""Return \(O(L)\to O(L\otimes_R S)\), \(g\mapsto g\otimes S\), along ``ring_map``.

            Scalar extension is a functor, so it carries an isometry of \(L\)
            to an isometry of \(L\otimes_R S\), whose form is the scalar
            extension of the form of \(L\), and it respects composition: this
            is a group morphism.  The image of \(g\) sends \(e\otimes 1\) to
            \(g(e)\otimes 1\) on the framing, through the scalar-extension
            unit \(x\mapsto x\otimes 1\).  It is injective when that unit is,
            as it is along \(R\to\operatorname{Frac}(R)\) for a lattice.
            """
            changed = self.base_change(ring_map)
            target = changed.Aut()

            def extend(isometry):
                return target(
                    lambda label: _base_change_element(
                        self,
                        changed,
                        ring_map,
                        isometry(self.module_generator(label)),
                    )
                )

            return self.Aut().Mor(target)(extend)

        @cached_method
        def witt_index(self):
            r"""Return the Witt index of \(L_K=L\otimes_R K\), \(K=\operatorname{Frac}(R)\).

            The Witt index of a nondegenerate quadratic space \(V\) is the
            common dimension of its maximal totally isotropic subspaces, and
            it is the number \(r\) of hyperbolic planes in a splitting
            \(V=H_1\perp\cdots\perp H_r\perp V_0\) with \(V_0\) zero or
            anisotropic (O'Meara, *Introduction to Quadratic Forms*, §42F).
            A lattice answers through its quadratic space :meth:`vector_space`.
            Over QQ, repeated exact rational isotropy decisions and orthogonal
            plane splittings give the Witt index. Other supported number
            fields use the private OSCAR/Hecke realization.
            Over AA and RR, Sylvester's law gives
            ``min(p,q)`` from exact signature. For RR, congruence and the
            owned scalar sign decisions must succeed; undecided signs
            are refused instead of being counted as zero or negative.

            EXAMPLES::

                sage: V = Lattices(AA)([[1, 0], [0, -2]])
                sage: assert V.witt_index() == ZZ(1)
                sage: assert V.is_anisotropic() is False
                sage: D = Lattices(AA)([[2]])
                sage: assert D.witt_index() == ZZ(0)
                sage: assert D.is_anisotropic() is True
                sage: a = RR.pi()
                sage: V = Lattices(RR)([[a, 0], [0, -1]])
                sage: assert V.witt_index() == ZZ(1)
                sage: assert V.is_anisotropic() is False
            """
            space = self.vector_space()
            if space is not self:
                return space.witt_index()
            field = self.base_ring()
            assert self.module_rank().is_finite() and self.is_nondegenerate(), (
                f"the Witt index is defined here for a nondegenerate quadratic space of finite dimension, and {self!r} is not one"
            )
            if self.module_rank() == cardinal(0):
                return _owned_integers().zero()
            from sage.rings.rational_field import QQ as SageQQ
            from sage_extensions.categories.rings.ring_foundation import (
                _owned_real_algebraic_numbers,
            )

            from sage_extensions.categories.rings.number_fields import (
                NumberFieldsWithChosenPrimitiveElement,
                OwnedNumberFields,
            )

            from sage_extensions.rings.real import RR

            match field:
                case _ if field is _owned_real_algebraic_numbers():
                    _anisotropic, hyperbolic = lattice_engines._real_witt_bases(self)
                    index = int(hyperbolic.cardinality()) // 2
                case _ if field is RR:
                    signature = self.signature_pair()
                    index = min(
                        signature.first().finite_value(),
                        signature.second().finite_value(),
                    )
                case _ if _engine_ring(field) is SageQQ:
                    index = lattice_engines._rational_witt_index(self)
                case _ if (
                    field in OwnedNumberFields()
                    and field in NumberFieldsWithChosenPrimitiveElement()
                    and _engine_ring(field).is_absolute()
                ):
                    index = lattice_engines._oscar_lattices.number_field_witt_index(
                        field, self.gram_tensor()
                    )
                case _:
                    assert False, (
                        f"the Witt index of {self!r} is computed here over AA, RR and represented absolute number fields, but {self!r} is over {field}"
                    )
            integers = _owned_integers()
            return _owned_engine_element(integers, SageZZ(index))

        @cached_method
        def diagonalization(self):
            r"""Return an isometry from a diagonal space to this space.

            This is congruence diagonalization of a finite symmetric
            bilinear space over an exact field of characteristic not two.
            The space may be degenerate. The returned map retains the
            diagonal space, its basis, evaluation in the original space
            and its inverse. An integral lattice must first be extended
            to its desired coefficient field: rational diagonalization
            need not be an integral change of basis.

            The private computation reuses Sage's
            ``QuadraticForm.rational_diagonal_form(return_matrix=True)``
            with its documented law ``T.transpose()*G*T == D.matrix()``.
            Over RR with supplied nondegeneracy it instead refines a
            finite family of norm enclosures until a nonisotropic pivot
            is found, then uses fraction-free orthogonal projection.
            The inverse is retained through the elementary basis changes;
            no arbitrary-real zero decision or later inversion is needed.

            EXAMPLES::

                sage: V = Lattices(QQ)("U")
                sage: phi = V.diagonalization()
                sage: D = phi.domain()
                sage: assert phi.codomain() is V
                sage: assert all(D.b(x,y) == 0 for i,x in enumerate(D.module_generators()) for j,y in enumerate(D.module_generators()) if i != j)
                sage: assert V.gram_tensor().pullback(phi) == D.gram_tensor()
                sage: assert all(phi(phi.inverse()(v)) == v for v in V.module_generators())
                sage: R = Lattices(AA)([[0, 1, 0], [1, 0, 0], [0, 0, 0]])
                sage: psi = R.diagonalization()
                sage: assert R.gram_tensor().pullback(psi) == psi.domain().gram_tensor()
                sage: assert Lattices(QQ)(0).diagonalization().domain().module_rank() == 0
                sage: W = Lattices(RR)([[0, RR.pi(), 0], [RR.pi(), 0, 0], [0, 0, 0]])
                sage: phi = W.diagonalization()
                sage: assert W.gram_tensor().pullback(phi) == phi.domain().gram_tensor()
                sage: assert W.signature_pair().first() == cardinal(1)
                sage: assert W.signature_pair().second() == cardinal(1)
                sage: assert all(phi(phi.inverse()(v)) == v for v in W.module_generators())
                sage: assert all(phi.inverse()(phi(v)) == v for v in phi.domain().module_generators())
                sage: H = Lattices(RR).Nondegenerate()([[0, 1], [1, 0]])
                sage: rho = H.diagonalization()
                sage: assert rho.codomain() is H
                sage: assert H.gram_tensor().pullback(rho) == rho.domain().gram_tensor()
                sage: assert all(rho(rho.inverse()(v)) == v for v in H.module_generators())
                sage: assert all(rho.inverse()(rho(v)) == v for v in rho.domain().module_generators())
                sage: from sage_extensions.categories.sets.set_categories import NN, Sets
                sage: a = Sets().Mor(NN, QQ)(lambda n: QQ(1) + QQ(1)/QQ(2)**int(n))
                sage: z = Sets().Mor(NN, QQ)(lambda n: QQ(1)/QQ(2)**int(n))
                sage: x, t = RR.of_cauchy(a), RR.of_cauchy(z)
                sage: C = Lattices(RR).Nondegenerate()([[t, x], [x, t]])
                sage: eta = C.diagonalization()
                sage: assert eta.codomain() is C
                sage: assert eta.inverse().domain() is C
                sage: assert eta.inverse().codomain() is eta.domain()
                sage: assert eta.domain().signature_pair().first() == cardinal(1)
                sage: assert eta.domain().signature_pair().second() == cardinal(1)
                sage: Z = Lattices(RR).Nondegenerate()(0)
                sage: empty = Z.diagonalization()
                sage: assert empty(empty.domain().zero()) == Z.zero()
                sage: assert empty.inverse()(Z.zero()) == empty.domain().zero()
            """
            from sage_extensions.categories.rings.ring_foundation import OwnedFields

            field = self.base_ring()
            assert field in OwnedFields() and field.is_exact(), (
                f"exact congruence diagonalization of {self} requires an exact coefficient field"
            )
            assert field(2) != field.zero(), (
                f"congruence diagonalization of {self} requires characteristic different from two"
            )
            assert self.module_rank().is_finite(), (
                f"congruence diagonalization of {self} requires a finite basis"
            )
            return lattice_engines._congruence_diagonalization(self)

        @cached_method
        def witt_decomposition(self):
            r"""Return an isometry ``U^w orthogonal_sum A -> self`` over a field.

            Here ``self`` is nondegenerate and finite-dimensional and
            ``A`` is anisotropic. The returned domain retains the
            hyperbolic summand at index zero and ``A`` at index one,
            including their inclusions and projections. This is the
            field-valued Witt decomposition of
            ``LeanCategories/Lattices/Valued/Witt.lean``; the displayed
            order and direction are fixed by this method's contract.
            To decompose an integral lattice rationally, first extend
            scalars along its fraction-field map.

            The QQ computation repeatedly uses the exact rational
            isotropy decision and witness, then splits the plane given
            by its hyperbolic partner. The terminal complement is
            anisotropic by the same decision.
            Over AA or represented exact RR, congruence diagonalization
            and decided scalar signs and positive square roots supply the
            normalized hyperbolic pairs and a definite complement. RR
            accepts closed expressions and regular Cauchy presentations;
            nonsingular RR Witt-basis normalization refines signs under
            known nonzero hypotheses. Explicit normalization and pair
            coordinate changes retain the inverse of the returned map,
            without generic span reduction or another matrix inversion.

            EXAMPLES::

                sage: V = Lattices(QQ)("U") + Lattices(QQ)([[-2]])
                sage: phi = V.witt_decomposition()
                sage: assert phi.codomain() is V
                sage: H = phi.domain().biproduct_factor(0)
                sage: A = phi.domain().biproduct_factor(1)
                sage: assert H.module_rank() == 2 and A.module_rank() == 1
                sage: assert A.is_anisotropic() is True
                sage: assert V.gram_tensor().pullback(phi) == phi.domain().gram_tensor()
                sage: assert all(phi.inverse()(phi(v)) == v for v in phi.domain().module_generators())
                sage: Z = Lattices(QQ)(0)
                sage: assert Z.witt_decomposition().codomain() is Z
                sage: empty = Z.witt_decomposition()
                sage: assert Z.witt_index() == ZZ.zero()
                sage: assert empty.domain().biproduct_factor(1) is Z
                sage: assert empty(empty.inverse()(Z.zero())) == Z.zero()
                sage: assert empty.inverse()(empty(empty.domain().zero())) == empty.domain().zero()
                sage: W = Lattices(QQ)([[1, 0], [0, -2]])
                sage: assert W.witt_decomposition().domain().biproduct_factor(0).module_rank() == 0
                sage: V = Lattices(AA)([[0, 1, 0], [1, 0, 0], [0, 0, -2]])
                sage: phi = V.witt_decomposition()
                sage: assert V.gram_tensor().pullback(phi) == phi.domain().gram_tensor()
                sage: assert phi.domain().biproduct_factor(0).module_rank() == 2
                sage: assert phi.domain().biproduct_factor(1).is_anisotropic() is True
                sage: assert all(phi(phi.inverse()(v)) == v for v in V.module_generators())
                sage: Z = Lattices(RR).Nondegenerate()(0)
                sage: empty = Z.witt_decomposition()
                sage: assert empty.codomain() is Z
                sage: assert empty.domain().biproduct_factor(0).module_rank() == 0
                sage: assert empty.domain().biproduct_factor(1).module_rank() == 0
                sage: from sage_extensions.categories.sets.set_categories import NN, Sets
                sage: a = Sets().Mor(NN, QQ)(lambda n: QQ(1) + QQ(1)/QQ(2)**int(n))
                sage: x = RR.of_cauchy(a)
                sage: C = Lattices(RR).Nondegenerate()([[x, 0, 0], [0, -x, 0], [0, 0, x]])
                sage: eta = C.witt_decomposition()
                sage: assert eta.codomain() is C and eta.inverse().domain() is C
                sage: assert eta.inverse().codomain() is eta.domain()
                sage: assert eta.domain().biproduct_factor(0).module_rank() == 2
                sage: assert eta.domain().biproduct_factor(1).module_rank() == 1
                sage: assert Lattices(AA)(0).witt_decomposition().domain().module_rank() == 0
                sage: V = Lattices(RR)([[RR.pi(), 0], [0, -1]])
                sage: phi = V.witt_decomposition()
                sage: assert phi.codomain() is V
                sage: assert V.gram_tensor().pullback(phi) == phi.domain().gram_tensor()
                sage: assert all(phi(phi.inverse()(v)) == v for v in V.module_generators())
            """
            from sage_extensions.categories.rings.ring_foundation import (
                OwnedFields,
                _owned_rationals,
                _owned_real_algebraic_numbers,
            )

            from sage_extensions.rings.real import RR

            field = self.base_ring()
            assert field in OwnedFields(), (
                f"a Witt decomposition is taken over a field, but {self} is over {field}; "
                "extend scalars to the desired field first"
            )
            assert self.module_rank().is_finite() and self.is_nondegenerate(), (
                f"a Witt decomposition of {self} requires a nondegenerate finite-dimensional form"
            )
            if self.module_rank() == cardinal(0):
                hyperbolic = Lattices(field)("U") ** 0
                normal = Lattices(field).orthogonal_sum((hyperbolic, self))
                forward = normal.module_category().Mor(normal, self)(())
                backward = self.module_category().Mor(self, normal)(())
                module_isomorphism = normal.module_category().Core().Mor(normal, self)._from_known_inverse_pair(
                    forward, backward,
                )
                isometries = normal.Isom(self)
                return isometries.element_class(isometries, module_isomorphism)
            if field is _owned_rationals():
                return self._rational_witt_decomposition()
            if field is RR:
                return lattice_engines._real_witt_decomposition(self)
            if field is _owned_real_algebraic_numbers():
                anisotropic_basis, hyperbolic_basis = (
                    lattice_engines._real_witt_bases(self)
                )
            else:
                raise NotImplementedError(
                    f"a Witt decomposition of {self} is computed here over QQ, AA and RR, not {field}"
                )
            complement = self.subobject_on(anisotropic_basis)
            plane = Lattices(field)("U")
            hyperbolic = plane ** (int(hyperbolic_basis.cardinality()) // 2)
            labels = hyperbolic.module_generating_set()
            inclusion = hyperbolic.Emb(self)(
                lambda label: hyperbolic_basis.value(labels.ranking_map()(label))
            )
            return self.orthogonal_decomposition(
                (inclusion, complement.inclusion())
            ).inverse()

        @cached_method
        def _rational_witt_decomposition(self):
            r"""Split rational hyperbolic planes until the complement is anisotropic."""
            ring = self.base_ring()
            assert ring is _owned_rationals() and self.is_nondegenerate()
            plane = Lattices(ring)("U")
            if self.is_isotropic() is True:
                isotropic = self.isotropic_vector()
                partner = isotropic.hyperbolic_partner()
                first = plane.Emb(self)((isotropic, partner)).orthogonal_splitting()
                complement = first.domain().biproduct_factor(1)
                lower = complement._rational_witt_decomposition()
                return self._extend_hyperbolic_splitting(first, lower)
            hyperbolic = plane ** 0
            inclusion = hyperbolic.Emb(self)(())
            return self.orthogonal_decomposition(
                (inclusion, self.Aut().identity())
            ).inverse()

        def _extend_hyperbolic_splitting(self, first, lower):
            r"""Combine a chosen plane and the splitting of its complement."""
            lower_plane = lower.domain().biproduct_factor(0)
            lower_index = int(lower_plane.module_rank()) // 2
            if lower_index == 0:
                return first
            lower_inclusion = lower.domain().injection(0)
            complement_inclusion = first.domain().injection(1)
            images = tuple(
                first(first.domain().injection(0)(vector))
                for vector in first.domain().biproduct_factor(0).module_generators()
            ) + tuple(
                first(complement_inclusion(lower(lower_inclusion(vector))))
                for vector in lower_plane.module_generators()
            )
            hyperbolic = Lattices(self.base_ring())("U") ** (lower_index + 1)
            return hyperbolic.Emb(self)(images).orthogonal_splitting()

        def is_isotropic(self) -> bool | Predicate:
            r"""Return whether $L_K$ contains a nonzero isotropic vector.

            Here $K=\operatorname{Frac}(R)$. A nonzero radical already gives
            an isotropic vector; in the nondegenerate case isotropy is
            equivalent to positive Witt index.  Over ``ZZ`` and ``QQ`` the
            question is whether ``b(x, x) = 0`` has a nonzero rational
            solution, which PARI's ``qfsolve`` decides with a witness or an
            obstruction (Hasse--Minkowski, Serre, *A Course in Arithmetic*,
            Ch. IV, 3.2, Thm. 8); ``TRAPS.md`` records why this route is not
            the Witt index.
            If nondegeneracy itself is undecided, the common formed-module
            zero-fibre construction retains the isotropy proposition.
            An undecided hypothesis does not produce ``None``.
            """
            from sage.rings.rational_field import QQ as SageQQ

            rank = self.module_rank()
            if not rank.is_finite():
                raise ValueError(
                    f"isotropy is defined here for finite-rank lattices, not {self!r}"
                )
            match self.is_nondegenerate():
                case False:
                    return int(rank) > 0
                case True if (
                    _engine_ring(self.base_ring()) is SageZZ
                    or _engine_ring(self.base_ring()) is SageQQ
                ):
                    return lattice_engines._isotropic_vector_witness(self) is not None
                case True:
                    return bool(self.witt_index() > 0)
                case _:
                    return super().is_isotropic()

        def isotropic_vector(self) -> Lattices.ElementMethods:
            r"""Return a nonzero isotropic vector; raise ``ValueError`` if none exists.

            PARI supplies the witness over QQ. Over ZZ the returned vector
            is integral and primitive. A nonzero radical also supplies a
            witness; the zero lattice has none. Over AA the retained
            diagonalization supplies a radical vector or a normalized
            opposite-sign pair, without enumerating real points. The same
            construction applies to RR when its exact scalar
            operations and comparisons are decided. With supplied
            nondegeneracy, RR instead refines signs of nonzero diagonal
            entries and normalizes under established positivity hypotheses.

            EXAMPLES::

                sage: L = Lattices(ZZ)([[3, 0, 0, 0], [0, 5, 0, 0], [0, 0, -7, 0], [0, 0, 0, -11]])
                sage: v = L.isotropic_vector()
                sage: v.parent() is L and v != L.zero() and v.q() == ZZ(0) and v.content() == ZZ(1)
                True
                sage: Lattices(ZZ)([[1, 0], [0, -2]]).isotropic_vector()
                Traceback (most recent call last):
                ...
                ValueError: the lattice has no nonzero isotropic vector
                sage: D = Lattices(ZZ)([[0, 0], [0, 2]])
                sage: r = D.isotropic_vector()
                sage: r != D.zero() and r.q() == ZZ(0)
                True
                sage: V = Lattices(AA)([[1, 0], [0, -2]])
                sage: v = V.isotropic_vector()
                sage: assert v.parent() is V and v != V.zero() and V.q(v) == AA(0)
                sage: D = Lattices(AA)([[2, 0], [0, 0]])
                sage: assert D.isotropic_vector() != D.zero()
            """
            from sage_extensions.categories.rings.ring_foundation import _owned_real_algebraic_numbers
            from sage_extensions.rings.real import RR

            if self.base_ring() in (_owned_real_algebraic_numbers(), RR):
                vector = lattice_engines._real_representation_witness(
                    self, self.base_ring().zero()
                )
            else:
                vector = lattice_engines._isotropic_vector_witness(self)
            if vector is None:
                raise ValueError("the lattice has no nonzero isotropic vector")
            return vector

        def represents(self, value) -> bool | Predicate:
            r"""Return whether some nonzero ``x`` in this lattice has ``b(x, x) = value``.

            A form represents ``a`` when ``b(x, x) = a`` for some ``x != 0``
            (Serre, *A Course in Arithmetic*, Ch. IV, 1.6): the hypersurface
            ``b(x, x) = a`` has a nonzero point in ``L``.  The elementwise
            ``represents`` of a vector is the statement ``b(v, v) = a`` about
            that one vector.  The lattice is nondegenerate of finite rank over
            ``QQ``, ``AA`` or ``ZZ``.

            - ``a = 0``: isotropy, :meth:`is_isotropic`.  Over ``ZZ`` a
              rational isotropic vector clears to an integral one.
            - Over ``QQ``, ``a != 0``: ``L`` represents ``a`` exactly when
              ``L perp <-a>`` represents 0 (Serre, Ch. IV, 1.6, Cor. 1 of
              Prop. 3'), which PARI decides (Hasse--Minkowski, Ch. IV, 3.2,
              Thm. 8).
            - Over ``ZZ``, definite: every solution lies in the bounded region
              of Cassels, *Rational Quadratic Forms*, Ch. 9, §1, (1.2)--(1.3),
              which :meth:`vectors_of_square` enumerates.
            - Over ``ZZ``, indefinite of rank 2: :meth:`representation_vector`
              finds every solution class.
            - Over ``ZZ``, indefinite of rank at least 3: every ``L tensor
              ZZ_p`` must represent ``a``, read from the genus's
              :meth:`~_Genus.local_representations`; ``L tensor RR`` does,
              being indefinite.  These local tests exclude impossible norms;
              surviving norms are decided by the finite integral-overlattice
              and primitive-embedding decision for ``<a> -> L``.  Local
              representability alone is not used as an integral witness.
            - Over ``AA`` or applicable represented ``RR``, ``a != 0``:
              a positive value is represented exactly when the positive index of inertia is nonzero, and likewise
              for a negative value and the negative index.

            EXAMPLES::

                sage: C = Lattices(ZZ)
                sage: C("E8").represents(-2) and not C("E8").represents(-1)
                True
                sage: C([[-1, 0, 0], [0, -1, 0], [0, 0, -1]]).represents(-7)
                False
                sage: (C("U") + C("U")).represents(0)
                True
                sage: C("U").represents(2) and not C("U").represents(1)
                True
                sage: C([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 2, 0], [0, 0, 0, 2]]).represents(1)
                False
                sage: assert C(0).represents(0) is False and C(0).represents(1) is False
            """
            from sage.rings.rational_field import QQ as SageQQ
            from sage_extensions.categories.rings.ring_foundation import _owned_real_algebraic_numbers
            from sage_extensions.rings.real import RR

            ring = self.base_ring()
            value = ring(value)
            assert self.module_rank().is_finite() and self.is_nondegenerate(), (
                f"representation of {value} is decided here for a nondegenerate lattice of finite rank, and {self!r} is not one"
            )
            rank = int(self.module_rank())
            match ring:
                case _ if rank == 0:
                    return False
                case _ if value == ring.zero():
                    return self.is_isotropic()
                case _ if ring in (_owned_real_algebraic_numbers(), RR):
                    signature = self.signature_pair()
                    sign = ring._sign_of_nonzero(value) if ring is RR else (1 if value > ring.zero() else -1)
                    index = signature.first() if sign > 0 else signature.second()
                    return index != cardinal(0)
                case _ if _engine_ring(ring) is SageQQ:
                    return (
                        lattice_engines._rational_representation_witness(self, value)
                        is not None
                    )
                case _ if _engine_ring(ring) is not SageZZ:
                    assert False, (
                        f"representation of {value} by {self!r} is decided here over ZZ, QQ, AA and RR, not over {ring}"
                    )
                case _ if self.is_definite():
                    return self.vectors_of_square(value).domain().cardinality() != 0
                case _ if rank == 2:
                    return _indefinite_binary_representation(self, value) is not None
                case _ if not _locally_represented(
                    self.genus().local_representations(), value
                ):
                    return False
                case _:
                    line = Lattices(ring)([[value]])
                    return negation(line.Emb(self).is_empty())

        def representation_vector(self, value) -> Lattices.ElementMethods:
            r"""Return a nonzero ``x`` in this lattice with ``b(x, x) = value``; raise ``ValueError`` if none exists.

            The routing is that of :meth:`represents`.

            - ``a = 0``: :meth:`isotropic_vector`, primitive over ``ZZ``.
            - Over ``QQ``: the zero of ``L perp <-a>`` that decides
              :meth:`represents`, rescaled.
            - Over ``AA`` or represented exact ``RR``: rescale a diagonal
              vector of the required sign using the positive square root of the norm ratio.
            - Over ``ZZ``, definite: a vector of :meth:`vectors_of_square`.
            - Over ``ZZ``, indefinite of rank 2 with ``L tensor QQ``
              anisotropic: PARI's ``qfbsolve`` representatives.  With ``L
              tensor QQ`` isotropic, a primitive isotropic ``e`` and an
              ``f`` with ``b(e, f) = d = div(e)`` form a basis of ``L``,
              because ``b(e, -)`` has kernel ``QQ e cap L = ZZ e``; so
              ``b(x e + y f, x e + y f) = y (2 d x + c y)`` with ``c = b(f, f)``,
              and every solution has ``y | a`` and ``2 d x = a / y - c y``.
            - Over ``ZZ``, indefinite of rank at least 3 with ``a != 0``:
              compose a finite integral overlattice inclusion of ``<a>``
              with a primitive embedding into this lattice. The finite
              discriminant bilinear form supplies the overlattices, OSCAR
              supplies the primitive decision, and the existing integral
              Isom objects supply target transport. This is a finite
              classification route, not an unbounded vector search.

            EXAMPLES::

                sage: C = Lattices(ZZ)
                sage: L = C("U") + C("U")
                sage: x = L.representation_vector(0)
                sage: x != L.zero() and x.q() == ZZ(0)
                True
                sage: C([[1, 0], [0, -2]]).representation_vector(-1).q() == ZZ(-1)
                True
                sage: C([[0, 2], [2, 2]]).representation_vector(6).q() == ZZ(6)
                True
                sage: V = Lattices(AA)([[1, 0], [0, -2]])
                sage: assert V.represents(AA(3)) is True and V.represents(AA(-3)) is True
                sage: assert V.q(V.representation_vector(AA(-3))) == AA(-3)
                sage: D = Lattices(AA)([[2]])
                sage: assert D.represents(AA(-1)) is False
                sage: assert D.q(D.representation_vector(AA(3))) == AA(3)
                sage: L = C("U") + C([[1]])
                sage: x = L.representation_vector(3)
                sage: assert x.parent() is L and x != L.zero() and L.q(x) == ZZ(3)
                sage: M = C([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]])
                sage: assert M.q(M.representation_vector(5)) == ZZ(5)
                sage: B = C([[-9, 1, 0], [1, 7, 0], [0, 0, 2]])
                sage: assert B.spinor_genus_count() > ZZ(1)
                sage: assert B.represents(ZZ(1)) is False
                sage: assert B.represents(ZZ(2)) is True
                sage: v = B.representation_vector(ZZ(2))
                sage: assert v.parent() is B and B.q(v) == ZZ(2)
                sage: B.representation_vector(ZZ(1))  # doctest: +ELLIPSIS
                Traceback (most recent call last):
                ...
                ValueError: ... does not represent 1
                sage: C(0).representation_vector(1)  # doctest: +ELLIPSIS
                Traceback (most recent call last):
                ...
                ValueError: ... does not represent 1
            """
            from sage.rings.rational_field import QQ as SageQQ
            from sage_extensions.categories.rings.ring_foundation import _owned_real_algebraic_numbers
            from sage_extensions.rings.real import RR

            ring = self.base_ring()
            value = ring(value)
            assert self.module_rank().is_finite() and self.is_nondegenerate(), (
                f"a representation of {value} is constructed here in a nondegenerate lattice of finite rank, and {self!r} is not one"
            )
            rank = int(self.module_rank())
            match ring:
                case _ if rank == 0:
                    found = None
                case _ if value == ring.zero():
                    return self.isotropic_vector()
                case _ if ring in (_owned_real_algebraic_numbers(), RR):
                    found = lattice_engines._real_representation_witness(
                        self, value
                    )
                case _ if _engine_ring(ring) is SageQQ:
                    found = lattice_engines._rational_representation_witness(
                        self, value
                    )
                case _ if _engine_ring(ring) is not SageZZ:
                    assert False, (
                        f"a representation of {value} in {self!r} is constructed here over ZZ, QQ, AA and RR, not over {ring}"
                    )
                case _ if self.is_definite():
                    found = next(iter(self.vectors_of_square(value)), None)
                case _ if rank == 2:
                    found = _indefinite_binary_representation(self, value)
                case _ if self.represents(value) is False:
                    found = None
                case _:
                    line = Lattices(ring)([[value]])
                    embedding = line.Emb(self).an_element()
                    found = embedding(line.module_generators()[0])
            if found is None:
                raise ValueError(f"{self!r} does not represent {value}")
            return found

        def spinor_norm(self, field_map=None, form_multiplier=None):
            r"""Return the spinor norm \(g\mapsto\mathrm{sn}_{K'}(g\otimes K')\) on \(O(L)\).

            Let \(K=\operatorname{Frac}(R)\), \(V=L\otimes_R K\) the quadratic
            space :meth:`vector_space`, and \(c\in K^\times\) the
            ``form_multiplier``.  Every \(g\in O(V)\) is a product
            \(s_{v_1}\cdots s_{v_m}\) of reflections in anisotropic vectors,
            and the class
            \[\mathrm{sn}_K(g)=\prod_{i=1}^{m}c\,(v_i,v_i)\,(K^\times)^2\in K^\times/(K^\times)^2\]
            does not depend on the factorization, so
            \(\mathrm{sn}_K\colon O(V)\to K^\times/(K^\times)^2\) is a group
            morphism (O'Meara, *Introduction to Quadratic Forms*, §55, where
            \(c=1\)).  Gritsenko--Hulek--Sankaran (*Abelianisation of
            orthogonal groups*, arXiv:0810.1614, §1, after Kneser) take
            \(c=-\tfrac12\), the default here: in signature \((2,n)\) a
            reflection in a vector of negative square then fixes each
            component of the period domain.  Changing \(c\) multiplies
            \(\mathrm{sn}_K(g)\) by \(c^m\), a square when \(m\) is even, so
            every choice agrees on \(SO(V)\) (O'Meara §55).

            A field morphism \(\varphi\colon K\to K'\) (``field_map``, by
            default the identity of \(K\)) carries a factorization over \(K\)
            to one over \(K'\), so
            \(\mathrm{sn}_{K'}(g\otimes K')=\varphi_*\,\mathrm{sn}_K(g)\) for
            \(g\in O(V)\), with \(\varphi_*\) the square-class functor
            ``Monoids().Commutative().square_class_group()``.  The morphism returned
            is \(g\mapsto\varphi_*\,\mathrm{sn}_K(g\otimes K)\) on \(O(L)\): it
            is \(\mathrm{sn}_K\) of \(O(V)\) itself when \(R=K\), and along the
            real place \(\mathbb Q\to\mathbb R\) it is the real spinor norm
            whose kernel is :meth:`O_plus`.

            Over \(\mathbb Q\) the private computation is the discriminant of
            the Wall form of the isometry, by GAP's ``WallForm``; represented
            absolute number fields diagonalize the Gram matrix and use OSCAR's
            reflection factorization ``spin`` through their selected
            primitive-element presentation.
            """
            ring = self.base_ring()
            field = ring.fraction_field()
            assert self.module_rank().is_finite() and self.is_nondegenerate(), (
                f"{self!r} has no spinor norm: the spinor norm is defined on the orthogonal group of a nondegenerate quadratic space of finite dimension"
            )
            from sage.rings.rational_field import QQ as SageQQ

            from sage_extensions.categories.rings.number_fields import (
                NumberFieldsWithChosenPrimitiveElement,
                OwnedNumberFields,
            )

            supported_number_field = field in OwnedNumberFields() and (
                _engine_ring(field) is SageQQ
                or (
                    field in NumberFieldsWithChosenPrimitiveElement()
                    and _engine_ring(field).is_absolute()
                )
            )
            assert supported_number_field, (
                f"the spinor norm of {self!r} is computed here over represented absolute number fields, but Frac(R) = {field}"
            )
            multiplier = _spinor_norm_multiplier(field, form_multiplier)
            extension = self.orthogonal_group_base_change(ring.fraction_field_map())
            square_classes = field.square_class_group()

            def spinor_norm_class(isometry):
                changed = extension(isometry)
                match field:
                    case _ if _engine_ring(field) is SageQQ:
                        representative = _rational_spinor_norm_representative(changed)
                    case _:
                        representative = _number_field_spinor_norm_representative(
                            changed
                        )
                odd_reflection_count = isometry.determinant() == -ring.one()
                return square_classes(
                    multiplier * representative
                    if odd_reflection_count
                    else representative
                )

            match field_map:
                case None:
                    return self.Aut().Mor(square_classes)(spinor_norm_class)
                case _:
                    assert field_map.domain() is field, (
                        f"the spinor norm of {self!r} is carried along a map out of Frac(R) = {field}, but {field_map} starts at {field_map.domain()}"
                    )
                    change_of_field = Monoids().Commutative().square_class_group()(field_map)
                    return self.Aut().Mor(change_of_field.codomain())(
                        lambda isometry: change_of_field(spinor_norm_class(isometry)),
                    )

        def spinor_kernel(self, field_map=None, form_multiplier=None):
            r"""Return \(O_{\mathrm{sn}_{K'}}(L)=O(L)\cap\ker\mathrm{sn}_{K'}\) for :meth:`spinor_norm`.

            With ``field_map`` omitted, \(K'=K=\operatorname{Frac}(R)\) and
            this is the \(R\)-spinor kernel: the elements of \(O(L)\) lying in
            the \(K\)-spinor kernel of :meth:`spinor_norm_sequence`.
            Gritsenko--Hulek--Sankaran (arXiv:0810.1614, §1) write
            \(O^+(L)=O(L)\cap\ker\mathrm{sn}_{\mathbb R}\), which is
            :meth:`O_plus`, and \(O'(L)=SO(L)\cap\ker\mathrm{sn}_{\mathbb Q}\),
            which is :meth:`spinorial_kernel`.
            """
            return _spinor_norm_kernel(
                self.spinor_norm(field_map, form_multiplier),
                "sn(g) = 1",
            )

        @cached_method
        def O_plus(self):
            r"""Return \(O^+(L)=O(L)\cap\ker\mathrm{sn}_{\mathbb R}\) (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, §1).

            \(\mathrm{sn}_{\mathbb R}\) is :meth:`spinor_norm` along the real
            place of \(\operatorname{Frac}(R)=\mathbb Q\), with the paper's
            multiplier \(-\tfrac12\).  The positive-cone subgroup in signature
            \((1,n)\) is :meth:`O_component`.
            """
            field = self.base_ring().fraction_field()
            assert field in PrimeFields() and field.characteristic() == 0, (
                f"O^+({self!r}) is the kernel of the real spinor norm at the real place of Frac(R); QQ has exactly "
                f"one, but Frac(R) = {field}: pass a real embedding of it to spinor_kernel"
            )
            from sage_extensions.rings.real import RR

            real_place = field.Mor(RR)(lambda rational: RR(rational))
            real_spinor_norm = self.spinor_norm(real_place)
            return _spinor_norm_kernel(
                real_spinor_norm.codomain().sign_isomorphism() * real_spinor_norm,
                "sn_RR(g) = 1",
                character_data={"spinor_kernel": True},
            )

        @cached_method
        def spinorial_kernel(self):
            r"""Return the spinorial kernel \(O'(L)=SO(L)\cap\ker\mathrm{sn}_{\mathbb Q}\).

            Gritsenko--Hulek--Sankaran, arXiv:0810.1614, §1.  On \(SO\) the
            spinor norm does not depend on its multiplier (O'Meara §55), so
            neither does \(O'(L)\).
            """
            return self.SO().intersection(self.spinor_kernel())

        @cached_method
        def spinor_norm_sequence(self, form_multiplier=None):
            r"""Return \(1\to K_{\mathrm{sn}_K}\to O(L_K)\xrightarrow{\mathrm{sn}_K}K^\times/(K^\times)^2\to C_{\mathrm{sn}_K}\to 1\).

            \(K=\operatorname{Frac}(R)\), \(L_K\) is :meth:`vector_space` and
            \(\mathrm{sn}_K\) is :meth:`spinor_norm` of \(L_K\) with the given
            multiplier.
            """
            return SpinorNormSequence(self, form_multiplier)

        @cached_method
        def component_character(self):
            r"""Return \(\chi_\Omega\colon O(L)\to C_2\), the character of the positive cone.

            In signature \((1,n)\) the cone \(\{v: b(v,v)>0\}\) has two
            components, and an isometry either preserves each of them or
            exchanges the two.  That assignment is a group morphism to the
            cyclic group of order two, and :meth:`positive_cone_subgroup` is
            its kernel.
            """
            _signature = self.signature_pair()
            positive, negative = _signature.first(), _signature.second()
            integers = positive.parent()
            if positive != integers.one() or negative < integers.one():
                raise ValueError(
                    f"{self!r} has no positive-cone component character: the cone b(v,v) > 0 has two components only in signature (1,n) with n >= 1, but this lattice has signature {(positive, negative)}"
                )

            target = OwnedGroups().C(2)
            exchange = target.group_generators()[0]
            return self.Aut().Mor(target)(
                lambda isometry: (
                    target.one() if isometry.preserves_positive_cone() else exchange
                ),
            )

        def positive_cone_subgroup(self):
            r"""Return the positive-cone-preserving subgroup in signature ``(1,n)``."""
            _signature = self.signature_pair()
            positive, negative = _signature.first(), _signature.second()
            integers = positive.parent()
            if positive != integers.one() or negative < integers.one():
                raise ValueError(
                    f"{self!r} has no positive-cone-preserving subgroup of O(L): the positive cone has two components only in signature (1,n) with n >= 1, but this lattice has signature {(positive, negative)}"
                )

            return self.Aut().predicate_subgroup(
                lambda automorphism: automorphism.preserves_positive_cone(),
                "g preserves the positive cone",
            )

        def O_component(self):
            r"""Return the subgroup preserving the selected positive-cone component."""
            return self.positive_cone_subgroup()

        @cached_method
        def decomposition(self):
            r"""Return the represented direct-sum decomposition, or ``None`` when this lattice was not built as one.

            A lattice built as an orthogonal sum is an object of
            ``OrthogonalSumLattices(R)``, whose datum is its family of summands.
            """
            match self in OrthogonalSumLattices(self.base_ring()):
                case True:
                    return DirectSumObjects(
                        Modules(self.base_ring())
                    ).verify_decomposition(self, self.biproduct_factors())
                case False:
                    return None

        def is_decomposable(self):
            r"""Whether this lattice has a nontrivial integral orthogonal sum.

            An exhibited sum or an orthogonal partition of the displayed basis
            proves decomposability.  Rank one and the rank-two determinant
            obstruction decide some negative cases.  Otherwise the property
            remains a proposition; a connected displayed Gram is not a proof.
            """
            rank = self.module_rank()
            if not rank.is_finite():
                return AtomicProposition("orthogonally decomposable", self)
            n = int(rank)
            if n <= 1:
                return False
            if self.decomposition() is not None and sum(
                int(factor.module_rank()) > 0 for factor in self.biproduct_factors()
            ) > 1:
                return True
            if self.base_ring() is _owned_integers() and self.form_content() > 1:
                return self.untwisted_form().is_decomposable()
            gram = self.gram_tensor()
            reached = {0}
            frontier = [0]
            while frontier:
                row = frontier.pop()
                for column in range(n):
                    if column not in reached and gram[row, column] != self.base_ring().zero():
                        reached.add(column)
                        frontier.append(column)
            if len(reached) < n:
                return True
            if n == 2 and self.base_ring() is _owned_integers():
                binary = self._binary_orthogonal_split()
                if binary is not None:
                    return True
                if self.is_positive_definite() is True or self.is_negative_definite() is True:
                    return False
            if self in RootLattices():
                root_type = str(self.root_system_type_name())
                if root_type[:1] in {"A", "D", "E"} and root_type[1:].isdigit():
                    # A root of square -2 in an orthogonal sum lies wholly in
                    # one factor. Connected finite ADE roots span their lattice.
                    return False
            if n == 2 and self.base_ring() is _owned_integers() and self.is_even() is True:
                if self.determinant() % 4 != 0:
                    return False
            return AtomicProposition("orthogonally decomposable", self)

        def _binary_orthogonal_split(self):
            r"""Return a unimodular orthogonal basis for a definite binary form, if one exists.

            If a rank-two form splits, a primitive summand generator has
            nonzero norm ``a`` dividing the determinant. The inverse Gram
            bounds its coordinates by the square roots of the opposite
            diagonal entries after choosing the definite sign.
            """
            if int(self.module_rank()) != 2 or self.base_ring() is not _owned_integers():
                return None
            if not (self.is_positive_definite() is True or self.is_negative_definite() is True):
                return None
            from math import isqrt

            gram = self.gram_tensor()
            sign = 1 if self.is_positive_definite() is True else -1
            bound_x = isqrt(int(sign * gram[1, 1]))
            bound_y = isqrt(int(sign * gram[0, 0]))
            determinant = self.determinant()
            for x in range(-bound_x, bound_x + 1):
                for y in range(-bound_y, bound_y + 1):
                    if gcd(x, y) != 1:
                        continue
                    first = gram[0, 0] * x + gram[0, 1] * y
                    second = gram[1, 0] * x + gram[1, 1] * y
                    norm = x * first + y * second
                    if norm == 0 or determinant % norm or gcd(first, second) != abs(norm):
                        continue
                    complement = (second // norm, -first // norm)
                    return (norm, determinant // norm, (x, y), complement)
            return None

        def is_indecomposable(self):
            r"""Whether no nontrivial integral orthogonal sum exists."""
            if self.module_rank().is_finite() and int(self.module_rank()) == 0:
                return False
            answer = self.is_decomposable()
            return not answer if isinstance(answer, bool) else negation(answer)

        def form_content(self):
            r"""Positive generator of the Gram-entry ideal of a finite integral lattice."""
            if self.base_ring() is not _owned_integers() or not self.module_rank().is_finite():
                raise NotImplementedError("form content requires a finite integral lattice")
            rank = int(self.module_rank())
            gram = self.gram_tensor()
            content = self.base_ring().zero()
            for row in range(rank):
                for column in range(rank):
                    content = gcd(content, gram[row, column])
            return abs(content)

        def is_twisted(self):
            r"""Whether the integral form is a nonunit scalar multiple of another.

            Integral basis change preserves the ideal generated by all pairing
            values. For finite free lattices its Gram-entry ideal decides the
            property. Unit scaling, including ``-1``, preserves the class.
            """
            if self.base_ring() is not _owned_integers() or not self.module_rank().is_finite():
                return AtomicProposition("twisted by a nonunit", self)
            return self.form_content() != self.base_ring().one()

        def is_untwisted(self):
            r"""Whether the integral form has no nonunit scalar factor."""
            answer = self.is_twisted()
            return not answer if isinstance(answer, bool) else negation(answer)

        def untwisted_form(self):
            r"""Divide the selected finite integral Gram form by its content."""
            content = self.form_content()
            if content == 0:
                raise ValueError("the zero form has no canonical nonzero content to remove")
            if content == 1:
                return self
            rank = int(self.module_rank())
            gram = self.gram_tensor()
            return Lattices(self.base_ring())(
                [[gram[row, column] // content for column in range(rank)]
                 for row in range(rank)]
            )

        def indecomposable_name(self):
            return _indecomposable_name(self)

        def indecomposable_summands(self):
            r"""Return the family of indecomposable summands, in order.

            A summand may itself be an orthogonal sum -- as every summand of
            ``L + M + N`` is, ``+`` being binary -- so this descends through
            the represented decompositions until every summand is
            indecomposable.
            """

            if self.decomposition() is None:
                split = self._binary_orthogonal_split() if self.module_rank().is_finite() and int(self.module_rank()) == 2 else None
                if split is not None:
                    first, second, _, _ = split
                    category = Lattices(self.base_ring())
                    return finite_family((category([[first]]), category([[second]])), name="Indecomposable summands")
                return finite_family((self,), name="Indecomposable summands")
            summands = []
            for factor in self.biproduct_factors():
                summands.extend(factor.indecomposable_summands())
            return finite_family(summands, name="Indecomposable summands")

        def decomposition_names(self):
            r"""Return the registered name of each indecomposable summand."""
            return self.indecomposable_summands().map(
                lambda summand: summand.indecomposable_name(),
                name="Decomposition names",
            )

        def is_isometric(self, other):
            r"""Return whether ``self`` and ``other`` are isometric when decidable.

            Outside the implemented exact regimes the live isometry Mor answers
            the proposition that it is empty, and this answers its negation,
            instead of treating matching coarse invariants as a proof.
            """
            return negation(self.Isom(other).is_empty())

        def isometry_to(self, other):
            r"""Return an explicit isometry ``self -> other`` when one is constructible.

            A proved empty isometry Mor returns ``None``.  An undecided
            Mor, or a theorem-backed nonempty Mor whose current exact
            machinery does not exhibit a witness, retains that distinction by
            raising from :meth:`Isom(...).an_element` rather than turning it
            into a false negative.
            """
            mor = self.Isom(other)
            empty = mor.is_empty()
            match empty:
                case True:
                    return None
            assert empty is False, (
                f"cannot decide whether {self!r} and {other!r} are isometric: no available exact classification algorithm decides this pair"
            )
            return mor.an_element()

        def is_isometric_to(self, other):
            r"""Return the verified boolean isometry decision.

            Unlike :meth:`is_isometric`, this semantic spelling is strictly
            boolean: an unresolved exact-classification case raises instead of
            returning the undecided proposition.
            """
            decision = self.is_isometric(other)
            assert decision is True or decision is False, (
                f"cannot decide whether {self!r} and {other!r} are isometric: no available exact classification algorithm decides this pair"
            )
            return decision

        def with_isometry(self, isometry):
            r"""Return the infinite-cyclic action on this lattice generated by ``isometry``."""
            from sage_extensions.categories.lattice_centralizers import (
                _equivariant_lattice,
            )

            return _equivariant_lattice(self, isometry)

        def similarity_mor(self, other, scale):
            r"""Return similarities of scale ``scale`` as ``Isom(L(scale),other)``."""
            return self.twist(scale).Isom(other)

        def is_similar(self, other, scale):
            r"""Return whether a similarity of the stated scale exists."""
            return self.twist(scale).is_isometric(other)

        def similarity(self, scale, images=None, codomain=None):
            r"""Return an explicit similarity as an isometry from ``L(scale)``.

            A scale-``a`` similarity ``sigma:L->M`` satisfies
            ``b_M(sigma x,sigma y)=a*b_L(x,y)``.  Hence its owned
            form-preserving arrow is exactly an isometry ``L(a)->M``.  When
            ``images`` is omitted, return the distinguished isometry supplied
            by the represented exact isometry Mor.
            """
            target = self if codomain is None else codomain
            mor = self.similarity_mor(target, scale)
            if images is None:
                return mor.an_element()
            return mor(images)

        def identity_morphism(self):
            r"""Return ``id_L`` in the lattice endomorphism Mor.

            The morphism is a callable on generators, not an enumerated
            image of every \(e_i\).

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: Iinf = Lattices(ZZ)(ZZ^NN)
                sage: f = Iinf.identity_morphism()
                sage: f(Iinf.basis_vector(7))
                e_7
            """
            return self.Aut().identity()

        def gram_tensor(self):
            r"""Return the Gram tensor of the form: type $(0,2)$, not a matrix.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: I2 = Lattices(ZZ)(ZZ^2)
                sage: I2.gram_tensor()
                I_2 ∈ ((ZZ^2)*)^{⊗2}
                sage: latex(I2.gram_tensor())
                I_{2}
                sage: latex(Lattices(ZZ)(ZZ^NN).gram_tensor())
                I_{\infty}
                sage: A2 = Lattices(ZZ)("A2")
                sage: latex(A2.gram_tensor())
                \left(\begin{array}{rr}
                -2 & 1 \\
                1 & -2
                \end{array}\right)
                sage: I2.gram_tensor().parent()
                ((ZZ^2)*)^{⊗2}
                sage: Lattices(ZZ)(ZZ^NN).gram_tensor()
                I_∞ ∈ (ZZ^NN ⊗ ZZ^NN)*
            """
            return self._preamble_gram_tensor

        def _evaluate_gram(self, left, right):
            r"""Contract the retained finite Gram with two lattice vectors."""
            labels = tuple(self.module_generating_set())
            left_coordinates = left.to_vector()
            right_coordinates = right.to_vector()
            gram = self.gram_tensor()
            ring = self.base_ring()
            return sum(
                (
                    left_coordinates(left_label)
                    * gram[left_position, right_position]
                    * right_coordinates(right_label)
                    for left_position, left_label in enumerate(labels)
                    for right_position, right_label in enumerate(labels)
                ),
                ring.zero(),
            )

        def b(self, left, right):
            r"""Evaluate the finite lattice pairing from its retained Gram."""
            if left not in self or right not in self:
                raise TypeError(
                    f"the pairing on {self} takes two of its vectors, but {left} or {right} is not in {self}"
                )
            if not self.module_rank().is_finite():
                return super().b(left, right)
            return self._evaluate_gram(left, right)

        def norm(self, element):
            r"""Return the finite Gram contraction ``b(element, element)``."""
            if element not in self:
                raise TypeError(
                    f"the norm on {self} is defined on its vectors, but {element} is not in {self}"
                )
            if not self.module_rank().is_finite():
                return super().norm(element)
            return self._evaluate_gram(element, element)

        def gram_matrix(self, basis=None):
            r"""Return the finite coordinate matrix of the selected form.

            With no ``basis`` this is the matrix of
            :meth:`algebraic_correlation_morphism` in the selected finite
            framing and its dual.  An infinite algebraic dual has no
            finite-support dual framing, so an infinite lattice has no
            default Gram *matrix*; its Gram tensor remains the form.  Passing
            finitely many vectors explicitly returns their finite pairing
            matrix.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: Lattices(ZZ)("U").gram_matrix().determinant()
                -1
                sage: Lattices(ZZ)("A2").gram_matrix().determinant()
                3
            """
            if basis is not None:
                selected = tuple(basis)
                for vector in selected:
                    if vector.parent() is not self:
                        raise ValueError(
                            f"cannot form the Gram matrix of {self!r} on {vector!r}: the vector lies in {vector.parent()!r}, not in this lattice"
                        )
                size = len(selected)
                return (
                    self.base_ring()
                    .matrix_space(size, size)
                    .from_rows(
                        tuple(
                            tuple(self.b(left, right) for right in selected)
                            for left in selected
                        )
                    )
                )
            assert self.module_rank().is_finite(), (
                f"{self!r} has rank {self.module_rank()}, so it has no Gram matrix on a basis; a Gram matrix needs finite rank. Pass a finite family of vectors to take their Gram matrix"
            )
            gram = self.gram_tensor()
            size = int(self.module_rank())
            return self.base_ring().matrix_space(size, size).from_rows(
                tuple(
                    tuple(gram[row, column] for column in range(size))
                    for row in range(size)
                )
            )

        def basis_vector(self, position):
            r"""Return the selected lattice basis vector at integer ``position``.

            Positional basis access is a lattice convenience distinct from the
            generic framing evaluation ``module_generator(label)``: it reads the
            label at ``position`` in the framing's enumeration.
            """
            labels = self.module_generating_set()
            return self.module_generator(labels[int(position)])

        def discriminant(self):
            r"""Return $d_\pm(b)=(-1)^{n(n-1)/2}\det G$, the signed determinant.

            An invariant of $L$, not the framing-dependent $\det G$.
            Transcribed from the archived integral-lattice discriminant
            (Lam, *Introduction to Quadratic Forms over Fields*, I.2).

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: Lattices(ZZ)("U").discriminant()
                1
                sage: Lattices(ZZ)(ZZ^2).discriminant()
                -1
            """

            return _discriminant_of_gram(self.gram_tensor())

        @cached_method
        def determinant(self):
            r"""Return the determinant of a finite-rank lattice form."""
            assert self.module_rank().is_finite(), (
                f"{self!r} has no determinant: it has rank {self.module_rank()}, and a determinant needs finite rank"
            )

            rank = int(self.module_rank())
            gram = self.gram_tensor()
            value_module = self.value_module()
            if hasattr(value_module, "module_over_extension"):
                scalar_ring = value_module.extension_ring()
                try:
                    scalar_identification = value_module.regular_module_identification()
                except (AssertionError, TypeError, ValueError) as error:
                    raise TypeError(
                        f"the determinant of {self} requires a selected rank-one scalar-value identification; "
                        f"the value module {value_module} is not the restriction of the regular module of "
                        f"its extension ring"
                    ) from error
                if getattr(gram, "base_ring", lambda: None)() is scalar_ring:
                    scalar_entry = lambda row, column: gram[row, column]
                else:
                    scalar_entry = lambda row, column: scalar_identification(gram[row, column])
                matrix = scalar_ring.matrix_space(rank).from_rows(
                    (
                        scalar_entry(row, column)
                        for column in range(rank)
                    )
                    for row in range(rank)
                )
                return matrix.determinant()
            matrix = (
                value_module
                .matrix_space(rank)
                .from_rows(
                    (gram[row, column] for column in range(rank)) for row in range(rank)
                )
            )
            return matrix.determinant()

        def integral_representative_coefficient_bound(self) -> RingElement:
            r"""Bound the Gram coefficients of some integrally isometric representative.

            For a finite nondegenerate ZZ-lattice return an integer ``B``
            such that a basis exists with every absolute Gram coefficient
            at most ``B``. This does not bound the basis-change matrix or
            an embedding matrix, and does not construct the representative.
            No signature decision or unspecified constant is required.

            Write ``n=rank(L)`` and ``D=abs(det(L))``. A definite form has
            the bound ``2^(n*(n-1)/2)*D`` by the LLL basis inequalities.
            For indefinite forms of rank at least three, Li--Margulis,
            Appendix and Lemmas 13--14,
            supply a compact subset meeting the associated closed orbit.
            An elementary basis estimate makes its representative bound
            explicit. The full derivation, including indefinite binary
            forms and the distinction from embedding bounds, is in
            ``docs/theory/hyperbolic-index.md``, "An explicit coefficient
            bound for integral form representatives".

            EXAMPLES::

                sage: assert Lattices(ZZ)(0).integral_representative_coefficient_bound() == ZZ(0)
                sage: assert Lattices(ZZ)([[-7]]).integral_representative_coefficient_bound() == ZZ(7)
                sage: N = ZZ(10)^20
                sage: L = Lattices(ZZ)([[1, N], [N, N*N + 1]])
                sage: bound = L.integral_representative_coefficient_bound()
                sage: e, f = L.module_generators()
                sage: assert L.q(f) > bound
                sage: basis = (e, f - N*e)
                sage: assert all(abs(L.b(v, w)) <= bound for v in basis for w in basis)
                sage: U = Lattices(ZZ)([[0, 1], [1, 2*N]])
                sage: e, f = U.module_generators()
                sage: bound = U.integral_representative_coefficient_bound()
                sage: assert U.q(f) > bound
                sage: basis = (e, f - N*e)
                sage: assert all(abs(U.b(v, w)) <= bound for v in basis for w in basis)
            """
            return self.lattice_category().integral_representative_coefficient_bound(
                self.module_rank(), self.determinant()
            )

        def integral_completion_coefficient_bound(
            self, target_rank: Cardinal | int, target_determinant: RingElement | int
        ) -> RingElement:
            r"""Bound Gram coefficients of a completion of any integral embedding.

            Let this lattice have nonsingular Gram matrix ``A`` of rank
            ``m``, and let ``B`` be any nonsingular integral Gram matrix
            of the supplied rank ``n > m`` and determinant. For every
            integral ``tau`` with ``tau.transpose()*B*tau == A``, there
            is an integral completion ``gamma = (tau | tau1)`` whose
            determinant has absolute value the gcd of the maximal minors
            of ``tau``, and whose transformed Gram coefficients are
            bounded by the returned integer.

            The original columns ``tau`` are fixed. The completion is
            unimodular precisely when the embedding is primitive. This
            bounds neither ``gamma`` nor ``tau`` and constructs neither.
            It does not assert that an embedding exists. Only target
            invariants are needed, so a target or embedding need not
            already be constructed.

            This evaluates a constant in Li--Margulis, Lemma 20, using
            ``integral_representative_coefficient_bound``. See the full
            proof in ``docs/theory/hyperbolic-index.md``, "An explicit
            coefficient bound for integral completions".

            EXAMPLES::

                sage: T = Lattices(ZZ)([[4]])
                sage: assert T.integral_completion_coefficient_bound(2, 1) == ZZ(20)
                sage: # tau=(2,0)^t in the identity form has content two.
                sage: # gamma=diag(2,1) completes it with Gram diag(4,1).
                sage: L = Lattices(ZZ)([[1, 0], [0, 1]])
                sage: e, f = L.module_generators()
                sage: assert L.q(2*e) == ZZ(4) and L.b(2*e, f) == ZZ(0)
                sage: bound = T.integral_completion_coefficient_bound(2, L.determinant())
                sage: assert all(abs(L.b(v, w)) <= bound for v in (2*e, f) for w in (2*e, f))
                sage: Z = Lattices(ZZ)(0)
                sage: assert Z.integral_completion_coefficient_bound(2, -1) == ZZ(2)
            """
            integers = _owned_integers()
            assert self.base_ring() is integers, (
                "integral completion coefficient bounds require base ring ZZ"
            )
            source_rank = self.module_rank()
            assert source_rank.is_finite(), (
                "an integral completion coefficient bound requires finite source rank"
            )
            dimension = cardinal(target_rank)
            assert dimension.is_finite(), (
                "an integral completion coefficient bound requires finite target rank"
            )
            m, n = int(source_rank), int(dimension)
            assert n > m, "an integral completion requires strictly larger target rank"
            determinant = abs(integers(target_determinant))
            assert determinant > integers.zero(), (
                "an integral completion coefficient bound requires nonzero target determinant"
            )
            source_determinant = abs(self.determinant())
            assert source_determinant > integers.zero(), (
                "an integral completion coefficient bound requires a nondegenerate source"
            )
            category = self.lattice_category()
            if m == 0:
                return category.integral_representative_coefficient_bound(n, determinant)
            gram = self.gram_tensor()
            source_size = max(abs(gram[i, j]) for i in range(m) for j in range(m))
            k = n - m
            coefficient = category.integral_representative_coefficient_bound(k, integers.one())
            return (
                coefficient * source_determinant**k * determinant
                + integers(m + 1)**2 * source_size
            )

        def integral_embedding_coefficient_bound(self, target: Lattices.ParentMethods) -> RingElement:
            r"""Bound representatives of every target-isometry orbit of embeddings.

            Both endpoints are nondegenerate integral lattices of finite
            rank. For a definite or rationally split binary target this
            bounds every embedding. For an indefinite target of rank at
            least three it meets every orbit under the target orthogonal
            group, including nonprimitive images, in the original selected
            framings. It need not contain every embedding. Decidable
            predicates invariant under target isometries therefore admit
            complete finite search within this bound; arbitrary further
            predicates need their own justification. This scalar
            computation does not decide existence.
            For a nonsplit indefinite binary target, the existing finite
            norm-orbit representatives bound a first image; its pairing
            and the source determinant then bound the second image.
            This also meets every target-isometry orbit, with no assertion
            about predicates that are not invariant under those isometries.

            Combine the completion Gram bound, a Hermite basis of its
            finite-index overlattice, and the explicit integral isometry
            bound. See the full proof in docs/theory/hyperbolic-index.md.

            EXAMPLES::

                sage: U = Lattices(ZZ)("U")
                sage: T = U.twist(ZZ(4))
                sage: L = U.twist(ZZ(2)) + Lattices(ZZ)([[2]])
                sage: bound = T.integral_embedding_coefficient_bound(L)
                sage: e, f, a = L.module_generators()
                sage: j = T.Emb(L)((2*e, f))
                sage: assert L.gram_tensor().pullback(j) == T.gram_tensor()
                sage: assert bound >= ZZ(2)
                sage: N = ZZ(10)**20
                sage: D = Lattices(ZZ)([[1, N], [N, N*N + 1]])
                sage: assert Lattices(ZZ)([[1]]).integral_embedding_coefficient_bound(D) == N
                sage: assert Lattices(ZZ)(0).integral_embedding_coefficient_bound(L) == ZZ(0)
                sage: assert T.integral_embedding_coefficient_bound(U) == ZZ(4)
                sage: S = Lattices(ZZ)([[1, 2], [2, 0]])
                sage: assert Lattices(ZZ)([[1]]).integral_embedding_coefficient_bound(S) == ZZ(4)
                sage: S = Lattices(ZZ)([[0, 2], [2, 1]])
                sage: assert Lattices(ZZ)([[1]]).integral_embedding_coefficient_bound(S) == ZZ(4)
                sage: N = ZZ(100)
                sage: S = Lattices(ZZ)([[N*N, N], [N, 0]])
                sage: assert Lattices(ZZ)([[N*N]]).integral_embedding_coefficient_bound(S) == ZZ(2)*N**4
                sage: P = Lattices(ZZ)([[1, 0], [0, -2]])
                sage: assert Lattices(ZZ)([[1]]).integral_embedding_coefficient_bound(P) >= ZZ(1)
                sage: assert Lattices(ZZ)([[3]]).integral_embedding_coefficient_bound(P) == ZZ(0)
                sage: assert Lattices(ZZ)([[4]]).integral_embedding_coefficient_bound(P) >= ZZ(2)
                sage: assert P.integral_embedding_coefficient_bound(P) >= ZZ(1)
                sage: assert U.integral_embedding_coefficient_bound(P) == ZZ(0)
                sage: assert Lattices(ZZ)([[-2]]).integral_embedding_coefficient_bound(P) >= ZZ(1)
            """
            from math import factorial

            integers = _owned_integers()
            assert self.base_ring() is integers and target.base_ring() is integers, (
                "integral embedding bounds require ZZ endpoints"
            )
            assert self.module_rank().is_finite() and target.module_rank().is_finite(), (
                "integral embedding bounds require finite ranks"
            )
            assert self.is_nondegenerate() and target.is_nondegenerate(), (
                "integral embedding bounds require nondegenerate endpoints"
            )
            m, n = int(self.module_rank()), int(target.module_rank())
            if m == 0 or m > n:
                return integers.zero()
            source_gram = self.gram_tensor()
            if target.is_definite():
                return max(target.square_coordinate_bound(source_gram[i, i]) for i in range(m))
            if n == 2:
                gram = target.gram_tensor()
                a, b, c = gram[0, 0], gram[0, 1], gram[1, 1]
                discriminant = b*b - a*c
                if discriminant.is_square():
                    height = max(abs(source_gram[i, j]) for i in range(m) for j in range(m))
                    if a == 0 and c == 0:
                        return height
                    if a == 0:
                        a = c
                    return integers(2) * height * max(abs(a), abs(b), discriminant.sqrt())
                square = source_gram[0, 0]
                if square == 0:
                    return integers.zero()
                orbits = target.binary_fixed_norm_representatives(square)
                section = orbits.section()
                labels = tuple(target.module_generating_set())
                vectors = (section(orbit) for orbit in orbits)
                first_bound = max(
                    (abs(vector.to_vector()(label)) for vector in vectors for label in labels),
                    default=integers.zero(),
                )
                if m == 1:
                    return first_bound
                height = max(abs(a), abs(b), abs(c))
                return (abs(source_gram[0, 1]) + integers(2)*height*abs(self.determinant())) * first_bound
            completion_height = (
                max(abs(source_gram[i, j]) for i in range(m) for j in range(m))
                if m == n else self.integral_completion_coefficient_bound(n, target.determinant())
            )
            target_gram = target.gram_tensor()
            target_height = max(abs(target_gram[i, j]) for i in range(n) for j in range(n))
            isometry_bound = self.lattice_category().integral_isometry_coefficient_bound(
                n, target_height, integers(n*n) * completion_height,
            )
            return integers(n * factorial(n - 1)) * abs(self.determinant()) * isometry_bound

        def is_even(self) -> bool | Predicate:
            r"""Return whether ``b(x,x)`` lies in ``2R`` for every lattice vector.

            The represented Gram rule may decide this globally.  If it does
            not, the answer is the proposition that the lattice is even.
            """
            return _gram_is_even(self.gram_tensor(), self.base_ring())

        def is_unimodular(self) -> bool | Predicate:
            r"""Decide whether the selected Gram pairing induces ``L ≅ L^∨``.

            The finite-rank calculation uses the determinant; a represented
            infinite-rank pairing rule may decide the same question without
            constructing the full algebraic dual or a correlation cokernel.
            """
            from sage_extensions.categories._lattice import (
                _gram_is_unimodular,
            )

            return _gram_is_unimodular(self.gram_tensor(), self.base_ring())

        @cached_method
        def _integral_gram_inverse(self):
            r"""Return the exact rational inverse of a finite integral Gram matrix."""
            if _engine_ring(self.base_ring()) is not SageZZ:
                raise TypeError("the integral Gram inverse is defined here only over ZZ")
            return _engine_component_matrix(self.gram_tensor()).change_ring(SageZZ).inverse()

        def delta(self):
            r"""Return Nikulin's ``delta`` for an even 2-elementary lattice.

            This is zero exactly when the discriminant quadratic form is
            integer-valued, and one otherwise.  It suffices to test Smith
            generators: on a 2-elementary discriminant group every bilinear
            value lies in ``(1/2)ZZ/ZZ``, so the cross term ``2b(x,y)`` in
            ``q(x+y)`` is integral.
            """
            if _engine_ring(self.base_ring()) is not SageZZ:
                raise TypeError(
                    f"{self!r} has no Nikulin invariant delta: delta is defined for lattices over ZZ, and this lattice is over {self.base_ring()}"
                )
            if not self.is_even() or not self.is_p_elementary(self.base_ring()(2)):
                raise ValueError(
                    f"{self!r} has no Nikulin invariant delta: delta is defined for an even 2-elementary lattice, and {self!r} is not both even and 2-elementary"
                )
            ring = self.base_ring()
            if self.is_unimodular() is True:
                return ring.zero()
            # In the dual basis the discriminant quadratic form is
            # q(z) = z^T G^(-1) z mod 2Z. Since 2-elementarity gives
            # 2*G^(-1) integral, every cross term is integral; q is
            # integer-valued exactly when each diagonal entry of G^(-1)
            # is integral. This is the same Smith-generator criterion
            # without constructing the discriminant quadratic module.
            inverse = self._integral_gram_inverse()
            return ring(int(any(inverse[i, i] not in SageZZ for i in range(inverse.nrows()))))

        def level(self):
            r"""Return the level of a finite nondegenerate integral lattice.

            This is the least ``N > 0`` annihilating the discriminant form.
            For an even lattice the relevant form is
            ``q:A_L -> QQ/2ZZ``; for an odd lattice only the bilinear pairing
            ``b:A_L^2 -> QQ/ZZ`` is canonically defined.  In particular the
            even level need not equal the exponent of ``A_L``: ``<2>`` has
            discriminant group ``ZZ/2`` but level ``4``.
            """
            assert _engine_ring(self.base_ring()) is SageZZ, (
                f"cannot compute the level of {self!r}: the level is implemented only for lattices over ZZ, and this lattice is over {self.base_ring()}"
            )
            if not self.module_rank().is_finite() or not self.is_nondegenerate():
                raise ValueError(
                    f"{self!r} has no level: the level is defined for a nondegenerate lattice of finite rank, and this lattice has rank {self.module_rank()} or is degenerate"
                )

            gram = _engine_component_matrix(self.gram_tensor()).change_ring(SageZZ)
            if self.is_even():
                # Sage's quadratic form uses G as the matrix of 2Q and
                # computes precisely the least N for which N*G^-1 is
                # integral with even diagonal (QuadraticForm.level).
                from sage.quadratic_forms.quadratic_form import QuadraticForm

                level = QuadraticForm(SageZZ, gram).level()
            else:
                # The odd-lattice discriminant pairing has no quadratic
                # refinement: its exponent is the common denominator of G^-1.
                level = gram.inverse().denominator()
            return _owned_integers()(int(level))

        def bad_reduction_primes(self):
            r"""Return the primes of bad reduction of the quadric ``Q(x) = n``: the primes dividing ``2 det(L)``.

            For an odd prime ``p``, ``Q`` modulo ``p`` is nondegenerate exactly
            when ``p`` does not divide ``det(L)``; modulo 2, ``Q`` is the square
            of a linear form, so 2 is always a prime of bad reduction
            (dzackgarza/lattice-database, ``theory/zeta.md``, *Primes of bad reduction*).
            """
            ring = self.base_ring()
            assert _engine_ring(ring) is SageZZ, (
                f"the bad-reduction prime set here is defined for integral lattices over ZZ, but {self} is over {ring}"
            )
            determinant = self.determinant()
            assert determinant != ring.zero(), (
                f"the bad-reduction prime set of {self} is not finite because its form is degenerate"
            )
            return finite_ordered_set(
                tuple((ring(2) * abs(determinant)).prime_divisors())
            )

        def discriminant_character_discriminant(self):
            r"""Return the discriminant ``d`` of the field ``Q(sqrt(D))``, ``D = (-1)^m det(L)`` in rank ``2m``.

            It is 1 when ``D`` is a square.  For a prime ``p`` not dividing
            ``2 det(L)``, the character ``chi_D(p)`` is the Kronecker symbol
            ``(d/p)``, which is the Legendre symbol ``(D/p)``
            (dzackgarza/lattice-database, ``theory/zeta.md``, *The character of the
            discriminant*).
            """
            from sage.arith.misc import fundamental_discriminant

            ring = self.base_ring()
            assert _engine_ring(ring) is SageZZ, (
                f"the discriminant quadratic character here is defined for integral lattices over ZZ, but {self} is over {ring}"
            )
            rank = self.module_rank()
            assert rank.is_finite() and int(rank) % 2 == 0, (
                f"the discriminant quadratic character of {self} is stated in even rank, but {self} has rank {rank}"
            )
            determinant = self.determinant()
            assert determinant != ring.zero(), (
                f"the discriminant quadratic character of {self} requires a nonzero determinant"
            )
            signed = ((-ring.one()) ** (int(rank) // 2)) * determinant
            return _owned_engine_element(
                ring,
                fundamental_discriminant(_engine_element(ring, signed)),
            )

        def quadratic_hypersurface_zeta_factorization(self, *, cone):
            r"""Return the partial zeta factorization of the affine quadric level."""
            from sage_extensions.categories.lattice_zeta_invariants import (
                quadratic_hypersurface_zeta_factorization,
            )

            return quadratic_hypersurface_zeta_factorization(self, cone=cone)

        def is_voronoi_perfect(self) -> bool:
            r"""Return whether the rank-one tensors of the minimal shell span ``Sym^2(L_Q)``."""
            assert self.is_definite(), (
                f"Voronoi perfection is decided here for definite lattices, but {self} is not definite"
            )
            rank = int(self.module_rank())
            dimension = rank * (rank + 1) // 2
            rationals = self.base_ring().fraction_field()
            ambient = rationals.free_module(dimension)
            labels = tuple(self.module_generating_set())
            tensors = []
            for vector in self.shortest_vectors():
                coordinates = vector.to_vector()
                tensors.append(
                    ambient(
                        tuple(
                            rationals(coordinates(labels[left]))
                            * rationals(coordinates(labels[right]))
                            for left in range(rank)
                            for right in range(left, rank)
                        )
                    )
                )
            return int(ambient.subobject_on(tuple(tensors)).module_rank()) == dimension

        @cached_method
        def genus(self):
            r"""Return the genus of this lattice, the finite set of isometry classes locally isometric to it.

            Even and odd lattices alike have a genus [PS24, Def. 1.9.1];
            ``lean-categories`` states the map from isometry classes to genera
            as ``isometryClassToGenus``.  Constructing it stores this lattice
            and computes nothing.
            """
            assert _engine_ring(self.base_ring()) is SageZZ, (
                f"cannot compute the genus of {self!r}: the genus is implemented only for lattices over ZZ, and this lattice is over {self.base_ring()}"
            )
            if not self.module_rank().is_finite() or not self.is_nondegenerate():
                raise ValueError(
                    f"cannot compute the genus of {self!r}: the genus is implemented for a nondegenerate lattice of finite rank, and this lattice has rank {self.module_rank()} or is degenerate"
                )
            return _Genus(self)

        def conway_sloane_genus_symbol(self):
            r"""Return the canonical Conway--Sloane genus-symbol string of an integral lattice."""
            from sage.quadratic_forms.genera.genus import Genus as SageGenus

            assert _engine_ring(self.base_ring()) is SageZZ, (
                f"the integral genus symbol here is implemented for ZZ-lattices, but {self} is over {self.base_ring()}"
            )
            assert self.module_rank().is_finite() and self.is_nondegenerate(), (
                f"the integral genus symbol of {self} requires finite rank and a nondegenerate form"
            )
            genus = SageGenus(
                _engine_component_matrix(self.gram_tensor()).change_ring(SageZZ)
            )
            positive, negative = genus.signature_pair()
            head = f"{'II' if genus.is_even() else 'I'}_{{{positive},{negative}}}"
            match abs(genus.determinant()) == 1:
                case True:
                    return head
                case False:
                    local = tuple(
                        f"{symbol.prime()}: {repr(symbol).split(':', 1)[1].strip()}"
                        for symbol in genus.local_symbols()
                    )
                    return f"{head} ({'; '.join(local)})"

        def genus_class_number(self):
            r"""Return the class number of this lattice, the number of isometry classes in its genus [PS24, Def. 1.10.5]."""
            return self.genus().class_number()

        def spinor_genus_count(self):
            r"""Return the number of improper spinor genera in the integral genus."""
            ring = self.base_ring()
            assert _engine_ring(ring) is SageZZ, (
                f"the spinor-genus count here is implemented for ZZ-lattices, but {self} is over {ring}"
            )
            return ring(self.genus().spinor_genus_count())

        def spinor_genus_class_numbers(self):
            r"""Return class numbers of the improper spinor genera, with that of ``self`` first."""
            ring = self.base_ring()
            assert _engine_ring(ring) is SageZZ, (
                f"spinor genera here are implemented for ZZ-lattices, but {self} is over {ring}"
            )
            assert (
                self.module_rank().is_finite()
                and int(self.module_rank()) >= 3
                and self.is_nondegenerate()
            ), (
                f"spinor genera of {self} require a nondegenerate lattice of finite rank at least three"
            )
            gram = _engine_component_matrix(self.gram_tensor()).change_ring(SageZZ)
            gram.set_immutable()
            classes = _genus_classes(gram)
            numbers = (
                ring(len(classes[0])),
                *(
                    ring(value)
                    for value in sorted(
                        (len(spinor_genus) for spinor_genus in classes[1:]),
                        reverse=True,
                    )
                ),
            )
            return finite_family(numbers, name=f"Spinor-genus class numbers of {self}")

        def integral_hyperbolic_index(self):
            r"""Return the actual integral ``U``-summand index of this lattice.

            The earlier genus comparison decided whether a genus contains
            ``U^m + M``. Genus equality alone did not supply an isometry
            from that sum to this specified lattice. The constructive
            embedding decision used here decides the required stronger fact.
            """
            assert self.base_ring() is _owned_integers(), (
                f"the integral hyperbolic index of {self} is computed over ZZ"
            )
            return self.hyperbolic_index()

        @cached_method
        def _direct_hyperbolic_splitting(self):
            r"""Split planes found from primitive divisibility-one null vectors.

            In an even lattice a Bezout partner automatically admits its
            integral correction. In an odd lattice the existing partner
            construction decides the norm congruence. Repeat on the actual
            orthogonal complement. This gives a lower bound and an isometry;
            only reaching the inertia bound proves maximality without the
            complete embedding decision.
            """
            ring = self.base_ring()
            assert ring is _owned_integers() and self.module_rank().is_finite()
            plane = Lattices(ring)("U")
            signature = self.signature_pair()
            possible = min(int(signature.first()), int(signature.second()))
            if possible and self.is_isotropic() is True:
                isotropic = self.isotropic_vector()
                if isotropic.div() == ring.one():
                    try:
                        partner = isotropic.hyperbolic_partner()
                    except ValueError as error:
                        if str(error) != "the integral hyperbolic partner locus is empty":
                            raise
                    else:
                        first = plane.Emb(self)((isotropic, partner)).orthogonal_splitting()
                        complement = first.domain().biproduct_factor(1)
                        lower_index, lower = complement._direct_hyperbolic_splitting()
                        return lower_index + 1, self._extend_hyperbolic_splitting(first, lower)
            hyperbolic = plane ** 0
            inclusion = hyperbolic.Emb(self)(())
            zero = self.orthogonal_decomposition(
                (inclusion, self.Aut().identity())
            ).inverse()
            return 0, zero

        @cached_method
        def _hyperbolic_radical_quotient_section(self):
            r"""Return a nondegenerate radical quotient and a section into this lattice."""
            ring = self.base_ring()
            radical = self.identity_morphism().orthogonal_complement()
            from sage_extensions.rings.real import RR

            if ring is RR:
                from sage_extensions.categories.modules.pure.modules import (
                    _represented_real_rref,
                )

                labels = tuple(self.module_generating_set())
                radical_vectors = tuple(
                    radical.inclusion()(v) for v in radical.module_generators()
                )
                rows = tuple(
                    tuple(vector.to_vector()(label) for label in labels)
                    for vector in radical_vectors
                )
                _, pivots = _represented_real_rref(rows, len(labels), ring)
                lifts = tuple(
                    self.module_generators()[i]
                    for i in range(len(labels))
                    if i not in pivots
                )
                quotient = Lattices(ring)(
                    [[self.b(x, y) for y in lifts] for x in lifts]
                    if lifts else 0
                )
            else:
                reduced = radical.isotropic_reduction()
                quotient = Lattices(ring)(reduced)
                frame = reduced.coordinate_frame()
                perpendicular_inclusion = reduced.orthogonal_complement().inclusion()
                lifts = tuple(
                    perpendicular_inclusion(frame[i])
                    for i in range(int(reduced.module_rank()))
                )
            return quotient, quotient.Emb(self)(lifts)

        @cached_method
        def hyperbolic_index(self):
            r"""Return the largest number of orthogonal hyperbolic planes in ``self``.

            The integral index counts actual ``U`` summands of this lattice,
            not summands of another lattice in its genus. Primitive
            divisibility-one null vectors with integral hyperbolic partners
            construct actual planes and their complements directly. In even
            lattices such a partner is automatic; in odd lattices its norm
            congruence is decided. For larger candidate ranks, the
            discriminant length bounds the complementary rank, and a
            full-rank hyperbolic sum must be even. The general integral
            embedding Mor decides the remaining cases.
            Every such embedding splits because ``U^r`` is unimodular;
            excluding all ranks above the constructed lower bound proves
            maximality.
            Over a supported exact field this is the Witt index.
            For a degenerate finite-rank form, compute the same index on
            the nondegenerate quotient by its radical.

            EXAMPLES::

                sage: U = Lattices(ZZ)("U")
                sage: assert (U + U + Lattices(ZZ)([[2]])).hyperbolic_index() == ZZ(2)
                sage: assert U.twist(ZZ(2)).hyperbolic_index() == ZZ(0)
                sage: assert Lattices(ZZ)([[1, 0], [0, -1]]).hyperbolic_index() == ZZ(0)
                sage: assert Lattices(QQ)([[1, 0], [0, -1]]).hyperbolic_index() == ZZ(1)
            """
            from sage_extensions.categories.rings.ring_foundation import (
                _owned_real_algebraic_numbers,
            )
            from sage_extensions.rings.real import RR

            ring = self.base_ring()
            assert self.module_rank().is_finite(), (
                f"the hyperbolic index of {self} requires finite rank"
            )
            assert ring in (
                _owned_integers(), _owned_rationals(), _owned_real_algebraic_numbers(), RR
            ), (
                f"the hyperbolic index of {self} is computed here over ZZ, QQ, AA and RR"
            )
            if not self.is_nondegenerate():
                quotient, _section = self._hyperbolic_radical_quotient_section()
                return quotient.hyperbolic_index()
            if ring in (_owned_rationals(), _owned_real_algebraic_numbers(), RR):
                return self.witt_index()
            plane = Lattices(ring)("U")
            signature = self.signature_pair()
            upper_bound = min(int(signature.first()), int(signature.second()))
            direct_index, _direct_splitting = self._direct_hyperbolic_splitting()
            rank = int(self.module_rank())
            length = int(self.discriminant_length())
            upper_bound = min(upper_bound, (rank - length) // 2)
            if 2 * upper_bound == rank and self.is_even() is False:
                upper_bound -= 1
            assert direct_index <= upper_bound, (
                "a constructed unimodular summand must respect the discriminant and parity bounds"
            )
            for index in range(upper_bound, direct_index, -1):
                embeddings = (plane ** index).Emb(self)
                empty = embeddings.is_empty()
                assert empty is True or empty is False, (
                    "the integral embedding decision must decide this finite nondegenerate pair"
                )
                if empty is False:
                    return ring(index)
            return ring(direct_index)

        @cached_method
        def maximal_hyperbolic_index_splitting(self):
            r"""Return an isometry ``U^m orthogonal_sum M -> self`` with maximal ``m``.

            The first factor of the domain has rank ``2*m``. Its injection,
            the complementary injection, and the inverse of the returned
            isometry retain the embeddings and projections of the splitting.
            An integral witness comes from successive direct plane splits
            when they attain the maximal index. Otherwise it is selected
            from the complete embedding Mor after nonemptiness is decided
            by :meth:`hyperbolic_index`. ``orthogonal_splitting`` constructs
            the actual complement and an inverse over the original ring.
            Field witnesses come from the existing Witt decomposition.
            For a degenerate form, lift a maximal hyperbolic summand from
            the radical quotient and split its image in the original lattice.

            EXAMPLES::

                sage: U = Lattices(ZZ)("U")
                sage: L = U + Lattices(ZZ)([[2]])
                sage: phi = L.maximal_hyperbolic_index_splitting()
                sage: assert phi.codomain() is L
                sage: assert phi.domain().biproduct_factor(0).module_rank() == 2
                sage: assert L.gram_tensor().pullback(phi) == phi.domain().gram_tensor()
                sage: assert all(phi.inverse()(phi(v)) == v for v in phi.domain().module_generators())
                sage: assert all(phi(phi.inverse()(v)) == v for v in L.module_generators())
                sage: Z = Lattices(ZZ)(0)
                sage: eta = Z.maximal_hyperbolic_index_splitting()
                sage: assert eta.domain().biproduct_factor(0).module_rank() == 0
                sage: assert eta(eta.inverse()(Z.zero())) == Z.zero()
                sage: D = Lattices(ZZ)([[0, 1, 1], [1, 2, 1], [1, 1, 0]])
                sage: assert D.hyperbolic_index() == 1
                sage: delta = D.maximal_hyperbolic_index_splitting()
                sage: assert delta.codomain() is D
                sage: assert delta.domain().biproduct_factor(0).module_rank() == 2
                sage: assert all(delta(delta.inverse()(v)) == v for v in D.module_generators())
            """
            from sage_extensions.categories.rings.ring_foundation import (
                _owned_real_algebraic_numbers,
            )
            from sage_extensions.rings.real import RR

            ring = self.base_ring()
            assert self.module_rank().is_finite(), (
                f"a maximal hyperbolic splitting of {self} requires finite rank"
            )
            assert ring in (
                _owned_integers(), _owned_rationals(), _owned_real_algebraic_numbers(), RR
            ), (
                f"a maximal hyperbolic splitting of {self} is computed here over ZZ, QQ, AA and RR"
            )
            if not self.is_nondegenerate():
                quotient_lattice, section = self._hyperbolic_radical_quotient_section()
                quotient_splitting = quotient_lattice.maximal_hyperbolic_index_splitting()
                hyperbolic = quotient_splitting.domain().biproduct_factor(0)
                if int(hyperbolic.module_rank()) == 0:
                    zero = hyperbolic.Emb(self)(())
                    return self.orthogonal_decomposition(
                        (zero, self.Aut().identity())
                    ).inverse()
                first_inclusion = quotient_splitting.domain().injection(0)
                embedding = hyperbolic.Emb(self)(
                    tuple(
                        section(quotient_splitting(first_inclusion(v)))
                        for v in hyperbolic.module_generators()
                    )
                )
                return embedding.orthogonal_splitting()
            if ring in (_owned_rationals(), _owned_real_algebraic_numbers(), RR):
                return self.witt_decomposition()
            index = int(self.hyperbolic_index())
            direct_index, direct_splitting = self._direct_hyperbolic_splitting()
            if index == direct_index:
                return direct_splitting
            hyperbolic = Lattices(ring)("U") ** index
            embedding = hyperbolic.Emb(self).an_element()
            return embedding.orthogonal_splitting()

        def hyperbolic_plane_power_if_even_unimodular(self):
            r"""Return ``n`` when this lattice is the even unimodular lattice of signature ``(n,n)``.

            The indefinite even unimodular lattice of balanced signature is
            uniquely isometric to ``U^n``. Return ``None`` when those hypotheses
            do not hold.
            """
            signature = self.signature_pair()
            positive, negative = int(signature.first()), int(signature.second())
            if (
                positive > 0
                and positive == negative
                and self.is_even()
                and self.is_unimodular()
            ):
                return positive
            return None

        def is_locally_isometric(self, other, prime) -> bool:
            r"""Return whether ``self`` and ``other`` are isometric over ``ZZ_p``."""
            if other not in Lattices(self.base_ring()):
                raise TypeError(
                    f"cannot compare {self!r} and {other!r} over ZZ_{prime}: {other!r} is not a lattice over {self.base_ring()}"
                )
            return bool(
                self.genus().local_symbol(prime) == other.genus().local_symbol(prime)
            )

        def divisibility_ideal(self, element):
            r"""Return the ideal \(b(v, L) = \{b(v,x) : x\in L\}\) of the base ring.

            The pairings against a generating set generate it.  Over
            \(\mathbb Z\) its positive generator is :meth:`div`.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: L = Lattices(ZZ)([[2, 0], [0, -6]])
                sage: L.divisibility_ideal(L.basis_vector(1)) == ZZ.ideal(6)
                True
            """
            assert element.parent() is self, (
                f"cannot form the divisibility ideal b(v, L) of {element!r} in {self!r}: the vector lies in {element.parent()!r}, not in this lattice"
            )
            ring = self.base_ring()
            pairings = tuple(self.generator_pairings(element).values())
            if not pairings:
                return ring.ideal(ring.zero())
            return ring.ideal(*pairings)

        def generator_pairings(self, element):
            r"""Return the pairings of ``element`` against the selected generators.

            At finite rank every generator is paired; at infinite rank the
            pairing rule of the Gram presentation returns the finitely many
            nonzero pairings.
            """
            assert element.parent() is self, (
                f"cannot pair {element!r} against the generators of {self!r}: the vector lies in {element.parent()!r}, not in this lattice"
            )
            match self.module_rank().is_finite():
                case True:
                    return {
                        label: element.b(self.module_generator(label))
                        for label in self.module_generating_set()
                    }
                case False:
                    return self.gram_tensor().pairings_against(element)

        def is_totally_isotropic(self) -> bool:
            r"""Return whether the form vanishes identically: \(\operatorname{rad}(L)=L\).

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: U = Lattices(ZZ)("U")
                sage: U.is_totally_isotropic()
                False
                sage: U.subobject_on((U.basis_vector(0),)).is_totally_isotropic()
                True
            """
            assert self.module_rank().is_finite(), (
                f"cannot decide whether {self!r} is totally isotropic: it has rank {self.module_rank()}, and total isotropy is decided here only at finite rank"
            )
            zero = self.base_ring().zero()
            return all(
                value == zero
                for generator in self.module_generators()
                for value in self.generator_pairings(generator).values()
            )

        def div(self, element):
            r"""Return the divisibility ``gcd{b(element,x): x in L}`` over ``ZZ``."""
            if element.parent() is not self:
                raise TypeError(
                    f"cannot compute the divisibility of {element!r} in {self!r}: the vector lies in {element.parent()!r}, not in this lattice"
                )

            ring = self.base_ring()
            assert _engine_ring(ring) is SageZZ, (
                f"cannot compute the divisibility of {element!r} as an integer: {self!r} is over {ring}, not ZZ; use divisibility_ideal for the ideal b(v, L)"
            )
            pairings = tuple(
                abs(ring(value)) for value in self.generator_pairings(element).values()
            )
            if not pairings:
                return ring.zero()
            divisor = pairings[0]
            for value in pairings[1:]:
                divisor = divisor.gcd(value)
            return abs(divisor)

        def linear_dual(self):
            r"""Return the exact algebraic dual ``Hom_R(L,R)``."""
            return self.dual_module()

        def metric_map(self):
            r"""Return ``L -> L.linear_dual()``, ``v |-> b(v,-)``."""
            return self.algebraic_correlation_morphism()

        def divisible_sublattice(self, divisor):
            r"""Return ``{v in L : b(v,L) subset divisor*R}`` with both pullback maps.

            At divisor zero this is the radical. The inclusion ``i`` into
            this lattice and ``k=map_to_ideal_dual()`` satisfy ``j*i=u*k``,
            where ``j`` is the generic-fibre inclusion and ``u`` the
            retained ideal-dual inclusion.

            EXAMPLES::

                sage: L = Lattices(ZZ)([[0, 0], [0, 2]])
                sage: e, f = tuple(L.module_generators())
                sage: i0 = L.divisible_sublattice(0).inclusion()
                sage: i2 = L.divisible_sublattice(2).inclusion()
                sage: i3 = L.divisible_sublattice(3).inclusion()
                sage: i0.is_in_image(e) and not i0.is_in_image(f)
                True
                sage: i2.is_in_image(e) and i2.is_in_image(f)
                True
                sage: i3.is_in_image(e) and not i3.is_in_image(f) and i3.is_in_image(L.scalar_multiple(3, f))
                True
                sage: D = L.divisible_sublattice(3)
                sage: j = ModulesOverIntegralDomains(ZZ)(L).generic_fibre_map()
                sage: i = D.inclusion()
                sage: k = D.map_to_ideal_dual()
                sage: u = D.defining_ideal_dual().inclusion()
                sage: all(j(i(x)) == u(k(x)) for x in D.module_generators())
                True
            """
            return self.ideal_dual(divisor).integral_pullback()

        @cached_method
        def dual_lattice(self):
            r"""Return the metric dual ``L^#`` in the rational span of L.

            The underlying module remains an ``R``-module.  For a
            non-unimodular integral lattice its form takes values in
            ``Frac(R)``; it is not turned into a vector space over ``Frac(R)``.
            At infinite rank this is a represented metric-dual lattice in the
            rational span when the Gram rule supplies an inverse rule.  It is
            not the full algebraic dual returned by :meth:`linear_dual`.
            """
            ring = self.base_ring()
            assert self in FormModules(ring).Nondegenerate(), (
                f"{self!r} has no metric dual: the dual lattice is defined for a nondegenerate form, and {self!r} is not known to be nondegenerate; it is an object of {self.category()}"
            )
            match self.module_rank().is_finite():
                case False:
                    dual = ring.free_module(self.module_generating_set())
                    return Lattices(ring)(self.gram_tensor().dual_gram_on(dual))

            fraction_field = ring.fraction_field()
            dual_gram = self.gram_tensor().change_ring(fraction_field).dual_pairing()
            dual_module = self.dual_module()
            if ring is fraction_field:
                # Over a field the metric dual is again a vector space over
                # that field, and the inverse Gram is an ordinary scalar
                # tensor. Keep it as the defining datum rather than wrapping
                # it in a module-valued bilinear map whose Gram is only an
                # indexed family of evaluations.
                return _lattice_on_gram(
                    Lattices(ring),
                    dual_module,
                    dual_gram,
                    _normalized_lattice_names(None, dual_module.module_rank()),
                    None,
                )
            scalars = fraction_field.regular_module()
            scalar_generator = next(iter(scalars.module_generators()))
            # The dual lattice has one value type in every case: the selected
            # restriction-of-scalars module Res_{R -> K}(K).  Even when every
            # inverse-Gram entry lies in R (notably for unimodular lattices),
            # returning an R-valued form here gives its norm a different
            # interface and breaks generic descent through ``underlying_element``.
            value_module = Modules(fraction_field).restriction_of_scalars(
                fraction_field.algebra_structure_morphism()
            )(scalars)
            # ``dual_gram`` is a tensor over Frac(R), on the fraction-field
            # extension of the dual basis. Transfer its coefficients through
            # the selected R-basis by stating the bilinear evaluation in the
            # actual R-module Hom parent.
            labels = tuple(self.module_generating_set())

            def rational_pairing(left, right):
                left_coordinates = left.to_vector()
                right_coordinates = right.to_vector()
                value = sum(
                    (
                        fraction_field(left_coordinates(left_label))
                        * dual_gram[row, column]
                        * fraction_field(right_coordinates(right_label))
                        for row, left_label in enumerate(labels)
                        for column, right_label in enumerate(labels)
                    ),
                    fraction_field.zero(),
                )
                return value_module.wrap(scalars.scalar_multiple(value, scalar_generator))

            rational = dual_module.bilinear_hom_space(value_module)._from_bilinear_evaluation(
                rational_pairing,
                defining_tensor=dual_gram,
            )
            return FormModules(ring)(
                rational,
                _extra_categories=(FormModules(ring).Nondegenerate(), BilinearFormModules(ring).Symmetric()),
            )

        @cached_method
        def dual_lattice_to_linear_dual(self):
            r"""Return ``L^# -> L^*`` induced by ``x |-> b(x,-)``.

            The represented metric dual is built on the selected algebraic
            dual basis.  Its basis vector indexed by ``i`` is therefore sent
            to the coordinate functional ``e_i^*``; this is exactly
            ``x |-> b(x,-)`` on the metric dual.  The target internal-Mor
            object need not itself have a selected module basis.
            """
            dual_lattice = self.dual_lattice()
            linear_dual = self.linear_dual()

            def coordinate_functional(label):
                if self.module_rank().is_finite():
                    # Finite free form modules retain their algebraic dual
                    # on this selected dual basis, rather than as a Mor
                    # parent accepting a callable functional.
                    return linear_dual.module_generator(label)

                def value(source_label):
                    match source_label == label:
                        case True:
                            return self.base_ring().one()
                        case False:
                            return self.base_ring().zero()

                return linear_dual(value)

            return self.module_category().Mor(dual_lattice, linear_dual)(
                coordinate_functional
            )

        def metric_dual(self):
            r"""Return the metric dual ``L^#``; explicit synonym for ``dual_lattice``."""
            return self.dual_lattice()

        def dual_basis(self):
            r"""Return the selected basis of ``L^#`` dual to the selected basis of ``L``."""
            return self.dual_lattice().module_generators()

        @cached_method
        def correlation_morphism(self):
            r"""Return ``L -> L^#``, ``v |-> b(v,-)``, whose selected-basis matrix is ``G``."""

            dual_lattice = self.dual_lattice()
            if self.module_rank().is_finite():
                return self.gram_tensor().curry_bilinear(self, dual_lattice)
            return self.module_category().Mor(self, dual_lattice)(
                lambda label: dual_lattice.linear_combination(
                    self.generator_pairings(self.module_generator(label))
                )
            )

        def correlation(self):
            return self.correlation_morphism()

        @cached_method
        def discriminant_module(self):
            r"""Return ``A_L = coker(L -> L^#)`` with the selected dual-basis presentation."""

            return _discriminant_module(self)

        def discriminant_projection(self):
            r"""Return the quotient morphism ``L^# -> A_L``."""
            return self.discriminant_module().projection()

        def discriminant_class(self, dual_lattice_element):
            r"""Project an element of ``L^#`` to its discriminant class."""
            if dual_lattice_element.parent() is self:
                dual_lattice_element = self.correlation_morphism()(dual_lattice_element)
            return self.discriminant_module().discriminant_class(dual_lattice_element)

        def primitive_dual(self, element):
            r"""Return ``correlation(element)/div(element)`` in ``L^#``.

            For the zero vector this is the zero correlation image, matching
            the archived convention without dividing by the zero
            divisibility.  For a nonzero integral vector, divisibility is the
            positive generator of its pairing ideal, so every selected dual
            coordinate of the correlation image is divisible by it.
            """
            if element.parent() is not self:
                raise TypeError(
                    f"cannot form the primitive dual correlation(v)/div(v) of {element!r} in {self!r}: the vector lies in {element.parent()!r}, not in this lattice"
                )
            correlation_image = self.correlation_morphism()(element)
            if element.is_zero():
                return correlation_image
            divisibility = self.div(element)
            if divisibility <= self.base_ring().zero():
                raise ArithmeticError(
                    f"the nonzero vector {element!r} of {self!r} has divisibility {divisibility}, but the divisibility of a nonzero vector is a positive integer"
                )
            dual_lattice = self.dual_lattice()
            divided_coefficients = {}
            coordinates = correlation_image.to_vector()
            for label in coordinates.support().domain():
                coefficient = coordinates(label)
                quotient = coefficient // divisibility
                if divisibility * quotient != coefficient:
                    raise ArithmeticError(
                        f"the dual coordinate {coefficient} of correlation({element!r}) in {self!r} is not divisible by div(v) = {divisibility}, but div(v) generates the ideal of all pairings b(v, L)"
                    )
                divided_coefficients[label] = quotient
            return dual_lattice.linear_combination(divided_coefficients)

        def divided_discriminant_class(self, element):
            r"""Return the class represented by ``correlation(element)/div(element)``."""
            if element.parent() is not self:
                raise TypeError(
                    f"cannot form the discriminant class of correlation(v)/div(v) for {element!r} in {self!r}: the vector lies in {element.parent()!r}, not in this lattice"
                )
            divisibility = self.div(element)
            if divisibility == 0:
                raise ValueError(
                    f"{element!r} has divisibility 0 in {self!r}, so correlation(v)/div(v) is undefined; the discriminant class [v/div(v)] needs a vector with nonzero pairing against the lattice"
                )
            return self.discriminant_class(self.primitive_dual(element))

        def get_isotropic_type(self, element) -> str:
            r"""Classify a primitive isotropic vector in an even 2-elementary lattice.

            Divisibility one is ``"Odd"``.  Divisibility two is separated by
            whether the class ``[v/2]`` in the discriminant quadratic module
            is characteristic, giving ``"Even characteristic"`` or
            ``"Even ordinary"``.  These names classify the cusp type; they do
            not assert that the ambient lattice itself is odd or even beyond
            the explicit quadratic-form hypothesis.
            """
            if element.parent() is not self:
                raise TypeError(
                    f"cannot classify the isotropic type of {element!r} in {self!r}: the vector lies in {element.parent()!r}, not in this lattice"
                )
            if not element.is_isotropic():
                raise ValueError(
                    f"cannot classify the isotropic type of {element!r} in {self!r}: the vector is not isotropic, q(v) = {element.q()}"
                )
            if not element.is_primitive():
                raise ValueError(
                    f"cannot classify the isotropic type of {element!r} in {self!r}: the vector is not primitive"
                )
            if not self.is_even() or not self.is_p_elementary(self.base_ring()(2)):
                raise ValueError(
                    f"cannot classify the isotropic type of {element!r}: the classification by divisibility and [v/2] holds for an even 2-elementary lattice, and {self!r} is not both even and 2-elementary"
                )
            divisibility = self.div(element)
            if divisibility == self.base_ring().one():
                return "Odd"
            if divisibility != self.base_ring()(2):
                raise ValueError(
                    f"the primitive isotropic vector {element!r} of the 2-elementary lattice {self!r} has divisibility {divisibility}, but in a 2-elementary lattice a primitive vector has divisibility 1 or 2"
                )
            divided_class = self.divided_discriminant_class(element)
            if divided_class.is_characteristic():
                return "Even characteristic"
            return "Even ordinary"

        def radical(self):
            r"""Return ``rad(L)=id_L(L)^perp`` as a subobject of ``L``."""
            return self.identity_morphism().orthogonal_complement()

        @cached_method
        def isotropic_reduction(self):
            r"""Return ``S^perp/S`` when this lattice is represented as a subobject.

            One reduction per subobject, so its parabolic subgroup, the
            generators selected on it and the actions out of it persist.
            """

            if self not in ModuleSubobjects(self.base_ring()):
                raise TypeError(
                    f"cannot form S^perp/S for {self!r}: the isotropic reduction is taken of a sublattice with an inclusion into a lattice, but {self!r} is only an object of {self.category()}"
                )
            return self.inclusion().isotropic_reduction()

        def I_perp_mod_I(self, vectors):
            r"""Return ``I^perp/I`` for the primitive isotropic span of ``vectors``.

            This is the archived parent-facing name for the same owned
            isotropic-reduction construction.  The input vectors are promoted
            immediately to a represented primitive totally isotropic
            subobject, so the quotient retains its inclusion, perpendicular,
            projection lifts and parabolic data.
            """
            isotropic = self.primitive_isotropic_subobject(*tuple(vectors))
            return isotropic.inclusion().isotropic_reduction()

        def radical_quotient(self):
            r"""Return the nondegenerate quotient ``L/rad(L)``."""
            return self.radical().isotropic_reduction()

        def overlattice(self, *discriminant_classes):
            r"""Return the inclusion ``L -> L'`` generated by discriminant classes.

            The supplied classes are lifted to ``L^#``.  Together with ``L``
            they span ``L'`` inside ``L tensor QQ``; the result is accepted
            exactly when the inherited form is integral on that span.
            """
            assert _engine_ring(self.base_ring()) is SageZZ
            assert self.module_rank().is_finite() and self.is_nondegenerate()

            from functools import reduce

            from sage.modules.free_module import FreeModule as SageFreeModule
            from sage.rings.rational_field import QQ as SageQQ

            discriminant_module = self.discriminant_module()
            ring = self.base_ring()
            rationals = ring.fraction_field()
            rank = int(self.module_rank())
            dual_gram = self.gram_tensor().change_ring(rationals).dual_tensor()
            rational_rows = [
                [rationals.one() if i == j else rationals.zero() for j in range(rank)]
                for i in range(rank)
            ]
            dual_labels = tuple(self.dual_lattice().module_generating_set())
            for discriminant_class in discriminant_classes:
                element = (
                    discriminant_class
                    if discriminant_class.parent() is discriminant_module
                    else discriminant_module(discriminant_class)
                )
                lift = discriminant_module.dual_lattice_lift(element)
                lift_coordinates = lift.to_vector()
                dual_coordinates = tensor(
                    rationals,
                    (),
                    (rank,),
                    [lift_coordinates(label) for label in dual_labels],
                )
                rational_rows.append(tuple(dual_gram * dual_coordinates))

            denominator = reduce(
                lambda current, coordinate: current.lcm(coordinate.denominator()),
                (coordinate for row in rational_rows for coordinate in row),
                ring.one(),
            )

            # Private HNF/span workspace.  Only backend scalars enter this block.
            backend_denominator = _engine_element(ring, denominator)
            scaled_rows = [
                [
                    SageZZ(backend_denominator * _engine_element(rationals, coordinate))
                    for coordinate in row
                ]
                for row in rational_rows
            ]
            scaled_span = SageFreeModule(SageZZ, rank).submodule(scaled_rows)
            integral_basis_backend = scaled_span.basis_matrix()
            integral_basis_rows = [
                [_owned_engine_element(ring, entry) for entry in row]
                for row in integral_basis_backend.rows()
            ]
            basis_rows = tensor.matrix(
                rationals,
                tuple(
                    tuple(
                        _owned_engine_element(
                            rationals,
                            SageQQ(_engine_element(ring, entry))
                            / SageQQ(backend_denominator),
                        )
                        for entry in row
                    )
                    for row in integral_basis_rows
                ),
            )

            def basis_inclusion(scalars, rows):
                # The map scalars^rank -> L sending e_j to the j-th basis
                # vector of L', whose coordinates in L are rows[j].
                space = scalars.matrix_space(rank, rank)
                coordinates = space.codomain()
                coordinate_labels = tuple(coordinates.module_generating_set())
                return space(
                    tuple(
                        coordinates.linear_combination(
                            {
                                label: entry
                                for label, entry in zip(
                                    coordinate_labels, row, strict=True
                                )
                                if entry
                            }
                        )
                        for row in rows
                    )
                )

            basis_map = basis_inclusion(
                rationals,
                tuple(
                    tuple(basis_rows[row, column] for column in range(rank))
                    for row in range(rank)
                ),
            )
            gram = self.gram_tensor().change_ring(rationals).pullback(basis_map)
            if not all(gram[i, j] in ring for i in range(rank) for j in range(rank)):
                raise ValueError(
                    f"the discriminant classes {discriminant_classes!r} of {self!r} do not give an integral overlattice: the form is not integral on the span of L and their lifts, so the classes do not span an isotropic subgroup of the discriminant form"
                )
            integral_entries = [
                [ring(gram[i, j]) for j in range(rank)] for i in range(rank)
            ]

            labels = finite_ordered_set(range(rank))
            integral_gram = tensor(
                ring,
                (),
                (rank, rank),
                integral_entries,
            )
            enlarged = Lattices(ring)(
                integral_gram,
                module_generators=labels,
            )
            # The image of e_s is the preimage of d e_s under the inclusion of
            # d L' into L, read in the basis of L'.
            integral_basis = basis_inclusion(ring, integral_basis_rows)
            images = {}
            for source_position, source_label in enumerate(
                self.module_generating_set()
            ):
                target = [
                    denominator if index == source_position else ring.zero()
                    for index in range(rank)
                ]
                coefficients = _solve_preimage_integrally(integral_basis, target, ring)
                images[source_label] = enlarged.linear_combination(
                    {
                        label: coefficient
                        for label, coefficient in zip(labels, coefficients, strict=True)
                        if coefficient
                    }
                )
            return self.Emb(enlarged)(images)

        def maximal_overlattice(self):
            r"""Return one maximal integral/even overlattice inclusion of ``L``.

            Nikulin's overlattice correspondence identifies integral
            overlattices with bilinear-isotropic subgroups of ``A_L`` and,
            for even ``L``, even overlattices with quadratic-isotropic
            subgroups.  ``discriminant_group()`` selects the applicable form;
            choosing one maximal isotropic subgroup therefore gives one
            maximal overlattice.  No uniqueness is asserted.
            """
            if not self.is_nondegenerate():
                raise ValueError(
                    f"{self!r} has no maximal overlattice by Nikulin's correspondence: that needs a finite discriminant form, and {self!r} is degenerate"
                )
            form = self.discriminant_group()
            maximal = form.maximal_isotropic_subgroups()
            if maximal.cardinality() == 0:
                raise ArithmeticError(
                    f"the discriminant form {form!r} of {self!r} returned no maximal isotropic subgroup, but every finite discriminant form has one (the zero subgroup is isotropic)"
                )
            subgroup = maximal[0]
            inclusion = form.overlattice_from_isotropic_subobject(subgroup)
            for larger in form.isotropic_subgroups():
                if int(larger.cardinality()) <= int(subgroup.cardinality()):
                    continue
                if all(element in larger for element in subgroup.embedded_elements()):
                    raise ArithmeticError(
                        f"the isotropic subgroup {subgroup!r} of the discriminant form of {self!r} was returned as maximal, but it lies in the larger isotropic subgroup {larger!r}"
                    )
            return inclusion

        def integral_overlattice_inclusions(self):
            r"""Return all integral overlattice inclusions ``L -> L'``.

            Nikulin's overlattice correspondence identifies integral
            overlattices with bilinear-isotropic subgroups of the discriminant
            bilinear form.  The zero subgroup contributes the identity
            extension.
            """
            assert _engine_ring(self.base_ring()) is SageZZ, (
                f"cannot enumerate the integral overlattices of {self!r}: this is implemented only for lattices over ZZ, and this lattice is over {self.base_ring()}"
            )
            if not self.module_rank().is_finite() or not self.is_nondegenerate():
                raise ValueError(
                    f"cannot enumerate the integral overlattices of {self!r}: Nikulin's correspondence needs a nondegenerate lattice of finite rank"
                )
            return _overlattice_inclusions(self.discriminant_bilinear_form())

        def local_modification(self, prime, *discriminant_classes):
            r"""Return the isotropic ``p``-primary overlattice modification.

            A local modification at ``p`` is the usual discriminant-form glue
            along an isotropic subgroup contained in the ``p``-primary part of
            ``A_L``.  The returned value is the actual inclusion ``L -> L'``.
            """
            prime = self.base_ring()(prime)
            if not prime.is_prime():
                raise ValueError(
                    f"cannot take a local modification of {self!r} at {prime}: a local modification is taken at a prime p, and {prime} is not prime"
                )
            form = self.discriminant_group()
            classes = tuple(
                element if element.parent() is form else form(element)
                for element in discriminant_classes
            )
            for element in classes:
                order = element.additive_order()
                if order != prime ** int(order.valuation(prime)):
                    raise ValueError(
                        f"cannot take the local modification of {self!r} at p={prime}: every glue class must lie in the {prime}-primary part of the discriminant group, but the class {element} has order {order}"
                    )
            subgroup = form.subgroup_on(classes)
            return form.overlattice_from_isotropic_subobject(subgroup)

        def even_overlattice_inclusions(self):
            r"""Return all even overlattice inclusions ``L -> L'``.

            For an even integral lattice, Nikulin's overlattice correspondence
            identifies even overlattices with isotropic subgroups of the
            discriminant quadratic form.  The zero subgroup is included and
            therefore contributes the identity extension.
            """
            assert _engine_ring(self.base_ring()) is SageZZ, (
                f"cannot enumerate the even overlattices of {self!r}: this is implemented only for lattices over ZZ, and this lattice is over {self.base_ring()}"
            )
            if (
                not self.is_even()
                or not self.module_rank().is_finite()
                or not self.is_nondegenerate()
            ):
                raise ValueError(
                    f"cannot enumerate the even overlattices of {self!r}: Nikulin's correspondence with isotropic subgroups of the discriminant quadratic form needs an even nondegenerate lattice of finite rank, and {self!r} fails one of these"
                )
            return _overlattice_inclusions(self.discriminant_quadratic_form())

        def embeds_in_even_unimodular(self, positive, negative) -> bool:
            r"""Decide primitive embeddability into an even unimodular ``II_{p,q}``.

            Nikulin's primitive-embedding criterion reduces this to existence
            of the orthogonal complement: its signature is the signature
            difference and its discriminant quadratic form is ``-q_L``.
            """
            ring = self.base_ring()
            positive = ring(positive)
            negative = ring(negative)
            assert _engine_ring(ring) is SageZZ, (
                f"cannot decide whether {self!r} embeds primitively in II_({positive},{negative}): Nikulin's criterion is implemented only for lattices over ZZ, and this lattice is over {ring}"
            )
            if (
                not self.is_even()
                or not self.module_rank().is_finite()
                or not self.is_nondegenerate()
            ):
                raise ValueError(
                    f"cannot decide whether {self!r} embeds primitively in II_({positive},{negative}): Nikulin's criterion needs an even nondegenerate lattice of finite rank, and {self!r} fails one of these"
                )
            _signature = self.signature_pair()
            source_positive, source_negative = (
                ring(int(_signature.first())),
                ring(int(_signature.second())),
            )
            if (positive - negative) % 8 != 0:
                return False
            if positive < source_positive or negative < source_negative:
                return False
            complement_signature = signature_pair(
                positive - source_positive,
                negative - source_negative,
            )
            return (
                self.discriminant_quadratic_form()
                .twist(-1)
                .is_discriminant_form_of_even_lattice(complement_signature)
            )

        def embed_in_even_unimodular(self, positive, negative):
            r"""Return one primitive embedding into an even unimodular lattice."""
            positive = int(positive)
            negative = int(negative)
            if self.module_rank() == 1 and (positive == 0 or negative == 0):
                category = Lattices(self.base_ring())
                e8 = category("E8")
                block = e8.twist(-1) if positive else e8
                target = _orthogonal_sum(
                    tuple(block for _ in range((positive + negative) // 8))
                )
                (source_generator,) = self.module_generators()
                source_square = self.b(source_generator, source_generator)
                for target_generator in target.module_generators():
                    if target.b(target_generator, target_generator) != source_square:
                        continue
                    return self.Emb(target)((target_generator,))
                for embedding in self.Emb(target):
                    if embedding.is_primitive():
                        return embedding

            if not self.embeds_in_even_unimodular(positive, negative):
                raise ValueError(
                    f"{self!r} has no primitive embedding into II_{{{positive},{negative}}}: by Nikulin's criterion no even lattice of the complementary signature has discriminant form -q_L"
                )

            target_gram, embedding_matrix = (
                lattice_engines._oscar_lattices.even_unimodular_primitive_embedding(
                    self.gram_tensor(), positive, negative
                )
            )
            target = Lattices(self.base_ring())(target_gram)
            target_generators = tuple(target.module_generators())
            images = tuple(
                sum(
                    (
                        target.scalar_multiple(
                            embedding_matrix[row, column], target_generators[row]
                        )
                        for row in range(int(target.module_rank()))
                        if embedding_matrix[row, column]
                    ),
                    target.zero(),
                )
                for column in range(int(self.module_rank()))
            )
            embedding = self.Emb(target)(images)
            embedding.validate_primitivity(check=False)
            lattice_engines.validate_lattice_signature(
                (target, signature_pair(positive, negative)), check=False
            )
            return embedding

        def glue_map(self, first, second):
            r"""Return the glue anti-isometry presenting a primitive extension.

            ``first`` and ``second`` are primitive orthogonal subobjects
            ``S,R <= L`` with ranks summing to ``rk(L)``.  Then

            ``L/(S + R)``

            embeds in ``A_S ⊕ A_R`` as the graph of an anti-isometry
            ``H_S -> H_R`` between subgroups of the two discriminant forms.
            The returned arrow is that anti-isometry written as an ordinary
            isometry ``H_S -> H_R(-1)``.  Its domain and codomain are actual
            formed subobjects carrying their inclusions into ``A_S`` and
            ``A_R(-1)``.

            Which discriminant form states this is the parity of ``L``, and
            the returned arrow says which one it used.

            - ``L`` even.  Its sublattices are even, both discriminants carry
              their ``K/2R``-valued quadratic forms, and the glue satisfies
              ``q_R(gamma x) = -q_S(x)``.  Domain and codomain are torsion
              quadratic forms and ``is_quadratic()`` holds.
            - ``L`` odd.  Only the ``K/R``-valued bilinear forms are defined
              on both discriminants -- one of ``S``, ``R`` may itself be even,
              while the extension is not -- and the glue satisfies
              ``b_R(gamma x, gamma y) = -b_S(x,y)``.  Domain and codomain are
              torsion bilinear forms and ``is_quadratic()`` fails.

            The odd statement asks no hypothesis the even one does not; it
            concludes less.  A quadratic-isotropic subgroup is
            bilinear-isotropic and not conversely, so reading an even ``L``
            through its bilinear form would lose exactly the distinction
            between an integral overlattice and an even one.

            Peters and Sterk, *Symmetric and Quadratic Forms, with
            Applications to Coding Theory, Algebraic Geometry and Topology*
            (version of June 2024) state both parities at once, as "symmetric
            (respectively quadratic)": Prop. 15.1.1 for the glue criterion
            ``b_R(psi -, psi -) + b_S(-,-) = 0`` and its reading as an
            anti-isometry, Prop. 15.1.3 for the converse construction with
            ``[L:S+R] = |H_S|`` and ``S``, ``R`` primitive in the result,
            Prop. 1.7.4 for the overlattice correspondence in each parity,
            and Example 1.7.5.1 for a subgroup of ``A_{U(2)}`` that is
            bilinear-isotropic and not quadratic-isotropic.
            """
            ring = self.base_ring()
            assert _engine_ring(ring) is SageZZ, (
                f"cannot compute the glue map of {self!r} along {first!r} and {second!r}: glue maps are implemented only for lattices over ZZ, and this lattice is over {ring}"
            )
            for subobject in (first, second):
                assert (
                    subobject in ModuleSubobjects(ring)
                    and subobject.inclusion().codomain() is self
                ), (
                    f"cannot compute the glue map of {self!r}: {subobject!r} is not a sublattice of {self!r} with an inclusion into it"
                )
                assert subobject.is_primitive(), (
                    f"cannot compute the glue map of {self!r}: the sublattice {subobject!r} is not primitive, but L is a primitive extension of S + R only for primitive S and R"
                )
            assert first.module_rank() + second.module_rank() == self.module_rank(), (
                f"cannot compute the glue map of {self!r}: a primitive extension needs rk(S) + rk(R) = rk(L), but rk(S) = {first.module_rank()}, rk(R) = {second.module_rank()} and rk(L) = {self.module_rank()}"
            )
            assert all(
                self.b(left, right) == ring.zero()
                for left in first.embedded_module_generators()
                for right in second.embedded_module_generators()
            ), (
                f"cannot compute the glue map of {self!r}: the sublattices {first!r} and {second!r} are not orthogonal, but a primitive extension of S + R needs b(S, R) = 0"
            )

            quadratic = self.is_even()
            if quadratic:
                first_discriminant = first.discriminant_quadratic_form()
                second_discriminant = second.discriminant_quadratic_form()
            else:
                first_discriminant = first.discriminant_bilinear_form()
                second_discriminant = second.discriminant_bilinear_form()
            glue_forms = _torsion_form_modules(ring, quadratic=quadratic)
            first_inclusion = tensor.from_morphism(first.inclusion())
            second_inclusion = tensor.from_morphism(second.inclusion())
            ambient_gram = self.gram_tensor()

            graph = {}
            for ambient_generator in self.module_generators():
                coordinates = ambient_generator.to_vector()
                labels = tuple(self.module_generating_set())
                ambient_vector = tensor.vector(
                    ring,
                    [coordinates(label) for label in labels],
                )
                ambient_covector = ambient_gram * ambient_vector
                first_covector = ambient_covector * first_inclusion
                second_covector = ambient_covector * second_inclusion
                first_class = first_discriminant.linear_combination(
                    {
                        label: ring(coefficient)
                        for label, coefficient in zip(
                            first_discriminant.module_generating_set(),
                            first_covector,
                            strict=True,
                        )
                        if coefficient
                    }
                )
                second_class = second_discriminant.linear_combination(
                    {
                        label: ring(coefficient)
                        for label, coefficient in zip(
                            second_discriminant.module_generating_set(),
                            second_covector,
                            strict=True,
                        )
                        if coefficient
                    }
                )
                if first_class == first_discriminant.zero():
                    if second_class != second_discriminant.zero():
                        raise ArithmeticError(
                            f"the glue relation of {self!r} along {first!r} and {second!r} sends the zero class of A_S to the nonzero class {second_class!r} of A_R, so it is not the graph of a group homomorphism H_S -> H_R"
                        )
                    continue
                previous = graph.get(first_class)
                if previous is not None and previous != second_class:
                    raise ArithmeticError(
                        f"the glue relation of {self!r} along {first!r} and {second!r} sends the class {first_class!r} of A_S to both {previous!r} and {second_class!r} in A_R, so it is not the graph of a function H_S -> H_R"
                    )
                graph[first_class] = second_class

            source_classes = tuple(graph)
            target_classes = tuple(graph[value] for value in source_classes)
            abstract_glue = (
                Modules(first_discriminant.base_ring())
                .FinitelyPresented()
                .Torsion()(
                    _relations_among_generators(first_discriminant, source_classes)
                )
            )
            labels = tuple(abstract_glue.module_generating_set())

            glue_values = first_discriminant.value_module()
            source_images = {
                label: source_class
                for label, source_class in zip(labels, source_classes, strict=True)
            }

            def source_inclusion(source):
                return source.Mono(first_discriminant)(
                    source_images, quadratic=quadratic
                )

            source_form = glue_forms.from_module(
                abstract_glue,
                _form_gram_on(first_discriminant, source_classes, quadratic=quadratic),
                glue_values,
                _subobject_ambient=first_discriminant,
                _subobject_generator_images=source_images,
                _subobject_inclusion_factory=source_inclusion,
            )
            target_gram = tuple(
                tuple(-entry for entry in row)
                for row in _form_gram_on(
                    second_discriminant, target_classes, quadratic=quadratic
                )
            )
            # The twist is taken on the module underlying A_R, which is A_R
            # itself when it is the discriminant module and its bilinear
            # reading when the summand is even inside an odd L, so the classes
            # cross into the twist the same way in both parities.
            second_twist = second_discriminant.twist(-1)
            target_images = {
                label: second_twist(target_class)
                for label, target_class in zip(labels, target_classes, strict=True)
            }

            def target_inclusion(target):
                return target.Mono(second_twist)(target_images, quadratic=quadratic)

            target_form = glue_forms.from_module(
                abstract_glue,
                target_gram,
                glue_values,
                _subobject_ambient=second_twist,
                _subobject_generator_images=target_images,
                _subobject_inclusion_factory=target_inclusion,
            )

            second_unformed = second_discriminant.unformed_module()
            target_subgroup = second_unformed.subobject_on(
                tuple(second_unformed(target_class) for target_class in target_classes)
            )
            extension_index = first.sum(second).index()
            if source_form.cardinality() != extension_index:
                raise ArithmeticError(
                    f"the glue subgroup H_S of {self!r} along {first!r} has order {source_form.cardinality()}, but a primitive extension has |H_S| = [L:S+R] = {extension_index}"
                )
            if target_subgroup.cardinality() != extension_index:
                raise ArithmeticError(
                    f"the glue subgroup H_R of {self!r} along {second!r} has order {target_subgroup.cardinality()}, but the glue map is a bijection H_S -> H_R with |H_S| = [L:S+R] = {extension_index}"
                )

            forward = source_form.module_category().Mor(source_form, target_form)(
                {label: target_form.module_generator(label) for label in labels}
            )
            inverse = target_form.module_category().Mor(target_form, source_form)(
                {label: source_form.module_generator(label) for label in labels}
            )
            return _torsion_form_isometry(forward, inverse, quadratic=quadratic)

        @cached_method
        def discriminant_bilinear_form(self):
            r"""Return ``A_L`` with its descended ``K/R``-valued bilinear form."""

            module = self.discriminant_module()
            assert module in DiscriminantBilinearModules(self.base_ring())
            if module in DiscriminantQuadraticModules(self.base_ring()):
                return module.associated_bilinear_form()
            return module

        @cached_method
        def discriminant_quadratic_form(self):
            r"""Return ``A_L`` with its ``K/2R``-valued quadratic form when ``L`` is even."""

            if not self.is_even():
                raise ValueError(
                    f"{self!r} has no discriminant quadratic form: q_L: A_L -> Q/2Z is defined only for an even lattice, and {self!r} is odd; use discriminant_bilinear_form"
                )
            module = self.discriminant_module()
            assert module in DiscriminantQuadraticModules(self.base_ring())
            return module

        @cached_method
        def discriminant_group(self):
            r"""Return the ``ZZ`` discriminant group with every form supported by ``L``."""
            if _engine_ring(self.base_ring()) is not SageZZ:
                raise TypeError(
                    f"{self!r} is over {self.base_ring()}, not ZZ, so it has no discriminant group; use discriminant_module for the discriminant module over its base ring"
                )
            return (
                self.discriminant_quadratic_form()
                if self.is_even()
                else self.discriminant_bilinear_form()
            )

        @cached_method
        def _discriminant_invariant_factors(self):
            r"""Return the nontrivial invariant factors of ``A_L`` over ``ZZ``."""
            if _engine_ring(self.base_ring()) is not SageZZ:
                raise TypeError(
                    f"cannot compute discriminant invariant factors of {self!r}: the lattice is over {self.base_ring()}, not ZZ"
                )
            ring = self.base_ring()
            return tuple(
                abs(invariant)
                for invariant in self.correlation_morphism().cokernel().invariant_factors()
                if abs(invariant) > ring.one()
            )

        @cached_method
        def discriminant_length(self):
            r"""Return the minimal number of generators of ``A_L`` over ``ZZ``."""
            if _engine_ring(self.base_ring()) is not SageZZ:
                raise TypeError(
                    f"cannot compute the length of the discriminant group of {self!r}: it is implemented only for lattices over ZZ, and this lattice is over {self.base_ring()}"
                )
            return self.base_ring()(len(self._discriminant_invariant_factors()))

        @cached_method
        def is_p_elementary(self, prime) -> bool:
            r"""Return whether ``A_L`` is an elementary abelian ``prime``-group.

            For a finite-rank nondegenerate integral lattice with Gram matrix
            ``G``, the exponent of ``coker(G)`` is the least positive integer
            ``m`` for which ``m*G^(-1)`` is integral.  Thus ``A_L`` is
            ``p``-elementary exactly when the common denominator of ``G^(-1)``
            divides the prime ``p``.  This tests the exponent directly without
            constructing Smith normal form of the cokernel.
            """
            if _engine_ring(self.base_ring()) is not SageZZ:
                raise TypeError(
                    f"cannot decide whether {self!r} is {prime}-elementary: it is implemented only for lattices over ZZ, and this lattice is over {self.base_ring()}"
                )
            ring = self.base_ring()
            prime = ring(prime)
            if not prime.is_prime():
                raise ValueError(
                    f"cannot decide whether {self!r} is p-elementary for p = {prime}: {prime} is not prime"
                )
            if self.is_unimodular() is True:
                # A unimodular lattice has trivial discriminant group, so its
                # p-elementarity is immediate for every prime. Avoid building
                # the correlation cokernel merely to enumerate no invariants.
                return True
            denominator = _owned_engine_element(ring, self._integral_gram_inverse().denominator())
            return denominator == ring.one() or denominator == prime

        def is_coeven(self) -> bool:
            r"""Return whether the discriminant quadratic form is integer-valued.

            This is the coeven property of an even nondegenerate integral
            lattice.  Unlike :meth:`delta`, it is not restricted to
            2-elementary discriminant groups: every element of ``A_L`` is
            checked in the finite discriminant quadratic module.
            """
            if _engine_ring(self.base_ring()) is not SageZZ:
                raise TypeError(
                    f"cannot decide whether {self!r} is coeven: it is implemented only for lattices over ZZ, and this lattice is over {self.base_ring()}"
                )
            if not self.is_even():
                raise ValueError(
                    f"cannot decide whether {self!r} is coeven: coevenness is a property of the discriminant quadratic form, which exists only for an even lattice, and {self!r} is odd"
                )
            if not self.is_nondegenerate():
                raise ValueError(
                    f"cannot decide whether {self!r} is coeven: coevenness needs a finite discriminant quadratic form, and {self!r} is degenerate"
                )
            discriminant_form = self.discriminant_quadratic_form()
            ring = self.base_ring()
            return all(
                discriminant_form.q(element).lift() in ring
                for element in discriminant_form
            )

        def is_coodd(self) -> bool:
            r"""Return the negation of :meth:`is_coeven`."""
            return not self.is_coeven()

        def two_u_eichler_model(self):
            r"""Return the represented ``U + U + self`` Eichler model."""
            from sage_extensions.categories.eichler_criterion import (
                TwoUEichlerModel,
            )

            return TwoUEichlerModel(self)

        def two_u_eichler_model_from_represented_biproduct(self):
            r"""Wrap this existing represented ``U + U + K`` biproduct as an Eichler model."""
            from sage_extensions.categories.eichler_criterion import (
                TwoUEichlerModel,
            )

            return TwoUEichlerModel.from_represented_biproduct(self)

        def two_hyperbolic_plane_splitting(self) -> LatticeIsometryMethods | None:
            r"""Return a selected isometry ``U + U + K -> self``.

            Each plane is split by its isotropic reduction. The source is
            their orthogonal biproduct with the second reduction, retaining
            the quotient lattices and their universal injections.
            The genus comparison first decides whether two integral U
            summands exist. For an even indefinite lattice in such a genus,
            rank(L) >= length(A_L)+4; uniqueness in that genus follows from
            Nikulin, Theorem 1.14.2 (Math. USSR-Izv. 14 (1980), 103--167).
            Therefore exhaustive integral-vector enumeration for a null
            vector of divisibility one terminates whenever it is invoked.
            The second reduction similarly has rank >= length(A)+2 and a
            unimodular hyperbolic summand. Neither selected PARI witness
            nor an initial Gram framing determines which null line is used.

            EXAMPLES::

                sage: L = Lattices(ZZ)([[0, 1, 1, 0], [1, 2, 1, 1], [1, 1, 0, 2], [0, 1, 2, 2]])
                sage: splitting = L.two_hyperbolic_plane_splitting()
                sage: splitting.codomain() is L
                True
                sage: splitting.inverse() * splitting == splitting.domain().Isom(splitting.domain()).one()
                True
                sage: source = splitting.domain()
                sage: source.biproduct_factor(0).module_rank() == source.biproduct_factor(1).module_rank() == 2
                True
                sage: all(splitting.inverse()(splitting(source.injection(i)(v))) == source.injection(i)(v) for i in (0, 1) for v in source.biproduct_factor(i).module_generators())
                True
                sage: splitting * splitting.inverse() == L.Isom(L).identity()
                True

            Recover the splitting after changing the basis of ``2U + E8(-1)``::

                sage: C = Lattices(ZZ)
                sage: standard = C("U") + C("U") + C("E8")
                sage: basis = tuple(standard.module_generators())
                sage: changed = tuple(basis[i] + basis[i + 1] for i in range(11)) + (basis[11],)
                sage: scrambled = C(tuple(tuple(standard.b(x, y) for y in changed) for x in changed))
                sage: recovered = scrambled.two_hyperbolic_plane_splitting()
                sage: recovered.domain().splits_two_hyperbolic_planes()
                True
                sage: all(recovered.inverse()(recovered(x)) == x for x in recovered.domain().module_generators())
                True
                sage: all(scrambled.b(recovered(x), recovered(y)) == recovered.domain().b(x, y) for x in recovered.domain().module_generators() for y in recovered.domain().module_generators())
                True
            """
            assert _engine_ring(self.base_ring()) is SageZZ and self.is_even(), (
                f"the integral two-hyperbolic-plane splitting is computed for even ZZ-lattices, not {self}"
            )
            if not self.is_isotropic() or self.integral_hyperbolic_index() < 2:
                return None
            first = self.isotropic_vector()
            if first.div() != self.base_ring().one():
                first = lattice_engines._unit_divisibility_isotropic_witness(self)
            first_reduction = first.isotropic_reduction()
            first_splitting = first_reduction.integral_hyperbolic_splitting()
            if not first_reduction.is_isotropic():
                return None
            second = first_reduction.isotropic_vector()
            if second.div() != self.base_ring().one():
                second = lattice_engines._unit_divisibility_isotropic_witness(
                    first_reduction
                )
            second_reduction = second.isotropic_reduction()
            second_splitting = second_reduction.integral_hyperbolic_splitting()
            first_sum = first_splitting.codomain()
            second_sum = second_splitting.codomain()
            first_plane = first_sum.biproduct_factor(0)
            second_plane = second_sum.biproduct_factor(0)
            normal = Lattices(self.base_ring()).orthogonal_sum(
                (first_plane, second_plane, second_reduction)
            )
            first_assembly = first_splitting.inverse()
            reduction_embedding = first_assembly * first_sum.injection(1)
            second_assembly = reduction_embedding * second_splitting.inverse()
            assembled = normal.from_coproduct_cocone(
                (
                    first_assembly * first_sum.injection(0),
                    second_assembly * second_sum.injection(0),
                    second_assembly * second_sum.injection(1),
                )
            )
            return normal.Isom(self)(
                lambda label: assembled(normal.module_generator(label))
            )

        def rational_polyhedral_cone(
            self,
            halfspace_covectors,
            *,
            equation_covectors=(),
            wall_roots=None,
            complete=None,
        ):
            r"""Return the exact rational polyhedral cone cut out in this lattice."""
            from sage_extensions.categories.polyhedral_cones import (
                _rational_polyhedral_cone,
            )

            return _rational_polyhedral_cone(
                self,
                halfspace_covectors,
                equation_covectors=equation_covectors,
                wall_roots=wall_roots,
                complete=complete,
            )

        def number_field_vinberg(self, real_embedding):
            r"""Retain the selected real place for number-field Vinberg enumeration."""
            from sage_extensions.categories.hyperbolic_lattices import (
                NumberFieldVinbergLattice,
            )

            return NumberFieldVinbergLattice(self, real_embedding)

        def reflection(self, root):
            r"""Return the integral orthogonal reflection in ``root``.

            The reflection exists exactly when ``root`` is an integral reflection vector: for every selected
            module generator ``e_i``, ``2*b(e_i,root)/b(root,root)`` must lie
            in the base ring.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: U = Lattices(ZZ)("U")
                sage: root = U.basis_vector(0) + U.basis_vector(1)
                sage: U.reflection(root)(U.basis_vector(0))
                -e_1
            """
            if root.parent() is not self:
                raise TypeError(
                    f"cannot reflect {self!r} in {root!r}: the vector lies in {root.parent()!r}, not in this lattice"
                )
            assert root.q() != self.base_ring().zero(), (
                f"there is no reflection of {self!r} in {root}: s_r is defined only for b(r, r) != 0"
            )
            if not root.is_integral_reflection_vector():
                raise ValueError(
                    f"the reflection of {self!r} in {root} is not an isometry of the lattice: 2 b(x, r)/b(r, r) is not in {self.base_ring()} for every x, so {root} is not an integral reflection vector"
                )
            ring = self.base_ring()
            fraction_field = ring.fraction_field()
            norm = fraction_field(root.q())

            def image(label):
                generator = self.module_generator(label)
                coefficient = ring(fraction_field(ring(2) * generator.b(root)) / norm)
                return generator - self.scalar_multiple(coefficient, root)

            return self.Aut()(image)

        def _eichler_transvection_column_matrix(self, isotropic, orthogonal):
            r"""Return the exact column matrix of the Eichler transvection ``t(e,a)``."""
            assert isotropic.parent() is self and orthogonal.parent() is self, (
                f"cannot form the Eichler transvection t(e, a) of {self!r} with e = {isotropic!r}, a = {orthogonal!r}: they lie in {isotropic.parent()!r} and {orthogonal.parent()!r}, not both in this lattice"
            )
            ring = self.base_ring()
            zero = ring.zero()
            assert isotropic.q() == zero, (
                f"cannot form the Eichler transvection t(e, a) of {self!r}: e = {isotropic!r} must be isotropic, but q(e) = {isotropic.q()}"
            )
            assert isotropic.b(orthogonal) == zero, (
                f"cannot form the Eichler transvection t(e, a) of {self!r}: a = {orthogonal!r} must lie in e^perp for e = {isotropic!r}, but b(e, a) = {isotropic.b(orthogonal)}"
            )
            fraction_field = ring.fraction_field()
            half_norm = fraction_field(orthogonal.q()) / fraction_field(ring(2))
            from sage.matrix.constructor import matrix

            from sage_extensions.categories.rings.ring_foundation import (
                _engine_element,
                _engine_ring,
                _owned_engine_element,
            )

            labels = tuple(self.module_generating_set())
            engine = _engine_ring(ring)
            isotropic_coordinates = tuple(
                _engine_element(ring, isotropic.to_vector()(label)) for label in labels
            )
            orthogonal_coordinates = tuple(
                _engine_element(ring, orthogonal.to_vector()(label)) for label in labels
            )
            gram = _engine_component_matrix(self.gram_tensor())
            pairings_with_isotropic = gram * matrix(
                engine, len(labels), 1, isotropic_coordinates
            )
            pairings_with_orthogonal = gram * matrix(
                engine, len(labels), 1, orthogonal_coordinates
            )
            columns = []
            for source_position, label in enumerate(labels):
                pairing_with_isotropic = _owned_engine_element(
                    ring, pairings_with_isotropic[source_position, 0]
                )
                pairing_with_orthogonal = _owned_engine_element(
                    ring, pairings_with_orthogonal[source_position, 0]
                )
                half_coefficient = half_norm * fraction_field(pairing_with_isotropic)
                assert half_coefficient in ring, (
                    f"the Eichler transvection t(e, a) with e = {isotropic!r}, a = {orthogonal!r} does not preserve {self!r}: q(a) b(e, {self.module_generator(label)})/2 = {half_coefficient} is not in {ring}"
                )
                integral_half_coefficient = ring(half_coefficient)
                columns.append(
                    tuple(
                        (
                            (ring.one() if target_position == source_position else zero)
                            - pairing_with_orthogonal
                            * _owned_engine_element(
                                ring, isotropic_coordinates[target_position]
                            )
                            + pairing_with_isotropic
                            * _owned_engine_element(
                                ring, orthogonal_coordinates[target_position]
                            )
                            - integral_half_coefficient
                            * _owned_engine_element(
                                ring, isotropic_coordinates[target_position]
                            )
                        )
                        for target_position in range(len(labels))
                    )
                )
            return matrix(
                engine,
                [
                    [
                        _engine_element(ring, columns[source_position][target_position])
                        for source_position in range(len(labels))
                    ]
                    for target_position in range(len(labels))
                ],
            )

        def eichler_transvection(self, isotropic, orthogonal):
            r"""Return the Eichler transvection \(t(e,a)\in O(L)\).

            For isotropic \(e\) and \(a\in e^\perp\),

            \[
            t(e,a)(x) = x - b(a,x)\,e + b(e,x)\,a - \tfrac12 q(a)\,b(e,x)\,e .
            \]

            It fixes \(e\) and acts trivially on \(e^\perp/e\), so it lies in
            the unipotent radical of the parabolic subgroup stabilizing
            \(\mathbb Z e\).  These transvections generate the stable
            orthogonal group and put vectors into normal form, which is how
            Eichler's criterion realizes its orbit equivalences.  The formula
            is transcribed at ``notes/topics/coble-enriques-lattice-theory/``
            ``reflective-two-elementary-lattices.md``, which attributes it to
            Dawes, section 2 equation (7).
            \(t(e,a)\) preserves \(L\) exactly when every coefficient
            \(\tfrac12 q(a)\,b(e,x)\) is integral, automatic on an even
            lattice and asserted otherwise.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: L = Lattices(ZZ)("U") + Lattices(ZZ)("A2")
                sage: e, f, a, _b = L.module_generators()
                sage: t = L.eichler_transvection(e, a)
                sage: t(e) == e and t(f) == f + a + e
                True
            """
            assert isotropic.parent() is self and orthogonal.parent() is self, (
                f"cannot form the Eichler transvection t(e, a) of {self!r} with e = {isotropic!r}, a = {orthogonal!r}: they lie in {isotropic.parent()!r} and {orthogonal.parent()!r}, not both in {self!r}"
            )
            assert isotropic.q() == self.base_ring().zero(), (
                f"cannot form the Eichler transvection t(e, a) of {self!r}: e = {isotropic!r} must be isotropic, but q(e) = {isotropic.q()}"
            )
            assert isotropic.b(orthogonal) == self.base_ring().zero(), (
                f"cannot form the Eichler transvection t(e, a) of {self!r}: a = {orthogonal!r} must lie in e^perp for e = {isotropic!r}, but b(e, a) = {isotropic.b(orthogonal)}"
            )
            return self.Aut()._isometry_from_column_matrix(
                self._eichler_transvection_column_matrix(isotropic, orthogonal)
            )

        def is_positive_definite(self) -> bool:
            signature = self.signature_pair()
            return (
                (signature.first() == self.module_rank()) is True
                and (signature.second() == cardinal(0)) is True
            )

        def is_negative_definite(self) -> bool:
            signature = self.signature_pair()
            return (
                (signature.first() == cardinal(0)) is True
                and (signature.second() == self.module_rank()) is True
            )

        def is_definite(self) -> bool:
            return self.is_positive_definite() or self.is_negative_definite()

        def definiteness(self):
            r"""Return the sign type of this finite-rank real quadratic lattice.

            The result is one of ``positive_definite``, ``negative_definite``,
            ``positive_semidefinite``, ``negative_semidefinite``, ``indefinite``
            or ``zero``. It is determined by the owned archimedean signature
            pair together with the rank, so the radical dimension is retained.
            """
            rank = int(self.module_rank())
            signature = self.signature_pair()
            positive = int(signature.first())
            negative = int(signature.second())
            zero = rank - positive - negative
            match (positive, negative, zero):
                case (0, 0, _):
                    return "zero"
                case (_, 0, 0):
                    return "positive_definite"
                case (0, _, 0):
                    return "negative_definite"
                case (_, 0, _):
                    return "positive_semidefinite"
                case (0, _, _):
                    return "negative_semidefinite"
                case _:
                    return "indefinite"

        def is_elliptic(self) -> bool:
            r"""Return whether this finite-rank lattice is negative definite.

            In the reflection-lattice convention used by the project, an
            elliptic form has signature ``(0,n,0)``.  The public signature pair
            records only the positive and negative indices, while the rank
            determines the radical dimension.
            """

            return self.is_negative_definite()

        def is_parabolic(self) -> bool:
            r"""Return whether the form has signature ``(0,n-1,1)``.

            Thus a parabolic lattice is negative semidefinite with a
            one-dimensional radical; negative-definite (elliptic) lattices are
            deliberately excluded.
            """

            rank = self.module_rank()
            if not rank.is_finite():
                return False
            finite_rank = int(rank.finite_value())
            if finite_rank < 2:
                return False
            signature = self.signature_pair()
            return (
                (signature.first() == cardinal(0)) is True
                and (signature.second() == cardinal(finite_rank - 1)) is True
            )

        def lll_reduction(self):
            return _lll_reduction(self)

        def LLL(self):
            r"""Return the same formed lattice in an LLL-reduced framing."""
            return self.lll_reduction().reduced

        def bkz_reduction(self, block_size=20):
            return _bkz_reduction(self, block_size=block_size)

        def BKZ(self, block_size=20):
            r"""Return the same formed lattice in a BKZ-reduced framing."""
            return self.bkz_reduction(block_size=block_size).reduced

        def hkz_reduction(self):
            return _hkz_reduction(self)

        def HKZ(self):
            r"""Return the full-block BKZ (HKZ) reframing."""
            return self.hkz_reduction().reduced

        @cached_method
        def minimum(self):
            r"""Return the nonzero square closest to zero for a definite ZZ-lattice.

            For a positive definite lattice this is its minimum. For a
            negative definite lattice this is minus the minimum of the
            negated form; the squares themselves have no lower bound.
            The zero lattice has no nonzero vector and raises ValueError.

            EXAMPLES::

                sage: c = ZZ(2)**34
                sage: L = Lattices(ZZ)([[2*c, -c], [-c, 2*c]])
                sage: assert L.minimum() == 2*c
                sage: N = Lattices(ZZ)([[-2*c, c], [c, -2*c]])
                sage: assert N.minimum() == -2*c
                sage: Lattices(ZZ)(0).minimum()
                Traceback (most recent call last):
                ...
                ValueError: the zero lattice has no nonzero vector and no minimum
            """
            return _minimum(self)

        def square_coordinate_bound(self, square: RingElement | int) -> RingElement:
            r"""Bound every integral coordinate of every vector of this square.

            For a definite ZZ-lattice of finite rank in its selected framing,
            return an integer ``b >= 0`` such that every vector ``v``
            with ``q(v) == square`` has all coordinates in ``[-b,b]``.
            Both signs of definiteness are allowed. A square of the wrong
            sign has no vectors and receives bound zero. The zero lattice
            also receives bound zero. A bound of zero is not an emptiness
            decision: the zero vector has square zero.

            If ``P`` is the positive definite choice of ``G`` or ``-G``
            and ``a`` the correspondingly signed square, Cauchy--Schwarz gives
            ``v_i^2 <= a*(P.inverse())[i,i]``. Exact rational inversion,
            flooring and integer square root evaluate the uniform bound.
            No floating-point eigenvalue or square-root estimate is used.
            The proof and the use for constrained embeddings are in
            ``docs/theory/hyperbolic-index.md``, "Definite targets: a
            bound containing every embedding".

            EXAMPLES::

                sage: L = Lattices(ZZ)([[2, 1], [1, 2]])
                sage: assert L.square_coordinate_bound(2) == ZZ(1)
                sage: assert L.square_coordinate_bound(-2) == ZZ(0)
                sage: assert L.square_coordinate_bound(0) == ZZ(0)
                sage: assert L.twist(ZZ(-1)).square_coordinate_bound(-2) == ZZ(1)
                sage: assert Lattices(ZZ)(0).square_coordinate_bound(1) == ZZ(0)
                sage: N = ZZ(10)^20
                sage: S = Lattices(ZZ)([[1, N], [N, N*N + 1]])
                sage: assert S.square_coordinate_bound(1) == N
                sage: e, f = S.module_generators()
                sage: assert S.q(f - N*e) == ZZ(1)
            """
            assert self.base_ring() is _owned_integers(), (
                "this square-coordinate bound is computed for integral lattices over ZZ"
            )
            assert self.module_rank().is_finite(), (
                "this square-coordinate bound requires a finite framing"
            )
            return _square_coordinate_bound(self, self.base_ring()(square))

        def elements_of_norm(self, value):
            r"""Return the full norm fibre, retaining finite integral enumeration.

            For definite integral lattices the existing finite square-shell
            computation supplies every point, so exhausting this fibre
            terminates, including at norm zero. Nonzero fibres of split
            nondegenerate binary integral forms also retain their complete
            finite divisor enumeration. Its inclusion still lands
            in this lattice. Other fibres use the general equalizer locus;
            no enumeration is inferred over an uncountable coefficient ring.

            EXAMPLES::

                sage: L = Lattices(ZZ)([[2, -1], [-1, 2]])
                sage: F = L.elements_of_norm(ZZ(0))
                sage: assert tuple(F) == (L.zero(),)
                sage: assert F.inclusion().codomain() is L
                sage: assert F.inclusion()(F.an_element()) == L.zero()
                sage: assert L.elements_of_norm(ZZ(2)).cardinality() == cardinal(6)
                sage: assert L.elements_of_norm(ZZ(1)).is_empty() is True
                sage: N = L.twist(ZZ(-1))
                sage: assert N.elements_of_norm(ZZ(-2)).cardinality() == cardinal(6)
                sage: assert N.elements_of_norm(ZZ(2)).is_empty() is True
                sage: U = Lattices(ZZ)("U")
                sage: assert U.elements_of_norm(ZZ(2)).cardinality() == cardinal(2)
                sage: assert U.elements_of_norm(ZZ(2)).inclusion().codomain() is U
                sage: Z = Lattices(ZZ)(0)
                sage: assert tuple(Z.elements_of_norm(ZZ(0))) == (Z.zero(),)
                sage: assert Z.elements_of_norm(ZZ(1)).is_empty() is True
            """
            value = self.value_module()(value)
            if (
                self.base_ring() is _owned_integers()
                and self.module_rank().is_finite()
                and (self.module_rank() == 0 or self.is_definite())
            ):
                return self.vectors_of_square(value).domain()
            if (
                self.base_ring() is _owned_integers()
                and self.module_rank() == 2
                and value != self.base_ring().zero()
            ):
                discriminant = lattice_engines._binary_form_discriminant(self)
                if discriminant > 0 and discriminant.is_square():
                    return self.vectors_of_square(value).domain()
            return self.square_fibre(value).object()

        @cached_method
        def vectors_of_square(self, square):
            r"""Return the complete square fibre with its lattice inclusion.

            Definite fibres over ``ZZ`` and nonzero split binary fibres are
            finite and enumerated. Other fibres retain the complete defining
            locus; the orbits of a nonsplit binary fibre under ``O(L)`` or
            ``SO(L)`` are :meth:`binary_fixed_norm_representatives`.  A definite
            fibre over another base ring is one of these (``STY-129``): over
            ``QQ`` the fibre of ``x^2 + y^2`` at ``1`` contains ``(3/5, 4/5)``,
            and it is not the finite shell of the integral span.
            Nonintegral bases return the general norm fibre directly;
            constructing that locus requires no definiteness decision.

            EXAMPLES::

                sage: from sage_extensions.categories.sets.set_categories import NN, Sets
                sage: a = Sets().Mor(NN, QQ)(lambda n: QQ(1)/QQ(2)**int(n))
                sage: z = RR.of_cauchy(a)
                sage: V = Lattices(RR)([[z]])
                sage: F = V.vectors_of_square(RR.zero())
                sage: assert F is V.elements_of_norm(RR.zero())
                sage: assert F.inclusion().codomain() is V
                sage: assert F.is_empty() is False
                sage: assert F.an_element() == V.zero()
            """
            square = self.base_ring()(square)
            if self.base_ring() is not _owned_integers():
                return self.square_fibre(square).object()
            if self.base_ring() is _owned_integers() and self.module_rank() == 0:
                from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

                return self.finite_subsets()(
                    finite_ordered_set((self.zero(),) if square == self.base_ring().zero() else ())
                )
            if not self.module_rank().is_finite():
                return self.square_fibre(square).object()
            if self.definiteness() in ("positive_definite", "negative_definite"):
                return self.finite_subsets()(_vectors_of_square(self, square))
            if (
                self.module_rank() == 2
                and square
                and _engine_ring(self.base_ring()) is SageZZ
            ):
                discriminant = lattice_engines._binary_form_discriminant(self)
                if discriminant > 0 and discriminant.is_square():
                    return self.finite_subsets()(
                        self._split_binary_square_fibre(square)
                    )
            return self.square_fibre(square).object()

        @cached_method
        def _split_binary_square_fibre(self, square):
            r"""Return the complete finite nonzero fibre of a split binary form."""
            from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

            return finite_ordered_set(
                lattice_engines._split_binary_vectors_of_square(self, square)
            )

        @cached_method
        def _split_binary_square_fibre_action(self, square, special=False):
            r"""Return the O(L)- or SO(L)-action on a complete split binary fibre."""
            from sage_extensions.categories.group.g_objects import GObjects
            from sage_extensions.categories.sets.set_categories import Sets

            orthogonal = self.orthogonal_group()
            acting_group = self.special_orthogonal_group() if special else orthogonal
            reversing_data = None
            reversing = None

            def reversing_isometry():
                nonlocal reversing_data, reversing
                if reversing_data is None:
                    reversing_data = lattice_engines._split_binary_orthogonal_group_generators(self)
                if reversing is None and len(reversing_data) == 2:
                    reversing = orthogonal(reversing_data[1])
                return reversing

            def same_orbit(left, right):
                if right == left or right == -left:
                    return True
                if special:
                    return False
                reflection = reversing_isometry()
                return reflection is not None and (
                    right == reflection(left) or right == -reflection(left)
                )

            return GObjects(acting_group, Sets()).on_set(
                self._split_binary_square_fibre(square),
                lambda isometry, vector: isometry(vector),
                orbit_relation=same_orbit,
            )

        @cached_method
        def vectors_of_square_and_divisibility(self, square, divisibility):
            return _vectors_of_square_and_divisibility(self, square, divisibility)

        @cached_method
        def roots(self):
            return _roots(self)

        @cached_method
        def roots_of_square(self, square):
            return _roots_of_square(self, square)

        @cached_method
        def possible_root_lengths(self):
            r"""Return the possible absolute self-pairings of reflective roots.

            Only the exponent of coker(L -> L dual) enters the bound.
            Its discriminant pairing is not needed for this computation.
            """
            assert self.module_rank().is_finite(), f"the root-length bound of {self} requires finite rank"
            assert self.determinant() != 0, f"the root-length bound of {self} requires a nondegenerate form"
            exponent = abs(self.correlation_morphism().cokernel().exponent())
            return finite_ordered_set(tuple((self.base_ring()(2) * exponent).divisors()))

        def reflective_root_locus(self):
            r"""Primitive nonisotropic vectors with integral reflections.

            The condition is ``2 b(v,L) / b(v,v)`` integral; the locus can
            be infinite for an indefinite lattice.
            """

            return self.condition_set(lambda vector: vector.is_root())

        @cached_method
        def root_module_generating_set(self):
            r"""Return a set of roots of \(L\) that generates \(L\) as a module.

            A semi-decision for \(L=\mathbb Z\Phi(L)\) on a lattice of any
            signature: PARI enumerates integer coordinates in increasing L1
            degree, so the search returns exactly
            when \(\Phi(L)\) generates \(L\) and runs without end otherwise.
            """
            from sage_extensions.categories.lattice_engines import (
                _roots_generating_lattice,
            )

            rows = _roots_generating_lattice(
                self.gram_tensor(), self.possible_root_lengths()
            )
            return finite_ordered_set(tuple(self(row) for row in rows))

        @cached_method
        def root_sublattice(self):
            return _root_sublattice(self)

        @cached_method
        def reflective_root_system_components(self):
            r"""Return the irreducible components of the reflective root system.

            Each component is a connected Coxeter diagram of simple roots in
            this lattice; its :meth:`label`, :meth:`root_scale` and
            :meth:`isomorphism_from_type_diagram` give its type, its scale and
            the order of its simple roots that the diagram of the type fixes.
            """
            return _reflective_root_system_components(self)

        @cached_method
        def norm_two_root_types(self) -> str:
            r"""Return the type of the root system \(\{v\in L : |b(v,v)| = 2\}\) of an even definite lattice over ``ZZ``.

            The value is the label of the type: each irreducible component is
            spelled by its letter and rank, and the components are joined by
            ``+``, ``E`` before ``D`` before ``A`` and decreasing rank within
            one letter, as ``E8+E8+A1`` and ``E7+D10``.  The empty root system
            is the empty sum ``""``.  No owned object presents the types of
            finite root systems, so the label is the answer, as for
            :meth:`root_system_type_name` of a root lattice.

            The norm-two vectors of an integral lattice generate a direct sum
            of root lattices (Witt's theorem, Conway--Sloane, *SPLAG*, Ch. 4,
            §3).  On an even lattice they are all its reflective roots of
            norm two; the reflective root system of
            :meth:`reflective_root_system_components` can also contain roots
            of norm four, which this type omits.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: (Lattices(ZZ)("E8") + Lattices(ZZ)("E8") + Lattices(ZZ)("A1")).norm_two_root_types()
                'E8+E8+A1'
            """
            assert self.base_ring() is _owned_integers(), (
                f"the norm-two root type of {self} is computed for lattices over ZZ, but {self} is a lattice over {self.base_ring()}"
            )
            assert self.module_rank().is_finite(), (
                f"the norm-two vectors of {self} form a finite root system only for a lattice of finite rank, but {self} has rank {self.module_rank()}"
            )
            assert self.is_definite(), (
                f"the norm-two vectors of {self} form a finite root system only when the lattice is definite, but {self} has signature {self.signature_pair()}"
            )
            assert self.is_even() is True, (
                f"the norm-two root type is stated for even lattices, but {self} is not known to be even: an odd lattice also has reflective roots of norm one"
            )
            return _norm_two_root_types(self)

        def reduction_cell(self, inequalities, *, equations=()):
            r"""Return the homogeneous rational cell ``{x : a(x) >= 0, e(x) = 0}`` in this lattice.

            The cell is a rational polyhedral cone.  Each rational wall, given
            by its coordinates in the dual framing, is stated by the primitive
            integral covector on its ray, which cuts out the same half-space.
            """
            from sage_extensions.categories.polyhedral_cones import (
                _engine_rational_coordinates,
                _integral_covector,
            )

            def covector(wall):
                return _integral_covector(self, _engine_rational_coordinates(wall))

            return self.rational_polyhedral_cone(
                tuple(covector(wall) for wall in inequalities),
                equation_covectors=tuple(covector(wall) for wall in equations),
            )

        def reduction_complex_exploration(
            self,
            cells,
            adjacencies,
            *,
            complete=False,
        ):
            r"""Return the selected finite exact reduction-complex exploration."""
            from sage_extensions.categories.reduction_complexes import (
                RationalReductionComplexExploration,
            )

            return RationalReductionComplexExploration(
                self,
                cells,
                adjacencies,
                complete=complete,
            )

        def lorentzian_reduction_complex(self, marked_vectors=None):
            r"""Return the completed Lorentzian perfect-domain traversal of this lattice."""
            from sage_extensions.categories.reduction_complexes import (
                _lorentzian_reduction_complex,
            )

            return _lorentzian_reduction_complex(self, marked_vectors=marked_vectors)

        def integral_structure(self, vectors: IndexedFamily):
            r"""The ``ZZ``-lattice spanned by a finite family of vectors of this ``QQ``-space, as ``L -> Res(V)``.

            This is the case ``ZZ`` in ``QQ``: ``V`` is over ``QQ`` and the lattice
            is a ``ZZ``-module.  ``Res`` restricts scalars along ``ZZ -> QQ``.  A
            finite sequence of vectors enters as the family over its positions
            (``finite_family``).  The lattice is the
            image of the module map from the free module on the family to
            ``Res(V)``, a subobject of one ``ZZ``-module, and its
            inclusion is the monomorphism on which
            ``IntegralStructureAction(G, inclusion)`` acts.  Repeated calls
            on one space land in the same ``Res(V)``, the image of ``V`` under
            the one restriction functor along ``ZZ -> QQ``, so two integral
            structures are compared as subobjects of one object.
            """
            integers = _owned_integers()
            field_map = integers.fraction_field_map()
            assert field_map.codomain() is self.base_ring(), (
                f"an integral structure of {self} is a ZZ-lattice in a QQ-space, but {self} is over "
                f"{self.base_ring()}, not QQ"
            )
            restricted = Modules(self.base_ring()).restriction_of_scalars(field_map)(self)
            family = finite_family(
                (restricted(self(vector)) for vector in vectors),
                name="Spanning family of an integral structure",
            )
            free = integers.free_module(family.index_set())
            span = free.module_category().Mor(free, restricted)(family.value)
            return span.image().inclusion()

        def vector_primitive_extension(self, element):
            r"""Return the primitive-extension/gluing datum cut out by ``element``."""

            return VectorPrimitiveExtension(self, element)

        def definite_complement_extensions(self, left, right):
            r"""Return all isometries ``g`` with ``g(left)=right`` in the definite-complement regime."""

            return _definite_complement_extensions(self, left, right)

        def binary_fixed_norm_representatives(self, square, acting_group=None):
            r"""Return the orbit set ``X/G`` of the square fibre ``X = q^{-1}(square)``.

            ``G`` is ``acting_group``, which is ``O(self)`` (the default) or
            ``SO(self)``; the ``SO(self)``-set is the restriction of the
            ``O(self)``-action along the inclusion ``SO(self) -> O(self)``.
            The lattice must be nondegenerate of rank two over ``ZZ``.
            The result is the orbit set with its projection ``X -> X/G`` and
            its section ``X/G -> X``, presented by a finite transversal.

            The orbit relation of the fibre is decided by the rank-one
            perpendicular extension: two vectors of equal content are in one
            ``O(self)``-orbit exactly when an isometry carries one primitive
            part to the other (``definite_complement_extensions``), and in one
            ``SO(self)``-orbit exactly when such an isometry has determinant
            one. The transversal is PARI's list of classes modulo ``SO(self)``
            for a nonsplit indefinite form (``qfbsolve`` flag 3, imprimitive
            classes included), merged by that relation, and the finite fibre
            otherwise. That the nonsplit fibre has finitely many orbits is
            Cassels, *Rational Quadratic Forms*, Ch. 9, Lemma 6.1. At square
            zero a split form has infinitely many content classes.

            EXAMPLES::

                sage: L = Lattices(ZZ)([[1, 0], [0, -2]])
                sage: orbits = L.binary_fixed_norm_representatives(1)
                sage: orbits.cardinality() == NN(1)
                True
                sage: all(orbits.section()(orbit).q() == ZZ(1) for orbit in orbits)
                True
                sage: L.binary_fixed_norm_representatives(3).cardinality() == NN(0)
                True
            """
            from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

            square = self.base_ring()(square)
            orthogonal = self.orthogonal_group()
            special = self.special_orthogonal_group()
            group = orthogonal if acting_group is None else acting_group
            restricted = group is special
            assert restricted or group is orthogonal, (
                f"the orbits of the square fibre of {self} are computed under O(L) or SO(L), "
                f"but {group} is neither"
            )
            discriminant = lattice_engines._binary_form_discriminant(self)
            if not discriminant:
                raise ValueError(
                    "binary orbit representatives require a nondegenerate form"
                )
            if discriminant > 0 and not discriminant.is_square():
                candidates = finite_ordered_set(
                    lattice_engines._binary_special_orthogonal_representatives(self, square)
                )
            elif not square and discriminant > 0:
                raise ValueError(
                    "the split zero-square fibre has infinitely many orthogonal orbits"
                )
            else:
                if discriminant > 0:
                    candidates = self._split_binary_square_fibre(square)
                    # For a split binary lattice, SO(L) = {+-1} and O(L) is
                    # generated by negation and, when it exists, one reversing
                    # isometry.  Use that theorem as the exact orbit decision;
                    # ``vectors_of_square`` is the complete finite fibre here,
                    # so its domain is the action's actual point set.  Building
                    # a second equalizer presentation of that same fibre would
                    # eagerly reconstruct the form and its value module.
                    action = self._split_binary_square_fibre_action(
                        square,
                        special=restricted,
                    )
                    return action.orbits_presented_by(candidates)

                # Definite fibres use their actual finite group action.
                from sage_extensions.categories.group.g_sets import FiniteGSets

                candidates = self.vectors_of_square(square)
                action = FiniteGSets(group)(candidates.domain(), lambda isometry, point: isometry(point))
                return action.orbits_presented_by(candidates.domain())

            def same_orbit(left, right, *, special_only):
                if left == right:
                    return True
                if left.content() != right.content():
                    return False
                if not square:
                    return False
                extensions = self.definite_complement_extensions(
                    left.primitive_part(), right.primitive_part()
                )
                if special_only:
                    return any(extension.determinant() == 1 for extension in extensions)
                return bool(extensions)

            action = self.square_fibre_action(
                square, orbit_relation=lambda left, right: same_orbit(left, right, special_only=False)
            )
            if restricted:
                action = action.restrict_action(
                    special.inclusion(),
                    orbit_relation=lambda left, right: same_orbit(left, right, special_only=True),
                )
            return action.orbits_presented_by(candidates)

        def reduction_cycle(self, bound, start):
            r"""Return the binary period automorph and bounded vectors, or ``None``.

            Start at the specified primitive positive vector. The private
            edgewalk realization follows the frozen cycle contract. The
            period is a lattice isometry; its vector family is a finite
            subset with its inclusion into this lattice.

            EXAMPLES::

                sage: for gram, size in (([[2, 0], [0, -6]], 1), ([[4, 2], [2, -2]], 1), ([[2, 0], [0, -4]], 2)):
                ....:     L = Lattices(ZZ)(gram)
                ....:     period, vectors = L.reduction_cycle(ZZ(4), L.basis_vector(0))
                ....:     assert period.inverse() * period == L.Isom(L).identity()
                ....:     assert vectors.cardinality() == size
                ....:     assert all(v.parent() is L and ZZ(0) < v.q() <= ZZ(4) for v in vectors)
                sage: L = Lattices(ZZ)([[2, 0], [0, -6]])
                sage: period, vectors = L.reduction_cycle(ZZ(4), L.basis_vector(0))
                sage: labels = tuple(L.module_generating_set())
                sage: tuple(tuple(int(period(v).to_vector()(label)) for label in labels) for v in L.module_generators())
                ((2, 1), (3, 2))
                sage: tuple(tuple(int(v.to_vector()(label)) for label in labels) for v in vectors)
                ((2, 1),)
            """
            result = lattice_engines._binary_reduction_cycle(self, bound, start)
            if result is None:
                return None
            automorphism, vectors = result
            values = Sets().product((self.Isom(self), self.finite_subsets()))
            return values((automorphism, self.finite_subsets()(vectors)))

        def gluing_route_discriminant_classes(self, left, right):
            r"""Return admissible ``O(A_L)`` classes from the primitive-extension gluing route."""

            return _gluing_route_discriminant_classes(self, left, right)

        def stable_complement_root_reflections(self, element):
            r"""Return stable reflections in root-orbit representatives of ``element^perp``."""

            return _stable_complement_root_reflections(self, element)

        @cached_method
        def primitive_isotropic_subobject(self, *basis):
            r"""Return the primitive totally isotropic sublattice spanned by ``basis``.

            Admission checks saturation and vanishing of the restricted form
            before refining the represented subobject, so a refused span leaves
            no wrongly placed object behind.  The stated family must also be
            nonempty and independent.  One subobject per spanning family, so
            its cached isotropic reduction (and parabolic) is shared.
            """
            from sage_extensions.categories.isotropic_parabolics import (
                PrimitiveIsotropicSubobjects,
            )

            elements = tuple(
                element if element_parent(element) is self else self(element)
                for element in basis
            )
            assert elements, (
                f"cannot form a primitive isotropic sublattice of {self!r} from the empty family: a primitive isotropic sublattice is spanned by a nonempty family of vectors"
            )
            subobject = self.subobject_on(elements)
            assert subobject.is_primitive(), (
                f"the span of {elements!r} in {self!r} is not primitive: its inclusion has a "
                f"cokernel with torsion, so it is not a primitive isotropic sublattice; saturate it first"
            )
            zero = self.base_ring().zero()
            embedded = subobject.embedded_module_generators()
            labels = subobject.module_generating_set()
            assert all(
                self.b(embedded[left], embedded[right]) == zero
                for left in labels
                for right in labels
            ), (
                f"the span of {elements!r} in {self!r} is not totally isotropic: b(x, y) is nonzero for some pair of these vectors"
            )
            subobject = refine(
                subobject,
                PrimitiveIsotropicSubobjects(self.base_ring()),
            )
            assert (
                subobject.module_rank() == finite_ordered_set(elements).cardinality()
            ), (
                f"the vectors {elements!r} in {self!r} are linearly dependent: they span a sublattice of rank {subobject.module_rank()}, so they are not a basis of it"
            )
            return subobject

        def covering_discriminant_classes(self, square):
            r"""Return discriminant classes covering primitive vectors of ``square``.

            For a primitive ``v`` write ``d = div(v)``.  Then ``v/d`` lies in
            ``L^#`` and ``x = [v/d]`` lies in ``A_L`` with additive order
            exactly ``d``: a smaller order ``e`` would put ``(e/d)v`` in
            ``L`` and contradict primitivity.  The discriminant quadratic form
            satisfies ``q_{A_L}(x) = q(v)/d^2``.  Thus the classes satisfying

            ``q_{A_L}(x) = square / ord(x)^2``

            form a finite covering list for primitive vectors of that square,
            computed by one pass over the finite discriminant group.  Under
            Eichler's criterion each class carries at most one stable orbit;
            whether a covering class is attained is a separate question.
            """
            from sage.matrix.constructor import matrix as sage_matrix
            from sage.modules.free_module_element import vector as sage_vector
            from sage.rings.rational_field import QQ as SageQQ

            discriminant = self.discriminant_group()
            values = discriminant.quadratic_value_module()
            bilinear_values = discriminant.bilinear_value_module()
            field = self.base_ring().fraction_field()
            target = field(square)
            unformed = discriminant.unformed_module()
            engine = unformed._smith_engine()
            assert engine is not None, (
                f"the covering discriminant classes of {self} cannot be enumerated: the Smith normal form of {discriminant} is not available"
            )

            generators = tuple(discriminant.module_generators())
            gram = sage_matrix(SageQQ, len(generators), len(generators))
            for left_position, left in enumerate(generators):
                gram[left_position, left_position] = SageQQ(
                    _engine_element(field, values.lift(discriminant.q(left)))
                )
                for right_position in range(left_position):
                    pairing = discriminant.b(left, generators[right_position])
                    representative = SageQQ(
                        _engine_element(field, bilinear_values.lift(pairing))
                    )
                    gram[left_position, right_position] = representative
                    gram[right_position, left_position] = representative

            targets_by_order = {}
            matches = []
            for position in range(int(engine.cardinality())):
                engine_element = engine[position]
                order = int(engine_element.additive_order())
                target_value = targets_by_order.get(order)
                if target_value is None:
                    target_value = values(target / field(order) ** 2)
                    targets_by_order[order] = target_value
                coordinates = sage_vector(SageQQ, tuple(engine_element.lift()))
                raw_value = (coordinates * gram * coordinates.column())[0]
                value = values(_owned_engine_element(field, raw_value))
                if value == target_value:
                    matches.append(
                        discriminant._element_from_unformed_module(
                            unformed._from_smith_engine_element(engine_element)
                        )
                    )
            return finite_ordered_set(tuple(matches))

        def hyperbolic_plane_summand_count(self):
            r"""Return the number of represented indecomposable hyperbolic-plane summands."""
            plane = Lattices(self.base_ring())("U")
            return sum(
                1
                for summand in self.indecomposable_summands()
                if summand.is_isometric(plane)
            )

        def splits_two_hyperbolic_planes(self) -> bool:
            r"""Return whether the represented decomposition splits at least two copies of ``U``.

            This reads the selected decomposition.  A Gram-matrix presentation
            with no represented decomposition therefore answers ``False`` even
            when the abstract lattice is isometric to one splitting ``U + U``.
            """
            if not self.is_decomposable():
                return False
            return self.hyperbolic_plane_summand_count() >= 2

        def eichler_criterion_applies(self) -> bool:
            r"""Return whether Eichler's criterion classifies primitive-vector orbits here."""
            return bool(self.is_even()) and self.splits_two_hyperbolic_planes()

        def are_in_one_stable_orbit(self, left, right) -> bool:
            r"""Decide whether two primitive vectors share one ``ker(rho_L)`` orbit.

            Eichler's criterion says that, for an even lattice splitting two
            hyperbolic planes, square, divisibility, and divided discriminant
            class are a complete invariant of a primitive-vector orbit.  Both
            vectors are therefore required to be primitive and to belong to
            this represented lattice.
            """
            assert left.parent() is self and right.parent() is self, (
                f"cannot compare the orbits of {left!r} and {right!r} in {self!r}: they lie in {left.parent()!r} and {right.parent()!r}, not both in this lattice"
            )
            assert self.eichler_criterion_applies(), (
                f"cannot decide the orbits of {left!r} and {right!r} under ker(O(L) -> O(A_L)) "
                f"by Eichler's criterion: the criterion needs an even lattice with a given "
                f"orthogonal decomposition containing two copies of U, and {self!r} is odd or has "
                f"no such decomposition"
            )
            for vector in (left, right):
                assert self.subobject_on((vector,)).is_primitive(), (
                    f"cannot apply Eichler's criterion to {vector!r} in {self!r}: the criterion classifies primitive vectors, and this vector is not primitive"
                )
            return (
                left.q() == right.q()
                and left.div() == right.div()
                and left.divided_discriminant_class()
                == right.divided_discriminant_class()
            )

        @cached_method
        def primitive_isotropic_vectors(self):
            r"""Return the exact locus of nonzero primitive isotropic vectors.

            Membership is ``q(v) = 0`` together with saturation of ``Z v``:
            the vector is not a proper multiple of another lattice vector.
            A nondegenerate binary form has at most two rational null lines;
            each supplies its two primitive generators. Higher-rank loci
            retain their exact membership predicate.
            """
            if (
                self.module_rank() == 2
                and self.is_nondegenerate()
                and _engine_ring(self.base_ring()) is SageZZ
            ):
                return self.finite_subsets()(
                    lattice_engines._binary_primitive_isotropic_vectors(self)
                )
            zero = self.zero()
            value_zero = self.base_ring().zero()

            def is_primitive_isotropic(vector) -> bool:
                if vector == zero:
                    return False
                if self.q(vector) != value_zero:
                    return False
                return bool(self.subobject_on((vector,)).is_primitive())

            return self.condition_set(is_primitive_isotropic)

        def cusps(self, rank=1):
            r"""Return the ``O(L)``-orbits of primitive isotropic rank-``rank`` subobjects.

            The finite ordered result retains each representative, its
            parabolic subgroup and stabilizer generators, and transporter
            witnesses for membership.  Rank one gives zero-dimensional cusps;
            rank two gives one-dimensional cusps.
            """
            return self.Aut().cusps(rank)

        def tits_building_incidence(self):
            r"""Return finite line/plane incidence in the ``O(L)`` quotient building.

            Rank-two flag representatives come from the exact indefinite
            flag computation with its selected flag.  Their two terms determine unique
            line and plane cusp orbits.  Each record retains the actual nested
            embeddings, transporters to the selected cusp representatives, and
            exact flag stabilizer generators.
            """
            return self.Aut().tits_building_incidence()

        def primitive_isotropic_sublattices(self, rank=1):
            r"""Return primitive totally isotropic rank-``rank`` subobjects of this lattice."""
            return _primitive_isotropic_sublattice_locus(self, rank)

        def vector_locus(self, norm, primitive=False):
            r"""Return vectors of square ``norm``, optionally restricted to primitive vectors."""
            selected_norm = self.base_ring()(norm)
            return self.condition_set(
                lambda vector: (
                    vector.q() == selected_norm
                    and (not primitive or vector.is_primitive())
                )
            )

        def isotropic_sublattice_locus(self, rank):
            r"""Return represented totally isotropic rank-``rank`` sublattices."""
            return _isotropic_sublattice_locus(self, rank)

        def isotropic_flag_locus(self, ranks):
            r"""Return nested represented isotropic sublattices with the stated ranks."""
            return _isotropic_flag_locus(self, ranks)

        def isotropic_flag(self, *basis):
            return IsotropicFlag(self, basis)

        def isotropic_line_orbit_representatives(self):
            return self.O().isotropic_orbit_representatives(1)

        def isotropic_plane_orbit_representatives(self):
            return self.O().isotropic_orbit_representatives(2)

        def isotropic_flag_orbit_representatives(self, rank=2):
            return self.O().isotropic_orbit_representatives(rank, flag=True)

        @cached_method
        def shortest_vectors(self):
            return _shortest_vectors(self)

        def theta_series(self, precision=20, variable="q"):
            return _theta_series(self, precision=precision, variable=variable)

        def theta_series_cuspidal_component(self, precision=20, variable="q"):
            r"""Return ``theta_L - theta_gen(L)``, the cuspidal component of the theta series of this definite integral lattice.

            By the Siegel--Weil formula the genus theta series is the
            Eisenstein component of ``theta_L``, so the difference is a cusp
            form; it is zero when the genus has one class.
            """
            genus_series = self.genus().theta_series(
                precision=precision, variable=variable
            )
            return (
                genus_series.parent()(
                    self.theta_series(precision=precision, variable=variable)
                )
                - genus_series
            )

        def is_regular(self, *, max_value=None):
            r"""Return whether this definite lattice represents every value its genus represents.

            A definite lattice is regular when it represents every value
            \(b(x,x)\) that some lattice of its genus represents.  A genus of
            one class holds only this lattice, so the lattice is regular.
            Otherwise the search compares theta series with those of the
            classes of the genus and answers ``False`` at the first value one
            of them represents and this lattice does not.  Without
            ``max_value`` it does not return on a regular lattice of class
            number above one, and a search that ``max_value`` stopped answers
            the proposition.
            """
            match int(self.genus_class_number()):
                case 1:
                    return True
                case _:
                    return _first_unrepresented_value(
                        self, self.genus().representatives(), max_value, "is_regular"
                    )

        def is_spinor_regular(self, *, max_value=None):
            r"""Return whether this definite lattice represents every value its spinor genus represents.

            The procedure of :meth:`is_regular` over the classes of the spinor
            genus of this lattice, which come first among the representatives
            of its genus: a spinor genus of one class answers ``True``.
            """
            count = int(self.spinor_genus_class_numbers()[0])
            match count:
                case 1:
                    return True
                case _:
                    classes = tuple(self.genus().representatives())[:count]
                    return _first_unrepresented_value(
                        self, classes, max_value, "is_spinor_regular"
                    )

        def is_modular(self, scale):
            r"""Return whether this lattice is isometric to \(L^*(k)\) for ``scale`` \(k\).

            \(L^*(k)\) is the dual lattice with its form multiplied by \(k\).
            Its determinant is \(k^n/\det L\) in rank \(n\), and it is integral
            exactly when its Gram tensor is, so a scale with \(k^n\ne(\det L)^2\)
            or a nonintegral \(L^*(k)\) answers ``False`` before the isometry
            question is asked.
            """
            ring = self.base_ring()
            rank = int(self.module_rank())
            determinant = self.determinant()
            match ring(scale) ** rank == determinant**2:
                case False:
                    return False
            twisted = self.dual_lattice().twist(scale)
            gram = twisted.gram_tensor()
            match all(
                gram[row, column] in ring
                for row in range(rank)
                for column in range(rank)
            ):
                case False:
                    return False
            return self.is_isometric(Lattices(ring)(twisted))

        def modular_scale(self):
            r"""Return the positive \(k\) with \(L\cong L^*(k)\), or ``None`` when there is none.

            \(L\cong L^*(k)\) forces \(k^n=(\det L)^2\) in rank \(n\), so at most one
            positive \(k\) is a candidate, and :meth:`is_modular` decides it.
            """
            square = self.determinant() ** 2
            rank = int(self.module_rank())
            scale = next((k for k in square.divisors() if k**rank == square), None)
            match scale is not None and self.is_modular(scale):
                case True:
                    return scale
            return None

        def hermite_invariant(self):
            return _hermite_invariant(self)

        def successive_minima(self):
            return _successive_minima(self)

        def gaussian_heuristic(self, *, exact_form=False):
            return _gaussian_heuristic(self, exact_form=exact_form)

        def hadamard_ratio(self):
            return _hadamard_ratio(self)

        def closest_vector(self, target):
            return _closest_vector(self, target)

        @cached_method
        def _exact_cvp_engine(self):
            return _exact_cvp_engine(self)

        def _has_close_vector(self, target, square_bound) -> bool:
            return self._exact_cvp_engine().has_close_vector(target, square_bound)

        def close_vectors(self, target, square_bound):
            r"""Return the lattice vectors within the stated quadratic bound of ``target``."""
            return _close_vectors(self, target, square_bound)

        @cached_method
        def affine_line_fibre(self, base, direction):
            r"""Retain all rational parameters whose affine-line point belongs to this lattice.

            The base lies in this lattice's rational span, or in the rational
            span of one of its retained ambient lattices. The fibre retains
            its evaluation into this lattice and its affine image. These
            distinguish a constant parameterization from its singleton image.
            """
            ring = self.base_ring()
            field_map = ring.fraction_field_map()
            field = field_map.codomain()
            ambient = self
            inclusion = Modules(ring).Mor(self, self).identity()
            while base.parent() is not ambient.base_change(field_map):
                if ambient not in ModuleSubobjects(ring):
                    raise ValueError(
                        "the affine base must belong to a retained ambient rational span"
                    )
                next_inclusion = ambient.inclusion()
                inclusion = (
                    Modules(ring).Mor(ambient, next_inclusion.codomain())(
                        next_inclusion
                    )
                    * inclusion
                )
                ambient = next_inclusion.codomain()
            rational = ambient.base_change(field_map)
            if direction.parent() is ambient:
                direction = (
                    ModulesOverIntegralDomains(ring)(ambient)
                    .generic_fibre_map()(direction)
                    .underlying_element()
                )
            direction = rational(direction)
            scalars = field.regular_module()
            linear = Modules(field).Mor(scalars, rational)(lambda label: direction)
            integral_inclusion = (
                ModulesOverIntegralDomains(ring)(ambient).generic_fibre_map()
                * inclusion
            )
            return linear.affine_inverse_image(integral_inclusion, offset=base)

        def affine_line_points(self, base, direction):
            r"""Return ``(p,s)`` presenting the integral points ``p + ZZ*s``, or ``None``.

            The full affine image and its maps are retained by
            ``affine_line_fibre(base,direction)``. The generator ``s`` is
            primitive in the intersection with the line. A constant line
            has ``s=0`` when its point is integral and is empty otherwise.

            EXAMPLES::

                sage: L = Lattices(ZZ)("U")
                sage: V = L.vector_space()
                sage: point, step = L.affine_line_points(V.zero(), V.zero())
                sage: point == L.zero() and step == L.zero()
                True
                sage: L.affine_line_fibre(V.zero(), V.zero()).image_point_set().cardinality() == 1
                True
            """
            if self.base_ring() is not _owned_integers():
                raise TypeError("an integral affine-line presentation requires ZZ")
            fibre = self.affine_line_fibre(base, direction)
            try:
                point = fibre.evaluation()(fibre.base_point())
            except ValueError:
                return None
            translations = fibre.image_translation_module()
            if translations.module_rank() == 0:
                step = self.zero()
            else:
                if translations.module_rank() != 1:
                    raise ArithmeticError(
                        "the intersection of a rational line with a lattice must have rank at most one"
                    )
                step = translations.inclusion()(
                    next(iter(translations.module_generators()))
                )
            return Sets().product((self, self))((point, step))

        def first_close_vector_shell(self, target, square_bound, max_multiplier):
            r"""Return the first nonempty scaled shell with ``1 <= m <= M``.

            The shell consists of ``x`` with ``q(x-m*target)`` between zero
            and ``m^2*square_bound``. The bound has the sign of the definite
            form (or is zero). Return ``None`` when the bounded family is
            empty. A nonempty result is an element of
            ``NN x self.finite_subsets()``; its subset retains its inclusion.

            EXAMPLES::

                sage: L = Lattices(ZZ)([[2]])
                sage: V = L.vector_space()
                sage: label = next(iter(V.module_generating_set()))
                sage: t = V.scalar_multiple(QQ(1)/QQ(2), V.module_generator(label))
                sage: L.first_close_vector_shell(t, QQ(0), NN(1)) is None
                True
                sage: m, shell = L.first_close_vector_shell(t, QQ(0), NN(2))
                sage: m == NN(2) and shell.domain() == Set((L.basis_vector(0),))
                True
            """
            from sage_indefinite_port.indefinite.scaled_shells import first_scaled_shell

            return first_scaled_shell(
                self, target, square_bound, max_multiplier
            )

        def scaled_close_vector_shells(self, target, square_bound, max_multiplier):
            r"""The bounded family ``m |-> close_vectors(m*t,m^2*b)``.

            Its positive integer index is the multiplier. Each value is
            the finite distance family on the whole signed sublevel shell;
            its boundary consists of points whose value is exactly ``m^2*b``.
            """
            maximum = NN(max_multiplier)
            ambient = self.vector_space()
            if target.parent() is self:
                target = (
                    ModulesOverIntegralDomains(self.base_ring())(self)
                    .generic_fibre_map()(target)
                    .underlying_element()
                )
            if target.parent() is not ambient:
                raise ValueError(
                    "the affine target must belong to the lattice or its rational span"
                )
            field = ambient.base_ring()
            bound = field(square_bound)
            sign_type = self.definiteness()
            if sign_type not in ("positive_definite", "negative_definite"):
                raise ValueError("close-vector shells require a definite form")
            if (sign_type == "positive_definite" and bound < 0) or (
                sign_type == "negative_definite" and bound > 0
            ):
                raise ValueError(
                    "the shell bound must have the sign of the definite form"
                )
            indices = FiniteOrderedSets().from_indexed(
                Sets.Δ[int(maximum) - 1],
                lambda index: NN(int(index) + 1),
                name="Positive multipliers up to the bound",
            )
            return indexed_family(
                indices,
                lambda m: self.close_vectors(
                    ambient.scalar_multiple(field(int(m)), target),
                    field(int(m) ** 2) * bound,
                ),
                name="Scaled affine close-vector shells",
            )

        def first_close_vector_sphere(self, target, square_bound, max_multiplier):
            r"""Return the first nonempty scaled sphere with ``1 <= m <= M``.

            Use the same scaled family as :meth:`first_close_vector_shell`,
            with equality ``q(x-m*target) = m^2*square_bound``. Return
            ``None`` if no sphere in the bounded family contains a vector.

            EXAMPLES::

                sage: L = Lattices(ZZ)([[-2]])
                sage: m, sphere = L.first_close_vector_sphere(L.zero(), QQ(-2), NN(1))
                sage: m == NN(1) and sphere.domain() == Set((L.basis_vector(0), -L.basis_vector(0)))
                True
            """
            from sage_indefinite_port.indefinite.scaled_shells import first_scaled_shell

            return first_scaled_shell(
                self, target, square_bound, max_multiplier, exact_distance=True
            )

        def babai(self, target):
            return _babai(self, target)

        approximate_closest_vector = babai

        def voronoi_cell(self, bound=None):
            r"""Return the Voronoi cell of this definite lattice, a convex polytope in ``L tensor QQ``."""
            return _voronoi_cell(self, bound=bound)

        def voronoi_facets(self):
            r"""Return the facets of the Voronoi cell, indexed by their relevant vectors."""
            return _voronoi_facets(self)

        def voronoi_relevant_vectors(self):
            r"""Return the Voronoi-relevant vectors, the normals of the facets of the cell."""
            return _voronoi_relevant_vectors(self)

        def contact_polytope(self):
            return _contact_polytope(self)

        def packing_radius(self):
            return _packing_radius(self)

        def covering_radius(self):
            return _covering_radius(self)

        def center_density(self):
            return _center_density(self)

        def packing_density(self):
            return _packing_density(self)

        def kissing_number(self):
            return _kissing_number(self)

        def twist(self, scalar):
            r"""Keep the module and rescale its form by ``scalar``.

            The result is the same free module with
            \(b'(x,y)=\mathrm{scalar}\cdot b(x,y)\).  The Gram is
            scaled as a type-$(0,2)$ tensor: a pairing rule is not
            materialized as a finite array.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: Iinf = Lattices(ZZ)(ZZ^NN)
                sage: Iinf.basis_vector(0)^2
                1
                sage: Iinf.twist(2).basis_vector(0)^2
                2
                sage: latex(Iinf.twist(2).gram_tensor())
                2\,I_{\infty}
                sage: Iinf.twist(2).gram_tensor()
                2 I_∞ ∈ (ZZ^NN ⊗ ZZ^NN)*
            """

            from sage_extensions.categories.modules.framed.formed.form_modules import (
                FormValueScalings,
            )

            return FormValueScalings(self.base_ring())(self, scalar)

        def __matmul__(self, other):
            r"""Return the tensor product lattice ``self \otimes other``."""
            category = Lattices(self.base_ring())
            match other in category:
                case True:
                    return category.tensor_product((self, other))
                case False:
                    return NotImplemented

        def __add__(self, other):
            r"""Return the orthogonal direct sum of the two summands.

            The two-index case of ``Lattices(R).orthogonal_sum``, in the
            concatenated basis.  Being binary, ``L + M + N`` is a
            two-summand sum whose first summand is a sum; the sum of three
            summands over a three-element index set is
            ``Lattices(R).orthogonal_sum([L, M, N])``.  Infinite \(\oplus\)
            infinite is not constructed.  ``sum([...])`` uses ``0 + L``.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: Lattices(ZZ)("U") + Lattices(ZZ)(ZZ^NN)
                Integral lattice of rank +Infinity and signature (+Infinity, 1)
            """
            if other == 0:
                return self

            category = Lattices(self.base_ring())
            assert other in category
            return category.orthogonal_sum((self, other))

        def __radd__(self, other):
            if other == 0:
                return self
            return NotImplemented

        def __pow__(self, exponent):
            r"""Return \(L^{\oplus n}\), the \(n\)-fold orthogonal direct sum.

            It is the biproduct of the constant family over \(\Delta[n-1]\),
            so \(L^{\oplus 3}\) has three summands, one per index.  ``L ** 0``
            is the empty sum: the zero lattice, the unit of ``+``.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: (Lattices(ZZ)("U") ** 3).signature_pair()
                (3, 3)
            """
            count = int(exponent)
            assert count >= 0, (
                f"cannot form the orthogonal power {self!r}^{count}: the exponent of an orthogonal power L^n is a natural number n >= 0"
            )
            category = Lattices(self.base_ring())
            if count == 0:
                return category(0)
            return category.orthogonal_sum(
                indexed_family(
                    Sets.Δ[count - 1],
                    lambda _position: self,
                    name=f"Orthogonal power summands of {self}",
                )
            )

        def _repr_(self):
            r"""Name the lattice by rank and, over \(\mathbb{Q}\), signature.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: Lattices(ZZ)("U")
                Integral lattice of rank 2 and signature (1, 1)
            """
            from sage.rings.integer_ring import ZZ
            from sage.rings.rational_field import QQ

            kind = (
                "Integral lattice"
                if _engine_ring(self.base_ring()) is ZZ
                else "Lattice"
            )
            rank = self.module_rank()
            if _engine_ring(self.base_ring().fraction_field()) is QQ:
                _signature = _signature_pair_of_gram(self.gram_tensor())
                if _signature is not None:
                    pos, neg = _signature.first(), _signature.second()
                    return f"{kind} of rank {rank} and signature ({pos}, {neg})"
            return f"{kind} of rank {rank} over {self.base_ring()}"

        def _latex_(self):
            r"""Display $L$ with its invariants; the Gram is $G_L$, not $L$.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: latex(Lattices(ZZ)("U"))
                \begin{gathered}
                L \in \mathrm{Lattices}(\mathbb{Z}), \quad \mathrm{rk}(L) = 2, \quad \mathrm{sig}(L) = (1, 1), \quad \mathrm{disc}(L) = 1 \\
                L = U \\
                G_L = \left(\begin{array}{rr}
                \cdot & 1 \\
                1 & \cdot
                \end{array}\right) \\
                \end{gathered}
            """

            _name, tex = _ring_notation(self.base_ring())
            return _lattice_latex(self, tex)

    class ElementMethods:
        r"""Operations generic to every lattice element.

        The pairing ``v.b(w)`` and the norm ``v.q()`` are the form module's;
        this level adds the lattice notation and the lattice invariants of a
        vector.
        """

        if TYPE_CHECKING:

            def __add__(
                self,
                other: Lattices.ElementMethods,
            ) -> Lattices.ElementMethods: ...
            def __sub__(
                self,
                other: Lattices.ElementMethods,
            ) -> Lattices.ElementMethods: ...

        def _lattice_terms(self):
            r"""The nonzero coefficients of this vector, in the order of the framing's enumeration."""
            ranking = self.parent().module_generating_set().ranking_map()
            coordinates = self.to_vector()
            return sorted(
                coordinates.parent()._selected_module_coefficients(coordinates).items(),
                key=lambda term: int(ranking(term[0])),
            )

        def _repr_(self):
            r"""Print the vector as a linear combination of the generator labels.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: Lattices(ZZ)("U").basis_vector(0)
                e_0
            """
            return repr_lincomb(
                [(f"e_{label}", coefficient) for label, coefficient in self._lattice_terms()],
                strip_one=True,
            )

        def _latex_(self):
            return repr_lincomb(
                [(f"e_{{{label}}}", coefficient) for label, coefficient in self._lattice_terms()],
                is_latex=True,
                strip_one=True,
            )

        def __mul__(self, other):
            r"""``v * w`` is \(b(v,w)\) for a vector of this lattice, and ``v * r`` the scalar multiple for ``r`` in the base ring.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: I2 = Lattices(ZZ)(ZZ^2)
                sage: e, f = I2.basis_vector(0), I2.basis_vector(1)
                sage: e.b(f), e*e
                (0, 1)
            """
            parent = self.parent()
            match element_parent(other) is parent:
                case True:
                    return parent.b(self, other)
            match other in parent.base_ring():
                case True:
                    return parent.scalar_multiple(other, self)
            return NotImplemented

        def __pow__(self, exponent):
            r"""``v^2`` is \(q(v)\)."""
            assert exponent == 2, (
                f"{self!r}^{exponent} is not defined: on a lattice vector only v^2 = q(v) is defined"
            )
            return self.q()

        __xor__ = __pow__

        def norm(self):
            r"""Return the form norm ``b(v,v)``."""
            return self.q()

        def divisibility_ideal(self):
            return self.parent().divisibility_ideal(self)

        def div(self):
            r"""Return the positive integer generator of ``b(v,L)`` over ``ZZ``.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: Lattices(ZZ)(ZZ^NN).basis_vector(0).div()
                1
            """
            return self.parent().div(self)

        def divisor(self):
            r"""Return the positive generator of ``b(v,L)`` over ``ZZ``."""
            return self.div()

        def bezout_partner(self) -> Lattices.ElementMethods:
            r"""Return an integral ``h`` with ``b(self,h) = self.div()``.

            Lift the positive generator of the image of ``b(self,-)``
            through that module morphism. The module-map image factorization
            owns the lift. For a radical vector the selected partner is zero.

            EXAMPLES::

                sage: L = Lattices(ZZ)([[0, 6], [6, 0]])
                sage: v = L.linear_combination({0: ZZ(2), 1: ZZ(3)})
                sage: h = v.bezout_partner()
                sage: h.parent() is L and v.b(h) == ZZ(6)
                True
                sage: L.zero().bezout_partner() == L.zero()
                True
            """
            lattice = self.parent()
            ring = lattice.base_ring()
            assert _engine_ring(ring) is SageZZ, (
                f"an integer Bezout partner requires a lattice over ZZ, not {ring}"
            )
            regular = ring.regular_module()
            pairing = lattice.left_curry()(self)
            generator = regular.scalar_multiple(
                self.div(), regular.module_generators()[0]
            )
            if not lattice.module_rank().is_finite():
                support = lattice.subobject_on(
                    tuple(
                        lattice.module_generator(label)
                        for label in lattice.generator_pairings(self)
                    )
                )
                inclusion = support.inclusion()
                restricted = pairing * inclusion
                return inclusion(restricted.preimage(generator))
            return pairing.preimage(generator)

        def hyperbolic_partner_locus(self):
            r"""Restrict the square-zero locus to the pairing's affine fibre.

            The module-map fibre first imposes ``b(self,w)=div(self)``
            over ZZ, or ``b(self,w)=1`` over a field.
            Its square-zero equalizer retains the quadratic constraint and
            the inclusion into that affine fibre. Composing with the fibre
            inclusion gives the lattice inclusion. The object contains every
            partner, whether or not point finding is available.

            EXAMPLES::

                sage: L = Lattices(ZZ)([[0, 2, 0], [2, 2, 0], [0, 0, -2]])
                sage: e, f, a = tuple(L.module_generators())
                sage: locus = e.hyperbolic_partner_locus()
                sage: f + a in locus.object() and f not in locus.object()
                True
                sage: locus.object().inclusion()(locus.object()(f + a)) == f + a
                True
                sage: fresh = e.hyperbolic_partner_locus().object()
                sage: w = fresh.an_element()
                sage: assert w.parent() is L and w.q() == ZZ.zero()
                sage: assert L.b(e, w) == ZZ(2)
                sage: assert fresh.an_element() is w
                sage: Q = Lattices(QQ)("U")
                sage: x = Q.module_generators()[0]
                sage: point = x.hyperbolic_partner_locus().object().an_element()
                sage: assert Q.q(point) == QQ.zero() and Q.b(x, point) == QQ.one()
            """
            lattice = self.parent()
            ring = lattice.base_ring()
            from sage_extensions.categories.rings.ring_foundation import OwnedFields

            pairing = lattice.left_curry()(self)
            regular = pairing.codomain()
            scale = ring.one() if ring in OwnedFields() else self.div()
            prescribed = regular.scalar_multiple(
                scale, regular.module_generators()[0]
            )
            fibre = pairing.solution_fibre(prescribed)
            square = Sets().Mor(fibre, ring)(lambda vector: vector.q())
            zero = Sets().Mor(fibre, ring)(lambda vector: ring.zero())
            construction = Sets().equalizer_construction(square, zero)
            if (self.q() == ring.zero()) is True:
                field_case = (
                    ring in OwnedFields() and ring.is_exact()
                    and ring.is_finite() is False
                    and lattice.module_rank() != cardinal(0)
                    and (ring(2) != ring.zero()) is True
                )
                integral_case = (
                    ring is _owned_integers()
                    and lattice.module_rank().is_finite()
                    and self.is_primitive() is True
                )
                if field_case or integral_case:
                    construction.object()._retain_point_computation(self.hyperbolic_partner)
            return construction

        def hyperbolic_partner(self) -> Lattices.ElementMethods:
            r"""Return an isotropic partner of the supplied isotropic vector.

            Over an exact field of characteristic different from two,
            the pairing is one: solve ``b(self,v)=1`` and return
            ``v-q(v)*self/2``. The vector must be outside the radical.
            These equations give square zero and pairing one because
            ``q(self)=0``. The solver operates on the actual module map.

            Over ZZ the pairing is ``self.div()``, and the vector must be
            primitive, isotropic and outside the radical.
            The Bezout correction is integral when ``2*div(self)`` divides
            the square of the selected Bezout partner. This includes every
            primitive isotropic vector of divisibility one in an even lattice.
            Otherwise, in finite rank, put ``K=ker b(self,-)``. The square
            of ``h+k`` modulo ``2d`` depends only on the class of ``k`` in
            ``K/(ZZ*self+2d*K)``. Enumerating this finite module decides
            existence: a zero residue permits the exact correction along
            ``self``; every partner gives such a residue. The full locus
            remains represented by :meth:`hyperbolic_partner_locus`.

            EXAMPLES::

                sage: L = Lattices(ZZ)([[0, 1], [1, 2]])
                sage: e = L.basis_vector(0)
                sage: f = e.hyperbolic_partner()
                sage: f.parent() is L and f.q() == ZZ(0) and e.b(f) == ZZ(1)
                True
                sage: M = Lattices(ZZ)([[0, 2, 0], [2, 2, 0], [0, 0, -2]])
                sage: u = M.basis_vector(0)
                sage: h = u.hyperbolic_partner()
                sage: h.parent() is M and h.q() == ZZ(0) and u.b(h) == ZZ(2)
                True
                sage: Lattices(ZZ)([[0, 2], [2, 2]]).basis_vector(0).hyperbolic_partner()
                Traceback (most recent call last):
                ...
                ValueError: the integral hyperbolic partner locus is empty
                sage: V = Lattices(QQ)("U")
                sage: e = V.basis_vector(0) * QQ(2)
                sage: f = e.hyperbolic_partner()
                sage: assert f.parent() is V and V.q(f) == QQ(0) and V.b(e,f) == QQ(1)
                sage: assert f in e.hyperbolic_partner_locus().object()
                sage: W = Lattices(AA)([[1, 0], [0, -2]])
                sage: e = W.linear_combination({0: AA(2).sqrt(), 1: AA(1)})
                sage: f = e.hyperbolic_partner()
                sage: assert W.q(f) == AA(0) and W.b(e,f) == AA(1)
            """
            lattice = self.parent()
            ring = lattice.base_ring()
            from sage_extensions.categories.rings.ring_foundation import OwnedFields

            if ring in OwnedFields():
                assert ring.is_exact() and ring(2) != ring.zero(), (
                    "exact hyperbolic partner construction requires an exact field of characteristic different from two"
                )
                assert self.q() == ring.zero(), (
                    f"a hyperbolic partner requires an isotropic vector, not {self}"
                )
                pairing = lattice.left_curry()(self)
                regular = pairing.codomain()
                unit = regular.scalar_multiple(ring.one(), regular.module_generators()[0])
                partner = pairing.preimage(unit)
                candidate = partner - lattice.scalar_multiple(partner.q() / ring(2), self)
                locus = self.hyperbolic_partner_locus().object()
                return locus.inclusion()(locus(candidate))
            assert self.content() == ring.one() and self.q() == ring.zero(), (
                f"an integral hyperbolic partner requires a primitive isotropic vector, not {self}"
            )
            divisibility = self.div()
            assert divisibility != ring.zero(), (
                f"{self} lies in the radical of {lattice} and cannot span a hyperbolic plane"
            )
            partner = self.bezout_partner()
            correction, remainder = partner.q().quo_rem(ring(2) * divisibility)
            if remainder != ring.zero():
                if not lattice.module_rank().is_finite():
                    raise NotImplementedError(
                        "the norm-congruence selection requires a finite-rank pairing kernel"
                    )
                kernel = lattice.left_curry()(self).kernel()
                modulus = ring(2) * divisibility
                relations = kernel.subobject_on(
                    tuple(
                        kernel.scalar_multiple(modulus, v)
                        for v in kernel.module_generators()
                    )
                    + (kernel.inclusion().lift(self),)
                )
                projection = relations.inclusion().cokernel_projection()
                for residue in projection.codomain():
                    lifted = partner + kernel.inclusion()(projection.preimage(residue))
                    quotient, residue_square = lifted.q().quo_rem(modulus)
                    if residue_square == ring.zero():
                        partner, correction = lifted, quotient
                        break
                else:
                    raise ValueError("the integral hyperbolic partner locus is empty")
            candidate = partner - lattice.scalar_multiple(correction, self)
            locus = self.hyperbolic_partner_locus().object()
            return locus.inclusion()(locus(candidate))

        def primitive_dual(self):
            r"""Return ``v/div(v)`` under the metric embedding ``L -> L^#``."""
            return self.parent().primitive_dual(self)

        def primitive_dual_in_discriminant_bilinear_form(self):
            r"""Return the class of ``v/div(v)`` in the discriminant bilinear form."""
            form = self.parent().discriminant_bilinear_form()
            return form.discriminant_class(self.primitive_dual())

        def primitive_dual_in_discriminant_quadratic_form(self):
            r"""Return the class of ``v/div(v)`` in the discriminant quadratic form.

            This operation requires an even lattice, exactly as the
            discriminant quadratic form itself does.
            """
            form = self.parent().discriminant_quadratic_form()
            return form.discriminant_class(self.primitive_dual())

        def divided_discriminant_class(self):
            return self.parent().divided_discriminant_class(self)

        def discriminant_class(self):
            r"""Return ``[v/div(v)]`` in the discriminant module for primitive ``v``."""
            if not self.is_primitive():
                raise ValueError(
                    f"{self!r} has no discriminant class [v/div(v)] here: this class is defined for a primitive vector, and {self!r} is not primitive in {self.parent()!r}"
                )
            return self.divided_discriminant_class()

        def to_covector(self):
            r"""Return \(b(v,-)\in\operatorname{Hom}_R(L,R)\), the image of \(v\) under the algebraic correlation.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: U = Lattices(ZZ)("U")
                sage: e, f = U.module_generators()
                sage: e.to_covector().parent() is U.dual_module()
                True
            """
            return self.parent().algebraic_correlation_morphism()(self)

        def sublattice(self):
            r"""Return \(Rv\hookrightarrow L\): the rank-one subobject spanned by this vector, with its inclusion."""
            return self.parent().subobject_on((self,))

        def is_primitive(self) -> bool:
            r"""Test primitivity of the map ``R -> L``, ``1 |-> self``.

            This map must be injective and have torsion-free cokernel.
            The inclusion of its image alone loses the first condition:
            the zero submodule is primitive but the zero vector in a
            lattice over a nonzero integral domain is not primitive.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: U = Lattices(ZZ)("U")
                sage: e, f = U.module_generators()
                sage: e.is_primitive(), (2 * e).is_primitive(), (2 * e + 3 * f).is_primitive()
                (True, False, True)
                sage: U.zero().is_primitive()
                False
                sage: U.zero().sublattice().is_primitive()
                True
                sage: Q = Lattices(QQ)([[1]])
                sage: (Q.basis_vector(0) * QQ(2)).is_primitive()
                True
            """
            lattice = self.parent()
            line = lattice.base_ring().free_module(1)
            return line.module_category().Mor(line, lattice)((self,)).is_primitive()

        def orthogonal_complement(self):
            r"""Return \(v^\perp\hookrightarrow L\) as a subobject of the lattice."""
            return self.sublattice().orthogonal_complement()

        def perp(self):
            r"""Synonym for :meth:`orthogonal_complement`."""
            return self.orthogonal_complement()

        def isotropic_reduction(self):
            r"""Return \(v^\perp/Rv\) as a lattice for a primitive isotropic vector.

            For nonprimitive isotropic vectors the cokernel has torsion, so it
            is not an object of :class:`Lattices`; use
            :meth:`isotropic_quotient` for that formed-module quotient.
            """
            if not self.is_isotropic():
                raise ValueError(
                    f"cannot form the isotropic reduction of {self!r}: q(v) = {self.q()} is nonzero"
                )
            if not self.is_primitive():
                raise NotPrimitiveError(
                    f"cannot form the lattice v^perp/Rv for {self!r}: the vector is not primitive; use isotropic_quotient() to retain the torsion quotient"
                )
            return self.parent().primitive_isotropic_subobject(self).isotropic_reduction()

        def isotropic_quotient(self):
            r"""Return the formed module \(v^\perp/Rv\), retaining torsion.

            The rank-one subobject \(Rv\) is not saturated.  For isotropic
            \(v\), its image in \(v^\perp\) lies in the radical of the
            restricted form, so that form descends along the literal cokernel
            \(v^\perp/Rv\).  In particular, nonprimitive input is not
            silently replaced by its primitive line.
            """
            if not self.is_isotropic():
                raise ValueError(
                    f"cannot form the isotropic quotient of {self!r}: q(v) = {self.q()} is nonzero"
                )
            line = self.sublattice()
            line_in_ambient = line.inclusion()
            perpendicular = line_in_ambient.orthogonal_complement()
            perpendicular_in_ambient = perpendicular.inclusion()
            line_in_perpendicular = line.Mono(perpendicular)(
                {
                    label: perpendicular_in_ambient.lift(
                        line_in_ambient(line.module_generator(label))
                    )
                    for label in line.module_generating_set()
                }
            )
            value_module = perpendicular.value_module()
            value_identity = (
                value_module.module_category()
                .Mor(value_module, value_module)
                .identity()
            )
            descended = perpendicular._formed_form().descend_along(
                line_in_perpendicular, value_identity
            )
            return FormModules(descended.module().base_ring())(descended)

        def e_perp_mod_e(self):
            r"""Return ``v^perp/Rv``; archived synonym for :meth:`isotropic_reduction`."""
            return self.isotropic_reduction()

        def is_root(self) -> bool:
            r"""Return whether this vector lies in ``R(L) = {v : v primitive, s_v in O(L)}``.

            A root is a primitive integral reflection vector (owner ruling,
            #406; requested from ``lean-categories``, see research issue #406).
            ``s_{2r} = s_r``, so integrality alone admits non-primitive
            multiples; :meth:`is_integral_reflection_vector` is that weaker
            predicate.

            EXAMPLES::

                sage: from sage_extensions.categories.lattices import Lattices
                sage: Iinf = Lattices(ZZ)(ZZ^NN)
                sage: Iinf.basis_vector(0).is_root()
                True
                sage: Iinf.linear_combination({0: ZZ(2), 1: ZZ(1)}).is_root()
                False
                sage: L = Lattices(ZZ)([[1, 0, 0], [0, 2, 0], [0, 0, -2]])
                sage: v = 2 * L.basis_vector(0)
                sage: v.is_integral_reflection_vector(), v.is_root()
                (True, False)
            """
            parent = self.parent()
            return bool(
                self.is_integral_reflection_vector()
                and parent.subobject_on((self,)).is_primitive()
            )

        def is_integral_reflection_vector(self) -> bool:
            r"""Return whether ``s_r(x) = x - 2 b(x, r)/b(r, r) r`` maps the lattice into itself.

            ``lean-categories`` FOUNDATIONS §60.1 (*integral reflection
            vector*): ``2 b(x, r)/b(r, r)`` is integral for every ``x``.  No
            primitivity is required; :meth:`is_root` adds it.
            """

            parent = self.parent()
            ring = parent.base_ring()
            assert ring.is_integral_domain(), (
                f"cannot decide whether {self!r} is an integral reflection vector: the reflection is defined here for lattices over an integral domain, and {ring} is not one"
            )
            norm = ring(self.q())
            if norm == ring.zero():
                # s_r exists only for b(r, r) != 0, so a vector of square zero is not one.
                return False
            fraction_field = ring if ring.is_field() else ring.fraction_field()
            norm_in_fraction_field = fraction_field(norm)
            return all(
                fraction_field(ring(2) * coefficient) / norm_in_fraction_field in ring
                for coefficient in parent.generator_pairings(self).values()
            )


class OrthogonalSumLattices(OwnedCategoryOverBaseRing):
    r"""Orthogonal lattice sums with their underlying module biproducts.

    The selected projections are module maps. For example, projecting
    ``<1> orthogonal_sum <1>`` onto its first summand kills a vector of
    square one, so it does not preserve the form. The direct-sum datum
    therefore belongs to Modules(R); the orthogonal form additionally
    places this object in Lattices(R).

    EXAMPLES::

        sage: A = Lattices(ZZ)([[1]])
        sage: X = Lattices(ZZ).orthogonal_sum((A, A))
        sage: assert X in DirectSumObjects(Modules(ZZ))
        sage: assert X not in DirectSumObjects(Lattices(ZZ))
        sage: assert X.decomposition() is X
        sage: v = X.injection(1)(A.module_generators()[0])
        sage: assert X.q(v) == ZZ(1) and A.q(X.projection(0)(v)) == ZZ(0)
        sage: Lattices(ZZ).product((A, A))
        Traceback (most recent call last):
        ...
        NotImplementedError: a categorical lattice product is not supplied by the orthogonal-sum construction
    """

    def an_object(self):
        lattice = Lattices(self.base_ring()).an_object()
        return Lattices(self.base_ring()).orthogonal_sum((lattice, lattice))

    def _repr_object_names(self):
        return f"chosen orthogonal lattice sums over {self.base_ring()}"

    def super_categories(self):
        from sage_extensions.categories.modules.pure.modules import (
            BiproductModules,
        )

        return [
            Lattices(self.base_ring()),
            BiproductModules(self.base_ring()),
        ]

    class ParentMethods:
        def _biproduct_factor_position(self, index):
            factors = self.biproduct_factors()
            normalized = factors.index_set()(index)
            return int(factors.index_set().ranking_map()(normalized))

        def _biproduct_block_offsets(self):
            r"""The positions at which the summands' blocks begin in the concatenated framing."""
            return _block_offsets(
                tuple(
                    cardinal(factor.module_rank())
                    for factor in self.biproduct_factors()
                )
            )

        def injection(self, index):
            r"""Return the selected summand inclusion into this orthogonal sum."""
            factors = self.biproduct_factors()
            normalized = factors.index_set()(index)
            position = self._biproduct_factor_position(normalized)
            summand = factors[normalized]
            source_labels = summand.module_generating_set()
            target_labels = self.module_generating_set()
            offset = self._biproduct_block_offsets()[position]

            def image(label):
                source_position = int(source_labels.ranking_map()(label))
                target_label = target_labels.ranking_map().inverse()(
                    offset + source_position
                )
                return self.module_generator(target_label)

            return summand.module_category().Mor(summand, self)(image)

        def projection(self, index):
            r"""Return the selected projection from this orthogonal sum."""
            factors = self.biproduct_factors()
            normalized = factors.index_set()(index)
            position = self._biproduct_factor_position(normalized)
            summand = factors[normalized]
            offsets = self._biproduct_block_offsets()
            source_labels = self.module_generating_set()
            target_labels = summand.module_generating_set()

            def image(label):
                source_position = int(source_labels.ranking_map()(label))
                which, place = _block_position(offsets, source_position)
                match which == position:
                    case True:
                        target_label = target_labels.ranking_map().inverse()(place)
                        return summand.module_generator(target_label)
                    case False:
                        return summand.zero()

            return self.module_category().Mor(self, summand)(image)

        def from_coproduct_cocone(self, legs, *, codomain=None):
            r"""Return the underlying module map with these legs and apex.

            ``codomain`` supplies the apex for an empty family; a nonempty
            family can determine it from its first leg.
            """
            from sage_extensions.categories.abstract_categories.products import (
                _finite_factor_family,
            )

            factors = self.biproduct_factors()
            legs = _finite_factor_family(legs, name="Coproduct cocone legs")
            assert legs.index_set() == factors.index_set(), (
                f"the cocone {legs!r} under {self!r} does not have one leg per factor: legs are indexed by {legs.index_set()!r}, factors by {factors.index_set()!r}"
            )
            target = codomain
            if target is None:
                if factors.index_set().cardinality() == cardinal(0):
                    raise ValueError("an empty coproduct cocone needs its codomain")
                first = factors.index_set().ranking_map().inverse()(0)
                target = legs[first].codomain()
            assert all(leg.codomain() is target for leg in legs), (
                f"the legs of the cocone {legs!r} under {self!r} do not all have the codomain {target!r}, so they have no common apex"
            )
            assert all(
                legs.value(index).domain() is factors.value(index)
                for index in factors.index_set()
            ), (
                f"some leg of the cocone {legs!r} under {self!r} does not start at its factor of the biproduct"
            )
            offsets = self._biproduct_block_offsets()
            source_labels = self.module_generating_set()

            def image(label):
                source_position = int(source_labels.ranking_map()(label))
                which, place = _block_position(offsets, source_position)
                factor_index = factors.index_set().ranking_map().inverse()(which)
                factor = factors[factor_index]
                factor_label = (
                    factor.module_generating_set().ranking_map().inverse()(place)
                )
                return legs[factor_index](factor.module_generator(factor_label))

            return self.module_category().Mor(self, target)(image)

        def from_product_cone(self, legs, *, domain=None):
            r"""Return the underlying module map with these legs and apex.

            ``domain`` supplies the apex for an empty family; a nonempty
            family can determine it from its first leg.
            """
            from sage_extensions.categories.abstract_categories.products import (
                _finite_factor_family,
            )

            factors = self.biproduct_factors()
            legs = _finite_factor_family(legs, name="Product cone legs")
            assert legs.index_set() == factors.index_set(), (
                f"the cone {legs!r} over {self!r} does not have one leg per factor: legs are indexed by {legs.index_set()!r}, factors by {factors.index_set()!r}"
            )
            source = domain
            if source is None:
                if factors.index_set().cardinality() == cardinal(0):
                    raise ValueError("an empty product cone needs its domain")
                first = factors.index_set().ranking_map().inverse()(0)
                source = legs[first].domain()
            assert all(leg.domain() is source for leg in legs), (
                f"the legs of the cone {legs!r} over {self!r} do not all have the domain {source!r}, so they have no common apex"
            )
            assert all(
                legs.value(index).codomain() is factors.value(index)
                for index in factors.index_set()
            ), (
                f"some leg of the cone {legs!r} over {self!r} does not land in its factor of the biproduct"
            )

            def image(label):
                generator = source.module_generator(label)
                return sum(
                    (
                        self.injection(index)(legs.value(index)(generator))
                        for index in factors.index_set()
                    ),
                    self.zero(),
                )

            return source.module_category().Mor(source, self)(image)

        def orthogonal_sum_map(self, product):
            r"""Return ``prod_i G_i -> O(L)``, ``(g_i) |-> sum_i g_i``, for subgroups ``G_i <= O(L_i)``.

            ``L = sum_i L_i`` is this orthogonal sum.  ``product`` is a selected
            product of groups ``prod_i G_i`` (``OwnedGroups().product_construction``),
            its ``i``-th factor, in the order of the summands, a subgroup of
            ``O(L_i)``.  ``sum_i g_i`` is the isometry acting by ``g_i`` on the
            summand ``L_i``: the map out of the biproduct whose legs are
            ``L_i --g_i--> L_i --> L``.  The map is injective, since
            ``sum_i g_i`` restricts to ``g_i`` on ``L_i``.
            """
            from sage_extensions.categories.lattice_morphisms import (
                _subgroup_inclusion_into,
            )

            factors = self.biproduct_factors()
            labels = tuple(factors.index_set())
            shape = product.diagram().domain()
            projections = {
                index: product.structure_morphism(shape(position))
                for position, index in enumerate(labels)
            }
            inclusions = {
                index: _subgroup_inclusion_into(projections[index].codomain(), factors[index].O())
                for index in labels
            }
            source = product.object()

            def block_isometry(element):
                legs = finite_indexed_family(
                    factors.index_set(),
                    lambda index: factors[index].module_category().Mor(factors[index], self)(
                        lambda label, index=index: self.injection(index)(
                            inclusions[index](projections[index](element))(
                                factors[index].module_generator(label)
                            )
                        )
                    ),
                    name=f"Blocks of an element of {source}",
                )
                block_sum = self.from_coproduct_cocone(legs)
                return self.O()(lambda label: block_sum(self.module_generator(label)))

            return source.Mor(self.O()).elementwise(block_isometry)


class DefiniteLattices(OwnedCategoryOverBaseRing):
    r"""Finite-rank definite lattices.

    Over ``ZZ`` their reflective roots are finite in number and enumerated
    shell by shell.  Over ``QQ`` a definite space of rank at least 2 has
    infinite square fibres (``x^2 + y^2 = 1`` has ``(3/5, 4/5)``), so finiteness
    of the roots is not a consequence of definiteness alone.
    """

    def super_categories(self):
        return [Lattices(self.base_ring()).FinitelyGenerated()]

    def an_object(self):
        return self(Lattices(self.base_ring()).an_object())

    def _call_(self, lattice):
        from sage_extensions.refine import refine

        finite = Lattices(self.base_ring()).FinitelyGenerated()
        if lattice not in finite or not (lattice.is_positive_definite() or lattice.is_negative_definite()):
            raise ValueError("finite reflective-root enumeration requires a definite lattice")
        return refine(lattice, self)

    class ParentMethods:
        @cached_method
        def reflective_roots(self):
            r"""All primitive reflective roots of this definite lattice."""
            sign = (
                self.base_ring().one()
                if self.is_positive_definite()
                else -self.base_ring().one()
            )
            return finite_ordered_set(
                tuple(
                    root
                    for length in self.possible_root_lengths()
                    for root in self.roots_of_square(sign * length)
                )
            )


class EvenTwoElementaryLattices(OwnedCategoryOverBaseRing):
    r"""Nondegenerate even integral lattices with 2-elementary discriminant group.

    This is a refinement of lattices, not a property of arbitrary even forms.
    """

    def super_categories(self):
        if _engine_ring(self.base_ring()) is not SageZZ:
            raise TypeError("2-elementary integral lattices require the integer coefficient ring")
        return [
            Lattices(self.base_ring()).Even().Nondegenerate().FinitelyGenerated(),
        ]

    class ParentMethods:
        def delta(self):
            r"""Return Nikulin's invariant on the even 2-elementary lattice surface."""
            return Lattices.ParentMethods.delta(self)

        @cached_method
        def two_elementary_invariants(self):
            r"""Return Nikulin's \((r,a,\delta)\) for an even 2-elementary lattice.

            The rank, the length of the discriminant group and \(\delta\) are
            three natural numbers, so the triple is a point of
            \(\mathbb N^3\).
            """
            # Membership in this category already establishes evenness and
            # 2-elementarity in its constructor. For a finite nondegenerate
            # integral lattice, |det(G)| is |A_L|; since A_L is elementary
            # abelian of exponent 2, |A_L| = 2^a where a is its length. Avoid
            # recomputing Smith invariant factors merely to recover a. Compute
            # delta from the same integral Gram inverse without calling
            # ``self.delta()``: that public validator repeats the evenness and
            # 2-elementarity checks already proved by this category's
            # constructor, including another discriminant-exponent check.
            determinant = abs(int(self.determinant()))
            delta = self.base_ring().zero()
            if determinant != 1:
                inverse = self._integral_gram_inverse()
                delta = self.base_ring()(
                    int(any(inverse[i, i] not in SageZZ for i in range(inverse.nrows())))
                )
            return nikulin_invariants(
                self.module_rank(), self.base_ring()(determinant.bit_length() - 1), delta
            )

    def an_object(self):
        return self(Lattices(self.base_ring())("U"))

    def _call_(self, lattice):
        from sage_extensions.refine import refine

        lattice = Lattices(self.base_ring())(lattice)
        if lattice not in Lattices(self.base_ring()).FinitelyGenerated():
            raise ValueError("a 2-elementary even lattice must have finite rank")
        if not lattice.is_even() or not lattice.is_nondegenerate() or not lattice.is_p_elementary(self.base_ring()(2)):
            raise ValueError("a 2-elementary even lattice must be nondegenerate, even and have 2-elementary discriminant")
        return refine(lattice, self)


def FiniteRankLattices(base_ring):
    r"""``Lattices(R).FinitelyGenerated()``, under the name the session catalogue uses."""
    return Lattices(base_ring).FinitelyGenerated()


def NondegenerateLattices(base_ring):
    r"""``Lattices(R).Nondegenerate()``, under the name the session catalogue uses."""
    return Lattices(base_ring).Nondegenerate()


def EvenLattices(base_ring):
    r"""``Lattices(R).Even()``, under the name the session catalogue uses."""
    return Lattices(base_ring).Even()


class RankOneRationalWittDecomposition:
    r"""The rational Witt decomposition attached to a primitive isotropic line.

    The integral objects ``I <= I^perp <= L`` and ``K_I=I^perp/I`` remain the
    source arithmetic data.  After base change to ``Frac(R)``, a selected
    isotropic partner ``f`` with ``b(e,f)=1`` gives

    ``L_Q = <e,f> perp K_Q``.

    In a non-unimodular cusp ``f`` need not lie in ``L``; that failure is the
    integral gluing which can restrict the Levi image.
    """

    def __init__(
        self,
        reduction,
        bezout_partner,
        rational_lattice,
        rational_isotropic,
        rational_partner,
        hyperbolic_plane,
        orthogonal_summand,
    ) -> None:
        self._reduction = reduction
        self._bezout_partner = bezout_partner
        self._rational_lattice = rational_lattice
        self._rational_isotropic = rational_isotropic
        self._rational_partner = rational_partner
        self._hyperbolic_plane = hyperbolic_plane
        self._orthogonal_summand = orthogonal_summand

    def reduction(self):
        return self._reduction

    def integral_line(self):
        return self.reduction().isotropic_sublattice()

    def integral_perpendicular(self):
        return self.reduction().orthogonal_complement()

    def integral_reduction(self):
        return self.reduction()

    def divisibility(self):
        inclusion = self.reduction().isotropic_embedding()
        generator = self.integral_line().module_generators()[0]
        return inclusion(generator).div()

    def bezout_partner(self):
        r"""Return integral ``h`` with ``b(e,h)=div(e)``."""
        return self._bezout_partner

    def rational_lattice(self):
        return self._rational_lattice

    def isotropic_vector(self):
        return self._rational_isotropic

    def dual_isotropic_vector(self):
        return self._rational_partner

    def hyperbolic_plane(self):
        return self._hyperbolic_plane

    def orthogonal_summand(self):
        return self._orthogonal_summand

    def __repr__(self) -> str:
        return f"Rational Witt decomposition of {self.reduction().isotropic_embedding().codomain()} along {self.integral_line()}"


class RankOneParabolicLeviExactSequence:
    r"""The exact sequence ``1 -> U_I -> P_I^1 -> M_I^1 -> 1``.

    Here ``P_I^1`` is the pointwise stabilizer of a primitive isotropic line,
    ``M_I^1`` is its represented image in ``O(K_I)``, and ``U_I`` is the
    kernel.  The target is the actual gluing-preserving image, not the whole
    orthogonal group of the reduction.
    """

    def __init__(self, reduction) -> None:
        self._reduction = reduction

    def reduction(self):
        return self._reduction

    def source(self):
        return self.reduction().pointwise_parabolic_subgroup()

    def kernel(self):
        return self.reduction().unipotent_kernel()

    def target(self):
        return self.reduction().pointwise_levi_image()

    @cached_method
    def projection(self):
        target = self.target()
        levi = self.reduction().levi_action()
        return self.source().Mor(target)(
            lambda isometry: target(levi(isometry)),
        )

    def lift(self, isometry):
        r"""Return the retained pointwise-parabolic lift of one target element."""
        return self.reduction().pointwise_levi_lift(isometry)

    def __repr__(self) -> str:
        return f"1 -> {self.kernel()} -> {self.source()} -> {self.target()} -> 1"


def _spinor_norm_multiplier(field, form_multiplier):
    r"""Return the multiplier \(c\) of a spinor norm \(s_v\mapsto[c\,(v,v)]\) over ``field``.

    Omitted, it is \(-\tfrac12\), the choice of Gritsenko--Hulek--Sankaran
    (arXiv:0810.1614, §1).
    """
    multiplier = (
        field(-1) / field(2) if form_multiplier is None else field(form_multiplier)
    )
    assert multiplier.is_unit(), (
        f"the spinor norm is taken for the reflection values c(v, v) with c a unit of {field}, but c = {multiplier}"
    )
    return multiplier


def _spinor_norm_kernel(spinor_norm, description, *, character_data=None):
    r"""Return \(\ker\mathrm{sn}=\mathrm{sn}^{-1}(\{[1]\})\), retaining \(\mathrm{sn}\) as its preimage morphism."""
    return PreimageSubgroups(spinor_norm.domain())(
        spinor_norm,
        spinor_norm.codomain().subgroup(()),
        description=description,
        character_data=character_data,
    )


class DiscriminantReductionSequence:
    r"""The discriminant reduction sequence \(1\to K_L\to O(L)\xrightarrow{f}O(A_L)\to C_L\to 1\).

    An isometry \(g\) of \(L\) acts on the dual lattice \(L^\vee\) and
    preserves \(L\), so it induces an isometry of the discriminant form
    \(A_L=L^\vee/L\); \(f\colon g\mapsto\bar g\) is the discriminant
    reduction morphism.  Its kernel \(K_L\), the discriminant reduction
    kernel, is the stable orthogonal group \(\tilde O(L)\)
    (Gritsenko--Hulek--Sankaran, arXiv:0810.1614, §1), and
    \(C_L=O(A_L)/f(O(L))\) is the discriminant reduction cokernel.  The
    sequence is an exact sequence of groups exactly when \(f(O(L))\) is
    normal in \(O(A_L)\): only then is \(C_L\) a group, and
    :meth:`cokernel_projection` asserts it.
    """

    def __init__(self, lattice) -> None:
        self._lattice = lattice

    def lattice(self):
        return self._lattice

    def source(self):
        r"""Return \(O(L)\)."""
        return self._lattice.Aut()

    def target(self):
        r"""Return \(O(A_L)\)."""
        return self._lattice.discriminant_group().orthogonal_group()

    def morphism(self):
        r"""Return the discriminant reduction morphism \(f\colon O(L)\to O(A_L)\)."""
        return self._lattice.discriminant_representation()

    def kernel(self):
        r"""Return the discriminant reduction kernel \(K_L=\ker f=\tilde O(L)\)."""
        return self._lattice.stable_orthogonal_group()

    def kernel_inclusion(self):
        r"""Return \(K_L\hookrightarrow O(L)\)."""
        return self.kernel().inclusion()

    def image(self):
        r"""Return \(f(O(L))\le O(A_L)\)."""
        return self._lattice.discriminant_image()

    @cached_method
    def cokernel_projection(self):
        r"""Return \(O(A_L)\to C_L=O(A_L)/f(O(L))\).

        This is the equivariant projection to the left-coset pointed set.
        When the image is normal, that coset space is canonically the ordinary
        group cokernel.
        """
        return self.morphism().coset_cokernel_projection()

    def cokernel(self):
        r"""Return the discriminant reduction cokernel \(C_L=O(A_L)/f(O(L))\)."""
        return self.cokernel_projection().codomain()

    def __repr__(self) -> str:
        return f"1 -> {self.kernel()} -> {self.source()} -> {self.target()} -> C_L -> 1"


class SpinorNormSequence:
    r"""The \(K\)-spinor norm sequence \(1\to K_{\mathrm{sn}_K}\to O(L_K)\xrightarrow{\mathrm{sn}_K}K^\times/(K^\times)^2\to C_{\mathrm{sn}_K}\to 1\).

    Here \(K=\operatorname{Frac}(R)\), \(L_K=L\otimes_R K\) and
    \(\mathrm{sn}_K\) is the spinor norm of \(L_K\) with the stated
    multiplier (``Lattices(K)`` objects' ``spinor_norm``).  Its kernel
    \(K_{\mathrm{sn}_K}\le O(L_K)\) is the \(K\)-spinor kernel; the
    elements of \(O(L)\) lying in it form the \(R\)-spinor kernel, the
    ``spinor_kernel`` of \(L\).  The target is abelian, so the image of
    \(\mathrm{sn}_K\) is normal and \(C_{\mathrm{sn}_K}\) is a group.
    """

    def __init__(self, lattice, form_multiplier) -> None:
        self._lattice = lattice
        self._form_multiplier = _spinor_norm_multiplier(
            lattice.base_ring().fraction_field(),
            form_multiplier,
        )

    def lattice(self):
        return self._lattice

    def form_multiplier(self):
        r"""Return \(c\), with \(\mathrm{sn}_K(s_v)=[c\,(v,v)]\)."""
        return self._form_multiplier

    def quadratic_space(self):
        r"""Return \(L_K=L\otimes_R K\)."""
        return self._lattice.vector_space()

    def source(self):
        r"""Return \(O(L_K)\)."""
        return self.quadratic_space().Aut()

    def target(self):
        r"""Return \(K^\times/(K^\times)^2\)."""
        return self.quadratic_space().base_ring().square_class_group()

    @cached_method
    def morphism(self):
        r"""Return \(\mathrm{sn}_K\colon O(L_K)\to K^\times/(K^\times)^2\)."""
        return self.quadratic_space().spinor_norm(form_multiplier=self._form_multiplier)

    @cached_method
    def kernel(self):
        r"""Return the \(K\)-spinor kernel \(K_{\mathrm{sn}_K}=\ker\mathrm{sn}_K\le O(L_K)\)."""
        return _spinor_norm_kernel(self.morphism(), "sn_K(g) = 1")

    def kernel_inclusion(self):
        r"""Return \(K_{\mathrm{sn}_K}\hookrightarrow O(L_K)\)."""
        return self.kernel().inclusion()

    @cached_method
    def image(self):
        r"""Return the represented image of ``sn_K`` in low anisotropic dimension.

        For a one-dimensional anisotropic space the orthogonal group consists
        of the identity and one reflection, so the image is generated by the
        reflection class ``[c q(v)]``.  For an anisotropic binary space, fix
        one represented value ``a``.  The spinor norms of rotations form the
        norm subgroup of the associated quadratic extension; a square class
        ``[t]`` lies in it exactly when the binary form represents ``a t``.
        The full orthogonal image is that subgroup together with its reflection
        coset ``[c a]``.
        """
        space = self.quadratic_space()
        target = self.target()
        field = space.base_ring()
        assert field in PrimeFields() and field.characteristic() == 0, (
            f"the K-spinor norm image of {self._lattice!r} is computed here only for K = QQ, and K = {field}"
        )
        dimension = int(space.module_rank())
        assert dimension in (1, 2) and space.witt_index() == 0, (
            f"the represented low-dimensional spinor image is for anisotropic dimensions 1 and 2, but {space} has dimension {dimension} and Witt index {space.witt_index()}"
        )
        generators = tuple(space.module_generators())
        first_value = space.norm(generators[0])
        reflection_class = target(self._form_multiplier * first_value)

        match dimension:
            case 1:
                predicate = lambda square_class: bool(
                    square_class.is_one() or square_class == reflection_class
                )
                description = (
                    f"the subgroup generated by the reflection class {reflection_class}"
                )
            case 2:

                def in_rotation_image(square_class):
                    return _rational_anisotropic_binary_form_represents(
                        space,
                        first_value * square_class.representative(),
                    )

                predicate = lambda square_class: bool(
                    in_rotation_image(square_class)
                    or in_rotation_image(square_class * reflection_class)
                )
                description = f"the spinor-norm subgroup generated by products of represented values and the reflection class {reflection_class}"
        return PredicateSubgroups(target)(predicate, description)

    @cached_method
    def cokernel_projection(self):
        r"""Return \(K^\times/(K^\times)^2\to C_{\mathrm{sn}_K}\), the quotient by the image of \(\mathrm{sn}_K\).

        The image is generated by the spinor norms of the rotations, which
        do not depend on \(c\), and the classes \([c\,(v,v)]\) of the
        reflections (O'Meara, *Introduction to Quadratic Forms*, §55).  For
        \(V=L_K\) over \(K=\mathbb Q\):

        - in dimension at least 3, the rotations have as spinor norms all
          of \(\mathbb Q^\times\) when \(V\) is indefinite, and exactly the
          positive rationals when \(V\) is definite (O'Meara 101:8).  For
          definite \(V\) the reflections add \([c\,(v,v)]\), whose sign is
          that of \(c\) times the sign of the form: the image is the positive
          classes when that sign is positive, and \(C_{\mathrm{sn}_K}\) is
          then \(\{\pm1\}\) through the sign, and everything otherwise;
        - when \(V\) is isotropic, that is when its Witt index is positive,
          the rotations already have every class as spinor norm (O'Meara
          55:2a), and \(C_{\mathrm{sn}_K}\) is trivial.

        In anisotropic dimensions one and two, ``image()`` supplies the
        represented reflection/norm subgroup and this method returns its
        ordinary abelian-group cokernel projection.
        """
        space = self.quadratic_space()
        target = self.target()
        field = space.base_ring()
        assert field in PrimeFields() and field.characteristic() == 0, (
            f"the K-spinor norm cokernel of {self._lattice!r} is computed here only for K = QQ, and K = {field}"
        )
        dimension = int(space.module_rank())
        trivial = OwnedGroups().C(1)
        onto = target.Mor(trivial)(lambda _square_class: trivial.one())
        match dimension:
            case 1 | 2 if space.witt_index() == 0:
                return self.image().inclusion().cokernel_projection()
            case _ if dimension >= 3 and not space.is_definite():
                return onto
            case _ if dimension >= 3:
                form_is_positive = space.is_positive_definite()
                reflection_classes_are_positive = (
                    self._form_multiplier > 0
                ) == form_is_positive
                if not reflection_classes_are_positive:
                    return onto
                signs = OwnedGroups().C(2)
                negative = signs.group_generators()[0]
                return target.Mor(signs)(
                    lambda square_class: (
                        signs.one() if square_class.representative() > 0 else negative
                    ),
                )
            case _:
                assert space.witt_index() > 0, (
                    f"the K-spinor norm cokernel of {self._lattice!r} is not computed: L_K is an anisotropic space "
                    f"of dimension {dimension}, and the image of sn_K, generated by the classes c(v, v) of its "
                    f"anisotropic vectors and the norms of its rotations (O'Meara 55:2), is not computed"
                )
                return onto

    def cokernel(self):
        r"""Return the \(K\)-spinor norm cokernel \(C_{\mathrm{sn}_K}\)."""
        return self.cokernel_projection().codomain()

    def __repr__(self) -> str:
        return f"1 -> K_sn -> {self.source()} -> {self.target()} -> C_sn -> 1"


def _rational_anisotropic_binary_form_represents(space, value) -> bool:
    r"""Decide whether an anisotropic binary quadratic space over ``QQ`` represents ``value``.

    PARI's ``qfsolve`` decides isotropy of ``q - value*z^2``.  Since the
    binary form ``q`` is anisotropic, any nonzero isotropic vector of this
    ternary form has ``z != 0``, and rescaling by ``z`` is exactly a vector
    represented by ``q`` with norm ``value``.
    """
    from sage.matrix.constructor import matrix
    from sage.quadratic_forms.qfsolve import qfsolve
    from sage.rings.integer import Integer as SageInteger
    from sage.rings.rational_field import QQ as SageQQ

    gram = _engine_component_matrix(space.gram_tensor()).change_ring(SageQQ)
    augmented = matrix(SageQQ, 3, 3)
    for row in range(2):
        for column in range(2):
            augmented[row, column] = gram[row, column]
    augmented[2, 2] = -SageQQ(_engine_element(space.base_ring(), value))
    return not isinstance(qfsolve(augmented), SageInteger)


class IsotropicReductions(OwnedCategoryOverBaseRing):
    r"""Lattices \(K_I=I^\perp/I\) built from a totally isotropic \(\iota:I\hookrightarrow L\).

    An object is the quotient lattice itself, together with the data that
    built it: the embedding \(\iota\), the complement \(I^\perp\), the
    inclusion \(I\hookrightarrow I^\perp\) and the chosen lifts of the
    framing of \(K_I\) into \(I^\perp\).  The parabolic subgroup
    \(P_I=\operatorname{Stab}_{O(L)}(I)\) acts on \(K_I\) through its Levi
    quotient; the kernel of that action together with the restriction to
    \(I\) is the unipotent radical.
    """

    def an_object(self):
        r"""The reduction of \(U\oplus U\) by an isotropic line, which is \(U\)."""
        plane = Lattices(self.base_ring())("U")
        return (plane + plane).basis_vector(0).isotropic_reduction()

    def _repr_object_names(self) -> str:
        return f"isotropic reductions over {self.base_ring()}"

    def super_categories(self):
        return [Lattices(self.base_ring())]

    def _call_(self, isotropic_embedding, *, coordinate_frame=None):
        r"""Return \(K_I=I^\perp/I\) for the totally isotropic embedding \(\iota:I\hookrightarrow L\).

        \(I\) pairs to zero against \(I^\perp\), so the form of \(L\)
        descends to the quotient of \(I^\perp\) by the image of \(I\).  The
        quotient is framed by its invariant-factor generators, lifted into
        \(I^\perp\); its Gram presentation is the form of \(L\) on those
        lifts.  The reduction is built in one construction that retains the
        embedding, the complement \(I^\perp\), the inclusion
        \(I\hookrightarrow I^\perp\), the lifts and the invariant-factor
        normalization of the quotient.
        """
        source = isotropic_embedding.domain()
        target = isotropic_embedding.codomain()
        ring = target.base_ring()
        assert ring is self.base_ring(), (
            f"cannot form I^perp/I in {self} along {isotropic_embedding!r}: its codomain {target!r} is a lattice over {ring}, not over {self.base_ring()}"
        )
        assert source.is_totally_isotropic(), (
            f"cannot form I^perp/I along {isotropic_embedding!r}: the sublattice I = {source!r} is not totally isotropic in {target!r}"
        )

        perpendicular = isotropic_embedding.orthogonal_complement()
        perpendicular_inclusion = perpendicular.inclusion()
        into_perpendicular = source.Mono(perpendicular)(
            lambda label: perpendicular_inclusion.lift(
                isotropic_embedding(source.module_generator(label))
            )
        )
        assert into_perpendicular.is_primitive(), (
            f"I^perp/I is not a free {ring}-module for I = {source!r} in {target!r}: I is not primitive in its orthogonal complement I^perp, so the quotient has torsion"
        )
        quotient = into_perpendicular.cokernel()
        normalization = quotient.invariant_factor_form()
        quotient_module_generators = quotient.smith_form_module_generators()
        rank = int(quotient_module_generators.cardinality())
        labels = Sets.Δ[rank - 1]

        def lift(position):
            quotient_generator = quotient_module_generators[int(position)]
            coordinates = quotient.framing_morphism().lift(quotient_generator)
            return perpendicular.linear_combination(
                {label: coordinates(label) for label in coordinates.support().domain()}
            )

        match coordinate_frame:
            case None:
                lifts = finite_indexed_family(
                    labels,
                    lift,
                    name="Isotropic-reduction coordinate frame",
                )
            case _:
                normalized = normalization.codomain()
                normalized_labels = normalized.module_generating_set()
                presentation_projection = quotient.presentation_projection()

                def selected_lift(position):
                    candidate = perpendicular(coordinate_frame[position])
                    normalized_image = normalization.forward()(
                        presentation_projection(candidate)
                    )
                    expected = normalized.module_generator(
                        normalized_labels[int(position)]
                    )
                    if normalized_image != expected:
                        raise ValueError(
                            f"{candidate!r} is not a lift of quotient generator {position!r} for the isotropic reduction of {isotropic_embedding!r}"
                        )
                    return candidate

                lifts = finite_indexed_family(
                    labels,
                    selected_lift,
                    name="Isotropic-reduction coordinate frame",
                )
        module = ring._fresh_free_module_on(labels)
        match rank:
            case 0:
                gram = _IdentityGram(module)
            case _:
                gram = tensor(
                    ring,
                    (),
                    (rank, rank),
                    (
                        perpendicular.b(lifts[i], lifts[j])
                        for i in range(rank)
                        for j in range(rank)
                    ),
                )
        return _lattice_object(
            Lattices(ring),
            module,
            gram,
            extra_categories=(self,),
            construction_data={
                "isotropic_embedding": isotropic_embedding,
                "orthogonal_complement": perpendicular,
                "isotropic_inclusion": into_perpendicular,
                "coordinate_frame": lifts,
                "reduction_normalization": normalization,
            },
        )

    class ParentMethods:
        def __init__(
            self,
            isotropic_embedding,
            orthogonal_complement,
            isotropic_inclusion,
            coordinate_frame,
            reduction_normalization,
            **rest,
        ) -> None:
            self._preamble_isotropic_embedding = isotropic_embedding
            self._preamble_orthogonal_complement = orthogonal_complement
            self._preamble_isotropic_inclusion = isotropic_inclusion
            self._preamble_coordinate_frame = coordinate_frame
            self._preamble_reduction_normalization = reduction_normalization
            super().__init__(**rest)

        def __eq__(self, other) -> bool:
            r"""Compare reductions by their defining isotropic embedding, not their coordinate frame."""
            if self is other:
                return True
            return (
                hasattr(other, "base_ring")
                and other.base_ring() is self.base_ring()
                and other in IsotropicReductions(self.base_ring())
                and other.isotropic_embedding() is self.isotropic_embedding()
            )

        def __ne__(self, other) -> bool:
            return not self == other

        def __hash__(self) -> int:
            return hash(
                (
                    IsotropicReductions(self.base_ring()),
                    id(self.isotropic_embedding()),
                )
            )

        def isotropic_embedding(self):
            r"""Return \(\iota:I\hookrightarrow L\), the embedding this reduces."""
            return self._preamble_isotropic_embedding

        def isotropic_sublattice(self):
            r"""Return \(I\), the totally isotropic sublattice."""
            return self.isotropic_embedding().domain()

        def orthogonal_complement(self):
            r"""Return \(I^\perp\hookrightarrow L\) as a subobject of the lattice."""
            return self._preamble_orthogonal_complement

        def isotropic_inclusion(self):
            r"""Return \(I\hookrightarrow I^\perp\)."""
            return self._preamble_isotropic_inclusion

        def inclusion(self):
            r"""Return \(I\hookrightarrow I^\perp\), the inclusion defining the quotient."""
            return self.isotropic_inclusion()

        @cached_method
        def integral_hyperbolic_splitting(self):
            r"""Return ``L -> U orthogonal_sum (I^perp/I)`` for a unit cusp.

            The ambient lattice must be even over ``ZZ`` and the isotropic
            line must have divisibility one. If ``e`` generates the line
            and ``f`` is its integral isotropic partner, a quotient lift
            ``z`` is sent to ``z-b(z,f)e``. This is independent of its lift
            modulo ``I`` and lies in ``<e,f>^perp``. The resulting section
            and the hyperbolic-plane embedding assemble through the general
            orthogonal biproduct.

            EXAMPLES::

                sage: L = Lattices(ZZ)("U") + Lattices(ZZ)([[-2]])
                sage: R = L.basis_vector(0).isotropic_reduction()
                sage: splitting = R.integral_hyperbolic_splitting()
                sage: splitting.domain() is L and splitting.codomain().biproduct_factor(1) is R
                True
                sage: all(splitting.inverse()(splitting(x)) == x for x in L.module_generators())
                True
            """
            ambient = self.isotropic_embedding().codomain()
            ring = ambient.base_ring()
            if _engine_ring(ring) is not SageZZ or not ambient.is_even():
                raise ValueError(
                    "an integral hyperbolic splitting requires an even ZZ-lattice"
                )
            line = self.isotropic_sublattice()
            if line.module_rank() != 1:
                raise ValueError(
                    "an integral hyperbolic splitting requires an isotropic line"
                )
            e = self.isotropic_embedding()(line.module_generators()[0])
            if e.div() != ring.one():
                raise ValueError(
                    "an integral hyperbolic splitting requires divisibility one"
                )
            f = e.hyperbolic_partner()
            perpendicular_inclusion = self.orthogonal_complement().inclusion()

            def section_image(label):
                lift = perpendicular_inclusion(self.coordinate_frame()[label])
                return lift - ambient.scalar_multiple(lift.b(f), e)

            section = Lattices(ring).Mor(self, ambient)(section_image)
            plane = Lattices(ring)("U")
            labels = tuple(plane.module_generating_set())
            plane_embedding = plane.Mor(ambient)(
                lambda label: e if label == labels[0] else f
            )
            return ambient.orthogonal_decomposition((plane_embedding, section))

        @cached_method
        def rational_witt_decomposition(self):
            r"""Return a rational hyperbolic splitting adapted to an isotropic line.

            If ``e`` generates ``I`` and ``d=div(e)``, an exact Bezout
            combination of the selected lattice frame gives ``h in L`` with
            ``b(e,h)=d``.  Over the fraction field put

            ``f = h/d - q(h)e/(2d^2)``.

            Then ``e^2=f^2=0`` and ``b(e,f)=1``.  The orthogonal complement of
            ``<e,f>`` is the residual rational summand; it need not be
            anisotropic. For example, splitting one plane out of 2U leaves
            another hyperbolic plane. This relative splitting does not
            compute the maximal Witt index. The
            integral line, perpendicular and quotient remain separately
            retained; no integral splitting is asserted.
            """
            line = self.isotropic_sublattice()
            if int(line.module_rank()) != 1:
                raise ValueError(
                    f"cannot form the rational Witt decomposition of {self!r}: it is implemented for an isotropic sublattice I of rank 1, and I = {line!r} has rank {line.module_rank()}"
                )
            ambient = self.isotropic_embedding().codomain()
            ring = ambient.base_ring()
            if _engine_ring(ring) is not SageZZ:
                raise ValueError(
                    f"cannot form the rational Witt decomposition of {self!r}: the Bezout partner of e is computed only in a lattice over ZZ, and {ambient!r} is over {ring}"
                )
            line_generator = line.module_generators()[0]
            isotropic = self.isotropic_embedding()(line_generator)
            divisibility = isotropic.div()
            bezout_partner = isotropic.bezout_partner()

            fraction_map = ring.fraction_field_map()
            rational = ambient.base_change(fraction_map)
            field = rational.base_ring()

            def rationalize(vector):
                coordinates = vector.to_vector()
                return rational.linear_combination(
                    {
                        label: fraction_map(coordinates(label))
                        for label in coordinates.support().domain()
                    }
                )

            rational_isotropic = rationalize(isotropic)
            rational_bezout = rationalize(bezout_partner)
            d = fraction_map(divisibility)
            two = field(2)
            correction = rational.q(rational_bezout) / (two * d * d)
            rational_partner = rational.scalar_multiple(
                field.one() / d, rational_bezout
            ) - rational.scalar_multiple(correction, rational_isotropic)
            if rational.q(rational_partner) != field.zero():
                raise ArithmeticError(
                    f"the rational Witt partner f = {rational_partner!r} of e = {rational_isotropic!r} in {rational!r} is not isotropic: q(f) = {rational.q(rational_partner)}"
                )
            if rational.b(rational_isotropic, rational_partner) != field.one():
                raise ArithmeticError(
                    f"the pair e = {rational_isotropic!r}, f = {rational_partner!r} in {rational!r} is not a hyperbolic pair: b(e, f) = {rational.b(rational_isotropic, rational_partner)}, not 1"
                )
            hyperbolic_plane = rational.subobject_on(
                (rational_isotropic, rational_partner)
            )
            orthogonal_summand = hyperbolic_plane.orthogonal_complement()
            if int(orthogonal_summand.module_rank()) + 2 != int(rational.module_rank()):
                raise ArithmeticError(
                    f"the orthogonal complement of the hyperbolic plane <e, f> in {rational!r} has rank {orthogonal_summand.module_rank()}, but it must have rank {rational.module_rank()} - 2"
                )
            return RankOneRationalWittDecomposition(
                self,
                bezout_partner,
                rational,
                rational_isotropic,
                rational_partner,
                hyperbolic_plane,
                orthogonal_summand,
            )

        def rational_lifts(self, target, isometry):
            r"""The kernel-group torsor of rational lifts of a marked-line reduction map."""
            from sage_extensions.categories.isotropic_lifts import (
                IsotropicReductionLiftTorsors,
            )

            return IsotropicReductionLiftTorsors(self.base_ring())(
                self, target, isometry
            )

        def coordinate_frame(self):
            r"""Return the chosen lifts of the framing of \(K_I\) into \(I^\perp\)."""
            return self._preamble_coordinate_frame

        def with_coordinate_frame(self, coordinate_frame):
            r"""Return this reduction with another lift frame of the same quotient generators."""
            return IsotropicReductions(self.base_ring())(
                self.isotropic_embedding(),
                coordinate_frame=coordinate_frame,
            )

        def reduction_lifts(self):
            r"""Archived name for :meth:`coordinate_frame`."""
            return self.coordinate_frame()

        def quotient_lattice(self):
            r"""Return \(K_I=I^\perp/I\), which is this lattice."""
            return self

        @cached_method
        def projection(self):
            r"""Return the quotient morphism \(\pi:I^\perp\twoheadrightarrow K_I\)."""
            perpendicular = self.orthogonal_complement()
            quotient = self.isotropic_inclusion().cokernel()
            normalization = self._preamble_reduction_normalization
            normalized = normalization.codomain()
            normalized_labels = normalized.module_generating_set()
            labels = self.module_generating_set()
            presentation_projection = quotient.presentation_projection()

            def image(label):
                normalized_element = normalization.forward()(
                    presentation_projection(perpendicular.module_generator(label))
                )
                coordinates = normalized.framing_morphism().lift(normalized_element)
                return self.linear_combination(
                    {
                        labels[
                            int(normalized_labels.ranking_map()(normalized_label))
                        ]: coordinates(normalized_label)
                        for normalized_label in coordinates.support().domain()
                    }
                )

            return perpendicular.module_category().Mor(perpendicular, self)(image)

        @cached_method
        def parabolic_subgroup(self):
            r"""Return \(P_I=\operatorname{Stab}_{O(L)}(I)\), the setwise stabilizer of \(I\)."""
            embedding = self.isotropic_embedding()
            return embedding.codomain().O().setwise_stabilizer(embedding)

        @cached_method
        def pointwise_parabolic_subgroup(self):
            r"""Return ``P_I^1``, the subgroup fixing the isotropic sublattice pointwise."""
            embedding = self.isotropic_embedding()
            return embedding.codomain().O().pointwise_stabilizer(embedding)

        @cached_method
        def perpendicular_restriction(self):
            r"""Return ``r:P_I -> O(I^perp)``, restriction to the full perpendicular.

            This is deliberately not the joint action on ``I`` and
            ``I^perp/I``.  Its kernel consists of ambient isometries fixing
            every vector of ``I^perp`` pointwise.
            """
            parabolic = self.parabolic_subgroup()
            perpendicular = self.orthogonal_complement()
            inclusion = perpendicular.inclusion()
            target = perpendicular.Aut()

            def restrict(isometry):
                return target(
                    lambda label: inclusion.lift(
                        isometry(inclusion(perpendicular.module_generator(label)))
                    )
                )

            return parabolic.Mor(target)(restrict)

        @cached_method
        def _pointwise_perpendicular_kernel_data(self):
            r"""Retain the complete integral linear solution module for ``ker(r)``.

            Put ``J=I^perp`` and ``R=rad(J)``.  The quotient ``L/J`` is
            required to be free in the represented integral computation.  An
            isometry fixing ``J`` pointwise is uniquely ``1+N`` with
            ``N:L/J -> R``.  For chosen quotient lifts ``f_a`` the remaining
            isometry equations are

            ``b(N f_a, f_b) + b(f_a, N f_b) = 0``.

            They are homogeneous integral linear equations.  Their kernel is
            therefore the complete parameter module; no quotient-action or
            arithmetic image computation enters this construction.
            """
            ambient = self.isotropic_embedding().codomain()
            ring = ambient.base_ring()
            if _engine_ring(ring) is not SageZZ:
                raise TypeError(
                    f"the pointwise-perpendicular kernel is presently solved integrally over ZZ, but {ambient} is over {ring}"
                )
            perpendicular = self.orthogonal_complement()
            inclusion = perpendicular.inclusion()
            quotient = inclusion.cokernel()
            if quotient.is_torsion_free() is not True:
                raise ValueError(
                    f"the quotient {ambient}/{perpendicular} must be torsion-free for the pointwise-perpendicular kernel construction"
                )
            quotient_trivialization = quotient.finite_free_trivialization()
            quotient_free = quotient_trivialization.codomain()
            quotient_projection = inclusion.cokernel_projection()
            quotient_map = quotient_trivialization.forward() * quotient_projection
            quotient_labels = tuple(quotient_free.module_generating_set())
            quotient_lifts = {
                label: quotient_projection.preimage(
                    quotient_trivialization.inverse()(
                        quotient_free.module_generator(label)
                    )
                )
                for label in quotient_labels
            }

            radical = perpendicular.radical()
            radical_inclusion = radical.inclusion()
            radical_labels = tuple(radical.module_generating_set())
            radical_vectors = {
                label: inclusion(radical_inclusion(radical.module_generator(label)))
                for label in radical_labels
            }

            parameter_labels = finite_ordered_set(tuple(
                (quotient_label, radical_label)
                for quotient_label in quotient_labels
                for radical_label in radical_labels
            ))
            parameters = ring.free_module(parameter_labels)
            equation_labels = finite_ordered_set(tuple(
                (left, right)
                for left_position, left in enumerate(quotient_labels)
                for right in quotient_labels[left_position:]
            ))
            equations = ring.free_module(equation_labels)

            def equation_image(variable_label):
                quotient_label, radical_label = variable_label
                radical_vector = radical_vectors[radical_label]
                coefficients = {}
                for left, right in equation_labels:
                    coefficient = ring.zero()
                    if quotient_label == left:
                        coefficient += ambient.b(radical_vector, quotient_lifts[right])
                    if quotient_label == right:
                        coefficient += ambient.b(quotient_lifts[left], radical_vector)
                    if coefficient != ring.zero():
                        coefficients[(left, right)] = coefficient
                return equations.linear_combination(coefficients)

            equation = parameters.module_category().Mor(parameters, equations)(equation_image)
            solution = equation.kernel()

            def correction(parameter, quotient_label):
                coordinates = solution.inclusion()(parameter).to_vector()
                result = ambient.zero()
                for radical_label in radical_labels:
                    coefficient = coordinates((quotient_label, radical_label))
                    if coefficient != ring.zero():
                        result += ambient.scalar_multiple(
                            coefficient, radical_vectors[radical_label]
                        )
                return result

            def shift(parameter, element):
                quotient_coordinates = quotient_map(element).to_vector()
                result = ambient.zero()
                for quotient_label in quotient_labels:
                    coefficient = quotient_coordinates(quotient_label)
                    if coefficient != ring.zero():
                        result += ambient.scalar_multiple(
                            coefficient, correction(parameter, quotient_label)
                        )
                return result

            def isometry(parameter):
                # The Eichler-type transvection is given by its generator images
                # in O(L) itself (``CON-17``); its inverse is the transvection
                # at ``-parameter``, computed on request.
                forward = ambient.Mor(ambient)({
                    label: ambient.module_generator(label)
                    + shift(parameter, ambient.module_generator(label))
                    for label in ambient.module_generating_set()
                })
                return ambient.Isom(ambient)._from_inverse_computation(
                    forward, lambda: isometry(-parameter)
                )

            return solution, isometry

        def pointwise_perpendicular_parameter_module(self):
            r"""Return the complete integral parameter module for ``ker(r)``."""
            return self._pointwise_perpendicular_kernel_data()[0]

        def pointwise_perpendicular_isometry(self, parameter):
            r"""Evaluate one integral kernel parameter as an isometry of the ambient lattice."""
            parameters, isometry = self._pointwise_perpendicular_kernel_data()
            return isometry(parameters(parameter))

        @cached_method
        def pointwise_perpendicular_kernel(self):
            r"""Return ``ker(P_I -> O(I^perp))`` with effective integral generators.

            The selected generators are the images of a complete generating
            family of the homogeneous integral parameter module.  This is the
            pointwise kernel on the whole perpendicular, not the kernel of the
            joint action on ``I`` and ``I^perp/I``.
            """
            parameters = self.pointwise_perpendicular_parameter_module()
            ambient = self.isotropic_embedding().codomain()
            generators = tuple(
                self.pointwise_perpendicular_isometry(
                    parameters.module_generator(label)
                )
                for label in parameters.module_generating_set()
            )
            return ambient.O().subgroup(generators)

        @cached_method
        def levi_action(self):
            r"""Return \(\rho:P_I\to O(K_I)\), \(g\mapsto\bar g\), the action on \(I^\perp/I\).

            An isometry stabilizing \(I\) stabilizes \(I^\perp\), so it
            descends to the quotient.  The descended map is read on the
            chosen lifts.

            For a line \(I\) the owner selects two choices on the
            morphism, both computed only on first request: the set section
            :meth:`_levi_section` on the image (``select_section``; the image is
            the subset of \(O(K_I)\) cut out by :meth:`_levi_image_contains`),
            and generators of ``kernel()`` from :meth:`_levi_kernel_generators`
            (its selected generating resolution).  For a higher-rank \(I\) with
            \(O(K_I)\) not placed finite, the selected section is the one that
            asserts (port #18 owns those extension equations).
            """
            from sage_extensions.categories.group.groups import OwnedFiniteGroups

            perpendicular = self.orthogonal_complement()
            perpendicular_inclusion = perpendicular.inclusion()
            lifts = self.reduction_lifts()
            projection = self.projection()
            automorphisms = self.Aut()

            def descend(isometry):
                return automorphisms(
                    lambda label: projection(
                        perpendicular_inclusion.lift(
                            isometry(perpendicular_inclusion(lifts(label)))
                        )
                    )
                )

            levi = self.parabolic_subgroup().Mor(automorphisms)(descend)
            reduces_a_line = self.isotropic_sublattice().module_rank() == NN(1)
            finite_reduction_group = automorphisms in OwnedFiniteGroups()
            # When I has rank >= 2 and O(K_I) is placed finite, ``lift``'s own
            # finite-image word section applies and nothing is selected.
            if reduces_a_line or not finite_reduction_group:
                image = automorphisms.condition_set(self._levi_image_contains)
                levi.select_section(Sets().Mor(image, levi.domain())(self._levi_section))
            if reduces_a_line:
                kernel = levi.kernel()
                kernel.select_group_generators(
                    lambda: finite_ordered_set(
                        tuple(kernel(generator) for generator in self._levi_kernel_generators())
                    )
                )
            return levi

        @cached_method
        def _levi_fibres(self, isometry):
            r"""The two lift torsors over ``isometry``: \(F^+(\gamma)\), then \(F^-(\gamma)\).

            For a primitive isotropic line \(I=\mathbf Z e\) every \(g\in P_I\)
            sends \(e\) to \(\pm e\), so \(\rho^{-1}(\gamma)\) is the union of the
            integral loci of the marked-line lift torsor ``rational_lifts(self,
            gamma)`` (lifts fixing \(e\)) and of the torsor to the reduction of
            the same line marked by \(-e\) (Gritsenko--Hulek--Sankaran,
            arXiv:0810.1614, section 3.1, (4)--(5), as cited in
            ``isotropic_lifts.py``).  Each integral locus is empty exactly when
            its finite residue locus is.

            For \(I\) of rank at least 2, a lift must also choose the action on
            \(I\) and solve the extension equations \(B = XA + A^tX^t\); those
            are the specialized extension equations of port #18, and research
            has no route here.
            """
            rank = self.isotropic_sublattice().module_rank()
            assert rank == NN(1), (
                f"cannot lift {isometry!r} from O(K_I) to P_I for K_I = {self!r}: I has rank {rank}, "
                f"and O(K_I) is not placed finite, so a lift solves the extension equations of an "
                f"isotropic sublattice of rank at least 2, which are sage-indefinite-port #18's "
                f"computation"
            )
            opposite, identification = self._opposite_marking()
            return (
                self.rational_lifts(self, isometry),
                self.rational_lifts(opposite, identification * isometry),
            )

        def _levi_image_contains(self, isometry):
            r"""Whether ``isometry`` lies in the image of :meth:`levi_action`: some fibre of :meth:`_levi_fibres` has an integral member."""
            return any(
                fibre._integral_base_point_or_none() is not None
                for fibre in self._levi_fibres(isometry)
            )

        def _levi_section(self, isometry):
            r"""One point of \(\rho^{-1}(\gamma)\): the integral base point of the first nonempty fibre of :meth:`_levi_fibres`.

            A set-theoretic section of \(\rho\) on its image, not a
            homomorphic splitting.  Its domain, the subset of \(O(K_I)\) cut
            out by :meth:`_levi_image_contains`, has already decided that a
            fibre is nonempty.
            """
            lattice = self.isotropic_embedding().codomain()
            fibre = next(
                fibre
                for fibre in self._levi_fibres(isometry)
                if fibre._integral_base_point_or_none() is not None
            )
            return self.parabolic_subgroup()(lattice.integral_isometry(fibre.integral_base_point()))

        def _levi_kernel_generators(self):
            r"""A generating family of \(\ker\rho\) for an isotropic line \(I=\mathbf Z e\).

            \(\ker\rho=F^+(1)\cup F^-(1)\).  \(F^+(1)\) is the integral
            Eichler transvection kernel \(K_{\mathbf Z}\), generated by
            ``integral_kernel_group_generators`` of the identity marking;
            \(F^-(1)\) is empty or a coset \(\tau K_{\mathbf Z}\), so one point
            \(\tau\) of it is added when it is nonempty.
            """
            lattice = self.isotropic_embedding().codomain()
            parabolic = self.parabolic_subgroup()
            fixing, reversing = self._levi_fibres(self.Aut().one())
            transvections = (
                parabolic(lattice.integral_isometry(transvection))
                for transvection in fixing.integral_kernel_group_generators()
            )
            reversal = (
                ()
                if reversing.integral_members().is_empty() is True
                else (parabolic(lattice.integral_isometry(reversing.integral_base_point())),)
            )
            return finite_ordered_set((*transvections, *reversal))

        @cached_method
        def _opposite_marking(self):
            r"""The reduction of the same line marked by \(-e\), with \(K_I\to K_I'\) induced by \(\mathrm{id}_{I^\perp}\).

            Both reductions are quotients of the same \(I^\perp\subseteq L\)
            by the same line, so the identity of \(I^\perp\) induces an
            isometry between them; it is read on the chosen lifts.  The
            marked vector \(e\) is the image of the single module generator
            of the line \(I\).
            """
            lattice = self.isotropic_embedding().codomain()
            line = self.isotropic_sublattice()
            labels = line.module_generating_set()
            assert labels.cardinality() == NN(1), (
                f"the opposite marking of {self!r} reverses a marked isotropic line, but I = {line!r} "
                f"has {labels.cardinality()} module generators"
            )
            marked = self.isotropic_embedding()(line.module_generator(labels.an_element()))
            opposite = lattice.primitive_isotropic_subobject(-marked).isotropic_reduction()
            own = self.orthogonal_complement().inclusion()
            theirs = opposite.orthogonal_complement().inclusion()
            lifts = self.reduction_lifts()
            projection = opposite.projection()
            identification = self.Isom(opposite)(
                lambda label: projection(theirs.lift(own(lifts(label))))
            )
            return opposite, identification

        def levi_image(self):
            r"""Return \(\operatorname{im}(P_I\to O(K_I))\), the image of :meth:`levi_action`.

            The image is generated by the images of the generators the caller
            selected on ``parabolic_subgroup()``
            (``select_group_resolution``); no generators of \(P_I\) are
            computed here, and none is requested from the indefinite
            stabilizer computation, which is what consumes this image.  The
            image in a trivial \(O(K_I)\) is trivial without any.
            """
            return self.levi_action().image()

        def levi_image_generators(self):
            r"""Return the generators of :meth:`levi_image`: the images of the selected generators of \(P_I\)."""
            return self.levi_image().selected_subgroup_generators()

        def levi_lift(self, isometry):
            r"""Return a lift of ``isometry`` to \(P_I\) when it lies in :meth:`levi_image`, else ``None``.

            The lift is ``levi_action().lift``, a set-theoretic section, not
            a homomorphic splitting: for a line \(I\) the torsor section
            :meth:`_levi_section`, otherwise the word section of the finite
            image computed from the selected generators of \(P_I\), which
            needs \(O(K_I)\) finite, as when \(K_I\) is definite.
            """
            if isometry.parent() is not self.Aut():
                raise ValueError(
                    f"cannot lift {isometry!r} to P_I: it lies in {isometry.parent()!r}, not in O(K_I) for K_I = {self!r}"
                )
            if isometry not in self.levi_image():
                return None
            return self.levi_action().lift(isometry)

        @cached_method
        def _rank_one_combined_levi_lift_table(self):
            r"""Lifts in \(P_I\) indexed by the joint image in \(GL(I)\times O(K_I)\), for rank one.

            Computed from the generators selected on ``parabolic_subgroup()``
            by the finite-image traversal of \(g\mapsto(\rho_I(g),\bar g)\);
            \(GL(I)=\{\pm1\}\) for a line, so the image has at most
            \(2|O(K_I)|\) elements.
            """
            line = self.isotropic_sublattice()
            if int(line.module_rank()) != 1:
                raise ValueError(
                    f"cannot tabulate the lifts to P_I for K_I = {self!r}: this is implemented for an isotropic sublattice I of rank 1, and I = {line!r} has rank {line.module_rank()}"
                )
            action = self.isotropic_action()
            levi = self.levi_action()

            def joint_image(isometry):
                return (action(isometry), levi(isometry))

            def multiply(left, right):
                return (left[0] * right[0], left[1] * right[1])

            return self.parabolic_subgroup().finite_image_lifts(
                joint_image,
                multiply=multiply,
                image_bound=2 * int(self.Aut().cardinality()),
            )

        @cached_method
        def pointwise_levi_image(self):
            r"""Return the image of ``P_I^1`` in ``O(K_I)`` for a rank-one reduction.

            ``P_I^1`` is the kernel of :meth:`isotropic_action`, so its image
            is the second component of the joint image over the identity of
            \(GL(I)\).  The image in a trivial \(O(K_I)\) is trivial.
            """
            automorphisms = self.Aut()
            if automorphisms.is_trivial() is True:
                return automorphisms.trivial_subgroup()
            identity_on_line = self.isotropic_action().codomain().one()
            return automorphisms.subgroup(
                target
                for (on_line, target) in self._rank_one_combined_levi_lift_table()
                if (on_line == identity_on_line) is True
            )

        def pointwise_levi_lift(self, isometry):
            r"""Return a lift in ``P_I^1`` exactly when ``isometry`` lies in its Levi image."""
            if isometry.parent() is not self.Aut():
                raise ValueError(
                    f"cannot lift {isometry!r} to P_I^1: it lies in {isometry.parent()!r}, not in O(K_I) for K_I = {self!r}"
                )
            if (isometry == self.Aut().one()) is True:
                return self.pointwise_parabolic_subgroup().one()
            if isometry not in self.pointwise_levi_image():
                return None
            identity_on_line = self.isotropic_action().codomain().one()
            return self._rank_one_combined_levi_lift_table()[identity_on_line, isometry]

        @cached_method
        def parabolic_levi_exact_sequence(self):
            r"""Return ``1 -> U_I -> P_I^1 -> M_I^1 -> 1`` in the represented rank-one regime."""
            return RankOneParabolicLeviExactSequence(self)

        @cached_method
        def unipotent_kernel(self):
            r"""Return \(U_I=\ker(P_I\to GL(I)\times O(K_I))\), the unipotent radical."""
            self.isotropic_embedding()
            levi = self.levi_action()
            identity = self.Aut().one()
            return self.pointwise_parabolic_subgroup().predicate_subgroup(
                lambda isometry: levi(isometry) == identity,
                "g fixes I pointwise and acts trivially on I^perp/I",
            )

        def lift_isometry(self, isometry):
            r"""Return \(g\in P_I\) with \(\bar g=\) ``isometry``, when \(L\) splits along the lifts.

            The chosen lifts span \(K'\subseteq I^\perp\), a copy of
            \(K_I\).  When \(K'\) is primitive and \(M=K'^\perp\) is
            unimodular, \(L=M\perp K'\), so \(g=\mathrm{id}_M\perp\sigma\)
            lies in \(P_I\) and has the required Levi image; \(M\) then
            contains \(I\).  Without such a splitting the Levi quotient need
            not lift, which the assertion states.

            Unimodularity of \(M\) is what makes the splitting computable:
            the correlation \(M\to M^\vee\) is then an isomorphism, and the
            \(M\)-component of \(x\in L\) is the correlation's inverse
            applied to \(b(x,-)|_M\).
            """
            automorphisms = self.Aut()
            assert isometry.parent() is automorphisms, (
                f"cannot lift {isometry!r} to P_I: it lies in {isometry.parent()!r}, not in O(K_I) for K_I = {self!r}"
            )
            lattice = self.isotropic_embedding().codomain()
            perpendicular_inclusion = self.orthogonal_complement().inclusion()
            lifts = self.reduction_lifts()
            labels = self.module_generating_set()
            embedded_lifts = finite_indexed_family(
                labels,
                lambda label: perpendicular_inclusion(lifts(label)),
                name="Embedded isotropic-reduction lifts",
            )
            complement = lattice.subobject_on(embedded_lifts)
            unimodular_summand = complement.orthogonal_complement()
            assert complement.is_primitive() and unimodular_summand.is_unimodular(), (
                f"cannot lift {isometry!r} from O(K_I) to P_I by id_M + sigma for K_I = {self!r}: the lifts of K_I span a sublattice K' of {lattice!r} that is not primitive or whose orthogonal complement M is not unimodular, so {lattice!r} does not split as M + K'"
            )
            complement_inclusion = complement.inclusion()
            summand_inclusion = unimodular_summand.inclusion()
            into_complement = self.module_category().Mor(self, complement)(
                lambda label: complement_inclusion.lift(embedded_lifts(label))
            )
            correlation = unimodular_summand.correlation_isomorphism()
            summand_dual = correlation.forward().codomain()

            def summand_component(vector):
                covector = summand_dual.linear_combination(
                    {
                        label: coefficient
                        for label in summand_dual.module_generating_set()
                        if (
                            coefficient := lattice.b(
                                vector,
                                summand_inclusion(
                                    unimodular_summand.module_generator(label)
                                ),
                            )
                        )
                    }
                )
                return correlation.inverse()(covector)

            def image(label):
                vector = lattice.module_generator(label)
                fixed_part = summand_component(vector)
                embedded_fixed = summand_inclusion(fixed_part)
                moved_part = into_complement.lift(
                    complement_inclusion.lift(vector - embedded_fixed)
                )
                return embedded_fixed + complement_inclusion(
                    into_complement(isometry(moved_part))
                )

            lifted = lattice.O()(image)
            assert lifted in self.parabolic_subgroup(), (
                f"the isometry id_M + sigma of {lattice!r} built from {isometry!r} does not stabilize I, so it is not in P_I for K_I = {self!r}"
            )
            assert self.levi_action()(lifted) == isometry, (
                f"the isometry id_M + sigma of {lattice!r} descends to {self.levi_action()(lifted)!r} on I^perp/I = {self!r}, not to {isometry!r}"
            )
            return lifted


class NoncrystallographicRootLattices(OwnedCategoryOverBaseRing):
    r"""Finite noncrystallographic root lattices over their exact coefficient order."""

    def an_object(self):
        return Lattices.root_lattice("H", 3)

    def _repr_object_names(self):
        return f"noncrystallographic root lattices over {self.base_ring()}"

    def super_categories(self):
        return [Lattices(self.base_ring()).FinitelyGenerated().Nondegenerate().Even()]

    class ParentMethods:
        def __init__(self, coxeter_type, **rest) -> None:
            self._preamble_coxeter_type = coxeter_type
            super().__init__(**rest)

        def coxeter_type(self):
            return self._preamble_coxeter_type

        def simple_roots(self):
            return self.module_generators()

        @cached_method
        def roots(self):
            r"""Return the finite H-root system from its Coxeter reflection group.

            Sage's maintained finite Coxeter-group implementation computes all roots
            in the basis of simple roots.  The H3/H4 coefficients lie in the
            golden integer order defining this lattice; crossing them through
            that order both preserves the selected framing and rejects an
            accidental nonintegral coordinate.
            """
            family, rank = self.coxeter_type()
            coxeter = Groups.Coxeter(
                [family, rank],
                base_ring=self.base_ring().fraction_field(),
            )
            backend_roots = _engine_group(coxeter).roots()
            ring = self.base_ring()
            engine_order = _engine_ring(ring)
            labels = tuple(self.module_generating_set())
            return finite_ordered_set(
                tuple(
                    self.linear_combination(
                        {
                            label: _owned_engine_element(
                                ring, engine_order(coefficient)
                            )
                            for label, coefficient in zip(
                                labels, tuple(root), strict=True
                            )
                            if coefficient
                        }
                    )
                    for root in backend_roots
                )
            )

        def coxeter_number(self):
            family, rank = self.coxeter_type()
            if family != "H" or rank not in (3, 4):
                raise ValueError(
                    f"{self!r} has Coxeter type {family}{rank}, but the Coxeter number is implemented here only for the noncrystallographic types H3 and H4"
                )
            return self.base_ring().base_ring()(10 if rank == 3 else 30)

        def simple_reflections(self):
            return finite_ordered_set(
                tuple(self.reflection(root) for root in self.simple_roots())
            )


class RootLattices(OwnedCategory):
    r"""Negative-definite ADE root lattices with a chosen simple-root framing."""

    def an_object(self):
        r"""Return the canonical ``A2`` root lattice as an inhabitant."""
        return Lattices(_owned_integers())("A2")

    @classmethod
    def _repr_object_names(cls):
        return "root lattices"

    def super_categories(self):
        return [Lattices(_owned_integers()).FinitelyGenerated().Nondegenerate().Even()]

    class ParentMethods:
        def __init__(self, root_system_type_name, **rest) -> None:
            self._preamble_root_system_type_name = root_system_type_name
            super().__init__(**rest)

        def root_system_type_name(self):
            r"""Return the name of the type of the root system of the simple roots, as ``A2`` or ``A2xA1``."""
            return self._preamble_root_system_type_name

        def _engine_cartan_type(self):
            r"""Return the private engine Cartan type named by :meth:`root_system_type_name`."""
            return CartanType(self.root_system_type_name())

        @cached_method
        def dynkin_diagram(self):
            r"""Return the Dynkin diagram of the simple roots.

            It is the Coxeter diagram of the simple roots that retains the
            roots: its vertices are the simple roots, with their squares and
            pairings, which is the datum a Dynkin diagram draws; its connected components
            are the irreducible components of the root system.
            """
            from sage_extensions.categories.coxeter_diagrams import (
                CoxeterDiagrams,
            )

            return CoxeterDiagrams().from_roots(self.simple_roots())

        def simple_roots(self):
            r"""Return the selected framing, which is the chosen simple system."""
            return self.module_generators()

        def coxeter_number(self):
            cartan_type = self._engine_cartan_type()
            if not cartan_type.is_irreducible():
                raise ValueError(
                    f"{self!r} has no single Coxeter number: its root system of type {self.root_system_type_name()} is reducible, and each irreducible component has its own Coxeter number"
                )
            return self.base_ring()(int(cartan_type.coxeter_number()))

        def highest_root(self):
            r"""Return the highest root in the selected simple-root framing.

            It is the image under the framing morphism \(R^n \to L\), whose
            basis vectors go to the simple roots, of the coefficient vector of
            the highest root in the basis of simple roots.
            """
            from sage.combinat.root_system.root_system import RootSystem

            cartan_type = self._engine_cartan_type()
            if not cartan_type.is_irreducible():
                raise ValueError(
                    f"{self!r} has no single highest root: its root system of type {self.root_system_type_name()} is reducible, and each irreducible component has its own highest root"
                )
            coefficients = (
                RootSystem(cartan_type).root_lattice().highest_root().to_vector()
            )
            vector = self.framing_source()(
                {
                    label: self.base_ring()(int(coefficient))
                    for label, coefficient in zip(
                        self.module_generating_set(), coefficients, strict=True
                    )
                }
            )
            return self.framing_morphism()(vector)

        def simple_reflections(self):
            return finite_ordered_set(
                tuple(self.reflection(root) for root in self.simple_roots())
            )

        def fundamental_weights(self):
            r"""Return the weights dual to the simple coroots."""

            norm = self.simple_roots()[0].norm()
            if norm not in (2, -2):
                raise ValueError(
                    f"cannot form the fundamental weights of {self!r}: its simple roots must have square +2 or -2 in a simply-laced root lattice, but the first has square {norm}"
                )
            sign = norm // self.base_ring()(2)
            return FiniteOrderedSets().from_indexed(
                self.dual_basis(),
                lambda weight: weight.parent().scalar_multiple(sign, weight),
            )

    class ElementMethods:
        def is_positive_root(self) -> bool:
            coordinates = self.to_vector()
            return bool(
                self.is_root()
                and all(
                    coordinates(label) >= 0 for label in coordinates.support().domain()
                )
            )

        def is_negative_root(self) -> bool:
            return bool((-self).is_positive_root())

        def height(self):
            coordinates = self.to_vector()
            return sum(
                (coordinates(label) for label in coordinates.support().domain()),
                self.parent().base_ring().zero(),
            )

        def coroot(self):
            r"""Return ``alpha^vee = 2*b(alpha,-)/b(alpha,alpha)`` in ``L^#``."""
            parent = self.parent()
            if not self.is_root():
                raise ValueError(
                    f"{self!r} has no coroot in {parent!r}: the coroot 2 b(alpha, -)/b(alpha, alpha) is defined for a root, and {self!r} is not a root"
                )
            norm = self.norm()
            two = parent.base_ring()(2)
            dual_lattice = parent.dual_lattice()
            return dual_lattice.linear_combination(
                {
                    label: two * parent.module_generator(label).b(self) / norm
                    for label in parent.module_generating_set()
                    if parent.module_generator(label).b(self) != 0
                }
            )
