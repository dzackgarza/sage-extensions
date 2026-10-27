r"""Rational polyhedral fans in a cocharacter lattice.

A fan \(\Sigma\) in \(N_{\mathbb R}\) is a finite set of strongly convex
rational polyhedral cones, closed under taking faces and pairwise
intersections (Cox--Little--Schenck, *Toric Varieties*, Def. 3.1.2).  The
fan is the object; its cones are its elements.  The lattice \(N\) is an
owned free \(\mathbb Z\)-module of finite rank, and every ray generator is
an element of \(N\).

Sage's ``Fan`` and ``Cone`` are the private polyhedral computation engine.
"""

from sage.structure.element import parent as element_parent
from sage.geometry.cone import Cone as _SageCone
from sage.geometry.fan import Fan as _SageFan
from sage.geometry.toric_lattice import ToricLattice as _SageToricLattice
from sage.misc.cachefunc import cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.structure.element import Element

from sage_extensions.categories.abstract_categories.objects import (
    OwnedParameterizedCategory,
)
from sage_extensions.categories.modules.pure.modules import (
    BilinearMap,
    FinitelyGeneratedFreeModules,
)
from sage_extensions.categories.rings.ring_foundation import (
    _own_ring,
    _owned_integers,
)
from sage_extensions.categories.sets.cardinals import cardinal
from sage_extensions.categories.sets.finite_ordered_sets import finite_ordered_set
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
)
from sage_extensions.categories.sets.set_categories import FiniteSets
from sage_extensions.owned_category import _object_of


def _integers():
    return _owned_integers()


def _engine_lattice(module):
    r"""Sage's toric lattice of the same rank, the engine coordinate space."""
    return _SageToricLattice(int(module.module_rank()), "N")


def _engine_vector(module, element):
    r"""Coordinates of an owned free-module element in its chosen frame."""
    coordinates = module(element).to_vector()
    return _engine_lattice(module)(
        [int(coordinates(label)) for label in module.module_generating_set()]
    )


def _owned_vector(module, coordinates):
    r"""The element of the owned module with the stated frame coordinates."""
    integers = _integers()
    return module.linear_combination(
        {
            label: integers(int(coordinate))
            for label, coordinate in zip(module.module_generating_set(), coordinates, strict=True)
            if int(coordinate) != 0
        }
    )


def _engine_fan(fan):
    r"""Return a fan's private Sage realization to a toric-engine adapter.

    Protected fan contract (\`OWN-05\`--\`OWN-07\`).  The implementing
    endpoint is \`RationalPolyhedralFans.ParentMethods._engine_fan\`.
    Permitted callers are the toric-scheme adapters that must construct a Sage
    toric variety, Sage fan morphism, or Sage Chow-class computation after the
    owned fan operation has been selected.  The returned fan remains inside
    that adapter.
    """
    return fan._engine_fan()


def _engine_cone(cone):
    r"""Return a cone's private Sage realization to a toric-engine adapter.

    Protected cone contract paired with :func:\`_engine_fan\`.  The
    implementing endpoint is \`RationalPolyhedralFans.ElementMethods._engine_cone\`;
    permitted callers are maintained Sage adapters whose selected operation
    requires this cone object.  The raw cone does not become mathematical
    output.
    """
    return cone._engine_cone()


def _cone_key(engine_cone):
    return frozenset(tuple(int(c) for c in ray) for ray in engine_cone.rays())


class RationalPolyhedralFans(OwnedParameterizedCategory):
    r"""Fans of strongly convex rational polyhedral cones in one lattice ``N``.

    The parameter is the cocharacter lattice ``N``, an owned finitely
    generated free ``ZZ``-module.  A fan is a finite set whose elements are
    its cones, so the category refines finite sets.
    """

    def parameter_category(self):
        r"""A fan lives in one finitely generated free ``ZZ``-module."""
        return FinitelyGeneratedFreeModules(_integers())

    def an_object(self):
        r"""The fan of projective space of the lattice's rank."""
        return self.projective_space_fan()

    def lattice(self):
        return self.base()

    cocharacter_lattice = lattice

    @cached_method
    def character_lattice(self):
        r"""The character lattice ``M`` of the torus ``T_N`` (CLS §1.1).

        ``M`` is the dual module of ``N``, and its frame is the dual frame of
        the chosen frame of ``N``.
        """
        return self.lattice().dual_module()

    @cached_method
    def character_cocharacter_pairing(self):
        r"""The perfect evaluation pairing ``<-,->: M ⊗ N -> ZZ`` (CLS (1.1.2)).

        This is the duality of the two lattices, ``<m, u> = m(u)`` on the
        frames.  It is not a form on either of them: a positive form a session
        may additionally put on ``N`` is a different morphism, out of the
        tensor square of ``N``.
        """
        characters = self.character_lattice()
        cocharacters = self.lattice()
        integers = _integers()
        values = integers.regular_module()
        return BilinearMap(
            characters,
            cocharacters,
            values,
            lambda character_label, cocharacter_label: integers(
                characters.module_generator(character_label)(
                    cocharacters.module_generator(cocharacter_label)
                )
            ),
        )

    def character_cocharacter_value(self, character, cocharacter):
        r"""Return the scalar integer ``<character, cocharacter>``.

        The bilinear classifier above lands in the rank-one module underlying
        ``ZZ``.  Toric valuations use its scalar coefficient, which is extracted
        here at the pairing owner rather than independently by each consumer.
        """
        pairing = self.character_cocharacter_pairing()
        values = pairing.codomain()
        labels = values.module_generating_set()
        assert labels.cardinality() == 1, (
            f"the pairing of characters with cocharacters of {self} must take values in ZZ, a "
            f"free module of rank 1, but it takes values in {values} of rank {labels.cardinality()}"
        )
        (label,) = labels
        integers = _integers()
        return integers(pairing(character, cocharacter).to_vector()(label))

    def _repr_object_names(self):
        return f"rational polyhedral fans in {self.lattice()}"

    def super_categories(self):
        return [FiniteSets()]

    def _call_(self, maximal_cones):
        r"""The fan generated by a family of cones, each given by its rays.

        Every ray is an element of ``N`` (frame coordinates are accepted as
        syntactic ingress).  The cones are closed under faces and
        intersections by construction of the fan; the engine refuses a
        family whose cones do not intersect in common faces.
        """
        lattice = self.lattice()
        engine_lattice = _engine_lattice(lattice)
        engine_cones = []
        for rays in maximal_cones:
            engine_rays = []
            for ray in rays:
                element = ray if ray in lattice else _owned_vector(lattice, ray)
                engine_rays.append(_engine_vector(lattice, element))
            engine_cones.append(_SageCone(engine_rays, lattice=engine_lattice))
        if not engine_cones:
            engine_cones = [_SageCone([], lattice=engine_lattice)]
        return _object_of(self, engine_fan=_SageFan(engine_cones, lattice=engine_lattice))

    def _from_engine_fan(self, engine_fan):
        r"""Adopt one engine fan whose lattice rank matches ``N``."""
        assert int(engine_fan.lattice_dim()) == int(self.lattice().module_rank()), (
            f"a fan in {self} lives in the lattice N = {self.lattice()} of rank "
            f"{self.lattice().module_rank()}, but this fan lives in a lattice of rank "
            f"{engine_fan.lattice_dim()}"
        )
        return _object_of(self, engine_fan=engine_fan)

    @cached_method
    def trivial_fan(self):
        r"""The fan whose only cone is the origin: the fan of the torus ``T_N``."""
        return self(())

    @cached_method
    def projective_space_fan(self):
        r"""The fan of ``P^n`` (CLS Example 3.1.10): rays ``e_1,...,e_n`` and ``-sum e_i``."""
        lattice = self.lattice()
        labels = lattice.module_generating_set()
        integers = _integers()
        rays = finite_ordered_set(
            tuple(lattice.module_generator(label) for label in labels)
            + (lattice.linear_combination({label: -integers.one() for label in labels}),)
        )
        return self(
            tuple(
                tuple(ray for ray in rays if ray != omitted) for omitted in rays
            )
        )

    @cached_method
    def weighted_projective_space_fan(self, weights):
        r"""The fan of ``P(q_0,...,q_n)`` for the stated weights (CLS Example 3.1.17).

        The rays are the images of the standard basis of ``ZZ^{n+1}`` under
        the quotient by ``(q_0,...,q_n)``, and the maximal cones omit one ray
        each.  The quotient presentation is Sage's, in
        ``sage.schemes.toric.library.toric_varieties.WP``.
        """
        from sage.schemes.toric.library import toric_varieties

        # The weights are a family indexed by the homogeneous coordinates, so
        # they are presented by the graph of that family: pairing each weight
        # with its coordinate keeps repeated weights apart, which a set of the
        # weights alone would not.
        homogeneous_weights = finite_ordered_set(
            tuple(enumerate(int(weight) for weight in weights))
        )
        assert all(weight > 0 for _, weight in homogeneous_weights), (
            f"the weights of a weighted projective space P(q_0, ..., q_n) must be positive, but "
            f"they are {tuple(weights)}"
        )
        assert homogeneous_weights.cardinality() == int(self.lattice().module_rank()) + 1, (
            f"P(q_0, ..., q_n) in the lattice {self.lattice()} of rank "
            f"{self.lattice().module_rank()} needs {int(self.lattice().module_rank()) + 1} weights, "
            f"but {homogeneous_weights.cardinality()} were given"
        )
        return self._from_engine_fan(
            toric_varieties.WP(
                *(weight for _, weight in homogeneous_weights)
            ).fan()
        )

    @cached_method
    def hirzebruch_surface_fan(self, twist):
        r"""The fan of the Hirzebruch surface ``F_a`` (CLS Example 3.1.16).

        The rays are ``e_1``, ``e_2``, ``-e_1 + a e_2`` and ``-e_2``; the four
        maximal cones are the consecutive pairs.  ``F_0`` is ``P^1 x P^1`` and
        ``F_1`` is the blow-up of ``P^2`` at one point.
        """
        lattice = self.lattice()
        assert int(lattice.module_rank()) == 2, (
            f"a Hirzebruch surface F_a is a toric surface, so its fan lives in a lattice of rank 2, "
            f"but {lattice} has rank {lattice.module_rank()}"
        )
        integers = _integers()
        twist = integers(twist)
        first, second = tuple(lattice.module_generating_set())
        u1 = lattice.module_generator(first)
        u2 = lattice.module_generator(second)
        u3 = lattice.linear_combination({first: -integers.one(), second: twist})
        u4 = lattice.linear_combination({second: -integers.one()})
        return self(((u1, u2), (u2, u3), (u3, u4), (u4, u1)))

    class ParentMethods:
        def __init__(self, engine_fan, **rest) -> None:
            self._fan_engine = engine_fan
            super().__init__(**rest)

        def _engine_fan(self):
            r"""The private polyhedral computation object; see :func:\`_engine_fan\`."""
            return self._fan_engine

        def lattice(self):
            r"""The cocharacter lattice ``N`` this fan lives in."""
            return self.category().lattice()

        cocharacter_lattice = lattice

        def character_lattice(self):
            r"""The character lattice ``M`` of the torus of this fan."""
            return self.category().character_lattice()

        def character_cocharacter_pairing(self):
            r"""The perfect pairing ``M ⊗ N -> ZZ`` of the torus of this fan."""
            return self.category().character_cocharacter_pairing()

        def character_cocharacter_value(self, character, cocharacter):
            r"""Return the scalar integer ``<character, cocharacter>``."""
            return self.category().character_cocharacter_value(character, cocharacter)

        def dimension(self):
            r"""The rank of ``N``, which is the dimension of the toric variety."""
            return _integers()(int(self.lattice().module_rank()))

        def _cone(self, engine_cone):
            return self.element_class(self, engine_cone)

        @cached_method
        def cones(self, dimension):
            r"""The cones of the stated dimension, as a finite ordered set."""
            return finite_ordered_set(
                tuple(self._cone(cone) for cone in self._engine_fan().cones(int(dimension)))
            )

        @cached_method
        def maximal_cones(self):
            return finite_ordered_set(
                tuple(self._cone(cone) for cone in self._engine_fan().generating_cones())
            )

        @cached_method
        def rays(self):
            r"""The primitive ray generators, as elements of ``N``."""
            lattice = self.lattice()
            return finite_ordered_set(
                tuple(_owned_vector(lattice, ray) for ray in self._engine_fan().rays())
            )

        def __iter__(self):
            for dimension in range(int(self.dimension()) + 1):
                for cone in self._engine_fan().cones(dimension):
                    yield self._cone(cone)

        def cardinality(self):
            r"""The number of cones, the origin included."""
            return sum(
                (
                    self.cones(dimension).cardinality()
                    for dimension in range(int(self.dimension()) + 1)
                ),
                cardinal(0),
            )

        def __contains__(self, candidate) -> bool:
            return candidate.parent() is self

        def is_complete(self) -> bool:
            r"""Whether the cones cover ``N_R`` (CLS Def. 3.1.18)."""
            return bool(self._engine_fan().is_complete())

        def is_smooth(self) -> bool:
            r"""Whether every cone is generated by part of a basis of ``N`` (CLS Def. 1.2.16)."""
            return bool(self._engine_fan().is_smooth())

        def is_simplicial(self) -> bool:
            return bool(self._engine_fan().is_simplicial())

        def is_isomorphic(self, other) -> bool:
            r"""Whether a lattice isomorphism carries this fan onto ``other``.

            By CLS Thm 3.3.4 such an isomorphism induces an isomorphism of the
            two toric varieties over any base, so this decides the standard
            identifications instead of recognizing ray coordinates.  The
            search is Sage's ``fan_isomorphism`` in ``sage.geometry.fan``.
            """
            return bool(self._engine_fan().is_isomorphic(other._engine_fan()))

        def is_compatible_with(self, lattice_morphism, codomain_fan) -> bool:
            r"""Whether ``phi`` carries every cone of this fan into a cone of ``codomain_fan``.

            This is the compatibility of CLS Def. 3.3.1, the condition under
            which ``phi: N -> N'`` induces a toric morphism.  Every cone of a
            fan is a face of a maximal cone, and a cone lies in a convex cone
            exactly when its ray generators do, so ``phi`` is compatible
            exactly when each maximal cone has a maximal cone of
            ``codomain_fan`` containing the images of its rays.
            """
            return all(
                codomain_fan.maximal_cone_containing_image(lattice_morphism, cone)
                is not None
                for cone in self.maximal_cones()
            )

        def maximal_cone_containing_image(self, lattice_morphism, source_cone):
            r"""A maximal cone of this fan containing ``phi(sigma)``, or ``None``.

            ``phi(sigma)`` is the cone spanned by the images of the ray
            generators of ``sigma``, so it lies in a cone ``tau`` exactly when
            every such image does (CLS Def. 3.3.1).  The first maximal cone of
            this fan, in its chosen order, containing them is returned.
            """
            return next(
                (
                    candidate
                    for candidate in self.maximal_cones()
                    if all(
                        candidate.contains(lattice_morphism(ray))
                        for ray in source_cone.rays()
                    )
                ),
                None,
            )

        def toric_variety(
            self,
            base_ring,
            *,
            polarizing_polytope=None,
            placements=(),
            **level_data,
        ):
            r"""Return ``X_Sigma`` over the stated base.

            ``polarizing_polytope`` is selected construction data when this fan
            was obtained as the normal fan of a lattice polytope.
            ``placements`` are further categories the variety is an object of
            by its construction (a star subdivision is an object of
            ``ToricFixedPointBlowups(k)``), with the level data they declare.
            """
            from sage_extensions.categories.schemes.toric.toric_schemes import (
                _toric_variety,
            )

            return _toric_variety(
                self,
                base_ring,
                polarizing_polytope=polarizing_polytope,
                placements=placements,
                **level_data,
            )

        def _repr_(self) -> str:
            return (
                f"Fan in {self.lattice()} with {self.rays().cardinality()} rays "
                f"and {self.maximal_cones().cardinality()} maximal cones"
            )

    class ElementMethods(Element):
        r"""A cone of the fan."""

        def __init__(self, parent, engine_cone) -> None:
            self._cone_engine = engine_cone
            super().__init__(parent)

        def _engine_cone(self):
            r"""The private cone computation object; see :func:\`_engine_cone\`."""
            return self._cone_engine

        def lattice(self):
            return self.parent().lattice()

        def dimension(self):
            return _integers()(int(self._engine_cone().dim()))

        def rays(self):
            r"""The primitive ray generators of this cone, as elements of ``N``."""
            lattice = self.lattice()
            return finite_ordered_set(
                tuple(_owned_vector(lattice, ray) for ray in self._engine_cone().rays())
            )

        def is_smooth(self) -> bool:
            return bool(self._engine_cone().is_smooth())

        def is_simplicial(self) -> bool:
            return bool(self._engine_cone().is_simplicial())

        def faces(self, dimension):
            r"""The faces of the stated dimension, as cones of the same fan."""
            fan = self.parent()
            return finite_ordered_set(
                tuple(fan._cone(face) for face in self._engine_cone().faces(int(dimension)))
            )

        def is_face_of(self, other) -> bool:
            assert other.parent() is self.parent(), (
                f"whether {self} is a face of {other} is decided for cones of one fan, but they "
                f"lie in {self.parent()} and {other.parent()}"
            )
            return bool(self._engine_cone().is_face_of(other._engine_cone()))

        def intersection(self, other):
            r"""``sigma cap tau``, a cone of the same fan (CLS Def. 3.1.2).

            A fan is closed under pairwise intersections and the intersection
            of two of its cones is a face of each, so this is the common face
            along which their two affine charts are glued.
            """
            assert other.parent() is self.parent(), (
                f"the intersection of {self} and {other} is taken for cones of one fan, but they "
                f"lie in {self.parent()} and {other.parent()}"
            )
            return self.parent()._cone(
                self._engine_cone().intersection(other._engine_cone())
            )

        def contains(self, element) -> bool:
            return bool(self._engine_cone().contains(_engine_vector(self.lattice(), element)))

        def relative_interior_contains(self, element) -> bool:
            return bool(
                self._engine_cone().relative_interior_contains(
                    _engine_vector(self.lattice(), element)
                )
            )

        def character_lattice(self):
            r"""The character lattice ``M`` the dual cone lives in."""
            return self.parent().character_lattice()

        @cached_method
        def semigroup_generators(self):
            r"""The Hilbert basis of ``S_sigma = sigma^vee cap M`` (CLS Prop. 1.2.17).

            This finite set generates the affine semigroup whose semigroup
            algebra is the coordinate algebra of the affine chart ``U_sigma``.
            Gordan's lemma is what makes it finite; the Hilbert-basis
            computation is Sage's ``Cone.Hilbert_basis``.
            """
            characters = self.character_lattice()
            return finite_ordered_set(
                tuple(
                    _owned_vector(characters, generator)
                    for generator in self._engine_cone().dual().Hilbert_basis()
                )
            )

        def semigroup_coefficients(self, character):
            r"""The multiplicities writing ``m`` over the chosen generators of ``S_sigma``.

            Every ``m`` in ``S_sigma`` is a nonnegative integer combination of
            the Hilbert basis, so the character ``chi^m`` is the corresponding
            monomial in the chart's coordinate algebra.  The Hilbert basis need
            not be linearly independent, so the multiplicities are not unique;
            two expansions of one ``m`` differ by the toric ideal and name the
            same element of ``k[S_sigma]``.  The integer program that selects
            one is Sage's ``Cone.Hilbert_coefficients``.
            """
            assert self.dual_cone_contains(character), (
                f"the character {character} is not in the dual cone of {self}, so it is not in "
                "the semigroup S_sigma and has no expansion in its generators"
            )
            integers = _integers()
            generators = self.semigroup_generators()
            multiplicities = self._engine_cone().dual().Hilbert_coefficients(
                list(_engine_vector(self.character_lattice(), character))
            )
            return finite_indexed_family(
                generators,
                lambda generator: integers(
                    int(multiplicities[int(generators.ranking_map()(generator))])
                ),
                name="Semigroup multiplicities of a character",
            )

        @cached_method
        def face_supporting_generators(self, face):
            r"""The chosen generators of ``S_sigma`` that vanish on the face ``tau`` (CLS Prop. 1.3.16).

            They generate the face \(\sigma^\vee\cap\tau^\perp\) of \(\sigma^\vee\).  The
            set is determined by the two cones, so it is computed once per face.
            """
            assert face.is_face_of(self), f"{face} is not a face of {self}"
            return finite_ordered_set(
                tuple(
                    generator
                    for generator in self.semigroup_generators()
                    if face.orthogonal_contains(generator)
                )
            )

        @cached_method
        def face_supporting_character(self, face):
            r"""The character ``m`` with ``sigma cap m^perp = tau`` (CLS Prop. 1.3.16).

            The sum of the chosen generators of \(S_\sigma\) that vanish on
            \(\tau\): their sum lies in the relative interior of
            \(\sigma^\vee\cap\tau^\perp\), so \(\sigma\cap m^\perp=\tau\).
            """
            return sum(self.face_supporting_generators(face), self.character_lattice().zero())

        def pair_with(self, character):
            r"""The evaluation ``<m, -> `` of a character on this cone's rays.

            Returned as the finite ordered set of values ``<m, u>``, one for
            each primitive ray generator ``u`` of the cone.
            """
            return finite_ordered_set(
                tuple(
                    self.parent().character_cocharacter_value(character, ray)
                    for ray in self.rays()
                )
            )

        def dual_cone_contains(self, character) -> bool:
            r"""Whether ``m`` is in ``sigma^vee``, i.e. ``<m,u> >= 0`` on every ray."""
            zero = _integers().zero()
            return all(value >= zero for value in self.pair_with(character))

        def orthogonal_contains(self, character) -> bool:
            r"""Whether ``m`` is in ``sigma^perp``, i.e. ``<m,u> = 0`` on every ray."""
            zero = _integers().zero()
            return all(value == zero for value in self.pair_with(character))

        def __eq__(self, other) -> bool:
            return (
                element_parent(other) is self.parent()
                and _cone_key(self._engine_cone()) == _cone_key(other._engine_cone())
            )

        def __ne__(self, other) -> bool:
            return not self == other

        def __hash__(self) -> int:
            return hash(_cone_key(self._engine_cone()))

        def _repr_(self) -> str:
            return f"{self.dimension()}-dimensional cone with rays {self.rays()}"


__all__ = ["RationalPolyhedralFans"]
