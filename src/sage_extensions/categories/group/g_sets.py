r"""Finite represented ``G``-sets, their orbits, fixed points, and torsors.

A ``G``-set is an object of ``Sets()`` with a chosen ``G``-action, so its
category is ``GObjects(G, Sets())``.  The finite represented objects
additionally record the action as a group morphism ``G -> Sym(X)``, which is
the engine used to compute equivariance, fixed points, orbits, and the
standard finite free/cofree constructions.
"""

from sage.categories.category import Category
from sage.libs.gap.libgap import libgap
from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.element import Element, parent as element_parent
from sage.structure.parent import Parent
from sage.structure.richcmp import op_EQ, op_NE

from sage_extensions.categories.abstract_categories.mor_categories import (
    CategoryPacketMethods,
    MorCategoryConstruction,
)
from sage_extensions.categories.abstract_categories.objects import (
    OwnedParameterizedCategory,
)
from sage_extensions.categories.group.g_objects import GObjectMor, GObjects
from sage_extensions.categories.group.groups import (
    OwnedFiniteGroups,
    OwnedGroups,
    PermutationGroups,
    SymmetricGroups,
    _GroupMorRealizationMixin,
    _encodes_elements_in_gap,
    _named_by_its_own_words,
    _engine_group,
    _engine_left_coset_positions,
    _engine_point,
    _owned_group,
)
from sage_extensions.categories.rings.ring_foundation import (
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.finite_ordered_sets import (
    _subset_on_positions,
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
)
from sage_extensions.categories.sets.set_categories import (
    EnumeratedSets,
    FiniteSets,
    Sets,
)
from sage_extensions.logic import AtomicProposition, Unknown, ask
from sage_extensions.owned_category import _object_of, owned_category_join
from sage_extensions.validation import validator


class GSetMorCategoryConstruction(MorCategoryConstruction):
    def fixed_category_class(self):
        return GSetMor


def _orbit_schreier_morphism(orbit, word_section, augmentation, *, drop_trivial=False):
    r"""Schreier's lemma on a pointed finite orbit: ``E -> G`` onto the base-point stabilizer.

    ``orbit`` is a finite ``G``-set, ``augmentation`` a free cover
    ``pi: F ->> G`` and ``word_section`` the Sets Mor ``p |-> t_p`` into ``F``
    with ``pi(t_p)`` carrying the base point to ``p``.  The words
    ``t_(s.p)^-1 s t_p``, over points ``p`` and free generators ``s``, generate
    the stabilizer of the base point in ``F``; the returned group morphism
    from the free group on them to ``G`` has that stabilizer's image as image.
    This is the one Schreier construction; its callers corestrict it to the
    subgroup they present.

    Each image ``s.p`` in the family is the action of ``pi(s)`` at ``p``, which
    is the orbit's permutation representation at that letter: the family is
    read from the ``G``-set's own action, in the order the orbit presents its
    points and the cover presents its letters.  Nothing a search of a larger
    action recorded is a datum of it, so a point's family is the same whether
    or not a sweep that reached it visited other points too.

    ``drop_trivial`` drops the Schreier generators whose image in ``G`` is the
    identity.  The pair that first reaches a point is one of them: that point's
    transversal is the pair's word applied to its predecessor's, so the word
    ``t_(s.p)^-1 s t_p`` is empty and its image is trivial
    (Holt--Eick--O'Brien, *Handbook of Computational Group Theory*,
    Chapman & Hall/CRC, 2005, Section 4.1, p. 79).  Which other pairs have a
    trivial image is a property of the section and the cover, so it is decided
    from the family's own images, never from the route that built the set.
    """
    from sage_extensions.categories.sets.set_categories import finite_ordinal_set

    free = augmentation.domain()
    group = augmentation.codomain()
    letter_words = tuple(free.group_generators())
    letters = tuple(augmentation(letter) for letter in letter_words)
    representation = orbit.permutation_representation()
    permutations = tuple(representation(letter) for letter in letters)
    points = tuple(orbit)
    positions = orbit.ranking_map()
    sections = tuple(word_section(point) for point in points)
    words = tuple(
        (~sections[int(positions(permutations[letter_position](point)))])
        * letter_words[letter_position]
        * sections[position]
        for position, point in enumerate(points)
        for letter_position in range(len(letter_words))
    )
    if drop_trivial:
        images = tuple(
            image for image in map(augmentation, words) if image != group.one()
        )
        labels = finite_ordinal_set(len(images))
        return OwnedGroups.Free(index_set=labels).Mor(group)(
            Sets().Mor(labels, group)(lambda label: images[int(label)])
        )
    labels = finite_ordinal_set(len(words))
    source = OwnedGroups.Free(index_set=labels)
    word_map = source.Mor(free)(
        Sets().Mor(labels, free)(lambda label: words[int(label)])
    )
    return augmentation * word_map


class FiniteGSets(CategoryPacketMethods, OwnedParameterizedCategory):
    r"""The represented finite objects of ``GObjects(G, Sets())``."""

    def parameter_category(self):
        r"""A finite ``G``-set is indexed by the acting group ``G``."""
        return OwnedGroups()

    def an_object(self):
        r"""The three-point set with the trivial action of the group."""
        from sage_extensions.categories.sets.set_categories import (
            finite_ordinal_set,
        )

        return self.trivial(finite_ordinal_set(3))

    @staticmethod
    def __classcall__(cls, group):
        return OwnedParameterizedCategory.__classcall__(cls, _owned_group(group))

    def __init__(self, group):
        OwnedParameterizedCategory.__init__(self, group)

    def _make_named_class_key(self, name):
        return self.group()

    def group(self):
        return self.parameter()

    acting_group = group

    def super_categories(self):
        return [GObjects(self.group(), Sets()), FiniteSets(), EnumeratedSets()]

    def _repr_object_names(self):
        return f"finite {self.group()}-sets"

    def _call_(self, point_set, action, *, injectivity_decision=None):
        r"""The finite ``G``-set on ``point_set`` with the action ``action(g, x)``."""
        return _finite_g_set_from_action(
            self.group(),
            point_set,
            action,
            injectivity_decision=injectivity_decision,
        )

    def from_permutation_representation(self, representation):
        r"""The finite action defined by the supplied ``G -> Perm(X)``.

        The permutation group retains its actual point set. The supplied
        group morphism is the action datum, including when it has a kernel.
        """
        if representation.domain() is not self.group():
            raise ValueError("the permutation representation must start at the acting group")
        permutations = representation.codomain()
        if permutations not in PermutationGroups():
            raise TypeError("the action morphism must land in a permutation group")
        if representation not in self.group().Mor(permutations):
            raise TypeError("a finite action requires a group morphism")
        points = permutations.natural_points()
        if points not in FiniteSets():
            raise ValueError("a finite action requires a finite permutation domain")
        return _object_of(
            self,
            point_set=points,
            permutation_representation=representation,
        )

    def trivial(self, point_set):
        r"""Equip ``point_set`` with the trivial action of this category's group."""
        return self(point_set, lambda _group_element, point: point)

    def _orbit_words(self, seeds, action, augmentation, *, point_key=None, retain_transitions=False, targets=()):
        r"""The one orbit search: the union of the orbits of ``seeds``, each point with a word.

        ``augmentation`` is a free cover ``pi: F ->> G``.  Breadth-first search
        over the free generators reaches each new point ``s.y`` by the word
        ``s t_y``.  Points are recorded by rank in a dictionary keyed by the
        point, or by its supplied injective rank key when the points are
        unhashable. The caller supplies an effective action and the
        hypothesis that these orbits are finite.  ``retain_transitions`` also
        returns the position table ``(point position, letter position) -> image
        position`` of the sweep itself: the search evaluates every pair
        exactly once, and the set realized from it reads that table into the
        selected generators' permutations instead of paying the action
        evaluations again.  The table's letter positions index
        ``free.group_generators()``. With ``targets``, return the visited
        prefix on first reaching a target. Transition tables require the
        complete sweep and cannot be requested with a target.
        """
        targets = tuple(targets)
        if targets and retain_transitions:
            raise ValueError("a complete transition table requires the full finite orbit")
        free = augmentation.domain()
        steps = tuple((word, augmentation(word)) for word in free.group_generators())
        points = list(finite_ordered_set(tuple(seeds)))
        key = (lambda point: point) if point_key is None else point_key
        rank = {key(point): position for position, point in enumerate(points)}
        words = [free.one() for _point in points]
        target_keys = {key(point) for point in targets}
        if target_keys.intersection(rank):
            return points, words
        transitions = {} if retain_transitions else None
        position = 0
        while position < len(points):
            for letter_position, (word, element) in enumerate(steps):
                image = action(element, points[position])
                image_key = key(image)
                if image_key not in rank:
                    rank[image_key] = len(points)
                    points.append(image)
                    words.append(word * words[position])
                if transitions is not None:
                    transitions[(position, letter_position)] = rank[image_key]
                if image_key in target_keys:
                    return points, words
            position += 1
        if retain_transitions:
            return points, words, transitions
        return points, words

    def transporter_from_finite_orbit(self, source, target, action):
        r"""Return one element carrying ``source`` to ``target`` in a finite orbit.

        The supplied effective action has hashable points and a finite
        source orbit. The existing orbit-word search stops on a witness;
        exhausting the orbit proves that the transporter is empty.
        """
        group = self.group()
        if source == target:
            return group.one()
        augmentation = group.selected_group_resolution().augmentation()
        points, words = self._orbit_words((source,), action, augmentation, targets=(target,))
        return next((augmentation(word) for point, word in zip(points, words, strict=True) if point == target), None)

    def transporter_on_left_cosets(self, subgroup, source, target, inclusion):
        r"""Transport source*H to target*H under the supplied group inclusion.

        The finite-index hypothesis comes from a finite ambient group, a
        selected finite coset action, or the subgroup's finite quotient
        data. Enumerate only the acting group's source orbit, retaining
        the actual coset equality and inverse witness.
        """
        from sage_extensions.categories.group.predicate_subgroups import PredicateSubgroups

        ambient = subgroup.supergroup()
        if inclusion.domain() is not self.group() or inclusion.codomain() is not ambient:
            raise ValueError("the coset action needs an inclusion into the subgroup's ambient group")
        finite = ambient in OwnedFiniteGroups()
        if not finite and ambient.has_selected_left_cosets(subgroup):
            finite = ambient.left_cosets(subgroup) in FiniteGSets(ambient)
        if not finite and subgroup in PredicateSubgroups(ambient):
            finite = subgroup.has_finite_coset_space()
        if not finite:
            raise ValueError(f"no finite left-coset action is supplied for {subgroup}")
        points = _LeftCosetPointSet(ambient, subgroup)
        return self.transporter_from_finite_orbit(
            points(source), points(target),
            lambda element, point: points(inclusion(element) * point.representative()),
        )

    def preimage_coset_space(self, subgroup, morphism, target, augmentation):
        r"""Return G/f^-1(H) from its orbit in the finite target's cosets.

        Only f(G)'s orbit of H is needed; the ambient target need not be
        the image of f. The supplied free cover retains the section and
        the full Schreier generating morphism of the preimage.
        """
        if subgroup.supergroup() is not self.group() or morphism.domain() is not self.group():
            raise ValueError("the finite preimage and its morphism must have this acting group as source")
        if morphism.codomain() not in OwnedFiniteGroups() or target.supergroup() is not morphism.codomain():
            raise ValueError("the preimage coset action requires a subgroup of the finite target")
        points = _LeftCosetPointSet(morphism.codomain(), target)

        @cached_function(key=lambda element: (id(element), element))
        def image(element):
            return morphism(element)

        return self.pointed_orbit(
            subgroup, points(morphism.codomain().one()),
            lambda element, point: points(image(element) * point.representative()),
            augmentation,
        )

    def from_finite_orbits(self, seeds, action):
        r"""The union of the finite orbits of supplied points under a given action.

        The caller supplies an effective action and the hypothesis that these
        orbits are finite. Enumerating generator images then terminates at
        exactly their union; no search bound is a finiteness certificate.
        The one breadth-first sweep both reaches the point set and supplies
        the selected letters' permutations on it, so the resulting ``G``-set's
        action is realized without evaluating the supplied action a second
        time (``orbit_schreier_morphism`` reads the images back from
        ``permutation_representation``).  The sweep is a route to that set,
        not a datum of it: a later question about this action is answered by
        the action.  The seeds are materialized once, so a one-shot iterable is
        consumed before, not after, the sweep.

        The finished sweep is closed under every selected letter, so the
        positions reachable in its table from any of its points are exactly
        that point's orbit, and the words composed along them carry the point
        to each other one.  The set retains that table, and the first orbit
        question about one of its seeds is answered from it -- the points, the
        section and the orbit's own table -- without a second search
        (``_orbit_of``).  A point listed twice is one seed; the orbit of a point
        the sweep did not start from is searched for.  The orbit sets are built
        on that first question, not here: a caller that reads only the union
        builds none of them.
        """
        seeds = tuple(seeds)
        augmentation = self.group().selected_group_resolution().augmentation()
        points, _sweep_words, transitions = self._orbit_words(
            seeds, action, augmentation, retain_transitions=True,
        )
        g_set = self._from_orbit_sweep(points, action, augmentation, transitions)
        g_set._finished_sweep = (frozenset(seeds), points, transitions, action, augmentation, {})
        return g_set

    def _orbit_within_sweep(self, points, transitions, augmentation, seed):
        r"""The orbit of one seed inside a finished sweep, read off the sweep's table.

        ``_orbit_words`` returns ``transitions`` as the complete table
        ``(point position, letter position) -> point position`` of a sweep that
        ran to exhaustion, so the sweep is closed under every selected letter
        and the positions reachable from ``seed``'s are exactly ``seed``'s
        orbit.  The breadth-first walk over that table assigns each reachable
        position the word carrying ``seed`` to it: it reaches the position of
        ``s.q`` from that of ``q`` by the letter ``s``, so the word there is
        ``s * t_q``, the composition ``_orbit_words`` itself uses.  The walk
        multiplies positions and words of the free cover and evaluates no
        action.

        The sweep's own word list is not read here: it writes the identity at
        every seed the sweep started from, so it is a section from a lone seed
        and from no other.  The returned points are in walk order with ``seed``
        first, the words are in that order, and the table is the sweep's
        restricted to this orbit and renumbered by that order.  The points are
        hashable, as the sweep's own rank dictionary requires.
        """
        free = augmentation.domain()
        letters = tuple(free.group_generators())
        position_of = {point: position for position, point in enumerate(points)}
        reached = [position_of[seed]]
        index = {reached[0]: 0}
        words = [free.one()]
        cursor = 0
        while cursor < len(reached):
            for letter_position, letter in enumerate(letters):
                image = transitions[(reached[cursor], letter_position)]
                if image not in index:
                    index[image] = len(reached)
                    reached.append(image)
                    words.append(letter * words[cursor])
            cursor += 1
        orbit_transitions = {
            (index[current], letter_position): index[transitions[(current, letter_position)]]
            for current in reached
            for letter_position in range(len(letters))
        }
        return tuple(points[position] for position in reached), words, orbit_transitions

    def _from_orbit_sweep(self, points, action, augmentation, transitions):
        r"""Realize the finite action from its complete generator transition table.

        The orbit sweep has evaluated every selected letter on every point.
        Its columns are the images of those letters under ``G -> Sym(X)``.
        Retain these finite permutations when admitting the elementwise
        morphism; other group elements use the supplied defining action.
        The table is read here into that representation and is not stored: the
        construction's datum is the point set with the action on it, and this
        one table entry per letter and point is the sweep's route to it.  The
        representation it builds is the one ``orbit_generator_permutations``
        and the Schreier construction read.
        """
        point_set = finite_ordered_set(tuple(points))
        permutations = SymmetricGroups()(point_set)
        letters = tuple(augmentation.domain().group_generators())
        assert len(transitions) == len(points) * len(letters)
        generator_images = {
            augmentation(letter): permutations([
                transitions[(position, letter_position)] + 1
                for position in range(len(points))
            ])
            for letter_position, letter in enumerate(letters)
        }

        def permutation(element):
            if element in generator_images:
                return generator_images[element]
            return _permutation_from_point_map(
                permutations, point_set, lambda point: action(element, point),
            )

        representation = self.group().Mor(permutations).elementwise(permutation)
        return _object_of(
            self,
            point_set=point_set,
            permutation_representation=representation,
            point_action=action,
        )

    def pointed_orbit(self, subgroup, base, action, augmentation=None):
        r"""``G/H`` realized as the orbit of ``base``, for ``H`` the stabilizer of ``base``.

        The defining hypothesis is the caller's: ``H`` is the stabilizer of
        ``base`` and the orbit is finite.  Then ``gH |-> g.base`` identifies
        ``G/H`` with the orbit; the orbit search supplies the section
        ``p |-> t_p`` as a word section ``orbit -> F`` composed with the free
        cover ``pi: F ->> G`` (by default the selected one).  The result is the
        ``LeftCosetGSets(H)`` object retaining the orbit action, the base
        point, the section and its word factor.
        """
        if augmentation is None:
            augmentation = self.group().selected_group_resolution().augmentation()
        points, words, transitions = self._orbit_words(
            (base,), action, augmentation, retain_transitions=True,
        )
        orbit = self._from_orbit_sweep(points, action, augmentation, transitions)
        return orbit._pointed_coset_space(subgroup, base, words, augmentation)

    def underlying_category(self):
        r"""``FinSet``, the codomain of the forgetful functor."""
        return FiniteSets()

    # Functors out of finite G-sets, sited on their domain.

    @cached_method
    def forgetful_functor(self):
        r"""``U : FinGSet_G -> FinSet``, the underlying finite set of a finite ``G``-set."""
        from sage_extensions.categories.functors.g_sets import (
            UnderlyingFiniteGSetFunctor,
        )

        return UnderlyingFiniteGSetFunctor(self.group())

    @cached_method
    def orbits_functor(self):
        r"""``X |-> X/G : FinGSet_G -> FinSet``."""
        from sage_extensions.categories.functors.g_sets import GSetOrbitsFunctor

        return GSetOrbitsFunctor(self.group())

    @cached_method
    def fixed_points_functor(self):
        r"""``X |-> X^G : FinGSet_G -> FinSet``."""
        from sage_extensions.categories.functors.g_sets import (
            GSetFixedPointsFunctor,
        )

        return GSetFixedPointsFunctor(self.group())

    @cached_method
    def orbits_trivial_adjunction(self):
        r"""``(-)/G -| Triv_G``."""
        from sage_extensions.categories.functors.g_sets import (
            _g_set_orbits_trivial_adjunction,
        )

        return _g_set_orbits_trivial_adjunction(self.group())

    @cached_method
    def underlying_cofree_adjunction(self):
        r"""``U -| Map(G, -)``: the underlying set is left adjoint to the cofree ``G``-set."""
        from sage_extensions.categories.functors.g_sets import (
            _underlying_cofree_g_set_adjunction,
        )

        return _underlying_cofree_g_set_adjunction(self.group())

    _MorCategory = GSetMorCategoryConstruction

    class ParentMethods:
        _derived_construction_parameters = frozenset(
            {"acting_group", "action", "underlying_category"}
        )

        def __init__(self, point_set, permutation_representation, point_action=None, **rest) -> None:
            assert point_set in FiniteSets(), (
                f"cannot form a finite G-set on {point_set}: it is not a finite set, only "
                f"known to be in {point_set.category()}"
            )
            group = permutation_representation.domain()
            self._point_set = point_set
            self._permutation_representation = permutation_representation
            self._point_action = point_action
            super().__init__(
                acting_group=group,
                action=self.action_of,
                underlying_category=Sets(),
                facade=point_set,
                **rest,
            )
            self.validate_point_closure(check=False)

        @validator
        def validate_point_closure(self) -> None:
            r"""Raise ``ValueError`` unless ``G`` maps the point set into itself (``OWN-22``).

            The permutation representation ``G -> Sym(n)`` is a group
            morphism, so it restricts to an action on the point set ``X``
            exactly when ``X`` is stable under it.  Stability is decided on
            the chosen group generators, or on every element of a finite
            group without them.
            """
            group = self.acting_group()
            representation = self.permutation_representation()
            permutations = representation.codomain()
            match group:
                case _ if group.has_selected_group_resolution():
                    determining = group.group_generators()
                case _ if group.is_finite() is True:
                    determining = group
                case _:
                    assert False, (
                        f"cannot check that {representation} is an action of {group} on "
                        f"{self.point_set()}: {group} has no chosen group generators and is "
                        f"not known to be finite"
                    )
            for group_generator in determining:
                permutation = permutations(representation(group_generator))
                for point in self.point_set():
                    image = permutation(point)
                    if image not in self.point_set():
                        raise ValueError(
                            f"{representation} is not an action of {group} on "
                            f"{self.point_set()}: {group_generator} sends {point} outside it"
                        )

        def permutation_representation(self):
            r"""Return the chosen action as the group morphism ``G -> Sym(X)``."""
            return self._permutation_representation

        @cached_method
        def action_of(self, group_element):
            r"""Evaluate the retained group map to obtain the permutation of ``X``.

            The group arrow owns admission of its source point. In particular,
            a supplied word in a generated subgroup retains that premise when
            its element is represented in the containing group; evaluating the
            action does not ask the subgroup's membership problem again.
            """
            if self._point_action is not None:
                return Sets().Mor(self, self)(
                    lambda point: self._point_action(group_element, point)
                )
            permutation = self.permutation_representation()(group_element)
            return Sets().Mor(self, self)(
                lambda point: permutation(point)
            )

        def point_set(self):
            r"""Return the finite set used to present the points of this ``G``-set."""
            return self._point_set

        def __iter__(self):
            return iter(self.point_set())

        def __contains__(self, point) -> bool:
            return point in self.point_set()

        is_parent_of = __contains__

        def __call__(self, point):
            return self._element_constructor_(point)

        def _element_constructor_(self, point):
            assert point in self.point_set(), f"{point!r} is not a point of {self}"
            return self.point_set()(point)


        def fixed_points(self):
            r"""The fixed-point set ``X^G``."""
            return FiniteGSets(self.acting_group()).fixed_points_functor()(self)

        @cached_method
        def _orbit_labels(self):
            r"""The rank of the first point of each point's orbit, keyed by the point's rank.

            The orbits are those of the image of ``G`` in ``Sym(X)``, which
            GAP computes from the images of the chosen group generators, or
            of every element of a finite group without them.
            """
            group = self.acting_group()
            match group:
                case _ if group.has_selected_group_resolution():
                    action_generators = group.group_generators()
                case _ if group.is_finite() is True:
                    action_generators = group
                case _:
                    assert False, (
                        f"cannot compute the orbits of {self}: the acting group {group} "
                        f"has no chosen group generators and is not known to be finite"
                    )
            representation = self.permutation_representation()
            image_group = representation.codomain().subgroup(
                tuple(representation(generator) for generator in action_generators)
            )
            image_engine = _engine_group(image_group)
            # One GAP Orbits call on the full permutation domain 1..|X|.
            labels = {}
            for orbit in image_engine.orbits():
                first = min(int(image) for image in orbit) - 1
                for image in orbit:
                    labels[int(image) - 1] = first
            assert len(labels) == int(self.cardinality().finite_value()), (
                f"the orbits of {image_group} do not cover the {self.cardinality()} points of {self}"
            )
            return labels

        def _orbit_relation_decision(self, source, target) -> bool:
            r"""Two points share an orbit exactly when their orbits have the same first point."""
            labels = self._orbit_labels()
            ranking = self.ranking_map()
            return labels[int(ranking(source))] == labels[int(ranking(target))]

        def _orbit_subset(self, point):
            r"""The orbit ``G . point`` as the block of the retained partition of ``X``.

            Protected computation, owned here because the partition is this
            object's datum: ``_orbit_labels`` returns, for every position of
            ``X``, the position of the first point of its orbit, computed once
            from the orbits of the chosen group generators.  Its fibres are the
            orbits, so the orbit of ``point`` is the subobject of ``X`` on the
            positions carrying ``point``'s label, in the order of ``X``, and that
            is a read of the partition.

            ``GObjects.in_same_orbit`` is the two-point relation on ``X``, and
            deciding it at each point of ``X`` answers the same membership by
            re-deriving the partition; it is not asked here.  The only question
            put to the enumeration is ``point``'s own position.
            """
            assert point in self, f"{point} is not a point of {self}"
            labels = self._orbit_labels()
            first = labels[int(self.ranking_map()(point))]
            positions = tuple(
                sorted(position for position, label in labels.items() if label == first)
            )
            return _subset_on_positions(
                self.point_set(),
                positions,
                description=lambda: f"Orbit of {point} under {self.acting_group()}",
            )

        def orbit_stabilizers(self):
            r"""The family of point stabilizers indexed by the orbit classes."""
            orbits = self.orbits()
            return finite_indexed_family(
                orbits,
                lambda orbit: self.stabilizer(orbit.representative()),
                description=lambda self=self: f"Orbit stabilizers of {self}",
            )

        def is_transitive_action(self) -> bool:
            r"""Whether the action has one orbit."""
            return bool(self.orbits().cardinality() == cardinal(1))

        def is_free_action(self):
            r"""Whether every point stabilizer is trivial, when decidable.

            A nonempty finite set cannot carry a free action of an infinite
            group.  For a finite acting group, direct finite enumeration is an
            exact decision procedure for the point-stabilizer condition.
            """
            group = self.acting_group()
            if group.is_finite() is False:
                return False
            if group.is_finite() is not True:
                return AtomicProposition("is_free_action", self)
            identity = group.one()
            return all(
                self.act(group_element, point) != point
                for point in self
                for group_element in group
                if group_element != identity
            )

        def is_torsor(self):
            r"""Whether this finite represented action is free and transitive."""
            free = self.is_free_action()
            if free is not True:
                return free
            return self.is_transitive_action()

        def _pointed_coset_space(self, subgroup, base, words, augmentation):
            r"""``G/H`` on this transitive ``G``-set, from the words of its points in rank order."""
            ranking = self.ranking_map()
            word_section = Sets().Mor(self, augmentation.domain())(
                lambda point: words[int(ranking(point))]
            )
            return LeftCosetGSets(subgroup).from_transitive_action(
                self,
                base,
                augmentation * word_section,
                word_section=word_section,
                augmentation=augmentation,
            )

        def setwise_transporter_witness(self, source_subset, target_subset):
            r"""One actual group element carrying a finite subset onto another.

            Sweep only the finite orbit of the source subset under the
            supplied action; retain its free-word section.  Return ``None``
            precisely when the target subset is absent from that orbit.
            The action may come from an infinite group with finite image.
            """
            points = self.point_set()
            power = points.power_set()
            source_subset = power(source_subset)
            target_subset = power(target_subset)
            ranking = points.ranking_map()

            def members(subobject):
                inclusion = subobject.inclusion()
                return tuple(inclusion(member) for member in inclusion.domain())

            def key(subobject):
                return frozenset(int(ranking(member)) for member in members(subobject))

            def action(element, subobject):
                return power(tuple(self.act(element, member) for member in members(subobject)))

            category = FiniteGSets(self.acting_group())
            augmentation = self.acting_group().selected_group_resolution().augmentation()
            orbit_points, words = category._orbit_words(
                (source_subset,), action, augmentation, point_key=key,
            )
            target_key = key(target_subset)
            for point, word in zip(orbit_points, words, strict=True):
                if key(point) == target_key:
                    return augmentation(word)
            return None

        def setwise_stabilizer(self, subset):
            r"""Return ``{g : g.S = S}`` by the finite orbit of ``S``.

            Direct image gives the action on the power set
            (Mathlib ``Set.mulActionSet``). Its point stabilizer is the
            setwise stabilizer. Reuse finite-orbit enumeration and Schreier
            generators; do not enumerate the entire power set. Subsets are
            owned subobjects, interned here by their finite rank sets so
            their presentation identity cannot split one orbit point.
            """
            points = self.point_set()
            power = points.power_set()
            subset = power(subset)
            ranking = points.ranking_map()
            selected = {}

            def point(members):
                ranks = frozenset(int(ranking(member)) for member in members)
                if ranks not in selected:
                    selected[ranks] = power(tuple(points[rank] for rank in sorted(ranks)))
                return selected[ranks]

            def members(subobject):
                inclusion = subobject.inclusion()
                return (inclusion(member) for member in inclusion.domain())

            start = point(members(subset))

            def action(element, subobject):
                return point(self.act(element, member) for member in members(subobject))

            def subset_ranks(subobject):
                return frozenset(int(ranking(member)) for member in members(subobject))

            category = FiniteGSets(self.acting_group())
            augmentation = self.acting_group().selected_group_resolution().augmentation()
            orbit_points, words = category._orbit_words(
                (start,), action, augmentation, point_key=subset_ranks,
            )
            orbit = category(finite_ordered_set(tuple(orbit_points)), action)
            orbit_ranking = orbit.ranking_map()
            word_section = Sets().Mor(orbit, augmentation.domain())(
                lambda image: words[int(orbit_ranking(image))]
            )
            generating_morphism = _orbit_schreier_morphism(
                orbit,
                word_section,
                augmentation,
            )
            from sage_extensions.categories.group.predicate_subgroups import (
                StabilizerSubgroups,
            )

            return StabilizerSubgroups(self.acting_group())(
                start,
                orbit.action_functor(),
                lambda group_element: orbit.act(group_element, start) == start,
                lambda: f"setwise stabilizer of {_named_by_its_own_words(subset)} in {self.acting_group()}",
                generating_morphism=generating_morphism,
            )

        @cached_method(key=lambda self, point: self.ranking_map()(point))
        def _orbit_of(self, point):
            r"""The single orbit datum of ``point``: its orbit ``G``-set and its words, by the selected cover.

            The orbit of ``point`` is the ``G``-set on the points reachable
            from it, with this set's action restricted to them.  The
            breadth-first sweep that reaches them is this method's own work,
            cached on the point's rank: it runs in this set's permutation
            representation, which is its action, so no supplied action is
            evaluated a second time, and the words it assigns are the section
            ``p |-> t_p``.  The orbit is realized from that sweep's table,
            which is read at construction and not stored.

            A set built by ``from_finite_orbits`` retains its construction's
            finished sweep, which reached every seed's orbit: its table gives the
            seed's orbit, its section and the orbit's own table, so the first
            question about a seed searches nothing.
            """
            category = FiniteGSets(self.acting_group())
            sweep = self.__dict__.get("_finished_sweep")
            if sweep is not None and point in sweep[0]:
                _seeds, points, transitions, action, augmentation, orbits = sweep
                orbit_points, orbit_words, orbit_transitions = category._orbit_within_sweep(
                    points, transitions, augmentation, point,
                )
                # One orbit set per orbit: the points of an orbit, as a set,
                # name it whichever of them is asked about.
                reached = frozenset(orbit_points)
                if reached not in orbits:
                    orbits[reached] = (
                        self if len(orbit_points) == len(points)
                        else category._from_orbit_sweep(
                            orbit_points, action, augmentation, orbit_transitions,
                        )
                    )
                orbit = orbits[reached]
                ranking = orbit.ranking_map()
                section = [None] * len(orbit_points)
                for position, member in enumerate(orbit_points):
                    section[int(ranking(member))] = orbit_words[position]
                return orbit, section, augmentation
            augmentation = self.acting_group().selected_group_resolution().augmentation()
            representation = self.permutation_representation()
            # One permutation per group element for the duration of the sweep:
            # the representation answers a generator from its own images, and
            # any other element through the action.
            permutations = {}

            def action(element, candidate):
                if element not in permutations:
                    permutations[element] = representation(element)
                return permutations[element](candidate)

            points, words, transitions = category._orbit_words(
                (point,), action, augmentation, point_key=self.ranking_map(),
                retain_transitions=True,
            )
            orbit = category._from_orbit_sweep(points, action, augmentation, transitions)
            return orbit, words, augmentation

        @cached_method(key=lambda self, point: self.ranking_map()(point))
        def orbit_generator_permutations(self, point):
            r"""Return the selected cover's generator actions on the orbit of ``point``.

            The order is that of the letters in ``orbit_schreier_factors``, and
            the ``j``-th permutation is the orbit's own action at the ``j``-th
            letter, ``permutation_representation()(letter)``: the orbit owns
            that datum, so no table of a search that reached it is consulted.
            The positions are the orbit's selected point order.
            """
            orbit, _words, augmentation = self._orbit_of(point)
            representation = orbit.permutation_representation()
            return tuple(
                representation(augmentation(generator))
                for generator in augmentation.domain().group_generators()
            )

        @cached_method(key=lambda self, point: self.ranking_map()(point))
        def orbit_schreier_morphism(self, point):
            r"""Schreier's lemma on the orbit of ``point``: ``E -> G`` with image ``G_point``.

            The family is derived data of this ``G``-set at this point, so it is
            computed on the first request and the later ones are answered from
            the cache: the sections it realizes and the composites it forms are
            not paid for twice.
            """
            orbit, words, augmentation = self._orbit_of(point)
            ranking = orbit.ranking_map()
            word_section = Sets().Mor(orbit, augmentation.domain())(
                lambda image: words[int(ranking(image))]
            )
            return _orbit_schreier_morphism(orbit, word_section, augmentation)

        def orbit_transversal_words(self, point):
            r"""Return the orbit of ``point`` and the section ``p |-> t_p`` into the selected free cover.

            The transversal of an orbit point is returned as its *word* in the
            selected free cover, before it is realized as an element of the acting
            group.  ``augmentation() * section`` is the transversal map that
            :meth:`orbit_schreier_factors` materializes; a caller whose group is
            reached through an engine reads the words and realizes them there, so
            realizing ``|orbit|`` transversals costs that caller's own products
            rather than ``|orbit|`` owned word evaluations.
            """
            orbit, words, augmentation = self._orbit_of(point)
            ranking = orbit.ranking_map()
            section = Sets().Mor(orbit, augmentation.domain())(
                lambda image: words[int(ranking(image))]
            )
            return orbit, section

        @cached_method(key=lambda self, point: self.ranking_map()(point))
        def orbit_schreier_factors(self, point):
            r"""Return the letters and transversals whose composites are the Schreier family.

            :meth:`orbit_schreier_morphism` emits ``t_(s.p)^-1 s t_p`` over the
            orbit points ``p`` and the cover's letters ``s``, in that order.  The
            letters and the transversals are returned here separately, so a caller
            can realize the whole family by reading ``|letters| + |orbit|``
            elements and composing instead of reading ``|letters| * |orbit|`` of
            them.  Both are group elements of this G-set's group, in the order the
            family uses: ``letters[j]`` is the ``j``-th letter and
            ``transversals[i]`` is ``t_p`` for the ``i``-th orbit point, the
            augmentation of that point's section word.

            The pairs are derived data of this ``G``-set at this point, so they
            are computed on the first request and later requests are answered
            from the cache: realizing the transversals is not paid for twice.

            The composite law is the caller's to check: for the ``i``-th orbit
            point ``p`` and the ``j``-th letter ``s``, the family element is
            ``~transversals[position of s.p] * letters[j] * transversals[i]``.
            """
            _orbit, words, augmentation = self._orbit_of(point)
            return (
                tuple(
                    augmentation(generator)
                    for generator in augmentation.domain().group_generators()
                ),
                tuple(augmentation(word) for word in words),
            )

        @cached_method(key=lambda self, point: self.ranking_map()(point))
        def orbit_as_coset_space(self, point):
            r"""The orbit of ``point`` as ``G/G_point``, with the section of ``G -> G/G_point``."""
            return self.coset_space_for(point, self.stabilizer(point))

        def coset_space_for(self, point, subgroup):
            r"""``G/H`` on the orbit of ``point``, for a subgroup ``H`` presenting ``G_point``.

            The caller states that ``H`` is the stabilizer of ``point`` (for
            example a preimage subgroup cut out by the same condition); the
            orbit datum of ``point`` is the one computed for this ``G``-set.
            """
            orbit, words, augmentation = self._orbit_of(point)
            return orbit._pointed_coset_space(subgroup, orbit(point), words, augmentation)

        def transporter_witness(self, source, target):
            r"""Return one ``g`` with ``g.source = target``, or ``None`` when they lie in different orbits.

            The witness is the section of the pointed orbit ``G.source`` at
            ``target``; ``target`` outside that finite orbit has none.
            """
            if source not in self or target not in self:
                raise ValueError(
                    f"no transporter from {source} to {target} in {self}: both must be "
                    f"points of {self.point_set()}"
                )
            orbit, words, augmentation = self._orbit_of(source)
            if target not in orbit:
                return None
            return augmentation(words[int(orbit.ranking_map()(orbit(target)))])

        def _named_stabilizer(self, point):
            r"""Protected value hook: ``G_point`` by GAP when ``G`` is a finite group of GAP elements.

            The stabilizer is the preimage of the point stabilizer of the
            image of ``G`` in ``Sym(X)`` under the action homomorphism,
            ``PreImage(rho, Stabilizer(rho(G), x))``; GAP computes it by a
            stabilizer chain (Seress, *Permutation Group Algorithms*,
            section 4.1). The generators are those of GAP's small generating
            set, not the ``|orbit| * |letters|`` Schreier generators of the
            orbit search.

            GAP's group constructor takes the identity beside the generators,
            and the identity is a datum of ``G``: it is read from ``G`` itself,
            so a generating family of any length presents the same group. The
            trivial group has the empty family, and ``G``'s point stabilizers
            there are trivial, which is the answer this hook returns.
            """
            group = self.acting_group()
            if not (
                group.has_selected_group_resolution()
                and group.is_finite() is True
                and _encodes_elements_in_gap(_engine_group(group))
            ):
                return None
            generators = tuple(group.group_generators())
            representation = self.permutation_representation()
            symmetric = representation.codomain()
            engine_generators = libgap([libgap(group._to_engine(generator)) for generator in generators])
            images = libgap([
                libgap(symmetric._to_engine(representation(generator)))
                for generator in generators
            ])
            homomorphism = libgap.GroupHomomorphismByImagesNC(
                libgap.Group(
                    engine_generators,
                    libgap.Identity(libgap(group._to_engine(group.one()))),
                ),
                libgap.SymmetricGroup(int(self.point_set().cardinality())),
                engine_generators,
                images,
            )
            position = int(self.ranking_map()(point)) + 1
            stabilizer = libgap.PreImage(
                homomorphism,
                libgap.Stabilizer(libgap.Image(homomorphism), position),
            )
            engine = _engine_group(group)
            return group.subgroup(tuple(
                group._from_engine(engine(element))
                for element in libgap.SmallGeneratingSet(stabilizer)
            ) or (group.one(),))

        def _stabilizer_generating_morphism(self, point):
            r"""Protected value hook: the Schreier morphism ``E -> G`` onto ``G_point``.

            Owner ``GObjects``, supplied here by ``FiniteGSets``; its only
            caller is ``GObjects.stabilizer``, which passes it to the
            stabilizer constructor as that subgroup's generating datum.
            Without a selected resolution of ``G`` no value is supplied.
            """
            if not self.acting_group().has_selected_group_resolution():
                return None
            return self.orbit_schreier_morphism(point)

        def transporter(self, source, target):
            r"""Return the unique transporter between two points of a torsor.

            A general action has a transporter *coset*, not a unique element.
            ``transporter_witness`` is the generic finite-action operation;
            this spelling is reserved for the torsor case.
            """
            if self.is_torsor() is not True:
                raise ValueError(
                    f"{self} is not known to be a torsor under {self.acting_group()} (a free "
                    f"transitive action), so the element carrying {source} to {target} is "
                    f"not unique; use transporter_witness() for one such element"
                )
            return self.transporter_witness(source, target)

        @cached_method
        def ranking_map(self):
            r"""The point set's own enumeration, read on this $G$-set.

            An enumeration of the points is a bijection of sets and nothing
            more: it is not equivariant, since a group element moves a point
            to one of another position.
            """
            points = self.point_set().ranking_map()
            return self._ranking_isomorphism(points, points.inverse())

        def _repr_(self):
            return f"{self.point_set()} with {self.acting_group()}-action"


class LeftCosetGSets(OwnedParameterizedCategory):
    r"""The represented transitive left-coset ``G``-sets ``G/H``."""

    def parameter_category(self):
        from sage_extensions.categories.group.groups import Subgroups

        subgroup = self.parameter()
        return Subgroups(subgroup.supergroup())

    def subgroup(self):
        return self.parameter()

    def super_categories(self):
        return [GObjects(self.subgroup().supergroup(), Sets())]

    def an_object(self):
        subgroup = self.subgroup()
        return _left_coset_g_set(subgroup.supergroup(), subgroup)

    def from_transitive_action(self, action, base_point, representative_map, *, word_section=None, augmentation=None):
        r"""Realize ``G/H`` by a finite pointed transitive ``G``-set.

        The construction data are an actual finite action ``X``, a point
        ``x_0`` with stabilizer the specified ``H``, and an owned map
        ``s: X -> G`` satisfying ``s(x).x_0 = x``. These defining hypotheses
        identify ``gH`` with ``g.x_0``; a finite list alone is not such an
        identification. The action, point and map are retained literally.

        This realization does not require ``G`` to be finite or compute a
        presentation of it. Its representative map may be the composite of
        an actual free-word section with a free cover ``pi: F ->> G``; the
        caller then also supplies those two factors, which the Schreier
        generating morphism of ``H`` reads.
        """
        subgroup = self.subgroup()
        group = subgroup.supergroup()
        if action not in FiniteGSets(group):
            raise TypeError("a finite coset realization needs a finite action of the specified ambient group")
        if representative_map not in Sets().Mor(action, group):
            raise TypeError("the representative map must have the exact action as source and ambient group as target")
        return _object_of(
            owned_category_join((self, FiniteGSets(group))),
            point_set=action.point_set(),
            permutation_representation=action.permutation_representation(),
            coset_subgroup=subgroup,
            coset_action=action,
            coset_base_point=action(base_point),
            coset_representative_map=representative_map,
            coset_word_section=word_section,
            coset_augmentation=augmentation,
        )

    class ParentMethods:
        def __init__(
            self, coset_subgroup, coset_action=None, coset_base_point=None,
            coset_representative_map=None, coset_word_section=None,
            coset_augmentation=None, **rest,
        ) -> None:
            self._coset_subgroup = coset_subgroup
            self._coset_action = coset_action
            self._coset_base_point = coset_base_point
            self._coset_representative_map = coset_representative_map
            self._coset_word_section = coset_word_section
            self._coset_augmentation = coset_augmentation
            super().__init__(**rest)

        @cached_method(key=lambda self, drop_trivial=False: bool(drop_trivial))
        def schreier_generating_morphism(self, *, drop_trivial=False):
            r"""Schreier's lemma: ``E ->> H`` from the section of ``G -> G/H``.

            The transversal sends the base point to its selected coset.
            Thus ``t_(s.p)^-1 s t_p`` fixes the base point, whose stabilizer
            is the supplied H. This defining range law gives the
            corestriction of the complete Schreier generating map.
            ``drop_trivial`` omits the generators whose image is the identity
            (``_orbit_schreier_morphism``), so the family presents the same
            subgroup without its trivial members.

            The morphism is derived data of this coset space, so it is computed
            on the first request for it and a later request for the same family
            -- the whole one or the trimmed one, the default written out or not
            -- is answered from the cache: the point-letter family is not built
            a second time.
            """
            assert self._coset_word_section is not None, (
                f"Schreier generators of {self.subgroup()} are read from a pointed coset space "
                f"with a word section through a free cover, which {self} was not built with"
            )
            schreier = _orbit_schreier_morphism(
                self, self._coset_word_section, self._coset_augmentation,
                drop_trivial=drop_trivial,
            )
            return schreier._corestrict_to_subgroup(self.subgroup())

        @cached_method
        def right_coset_projection(self):
            r"""``G -> H\\G``, presented on ``G/H`` by ``Hx |-> x^-1 H``: the set map ``x |-> x^-1 H``."""
            group = self.acting_group()
            return Sets().Mor(group, self)(lambda element: self.coset_of(~element))

        @cached_method
        def right_coset_section(self):
            r"""The right-coset transversal ``p |-> t_p^-1``: ``H t_p^-1`` is the right coset presented by ``p``."""
            section = self.representative_map()
            return Sets().Mor(self, self.acting_group())(lambda point: ~section(point))

        def double_cosets(self, left_subgroup):
            r"""``Q \\ G / H``: the orbit set of ``Q`` acting on ``G/H`` through its inclusion.

            The double coset of an orbit is ``Q t_p H`` for any point ``p`` of
            it; the orbit set retains this coset space, its projection from
            ``G`` and its section.  ``Q`` is a subgroup of ``G`` itself.
            """
            group = self.acting_group()
            assert left_subgroup is group or left_subgroup.supergroup() is group, (
                f"the double cosets {left_subgroup} \\ {group} / {self.subgroup()} are the orbits of a "
                f"subgroup of {group}, but {left_subgroup} is a subgroup of {left_subgroup.supergroup()}"
            )
            inclusion = (
                OwnedGroups().Mor(group, group).identity()
                if left_subgroup is group
                else left_subgroup.inclusion()
            )
            acted = FiniteGSets(left_subgroup).from_permutation_representation(
                self.permutation_representation() * inclusion,
            )
            return _double_coset_set(acted, self, _DoubleCosetSet)

        def inverted_double_cosets(self, right_subgroup):
            r"""``Q \ G / H`` for this ``G/Q``, read through inversion ``x |-> x^-1``.

            ``H`` acts on ``G/Q``; inversion carries ``QxH`` to ``H x^-1 Q``,
            so the ``H``-orbit of ``tQ`` is the double coset ``Q t^-1 H``.
            The result's projection from ``G`` is ``g |-> H-orbit of g^-1 Q``
            and its section sends an orbit to ``t^-1``; the inversion is
            retained as the set map ``G -> G`` it is.
            """
            group = self.acting_group()
            assert right_subgroup is group or right_subgroup.supergroup() is group, (
                f"the double cosets {self.subgroup()} \\ {group} / {right_subgroup} need a subgroup of "
                f"{group}, but {right_subgroup} is a subgroup of {right_subgroup.supergroup()}"
            )
            inclusion = (
                OwnedGroups().Mor(group, group).identity()
                if right_subgroup is group
                else right_subgroup.inclusion()
            )
            acted = FiniteGSets(right_subgroup)(
                self, lambda element, point: self.act(inclusion(element), point)
            )
            return _double_coset_set(acted, self, _InvertedDoubleCosetSet)

        def subgroup(self):
            r"""Return ``H <= G`` for this represented left-coset ``G/H``."""
            return self._coset_subgroup

        def coset_of(self, element):
            r"""Return the unique left coset containing ``element``."""
            if self._coset_action is not None:
                return self.action_of(element)(self._coset_base_point)
            group = self.acting_group()
            element = group(element)
            if group.is_finite() is not True:
                return self.point_set()(element)
            for coset in self.point_set():
                if element in coset:
                    return coset
            raise ArithmeticError(
                f"{element} belongs to no represented left coset of {self.subgroup()} in {group}"
            )

        def base_point(self):
            r"""Return the distinguished point ``H`` of ``G/H``."""
            if self._coset_action is not None:
                return self(self._coset_base_point)
            return self.coset_of(self.acting_group().one())

        @cached_method
        def representative_map(self):
            r"""Return the chosen set map ``G/H -> G`` representing each coset.

            This is a section of ``g |-> gH`` as sets, with no equivariance
            claim. A pointed-action realization transports its actual supplied
            map through the identity on points, preserving that map's admitted
            range in a possibly infinite generated group. The older symbolic
            and finite subset realizations retain their chosen representatives.
            """
            if self._coset_action is not None:
                identify = Sets().Mor(self, self._coset_action)(lambda point: point)
                return self._coset_representative_map * identify
            return Sets().Mor(self, self.acting_group())(
                lambda coset: (
                    coset.representative()
                    if isinstance(coset, _LeftCosetPoint)
                    else next(iter(coset))
                )
            )

        @cached_method
        def regular_g_set(self):
            r"""Return ``G`` with its left regular action."""
            group = self.acting_group()
            if group.is_finite() is True:
                return FiniteGSets(group)(
                    finite_ordered_set(tuple(group)),
                    lambda group_element, point: group_element * point,
                )
            return GObjects(group, Sets()).on_set(
                group, lambda group_element, point: group_element * point,
            )

        @cached_method
        def projection(self):
            r"""Return the equivariant quotient map ``G -> G/H`` of left ``G``-sets."""
            regular = self.regular_g_set()
            return regular.Mor(self)(lambda element: self.coset_of(element))

        @cached_method
        def normal_quotient_comparison(self):
            r"""Return the canonical set isomorphism ``G/H ~= coker(H -> G)`` when ``H`` is normal."""
            inclusion = self.subgroup().inclusion()
            assert inclusion.is_normal(), (
                f"{self.subgroup()} is not normal in {self.acting_group()}, so {self} has no quotient-group structure"
            )
            quotient = inclusion.cokernel()
            quotient_projection = inclusion.cokernel_projection()
            forward = quotient_projection * self.representative_map()
            inverse = Sets().Mor(quotient, self)(
                lambda quotient_element: self.coset_of(
                    quotient_projection.lift(quotient_element)
                )
            )
            return Sets().Core().Mor(self, quotient)._from_known_inverse_pair(forward, inverse)


class GSetMor(GObjectMor):
    r"""The equivariant Mor category between represented finite ``G``-sets.

    A morphism of finite ``G``-sets is a map of the underlying finite sets
    that commutes with the actions, so its arrow is the ``GObjects(G, Sets())``
    arrow threaded through the arrow of ``FiniteSets().Mor``.
    """


class _Orbit:
    r"""The orbit ``G . x`` of one point ``x``, a point of the orbit set ``X/G``.

    Two orbits are equal exactly when they meet, so the selected point
    ``x`` is a representative and not part of the orbit's identity.
    """

    def __init__(self, parent, representative) -> None:
        self._representative = representative
        super().__init__(parent)

    def representative(self):
        r"""The point this orbit was named by."""
        return self._representative

    def g_set(self):
        return self.parent().g_set()

    def acting_group(self):
        return self.g_set().acting_group()

    def _decided_orbit_relation(self, point) -> bool:
        r"""Whether ``point`` lies in this orbit, where the orbit relation of ``X`` decides it.

        Membership and equality of orbits answer ``True`` or ``False`` and
        nothing else, so they are exact operations on the relation, not
        predicates: where ``ask`` of the relation is ``Unknown`` they reach
        the assertion frontier (``CAT-01``, ``DEV-52``) and never answer
        ``False`` for a question no procedure decided.
        """
        g_set = self.g_set()
        relation = ask(g_set.in_same_orbit(self.representative(), point))
        assert relation is not Unknown, (
            f"whether {point} lies in the orbit of {self.representative()} under "
            f"{self.acting_group()} is defined, but no procedure supplied by {g_set} decides it"
        )
        return relation

    def __contains__(self, point) -> bool:
        return point in self.g_set() and self._decided_orbit_relation(point)

    @cached_method
    def points(self):
        r"""The subset ``G . x`` of ``X``, read from the orbit partition of ``X``.

        A finite ``G``-set retains its orbit partition: ``_orbit_labels`` gives
        the first point of each point's orbit, once, from the chosen group
        generators, and the orbit of ``x`` is the block carrying ``x``'s label
        (`FiniteGSets._orbit_subset`).  Where no such partition is retained the
        subset is cut out by the orbit relation instead, wherever that relation
        is decided.
        """
        g_set = self.g_set()
        match g_set:
            case _ if g_set in FiniteGSets(g_set.acting_group()):
                return g_set._orbit_subset(self._representative)
            case _:
                return g_set.condition_set(self._decided_orbit_relation)

    def cardinality(self):
        r"""``|G . x| = [G : G_x]``, the index of the stabilizer of the representative.

        This is the orbit-stabilizer theorem.  On a finite set ``X`` the orbit
        is a block of the orbit partition the construction of a finite
        ``G``-set retains, so its cardinality is the number of points carrying
        its label and is read there.  Otherwise it is the index of the
        stabilizer, which the category of the stabilizer computes (an open
        subgroup of a profinite group knows its index from the degree of its
        fixed field).
        """
        g_set = self.g_set()
        match g_set:
            case _ if g_set in FiniteSets():
                return self.points().cardinality()
            case _:
                return self.stabilizer().index()

    def stabilizer(self):
        r"""The stabilizer of the representative; other points have conjugate stabilizers."""
        return self.g_set().stabilizer(self.representative())

    def transporter_from(self, point):
        r"""One group element carrying ``point`` to the representative."""
        assert point in self, f"{point} is not a point of {self}"
        return self.g_set().transporter_witness(point, self.representative())

    def _richcmp_(self, other, op):
        if op not in (op_EQ, op_NE):
            return NotImplemented
        if element_parent(other) is not self.parent():
            return op == op_NE
        meet = self._decided_orbit_relation(other.representative())
        return meet if op == op_EQ else not meet

    def __hash__(self) -> int:
        # Equal orbits may have different representatives, and the orbit
        # set supplies no invariant of an orbit beyond its parent.
        return hash(id(self.parent()))

    def _repr_(self) -> str:
        return f"Orbit of {self.representative()} under {self.acting_group()}"


class _OrbitSet:
    r"""The orbit set ``X/G`` of a ``G``-set ``X``.

    It is the coequalizer in ``Sets()`` of the action and the projection
    ``G x X -> X``.  The datum is ``X``; a point is an orbit named by one of
    its points, and equality of orbits is the orbit relation of ``X``.
    """

    def __init__(self, g_set, **rest) -> None:
        self._g_set = g_set
        super().__init__(**rest)

    def g_set(self):
        return self._g_set

    def orbit_of(self, point):
        r"""The orbit ``G . point``, the image of ``point`` under the projection ``X -> X/G``."""
        assert point in self.g_set(), f"{point} is not a point of {self.g_set()}"
        return self.element_class(self, self.g_set()(point))

    @cached_method
    def projection(self):
        r"""The projection ``X -> X/G`` of the coequalizer."""
        return Sets().Mor(self.g_set(), self)(self.orbit_of)

    def __contains__(self, orbit) -> bool:
        return element_parent(orbit) is self

    def __call__(self, orbit):
        return self._element_constructor_(orbit)

    def _element_constructor_(self, orbit):
        assert orbit in self, f"{orbit} is not an orbit of {self}"
        return orbit

    @cached_method
    def _orbits(self):
        r"""One orbit through each point, the first time the points meet it."""
        g_set = self.g_set()
        assert g_set in FiniteSets(), (
            f"the orbits of {g_set} are listed only when it is a finite set"
        )
        if g_set in FiniteGSets(g_set.acting_group()):
            # A finite G-set lists its orbits by their first points.
            labels = g_set._orbit_labels()
            ranking = g_set.ranking_map()
            return tuple(
                self.orbit_of(point)
                for point in g_set
                if labels[int(ranking(point))] == int(ranking(point))
            )
        found = []
        for point in g_set:
            orbit = self.orbit_of(point)
            if orbit not in found:
                found.append(orbit)
        return tuple(found)

    def __iter__(self):
        return iter(self._orbits())

    @cached_method
    def ranking_map(self):
        r"""The orbits in the order of their first points in the enumeration of ``X``."""
        orbits = self._orbits()
        return self._ranking_isomorphism(
            lambda orbit: orbits.index(self(orbit)),
            lambda position: orbits[position],
        )

    def _repr_(self) -> str:
        return f"Orbit set of {self.g_set()}"


class _DoubleCosetSet(_OrbitSet):
    r"""``Q \\ G / H`` as the ``Q``-orbits on the coset space ``G/H``.

    The data are the orbit ``Q``-set on ``G/H`` and the pointed coset space
    ``G/H`` with its section.  The projection ``G -> Q \\ G / H`` is
    ``g |-> Q-orbit of gH``; the section sends an orbit to the coset
    representative of its named point.
    """

    def __init__(self, g_set, coset_space, **rest) -> None:
        self._coset_space = coset_space
        super().__init__(g_set, **rest)

    def coset_space(self):
        return self._coset_space

    def group(self):
        return self._coset_space.acting_group()

    def _coset_of(self, element):
        return self._coset_space.coset_of(element)

    def _representative_of(self, orbit):
        return self._coset_space.representative_map()(orbit.representative())

    @cached_method
    def double_coset_projection(self):
        r"""``G -> Q \\ G / H``, ``g |-> QgH``."""
        return Sets().Mor(self.group(), self)(lambda element: self.orbit_of(self._coset_of(element)))

    @cached_method
    def double_coset_section(self):
        r"""``Q \\ G / H -> G``, one representative of each double coset."""
        return Sets().Mor(self, self.group())(self._representative_of)

    def _repr_(self) -> str:
        return f"Double cosets presented as the orbit set of {self.g_set()}"


class _InvertedDoubleCosetSet(_DoubleCosetSet):
    r"""``Q \\ G / H`` as the ``H``-orbits on ``G/Q``, through inversion.

    ``QxH`` corresponds to the ``H``-orbit of ``x^-1 Q``: the projection is
    ``g |-> H-orbit of g^-1 Q`` and the section ``t^-1`` for the
    representative ``t`` of an orbit, both through the retained inversion.
    """

    @cached_method
    def inversion(self):
        r"""The set map ``G -> G``, ``g |-> g^-1``."""
        group = self.group()
        return Sets().Mor(group, group)(lambda element: ~element)

    def _coset_of(self, element):
        return self._coset_space.coset_of(self.inversion()(element))

    def _representative_of(self, orbit):
        return self.inversion()(self._coset_space.representative_map()(orbit.representative()))


def _double_coset_set(g_set, coset_space, engine):
    r"""Construct a double-coset set on the orbit set of ``g_set``, placed as ``_orbit_set`` places it."""
    match g_set:
        case _ if g_set in FiniteSets() and g_set in EnumeratedSets():
            category = owned_category_join((FiniteSets(), EnumeratedSets()))
        case _ if g_set in FiniteSets():
            category = FiniteSets()
        case _:
            category = Sets()
    return _object_of(category, _engine=(category, engine, _Orbit), g_set=g_set, coset_space=coset_space)


class _TransversalOrbitSet(_OrbitSet):
    r"""The orbit set ``X/G`` presented by a finite set ``S subset X`` meeting every orbit.

    The datum adds to ``X`` a finite set ``S`` of points meeting every orbit;
    the caller's construction states this (``OWN-22``), as a theorem on the
    action does (a finiteness theorem for the orbits and an algorithm listing
    points of each).  ``X`` may be infinite.  The orbits are the distinct
    orbits of the points of ``S`` under the orbit relation of ``X``, which
    must be decided; :meth:`section` is the set map ``X/G -> X`` choosing the
    first point of ``S`` in an orbit, a section of :meth:`projection`.
    """

    def __init__(self, g_set, orbit_covering, **rest) -> None:
        self._orbit_covering = orbit_covering
        super().__init__(g_set, **rest)

    def orbit_covering(self):
        r"""The finite set ``S`` of points meeting every orbit."""
        return self._orbit_covering

    @cached_method
    def _representatives(self):
        r"""The points of ``S`` that are first in their orbit, each decided once.

        Each point of ``S`` is decided against the representatives already
        recorded, by orbit membership (the G-set's decided orbit relation); a decided relation
        on a general ``X`` has no canonical form to key by, so the record is
        keyed by representative point and grows by one per new orbit.  The
        decisions made are at most ``|S|`` times the number of orbits.
        """
        record = {}
        for point in self.orbit_covering():
            if not any(point in self.orbit_of(chosen) for chosen in record):
                record[point] = point
        return record

    @cached_method
    def _orbits(self):
        r"""One orbit per recorded representative, in the order of ``S``."""
        return tuple(self.orbit_of(point) for point in self._representatives())

    @cached_method
    def section(self):
        r"""The section ``s: X/G -> X`` of the projection, choosing the first point of ``S``.

        The orbit of a point ``x`` is sent to the recorded representative
        related to ``x``; every orbit has one because ``S`` meets it.
        """
        g_set = self.g_set()
        representatives = self._representatives()

        def chosen_point(orbit):
            point = orbit.representative()
            for chosen in representatives:
                if point in self.orbit_of(chosen):
                    return chosen
            assert False, (
                f"{orbit} meets no point of {self.orbit_covering()}, so that set does not meet "
                f"every orbit of {g_set}"
            )

        return Sets().Mor(self, g_set)(chosen_point)


def _orbit_set_presented_by(g_set, covering):
    r"""The orbit set ``X/G`` of ``X``, finite and enumerated through a finite set meeting every orbit."""
    category = owned_category_join((FiniteSets(), EnumeratedSets()))
    return _object_of(
        category,
        _engine=(category, _TransversalOrbitSet, _Orbit),
        g_set=g_set,
        orbit_covering=covering,
    )


def _orbit_set(g_set):
    r"""The orbit set ``X/G`` of the ``G``-set ``X``, finite and enumerated with ``X``."""
    match g_set:
        case _ if g_set in FiniteSets() and g_set in EnumeratedSets():
            category = owned_category_join((FiniteSets(), EnumeratedSets()))
        case _ if g_set in FiniteSets():
            category = FiniteSets()
        case _:
            category = Sets()
    return _object_of(category, _engine=(category, _OrbitSet, _Orbit), g_set=g_set)


class _GSetOnPoints:
    r"""A ``G``-set on a given set of points, with the procedure deciding its orbit relation.

    The data are the point set, the relation, a function of two points
    answering ``True``, ``False`` or ``Unknown``, and the stabilizer, a
    function naming the subgroup that fixes a point; the action is the
    ``GObjects`` datum.
    """

    def __init__(self, point_set, orbit_relation, stabilizer, **rest) -> None:
        self._point_set = point_set
        self._orbit_relation = orbit_relation
        self._stabilizer = stabilizer
        super().__init__(**rest)

    def point_set(self):
        return self._point_set

    def _emptiness_decision(self):
        r"""``Sets``' emptiness hook: a ``G``-set on points has the points of its point set."""
        return self.point_set()._emptiness_decision()

    def __contains__(self, point) -> bool:
        return point in self.point_set()

    is_parent_of = __contains__

    def __call__(self, point):
        return self._element_constructor_(point)

    def _element_constructor_(self, point):
        assert point in self.point_set(), f"{point!r} is not a point of {self}"
        return self.point_set()(point)

    def _normalize_admitted_element(self, point):
        r"""Preserve an actual group carrier's admitted word during arrow evaluation."""
        points = self.point_set()
        if points in OwnedGroups():
            return _GroupMorRealizationMixin._normalize_admitted_element(points, point)
        return None

    def __iter__(self):
        return iter(self.point_set())

    def _orbit_relation_decision(self, source, target):
        return self._orbit_relation(source, target)

    def _named_stabilizer(self, point):
        return self._stabilizer(point)

    def _repr_(self) -> str:
        return f"{self.point_set()} with {self.acting_group()}-action"


def _g_set_on_points(group, point_set, action, orbit_relation, stabilizer):
    r"""The ``G``-set on ``point_set`` with the action ``action(g, x)``.

    ``orbit_relation(x, y)`` decides whether ``y in G . x``, answering
    ``Unknown`` where no procedure decides it.  ``stabilizer(x)`` is the
    subgroup ``G_x`` the action names: the centralizer of an element under
    conjugation, the normalizer of a subgroup under conjugation.
    """
    g_sets = GObjects(group, Sets())
    match point_set:
        case _ if point_set in FiniteSets():
            category = owned_category_join((g_sets, FiniteSets()))
        case _:
            category = g_sets
    return _object_of(
        category,
        _engine=(category, _GSetOnPoints, None),
        point_set=point_set,
        orbit_relation=orbit_relation,
        stabilizer=stabilizer,
        acting_group=group,
        action=lambda group_element: (lambda point: action(group_element, point)),
        underlying_category=Sets(),
        facade=point_set,
    )


def _permutation_from_point_map(permutation_group, point_set, mapping):
    # A permutation is a bijection of the backend point domain. Let the
    # permutation engine check that property instead of searching all pairs
    # of points for preimage counts at this owned/engine boundary.
    ranking, _inverse = permutation_group._natural_point_ranking_and_inverse()
    images = [int(ranking(mapping(point))) + 1 for point in ranking.domain()]
    try:
        return permutation_group(images)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"the map {mapping} on {point_set} is not represented by a permutation"
        ) from error


def _owned_point_set(point_set):
    r"""Read a literal family of points as an owned finite ordered set.

    Literal ingress adapter: an owned set is already the point set; a Python
    tuple or list is read entry by entry, and a point written as a Python
    ``int`` is the owned integer, the same point a permutation group's
    elements return.
    """
    if point_set in FiniteSets():
        return point_set
    integers = _owned_integers()
    def own_point(point):
        match point:
            case int():
                return integers(point)
            case _:
                return point

    return finite_ordered_set(tuple(own_point(point) for point in point_set))


def _finite_g_set_from_action(
    group,
    point_set,
    action,
    *,
    injectivity_decision=None,
    category=None,
    construction_data=None,
):
    r"""Construct a represented finite ``G``-set from a binary action.

    ``action(g, x)`` is retained in the defining elementwise group morphism
    ``G -> Sym(X)``. Its value uses only the finite point set, never a source
    word-preimage solver. The action laws are the admitted defining laws;
    generator or finite-group computations belong to the explicit validators
    and orbit operations. Additional construction placement is joined with
    the actual finite-action owner rather than replacing it.
    """
    point_set = _owned_point_set(point_set)
    assert point_set in FiniteSets(), (
        f"cannot form a finite G-set on {point_set}: it is not a finite set, only "
        f"known to be in {point_set.category()}"
    )
    group = _owned_group(group)
    # The symmetric-group owner retains X and its ranking while its private
    # engine acts on 1,...,|X|. Arbitrary owned points never become engine
    # domain labels.
    permutations = SymmetricGroups()(point_set)
    mor = group.Mor(permutations)
    permutation_representation = mor.elementwise(
        lambda group_element: _permutation_from_point_map(
            permutations, point_set, lambda point: action(group_element, point),
        ),
        injectivity_decision=injectivity_decision,
    )
    selected_category = (
        FiniteGSets(permutation_representation.domain())
        if category is None
        else owned_category_join((category, FiniteGSets(group)))
    )
    return _object_of(
        selected_category,
        point_set=point_set,
        permutation_representation=permutation_representation,
        point_action=action,
        **dict(construction_data or {}),
    )


class _LeftCosetPoint(Element):
    r"""An equivalence class ``gH`` represented by ``g``; no coset enumeration."""

    def __init__(self, parent, representative):
        Element.__init__(self, parent)
        self._representative = representative

    def representative(self):
        return self._representative

    def __contains__(self, element):
        return self.representative().inverse() * element in self.parent().subgroup()

    @cached_method
    def _canonical_key(self):
        r"""The canonical transversal position of ``gH`` (see ``_LeftCosetPointSet._coset_key``), else ``None``."""
        key = self.parent()._coset_key()
        return None if key is None else key(self.representative())

    def __eq__(self, other):
        if not (isinstance(other, _LeftCosetPoint) and other.parent() is self.parent()):
            return False
        key = self._canonical_key()
        if key is not None:
            return key == other._canonical_key()
        return self.representative().inverse() * other.representative() in self.parent().subgroup()

    def __hash__(self):
        r"""Hash by the canonical coset key, so orbit searches look cosets up instead of comparing pairwise."""
        return hash((id(self.parent()), self._canonical_key()))

    def _repr_(self):
        return f"{self.representative()} * {self.parent().subgroup()}"


class _LeftCosetPointSet(Parent):
    r"""The quotient set of ``G`` under ``g ~ h`` iff ``g^-1 h in H``.

    This is a private representation of the selected points of the owned
    left-``G``-set ``G/H``; the action and quotient map belong to
    ``LeftCosetGSets(H)``, not to this point representation.
    """

    def __init__(self, group, subgroup):
        self._group = group
        self._subgroup = subgroup
        Parent.__init__(self, category=Sets())

    def subgroup(self):
        return self._subgroup

    @cached_method
    def _coset_key(self):
        r"""A map ``g |-> key(gH)`` with equal keys exactly for equal cosets, or ``None``.

        For finite GAP-encoded ``G`` the key is the position of ``g`` in
        GAP's transversal of ``H``.  For a preimage ``H = f^-1(K)`` along
        ``f: G -> Q`` into a finite GAP-encoded ``Q``, ``gH = g'H`` exactly
        when ``f(g)K = f(g')K``, so the key is the transversal position of
        ``f(g)`` in ``Q/K``.  Otherwise no canonical form is available.
        """
        from sage_extensions.categories.group.predicate_subgroups import PreimageSubgroups

        if self._subgroup in PreimageSubgroups(self._group) and self._subgroup.supergroup() is self._group:
            morphism = self._subgroup.preimage_morphism()
            image_positions = _engine_left_coset_positions(
                morphism.codomain(), self._subgroup.target_subgroup()
            )
            if image_positions is not None:
                return lambda element: image_positions.position_of(morphism(element))
        positions = _engine_left_coset_positions(self._group, self._subgroup)
        if positions is not None:
            return positions.position_of
        return None

    def _element_constructor_(self, representative):
        if isinstance(representative, _LeftCosetPoint) and representative.parent() is self:
            return representative
        return _LeftCosetPoint(self, self._group(representative))

    def __contains__(self, point):
        return isinstance(point, _LeftCosetPoint) and point.parent() is self


def _left_coset_g_set(group, subgroup):
    r"""Return ``G/H`` as its pointed transitive left ``G``-set."""
    group = _owned_group(group)
    if subgroup.supergroup() is not group:
        raise ValueError(
            f"cannot form left cosets of {subgroup} in {group}: the subgroup lies in {subgroup.supergroup()}"
        )
    from sage_extensions.categories.group.predicate_subgroups import (
        PredicateSubgroups,
    )

    # Kernels/preimages into finite groups, and intersections described by
    # complete finite characters, retain a finite coset realization with
    # its section for finite and infinite G alike.
    if subgroup in PredicateSubgroups(group) and subgroup.has_finite_coset_space():
        return subgroup.coset_space()
    if group.is_finite() is not True:
        points = _LeftCosetPointSet(group, subgroup)
        category = LeftCosetGSets(subgroup)
        return _object_of(
            category,
            _engine=(category, _GSetOnPoints, None),
            point_set=points,
            orbit_relation=lambda _left, _right: True,
            stabilizer=None,
            acting_group=group,
            action=lambda element: (lambda coset: points(element * points(coset).representative())),
            underlying_category=Sets(),
            facade=points,
            coset_subgroup=subgroup,
        )
    points = _LeftCosetPointSet(group, subgroup)
    return FiniteGSets(group).pointed_orbit(
        subgroup,
        points(group.one()),
        lambda element, coset: points(element * coset.representative()),
    )


def _fixed_point_set(g_set):
    r"""Return the finite fixed-point set ``X^G``."""
    return finite_ordered_set(g_set).filtered(g_set.is_invariant)


class Torsors(OwnedParameterizedCategory):
    r"""The owned category of free transitive ``G``-sets."""

    @staticmethod
    def __classcall__(cls, group):
        return OwnedParameterizedCategory.__classcall__(cls, _owned_group(group))

    def parameter_category(self):
        r"""A torsor is parameterized by its actual acting group ``G``."""
        return OwnedGroups()

    def group(self):
        return self.base()

    acting_group = group

    def an_object(self):
        r"""The regular torsor of a represented finite acting group."""
        group = self.group()
        assert group in OwnedFiniteGroups(), (
            f"a torsor under {group} exists for every group, but the current finite-G-set realization can "
            "exhibit the regular torsor only when the acting group is represented as finite"
        )
        points = finite_ordered_set(tuple(group))
        return self(
            FiniteGSets(group)(
                points,
                lambda group_element, point: group_element * point,
            )
        )

    def super_categories(self):
        return [GObjects(self.group(), Sets())]

    def _repr_object_names(self):
        return f"torsors under {self.group()}"

    def _call_(self, candidate):
        finite_g_sets = FiniteGSets(self.group())
        if candidate not in finite_g_sets or candidate.is_torsor() is not True:
            raise ValueError(
                f"{candidate} is not a torsor under {self.group()}: it must be a finite "
                f"{self.group()}-set whose action is free and transitive"
            )
        return _object_of(
            owned_category_join((candidate.category(), self)),
            point_set=candidate.point_set(),
            permutation_representation=candidate.permutation_representation(),
        )

    def from_action(self, acted_set, difference, point):
        r"""Select an action with a difference map and a nonempty witness.

        The difference satisfies ``difference(p, q) · q = p`` and
        ``difference(g · p, p) = g``. The point witnesses that the acted set
        is nonempty; it is not a chosen origin of the torsor.
        These are the fields of Mathlib's ``Torsor`` in
        ``Mathlib/Algebra/Torsor/Defs.lean``.
        """
        pass

    def from_trivialization(self, trivialization, *, base_point=None):
        r"""Transport the regular torsor along a chosen set isomorphism ``G -> T``.

        This works for infinite groups. The inverse is part of the given
        isomorphism; a selected point alone is not a trivialization. When
        the chosen point defining the trivialization is already available,
        retain it rather than evaluating the group identity through the
        potentially costly realization a second time. The supplied point
        must be the image of the identity under the selected trivialization.
        """
        if trivialization.domain() is not self.group():
            raise ValueError("a torsor trivialization must start at its acting group")
        return _object_of(
            TrivializedTorsors(self.group()),
            trivialization=trivialization,
            selected_base_point=base_point,
        )

    class ParentMethods:
        def _emptiness_decision(self) -> bool:
            r"""``Sets``' emptiness hook: a torsor is not empty, by definition.

            A torsor under ``G`` is a nonempty ``G``-set on which ``G`` acts
            freely and transitively: Mathlib's ``AddTorsor``
            (``Mathlib/Algebra/Torsor/Defs.lean``) carries the field
            ``nonempty : Nonempty P``, and ``lean-categories`` Definition 34.2
            (``FOUNDATIONS.md``, *Torsor*) requires the torsor to be locally
            nonempty.  A possibly empty locus on which ``G`` acts, such as the
            integral lifts of an isotropic reduction isometry, is a ``G``-set,
            not an object of this category.
            """
            return False

        def difference(self, left, right):
            r"""The unique group element carrying ``right`` to ``left``."""
            pass

        def an_element(self):
            r"""Return the selected point trivializing this represented torsor.

            A torsor has no canonical point.  The represented finite ``G``-set
            already carries an ordered point set, so its first point is the
            presentation's selected trivializing choice.
            """
            return next(iter(self.point_set()))

        def __iter__(self):
            r"""Enumerate through a chosen point and the free transitive action."""
            chosen = self.an_element()
            return (
                self.act(group_element, chosen)
                for group_element in self.acting_group()
            )

        def cardinality(self):
            r"""``|T| = |G|`` for a ``G``-torsor."""
            return self.acting_group().cardinality()


class OrbitRepresentativeSets(OwnedParameterizedCategory):
    r"""Selected orbit transversals, with no universal finiteness claim."""

    def parameter_category(self):
        return OwnedGroups()

    def super_categories(self):
        return [Sets()]

    def _call_(self, action, points):
        if action.acting_group() is not self.base():
            raise ValueError("the transversal and action must use the same group")
        if points in Sets():
            selected = points
        else:
            selected = finite_ordered_set(tuple(action(point) for point in points))
        category = owned_category_join((self, FiniteSets())) if selected in FiniteSets() else self
        return _object_of(category, action=action, points=selected)

    class ParentMethods:
        def __init__(self, action, points, **rest):
            self._action = action
            self._points = points
            super().__init__(facade=points, **rest)

        def action(self):
            return self._action

        def orbit_quotient(self):
            return self.action().orbits()

        def __iter__(self):
            return iter(self._points)

        def cardinality(self):
            return self._points.cardinality()

        def __contains__(self, point):
            return point in self._points

        def _element_constructor_(self, point):
            return self._points(point)

        @cached_method
        def inclusion(self):
            return Sets().Mor(self, self.action())(lambda point: point)

        @cached_method
        def projection(self):
            return self.orbit_quotient().projection() * self.inclusion()

        @cached_method
        def section(self):
            def representative(orbit):
                for point in self:
                    if (self.projection()(point) == orbit) is True:
                        return point
                raise ValueError("the selected family has no decidable representative of this orbit")

            return Sets().Mor(self.orbit_quotient(), self)(representative)


class TrivializedTorsors(OwnedParameterizedCategory):
    r"""Torsors presented by an isomorphism from the regular group action."""

    def parameter_category(self):
        return OwnedGroups()

    def super_categories(self):
        return [Torsors(self.base())]

    class ParentMethods:
        _derived_construction_parameters = ("acting_group", "action", "underlying_category")

        def __init__(self, trivialization, selected_base_point=None, **rest):
            self._trivialization = trivialization
            self._selected_base_point = selected_base_point
            group = trivialization.domain()
            points = trivialization.codomain()
            inverse = trivialization.inverse()
            super().__init__(
                acting_group=group,
                action=lambda g: lambda x: trivialization(g * inverse(x)),
                underlying_category=Sets(),
                facade=points,
                **rest,
            )

        def trivialization(self):
            return self._trivialization

        def point_set(self):
            return self.trivialization().codomain()

        @cached_method
        def base_point(self):
            r"""The point the selected trivialization sends the identity to.

            This is a datum of the torsor, not of the call that reads it: the
            group, the trivialization and the selected point are all fixed at
            construction, so every call asks for the same point.  Reading that
            point through the trivialization is not free -- the point sets of
            the torsors built from a condition set decide their defining
            predicate on ingress -- so it is computed once per torsor.  A point
            supplied to ``Torsors.from_trivialization`` is the point returned,
            as that method states.
            """
            if self._selected_base_point is not None:
                return self._selected_base_point
            return self.trivialization()(self.acting_group().one())

        def an_element(self):
            return self.base_point()

        def difference(self, left, right):
            r"""Return the unique ``g`` with ``g * right = left``."""
            inverse = self.trivialization().inverse()
            return inverse(left) * inverse(right).inverse()

        def __contains__(self, point):
            return point in self.point_set()

        def _element_constructor_(self, point):
            return self.point_set()(point)


__all__ = [
    "FiniteGSets",
    "LeftCosetGSets",
    "GSetMor",
    "Torsors",
]
