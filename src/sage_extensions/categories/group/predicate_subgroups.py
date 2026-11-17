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
    _named_by_its_own_words,
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


def _fix_selected_generating_morphism(subgroup, generating_morphism, *, replace=False) -> None:
    r"""Retain ``E ->> H`` from a free group as ``H``'s selected resolution, realized at first read.

    ``generating_morphism`` computes, from the constructed subgroup, a group
    morphism from a free group onto it.  Fixing the datum at construction
    computes nothing (``OWN-22``): the morphism, and the degree-zero
    resolution read off its free basis, are built when the generators are
    first requested and cached by the resolution registry.

    ``replace`` lets the constructing owner supersede a family a coarser rule
    selected at construction --- the preimage construction selects Schreier's
    family over the cosets of a finite target group, and an owner that reads
    the acted-on point itself (``LatticeIsometryMethods.discriminant_preimage``)
    supplies the same subgroup's family from that point's orbit instead.
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

    _fix_selected_resolution(subgroup, OwnedGroups(), resolution, replace=replace)


def _free_cover(ambient, generators):
    r"""``pi: F ->> G``: the selected free cover, or the free group on supplied generators of ``G``."""
    if generators is None:
        return ambient.selected_group_resolution().augmentation()
    return ambient.free_cover(generators)


def _preimage_coset_space(subgroup, morphism, target, generators):
    r"""G/f^-1(H) as the image's orbit of H in the finite target's cosets."""
    from sage_extensions.categories.group.g_sets import FiniteGSets

    return FiniteGSets(subgroup.supergroup()).preimage_coset_space(
        subgroup, morphism, target, _free_cover(subgroup.supergroup(), generators),
    )


def _incidence_ambient_sources(subgroup, quotient):
    r"""The ambient flag row, with one registered source plane named for each flag.

    The incidence covers the ``Stab_Gamma(P)``-orbits of the lines of a plane by
    the ambient flag row carried to that plane: for each ambient flag orbit a
    source plane is registered in the quotient (``register_isotropic_lift``), so
    the element carrying it to a target plane is the composite of two registered
    lifts and no isometry search is run per plane.

    The ambient flag row need not choose the ambient plane row's representative,
    and then there is no registered source lift for its plane.  Each such flag is
    normalized once to a registered ambient representative, rather than starting
    a fresh isometry search against every much larger transported target plane;
    the third component is that source normalization, when one is needed.

    Returns one ``(ambient_flag, source_lift, source_witness)`` per ambient flag
    orbit, in the ambient row's order, which is the position that names the
    covering in the quotient's covering registry.
    """
    orthogonal_group = subgroup.supergroup()
    ambient_sources = []
    ambient_plane_representatives = None
    for ambient_flag in orthogonal_group.isotropic_orbit_representatives(2, flag=True):
        _ambient_line, ambient_plane = ambient_flag.terms()
        source_lift = quotient.isotropic_lift_of(ambient_plane)
        if source_lift is not None:
            ambient_sources.append((ambient_flag, source_lift, None))
            continue
        if ambient_plane_representatives is None:
            ambient_plane_representatives = tuple(
                orthogonal_group.isotropic_orbit_representatives(2)
            )
        for source_plane in ambient_plane_representatives:
            source_lift = quotient.isotropic_lift_of(source_plane)
            if source_lift is None:
                continue
            source_witness = orthogonal_group.isotropic_equivalence_witness(
                ambient_plane, source_plane
            )
            if source_witness is not None:
                ambient_sources.append((ambient_flag, source_lift, source_witness))
                break
        else:
            ambient_sources.append((ambient_flag, None, None))
    return tuple(ambient_sources)


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

        ``description`` is the constructing owner's words for the condition
        that cuts this subgroup out (``g commutes with (1 2)``), as a function
        of nothing: it is asked when the name or the rendering is read, never
        here, so no operand of the condition is rendered while the subgroup is
        built and a condition naming another subgroup states that subgroup's
        own description at read (:func:`_named_by_its_own_words`).

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
            # The clause that cuts this subgroup out, declared and set at the
            # level that introduces it: it is what the rendering prints beside
            # the ambient group and what a record names, and it is not the
            # realization's ``_description``, which says what a whole group
            # prints.  It is the constructing owner's own words for the
            # condition, as a function of nothing, asked where it is read and
            # never here.
            assert callable(description), (
                f"the condition cutting a subgroup of {supergroup} out is stated as a "
                f"function of nothing, but {description!r} is not callable"
            )
            self._stated_clause = description
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
                sage: P = G.predicate_subgroup(lambda g: g in H, lambda: "transposition subgroup")
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
                sage: P = F.predicate_subgroup(lambda g: phi(g) == C.one(), lambda: "even exponent")
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
                image_size = quotient.image_order()
                subgroup_image_size = quotient.subgroup_image_order()
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

        def _supplies_engine(self) -> bool:
            r"""A predicate subgroup is realized inside its supergroup's engine, so it has one exactly when the supergroup does."""
            return self.supergroup()._supplies_engine()

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

        def stabilizer(self, target, action="setwise"):
            r"""Restrict the ambient stabilizer to this subgroup.

            For H <= G acting on a marking x, H_x = H intersect G_x.
            The ambient operation owns the distinction between setwise and
            pointwise stabilization; intersection retains the subgroup's
            finite character and generating morphisms.
            """
            return self.intersection(self.supergroup().stabilizer(target, action=action))

        def intersection(self, other):
            r"""Intersect subgroups through their common owning construction."""
            return IntersectionSubgroups(self.supergroup())((self, other))

        @cached_method
        def finite_character_quotient(self):
            if not self.character_data_is_complete():
                raise ValueError(
                    f"{self} has no finite character quotient: it is not known to be the full "
                    f"preimage of a subgroup of a finite quotient of {self.supergroup()} by "
                    f"determinant, spinor norm and discriminant characters"
                )
            return OrthogonalCharacterQuotient(self)

        @cached_method
        def discriminant_image(self):
            r"""``rho(self)`` in ``O(A_L)``, exactly, from the retained character data.

            This subgroup is ``chi^-1(S)`` for the joint character map
            ``chi = (rho, det, sn)``; its discriminant image is the meet of
            the retained discriminant-preimage targets with the rho-images of
            the sign kernels it intersects, a finitely generated subgroup of
            ``O(A_L)`` computed without any generating family of this
            subgroup itself (``OrthogonalCharacterQuotient.discriminant_image``).
            Incomplete character data makes the image uncharacterized, and
            the quotient's ``ValueError`` propagates.
            """
            return self.finite_character_quotient().discriminant_image()

        def discriminant_generator_lifts(self):
            r"""Live isometries of this subgroup whose discriminant images generate ``rho(self)``.

            One lift per selected group generator of :meth:`discriminant_image`; each returned
            lift is checked against the character map and admitted by this subgroup's
            defining predicate, and the subgroup generated by their discriminant morphisms
            is asserted to equal the discriminant image itself, as a subgroup of the same
            ``O(A_L)`` (``OrthogonalCharacterQuotient.subgroup_generator_lifts``).
            """
            return self.finite_character_quotient().subgroup_generator_lifts()

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
            assert self.contains_character_kernel(), (
                f"{self} has no complete finite-character condition realizing its coset space"
            )
            quotient = self.finite_character_quotient()
            return _preimage_coset_space(
                self, quotient.character_representation(), quotient._character_target(), generators,
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
            r"""Return subgroup null orbits; ``flag=True`` accepts a ``FlagType`` or complete-flag rank."""
            return _subgroup_isotropic_orbit_representatives(
                self, rank, flag=flag
            )

        def isotropic_vector_reduction_image(self, representative):
            r"""Return the group that ``Stab_Gamma(v)`` induces on ``v^perp/<v>``.

            ``v`` is a primitive isotropic vector of the ambient lattice and
            ``Gamma = self`` is a subgroup of its orthogonal group cut out by a
            condition on the discriminant group, ``Gamma = rho^-1(rho(Gamma))``.

            The returned
            :class:`sage_extensions.categories.isotropic_orbits.IsotropicVectorReductionImage`
            is the image ``G_v`` of the stabilizer in ``O(v^perp/<v>)``, the image
            ``rho(K_v)`` of the kernel of the parabolic's Levi map in ``O(A_L)`` --
            with whether that image is trivial as an output, because one lift of an
            isometry decides membership only when it is -- and a membership test
            for an isometry of ``v^perp/<v>``.  Two lifts differ by an element of
            ``K_v``, a unipotent group containing the Eichler transvections
            ``t(v, a)``, ``a`` orthogonal to ``v`` (V. Gritsenko, K. Hulek,
            G. Sankaran, *Abelianisation of orthogonal groups and the fundamental
            group of modular varieties*, arXiv:0810.1614, §3.1, equation (4)), so
            the criterion is ``rho(g)`` in ``rho(K_v) rho(Gamma)``, computed in the
            finite group ``O(A_L)``; the quotient action is the quotient block of
            Dutour Sikirić--Hulek, arXiv:2302.01679v2, theorem
            `theorem_isotropic_k_planes`, printed pp. 33--34.

            Where it is needed: Sterk's five Enriques cusp diagrams (H. Sterk,
            *Compactifications of the period space of Enriques surfaces, Part I*,
            Math. Z. 207 (1991), 4.3.5--4.3.9) are diagrams of the reflection
            subgroup of ``G_v`` for ``Gamma_{En,2}`` on ``T_{En}``
            (Proposition 2.7, p. 6 for the group; Proposition 4.2.3 with
            Remark 4.2.4, p. 16 for its five cusps); the output is the subgroup
            input of the chamber anchored at the cusp.
            """
            from sage_extensions.categories.isotropic_orbits import (
                IsotropicVectorReductionImage,
            )

            return IsotropicVectorReductionImage(self, representative)

        def isotropic_plane_orbits(self, representatives=None, *, stabilizer_generators=None):
            r"""Return this subgroup's orbits of primitive isotropic planes, one per divided-class point.

            The planes of an indefinite lattice are classified inside each
            ``O(L)``-orbit, and the splitting of one such orbit under the
            subgroup is a double-coset computation in an infinite group.  Each
            step below is a published statement, and the computation is finite.

            **1. The ambient orbits and their representatives.**  For the
            Enriques period lattice ``T_{\mathrm{En}} = U \oplus U(2) \oplus
            E_8(-2)`` there are exactly two ``O(T_{\mathrm{En}})``-orbits of
            primitive isotropic planes, represented by
            ``P_1 = \mathbb{Z} e_1 + \mathbb{Z} e_3`` and
            ``P_2 = \mathbb{Z}(2 e_1 + 2 e_2 + w) + \mathbb{Z} e_3`` with ``w``
            a vector of ``E_8(-2)`` of norm ``-8``: H. Sterk,
            *Compactifications of the period space of Enriques surfaces, Part
            I*, Math. Z. 207 (1991), Proposition 4.6 (p. 29), with the two
            ``0``-cusps of Proposition 4.5 (p. 28) for the lines.  These are
            the integers' representatives ``(e_1, e_2)`` of ``U`` and
            ``(e_3, e_4)`` of ``U(2)``: D. Dutour Sikirić and K. Hulek,
            *Moduli of polarised Enriques surfaces -- computational aspects*,
            J. London Math. Soc. 110 (2024), arXiv:2302.01679, §3.6 (the Tits
            building), p. 22.  They are the ``representatives`` argument; a
            lattice whose ambient plane orbit is enumerated by the port's
            marking classes needs no argument.

            **2. One plane, one divided class set.**  ``\Gamma`` acts on a
            plane through its divided discriminant classes ``[u/div(u)]`` in
            ``A_L = L^\#/L``, and ``A_L`` has exponent two, so the class set is
            read off ``P/2P`` (:func:`_divided_discriminant_classes`).

            **3. The double-coset reduction.**  The subgroup is a character
            kernel, so ``\Gamma = \rho^{-1}(\rho(\Gamma))``; with
            ``U = \widetilde{O}(L) = \ker \rho \subset K = \Gamma`` and
            ``H = G_x`` the stabilizer of the plane, the quotient map
            ``O(L) \to O(L)/\widetilde{O}(L) \cong O^+_{10}(\mathbb{F}_2)``
            carries the double cosets ``\Gamma \backslash O(L) / H`` onto those
            of the finite image (Dutour Sikirić--Hulek, Lemma 3.6, printed
            p. 22), and those double cosets *are* the ``\Gamma``-orbits of the
            ``O(L)``-orbit ``xG``.  So the ``\Gamma``-orbits are the
            ``\rho(\Gamma)``-orbits on the finite ``\rho(O(L))``-orbit of the
            plane's class set, which is the computation here.

            **4. The check the published indices supply, and the check the call now
            demands.**  The count in step 3 is the number of ``\Gamma``-orbits of
            planes only when ``\rho(G_x) = \mathrm{Stab}_Q(J_x)``, ``G_x`` being the
            stabilizer of the plane ``x`` and ``J_x`` its divided class set:
            ``\rho(G_x) \subseteq \mathrm{Stab}_Q(J_x)`` always, since ``x \mapsto J_x``
            is built from lattice operations and ``\widetilde{O}(L) = \ker \rho`` acts
            trivially, so ``|Q . J_x| \le [Q : \rho(G_x)]`` and a count read off
            ``Q . J_x`` is a *lower bound* until the two agree.  Dutour Sikirić--Hulek,
            §3.6, p. 22 supply that agreement for ``N = U \oplus U(2) \oplus E_8(-2)``:
            the images of the stabilizers of ``P_1`` and ``P_2`` have index
            ``527 = 17 \cdot 31`` and ``23715 = 3^2 \cdot 5 \cdot 17 \cdot 31`` in
            ``\rho(O(N))``, and their class sets are exactly those sizes, so the trivial-image subgroup has
            ``527 + 23715 = 24242`` plane orbits, the ``1``-cusps of that paper's
            ``\widetilde{\mathcal{M}}_{\mathrm{En}}``.  With both of the paper's orbits
            present, a computed set of class-orbit sizes equal to ``{527, 23715}``
            forces the equality orbit by orbit, because each size bounds its own index
            from below and the two published indices are distinct.  For
            ``\Gamma = \Gamma_{\mathrm{En},2}`` -- the image in ``O(T_{\mathrm{En}})``
            of ``\{g \in O(L) : g I_{\mathrm{En}} = I_{\mathrm{En}} g,\ g(h) = h\}``,
            V. Alexeev, P. Engel, D. Z. Garza, L. Schaffler, *Compact moduli of
            Enriques surfaces of degree 2*, Nagoya Math. J. 259 (2025), Def. 2.6, with
            ``F_{En,2} = \mathbb{D}(T_{\mathrm{En}})/\Gamma_{\mathrm{En},2}`` of Def. 2.7
            and the boundary of Cor. 3.12 -- the same finite computation returns the
            ``9`` plane orbits those authors state for the ``1``-cusps of ``F_{En,2}``
            (§3.3, p. 590).  The lattice hypothesis of that citation is checked by
            exhibiting an isometry onto ``N``, not by comparing invariants.

            Where neither applies the call uses the plane's own setwise
            stabilizer: its generators are constructed at any primitive
            isotropic plane by integer linear algebra from the block equations
            of the parabolic (Dutour Sikirić--Hulek, Theorem 4.9, printed
            p. 22), and ``is_parabolic_complete()`` decides on three computed
            indices whether they are the whole stabilizer.  That
            route needs neither the lattice to be ``N`` nor the two indices
            above to agree, because with ``\rho(G_x)`` in hand the orbits are
            the double cosets ``\rho(\Gamma) \backslash \rho(O(L)) /
            \rho(G_x)`` themselves, computed by ``splitting_isometries``.  On
            ``T_{\mathrm{Co}}`` the agreement genuinely fails — the plane's
            stabilizer maps onto a subgroup of index ``8`` in the stabilizer of
            its order-four isotropic subgroup, while its divided class set is a
            single ``\rho(O(L))``-orbit of ``23715`` points — so the class set
            there is short by a factor of ``8`` and the double cosets are what
            the count is read from.  Where the parabolic's family is *not*
            established to be all of ``\rho(G_x)`` the call raises, naming the
            representative and the missing factor, instead of returning a
            count.  An alternative for such a lattice is
            ``stabilizer_generators``, a mapping from the position of a representative
            to generators of its stabilizer in ``O(L)``; each is checked to stabilize
            the plane, and ``[Q : \langle\rho(h)\rangle]`` then bounds ``[Q : \rho(G_x)]``
            from above, closing the same sandwich.

            Each returned :class:`IsotropicPlaneOrbit` realizes its plane from
            the representative it was split out of, by the word in the ambient
            generators above it, and checks that the transported plane has the
            class set it should.
            """
            from sage_extensions.categories.isotropic_orbits import (
                _divided_class_isotropic_plane_orbits,
            )

            return _divided_class_isotropic_plane_orbits(
                self, representatives, stabilizer_generators
            )

        def isotropic_orbit_iterator(self, rank, *, height_bound=None):
            r"""Yield the first primitive isotropic subobject of each orbit of this subgroup."""
            from sage_extensions.categories.isotropic_orbits import _isotropic_orbit_iterator

            return _isotropic_orbit_iterator(self, self.supergroup().domain(), rank, height_bound)

        def isotropic_are_equivalent(self, left, right, *, flag=False) -> bool:

            return self.isotropic_equivalence_witness(left, right, flag=flag) is not None

        def isotropic_equivalence_witness(self, left, right, *, flag=False):
            from sage_extensions.categories.orthogonal_quotients import (
                _subgroup_isotropic_equivalence_witness,
            )

            return _subgroup_isotropic_equivalence_witness(
                self, left, right, flag=flag
            )

        @cached_method
        def cusps(self, rank=1):
            r"""Return the retained primitive-isotropic cusp orbits of this subgroup and rank."""
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

            A line cusp meets a plane cusp when some element of this subgroup
            carries a line of the first into a plane of the second.  At one
            plane ``P`` these pairs are covered by the ``Stab_Gamma(P)``-orbits
            of the isotropic lines of ``P``: the lines of a totally isotropic
            plane are isotropic, and two flags over the same plane are
            ``Gamma``-equivalent exactly when their lines lie in one
            ``Stab_Gamma(P)``-orbit.  Where the plane's parabolic is complete
            a covering of those orbits is supplied by it, so the incidence
            never reaches the indefinite port's generic stabilizer enumeration
            (:func:`...orthogonal_quotients._plane_parabolic_incidence_flags`);
            where it is not, the flag row keeps its own route.  Distinct
            flag orbits may have the same two cusp endpoints, so the returned
            relation retains one certificate per endpoint pair, not one edge
            per flag orbit.  Each certificate retains actual subgroup
            transporters to its two cusp vertices rather than transporters
            inherited from the full orthogonal group.

            The incidence is a relation between orbit vertices, so it is read
            from the two cusp rows and not from a third enumeration of the
            planes: the route visits each plane cusp's own representative, and
            a vertex is identified by the span of the term -- a span that is a
            cusp representative's is that cusp's, carried there by the
            identity -- rather than by a witness question against every cusp of
            the row.  The witness search remains for a term that is no
            representative, which is what the flag route's planes are.

            A line vertex is no representative either -- the lines of a plane
            are not the line row's chosen ones -- so the line row is indexed by
            the finite image instead: the ``rho(Gamma)``-orbit of the line's
            divided class pair is an invariant of the line orbits the row was
            split by, so a line's own key names the cusps that can contain it
            and the witness is asked only of those.  A key no cusp carries is
            answered exactly, being the invariant it is, and a key two cusps
            share -- possible where the finite image is coarser than the row --
            is decided between them by the witness each certificate retains.

            The covering of one plane is the covering of every plane, when the
            subgroup is invariant under conjugation by the ambient group: an
            ambient isometry then carries the subgroup to itself, so the family
            at one plane, carried to another by the composite of the two planes'
            registered lifts, is exactly the family of the other plane.  The
            plane's parabolic, its conjugated generators, their word section
            and its double cosets are therefore computed once for the row and
            once per ambient flag orbit, and the quotient retains that one
            record per orbit, which is what makes the plane count affordable at
            all: the record is
            :meth:`...OrthogonalCharacterQuotient.isotropic_covering_reference`
            and the carry is its
            :meth:`...OrthogonalCharacterQuotient.transport_covering`.  The
            invariance is the quotient's own decision
            (:meth:`...OrthogonalCharacterQuotient.preserves_conjugation`):
            the subgroup is ``chi^-1(S)`` for its finite character image ``S``,
            and it holds exactly when ``S`` is normal in ``chi(O(L))`` -- so for
            the kernel of any character, ``ker rho``, ``ker(rho, sn)`` and a
            sign kernel alike, and for the preimage of any normal image.
            What a subgroup's covering *is* remains its own question, and it is
            answered for every character: the double cosets descend to the
            finite image ``chi(Pi)`` because the parabolic meets ``ker chi`` in
            a normal subgroup of itself and that subgroup lies in the subgroup
            of ``Pi`` the covering is taken for (D. Dutour Sikirić and
            K. Hulek, arXiv:2302.01679v2, Lemma 3.6, printed p. 22).

            A plane's certificates are made while the row holds the plane, and the
            transport data of the lines carried there is released at that point
            (:meth:`...OrthogonalCharacterQuotient.release_isotropic_transports`).
            What the row retains as it walks is therefore its coverings and the
            relation it returns, not one flag certificate and one transport datum
            per line per plane.
            """
            from sage_extensions.categories.isotropic_orbits import (
                ArithmeticCuspIncidence,
                IsotropicFlag,
                _span_key,
            )
            from sage_extensions.categories.orthogonal_quotients import (
                _isotropic_line_image_key,
                _plane_parabolic_incidence_flags,
            )
            from sage_extensions.categories.sets.finite_ordered_sets import (
                finite_ordered_set,
            )

            lattice = self.supergroup().domain()
            line_cusps = self.cusps(1)
            plane_cusps = self.cusps(2)

            def matching_cusps(term, cusps):
                matches = []
                for cusp in cusps:
                    if term not in cusp.universe():
                        continue
                    witness = cusp.transporter_witness(term)
                    if witness is not None:
                        matches.append((cusp, witness))
                return matches

            # A cusp and the plane it is the orbit of are one span: the cusp
            # rows are built from the orbit rows, so a term whose span is a
            # cusp representative's is that cusp's, carried there by the
            # identity -- an isometry of the lattice, hence an element of this
            # subgroup.  Reading the vertex off the span is exact and costs one
            # key; asking the cusp row instead costs one witness question per
            # cusp, and a kernel row has 189720 plane cusps at every one of its
            # 189720 planes.  A term that is no representative -- the flag
            # route's planes are not transported from a retained one -- keeps
            # the witness search, which is the only statement available there.
            plane_cusp_by_span = {
                _span_key(cusp.representative()): cusp for cusp in plane_cusps
            }
            line_cusp_by_span = {
                _span_key(cusp.representative()): cusp for cusp in line_cusps
            }
            identity = self.supergroup().one()

            # A line of a plane is no representative of the line row, so its
            # span identifies no cusp and the witness search is what remains --
            # one question per line cusp, at every line of every plane.  What
            # does identify it is the finite image: the divided class pair
            # ``{c, -c}`` of a line is carried by a subgroup element onto the
            # pair of the image line, so the ``rho(Gamma)``-orbit of that pair
            # is an invariant of the line orbits of this row (D. Dutour
            # Sikirić and K. Hulek, arXiv:2302.01679v2, Lemma 3.6, printed
            # p. 22, which is the reduction the row itself was split by).  The
            # row is indexed by it once; a line's own key then names the cusps
            # that can contain it, and the witness is asked only of those.
            quotient = self.finite_character_quotient()
            line_cusps_by_key = None
            if quotient._has_discriminant:
                line_cusps_by_key = {}
                for cusp in line_cusps:
                    key = _isotropic_line_image_key(quotient, cusp.representative())
                    line_cusps_by_key.setdefault(key, []).append(cusp)

            def line_vertex_candidates(term):
                cusp = line_cusp_by_span.get(_span_key(term))
                if cusp is not None:
                    return [(cusp, identity)]
                if line_cusps_by_key is not None:
                    bucket = line_cusps_by_key.get(
                        _isotropic_line_image_key(quotient, term)
                    )
                    # A key no cusp carries is a line of no cusp of this row:
                    # the key is the invariant, so the empty answer is exact.
                    if not bucket:
                        return []
                    if len(bucket) == 1:
                        # One cusp carries the key, and the key is an invariant
                        # of the row's orbits, so the vertex is decided: the
                        # question that remains is the certificate's
                        # transporter.  Where the row's own words already
                        # exhibit one -- the two objects' chains share a root,
                        # which is what makes their composite a transporter
                        # rather than a bridge -- that composite is read off
                        # them, and no stabilizer word section is built.
                        term_root, _term_word = quotient.transported_from_root(term)
                        cusp_root, _cusp_word = quotient.transported_from_root(
                            bucket[0].representative()
                        )
                        if _span_key(term_root) == _span_key(cusp_root):
                            carried = quotient.isotropic_transport_between(
                                term, bucket[0].representative()
                            )
                            if carried is not None and carried in self:
                                return [(bucket[0], carried)]
                    return matching_cusps(term, bucket)
                return matching_cusps(term, line_cusps)

            def plane_vertex_candidates(term):
                cusp = plane_cusp_by_span.get(_span_key(term))
                if cusp is not None:
                    return [(cusp, identity)]
                return matching_cusps(term, plane_cusps)

            # A covering of the incidence by flags: at each plane
            # representative cover the Stab_Gamma(P)-orbits of the lines of P
            # from the plane's own parabolic, and use the flag row wherever
            # that route does not apply.  The lines of P need not form one orbit of the
            # parabolic -- the divisibility of a line of P is an invariant the
            # parabolic preserves -- so the Stab_Gamma(P)-orbits are computed
            # per orbit of the parabolic on the lines of P, and those orbits
            # are the ambient flag orbits read at this plane: the ambient
            # flags whose plane term is carried to P by an ambient isometry,
            # transported by it.
            orthogonal_group = self.supergroup()
            ambient_sources = _incidence_ambient_sources(self, quotient)
            # The building incidence is a relation between two orbit vertices, not
            # the quotient's set of flag orbits.  Several flags can witness the
            # same relation, and the parabolic covering can repeat one of its
            # K-orbits when the selected line-fixing generators are a proper
            # subgroup of the full line stabilizer, so one actual flag certificate
            # is retained for each endpoint pair.  The certificate is made while
            # the row holds the plane that produced it, and the flag and the
            # registered transport of its line are spent at that point: a row that
            # kept them would hold one flag and one transport datum for every line
            # of every plane -- three of each per plane, for 189720 planes --
            # beside the relation it returns.  Identity is intentional below:
            # every vertex is one of the retained objects of the two cusp rows, and
            # comparing distinct cusps would start another orbit search.
            incidences = []
            endpoint_pairs = set()

            def retain_flag(flag):
                r"""Retain the certificate of one flag over a new endpoint pair, and answer it."""
                line, plane = flag.terms()
                line_vertices = line_vertex_candidates(line)
                plane_vertices = plane_vertex_candidates(plane)
                if len(line_vertices) != 1 or len(plane_vertices) != 1:
                    raise ArithmeticError(
                        f"the isotropic flag {flag} of {lattice} lies in {len(line_vertices)} "
                        f"line cusps and {len(plane_vertices)} plane cusps of {self}; each "
                        f"term of a flag must lie in exactly one cusp"
                    )
                line_cusp, line_transporter = line_vertices[0]
                plane_cusp, plane_transporter = plane_vertices[0]
                if line_transporter is None or plane_transporter is None:
                    raise ArithmeticError(
                        f"the isotropic flag {flag} of {lattice} lies in the cusps "
                        f"{line_cusp} and {plane_cusp} of {self}, but no element of {self} "
                        f"carries the cusp representatives to its terms"
                    )
                certificate = ArithmeticCuspIncidence(
                    self,
                    flag,
                    line_cusp,
                    plane_cusp,
                    line_transporter,
                    plane_transporter,
                )
                if certificate.lattice() is not lattice:
                    raise ArithmeticError(
                        f"the Tits building incidence of {self} has a cusp incidence in a lattice "
                        f"other than {lattice}, the lattice {self.supergroup()} acts on"
                    )
                endpoints = (id(line_cusp), id(plane_cusp))
                if endpoints not in endpoint_pairs:
                    endpoint_pairs.add(endpoints)
                    incidences.append(certificate)
                return certificate

            parabolic_routed = True
            # The row's covering is one datum per source family: it is computed
            # at one plane, retained by the quotient, and carried to every other
            # plane by the composite of the two planes' registered lifts.  The
            # carry is exact because the quotient decides whether the subgroup
            # is invariant under conjugation by an ambient isometry; where it
            # is, the carried family is the other plane's -- same orbits, same
            # count -- so the plane's parabolic, its images, its word section
            # and its double cosets are paid once for the row.
            transported_covering = quotient.preserves_conjugation()
            # The planes of this row are the plane cusps of this row: a cusp's
            # representative is the plane, so the incidence is computed at each
            # cusp's own representative and its plane vertex is read from the
            # cusp, never searched for among the cusps.  Walking the orbit row
            # again here would also walk and register a second copy of every
            # plane -- 189720 of them on T_Co.
            for plane_cusp in plane_cusps:
                plane = plane_cusp.representative()
                target_lift = quotient.isotropic_lift_of(plane)
                covered_here = False
                plane_flags = []
                carried_lines = []
                for position, (ambient_flag, source_lift, source_witness) in enumerate(
                    ambient_sources
                ):
                    _ambient_line, ambient_plane = ambient_flag.terms()
                    known = (
                        quotient.isotropic_covering_of(plane, position)
                        if transported_covering
                        else None
                    )
                    if known is not None:
                        # The row's covering was computed at this plane: it is
                        # the family here, and needs no carrying.
                        plane_flags.extend(known[1])
                        covered_here = True
                        continue
                    if transported_covering and target_lift is not None:
                        # Every other plane is that one covering carried here.
                        # The composite of the two planes' registered lifts
                        # carries the computed plane onto this one, and the
                        # subgroup is invariant under it, so the family it gives
                        # is this plane's -- same orbits, same count.
                        reference = quotient.isotropic_covering_reference(position)
                        if reference is not None:
                            _reference_plane, reference_lift, reference_flags = reference
                            carried = quotient.transport_covering(
                                reference_lift, reference_flags, target_lift
                            )
                            plane_flags.extend(carried)
                            carried_lines.extend(flag.terms()[0] for flag in carried)
                            covered_here = True
                            continue
                    # The source row now meets the source lift at one registered
                    # plane.  Composing that normalization with the row's own
                    # lifts gives an exact ambient witness to each target plane,
                    # without an isometry search against the transported target.
                    if source_lift is not None and target_lift is not None:
                        witness = target_lift * ~source_lift
                        if source_witness is not None:
                            witness = witness * source_witness
                    else:
                        witness = orthogonal_group.isotropic_equivalence_witness(
                            ambient_plane, plane
                        )
                    if witness is None:
                        continue
                    transported_flag = witness.transport_isotropic_object(ambient_flag)
                    quotient.register_isotropic_transport(
                        transported_flag.terms()[0],
                        ambient_flag.terms()[0],
                        witness,
                    )
                    from_parabolic = _plane_parabolic_incidence_flags(
                        self, plane, transported_flag
                    )
                    if from_parabolic is None:
                        parabolic_routed = False
                        break
                    if transported_covering and target_lift is not None:
                        quotient.register_isotropic_covering(
                            plane, position, target_lift, from_parabolic
                        )
                    plane_flags.extend(from_parabolic)
                    covered_here = True
                if not parabolic_routed:
                    break
                if not covered_here:
                    parabolic_routed = False
                    break
                for flag in plane_flags:
                    retain_flag(flag)
                if carried_lines:
                    # The plane's certificates retain their own transporters, so
                    # the carried lines' registered data is spent: released here,
                    # the registry is the row's coverings and not its planes.
                    quotient.release_isotropic_transports(carried_lines)
            if not parabolic_routed:
                # The flag row's planes are no representatives, so the vertices of
                # its flags are searched for rather than read, and the whole row is
                # read at once: two certificates over one endpoint pair there
                # expose an over-split flag row, which the covering route cannot.
                incidences = []
                endpoint_pairs = set()
                candidate_incidences = tuple(
                    retain_flag(flag)
                    for flag in self.isotropic_orbit_representatives(2, flag=True)
                )
                for position, first in enumerate(candidate_incidences):
                    for second in candidate_incidences[position + 1:]:
                        if first.line_cusp() is not second.line_cusp() or first.plane_cusp() is not second.plane_cusp():
                            continue
                        if self.isotropic_equivalence_witness(first.flag(), second.flag(), flag=True) is not None:
                            raise ArithmeticError(
                                f"the flags {first.flag()} and {second.flag()} of {lattice} are "
                                f"equivalent under {self}, yet they are recorded as two flag orbits "
                                f"over the line cusp {first.line_cusp()} and the plane cusp "
                                f"{first.plane_cusp()}: the flag orbits are over-split"
                            )
            return finite_ordered_set(tuple(incidences))

        def tits_building_incidence_by_divided_classes(self):
            r"""Return this subgroup's line/plane building incidence, decided by divided classes.

            The relation :meth:`tits_building_incidence` returns, computed from
            the data an edge is decided by instead of from flags and
            transporters: an edge joins a line cusp to a plane cusp, and which
            line cusp a line of a plane lies in is named by the
            ``rho(Gamma)``-orbit of the line's divided class pair.

            **What one plane needs.**  A primitive isotropic line ``x = <v>``
            has divided class ``c = [v / div(v)]`` in ``A_L = L^\#/L``, and an
            isometry carries ``c`` to the divided class of its image because an
            isometry preserves primitivity and divisibility
            (:func:`...orthogonal_quotients._isotropic_line_class_points`).
            So, for ``P_0`` the plane the row's one covering was computed at,

            * the plane's registered lift ``s_P``, which carries ``P_0`` onto
              ``P``, and the finite element ``rho(s_P)`` registered beside it --
              one span-keyed lookup, no construction;
            * the composite ``s_P s_{P_0}^{-1}``, as its action
              ``rho(s_P) rho(s_{P_0})^{-1}`` on ``A_L`` -- one product and one
              inversion of elements of ``O(A_L)``, so that no plane's action
              costs the dual action of an integral matrix
              (:func:`...orthogonal_quotients._composite_divided_class_action`);
            * the covering's line class pairs ``{c, -c}``, three of them at
              ``P_0`` and the same three for every plane, carried by that action
              (:func:`...orthogonal_quotients._carried_divided_classes`);
            * the line cusp row indexed by that orbit, once for the row.

            The edge at ``P`` is the pair (that cusp, the cusp of ``P``).  The
            containment ``c(g x)`` in the divided classes of ``g P`` -- which
            also holds, since an isometry carries a line of ``P_0`` to a line of
            ``P`` -- is necessary rather than sufficient for incidence, and the
            vertices are separated by the orbit, not by containment: what names
            the line cusp is the invariant the row's own reduction is stated in
            (D. Dutour Sikirić and K. Hulek, arXiv:2302.01679v2, Lemma 3.6,
            printed p. 22).

            **What it does not construct.**  No ``IsotropicFlag``, no
            ``PrimitiveIsotropic`` subobject and no certificate per plane: the
            classes are sets of classes of ``A_L`` and the elements are elements
            of the finite character image.  A constructed parent of this library
            is retained for the process (``_lattice_on_gram``'s construction
            cache, and the morphism and category-packet caches above it), so
            three carried flags a plane is 350-400 KB a plane and 63-72 GiB at
            the kernel rows' 189720 planes.  A flag is built in two places only:
            the row's covering, at the plane it is computed at, and once at the
            first plane that is not that one, to check that the carried class
            pair is the class pair of the carried line.

            **What it refuses.**  The route decides an edge only where the
            row's own key separates the line cusps: where two line cusps share
            one finite image the class data names both, and a lattice witness is
            what tells them apart, so the call raises naming the plane and the
            cusps instead of choosing one.  It also refuses a subgroup that is
            not invariant under conjugation by the ambient group, because then
            each plane's covering has to be computed at that plane -- the
            certificate route's work, and its per-plane parents with it.  In
            both cases :meth:`tits_building_incidence` remains the route that
            answers.

            The returned relation is a set of
            :class:`...isotropic_orbits.DividedClassCuspIncidence` records: one
            per endpoint pair, carrying the two vertices and the class pair that
            decided it, and no transporter.  A reader who wants a transporter in
            hand asks :meth:`tits_building_incidence`.
            """
            from sage_extensions.categories.isotropic_orbits import (
                DividedClassCuspIncidence,
            )
            from sage_extensions.categories.orthogonal_quotients import (
                _carried_divided_classes,
                _composite_divided_class_action,
                _isotropic_line_class_points,
                _isotropic_line_image_key,
                _plane_parabolic_incidence_flags,
            )
            from sage_extensions.categories.sets.finite_ordered_sets import (
                FiniteOrderedSets,
                finite_ordinal_set,
            )

            lattice = self.supergroup().domain()
            quotient = self.finite_character_quotient()
            if not quotient._has_discriminant:
                raise ValueError(
                    f"the building incidence of {self} cannot be decided by divided classes: the "
                    "subgroup cuts no discriminant condition, so a line carries no class data that "
                    "names its cusp, and tits_building_incidence is the route that decides the edges"
                )
            if not quotient.preserves_conjugation():
                raise ValueError(
                    f"the building incidence of {self} cannot be carried from one plane to another: "
                    "the subgroup is not invariant under conjugation by an isometry of its ambient "
                    "group, so every plane's covering has to be computed at that plane, which is the "
                    "certificate route's work; tits_building_incidence is that route"
                )
            orthogonal_group = self.supergroup()
            line_cusps = self.cusps(1)
            plane_cusps = self.cusps(2)
            # The line vertices, indexed once by the invariant the row was split
            # by: a key no cusp carries is a line of no cusp, and a key two
            # cusps share leaves the class data unable to choose between them.
            line_cusps_by_key = {}
            for cusp in line_cusps:
                key = _isotropic_line_image_key(quotient, cusp.representative())
                entry = line_cusps_by_key.setdefault(key, (key, []))
                entry[1].append(cusp)
            # One covering per ambient flag orbit, computed once at the first
            # plane of the row that has a registered lift for that source, and
            # kept as its line class pairs: the classes are what is carried from
            # then on, and the flags are not read again.
            sources = _incidence_ambient_sources(self, quotient)
            coverings = {}
            for plane_cusp in plane_cusps:
                if len(coverings) == len(sources):
                    break
                plane = plane_cusp.representative()
                registered = quotient.registered_isotropic_lift(plane)
                if registered is None:
                    continue
                lift, lift_discriminant = registered
                for position, (ambient_flag, source_lift, source_witness) in enumerate(sources):
                    if position in coverings:
                        continue
                    if source_lift is not None:
                        witness = lift * ~source_lift
                        if source_witness is not None:
                            witness = witness * source_witness
                    else:
                        witness = orthogonal_group.isotropic_equivalence_witness(
                            ambient_flag.terms()[1], plane
                        )
                    if witness is None:
                        continue
                    seeded = witness.transport_isotropic_object(ambient_flag)
                    covering = _plane_parabolic_incidence_flags(self, plane, seeded)
                    if covering is None:
                        raise ArithmeticError(
                            f"the incidence of {self} has no covering at {plane}: the plane's "
                            "parabolic does not cover the stabilizer's orbits on its lines, so the "
                            "edges at this row's planes are decided by the certificate route"
                        )
                    quotient.register_isotropic_covering(plane, position, lift, covering)
                    coverings[position] = (
                        plane,
                        lift,
                        lift_discriminant,
                        covering,
                        tuple(
                            _isotropic_line_class_points(lattice, flag.terms()[0])
                            for flag in covering
                        ),
                    )
            if len(coverings) != len(sources):
                raise ArithmeticError(
                    f"the incidence of {self} needs one covering per ambient flag orbit and "
                    f"{len(coverings)} of {len(sources)} were computed: no plane of the row carries a "
                    "registered lift for the others, so their covering cannot be carried to the row"
                )
            incidences = []
            endpoint_pairs = set()
            transport_checked = set()
            for plane_cusp in plane_cusps:
                plane = plane_cusp.representative()
                registered = quotient.registered_isotropic_lift(plane)
                if registered is None:
                    raise ArithmeticError(
                        f"the plane {plane} of the cusp {plane_cusp} of {self} has no registered lift, "
                        "so no covering of the row can be carried onto it: the class data of its lines "
                        "is what the lift carries, and without it the edges at this plane are undecided"
                    )
                target_lift, target_discriminant = registered
                for position, (
                    reference_plane,
                    reference_lift,
                    reference_discriminant,
                    covering,
                    reference_classes,
                ) in coverings.items():
                    move = target_lift * ~reference_lift
                    action = _composite_divided_class_action(
                        quotient, target_discriminant, reference_discriminant
                    )
                    for flag, classes in zip(covering, reference_classes, strict=True):
                        carried = _carried_divided_classes(classes, action)
                        if position not in transport_checked and plane is not reference_plane:
                            # The carried class is the class of the carried line:
                            # the one plane of the row that builds a flag's worth
                            # of work, to check the finite image's action on
                            # ``A_L`` against the lattice's own image of the
                            # carried line.  The reference plane's own move is the
                            # identity, so the check is made at the first plane
                            # that is a different one.
                            image_line = move.transport_isotropic_object(flag).terms()[0]
                            if str(_isotropic_line_class_points(lattice, image_line)) != str(carried):
                                raise ArithmeticError(
                                    f"the divided classes of the line of {flag} carried to {plane} by "
                                    f"the finite image are not the classes of the carried line: the "
                                    "action of the image on A_L and the induced action of the isometry "
                                    "on the lattice disagree, so no edge is read from the classes"
                                )
                        entry = line_cusps_by_key.get(
                            frozenset(quotient.isotropic_class_orbit(carried))
                        )
                        key, candidates = entry if entry is not None else (None, ())
                        if len(candidates) != 1:
                            named = ", ".join(str(cusp) for cusp in candidates) or "none"
                            raise ArithmeticError(
                                f"the line of the covering flag {flag} carried to {plane} lies in "
                                f"{len(candidates)} line cusps of {self} ({named}): the finite image "
                                "does not separate this line's cusp from the others, and no edge is "
                                "read from class data that names more than one vertex; "
                                "tits_building_incidence decides it with a transporter"
                            )
                        endpoints = (id(candidates[0]), id(plane_cusp))
                        if endpoints in endpoint_pairs:
                            continue
                        endpoint_pairs.add(endpoints)
                        incidences.append(
                            DividedClassCuspIncidence(
                                self, candidates[0], plane_cusp, key
                            )
                        )
                    if plane is not reference_plane:
                        transport_checked.add(position)
            # The relation is a finite ordered set whose inverse is the walk's
            # own identity index.  A cusp's hash is constant over its universe
            # (``_ArithmeticCuspEngine.__hash__``: a cusp has no cheap canonical
            # key, so its hash is the constant the category's rule prescribes),
            # and the literal ingress :func:`finite_ordered_set` identifies
            # repeated points through a dictionary of them, which for constant
            # hashes compares every point with every other -- at the certificate
            # route's one certificate a plane that is ``n(n-1)/2`` comparisons of
            # two cusps, each a transporter search.  Supplying the inverse the
            # walk already used keeps the ingress linear, and the points are
            # distinct objects because the walk admitted one per endpoint pair.
            points = tuple(incidences)
            positions = {id(point): position for position, point in enumerate(points)}
            return FiniteOrderedSets().from_indexed(
                finite_ordinal_set(len(points)),
                lambda position: points[int(position)],
                index_of=lambda point: positions.get(id(point)),
            )

        def _predicate_clause(self) -> str:
            r"""Return the condition that cuts this subgroup out, asked where it is read.

            The clause is the constructing owner's own words for a condition on
            one element -- ``sn_RR(g) = 1``, ``g commutes with (1 2)`` -- and it
            is read by the rendering (:meth:`_repr_`) and by the record's name
            (:meth:`description`), never at construction.

            A kind whose condition names another *subgroup* --
            :class:`PreimageSubgroups`, :class:`StabilizerSubgroups` -- passes
            a clause that names it there, so the operand is named by its own
            description when this is asked and is not rendered when the
            subgroup is built.
            """
            return self._stated_clause()

        def description(self) -> str:
            r"""Return this subgroup's own name: the condition that cuts it out.

            Every construction of this owner states one clause -- ``sn_RR(g) =
            1`` for ``O^+(L)``, ``rho_L(g) lies in ...`` for a preimage -- and
            the clause is the whole of what a reader is told about the subgroup.
            This is not the subgroup's rendering: ``_repr_`` writes the clause
            beside the ambient group, which is a rendering of the pair.

            An intersection is named by the condition its construction states
            too, but its construction states its operands instead of a clause,
            so it states its own description one level down
            (:meth:`IntersectionSubgroups.ParentMethods.description`).

            Read by :func:`sage_extensions.categories._lattice._group_label`.
            """
            return f"the subgroup where {self._predicate_clause()}"

        def _repr_(self):
            return f"{{g in {self.supergroup()} : {self._predicate_clause()}}}"


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

    def _call_(self, morphism, *, generating_morphism_factory=None):
        r"""Construct the kernel with its defining map and chosen free augmentation."""
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
            description=lambda: "elements mapped to the identity by the defining morphism",
            kernel_morphism=morphism,
            generating_morphism_factory=generating_morphism_factory,
        )

    @classmethod
    def _repr_object_names(cls):
        return "kernel subgroups"

    class ParentMethods:
        def __init__(self, kernel_morphism, generating_morphism_factory=None, **rest) -> None:
            self._kernel_morphism = kernel_morphism
            super().__init__(**rest)
            if generating_morphism_factory is not None:
                _fix_selected_generating_morphism(self, generating_morphism_factory)
            # Schreier's lemma: a finitely generated group mapping to a finite
            # group has its kernel generated by the Schreier family of the
            # finite image, so that family is this kernel's selected datum.
            if (
                not _retains_group_resolution(self)
                and self.supergroup().has_selected_group_resolution()
                and kernel_morphism.codomain() in OwnedFiniteGroups()
            ):
                _fix_selected_generating_morphism(
                    self, lambda kernel: kernel.schreier_generating_morphism()
                )

        def kernel_morphism(self):
            return self._kernel_morphism

        def schreier_generators(self, *, generators=None):
            r"""The Schreier generating family, indexed by the retained free basis."""
            morphism = self.schreier_generating_morphism(generators=generators)
            return morphism.domain().group_generators().map(morphism, name="Schreier generators")

        def index(self, *, generators=None):
            r"""The index of a kernel with a represented finite image.

            First isomorphism: ``G/ker(f)`` is the image of ``f``. The
            finite-image transversal retains a representative of every
            image element, including when ``G`` is infinite. Explicit
            generators may be supplied when the ambient group has not
            selected a generating resolution.
            """
            return self.coset_space(generators=generators).cardinality()

        def schreier_generators(self, *, generators=None):
            r"""The Schreier generating family, indexed by the retained free basis."""
            morphism = self.schreier_generating_morphism(generators=generators)
            return morphism.domain().group_generators().map(morphism, name="Schreier generators")

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

        def schreier_generators(self, *, generators=None):
            r"""The kernel's Schreier generating family on the retained free basis."""
            morphism = self.schreier_generating_morphism(generators=generators)
            return morphism.domain().group_generators().map(morphism, name="Schreier generators")

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
        whole = PredicateSubgroups(group)(lambda _element: True, lambda: "the whole group")
        return self(group.Mor(group).identity(), whole)

    def _call_(
        self,
        morphism,
        subgroup,
        *,
        stated_clause,
        predicate=None,
        character_data=None,
        character_data_complete=None,
        generating_morphism=None,
    ):
        r"""Construct the inverse image of ``subgroup`` along ``morphism``.

        ``generating_morphism``, when the constructing owner has one, maps
        the constructed preimage to a free generating morphism onto it.
        Otherwise a finitely generated source mapping to a finite group
        selects the Schreier family of the finite image.

        ``stated_clause`` is the constructing owner's condition for the record,
        as a function of nothing (``rho_L(g) lies in ...``, ``sn_RR(g) = 1``);
        it is asked when the subgroup's name or rendering is read, never here.
        The condition names the subgroup this construction operates on, so the
        owner that names it states that subgroup's own description at read
        (:func:`_named_by_its_own_words`).
        """
        group = self.base()
        if morphism.domain() is not group:
            raise ValueError(
                f"cannot take the preimage of {subgroup} along {morphism} as a subgroup of "
                f"{group}: the domain of {morphism} is {morphism.domain()}, not {group}"
            )
        if subgroup is morphism.codomain():
            subgroup = PredicateSubgroups(subgroup)(
                lambda _element: True, lambda: "the whole codomain"
            )
        if subgroup not in Subgroups(morphism.codomain()):
            raise ValueError(
                f"cannot take the preimage of {subgroup} under {morphism}: "
                f"the specified target is not a subgroup of {morphism.codomain()}"
            )
        if predicate is None:
            def predicate(element):
                return subgroup.is_parent_of(morphism(element))
        return _object_of(
            _predicate_subgroup_category(self),
            _ambient=OwnedGroups(),
            supergroup=group,
            predicate=predicate,
            description=stated_clause,
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

        def schreier_generators(self, *, generators=None):
            r"""The Schreier generating family, indexed by the retained free basis."""
            morphism = self.schreier_generating_morphism(generators=generators)
            return morphism.domain().group_generators().map(morphism, name="Schreier generators")

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
                lambda: (
                    f"elements of {_named_by_its_own_words(target)} in "
                    f"{_named_by_its_own_words(image)}"
                ),
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
            lambda: f"g stabilizes {identity}",
        )

    def _call_(
        self,
        stabilized_object,
        action,
        predicate,
        stated_clause,
        *,
        generating_morphism=None,
        basis_change=None,
        vector_witness=None,
    ):
        r"""Construct the stabilizer retaining the stabilized object and action.

        ``vector_witness(left, right)`` is the action owner's exact decision of
        vector equivalence under this stabilizer, when it supplies one.

        ``stated_clause`` is the constructing owner's condition for the record,
        as a function of nothing: ``g fixes the plane ...``, ``normalizer of ...
        in ...``.  It is asked when the subgroup's name or rendering is read,
        never here, so an owner whose condition names a subgroup states that
        subgroup's own description at read and renders nothing at construction.

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
        assert callable(stated_clause), (
            f"the stabilizer of {stabilized_object} in {group} states the condition that cuts "
            f"it out as a function of nothing, but {stated_clause!r} is not callable"
        )
        return _object_of(
            _predicate_subgroup_category(self),
            _ambient=OwnedGroups(),
            supergroup=group,
            predicate=predicate,
            description=stated_clause,
            stabilized_object=stabilized_object,
            stabilizer_action=action,
            generating_morphism=generating_morphism,
            basis_change=basis_change,
            vector_witness=vector_witness,
        )

    @classmethod
    def _repr_object_names(cls):
        return "stabilizer subgroups"

    class ParentMethods:
        def __init__(self, stabilized_object, stabilizer_action, basis_change=None, vector_witness=None, **rest) -> None:
            self._stabilized_object = stabilized_object
            self._stabilizer_action = stabilizer_action
            self._basis_change = basis_change
            self._vector_witness = vector_witness
            super().__init__(**rest)

        def owned_vector_witness(self):
            r"""The action owner's exact vector decision for this stabilizer, or ``None``."""
            return self._vector_witness

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
            description=lambda: f"g commutes with {element}",
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
        whole = PredicateSubgroups(group)(lambda _element: True, lambda: "the whole group")
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
        # Retain character_data from intersected subgroups when not supplied explicitly
        # (e.g. Γ_h = ρ⁻¹(H) ∩ O⁺(N) via G.intersection): merged data makes
        # finite_character_quotient available on the intersection itself.
        if character_data is None and character_data_complete is None:
            merged = {}
            complete = True
            for sg in subgroups:
                if sg in PredicateSubgroups(group):
                    snap = sg._character_data_snapshot()
                    # merge deterministically: OR for kernels, concat for preimages
                    merged["determinant_kernel"] = bool(merged.get("determinant_kernel", False) or snap.get("determinant_kernel", False))
                    merged["spinor_kernel"] = bool(merged.get("spinor_kernel", False) or snap.get("spinor_kernel", False))
                    if snap.get("discriminant_preimages", ()):
                        merged["discriminant_preimages"] = tuple(merged.get("discriminant_preimages", ())) + tuple(snap.get("discriminant_preimages", ()))
                    complete = complete and sg.character_data_is_complete()
                else:
                    complete = False
            if merged:
                character_data = {k: v for k, v in merged.items() if v}
                character_data_complete = complete
        return _object_of(
            _predicate_subgroup_category(self),
            _ambient=OwnedGroups(),
            supergroup=group,
            predicate=lambda element: conjunction(subgroup.is_parent_of(element) for subgroup in subgroups),
            description=lambda: "g lies in every selected subgroup",
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
            # Both sides are finite-index character kernels (e.g. discriminant
            # preimage ∩ spinor kernel for Γ_h). Neither is generated, but
            # the ambient O(N) is — use its finite-index Schreier.
            if not _retains_group_resolution(self) and intersected_subgroups.cardinality() == cardinal(2):
                group = self.supergroup()
                if all(
                    sg in PredicateSubgroups(group) and sg.contains_character_kernel()
                    for sg in intersected_subgroups
                ) and group.has_selected_group_resolution():
                    _fix_selected_generating_morphism(
                        self,
                        lambda intersection, intersected_subgroups=intersected_subgroups: (
                            intersection._character_intersection_generating_morphism(intersected_subgroups)
                        ),
                    )
                    return
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
                # still a finite-index subgroup, even though one
                # PreimageSubgroups object does not present it.  Restrict its
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

        def description(self) -> str:
            r"""Return this intersection's own name: the subgroups it meets.

            An intersection's defining data are its operands, and each of them
            states its own description, so the name is theirs: ``the
            intersection of`` the operands' descriptions.  The condition this
            subgroup's construction states -- ``g lies in every selected
            subgroup`` -- says what an intersection is and not which one it is,
            so it is the rendering's clause (:meth:`_repr_`) and not this.

            The operands are written in one order because an intersection is
            symmetric and the retained set has no chosen one: the sorted order of
            their descriptions, so one call writes one name in every process.

            Read by :func:`sage_extensions.categories._lattice._group_label`.
            """
            described = sorted(
                subgroup.description() for subgroup in self._intersected_subgroups
            )
            return "the intersection of " + " and ".join(described)

        def _restricted_preimage_generating_morphism(self, morphism, target, generated):
            r"""``E ->> f^-1(K) cap B`` through the Schreier morphism onto ``(f i)^-1(K)``.

            The restricted inclusion lands in B and its composite with f
            lands in K. These two range laws give the intersection
            corestriction at its constructing owner.
            """
            inclusion = generated.inclusion()
            restricted = (morphism * inclusion).preimage_subgroup(
                target,
                stated_clause=lambda: (
                    f"{morphism}(g) lies in {_named_by_its_own_words(target)}"
                ),
            )
            augmentation = restricted.schreier_generating_morphism()
            return (inclusion * restricted.inclusion() * augmentation)._corestrict_to_subgroup(self)

        def _restricted_character_generating_morphism(self, character_subgroup, generated):
            r"""Generate ``Gamma cap B`` by restricting a finite character condition to ``B``.

            If ``Gamma = rho^-1(H)`` in ``G``, then
            ``[B:B cap Gamma] <= [rho(G):H]``.  This exact finite bound
            supplies the existing predicate-subgroup Schreier computation;
            no membership or word algorithm for an arbitrary generated
            subgroup of ``G`` is assumed.

            The restricted predicate and its inclusion supply both
            intersection range laws for the resulting corestriction.
            """
            quotient = character_subgroup.finite_character_quotient()
            index_bound = quotient.index()
            inclusion = generated.inclusion()
            restricted = generated.predicate_subgroup(
                lambda element: inclusion(element) in character_subgroup,
                lambda: (
                    f"the inclusion into {self.supergroup()} lies in "
                    f"{_named_by_its_own_words(character_subgroup)}"
                ),
            )
            augmentation = restricted.finite_index_schreier_generating_morphism(
                index_bound=index_bound,
                generators=generated.group_generators(),
            )
            return (inclusion * restricted.inclusion() * augmentation)._corestrict_to_subgroup(self)

        def _character_intersection_generating_morphism(self, intersected_subgroups):
            # Lazy: finite-family prerequisite is checked at realization, not construction
            group = self.supergroup()
            if not group.has_selected_finite_group_generating_set():
                raise ValueError(f"cannot generate {self}: ambient {group} has no retained finite generating family")
            # Exact index is available on the intersection itself now that character_data is retained.
            # Only fall back to product bound when the intersection's character quotient is
            # not yet complete (ValueError: no finite character quotient), not on arbitrary errors.
            try:
                q = self.finite_character_quotient()
                # The intersection retains merged character data, so its own
                # character quotient answers the exact index from the group
                # orders of the generated image; no image element is listed.
                index_bound = q.index()
            except ValueError:
                index_bound = 1
                for cs in intersected_subgroups:
                    q = cs.finite_character_quotient()
                    index_bound *= q.index()
            return self.finite_index_schreier_generating_morphism(
                index_bound=index_bound,
                generators=group.group_generators(),
            )

__all__ = [
    "CentralizerSubgroups",
    "IntersectionSubgroups",
    "KernelSubgroups",
    "PredicateSubgroups",
    "PreimageSubgroups",
    "StabilizerSubgroups",
]
