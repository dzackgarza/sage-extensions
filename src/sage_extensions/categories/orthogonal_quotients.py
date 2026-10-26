r"""Finite character quotients controlling arithmetic-subgroup orbit splitting."""
from sage.libs.gap.libgap import libgap
from sage.misc.cachefunc import cached_method
from sage.structure.element import parent as element_parent

from sage_extensions.categories.group.g_sets import FiniteGSets
from sage_extensions.categories.group.groups import Subgroups
from sage_extensions.categories.sets.finite_ordered_sets import (
    OrderedEnumeratedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import finite_indexed_family
from sage_extensions.categories.rings.ring_foundation import _owned_integers
from sage_extensions.categories.sets.set_categories import NN, Set, Sets


class OrthogonalCharacterQuotient:
    r"""The finite image of ``O(L)`` under the characters defining a subgroup.

    Components are the discriminant representation and optional determinant /
    real spinor norm (the character whose kernel is ``O^+(L)``, with values
    in \(\mathbb R^\times/(\mathbb R^\times)^2=\{\pm1\}\)).  The finite image is generated from live ``O(L)``
    generators, retaining one live lattice isometry above every quotient
    element.  This avoids introducing a parallel matrix-group model of the
    infinite arithmetic group.
    """

    def __init__(self, subgroup) -> None:
        self.subgroup = subgroup
        if not subgroup.character_data_is_complete():
            raise ValueError(
                f"{subgroup} is not the kernel of a finite quotient of O(L) by "
                f"characters: its discriminant, determinant and spinor characters do not "
                f"determine the whole subgroup"
            )
        # This finite-image algorithm is explicitly generator-driven: it reads
        # the generating epimorphism onto O(L), which O(L) selects at
        # construction; merely knowing O(L) is finitely generated would not do.
        self.supergroup = subgroup.supergroup()
        self.lattice = self.supergroup.domain()
        data = subgroup._character_data_snapshot()
        self.discriminant_preimages = tuple(data.get("discriminant_preimages", ()))
        self.determinant_kernel = bool(data.get("determinant_kernel", False))
        self.spinor_kernel = bool(data.get("spinor_kernel", False))
        if not (
            self.discriminant_preimages
            or self.determinant_kernel
            or self.spinor_kernel
        ):
            raise ValueError(
                f"{subgroup} defines no finite quotient of O({self.lattice}) by "
                f"characters: it is not cut out by the discriminant representation, "
                f"the determinant or the real spinor norm"
            )
        self._has_discriminant = bool(self.discriminant_preimages)
        factors = {}
        labels = []
        if self._has_discriminant:
            self._discriminant_group = self.lattice.discriminant_group().O()
            labels.append("discriminant")
            factors["discriminant"] = self._discriminant_group
            for target in self.discriminant_preimages:
                if (
                    target is not self._discriminant_group
                    and target not in Subgroups(self._discriminant_group)
                ):
                    raise ValueError(
                        f"{subgroup} is described as the preimage of {target} under "
                        f"O(L) -> O(A_L) for L = {self.lattice}, but {target} is not a "
                        f"subgroup of O(A_L) = {self._discriminant_group}"
                    )
        signs = finite_ordered_set(
            (self.lattice.base_ring()(-1), self.lattice.base_ring()(1))
        )
        if self.determinant_kernel:
            labels.append("determinant")
            factors["determinant"] = signs
        if self.spinor_kernel:
            # The real spinor norm sn_RR of O^+(L), valued in RR^x/(RR^x)^2,
            # read through its isomorphism [a] |-> sign(a) onto {-1, 1}.
            self._real_spinor_norm = self.lattice.O_plus().preimage_morphism()
            labels.append("spinor")
            factors["spinor"] = signs
        self._image_labels = finite_ordered_set(tuple(labels))
        self._image_space = Sets().product(
            finite_indexed_family(
                self._image_labels,
                factors.__getitem__,
                name="Orthogonal character quotient factors",
            )
        )
        self._witnesses = self._enumerate_image()

    def image_space(self):
        r"""Return the owned product in which all character images live."""
        return self._image_space

    def image(self, isometry):
        components = {}
        if self._has_discriminant:
            components["discriminant"] = isometry.discriminant_morphism()
        if self.determinant_kernel:
            components["determinant"] = self.lattice.base_ring()(isometry.determinant())
        if self.spinor_kernel:
            ring = self.lattice.base_ring()
            components["spinor"] = (
                ring.one() if self._real_spinor_norm(isometry).is_one() else -ring.one()
            )
        return self.image_space()(components.__getitem__)

    def _multiply(self, left, right):
        result = {}
        if self._has_discriminant:
            result["discriminant"] = left["discriminant"] * right["discriminant"]
        if self.determinant_kernel:
            result["determinant"] = left["determinant"] * right["determinant"]
        if self.spinor_kernel:
            result["spinor"] = left["spinor"] * right["spinor"]
        return self.image_space()(result.__getitem__)

    def _ambient_bound(self):
        bound = 1
        if self._has_discriminant:
            bound *= int(self._discriminant_group.order())
        if self.determinant_kernel:
            bound *= 2
        if self.spinor_kernel:
            bound *= 2
        return bound

    def _enumerate_image(self):
        return self.supergroup.finite_image_lifts(
            self.image,
            multiply=self._multiply,
            image_bound=self._ambient_bound(),
        )

    def _allowed(self, key) -> bool:
        if self._has_discriminant:
            discriminant_image = key["discriminant"]
            if any(
                discriminant_image not in target
                for target in self.discriminant_preimages
            ):
                return False
        if self.determinant_kernel:
            if key["determinant"] != 1:
                return False
        if self.spinor_kernel and key["spinor"] != 1:
            return False
        return True

    @cached_method
    def image_keys(self):
        return Set(tuple(self._witnesses))

    @cached_method
    def section(self):
        r"""A selected set-theoretic section of the finite character image.

        The retained Cayley witnesses supply the owned map
        `image_keys -> U(O(L))`, whose composition with the character map
        is the identity. Its values are live lattice isometries. No
        group-homomorphism law is claimed for the section.
        """
        keys = self.image_keys()
        return Sets().Mor(keys, self.supergroup)(
            lambda key: self._witnesses[keys(key)]
        )

    def subgroup_image_keys(self):
        return Set(
            tuple(key for key in self._witnesses if self._allowed(key))
        )

    def stabilizer_image_keys(self, stabilizer_generators):
        return frozenset(self.stabilizer_image_witnesses(stabilizer_generators))

    def stabilizer_image_witnesses(self, stabilizer_generators):
        r"""Return one live stabilizer element above every generated character image."""
        return self.supergroup.finite_image_lifts(
            self.image,
            generators=tuple(stabilizer_generators),
            multiply=self._multiply,
            image_bound=self._ambient_bound(),
        )

    def _gap_regular_model(self):
        r"""Return the right-regular libGAP model of the finite character image.

        The quotient keys remain the owned public representation.  GAP sees
        only their right-regular permutations, so its finite-group algorithms
        can compute subgroup and double-coset combinatorics without becoming
        part of the mathematical API.
        """
        keys = tuple(self.image_keys())
        positions = {key: position + 1 for position, key in enumerate(keys)}
        permutations = {}
        for key in keys:
            images = [
                positions[self._multiply(source, key)]
                for source in keys
            ]
            permutations[key] = libgap.PermList(images)
        group = libgap.Group(list(permutations.values()))
        if int(group.Size()) != len(keys):
            raise ArithmeticError(
                f"the right-regular permutation representation of the character image "
                f"of O({self.lattice}) has order {group.Size()} in GAP, but the image has "
                f"{len(keys)} elements"
            )
        return keys, permutations, group

    def right_coset_transversal(self):
        r"""Return one live lift for every right coset ``H r`` in the image.

        Here ``Q = rho(O(L))`` is the represented finite character image and
        ``H = rho(Gamma)`` is the image of the selected arithmetic subgroup.
        A right coset is therefore the subset ``H r = {h r : h in H}`` of
        ``Q``.  GAP computes representatives in the private regular-action
        model; before crossing them back, this method reconstructs those
        subsets with :meth:`_multiply` and verifies that they are disjoint and
        cover all of ``Q``.  The public result consists only of live lattice
        isometries lifting the chosen quotient representatives.
        """
        subgroup = self.subgroup_image_keys()
        keys, permutations, group = self._gap_regular_model()
        gap_subgroup = libgap.Subgroup(
            group,
            [permutations[key] for key in subgroup],
        )
        quotient_representatives = []
        for right_coset in libgap.RightCosets(group, gap_subgroup):
            gap_representative = right_coset.Representative()
            quotient_representative = next(
                (
                    key
                    for key in keys
                    if permutations[key] == gap_representative
                ),
                None,
            )
            if quotient_representative is None:
                raise ArithmeticError(
                    f"GAP returned the right-coset representative {gap_representative}, "
                    f"which is not the permutation of any element of the character image "
                    f"of O({self.lattice})"
                )
            quotient_representatives.append(quotient_representative)

        owned_cosets = tuple(
            frozenset(
                self._multiply(subgroup_element, representative)
                for subgroup_element in subgroup
            )
            for representative in quotient_representatives
        )
        if len(set(owned_cosets)) != len(owned_cosets):
            raise ArithmeticError(
                f"the right-coset representatives of the image of {self.subgroup} in the "
                f"character image of O({self.lattice}) are not a transversal: two of "
                f"them lie in the same coset"
            )
        covered = frozenset().union(*owned_cosets) if owned_cosets else frozenset()
        if Set(covered) != self.image_keys():
            raise ArithmeticError(
                f"the right cosets of the image of {self.subgroup} do not cover the "
                f"character image of O({self.lattice}): they cover {len(covered)} of its "
                f"elements"
            )
        return finite_ordered_set(
            tuple(
                self._witnesses[representative]
                for representative in quotient_representatives
            )
        )

    def splitting_isometries(self, stabilizer_generators):
        r"""Return one lift ``g`` per double coset ``Gamma g Stab`` of ``O(L)``.

        ``Stab`` is the stabilizer in ``G = O(L)`` of a point ``x`` of a
        ``G``-set, given by ``stabilizer_generators``, and ``Gamma`` is the
        selected subgroup.  The ``G``-orbit of ``x`` is ``G/Stab``, and its
        ``Gamma``-orbits are the double cosets ``Gamma \ G / Stab``: the
        points ``g x`` and ``g' x`` lie in one ``Gamma``-orbit exactly when
        ``g'`` lies in ``Gamma g Stab``.  As ``Gamma`` contains the kernel of
        the character map ``rho``, it is ``rho^{-1}(rho(Gamma))``, so
        ``Gamma g Stab = Gamma g' Stab`` exactly when ``rho(g)`` and
        ``rho(g')`` lie in one double coset ``rho(Gamma) q rho(Stab)`` of the
        finite image.  The returned lifts ``g`` therefore give one point
        ``g x`` in each ``Gamma``-orbit.  The order matters when the image is
        not abelian: a transversal of ``rho(Stab) \ Q / rho(Gamma)`` need not
        be one of ``rho(Gamma) \ Q / rho(Stab)``.
        """
        stabilizer = self.stabilizer_image_keys(stabilizer_generators)
        subgroup = self.subgroup_image_keys()
        keys, permutations, group = self._gap_regular_model()
        # GAP's DoubleCosets(G, U, V) lists the double cosets U g V.  The
        # key-to-permutation map is a homomorphism (GAP composes left to
        # right, and each key acts by right multiplication), so U is the
        # image of Gamma and V the image of the stabilizer.
        left = libgap.Subgroup(
            group,
            [permutations[key] for key in subgroup],
        )
        right = libgap.Subgroup(
            group,
            [permutations[key] for key in stabilizer],
        )
        representatives = []
        for double_coset in libgap.DoubleCosets(group, left, right):
            gap_representative = double_coset.Representative()
            quotient_representative = next(
                (
                    key
                    for key in keys
                    if permutations[key] == gap_representative
                ),
                None,
            )
            if quotient_representative is None:
                raise ArithmeticError(
                    f"GAP returned the double-coset representative {gap_representative}, "
                    f"which is not the permutation of any element of the character image "
                    f"of O({self.lattice})"
                )
            representatives.append(self._witnesses[quotient_representative])
        return finite_ordered_set(tuple(representatives))

    def witness_meets_subgroup(self, witness, stabilizer_generators) -> bool:
        return self.adjust_witness_into_subgroup(witness, stabilizer_generators) is not None

    def adjust_witness_into_subgroup(self, witness, target_stabilizer_generators):
        r"""Left-adjust ``witness`` by the target stabilizer until it lies in the subgroup.

        If ``witness(x)=y`` and ``t`` stabilizes ``y``, then ``t*witness`` still
        carries ``x`` to ``y``.  Thus the relevant finite-character condition
        is ``rho(t) rho(witness) in rho(Gamma)``.  Right multiplication by a
        target stabilizer would instead act on the source and is not the same
        transporter problem.
        """
        if witness in self.subgroup:
            return witness
        subgroup_keys = self.subgroup_image_keys()
        for stabilizer_key, stabilizer_witness in self.stabilizer_image_witnesses(
            target_stabilizer_generators
        ).items():
            candidate_key = self._multiply(stabilizer_key, self.image(witness))
            if candidate_key not in subgroup_keys:
                continue
            candidate = stabilizer_witness * witness
            if candidate not in self.subgroup:
                raise ArithmeticError(
                    f"the characters say {candidate} lies in {self.subgroup}, but the "
                    f"subgroup's defining predicate rejects it: the characters do not "
                    f"determine {self.subgroup}"
                )
            return candidate
        return None


_MISSING_ARITHMETIC_GENERATING_SET = (
    "Over an indefinite lattice L, O(L) is an infinite arithmetic group and no "
    "generating set of this subgroup is known.  The missing operation is a "
    "generating set for an arithmetic subgroup of O(L), which belongs in "
    "lattice_engines.py"
)


def _finite_supergroup_elements(subgroup):
    r"""Return the elements of a subgroup whose supergroup is a finite ``O(L)``.

    A predicate subgroup with no character data has no finite quotient of
    ``O(L)`` describing it, so the only thing that describes it is the group
    itself.  The listing runs through the enumeration of ``O(L)``, which is
    supplied for a definite lattice of finite rank over ``ZZ``, where ``O(L)``
    is finite (``lean-categories`` ``orthogonalGroup_finite``).  A definite
    lattice over ``QQ`` is a quadratic space whose ``O(V)`` is not finite in
    rank at least 2, so definiteness alone does not make the listing finite.
    """
    supergroup = subgroup.supergroup()
    lattice = supergroup.domain()
    assert lattice.is_definite(), (
        f"cannot list the elements of {subgroup}: it is cut out by a predicate that "
        f"is not a character kernel, so its elements must be listed inside O(L), "
        f"and {lattice} is not definite.  "
        + _MISSING_ARITHMETIC_GENERATING_SET
    )
    assert lattice.base_ring() is _owned_integers(), (
        f"cannot list the elements of {subgroup}: it is cut out by a predicate that "
        f"is not a character kernel, so its elements must be listed inside O(L), and "
        f"O(L) is enumerated for a definite lattice over ZZ, while {lattice} is over {lattice.base_ring()}"
    )
    return tuple(
        automorphism for automorphism in supergroup if automorphism in subgroup
    )


def _finite_subgroup_vector_orbit_representatives(subgroup, square):
    r"""Return one representative of each orbit of a listable subgroup."""
    lattice = subgroup.supergroup().domain()
    action = FiniteGSets(subgroup)(
        lattice.vectors_of_square(square),
        lambda automorphism, vector: automorphism(vector),
    )
    return finite_ordered_set(
        tuple(orbit.representative() for orbit in action.orbits())
    )


def _subgroup_vector_orbit_representatives(subgroup, square):
    if not subgroup.contains_character_kernel():
        return _finite_subgroup_vector_orbit_representatives(subgroup, square)
    quotient = OrthogonalCharacterQuotient(subgroup)
    orthogonal_group = subgroup.supergroup()
    lattice = orthogonal_group.domain()
    square = lattice.base_ring()(square)

    if square == lattice.base_ring().zero() and not lattice.is_definite():
        primitive_orbits = orthogonal_group.orbit_decomposition(
            lattice.primitive_isotropic_vectors()
        )
        primitive_representatives = []
        for representative in primitive_orbits.representatives():
            stabilizer = orthogonal_group.vector_stabilizer_generators(representative)
            primitive_representatives.extend(
                splitting(representative)
                for splitting in quotient.splitting_isometries(stabilizer)
            )
        primitive_representatives = tuple(primitive_representatives)
        zero = lattice.zero()
        if not primitive_representatives:
            return finite_ordered_set((zero,))
        orbit_count = len(primitive_representatives)

        def element_at(index):
            position = int(index)
            if position == 0:
                return zero
            content_position, orbit_position = divmod(position - 1, orbit_count)
            return lattice.scalar_multiple(
                lattice.base_ring()(content_position + 1),
                primitive_representatives[orbit_position],
            )

        def index_of(vector):
            if element_parent(vector) is not lattice:
                return None
            if vector == zero:
                return NN(0)
            if vector.q() != square:
                return None
            content = int(vector.content())
            primitive_part = vector.primitive_part()
            orbit_position = next(
                (
                    position
                    for position, representative in enumerate(primitive_representatives)
                    if primitive_part == representative
                ),
                None,
            )
            if orbit_position is None:
                return None
            return NN(1 + (content - 1) * orbit_count + orbit_position)

        return OrderedEnumeratedSets()(
            NN,
            element_at,
            index_of=index_of,
            name=f"Square-zero orbit representatives of {subgroup}",
        )

    def split_representatives():
        for representative in orthogonal_group.vector_orbit_representatives(square):
            stabilizer = orthogonal_group.vector_stabilizer_generators(representative)
            for splitting in quotient.splitting_isometries(stabilizer):
                yield splitting(representative)

    return finite_ordered_set(split_representatives())


def _subgroup_vector_equivalence_witness(subgroup, left, right):
    orthogonal_group = subgroup.supergroup()
    if not subgroup.contains_character_kernel():
        lattice = orthogonal_group.domain()
        source, target = lattice(left), lattice(right)
        return next(
            (
                automorphism
                for automorphism in _finite_supergroup_elements(subgroup)
                if automorphism(source) == target
            ),
            None,
        )
    witness = orthogonal_group.vector_equivalence_witness(left, right)
    if witness is None:
        return None
    stabilizer = orthogonal_group.vector_stabilizer_generators(right)
    return OrthogonalCharacterQuotient(subgroup).adjust_witness_into_subgroup(
        witness, stabilizer
    )


def _assert_isotropic_splitting_has_character_data(subgroup) -> None:
    r"""Assert that a subgroup splitting isotropic orbits carries character data.

    A primitive isotropic subobject of positive rank exists only in an
    indefinite lattice, so the route that reads a predicate subgroup by listing
    it inside a finite ``O(L)`` is never available here: that listing is finite
    only for a definite lattice, and a definite lattice has no isotropic
    vector.  Character data is therefore the only description of a subgroup
    that splits an isotropic orbit.
    """
    assert subgroup.contains_character_kernel(), (
        f"{subgroup} is cut out by a predicate that is not a character kernel, "
        "so no finite character quotient describes it, and the subgroup itself "
        "cannot be listed instead: that listing is finite only for a definite "
        "lattice, which has no isotropic vector.  "
        + _MISSING_ARITHMETIC_GENERATING_SET
    )


def _subgroup_isotropic_orbit_representatives(subgroup, rank, *, flag=False):
    _assert_isotropic_splitting_has_character_data(subgroup)
    quotient = OrthogonalCharacterQuotient(subgroup)
    orthogonal_group = subgroup.supergroup()
    representatives = []
    for representative in orthogonal_group.isotropic_orbit_representatives(
        rank, flag=flag
    ):
        stabilizer = orthogonal_group.isotropic_stabilizer_generators(
            representative, flag=flag
        )
        representatives.extend(
            splitting.transport_isotropic_object(representative)
            for splitting in quotient.splitting_isometries(stabilizer)
        )
    return finite_ordered_set(tuple(representatives))


def _subgroup_isotropic_equivalence_witness(subgroup, left, right, *, flag=False):
    _assert_isotropic_splitting_has_character_data(subgroup)
    orthogonal_group = subgroup.supergroup()
    witness = orthogonal_group.isotropic_equivalence_witness(
        left, right, flag=flag
    )
    if witness is None:
        return None
    stabilizer = orthogonal_group.isotropic_stabilizer_generators(
        right, flag=flag
    )
    return OrthogonalCharacterQuotient(subgroup).adjust_witness_into_subgroup(
        witness, stabilizer
    )


__all__ = ["OrthogonalCharacterQuotient"]
