"""Subgroups specified by a membership predicate rather than generators."""

from sage.misc.cachefunc import cached_method

from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.abstract_categories.objects import (
    OwnedParameterizedCategory,
    _fix_selected_resolution,
)
from sage_extensions.categories.group.groups import (
    OwnedFiniteGroups,
    OwnedGroups,
    Subgroups,
    _selected_group_resolution,
    _finite_group_morphism_kernel_cardinality,
    _finite_group_morphism_kernel_is_abelian,
    _finite_if_bounded_by,
    _owned_group,
)
from sage_extensions.categories.orthogonal_quotients import (
    OrthogonalCharacterQuotient,
    _subgroup_isotropic_orbit_representatives,
    _subgroup_vector_orbit_representatives,
)
from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.set_categories import Set, _ConditionSetEngine
from sage_extensions.logic import AtomicProposition, conjunction
from sage_extensions.owned_category import _object_of


def _retains_group_resolution(group) -> bool:
    r"""Whether ``group`` has a selected free-group augmentation, without realizing it."""
    return group.has_selected_resolution(OwnedGroups())


def _fix_selected_generating_morphism(subgroup, generating_morphism) -> None:
    r"""Retain ``E ->> H`` from a free group as ``H``'s selected resolution, realized at first read.

    ``generating_morphism`` computes, from the constructed subgroup, a group
    morphism from a free group onto it.  Fixing the datum at construction
    computes nothing (``OWN-22``): the morphism, and the degree-zero
    resolution read off its free basis, are built when the generators are
    first requested and cached by the resolution registry.
    """

    def resolution():
        augmentation = generating_morphism(subgroup)
        free = augmentation.domain()
        return _selected_group_resolution(
            subgroup,
            free,
            free.free_basis(),
            augmentation * free.group_generator_morphism(),
        )

    _fix_selected_resolution(subgroup, OwnedGroups(), resolution)


def _free_cover(ambient, generators):
    r"""``pi: F ->> G``: the selected free cover, or the free group on supplied generators of ``G``."""
    if generators is None:
        return ambient.selected_group_resolution().augmentation()
    return ambient.free_cover(generators)


def _preimage_coset_space(subgroup, morphism, target, generators):
    r"""``G/P`` for ``P = f^-1(K)``, ``f: G -> Q`` finite: the orbit of ``K`` in ``Q/K``.

    ``G`` acts on ``Q/K`` through ``f``; the stabilizer of the base point
    ``K`` is ``f^-1(K) = P``.  The finiteness used is that of ``Q``.
    """
    from sage_extensions.categories.group.g_sets import FiniteGSets

    assert morphism.codomain() in OwnedFiniteGroups(), (
        f"the cosets of {subgroup} are realized through the finite group {morphism.codomain()}, "
        f"but it is not known to be finite"
    )
    image_cosets = morphism.codomain().left_cosets(target)
    return FiniteGSets(subgroup.supergroup()).pointed_orbit(
        subgroup,
        image_cosets.base_point(),
        lambda element, point: image_cosets.act(morphism(element), point),
        _free_cover(subgroup.supergroup(), generators),
    )


def _predicate_subgroup_category(category):
    r"""The category a predicate subgroup of ``category.base()`` is constructed in.

    A subgroup of a finite group is finite (Lagrange), and every subgroup
    of an abelian group is abelian. Both refinements follow from the
    ambient group, independently of whether the predicate is decidable.
    For example, the equalizer of two maps of abelian groups must remain
    in Ab, whereas the equalizer of arbitrary group maps need not.
    """
    group = category.base()
    return Cat().meet((
        category,
        *_finite_if_bounded_by(group),
        *((OwnedGroups().Commutative(),) if group in OwnedGroups().Commutative() else ()),
    ))


class PredicateSubgroups(OwnedParameterizedCategory):

    @staticmethod
    def __classcall__(cls, supergroup):
        return OwnedParameterizedCategory.__classcall__(cls, _owned_group(supergroup))

    def parameter_category(self):
        return OwnedGroups()

    def an_object(self):
        r"""The whole parameter group cut out by the tautological predicate.

        Every element commutes with the identity, so this is the whole group --
        cut out by a predicate, which is what membership here states.
        """
        group = self.base()
        return group.centralizer(group.one())

    def _repr_object_names(self):
        return "predicate subgroups"

    def super_categories(self):
        return [Subgroups(self.base())]

    def _call_(
        self,
        predicate,
        description,
        *,
        character_data=None,
        character_data_complete=None,
        generating_morphism=None,
        cardinality_decision=None,
        enumeration=None,
    ):
        r"""Construct the predicate subgroup of this category's ambient group.

        ``generating_morphism``, when the constructing owner has one, is a
        group morphism from a free group to the ambient group whose image is
        this subgroup; it becomes the subgroup's selected generating datum,
        as for :class:`StabilizerSubgroups`.
        """
        return _object_of(
            _predicate_subgroup_category(self),
            _ambient=OwnedGroups(),
            supergroup=self.base(),
            predicate=predicate,
            description=description,
            character_data=character_data,
            character_data_complete=character_data_complete,
            generating_morphism=generating_morphism,
            cardinality_decision=cardinality_decision,
            enumeration=enumeration,
        )

    class ParentMethods:
        def __init__(
            self,
            supergroup,
            predicate,
            description,
            character_data=None,
            character_data_complete=None,
            generating_morphism=None,
            cardinality_decision=None,
            enumeration=None,
            **rest,
        ) -> None:
            self._predicate = predicate
            self._admitted_members = {}
            self._description = description
            self._character_data = dict(character_data or {})
            self._character_data_complete = (
                bool(character_data)
                if character_data_complete is None
                else bool(character_data_complete)
            )
            self._specified_cardinality_decision = cardinality_decision
            self._specified_enumeration = enumeration
            super().__init__(supergroup=supergroup, **rest)
            # A generating morphism E -> G supplied by the constructing owner,
            # with image this subgroup, is a selected datum; its corestriction
            # to this subgroup is realized at the first read.  A bare
            # predicate supplies none.
            if generating_morphism is not None:
                _fix_selected_generating_morphism(
                    self,
                    lambda subgroup: generating_morphism._corestrict_to_subgroup(subgroup),
                )

        def defining_predicate(self):
            return self._predicate

        def universe(self):
            r"""The literal ambient set for the inherited predicate-subset operations."""
            return self.supergroup()

        predicate = defining_predicate

        # The subgroup is the same predicate subset of its ambient group.
        # Reuse the set owner's membership, admission and enumeration rules;
        # group closure is a premise of this subgroup construction.
        __contains__ = _ConditionSetEngine.__contains__
        is_parent_of = __contains__
        _points_satisfying = _ConditionSetEngine._points_satisfying
        _retain_admitted_member = _ConditionSetEngine._retain_admitted_member

        def __iter__(self):
            r"""Enumerate ``{g in G : P(g)}`` by filtering an enumeration of ``G``.

            A finite group is enumerated by its realization (GAP's for an
            engine group, Sage's ``GroupOfIsometries`` for ``O(L)`` of a
            definite lattice over ``ZZ``), so a predicate subgroup of a
            finite group is that enumeration filtered by ``P``; a
            realization without one states its own frontier.  Any other
            supergroup is enumerated by the set owner's rule, from a chosen
            enumeration of ``G``.
            """
            group = self.supergroup()
            if self._specified_enumeration is not None:
                selected = self._specified_enumeration()
                if selected is not None:
                    return iter(selected)
            match group:
                case _ if group in OwnedFiniteGroups():
                    return self._points_satisfying(group)
                case _:
                    return _ConditionSetEngine.__iter__(self)

        def _element_constructor_(self, datum):
            r"""Read ambient group literals, then use the set owner's predicate admission."""
            return _ConditionSetEngine._element_constructor_(self, self.supergroup()(datum))

        def finite_index_schreier_generators(self, *, index_bound, generators=None):
            r"""Generate a finite-index predicate subgroup by coset traversal.

            The index bound is required: a predicate alone does not certify
            finite index. Representatives of cosets ``r H`` are recognized
            by membership of ``r^(-1) x`` in ``H``. The resulting Schreier
            words ``t_(s r H)^(-1) s r`` generate the subgroup.

            EXAMPLES::

                sage: G = Groups.S(3)
                sage: H = G.subgroup((G((1, 2)),))
                sage: P = G.predicate_subgroup(lambda g: g in H, "transposition subgroup")
                sage: generators = P.finite_index_schreier_generators(index_bound=3)
                sage: all(g in P for g in generators)
                True
                sage: G.subgroup(generators).cardinality() == 2
                True
                sage: P.finite_index_schreier_generators(index_bound=2)
                Traceback (most recent call last):
                ...
                ValueError: the subgroup index exceeds the supplied bound
                sage: P.finite_index_schreier_generators(index_bound=2.5)
                Traceback (most recent call last):
                ...
                ValueError: the subgroup index bound must be an integer
                sage: F, C = Groups.Free(1), Groups.C(2)
                sage: s, t = F.group_generators()[0], C.group_generators()[0]
                sage: phi = F.Mor(C)({next(iter(F.free_basis())): t})
                sage: P = F.predicate_subgroup(lambda g: phi(g) == C.one(), "even exponent")
                sage: generators = P.finite_index_schreier_generators(index_bound=2)
                sage: any(g == s*s or g == ~(s*s) for g in generators)
                True
            """
            ambient = self.supergroup()
            if generators is None:
                assert ambient.has_selected_group_resolution() and ambient.has_selected_finite_group_generating_set(), (
                    f"cannot compute finite Schreier generators of {self}: {ambient} has no "
                    "selected finite generating set; pass a finite generating family"
                )
                generators = tuple(ambient.group_generators())
            else:
                generators = tuple(generators)
            bound = int(index_bound)
            if bound != index_bound:
                raise ValueError("the subgroup index bound must be an integer")
            if bound < 1:
                raise ValueError("the subgroup index bound must be positive")
            representatives = [ambient.one()]

            def representative_of(candidate):
                for representative in representatives:
                    if (~representative) * candidate in self:
                        return representative
                return None

            for representative in representatives:
                for generator in generators:
                    for step in (generator, ~generator):
                        candidate = step * representative
                        if representative_of(candidate) is None:
                            representatives.append(candidate)
                            if len(representatives) > bound:
                                raise ValueError("the subgroup index exceeds the supplied bound")
            from sage_extensions.categories.sets.finite_families import finite_family

            return finite_family(
                (
                    self((~representative_of(generator * representative)) * generator * representative)
                    for representative in representatives
                    for generator in generators
                ),
                name="Schreier generators of a finite-index subgroup",
            )

        def _selected_schreier_augmentation(self, words):
            r"""Map the free group on a selected Schreier family onto this subgroup.

            This is the common represented boundary for a *known* generating
            family of a predicate subgroup. Its input has an owned finite
            index set and actual elements of this subgroup; its output is
            the free-group Mor landing in this literal subgroup, rather than
            another subgroup generated by the same ambient elements.
            """
            from sage_extensions.categories.sets.indexed_families import IndexedFamily
            from sage_extensions.categories.sets.set_categories import FiniteSets, Sets

            if not isinstance(words, IndexedFamily) or words.index_set() not in FiniteSets():
                raise TypeError("Schreier augmentation requires an owned finite generator family")
            if not all(self.is_parent_of(words.value(label)) is True for label in words.index_set()):
                raise ValueError("Schreier augmentation generators must be admitted in the actual subgroup")
            free = OwnedGroups.Free(index_set=words.index_set())
            ambient_map = free.Mor(self.supergroup())(
                Sets().Mor(words.index_set(), self.supergroup())(
                    lambda label: words.value(label)
                )
            )
            return ambient_map.factor_through(self.inclusion())

        def finite_index_schreier_generating_morphism(self, *, index_bound, generators=None):
            r"""The free generating epimorphism onto a bounded finite-index subgroup."""
            words = self.finite_index_schreier_generators(
                index_bound=index_bound, generators=generators
            )
            return self._selected_schreier_augmentation(words)

        def _character_data_snapshot(self):
            r"""Return private finite-character representation metadata."""
            return dict(self._character_data)

        def character_data_is_complete(self) -> bool:
            r"""Whether the retained finite characters define this whole subgroup."""
            return self._character_data_complete

        def contains_character_kernel(self) -> bool:
            data = self._character_data_snapshot()
            return self.character_data_is_complete() and bool(
                data.get("determinant_kernel", False)
                or data.get("spinor_kernel", False)
                or data.get("discriminant_preimages", ())
            )

        def _finiteness_decision(self):
            r"""A subgroup of a finite group is finite; finite-index character preimages inherit infinitude."""
            ambient = self.supergroup().is_finite()
            if ambient is True:
                return True
            if ambient is False and self.contains_character_kernel():
                return False
            return AtomicProposition("is_finite", self)

        def _cardinality_decision(self):
            r"""``|H|``: from the retained character data, from selected generators, else by counting.

            With complete finite-character data ``H`` is the preimage of a
            subgroup of a finite quotient, so ``|H| = |G| |image of H| /
            |image of G|``. A selected finite generating family of ``H``
            gives its order through its own generated engine subgroup,
            independently of the ambient group's order. Otherwise, in a
            finite ``G``, ``H`` is the set of
            elements satisfying the predicate, counted exactly in one pass over
            ``G``, at a cost linear in ``|G|``: the predicate is a Python
            function, which GAP's subgroup search by a property cannot evaluate.
            """
            if self._specified_cardinality_decision is not None:
                return self._specified_cardinality_decision()
            if _retains_group_resolution(self) and not self.contains_character_kernel():
                generated = self.supergroup()._engine_subgroup_from_generators(
                    tuple(self.group_generators())
                )
                return cardinal(generated.order())
            supergroup_cardinality = self.supergroup().cardinality()
            if self.contains_character_kernel():
                quotient = self.finite_character_quotient()
                image_size = int(quotient.image_keys().cardinality())
                subgroup_image_size = int(quotient.subgroup_image_keys().cardinality())
                if supergroup_cardinality.is_finite():
                    order = int(supergroup_cardinality.finite_value())
                    return cardinal(order * subgroup_image_size // image_size)
                if supergroup_cardinality.is_countably_infinite():
                    return supergroup_cardinality
            assert supergroup_cardinality.is_finite(), (
                f"cannot compute the order of the subgroup {self}: its group "
                f"{self.supergroup()} has order {supergroup_cardinality}, which is not finite, "
                f"and the subgroup is not known as the preimage of a subgroup of a finite quotient"
            )
            return cardinal(sum(1 for _element in self))

        @cached_method
        def _engine_group(self):
            r"""The engine subgroup on this subgroup's selected determining family.

            Engine contract (``OWN-05``), declared in ``groups.py``.  The
            retained generating morphism supplies generators when present.
            A bare predicate instead supplies only its members, enumerated
            by the existing finite-supergroup rule.
            """
            generators = tuple(self.group_generators()) if _retains_group_resolution(self) else self
            return self.supergroup()._engine_subgroup_from_generators(generators)

        def _to_engine(self, element):
            assert element in self, f"{element} is not an element of the subgroup {self}"
            return self.supergroup()._to_subgroup_engine(element, self._engine_group())

        def _from_engine(self, engine_element):
            return self.supergroup()._from_subgroup_engine(engine_element)

        def one(self):
            r"""The ambient identity, which lies in the declared subgroup."""
            return self.supergroup().one()

        def intersection(self, other):
            if other.supergroup() is not self.supergroup():
                raise ValueError(
                    f"cannot intersect {self} and {other}: they are subgroups of different "
                    f"groups, {self.supergroup()} and {other.supergroup()}"
                )
            left = self._character_data_snapshot()
            right = other._character_data_snapshot()
            data = {
                "determinant_kernel": bool(left.get("determinant_kernel", False))
                or bool(right.get("determinant_kernel", False)),
                "spinor_kernel": bool(left.get("spinor_kernel", False))
                or bool(right.get("spinor_kernel", False)),
                "discriminant_preimages": tuple(left.get("discriminant_preimages", ()))
                + tuple(right.get("discriminant_preimages", ())),
            }
            return IntersectionSubgroups(self.supergroup())(
                (self, other),
                character_data=data,
                character_data_complete=(
                    self.character_data_is_complete()
                    and other.character_data_is_complete()
                ),
            )

        def finite_character_quotient(self):
            if not self.character_data_is_complete():
                raise ValueError(
                    f"{self} has no finite character quotient: it is not known to be the full "
                    f"preimage of a subgroup of a finite quotient of {self.supergroup()} by "
                    f"determinant, spinor norm and discriminant characters"
                )
            return OrthogonalCharacterQuotient(self)

        def has_finite_coset_space(self) -> bool:
            r"""Whether complete finite characters realize ``G/self`` as a finite ``G``-set."""
            return (
                self.contains_character_kernel()
                and self.supergroup().has_selected_group_resolution()
            )

        def coset_space(self, *, generators=None):
            r"""Realize the cosets of a complete finite-character subgroup.

            Complete character data states ``self = rho^-1(H)`` for a
            finite image, so the orbit of the identity coset is finite.
            The ordinary pointed-orbit construction retains its lifts and
            Schreier morphism, including when several character conditions
            were intersected and no single preimage presentation remains.
            """
            from sage_extensions.categories.group.g_sets import (
                FiniteGSets,
                _LeftCosetPointSet,
            )

            assert self.contains_character_kernel(), (
                f"{self} has no complete finite-character condition realizing its coset space"
            )
            group = self.supergroup()
            points = _LeftCosetPointSet(group, self)
            return FiniteGSets(group).pointed_orbit(
                self,
                points(group.one()),
                lambda element, coset: points(element * coset.representative()),
                _free_cover(group, generators),
            )

        def vector_orbit_representatives(self, square):

            return _subgroup_vector_orbit_representatives(self, square)

        def vectors_are_equivalent(self, left, right) -> bool:

            return self.vector_equivalence_witness(left, right) is not None

        def vector_equivalence_witness(self, left, right):
            from sage_extensions.categories.orthogonal_quotients import (
                _subgroup_vector_equivalence_witness,
            )

            return _subgroup_vector_equivalence_witness(self, left, right)

        def isotropic_orbit_representatives(self, rank, *, flag=False):

            return _subgroup_isotropic_orbit_representatives(
                self, rank, flag=flag
            )

        def isotropic_are_equivalent(self, left, right, *, flag=False) -> bool:

            return self.isotropic_equivalence_witness(left, right, flag=flag) is not None

        def isotropic_equivalence_witness(self, left, right, *, flag=False):
            from sage_extensions.categories.orthogonal_quotients import (
                _subgroup_isotropic_equivalence_witness,
            )

            return _subgroup_isotropic_equivalence_witness(
                self, left, right, flag=flag
            )

        def cusps(self, rank=1):
            r"""Return this arithmetic subgroup's primitive-isotropic cusp orbits."""
            from sage_extensions.categories.isotropic_orbits import _arithmetic_cusp
            from sage_extensions.categories.sets.finite_ordered_sets import (
                finite_ordered_set,
            )

            return finite_ordered_set(
                tuple(
                    _arithmetic_cusp(self, representative)
                    for representative in self.isotropic_orbit_representatives(rank)
                )
            )

        def tits_building_incidence(self):
            r"""Return this subgroup's line/plane quotient-building incidence.

            Rank-two flags are split under the same finite-character quotient
            as the line and plane orbits, so each edge retains actual subgroup
            transporters to its two cusp vertices rather than transporters
            inherited from the full orthogonal group.
            """
            from sage_extensions.categories.isotropic_orbits import (
                ArithmeticCuspIncidence,
            )
            from sage_extensions.categories.sets.finite_ordered_sets import (
                finite_ordered_set,
            )

            lattice = self.supergroup().domain()
            line_cusps = self.cusps(1)
            plane_cusps = self.cusps(2)
            incidences = []
            for flag in self.isotropic_orbit_representatives(2, flag=True):
                line, plane = flag.terms()
                line_vertices = tuple(cusp for cusp in line_cusps if line in cusp)
                plane_vertices = tuple(cusp for cusp in plane_cusps if plane in cusp)
                if len(line_vertices) != 1 or len(plane_vertices) != 1:
                    raise ArithmeticError(
                        f"the isotropic flag {flag} of {lattice} lies in {len(line_vertices)} "
                        f"line cusps and {len(plane_vertices)} plane cusps of {self}; each "
                        f"term of a flag must lie in exactly one cusp"
                    )
                line_cusp = line_vertices[0]
                plane_cusp = plane_vertices[0]
                line_transporter = line_cusp.transporter_witness(line)
                plane_transporter = plane_cusp.transporter_witness(plane)
                if line_transporter is None or plane_transporter is None:
                    raise ArithmeticError(
                        f"the isotropic flag {flag} of {lattice} lies in the cusps "
                        f"{line_cusp} and {plane_cusp} of {self}, but no element of {self} "
                        f"carries the cusp representatives to its terms"
                    )
                incidences.append(
                    ArithmeticCuspIncidence(
                        self,
                        flag,
                        line_cusp,
                        plane_cusp,
                        line_transporter,
                        plane_transporter,
                    )
                )
            if any(incidence.lattice() is not lattice for incidence in incidences):
                raise ArithmeticError(
                    f"the Tits building incidence of {self} has a cusp incidence in a lattice "
                    f"other than {lattice}, the lattice {self.supergroup()} acts on"
                )
            return finite_ordered_set(tuple(incidences))

        def _repr_(self):
            return f"{{g in {self.supergroup()} : {self._description}}}"


class _PredicateSubgroupConstruction(OwnedParameterizedCategory):
    @staticmethod
    def __classcall__(cls, supergroup):
        return OwnedParameterizedCategory.__classcall__(cls, _owned_group(supergroup))

    def parameter_category(self):
        return OwnedGroups()

    def super_categories(self):
        return [PredicateSubgroups(self.base())]

class KernelSubgroups(_PredicateSubgroupConstruction):
    def an_object(self):

        group = self.base()
        return self(group.Mor(group).identity())

    def _call_(self, morphism):
        r"""Construct the kernel subgroup retaining its defining morphism."""
        group = self.base()
        if morphism.domain() is not group:
            raise ValueError(
                f"{morphism} has no kernel in {group}: its domain is "
                f"{morphism.domain()}, not {group}"
            )
        identity = morphism.codomain().one()
        return _object_of(
            _predicate_subgroup_category(self),
            _ambient=OwnedGroups(),
            supergroup=group,
            predicate=lambda element: morphism(element) == identity,
            description="elements mapped to the identity by the defining morphism",
            kernel_morphism=morphism,
        )

    @classmethod
    def _repr_object_names(cls):
        return "kernel subgroups"

    class ParentMethods:
        def __init__(self, kernel_morphism, **rest) -> None:
            self._kernel_morphism = kernel_morphism
            super().__init__(**rest)
            # Schreier's lemma: a finitely generated group mapping to a finite
            # group has its kernel generated by the Schreier family of the
            # finite image, so that family is this kernel's selected datum.
            if (
                self.supergroup().has_selected_group_resolution()
                and kernel_morphism.codomain() in OwnedFiniteGroups()
            ):
                _fix_selected_generating_morphism(
                    self, lambda kernel: kernel.schreier_generating_morphism()
                )

        def kernel_morphism(self):
            return self._kernel_morphism

        def index(self, *, generators=None):
            r"""The index of a kernel with a represented finite image.

            First isomorphism: ``G/ker(f)`` is the image of ``f``. The
            finite-image transversal retains a representative of every
            image element, including when ``G`` is infinite. Explicit
            generators may be supplied when the ambient group has not
            selected a generating resolution.
            """
            return self.coset_space(generators=generators).cardinality()

        def has_finite_coset_space(self) -> bool:
            r"""Whether ``G/ker(f)`` is realized through ``f`` into a finite group with selected generators of ``G``."""
            return (
                self.kernel_morphism().codomain() in OwnedFiniteGroups()
                and self.supergroup().has_selected_group_resolution()
            )

        def coset_space(self, *, generators=None):
            r"""``G/ker(f)`` as the orbit of the identity in ``Q`` under ``G`` acting through ``f``."""
            morphism = self.kernel_morphism()
            return _preimage_coset_space(self, morphism, morphism.codomain().subgroup(()), generators)

        def schreier_generating_morphism(self, *, generators=None):
            r"""Schreier's lemma on the coset space ``G/ker(f)`` with its section."""
            return self.coset_space(generators=generators).schreier_generating_morphism()

        def _cardinality_decision(self):
            r"""Return the exact kernel order when the ambient group is finite."""
            if self.kernel_morphism().is_injective() is True:
                return cardinal(1)
            if self.supergroup().is_finite() is True:
                return _finite_group_morphism_kernel_cardinality(
                    self.kernel_morphism()
                )
            return super()._cardinality_decision()

        def _abelianity_decision(self):
            r"""Decide abelianity from the represented exact kernel when finite."""
            if self.supergroup().is_finite() is True:
                return _finite_group_morphism_kernel_is_abelian(
                    self.kernel_morphism()
                )
            assert False, (
                f"cannot decide whether the kernel {self} of {self.kernel_morphism()} is "
                f"abelian: this is decided only when the domain {self.supergroup()} is known "
                f"to be finite"
            )


class PreimageSubgroups(_PredicateSubgroupConstruction):
    def an_object(self):

        group = self.base()
        whole = PredicateSubgroups(group)(lambda _element: True, "the whole group")
        return self(group.Mor(group).identity(), whole)

    def _call_(
        self,
        morphism,
        subgroup,
        *,
        predicate=None,
        description=None,
        character_data=None,
        character_data_complete=None,
        generating_morphism=None,
    ):
        r"""Construct the inverse image of ``subgroup`` along ``morphism``.

        ``generating_morphism``, when the constructing owner has one, maps
        the constructed preimage to a free generating morphism onto it.
        Otherwise a finitely generated source mapping to a finite group
        selects the Schreier family of the finite image.
        """
        group = self.base()
        if morphism.domain() is not group:
            raise ValueError(
                f"cannot take the preimage of {subgroup} along {morphism} as a subgroup of "
                f"{group}: the domain of {morphism} is {morphism.domain()}, not {group}"
            )
        if subgroup is morphism.codomain():
            subgroup = PredicateSubgroups(subgroup)(
                lambda _element: True, "the whole codomain"
            )
        if subgroup not in Subgroups(morphism.codomain()):
            raise ValueError(
                f"cannot take the preimage of {subgroup} under {morphism}: "
                f"the specified target is not a subgroup of {morphism.codomain()}"
            )
        if predicate is None:
            def predicate(element):
                return subgroup.is_parent_of(morphism(element))
        if description is None:
            description = f"{morphism}(g) lies in {subgroup}"
        return _object_of(
            _predicate_subgroup_category(self),
            _ambient=OwnedGroups(),
            supergroup=group,
            predicate=predicate,
            description=description,
            character_data=character_data,
            character_data_complete=character_data_complete,
            preimage_morphism=morphism,
            target_subgroup=subgroup,
            generating_morphism=generating_morphism,
        )

    @classmethod
    def _repr_object_names(cls):
        return "preimage subgroups"

    class ParentMethods:
        def __init__(self, preimage_morphism, target_subgroup, **rest) -> None:
            self._preimage_morphism = preimage_morphism
            self._target_subgroup = target_subgroup
            super().__init__(**rest)
            if (
                not _retains_group_resolution(self)
                and self.supergroup().has_selected_group_resolution()
                and preimage_morphism.codomain() in OwnedFiniteGroups()
            ):
                _fix_selected_generating_morphism(
                    self, lambda preimage: preimage.schreier_generating_morphism()
                )

        def preimage_morphism(self):
            return self._preimage_morphism

        def target_subgroup(self):
            return self._target_subgroup

        def has_finite_coset_space(self) -> bool:
            r"""Whether ``G/f^-1(K)`` is realized through ``f`` into a finite group with selected generators of ``G``."""
            return (
                self.preimage_morphism().codomain() in OwnedFiniteGroups()
                and self.supergroup().has_selected_group_resolution()
            )

        def coset_space(self, *, generators=None):
            r"""``G/f^-1(K)`` as the orbit of ``K`` in ``Q/K`` under ``G`` acting through ``f``."""
            return _preimage_coset_space(
                self, self.preimage_morphism(), self.target_subgroup(), generators
            )

        def schreier_generating_morphism(self, *, generators=None):
            r"""Schreier's lemma on the coset space ``G/f^-1(K)`` with its section.

            Explicit generators may replace the selected cover of the ambient
            group; they must generate it.
            """
            return self.coset_space(generators=generators).schreier_generating_morphism()

        def selected_group_resolution(self):
            r"""The selected generating epimorphism onto ``f^-1(K)``, assembled when ``f: G -> Q`` has infinite codomain.

            For finite ``Q`` the Schreier family is selected at construction.
            For infinite ``Q``, ``f^-1(K) = f^-1(K cap f(G))`` is generated by
            ``ker(f)`` together with one preimage of each generator of
            ``K cap f(G)`` (``kernel_image_generating_morphism``), from three
            data the caller supplies: generators selected on ``f.kernel()``,
            a finite realization of ``Q / f(G)`` (``Q.left_cosets(f.image())``
            a finite ``Q``-set, e.g. by ``Q.select_left_cosets``), and a
            section of ``f`` on its image (``f.lift``).  Each missing datum is
            asserted by name.  The family is computed on first request and
            retained (``OWN-22``).
            """
            match self.preimage_morphism().codomain():
                case _ if _retains_group_resolution(self):
                    pass
                case codomain if codomain in OwnedFiniteGroups():
                    pass
                case _:
                    _fix_selected_generating_morphism(
                        self, lambda preimage: preimage.kernel_image_generating_morphism()
                    )
            return super().selected_group_resolution()

        def kernel_image_generating_morphism(self):
            r"""``E ->> f^-1(K)`` sending free generators to ``ker(f)``'s and to lifts of ``K cap f(G)``'s generators.

            ``K cap f(G)`` is the stabilizer in ``K`` of the base coset of the
            finite ``Q``-set ``Q / f(G)``; Schreier's lemma on the ``K``-orbit
            of that coset gives its generators.  Their preimages under ``f``
            together with the generators of ``ker(f)`` generate ``f^-1(K)``:
            for ``g in f^-1(K)``, ``f(g)`` is a word in the former, and ``g``
            differs from that word's lift by an element of ``ker(f)``.
            """
            from sage_extensions.categories.group.g_sets import FiniteGSets

            morphism = self.preimage_morphism()
            target = self.target_subgroup()
            codomain = morphism.codomain()
            kernel = morphism.kernel()
            assert kernel.has_selected_group_resolution(), (
                f"the preimage {self} is generated by ker({morphism}) and lifts of generators of "
                f"{target} cap {morphism}({self.supergroup()}), but no generators of the kernel were "
                f"supplied, and {codomain} is not known to be finite so Schreier's lemma does not give "
                f"them: select them with {morphism}.kernel().select_group_resolution(generators=...)"
            )
            image = morphism.image()
            image_cosets = codomain.left_cosets(image)
            assert image_cosets in FiniteGSets(codomain), (
                f"the preimage {self} needs {target} cap {image} generated through the finite "
                f"coset space {codomain}/{image}, but {image} is not known to have finite index in "
                f"{codomain}: realize {codomain}/{image} as a finite {codomain}-set and select it with "
                f"{codomain}.select_left_cosets(...)"
            )
            assert target.has_selected_group_resolution(), (
                f"the preimage {self} needs generators of {target}, which has none selected"
            )
            inclusion = target.inclusion()
            base = image_cosets.base_point()
            intersection = target.predicate_subgroup(
                lambda element: image_cosets.act(inclusion(element), base) == base,
                f"elements of {target} in {image}",
            )
            orbit = FiniteGSets(target).pointed_orbit(
                intersection,
                base,
                lambda element, point: image_cosets.act(inclusion(element), point),
            )
            schreier = orbit.schreier_generating_morphism()
            lifts = tuple(
                morphism.lift(inclusion(intersection.inclusion()(schreier(word))))
                for word in schreier.domain().group_generators()
            )
            elements = (
                *(kernel.inclusion()(generator) for generator in kernel.group_generators()),
                *lifts,
            )
            cover = self.supergroup().free_cover(elements)
            return cover.factor_through(self.inclusion())

class StabilizerSubgroups(_PredicateSubgroupConstruction):
    def an_object(self):
        group = self.base()
        identity = group.one()
        return self(
            identity,
            group.conjugation_g_set().action_functor(),
            lambda element: element * identity * element.inverse() == identity,
        )

    def _call_(
        self,
        stabilized_object,
        action,
        predicate,
        *,
        description=None,
        generating_morphism=None,
        basis_change=None,
    ):
        r"""Construct the stabilizer retaining the stabilized object and action.

        ``generating_morphism`` is the action owner's free generating
        morphism onto the stabilizer, when its action supplies one.
        ``basis_change`` is the automorphism of the acted-on object through
        which that owner computed the generators (the basis adapted to a
        flag), when it used one.
        """
        from sage_extensions.categories.functors.core import Functor

        group = self.base()
        if not isinstance(action, Functor) or action.domain() is not group.classifying_category():
            raise TypeError(
                f"the stabilizer of {stabilized_object} in {group} requires the actual "
                f"action functor B({group}) -> C, but received {action!r}"
            )
        if description is None:
            description = f"g stabilizes {stabilized_object} {action}"
        return _object_of(
            _predicate_subgroup_category(self),
            _ambient=OwnedGroups(),
            supergroup=group,
            predicate=predicate,
            description=description,
            stabilized_object=stabilized_object,
            stabilizer_action=action,
            generating_morphism=generating_morphism,
            basis_change=basis_change,
        )

    @classmethod
    def _repr_object_names(cls):
        return "stabilizer subgroups"

    class ParentMethods:
        def __init__(self, stabilized_object, stabilizer_action, basis_change=None, **rest) -> None:
            self._stabilized_object = stabilized_object
            self._stabilizer_action = stabilizer_action
            self._basis_change = basis_change
            super().__init__(**rest)

        def basis_change(self):
            r"""The automorphism ``P`` the generators were computed through: ``P(e_j) = b_j``, ``b`` adapted to the stabilized flag."""
            assert self._basis_change is not None, (
                f"{self} was not constructed through an adapted basis"
            )
            return self._basis_change

        def stabilized_object(self):
            return self._stabilized_object

        def stabilizer_action(self):
            return self._stabilizer_action

        def restricted_stabilizer_action(self):
            r"""The action of this stabilizer, restricted along its inclusion.

            For ``i: H -> G`` and the retained action ``rho: BG -> C``,
            this is the actual composite ``B(i) ; rho: BH -> C``.
            It retains the original stabilized object and does not replace
            the action by the predicate defining membership in ``H``.

            Unexecuted distinguishing specimen: take ``G = S3`` acting on
            itself by conjugation, and ``H = Stab_G((1,2))``. The restricted
            action has domain ``BH``, not ``BG``; on the unique object it
            agrees with the original action, while the morphism associated
            to ``h in H`` acts as conjugation by its image under ``i``.
            In particular, merely returning ``rho`` would have the wrong
            domain, even though every ``h`` fixes the selected point.
            """
            from sage_extensions.categories.group.classifying_categories import (
                ClassifyingFunctor,
            )

            return ClassifyingFunctor(self.inclusion()).then(self.stabilizer_action())


class CentralizerSubgroups(_PredicateSubgroupConstruction):
    def an_object(self):
        group = self.base()
        return self(group.one())

    def _call_(self, element):
        r"""Construct the centralizer of ``element`` in the ambient group."""
        group = self.base()
        if element not in group:
            raise ValueError(
                f"cannot form the centralizer of {element} in {group}: {element} is not an "
                f"element of {group}"
            )
        return _object_of(
            _predicate_subgroup_category(self),
            _ambient=OwnedGroups(),
            supergroup=group,
            predicate=lambda candidate: element * candidate == candidate * element,
            description=f"g commutes with {element}",
            centralizing_element=element,
        )

    @classmethod
    def _repr_object_names(cls):
        return "centralizer subgroups"

    class ParentMethods:
        def __init__(self, centralizing_element, **rest) -> None:
            self._centralizing_element = centralizing_element
            super().__init__(**rest)

        def centralizing_element(self):
            return self._centralizing_element


class IntersectionSubgroups(_PredicateSubgroupConstruction):
    def an_object(self):
        group = self.base()
        whole = PredicateSubgroups(group)(lambda _element: True, "the whole group")
        return self((whole, whole))

    def _call_(
        self,
        subgroups,
        *,
        character_data=None,
        character_data_complete=None,
    ):
        r"""Construct the intersection of subgroups of this ambient group."""
        group = self.base()
        subgroups = tuple(subgroups)
        if any(subgroup.supergroup() is not group for subgroup in subgroups):
            raise ValueError(
                f"cannot form the intersection in {group}: the subgroups "
                f"{[subgroup for subgroup in subgroups if subgroup.supergroup() is not group]} "
                f"are not subgroups of {group}"
            )
        return _object_of(
            _predicate_subgroup_category(self),
            _ambient=OwnedGroups(),
            supergroup=group,
            predicate=lambda element: conjunction(subgroup.is_parent_of(element) for subgroup in subgroups),
            description="g lies in every selected subgroup",
            character_data=character_data,
            character_data_complete=character_data_complete,
            intersected_subgroups=Set(subgroups),
        )

    @classmethod
    def _repr_object_names(cls):
        return "intersection subgroups"

    class ParentMethods:
        def __init__(self, intersected_subgroups, **rest) -> None:
            self._intersected_subgroups = intersected_subgroups
            super().__init__(**rest)
            # For f: G -> F finite, K <= F and B <= G finitely generated with
            # inclusion i, f^-1(K) cap B = i((f i)^-1(K)); the Schreier family
            # of that restricted preimage, pushed into G, generates this
            # intersection.
            if not _retains_group_resolution(self) and intersected_subgroups.cardinality() == cardinal(2):
                group = self.supergroup()
                for preimage in intersected_subgroups:
                    match preimage:
                        case _ if preimage in KernelSubgroups(group):
                            morphism = preimage.kernel_morphism()
                            target = morphism.codomain().subgroup(())
                        case _ if preimage in PreimageSubgroups(group):
                            morphism = preimage.preimage_morphism()
                            target = preimage.target_subgroup()
                        case _:
                            continue
                    generated = next(
                        other for other in intersected_subgroups if other is not preimage
                    )
                    if morphism.codomain() in OwnedFiniteGroups() and generated.has_selected_group_resolution():
                        _fix_selected_generating_morphism(
                            self,
                            lambda intersection, morphism=morphism, target=target, generated=generated: (
                                intersection._restricted_preimage_generating_morphism(
                                    morphism, target, generated
                                )
                            ),
                        )
                        return
                # An intersection of several character kernels/preimages is
                # still a finite-index subgroup, even though it is no longer
                # presented by one PreimageSubgroups object.  Restrict its
                # complete character condition to the supplied generated
                # subgroup and apply the same finite-index Schreier lemma.
                for character_subgroup in intersected_subgroups:
                    if (
                        character_subgroup not in PredicateSubgroups(group)
                        or not character_subgroup.contains_character_kernel()
                    ):
                        continue
                    generated = next(
                        other for other in intersected_subgroups if other is not character_subgroup
                    )
                    if generated.has_selected_group_resolution():
                        _fix_selected_generating_morphism(
                            self,
                            lambda intersection, character_subgroup=character_subgroup, generated=generated: (
                                intersection._restricted_character_generating_morphism(
                                    character_subgroup, generated
                                )
                            ),
                        )
                        return

        def intersected_subgroups(self):
            return self._intersected_subgroups

        def _restricted_preimage_generating_morphism(self, morphism, target, generated):
            r"""``E ->> f^-1(K) cap B`` through the Schreier morphism onto ``(f i)^-1(K)``."""
            inclusion = generated.inclusion()
            restricted = (morphism * inclusion).preimage_subgroup(target)
            augmentation = restricted.schreier_generating_morphism()
            return (inclusion * restricted.inclusion() * augmentation).factor_through(self.inclusion())

        def _restricted_character_generating_morphism(self, character_subgroup, generated):
            r"""Generate ``Gamma cap B`` by restricting a finite character condition to ``B``.

            If ``Gamma = rho^-1(H)`` in ``G``, then
            ``[B:B cap Gamma] <= [rho(G):H]``.  This exact finite bound
            supplies the existing predicate-subgroup Schreier computation;
            no membership or word algorithm for an arbitrary generated
            subgroup of ``G`` is assumed.
            """
            quotient = character_subgroup.finite_character_quotient()
            index_bound = (
                int(quotient.image_keys().cardinality())
                // int(quotient.subgroup_image_keys().cardinality())
            )
            inclusion = generated.inclusion()
            restricted = generated.predicate_subgroup(
                lambda element: inclusion(element) in character_subgroup,
                f"the inclusion into {self.supergroup()} lies in {character_subgroup}",
            )
            augmentation = restricted.finite_index_schreier_generating_morphism(
                index_bound=index_bound,
                generators=generated.group_generators(),
            )
            return (inclusion * restricted.inclusion() * augmentation).factor_through(self.inclusion())

__all__ = [
    "CentralizerSubgroups",
    "IntersectionSubgroups",
    "KernelSubgroups",
    "PredicateSubgroups",
    "PreimageSubgroups",
    "StabilizerSubgroups",
]
