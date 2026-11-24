r"""Finite character quotients controlling arithmetic-subgroup orbit splitting."""
from operator import index
from typing import NamedTuple

from sage.libs.gap.libgap import libgap
from sage.misc.cachefunc import cached_method
from sage.structure.element import parent as element_parent

from sage_extensions.categories._lattice import orbit_row_record_name
from sage_extensions.categories.group.g_sets import FiniteGSets
from sage_extensions.categories.group.groups import Subgroups
from sage_extensions.categories.sets.finite_ordered_sets import (
    OrderedEnumeratedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import finite_indexed_family
from sage_extensions.categories.rings.ring_foundation import _owned_integers
from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.set_categories import NN, Set, Sets
from sage_extensions.timing import stage, timed_stage


def _letters_in_owned_order(factor_groups, letters):
    r"""Read a GAP factorization word in the owned multiplication order.

    ``letters`` are signed generator indices from a GAP word preimage,
    a product in the GAP group's own law.  An engine that
    multiplies by the reversed law (permutation, word and automorphism
    engines act on the right, ``groups._law_reversed``) reverses the same
    letters when they are evaluated by the owned product.  The discriminant
    factor is the only nonabelian candidate among the character factors, so
    the first factor's law decides the flip; the uniform flip is exact only
    because every later factor is abelian, which this assert refuses to
    assume (the referee's residual finding).  A second nonabelian character
    factor would need the joint law, not two independent flips.
    """
    from sage_extensions.categories.group.groups import (
        _gap_model,
        _law_reversed,
    )

    assert all(
        bool(libgap.IsAbelian(_gap_model(group))) for _label, group in factor_groups[1:]
    ), (
        "a single letter flip is exact only when every character factor past the "
        "discriminant factor is abelian; re-derive the flip from the joint law instead"
    )
    if factor_groups and _law_reversed(factor_groups[0][1]):
        return letters[::-1]
    return letters


def _f2_rank(vectors, width):
    r"""F2-rank of a list of 0/1 vectors: Sage's maintained ``GF(2)`` matrix rank."""
    from sage.all import GF
    from sage.matrix.constructor import matrix

    if not vectors:
        return 0
    return matrix(GF(2), [[int(x) for x in v] for v in vectors]).rank()


NO_SPLIT = "NOSPLIT"
r"""The answer that an ambient line orbit does not split into more than one orbit."""

NO_SPLIT_BY_REFLECTION = "a reflection fixing the line changes the character"
r"""The witness of ``NO_SPLIT``: one integral reflection root, orthogonal to the
line's generator, lying in the subgroup, and changing the character.  It proves
``G = Gamma * Stab(line)`` outright -- Gritsenko--Hulek--Sankaran's criterion is
not used -- so it needs no hypothesis on the lattice."""

NO_SPLIT_BY_ZERO_CLASS = "the line's divided class is the zero class"
r"""The witness of ``NO_SPLIT``: the divided class is `0`, where the double
cosets are a single coset because the class stabilizer is the whole image."""

NO_SPLIT_BY_SIGN_PATTERNS = "the stabilizer's sign patterns span the sign space"
r"""The witness of ``NO_SPLIT``: the stabilizer's own exhibited elements present
every sign coset that ``ker rho`` realizes, so the character image of the
stabilizer is the whole preimage of the class stabilizer."""


class _NoSplit(str):
    r"""The answer that an ambient line orbit does not split, with the proof that said so.

    It compares equal to the plain string ``"NOSPLIT"``, which is the answer every
    consumer of this call tests for, and it carries the witness in ``reason`` --
    one of ``NO_SPLIT_BY_REFLECTION``, ``NO_SPLIT_BY_ZERO_CLASS`` and
    ``NO_SPLIT_BY_SIGN_PATTERNS``.  The three arguments are different: the first
    exhibits a single element, the second counts double cosets at the zero class,
    and the third spans a sign space; a run that reports only the answer cannot
    say which of them held, and they fail differently.
    """

    reason = ""

    def __new__(cls, reason):
        assert reason in (
            NO_SPLIT_BY_REFLECTION,
            NO_SPLIT_BY_ZERO_CLASS,
            NO_SPLIT_BY_SIGN_PATTERNS,
        ), f"a no-split answer carries one of this module's three witnesses, not {reason!r}"
        instance = super().__new__(cls, NO_SPLIT)
        instance.reason = reason
        return instance

    def _repr_(self):
        return f"{NO_SPLIT} ({self.reason})"


class _GapWordSection:
    r"""A GAP stabilizer-chain word section of a finitely generated group.

    ``gap_generators`` is a tuple of libgap elements, and ``parent`` the libgap
    group that contains them when it has a stabilizer chain of its own.  With a
    parent, the generated group is bound as ``Subgroup(parent, gens)`` and GAP
    reuses the parent's chain — building ``Group(gens)`` fresh instead pays a
    new stabilizer-chain construction whose cost at the Enriques discriminant
    image sizes runs over the memory guard — while parent reuse is the
    documented GAP mechanism for subgroups of a chained group.  Without a
    parent the fresh ``Group(gens)`` is used.

    An explicit free-group epimorphism returns a word in the supplied
    generator positions; ``letters_of`` reads that word as signed 1-based
    generator indices. Word preimages use GAP's homomorphism machinery
    rather than the shortest-word enumeration of ``Factorization``. This
    is the engine behind the generated-model reads of
    ``OrthogonalCharacterQuotient`` and behind
    ``LatticeIsometryMor.discriminant_lift``; the owning layers evaluate the
    letters in their own generators and verify the result against the requested
    image element, so an engine inconsistency surfaces as an ``ArithmeticError``,
    never as a wrong element.
    The words retain the supplied ordered family, including redundant
    generators, through the change of finite representation:

    >>> from sage.all import QQ, block_diagonal_matrix, diagonal_matrix, identity_matrix
    >>> from sage.matrix.constructor import matrix
    >>> rotation = matrix(QQ, [[0, 1], [-1, 1]])
    >>> reflection = matrix(QQ, [[0, 1], [1, 0]])
    >>> square_rotation = matrix(QQ, [[0, 1], [-1, 0]])
    >>> identity = identity_matrix(QQ, 2)
    >>> coupled = block_diagonal_matrix(reflection, rotation)
    >>> family = (
    ...     -identity_matrix(QQ, 4), coupled,
    ...     block_diagonal_matrix(-square_rotation, identity),
    ...     block_diagonal_matrix(reflection, identity),
    ...     block_diagonal_matrix(reflection, reflection),
    ...     identity_matrix(QQ, 4), -identity_matrix(QQ, 4),
    ...     block_diagonal_matrix(identity, -reflection),
    ...     diagonal_matrix(QQ, [-1, 1, -1, -1]),
    ...     diagonal_matrix(QQ, [1, 1, -1, -1]),
    ...     diagonal_matrix(QQ, [1, -1, -1, -1]),
    ...     block_diagonal_matrix(-reflection, identity), coupled,
    ...     block_diagonal_matrix(reflection, rotation.inverse()),
    ... )
    >>> section = _GapWordSection(tuple(libgap(g) for g in family))
    >>> section.order()
    96
    >>> evaluations = []
    >>> for point in libgap.AsList(section.permutation_group):
    ...     evaluated = identity_matrix(QQ, 4)
    ...     for letter in section.letters_of_permutation(point):
    ...         generator = family[abs(letter) - 1]
    ...         evaluated = evaluated * (generator if letter > 0 else generator.inverse())
    ...     evaluations.append(libgap.Image(section._to_permutation, libgap(evaluated)) == point)
    >>> all(evaluations)
    True
    """

    def __init__(self, gap_generators, parent=None) -> None:
        self._generators = list(gap_generators)
        self._parent = parent
        self._permutation_model = None
        self._word_epimorphism = None

    @property
    def gap_group(self):
        r"""The generated group: parent-bound when a chained parent is given."""
        if self._parent is not None:
            # GAP's Subgroup(parent, gens) checks membership and raises when a
            # generator lies outside the parent, so a wrong binding is loud.
            return libgap.Subgroup(self._parent, self._generators)
        return libgap.Group(self._generators)

    @property
    def permutation_group(self):
        r"""The faithful permutation model, built when letters are requested.

        Group orders use the parent-bound native group. Word preimages use
        this model together with the explicit epimorphism from the original
        ordered generator family, independently of the model's generators.

        With a parent, the model is the parent's own ``IsomorphismPermGroup``
        restricted to the generated subgroup (GAP reference 40.6,
        ``RestrictedMapping``). For a group of form automorphisms this is the
        action on the finite module, of degree at most its order: O^+_8(2)
        gets a model of degree 255 in under a second, where a fresh
        ``Group(gens)`` without the parent's filters does not finish within 1175 s
        on the same group.
        """
        if self._permutation_model is None:
            if self._parent is None:
                to_permutation = libgap.IsomorphismPermGroup(libgap.Group(self._generators))
                self._permutation_model = (to_permutation, libgap.Range(to_permutation))
            else:
                parent_model = libgap.IsomorphismPermGroup(self._parent)
                group = self.gap_group
                self._permutation_model = (
                    libgap.RestrictedMapping(parent_model, group),
                    libgap.Image(parent_model, group),
                )
        return self._permutation_model[1]

    @property
    def _to_permutation(self):
        if self._permutation_model is None:
            self.permutation_group
        return self._permutation_model[0]

    def order(self) -> int:
        return int(libgap.Order(self.gap_group))

    def letters_of(self, gap_element) -> tuple:
        r"""Signed generator indices whose word maps to ``gap_element``."""
        point = libgap.Image(self._to_permutation, gap_element)
        return self.letters_of_permutation(point)

    def letters_of_permutation(self, point) -> tuple:
        r"""Signed indices in the supplied family for a permutation image.

        GAP reference 39.5-1 constructs word preimages through an explicit
        free-group epimorphism. The permutation model can choose different
        generators, so its own factorization indices cannot name our family.
        https://gap-system.github.io/gap/doc/ref/chap39.html#X7E19F92284F6684E
        """
        if self._word_epimorphism is None:
            free = libgap.FreeGroup(len(self._generators))
            images = [libgap.Image(self._to_permutation, generator) for generator in self._generators]
            self._word_epimorphism = libgap.GroupHomomorphismByImages(
                free, self.permutation_group, libgap.GeneratorsOfGroup(free), images
            )
        word = libgap.PreImagesRepresentative(self._word_epimorphism, point)
        return tuple(int(index) for index in libgap.LetterRepAssocWord(word))


def _double_coset_adjustment(subgroup_permutation, stabilizer_permutation, coset_point, permutation_product):
    r"""One element of ``stabilizer_permutation`` inside ``subgroup_permutation * coset_point``, or ``None``.

    This is the coset question :meth:`OrthogonalCharacterQuotient.adjust_witness_into_subgroup`
    asks: an element ``x`` of the stabilizer image ``W`` with ``x`` in ``S * t``
    (``S`` the subgroup's character image, ``t`` the witness image) exists
    exactly when ``t`` lies in the product ``S * W``, because ``x = s t``
    reads ``t = s^-1 x`` with ``s^-1`` in ``S`` and ``x`` in ``W``.  Membership
    in a double coset of this shape is answered by GAP without listing it,
    while intersecting a group with a coset domain enumerates the coset,
    which has ``|S|`` elements.

    **A trivial ``S`` makes the double coset the subgroup ``W``.**  Then the
    question asked is ``W``'s own membership test: the coset point is the
    element asked for when it lies in ``W``, and there is none when it does
    not.  A nontrivial ``S`` asks the coset walk below, whose length is the
    index ``[S : S cap W]``.

    The exhibited element walks the right cosets of ``W`` under right
    multiplication by the generators of ``S`` and their inverses: ``t`` in
    ``S * W`` means ``W t^-1 = W s^-1`` for some ``s`` in ``S`` (from
    ``t = s w``), so the coset ``W t^-1`` lies on that walk, and the element
    ``s`` that reaches it satisfies ``s t`` in ``W`` -- the required ``x``.
    Each coset is keyed by its ``CanonicalRightCosetElement`` (two equal right
    cosets have equal canonical elements), so the
    walk visits every coset once and its length is the index
    ``[S : S cap W]``, never an enumeration of ``S``, of ``W`` or of the coset.
    """
    from sage.libs.gap.libgap import libgap

    one = libgap.One(permutation_product)
    if int(libgap.Size(subgroup_permutation)) == 1:
        # S is trivial, so S * 1 * W is the subgroup W: the element asked for is
        # coset_point itself when it lies in W, and nothing otherwise.
        return coset_point if bool(coset_point in stabilizer_permutation) else None
    if not bool(
        coset_point
        in libgap.DoubleCoset(subgroup_permutation, one, stabilizer_permutation)
    ):
        return None
    generators = list(libgap.GeneratorsOfGroup(subgroup_permutation))
    steps = [generator for generator in generators]
    steps.extend(generator ** -1 for generator in generators)
    base_key = str(
        libgap.CanonicalRightCosetElement(stabilizer_permutation, one)
    )
    needle_key = str(
        libgap.CanonicalRightCosetElement(stabilizer_permutation, coset_point ** -1)
    )
    reached = {base_key: one}
    frontier = [one]
    while needle_key not in reached:
        following = []
        for element in frontier:
            for step in steps:
                image = element * step
                key = str(
                    libgap.CanonicalRightCosetElement(stabilizer_permutation, image)
                )
                if key in reached:
                    continue
                reached[key] = image
                following.append(image)
        if not following:
            # The double coset above contains coset_point, so the coset
            # W coset_point^-1 is W s^-1 for the s that factors coset_point
            # over S * W: the walk must reach it.  Missing it means the
            # canonical keys do not identify the cosets GAP's DoubleCoset
            # membership decided on, which is an engine inconsistency rather
            # than a negative answer.
            raise ArithmeticError(
                "the double-coset membership admitted a coset element that the "
                "canonical coset walk did not reach: the coset keys and the "
                "double coset disagree on the same finite permutation group"
            )
        frontier = following
    return reached[needle_key] * coset_point


def _exact_stabilizer_span_key(quotient, representative, flag=False):
    r"""The span datum an exact stabilizer family is retained by.

    :meth:`OrthogonalCharacterQuotient.exact_isotropic_stabilizer_generators`
    depends on the representative through the spans of its terms alone -- its
    own span for a subobject, each term's for a flag -- so an
    equal-but-distinct copy of a representative has that representative's
    family, and two subobjects spanning different sublattices have their own.
    """
    from sage_extensions.categories.isotropic_orbits import _span_key

    terms = tuple(representative.terms()) if flag else (representative,)
    return (bool(flag), tuple(_span_key(term) for term in terms))


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
        # The transported objects the rows of this quotient record, keyed by
        # span, and the one ambient witness kept per pair of chain roots.
        self._transported_isotropic_objects = {}
        self._isotropic_root_bridges = {}

    @property
    def _witnesses(self):
        r"""One live lift above every image element, enumerated elementwise.

        Retained for the elementwise reads (``image_keys``, ``section``,
        ``subgroup_image_keys`` and ``_gap_regular_model``), whose contract is
        a listed image.  It realizes only when one of those reads asks for it;
        construction of the quotient stays free of it, and the generated-group
        reads (``image_order``, ``subgroup_image_order``,
        ``right_coset_transversal``, ``splitting_isometries``,
        ``adjust_witness_into_subgroup``, ``discriminant_image``) never need a
        listed image.
        """
        witnesses = self.__dict__.get("_witnesses_cache")
        if witnesses is None:
            witnesses = self._enumerate_image()
            self.__dict__["_witnesses_cache"] = witnesses
        return witnesses

    def image_space(self):
        r"""Return the owned product in which all character images live."""
        return self._image_space

    @cached_method
    def _character_product_construction(self):
        r"""The product in groups of the retained finite character codomains."""
        from sage_extensions.categories.group.groups import OwnedGroups

        factors = dict(self._model_factors())
        return OwnedGroups().product_construction(finite_indexed_family(
            self._image_labels, factors.__getitem__, name="Orthogonal character groups",
        ))

    @cached_method
    def character_representation(self):
        r"""The joint homomorphism from ``O(L)`` to its finite character product.

        Its actual image can be a proper subgroup of the product. Sign
        factors use the order-two group; the discriminant factor retains
        its owned orthogonal group.
        """
        construction = self._character_product_construction()
        diagram = construction.diagram()

        def leg(index):
            label = index.value()
            target = diagram(index)
            if label == "discriminant":
                return self.lattice.discriminant_representation()
            if label == "determinant":
                return self.supergroup.Mor(target).elementwise(
                    lambda isometry: self._c2_of_sign(self.lattice.base_ring()(isometry.determinant()))
                )
            return self.supergroup.Mor(target).elementwise(
                lambda isometry: target.one() if self._real_spinor_norm(isometry).is_one()
                else target.group_generators()[0]
            )

        cone = diagram.Cones().cone(self.supergroup, leg)
        return construction.factor(cone).apex_map()

    @cached_method
    def _character_target(self):
        r"""The subgroup of the character product whose preimage is Gamma."""
        construction = self._character_product_construction()
        product = construction.object()
        shape = construction.diagram().domain()
        projections = {
            label: construction.structure_morphism(shape(label)) for label in self._image_labels
        }

        def allowed(point):
            for label in self._image_labels:
                component = projections[label](point)
                if label == "discriminant":
                    if any(component not in target for target in self.discriminant_preimages):
                        return False
                elif component.is_one() is not True:
                    return False
            return True

        return product.predicate_subgroup(
            allowed, lambda: "the specified finite character conditions"
        )

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

    # ------------------------------------------------------------------
    # The generated model: the character image as a GAP-generated group.
    #
    # The elementwise views above list the finite image with one live lift
    # per element.  For arithmetic subgroups their image is far too large
    # for any listing (O(A_N) of the Enriques coinvariant lattice has order
    # ~5*10^13), so the image is instead realized *by generators*: the
    # character images of the ambient group's selected finite generating
    # family generate chi(O(L)); the subgroup's image is the meet of its
    # discriminant-preimage targets with the kernels of the sign characters
    # it intersects.  Both are subgroups of one direct product of the
    # character codomains, and GAP's stabilizer-chain methods then answer
    # orders, transversals, double cosets and coset memberships exactly.  A
    # ``_GapWordSection`` carries every returned quotient element back to a
    # word in the *ambient* generators, so every lift is a live lattice
    # isometry, checked once against the character map before it is
    # delivered.

    def _model_factors(self):
        r"""``(label, owned group)`` per character factor, in image order."""
        from sage_extensions.categories.group.groups import OwnedGroups

        factors = []
        for label in self._image_labels:
            if label == "discriminant":
                factors.append((label, self._discriminant_group))
            else:
                factors.append((label, OwnedGroups().C(2)))
        return tuple(factors)

    def _sign_factor_group(self):
        r"""The order-two cyclic group modelling every sign-character factor."""
        return next(
            group for label, group in self._model_factors() if label != "discriminant"
        )

    def _c2_of_sign(self, sign):
        r"""The ``{+-1}`` ring element as an element of the cyclic group of order two."""
        factor_group = self._sign_factor_group()
        ring = self.lattice.base_ring()
        if sign == ring.one():
            return factor_group.one()
        assert sign == -ring.one(), (
            f"the sign character of an isometry of {self.lattice} is +-1, but got {sign}"
        )
        return next(iter(factor_group.group_generators()))

    def _sign_of_c2(self, element):
        r"""The ``{+-1}`` reading of an element of the order-two factor group."""
        factor_group = self._sign_factor_group()
        ring = self.lattice.base_ring()
        return ring.one() if element == factor_group.one() else -ring.one()

    @cached_method
    def _gap_product(self):
        r"""The GAP direct product of the character codomains, with structure maps."""
        from sage_extensions.categories.group.groups import _gap_model

        factors = self._model_factors()
        models = tuple(_gap_model(group) for _label, group in factors)
        if len(models) == 1:
            product = models[0]
            return factors, product, (libgap.IdentityMapping(product),), (libgap.IdentityMapping(product),)
        product = libgap.DirectProduct(*models)
        embeddings = tuple(libgap.Embedding(product, position + 1) for position in range(len(models)))
        projections = tuple(libgap.Projection(product, position + 1) for position in range(len(models)))
        return factors, product, embeddings, projections

    def _ambient_generators(self):
        r"""The selected finite generating family of ``O(L)`` driving this quotient."""
        ambient = self.supergroup
        if not (
            ambient.has_selected_group_resolution()
            and ambient.has_selected_finite_group_generating_set()
        ):
            raise ValueError(
                f"the character image of {ambient} for {self.subgroup} cannot be realized as a "
                f"generated group: the ambient group retains no finite generating family; this "
                "quotient is explicitly generator-driven"
            )
        return tuple(ambient.group_generators())

    def _gap_of_key(self, key):
        r"""An owned character key as an element of the GAP direct product."""
        from sage_extensions.categories.group.groups import _element_to_engine

        factors, product, embeddings, _projections = self._gap_product()
        element = libgap.One(product)
        for position, (label, group) in enumerate(factors):
            if label == "discriminant":
                component = _element_to_engine(group, key[label])
            else:
                component = _element_to_engine(group, self._c2_of_sign(key[label]))
            element = element * libgap.Image(embeddings[position], component)
        return element

    def _key_of_gap(self, element):
        r"""An element of the GAP direct product as an owned character key."""
        from sage_extensions.categories.group.groups import _element_from_engine

        factors, _product, _embeddings, projections = self._gap_product()
        components = {}
        for position, (label, group) in enumerate(factors):
            component = libgap.Image(projections[position], element)
            owned = _element_from_engine(group, component)
            components[label] = owned if label == "discriminant" else self._sign_of_c2(owned)
        return self.image_space()(components.__getitem__)

    @cached_method
    def _image_section(self):
        r"""The generated character image ``chi(O(L))`` with its word section.

        The section's group is bound to the direct product's own engine
        (``Subgroup(product, images)``), reusing its stabilizer chain instead of
        building a fresh one for the generated subgroup.
        """
        generators = self._ambient_generators()
        images = tuple(self._gap_of_key(self.image(generator)) for generator in generators)
        return generators, images, _GapWordSection(images, parent=self._gap_product()[1])

    def _gap_image(self):
        r"""``chi(O(L))`` as a generated group of the direct product."""
        return self._image_section()[2].gap_group

    @cached_method
    def _character_permutation_factors(self):
        r"""The shared faithful factor models and their target embeddings.

        A character key can be mapped to this model without constructing its
        element in the enormous intermediate GAP direct product.  The model
        is shared with ``_character_permutation_model`` so the resulting
        permutations belong to exactly the same GAP parent.
        """
        from sage_extensions.categories.group.groups import _gap_model

        factors = self._model_factors()
        models = tuple(
            libgap.IsomorphismPermGroup(_gap_model(group)) for _label, group in factors
        )
        ranges = tuple(libgap.Range(model) for model in models)
        if len(ranges) == 1:
            target = ranges[0]
            embeddings = (libgap.IdentityMapping(target),)
        else:
            target = libgap.DirectProduct(*ranges)
            embeddings = tuple(
                libgap.Embedding(target, position + 1)
                for position in range(len(ranges))
            )
        return factors, models, target, embeddings

    def _permutation_of_key(self, key):
        r"""Faithful finite-character permutation, without GAP product membership.

        ``Image(Embedding(product,i), component)`` can require an expensive
        word problem in the 4.7e13-element discriminant direct product.
        Embed each component only *after* its small faithful permutation
        representation has been computed; the result is the same homomorphism
        as ``_character_permutation_model`` by construction.
        """
        from sage_extensions.categories.group.groups import _element_to_engine

        factors, models, target, embeddings = self._character_permutation_factors()
        result = libgap.One(target)
        for position, (label, group) in enumerate(factors):
            component = (
                _element_to_engine(group, key[label])
                if label == "discriminant"
                else _element_to_engine(group, self._c2_of_sign(key[label]))
            )
            result = result * libgap.Image(
                embeddings[position], libgap.Image(models[position], component)
            )
        return result

    @cached_method
    def _character_permutation_model(self):
        r"""A faithful permutation model of the whole character product, factor by factor.

        The character image lives in a direct product of finite codomains, and
        GAP's ``IsomorphismPermGroup`` on that product falls back to the regular
        representation, which does not return for an image of order ``4.7e13``.
        Each factor's own model is small -- the nonzero vectors of the ``F_2``
        module for the discriminant factor, two points for a sign -- so the
        product of those models, acting on the disjoint union of their moved
        points, is a faithful permutation model of the product, and a subgroup
        of it is computed there by the ordinary finite-group algorithms
        (``RightTransversal``, ``DoubleCosets``, ``IsNormal``).

        The returned homomorphism is defined by the product's own generators,
        each read one factor at a time through the product's projections and
        written back through the permutation product's embeddings.

        The constructor is the one that does not verify, because the image
        family is a composite of homomorphisms and needs no verification: for
        each character factor ``i`` the projection ``pi_i`` of the direct
        product onto its factor is a homomorphism and the embedding of a factor
        into the product is one, in the other direction (GAP Reference Manual,
        ``DirectProduct`` with ``Projection`` and ``Embedding``);
        ``IsomorphismPermGroup`` of that factor is an isomorphism onto its
        permutation image (GAP Reference Manual, ``IsomorphismPermGroup``).  A
        product of homomorphisms into subgroups that commute pairwise -- the
        embedded factors of a direct product do -- is a homomorphism, so
        ``g |-> prod_i emb_i(model_i(pi_i(g)))`` is a homomorphism, and it is
        injective because each ``model_i`` is.  The verifying constructor asks
        GAP to confirm exactly that from the source's stabilizer chain, and a
        direct product of a discriminant factor with a sign factor has no such
        chain that can be built at the orders this class meets, which is why
        the image family is proved here rather than checked.

        What this model is *not* is the elementwise route: ``Image`` of an
        element of the product sifts it through the source's stabilizer chain,
        which for this product is the word problem the model exists to avoid.
        An element of the finite image is therefore mapped by
        :meth:`_permutation_of_key`, factor by factor, and the callers that
        walk a row use that; this model is what names the shared target group.
        """
        from functools import reduce
        from operator import mul

        factors, product, _embeddings, projections = self._gap_product()
        _factors, models, target, target_embeddings = self._character_permutation_factors()
        ranges = tuple(libgap.Range(model) for model in models)
        generators = libgap.GeneratorsOfGroup(product)
        images = [
            reduce(
                mul,
                (
                    libgap.Image(
                        target_embeddings[position],
                        libgap.Image(
                            models[position],
                            libgap.Image(projections[position], generator),
                        ),
                    )
                    for position in range(len(ranges))
                ),
                libgap.One(target),
            )
            for generator in generators
        ]
        return libgap.GroupHomomorphismByImagesNC(
            product, target, generators, images
        )

    @cached_method
    def _gap_character_target(self):
        r"""The retained condition subgroup S of the full character product.

        Each selected sign factor is required to be the identity. The
        discriminant factor is the intersection of the supplied targets.
        Its embedding therefore already satisfies all the sign conditions.
        """
        from sage_extensions.categories.group.groups import _element_to_engine

        factors, product, embeddings, _projections = self._gap_product()
        if not self._has_discriminant:
            return libgap.TrivialSubgroup(product)
        position = next(index for index, (label, _group) in enumerate(factors) if label == "discriminant")
        pieces = tuple(
            libgap.Subgroup(product, [
                libgap.Image(embeddings[position], _element_to_engine(self._discriminant_group, generator))
                for generator in target.group_generators()
            ])
            for target in self.discriminant_preimages
        )
        condition = pieces[0]
        for piece in pieces[1:]:
            condition = libgap.Intersection(condition, piece)
        return condition

    @cached_method
    def _gap_subgroup(self):
        r"""``chi(self.subgroup)`` as a generated subgroup of the character image.

        ``self.subgroup`` is, by its complete character data, exactly
        ``chi^-1(S)`` for ``S`` the meet of the discriminant-preimage targets
        with the kernels of the sign characters it intersects; that meet is
        formed here inside the direct product, from the targets' retained
        generating families and one projection kernel per sign factor.
        """
        factors, _product, embeddings, projections = self._gap_product()
        image = self._gap_image()
        if self._has_discriminant and not (self.determinant_kernel and self.spinor_kernel):
            # Injectivity of pi_1 on Q cap S (proof at
            # _joint_discriminant_image_gap): Q cap S = {(a, +1) : a in T_tot},
            # so the joint subgroup is the embedding of T_tot, never a meet in
            # the product model.  Every embedded generator lies in Q because
            # T_tot lives in rho(K_0), and a lift of gamma has all signs +1.
            joint = self._joint_discriminant_image_gap()
            position = next(
                index for index, (label, _group) in enumerate(factors) if label == "discriminant"
            )
            embedded = [
                libgap.Image(embeddings[position], generator)
                for generator in libgap.GeneratorsOfGroup(joint)
            ]
            return libgap.Subgroup(image, embedded)
        return libgap.Intersection(image, self._gap_character_target())

    def image_order(self) -> int:
        r"""``|chi(O(L))|`` without any group built inside the direct product.

        ``|im chi| = |im rho| * 2^j`` where ``j`` is the F2-dimension of the
        sign patterns realized on ``ker rho``.  A sign product
        ``prod s_i^{e_i}`` is trivial on ``ker rho`` exactly when it descends
        to a homomorphism on ``im rho``; the descent of each of the ``2^m``
        sign products is tested by ``GroupHomomorphismByImages`` on the
        generators of ``im rho`` — all inside the ``O(A_L)`` engine, whose
        parent-bound chains are instant at the Enriques size, while the direct
        product's own chain is the bottleneck.  No image element is listed; no
        ambient-order substitution.

        With the discriminant factor alone the whole question is the order of
        ``rho(O(L))`` itself, and that one fact is asked of the lattice
        (:meth:`discriminant_image_order`), which answers it from the finite
        discriminant form when a theorem states the image and so asks for no
        generating family of ``O(L)``.
        """
        from itertools import product as _product_tuples

        from sage_extensions.categories.group.groups import (
            OwnedGroups,
            _element_to_engine,
            _gap_model,
        )

        sign_labels = [
            label for label in self._image_labels if label != "discriminant"
        ]
        if self._has_discriminant and not sign_labels:
            return self.discriminant_image_order()
        ambient = self._ambient_generators()
        if not self._has_discriminant:
            # Sign-only quotient: the joint image lives in C2^m itself; build it
            # there directly (at most 2^m elements, no engine chains needed).
            ring = self.lattice.base_ring()
            c2 = _gap_model(OwnedGroups().C(2))
            c2gen = list(libgap.GeneratorsOfGroup(c2))[0]
            m0 = len(sign_labels)
            product_engine = c2 if m0 == 1 else libgap.DirectProduct(*([c2] * m0))
            embeddings = (
                (libgap.IdentityMapping(c2),)
                if m0 == 1
                else tuple(libgap.Embedding(product_engine, k + 1) for k in range(m0))
            )
            tuples = []
            for generator in ambient:
                point = libgap.One(product_engine)
                for k, label in enumerate(sign_labels):
                    if label == "spinor":
                        value = self.lattice.O_plus().preimage_morphism()(generator).is_one()
                    else:
                        value = ring(generator.determinant()) == ring.one()
                    if not value:
                        point = point * libgap.Image(embeddings[k], c2gen)
                tuples.append(point)
            return int(libgap.Order(libgap.Group(tuples)))
        og = self._discriminant_group
        engine = _gap_model(og)
        rho_images = list(self.ambient_discriminant_images())
        im_rho = libgap.Subgroup(engine, rho_images)
        ambient_order = int(libgap.Order(im_rho))
        # sign value (+1/-1) of each ambient generator per sign factor
        ring = self.lattice.base_ring()
        factor_values = []
        for label in sign_labels:
            if label == "spinor":
                morphism = self.lattice.O_plus().preimage_morphism()
                values = [
                    1 if morphism(generator).is_one() else 0 for generator in ambient
                ]
            else:
                values = [
                    1 if ring(generator.determinant()) == ring.one() else 0
                    for generator in ambient
                ]
            factor_values.append(values)
        j, _labels = self._sign_descent_rank()
        return ambient_order * (1 << j)

    @cached_method
    def discriminant_image_order(self) -> int:
        r"""``|rho(O(L))|``: the finite group's own order when a theorem states the image.

        Nikulin, *Integral symmetric bilinear forms and some of their
        applications*, Math. USSR-Izv. 14 (1980), Theorem 3.6.3, makes ``rho``
        surjective for an even, indefinite, nondegenerate 2-elementary lattice,
        and then the order of the image is the order of ``O(A_L, q_L)`` itself,
        which the discriminant form supplies.  The certificate is the
        lattice's own
        (:meth:`sage_extensions.categories.lattices.Lattices.ParentMethods.discriminant_representation_is_surjective_by_theorem`),
        and it is what makes this order readable without a generating family of
        ``O(L)``.  Every other lattice keeps the generated-image route: ``rho``
        on the selected generating family of ``O(L)``, and the order of the
        subgroup those images generate.
        """
        if self.lattice.discriminant_representation_is_surjective_by_theorem() is True:
            return int(self._discriminant_group.cardinality())
        from sage_extensions.categories.group.groups import _gap_model

        engine = _gap_model(self._discriminant_group)
        images = list(self.ambient_discriminant_images())
        return int(libgap.Order(libgap.Subgroup(engine, images)))

    @cached_method
    def _joint_discriminant_image_gap(self):
        r"""``pi_1(Q cap S) = (cap_i H_i) cap rho(K_0)``, one meet inside ``O(A_L)``.

        Here ``S`` is the retained joint condition: every element of ``S`` has
        all sign components ``+1`` (the kernel of every sign projection is part
        of ``S`` by construction).  Hence ``pi_1`` is **injective** on
        ``Q cap S`` (each ``q`` is determined by its discriminant component),
        and

            ``pi_1(Q cap S) = T_tot := (cap_i H_i) cap rho(K_0)``,

        with ``K_0`` the **joint** sign kernel ``cap ker sn_j`` of the ambient
        group ``O(L)`` — no surjectivity, no containment of the targets, no
        separate marginals: ``K_0`` is one object, its rho-image is one
        subgroup pushed through ``rho`` from ``K_0``'s retained generating
        family, and the meet is one ``Intersection`` of small generated
        subgroups of ``O(A_L)``.  With more than one sign factor the joint
        ``K_0`` family is not formed here.  ``T_tot`` is contained in the meet of
        the preimage targets, so that meet is the whole answer whenever it is
        trivial -- the case of every kernel row whose discriminant target is
        trivial -- and the call refuses (``NotImplementedError``) only for a
        nontrivial meet together with two sign factors, where the product-model
        branch answers instead.
        """
        from sage_extensions.categories.group.groups import (
            _element_to_engine,
            _gap_model,
        )

        og_engine = _gap_model(self._discriminant_group)
        pieces = []
        for target in self.discriminant_preimages:
            pieces.append(
                libgap.Subgroup(
                    og_engine,
                    [
                        _element_to_engine(self._discriminant_group, generator)
                        for generator in target.group_generators()
                    ],
                )
            )
        if not pieces:
            raise ValueError(
                f"{self.subgroup} retains no discriminant preimage: its joint "
                "discriminant image is not characterized by its characters"
            )
        target_meet = libgap.Intersection(*pieces) if len(pieces) > 1 else pieces[0]
        # ``pi_1(Q cap S)`` is contained in the meet of the preimage targets, so a
        # trivial meet of the targets is already the whole answer and no sign kernel
        # can make it smaller.  Every kernel row whose preimage targets are trivial --
        # ``Otilde``, ``SOtilde``, ``Otilde^+`` and ``SOtilde^+`` -- is this case.
        if int(libgap.Size(target_meet)) == 1:
            return target_meet
        if not (self.determinant_kernel or self.spinor_kernel) and (
            self.lattice.discriminant_representation_is_surjective_by_theorem() is True
        ):
            # No sign factor: ``K_0`` is the whole of ``O(L)``, and ``rho`` is
            # onto by the lattice's certificate, so ``rho(K_0)`` is the whole of
            # ``O(A_L)`` and the meet with it changes nothing.  The targets'
            # meet is already ``T_tot``, and no ambient generator image is read
            # for it.
            return target_meet
        if self.determinant_kernel and self.spinor_kernel:
            raise NotImplementedError(
                "the joint intersection of two sign kernels inside O(L) is not "
                "generated in this route; the product-model "
                "computation is used instead"
            )
        lattice = self.lattice
        if self.spinor_kernel:
            kernel_selection = lattice.O_plus()
        elif self.determinant_kernel:
            kernel_selection = lattice.SO()
        else:
            kernel_selection = None
        if kernel_selection is None:
            # No sign factor: K_0 is the whole ambient group, and its
            # rho-image piece is exactly what carries rho(O(L)) into the meet
            # (dropping it reintroduces the refuted target-alone answer on
            # nonsurjective rho).  The images of that same generating family are
            # the quotient's cached sweep, so K_0 contributes no second one.
            kernel_images = list(self.ambient_discriminant_images())
        else:
            rho = lattice.discriminant_representation()
            kernel_images = [
                _element_to_engine(self._discriminant_group, rho(g))
                for g in kernel_selection.group_generators()
            ]
        pieces.append(libgap.Subgroup(og_engine, kernel_images))
        return libgap.Intersection(*pieces) if len(pieces) > 1 else pieces[0]

    @cached_method
    def _permutation_character_target(self):
        r"""The exact condition subgroup in the shared faithful permutation model.

        Every incidence adjustment uses the same target subgroup.  It is
        computed once, rather than once per witness (up to 569160 witnesses in
        a Coble kernel incidence row), and it is computed factor by factor: the
        condition subgroup of the character product is the meet of the retained
        discriminant-preimage targets, each of which is a subgroup of the
        discriminant factor, so its image is the meet of those targets' images
        under that factor's own model.  No element and no subgroup of the
        character product is built, which is what mapping the meet through the
        product's homomorphism would cost: ``Image`` of a subgroup sifts each
        of its generators through the source's stabilizer chain, and the direct
        product of the discriminant factor with a sign factor has order 9.4e13
        on ``T_Co``.
        """
        from sage_extensions.categories.group.groups import _element_to_engine

        factors, models, target, embeddings = self._character_permutation_factors()
        if not self._has_discriminant:
            return libgap.TrivialSubgroup(target)
        position = next(
            index for index, (label, _group) in enumerate(factors) if label == "discriminant"
        )
        pieces = tuple(
            libgap.Subgroup(
                target,
                [
                    libgap.Image(
                        embeddings[position],
                        libgap.Image(
                            models[position],
                            _element_to_engine(self._discriminant_group, generator),
                        ),
                    )
                    for generator in preimage.group_generators()
                ],
            )
            for preimage in self.discriminant_preimages
        )
        condition = pieces[0]
        for piece in pieces[1:]:
            condition = libgap.Intersection(condition, piece)
        return condition

    def subgroup_image_order(self) -> int:
        r"""``|chi(self.subgroup)|``, from the generated image; no image element is listed.

        The joint subgroup's discriminant image equals ``pi_1(Q cap S)`` (with
        an explicit proof at :meth:`_joint_discriminant_image_gap`), and
        ``pi_1|_{Q cap S}`` is injective, so ``|chi(self.subgroup)| = |T_tot|``
        and computing the joint subgroup in the full product model is never
        required here.  Sign-kernel-only data keeps the kernel route.
        """
        if self._has_discriminant and not (self.determinant_kernel and self.spinor_kernel):
            return int(libgap.Order(self._joint_discriminant_image_gap()))
        return int(libgap.Order(self._gap_subgroup()))

    def index(self) -> int:
        r"""``[O(L):self.subgroup] = |chi(O(L))| / |chi(self.subgroup)|``, exactly.

        The subgroup is ``chi^-1`` of its own character image, so the cosets
        of ``self.subgroup`` in ``O(L)`` are in bijection with the cosets of
        ``chi(self.subgroup)`` in ``chi(O(L))``; the quotient of the two GAP
        orders is that index, with divisibility checked.
        """
        image_order = self.image_order()
        subgroup_order = self.subgroup_image_order()
        index, remainder = divmod(image_order, subgroup_order)
        if remainder:
            raise ArithmeticError(
                f"the character image of {self.subgroup} has order {subgroup_order}, which does "
                f"not divide the ambient image order {image_order}: the retained character data "
                "are inconsistent with a subgroup of the character image"
            )
        return index

    def subgroup_generator_lifts(self):
        r"""Live isometries of ``self.subgroup`` above the generators of its discriminant image.

        Write ``Q = chi(O(L))`` and ``S`` for the retained joint condition;
        then ``chi(Gamma) = Q cap S`` (the subgroup is ``chi``'s full
        preimage, by the completeness of its character data), and the
        discriminant image is ``pi_1(Q cap S)``.  For ``gamma`` ranging over
        the selected group generators of that projected image, the point
        ``(gamma, 1, ...)`` lies in ``Q cap S``: it is the image of the
        discriminant factor because ``gamma`` was projected, and its sign
        components are all one.  The ambient word section therefore factors
        that point over the character images of the ambient generators, and
        the owned word evaluates to an isometry of ``L`` whose character
        image is ``(gamma, 1, ...)`` exactly, so it lies in ``Gamma``.  Every
        returned lift is checked against the character map
        (:meth:`_checked_lift`) and admitted by the subgroup's defining
        predicate; every discriminant morphism of a returned lift is a
        constructible, typed element of ``O(A_L)``, so the family realizes
        ``rho(Gamma)`` as ``<rho(lift_i)>``.  That generated subgroup is
        asserted to equal :meth:`discriminant_image` (equal order, every
        image generator lying in the image, every projected generator induced
        by a lift), as an object of ``Subgroups(O(A_L))`` of the same
        containing group.

        This is the presented generator family whose discriminator images a
        consumer can build itself; it contains no claim about generating
        ``Gamma`` itself (the stable kernel of ``O(L) -> O(A_L)`` inside the
        subgroup is needed for that: an open capability of the lattice-engine
        owner, named by ``_MISSING_ARITHMETIC_GENERATING_SET``).
        """
        if not self._has_discriminant:
            raise ValueError(
                f"{self.subgroup} retains no discriminant preimage: the discriminant "
                "image of its generators is not characterized by its characters"
            )
        from sage_extensions.categories.group.groups import (
            _element_to_engine,
            _gap_model,
        )

        image = self.discriminant_image()
        image_generators = tuple(image.group_generators())
        generators, _images, section = self._image_section()
        to_permutation = section._to_permutation
        ring = self.lattice.base_ring()
        lifts = []
        for gamma in image_generators:
            key = self.image_space()(
                lambda label: gamma if label == "discriminant" else ring.one()
            )
            point = libgap.Image(to_permutation, self._gap_of_key(key))
            letters = section.letters_of_permutation(point)
            lift = self._checked_lift(key, letters)
            if lift not in self.subgroup:
                raise ArithmeticError(
                    f"the character image of {lift} is {key}, which lies in the retained "
                    f"condition of {self.subgroup}, but the subgroup's defining predicate "
                    f"rejects it: the retained character data do not determine {self.subgroup}"
                )
            lifts.append(lift)
        # The warrant that generators have been lifted over the whole image:
        # group equality of the lifted images with the projected image, as
        # subgroups of O(A_L)'s engine model.
        engine_model = _gap_model(self._discriminant_group)
        lifted_images = [
            _element_to_engine(self._discriminant_group, lift.discriminant_morphism())
            for lift in lifts
        ]
        realized = libgap.Subgroup(engine_model, lifted_images)
        image_generators_gap = [
            _element_to_engine(self._discriminant_group, generator)
            for generator in image_generators
        ]
        if int(libgap.Order(realized)) != int(image.cardinality()) or any(
            candidate not in realized for candidate in image_generators_gap
        ):
            raise ArithmeticError(
                f"the lifts returned by {self.subgroup}.finite_character_quotient() generate a "
                "discriminant subgroup strictly smaller than the discriminant image: the "
                "retained condition does not generate what it projects to"
            )
        return finite_ordered_set(tuple(lifts))

    def _evaluate_letters(self, letters):
        r"""Signed generator indices evaluated in the ambient group's generators.

        The word section factors elements in the GAP group's own
        multiplication.  When the discriminant factor's engine multiplies by
        the reversed law (automorphism engines act on the right), the owned
        product reads the same letters in the opposite order; the sign
        factors are abelian and insensitive to the flip.  The check against
        the character map (:meth:`_checked_lift`) catches any remaining
        mismatch as an ``ArithmeticError``.
        """
        letters = _letters_in_owned_order(self._model_factors(), letters)
        generators, _images, _section = self._image_section()
        value = self.supergroup.one()
        for index in letters:
            value = value * (generators[index - 1] if index > 0 else ~generators[-index - 1])
        return value

    def _checked_lift(self, element, letters):
        r"""Evaluate ``letters`` and verify the lift carries the expected character image.

        The word section is maintained by GAP's stabilizer-chain machinery;
        this one character-map evaluation per delivered lift is the check that
        the chain agrees with the retained characters.  A disagreement is an
        engine inconsistency and raises ``ArithmeticError``; it never yields a
        silently wrong isometry.
        """
        live = self._evaluate_letters(letters)
        image = self.image(live)
        if image != element:
            raise ArithmeticError(
                f"the word-section lift of the character image {element} was checked against the "
                f"character map of {self.subgroup} and maps to {image}: the retained word section "
                "is inconsistent with the character map, so the lift cannot be trusted"
            )
        return live

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

    def _owned_coset_representative(self, point):
        r"""Transport a native coset representative to the owned product law.

        A reversed model takes an owned H*g*K coset to K*a*H.
        Inverting a representative of H*a*K gives the required K*a^-1*H.
        The same inversion transports native right cosets to owned right
        cosets. The later sign factors are abelian, so the first factor
        determines the joint convention, as for factorization words.
        """
        from sage_extensions.categories.group.groups import _law_reversed

        return point ** -1 if _law_reversed(self._model_factors()[0][1]) else point

    def right_coset_transversal(self):
        r"""Return one live lift for every right coset ``H r`` in the image.

        Here ``Q = rho(O(L))`` is the represented finite character image and
        ``H = rho(Gamma)`` is the image of the selected arithmetic subgroup.
        A right coset is therefore the subset ``H r = {h r : h in H}`` of
        ``Q``.  GAP computes the representatives in the generated model (the
        documented contract of ``RightTransversal``: exactly one element of
        ``Q`` from every right coset ``H\Q``), and each is carried back to a
        word in the ambient generators by the word section.  Before a lift is
        delivered it is checked against the character map itself
        (:meth:`_checked_lift`), and the count is checked against the group
        orders: a transversal of ``H\Q`` has exactly ``|Q|/|H|`` elements.
        """
        generators, _images, section = self._image_section()
        to_permutation = section._to_permutation
        permutation_image = section.permutation_group
        subgroup_permutation = libgap.Image(to_permutation, self._gap_subgroup())
        transversal = libgap.AsList(
            libgap.RightTransversal(permutation_image, subgroup_permutation)
        )
        if len(transversal) * self.subgroup_image_order() != self.image_order():
            raise ArithmeticError(
                f"GAP returned {len(transversal)} right-coset representatives of the image of "
                f"{self.subgroup} in the character image of O({self.lattice}), but the group "
                f"orders say the coset space has {self.index()} elements"
            )
        lifts = []
        for point in transversal:
            point = self._owned_coset_representative(point)
            letters = section.letters_of_permutation(point)
            key = self._key_of_gap(
                libgap.PreImagesRepresentative(to_permutation, point)
            )
            lifts.append(self._checked_lift(key, letters))
        return finite_ordered_set(tuple(lifts))

    @cached_method
    def _im_rho_engine_and_section(self):
        r"""``im rho`` inside the ``O(A_L)`` engine, with a parent-bound word section.

        The subgroup is bound to the FQF engine of ``O(A_L)`` (whose chains are
        instant at the Enriques size), and letters index the ambient ``O(L)``
        generators through ``rho``.

        ``rho`` is evaluated on *every* ambient generator, so this is the one
        computation of ``rho(O(L))`` the quotient schedules: the returned tuple
        is cached per subgroup (hence per lattice), and the callers that need the
        ambient generator images read them from here rather than sweeping the
        generating family again.  On ``T_Co`` one sweep is 26 s of
        ``discriminant_morphism`` constructions over 340 generators, which is
        why every lift of a row reads the images from here.
        """
        from sage_extensions.categories.group.groups import (
            _element_to_engine,
            _gap_model,
        )

        og = self._discriminant_group
        engine = _gap_model(og)
        ambient = self._ambient_generators()
        images = list(self.ambient_discriminant_images())
        subgroup = libgap.Subgroup(engine, images)
        section = _GapWordSection(images, parent=engine)
        return engine, subgroup, section, ambient

    @cached_method
    def ambient_discriminant_images(self):
        r"""``rho`` on the selected generating family of ``O(L)``, once per lattice.

        ``rho`` is the lattice's discriminant representation and the family is
        the ambient group's selected generating set; both are fixed objects of
        the lattice's own construction, so the images are a datum of the lattice,
        not of a row, a class or a call.  They are engine elements of the
        ``O(A_L)`` model, the form every caller here wants: the word section of
        :meth:`_im_rho_engine_and_section`, the sign-descent test, and the
        double-coset walk all consume them.

        Computing them is a ``discriminant_morphism`` construction per generator
        (340 generators on ``T_Co``; 26 s in one sweep),
        which is why this is memoized rather than recomputed where it is needed.
        """
        from sage_extensions.categories.group.groups import _element_to_engine

        og = self._discriminant_group
        rho = self.lattice.discriminant_representation()
        return tuple(
            _element_to_engine(og, rho(g)) for g in self._ambient_generators()
        )

    @cached_method
    def _sign_descent_rank(self):
        r"""``(j, sign_labels)``: F2-dimension of sign patterns realized on ``ker rho``.

        A sign product is trivial on ``ker rho`` exactly when it descends to a
        homomorphism on ``im rho``; each of the ``2^m`` products is tested by
        ``GroupHomomorphismByImages`` on the rho-images of the ambient
        generators, inside the ``O(A_L)`` engine only.

        The rho-images are read from :meth:`_im_rho_engine_and_section`, which is
        the quotient's single evaluation of ``rho`` on the ambient family; the
        rank itself is a property of the lattice and its characters, not of a
        row, so the pair is cached as well.
        """
        from itertools import product as _product_tuples

        from sage_extensions.categories.group.groups import (
            OwnedGroups,
            _gap_model,
        )

        sign_labels = [
            label for label in self._image_labels if label != "discriminant"
        ]
        m = len(sign_labels)
        if not self._has_discriminant or m == 0:
            return m, sign_labels
        _engine, im_rho, _section, ambient = self._im_rho_engine_and_section()
        rho_images = self.ambient_discriminant_images()
        ring = self.lattice.base_ring()
        # F2 encoding of signs: 0 = +1 (trivial), 1 = -1, so the sign of a
        # product is the F2 sum of the selected values.
        factor_values = []
        for label in sign_labels:
            if label == "spinor":
                morphism = self.lattice.O_plus().preimage_morphism()
                factor_values.append([0 if morphism(g).is_one() else 1 for g in ambient])
            else:
                factor_values.append(
                    [0 if ring(g.determinant()) == ring.one() else 1 for g in ambient]
                )
        c2 = _gap_model(OwnedGroups().C(2))
        c2gen = list(libgap.GeneratorsOfGroup(c2))[0]
        # The descended exponent set is an F2-subspace of C2^m (products of
        # descended characters descend), so its dimension is the F2-rank of the
        # collected vectors -- not the count of nonzero vectors, which would
        # overcount a 2-dimensional descent space by 3 and could drive j < 0.
        descended_vectors = []
        for exponents in _product_tuples((0, 1), repeat=m):
            if not any(exponents):
                continue
            combined = [
                sum(e * v for e, v in zip(exponents, col)) % 2
                for col in zip(*factor_values)
            ]
            target_images = [libgap.One(c2) if v == 0 else c2gen for v in combined]
            hom = libgap.GroupHomomorphismByImages(im_rho, c2, rho_images, target_images)
            if bool(hom):
                descended_vectors.append(exponents)
        rank = _f2_rank(descended_vectors, m)
        return m - rank, sign_labels

    def plane_odd_character_witness(self, representative):
        r"""Return an isometry fixing the plane whose character image is outside the subgroup's.

        For a primitive isotropic plane `P` and a subgroup `Gamma = chi^{-1}(A)` of
        finite index, the `Gamma`-orbits inside the `O(L)`-orbit of `P` are the double
        cosets `A \\ F / F_P` with `F = chi(O(L))`, `A = chi(Gamma)` and
        `F_P = chi(Stab_{O(L)}(P))` (D. Dutour Sikirić and K. Hulek,
        arXiv:2302.01679v2, Lemma 3.6, p. 22).  When `[F : A] = 2` and `A` is normal --
        the case of `Gamma = O^+ = ker(sn)`, whose image is the kernel of the real
        spinor norm in `F` -- *one* element of `F_P` outside `A` decides the count:
        then `A F_P = F`, so there is one double coset and the whole `O(L)`-orbit of
        `P` is a single `Gamma`-orbit.

        The element is searched over the plane actions of odd determinant, through
        :meth:`...PrimitiveIsotropicSubobjects.plane_block_lift` (Dutour Sikirić--Hulek,
        Theorem 4.9, printed pp. 33--34) with the quotient block prescribed as the
        identity, and every candidate is an integral isometry of the lattice by that
        construction.  The candidate is then asked whether it lies in the subgroup,
        which is the same question as whether its character image lies in `chi(Gamma)`,
        because `Gamma` is `chi^{-1}` of its own image: the decision is about `chi` --
        never about a determinant or a spinor norm read separately -- and it is one
        element's evaluation, not an enumeration of the image.

        ``None`` means no candidate action in the list admitted a lift outside `Gamma`;
        it is not a claim that `chi(Stab(P))` is contained in `chi(Gamma)`, and the
        caller must then keep the exact route (:func:`_plane_orbit_from_odd_stabilizer` keeps
        it by splitting with an ambient odd isometry instead, only after checking that
        the subgroup has index two).
        """
        from sage.matrix.constructor import matrix
        from sage.rings.integer_ring import ZZ as SageZZ

        if int(representative.module_rank()) != 2:
            raise ValueError(
                f"the plane witness is defined for a rank-two primitive isotropic "
                f"subobject, but {representative!r} has rank {int(representative.module_rank())}"
            )
        # The witness belongs to the plane, not to the basis it is presented in: the
        # block equations are solved in that basis, so a representative whose basis
        # has large coordinates makes them ill-conditioned and its block data
        # expensive to build.  The Hermite form of the two coefficient rows is
        # another basis of the same span -- the same plane, represented exactly --
        # and it is what the solver is given.  `primitive_isotropic_subobject`
        # re-checks primitivity and total isotropy on the new basis.
        lattice = self.lattice
        lattice_labels = tuple(lattice.module_generating_set())
        inclusion = representative.inclusion()
        coordinates = matrix(
            SageZZ,
            [
                [
                    int(inclusion(representative.module_generator(label)).to_vector()(basis_label))
                    for basis_label in lattice_labels
                ]
                for label in representative.module_generating_set()
            ],
        )
        normalized = coordinates.hermite_form()
        if normalized != coordinates:
            representative = lattice.primitive_isotropic_subobject(
                *(
                    lattice.linear_combination(
                        {
                            basis_label: lattice.base_ring()(int(entry))
                            for basis_label, entry in zip(lattice_labels, row)
                            if entry
                        }
                    )
                    for row in normalized.rows()
                )
            )
        # One element decides it: `Gamma` is the preimage `chi^{-1}(A)` of its own
        # character image, so `chi(g) in A` exactly when `g in Gamma`.  Asking the
        # subgroup itself is one character evaluation on one isometry; listing
        # `chi(Gamma)` first (`subgroup_image_keys`) builds one live lift per element
        # of the ambient image -- of order ~4.7*10^13 here -- and does not return.
        for action in (
            matrix(SageZZ, [[0, 1], [1, 0]]),
            matrix(SageZZ, [[1, 0], [0, -1]]),
            matrix(SageZZ, [[-1, 0], [0, 1]]),
            matrix(SageZZ, [[1, 1], [0, -1]]),
            matrix(SageZZ, [[1, 0], [1, -1]]),
            matrix(SageZZ, [[0, 1], [-1, 0]]),
            matrix(SageZZ, [[1, 1], [1, 0]]),
        ):
            lift = representative.plane_block_lift(action)
            if lift is None:
                continue
            if lift not in self.subgroup:
                return lift
        return None

    def line_stabilizer_sign_patterns(self, vector):
        r"""The sign patterns the exhibited elements of a line stabilizer realize.

        ``vector`` generates a primitive isotropic line \(x\).  Every element
        exhibited here fixes \(x\) as a set, and each contributes one pattern:
        the value of every sign character of this quotient on it, in the
        quotient's own label order, as a vector over \(\mathbb F_2\).

        * the negation \(-1\), which carries \(v\) to \(-v\);
        * the Levi part \(1_{\mathrm{plane}} + (-1)_{\mathrm{complement}}\) of
          the parabolic at \(x\), built by :func:`_split_signature_witness`
          (S. Zemel, arXiv:1902.08264v2, Proposition 1.10, p. 13);
        * the integral reflections in the basis vectors orthogonal to \(v\) and in
          their pairwise sums and differences.

        The square-\(2\) fibre of an indefinite lattice is infinite, so
        ``Lattices.vectors_of_square_and_divisibility`` is not enumerated here: the
        family is the finite list above, and a lattice whose patterns are not all
        presented by it is refused rather than searched further.

        **What these patterns bound.**  The line stabilizer's image can
        correlate its signs with its discriminant image -- an element with
        nontrivial discriminant image and nontrivial sign is a graph character
        -- so a sign product on such an element proves nothing about the signs
        realized inside \(\ker\rho\).  Where this quotient has a discriminant
        factor the family is therefore restricted to the elements whose
        discriminant image is trivial, and the patterns bound the sign space of
        \(\operatorname{Stab}_{O(L)}(x)\cap\ker\rho\); where it has none there
        is no \(\rho\) to restrict to, and the patterns bound the sign space of
        the whole stabilizer.  Either bound is from below: every pattern is
        exhibited by an element checked here -- an isometry carrying \(v\) to
        \(\pm v\), with the required discriminant image -- and a candidate that
        fails a check contributes nothing.

        The enumeration stops once the exhibited patterns span the sign space
        of \(\ker\rho\), which :meth:`_sign_descent_rank` measures, so the
        reflection enumeration is reached only where the negation and the Levi
        part do not already span it.
        """
        from itertools import chain, combinations

        lattice = self.lattice
        ring = lattice.base_ring()
        zero = ring.zero()
        sign_space_rank, sign_labels = self._sign_descent_rank()
        if not sign_labels or sign_space_rank == 0:
            return ()
        # The signs inside ker rho are the ones a discriminant factor cannot see.
        in_discriminant_kernel = self._has_discriminant
        rho = lattice.discriminant_representation() if in_discriminant_kernel else None
        trivial_discriminant = (
            self._discriminant_group.one() if in_discriminant_kernel else None
        )
        group = self.supergroup

        def pattern(element):
            values = []
            for label in sign_labels:
                if label == "spinor":
                    values.append(0 if self._real_spinor_norm(element).is_one() else 1)
                else:
                    values.append(0 if ring(element.determinant()) == ring.one() else 1)
            return tuple(values)

        def fixes_the_line(element) -> bool:
            image = element(vector)
            return image == vector or image == -vector

        def candidates():
            labels = tuple(lattice.module_generating_set())
            negation = group({label: -lattice.module_generator(label) for label in labels})
            assert negation * negation == group.one(), (
                f"the negation of {lattice} built from its module generators is not an "
                f"involution: it is not an element of the line stabilizer"
            )
            yield negation
            levi = _split_signature_witness(lattice, vector)
            if levi is not None:
                yield levi
            basis = tuple(lattice.module_generators())
            for root in chain(
                basis,
                (
                    first + sign * second
                    for first, second in combinations(basis, 2)
                    for sign in (1, -1)
                ),
            ):
                if root.q() == zero or lattice.b(root, vector) != zero:
                    continue
                if not root.is_integral_reflection_vector():
                    continue
                yield lattice.reflection(root)

        patterns = []
        for element in candidates():
            if not fixes_the_line(element):
                continue
            if in_discriminant_kernel and rho(element) != trivial_discriminant:
                continue
            patterns.append(pattern(element))
            if _f2_rank(patterns, len(sign_labels)) == sign_space_rank:
                break
        return tuple(patterns)

    def isotropic_line_stabilizer_image(self, representative):
        r"""Return the datum splitting the ambient line orbit, or ``None`` where it is not certified.

        For a single determinant or component character, an integral reflection
        fixing the line and changing that character proves ``G = Gamma Stab(line)``.
        Such a witness returns ``"NOSPLIT"`` for the whole ambient line orbit,
        independently of the number of integral hyperbolic planes.

        Let ``x = <v>`` be a primitive isotropic line, ``p = div(v)`` and ``c = [v/p]`` in
        ``A_L``.  The claim is ``rho(Stab_{O(L)}(x)) = Stab_{O(A_L)}(c)`` in the
        discriminant factor, and no integral stabilizer is needed for it.
        Eichler's criterion (Gritsenko--Hulek--Sankaran, Lemma 7.8, p. 503) says that, in a
        lattice with two orthogonal hyperbolic planes, the ``\widetilde{SO}(L)``-orbit of a
        primitive vector is decided by its length and its normalized discriminant class.
        The lattice the criterion is applied to is even as well as split by two
        orthogonal hyperbolic planes (Gritsenko--Hulek--Sankaran, Lemma 7.8, p. 503,
        with arXiv:1012.4155, eq. (49)); both halves of the hypothesis are the
        lattice's own and
        :meth:`sage_extensions.categories.lattices.Lattices.eichler_criterion_applies`
        decides them.

        **A lattice where the criterion does not apply is refused.**  What decides
        the ``O(L)``-orbit of a primitive isotropic ``v`` there is the isometry class
        of ``v^\perp/\mathbb{Z} v`` (Conway--Sloane, *Sphere Packings, Lattices and
        Groups*, ch. 16), so the call below returns ``None`` and the caller keeps
        its exact integral route.
        Let ``gamma`` belong to ``Stab_{O(A_L)}(c)`` and choose ``g`` in ``O(L)`` above it
        (the character representation is computed by this quotient, so such a lift exists).
        Then ``g(v)`` has the same length and the same normalized class ``c`` as ``v``, so by
        the criterion some ``k`` in ``\widetilde{SO}(L)`` takes ``g(v)`` to ``v``; then
        ``kg`` fixes ``v``, and ``kg`` has the same discriminant image ``gamma``.  That is
        surjectivity of the line stabilizer onto the finite class stabilizer.

        The sign characters are separate and are decided by the pattern space of the
        stabilizer's own exhibited elements
        (:meth:`line_stabilizer_sign_patterns`): the split of the ambient orbit needs
        ``chi(Stab(x))`` to be the whole preimage of the class stabilizer, so the
        patterns have to span the sign space that ``ker rho`` realizes
        (:meth:`_sign_descent_rank`), and a pattern space of smaller rank leaves a
        coset whose membership in ``chi(Stab(x))`` no exhibited element decides.  The
        caller then keeps its exact integral route rather than reading a smaller
        stabilizer image as the whole one.  Nothing below returns a partial
        discriminant image.
        """
        lattice = self.lattice
        inclusion = representative.inclusion()
        label = next(iter(representative.module_generating_set()))
        vector = inclusion(representative.module_generator(label))
        if not self._has_discriminant and self.determinant_kernel != self.spinor_kernel:
            # For one sign character chi, a stabilizer element with chi=-1
            # proves G = ker(chi) Stab(line), hence one double coset. This
            # certificate uses no Eichler transitivity hypothesis. The
            # reflection constructor verifies integrality; orthogonality
            # makes it fix the line pointwise. A missing witness supplies
            # no conclusion about the full stabilizer.
            from itertools import chain, combinations

            basis = tuple(lattice.module_generators())
            candidates = chain(
                basis,
                (first + sign * second for first, second in combinations(basis, 2) for sign in (1, -1)),
            )
            zero = lattice.base_ring().zero()
            for root in candidates:
                norm = root.q()
                if norm == zero or (self.spinor_kernel and norm < zero):
                    continue
                if lattice.b(root, vector) != zero or not root.is_integral_reflection_vector():
                    continue
                if lattice.reflection(root) not in self.subgroup:
                    return _NoSplit(NO_SPLIT_BY_REFLECTION)
        # The criterion's hypothesis is the lattice's own -- two orthogonal hyperbolic
        # planes and an even form (Gritsenko--Hulek--Sankaran, Lemma 7.8, p. 503) --
        # and ``Lattices.eichler_criterion_applies`` is where it is decided.
        # Without it the parabolic route below applies instead:
        # the split-signature witness -- an element of the stabilizer with trivial
        # discriminant image and real spinor norm ``-1``, the Levi part ``(1, -1)``
        # of Zemel's Proposition 1.10 (arXiv:1902.08264v2, p. 13) -- together with
        # the exact fibre index of the line's divided datum.  The complement's own
        # discriminant action is not that index: it is surjective on its own
        # discriminant group for the divisor-2 line of an even glued overlattice
        # whose complement isometries still do not extend integrally, so the
        # complement's surjectivity alone does not justify the index-one
        # assertion.  Both halves are computed, never asserted; a failure of
        # either returns ``None`` and the caller keeps its exact integral route.
        if not lattice.eichler_criterion_applies():
            if _split_signature_witness(lattice, vector) is None:
                return None
            # The class route below is the fibre of the datum map, and its fibre
            # size is the index in the exact ambient stabilizer image. A lower
            # bound equal to the target certifies index one. Otherwise this
            # test makes no claim about the index; keep the exact route.
            if general_image_certificate(self, representative) is None:
                return None
        discriminant_class = lattice.divided_discriminant_class(vector)
        zero_class = lattice.discriminant_group().zero()
        sign_space_rank, sign_labels = self._sign_descent_rank()
        # The sign cosets the stabilizer presents, as the patterns its exhibited
        # elements realize.  A pattern space of smaller rank than the one ker rho
        # realizes leaves a coset of the character image outside chi(Stab(x)), and
        # then neither the class-stabilizer equality below nor its sign factors are
        # certified: the caller keeps its exact integral route.
        if (
            _f2_rank(self.line_stabilizer_sign_patterns(vector), len(sign_labels))
            < sign_space_rank
        ):
            return None
        if discriminant_class == zero_class:
            # Double cosets Gamma \\ im rho / im rho are one coset: Stab_{im rho}(0)
            # is all of im rho, and Eichler's lifting argument takes place inside
            # that image.  The sign factors are presented by the stabilizer's own
            # exhibited patterns, which the test above has just certified to span
            # the sign space of ker rho, so no sign coset is left to lift.
            return _NoSplit(NO_SPLIT_BY_ZERO_CLASS)
        if not self._has_discriminant:
            # A sign-only character quotient has no im rho at all.  The same
            # principle applies: the stabilizer's patterns span every sign character,
            # so the signs it presents are the whole sign image of O(L) and the
            # ambient orbit does not split.
            return _NoSplit(NO_SPLIT_BY_SIGN_PATTERNS)
        finite_orthogonal = self._discriminant_group
        # An unoriented line is a *set*: its stabilizer may interchange v and -v, so
        # the discriminant image is the stabilizer of the class set {c, -c}, not of c
        # alone.  -1 is orthogonal to every form and negates both, so this is the set
        # stabilizer, and it is computed inside im rho -- the actual image of the
        # discriminant representation, which is exactly where the lifting argument is
        # allowed to work.  The set is stabilised by GAP's own elementwise action.
        from sage.libs.gap.libgap import libgap

        negative_class = -discriminant_class
        # The setwise stabilizer lives in im(rho), computed by GAP on the class set.
        # An unoriented line is a *set*: its stabilizer may interchange v and -v, so the
        # discriminant image is Stab({c, -c}) and -1 belongs to it whenever c != -c.
        # Computing inside im rho is what the lifting argument means: no element of
        # O(A_L) outside the retained image is promoted to a complete image.
        from sage.libs.gap.libgap import libgap

        class_points = libgap.Set(
            [
                finite_orthogonal._engine_abelian_element(discriminant_class),
                finite_orthogonal._engine_abelian_element(-discriminant_class),
            ]
        )
        engine, im_rho, _section, ambient = self._im_rho_engine_and_section()
        # Every sign coset is presented by the stabilizer: the patterns collected
        # above span the sign space of ker rho, so the double cosets inside im rho
        # are the double cosets of the whole character image and one lift per class
        # orbit carries each Gamma-orbit.
        return class_points, bool(sign_labels)

    def is_no_split(self, datum) -> bool:
        r"""Whether a line-splitting datum is this call's answer that nothing splits.

        ``isotropic_line_stabilizer_image`` answers either with the no-split
        value or with a class-point family; this asks which, so a consumer states
        the branch instead of comparing against a spelling of it.
        """
        return isinstance(datum, str) and str(datum) == NO_SPLIT

    def no_split_reasons(self) -> tuple:
        r"""The witnesses a no-split answer can name, in this module's order.

        The three are different arguments and fail differently -- a reflection
        exhibited, a zero divided class, a sign space spanned -- so a caller that
        reports one says which.  The names are this module's, and a reader asks
        here rather than restating them.
        """
        return (
            NO_SPLIT_BY_REFLECTION,
            NO_SPLIT_BY_ZERO_CLASS,
            NO_SPLIT_BY_SIGN_PATTERNS,
        )

    def splitting_isometries_from_line_class(self, class_points, stab_sign_flip):
        r"""Splitting lifts from the rho(Gamma)-orbits on the isotropic class pairs.

        ``class_points`` is the engine set of the normalized discriminant classes
        ``{c, -c}`` of the line's generator, built by
        :meth:`isotropic_line_stabilizer_image`.  Its setwise stabilizer inside
        ``im rho`` is the right-hand group of the double cosets that split the ambient
        line orbit, and those double cosets are computed as the ``rho(Gamma)``-orbits
        on the ``im rho``-orbit of the class set -- the orbit--double-coset bijection
        stated in :meth:`_iter_splitting_isometries_in_im_rho_from_image` -- so the
        stabilizer itself is never formed.

        This is the entry point of :meth:`isotropic_line_stabilizer_image`'s argument:
        it transports by representatives of the cosets of the class stabilizer instead
        of asking for the integral stabilizer's generators.  Every lift is still
        checked against the character map, and the checked image is what
        :meth:`_iter_splitting_isometries_in_im_rho_from_image` yields beside the lift;
        a caller that transports by the lift takes the lift alone.
        """
        return (
            lift
            for lift, _discriminant_image in self._iter_splitting_isometries_in_im_rho_from_image(
                (), stab_sign_flip, point=class_points
            )
        )

    @cached_method(key=_exact_stabilizer_span_key)
    def exact_isotropic_stabilizer_generators(self, representative, *, flag=False):
        r"""Return elements of ``H = Stab_{O(L)}(representative)`` whose image ``chi(H)`` is exact.

        The double-coset split of :meth:`splitting_isometries` is
        ``chi(Gamma) \ Q / chi(H)`` with ``Q = chi(O(L))``, so it needs the finite
        image ``chi(H)`` exactly; generators of a proper subgroup of ``H`` with a
        smaller image split one ``Gamma``-orbit into several.  The ambient
        family ``isotropic_stabilizer_generators`` need not generate ``H``: the
        plane-parabolic family is complete only when the lattice splits along the
        plane (``is_parabolic_complete``), which fails on ``U(2) + U(2) + A_2``.

        **Upper bound.**  Every term ``W`` of the representative (the subobject
        itself, or each term of a flag) has the divided class set
        ``D(W) = {[u/div(u)] : u primitive in W}`` in ``A_L``
        (:func:`_isotropic_divided_class_set`).  An element of ``H`` carries each
        term onto itself and primitive vectors to primitive vectors of the same
        divisibility, so ``rho(h)`` preserves every ``D(W)``.  Hence
        ``chi(H) <= U = {q in Q : pi_disc(q) D(W) = D(W) for every term W}``,
        and ``|U| = |Q| / |orbit of the data|`` by orbit--stabilizer.

        **Lower bound and closure.**  ``chi`` of the ambient family generates
        ``V <= chi(H)``.  While ``V != U``, each right-coset representative ``r``
        of ``V`` in ``U`` is lifted to ``g`` in ``O(L)`` by the word section
        (checked against the character map); ``g`` carries the representative to
        an object with the same divided data, and the ambient equivalence
        witness ``k`` with ``k(g x) = x`` gives ``k g`` in ``H``.  Its image is
        added to ``V``.  The loop ends when ``|V| = |U|``, which proves
        ``chi(H) = U`` with every generator an exhibited element of ``H``.  A
        pass that adds nothing certifies nothing, and raises: the divided data
        need not be a complete invariant, and no smaller image is guessed.

        **Retention.**  The family is a function of the spans of the
        representative's terms
        (:func:`_exact_stabilizer_span_key`), not of which copy of them a row
        holds, and a row asks for the same cusp's stabilizer once per object
        compared against it.  The datum is therefore retained here, at the
        operation that owns it, so every caller reads the one family its span
        has instead of recomputing it per question.
        """
        # Retain only line stabilizers: there are 527 line cusps on T_Co,
        # while there are 189720 plane cusps and 569160 flag certificates.
        # The same line is queried at every incident plane, and the exact
        # family is determined by its span.  Without this lookup the caller
        # reconstructs the ambient stabilizer and its enormous finite image
        # on every incidence edge, despite the retention contract above.
        key = (
            _exact_stabilizer_span_key(self, representative)
            if not flag and int(representative.module_rank()) == 1
            else None
        )
        families = self.__dict__.setdefault("_exact_isotropic_stabilizer_families", {})
        if key is not None and key in families:
            return families[key]

        # A line row retains the ambient isometry that placed every split
        # representative.  Its stabilizer is the conjugate of the source
        # stabilizer, including its entire character image.  Compute the
        # exact source family once instead of independently closing the
        # stabilizer image at every transported cusp (527 on T_Co).
        if not flag:
            from sage_extensions.categories.isotropic_orbits import _span_key

            root, transport = self.transported_from_root(representative)
            if _span_key(root) != _span_key(representative):
                inverse = ~transport
                result = tuple(
                    transport * generator * inverse
                    for generator in self.exact_isotropic_stabilizer_generators(root)
                )
                if key is not None:
                    families[key] = result
                return result

        ambient = self.supergroup
        # The stabilizer of a primitive isotropic plane is the parabolic subgroup at
        # it, and that subgroup's own construction hands out its elements from the
        # plane's block equations (Dutour Sikirić and Hulek, *Moduli of polarised
        # Enriques surfaces -- computational aspects*, arXiv:2302.01679v2,
        # Theorem 4.9, the block form of an isometry preserving an isotropic plane).
        # A flag is stabilized by the elements of its top term's parabolic that fix
        # its lower terms: ``Stab_{O(L)}(l <= P) = Stab_{O(L)}(P) cap Stab_{O(L)}(l)``,
        # by the definition of a stabilizer.  The marked-lattice family for a plane or
        # a flag reaches the same stabilizer by spelling each of its generators as a
        # word in the ambient generating family and multiplying the word out, which is
        # minutes a plane and more than that a flag at the Enriques rank.  The
        # parabolic family is taken in ``O(L)``, so an element of it need not lie in
        # the ambient group ``H`` is a subgroup of -- ``O^+``, ``Otilde``,
        # ``Otilde^+`` or a polarization group -- and only the elements that do are
        # elements of ``H``: each one is asked of the ambient group itself, whose
        # membership predicate is the character test defining it.  Either family is a
        # seed only: the closure below certifies ``chi(H)`` against the upper bound, so
        # what it needs from this line is elements of ``H``, not a family that
        # generates ``H``.
        if flag and int(representative.top().module_rank()) == 2:
            in_ambient = tuple(
                generator
                for generator in representative.top().parabolic_stabilizer_generators()
                if generator in ambient
                and all(term.stabilizes(generator) for term in representative.terms())
            )
        elif not flag and int(representative.module_rank()) == 2:
            in_ambient = tuple(
                generator
                for generator in representative.parabolic_stabilizer_generators()
                if generator in ambient
            )
        else:
            in_ambient = ()
        if in_ambient:
            generators = list(in_ambient)
        else:
            generators = list(ambient.isotropic_stabilizer_generators(representative, flag=flag))
        _section_generators, _images, section = self._image_section()
        image = self._gap_image()
        factors, product, _embeddings, projections = self._gap_product()
        if self._has_discriminant:
            position = next(
                index for index, (label, _group) in enumerate(factors) if label == "discriminant"
            )
            projection = libgap.RestrictedMapping(projections[position], image)
            discriminant_image = libgap.Image(projection)
            terms = tuple(representative.terms()) if flag else (representative,)
            finite_orthogonal = self._discriminant_group
            data = libgap(
                [
                    libgap.Set(
                        [
                            finite_orthogonal._engine_abelian_element(divided_class)
                            for divided_class in _isotropic_divided_class_set(self.lattice, term)
                        ]
                    )
                    for term in terms
                ]
            )
            termwise_action = libgap.function_factory(
                "function(x, g) return List(x, part -> Set(List(part, y -> ImageElm(g, y)))); end"
            )
            upper = libgap.PreImages(
                projection, libgap.Stabilizer(discriminant_image, data, termwise_action)
            )
        else:
            upper = image
        lower = libgap.Subgroup(
            product, [self._gap_of_key(self.image(generator)) for generator in generators]
        )
        if not bool(libgap.IsSubset(upper, lower)):
            raise ArithmeticError(
                f"an ambient stabilizer generator of {representative} moves its divided "
                f"discriminant data: it does not stabilize {representative}"
            )
        target = int(libgap.Size(upper))
        while int(libgap.Size(lower)) < target:
            before = int(libgap.Size(lower))
            for coset in libgap.AsList(libgap.RightTransversal(upper, lower)):
                # The transversal is a transversal of the subgroup this pass
                # started from, so it lists more cosets than the image still
                # misses: the pass ends the moment the image reaches its upper
                # bound, and every question asked after that point is one the
                # pass has already answered.
                if int(libgap.Size(lower)) == target:
                    break
                lift = self._checked_lift(self._key_of_gap(coset), section.letters_of(coset))
                moved = lift.transport_isotropic_object(representative)
                witness = ambient.isotropic_equivalence_witness(moved, representative, flag=flag)
                if witness is None:
                    raise ArithmeticError(
                        f"{lift} is an element of {ambient}, yet {ambient} does not carry "
                        f"{moved} back to {representative}"
                    )
                element = witness * lift
                key = self._gap_of_key(self.image(element))
                closed = libgap.ClosureGroup(lower, key)
                if int(libgap.Size(closed)) > int(libgap.Size(lower)):
                    generators.append(element)
                    lower = closed
            if int(libgap.Size(lower)) == before:
                raise ArithmeticError(
                    f"the stabilizer of {representative} in {ambient} has character image of "
                    f"order at least {before}, and the stabilizer of its divided discriminant "
                    f"data has order {target}; no exhibited stabilizer element closes the index "
                    f"{target // before}, so the exact image chi(Stab) is not certified"
                )
        result = tuple(generators)
        if key is not None:
            families[key] = result
        return result

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

        ``self.index() == 1`` means ``rho(Gamma) = Q = rho(O(L))``, and since
        ``Gamma`` is ``rho^{-1}`` of its own character image it is then all of
        ``O(L)``; so ``Gamma g Stab = O(L)`` for every ``g``, the double-coset
        space is a single point, and the identity lift is its representative.
        That is the same computation's answer read rather than enumerated,
        which matters because -- as
        :meth:`_iter_splitting_isometries_in_im_rho_from_image` records -- the
        enumeration does not return inside a group of order ``|Q|``.
        """
        if self.index() == 1:
            return finite_ordered_set((self.supergroup.one(),))
        # A stabilizer can correlate its signs with its discriminant image.
        # Joint conditions use the full joint image of every supplied generator.
        if self._has_discriminant and not (self.determinant_kernel or self.spinor_kernel):
            return self._splitting_isometries_in_im_rho(stabilizer_generators)
        # The image of the stabilizer is the subgroup generated by the
        # character images of its retained generators: chi is a homomorphism,
        # so chi(<S>) = <chi(S)>.  No element of the stabilizer's image is
        # listed.
        return self.splitting_isometries_from_stabilizer_image(
            tuple(self.image(generator) for generator in stabilizer_generators)
        )

    def splitting_isometries_from_stabilizer_image(self, stabilizer_image):
        r"""Return one lift per double coset from the stabilizer's *image*.

        This is :meth:`splitting_isometries` with its right-hand group supplied as
        the character image of the stabilizer instead of as generators of it.  The
        two are the same computation whenever the image is known --
        ``chi(<S>) = <chi(S)>`` -- and the image is what a double-coset split needs:
        ``Gamma \ G / Stab`` is the double coset space
        ``chi(Gamma) \ chi(G) / chi(Stab)`` because ``Gamma`` contains ``ker chi``
        (D. Dutour Sikirić and K. Hulek, arXiv:2302.01679v2, Lemma 3.6, p. 22: the
        quotient map pairs the double coset decompositions by ``(K, H)`` and by
        ``(K/U, H-bar)`` when ``U ⊂ K`` is normal).

        A caller that can certify ``chi(Stab)`` without asking for the stabilizer's
        generators -- as an isotropic line's stabilizer is certified by the Eichler
        and split-signature witnesses of :meth:`isotropic_line_stabilizer_image` --
        therefore gets the split without enumerating that stabilizer.
        """
        if self.index() == 1:
            return finite_ordered_set((self.supergroup.one(),))
        generators, _images, section = self._image_section()
        to_permutation = section._to_permutation
        permutation_image = section.permutation_group
        stabilizer_gap = libgap.Subgroup(
            self._gap_image(),
            [self._gap_of_key(key) for key in stabilizer_image],
        )
        # GAP's DoubleCosets(G, U, V) lists the double cosets U g V, so U is
        # the image of Gamma and V the image of the stabilizer.
        left = libgap.Image(to_permutation, self._gap_subgroup())
        right = libgap.Image(to_permutation, stabilizer_gap)
        representatives = []
        for double_coset in libgap.AsList(libgap.DoubleCosets(permutation_image, left, right)):
            point = self._owned_coset_representative(libgap.Representative(double_coset))
            letters = section.letters_of_permutation(point)
            key = self._key_of_gap(
                libgap.PreImagesRepresentative(to_permutation, point)
            )
            representatives.append(self._checked_lift(key, letters))
        return finite_ordered_set(tuple(representatives))

    def _splitting_isometries_in_im_rho(self, stabilizer_generators):
        r"""Double cosets computed inside ``im rho``: from retained integral generators."""
        return finite_ordered_set(
            tuple(
                lift
                for lift, _discriminant_image in self._iter_splitting_isometries_in_im_rho(
                    stabilizer_generators
                )
            )
        )

    def _iter_splitting_isometries_in_im_rho(self, stabilizer_generators, *, spellings=False):
        r"""Yield the lifts of :meth:`_splitting_isometries_in_im_rho` one at a time.

        ``spellings`` asks for each lift's own word beside it, as a
        :class:`_LiftSpelling`, which is what a registry keeps in place of the
        product (:meth:`register_isotropic_lift`).
        """
        from sage_extensions.categories.group.groups import _element_to_engine

        rho = self.lattice.discriminant_representation()
        discriminant_image_generators = tuple(
            _element_to_engine(self._discriminant_group, rho(s))
            for s in stabilizer_generators
        )
        return self._iter_splitting_isometries_in_im_rho_from_image(
            discriminant_image_generators,
            self._stabilizer_sign_flips(stabilizer_generators),
            spellings=spellings,
        )

    def _stabilizer_sign_flips(self, stabilizer_generators):
        r"""Whether the integral stabilizer takes a nontrivial value on a sign character.

        Only an element *inside ker rho* proves that a sign factor is already present in
        the stabilizer: a nontrivial sign with a nontrivial discriminant image can just
        be a graph character and must never stand for this boolean.
        """
        j, sign_labels = self._sign_descent_rank()
        ring = self.lattice.base_ring()
        rho = self.lattice.discriminant_representation()
        trivial_discriminant = self._discriminant_group.one()

        def sign_of(element, label):
            if label == "spinor":
                return self.lattice.O_plus().preimage_morphism()(element).is_one()
            return ring(element.determinant()) == ring.one()

        return any(
            rho(s) == trivial_discriminant and not sign_of(s, label)
            for s in stabilizer_generators
            for label in sign_labels
        )

    def _kernel_sign_flip(self, label):
        r"""One explicit element of ``ker rho`` whose ``label`` sign is nontrivial, or ``None``.

        ``label`` is a sign character -- ``"spinor"`` or ``"determinant"`` -- that does not
        descend to ``im rho``.  The double-coset machinery then needs one *witness* of that:
        an isometry with ``rho(g) = 1`` and the named sign ``-1``, which lifts the remaining
        sign coset.  It does **not** need a generating family of ``ker rho = Otilde(L)``, and
        for the Enriques period lattice no statement supplies one: Kneser's conditions fail
        there (``rank_2(N) = 2``) and ``N`` has no second hyperbolic plane, so
        Gritsenko--Hulek--Sankaran's generation statements do not reach it
        (arXiv:0810.1614v1, Proposition 5.6, p. 17), and ``Otilde(L)`` is an infinite
        arithmetic group with no selected resolution, so a witness of the named sign is
        what this route asks for.

        A witness, on the other hand, is a single reflection, and for ``N = U + U(2) +
        E8(-2)`` it is named on the page: *"the reflection with respect to a vector of length
        2 in the summand U of N gives an element in Otilde(N) with real spinor norm -1"* --
        D. Dutour Sikirić and K. Hulek, *Moduli of polarised Enriques surfaces --
        computational aspects*, J. London Math. Soc. 110 (2024), arXiv:2302.01679v2, p. 2,
        where that element is what makes ``Otilde^+(N)`` the index-two subgroup of
        ``Otilde(N)``.  In the multiplier convention of §1 of
        Gritsenko--Hulek--Sankaran the real spinor norm of a reflection is ``-(r,r)/2``, so a
        vector of square ``2`` has sign ``-1``.

        The candidates are the lattice's own basis and its pairwise sums and differences --
        finitely many, the same list :meth:`isotropic_line_stabilizer_image` searches for its
        sign witness -- and each is checked before it is returned: the reflection must be
        integral, its discriminant image must be trivial, and the named sign must be ``-1``.
        A lattice where none of them is a witness returns ``None``, and the caller refuses,
        which is the honest reading of "no witness was exhibited" rather than a guess.
        """
        from itertools import chain, combinations

        lattice = self.lattice
        ring = lattice.base_ring()
        rho = lattice.discriminant_representation()
        trivial_discriminant = self._discriminant_group.one()

        def sign_of(element):
            if label == "spinor":
                return lattice.O_plus().preimage_morphism()(element).is_one()
            return ring(element.determinant()) == ring.one()

        basis = tuple(lattice.module_generators())
        candidates = chain(
            basis,
            (
                first + sign * second
                for first, second in combinations(basis, 2)
                for sign in (1, -1)
            ),
        )
        for vector in candidates:
            if not vector.is_integral_reflection_vector():
                continue
            reflection = lattice.reflection(vector)
            if rho(reflection) != trivial_discriminant:
                continue
            if not sign_of(reflection):
                return reflection
        return None

    def _iter_splitting_isometries_in_im_rho_from_image(
        self, discriminant_image_generators, stab_sign_flip, *, point=None, spellings=False,
    ):
        r"""Yield the splitting lifts of
        :meth:`_iter_splitting_isometries_in_im_rho_from_image`, one ``(lift, image)`` at a time.

        ``image`` is the lift's discriminant image, the element of ``O(A_L)`` it
        acts by on ``A_L = L^\#/L``: the character map evaluated on the lift
        where the route evaluates it, and the same product of the split's own
        ``rho``-images where the route spells the lifts.

        ``discriminant_image_generators`` are *already lowered* to the engine by the
        caller (``_splitting_isometries_in_im_rho`` applies ``rho`` and the crossing
        once); applying ``rho`` here again would evaluate a group morphism on a raw
        engine element, which is exactly the boundary the owner never crosses.  A
        caller that retains a point of the finite ``im rho``-set whose stabilizer is
        the right-hand group of the double cosets passes it as ``point`` instead, and
        the double cosets are then computed as the ``rho(Gamma)``-orbits on the
        ``im rho``-orbit of that point.

        **The bijection, and its source.**  Let ``Q = im rho`` act transitively on the
        set ``X = Q . point``, let ``V = Stab_Q(point)`` be the setwise stabilizer of
        the point, and let ``U = rho(Gamma) <= Q``.  The orbit--coset bijection
        ``gV |-> g . point`` identifies the ``U``-orbits on the coset space ``Q / V``
        -- which are exactly the double cosets ``U \ Q / V`` -- with the ``U``-orbits
        on ``X`` (Betten--Fripertinger--Kerber, *Algebraic Combinatorics Via Finite
        Group Actions*, chapter "Double Cosets",
        ``mathe2.uni-bayreuth.de/frib/html/book/hyl00_14.html``: if ``G X`` is
        transitive and ``U <= G`` then, for each ``x`` in ``X``, the map
        ``U(gx) |-> UgG_x`` is a bijection from the orbits of ``U`` on ``X`` onto the
        double cosets ``U \ G / G_x``, so a transversal of the double cosets yields a
        transversal of the orbits of ``U``).  Computing the orbits on a few hundred
        points -- the isotropic classes of ``A_L``, or the images of the isotropic
        planes -- is what keeps this route inside its budget: the double-coset
        enumeration in a group of order ``|im rho|`` does not return at the Enriques
        size, while the orbit walk of the class set under the ``im rho``-generators
        terminates.  The walk doubles as a transversal of ``Q / V``: every reached
        point carries the engine element that carries the start to it, so the
        representative of each ``rho(Gamma)``-orbit is read off the walk itself.
        """
        from sage_extensions.categories.group.groups import _element_to_engine

        j, sign_labels = self._sign_descent_rank()
        engine, im_rho, _section, ambient = self._im_rho_engine_and_section()
        rho_images = self.ambient_discriminant_images()

        flip_element = None
        if j >= 1 and sign_labels and not stab_sign_flip:
            # The stabilizer leaves a sign coset to lift, and one explicit element of
            # ker rho exhibits it; Otilde(L)'s generating family is neither needed nor
            # known.  Where the stabilizer does present every sign coset there is
            # nothing to lift, and no kernel element is searched for.
            for label in sign_labels:
                flip_element = self._kernel_sign_flip(label)
                if flip_element is not None:
                    break
            if len(sign_labels) == 1 and flip_element is None:
                raise ValueError(
                    f"the stabilizer's discriminant image leaves a sign coset to lift, and no "
                    f"kernel element with nontrivial {sign_labels[0]} is available to lift it: "
                    "a plain sign predicate is not a substitute for a ker(rho) witness"
                )
        # Words in the rho-images of the ambient generators: the letters index
        # the ambient O(L) generators, and the orbit walk below records them
        # itself, so no free-group epimorphism is scheduled on this route.
        from sage_extensions.categories.group.groups import _law_reversed

        if point is not None:
            # The orbit route: the double cosets as the rho(Gamma)-orbits on the
            # im rho-orbit of the point, walked breadth-first with the im
            # rho-generators.  Every reached point carries the engine element that
            # carries the start to it, which is the transversal of Q / Stab(point)
            # the bijection above reads the double-coset representatives from.
            setwise_action = libgap.function_factory(
                "function(x, g) return Set(List(x, y -> ImageElm(g, y))); end"
            )
            identity = libgap.One(engine)
            orbit_points = [point]
            orbit_elements = [identity]
            keys = {str(point): 0}
            frontier = [(point, identity)]
            # Which product order carries the start to an image is a property of
            # the action's composition law, not of a generator and not of a
            # point: `setwise_action` rewrites the set by `ImageElm`, so the walk's
            # element must compose on the side that action reads, and that side is
            # the same for every generator.  It is therefore settled once, and not
            # on the first edge a generator reaches: the frontier starts at the
            # point itself, with the identity beside it, and at the identity both
            # orders carry the start to the same image -- an answer read off that
            # edge is an answer about nothing.  The order is settled on the first
            # edge whose element is not the identity; until one is reached, the
            # law's own order is used.
            right_order = None
            while frontier:
                following = []
                for reached_point, reached_element in frontier:
                    for generator in rho_images:
                        image = setwise_action(reached_point, generator)
                        marker = str(image)
                        if marker in keys:
                            continue
                        if right_order is None:
                            reached = reached_element * generator
                            if setwise_action(point, reached) == image:
                                if reached_point is not point:
                                    right_order = True
                            else:
                                reached = generator * reached_element
                                assert setwise_action(point, reached) == image, (
                                    "the orbit walk's transversal element does not carry the "
                                    "start to the reached point"
                                )
                                if reached_point is not point:
                                    right_order = False
                        elif right_order:
                            reached = reached_element * generator
                        else:
                            reached = generator * reached_element
                        keys[marker] = len(orbit_points)
                        orbit_points.append(image)
                        orbit_elements.append(reached)
                        following.append((image, reached))
                frontier = following
            # The rho(Gamma)-orbits on the orbit points: the double cosets.  One
            # representative element per orbit, read off the walk's own transversal:
            # the element that carries the start to the orbit's first-reached point.
            left_generators = list(
                libgap.GeneratorsOfGroup(self._joint_discriminant_image_gap())
            )
            representative_elements = []
            unvisited = list(range(len(orbit_points)))
            while unvisited:
                current = unvisited[0]
                representative_elements.append(orbit_elements[current])
                component = {current}
                walk = [current]
                while walk:
                    following = []
                    for position in walk:
                        for generator in left_generators:
                            marker = str(setwise_action(orbit_points[position], generator))
                            target = keys.get(marker)
                            if target is None or target in component:
                                continue
                            component.add(target)
                            following.append(target)
                    walk = following
                unvisited = [index for index in unvisited if index not in component]
            free = libgap.FreeGroup(len(rho_images))
            epi = libgap.GroupHomomorphismByImagesNC(
                free, im_rho, list(free.GeneratorsOfGroup()), rho_images
            )
            for element in representative_elements:
                word = libgap.PreImagesRepresentative(epi, element)
                letters = tuple(int(x) for x in libgap.LetterRepAssocWord(word))
                if _law_reversed(self._discriminant_group):
                    letters = letters[::-1]
                key_disc = self._discriminant_group._from_engine(element)
                value = self.supergroup.one()
                for index in letters:
                    value = value * (ambient[index - 1] if index > 0 else ~ambient[-index - 1])
                lifts = [value]
                if j >= 1 and len(sign_labels) == 1 and not stab_sign_flip and flip_element is not None:
                    lifts.append(flip_element * value)
                for position, lift in enumerate(lifts):
                    image_of_lift = self.image(lift)
                    if image_of_lift["discriminant"] != key_disc:
                        raise ArithmeticError(
                            "splitting lift's discriminant image disagrees with the word section"
                        )
                    if spellings:
                        yield (
                            lift,
                            image_of_lift["discriminant"],
                            _LiftSpelling(letters, flip_element if position else None),
                        )
                    else:
                        yield lift, image_of_lift["discriminant"]
            return
        # The coset-walk route, for callers that hold the integral stabilizer
        # generators (or their images) and no point of the finite set.  The
        # realization walks the right-coset action of im rho on
        # im rho / rho(Stab): the double cosets rho(Gamma) \ im rho / rho(Stab)
        # are the rho(Gamma)-orbits on that coset space (the orbit--coset
        # bijection above, with the reduction to the finite image from
        # Dutour Sikiric--Hulek, Lemma 3.6, printed p. 22), and the action is
        # GAP's own FactorCosetAction -- the native chain-based coset action,
        # the same machinery the double-coset enumeration rides -- rather than
        # the generic action on external coset objects.
        to_perm = libgap.IsomorphismPermGroup(im_rho)
        im_rho_perm = libgap.Range(to_perm)
        right = libgap.Subgroup(im_rho, list(discriminant_image_generators))
        right_perm = libgap.Image(to_perm, right)
        action = libgap.FactorCosetAction(im_rho_perm, right_perm)
        degree = int(libgap.Index(im_rho_perm, right_perm))
        # The base point of the action is the trivial coset: every generator
        # of the stabilizer image fixes it, and a walk that started elsewhere
        # would spell words for the wrong cosets.
        base = 1
        for generator in libgap.GeneratorsOfGroup(right_perm):
            if int(base ** libgap.Image(action, generator)) != base:
                raise ArithmeticError(
                    "the trivial coset is not the base point of the right-coset "
                    "action of im rho: the splitting walk cannot start there"
                )
        # A breadth-first walk over the action, on a small generating subset
        # of the rho-images: a lift to O(L) of an element of rho(O(L))
        # written as a word in the images of the ambient generators is the
        # same word in those generators (the homomorphism property of the
        # discriminant representation, rho(gh) = rho(g) rho(h)), and the walk
        # records, for every coset it reaches, the last generator image that
        # carried its parent there -- so each lift is spelled by one owned
        # product per coset along the walk's own tree, not by a per-coset
        # word problem, whose cost per double coset multiplies by the row's
        # 189720 double cosets, and not by a factorization whose
        # chain-with-words exceeds this VM's memory guard.
        perm_images = [libgap.Image(to_perm, image) for image in rho_images]
        small_indices = []
        closure = libgap.TrivialSubgroup(im_rho_perm)
        for index, image in enumerate(perm_images):
            if not bool(image in closure):
                small_indices.append(index)
                closure = libgap.ClosureGroup(closure, image)
        if int(libgap.Order(closure)) != int(libgap.Order(im_rho_perm)):
            raise ArithmeticError(
                "the rho-images of the ambient generators do not generate im rho: the "
                "word section of the splitting cannot be built"
            )
        edges = [libgap.Image(action, perm_images[index]) for index in small_indices]
        coset_walk = libgap.function_factory(
            """
function(edges, degree, base)
  local parents, edgenumbers, queue, head, p, i, q;
  parents := List([1..degree], i -> 0);
  edgenumbers := List([1..degree], i -> 0);
  queue := [base];
  head := 1;
  while head <= Length(queue) do
    p := queue[head];
    head := head + 1;
    for i in [1..Length(edges)] do
      q := p ^ edges[i];
      if q <> base and parents[q] = 0 then
        parents[q] := p;
        edgenumbers[q] := i;
        Add(queue, q);
      fi;
    od;
  od;
  if Length(queue) <> degree then
    Error("the coset walk did not reach every point of the coset action");
  fi;
  return [parents, edgenumbers, queue];
end
"""
        )
        walk_data = [entry for entry in coset_walk(edges, degree, base)]
        parents = [int(entry) for entry in walk_data[0]]
        edge_numbers = [int(entry) for entry in walk_data[1]]
        queue = [int(entry) for entry in walk_data[2]]
        # The rho(Gamma)-orbits on the coset space: the double cosets.  A
        # trivial left group -- the kernel rows, where rho(ker rho) and
        # rho(ker(rho, sn)) are both trivial -- leaves every coset its own
        # orbit, and an index-one left group is all of im rho, one orbit;
        # both are read rather than walked.  Otherwise GAP's Orbits
        # partitions the degree-many points under the left group's action
        # images.
        left = self._joint_discriminant_image_gap()
        if int(libgap.Order(left)) == 1 or int(
            libgap.Index(im_rho_perm, libgap.Image(to_perm, left))
        ) == 1:
            representative_points = queue
        else:
            orbit_reps = libgap.function_factory(
                """
function(action, to_perm, leftgens, degree)
  local edges;
  edges := List(leftgens, g -> Image(action, Image(to_perm, g)));
  return List(Orbits(Group(edges), [1..degree]), Representative);
end
"""
            )
            representative_points = [
                int(entry)
                for entry in orbit_reps(
                    action, to_perm, list(libgap.GeneratorsOfGroup(left)), degree
                )
            ]
        # The walk's own records are Python integers now; the GAP-side
        # action, its image group and the walk lists are released before the
        # lifts are spelled, so the row's footprint is the lifts and the
        # planes it returns, not the machinery that reached them.
        del walk_data, coset_walk, action, perm_images, closure, right_perm
        # Each representative's lift is spelled along the walk's own tree:
        # the value of a reached point is the generator image of its last
        # edge composed with the value of its parent, on the side the
        # engine's law dictates for owned elements -- the same letter
        # reversal the free-group route applies.  A point whose children
        # have all been spelled releases its value, so the tree the kernel
        # rows spell holds only the open frontier, not every lift at once.
        #
        # The lift's discriminant image is spelled beside it, one element of
        # ``O(A_L)`` per reached point: ``rho`` is a homomorphism of the owned
        # laws, so the very expression that composes the lift's generators
        # composes their ``rho``-images to ``rho`` of the lift.  The images are
        # the split's own evaluation of ``rho`` on the ambient family, crossed
        # back to the owned model once per walk generator rather than once per
        # lift -- reading ``rho`` off a lift's matrix is the row's dominant
        # per-plane cost, and a kernel row spells 189720 lifts.
        reversed_law = _law_reversed(self._discriminant_group)
        ambient_subset = [ambient[index] for index in small_indices]
        from sage_extensions.categories.group.groups import _element_from_engine

        image_subset = [
            _element_from_engine(self._discriminant_group, rho_images[index])
            for index in small_indices
        ]
        values = [None] * (degree + 1)
        values[base] = self.supergroup.one()
        images = [None] * (degree + 1)
        images[base] = self._discriminant_group.one()
        remaining_children = [0] * (degree + 1)
        for point in queue:
            remaining_children[parents[point - 1]] += 1
        # The word of every reached lift, in the left-to-right order of its
        # product, so that a consumer can keep the word instead of the product:
        # the product's integer entries grow with the plane, the word does not.
        # A point whose children have all been spelled releases its word with
        # its value, so the tree holds the open frontier and not every lift.
        spellings_of = [None] * (degree + 1)
        spellings_of[base] = ()
        checked = False
        flipped_checked = False
        for point in representative_points:
            chain = []
            walker = point
            while values[walker] is None:
                chain.append(walker)
                walker = parents[walker - 1]
            for reached in reversed(chain):
                edge = edge_numbers[reached - 1] - 1
                letter = small_indices[edge] + 1
                parent = parents[reached - 1]
                if reversed_law:
                    values[reached] = ambient_subset[edge] * values[parent]
                    images[reached] = image_subset[edge] * images[parent]
                    spellings_of[reached] = (letter,) + spellings_of[parent]
                else:
                    values[reached] = values[parent] * ambient_subset[edge]
                    images[reached] = images[parent] * image_subset[edge]
                    spellings_of[reached] = spellings_of[parent] + (letter,)
            value = values[point]
            if point != base and not checked:
                # The spelled element against the character map, on a lift whose
                # word is not empty: one evaluation of ``rho`` per row, so a
                # spelling that has left the homomorphism property is loud
                # rather than a row of lifts whose classes are carried by a
                # product that is not the lift's image.
                if images[point] != self.image(value)["discriminant"]:
                    raise ArithmeticError(
                        "the discriminant image spelled beside a tree-spelled lift is not "
                        "the lift's own image: the spelling does not compose the split's "
                        "rho-images to rho of the lift, so no lift of this row may be "
                        "registered with the element it was spelled with"
                    )
                if spellings and self._spelled_lift(_LiftSpelling(spellings_of[point], None)) != value:
                    # The word the registry is handed must spell the lift the row
                    # transports by, or every edge read from it is an edge at a
                    # plane the word does not carry onto.
                    raise ArithmeticError(
                        "the word spelled beside a tree-spelled lift does not spell the lift: "
                        "the row would register a word whose product carries its source plane "
                        "elsewhere, so no lift of this row may be registered by its word"
                    )
                checked = True
            flipped = (
                flip_element * value
                if j >= 1
                and len(sign_labels) == 1
                and not stab_sign_flip
                and flip_element is not None
                else None
            )
            if spellings and flipped is not None and not flipped_checked:
                # The sign sheet's lift is a word times the kernel witness, and
                # the word is what the registry keeps: checked once per row, on
                # the first plane of that sheet, so a registry of Otilde+ lifts
                # is never a registry of words whose witness sits on the wrong
                # side.  The branch runs only where a stabilizer leaves a sign
                # coset to lift and does not present it: no lattice a test can
                # afford does, and neither of T_Co's kernel rows does -- Otilde
                # has no sign character and Otilde+'s plane stabilizer presents
                # the coset (its parabolic family holds an element of trivial
                # discriminant image and spinor norm -1), so neither row spells
                # a sheet's word here.
                if (
                    self._spelled_lift(_LiftSpelling(spellings_of[point], flip_element))
                    != flipped
                ):
                    raise ArithmeticError(
                        "the word spelled beside a sign sheet's lift does not spell it: the "
                        "sheet's lift is its kernel witness times that word, and a registry "
                        "that keeps the word must keep the side the witness multiplies on"
                    )
                flipped_checked = True
            if spellings:
                yield value, images[point], _LiftSpelling(spellings_of[point], None)
            else:
                yield value, images[point]
            if flipped is not None:
                # The sign sheet's lift is a kernel element times the lift, so
                # it acts on the classes exactly as the lift does.
                if spellings:
                    yield flipped, images[point], _LiftSpelling(spellings_of[point], flip_element)
                else:
                    yield flipped, images[point]
            parent = parents[point - 1]
            if parent:
                remaining_children[parent] -= 1
                if not remaining_children[parent]:
                    values[parent] = None
                    images[parent] = None
                    spellings_of[parent] = None

    def witness_meets_subgroup(self, witness, stabilizer_generators) -> bool:
        return self.adjust_witness_into_subgroup(witness, stabilizer_generators) is not None

    def separates_witness_orbits(self, witness, left) -> bool:
        r"""Whether the finite character image proves no subgroup element carries ``left`` past ``witness``.

        ``witness`` is an isometry of the lattice carrying the primitive
        isotropic subobject ``left`` to ``witness(left)``.  The two lie in one
        subgroup orbit exactly when some subgroup element does the same
        carrying, and this method decides *separation* -- that no such element
        exists -- on the finite character image alone, before any integral
        stabilizer is computed (on the ``Gamma_{Co,2}`` row of ``T_Co``
        every failed transporter search of the cusp rows reached the exact
        stabilizer route through the absence of this decision, and the
        adjustment inside it was killed at the memory guard).

        * **Rank one.**  The divided discriminant class of a line is
          equivariant, ``[g v / div(g v)] = chi(g) [v / div(v)]`` -- an
          isometry preserves primitivity and divisibility, and the class of the
          image is the image of the class under the discriminant
          representation.  A subgroup element carrying ``left`` to
          ``witness(left)`` therefore maps the class set of ``left`` onto the
          class set of ``witness(left)``, so the two lines are separated as
          soon as their class sets lie in different orbits of ``rho(Gamma)``
          (the discriminant projection of the retained character condition,
          :meth:`_joint_discriminant_image_gap`).  The test walks that orbit:
          its length is the orbit of a class set, at most the number of
          isotropic classes of ``A_L``.  This direction needs no hypothesis:
          the equivariance holds for every isometry.

        * **Rank two, complete parabolic.**  A subgroup element ``gamma``
          carrying ``left`` to ``witness(left)`` factors as ``witness s`` with
          ``s`` in ``Stab(left)``, so ``chi(witness)`` lies in
          ``chi(Gamma) chi(Stab(left))``.  Where the plane's parabolic is
          certified complete (:meth:`is_parabolic_complete`) the
          image of its family is exactly ``chi(Stab(left))``, and the test is
          one double-coset membership -- answered by GAP without listing the
          double coset.  Both answers are exact for a quotient without sign
          factors; with sign factors a negative still separates (the
          discriminant component of a subgroup element lies in
          ``rho(Gamma)``), while a positive is inconclusive and the caller
          keeps its integral route.

        Any other case returns ``False``: no cheap decision is claimed, and the
        caller decides through its own exact route.
        """
        from sage.libs.gap.libgap import libgap

        if not self._has_discriminant:
            return False
        lattice = self.lattice
        rank = int(left.module_rank())
        if rank == 1:
            source = _isotropic_line_class_points(lattice, left)
            target = _isotropic_line_class_points(
                lattice, witness.transport_isotropic_object(left)
            )
            return str(target) not in self.isotropic_class_orbit(source)
        if rank == 2:
            from sage_extensions.categories.group.groups import (
                _element_to_engine,
                _gap_model,
            )

            stabilizer_image = self.parabolic_image_subgroup(left)
            if stabilizer_image is None:
                return False
            witness_image = _element_to_engine(
                self._discriminant_group, self.image(witness)["discriminant"]
            )
            engine = _gap_model(self._discriminant_group)
            return not bool(
                witness_image
                in libgap.DoubleCoset(
                    self._joint_discriminant_image_gap(),
                    libgap.One(engine),
                    stabilizer_image,
                )
            )
        return False

    @cached_method
    def isotropic_class_orbit(self, point):
        r"""The ``rho(Gamma)``-orbit of a set of discriminant classes, as a set of string keys.

        The equivariance of the divided class makes this orbit an invariant of
        the subgroup orbits (see :meth:`separates_witness_orbits`); the walk
        is bounded by the orbit of the class data, at most the number of
        classes of ``A_L``.

        The orbit of a class set is a function of that set's value, and a
        kernel row asks it at 569160 carried sets drawn from the 2048 classes
        of ``A_L``, so the answer is recorded by the rendering the walk's own
        frontier already compares by: a second ask at one class set is a
        dictionary hit rather than another walk over the image's generators.
        The recorded answer is a frozen set, because every ask at that class
        set is answered with the one walk.
        """
        from sage.libs.gap.libgap import libgap

        rendering = str(point)
        recorded = self.__dict__.setdefault("_isotropic_class_orbit_recorded", {})
        answer = recorded.get(rendering)
        if answer is not None:
            return answer
        generators = list(
            libgap.GeneratorsOfGroup(self._joint_discriminant_image_gap())
        )
        setwise_action = libgap.function_factory(
            "function(x, g) return Set(List(x, y -> ImageElm(g, y))); end"
        )
        seen = {rendering}
        frontier = [point]
        while frontier:
            following = []
            for reached in frontier:
                for generator in generators:
                    image = setwise_action(reached, generator)
                    marker = str(image)
                    if marker in seen:
                        continue
                    seen.add(marker)
                    following.append(image)
            frontier = following
        answer = frozenset(seen)
        recorded[rendering] = answer
        return answer

    def invariant_separates_isotropic_orbits(self, left, right) -> bool:
        r"""Whether the equivariant class data of two primitive isotropic subobjects lies in different ``rho(Gamma)``-orbits.

        A subgroup element carrying ``left`` to ``right`` maps the divided
        class data of ``left`` onto that of ``right`` -- the class of the
        image is the image of the class -- so differing orbits separate the
        subobjects before any isometry search runs (on ``T_Co`` the
        indefinite port's plane isometry between two word-transported
        representatives of the ``Gamma_{Co,2}`` row reaches PARI's ``qfauto``
        on the reduction of the transported basis, and the search is killed
        at the memory guard; the separated pairs never start it).  For a
        line the data is its divided class set; for a plane the divided
        classes of its two generators and their sum.
        """
        if not self._has_discriminant:
            return False
        lattice = self.lattice
        rank = int(left.module_rank())
        if rank == 1:
            source = _isotropic_line_class_points(lattice, left)
            target = _isotropic_line_class_points(lattice, right)
        elif rank == 2:
            from sage.libs.gap.libgap import libgap

            from sage_extensions.categories.isotropic_orbits import (
                _divided_discriminant_classes,
            )

            finite_orthogonal = lattice.discriminant_group().orthogonal_group()
            engine_set = lambda classes: libgap.Set(
                [
                    finite_orthogonal._engine_abelian_element(class_)
                    for class_ in classes
                ]
            )
            source = engine_set(_divided_discriminant_classes(lattice, left))
            target = engine_set(_divided_discriminant_classes(lattice, right))
        else:
            return False
        return str(target) not in self.isotropic_class_orbit(source)

    @cached_method
    def preserves_conjugation(self) -> bool:
        r"""Whether ``chi(Gamma)`` is normal in ``chi(O(L))``, and so ``Gamma`` in ``O(L)``.

        ``Gamma = chi^-1(S)`` for the retained ``S = chi(Gamma)``, and ``chi``
        maps ``O(L)`` onto its finite image.  A surjection carries normal
        subgroups to normal subgroups and carries the preimages of normal
        subgroups back, so ``g Gamma g^-1 = Gamma`` for every ``g`` in ``O(L)``
        exactly when ``S`` is normal in ``chi(O(L))``: one statement, and the
        finite one is what this call decides.

        Two cases need no normality computation -- a kernel, whose image is
        trivial, and the whole group, whose image is all of ``chi(O(L))``.
        Everything else is GAP's ``IsNormal`` of the retained image inside the
        generated finite image.  A *proper* image can be normal: the
        three-element rotation subgroup of the discriminant image of ``A_1^3``
        is ``A_3`` in ``S_3``, and the invariance holds for its preimage as it
        does for a kernel's.  It fails for a point stabilizer of a larger orbit,
        which is how a row split by the stabilizer of a point still answers
        ``False``.

        Where it is used: the incidence of a row transports one plane's
        covering to the row's other planes, which is a conjugation statement
        and nothing else.
        """
        if self.subgroup_image_order() == 1 or self.index() == 1:
            return True
        return bool(libgap.IsNormal(self._gap_image(), self._gap_subgroup()))

    def register_isotropic_covering(self, plane, source, lift, flags) -> None:
        r"""Record the row's covering of ``source``, computed once at ``plane``.

        ``source`` is the caller's token for the family the covering covers --
        the position of the ambient flag among the ambient flag row, in the
        incidence -- ``plane`` the plane the covering was computed at, and
        ``lift`` the registered isometry that carries ``source``'s plane onto
        it.  One record per ``source`` is the whole row: the covering of every
        other plane is this one carried there by the composite of the two
        planes' registered lifts (:meth:`transport_covering`), so nothing about
        the covering is recomputed at a second plane.

        The record retains the computed plane by span, as the transport
        registry does, so an equal-but-distinct copy of that plane finds it.
        """
        from sage_extensions.categories.isotropic_orbits import _span_key

        self.__dict__.setdefault("_isotropic_covering_registry", {})[source] = (
            plane,
            _span_key(plane),
            lift,
            tuple(flags),
        )

    def isotropic_covering_of(self, plane, source):
        r"""``(lift, flags)``: the covering ``source``'s row computed *at* ``plane``, or ``None``.

        A row computes one covering per source family and no more, so this
        answers at the plane that computation happened at -- matched by span,
        so an equal-but-distinct copy of the plane finds it -- and at no other
        plane of the row.  A plane the covering has not been carried to yet is
        :meth:`isotropic_covering_reference`'s to answer, and the carry itself
        is :meth:`transport_covering`'s.
        """
        from sage_extensions.categories.isotropic_orbits import _span_key

        record = self.__dict__.get("_isotropic_covering_registry", {}).get(source)
        if record is None or record[1] != _span_key(plane):
            return None
        return record[2], record[3]

    def isotropic_covering_reference(self, source):
        r"""``(plane, lift, flags)``: the row's covering of ``source``, wherever it was computed.

        ``plane`` is that plane, ``lift`` the registered isometry that carries
        ``source``'s plane onto it, and ``flags`` the covering computed there.
        The family at any other plane of the row is
        ``transport_covering(lift, flags, isotropic_lift_of(other))``: the
        composite of the two planes' registered lifts, which carries the
        computed plane onto the other.  ``None`` where the row has computed no
        covering for ``source``.
        """
        record = self.__dict__.get("_isotropic_covering_registry", {}).get(source)
        if record is None:
            return None
        return record[0], record[2], record[3]

    def transport_covering(self, reference_lift, flags, lift):
        r"""The covering ``flags``, carried to the plane that ``lift`` carries its plane to.

        Every term is transported by ``lift * ~reference_lift``, the composite
        that carries the reference plane onto the target.  Construction and
        registration are two phases: the carried family is one image of the
        given one, built as such, and each carried line's transport is then
        registered with the same element so the certificate of an edge at the
        target plane is read off the registry.
        """
        move = lift * ~reference_lift
        carried = tuple(move.transport_isotropic_object(flag) for flag in flags)
        for flag, image in zip(flags, carried, strict=True):
            self.register_isotropic_transport(
                image.terms()[0], flag.terms()[0], move
            )
        return carried

    def _spelled_lift(self, spelling):
        r"""The isometry a registered lift's word spells, in ``O(L)``.

        ``spelling.letters`` are signed one-based indices into the ambient
        generating family in left-to-right product order, so the product is the
        same expression the walk and the word section composed: one product a
        letter, and the sign sheet's witness on the left where the lift is that
        sheet's.  This is the read that costs what the lift costs; the registry
        keeps the word so that a row need not.
        """
        ambient = self._ambient_generators()
        value = self.supergroup.one()
        for letter in spelling.letters:
            value = value * (
                ambient[letter - 1] if letter > 0 else ~ambient[-letter - 1]
            )
        if spelling.flip is not None:
            value = spelling.flip * value
        return value

    def register_isotropic_lift(
        self, plane, lift, parabolic_generators, discriminant_image, *, spelling=None
    ):
        r"""Record one representative of the parabolic split and its certified data.

        ``lift`` carries the source plane, whose complete parabolic is generated
        by ``parabolic_generators``, to ``plane``.  Conjugating that family by
        the lift therefore generates the target plane's complete parabolic.
        Retaining both data lets every consumer use the split's own witness and
        certificate instead of repeating an integral isometry or parabolic
        completeness computation.

        ``discriminant_image`` is the lift's character image in the
        discriminant factor -- the element of ``O(A_L)`` the lift acts by on
        ``A_L = L^\#/L``.  It is the split's own evaluation of ``rho`` on the
        lift, retained so that a consumer of the row who wants the lift's action
        on the divided classes composes finite elements instead of inverting the
        lift's matrix to read its dual action: a lift of a kernel row is a word
        in the ambient generators whose entries grow with the plane it reaches,
        and the dual action of such a word is the row's dominant per-plane cost.
        Both the element and the inverse of it are one product in ``O(A_L)``,
        a group whose order is the lattice's finite datum rather than the
        plane's matrix.

        The record is keyed by the plane's span, not by the plane object: a
        split's consumers hold equal-but-distinct copies of a plane, and a
        kernel row registers 189720 of them, so the span key is what makes the
        lookup one dictionary hit instead of a scan of every plane recorded so
        far.

        ``spelling`` records the lift as the word that spells it instead of as
        the product: a row's lift is a word in the ambient generators whose
        product has integer entries that grow with the plane it reaches, so a
        registry of one product a plane costs 9.2 KiB an entry where the row
        starts and ~18 KB a plane in its tail bands, while the word is hundreds
        of bytes however far the walk has gone.  The product is spelled on
        demand (:meth:`_spelled_lift`), and the planes no consumer transports
        at are the row's 189720 -- the finite element beside the word is what a
        per-plane reader uses.
        """
        from sage_extensions.categories.isotropic_orbits import _span_key

        self.__dict__.setdefault("_isotropic_lift_registry", {})[
            _span_key(plane)
        ] = (
            lift if spelling is None else spelling,
            tuple(parabolic_generators),
            discriminant_image,
        )

    def _registered_isotropic_split(self, plane):
        r"""The registered ``(lift, source parabolic generators, image)`` of ``plane``."""
        from sage_extensions.categories.isotropic_orbits import _span_key

        return self._registered_isotropic_split_of_span(_span_key(plane))

    def _registered_isotropic_split_of_span(self, span):
        r"""The registered ``(lift, source parabolic generators, image)`` of the plane ``span`` names.

        The registry is keyed by the span (:meth:`register_isotropic_lift`), so a
        reader that already holds one -- a cusp of the row, whose whole datum is
        its span -- asks here.  The plane-keyed read above is this one with the
        span derived from the plane.  ``lift`` is spelled from the word the
        registry keeps when that is how the plane was registered: this is the
        read that costs the isometry, and a caller that wants only the finite
        element asks :meth:`registered_isotropic_discriminant_of_span`.
        """
        record = self.__dict__.get("_isotropic_lift_registry", {}).get(span)
        if record is None:
            return None
        retained, family, image = record
        lift = (
            self._spelled_lift(retained)
            if isinstance(retained, _LiftSpelling)
            else retained
        )
        return lift, family, image

    def registered_isotropic_discriminant_of_span(self, span):
        r"""The finite element of the plane ``span`` names, or ``None``.

        ``rho`` of the plane's registered lift -- what the divided-class
        incidence reads at every plane of a row, and all it reads: the integral
        lift is needed only where something is transported by it, so this read
        does not spell one.
        """
        record = self.__dict__.get("_isotropic_lift_registry", {}).get(span)
        return None if record is None else record[2]

    def registered_isotropic_lift_of_span(self, span):
        r"""``(lift, discriminant image)`` of the plane ``span`` names, or ``None``.

        A row keeps a span a cusp, not a plane (:class:`..._ArithmeticCuspEngine`),
        and the registry is keyed by the span, so this is the read that costs the
        span the caller holds and no construction.  Asking
        :meth:`registered_isotropic_lift` instead derives the same span from a
        plane, which means building the plane first: on ``T_{Co}``'s kernel plane
        row that is one constructed parent a plane for an answer the cusp already
        names its key by.
        """
        record = self._registered_isotropic_split_of_span(span)
        if record is None:
            return None
        return record[0], record[2]

    def release_isotropic_lift_of_span(self, span) -> None:
        r"""Drop the registered lift of the plane ``span`` names, which its walk has spent.

        A row's walk reads one plane's lift once -- the composite that carries
        the covering to it, and the finite element that acts on the classes --
        and never asks for it again: what it keeps of the plane afterwards is the
        span its cusp holds.  The registry is the row's largest per-plane term
        (``register_isotropic_lift`` retains a spelling a plane, and a spelled
        lift is the row's cost), so a walk that releases each entry as it passes
        the plane makes the row's resident set its records and its cusps rather
        than every lift it walked.

        The plane's lift is spent by that: a second walk of the same row finds
        no registered lift and says so where it looks for one.  The covering the
        walk read is already retained beside its own reference
        (:meth:`register_isotropic_covering`), so carrying to the *other* planes
        is unaffected.
        """
        self.__dict__.get("_isotropic_lift_registry", {}).pop(span, None)

    def registered_isotropic_lift(self, plane):
        r"""``(lift, discriminant image)``: a plane's registered lift and its finite element.

        The two are one datum: the lift carries the source plane onto ``plane``,
        and its discriminant image is what it does to the classes of
        ``A_L = L^\#/L``.  A consumer that needs both -- the building
        incidence's walk, whose every plane moves a covering's classes by the
        composite of two registered lifts -- reads them in one span-keyed
        lookup rather than two.  The matching is by span, so an equal-but-distinct
        copy of the plane finds it.  ``None`` where the plane carries no
        registered lift.
        """
        record = self._registered_isotropic_split(plane)
        if record is None:
            return None
        return record[0], record[2]

    def isotropic_lift_of(self, plane):
        r"""The registered lift of a plane, matched by span equality.

        Two registered planes lie in one subgroup orbit exactly when the
        composite of one lift with the inverse of the other lies in the
        subgroup -- a question the finite character image decides.  The
        matching is by span, so an equal-but-distinct object finds its lift too,
        and the lookup is one keyed dictionary hit rather than a scan of the
        registry.
        """
        record = self._registered_isotropic_split(plane)
        return None if record is None else record[0]

    def isotropic_lift_discriminant_of(self, plane):
        r"""The discriminant image of a plane's registered lift, or ``None``.

        This is the finite element ``rho(s_P)`` in ``O(A_L)``, registered beside
        the lift by :meth:`register_isotropic_lift`; it is the datum an action
        on the divided classes is composed from, and it is read without
        touching the lift's matrix -- and, where the registry keeps the lift's
        word, without spelling it.
        """
        from sage_extensions.categories.isotropic_orbits import _span_key

        record = self._registered_isotropic_split_of_span(_span_key(plane))
        return None if record is None else record[2]

    def register_isotropic_transport(self, subobject, source, transport):
        r"""Record the datum that ``transport`` carries ``source`` onto ``subobject``.

        A row transports a representative by an isometry it holds, so the
        object it produces and that isometry are one datum
        (:class:`TransportedIsotropicObject`), returned here and retained by the
        transported object's span: a row's consumers hold equal-but-distinct
        copies of an object, and a kernel row registers 189720 planes, so the
        span key is what makes the lookup one dictionary hit instead of a scan
        of every object recorded so far.

        The source is retained because the word starts there: a transport whose
        source is itself a transported object is the next step of one chain
        (:meth:`transported_from_root`).
        """
        from sage_extensions.categories.isotropic_orbits import (
            TransportedIsotropicObject,
            _span_key,
        )

        datum = TransportedIsotropicObject(subobject, source, transport)
        self._transported_isotropic_objects[_span_key(subobject)] = datum
        return datum

    def isotropic_transport_of(self, subobject):
        r"""The recorded transport datum of ``subobject``, or ``None``.

        The datum is one step of a chain, not necessarily a word from a row's
        base representative; :meth:`transported_from_root` reads the whole
        chain.
        """
        from sage_extensions.categories.isotropic_orbits import _span_key

        return self._transported_isotropic_objects.get(_span_key(subobject))

    def retained_isotropic_transport_count(self):
        r"""How many carried-object transport datums this quotient retains.

        The number is the size of ``_transported_isotropic_objects``: one datum
        for each transported isotropic object still registered, keyed by the
        object's span, each holding the object, the source it was carried from
        and the isometry that placed it (:meth:`register_isotropic_transport`).
        A row transports the representatives it produces and keeps the isometry
        that placed each one, because a transporter between two transported
        objects is the composite of their words rather than an isometry search
        (:meth:`transported_from_root`), so the registry holds the row's carried
        data until a consumer releases it (:meth:`release_isotropic_transports`).

        The quotient's other retained structures are not counted: the rows'
        coverings are in ``_isotropic_covering_registry``, the planes' lifts in
        ``_isotropic_lift_registry``, and the witnesses between chain roots in
        ``_isotropic_root_bridges``.
        """
        return cardinal(len(self._transported_isotropic_objects))

    def release_isotropic_transports(self, subobjects) -> None:
        r"""Drop the retained transport data of ``subobjects``, which the caller has spent.

        A datum is read while a consumer makes the object's certificate and not
        afterwards: a certificate retains its own transporter, so the registry's
        copy is a cache with the consumer's lifetime.  The incidence carries one
        covering to every plane of a 189720-plane row and reads the carried lines
        of a plane while it makes that plane's edge certificates; kept, those data
        are one isometry, one subobject and one span key per line per plane, which
        is growth with the plane count and not with the row.

        A released datum costs a later reader a bridge between roots it can still
        find (:meth:`isotropic_transport_between` searches for the one ambient
        witness between two roots and retains it), never a wrong transporter: the
        chain a reader walks is shortened, not falsified.
        """
        from sage_extensions.categories.isotropic_orbits import _span_key

        registry = self._transported_isotropic_objects
        for subobject in subobjects:
            registry.pop(_span_key(subobject), None)

    def transported_from_root(self, subobject):
        r"""``(root, g)`` with ``g`` carrying the registered chain's ``root`` onto ``subobject``.

        Reading the chain composes one word per recorded step, so it costs one
        product per step and no isometry search.  The order is the order the
        steps act: ``g`` already carries the current object onto ``subobject``,
        and the datum's word carries that object's source onto the current one,
        so for ``root --step--> current --g--> subobject`` the composite is
        ``g * step``.  An unregistered object is its own root with the identity.
        """
        from sage_extensions.categories.isotropic_orbits import _span_key

        g = self.supergroup.one()
        current = subobject
        seen = set()
        while True:
            datum = self.isotropic_transport_of(current)
            if datum is None:
                break
            key = _span_key(datum.subobject())
            if key in seen:
                break
            seen.add(key)
            g = g * datum.transport()
            current = datum.source()
        return current, g

    def isotropic_transport_between(self, left, right):
        r"""An isometry carrying ``left`` onto ``right`` from the recorded transports, or ``None``.

        ``left`` and ``right`` are carried from their roots by ``g_left`` and
        ``g_right``, so ``g_right * b * ~g_left`` carries ``left`` onto
        ``right`` for any ``b`` carrying the left root onto the right root.
        When the two objects lie in one registered row the roots coincide,
        ``b`` is the identity, and no isometry is searched for; the roots of
        two different rows are representatives the rows themselves hold, so the
        one ambient witness between them is computed once and retained.
        """
        from sage_extensions.categories.isotropic_orbits import _span_key

        left_root, left_element = self.transported_from_root(left)
        right_root, right_element = self.transported_from_root(right)
        if _span_key(left_root) == _span_key(right_root):
            return right_element * ~left_element
        pair = (_span_key(left_root), _span_key(right_root))
        if pair not in self._isotropic_root_bridges:
            self._isotropic_root_bridges[pair] = (
                self.supergroup.isotropic_equivalence_witness(left_root, right_root)
            )
        bridge = self._isotropic_root_bridges[pair]
        if bridge is None:
            return None
        return right_element * bridge * ~left_element

    @cached_method
    def certified_parabolic_generators(self, plane):
        r"""Generators certified to be the whole parabolic at ``plane``, or ``None``.

        A representative produced by the parabolic split inherits the source
        family's completeness by conjugation: if `sP_0=P` and the `g_i`
        generate `Stab(P_0)`, then the `s g_i s^{-1}` generate
        `Stab(P)=s Stab(P_0) s^{-1}`.  In particular no new completeness
        decision, and no automorphism group of a transported Levi quotient, is
        needed (that recomputation reaches PARI `qfauto` on `T_Co`).
        An unregistered plane uses its own block-construction certificate.
        """
        record = self._registered_isotropic_split(plane)
        if record is not None:
            lift, source_family, _discriminant_image = record
            return tuple(lift * generator * ~lift for generator in source_family)
        if plane.is_parabolic_complete() is not True:
            return None
        return tuple(plane.parabolic_stabilizer_generators())

    def plane_class_index(self, plane):
        r"""``(J, |Stab_{O(q)}(J)|, |rho(Stab_Gamma(P))|, their quotient)`` at one plane.

        ``J = [P/2]`` is the order-four totally isotropic subgroup of ``A_L``
        that the plane's divided classes span
        (:func:`...isotropic_orbits._divided_discriminant_classes`), and the
        quantity the plane rows of ``T_Co`` are indexed by is

        .. math:: [\mathrm{Stab}_{O(q)}(J) : \rho(\mathrm{Stab}_\Gamma(P))],

        the plane analogue of the line index
        ``[Stab_{O(q)}(v̄) : ρ(Stab_Γ(v))]``.

        The right-hand order is read in the finite image: ``U = Pi cap ker chi``
        is normal in ``Pi`` and lies in ``Gamma`` because the subgroup is a
        preimage, so ``Pi -> Pi/U`` is ``chi`` on ``Pi`` and
        ``chi(Stab_Gamma(P)) = chi(Gamma) cap chi(Pi)`` (D. Dutour Sikirić and
        K. Hulek, arXiv:2302.01679v2, Lemma 3.6, printed p. 22).  That meet is
        taken in the faithful permutation model, from the certified parabolic's
        own character keys and the quotient's retained condition subgroup -- the
        two groups the covering is computed from.  The left-hand order is the
        stabilizer of the class set in ``O(q)``, asked of the finite group's own
        action on the classes of ``A_L``.

        Both orders and the quotient are returned, and nothing here decides what
        the quotient should be: a caller compares it with the value a page
        states, and a disagreement is a defect filed on research.
        """
        from sage.libs.gap.libgap import libgap
        from sage_extensions.categories.isotropic_orbits import (
            _divided_discriminant_classes,
        )

        family = self.certified_parabolic_generators(plane)
        if not family:
            raise ValueError(
                f"the plane {plane} carries no certified parabolic in {self.subgroup}, so "
                f"rho(Stab_Gamma(P)) cannot be read and the plane class index is not defined here"
            )
        _factors, _models, permutation_target, _embeddings = (
            self._character_permutation_factors()
        )
        permutations = tuple(
            self._permutation_of_key(self.image(generator)) for generator in family
        )
        parabolic = libgap.Subgroup(permutation_target, permutations)
        image_order = int(
            libgap.Size(
                libgap.Intersection(self._permutation_character_target(), parabolic)
            )
        )
        classes = frozenset(
            _divided_discriminant_classes(self.lattice, plane)
        )
        stabilizer_order = int(self._discriminant_group.stabilizer_of_classes(classes).cardinality())
        index, remainder = divmod(stabilizer_order, image_order)
        if remainder:
            raise ArithmeticError(
                f"the image of the parabolic at {plane} has order {image_order}, which does not "
                f"divide the order {stabilizer_order} of the stabilizer of its class set J: the "
                f"retained character data are inconsistent with a subgroup of O(q)"
            )
        return classes, stabilizer_order, image_order, index

    @cached_method
    def parabolic_image_subgroup(self, plane):
        r"""The discriminant image of a complete plane's parabolic, as a GAP subgroup of ``O(A_L)``.

        The family of :meth:`certified_parabolic_generators` generates the
        plane's stabilizer, so the image of that generated group is the group
        generated by its images: the subgroup returned here *is*
        ``rho(Stab_{O(L)}(plane))`` -- the right-hand group the double-coset
        decisions of :meth:`separates_witness_orbits` and the plane-orbit
        split need.  The certified family is cached once per plane, not
        recomputed once per pair.
        """
        from sage.libs.gap.libgap import libgap
        from sage_extensions.categories.group.groups import (
            _element_to_engine,
            _gap_model,
        )

        family = self.certified_parabolic_generators(plane)
        if family is None:
            return None
        rho = self.lattice.discriminant_representation()
        engine = _gap_model(self._discriminant_group)
        return libgap.Subgroup(
            engine,
            [
                _element_to_engine(self._discriminant_group, rho(generator))
                for generator in family
            ],
        )

    def adjust_witness_into_subgroup(
        self, witness, target_stabilizer_generators, *, stabilizer_reference=None, flag=False
    ):
        r"""Left-adjust ``witness`` by the target stabilizer until it lies in the subgroup.

        If ``witness(x)=y`` and ``t`` stabilizes ``y``, then ``t*witness`` still
        carries ``x`` to ``y``.  Thus the relevant finite-character condition
        is ``chi(t) chi(witness) in S``, where ``Gamma = chi^-1(S)``.

        A stabilizer element ``t`` meets that condition exactly when it lies
        in ``S chi(witness)^-1`` in the owned composition law. The finite
        character product retains S from its discriminant targets and sign
        kernels. GAP intersects the target stabilizer image with the coset
        in its own product convention. The chosen
        element is carried back to a word in the stabilizer generators by
        their own word section, and the composed candidate is then admitted by
        the subgroup's defining predicate; a characters-only candidate the
        predicate rejects is an ``ArithmeticError``, never a silent wrong
        witness.
        """
        if witness in self.subgroup:
            return witness
        from sage_extensions.categories.group.groups import _law_reversed

        # The shared faithful permutation target of the character factors.  The
        # direct character product can have order 4.7e13 on T_Co (9.4e13 with a
        # sign factor), and its generic permutation isomorphism attempts a
        # regular action; the factors' own models are the group the double
        # coset is computed in, and every element enters it through its own
        # character key (_permutation_of_key) rather than through the product,
        # whose elementwise images are a word problem.
        permutation_product = self._character_permutation_factors()[2]
        point = self._permutation_of_key(self.image(witness))
        stabilizer_generators = tuple(target_stabilizer_generators)
        # The same target cusp is queried for many transported lines.  Its
        # exact stabilizer family and finite word section depend on the span,
        # not on the source line or its witness.  Reuse the section for that
        # span instead of constructing a GAP word problem per incidence edge.
        # The repeated hot loop is over line cusps.  Do not retain a GAP
        # section for every plane of a large plane row (189720 on T_Co).
        key = (
            _exact_stabilizer_span_key(self, stabilizer_reference)
            if stabilizer_reference is not None and not flag
            and int(stabilizer_reference.module_rank()) == 1
            else None
        )
        sections = self.__dict__.setdefault("_stabilizer_adjustment_sections", {})
        retained = sections.get(key) if key is not None else None
        if retained is not None and retained[0] is stabilizer_generators:
            stabilizer_permutation, stabilizer_section = retained[1:]
        else:
            stabilizer_gaps = [
                self._permutation_of_key(self.image(generator))
                for generator in stabilizer_generators
            ]
            stabilizer_permutation = libgap.Subgroup(permutation_product, stabilizer_gaps)
            stabilizer_section = None
        subgroup_permutation = self._permutation_character_target()
        reversed_product = _law_reversed(self._model_factors()[0][1])
        # The element of the stabilizer image inside the subgroup's coset is
        # exhibited by a double-coset membership and a canonical coset walk,
        # never by an intersection with a coset domain: GAP answers membership
        # in a double coset of hundreds of millions of elements instantly,
        # while the intersection enumerates the coset.
        chosen = _double_coset_adjustment(
            subgroup_permutation,
            stabilizer_permutation,
            point if reversed_product else point ** -1,
            permutation_product,
        )
        if chosen is None:
            return None
        if reversed_product:
            chosen = chosen ** -1
        # Factor the chosen stabilizer image over the stabilizer's own
        # generators, so the adjustment is a live element of the stabilizer.
        if stabilizer_section is None:
            stabilizer_section = _GapWordSection(
                stabilizer_gaps,
                parent=permutation_product,
            )
            if key is not None:
                sections[key] = (stabilizer_generators, stabilizer_permutation, stabilizer_section)
        letters = stabilizer_section.letters_of_permutation(chosen)
        letters = _letters_in_owned_order(self._model_factors(), letters)
        adjustment = self.supergroup.one()
        for index in letters:
            adjustment = adjustment * (
                stabilizer_generators[index - 1]
                if index > 0
                else ~stabilizer_generators[-index - 1]
            )
        candidate = adjustment * witness
        # Check the word against the character map itself: without it a wrong
        # letter evaluation would surface as a silent "no adjustment found"
        # (``None``) instead of an engine inconsistency (referee's residual
        # finding; the same warrant ``_checked_lift`` gives the transversals).
        actual = self._permutation_of_key(self.image(adjustment))
        if actual != chosen:
            raise ArithmeticError(
                f"the stabilizer word-section of {self.subgroup} was checked against the "
                f"character map: the evaluation induces permutation {actual} where the "
                f"chosen quotient element is {chosen}, so the retained word section is "
                "inconsistent"
            )
        if candidate not in self.subgroup:
            raise ArithmeticError(
                f"the characters say {candidate} lies in {self.subgroup}, but the "
                f"subgroup's defining predicate rejects it: the characters do not "
                f"determine {self.subgroup}"
            )
        return candidate

    def discriminant_image(self):
        r"""``rho(self.subgroup)`` in ``O(A_L)``, exactly, from the retained characters.

        ``Gamma`` is ``chi^-1(S)`` for the joint character ``chi = (rho, det, sn)``,
        exactly, because its character data is complete, and
        ``pi_1(chi(Gamma)) = pi_1(Q cap S)`` follows immediately since ``Gamma``
        is the *full* preimage.  By the proof at
        :meth:`_joint_discriminant_image_gap` — every element of the retained
        condition ``S`` carries all sign components ``+1``, so ``pi_1|_{Q cap S}``
        is injective and

            ``rho(Gamma) = (cap_i H_i) cap rho(K_0)``

        as ONE meet inside ``O(A_L)``, with ``K_0`` the joint sign kernel
        ``cap ker sn_j`` (never the disproved separate-marginal formula
        ``(cap_i H_i) cap rho(ker sn) cap rho(ker det)``).  No surjectivity of
        ``rho``, no containment of the targets, no separate kernel spreads.
        When both sign kernels are present the joint ``K_0`` family is not
        formed in this route either, and the projection of the joint product-
        model subgroup is used instead.
        """
        if not self._has_discriminant:
            raise ValueError(
                f"{self.subgroup} retains no discriminant preimage: its image under the "
                "discriminant representation is not characterized by its characters"
            )
        from sage_extensions.categories.group.groups import (
            _named_by_its_own_words,
            _subgroup_from_gap,
        )

        if not (self.determinant_kernel and self.spinor_kernel):
            return _subgroup_from_gap(
                self._discriminant_group,
                self._joint_discriminant_image_gap(),
                lambda: (
                    f"the joint discriminant image of "
                    f"{_named_by_its_own_words(self.subgroup)} in {self._discriminant_group}"
                ),
            )
        factors, _product, _embeddings, projections = self._gap_product()
        position = next(
            index for index, (label, _group) in enumerate(factors) if label == "discriminant"
        )
        projected = libgap.Image(projections[position], self._gap_subgroup())
        return _subgroup_from_gap(
            self._discriminant_group,
            projected,
            lambda: (
                f"the projected discriminant image of "
                f"{_named_by_its_own_words(self.subgroup)} in {self._discriminant_group}"
            ),
        )

    @cached_method
    def discriminant_image_membership(self):
        r"""Return the membership test of ``rho(self.subgroup)`` inside ``O(A_L)``.

        The decision is one stabilizer chain of ``\rho(\Gamma)`` acting on the
        discriminant group, built once and reused, and each question is answered
        by sifting the element through that chain: the cost of a question is the
        length of the chain, never the size of the group (A. Seress, *Permutation
        Group Algorithms*, Cambridge University Press 2003, Chapter 4, the
        Schreier--Sims stabilizer chain and its sifting test; GAP answers
        ``x in G`` for a group with a known chain exactly that way).

        Listing the image is not an option here and not a fallback: on the
        Enriques period lattice ``T_{\mathrm{En}}`` the image
        ``rho(\Gamma_{\mathrm{En},2})`` has order ``696729600`` (H. Sterk,
        *Compactifications of the period space of Enriques surfaces, Part I*,
        Math. Z. 207 (1991), Proposition 2.7, p. 6 for the group; the order is
        measured by :meth:`subgroup_image_order`), and the elementwise reads of
        this quotient (:meth:`image_keys`, :meth:`subgroup_image_keys`) are
        deliberately not on this path.

        The chain is the ``O(A_L)`` engine's own: the group tested is the one
        :meth:`_joint_discriminant_image_gap` computes inside that engine, which
        is the same subgroup :meth:`discriminant_image` returns as owned data.
        """
        return DiscriminantImageMembership(self)


class DiscriminantImageMembership:
    r"""Membership in ``\rho(\Gamma)`` inside ``O(A_L)``, decided by sifting one chain.

    ``quotient`` is an :class:`OrthogonalCharacterQuotient`; the group is
    ``\rho(quotient.subgroup)`` in the ``O(A_L)`` engine that
    :meth:`OrthogonalCharacterQuotient.discriminant_image` also reads, and the
    chain is built on the first question and kept for the object's lifetime
    (the quotient caches the object, so a call site that asks once per root asks
    one chain, not one chain per root).

    A question is answered by GAP's ``\in`` on that group, which is the sifting
    membership test of Seress, *Permutation Group Algorithms*, Chapter 4: walk
    the chain from the top, and at each level multiply the point back to a
    previously stored orbit representative; a point that fails at any level is
    not in the group.  Nothing here lists the group's elements.
    """

    def __init__(self, quotient) -> None:
        from sage_extensions.categories.group.groups import _gap_model

        self._quotient = quotient
        self._discriminant_group = quotient._discriminant_group
        self._engine = _gap_model(self._discriminant_group)
        self._image = quotient._joint_discriminant_image_gap()

    def quotient(self):
        r"""Return the character quotient whose discriminant image this tests."""
        return self._quotient

    def contains(self, isometry) -> bool:
        r"""Whether the isometry of ``O(A_L)`` lies in ``\rho(\Gamma)``."""
        from sage_extensions.categories.group.groups import _element_to_engine

        return bool(
            _element_to_engine(self._discriminant_group, isometry) in self._image
        )

    def __contains__(self, isometry) -> bool:
        return self.contains(isometry)

    @cached_method
    def _engine_translates(self, factors):
        r"""Return the engine elements of one family of translates, converted once.

        ``factors`` is a tuple of isometries of ``O(A_L)`` -- one family, which is what
        :meth:`meets_translates` asks about once per candidate -- and the converted
        family is the cached datum of this object, keyed by the family and kept by
        ``cached_method`` (``AGENTS.md``: ``cached_method`` is the owner of a cached
        datum of an object).  The conversion is this object's boundary crossing: the
        isometries are owned elements and the chain sifted is the engine's, so what
        crosses is kept here and never handed back out.
        """
        from sage_extensions.categories.group.groups import _element_to_engine

        return tuple(
            _element_to_engine(self._discriminant_group, factor) for factor in factors
        )

    def meets_translates(self, factors, isometry) -> bool:
        r"""Whether ``f`` times the isometry lies in ``\rho(\Gamma)`` for some ``f`` of ``factors``.

        ``factors`` and ``isometry`` are isometries of the discriminant group as owned
        elements of ``O(A_L)``; their engine elements are this object's own datum
        (:meth:`_engine_translates`), so no caller converts one and none is returned.

        The family is the datum that repeats: one question asks about the same family
        once per candidate, so the family is converted once and kept.  The target is
        not: it is the question's own element, so it crosses here and this object
        retains nothing of it.
        """
        from sage_extensions.categories.group.groups import _element_to_engine

        target = _element_to_engine(self._discriminant_group, isometry)
        return any(
            translate * target in self._image
            for translate in self._engine_translates(tuple(factors))
        )


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
    r"""Return one representative of each orbit of a listable subgroup.

    The listing runs through the subgroup's action on the vectors of
    ``square``, which is finite only when the lattice is definite: for an
    indefinite lattice the vector set of a square is infinite whenever it is
    nonempty, and the orbits of an infinite group on it are not enumerated here.
    """
    lattice = subgroup.supergroup().domain()
    assert lattice.is_definite(), (
        f"cannot list the orbits of {subgroup}: it is cut out by a predicate that "
        f"is not a character kernel, so its orbits are read by listing the subgroup "
        f"inside O(L) acting on the vectors of square {square}, and {lattice} is not "
        f"definite.  "
        + _MISSING_ARITHMETIC_GENERATING_SET
    )
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
    quotient = subgroup.finite_character_quotient()
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
            description=lambda: f"Square-zero orbit representatives of {subgroup}",
        )

    def split_representatives():
        for representative in orthogonal_group.vector_orbit_representatives(square):
            stabilizer = orthogonal_group.vector_stabilizer_generators(representative)
            for splitting in quotient.splitting_isometries(stabilizer):
                yield splitting(representative)

    return finite_ordered_set(split_representatives())


def _preimage_vector_witness(subgroup, source, target):
    r"""Return an element of the preimage subgroup carrying ``source`` to ``target``, or ``None``.

    Any ``O(L)``-witness ``w`` gives all others as ``t w`` with ``t`` in ``Stab(target)``.
    The images of ``t w`` in the finite quotient form a finite set, explored by the stabilizer
    generators; an element lies in the subgroup according to its image alone.
    """
    orthogonal_group = subgroup.supergroup()
    witness = orthogonal_group.vector_equivalence_witness(source, target)
    if witness is None:
        return None
    morphism = subgroup.preimage_morphism()
    generators = tuple(orthogonal_group.vector_stabilizer_generators(target))
    seen = [morphism(witness)]
    frontier = [witness]
    while frontier:
        current = frontier.pop()
        if current in subgroup:
            return current
        for generator in generators:
            candidate = generator * current
            image = morphism(candidate)
            if all(image != known for known in seen):
                seen.append(image)
                frontier.append(candidate)
    return None


def _subgroup_vector_equivalence_witness(subgroup, left, right):
    r"""Return an element of ``subgroup`` carrying ``left`` onto ``right``, or ``None``.

    Four routes, in order:

    * the subgroup's action owner retained its own exact decision
      (``owned_vector_witness``), which is used as it stands;
    * the subgroup is the preimage of a finite-image subgroup along a morphism
      on an indefinite lattice: the witnesses of ``left |-> right`` inside the
      supergroup form the coset of the supergroup's stabilizer of ``right``, and
      that coset is walked through the images in the finite quotient;
    * the subgroup is a character kernel: a supergroup witness is adjusted into
      the subgroup inside the finite character quotient;
    * otherwise the subgroup is listed inside a finite ``O(L)``, which exists
      only for a definite lattice; for an indefinite one that listing refuses
      rather than answering, because the supergroup's orbit is a strictly larger
      relation than the subgroup's.
    """
    orthogonal_group = subgroup.supergroup()
    owned = getattr(subgroup, "owned_vector_witness", None)
    if owned is not None and owned() is not None:
        lattice = orthogonal_group.domain()
        return owned()(lattice(left), lattice(right))
    if not subgroup.contains_character_kernel():
        lattice = orthogonal_group.domain()
        source, target = lattice(left), lattice(right)
        if hasattr(subgroup, "preimage_morphism") and not lattice.is_definite():
            return _preimage_vector_witness(subgroup, source, target)
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
    return subgroup.finite_character_quotient().adjust_witness_into_subgroup(
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


def _isotropic_line_representatives(lattice, quotient):
    r"""Representatives of primitive isotropic *line* classes, from ``A_L`` first.

    Eichler's criterion (Gritsenko--Hulek--Sankaran, Lemma 7.8, p. 503) classifies
    primitive vectors of fixed length by norm and normalized discriminant class in an
    even lattice with two orthogonal hyperbolic planes.  For norm zero those are exactly the
    *line* orbits, once ``v`` and ``-v`` are identified by the class set ``{c, -c}``:
    their normalized class is the whole invariant.  This function constructs one
    integral representative for *every* candidate class, before any integral orbit
    enumeration is attempted.  If a candidate class cannot be exhibited physically the
    construction returns ``None`` and the caller falls back to its integral route --
    a partial finite family is never returned as if it were the line set.
    """
    if not lattice.eichler_criterion_applies():
        return None
    from sage.libs.gap.libgap import libgap
    from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set

    quadratic_module = lattice.discriminant_group()
    zero_class = quadratic_module.zero()
    # Ambient line orbits are orbits of the *unordered* pairs {c, -c} under im rho,
    # the actual integral discriminant image.  Eichler gives vector classes, and two
    # candidates lying in one im-rho orbit realise one line orbit, so they must never
    # be split by how many candidates cover it.  Compute those orbits by the faithful
    # owned action of ambient rho-images on the module elements, not by string labels
    # or a join of discriminant targets.
    candidates = tuple(lattice.covering_discriminant_classes(lattice.base_ring().zero()))
    if all(candidate == zero_class for candidate in candidates):
        # Every normalized class is zero, so there is exactly one ambient line class.
        # No partition under rho(O(L)), no joint character intersection, and above all
        # no ambient integral generating family is required: any primitive isotropic
        # vector with div one gives that class, checked here rather than asserted.
        for label in lattice.module_generating_set():
            vector = lattice.module_generator(label)
            if vector.q() != lattice.base_ring().zero():
                continue
            if not vector.is_primitive():
                continue
            if lattice.divided_discriminant_class(vector) != zero_class:
                continue
            return finite_ordered_set((lattice.primitive_isotropic_subobject(vector),))
        return None
    def key(element):
        return element

    pairs = {}
    for candidate in candidates:
        pair = frozenset({key(candidate), key(-candidate)})
        pairs.setdefault(pair, candidate)

    ambient = quotient._ambient_generators()
    rho = lattice.discriminant_representation()
    images = [rho(generator) for generator in ambient]
    orbits = []
    unseen = set(pairs)
    while unseen:
        pair_repr = min(unseen)
        orbit = {pair_repr}
        frontier = [pair_repr]
        while frontier:
            following = []
            for point in frontier:
                class_of_point = next(
                    class_value for candidate_key, class_value in pairs.items()
                    if candidate_key == point
                )
                for gamma in images:
                    image_point = frozenset({key(gamma(class_of_point)), key(-gamma(class_of_point))})
                    if image_point not in orbit:
                        orbit.add(image_point)
                        following.append(image_point)
            frontier = following
        unseen.difference_update(orbit)
        orbits.append(orbit)

    representatives = []
    for orbit in orbits:
        isotropic_vector = None
        for pair_key in orbit:
            candidate = next(
                class_value for candidate_key, class_value in pairs.items()
                if candidate_key == pair_key
            )
            if candidate == zero_class:
                for label in lattice.module_generating_set():
                    vector = lattice.module_generator(label)
                    if vector.q() != lattice.base_ring().zero():
                        continue
                    if not vector.is_primitive():
                        continue
                    if lattice.divided_discriminant_class(vector) != zero_class:
                        continue
                    isotropic_vector = vector
                    break
            else:
                for candidate_vector in lattice.vectors_of_square_and_divisibility(
                    lattice.base_ring().zero(), candidate.additive_order()
                ):
                    if not candidate_vector.is_primitive():
                        continue
                    if candidate_vector.q() != lattice.base_ring().zero():
                        continue
                    if lattice.divided_discriminant_class(candidate_vector) != candidate:
                        continue
                    isotropic_vector = candidate_vector
                    break
            if isotropic_vector is not None:
                break
        if isotropic_vector is None:
            return None
        representatives.append(lattice.primitive_isotropic_subobject(isotropic_vector))
    return finite_ordered_set(tuple(representatives))


def _isotropic_divided_class_set(lattice, term):
    r"""Return ``D(W) = {[u/div(u)] : u primitive in W}`` for a primitive isotropic ``W``.

    Let ``N`` be the exponent of ``A_L``.  For primitive ``u`` the class
    ``[u/div(u)]`` has order ``div(u)``, so ``div(u) | N``; then
    ``div(u) = gcd(N, b(u, L))`` and ``u/div(u)`` modulo ``L`` depend only on
    ``u mod N W``.  For rank one the primitive vectors are ``+-w``, so
    ``D(W) = {c, -c}``.  For rank ``k >= 2`` every residue ``a`` in ``(Z/N)^k``
    with ``gcd(a, N) = 1`` is the residue of a primitive vector, because
    ``SL_k(Z) -> SL_k(Z/N)`` is onto (Shimura, *Introduction to the Arithmetic
    Theory of Automorphic Functions*, Lemma 1.38).  A representative ``a`` in
    ``[0, N)^k`` is ``g a'`` with ``a'`` primitive and ``gcd(g, N) = 1``, and the
    primitive lift of ``a`` is congruent to ``g u'`` modulo ``N W``, so its class
    is ``g [u'/div(u')]``.
    """
    from itertools import product as _product_tuples
    from math import gcd

    inclusion = term.inclusion()
    domain = inclusion.domain()
    basis = tuple(inclusion(domain.module_generator(label)) for label in domain.module_generating_set())
    if len(basis) == 1:
        divided_class = lattice.divided_discriminant_class(basis[0])
        return (divided_class, -divided_class)
    exponent = int(abs(lattice.correlation_morphism().cokernel().exponent()))
    zero = lattice.discriminant_group().zero()
    classes = []
    for coefficients in _product_tuples(range(exponent), repeat=len(basis)):
        common = gcd(*coefficients)
        if common == 0 or gcd(common, exponent) != 1:
            continue
        vector = None
        for coefficient, element in zip(coefficients, basis):
            if coefficient:
                piece = (coefficient // common) * element
                vector = piece if vector is None else vector + piece
        divided_class = lattice.divided_discriminant_class(vector)
        scaled = zero
        for _ in range(common):
            scaled = scaled + divided_class
        classes.append(scaled)
    return tuple(classes)


def _bezout_partner(row):
    r"""Return ``(divisor, partner)``, the Bezout data of a pairing row.

    ``row`` holds ``b(e, g_j)`` for the module generators ``g_j``; the divisor is
    the positive generator of the ideal the row spans -- the ideal ``b(e, L)``
    for the primitive isotropic ``e`` the row belongs to -- and the partner is
    the coefficient list with ``sum(m_j row_j) = divisor``, so the lattice vector
    ``f = sum(m_j g_j)`` has ``b(e, f) = divisor``.  For a divisor-1 vector this
    is the hyperbolic partner of the plane the split-signature witness fixes
    (S. Zemel, *The Structure of Integral Parabolic Subgroups of Orthogonal
    Groups*, J. Algebra 559 (2020) 95-128, arXiv:1902.08264v2, proposition 1.10,
    p. 13); for a divisor-2 vector the partner pairs ``b(e, f) = 2``, the divisor
    itself.
    """
    from sage.arith.misc import xgcd

    divisor = 0
    partner = [0] * len(row)
    for position, entry in enumerate(row):
        if entry == 0:
            continue
        if divisor == 0:
            divisor, partner[position] = entry, 1
            continue
        step, left, right = xgcd(divisor, entry)
        partner = [left * coefficient for coefficient in partner]
        partner[position] = right
        divisor = step
    if divisor < 0:
        divisor, partner = -divisor, [-coefficient for coefficient in partner]
    return divisor, partner


def _split_signature_witness(lattice, vector):
    r"""Return the Levi-part witness ``1_plane + (-1) complement`` at a primitive isotropic line.

    The parabolic at a primitive isotropic line has Levi factor
    ``GL(plane) x O(complement)`` (S. Zemel, *The Structure of Integral Parabolic
    Subgroups of Orthogonal Groups*, J. Algebra 559 (2020) 95-128,
    arXiv:1902.08264v2, Proposition 1.10, p. 13: for an element of the parabolic
    with Levi part ``(M, gamma)``, the determinant is ``det gamma`` and the real
    spinor norm is the class of ``det M`` times the spinor norm of ``gamma``).
    The element that fixes the plane pointwise and negates the complement is the
    Levi part ``(1, -1)``: the decomposition is built from the vector itself,
    never from the selected basis -- the partner ``f`` is the Bezout combination
    of the module generators with ``b(e, f) = div(e)`` (the divisor, the positive
    generator of the ideal ``b(e, L)``; for a divisor-1 vector this is the
    hyperbolic partner with ``b(e, f) = 1``), the plane is ``<e, f>``, and the
    complement is the kernel of the two pairing constraints, computed from the
    Gram matrix.  The witness ``w = 1_plane + (-1)_complement`` is read on the
    module generators as the matrix ``2*Proj_plane - 1`` whose ``j``-th column
    holds the coordinates of the image of the ``j``-th generator.

    Four properties are computed here, never assumed, because the construction
    is a candidate the caller must certify (it is not a claim to assert):

    * the images define an isometry -- the matrix identity ``W^t G W = G`` and
      the integrality of ``W`` are computed here, and the ``Aut`` constructor's
      column-matrix route raises when they fail;
    * the witness fixes the representative's generating vector;
    * the discriminant image is trivial: the complement's negation acts as the
      identity on a 2-elementary discriminant group, and the fixed plane
      contributes nothing;
    * the real spinor norm is ``-1``: the complement's negation is a product of
      reflections in an orthogonal basis of the complement's real span, and an
      odd count of positive-norm factors makes the product negative in either
      sign convention.

    A witness that fails any check is not a witness, and ``None`` is returned so
    the caller keeps its refusal rather than a guess.
    """
    labels = tuple(lattice.module_generating_set())
    basis = tuple(lattice.module_generator(label) for label in labels)
    gram = [[int(lattice.b(left, right)) for right in basis] for left in basis]
    coordinates = [int(vector.to_vector()(label)) for label in labels]
    row = [
        sum(gram[i][j] * coordinates[i] for i in range(len(coordinates)))
        for j in range(len(basis))
    ]
    divisor, partner = _bezout_partner(row)
    if divisor == 0:
        # The pairing row vanishes identically, so the vector pairs trivially
        # with every module generator: no partner realizes the divisor.
        return None
    pairing = sum(
        gram[i][j] * coordinates[i] * partner[j]
        for i in range(len(coordinates))
        for j in range(len(partner))
    )
    if pairing != divisor and pairing != -divisor:
        # The Bezout data does not realize the divisor: the plane is degenerate.
        return None
    norm = sum(
        gram[i][j] * partner[i] * partner[j]
        for i in range(len(partner))
        for j in range(len(partner))
    )
    from sage.matrix.constructor import matrix as sage_matrix
    from sage.rings.rational_field import QQ as SageQQ

    # The witness w = 1_plane + (-1)_complement on the module generators: its
    # j-th column holds the coordinates of the image of the j-th generator,
    # computed as 2*alpha*e + 2*beta*f - g_j for the plane <e, f>.
    columns = []
    for j in range(len(basis)):
        beta = SageQQ(sum(gram[k][j] * coordinates[k] for k in range(len(coordinates)))) / pairing
        alpha = (
            SageQQ(sum(gram[k][j] * partner[k] for k in range(len(partner)))) - beta * norm
        ) / pairing
        column = [
            2 * alpha * coordinates[position] + 2 * beta * partner[position]
            for position in range(len(coordinates))
        ]
        column[j] -= 1
        columns.append(column)
    transformation = sage_matrix(SageQQ, columns).transpose()
    if any(entry.denominator() != 1 for entry in transformation.list()):
        return None
    gram_matrix = sage_matrix(SageQQ, gram)
    if transformation.transpose() * gram_matrix * transformation != gram_matrix:
        return None
    from sage.rings.integer_ring import ZZ as SageZZ

    integral = sage_matrix(
        SageZZ, [[int(entry) for entry in row] for row in transformation.rows()]
    )
    try:
        witness = lattice.Aut()._isometry_from_column_matrix(integral)
    except (TypeError, ValueError, ArithmeticError):
        return None
    if witness(vector) != vector:
        return None
    orthogonal = lattice.discriminant_group().orthogonal_group()
    if lattice.discriminant_representation()(witness) != orthogonal.one():
        return None
    if lattice.O_plus().preimage_morphism()(witness).is_one():
        return None
    return witness


def general_image_certificate(quotient, representative):
    r"""Return the datum orbit (with its integral transporters) when the fibre has one ``ker rho``-orbit, else ``None``.

    Let ``G = O(L)``, ``H = Stab_G(x)`` for a primitive isotropic line ``x``,
    ``N = ker rho`` and ``D = {c, -c}`` with ``c = [v/div v]`` for a
    primitive generator ``v`` of ``x``.  ``N``
    is normal in ``G``, so the ``N``-orbits inside the one ``G``-orbit ``G x``
    are the double cosets ``N \\ G / H``, and the orbit--stabilizer theorem for
    the action of ``G/N = im rho`` identifies those with the cosets
    ``im rho / rho(H)``: the coset ``N g x`` is sent to ``rho(g) D``, and the
    fibre over ``D`` has cardinality ``[Stab_{im rho}(D) : rho(H)]``.  If
    ``rho(g') = rho(g) rho(h)`` then ``g' = n g h`` with ``n`` in the normal
    ``N``, so ``g'`` and ``g h`` lie in the same ``N``-orbit: that is the whole
    proof, and no property of the plane's complement is used anywhere in it.

    The datum is the *unoriented* line's set ``D(x) = {c, -c}`` -- written by
    :func:`_isotropic_divided_class_set`, as a one-element set when ``c = -c``
    -- because that is what the stabilizer of a line preserves: an element of
    ``H`` may interchange ``v`` with ``-v``, so the signed class ``c`` alone is
    the wrong datum for an unoriented line.  A caller that works with a signed
    primitive vector throughout and fixes its orientation uses ``c`` instead;
    then uses the vector stabilizer in place of the line stabilizer. Both
    numerator and denominator must be changed; the two conventions are not
    interchangeable and this call is the line's own.

    Both groups are computed, never assumed.  The right-hand group is the
    setwise stabilizer of ``D(x)`` inside ``im rho`` -- the image of the
    *ambient* orthogonal group, which is in general a proper subgroup of
    ``O(A_L)`` and is never replaced by it, and which is the group whose cosets
    the double cosets are counted in.  The left-hand group is the image of the
    ambient line stabilizer ``Stab_{O(L)}(x)``'s own exhibited family
    (``supergroup.isotropic_stabilizer_generators``), every element of which is
    exhibited, so the lower bound is genuine; when its order reaches the
    right-hand one the two groups are equal and ``1`` is returned with nothing
    assumed.  Taking that family from the *selected* subgroup instead is wrong:
    for ``Gamma = ker rho`` every one of its elements has trivial image, so the
    lower bound would be trivial while ``rho(Stab_{O(L)}(x))`` need not be.
    For a sign-only quotient there is no discriminant factor at all, the datum
    is trivial and its stabilizer is the whole retained sign image, which is
    what the second branch computes from the sign patterns.

    When the two orders agree the index is one, and the call returns the datum
    orbit itself as a tuple of ``(datum, transporter)`` pairs: ``datum`` is the
    divided-class set of one ``ker rho``-orbit, ``transporter`` an actual
    integral isometry of ``L`` carrying the representative's line onto a line of
    that datum, and the first pair is the representative with the identity.  The
    orbit is walked breadth-first over an exactly chosen generating subfamily of
    the ambient discriminant images, each kept beside the integral generator
    producing it, so it is exhaustive and no edge rebuilds a section or a
    ``rho`` image.

    ``None`` is the other answer, and it is not a guess: the family's image is
    then a proper subgroup of the datum's stabilizer, or the family is too short
    to decide, and either way the datum may carry several ``ker rho``-orbits.
    The caller keeps the exact integral route (``splitting_isometries``, one
    double coset at a time), which exhibits them -- that is the actual integral
    orbit classification, including the nontrivial split.  The index is never
    replaced by the surjectivity of a complement's discriminant action: that
    implication fails for an even lattice with a divisor-2 line, where the
    complement's action is surjective on its own discriminant group while its
    isometries do not all extend integrally across the gluing that makes the
    line primitive of divisor two, so the complement says nothing about the
    ambient datum's fibre.
    """
    from sage.libs.gap.libgap import libgap

    lattice = quotient.lattice
    if int(representative.module_rank()) != 1:
        raise ValueError(
            f"the datum fibre index is the primitive isotropic *line*'s: {representative!r} "
            f"has rank {int(representative.module_rank())}, and a higher-rank term's datum "
            "carries incidence data this call does not model"
        )
    # The lower bound is the image of the *ambient* line stabilizer's own
    # exhibited family -- ``Stab_{O(L)}(x)``, the owner of the setwise line
    # stabilizer -- and never the selected subgroup's stabilizer family.  A
    # subgroup that is a kernel has trivial image at every one of its elements,
    # so ``rho(Gamma cap H)`` is trivial for ``Gamma = ker rho`` while
    # ``rho(Stab_{O(L)}(x))`` need not be, and comparing the datum against the
    # former would report an index for a group the caller never walks.
    family = quotient.supergroup.isotropic_stabilizer_generators(
        representative, flag=False
    )
    if not quotient._has_discriminant:
        # A sign-only quotient retains no discriminant factor, so the datum is
        # trivial in every component it has and every element of the retained
        # image fixes it: the target is the ambient sign image.  The lower bound
        # is the sign image of the ambient stabilizer's family.  Signs multiply
        # componentwise, so both orders are the sizes of the F2-spans of the
        # component patterns.
        labels = tuple(quotient._image_labels)

        def pattern(isometry):
            key = quotient.image(isometry)
            return tuple(0 if key[label].is_one() else 1 for label in labels)

        target = 2 ** _f2_rank(
            [pattern(generator) for generator in quotient._ambient_generators()],
            len(labels),
        )
        stabilizer_order = 2 ** _f2_rank(
            [pattern(element) for element in family], len(labels)
        )
        if target % stabilizer_order:
            raise ArithmeticError(
                f"the sign image of the stabilizer of {representative!r} has order "
                f"{stabilizer_order}, which is not a multiple of the ambient sign image's "
                f"order {target}; the stabilizer's image must lie in it"
            )
        if target != stabilizer_order:
            return None
        # No discriminant factor means the datum is a single point of the
        # retained image: its orbit is itself, transported by the identity.
        datum = libgap.Set(
            [
                quotient._discriminant_group._engine_abelian_element(divided_class)
                for divided_class in _isotropic_divided_class_set(lattice, representative)
            ]
        )
        return ((datum, quotient.supergroup.one()),)

    finite_orthogonal = quotient._discriminant_group
    terms = (representative,)
    data = libgap(
        [
            libgap.Set(
                [
                    finite_orthogonal._engine_abelian_element(divided_class)
                    for divided_class in _isotropic_divided_class_set(lattice, term)
                ]
            )
            for term in terms
        ]
    )
    termwise_action = libgap.function_factory(
        "function(x, g) return List(x, part -> Set(List(part, y -> ImageElm(g, y)))); end"
    )
    engine, im_rho, _section, _ambient = quotient._im_rho_engine_and_section()
    stabilizer_of_datum = libgap.Stabilizer(im_rho, data, termwise_action)
    target = int(libgap.Size(stabilizer_of_datum))
    rho = quotient.lattice.discriminant_representation()
    from sage_extensions.categories.group.groups import _element_to_engine

    images = [
        _element_to_engine(finite_orthogonal, rho(generator)) for generator in family
    ]
    lower = libgap.Subgroup(engine, images) if images else libgap.TrivialSubgroup(engine)
    stabilizer_order = int(libgap.Size(lower))
    if target % stabilizer_order:
        raise ArithmeticError(
            f"the datum stabilizer of {representative!r} has order {target}, which is not a "
            f"multiple of the order {stabilizer_order} of the stabilizer's discriminant image; "
            "the stabilizer's image must lie in the datum's stabilizer"
        )
    if target != stabilizer_order:
        return None
    # The fibre index is one, so the `ker rho`-orbits inside this `O(L)`-orbit are
    # in bijection with the points of the datum orbit under `im rho` -- and every
    # point of that orbit is reached by an actual integral isometry, not by a
    # reconstructed vector: the walk below composes the ambient generators that
    # `rho` is evaluated on, whose images are `ambient_discriminant_images()` in
    # the same order as `_ambient_generators()`.
    #
    # The finite image generates as a monoid, so a generating subfamily suffices
    # and the breadth-first walk over it is exhaustive.  The subfamily is chosen
    # by exact membership in the subgroup accumulated so far (``libgap.IN``), and
    # the integral generator producing each kept image is retained beside it; no
    # image is rebuilt, and `rho` is not evaluated again on any of them.
    ambient_images = quotient.ambient_discriminant_images()
    ambient_order = int(libgap.Size(im_rho))
    kept_images, kept_isometries = [], []
    accumulated = None
    for image, isometry in zip(ambient_images, _ambient, strict=True):
        if accumulated is not None and bool(libgap.IN(image, accumulated)):
            continue
        kept_images.append(image)
        kept_isometries.append(isometry)
        accumulated = libgap.Subgroup(engine, kept_images)
        if int(libgap.Size(accumulated)) == ambient_order:
            break
    if accumulated is None or int(libgap.Size(accumulated)) != ambient_order:
        raise ArithmeticError(
            f"the discriminant images of the ambient generators of {lattice!r} do not "
            f"generate the retained image of order {ambient_order}; the datum orbit cannot be "
            "walked from them"
        )
    identity = quotient.supergroup.one()
    # ``data[0]`` is this line's own divided-class set, already in the engine
    # model the generators act on: the start of the walk is that datum and the
    # identity isometry.
    walk = [(data[0], identity)]
    reached = {str(walk[0][0]): 0}
    frontier = [0]
    while frontier:
        position = frontier.pop()
        current, transporter = walk[position]
        for image, isometry in zip(kept_images, kept_isometries, strict=True):
            moved = termwise_action(current, image)
            key = str(moved)
            if key in reached:
                continue
            # The one-step transport of the datum is the ambient generator itself,
            # composed after the path that reached its predecessor, so every point
            # of the orbit carries an actual integral isometry onto it.
            reached[key] = len(walk)
            walk.append((moved, lattice.compose(isometry, transporter)))
            frontier.append(len(walk) - 1)
    return tuple(walk)


def _line_orbit_from_divided_classes(subgroup, representative):
    r"""The ``ker rho`` line orbits as divided classes, or ``None`` when the split is not one.

    Let ``G = O(L)``, ``H = Stab_G(x)`` for the line ``x``, ``Gamma = ker rho`` and
    ``c = [v/div v]`` for a generator ``v`` of ``x``.  Because ``Gamma`` is normal in ``G``
    and equal to the kernel of ``rho``, the double cosets ``Gamma \\ G / H`` correspond
    bijectively to the cosets ``rho(G)/rho(H)`` -- orbit--stabilizer for the action of the
    quotient ``G/ker rho``, which acts through ``rho`` -- and the map ``Gamma g x |-> rho(g) c``
    sends an orbit of a *signed vector* to its class, with fibre over ``c``
    of size ``[Stab_(rho(G))(c) : rho(Stab_G(v))]``.  An unoriented line's datum is
    the set ``{c, -c}``, because its stabilizer may carry ``v`` to ``-v``; the index computed
    below is the setwise one, ``[Stab_(rho(G))({c, -c}) : rho(H)]``, with ``rho(H)`` from
    :meth:`stabilizer_discriminant_image` and never from a signed-class stabilizer.

    When that index is 1 -- computed here from the two exact images, not assumed -- the
    ``Gamma``-orbits in ``G x`` are in bijection with the orbit of the unordered
    datum ``{c, -c}``. A representative must be in the specified ambient orbit;
    constructing a line with the same datum in a different ambient orbit is
    not sufficient. The exact witness check below enforces that condition.  An index greater
    than one is a case of the mathematics, not a fallback: the caller keeps the explicit
    isometry route, which is how the case of several isometries per class is handled.

    Only the stable orthogonal group itself is served here: ``Otilde^+`` is the kernel of the
    joint character ``rho x (real spinor norm)``, whose index is not this one, so its orbits are
    not these cosets and the caller keeps its own route.
    """
    lattice = subgroup.supergroup().domain()
    if subgroup != lattice.stable_orthogonal_group():
        return None
    labels = tuple(representative.module_generating_set())
    if len(labels) != 1:
        return None
    vector = representative.inclusion()(representative.module_generator(labels[0]))
    divisor = lattice.div(vector)
    if divisor <= lattice.base_ring().zero():
        return None
    walk = general_image_certificate(
        subgroup.finite_character_quotient(), representative
    )
    if walk is None:
        return None
    # Each point of the datum orbit carries an actual integral isometry of ``L``
    # onto it, built by the walk out of the ambient generators.  The line is that
    # isometry's image of the representative -- no divided-class search and no
    # general isometry search reconstructs it, and the same isometry is the
    # transporter the caller registers for the pair.
    inclusion = representative.inclusion()
    source = tuple(
        inclusion(representative.module_generator(label)) for label in labels
    )
    orbit = []
    for datum, transporter in walk:
        images = tuple(transporter(vector) for vector in source)
        line = lattice.primitive_isotropic_subobject(*images)
        if lattice.divided_discriminant_class(images[0]) not in datum:
            raise ArithmeticError(
                f"the transporter carried {representative!r} to a line whose divided class is "
                f"not in the datum it was walked to: the datum orbit and the integral orbit "
                "disagree"
            )
        orbit.append(line)
    return tuple(orbit)


def _plane_orbit_from_odd_stabilizer(subgroup, representative):
    r"""The `O^+`-orbits inside one `O(L)`-orbit of planes, or ``None``.

    Let `G = O(L)`, `P` a primitive isotropic plane, `H = Stab_G(P)` and
    `Gamma = O^+ = ker(sn)`, the kernel of the real spinor norm (Gritsenko--Hulek--
    Sankaran, arXiv:0810.1614, section 1).  `Gamma` is normal of index two, so by
    D. Dutour Sikirić and K. Hulek, arXiv:2302.01679v2, Lemma 3.6, p. 22, the
    `Gamma`-orbits inside `G.P` are the double cosets
    `chi(Gamma) \\ chi(G) / chi(H)`, where `chi = (rho, sn)` is the joint finite
    character.

    Exactly two answers, and both are computed:

    * an element of `H` whose character image lies outside `chi(Gamma)` puts
      `chi(H)` across both cosets, so `chi(Gamma) chi(H) = chi(G)` and the whole
      `G`-orbit is one `Gamma`-orbit -- its representative is the ambient one;
    * when no such element is found, the ambient `G`-orbit splits, and it splits into
      exactly two because `Gamma` has index two and `chi(H)` would then be contained
      in `chi(Gamma)`: the two representatives are `P` and `g_0 P`, with
      `g_0` any integral isometry of odd real spinor norm, which is computed here as a
      reflection in a square-two vector and checked not to lie in `O^+`.

    Nothing here enumerated a stabilizer's generating family, and no isometry is
    guessed: the odd stabilizer element comes from the plane block equations
    (:meth:`...PrimitiveIsotropicSubobjects.plane_block_lift`), and the ambient odd
    element is a reflection the constructor verifies.
    """
    lattice = subgroup.supergroup().domain()
    # Recognise `O^+` by the character data that defines it, never by comparing
    # subgroup objects: a comparison of two preimage subgroups can be false for the
    # same subgroup reached by another route, and a false answer here does not fail
    # loudly -- it falls through to the stabilizer enumeration this route exists to
    # avoid, which exceeds the runtime's memory guard on `6JRX` without
    # returning.  `O^+ = sn^{-1}(+1)` is exactly the subgroup cut out by the
    # spinor character alone.
    quotient = subgroup.finite_character_quotient()
    if not (
        quotient.spinor_kernel
        and not quotient.determinant_kernel
        and not quotient._has_discriminant
    ):
        return None
    # `O^+ = sn^{-1}(+1)` is the kernel of the real spinor norm, which is onto
    # `{+-1}` as soon as the lattice exhibits one integral odd element, so its index
    # is two and neither character image's order has to be computed: the odd element
    # below either exists -- and then it both certifies the index and supplies the
    # second representative of the split -- or the call refuses by name.
    witness = quotient.plane_odd_character_witness(representative)
    if witness is not None:
        return (representative,)
    odd_ambient = lattice.odd_spinor_norm_isometry()
    return (representative, odd_ambient.transport_isotropic_object(representative))


def _plane_orbit_from_parabolic_stabilizer(subgroup, representative):
    r"""The `Gamma`-orbits inside one `O(L)`-orbit of planes, from the plane's parabolic.

    Let `G = O(L)`, `P` a primitive isotropic plane, `H = Stab_G(P)` and
    `Gamma` a subgroup of finite index.  By D. Dutour Sikirić and K. Hulek,
    arXiv:2302.01679v2, Lemma 3.6, printed p. 22, the `Gamma`-orbits inside
    `G.P` are the double cosets `rho(Gamma) \ rho(G) / rho(H)`, where `rho` is
    the discriminant representation.  The right-hand group `rho(H)` is what the
    double-coset split needs, and it is supplied here from the plane's own
    parabolic rather than by enumerating a stabilizer's generating family:
    the block equations of the parabolic are solved over `ZZ` at any primitive
    isotropic plane (Dutour Sikirić--Hulek, Theorem 4.9, printed pp. 33--34),
    and :meth:`...PrimitiveIsotropicSubobjects.ParentMethods.is_parabolic_complete`
    decides on three computed indices whether the family they produce is the
    whole of `H`.  Where the parabolic is not established to be
    complete, ``None`` is returned and the caller keeps its own route.

    Otherwise the answer is the double cosets' transported planes, one at a
    time (:func:`_iter_transported_planes`).

    Each returned representative is the transported plane of one double
    coset, so the count of the row is the count of the double cosets
    themselves -- computed by
    :meth:`...OrthogonalCharacterQuotient._splitting_isometries_in_im_rho`
    as ``rho(Gamma)``-orbits on the right-coset action of ``im rho`` on
    ``im rho / rho(Stab)``, a walk that carries the word of every
    representative it reaches, not a per-coset word problem.  Where the
    subgroup cuts a sign character as well, the kernel-sign witness machinery
    of that walk lifts the sign sheet -- the same machinery the
    ``ker(rho, sn)`` line rows run on.  The walk is the method: a row whose
    sign sheet it cannot lift raises (``_kernel_sign_flip`` names the missing
    ker(rho) witness), and two sign kernels cut at once raise too, because the
    single-flip machinery covers one coset only -- neither falls back to the
    joint-character enumeration, whose per-coset word problem is the cost this
    route exists to avoid.  Nothing here enumerated a stabilizer's generating
    family of the ambient orthogonal group, and no isometry is guessed: the
    parabolic family is certified complete before it is used, and every lift
    is a word in the ambient generating family spelled by the walk that
    reached its double coset.
    """
    if representative.is_parabolic_complete() is not True:
        return None
    family = tuple(representative.parabolic_stabilizer_generators())
    if not family:
        return None
    quotient = subgroup.finite_character_quotient()
    if quotient.index() == 1:
        # ``Gamma`` is all of ``O(L)`` (a character-kernel subgroup of index
        # one is the whole group), so ``Gamma g Stab = O(L)`` for every ``g``:
        # the double-coset space is the single point the identity names, read
        # rather than walked.  This is the full-group plane row of the Scattone
        # cards, and the walk would re-derive the same one orbit.
        quotient.register_isotropic_lift(
            representative,
            quotient.supergroup.one(),
            family,
            quotient._discriminant_group.one(),
        )
        return (representative,)
    if not quotient._has_discriminant or (
        quotient.determinant_kernel and quotient.spinor_kernel
    ):
        raise ValueError(
            f"the plane row of {representative!r} under {subgroup} cannot be computed by "
            "the coset walk of the discriminant image: the subgroup cuts no discriminant "
            "condition, or both a determinant and a spinor kernel at once, and the "
            "walk's kernel-sign witness machinery lifts one sign coset only"
        )
    # The split's own lifts, the finite element each of them acts on the
    # discriminant group by, and the complete source family are retained with
    # the representatives they produced: the consumers of the row never search
    # for a witness or re-certify a transported parabolic (the search reaches
    # the port's generic enumeration, and the recomputation reaches PARI's
    # qfauto overflow on this lattice).
    quotient.register_isotropic_lift(
        representative,
        quotient.supergroup.one(),
        family,
        quotient._discriminant_group.one(),
    )
    return _iter_transported_planes(quotient, representative, family)


def _iter_transported_planes(quotient, representative, family, *, resume_after=0):
    r"""Yield the double cosets' transported planes of one plane's parabolic split.

    A kernel row numbers 189720 of them, and each one is a constructed parent of
    this library, kept for the process by the construction caches above it: a
    caller that materialises the row holds every plane of the row at once,
    which is 74 KB a plane and 13.47 GiB at the row's length.  The walk under
    the split is already lazy -- it yields one lift and its finite element at a
    time -- so the row is yielded here as well and the plane is the caller's to
    drop once its own datum (the cusp's span) exists.  What is retained per
    plane is the lift registry's `(spelling, source family, discriminant image)`,
    keyed by the plane's span: the *word* the walk spelled the lift by and not
    the lift's product, whose integer entries grow with the plane, because a
    consumer of the row reads the finite element a plane and spells the isometry
    only where it transports something
    (:meth:`...OrthogonalCharacterQuotient.register_isotropic_lift`).

    ``resume_after`` is the number of double cosets a caller already holds: it
    skips them before their transport and their cusp, so a run that kept the
    first ``k`` planes' registrations, spans and finite elements resumes at the
    ``k``-th and pays neither.  The skip counts steps of the walk *from the
    representative and family given here*, so a caller resuming another run's
    mark has to pin both: the drawn representative is not reproduced by a
    second process, and a family at another copy of the plane is another
    generating set, so the mark counts the planes of the anchor it was made
    on.  What a resume cannot save is the walk's own spelling, which is a
    product an edge and has to reach the same nodes.
    """
    for position, (
        splitting,
        discriminant_image,
        spelling,
    ) in enumerate(quotient._iter_splitting_isometries_in_im_rho(family, spellings=True)):
        if position < resume_after:
            continue
        transported = splitting.transport_isotropic_object(representative)
        quotient.register_isotropic_lift(
            transported, splitting, family, discriminant_image, spelling=spelling
        )
        yield transported


def _isotropic_line_class_points(lattice, line):
    r"""The engine set of the divided classes ``{c, -c}`` of a primitive isotropic line.

    The line's generator ``v`` has a divisibility ``div(v)`` and a divided
    class ``[v / div(v)]`` in ``A_L``; an unoriented line is the *set*
    ``{v, -v}``, so the class datum of the line is the set ``{c, -c}`` -- the
    same set :meth:`OrthogonalCharacterQuotient.isotropic_line_stabilizer_image`
    builds for its stabilizer, read here for the equivariance alone.
    """
    from sage.libs.gap.libgap import libgap

    inclusion = line.inclusion()
    domain = inclusion.domain()
    label = next(iter(domain.module_generating_set()))
    vector = inclusion(domain.module_generator(label))
    discriminant_class = lattice.divided_discriminant_class(vector)
    finite_orthogonal = lattice.discriminant_group().orthogonal_group()
    return libgap.Set(
        [
            finite_orthogonal._engine_abelian_element(discriminant_class),
            finite_orthogonal._engine_abelian_element(-discriminant_class),
        ]
    )


def _isotropic_line_image_key(quotient, line):
    r"""The key of a primitive isotropic line in the subgroup's finite image.

    An element of ``Gamma`` carries one isotropic line onto another, and the
    divided class of a primitive vector is carried by an isometry onto the
    divided class of its image, so the ``rho(Gamma)``-orbit of the class pair
    ``{c, -c}`` is an invariant of the ``Gamma``-orbits of lines: two lines of
    one orbit share their key, and a cusp whose key differs from a line's
    cannot contain it.  This is the equivariance
    :meth:`OrthogonalCharacterQuotient.invariant_separates_isotropic_orbits`
    reads as a question, read here as a key, so that a line row is indexed once
    instead of searched at every line.

    The key is the orbit itself, as the set of markers
    :meth:`OrthogonalCharacterQuotient.isotropic_class_orbit` walks: two class
    pairs with equal keys lie in one ``rho(Gamma)``-orbit and two with
    different keys in different ones, which is exactly what a dictionary of a
    row's cusps answers a line's own key with.  The direction a vertex needs is
    the sound one -- equal orbits are the same orbit, so a key no cusp carries
    is a line of no cusp -- while two cusps may still share a key where the
    finite image is coarser than the cusps, and the line is then decided among
    those cusps by the witness the certificate retains.  A quotient with no
    discriminant image has no key and answers ``None``, which leaves the caller
    its isometry route.
    """
    if not quotient._has_discriminant:
        return None
    return frozenset(
        quotient.isotropic_class_orbit(
            _isotropic_line_class_points(quotient.lattice, line)
        )
    )


class _LiftSpelling(NamedTuple):
    r"""One lift of a plane row, as the word it was spelled by rather than as its matrix.

    A lift of a kernel row is a word in the ambient group's selected generating
    family -- the walk that reaches its double coset composes one generator per
    edge of its own tree, and the double coset is spelled by the word section --
    and the word's *product* has integer entries that grow with the plane it
    reaches.  What a consumer of the row needs per plane is the finite element
    (registered beside this), and the integral isometry only where it transports
    something; so the registry keeps the word -- ``letters`` are signed,
    one-based indices into :meth:`_ambient_generators`, negative for an inverse,
    in left-to-right product order -- and the product is spelled when it is
    asked for (:meth:`_spelled_lift`).  ``flip`` is the kernel-sign witness a
    sign sheet's lift is multiplied by on the left, or ``None``.
    """

    letters: tuple
    flip: object


_SETWISE_DIVIDED_CLASS_ACTION = None


def _setwise_divided_class_action():
    r"""GAP's setwise action on a set of divided classes, read once per session."""
    global _SETWISE_DIVIDED_CLASS_ACTION
    if _SETWISE_DIVIDED_CLASS_ACTION is None:
        from sage.libs.gap.libgap import libgap

        _SETWISE_DIVIDED_CLASS_ACTION = libgap.function_factory(
            "function(x, g) return Set(List(x, y -> ImageElm(g, y))); end"
        )
    return _SETWISE_DIVIDED_CLASS_ACTION


def _composite_divided_class_action(quotient, target_image, reference_image):
    r"""The action of the composite ``s_P s_{P_0}^{-1}`` on ``A_L``, from the two images.

    ``target_image`` and ``reference_image`` are the registered finite elements
    of the two planes' lifts -- elements of ``O(A_L)``, one per plane, kept in
    the lift registry beside the lifts they belong to
    (:meth:`OrthogonalCharacterQuotient.register_isotropic_lift`).  The
    composite carries the reference plane to the target plane, and ``rho`` is a
    homomorphism of the owned laws, so its action on ``A_L = L^\#/L`` is
    ``rho(s_P) rho(s_{P_0})^{-1}``: one product and one inversion in a finite
    group, instead of the dual action of the composite's matrix, which inverts
    an integral isometry whose entries grow with the plane.

    The element returned is read in the model the classes are built in (the
    quotient's own ``O(A_L)``), which is what makes the carried classes
    comparable with a line's own pair.
    """
    from sage_extensions.categories.group.groups import _element_to_engine

    return _element_to_engine(
        quotient._discriminant_group, target_image * ~reference_image
    )


def _carried_divided_classes(classes, action):
    r"""The divided classes ``classes`` carried by ``action``, an automorphism of ``A_L``.

    A line's datum is the *set* ``{c, -c}``, so the carried datum is the set of
    carried classes and the pair moves as one pair.  The image is GAP's own
    action of a group element on the classes, applied setwise.
    """
    return _setwise_divided_class_action()(classes, action)


def _line_generator_in_plane(plane, line):
    r"""Return the line's generator and its coordinates, read in the plane's own domain.

    The line must be a subobject of the plane: its inclusion factors through
    the plane's, and the factored morphism reads the line's generator as a
    point of the plane's domain.  The coordinates are that point's coordinate
    vector, so a Levi restriction of the plane acts on them directly.
    """
    line_in_plane = line.inclusion().factor_through(plane.inclusion())
    line_domain = line.inclusion().domain()
    labels = tuple(line_domain.module_generating_set())
    line_vector = line_in_plane(line_domain.module_generator(labels[0]))
    return line_vector, line_vector.to_vector()


def _levi_restriction_fixes_line(plane, generator, line_vector, coordinates):
    r"""Whether the Levi restriction of ``generator`` on the plane fixes the line setwise.

    The Levi restriction acts on the plane's own domain, and the line's
    generator is read in the plane's coordinates: two vectors of a
    torsion-free rank-two module are proportional exactly when the determinant
    of their coordinate matrix vanishes, which is the setwise stabilizer
    condition on the line.
    """
    action = plane.levi_restriction(generator)
    image = action(line_vector)
    image_coordinates = image.to_vector()
    labels = tuple(plane.inclusion().domain().module_generating_set())
    determinant = image_coordinates(labels[0]) * coordinates(labels[1]) - image_coordinates(
        labels[1]
    ) * coordinates(labels[0])
    return determinant == plane.inclusion().domain().base_ring().zero()


def _plane_parabolic_incidence_flags(subgroup, plane, flag):
    r"""A flag covering of the Tits-building incidence at one plane, from its parabolic.

    Let ``G = O(L)``, ``P`` a primitive isotropic plane, ``F_0 = (ell_0 < P)``
    a flag whose line is one line of ``P``, ``Pi = Stab_G(P)`` the plane's
    parabolic and ``K = Stab_Gamma(P) = Gamma cap Pi``.  The incidence at the
    orbit of ``P`` is covered by the ``K``-orbits on the lines of ``P``.  Those lines
    decompose into ``Pi``-orbits -- the divisibility of a line of ``P`` is
    preserved by ``Pi``, so there can be several.  Write
    ``H = Pi cap Stab_G(ell_0)``.  The ``K``-orbits inside the ``Pi``-orbit of
    ``ell_0`` are the double cosets ``K \ Pi / H``.  This function covers them
    by the double cosets ``K \ Pi / R``, where ``R`` is the subgroup generated
    by the retained parabolic generators whose Levi restriction fixes the
    line.  Since ``R <= H``, the natural map of these double-coset sets onto
    ``K \ Pi / H`` is surjective: no ``K``-orbit is lost, although one can be
    represented more than once.  The public incidence call removes those
    repetitions when it retains one flag certificate per line/plane cusp pair.

    The quotient the row was split by is one finite character ``chi`` of
    ``O(L)`` -- the discriminant representation together with whichever sign
    characters the subgroup cuts -- and the subgroup is the full preimage
    ``Gamma = chi^-1(chi(Gamma))``.  Then ``U = Pi cap ker chi`` is normal in
    ``Pi``, being the kernel of a homomorphism restricted to it, and ``U <= K``
    because ``Gamma`` is a preimage.  The quotient map ``Pi -> Pi/U`` therefore
    pairs the two double-coset decompositions (D. Dutour Sikiri'c and K. Hulek,
    arXiv:2302.01679v2, Lemma 3.6, printed p. 22), and ``Pi/U`` *is* ``chi(Pi)``
    by the definition of ``U``.  So the covering is computed in the finite
    character image, with left group ``chi(K) = chi(Gamma) cap chi(Pi)`` and
    right group ``chi(R)``.  No character of the quotient is special here: the
    discriminant representation, a sign character, and the two together all
    give a normal ``U``, and the hypothesis of the lemma is only that.

    Each returned flag is ``F_0`` transported by one lifted double-coset
    representative, an element of the parabolic spelled as a word in the
    certified family and checked against the character map before it
    transports.  Together their line terms cover every ``K``-orbit of the
    ``Pi``-orbit, with repetitions allowed, and each plane term is the plane
    itself.  Where the parabolic is not established to be complete, or it
    carries no generator fixing the line, ``None`` is returned and the caller
    keeps its own route.
    """
    quotient = subgroup.finite_character_quotient()
    family = quotient.certified_parabolic_generators(plane)
    if not family:
        return None
    # The finite image the covering descends to: chi on the certified parabolic,
    # read in the faithful permutation model of the character factors, which is
    # the group the double cosets are computed in.  Every element enters that
    # model through its own character key (``_permutation_of_key``), factor by
    # factor: an element of the character product has to be sifted through the
    # product's stabiliser chain to be mapped, and the product of the
    # discriminant factor with a sign factor has no chain that can be built at
    # the orders this quotient meets.
    _factors, _models, permutation_target, _embeddings = (
        quotient._character_permutation_factors()
    )
    permutations = tuple(
        quotient._permutation_of_key(quotient.image(generator)) for generator in family
    )
    parabolic = libgap.Subgroup(permutation_target, permutations)
    section = _GapWordSection(permutations)
    # chi(K) = chi(Gamma) cap chi(Pi).  chi(Gamma) is the retained condition
    # subgroup's own image, read factorwise, and chi(Pi) is the parabolic's, so
    # the meet is taken between two subgroups of the one permutation target.
    # At index one chi(Gamma) is the whole image and contains chi(Pi), and the
    # meet then answers chi(Pi) itself without asking for the index, which is a
    # quotient of two orders of 4.7e13 and costs a minute on the Coble lattice.
    left = libgap.Intersection(quotient._permutation_character_target(), parabolic)
    # The right group: the image of the members of the certified family whose
    # Levi restriction on the plane fixes the line.
    line, plane_term = flag.terms()
    line_vector, line_coordinates = _line_generator_in_plane(plane_term, line)
    right_generators = [
        permutation
        for generator, permutation in zip(family, permutations, strict=True)
        if _levi_restriction_fixes_line(
            plane_term, generator, line_vector, line_coordinates
        )
    ]
    if not right_generators:
        return None
    right = libgap.Subgroup(permutation_target, right_generators)
    flags = []
    for double_coset in libgap.AsList(
        libgap.DoubleCosets(parabolic, left, right)
    ):
        point = libgap.Representative(double_coset)
        letters = _letters_in_owned_order(
            quotient._model_factors(), section.letters_of_permutation(point)
        )
        element = quotient.supergroup.one()
        for letter in letters:
            element = element * (
                family[letter - 1] if letter > 0 else ~family[-letter - 1]
            )
        if quotient._permutation_of_key(quotient.image(element)) != point:
            raise ArithmeticError(
                f"the word-section lift of a double-coset representative at {plane_term} "
                f"was checked against the character map and maps elsewhere: the parabolic "
                f"word section is inconsistent with the finite character image"
            )
        transported = element.transport_isotropic_object(flag)
        quotient.register_isotropic_transport(
            transported.terms()[0], line, element
        )
        flags.append(transported)
    return tuple(flags)


_EICHLER_LINE_LABELS = ("discriminant", "spinor")
r"""The character labels whose kernel contains the Eichler transvections.

$E_U(L_1)$ lies in the kernel of the discriminant character and in the spinor
kernel, so a subgroup cut out by a subset of these labels contains it.
"""


def _eichler_line_representatives(subgroup, quotient):
    r"""The subgroup's line orbits when Eichler's criterion alone decides them.

    Gritsenko--Hulek--Sankaran, arXiv:0810.1614v1, Proposition 3.3(i) (after
    Eichler, *Quadratische Formen und orthogonale Gruppen*, Satz 10.4): write
    $L = U \oplus U_1 \oplus L_0$ and let $E_U(L_1)$ be the group generated by the
    Eichler transvections $t(e, a)$, $t(f, a)$ with $a \in L_1$ and $e, f$ the two
    isotropic directions of the first $U$; if $u$ and $v$ are primitive with
    $(u, u) = (v, v)$ and $u^* = v^* \bmod L$, then some element of $E_U(L_1)$
    carries $u$ to $v$.  The same proposition states $E_U(L_1) \subseteq SO^+(L)$,
    and every Eichler transvection fixes $D(L)$ pointwise, so
    $E_U(L_1) \subseteq \widetilde O^+(L) = \ker \rho \cap O^+(L)$: the group the
    criterion names is the stable orthogonal group, and that is why its orbits
    bound the orbits of every subgroup that contains it.

    A subgroup containing $\widetilde O^+(L)$ contains $E_U(L_1)$, so it has at
    most as many orbits as $E_U(L_1)$, namely at most one per admissible value of
    $(v, v)$ and $[v / \mathrm{div}\, v]$.  When the lattice satisfies the
    proposition's hypothesis -- an even lattice with a $U \oplus U$ summand, which
    ``eichler_criterion_applies`` decides -- and the covering classes of square
    zero are exactly the zero class, there is one such value: every primitive
    isotropic vector has square zero and divided class zero, so $E_U(L_1)$, hence
    the subgroup, acts transitively on them, and any one of them is a
    representative.

    The three conditions are checked here rather than assumed: the subgroup's
    character labels are among the discriminant and spinor characters, so its
    kernel contains $\widetilde O^+(L)$; the lattice satisfies the criterion's
    hypothesis; and the covering classes of square zero are one class.  ``None``
    means one of them failed and the caller keeps its integral route.

    The representative is built from the lattice's own generating set by
    :func:`_isotropic_line_representatives`, which constructs it from the
    discriminant module: neither the ambient integral generating family nor
    ``_sign_descent_rank`` is touched, which is the whole point -- on
    $U \oplus U \oplus E_8(-1)^2 \oplus \langle -4 \rangle$ the ambient family's
    computation reaches the indefinite port's Lorentzian cell traversal and grows
    without bound.
    """
    labels = tuple(quotient._image_labels)
    if any(label not in _EICHLER_LINE_LABELS for label in labels):
        return None
    lattice = subgroup.supergroup().domain()
    if not lattice.eichler_criterion_applies():
        return None
    zero_class = lattice.discriminant_group().zero()
    covering = tuple(lattice.covering_discriminant_classes(lattice.base_ring().zero()))
    if not covering or any(candidate != zero_class for candidate in covering):
        return None
    constructed = _isotropic_line_representatives(lattice, quotient)
    if constructed is None:
        return None
    representatives = tuple(constructed)
    if len(representatives) != 1:
        return None
    return representatives


def _yield_subgroup_isotropic_orbit_representatives(subgroup, rank, *, flag=False):
    r"""Yield the subgroup's orbits of primitive isotropic subobjects one at a time.

    This is the row :func:`_subgroup_isotropic_orbit_representatives` collects,
    yielded rather than gathered.  A caller whose own datum is smaller than a
    representative -- the cusp row, which keeps a span a cusp -- must not have
    to hold every representative to reach the last one: a kernel plane row of
    ``T_{Co}`` has 189720 of them, and each is a constructed parent.

    The row is the ambient ``O(L)``-orbits, split under the subgroup: the
    character quotient's image (:mod:`sage_extensions.timing` records it as the
    ``discriminant image`` stage), the ambient row, and the splitting of each
    ambient representative by the coset walk and its transport, which the
    per-representative stages record together as one interval because they are
    one walk over the orbit's representatives rather than a measurement of any
    single one of them.
    """
    if not flag and index(rank) == 0:
        yield from subgroup.supergroup().isotropic_orbit_representatives(0)
        return
    lattice = subgroup.supergroup().domain()
    row = orbit_row_record_name(rank, flag=flag, lattice=lattice, subgroup=subgroup)
    with stage("discriminant image", row):
        _assert_isotropic_splitting_has_character_data(subgroup)
        quotient = subgroup.finite_character_quotient()
    orthogonal_group = subgroup.supergroup()
    if not flag and index(rank) == 1:
        from_eichler = _eichler_line_representatives(subgroup, quotient)
        if from_eichler is not None:
            yield from from_eichler
            return
    # The ambient classes always come from the port's classification: the
    # in-repo discriminant-class route exhibits its representatives by an
    # integral-point enumeration that does not return on the Enriques lattice
    # (its Normaliz walk fails there), while the port's line route answers the
    # same classes.
    sourced = orthogonal_group.isotropic_orbit_representatives(rank, flag=flag)
    with stage("coset splitting and transport", row):
        for representative in sourced:
            line_image = (
                quotient.isotropic_line_stabilizer_image(representative)
                if not flag and rank == 1
                else None
            )
            if line_image == "NOSPLIT":
                # The sign witness (or trivial quotient) proves G_0 = G Stab(x) for its index.
                yield representative
                continue
            if line_image is not None:
                # The coset walk's words are retained with the lines they
                # transported: a transporter between two transported
                # representatives is the composite of their words.
                for splitting in quotient.splitting_isometries_from_line_class(*line_image):
                    transported = splitting.transport_isotropic_object(representative)
                    quotient.register_isotropic_transport(
                        transported, representative, splitting
                    )
                    yield transported
                continue
            if not flag and index(rank) == 1:
                from_divided_classes = _line_orbit_from_divided_classes(subgroup, representative)
                if from_divided_classes is not None:
                    yield from from_divided_classes
                    continue
            if not flag and rank == 2:
                from_planes = _plane_orbit_from_odd_stabilizer(subgroup, representative)
                if from_planes is not None:
                    yield from from_planes
                    continue
            if not flag and rank == 2:
                from_parabolic = _plane_orbit_from_parabolic_stabilizer(subgroup, representative)
                if from_parabolic is not None:
                    yield from from_parabolic
                    continue
            stabilizer = quotient.exact_isotropic_stabilizer_generators(
                representative, flag=flag
            )
            for splitting in quotient.splitting_isometries(stabilizer):
                transported = splitting.transport_isotropic_object(representative)
                source_terms = (
                    tuple(representative.terms()) if flag else (representative,)
                )
                for moved, source in zip(
                    tuple(transported.terms()) if flag else (transported,),
                    source_terms,
                    strict=True,
                ):
                    quotient.register_isotropic_transport(moved, source, splitting)
                yield transported


@timed_stage(
    "isotropic orbit representatives",
    input=lambda subgroup, rank, *, flag=False: orbit_row_record_name(
        rank,
        flag=flag,
        lattice=subgroup.supergroup().domain(),
        subgroup=subgroup,
    ),
)
def _subgroup_isotropic_orbit_representatives(subgroup, rank, *, flag=False):
    r"""Return the subgroup's orbits of primitive isotropic subobjects, as one timed row.

    The row :func:`_yield_subgroup_isotropic_orbit_representatives` yields,
    gathered into the set it is.  A caller that keeps its own datum per orbit --
    the cusp row keeps a span -- takes the yielded row instead, so that the
    representatives it has finished with are dropped as it goes.
    """
    return finite_ordered_set(
        tuple(_yield_subgroup_isotropic_orbit_representatives(subgroup, rank, flag=flag))
    )


def _subgroup_isotropic_equivalence_witness(subgroup, left, right, *, flag=False):
    orthogonal_group = subgroup.supergroup()
    quotient = None
    if subgroup.contains_character_kernel():
        quotient = subgroup.finite_character_quotient()
        # The equivariant class data separates the orbits of two primitive
        # isotropic subobjects before any isometry search runs: a subgroup
        # element carrying one to the other maps the class data of the first
        # onto that of the second (the plane isometry between two
        # word-transported representatives reaches the port's generic
        # enumeration on this lattice, and the separated pairs never start it.
        if not flag and quotient.invariant_separates_isotropic_orbits(left, right):
            return None
    # The parabolic split's own lifts are ambient isometries between the
    # representatives it produced, so two registered planes have a witness
    # that no isometry search has to find.
    left_lift = quotient.isotropic_lift_of(left) if quotient is not None else None
    right_lift = quotient.isotropic_lift_of(right) if quotient is not None else None
    witness = None
    if left_lift is not None and right_lift is not None:
        witness = right_lift * ~left_lift
    elif quotient is not None:
        # The rows that produced these objects hold the words that transported
        # them, so an isometry between two transported objects is the composite
        # `g_right * b * ~g_left` of those words; no search is started for it.
        witness = quotient.isotropic_transport_between(left, right)
    if witness is None:
        witness = orthogonal_group.isotropic_equivalence_witness(left, right, flag=flag)
    if witness is None:
        return None
    if witness in subgroup:
        return witness
    if left_lift is not None and right_lift is not None:
        # These are two representatives of the parabolic split itself.  Its
        # double cosets already decide their subgroup orbits: a witness in the
        # subgroup was returned above, and otherwise the representatives are
        # in distinct orbits by construction (DSH Lemma 3.6, printed p. 22).
        # A second membership test in rho(Gamma) rho(Stab) is therefore not
        # merely redundant: GAP's DoubleCoset membership is the memory wall
        # measured while deduplicating the T_Co plane cusps.
        return None
    _assert_isotropic_splitting_has_character_data(subgroup)
    if quotient is None:
        quotient = subgroup.finite_character_quotient()
    if not flag and quotient.separates_witness_orbits(witness, left):
        return None
    stabilizer = quotient.exact_isotropic_stabilizer_generators(right, flag=flag)
    return quotient.adjust_witness_into_subgroup(
        witness, stabilizer, stabilizer_reference=right, flag=flag
    )


__all__ = [
    "OrthogonalCharacterQuotient",
    "NO_SPLIT",
    "NO_SPLIT_BY_REFLECTION",
    "NO_SPLIT_BY_ZERO_CLASS",
    "NO_SPLIT_BY_SIGN_PATTERNS",
]
