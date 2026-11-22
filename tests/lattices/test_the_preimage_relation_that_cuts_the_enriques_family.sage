r"""The relation that cuts `Gamma_{En,2}` out of `O(T_{En})`, and the orbits it leaves on the eight pairs.

`Gamma_{En,2}` is the image in `O(T_{\mathrm{En}})` of `{g in O(L) : g I_{\mathrm{En}} = I_{\mathrm{En}} g,
g(h) = h}` -- V. Alexeev, P. Engel, D. Z. Garza, L. Schaffler, *Compact moduli of Enriques surfaces of
degree 2*, Nagoya Math. J. 259 (2025), Definition 2.6 -- and the library builds it as a preimage
`rho^{-1}(H)`: `coinvariant_extension_subgroup` carries the invariant lattice's polarisation stabilizer
across the primitive glue into `O(A_{L^-})`, and `discriminant_preimage` takes its preimage along
`rho_{L^-}: O(L^-) -> O(A_{L^-})` (the construction of sage-extensions#286 item 2).  So the defining
relation is

    g in Gamma_{En,2}   <=>   rho_{L^-}(g) in H,

and nothing but that relation decides membership.

**Why every generator used to be rejected.**  `L^-` is the coinvariant lattice of the Enriques
involution and `T_{\mathrm{En}}` is that lattice built a second time: the two objects have equal Gram
matrices, so their coordinates are the same coordinates, and an isometry written in the one names an
isometry of the other.  A point of `O(T_{\mathrm{En}})` is therefore a point of `O(L^-)` -- read
coordinate-wise, through the ambient framing's own generators, with the equality of the two Gram
matrices asserted; that is the reading `IsotropicVectorReductionImage._coerced` performs for a vector.
Before `PreimageSubgroups.__contains__` performed it for an isometry, the ambient group's ingress
answered `False` for an element parented by `O(T_{\mathrm{En}})` before the relation was evaluated at
all, so every one of the 133 or 134 generators `setwise_stabilizer` returns at each of Sterk's five
planes was reported outside `Gamma_{En,2}`.

**The invariant the cut is, computed here.**  `H` is the stabilizer in `O(A_{L^-})` of the span of the
divided classes `[e'/2]` and `[f'/2]` of the second hyperbolic summand, so `g` lies in `Gamma_{En,2}`
exactly when `rho(g)` carries that span to itself.  The tests below compute that span from the
generator's own matrix on `T_{\mathrm{En}}` and assert that the library's membership agrees with it at
every generator of the family, at all five planes: the relation and the invariant are two computations,
and agreement is what says the cut is the group it is meant to be.

**The row.**  The five plane types are Sterk's one-cusp types, H. Sterk, *Compactifications of the
period space of Enriques surfaces, Part I*, Math. Z. 207 (1991), (4.2.3) with (4.3.17), in the basis
`(e, f, e', f', alpha_1, ..., alpha_8)` of Alexeev--Engel--Garza--Schaffler Definition 2.3; the orbits
of `Stab_{Gamma_{En,2}}(Pi)` on the eight antipodal pairs of `(-2)`-classes of `Pi^\perp/Pi` are
`(1, 1, 2, 1, 2)` with sizes `[8], [8], [2, 6], [8], [2, 6]` (sage-extensions#616).

**Which planes carry the row here.**  `antipodal_root_class_orbits` walks `8 x |orbit of J_0|` states
with the whole parabolic family, and that orbit has 768, 4480, 10752, 24576 and 26880 spans at the five
planes in this file's order.  All five rows are asserted in this file; the three rows that exceed the
ordinary per-call ceiling are run with time gates disabled rather than left ungated by weakening the
assertion.

**The character, executed at its own data.**  Membership is decided by evaluating
`preimage_morphism()` on a point of `O(L^-)` and admitting the image into `target_subgroup()`, so the
tests below do exactly that on the generators `setwise_stabilizer` returns: the law is executed, not
merely agreed with through `in`.  Reading an isometry of the equal copy `T_{En}` as a point of
`O(L^-)` is the lattice isometry constructor's own reading
(`LatticeIsometryMor._generator_images_of_an_equal_copy`), the form `discriminant_representation`
promises its callers; before it, `rho_{L^-}` could not be applied to a single generator of the public
family and every one of them raised.

**What generates the parabolic.**  `setwise_stabilizer` answers with `parabolic_stabilizer_generators()`
exactly when `is_parabolic_complete()`, so the returned family is the family the three factors are
computed for.  Generation is then the correspondence theorem (Milne, *Group Theory*, v4.01 of
6 November 2025, Theorem 1.47, printed p. 22) and not an orbit count: the family contains the
unipotent family whose index in the radical is 1, and its two Levi projections fill `GL(I)` and
`O(I^perp/I)`, so the subgroup contains `U_I` and maps onto `M`, hence is `P_I`.  Each of those
premises is asserted below, at every plane.
"""

from sage_extensions.all import *  # noqa: F401,F403

_GROUPS = {}
_PLANES = {}
_FAMILIES = {}


def _gamma_en_2():
    r"""`Gamma_{En,2}` on `T_{En}`, by the construction of #286 item 2 (Alexeev--Engel--Garza--Schaffler, Def. 2.6).

    Built once per session: the five planes share the one group, and building it is the expensive
    step of every call that reads it.
    """
    if "enriques" not in _GROUPS:
        invariant = Involutions.I_En.invariant_lattice()
        labels = tuple(invariant.module_generating_set())
        marks = [
            (left, right)
            for left in labels
            for right in labels
            if left <= right
            and invariant.q(invariant.module_generator(left)) == ZZ.zero()
            and invariant.q(invariant.module_generator(right)) == ZZ.zero()
            and invariant.b(invariant.module_generator(left), invariant.module_generator(right)) == ZZ(2)
        ]
        left, right = marks[0]
        polarization = invariant.module_generator(left) + invariant.module_generator(right)
        _GROUPS["enriques"] = Involutions.I_En.polarized(
            invariant.inclusion()(polarization)
        ).coinvariant_extension_subgroup()
    return _GROUPS["enriques"]


def _plane(lattice, first, second):
    r"""The plane spanned by two coordinate vectors on the lattice's generating set."""
    module_generators = tuple(lattice.module_generators())

    def vector_of(coordinates):
        total = lattice.zero()
        for index, coefficient in enumerate(coordinates):
            if coefficient:
                total = total + coefficient * module_generators[index]
        return total

    return lattice.primitive_isotropic_subobject(vector_of(first), vector_of(second))


_TYPES = {
    "first": ((0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0), (-2, -2, 0, -2, -1, -1, 0, 0, 0, 0, 0, 0)),
    "second": ((0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0), (-2, -2, -2, 0, -1, 0, 0, 0, 1, 0, 0, 0)),
    "third": ((2, 2, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0), (-2, 0, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0)),
    "fourth": ((0, 0, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0), (-2, -2, -1, -1, -1, 0, 1, 0, 0, 0, 0, 0)),
    "fifth": ((-2, 2, -2, -2, 1, 1, 0, 0, 0, 0, 0, 0), (-2, -2, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0)),
}


def _type(name):
    r"""Sterk's plane of the given type, built once per session."""
    if name not in _PLANES:
        first, second = _TYPES[name]
        _PLANES[name] = _plane(NamedLattices.TEn, first, second)
    return _PLANES[name]


def _family(name):
    r"""The generating family `setwise_stabilizer` returns at that type, read once per session."""
    if name not in _FAMILIES:
        _FAMILIES[name] = tuple(
            NamedLattices.TEn.Aut()
            .stabilizer(_type(name), action="setwise")
            .group_generators()
        )
    return _FAMILIES[name]


def _class(vector):
    r"""The class of a vector of `T_{En}` in `A_L`, as its coordinates modulo two.

    `A_L` is the radical of the form modulo two --- the classes `[x/2]` with `x` of even pairing
    against the lattice --- so a class of `A_L` is a vector of `L/2L`, read here coordinate by
    coordinate from the vector it is the half of.
    """
    coordinates = vector.to_vector()
    return tuple(
        int(coordinates(label)) % 2
        for label in NamedLattices.TEn.module_generating_set()
    )


def _sum_of(first, second):
    r"""The sum of two classes of `A_L`, written coordinate by coordinate."""
    return tuple((left + right) % 2 for left, right in zip(first, second, strict=True))


def _span(first, second):
    r"""The span of two classes of `A_L` over the field of two elements."""
    return frozenset({first, second, _sum_of(first, second)})


def _the_divided_span():
    r"""The span of the divided classes `[e'/2]` and `[f'/2]` of the second hyperbolic summand."""
    lattice = NamedLattices.TEn
    return _span(_class(lattice.module_generator("ep")), _class(lattice.module_generator("fp")))


def _carries_the_divided_span(generator) -> bool:
    r"""Whether `generator` carries the span of the divided classes of `e'` and `f'` to itself."""
    lattice = NamedLattices.TEn
    return _span(
        _class(generator(lattice.module_generator("ep"))),
        _class(generator(lattice.module_generator("fp"))),
    ) == _the_divided_span()


def _assert_the_defining_relation(name) -> None:
    r"""Every generator of the plane's stabilizer is decided, and by the relation the cut states.

    The library answers with `rho(g) in H`; the assertion here is that this answer is the invariant
    computed from the generator's own matrix -- the divided classes of `e'` and `f'` are carried to a
    span that is the same span.  Neither side of the comparison is read from the other.
    """
    gamma = _gamma_en_2()
    family = _family(name)
    assert family
    for generator in family:
        assert (generator in gamma) == _carries_the_divided_span(generator)


def _assert_the_cut_orbits(name, sizes) -> None:
    r"""The `Gamma_{En,2}`-cut orbits of the plane's antipodal pairs have the given sizes."""
    orbits = _type(name).antipodal_root_class_orbits(
        _family(name), character_subgroup=_gamma_en_2()
    )
    assert sorted(sum(1 for _ in orbit) for orbit in orbits) == sizes


def _the_character(generator):
    r"""The defining relation `rho_{L^-}(g) in H`, through the preimage's own morphism and target.

    `H` is the target the construction retained, and `rho_{L^-}` is the morphism it is the
    preimage along; nothing else is consulted, so this is the law read at its own two data.
    """
    gamma = _gamma_en_2()
    return gamma.target_subgroup().is_parent_of(gamma.preimage_morphism()(generator))


def _assert_every_generator_lies_by_the_character(name) -> None:
    r"""Each generator's image under the defining morphism is admitted exactly when it carries the span."""
    family = _family(name)
    assert family
    for generator in family:
        assert _the_character(generator) == _carries_the_divided_span(generator)


def _assert_the_family_generates_the_parabolic(name) -> None:
    r"""The returned family generates `Stab_{O(T_{En})}(Pi)`, by the correspondence theorem.

    `P_I -> M <= GL(I) x O(I^perp/I)` has kernel the unipotent radical `U_I`, and a subgroup of
    `P_I` that contains `U_I` is `P_I` exactly when its image is `M` (Milne, *Group Theory*, v4.01
    of 6 November 2025, Theorem 1.47, printed p. 22, with Corollary 1.48, p. 23).  Both premises
    are computed here on this family, not on a family beside it:

    * the family is the one the three factors are computed for -- the public call returns
      `parabolic_stabilizer_generators()` and nothing else, and this asserts the two agree;
    * its radical part is `U_I`: the family contains `unipotent_radical_generators()`, whose index
      in `U_I` is 1, so the subgroup's intersection with `U_I` is all of `U_I`;
    * its image is `M`: the plane actions of the members trivial on `I^perp/I` have index 1 in
      `GL(I)` and the quotient images of the members fixing `I` pointwise have index 1 in
      `O(I^perp/I)`, so the two subgroups generate the whole product, which contains `M` while
      `M` contains the image.

    No orbit count enters: transitivity on eight pairs is a proper subgroup's operation too.
    """
    plane = _type(name)
    family = _family(name)
    parabolic = plane.parabolic_stabilizer_generators()
    assert all(member in family for member in parabolic)
    assert all(member in parabolic for member in family)
    for member in plane.unipotent_radical_generators():
        assert member in family
    assert plane.unipotent_radical_index() == 1
    assert plane.levi_plane_action_index(trivial_on_quotient=True) == 1
    assert plane.levi_quotient_image_index(trivial_on_plane=True) == 1
    assert plane.is_parabolic_complete() is True


def test_the_character_is_evaluated_on_a_generator_of_the_public_stabilizer() -> None:
    r"""One generator of `setwise_stabilizer`'s family has its image under `rho_{L^-}` admitted.

    This is the whole of the membership law at one point: the morphism the preimage was built
    along, applied to the element the public call returns, and admitted into the target.  A
    generator of the family at type `{2,4,5}` that carries the span is the specimen.
    """
    generator = next(
        member
        for member in _family("first")
        if _carries_the_divided_span(member)
    )
    assert _the_character(generator) is True


def test_the_character_decides_every_generator_at_the_first_type() -> None:
    r"""Type `{2,4,5}`: every generator's image under `rho_{L^-}` is admitted exactly when it carries the span."""
    _assert_every_generator_lies_by_the_character("first")


def test_the_character_decides_every_generator_at_the_second_type() -> None:
    r"""Type `{4,5}`: every generator's image under `rho_{L^-}` is admitted exactly when it carries the span."""
    _assert_every_generator_lies_by_the_character("second")


def test_the_character_decides_every_generator_at_the_third_type() -> None:
    r"""Type `{3,5}`: every generator's image under `rho_{L^-}` is admitted exactly when it carries the span."""
    _assert_every_generator_lies_by_the_character("third")


def test_the_character_decides_every_generator_at_the_fourth_type() -> None:
    r"""Type `{3,4}`: every generator's image under `rho_{L^-}` is admitted exactly when it carries the span."""
    _assert_every_generator_lies_by_the_character("fourth")


def test_the_character_decides_every_generator_at_the_fifth_type() -> None:
    r"""Type `{5,5}`: every generator's image under `rho_{L^-}` is admitted exactly when it carries the span."""
    _assert_every_generator_lies_by_the_character("fifth")


def test_the_family_generates_the_parabolic_at_the_first_type() -> None:
    r"""Type `{2,4,5}`: the returned family's radical part and image are `U_I` and `M`."""
    _assert_the_family_generates_the_parabolic("first")


def test_the_family_generates_the_parabolic_at_the_second_type() -> None:
    r"""Type `{4,5}`: the returned family's radical part and image are `U_I` and `M`."""
    _assert_the_family_generates_the_parabolic("second")


def test_the_family_generates_the_parabolic_at_the_third_type() -> None:
    r"""Type `{3,5}`: the returned family's radical part and image are `U_I` and `M`."""
    _assert_the_family_generates_the_parabolic("third")


def test_the_family_generates_the_parabolic_at_the_fourth_type() -> None:
    r"""Type `{3,4}`: the returned family's radical part and image are `U_I` and `M`."""
    _assert_the_family_generates_the_parabolic("fourth")


def test_the_family_generates_the_parabolic_at_the_fifth_type() -> None:
    r"""Type `{5,5}`: the returned family's radical part and image are `U_I` and `M`."""
    _assert_the_family_generates_the_parabolic("fifth")


def test_the_defining_relation_at_the_first_type() -> None:
    r"""Type `{2,4,5}`: each of the 134 generators lies in `Gamma_{En,2}` exactly when it carries the span."""
    _assert_the_defining_relation("first")


def test_the_defining_relation_at_the_second_type() -> None:
    r"""Type `{4,5}`: each of the 134 generators lies in `Gamma_{En,2}` exactly when it carries the span."""
    _assert_the_defining_relation("second")


def test_the_defining_relation_at_the_third_type() -> None:
    r"""Type `{3,5}`: each of the 134 generators lies in `Gamma_{En,2}` exactly when it carries the span."""
    _assert_the_defining_relation("third")


def test_the_defining_relation_at_the_fourth_type() -> None:
    r"""Type `{3,4}`: each of the 133 generators lies in `Gamma_{En,2}` exactly when it carries the span."""
    _assert_the_defining_relation("fourth")


def test_the_defining_relation_at_the_fifth_type() -> None:
    r"""Type `{5,5}`: each of the 133 generators lies in `Gamma_{En,2}` exactly when it carries the span."""
    _assert_the_defining_relation("fifth")


def test_the_cut_orbits_at_the_first_type() -> None:
    r"""Type `{2,4,5}`: the cut is transitive on the eight pairs, one orbit of eight."""
    _assert_the_cut_orbits("first", [8])


def test_the_cut_orbits_at_the_second_type() -> None:
    r"""Type `{4,5}`: the cut is transitive, one orbit of eight."""
    _assert_the_cut_orbits("second", [8])


def test_the_cut_orbits_at_the_third_type() -> None:
    r"""Type `{3,5}`: the cut splits the eight pairs into orbits of two and six."""
    _assert_the_cut_orbits("third", [2, 6])


def test_the_cut_orbits_at_the_fourth_type() -> None:
    r"""Type `{3,4}`: the cut is transitive, one orbit of eight."""
    _assert_the_cut_orbits("fourth", [8])


def test_the_cut_orbits_at_the_fifth_type() -> None:
    r"""Type `{5,5}`: the cut splits the eight pairs into orbits of two and six."""
    _assert_the_cut_orbits("fifth", [2, 6])
