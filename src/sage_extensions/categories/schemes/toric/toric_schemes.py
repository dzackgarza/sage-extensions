r"""Toric schemes: schemes built from a fan in a cocharacter lattice.

A toric variety is a normal separated variety \(X\) containing a torus
\(T_N\) as a dense open subset, with the torus action on itself extending to
\(X\).  Every such \(X\) of finite type comes from a fan \(\Sigma\) in
\(N_{\mathbb R}\) (Cox--Little--Schenck, *Toric Varieties*, Cor. 3.1.8), and
the fan is the datum this layer constructs from.

Membership is a fact about how the object was built, never a recognition of
ray coordinates: an object of ``ToricSchemes(k)`` carries its fan, and the
standard identifications (``P^n``, ``P^1 x P^1``, a Hirzebruch surface, a
weighted projective space) are decided by an isomorphism of fans, which by
CLS Thm 3.3.4 is an isomorphism of the varieties.

The affine charts are constructed here, not read off a backend: the chart of
a cone is ``Spec`` of the semigroup algebra of \(S_\sigma=\sigma^\vee\cap M\),
and a face inclusion \(\tau\preceq\sigma\) is realized as the distinguished
open of the chart of \(\sigma\) at one monomial (CLS Prop. 1.3.16).  The
variety is the scheme glued from the charts of the maximal cones along the
transitions of their pairwise intersections, so what a session receives is an
owned glued scheme; Sage's ``ToricVariety`` stays as the private space the
fan-morphism construction computes in.

A transition is the content the charts do not already carry.  Two charts meet
in the chart of \(\gamma=\sigma\cap\tau\), presented on one side as
\(k[S_\sigma][1/\chi^{m_\sigma}]\) and on the other as
\(k[S_\tau][1/\chi^{m_\tau}]\).  Sending each chosen semigroup generator of
\(S_\tau\) to its character on the overlap gives a morphism into the whole
chart \(U_\tau\) that inverts \(\chi^{m_\tau}\), and the universal property of
the localization factors it uniquely through the open.  Reading a character of
\(S_\gamma\) inside \(k[S_\sigma][1/\chi^{m_\sigma}]\) uses
\(S_\gamma=S_\sigma+\mathbb Z_{\ge 0}(-m_\sigma)\), which is the same
Prop. 1.3.16.
"""

from itertools import combinations

from sage.matrix.constructor import matrix as _engine_matrix
from sage.misc.cachefunc import cached_function, cached_method
from sage.rings.integer_ring import ZZ as SageZZ
from sage.rings.rational_field import QQ as SageQQ
from sage.schemes.toric.variety import ToricVariety as _SageToricVariety

from sage_extensions.categories.algebras.algebras import Algebras
from sage_extensions.categories.algebras.semigroup_algebras import (
    AffineSemigroupAlgebras,
)
from sage_extensions.categories.divisors.chow_groups import (
    ChowGroups,
    TorusInvariantCycleGroups,
)
from sage_extensions.categories.divisors.class_groups import ClassGroups
from sage_extensions.categories.divisors.weil_divisor_groups import (
    WeilDivisorGroups,
)
from sage_extensions.categories.modules.pure.modules import BilinearMap
from sage_extensions.categories.rings.ring_foundation import (
    OwnedCategoryOverBaseRing,
    OwnedFields,
    OwnedIntegralDomains,
    _engine_ring,
    _own_ring,
    _owned_engine_element,
    _owned_integers,
)
from sage_extensions.categories.schemes.schemes import (
    Schemes,
    _engine_scheme,
    _scheme_mor_category,
)
from sage_extensions.categories.schemes.toric.fans import (
    RationalPolyhedralFans,
    _engine_cone,
    _engine_fan,
    _engine_vector,
    _owned_vector,
)
from sage_extensions.categories.schemes.varieties import (
    Curves,
    Surfaces,
    Varieties,
)
from sage_extensions.categories.sets.finite_ordered_sets import (
    FiniteOrderedSets,
    finite_ordered_set,
)
from sage_extensions.categories.sets.indexed_families import (
    finite_indexed_family,
)
from sage_extensions.categories.sets.set_categories import NN
from sage_extensions.refine import RealizationHook


def _integers():
    return _owned_integers()


def _ray_generator(ray):
    r"""The primitive generator ``u_rho`` in ``N`` of a one-dimensional cone."""
    return next(iter(ray.rays()))


def _pairing_on_ray(fan, character, ray):
    r"""``<m, u_rho>``, an integer, for a character and a ray of the fan."""
    return fan.character_cocharacter_value(character, _ray_generator(ray))


def _character_names(count):
    r"""Variable names for the semigroup generators of one chart."""
    return tuple(f"z{position}" for position in range(count))


def _semigroup_algebra(cone, base_ring):
    r"""The semigroup algebra ``k[S_sigma]`` of a cone (CLS Prop. 1.1.9).

    \(S_\sigma=\sigma^\vee\cap M\) is a finitely generated affine semigroup by
    Gordan's lemma, and choosing a generating set
    \(\mathcal A=(m_1,\dots,m_s)\) presents its algebra as
    \(k[z_1,\dots,z_s]/I_{\mathcal A}\) with \(I_{\mathcal A}\) the toric ideal
    of the integer matrix whose columns are the \(m_i\).  The toric ideal is
    computed by ``sage.schemes.toric.ideal.ToricIdeal``, whose matrix
    convention is exactly one column per variable.

    When the base is a domain, the result is a domain: \(R[S_\sigma]\) embeds
    in the group algebra \(R[M]\), a Laurent polynomial ring over \(R\).
    That placement is what lets a localization of a chart read a denominator
    as a power of the character it inverts, which is how the transition out of
    a face localization is written.  No domain placement is asserted over a
    base with zero divisors.
    """
    generators = cone.semigroup_generators()
    base = _own_ring(base_ring)
    extra_categories = (
        (OwnedIntegralDomains(),) if base in OwnedIntegralDomains() else ()
    )
    return AffineSemigroupAlgebras(base)(
        (
            tuple(_engine_vector(cone.character_lattice(), generator))
            for generator in generators
        ),
        extra_categories=extra_categories,
    )


@cached_function
def _face_supporting_character_monomial(face, cone, chart):
    r"""The monomial ``chi^m`` cutting ``face`` out of ``cone`` (CLS Prop. 1.3.16).

    ``m`` is ``cone.face_supporting_character(face)``, a sum of chosen
    semigroup generators, so in \(k[S_\sigma]\) the character \(\chi^m\) is the
    product of the corresponding variables with no integer program to solve.
    """
    algebra = chart.coordinate_algebra()
    labels = tuple(algebra.algebra_generating_set())
    ranking = cone.semigroup_generators().ranking_map()
    monomial = algebra.one()
    for generator in cone.face_supporting_generators(face):
        monomial = monomial * algebra.algebra_generator(labels[int(ranking(generator))])
    return monomial


@cached_function
def _character_monomial(character, cone, chart):
    r"""The monomial ``chi^m`` in ``k[S_sigma]`` of a character of ``S_sigma``.

    ``m`` is a nonnegative integer combination of the chosen semigroup
    generators, and the cone reports one such family of multiplicities; the
    monomial is the corresponding product of variables.  Two expansions of one
    ``m`` differ by the toric ideal, so they name one element of
    \(k[S_\sigma]\) (CLS Prop. 1.1.9).
    """
    algebra = chart.coordinate_algebra()
    labels = tuple(algebra.algebra_generating_set())
    monomial = algebra.one()
    for position, multiplicity in enumerate(cone.semigroup_coefficients(character)):
        monomial = monomial * algebra.algebra_generator(labels[position]) ** int(
            multiplicity
        )
    return monomial


@cached_function
def _affine_chart(cone, base_ring):
    r"""``U_sigma = Spec k[S_sigma]``, one chart per cone and base (CLS Prop. 1.3.9).

    The chart depends on the cone and the base field alone, so it is shared by
    every construction that reaches it: the atlas a toric variety is glued from
    holds exactly the objects its ``affine_chart`` answers with.
    """
    return (_semigroup_algebra(cone, base_ring)).affine_spectrum(base_ring=base_ring)


@cached_function
def _face_localization(face, cone, base_ring):
    r"""``U_tau = D(chi^{m_sigma})`` inside ``U_sigma`` for a face ``tau`` of ``sigma``."""
    chart = _affine_chart(cone, base_ring)
    return chart.distinguished_open(
        _face_supporting_character_monomial(face, cone, chart)
    )


@cached_function
def _character_on_overlap(character, face, cone, base_ring):
    r"""``chi^m`` in ``k[S_sigma][1/chi^{m_sigma}]`` for ``m`` a character of ``S_tau``.

    For \(\tau=\sigma\cap m_\sigma^\perp\) one has
    \(S_\tau=S_\sigma+\mathbb Z_{\ge 0}(-m_\sigma)\) (CLS Prop. 1.3.16), so
    every character of \(S_\tau\) is \(m'=a-c\,m_\sigma\) with \(a\in S_\sigma\)
    and \(c\ge 0\).  Raising \(m'\) by \(m_\sigma\) until it lies in
    \(\sigma^\vee\) finds the least such \(c\), and the search terminates
    because some \(c\) works; the answer is then the monomial of \(a\) divided
    by that power of the inverted character.
    """
    chart = _affine_chart(cone, base_ring)
    localized = _face_localization(face, cone, base_ring).coordinate_algebra()
    supporting = cone.face_supporting_character(face)
    assert face.dual_cone_contains(character), (
        f"the character {character} is not in the dual cone of the face {face} of {cone}, so "
        "chi^m is not a regular function on the chart of the face"
    )
    shifted = character
    exponent = 0
    while not cone.dual_cone_contains(shifted):
        shifted = shifted + supporting
        exponent += 1
    inverse = localized.localization_map()(
        localized.inverted_element()
    ).inverse_of_unit()
    return localized.localization_map()(
        _character_monomial(shifted, cone, chart)
    ) * inverse**exponent


@cached_function
def _face_transition_morphism(face, source_cone, target_cone, base_ring):
    r"""``U_sigma cap U_tau -> U_tau cap U_sigma``, one direction of a transition.

    Both sides are the chart of the common face \(\gamma\), presented as a
    localization of a different semigroup algebra.  Sending each chosen
    semigroup generator of \(S_\tau\) to its character on the overlap is a ring
    morphism out of \(k[S_\tau]\), so a morphism \(U_\sigma\cap U_\tau\to
    U_\tau\); it carries \(\chi^{m_\tau}\) to a unit, so it factors uniquely
    through the open \(U_\tau\cap U_\sigma\).  That factorization is the
    universal property of the localization, taken on the schemes.
    """
    source_open = _face_localization(face, source_cone, base_ring)
    target_open = _face_localization(face, target_cone, base_ring)
    target_chart = _affine_chart(target_cone, base_ring)
    target_algebra = target_chart.coordinate_algebra()
    labels = tuple(target_algebra.algebra_generating_set())
    extension = Algebras(base_ring).Associative().Unital().Commutative().Mor(
        target_algebra, source_open.coordinate_algebra()
    )(
        {
            labels[position]: _character_on_overlap(
                generator, face, source_cone, base_ring
            )
            for position, generator in enumerate(target_cone.semigroup_generators())
        }
    )
    # The extension is built from characters on the common face. Each target
    # semigroup generator is sent to a source monomial times a power of the
    # inverted source supporting character, so the target supporting character
    # maps to a unit by this construction. Preserve that universal-property
    # proof instead of asking generic unit membership to rediscover it through
    # ideal saturation in the source localization.
    induced = target_open.coordinate_algebra()._induced_morphism_from_unit_images(extension)
    return _scheme_mor_category(source_open, target_open)(induced)


@cached_function
def _face_transition(source_cone, target_cone, base_ring):
    r"""The atlas transition between the charts of two cones of one fan.

    The overlap is the chart of \(\gamma=\sigma\cap\tau\), which is a face of
    each, so it is a distinguished open of both charts and the two directions
    are mutually inverse.  Both presentations invert a character exactly when
    \(\gamma\) is a proper face of each cone, which is what two distinct
    maximal cones of a fan give: a supporting character of \(\sigma\) in
    \(\sigma\) itself lies in \(\sigma^\perp\), where it is already a unit and
    localizing at it says nothing.
    """
    # This private constructor is called only on distinct members of the
    # selected maximal-cone family (see `_toric_variety` below). Distinct
    # maximal cones cannot be faces of one another, so repeating Sage's two
    # cone-containment computations here is redundant.
    face = source_cone.intersection(target_cone)
    forward = _face_transition_morphism(face, source_cone, target_cone, base_ring)
    inverse = _face_transition_morphism(face, target_cone, source_cone, base_ring)
    return Schemes(base_ring).Core().Mor(forward.domain(), forward.codomain())(
        forward,
        inverse,
    )


def _pullback_character(character, lattice_morphism, domain_fan, codomain_fan):
    r"""Return ``phi^*(m)`` in the domain character lattice.

    If ``phi:N->N'`` is the cocharacter map, its dual is characterized by
    ``<phi^*m,n>=<m,phi(n)>``.  The chosen frames of the dual lattices make
    these pairings exactly the coordinates of the pulled-back character.
    """
    source_cocharacters = domain_fan.cocharacter_lattice()
    source_characters = domain_fan.character_lattice()
    target_pairing = codomain_fan.character_cocharacter_pairing()
    integers = _integers()
    return source_characters.linear_combination(
        {
            label: integers(
                target_pairing(
                    character,
                    lattice_morphism(source_cocharacters.module_generator(label)),
                )
            )
            for label in source_cocharacters.module_generating_set()
            if integers(
                target_pairing(
                    character,
                    lattice_morphism(source_cocharacters.module_generator(label)),
                )
            )
        }
    )


def _toric_chart_pullback(lattice_morphism, source_cone, target_cone, base_ring):
    r"""The affine pullback ``k[S_tau] -> k[S_sigma]`` induced by ``phi``.

    For ``phi(sigma) subset tau``, every ``m in S_tau`` pulls back to
    ``phi^*m in S_sigma``.  On the chosen semigroup generators this is the
    character monomial of that pulled-back lattice point.
    """
    source_chart = _affine_chart(source_cone, base_ring)
    target_chart = _affine_chart(target_cone, base_ring)
    source_algebra = source_chart.coordinate_algebra()
    target_algebra = target_chart.coordinate_algebra()
    target_labels = tuple(target_algebra.algebra_generating_set())
    target_generators = target_cone.semigroup_generators()
    domain_fan = source_cone.parent()
    codomain_fan = target_cone.parent()
    return target_algebra.Mor(source_algebra)(
        {
            target_labels[position]: _character_monomial(
                _pullback_character(
                    character,
                    lattice_morphism,
                    domain_fan,
                    codomain_fan,
                ),
                source_cone,
                source_chart,
            )
            for position, character in enumerate(target_generators)
        }
    )


def _owned_incidence_morphism(base, source, target, engine_matrix):
    r"""Raise one private incidence matrix to an owned module morphism."""
    source_labels = tuple(source.module_generating_set())
    target_labels = tuple(target.module_generating_set())
    assert engine_matrix.ncols() == len(source_labels)
    assert engine_matrix.nrows() == len(target_labels)

    def image(source_label):
        column = source_labels.index(source_label)
        return target.linear_combination(
            {
                target_label: base(int(engine_matrix[row, column]))
                for row, target_label in enumerate(target_labels)
                if engine_matrix[row, column]
            }
        )

    return source.module_category().Mor(source, target)(image)


class ToricSchemes(OwnedCategoryOverBaseRing):
    r"""Toric schemes over the stated base ring, each constructed from its fan.

    The level datum is the fan ``Sigma`` and the lattice polytope it was
    obtained from, or ``None``.  An object is the scheme glued from the charts
    of the maximal cones (:func:`_toric_variety`), placed here at construction;
    its private Sage scheme is Sage's ``ToricVariety`` of the same fan.
    """

    def an_object(self):
        r"""The projective line, as the toric variety of the fan of ``P^1``.

        The represented result retains the base-ring-dependent toric
        and integral-variety categories::

            sage: from dzack_research.preamble.all import QQ, ZZ, ToricSchemes, Varieties
            sage: all((ToricSchemes(R).an_object() in ToricSchemes(R) and
            ....:      ToricSchemes(R).an_object() in Varieties(R)) for R in (QQ, ZZ))
            True
        """

        cocharacters = _integers().free_module(1)
        return RationalPolyhedralFans(cocharacters).projective_space_fan().toric_variety(
            self.base_ring()
        )

    def _repr_object_names(self):
        return f"toric schemes over {self.base_ring()}"

    def super_categories(self):
        r"""A toric scheme over a ring with zero divisors is not placed in varieties.

            sage: from dzack_research.preamble.all import ZZ, ToricSchemes, Varieties
            sage: R = ZZ.quotient_ring(ZZ.ideal(4))
            sage: R.is_integral_domain()
            False
            sage: Varieties(R) in ToricSchemes(R).super_categories()
            False
        """
        base = self.base_ring()
        schemes = Schemes(base)
        categories = [schemes.Separated().FiniteType()]
        if base in OwnedIntegralDomains():
            categories.append(Varieties(base))
        from sage_extensions.categories.schemes.schemes import _normal_placement

        if _normal_placement(base):
            categories.append(schemes.Normal())
        return categories

    class ParentMethods:
        def __init__(self, toric_fan, polarizing_polytope, **rest) -> None:
            self._toric_fan = toric_fan
            self._polarizing_polytope = polarizing_polytope
            super().__init__(**rest)

        def fan(self):
            r"""The fan ``Sigma`` in ``N_R`` this variety was built from."""
            return self._toric_fan

        @RealizationHook
        def _affineness_decision(self):
            r"""Supply scheme affineness from the exact fan and coefficient ring.

            A fan with at most one maximal cone gives an affine scheme.
            With more than one, every nonempty field fiber is nonaffine:
            an affine toric variety has the faces of a single cone as its
            fan (CLS, Section 3.1). Thus this scheme is affine exactly when
            its coefficient ring is zero. This also retains an undecided
            zero-ring proposition instead of assuming the base is a field.
            """
            if len(tuple(self.fan().maximal_cones())) <= 1:
                return True
            base = self.scheme_base_ring()
            return base.zero() == base.one()

        def toric_fixed_point_blowup(self, center_cone):
            r"""Blow up the torus-fixed point indexed by ``center_cone``."""
            from sage_extensions.categories.schemes.toric.blowups import (
                _toric_fixed_point_blowup,
            )

            return _toric_fixed_point_blowup(self, center_cone)

        def cocharacter_lattice(self):
            r"""The lattice ``N`` of one-parameter subgroups of the torus."""
            return self.fan().cocharacter_lattice()

        def character_lattice(self):
            r"""The lattice ``M`` of characters of the torus."""
            return self.fan().character_lattice()

        def character_cocharacter_pairing(self):
            r"""The perfect pairing ``M ⊗ N -> ZZ``."""
            return self.fan().character_cocharacter_pairing()

        def is_toric(self) -> bool:
            r"""True: an object of this category was built from a fan."""
            return True

        def dimension(self):
            r"""The rank of ``N`` (CLS Thm. 3.1.19)."""
            return self.fan().dimension()

        def relative_dimension(self):
            r"""``dim X_Sigma`` over the base field, which is the rank of ``N``.

            The charts are the spectra of the semigroup algebras of the maximal
            cones, each of dimension ``dim N`` over a field, so the glued scheme
            has that relative dimension (CLS Thm. 3.1.19).
            """
            return self.dimension()

        def is_smooth(self) -> bool:
            r"""``X_Sigma`` is smooth exactly when every cone is smooth (CLS Thm. 3.1.19)."""
            return self.fan().is_smooth()

        def is_complete(self) -> bool:
            r"""``X_Sigma`` is complete exactly when ``Sigma`` is (CLS Thm. 3.4.1)."""
            return self.fan().is_complete()

        def is_orbifold(self) -> bool:
            r"""``X_Sigma`` has finite quotient singularities iff ``Sigma`` is simplicial."""
            return self.fan().is_simplicial()

        def is_normal(self) -> bool:
            r"""Every toric variety of a fan is normal (CLS Thm. 1.3.5)."""
            return True

        @cached_method
        def torus(self):
            r"""The dense torus ``T_N = Spec k[M]``, the chart of the zero cone."""
            trivial = RationalPolyhedralFans(self.cocharacter_lattice()).trivial_fan()
            return trivial.toric_variety(self.scheme_base_ring())

        def affine_chart(self, cone):
            r"""The affine chart ``U_sigma = Spec k[S_sigma]`` of one cone.

            This is the owned construction from the semigroup algebra, not a
            patch reconstructed from a computational image.  For a maximal cone it is the chart
            of the atlas this variety is glued from, the same object
            ``chart(cone)`` answers with.
            """
            assert cone in self.fan(), (
                f"the affine chart U_sigma of {self} is taken of a cone sigma of its fan, but "
                f"{cone} is not a cone of {self.fan()}"
            )
            return _affine_chart(cone, self.scheme_base_ring())

        def affine_cover(self):
            r"""The charts of the maximal cones, which cover ``X_Sigma``."""
            return FiniteOrderedSets().from_indexed(
                self.fan().maximal_cones(),
                self.affine_chart,
                name="Affine toric charts",
            )

        def face_localization(self, face, cone):
            r"""The open immersion ``U_tau -> U_sigma`` of a face inclusion.

            For \(\tau\preceq\sigma\) one has \(S_\tau=S_\sigma+\mathbb Z(-m)\)
            for any \(m\in S_\sigma\) with \(\tau=\sigma\cap m^\perp\), so
            \(U_\tau\) is the distinguished open \(D(\chi^m)\subseteq U_\sigma\)
            (CLS Prop. 1.3.16).  These are the maps the charts are glued along.
            """
            assert face.is_face_of(cone), (
                f"the open U_tau of U_sigma is defined for a face tau of sigma, but {face} is not "
                f"a face of {cone}"
            )
            return _face_localization(face, cone, self.scheme_base_ring())

        def torus_orbits(self, orbit_dimension):
            r"""The torus orbits of the stated dimension, as cones of the fan.

            The orbit-cone correspondence (CLS Thm. 3.2.6) is a bijection
            between the cones of ``Sigma`` and the orbits of the torus action,
            under which a cone of dimension ``k`` indexes an orbit of dimension
            ``n - k``.  The orbits are therefore returned as their cones.
            """
            return self.fan().cones(
                int(self.dimension()) - int(orbit_dimension)
            )

        def torus_fixed_point_subscheme(self, cone):
            r"""Return the torus-fixed closed point indexed by a full-dimensional cone.

            For a full-dimensional cone ``sigma``, the closed orbit in
            ``U_sigma = Spec k[S_sigma]`` is cut out by all nonconstant
            semigroup generators.  It is absent from every other maximal toric
            chart.  Gluing those local closed subschemes gives the orbit closure
            ``V(sigma)``, which is the fixed point used as a blowup center.
            """
            fan = self.fan()
            assert cone in fan.maximal_cones(), (
                f"the torus-fixed point of {self} must be indexed by a maximal cone of {fan}, "
                f"but {cone} is not maximal"
            )
            assert int(cone.dimension()) == int(fan.dimension()), (
                f"the orbit indexed by {cone} in {self} is not a fixed point: the cone has dimension "
                f"{cone.dimension()} while the fan has dimension {fan.dimension()}"
            )
            local_closed = {}
            for chart_cone in self.gluing_datum().chart_indices():
                chart = self.affine_chart(chart_cone)
                algebra = chart.coordinate_algebra()
                match chart_cone == cone:
                    case True:
                        equations = tuple(
                            algebra.algebra_generator(label)
                            for label in algebra.algebra_generating_set()
                        )
                    case False:
                        equations = (algebra.one(),)
                local_closed[chart_cone] = chart.closed_subscheme(equations)
            return self.chartwise_closed_subscheme(
                local_closed,
                name="Torus-fixed point",
            )

        @cached_method
        def torus_invariant_divisor_group(self):
            r"""``Div_T(X) = ⊕_rho ZZ D_rho``, free on the rays (CLS §4.1).

            The prime divisors are indexed by the rays themselves, which is the
            orbit-cone correspondence restricted to codimension one: ``D_rho``
            is the closure of the orbit of ``rho``.
            """
            return WeilDivisorGroups()(self, finite_ordered_set(tuple(self.fan().cones(1))))

        def weil_divisor_group(self, *args, **kwargs):
            return self.torus_invariant_divisor_group(*args, **kwargs)

        @cached_method
        def torus_invariant_cartier_divisor_group(self):
            r"""Return ``CDiv_T(X)=Div_T(X)`` for a smooth fan.

            This is the torus-invariant subgroup used by the toric divisor
            presentation, not the full ``CDiv(X)=Gamma(X,K_X^*/O_X^*)``
            returned by :meth:`cartier_divisor_group`.
            """
            assert self.fan().is_smooth(), (
                f"the torus-invariant Cartier divisors of {self} equal Div_T(X) only for a smooth "
                "fan, and its fan is not smooth"
            )
            return self.weil_divisor_group()

        @cached_method
        def torus_invariant_cartier_to_weil_morphism(self):
            r"""The inclusion ``CDiv_T(X) -> Div_T(X)`` for a smooth fan."""
            cartier = self.torus_invariant_cartier_divisor_group()
            weil = self.weil_divisor_group()
            assert cartier is weil, (
                f"for the smooth toric variety {self}, the torus-invariant Cartier divisors "
                f"{cartier} should be all of Div_T(X) = {weil}"
            )
            return weil.module_category().Mor(weil, weil).identity()

        def torus_invariant_prime_divisor(self, ray):
            r"""The prime divisor ``D_rho`` of one ray of the fan."""
            assert ray in self.fan(), (
                f"the prime divisor D_rho of {self} is defined for a ray rho of its fan, but "
                f"{ray} is not a cone of {self.fan()}"
            )
            return self.torus_invariant_divisor_group().module_generator(ray)

        def weil_multiplicity(self, divisor, ray):
            r"""Return the coefficient of ``D_rho`` in a torus-invariant Weil divisor."""
            assert ray in self.fan().cones(1), (
                f"the coefficient of D_rho in {divisor} is defined for a ray rho of the fan of "
                f"{self}, but {ray} is not a ray of it"
            )
            return self.weil_divisor_group()(divisor).to_vector()(ray)

        def order_of_character_along_prime_divisor(self, character, ray):
            r"""Return ``ord_{D_rho}(chi^m)=<m,u_rho>`` (CLS Prop. 4.1.2)."""
            character = self.character_lattice()(character)
            assert ray in self.fan().cones(1), (
                f"the order of vanishing along D_rho on {self} is defined for a ray rho of its fan, "
                f"but {ray} is not a ray of it"
            )
            return _pairing_on_ray(self.fan(), character, ray)

        def principal_divisor_of_character(self, character):
            r"""Return ``div(chi^m)`` as an element of the represented Weil group."""
            return self.character_divisor_morphism()(self.character_lattice()(character))

        def torus_invariant_divisor_support_subscheme(
            self,
            divisor,
            *,
            placements=(),
            construction_data=None,
        ):
            r"""Return the reduced union of torus-invariant primes in an effective divisor.

            On ``U_sigma=Spec k[S_sigma]`` the invariant prime ``D_rho`` for
            ``rho <= sigma`` is generated by the semigroup monomials
            ``chi^m`` with ``<m,u_rho> > 0``.  Intersecting those prime ideals
            gives the scheme-theoretic union of the selected components; the
            common chartwise closed-subscheme owner then glues the result.
            """
            group = self.torus_invariant_divisor_group()
            divisor = group(divisor)
            coordinates = divisor.to_vector()
            support = coordinates.support()
            zero = _integers().zero()
            assert all(coordinates(ray) >= zero for ray in support.domain()), (
                f"the support of {divisor} as a closed subscheme of {self} is defined here only for "
                "an effective divisor, but it has a negative coefficient"
            )
            selected = tuple(ray for ray in self.fan().cones(1) if ray in support)
            local_closed = {}
            for cone in self.gluing_datum().chart_indices():
                chart = self.affine_chart(cone)
                algebra = chart.coordinate_algebra()
                labels = tuple(algebra.algebra_generating_set())
                ideals = []
                cone_rays = tuple(cone.faces(1))
                for ray in selected:
                    if ray not in cone_rays:
                        continue
                    generators = tuple(
                        algebra.algebra_generator(labels[position])
                        for position, character in enumerate(cone.semigroup_generators())
                        if _pairing_on_ray(self.fan(), character, ray) > zero
                    )
                    ideals.append(algebra.ideal(*generators))
                if not ideals:
                    ideal = algebra.ideal(algebra.one())
                else:
                    ideal = ideals[0]
                    for component_ideal in ideals[1:]:
                        ideal = ideal.intersection(component_ideal)
                local_closed[cone] = chart.closed_subscheme(
                    tuple(ideal.ideal_generators())
                )
            return self.chartwise_closed_subscheme(
                local_closed,
                name="Support of a torus-invariant divisor",
                placements=placements,
                construction_data=construction_data,
            )

        @cached_method
        def toric_boundary_divisor(self):
            r"""The toric boundary ``sum_rho D_rho``, the complement of the torus."""
            group = self.torus_invariant_divisor_group()
            return group.linear_combination(
                {ray: _integers().one() for ray in self.fan().cones(1)}
            )

        def canonical_divisor(self):
            r"""``K_X = -sum_rho D_rho`` (CLS Thm. 8.2.3)."""
            return -self.toric_boundary_divisor()

        def canonical_reflexive_sheaf(self):
            r"""The rank-one reflexive dualizing sheaf ``O_X(K_X)``.

            For a normal toric variety this is the divisorial sheaf of the
            canonical Weil divisor, including when ``K_X`` is not Cartier.
            On the Cartier locus it agrees with the invertible canonical
            sheaf. Its general realization requires divisorial module
            gluing, not Cartier transition functions.
            """
            if self.is_cartier(self.canonical_divisor()):
                return self.invertible_sheaf_of_divisor(self.canonical_divisor())
            raise NotImplementedError(
                f"the reflexive divisorial sheaf O(K_X) on {self} requires "
                "a non-Cartier divisorial module gluing realization"
            )

        @cached_method
        def character_divisor_morphism(self):
            r"""``M -> Div_T(X)``, ``m |-> div(chi^m)`` (CLS Thm. 4.1.3).

            The principal divisor of a character is
            \(\operatorname{div}(\chi^m)=\sum_\rho\langle m,u_\rho\rangle
            D_\rho\).  This is the map whose cokernel is the class group.
            """
            characters = self.character_lattice()
            group = self.torus_invariant_divisor_group()
            fan = self.fan()
            rays = fan.cones(1)

            def image(label):
                character = characters.module_generator(label)
                return group.linear_combination(
                    {
                        ray: self.order_of_character_along_prime_divisor(
                            character,
                            ray,
                        )
                        for ray in rays
                    }
                )

            return characters.module_category().Mor(characters, group)(image)

        def has_torus_factor(self) -> bool:
            r"""Whether ``X`` splits off a torus factor (CLS Prop. 3.3.9).

            ``X_Sigma`` has a torus factor exactly when the ray generators fail
            to span ``N_R``, and by CLS Thm. 4.1.3 that failure is exactly the
            failure of ``M -> Div_T(X)`` to be injective.
            """
            return not self.character_divisor_morphism().is_injective()

        @cached_method
        def _class_group(self):
            r"""``Cl(X) = Div_T(X)/div(chi^M)`` (CLS Thm. 4.1.3).

            The sequence ``M -> Div_T(X) -> Cl(X) -> 0`` is exact for every
            fan, so the class group is this cokernel whether or not ``X`` has a
            torus factor; it is exact on the left exactly when ``X`` has none.
            """
            return ClassGroups().cokernel_of_principal_divisors(self, self.character_divisor_morphism())

        @cached_method
        def class_group_projection(self):
            r"""The quotient ``Div_T(X) ->> Cl(X)``.

            The class group is presented on the same prime divisors as
            ``Div_T(X)``, so the quotient sends each generator to the generator
            of the same name.
            """
            base = self.scheme_base_ring()
            assert self in Schemes(base).LocallyNoetherian().Integral(), (
                f"cannot form the class-group projection for {self}: the scheme-level Weil divisor class "
                "group is owned by locally Noetherian integral schemes, but this toric scheme is an object "
                f"of {self.category()}"
            )
            group = self.torus_invariant_divisor_group()
            classes = self.class_group()
            return group.module_category().Mor(group, classes)(
                {
                    label: classes.module_generator(label)
                    for label in group.module_generating_set()
                }
            )

        def divisor_class(self, divisor):
            r"""The class in ``Cl(X)`` of a torus-invariant divisor."""
            return self.class_group_projection()(divisor)

        @cached_method
        def local_divisor_group(self, cone):
            r"""``Div_T(U_sigma)``, free on the rays of one cone (CLS §4.1)."""
            return _integers()._fresh_free_module_on(
                finite_ordered_set(tuple(cone.faces(1))),
            )

        @cached_method
        def local_character_divisor_morphism(self, cone):
            r"""``M -> Div_T(U_sigma)``, the principal divisors on one chart."""
            characters = self.character_lattice()
            local = self.local_divisor_group(cone)
            fan = self.fan()
            rays = cone.faces(1)

            def image(label):
                character = characters.module_generator(label)
                return local.linear_combination(
                    {ray: _pairing_on_ray(fan, character, ray) for ray in rays}
                )

            return characters.module_category().Mor(characters, local)(image)

        def local_divisor_restriction(self, divisor, cone):
            r"""``sum_{rho in sigma(1)} -a_rho D_rho`` in ``Div_T(U_sigma)``.

            This is the right-hand side of the Cartier equations
            ``<m_sigma, u_rho> = -a_rho`` (CLS Thm. 4.2.8).
            """
            coordinates = self.torus_invariant_divisor_group()(divisor).to_vector()
            local = self.local_divisor_group(cone)
            return local.linear_combination(
                {ray: -coordinates(ray) for ray in cone.faces(1)}
            )

        def is_cartier(self, divisor) -> bool:
            r"""Whether ``D = sum a_rho D_rho`` is Cartier (CLS Thm. 4.2.8).

            ``D`` is Cartier exactly when every maximal cone ``sigma`` admits
            ``m_sigma`` in ``M`` with ``<m_sigma, u_rho> = -a_rho`` for every
            ``rho`` in ``sigma(1)``; that is, exactly when the local
            coefficient divisor lies in the image of ``M -> Div_T(U_sigma)``.
            Membership in that image is decided by the cokernel of the map.
            """
            for cone in self.fan().maximal_cones():
                projection = self.local_character_divisor_morphism(cone).cokernel_projection()
                image = projection(self.local_divisor_restriction(divisor, cone))
                if image != projection.codomain().zero():
                    return False
            return True

        def cartier_datum(self, divisor, cone):
            r"""``m_sigma`` in ``M`` with ``<m_sigma, u_rho> = -a_rho`` on ``sigma(1)``.

            This is the Cartier datum of ``D`` on the chart of ``sigma`` (CLS
            Thm. 4.2.8): the character whose principal divisor cancels ``D``
            there, so that ``D`` is cut out by ``chi^{-m_sigma}`` on
            ``U_sigma``.  It is a preimage under ``M -> Div_T(U_sigma)``, and
            it is unique when ``sigma`` is full-dimensional.
            """
            assert self.is_cartier(divisor), (
                f"the local character m_sigma of {divisor} on the chart of {cone} exists only for a "
                f"Cartier divisor, but {divisor} is not Cartier on {self}"
            )
            return self.local_character_divisor_morphism(cone).lift(
                self.local_divisor_restriction(divisor, cone)
            )

        def is_basepoint_free(self, divisor) -> bool:
            r"""Whether ``O_X(D)`` is generated by its global sections (CLS Thm. 6.1.7).

            On a complete fan this is convexity of the support function of a
            Cartier divisor: ``<m_sigma, u_rho> >= -a_rho`` for every maximal
            cone ``sigma`` and every ray ``rho`` of the fan.
            """
            assert self.fan().is_complete(), (
                f"nefness of {divisor} by convexity of its support function is decided here only "
                f"on a complete fan, but the fan of {self} is not complete"
            )
            if not self.is_cartier(divisor):
                return False
            fan = self.fan()
            coordinates = self.torus_invariant_divisor_group()(divisor).to_vector()
            for cone in fan.maximal_cones():
                character = self.cartier_datum(divisor, cone)
                for ray in fan.cones(1):
                    if _pairing_on_ray(fan, character, ray) < -coordinates(ray):
                        return False
            return True

        def is_ample(self, divisor) -> bool:
            r"""Whether ``D`` is ample (CLS Thm. 6.1.14).

            On a complete fan this is strict convexity of the support function
            of a Cartier divisor: ``<m_sigma, u_rho> > -a_rho`` for every
            maximal cone ``sigma`` and every ray ``rho`` that is not a face of
            ``sigma``.
            """
            assert self.fan().is_complete(), (
                f"ampleness of {divisor} by strict convexity of its support function is decided "
                f"here only on a complete fan, but the fan of {self} is not complete"
            )
            if not self.is_cartier(divisor):
                return False
            fan = self.fan()
            coordinates = self.torus_invariant_divisor_group()(divisor).to_vector()
            for cone in fan.maximal_cones():
                character = self.cartier_datum(divisor, cone)
                for ray in fan.cones(1):
                    if ray.is_face_of(cone):
                        continue
                    if _pairing_on_ray(fan, character, ray) <= -coordinates(ray):
                        return False
            return True

        @cached_method
        def _picard_group(self):
            r"""``Pic(X) = CDiv_T(X)/M`` (CLS Thm. 4.2.1).

            On a smooth fan every torus-invariant Weil divisor is Cartier (CLS
            Prop. 4.2.6), so ``CDiv_T(X) = Div_T(X)`` and the Picard group is
            the quotient this returns.  On a fan that is not smooth
            ``CDiv_T(X)`` is the proper subgroup that ``is_cartier`` decides one
            divisor at a time; constructing that subgroup is a kernel out of the
            free divisor group into a finitely presented cokernel, and the
            module layer represents kernels only between free modules.
            """
            assert self.fan().is_smooth(), (
                f"the Picard group of {self} is computed only for a smooth fan, where every Weil "
                "divisor is Cartier; its fan is not smooth, so test the divisors in question "
                "with is_cartier instead"
            )
            from sage_extensions.categories.divisors.picard_groups import PicardGroups

            return PicardGroups().cokernel_of_principal_divisors(self, self.character_divisor_morphism())

        @cached_method
        def _picard_to_class_group_morphism(
            self,
            base_picard_group=None,
            base_class_group=None,
            base_picard_to_class=None,
        ):
            r"""The natural comparison ``Pic(X) -> Cl(X)`` for a smooth toric variety.

            Since every invariant Weil divisor is Cartier on a smooth fan, the
            comparison is an isomorphism.  The two quotient-role objects retain
            the same presentation; this map records the comparison rather than
            identifying them by object identity.
            """
            supplied = (base_picard_group, base_class_group, base_picard_to_class)
            assert supplied == (None, None, None), (
                f"cannot use supplied projective-bundle base data {supplied} to compute Pic({self}) -> Cl({self}): "
                "the toric comparison is computed from the fan's divisor presentation"
            )
            picard = self.picard_group()
            classes = self.class_group()
            forward = picard.module_category().Mor(picard, classes)(
                {
                    label: classes.module_generator(label)
                    for label in picard.module_generating_set()
                }
            )
            inverse = classes.module_category().Mor(classes, picard)(
                {
                    label: picard.module_generator(label)
                    for label in classes.module_generating_set()
                }
            )
            return picard.module_category().Core().Mor(picard, classes)(forward, inverse)

        @cached_method
        def torus_invariant_cartier_class_projection(self):
            r"""The quotient ``CDiv_T(X) -> Pic(X)`` for a smooth toric variety."""
            base = self.scheme_base_ring()
            assert self in Schemes(base).LocallyNoetherian().Integral(), (
                f"cannot form the Cartier class projection for {self}: the comparison Pic({self}) -> "
                f"Cl({self}) requires a locally Noetherian integral scheme"
            )
            return (
                self.picard_to_class_group_morphism().inverse()
                * self.class_group_projection()
            )

        def divisor_polytope(self, divisor):
            r"""``P_D = {m in M_R : <m,u_rho> >= -a_rho for all rho}`` (CLS (4.3.2)).

            For an ample divisor this is the polytope whose normal fan is
            ``Sigma``, so it recovers the polarizing polytope of a variety
            built from one.
            """
            from sage_extensions.categories.schemes.polytopes import (
                ConvexPolytopes,
            )

            assert self.fan().is_complete(), (
                f"the polytope P_D of {divisor} is computed here only on a complete fan, where it "
                f"is bounded, but the fan of {self} is not complete"
            )
            coordinates = self.torus_invariant_divisor_group()(divisor).to_vector()
            cocharacters = self.cocharacter_lattice()
            halfspaces = tuple(
                (
                    coordinates(ray),
                    tuple(_engine_vector(cocharacters, _ray_generator(ray))),
                )
                for ray in self.fan().cones(1)
            )
            return ConvexPolytopes(self.character_lattice()).from_halfspaces(halfspaces)

        @cached_method
        def polarizing_divisor(self):
            r"""Return the torus-invariant Cartier divisor whose polytope is the selected ``P``.

            If ``P`` has normal fan ``Sigma`` then its support numbers are
            ``a_rho=-min_{m in P}<m,u_rho>``.  Thus
            ``P=P_D`` for ``D=sum a_rho D_rho``.  This is the inverse direction
            to :meth:`divisor_polytope` for a toric variety constructed from a
            chosen lattice polytope.
            """
            assert self.is_polarized(), (
                f"{self} was constructed from a fan, not from a lattice polytope, so it has no "
                "polarizing divisor"
            )
            polytope = self.polarizing_polytope()
            # P lives in its lattice M; the normal fan lives in N = M^*, whose
            # character lattice is M^**.  The vertices cross by biduality.
            from sage_extensions.categories.modules.pure.modules import Modules

            lattice = polytope.ambient_lattice()
            biduality = Modules(lattice.base_ring()).dualization().double_dual_morphism(lattice)
            assert biduality.codomain() is self.character_lattice(), (
                f"the polytope {polytope} of {self} lies in {lattice}, whose double dual "
                f"{biduality.codomain()} is not the character lattice {self.character_lattice()} of its fan"
            )
            group = self.torus_invariant_divisor_group()
            coefficients = {}
            for ray in self.fan().cones(1):
                values = tuple(
                    _pairing_on_ray(self.fan(), biduality(vertex), ray)
                    for vertex in polytope.vertices()
                )
                coefficients[ray] = -min(values)
            divisor = group.linear_combination(coefficients)
            assert self.is_cartier(divisor), (
                f"the divisor {divisor} of the polytope {polytope} of {self} is not Cartier, "
                "although a polytope with normal fan Sigma always gives a Cartier divisor"
            )
            return divisor

        def compatible_divisor_section(self, divisor, section, *, line_bundle=None):
            r"""Descend one character-basis section of ``O(D)`` to the toric affine atlas.

            On ``U_sigma`` the Cartier datum ``m_sigma`` trivializes ``O(D)``.
            Hence the global character ``chi^m`` has local coefficient
            ``chi^(m-m_sigma)``.  The common finite-atlas equalizer verifies
            these coefficients against the line-bundle transition functions.
            """
            divisor = self.torus_invariant_divisor_group()(divisor)
            assert self.is_cartier(divisor), (
                f"sections of O(D) are glued from characters on the charts only for Cartier D, "
                f"but {divisor} is not Cartier on {self}"
            )
            selected_line = self.invertible_sheaf_of_divisor(divisor) if line_bundle is None else line_bundle
            assert selected_line.scheme() is self, (
                f"the line bundle {selected_line} lives on {selected_line.scheme()}, not on {self}"
            )
            assert selected_line.associated_divisor() == divisor, (
                f"the line bundle {selected_line} is O({selected_line.associated_divisor()}), not "
                f"O({divisor})"
            )
            sections = self.divisor_section_space(divisor)
            section = sections(section)
            coordinates = section.to_vector()
            module_sheaf = selected_line.module_sheaf()
            local_components = {}
            for cone in self.gluing_datum().chart_indices():
                chart = self.affine_chart(cone)
                chart_ring = chart.coordinate_algebra()
                scalar_map = chart_ring.algebra_structure_morphism()
                cartier = self.cartier_datum(divisor, cone)
                local_coefficient = chart_ring.zero()
                for character in coordinates.support().domain():
                    coefficient = coordinates(character)
                    shifted = self.character_lattice()(character) - cartier
                    assert cone.dual_cone_contains(shifted), (
                        f"the character {character} of the section is not regular on the chart of "
                        f"{cone} after shifting by m_sigma = {cartier}, so it is not a lattice "
                        f"point of the polytope P_D of {divisor}"
                    )
                    local_coefficient += scalar_map(coefficient) * _character_monomial(
                        shifted,
                        cone,
                        chart,
                    )
                module = module_sheaf.sections_on_chart(cone)
                generator = module.module_generator(next(iter(module.module_generating_set())))
                local_components[cone] = module.scalar_multiple(local_coefficient, generator)
            return module_sheaf.gluing_datum().compatible_section(local_components)

        def zero_subscheme_of_divisor_section(
            self,
            divisor,
            section,
            *,
            line_bundle=None,
            _engine=None,
            construction_data=None,
        ):
            r"""Return the effective Cartier zero scheme of a represented toric section."""
            divisor = self.torus_invariant_divisor_group()(divisor)
            selected_line = self.invertible_sheaf_of_divisor(divisor) if line_bundle is None else line_bundle
            compatible = self.compatible_divisor_section(
                divisor,
                section,
                line_bundle=selected_line,
            )
            section_datum = selected_line.module_sheaf().gluing_datum()
            local_closed = {}
            for cone in self.gluing_datum().chart_indices():
                module = selected_line.module_sheaf().sections_on_chart(cone)
                label = next(iter(module.module_generating_set()))
                coefficient = module.framing_morphism().lift(
                    section_datum.compatible_section_component(compatible, cone)
                )(label)
                local_closed[cone] = self.affine_chart(cone).closed_subscheme(coefficient)
            return self.chartwise_closed_subscheme(
                local_closed,
                name="Zero scheme of a toric divisor section",
                _engine=_engine,
                construction_data=construction_data,
            )

        def divisor_section_characters(self, divisor):
            r"""The characters spanning ``H^0(X, O_X(D))`` (CLS Prop. 4.3.3).

            ``H^0(X,O_X(D))`` has the characters ``chi^m`` for ``m`` a lattice
            point of ``P_D`` as a basis, so the lattice points of the divisor
            polytope are returned as elements of ``M``.
            """
            # divisor_polytope is constructed in the selected character
            # lattice, and its integral_points() already returns elements of
            # that exact lattice.  Re-entering them through _owned_vector
            # treats a lattice element as a coordinate tuple; for a character
            # lattice represented as Hom(N, ZZ), iteration instead indexes the
            # matrix-shaped morphism and is not coordinate extraction.
            return self.divisor_polytope(divisor).integral_points()

        @cached_method
        def divisor_section_space(self, divisor):
            r"""Return ``H^0(X,O_X(D))`` with the character basis of ``P_D cap M``.

            For a torus-invariant Cartier divisor on a complete toric variety,
            the characters ``chi^m`` with ``m`` a lattice point of ``P_D`` form
            a basis of global sections (CLS Prop. 4.3.3).  The represented
            vector space therefore uses those actual character-lattice elements
            as its basis labels rather than replacing them by positions.
            """
            assert self.is_cartier(divisor), (
                f"H^0(X, O(D)) of {self} is computed from the lattice points of P_D only for Cartier "
                f"D, but {divisor} is not Cartier"
            )
            return self.scheme_base_ring().free_module(self.divisor_section_characters(divisor))

        def cox_monomial_of_section(self, divisor, character):
            r"""Return the Cox monomial representing ``chi^m`` as a section of ``O(D)``.

            For ``D=sum a_rho D_rho`` and ``m in P_D cap M``, the homogeneous
            Cox monomial is ``prod x_rho^(<m,u_rho>+a_rho)``.  Membership in
            ``P_D`` is exactly the nonnegativity of these exponents.
            """
            divisor = self.weil_divisor_group()(divisor)
            character = self.character_lattice()(character)
            sections = self.divisor_section_characters(divisor)
            assert character in sections, (
                f"the character {character} is not a lattice point of the polytope P_D of "
                f"{divisor}, so it is not a section of O(D) on {self}"
            )
            cox = self.cox_ring()
            coordinates = divisor.to_vector()
            zero = _integers().zero()
            monomial = cox.one()
            for label in cox.algebra_generating_set():
                ray = cox.cox_rays()[label]
                exponent = self.order_of_character_along_prime_divisor(character, ray)
                exponent += coordinates(ray)
                assert exponent >= zero, (
                    f"the Cox monomial of {character} as a section of O({divisor}) has the negative "
                    f"exponent {exponent} at the ray {ray}, so {character} is not in P_D"
                )
                monomial *= cox.algebra_generator(label) ** int(exponent)
            return monomial

        @cached_method
        def homogeneous_polynomial_section_space(self, divisor):
            r"""Return ``H^0(X,O(D))`` with its actual Cox monomials as basis labels."""
            divisor = self.weil_divisor_group()(divisor)
            characters = self.divisor_section_characters(divisor)
            monomials = FiniteOrderedSets().from_indexed(
                characters,
                lambda character: self.cox_monomial_of_section(divisor, character),
                name="Homogeneous Cox monomial sections",
            )
            return self.scheme_base_ring().free_module(monomials)

        @cached_method
        def section_homogeneous_polynomial_isomorphism(self, divisor):
            r"""Identify character sections with homogeneous Cox polynomials linearly."""
            divisor = self.weil_divisor_group()(divisor)
            source = self.divisor_section_space(divisor)
            target = self.homogeneous_polynomial_section_space(divisor)
            forward = source.module_category().Mor(source, target)(
                {
                    character: target.module_generator(
                        self.cox_monomial_of_section(divisor, character)
                    )
                    for character in source.module_generating_set()
                }
            )
            inverse = target.module_category().Mor(target, source)(
                {
                    monomial: source.module_generator(character)
                    for character, monomial in zip(
                        source.module_generating_set(),
                        target.module_generating_set(),
                        strict=True,
                    )
                }
            )
            return source.module_category().Core().Mor(source, target)(forward, inverse)

        def complete_linear_system(self, divisor):
            r"""Return ``|D|`` as the projectivization of the represented section space."""
            from sage_extensions.categories.divisors.linear_systems import (
                _complete_linear_system,
            )

            return _complete_linear_system(
                self,
                self.weil_divisor_group()(divisor),
                self.divisor_section_space(divisor),
            )

        def _engine_toric_divisor(self, divisor):
            r"""Return Sage's private toric divisor; see :func:\`_engine_toric_divisor\`."""
            divisor = self.weil_divisor_group()(divisor)
            coefficients = [
                int(self.weil_multiplicity(divisor, ray))
                for ray in self.fan().cones(1)
            ]
            return _engine_scheme(self).divisor(coefficients)

        def associated_projective_morphism(self, divisor):
            r"""Return the morphism ``phi_|D|: X -> |D|`` for a basepoint-free divisor.

            The monomial basis of ``H^0(X,O_X(D))`` indexed by ``P_D cap M``
            is the same basis used by Sage's toric divisor engine.  Evaluating
            those sections in homogeneous Cox coordinates gives the Kodaira
            map to the ambient projective space of the complete linear system.
            Basepoint-freeness is the exact condition ensuring this rational
            map is everywhere defined.
            """
            divisor = self.weil_divisor_group()(divisor)
            assert self.is_basepoint_free(divisor), (
                f"the map to projective space given by |{divisor}| on {self} is a morphism only "
                "when the divisor is basepoint-free, and this one is not"
            )
            system = self.complete_linear_system(divisor)
            line = self.invertible_sheaf_of_divisor(divisor)
            section_space = system.section_space()
            basis = tuple(section_space.module_generators())
            sections = tuple(self.compatible_divisor_section(divisor, section, line_bundle=line) for section in basis)
            datum = self.finite_affine_atlas()
            section_datum = line.module_sheaf().gluing_datum()

            def local_map(index):
                module = line.local_module(index)
                label = next(iter(module.module_generating_set()))
                coordinates = tuple(
                    module.framing_morphism().lift(
                        section_datum.compatible_section_component(section, index)
                    )(label)
                    for section in sections
                )
                return datum.chart(index).projective_morphism_from_coordinates(system, coordinates)

            return self.Mor(system)(finite_indexed_family(datum.chart_index_set(), local_map))

        def weight_cohomology_complex(self, divisor, weight):
            r"""Return the finite complex computing one toric line-bundle weight piece."""
            from sage_extensions.categories.schemes.geometric_cohomology import (
                _toric_weight_cohomology_complex,
            )

            return _toric_weight_cohomology_complex(self, divisor, weight)

        def _weight_cohomology_presentation(self, divisor, weight):
            r"""Return owned module pieces and differentials for one toric weight.

            Protected ToricSchemes computation contract under OWN-05--07.  The
            sole caller is geometric_cohomology._toric_weight_cohomology_complex.
            Inputs are an owned toric divisor and character; outputs are
            dictionaries of owned free modules and owned module morphisms.
            Sage's divisor, simplicial complex, chain complex and incidence
            matrices remain inside this toric adapter because no public Sage
            operation exposes the augmented incidence maps required by the
            represented cohomology complex.
            """
            base = self.scheme_base_ring()
            divisor = self.weil_divisor_group()(divisor)
            weight = self.character_lattice()(weight)
            engine_divisor = self._engine_toric_divisor(divisor)
            simplicial = engine_divisor._sheaf_complex(
                _engine_vector(self.character_lattice(), weight)
            )
            if int(simplicial.dimension()) == -1:
                degree_zero = base.free_module(1)
                degree_one = base.free_module(0)
                return (
                    {0: degree_zero, 1: degree_one},
                    {
                        0: degree_zero.module_category().Mor(
                            degree_zero, degree_one
                        )({0: degree_one.zero()})
                    },
                )

            engine = simplicial.chain_complex(
                augmented=True,
                base_ring=SageZZ,
                cochain=True,
            )
            top = int(simplicial.dimension())
            matrices = {
                q: engine.differential(q)
                for q in range(-1, top + 1)
            }
            pieces = {
                q + 1: base.free_module(engine_matrix.ncols())
                for q, engine_matrix in matrices.items()
            }
            pieces[top + 2] = base.free_module(0)
            differentials = {
                q + 1: _owned_incidence_morphism(
                    base,
                    pieces[q + 1],
                    pieces[q + 2],
                    engine_matrix,
                )
                for q, engine_matrix in matrices.items()
            }
            return pieces, differentials

        def _line_bundle_cohomology_candidate_weights(self, divisor):
            r"""Return the finite owned character set containing every nonzero weight.

            Protected ToricSchemes computation contract under OWN-05--07.  The
            sole caller is geometric_cohomology._toric_line_bundle_cohomology.
            The private Sage support polyhedron is consumed here; only owned
            character-lattice elements cross the boundary.
            """
            divisor = self.weil_divisor_group()(divisor)
            support = self._engine_toric_divisor(divisor)._sheaf_cohomology_support()
            characters = self.character_lattice()
            return finite_ordered_set(
                tuple(
                    _owned_vector(characters, point)
                    for point in support.integral_points()
                )
            )

        def weight_cohomology(self, divisor, weight, degree):
            r"""Return one weight piece ``H^degree(X,O_X(D))_weight``."""
            from sage_extensions.categories.schemes.geometric_cohomology import (
                _toric_weight_cohomology,
            )

            return _toric_weight_cohomology(self, divisor, weight, degree)

        def weight_scalar_cochain_map(self, divisor, weight, scalar):
            r"""Return scalar multiplication on the selected toric weight complex."""
            from sage_extensions.categories.schemes.geometric_cohomology import (
                _toric_weight_scalar_cochain_map,
            )

            return _toric_weight_scalar_cochain_map(self, divisor, weight, scalar)

        def weight_scalar_cohomology_map(self, divisor, weight, degree, scalar):
            r"""Return the cohomology map induced by scalar multiplication on a weight complex."""
            from sage_extensions.categories.schemes.geometric_cohomology import (
                _toric_weight_scalar_cohomology_map,
            )

            return _toric_weight_scalar_cohomology_map(
                self, divisor, weight, degree, scalar
            )

        @cached_method
        def line_bundle_cohomology(self, divisor, degree):
            r"""Return ``H^degree(X,O_X(D))`` from the represented toric weight complexes."""
            from sage_extensions.categories.schemes.geometric_cohomology import (
                _toric_line_bundle_cohomology,
            )

            return _toric_line_bundle_cohomology(self, divisor, degree)

        def line_bundle_cohomology_dimensions(self, divisor):
            r"""Return the degree-indexed dimensions of represented ``H^i(X,O_X(D))``."""
            degrees = finite_ordered_set(
                tuple(NN(degree) for degree in range(int(self.dimension()) + 1))
            )
            return finite_indexed_family(
                degrees,
                lambda degree: NN(
                    self.line_bundle_cohomology(divisor, int(degree)).dimension()
                ),
                name=f"Line-bundle cohomology dimensions of {divisor}",
            )

        def integral_singular_cohomology(self, degree):
            r"""``H^degree(X(CC); ZZ)``, the cohomology of the complex realization along ``QQ -> CC``."""
            from sage_extensions.categories.schemes.geometric_cohomology import (
                _integral_singular_cohomology_over_rationals,
            )
            return _integral_singular_cohomology_over_rationals(self, degree)

        @cached_method
        def cycle_class_isomorphism(self, codimension):
            r"""Return the integral cycle-class isomorphism in the supported toric complex realization."""
            from sage_extensions.categories.schemes.geometric_cohomology import (
                _toric_cycle_class_isomorphism,
            )

            return _toric_cycle_class_isomorphism(self, codimension)

        @cached_method
        def picard_to_chow_isomorphism(self):
            r"""Return ``Pic(X) -> CH^1(X)`` in the represented smooth complete surface regime."""
            from sage_extensions.categories.schemes.geometric_cohomology import (
                _toric_picard_to_chow_isomorphism,
            )

            return _toric_picard_to_chow_isomorphism(self)

        @cached_method
        def middle_cohomology_form(self):
            r"""Return the cup-product form on ``H^2(X(CC),ZZ)`` for a smooth complete toric surface."""
            from sage_extensions.categories.schemes.geometric_cohomology import (
                _toric_middle_cohomology_form,
            )

            return _toric_middle_cohomology_form(self)

        @cached_method
        def _hodge_structure(self):
            r"""The Hodge structure on ``H^*(X(CC); ZZ)``.

            The required value is ``⊕_k H^k(X(CC); ZZ)`` as an object of
            ``MixedHodgeStructures(ZZ)`` whose weight filtration splits with
            ``Gr^W_k = H^k`` in ``HodgeStructures(ZZ, k)`` (Deligne, Théorie de
            Hodge II, (2.1.1), (2.3.1)).
            """
            from sage_extensions.categories.schemes.geometric_cohomology import (
                _toric_hodge_structure,
            )

            return _toric_hodge_structure(self)

        def invertible_sheaf_of_divisor(self, divisor):
            r"""Return ``O_X(D)`` from the Cartier characters on the toric atlas.

            If ``m_sigma`` is the selected Cartier datum on ``U_sigma``, then
            ``chi^{m_sigma}`` is the local generator of ``O_X(D)``.  Hence on
            ``U_sigma cap U_tau`` the transition is
            ``chi^(m_sigma-m_tau)``.  These differences vanish on the common
            face, so the characters are units on the overlap and satisfy the
            cocycle additively.
            """
            from sage_extensions.categories.divisors.invertible_sheaves import (
                _finite_atlas_invertible_sheaf,
            )

            divisor = self.weil_divisor_group()(divisor)
            assert self.is_cartier(divisor), (
                f"O(D) is an invertible sheaf only for Cartier D, but {divisor} is not Cartier on {self}"
            )
            datum = self.finite_affine_atlas()
            units = {}
            for source_cone, target_cone in datum.transition_index_set():
                face = source_cone.intersection(target_cone)
                difference = self.cartier_datum(divisor, source_cone) - self.cartier_datum(
                    divisor,
                    target_cone,
                )
                units[source_cone, target_cone] = _character_on_overlap(
                    difference,
                    face,
                    source_cone,
                    self.scheme_base_ring(),
                )
            section_space = (
                self.divisor_section_space(divisor)
                if self.fan().is_complete()
                else None
            )
            return _finite_atlas_invertible_sheaf(
                datum,
                units,
                section_space=section_space,
                associated_divisor=divisor,
            )

        def ample_divisor_self_intersection(self, divisor):
            r"""Return ``D^2`` from the normalized area of ``P_D``.

            On a smooth complete toric surface a nef divisor satisfies
            ``D^2 = Vol(P_D)`` for lattice-normalized volume.  The supported
            interface asks for ampleness, which implies nefness and is already
            decided by the toric support-function criterion above.
            """
            assert int(self.dimension()) == 2, (
                f"the self-intersection D^2 as a polytope volume is computed for toric surfaces, but "
                f"{self} has dimension {self.dimension()}"
            )
            assert self.fan().is_smooth() and self.fan().is_complete(), (
                f"the self-intersection D^2 as a polytope volume is computed on a smooth complete "
                f"toric surface, but the fan of {self} is smooth: {self.fan().is_smooth()}, "
                f"complete: {self.fan().is_complete()}"
            )
            assert self.is_ample(divisor), (
                f"the self-intersection D^2 is computed as the volume of P_D only for ample D, but "
                f"{divisor} is not ample on {self}"
            )
            return self.divisor_polytope(divisor).normalized_volume()

        def ample_divisor_intersection(self, left, right):
            r"""Return ``left . right`` by polarization on a smooth complete toric surface."""
            group = self.weil_divisor_group()
            left = group(left)
            right = group(right)
            assert self.is_ample(left) and self.is_ample(right), (
                f"the intersection number D.E is computed by polarization only for ample D and E, "
                f"but {left} or {right} is not ample on {self}"
            )
            numerator = (
                self.ample_divisor_self_intersection(left + right)
                - self.ample_divisor_self_intersection(left)
                - self.ample_divisor_self_intersection(right)
            )
            quotient, remainder = numerator.quo_rem(_integers()(2))
            assert remainder == _integers().zero(), (
                f"(D+E)^2 - D^2 - E^2 = {numerator} for D = {left} and E = {right} on {self} is "
                "odd, but it must equal 2 D.E"
            )
            return quotient

        def divisor_intersection(self, left, right):
            r"""Return ``left . right`` on a smooth complete toric surface.

            The private Sage toric cohomology ring computes the exact divisor
            classes and integration.  The public result is crossed back to the
            owned integer ring; smoothness guarantees integrality.
            """
            assert int(self.dimension()) == 2, (
                f"the intersection pairing of divisors is computed for toric surfaces, but {self} "
                f"has dimension {self.dimension()}"
            )
            assert self.fan().is_smooth() and self.fan().is_complete(), (
                f"the intersection pairing of divisors is computed on a smooth complete toric "
                f"surface, but the fan of {self} is smooth: {self.fan().is_smooth()}, complete: "
                f"{self.fan().is_complete()}"
            )
            group = self.weil_divisor_group()
            left = group(left)
            right = group(right)
            rays = self.fan().cones(1)
            engine = _engine_scheme(self)

            def engine_divisor(divisor):
                coordinates = divisor.to_vector()
                return engine.divisor(
                    [int(coordinates(ray)) for ray in rays]
                )

            cohomology = engine.cohomology_ring()
            value = engine.integrate(
                cohomology(engine_divisor(left)) * cohomology(engine_divisor(right))
            )
            return _owned_engine_element(_integers(), SageZZ(value))

        @cached_method
        def _picard_intersection_pairing(self):
            r"""Return the integral intersection pairing on ``Pic(X)`` for a smooth complete toric surface."""
            assert int(self.dimension()) == 2, (
                f"the intersection pairing on Pic is computed for toric surfaces, but {self} has "
                f"dimension {self.dimension()}"
            )
            assert self.fan().is_smooth() and self.fan().is_complete(), (
                f"the intersection pairing on Pic is computed on a smooth complete toric surface, "
                f"but the fan of {self} is smooth: {self.fan().is_smooth()}, complete: "
                f"{self.fan().is_complete()}"
            )
            picard = self.picard_group()
            weil = self.weil_divisor_group()
            integers = _integers()
            values = integers.regular_module()
            return BilinearMap(
                picard,
                picard,
                values,
                lambda left_label, right_label: self.divisor_intersection(
                    weil.module_generator(left_label),
                    weil.module_generator(right_label),
                ),
            )

        def _is_del_pezzo(self) -> bool:
            r"""Decide Del Pezzo for a represented projective toric surface."""
            assert int(self.dimension()) == 2 and self.fan().is_complete(), (
                f"the toric Del Pezzo algorithm applies to complete toric surfaces, but {self} has "
                f"dimension {self.dimension()} and complete fan: {self.fan().is_complete()}"
            )
            return bool(self.is_ample(-self.canonical_divisor()))

        def _del_pezzo_degree(self):
            r"""Return ``(-K_X)^2`` by toric divisor intersection."""
            anticanonical = -self.canonical_divisor()
            return self.divisor_intersection(anticanonical, anticanonical)

        @cached_method
        def chow_group(self, cycle_dimension):
            r"""Return the integral Chow group ``A_k(X)`` in the selected degree.

            Orbit closures generate the full Chow group of a toric variety,
            and Sage's toric Chow implementation computes their exact rational-
            equivalence quotient, including integral torsion.  The Smith-form computation
            returns a finitely generated ``ZZ``-module in invariant-factor
            form; crossing those invariants back through a diagonal owned
            presentation keeps the computation private while the public result
            remains an owned module carrying ``X`` and ``k``.
            """
            cycle_dimension = int(cycle_dimension)
            dimension = int(self.dimension())
            assert 0 <= cycle_dimension <= dimension, (
                f"the Chow group CH_k of {self} is defined for 0 <= k <= {dimension}, but k = "
                f"{cycle_dimension}"
            )
            engine = _engine_scheme(self).Chow_group().degree(cycle_dimension).module()
            invariants = tuple(int(value) for value in engine.invariants())
            integers = _integers()
            rank = len(invariants)
            free = integers.free_module(rank)
            relations = integers.free_module(rank)
            relation = relations.module_category().Mor(relations, free)(
                {
                    position: (
                        integers(invariant) * free.module_generator(position)
                        if invariant != 0
                        else free.zero()
                    )
                    for position, invariant in enumerate(invariants)
                }
            )

            return ChowGroups(integers)(
                self,
                cycle_dimension,
                relation,
            )

        @cached_method
        def torus_invariant_cycle_group(self, cycle_dimension):
            r"""Return the free group on orbit closures of dimension ``cycle_dimension``."""
            cycle_dimension = int(cycle_dimension)
            dimension = int(self.dimension())
            assert 0 <= cycle_dimension <= dimension, (
                f"torus-invariant cycles of dimension k on {self} exist for 0 <= k <= {dimension}, "
                f"but k = {cycle_dimension}"
            )
            cone_dimension = dimension - cycle_dimension
            return TorusInvariantCycleGroups(_integers())(
                self,
                cycle_dimension,
                self.fan().cones(cone_dimension),
            )

        @cached_method
        def torus_invariant_cycle_class_map(self, cycle_dimension):
            r"""Return the rational-equivalence quotient from invariant cycles to ``CH_k(X)``."""
            cycle_dimension = int(cycle_dimension)
            source = self.torus_invariant_cycle_group(cycle_dimension)
            target = self.chow_group(cycle_dimension)
            engine_chow = _engine_scheme(self).Chow_group()
            engine_degree = engine_chow.degree(cycle_dimension).module()
            target_labels = tuple(target.module_generating_set())
            integers = _integers()

            def image(cone):
                coordinates = tuple(engine_degree(engine_chow(_engine_cone(cone))).vector())
                assert len(coordinates) == len(target_labels), (
                    f"the class of the orbit closure of {cone} in CH_{cycle_dimension} has "
                    f"{len(coordinates)} coordinates, but the Chow group has "
                    f"{len(target_labels)} generators"
                )
                return target.linear_combination(
                    {
                        label: integers(coefficient)
                        for label, coefficient in zip(target_labels, coordinates, strict=True)
                        if coefficient
                    }
                )

            return source.module_category().Mor(source, target)(image)

        @cached_method
        def cox_ring(self):
            r"""Return the Cox homogeneous coordinate ring graded by ``Cl(X)``."""
            from sage_extensions.categories.divisors.cox_rings import _cox_ring

            return _cox_ring(self)

        @cached_method
        def section_ring(self, divisor):
            r"""Return ``oplus_{n>=0} H^0(X,O_X(nD))`` as an owned graded algebra."""
            from sage_extensions.categories.divisors.section_rings import (
                SectionRings,
            )

            return SectionRings(self.scheme_base_ring())(
                self,
                self.weil_divisor_group()(divisor),
            )

        def log_pair(self, boundary_divisor=None):
            r"""Return ``(X, Delta)`` for a torus-invariant boundary ``Delta``.

            With no boundary supplied, ``Delta`` is the full toric boundary
            ``sum_rho D_rho``.
            """
            from sage_extensions.categories.schemes.log_pairs import (
                _toric_log_pair,
            )

            selected = (
                self.toric_boundary_divisor()
                if boundary_divisor is None
                else self.torus_invariant_divisor_group()(boundary_divisor)
            )
            return _toric_log_pair(self, selected)

        def is_polarized(self) -> bool:
            r"""Whether this variety was constructed from a polytope."""
            return self._polarizing_polytope is not None

        def polarizing_polytope(self):
            r"""The lattice polytope ``P`` with ``X = X_P``.

            A projective toric variety admits many ample divisors and so many
            polytopes; this returns the one the construction was given, and
            asserts when the variety came from a bare fan.
            """
            assert self.is_polarized(), (
                f"{self} was constructed from a fan, not from a lattice polytope, so it has no "
                "polarizing polytope; construct it from a lattice polytope to have one"
            )
            return self._polarizing_polytope

        def is_isomorphic_to(self, other) -> bool:
            r"""Whether an isomorphism of fans identifies the two varieties.

            CLS Thm. 3.3.4: a lattice isomorphism carrying one fan onto the
            other induces an isomorphism of the toric varieties over any base.
            """
            assert self.scheme_base_ring() is other.scheme_base_ring(), (
                f"{self} and {other} lie over different base rings, {self.scheme_base_ring()} and "
                f"{other.scheme_base_ring()}, so they are not isomorphic as varieties over one base"
            )
            return self.fan().is_isomorphic(other.fan())

        def is_projective_space(self) -> bool:
            r"""Whether ``X`` is ``P^n`` for ``n`` its own dimension."""
            comparison = RationalPolyhedralFans(
                self.cocharacter_lattice()
            ).projective_space_fan()
            return self.fan().is_isomorphic(comparison)

        def is_weighted_projective_space(self, weights) -> bool:
            r"""Whether ``X`` is ``P(q_0,...,q_n)`` for the stated weights."""
            comparison = RationalPolyhedralFans(
                self.cocharacter_lattice()
            ).weighted_projective_space_fan(weights)
            return self.fan().is_isomorphic(comparison)

        def is_hirzebruch_surface(self, twist) -> bool:
            r"""Whether ``X`` is the Hirzebruch surface ``F_a``."""
            comparison = RationalPolyhedralFans(
                self.cocharacter_lattice()
            ).hirzebruch_surface_fan(twist)
            return self.fan().is_isomorphic(comparison)

        def toric_morphism(self, lattice_morphism, codomain):
            r"""The toric morphism induced by a fan-compatible lattice map.

            A morphism ``phi: N -> N'`` is compatible with ``Sigma``, ``Sigma'``
            when every cone of ``Sigma`` maps into some cone of ``Sigma'``, and
            such a ``phi`` induces an equivariant morphism ``X_Sigma ->
            X_{Sigma'}`` (CLS Thm. 3.3.4).  Each maximal cone ``sigma`` is sent
            to the first maximal cone of ``Sigma'`` containing ``phi(sigma)``,
            and the chart of ``sigma`` maps into that chart by the pullback of
            characters along ``phi``.  The morphism is constructed by
            ``Mor(X_Sigma, X_Sigma')`` from the rule building it there.
            """
            codomain_fan = codomain.fan()
            assert self.fan().is_compatible_with(lattice_morphism, codomain_fan), (
                f"the lattice map {lattice_morphism} does not induce a toric morphism "
                f"{self} -> {codomain}: it does not carry every cone of the fan of {self} into a "
                "cone of the fan of the codomain (CLS Def. 3.3.1)"
            )
            base = self.scheme_base_ring()
            maximal_cones = self.fan().maximal_cones()
            chart_targets = finite_indexed_family(
                maximal_cones,
                lambda source_cone: codomain_fan.maximal_cone_containing_image(
                    lattice_morphism,
                    source_cone,
                ),
                name="Target charts of a toric morphism",
            )
            chart_pullbacks = finite_indexed_family(
                maximal_cones,
                lambda source_cone: _toric_chart_pullback(
                    lattice_morphism,
                    source_cone,
                    chart_targets.value(source_cone),
                    base,
                ),
                name="Chart pullbacks of a toric morphism",
            )
            engine_base = _engine_ring(base)
            native = None
            if bool(engine_base.is_field()):
                native = _engine_scheme(self).hom(
                    _engine_fan_morphism(lattice_morphism, self.fan(), codomain_fan),
                    _engine_scheme(codomain),
                )
            return _scheme_mor_category(self, codomain)(
                lambda mor: mor.element_class(
                    mor,
                    native,
                    mor=mor,
                    toric_lattice_morphism=lattice_morphism,
                    toric_chart_targets=chart_targets,
                    toric_chart_pullbacks=chart_pullbacks,
                )
            )


def _engine_fan_morphism(lattice_morphism, domain_fan, codomain_fan):
    r"""Sage's fan morphism of a compatible lattice map, on row vectors.

    Sage's ``FanMorphism`` acts on rays written as row vectors from the right,
    so the matrix rows are the images of the chosen generators of ``N``.  Its
    constructor performs the cone-containment check and refuses an
    incompatible map.
    """
    from sage.geometry.fan_morphism import FanMorphism

    domain_lattice = domain_fan.cocharacter_lattice()
    codomain_lattice = codomain_fan.cocharacter_lattice()
    assert lattice_morphism.domain() is domain_lattice, (
        f"the lattice map {lattice_morphism} must start at the lattice N = {domain_lattice} of "
        f"the domain fan, but it starts at {lattice_morphism.domain()}"
    )
    assert lattice_morphism.codomain() is codomain_lattice, (
        f"the lattice map {lattice_morphism} must end at the lattice N' = {codomain_lattice} of "
        f"the codomain fan, but it ends at {lattice_morphism.codomain()}"
    )
    rows = _engine_matrix(
        SageZZ,
        [
            list(
                _engine_vector(
                    codomain_lattice,
                    lattice_morphism(domain_lattice.module_generator(label)),
                )
            )
            for label in domain_lattice.module_generating_set()
        ],
    )
    return FanMorphism(rows, _engine_fan(domain_fan), _engine_fan(codomain_fan))


def _toric_variety(fan, base_ring, polarizing_polytope=None, placements=(), **level_data):
    r"""The toric scheme ``X_Sigma`` of a fan over a ring, an object of ``ToricSchemes(R)``.

    ``X_Sigma`` is the scheme glued from the affine charts of the maximal cones
    along the face localizations of their pairwise intersections (CLS
    Thm. 3.1.5); the atlas is indexed by the maximal cones themselves, so a
    chart is asked for by the cone it belongs to.  The gluing constructs it
    in ``ToricSchemes(R)`` with the fan and the polarizing polytope as that
    level's data, together with the placements the fan decides at
    construction (smooth exactly when the fan is, CLS Thm. 3.1.19; over a
    field, proper exactly when the fan is complete, CLS Thm. 3.4.1; a curve or
    a surface by the rank of ``N``; every complete toric surface is projective,
    CLS Prop. 6.3.25) and the further ``placements`` a caller constructs it in.
    Over a field, Sage's ``ToricVariety`` of the same fan
    is retained as a private realization; over a general base the owned affine
    gluing is the realization.
    """
    base = _own_ring(base_ring)
    assert fan in RationalPolyhedralFans(fan.cocharacter_lattice()), (
        f"a toric variety is built from a rational polyhedral fan, but {fan} is in {fan.category()}"
    )
    # These exact fan predicates may lower to nontrivial private Sage
    # computations. They are invariants of this selected fan, so evaluate
    # each once and reuse the verdict while determining the object's proven
    # scheme placements.
    smooth = fan.is_smooth()
    complete = fan.is_complete()
    dimension = int(fan.dimension())
    decided = [ToricSchemes(base)]
    if smooth:
        decided.append(GorensteinToricSchemes(base))
    # A fan isomorphic to the standard projective-space fan in dimension n
    # must have n+1 rays and n+1 maximal cones. Use these exact combinatorial
    # invariants to avoid running Sage's lattice fan-isomorphism search for
    # every other fan; the isomorphism test remains the proof when the
    # necessary counts agree.
    if (
        fan.rays().cardinality() == dimension + 1
        and fan.maximal_cones().cardinality() == dimension + 1
    ):
        projective_fan = RationalPolyhedralFans(
            fan.cocharacter_lattice()
        ).projective_space_fan()
        if fan.is_isomorphic(projective_fan):
            decided.append(ToricProjectiveSpaces(base))
    if smooth:
        decided.append(Schemes(base).Smooth())
    if base in OwnedFields() and complete:
        decided.append(Schemes(base).Proper())
    if base in OwnedIntegralDomains():
        match dimension:
            case 1:
                decided.append(Curves(base))
            case 2:
                decided.append(Surfaces(base))
            case _:
                pass
    match (base in OwnedFields(), dimension, complete):
        case (True, 2, True):
            decided.append(Surfaces(base).Projective())
        case _:
            pass
    engine_base = _engine_ring(base)
    native = (
        _SageToricVariety(_engine_fan(fan), base_ring=engine_base)
        if bool(engine_base.is_field())
        else None
    )
    cones = fan.maximal_cones()
    return Schemes(base).glue_affine_atlas(
        {cone: _affine_chart(cone, base) for cone in cones},
        tuple(
            _face_transition(source_cone, target_cone, base)
            for source_cone, target_cone in combinations(cones, 2)
        ),
        placements=(*decided, *placements),
        scheme_engine=native,
        toric_fan=fan,
        polarizing_polytope=polarizing_polytope,
        **level_data,
    )


class GorensteinToricSchemes(OwnedCategoryOverBaseRing):
    r"""Toric schemes whose canonical toric Weil divisor is Cartier."""

    def super_categories(self):
        return [ToricSchemes(self.base_ring())]

    def an_object(self):
        return self(ToricSchemes(self.base_ring()).an_object())

    def _call_(self, scheme):
        from sage_extensions.refine import refine

        if scheme not in ToricSchemes(self.base_ring()) or not scheme.is_cartier(scheme.canonical_divisor()):
            raise ValueError("the canonical toric divisor must be Cartier")
        return refine(scheme, self)

    class ParentMethods:
        @cached_method
        def canonical_line_bundle(self):
            r"""The invertible dualizing sheaf associated with Cartier ``K_X``."""
            return self.invertible_sheaf_of_divisor(self.canonical_divisor())

        def canonical_bundle(self, *args, **kwargs):
            return self.canonical_line_bundle(*args, **kwargs)

        @cached_method
        def anticanonical_line_bundle(self):
            r"""The invertible sheaf associated with Cartier ``-K_X``."""
            return self.invertible_sheaf_of_divisor(-self.canonical_divisor())

        def anticanonical_bundle(self, *args, **kwargs):
            return self.anticanonical_line_bundle(*args, **kwargs)


class ToricProjectiveSpaces(OwnedCategoryOverBaseRing):
    r"""Toric projective spaces with a distinguished fan realization."""

    def super_categories(self):
        return [GorensteinToricSchemes(self.base_ring())]

    def an_object(self):
        return self(ToricSchemes(self.base_ring()).an_object())

    def _call_(self, scheme):
        from sage_extensions.refine import refine

        if scheme not in ToricSchemes(self.base_ring()) or not scheme.is_projective_space():
            raise ValueError("the chosen toric fan must be projective space")
        return refine(scheme, self)
    class ParentMethods:
        @cached_method
        def hyperplane_divisor(self):
            r"""Return a torus-invariant hyperplane divisor on toric ``P^n``.

            Every ray divisor on the standard projective-space fan represents
            the positive generator of ``Pic(P^n)``.  Thus after the exact fan
            identification performed by ``is_projective_space``, selecting the
            first ray gives one distinguished representative of that class.
            """
            assert self.is_projective_space(), (
                f"a hyperplane divisor is defined here only on projective space, but {self} is not "
                "a toric projective space"
            )
            ray = next(iter(self.fan().cones(1)))
            return self.torus_invariant_prime_divisor(ray)

        @cached_method
        def hyperplane_line_bundle(self):
            r"""Return ``O_{P^n}(1)`` from the selected hyperplane divisor."""
            return self.invertible_sheaf_of_divisor(self.hyperplane_divisor())

        def O1(self, *args, **kwargs):
            return self.hyperplane_line_bundle(*args, **kwargs)



class SmoothCompleteRationalToricSchemes(OwnedCategoryOverBaseRing):
    r"""Smooth complete toric varieties over the chosen rational realization.

    The pointed fundamental-group realization uses a torus-fixed basepoint
    and computes the trivial group only in this regime.
    """

    def super_categories(self):
        if _engine_ring(self.base_ring()) is not SageQQ:
            raise TypeError("this topological realization is defined over QQ")
        return [ToricSchemes(self.base_ring())]

    def an_object(self):
        return self(ToricSchemes(self.base_ring()).an_object())

    def _call_(self, scheme):
        from sage_extensions.refine import refine

        if scheme not in ToricSchemes(self.base_ring()) or not (scheme.fan().is_smooth() and scheme.fan().is_complete()):
            raise ValueError("smooth complete rational toric realization requires a smooth complete fan")
        return refine(scheme, self)

    class ParentMethods:
        @cached_method
        def fundamental_group(self, base_point_cone=None):
            r"""Pointed fundamental group of this smooth complete toric realization."""
            from sage_extensions.categories.schemes.geometric_cohomology import _toric_fundamental_group
            return _toric_fundamental_group(self, base_point_cone)


__all__ = ["ToricSchemes", "ToricProjectiveSpaces", "GorensteinToricSchemes", "SmoothCompleteRationalToricSchemes"]
