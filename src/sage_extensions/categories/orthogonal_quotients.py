r"""Finite character quotients controlling arithmetic-subgroup orbit splitting."""
from operator import index

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
from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.set_categories import NN, Set, Sets


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


class _GapWordSection:
    r"""A GAP stabilizer-chain word section of a finitely generated group.

    ``gap_generators`` is a tuple of libgap elements, and ``parent`` the libgap
    group that contains them when it has a stabilizer chain of its own.  With a
    parent, the generated group is bound as ``Subgroup(parent, gens)`` and GAP
    reuses the parent's chain — building ``Group(gens)`` fresh instead pays a
    new stabilizer-chain construction whose cost at the Enriques discriminant
    image sizes was measured over the guard (`.tmp/enriques_staged2b.log`,
    A5), while parent reuse is the documented GAP mechanism for subgroups of a
    chained group.  Without a parent the fresh ``Group(gens)`` is used.

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
        """
        if self._permutation_model is None:
            to_permutation = libgap.IsomorphismPermGroup(libgap.Group(self._generators))
            self._permutation_model = (to_permutation, libgap.Range(to_permutation))
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

        return product.predicate_subgroup(allowed, "the specified finite character conditions")

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
        parent-bound chains are measured instant at the Enriques size
        (`.tmp/measure_pathB.log`), while the direct product's own chain is
        the measured wall (`.scratch/measure_a5_atoms.log`, t_b).  No image
        element is listed; no ambient-order substitution.
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
        if not sign_labels:
            return ambient_order
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
        subgroups of ``O(A_L)``.  With more than one sign factor and
        supergroup-family requirements the joint ``K_0`` family is not
        currently formed here, and the honest legacy branch below is kept;
        in that case this statement does not claim computation.
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
        if self.determinant_kernel and self.spinor_kernel:
            raise NotImplementedError(
                "the joint intersection of two sign kernels inside O(L) is not "
                "currently generated in this route; the legacy product-model "
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
        if not pieces:
            raise ValueError(
                f"{self.subgroup} retains no discriminant preimage: its joint "
                "discriminant image is not characterized by its characters"
            )
        return libgap.Intersection(*pieces) if len(pieces) > 1 else pieces[0]

    def subgroup_image_order(self) -> int:
        r"""``|chi(self.subgroup)|``, from the generated image; no image element is listed.

        The joint subgroup's discriminant image equals ``pi_1(Q cap S)`` (with
        an explicit proof at :meth:`_joint_discriminant_image_gap`), and
        ``pi_1|_{Q cap S}`` is injective, so ``|chi(self.subgroup)| = |T_tot|``
        and computing the joint subgroup in the full product model is never
        required here.  Sign-kernel-only data keeps the legacy kernel route.
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
        measured instant at the Enriques size, `.tmp/measure_pathB.log`), and
        letters index the ambient ``O(L)`` generators through ``rho``.

        ``rho`` is evaluated on *every* ambient generator, so this is the one
        computation of ``rho(O(L))`` the quotient schedules: the returned tuple
        is cached per subgroup (hence per lattice), and the callers that need the
        ambient generator images read them from here rather than sweeping the
        generating family again.  On ``T_Co`` one sweep is 26 s of
        ``discriminant_morphism`` constructions
        over 340 generators (`.tmp/p310b-probe1.log`), and the row used to
        schedule four of them before its first lift.
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
        (340 generators on ``T_Co``; 26 s in one sweep, `.tmp/p310b-probe1.log`),
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

    def isotropic_line_stabilizer_image(self, representative):
        r"""Return ``(discriminant image, whether a sign factor is covered)`` for an isotropic line.

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

        **A lattice without two hyperbolic planes is refused.**  The criterion is a
        statement about the lattice it is applied to: the two orthogonal hyperbolic
        planes are its hypothesis *in* ``L`` (Gritsenko--Hulek--Sankaran, Lemma 7.8,
        p. 503).  It is not inherited from an enlargement: on ``L + U`` it classifies
        the ``\widetilde{SO}(L + U)``-orbits of ``L + U``, and the element it
        produces need not preserve ``L``, so the two invariants it compares say
        nothing about the ``O(L)``-orbits of ``L``.  What decides the ``O(L)``-orbit
        of a primitive isotropic ``v`` is the isometry class of
        ``v^\perp/\mathbb{Z} v`` (Conway--Sloane, *Sphere Packings, Lattices and
        Groups*, ch. 16), which the discriminant group of a unimodular ``L`` cannot
        see.  Where the hypothesis is not exhibited the call below returns ``None``
        and the caller keeps its exact integral route.
        Let ``gamma`` belong to ``Stab_{O(A_L)}(c)`` and choose ``g`` in ``O(L)`` above it
        (the character representation is computed by this quotient, so such a lift exists).
        Then ``g(v)`` has the same length and the same normalized class ``c`` as ``v``, so by
        the criterion some ``k`` in ``\widetilde{SO}(L)`` takes ``g(v)`` to ``v``; then
        ``kg`` fixes ``v``, and ``kg`` has the same discriminant image ``gamma``.  That is
        surjectivity of the line stabilizer onto the finite class stabilizer.

        A norm ``-2`` root reflection is *not* used for the sign factor: its discriminant
        image is trivial, so it would be declared a stabilizer member for the wrong reason.
        The sign factor is a separate character and is decided by the subgroup's own
        membership test on a reflection in ``u perpendicular to v`` with ``u.u = 2``; if no
        such witness is exhibited there is no claim about that factor and the caller keeps
        its integral route.  Nothing below returns a partial discriminant image.
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
                    return "NOSPLIT"
        # The criterion's hypothesis is read on ``L`` itself (Gritsenko--Hulek--Sankaran,
        # Lemma 7.8, p. 503): two orthogonal hyperbolic planes in ``L``.  It is not
        # transferred from the enlargement ``L + U``, whose classification is of
        # ``\widetilde{SO}(L + U)``-orbits and whose moving element need not preserve
        # ``L``.  Without the hypothesis the class set below is uncertified, so the
        # call refuses and the caller keeps its exact integral route.
        if not _two_hyperbolic_planes(lattice):
            return None
        discriminant_class = lattice.divided_discriminant_class(vector)
        if discriminant_class == lattice.discriminant_group().zero():
            # Double cosets Gamma \\ im rho / im rho are one coset, *provided* no sign
            # factor remains to be lifted: Stab_{im rho}(0) = im rho, and
            # Eichler's lifting argument takes place inside that image.  The remaining
            # factor is independent: it is met only when no sign label remains or a
            # kernel-sign witness is exhibited.  A full discriminant stabilizer alone
            # would not supply this, so the joint condition below is kept explicit.
            # The factor labels are retained data; do not evaluate _sign_descent_rank
            # here, because that builds im rho through ambient generators again.  Two
            # nontrivial sign factors are beyond the single witness this shortcut proves:
            # one flip covers one sign coset, not a joint two-character image.
            sign_labels = [
                label
                for label, present in (
                    ("determinant", self.determinant_kernel),
                    ("spinor", self.spinor_kernel),
                )
                if present
            ]
            if not sign_labels:
                return "NOSPLIT"
            if len(sign_labels) > 1:
                return None
            # A norm +2 integral root reflection needs no rho evaluation to certify its
            # kernel membership: on a dual class x -> x - b(x,u)u the correction b(x,u)u
            # is a lattice vector, so the class is unchanged.  lattice.reflection has
            # already checked the integral-reflection-vector condition; the remaining
            # sign factor is the only character left to test.
            basis = tuple(lattice.module_generators())
            for index, first in enumerate(basis):
                for second in basis[index + 1 :]:
                    candidate = first + second
                    if candidate.q() != lattice.base_ring()(2):
                        continue
                    if lattice.b(candidate, vector) != lattice.base_ring().zero():
                        continue
                    if lattice.reflection(candidate) not in self.subgroup:
                        return "NOSPLIT"
            for root in lattice.vectors_of_square_and_divisibility(
                lattice.base_ring()(2), lattice.base_ring().one()
            ):
                if lattice.b(root, vector) != lattice.base_ring().zero():
                    continue
                if lattice.reflection(root) not in self.subgroup:
                    return "NOSPLIT"
            return None
        # A joint determinant *and* spinor sign quotient is not certified by one
        # nontrivial reflection: that witness covers one sign coset only, and the
        # remaining coset need not be generated.  Keep the integral joint-character
        # splitting there, with its double cosets in the full joint image, rather than
        # promoting the single flip to a complete stabilizer image.  This is checked
        # before _sign_descent_rank can ask for the ambient engine.
        if self.determinant_kernel and self.spinor_kernel:
            return None
        if not self._has_discriminant:
            # A sign-only character quotient has no im rho at all. This case cannot
            # use the discriminant-stabilizer image, but the same index-two principle
            # applies: one kernel-sign witness certifies that the orbit does not split,
            # so the integral stabilizer is not needed either.
            _rank, sign_labels = self._sign_descent_rank()
            if not sign_labels:
                return "NOSPLIT"
            for root in lattice.vectors_of_square_and_divisibility(
                lattice.base_ring()(2), lattice.base_ring().one()
            ):
                if lattice.b(root, vector) != lattice.base_ring().zero():
                    continue
                if lattice.reflection(root) not in self.subgroup:
                    return "NOSPLIT"
            return None
        discriminant_class = lattice.divided_discriminant_class(vector)
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
        _rank, sign_labels = self._sign_descent_rank()
        if not sign_labels:
            return class_points, False
        # A kernel-sign witness is what certifies splitting here: a reflection in a norm
        # ``+2`` vector orthogonal to the line fixes it, acts trivially on ``A_L``, and has
        # spinor class ``[2] * [-1/2] = [-1]``, outside ``O+``.  That is exactly the missing
        # piece of the sign character when it is *not* lifted; a generator with nontrivial
        # sign and nontrivial discriminant image would only supply a graph, not this witness.
        flip = False
        rho = lattice.discriminant_representation()
        square_two = lattice.base_ring()(2)
        trivial_discriminant = self._discriminant_group.one()
        zero_scalar = lattice.base_ring().zero()
        for root in lattice.vectors_of_square_and_divisibility(square_two, lattice.base_ring().one()):
            if lattice.b(root, vector) != zero_scalar:
                continue
            reflection = lattice.reflection(root)
            if (
                rho(reflection) == trivial_discriminant
                and reflection not in self.subgroup
            ):
                flip = True
                break
        if not flip:
            # No kernel-sign witness is exhibited, so this cannot certify that the sign
            # factor is included in the stabilizer's image: the double-coset machinery
            # needs the integral stabilizer instead of a partial character image.
            return None
        return class_points, flip

    def splitting_isometries_from_line_class(self, class_points, stab_sign_flip):
        r"""Splitting lifts from the rho(Gamma)-orbits on the isotropic class pairs.

        ``class_points`` is the engine set of the normalized discriminant classes
        ``{c, -c}`` of the line's generator, built by
        :meth:`isotropic_line_stabilizer_image`.  Its setwise stabilizer inside
        ``im rho`` is the right-hand group of the double cosets that split the ambient
        line orbit, and those double cosets are computed as the ``rho(Gamma)``-orbits
        on the ``im rho``-orbit of the class set -- the orbit--double-coset bijection
        stated in :meth:`_splitting_isometries_in_im_rho_from_image` -- so the
        stabilizer itself is never formed.

        This is the entry point of :meth:`isotropic_line_stabilizer_image`'s argument:
        it transports by representatives of the cosets of the class stabilizer instead
        of asking for the integral stabilizer's generators.  Every lift is still
        checked against the character map.
        """
        return self._splitting_isometries_in_im_rho_from_image(
            (), stab_sign_flip, point=class_points
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
        # A stabilizer can correlate its signs with its discriminant image.
        # Joint conditions use the full joint image of every supplied generator.
        if self._has_discriminant and not (self.determinant_kernel or self.spinor_kernel):
            return self._splitting_isometries_in_im_rho(stabilizer_generators)
        generators, _images, section = self._image_section()
        to_permutation = section._to_permutation
        permutation_image = section.permutation_group
        # The image of the stabilizer is the subgroup generated by the
        # character images of its retained generators: chi is a homomorphism,
        # so chi(<S>) = <chi(S)>.  No element of the stabilizer's image is
        # listed.
        stabilizer_gap = libgap.Subgroup(
            self._gap_image(),
            [self._gap_of_key(self.image(generator)) for generator in stabilizer_generators],
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
        from sage_extensions.categories.group.groups import _element_to_engine

        rho = self.lattice.discriminant_representation()
        discriminant_image_generators = tuple(
            _element_to_engine(self._discriminant_group, rho(s))
            for s in stabilizer_generators
        )
        return self._splitting_isometries_in_im_rho_from_image(
            discriminant_image_generators, self._stabilizer_sign_flips(stabilizer_generators)
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
        (arXiv:0810.1614v1, Proposition 5.6, p. 17; sage-extensions#17's reading in
        ``results/issue17-kernel-generation-blocker.md``).  Asking for that family is what
        stopped the ``Otilde^+(N)`` row, since ``Otilde(L)`` is an infinite arithmetic group
        with no selected resolution (sage-extensions#310, #339).

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

    def _splitting_isometries_in_im_rho_from_image(
        self, discriminant_image_generators, stab_sign_flip, *, right=None, point=None,
    ):
        r"""Splitting lifts computed inside ``im rho`` (the ``O(A_L)`` engine); see
        :meth:`splitting_isometries` for the exact sign bookkeeping.

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
        if j >= 1 and sign_labels:
            # A sign character that does not descend to im rho is lifted by one explicit
            # element of ker rho, exhibited below; Otilde(L)'s generating family is neither
            # needed nor known (sage-extensions#17, #310).
            for label in sign_labels:
                flip_element = self._kernel_sign_flip(label)
                if flip_element is not None:
                    break
            if len(sign_labels) == 1 and not stab_sign_flip and flip_element is None:
                raise ValueError(
                    f"the stabilizer's discriminant image leaves a sign coset to lift, and no "
                    f"kernel element with nontrivial {sign_labels[0]} is available to lift it: "
                    "a plain sign predicate is not a substitute for a ker(rho) witness"
                )
        representatives = []
        # Words in the rho-images of the ambient generators, via the
        # epimorphism F(S) ->> im rho: PreImagesRepresentative reuses the
        # parent chain, and the letters index the ambient O(L) generators.
        from sage_extensions.categories.group.groups import _law_reversed

        free = libgap.FreeGroup(len(rho_images))
        epi = libgap.GroupHomomorphismByImagesNC(
            free, im_rho, list(free.GeneratorsOfGroup()), rho_images
        )
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
            while frontier:
                following = []
                for reached_point, reached_element in frontier:
                    for generator in rho_images:
                        image = setwise_action(reached_point, generator)
                        marker = str(image)
                        if marker in keys:
                            continue
                        reached = generator * reached_element
                        if setwise_action(point, reached) != image:
                            # The engine product must compose as (g*h)(x) = g(h(x));
                            # the other order carries the start to a different point.
                            reached = reached_element * generator
                            assert setwise_action(point, reached) == image, (
                                "the orbit walk's transversal element does not carry the "
                                "start to the reached point"
                            )
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
                for lift in lifts:
                    image_of_lift = self.image(lift)
                    if image_of_lift["discriminant"] != key_disc:
                        raise ArithmeticError(
                            "splitting lift's discriminant image disagrees with the word section"
                        )
                    representatives.append(lift)
            return finite_ordered_set(tuple(representatives))
        # The double-coset route: retained for callers that hold the integral
        # stabilizer generators and no point of the finite set.
        to_perm = libgap.IsomorphismPermGroup(im_rho)
        im_rho_perm = libgap.Range(to_perm)
        left = libgap.Image(to_perm, self._joint_discriminant_image_gap())
        right = (
            libgap.Subgroup(
                im_rho,
                list(discriminant_image_generators),
            )
            if right is None
            else right
        )
        right_perm = libgap.Image(to_perm, right)
        _dcs = libgap.AsList(libgap.DoubleCosets(im_rho_perm, left, right_perm))
        for _n, double_coset in enumerate(_dcs):
            owned = self._owned_coset_representative(libgap.Representative(double_coset))
            element = libgap.PreImagesRepresentative(to_perm, owned)
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
            for lift in lifts:
                image_of_lift = self.image(lift)
                if image_of_lift["discriminant"] != key_disc:
                    raise ArithmeticError(
                        "splitting lift's discriminant image disagrees with the word section"
                    )
                representatives.append(lift)
        return finite_ordered_set(tuple(representatives))

    def witness_meets_subgroup(self, witness, stabilizer_generators) -> bool:
        return self.adjust_witness_into_subgroup(witness, stabilizer_generators) is not None

    def adjust_witness_into_subgroup(self, witness, target_stabilizer_generators):
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

        product = self._gap_product()[1]
        to_permutation = libgap.IsomorphismPermGroup(product)
        permutation_product = libgap.Range(to_permutation)
        point = libgap.Image(to_permutation, self._gap_of_key(self.image(witness)))
        stabilizer_generators = tuple(target_stabilizer_generators)
        stabilizer_gaps = [
            self._gap_of_key(self.image(generator)) for generator in stabilizer_generators
        ]
        stabilizer_gap = libgap.Subgroup(product, stabilizer_gaps)
        stabilizer_permutation = libgap.Image(to_permutation, stabilizer_gap)
        subgroup_permutation = libgap.Image(to_permutation, self._gap_character_target())
        reversed_product = _law_reversed(self._model_factors()[0][1])
        # For a reversed model, chi(t*g) is a*w. Choose u in S*a
        # intersect W and set w=u^-1, so a*w lies in S. For a model
        # preserving products, choose w directly from S*a^-1 intersect W.
        candidates = libgap.Intersection(
            stabilizer_permutation,
            libgap.RightCoset(subgroup_permutation, point if reversed_product else point ** -1),
        )
        if bool(libgap.IsEmpty(candidates)):
            return None
        chosen = libgap.Representative(candidates)
        if reversed_product:
            chosen = chosen ** -1
        # Factor the chosen stabilizer image over the stabilizer's own
        # generators, so the adjustment is a live element of the stabilizer.
        stabilizer_section = _GapWordSection(
            [libgap.Image(to_permutation, element) for element in stabilizer_gaps],
            parent=permutation_product,
        )
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
        expected = self._key_of_gap(
            libgap.PreImagesRepresentative(to_permutation, chosen)
        )
        if self.image(adjustment) != expected:
            raise ArithmeticError(
                f"the stabilizer word-section of {self.subgroup} was checked against the "
                f"character map: the evaluation induces {self.image(adjustment)} where the "
                f"chosen quotient element is {expected}, so the retained word section is "
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
            _subgroup_from_gap,
        )

        if not (self.determinant_kernel and self.spinor_kernel):
            return _subgroup_from_gap(
                self._discriminant_group, self._joint_discriminant_image_gap()
            )
        factors, _product, _embeddings, projections = self._gap_product()
        position = next(
            index for index, (label, _group) in enumerate(factors) if label == "discriminant"
        )
        projected = libgap.Image(projections[position], self._gap_subgroup())
        return _subgroup_from_gap(self._discriminant_group, projected)

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

    def image(self):
        r"""Return ``\rho(\Gamma)`` as the ``O(A_L)`` engine subgroup the chain is of."""
        return self._image

    def contains(self, isometry) -> bool:
        r"""Whether the isometry of ``O(A_L)`` lies in ``\rho(\Gamma)``."""
        from sage_extensions.categories.group.groups import _element_to_engine

        return bool(
            _element_to_engine(self._discriminant_group, isometry) in self._image
        )

    def __contains__(self, isometry) -> bool:
        return self.contains(isometry)


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
            name=f"Square-zero orbit representatives of {subgroup}",
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
    primitive vectors of fixed length by norm and normalized discriminant class in a
    lattice with two orthogonal hyperbolic planes.  For norm zero those are exactly the
    *line* orbits, once ``v`` and ``-v`` are identified by the class set ``{c, -c}``:
    their normalized class is the whole invariant.  This function constructs one
    integral representative for *every* candidate class, before any integral orbit
    enumeration is attempted.  If a candidate class cannot be exhibited physically the
    construction returns ``None`` and the caller falls back to its integral route --
    a partial finite family is never returned as if it were the line set.
    """
    if not _two_hyperbolic_planes(lattice):
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


def _two_hyperbolic_planes(lattice):
    r"""Whether two orthogonal unimodular hyperbolic planes are exhibited in the chosen basis.

    Eichler's criterion (Gritsenko--Hulek--Sankaran, *Moduli of K3 Surfaces and Irreducible
    Symplectic Manifolds*, Lemma 7.8, p. 503) needs that hypothesis; where the retained basis
    does not exhibit it the caller keeps the exact integral route, so the hypothesis is only
    ever entered on a detectable basis, never assumed.
    """
    generators = tuple(lattice.module_generators())
    isotropic = [v for v in generators if v.q() == lattice.base_ring().zero()]
    planes = []
    zero = lattice.base_ring().zero()
    for e in isotropic:
        for f in isotropic:
            pairing = lattice.b(e, f)
            if pairing not in (1, -1):
                continue
            if all(
                lattice.b(e, other) == zero and lattice.b(f, other) == zero
                for predecessor in planes
                for other in predecessor
            ):
                planes.append((e, f))
                break
    return len(planes) >= 2


def _line_orbit_from_divided_classes(subgroup, representative):
    r"""The ``ker rho`` line orbits as divided classes, or ``None`` when the split is not one.

    Let ``G = O(L)``, ``H = Stab_G(x)`` for the line ``x``, ``Gamma = ker rho`` and
    ``c = [v/div v]`` for a generator ``v`` of ``x``.  Because ``Gamma`` is normal in ``G``
    and equal to the kernel of ``rho``, the double cosets ``Gamma \\ G / H`` correspond
    bijectively to the cosets ``rho(G)/rho(H)`` -- orbit--stabilizer for the action of the
    quotient ``G/ker rho``, which acts through ``rho`` -- and the map ``Gamma g x |-> rho(g) c``
    sends an orbit to its class, with fibre over ``c`` of size
    ``[Stab_(rho(G))(c) : rho(H)]``.

    When that index is 1 -- computed here from the two exact images, not assumed -- the
    ``Gamma``-orbits in ``G x`` are in bijection with the classes of ``rho(G) c``, and a
    representative of each orbit is *any* primitive isotropic line with that divided class, so
    no isometry is needed: the lines come from
    ``Lattices.ParentMethods.primitive_isotropic_vector_of_divided_class``.  An index greater
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
    image_of_group = subgroup.supergroup().discriminant_image()
    image_of_stabilizer = representative.stabilizer_discriminant_image()
    order = image_of_group.cardinality().finite_value()
    stabilizer_order = image_of_stabilizer.cardinality().finite_value()
    if order % stabilizer_order:
        raise ArithmeticError(
            f"the discriminant image of the stabilizer of {representative!r} has order "
            f"{stabilizer_order}, which does not divide the order {order} of the image of "
            f"{subgroup.supergroup()}; the stabilizer's image must lie in the group's image"
        )
    # The class orbit in the order the walk reaches it, so the representatives this
    # function returns are the same tuple on every call: a set's iteration order is
    # not a datum a comparison against a recorded list can be made against.
    seen = {lattice.divided_discriminant_class(vector)}
    class_orbit = [lattice.divided_discriminant_class(vector)]
    frontier = [lattice.divided_discriminant_class(vector)]
    while frontier:
        current = frontier.pop()
        for generator in image_of_group.group_generators():
            moved = generator(current)
            if moved not in seen:
                seen.add(moved)
                class_orbit.append(moved)
                frontier.append(moved)
    if order % len(class_orbit):
        raise ArithmeticError(
            f"the class orbit of {representative!r} has {len(class_orbit)} elements, which does "
            f"not divide the order {order} of the discriminant image of {subgroup.supergroup()}"
        )
    index_per_class = (order // len(class_orbit)) // stabilizer_order
    if index_per_class != 1:
        return None
    # One construction for the whole orbit: the residue loop asks for the orbit's
    # classes together, so it fixes their residues in one pass over the translations
    # instead of one search per class (which would rebuild the search 527 times on
    # ``T_Co``, where the class orbit is the 527 nonzero isotropic classes).
    vectors = lattice.isotropic_lines_by_divided_class(divisor, classes=tuple(class_orbit))
    missing = tuple(component for component in class_orbit if component not in vectors)
    if missing:
        raise ValueError(
            f"the divided classes of the line orbit of {representative!r} in {lattice!r} are not "
            f"all realized at divisor {divisor}: {len(missing)} of the {len(class_orbit)} classes "
            f"have no primitive isotropic vector there, the first being {missing[0]}.  The "
            f"divided-class route supplies one representative per class or none, so this refuses "
            f"rather than returning a short family"
        )
    return tuple(
        lattice.primitive_isotropic_subobject(vectors[component])
        for component in class_orbit
    )


def _subgroup_isotropic_orbit_representatives(subgroup, rank, *, flag=False):
    if not flag and index(rank) == 0:
        return subgroup.supergroup().isotropic_orbit_representatives(0)
    _assert_isotropic_splitting_has_character_data(subgroup)
    quotient = subgroup.finite_character_quotient()
    orthogonal_group = subgroup.supergroup()
    representatives = []
    # The ambient classes always come from the port's classification: the
    # in-repo discriminant-class route exhibits its representatives by an
    # integral-point enumeration that does not return on the Enriques lattice
    # (its Normaliz walk is measured at over twenty minutes before failing),
    # while the port's line route answers the same classes in tens of seconds.
    sourced = orthogonal_group.isotropic_orbit_representatives(rank, flag=flag)
    for representative in sourced:
        line_image = (
            quotient.isotropic_line_stabilizer_image(representative)
            if not flag and rank == 1
            else None
        )
        if line_image == "NOSPLIT":
            # The sign witness (or trivial quotient) proves G_0 = G Stab(x) for its index.
            representatives.append(representative)
            continue
        if line_image is not None:
            representatives.extend(
                splitting.transport_isotropic_object(representative)
                for splitting in quotient.splitting_isometries_from_line_class(*line_image)
            )
            continue
        if not flag and index(rank) == 1:
            from_divided_classes = _line_orbit_from_divided_classes(subgroup, representative)
            if from_divided_classes is not None:
                representatives.extend(from_divided_classes)
                continue
        stabilizer = orthogonal_group.isotropic_stabilizer_generators(
            representative, flag=flag
        )
        representatives.extend(
            splitting.transport_isotropic_object(representative)
            for splitting in quotient.splitting_isometries(stabilizer)
        )
    return finite_ordered_set(tuple(representatives))


def _subgroup_isotropic_equivalence_witness(subgroup, left, right, *, flag=False):
    orthogonal_group = subgroup.supergroup()
    witness = orthogonal_group.isotropic_equivalence_witness(
        left, right, flag=flag
    )
    if witness is None:
        return None
    if witness in subgroup:
        return witness
    _assert_isotropic_splitting_has_character_data(subgroup)
    stabilizer = orthogonal_group.isotropic_stabilizer_generators(
        right, flag=flag
    )
    return subgroup.finite_character_quotient().adjust_witness_into_subgroup(
        witness, stabilizer
    )


__all__ = ["OrthogonalCharacterQuotient"]
