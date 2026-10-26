r"""The primitive extension cut out by a lattice isometry, and its centralizer.

For an isometry ``f`` of a nondegenerate lattice ``L`` the invariant lattice
``L^f`` and its orthogonal complement are primitive sublattices whose
orthogonal sum sits in ``L`` with finite index.  Nikulin's correspondence
presents that primitive extension by the anti-isometry

``gamma : H_+ -> H_-(-1)``,   ``H_+ <= A_{L^f}``,  ``H_- <= A_{(L^f)^perp}``,

whose graph is ``L/(L^f + (L^f)^perp)``.  The centralizer ``O(L,f)`` is then
the group of pairs ``(g_+, g_-)`` in ``O(L^f) x O((L^f)^perp)`` whose induced
discriminant automorphisms commute with ``gamma``, equivalently which carry
the graph onto itself.

This object is the isometry-cut sibling of ``VectorPrimitiveExtension``, which
records the same primitive-extension data for the decomposition cut out by one
anisotropic vector.  The two share the owned pieces they stand on: the
invariant lattice and formed coinvariants of the isometry, ``glue_map`` for
the anti-isometry, and ``centralizer`` for the subgroup.

What this file adds is the decomposition as one object, both halves of that
isomorphism -- the restriction morphisms ``O(L,f) -> O(L^f)`` and
``O(L,f) -> O((L^f)^perp)`` forwards, and ``centralizer_element`` back -- and
the cyclotomic summands ``ker Phi_d(f)`` of a finite-order isometry.
"""

from sage.arith.misc import divisors, euler_phi
from sage.misc.cachefunc import cached_function, cached_method
from sage.structure.sage_object import SageObject

from sage_extensions.categories.group.g_sets import FiniteGSets
from sage_extensions.categories.isotropic_orbits import _same_subobject
from sage_extensions.categories.modules.pure.modules import ModuleSubobjects
from sage_extensions.categories.rings.ring_foundation import _owned_integers
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import finite_indexed_family
from sage_extensions.categories.sets.set_categories import Sets
from sage_extensions.owned_category import _object_of



@cached_function
def _equivariant_lattice_acting_group():
    r"""Return the canonical infinite cyclic group acting on an equipped lattice."""
    from sage_extensions.categories.group.groups import OwnedGroups

    return OwnedGroups().Free(1, names="t")


def _equivariant_lattice(lattice, isometry):
    r"""Return ``(L,f)`` as the actual ``ZZ``-object in ``Lattices(R)`` defined by ``f``."""
    from sage_extensions.categories.functors.group_actions import GroupActionFunctor
    from sage_extensions.categories.group.g_objects import GObjects
    from sage_extensions.categories.lattices import Lattices

    isometry = lattice.O()(isometry)
    if isometry.domain() is not lattice or isometry.codomain() is not lattice:
        raise ValueError(
            f"cannot make {lattice} a lattice with isometry via {isometry}: f must be an "
            f"automorphism L -> L, but it maps {isometry.domain()} -> {isometry.codomain()}"
        )
    group = _equivariant_lattice_acting_group()
    orthogonal_group = lattice.O()
    generator = next(iter(group.group_generators()))

    def action(group_element):
        result = orthogonal_group.one()
        for letter in group.reduced_word(group_element):
            assert letter == generator or letter == ~generator, (
                f"the letter {letter} of the word for {group_element} is neither the "
                f"generator {generator} of the free group {group} of rank one nor its inverse"
            )
            step = isometry if letter == generator else ~isometry
            result = step * result
        return result

    category = Lattices(lattice.base_ring())
    functor = GroupActionFunctor(group, category, lattice, action)
    return GObjects(group, category)(functor)


def _restrict_isometry(isometry, sublattice):
    r"""Return the restriction of ``isometry`` to one stable represented sublattice."""
    lattice = isometry.domain()
    if isometry.codomain() is not lattice:
        raise ValueError(
            f"cannot restrict {isometry} to {sublattice}: restriction needs an "
            f"automorphism L -> L, but {isometry} maps {lattice} -> {isometry.codomain()}"
        )
    assert sublattice in ModuleSubobjects(lattice.base_ring()), (
        f"cannot restrict {isometry} to {sublattice}: it is not a submodule over "
        f"{lattice.base_ring()} (it is in {sublattice.category()})"
    )
    inclusion = sublattice.inclusion()
    if inclusion.codomain() is not lattice:
        raise ValueError(
            f"cannot restrict {isometry} to {sublattice}: it is a sublattice of "
            f"{inclusion.codomain()}, not of {lattice}"
        )
    images = {}
    for label in sublattice.module_generating_set():
        embedded = inclusion(sublattice.module_generator(label))
        moved = isometry(embedded)
        if not inclusion.is_in_image(moved):
            raise ValueError(
                f"cannot restrict {isometry} to {sublattice}: the sublattice is not "
                f"f-stable, since f sends {embedded} to {moved}, which is outside it"
            )
        images[label] = inclusion.lift(moved)
    return sublattice.O()(images)


class _CentralizerOrbitDecompositionEngine:
    r"""Private finite-set realization of a centralizer orbit quotient."""

    def __iter__(self):
        return iter(self._orbit_set)

    def __contains__(self, orbit) -> bool:
        return orbit in self._orbit_set

    is_parent_of = __contains__

    def _element_constructor_(self, orbit):
        if orbit not in self:
            raise ValueError(f"{orbit} is not an orbit of {self}")
        return orbit

    def orbits(self):
        return self


class _EquivariantVectorOrbitDecompositionEngine(_CentralizerOrbitDecompositionEngine):
    r"""The exact vector-orbit decomposition under ``O(L,f)`` when finite.

    The centralizer of ``f`` is listed only when the full orthogonal group is
    finite, equivalently in the definite regime supported by the existing
    subgroup engine.  No finite approximation is used for an indefinite
    arithmetic centralizer.
    """

    def __init__(self, isometry, square, **rest) -> None:
        self._isometry = isometry
        lattice = isometry.domain()
        if isometry.codomain() is not lattice:
            raise ValueError(
                f"cannot form vector orbits under the centralizer of {isometry}: it must "
                f"be an automorphism L -> L, but it maps {lattice} -> {isometry.codomain()}"
            )
        self._square = lattice.base_ring()(square)
        centralizer = isometry.centralizer_group()
        points = finite_ordered_set(
            tuple(lattice.vectors_of_square(self._square))
        )
        self._action = FiniteGSets(centralizer)(
            points,
            lambda automorphism, vector: automorphism(vector),
        )
        self._orbit_set = self._action.orbits()
        super().__init__(facade=True, **rest)

    def isometry(self):
        return self._isometry

    def lattice(self):
        return self.isometry().domain()

    def square(self):
        return self._square

    def group(self):
        return self.isometry().centralizer_group()

    def action(self):
        return self._action

    def point(self, vector):
        lattice = self.lattice()
        if vector.parent() is not lattice:
            vector = lattice(vector)
        if vector.q() != self.square():
            raise ValueError(
                f"{vector} has square {vector.q()}, so it is not in the shell of vectors "
                f"of square {self.square()} in {lattice}"
            )
        return self.action()(vector)

    def representatives(self):
        return finite_ordered_set(tuple(orbit.representative() for orbit in self))

    def orbit_of(self, vector):
        return self.action().orbits().orbit_of(self.point(vector))

    def stabilizer(self, representative):
        return self.orbit_of(representative).stabilizer()

    def transporter(self, source, target):
        source_orbit = self.orbit_of(source)
        target_orbit = self.orbit_of(target)
        if source_orbit != target_orbit:
            return None
        return self.action().transporter_witness(self.point(source), self.point(target))

    def _repr_(self) -> str:
        return f"Vector orbits of square {self.square()} under {self.group()}: {self.representatives()}"


def _equivariant_vector_orbit_decomposition(isometry, square):
    return _object_of(
        Sets().Finite(),
        _engine=(Sets(), _EquivariantVectorOrbitDecompositionEngine, None),
        isometry=isometry,
        square=square,
    )


def _transport_sublattice(automorphism, sublattice):
    return (automorphism * sublattice.inclusion()).image()


class EquivariantSublatticeFlag(SageObject):
    r"""A nested finite flag of represented sublattices stable under ``f``."""

    def __init__(self, isometry, terms) -> None:
        terms = tuple(terms)
        if not terms:
            raise ValueError(
                f"a flag of f-stable sublattices for {isometry} needs at least one term; "
                f"none was given"
            )
        previous = None
        for term in terms:
            _restrict_isometry(isometry, term)
            if previous is not None:
                previous.inclusion().factor_through(term.inclusion())
                if int(previous.module_rank()) >= int(term.module_rank()):
                    raise ValueError(
                        f"the flag of sublattices for {isometry} must have strictly "
                        f"increasing ranks, but {previous} of rank {previous.module_rank()} "
                        f"is followed by {term} of rank {term.module_rank()}"
                    )
            previous = term
        self._isometry = isometry
        self._terms = terms

    def isometry(self):
        return self._isometry

    def lattice(self):
        return self.isometry().domain()

    def terms(self):
        return finite_ordered_set(self._terms)

    def ranks(self):
        return finite_ordered_set(tuple(term.module_rank() for term in self._terms))

    def __repr__(self) -> str:
        return f"Equivariant sublattice flag of ranks {tuple(self.ranks())} in {self.lattice()}"


def _same_equivariant_flag(left, right) -> bool:
    left_terms = tuple(left.terms())
    right_terms = tuple(right.terms())
    if len(left_terms) != len(right_terms):
        return False
    return all(_same_subobject(source, target) for source, target in zip(left_terms, right_terms, strict=True))


def _transport_equivariant_flag(automorphism, flag):
    return EquivariantSublatticeFlag(
        flag.isometry(),
        tuple(_transport_sublattice(automorphism, term) for term in flag.terms()),
    )


class _EquivariantFiniteOrbitDecompositionEngine(_CentralizerOrbitDecompositionEngine):
    r"""Exact centralizer orbits on a supplied finite centralizer-stable family."""

    def __init__(self, isometry, candidates, action, equality, **rest) -> None:
        candidates = tuple(candidates)
        if not candidates:
            raise ValueError(
                f"cannot decompose into orbits of the centralizer of {isometry}: the "
                f"finite set of points is empty"
            )
        self._isometry = isometry
        self._candidate_action = action
        self._equality = equality
        self._points = finite_ordered_set(candidates)

        def acted_point(automorphism, candidate):
            image = self.act(automorphism, candidate)
            matches = tuple(target for target in self._points if self.same(image, target))
            assert len(matches) == 1, (
                f"the centralizer element {automorphism} sends {candidate} to {image}, "
                f"which equals {len(matches)} points of the set, not exactly one: the "
                f"set is not stable under the centralizer of {isometry}, or it repeats "
                f"a point"
            )
            return matches[0]

        self._g_set = FiniteGSets(isometry.centralizer_group())(
            self._points,
            acted_point,
        )
        self._orbit_set = self._g_set.orbits()
        super().__init__(facade=True, **rest)

    def isometry(self):
        return self._isometry

    def group(self):
        return self.isometry().centralizer_group()

    def action(self):
        return self._g_set

    def act(self, automorphism, candidate):
        return self._candidate_action(automorphism, candidate)

    def same(self, left, right) -> bool:
        return bool(self._equality(left, right))

    def point(self, candidate):
        matches = tuple(point for point in self._points if self.same(candidate, point))
        if len(matches) != 1:
            raise ValueError(
                f"{candidate} equals {len(matches)} points of the finite set acted on "
                f"by the centralizer of {self.isometry()}, not exactly one"
            )
        return matches[0]

    def representatives(self):
        return finite_ordered_set(tuple(orbit.representative() for orbit in self))

    def orbit_of(self, candidate):
        return self.action().orbits().orbit_of(self.point(candidate))

    def stabilizer(self, candidate):
        return self.orbit_of(candidate).stabilizer()

    def transporter(self, source, target):
        if self.orbit_of(source) != self.orbit_of(target):
            return None
        return self.action().transporter_witness(self.point(source), self.point(target))


def _equivariant_finite_orbit_decomposition(isometry, candidates, action, equality):
    return _object_of(
        Sets().Finite(),
        _engine=(Sets(), _EquivariantFiniteOrbitDecompositionEngine, None),
        isometry=isometry,
        candidates=tuple(candidates),
        action=action,
        equality=equality,
    )


def _isometry_power(isometry, exponent):
    r"""Return an exact nonnegative power of one lattice automorphism."""
    exponent = int(exponent)
    if exponent < 0:
        raise ValueError(
            f"cannot form the power {isometry}^{exponent}: this power is taken only "
            f"for nonnegative exponents"
        )
    result = isometry.domain().O().one()
    for _step in range(exponent):
        result = isometry * result
    return result


class CyclotomicDecomposition(SageObject):
    r"""The integral cyclotomic decomposition of a finite-order isometry.

    For an automorphism ``f`` of exact order ``n`` this owns the primitive
    sublattices ``L_d = ker(Phi_d(f))`` for ``d | n`` and the finite-index
    inclusion ``direct_sum_d L_d -> L``.  The finite quotient of that
    inclusion is the integral gluing datum.  Component isometries are allowed
    to act on the summands independently only when they extend across that
    quotient to an actual isometry of ``L`` commuting with ``f``.
    """

    def __init__(self, isometry, order) -> None:
        self._isometry = isometry
        self._order = int(order)
        if self._order <= 0:
            raise ValueError(
                f"cannot use {self._order} as the order of {isometry}: the order of an "
                f"isometry of finite order is a positive integer"
            )
        lattice = isometry.domain()
        if isometry.codomain() is not lattice:
            raise ValueError(
                f"cannot form the cyclotomic decomposition of {isometry}: it must be an "
                f"automorphism L -> L, but it maps {lattice} -> {isometry.codomain()}"
            )
        identity = lattice.O().one()
        if _isometry_power(isometry, self._order) != identity:
            raise ValueError(
                f"{isometry} does not have order {self._order}: its "
                f"{self._order}-th power is not the identity of {lattice}"
            )
        for proper_divisor in divisors(self._order):
            if proper_divisor == self._order:
                continue
            if _isometry_power(isometry, proper_divisor) == identity:
                raise ValueError(
                    f"{isometry} does not have order {self._order}: already its "
                    f"{proper_divisor}-th power is the identity of {lattice}"
                )

        integers = _owned_integers()
        self._divisors = finite_ordered_set(tuple(integers(int(divisor)) for divisor in divisors(self._order)))
        self._summands = finite_indexed_family(
            self._divisors,
            lambda divisor: isometry.cyclotomic_summand(int(divisor)),
            name=f"Cyclotomic summands of {isometry}",
        )
        nonzero = tuple(divisor for divisor in self._divisors if int(self._summands[divisor].module_rank()) != 0)
        if not nonzero:
            raise ArithmeticError(
                f"every cyclotomic summand ker(Phi_d(f)) of {isometry}, for d dividing "
                f"{self._order}, has rank zero; for an isometry of finite order they "
                f"span L tensor QQ"
            )
        self._nonzero_divisors = finite_ordered_set(nonzero)

        lattice = self.lattice()
        total_rank = sum(int(self._summands[divisor].module_rank()) for divisor in self._nonzero_divisors)
        if total_rank != int(lattice.module_rank()):
            raise ArithmeticError(
                f"the cyclotomic summands ker(Phi_d(f)) of {isometry} have total rank "
                f"{total_rank}, but {lattice} has rank {lattice.module_rank()}: they do "
                f"not span L tensor QQ"
            )
        ring = lattice.base_ring()
        zero = ring.zero()
        for left_position, left_divisor in enumerate(self._nonzero_divisors):
            left = self._summands[left_divisor]
            for right_divisor in tuple(self._nonzero_divisors)[left_position + 1 :]:
                right = self._summands[right_divisor]
                if any(
                    lattice.b(left_vector, right_vector) != zero for left_vector in left.embedded_module_generators() for right_vector in right.embedded_module_generators()
                ):
                    raise ArithmeticError(
                        f"the cyclotomic summands ker(Phi_{left_divisor}(f)) and "
                        f"ker(Phi_{right_divisor}(f)) of {isometry} are not orthogonal in "
                        f"{lattice}"
                    )

    def lattice(self):
        return self.isometry().domain()

    def isometry(self):
        return self._isometry

    def order(self):
        return self._order

    def divisor_set(self):
        return self._divisors

    def summands(self):
        return self._summands

    def summand(self, divisor):
        divisor = self.divisor_set()(divisor)
        return self.summands()[divisor]

    def nonzero_divisors(self):
        return self._nonzero_divisors

    @cached_method
    def orthogonal_sum(self):
        summands = tuple(self.summand(divisor) for divisor in self.nonzero_divisors())
        result = summands[0]
        for summand in summands[1:]:
            result = result + summand
        return result

    @cached_method
    def orthogonal_sum_inclusion(self):
        r"""Return ``direct_sum_d L_d -> L`` with finite-index image."""
        images = []
        for divisor in self.nonzero_divisors():
            summand = self.summand(divisor)
            inclusion = summand.inclusion()
            images.extend(inclusion(generator) for generator in summand.module_generators())
        return self.orthogonal_sum().Emb(self.lattice())(tuple(images))

    def index(self):
        return self.orthogonal_sum_inclusion().index()

    @cached_method
    def gluing_quotient(self):
        r"""Return ``L / direct_sum_d L_d``, the finite integral glue quotient."""
        return self.orthogonal_sum_inclusion().cokernel()

    @cached_method
    def component_isometries(self):
        r"""Return the restrictions ``f_d`` on every nonzero cyclotomic summand."""
        return finite_indexed_family(
            self.nonzero_divisors(),
            lambda divisor: _restrict_isometry(self.isometry(), self.summand(divisor)),
            name=f"Cyclotomic restrictions of {self.isometry()}",
        )

    @cached_method
    def component_centralizers(self):
        r"""Return ``Z_{O(L_d)}(f_d)`` for every nonzero cyclotomic component."""
        restrictions = self.component_isometries()
        return finite_indexed_family(
            self.nonzero_divisors(),
            lambda divisor: self.summand(divisor).O().centralizer(restrictions[divisor]),
            name=f"Cyclotomic component centralizers of {self.isometry()}",
        )

    def centralizer_group(self):
        r"""Return the actual ambient arithmetic centralizer ``Z_{O(L)}(f)``."""
        return self.isometry().centralizer_group()

    def restrict_centralizer_element(self, automorphism):
        r"""Restrict one ambient centralizer element to every cyclotomic summand.

        Commutation with ``f`` makes each polynomial kernel
        ``ker(Phi_d(f))`` stable, so every restriction is defined and belongs
        to ``Z_{O(L_d)}(f_d)``.  The result is indexed by the nonzero
        cyclotomic divisors and retains the actual component isometries.
        """
        if automorphism not in self.centralizer_group():
            raise ValueError(
                f"cannot restrict {automorphism} to the cyclotomic summands of "
                f"{self.isometry()}: it does not lie in the centralizer "
                f"{self.centralizer_group()}"
            )
        restrictions = self.component_isometries()
        centralizers = self.component_centralizers()

        def restrict(divisor):
            summand = self.summand(divisor)
            inclusion = summand.inclusion()
            component = summand.O()({label: inclusion.lift(automorphism(inclusion(summand.module_generator(label)))) for label in summand.module_generating_set()})
            if component * restrictions[divisor] != restrictions[divisor] * component:
                raise ArithmeticError(
                    f"the restriction of {automorphism} to the cyclotomic summand "
                    f"ker(Phi_{divisor}(f)) does not commute with f restricted there, "
                    f"although {automorphism} centralizes {self.isometry()}"
                )
            if component not in centralizers[divisor]:
                raise ArithmeticError(
                    f"the restriction of {automorphism} to the cyclotomic summand "
                    f"ker(Phi_{divisor}(f)) commutes with f there but is not in the "
                    f"centralizer {centralizers[divisor]}"
                )
            return component

        return finite_indexed_family(
            self.nonzero_divisors(),
            restrict,
            name=f"Cyclotomic restrictions of an element of {self.centralizer_group()}",
        )

    def _component_tuple(self, component_isometries):
        r"""Return the stated component isometries, one per nonzero divisor.

        ``component_isometries`` is indexed by the divisors, either as an
        indexed family over them or keyed by their integer values.
        """
        return {
            divisor: self.summand(divisor).O()(component_isometries[int(divisor)])
            for divisor in self.nonzero_divisors()
        }

    def _components_commute(self, components) -> bool:
        r"""Whether every component commutes with the restriction of ``f`` to its summand."""
        restrictions = self.component_isometries()
        return all(
            components[divisor] * restrictions[divisor] == restrictions[divisor] * components[divisor]
            for divisor in self.nonzero_divisors()
        )

    def _block_sum(self, components):
        r"""Return the orthogonal sum of the components on ``M = sum_d L_d``, in ``O(M)``."""
        result = self.orthogonal_sum().O().one()
        for divisor in self.nonzero_divisors():
            result = result * self._block_isometry(divisor, components[divisor])
        return result

    def lift_component_isometries(self, component_isometries):
        r"""Lift a compatible tuple of component isometries to ``O(L,f)``.

        The orthogonal sum ``g`` of the components is an isometry of the
        cyclotomic sum ``M``; the tuple is compatible exactly when ``g``
        extends along the finite-index inclusion ``M -> L``, and the lift is
        that extension (:meth:`LatticeEmbeddingMethods.isometry_extension`).
        Commutation with ``f`` holds on ``M`` because each component commutes
        with ``f_d``, hence on ``L tensor QQ``.
        """
        components = self._component_tuple(component_isometries)
        if not self._components_commute(components):
            raise ValueError(
                f"cannot lift {component_isometries} to the centralizer of "
                f"{self.isometry()}: some component does not commute with f restricted to "
                f"its cyclotomic summand"
            )
        return self.orthogonal_sum_inclusion().isometry_extension(self._block_sum(components))

    def component_isometries_extend(self, component_isometries) -> bool:
        r"""Whether the component tuple extends to an isometry of ``L`` commuting with ``f``.

        The orthogonal sum ``g`` of commuting components is an isometry of
        ``M``; it extends to ``L`` exactly when ``g_Q(L) = L``
        (:meth:`LatticeEmbeddingMethods.isometry_extends`), and it then
        commutes with ``f`` because it does so on the finite-index ``M``.
        """
        components = self._component_tuple(component_isometries)
        if not self._components_commute(components):
            return False
        return self.orthogonal_sum_inclusion().isometry_extends(self._block_sum(components))

    def _orthogonal_sum_image(self, divisor, element):
        r"""Return the image of ``element`` of ``L_d`` under ``L_d -> M = sum_e L_e``.

        ``M`` embeds in ``L`` by ``j``, and ``L_d -> M`` is the factorization
        of ``L_d -> L`` through ``j``.
        """
        summand = self.summand(divisor)
        return self.orthogonal_sum_inclusion().lift(summand.inclusion()(element))

    def _block_isometry(self, divisor, component):
        r"""Return ``component`` on ``L_d`` extended by the identity of every other ``L_e``, in ``O(M)``."""
        orthogonal_sum = self.orthogonal_sum()
        images = []
        for other in self.nonzero_divisors():
            images.extend(
                self._orthogonal_sum_image(other, component(generator) if other == divisor else generator)
                for generator in self.summand(other).module_generators()
            )
        by_label = dict(zip(orthogonal_sum.module_generating_set(), images, strict=True))
        return orthogonal_sum.O()(lambda label: by_label[label])

    def _block_restriction(self, divisor, automorphism):
        r"""Restrict a block-diagonal ``g`` in ``O(M)`` to ``L_d``, an element of ``O(L_d)``."""
        summand = self.summand(divisor)
        inclusion = summand.inclusion()
        orthogonal_sum_inclusion = self.orthogonal_sum_inclusion()
        return summand.O()(
            {
                label: inclusion.lift(
                    orthogonal_sum_inclusion(
                        automorphism(self._orthogonal_sum_image(divisor, summand.module_generator(label)))
                    )
                )
                for label in summand.module_generating_set()
            }
        )

    def gluing_subgroup(self):
        r"""Return ``L/M`` as the subgroup of ``A_M`` it defines, for ``M = sum_d L_d``.

        This is the glue of the finite-index inclusion ``M -> L``
        (:meth:`LatticeEmbeddingMethods.gluing_subgroup`).
        """
        return self.orthogonal_sum_inclusion().gluing_subgroup()

    @cached_method
    def glued_centralizer_generators(self):
        r"""Return group generators of ``Z_{O(L)}(f)`` glued from the component centralizers.

        Let ``Gamma <= O(M)`` be generated by the block-diagonal elements
        ``g_d``, one for each group generator of each
        ``Z_{O(L_d)}(f_d)``.  Every element of ``Z_{O(L)}(f)`` restricts to
        each ``L_d``, so ``Z_{O(L)}(f)`` is the subgroup of ``Gamma`` of
        elements preserving ``L``, restricted to ``L``: the extended subgroup
        of ``Gamma`` along the finite-index inclusion ``M -> L``
        (:meth:`LatticeEmbeddingMethods.extended_subgroup`), computed there
        as a preimage under ``rho_M: O(M) -> O(A_M)``.  No abstract product
        of the component groups is formed: a generated subgroup of ``O(M)``
        on the block-diagonal generators is the group the gluing needs.
        """
        orthogonal_sum = self.orthogonal_sum()
        centralizers = self.component_centralizers()
        block_generators = tuple(
            self._block_isometry(divisor, generator)
            for divisor in self.nonzero_divisors()
            for generator in centralizers[divisor].group_generators()
        )
        blocks = orthogonal_sum.O().subgroup(block_generators)
        return self.orthogonal_sum_inclusion().extended_subgroup(blocks).group_generators()

    @cached_method
    def glued_centralizer_discriminant_image(self):
        r"""Glue the component finite images to ``rho_L(Z_{O(L)}(f))``.

        Write ``M = direct_sum_d L_d`` and ``H = L/M <= A_M``.  The image
        of the product of component centralizers is the block product of
        their images in ``O(A_{L_d})``.  Its setwise stabilizer of ``H``
        is exactly the image of the compatible arithmetic tuples: any
        chosen arithmetic lifts preserve ``L`` precisely when their finite
        action preserves ``H``.  Descending that stabilizer to
        ``H^perp/H = A_L`` therefore gives the required image.

        This is the finite compatibility calculation of OSCAR's pinned
        ``_glue_stabilizers`` (``embeddings.jl:3085-3196``, ``d135b70b``).
        The finite setwise stabilizer includes both restriction kernels
        and the matching actions on the glue, without requiring generators
        of an indefinite component's full arithmetic centralizer.
        """
        from sage_extensions.categories.modules.framed.formed.torsion_form_modules import (
            _torsion_form_isometry,
        )
        from sage_extensions.categories.modules.pure.modules import Modules

        divisors = self.nonzero_divisors()
        orthogonal_sum = self.orthogonal_sum()
        form = orthogonal_sum.discriminant_group()
        group = form.orthogonal_group()

        def discriminant_inclusion(divisor):
            summand = self.summand(divisor)
            inclusion = summand.Emb(orthogonal_sum)(
                lambda label: self._orthogonal_sum_image(
                    divisor, summand.module_generator(label)
                )
            )
            return inclusion.discriminant_inclusion()

        inclusions = finite_indexed_family(divisors, discriminant_inclusion)
        factors = finite_indexed_family(
            divisors, lambda divisor: inclusions[divisor].domain()
        )
        product = Modules(orthogonal_sum.base_ring()).biproduct(factors)
        merge = product.from_coproduct_cocone(finite_indexed_family(
            divisors, lambda divisor: inclusions[divisor].module_morphism()
        ))
        split = merge.inverse()

        def block_isometry(divisor, component):
            inclusion = inclusions[divisor]
            factor = inclusion.domain()
            projection = product.projection(divisor) * split

            def image(label, action):
                element = form.module_generator(label)
                coordinate = projection(element)
                # An even summand inside an odd M is represented here by
                # its bilinear discriminant form.  Both readings retain
                # the same underlying presented module.
                component_class = action.domain()(factor.unformed_module()(coordinate))
                moved = factor(action(component_class))
                return element + inclusion(moved - coordinate)

            morphisms = form.module_category().Mor(form, form)
            inverse = ~component
            return group.from_morphism(_torsion_form_isometry(
                morphisms(lambda label: image(label, component)),
                morphisms(lambda label: image(label, inverse)),
                quadratic=orthogonal_sum.is_even(),
            ))

        restrictions = self.component_isometries()
        block_generators = tuple(
            block_isometry(divisor, generator)
            for divisor in divisors
            for generator in restrictions[divisor].centralizer_discriminant_image().group_generators()
        )
        blocks = group.subgroup_on(block_generators)
        points = form.elements()
        action = FiniteGSets(blocks)(
            points, lambda automorphism, element: blocks.inclusion()(automorphism)(element)
        )
        glue = self.gluing_subgroup().inclusion()
        subset = points.power_set()(tuple(
            glue(element) for element in glue.domain().elements()
        ))
        compatible = action.setwise_stabilizer(subset)
        into_form_group = blocks.inclusion() * compatible.inclusion()
        extension = self.orthogonal_sum_inclusion()
        return self.lattice().discriminant_group().orthogonal_group().subgroup_on(tuple(
            extension.discriminant_isometry_extension(into_form_group(generator))
            for generator in compatible.group_generators()
        ))


class PolarizedEquivariantLattice(SageObject):
    r"""An equivariant lattice ``(L,f)`` with an invariant polarization ``h``.

    This owns the three live objects that define the polarized arithmetic
    group: the centralizer ``Z_{O(L)}(f)``, the point stabilizer of ``h``, and
    their structured intersection.  The polarization is retained both in the
    ambient lattice and through its lift to the invariant lattice ``L^f``.
    """

    def __init__(self, isometry, polarization) -> None:
        lattice = isometry.domain()
        if isometry.codomain() is not lattice:
            raise ValueError(
                f"cannot polarize via {isometry}: it must be an automorphism L -> L, but "
                f"it maps {lattice} -> {isometry.codomain()}"
            )
        polarization = lattice(polarization)
        if isometry(polarization) != polarization:
            raise ValueError(
                f"{polarization} is not a polarization of ({lattice}, f): f sends it to "
                f"{isometry(polarization)}, so it is not in the invariant lattice L^f"
            )
        if polarization == lattice.zero():
            raise ValueError(
                f"the zero vector of {lattice} is not a polarization: a polarization is "
                f"nonzero"
            )
        self._isometry = isometry
        self._polarization = polarization

    def lattice(self):
        return self.isometry().domain()

    def isometry(self):
        return self._isometry

    def polarization(self):
        return self._polarization

    def primitive_extension(self):
        return self.isometry().primitive_extension()

    @cached_method
    def invariant_polarization(self):
        invariant = self.primitive_extension().invariant
        inclusion = invariant.inclusion()
        if not inclusion.is_in_image(self.polarization()):
            raise ArithmeticError(
                f"the polarization {self.polarization()} is fixed by {self.isometry()} but "
                f"is not in the image of the invariant lattice {invariant}"
            )
        return inclusion.lift(self.polarization())

    def centralizer_group(self):
        return self.isometry().centralizer_group()

    @cached_method
    def polarization_stabilizer(self):
        return self.lattice().O().stabilizer(self.polarization())

    @cached_method
    def polarized_group(self):
        r"""Return ``Z_{O(L)}(f) cap Stab(h)`` as a structured subgroup."""
        return self.centralizer_group().intersection(self.polarization_stabilizer())

    def __repr__(self) -> str:
        return f"{self.lattice()} equipped with {self.isometry()} and polarized by {self.polarization()}"


class IsometryPrimitiveExtension:
    r"""The primitive extension ``L^f + (L^f)^perp -> L`` cut out by ``f``.

    Every field below is an owned object: the two primitive sublattices with
    their inclusions, the finite index of their orthogonal sum, and the glue
    anti-isometry presenting the extension.
    """

    def __init__(self, isometry) -> None:
        lattice = isometry.domain()
        assert isometry.codomain() is lattice, (
            f"cannot form L^f + (L^f)^perp -> L for {isometry}: f must be an "
            f"automorphism L -> L, but it maps {lattice} -> {isometry.codomain()}"
        )
        assert lattice.module_rank().is_finite() and lattice.is_nondegenerate(), (
            f"cannot form L^f + (L^f)^perp -> L for {lattice}: the invariant lattice "
            f"and its orthogonal complement span L only when L has finite rank and a "
            f"nondegenerate form; {lattice} has rank {lattice.module_rank()}"
        )
        invariant = isometry.invariant_lattice()
        orthogonal_complement = isometry.formed_coinvariants()
        assert invariant.module_rank() + orthogonal_complement.module_rank() == lattice.module_rank(), (
            f"for {isometry}, L^f has rank {invariant.module_rank()} and (L^f)^perp has "
            f"rank {orthogonal_complement.module_rank()}, which do not add up to the rank "
            f"{lattice.module_rank()} of {lattice}: f is not of finite order"
        )

        self.isometry = isometry
        self.lattice = lattice
        self.invariant = invariant
        self.orthogonal_complement = orthogonal_complement

    def invariant_inclusion(self):
        r"""Return the retained primitive inclusion of the invariant lattice."""
        return self.invariant.inclusion()

    def orthogonal_complement_inclusion(self):
        r"""Return the retained primitive inclusion of the orthogonal complement."""
        return self.orthogonal_complement.inclusion()

    @cached_method
    def glue(self):
        r"""Return the Nikulin anti-isometry ``H_+ -> H_-(-1)`` of this extension."""
        return self.lattice.glue_map(self.invariant, self.orthogonal_complement)

    def invariant_gluing_subgroup(self):
        r"""Return ``H_+ = L/(L^f + (L^f)^perp)`` seen inside ``A_{L^f}``."""
        return self.glue().domain()

    @cached_method
    def index(self):
        r"""Return ``[L : L^f + (L^f)^perp]``, the order of the glue subgroup."""
        return self.orthogonal_sum_inclusion().index()

    def centralizer_group(self):
        r"""Return ``O(L,f) = Z_{O(L)}(f)`` as a predicate subgroup of ``O(L)``."""

        return self.lattice.Aut().centralizer(self.isometry)

    def centralizer_discriminant_image(self):
        r"""Return ``rho_L(O(L,f)) <= O(A_L)``, the finite image of the centralizer."""
        return self.isometry.centralizer_discriminant_image()

    def _full_discriminant_glue_data(self):
        r"""Return the primitive glue data when both discriminant forms are glued in full."""
        glue = self.glue()
        invariant_form = self.invariant.discriminant_group()
        coinvariant_form = self.orthogonal_complement.discriminant_group()
        glue_source = glue.domain()
        glue_target = glue.codomain()
        assert glue_source.cardinality() == invariant_form.cardinality(), (
            f"the glue subgroup of L^f for {self.isometry} has order "
            f"{glue_source.cardinality()}, but the discriminant group of L^f has order "
            f"{invariant_form.cardinality()}: this construction needs L to glue the whole "
            f"discriminant group of L^f"
        )
        assert glue_target.cardinality() == coinvariant_form.cardinality(), (
            f"the glue subgroup of (L^f)^perp for {self.isometry} has order "
            f"{glue_target.cardinality()}, but the discriminant group of (L^f)^perp has "
            f"order {coinvariant_form.cardinality()}: this construction needs L to glue "
            f"the whole discriminant group of (L^f)^perp"
        )
        return glue, invariant_form, coinvariant_form, glue_source, glue_target

    @cached_method
    def coinvariant_extension_subgroup(self):
        r"""Return the coinvariant restriction image in the full-glue involution case.

        Suppose ``f`` is an involution and the primitive extension glues the
        *entire* discriminant forms of ``L^f`` and ``(L^f)^perp``.  Then every
        isometry of the coinvariant lattice commutes with ``f|_{L^-}=-1``, and
        it extends across the primitive gluing exactly when its discriminant
        action belongs to

        ``gamma rho(O(L^f)) gamma^-1``.

        The returned group is therefore the actual finite-character preimage
        in ``O(L^-)``; it is not a separately represented copy of the ambient
        centralizer.
        """
        assert self.acts_as_negation_on_coinvariants(), (
            f"{self.isometry} does not act as -1 on (L^f)^perp in {self.lattice}: this "
            f"subgroup of O((L^f)^perp) is computed only when f is an involution"
        )

        _glue, invariant_form, coinvariant_form, _glue_source, _glue_target = (
            self._full_discriminant_glue_data()
        )

        invariant_image = self.invariant.discriminant_image()
        coinvariant_orthogonal_group = coinvariant_form.O()

        allowed_discriminant_image = coinvariant_orthogonal_group.subgroup_on(
            tuple(self._coinvariant_discriminant_from_invariant(generator) for generator in invariant_image.group_generators())
        )
        return self.orthogonal_complement.O().discriminant_preimage(allowed_discriminant_image)

    def _coinvariant_discriminant_from_invariant(self, invariant_automorphism):
        r"""Conjugate an invariant discriminant action across the primitive glue.

        If ``gamma:H_+ -> H_-(-1)`` is the glue anti-isometry, this returns
        the automorphism of ``A_{L^-}`` induced by
        ``gamma invariant_automorphism gamma^-1``.  The full-discriminant
        hypothesis is exactly the one required by
        :meth:`coinvariant_extension_subgroup`.
        """
        glue, invariant_form, coinvariant_form, glue_source, glue_target = (
            self._full_discriminant_glue_data()
        )
        source_inclusion = glue_source.inclusion()
        target_inclusion = glue_target.inclusion()
        twisted_coinvariant_form = target_inclusion.codomain()

        invariant_automorphism = invariant_form.O()(invariant_automorphism)
        images = {}
        for label in coinvariant_form.module_generating_set():
            element = coinvariant_form.module_generator(label)
            twisted = twisted_coinvariant_form(element)
            target_element = target_inclusion.lift(twisted)
            source_element = glue.inverse().forward()(target_element)
            invariant_class = source_inclusion(source_element)
            moved_invariant_class = invariant_automorphism(invariant_class)
            moved_source = source_inclusion.lift(moved_invariant_class)
            moved_target = glue.forward()(moved_source)
            moved_twisted = target_inclusion(moved_target)
            images[label] = coinvariant_form(moved_twisted)
        morphism = coinvariant_form.module_category().Mor(coinvariant_form, coinvariant_form)(images)
        from sage_extensions.categories.modules.framed.formed.torsion_form_modules import (
            _torsion_form_isometry,
        )

        group = coinvariant_form.O()
        isometry = _torsion_form_isometry(morphism, morphism.inverse(), quadratic=group.is_quadratic())
        return group.from_morphism(isometry)

    def lift_coinvariant_extension_element(self, coinvariant_part):
        r"""Lift ``g_-`` from the anti-invariant extension group to ``O(L,f)``.

        The selected ``g_-`` already has discriminant action in the conjugate
        of the invariant discriminant image.  Enumerate that finite image,
        choose the matching invariant discriminant action, lift it to an
        actual isometry of ``L^f``, and assemble the pair through the retained
        primitive glue.  The result is an ambient centralizer element whose
        coinvariant restriction is literally ``g_-``.
        """
        subgroup = self.coinvariant_extension_subgroup()
        if coinvariant_part not in subgroup:
            raise ValueError(
                f"{coinvariant_part} does not extend to an isometry of {self.lattice} "
                f"commuting with {self.isometry}: its discriminant action does not "
                f"preserve the glue of L^f + (L^f)^perp in L"
            )
        coinvariant_part = self.orthogonal_complement.O()(coinvariant_part)
        target_action = coinvariant_part.discriminant_morphism()
        invariant_group = self.invariant.O()
        invariant_image = self.invariant.discriminant_image()

        invariant_part = None
        for invariant_action in invariant_image:
            if self._coinvariant_discriminant_from_invariant(invariant_action) != target_action:
                continue
            invariant_part = invariant_group.discriminant_lift(invariant_action)
            if invariant_part is not None:
                break
        if invariant_part is None:
            raise ArithmeticError(
                f"{coinvariant_part} preserves the glue, but no isometry of L^f in "
                f"{self.lattice} induces the matching action on the discriminant group "
                f"of L^f"
            )

        lifted = self.centralizer_element(invariant_part, coinvariant_part)
        if self.coinvariant_restriction(lifted) != coinvariant_part:
            raise ArithmeticError(
                f"the lift {lifted} of {coinvariant_part} to the centralizer of "
                f"{self.isometry} restricts to {self.coinvariant_restriction(lifted)} on "
                f"(L^f)^perp, not to {coinvariant_part}"
            )
        return lifted

    def coinvariant_isotropic_orbit_representatives(self, rank, *, flag=False):
        r"""Return anti-invariant isotropic orbits under the ambient centralizer image."""
        return self.coinvariant_extension_subgroup().isotropic_orbit_representatives(
            rank,
            flag=flag,
        )

    def coinvariant_isotropic_equivalence_witness(self, left, right, *, flag=False):
        r"""Return an ambient centralizer element carrying ``left`` to ``right``.

        The finite-character subgroup first constructs the exact transporter
        on the anti-invariant lattice.  This method then lifts that transporter
        through the primitive gluing, so the witness acts on the original
        lattice rather than only on ``L^-``.
        """
        coinvariant_witness = self.coinvariant_extension_subgroup().isotropic_equivalence_witness(
            left,
            right,
            flag=flag,
        )
        if coinvariant_witness is None:
            return None
        return self.lift_coinvariant_extension_element(coinvariant_witness)

    def _restriction(self, automorphism, subobject):
        assert automorphism.domain() is self.lattice, (
            f"cannot restrict {automorphism} to {subobject}: it is an automorphism of "
            f"{automorphism.domain()}, not of {self.lattice}"
        )
        assert automorphism * self.isometry == self.isometry * automorphism, (
            f"cannot restrict {automorphism} to {subobject}: restriction is defined on "
            f"the centralizer O(L, f), and {automorphism} does not commute with "
            f"f = {self.isometry}"
        )
        inclusion = subobject.inclusion()
        summand = inclusion.domain()
        return summand.Aut()({label: inclusion.lift(automorphism(inclusion(summand.module_generator(label)))) for label in summand.module_generating_set()})

    def invariant_restriction(self, automorphism):
        r"""Return ``g|_{L^f}`` in ``O(L^f)`` for ``g`` in the centralizer.

        An element of ``O(L,f)`` commutes with ``f``, so it preserves the
        fixed lattice and, being an isometry of ``L``, its orthogonal
        complement.  Restriction is therefore defined and lands in the
        orthogonal group of the summand.
        """
        return self._restriction(automorphism, self.invariant)

    def coinvariant_restriction(self, automorphism):
        r"""Return ``g|_{(L^f)^perp}`` in ``O((L^f)^perp)`` for ``g`` in the centralizer."""
        return self._restriction(automorphism, self.orthogonal_complement)

    def acts_as_negation_on_coinvariants(self) -> bool:
        r"""Return whether ``f`` restricts to ``-1`` on ``(L^f)^perp``.

        This holds exactly when ``f`` is an involution: then ``(L^f)^perp`` is
        ``ker(f + 1)``, which is the statement the eigenspace decomposition
        ``V_pm = ker(f -+ 1)`` makes.
        """
        inclusion = self.orthogonal_complement_inclusion()
        return all(self.isometry(inclusion(generator)) == -inclusion(generator) for generator in inclusion.domain().module_generators())

    @cached_method
    def orthogonal_sum_inclusion(self):
        r"""Return the finite-index inclusion ``L^f + (L^f)^perp -> L``.

        The two summands are orthogonal of complementary rank, so their
        orthogonal sum is a lattice in its own right and this arrow is the
        primitive extension the class is named for.  Its cokernel has order
        :meth:`index`, so that scalar carries every vector of ``L`` into the
        image: an isometry of the two summands is read on ``L`` by clearing
        that one denominator.
        """
        invariant_inclusion = self.invariant_inclusion()
        coinvariant_inclusion = self.orthogonal_complement_inclusion()
        invariant_summand = invariant_inclusion.domain()
        coinvariant_summand = coinvariant_inclusion.domain()
        summands = invariant_summand + coinvariant_summand
        return summands.Emb(self.lattice)(
            tuple(invariant_inclusion(generator) for generator in invariant_summand.module_generators())
            + tuple(coinvariant_inclusion(generator) for generator in coinvariant_summand.module_generators())
        )

    def glue_graph(self):
        r"""Return the graph of ``gamma`` inside ``A_{L^f} x A_{(L^f)^perp}(-1)``.

        Nikulin presents ``L`` by the subgroup ``L/(L^f + (L^f)^perp)``, which
        sits in the sum of the two discriminant forms as the graph of the
        anti-isometry ``gamma``.  The graph is a finite group of order
        :meth:`index`, and it is what an isometry of the two summands has to
        preserve in order to be an isometry of ``L``.
        """
        glue = self.glue()
        gluing = glue.domain()
        into_invariant = gluing.inclusion()
        into_coinvariant = glue.codomain().inclusion()
        return finite_ordered_set(tuple((into_invariant(element), into_coinvariant(glue(element))) for element in gluing.elements()))

    def _discriminant_action(self, automorphism, ambient, element):
        r"""Return the image of a class of ``ambient`` under ``Disc(automorphism)``.

        An automorphism of a summand induces an automorphism of that summand's
        discriminant module, and that module is what underlies whichever
        finite form the glue map put the graph in: the discriminant module
        itself, its bilinear reading when an even summand sits inside an odd
        ``L``, or the twist ``A_R(-1)``.  Polarizing and rescaling both leave
        the underlying map alone -- an isometry of ``q`` is an isometry of its
        polar form and of any rescaling of either -- so the action is read on
        the discriminant module the finite form was stated on, and the class
        passes to and from it by coercion.
        """
        module = ambient.unformed_module()
        return ambient(automorphism.discriminant_morphism()(module(element)))

    def pair_preserves_glue_graph(self, invariant_part, coinvariant_part) -> bool:
        r"""Return whether ``(g_+, g_-)`` carries the graph of ``gamma`` onto itself.

        The pair acts on the sum of the two discriminant forms by its induced
        discriminant automorphisms ``Disc(g_+)`` and ``Disc(g_-)``, the second
        read on the twist ``A_{(L^f)^perp}(-1)`` in which ``gamma`` lands.  It
        extends to an isometry of ``L`` exactly when that action preserves the
        graph, which is Nikulin's criterion for a primitive extension.  Both
        maps are automorphisms of finite forms, so preserving the graph
        setwise is the same as permuting it.

        The criterion reads the same in either parity of ``L``; only the
        finite forms the graph lives in change, and which ones those are is
        settled once, by ``glue_map``, from the parity of ``L``.  An even
        ``L`` glues its quadratic discriminant forms and an odd one its
        bilinear forms, so the two ambients are taken from the endpoints of
        the glue arrow rather than chosen a second time here.
        """
        invariant_ambient = self.glue().domain().inclusion().codomain()
        coinvariant_ambient = self.glue().codomain().inclusion().codomain()
        graph = self.glue_graph()
        return all(
            (
                self._discriminant_action(invariant_part, invariant_ambient, invariant_class),
                self._discriminant_action(coinvariant_part, coinvariant_ambient, coinvariant_class),
            )
            in graph
            for invariant_class, coinvariant_class in graph
        )

    def centralizer_element(self, invariant_part, coinvariant_part):
        r"""Assemble ``g`` in ``O(L,f)`` from a compatible pair of restrictions.

        This is the inverse of :meth:`invariant_restriction` and
        :meth:`coinvariant_restriction`.  A pair ``(g_+, g_-)`` in
        ``O(L^f) x O((L^f)^perp)`` is an element of ``O(L,f)`` under two
        conditions.  It has to extend to ``L``, which is
        :meth:`pair_preserves_glue_graph`.  It then has to commute with ``f``,
        and since ``f`` is the identity on ``L^f`` that is the single
        condition that ``g_-`` commutes with ``f`` restricted to
        ``(L^f)^perp``.

        The extension itself is one denominator.  The orthogonal sum has index
        ``m`` in ``L``, so ``m x`` lies in the sum for every ``x`` in ``L``;
        applying the pair there and dividing by ``m`` again gives ``g x``, and
        the division is exact because the pair preserves the graph.  The
        returned arrow is built in ``O(L)``, whose constructor is what proves
        the assembled map preserves the form and is bijective.
        """
        lattice = self.lattice
        invariant_inclusion = self.invariant_inclusion()
        coinvariant_inclusion = self.orthogonal_complement_inclusion()
        invariant_summand = invariant_inclusion.domain()
        coinvariant_summand = coinvariant_inclusion.domain()
        assert invariant_part.parent() is invariant_summand.Aut(), (
            f"{invariant_part} lies in {invariant_part.parent()}, not in the orthogonal "
            f"group O(L^f) of the invariant lattice {invariant_summand}"
        )
        assert coinvariant_part.parent() is coinvariant_summand.Aut(), (
            f"{coinvariant_part} lies in {coinvariant_part.parent()}, not in the "
            f"orthogonal group O((L^f)^perp) of {coinvariant_summand}"
        )
        coinvariant_isometry = self.coinvariant_restriction(self.isometry)
        assert coinvariant_part * coinvariant_isometry == coinvariant_isometry * coinvariant_part, (
            f"({invariant_part}, {coinvariant_part}) does not give an element of O(L, f) "
            f"for f = {self.isometry}: the second component does not commute with f on "
            f"(L^f)^perp"
        )
        assert self.pair_preserves_glue_graph(invariant_part, coinvariant_part), (
            f"({invariant_part}, {coinvariant_part}) does not extend to an isometry of "
            f"{lattice}: it does not preserve the graph of the glue anti-isometry, "
            f"which is Nikulin's criterion for extending across L^f + (L^f)^perp -> L"
        )

        ring = lattice.base_ring()
        scalar = ring(int(self.index().finite_value()))
        inclusion = self.orthogonal_sum_inclusion()
        summands = inclusion.domain()
        moved = summands.module_category().Mor(summands, lattice)(
            tuple(invariant_inclusion(invariant_part(generator)) for generator in invariant_summand.module_generators())
            + tuple(coinvariant_inclusion(coinvariant_part(generator)) for generator in coinvariant_summand.module_generators())
        )
        scaling = lattice.module_category().Mor(lattice, lattice)(tuple(lattice.scalar_multiple(scalar, generator) for generator in lattice.module_generators()))

        def image(label):
            scaled = lattice.scalar_multiple(scalar, lattice.module_generator(label))
            return scaling.lift(moved(inclusion.lift(scaled)))

        return lattice.O()(image)

    def equivariant_vector_orbit_representatives(self, square):
        r"""Return ``O(L,f)``-orbit representatives of the vectors of ``square``.

        The centralizer is a subgroup of ``O(L)`` cut out by a predicate and
        not by a character, so the finite-character quotient that splits an
        ``O(L)`` orbit does not describe it.  What describes it is the group
        itself, and acting with it is a finite computation exactly when
        ``O(L)`` is finite, which for a lattice is definiteness; the
        assertion in the owning subgroup operation states that hypothesis.
        For the orbits under the full ``O(L)`` use
        ``L.O().vector_orbit_representatives(square)``.
        """
        return self.isometry.equivariant_vector_orbit_representatives(square)

    def equivariant_vector_orbit_decomposition(self, square):
        r"""Return the exact decorated-vector orbit package for this isometry."""
        return self.isometry.equivariant_vector_orbit_decomposition(square)

    def __repr__(self) -> str:
        return f"Primitive extension of {self.lattice} cut out by {self.isometry}"


def arithmetic_centralizer(orthogonal_group, isometry):
    r"""Return ``Z_{O(L)}(f)``, its group generators selected to be computed on first request.

    The subgroup is the predicate subgroup ``{g in O(L) : g f = f g}``.
    Construction computes nothing (``OWN-22``): the generating family is
    computed by :func:`_arithmetic_centralizer_group_generators` when
    ``group_generators()`` is first read.
    """
    from sage_extensions.categories.group.groups import OwnedGroups
    from sage_extensions.categories.group.predicate_subgroups import (
        CentralizerSubgroups,
    )

    centralizer = CentralizerSubgroups(orthogonal_group)(isometry)
    if not centralizer.has_selected_resolution(OwnedGroups()):
        centralizer.select_group_generators(
            lambda: _arithmetic_centralizer_group_generators(centralizer)
        )
    return centralizer


def _arithmetic_centralizer_group_generators(centralizer):
    r"""Compute a generating set of ``Z = Z_{O(L)}(f)`` for ``f`` of finite order.

    Let ``L_d = ker Phi_d(f)`` be the nonzero cyclotomic summands.

    - One summand with ``d`` in ``{1, 2}``: ``f = 1`` or ``f = -1`` is
      central, ``Z = O(L)``, and its generators are those of ``O(L)``.
    - ``L`` definite: ``O(L)`` is finite and GAP computes the centralizer of
      ``f`` in it.
    - Two or more summands: ``Z`` is glued from the component centralizers
      ``Z_{O(L_d)}(f_d)`` by
      :meth:`CyclotomicDecomposition.glued_centralizer_generators`.
    - One summand of rank ``phi(d)`` with ``d > 2`` over ``ZZ``: the hermitian
      rank is one, and ``Z`` is generated by ``f`` and ``-id``.  This is the
      rank-one branch of OSCAR ``image_centralizer_in_Oq`` at the pinned
      commit ``d135b70b``, ``lattices_with_isometry.jl:1737-1744``.
    - One summand with ``d > 2`` of larger hermitian rank in an indefinite
      ``L``: no route computes generators of its unitary group (port #18,
      2026-10-15).  That frontier asserts.
    """
    from sage.rings.infinity import Infinity

    from sage_extensions.categories.group.groups import (
        _finite_group_centralizer_generators,
    )

    group = centralizer.supergroup()
    isometry = centralizer.centralizing_element()
    lattice = group.lattice()
    framing = tuple(lattice.module_generators())
    if all(isometry(generator) == generator for generator in framing) or all(
        isometry(generator) == -generator for generator in framing
    ):
        return finite_ordered_set(tuple(group.group_generators()))
    order = isometry.module_morphism().multiplicative_order()
    assert order != Infinity, (
        f"the centralizer of {isometry} in {group} has group generators computed here only "
        f"for an isometry of finite order, through the cyclotomic summands ker Phi_d(f); "
        f"{isometry} has infinite order"
    )
    decomposition = isometry.cyclotomic_decomposition(order)
    nonzero_divisors = tuple(int(divisor) for divisor in decomposition.nonzero_divisors())
    match nonzero_divisors:
        case (1,) | (2,):
            generators = group.group_generators()
        case _ if lattice.is_definite():
            generators = _finite_group_centralizer_generators(group, isometry)
        case (_, _, *_):
            generators = decomposition.glued_centralizer_generators()
        case (divisor,) if (
            lattice.base_ring() is _owned_integers()
            and int(lattice.module_rank()) == int(euler_phi(divisor))
            and lattice.is_nondegenerate()
        ):
            # On the one-dimensional Q(zeta_d)-space, a commuting isometry
            # is multiplication by a with a * conjugate(a) = 1.  Its action
            # on L makes a an algebraic integer; every conjugate has absolute
            # value one, so Kronecker's theorem makes it a root of unity.
            # All roots of unity of Q(zeta_d) are generated by -1 and zeta_d,
            # and both act integrally as -id and f on this very lattice.
            negation = group(lambda label: -lattice.module_generator(label))
            generators = (isometry, negation)
        case (divisor,):
            assert False, (
                f"the centralizer of {isometry} in {group} is the unitary group of {lattice} "
                f"as a hermitian lattice over ZZ[zeta_{divisor}], on which {isometry} acts "
                f"by zeta_{divisor}; {lattice} is indefinite, and no route computes generators "
                f"of that unitary group (port #18, 2026-10-15)"
            )
    return finite_ordered_set(tuple(centralizer(generator) for generator in generators))


__all__ = [
    "CyclotomicDecomposition",
    "IsometryPrimitiveExtension",
    "PolarizedEquivariantLattice",
]
