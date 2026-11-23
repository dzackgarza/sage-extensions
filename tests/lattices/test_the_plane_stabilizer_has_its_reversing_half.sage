r"""The public plane stabilizer of `T_{\mathrm{En}}`, its determinant-`-1` half, and Sterk's counts.

At a primitive isotropic plane `\Pi` of `T_{\mathrm{En}}` the setwise stabilizer
`N_{O(T_{\mathrm{En}})}(\Pi)` acts on `\Pi` by `GL_2(\ZZ)`, and the family
`setwise_stabilizer(\Pi).group_generators()` is asserted here to contain the
determinant-`-1` part of that action whenever the plane has one -- the half
sage-extensions#623 reports can go missing.  Two levels are read, and neither is a
finite image:

* the lattice level, `g.determinant()` for `g` in the returned family, an integral
  isometry of the rank `12` lattice `T_{\mathrm{En}}`;
* the plane level, the matrices by which those isometries act on `\Pi`, read
  geometrically by `levi_plane_action_generators` -- the images `g(p_j)` of a basis
  `(p_1, p_2)` of `\Pi` in that basis, which the method asserts integral.

**Why the half can go missing.**  The family is enumerated one determinant half at a
time (`_levi_plane_action_presentation`): the special-linear half is a right-coset
walk in `SL_2(\ZZ)`, the reversing half the same walk started at `\mathrm{diag}(-1,1)`.
A right coset is `Hx`, so two names agree exactly when `x y^{-1} \in H`; the
comparison that decides the reversing half must not be the left-coset one, and at a
reversing element `y^{-1} = -\operatorname{adj}(y)`, so an adjugate written for the
inverse changes the partition as well (`tests/lattices/test_the_plane_projection_walks_its_right_cosets.sage`
separates the two spellings on a finite specimen).  What is asserted here is the
outcome at the planes that matter, on the integral families themselves.

**The five planes.**  Sterk's one-cusp types, H. Sterk, *Compactifications of the
period space of Enriques surfaces, Part I*, Math. Z. 207 (1991), (4.2.3) with the
stabilizer statement (4.3.16)-(4.3.17), in the basis
`(e, f, e', f', \alpha_1, \ldots, \alpha_8)` of Alexeev--Engel--Garza--Schaffler,
*Compact moduli of Enriques surfaces of degree 2*, Nagoya Math. J. 259 (2025),
Definition 2.3.  The orbits of `Stab_{\Gamma_{\mathrm{En},2}}(\Pi)` on the eight
antipodal pairs of `(-2)`-classes of `\Pi^\perp/\Pi` are asserted to have sizes
`[8], [8], [2, 6], [8], [2, 6]` -- one, one, two, one, two orbits -- the counts of
sage-extensions#616.

**What this row is not.**  At these five planes the determinant-`-1` half is present
before and after the #623 repair: the same families, the same determinants and the
same counts are returned at `19903dc` and at `1b20f71`, so these rows do not
separate the two coset comparisons and this file is not the repair's red test.  It
is the acceptance row the repair must leave standing, and the measurement -- at
both levels and on every plane -- that the earlier rows did not make.
"""

from sage_extensions.all import *  # noqa: F401,F403

_GROUPS = {}
_PLANES = {}
_FAMILIES = {}
_ACTIONS = {}


def _gamma_en_2():
    r"""`\Gamma_{\mathrm{En},2}` on `T_{\mathrm{En}}`, built once per session."""
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
    r"""The family `setwise_stabilizer` returns at that type, read once per session."""
    if name not in _FAMILIES:
        _FAMILIES[name] = tuple(
            NamedLattices.TEn.Aut()
            .stabilizer(_type(name), action="setwise")
            .group_generators()
        )
    return _FAMILIES[name]


def _actions(name):
    r"""The matrices by which that family acts on the plane, read once per session."""
    if name not in _ACTIONS:
        _ACTIONS[name] = tuple(_type(name).levi_plane_action_generators())
    return _ACTIONS[name]


def _lattice_determinants(name):
    r"""The determinants on `T_{\mathrm{En}}` realized by the returned family."""
    return {int(generator.determinant()) for generator in _family(name)}


def _plane_action_determinants(name):
    r"""The determinants of the plane actions the returned family realizes."""
    return {int(action.determinant()) for action in _actions(name)}


def _assert_the_reversing_half_is_present(name) -> None:
    r"""Both determinant signs are realized, on the lattice and on the plane.

    The family is a generating set of `N_{O(T_{\mathrm{En}})}(\Pi)`, so its
    determinants are those of the stabilizer's own elements; the plane actions are
    read from a basis of the plane, so their determinants are those of the image in
    `GL_2(\ZZ)`.  A stabilizer that omits its reversing half fails one or both.
    """
    lattice_determinants = _lattice_determinants(name)
    assert lattice_determinants == {1, -1}
    action_determinants = _plane_action_determinants(name)
    assert action_determinants == {1, -1}


def _assert_the_reversing_action_is_unimodular_and_integral(name) -> None:
    r"""Every plane action is an integral unimodular matrix, and one of them reverses.

    `levi_plane_action_generators` writes the images of the plane's basis in that
    basis and asserts the coordinates integral; the assertion here is that the
    determinants of those matrices are `1` and `-1` and nothing else, so that the
    reversing class is a genuine element of `GL_2(\ZZ)` and not a rational lift.
    """
    for action in _actions(name):
        entries = [entry for entry in action.list()]
        assert all(entry == int(entry) for entry in entries)
        assert abs(int(action.determinant())) == 1
    assert -1 in _plane_action_determinants(name)


def _assert_the_cut_orbits(name, sizes) -> None:
    r"""The `\Gamma_{\mathrm{En},2}`-cut orbits of the eight antipodal pairs have the given sizes."""
    orbits = _type(name).antipodal_root_class_orbits(
        _family(name), character_subgroup=_gamma_en_2()
    )
    assert sorted(sum(1 for _ in orbit) for orbit in orbits) == sizes


def test_the_stabilizer_has_its_reversing_half_at_the_first_type() -> None:
    r"""Type `{2,4,5}`: both levels realize determinant `-1`, with integral actions and one orbit of eight."""
    _assert_the_reversing_half_is_present("first")
    _assert_the_reversing_action_is_unimodular_and_integral("first")
    _assert_the_cut_orbits("first", [8])


def test_the_stabilizer_has_its_reversing_half_at_the_second_type() -> None:
    r"""Type `{4,5}`: both levels realize determinant `-1`, with integral actions and one orbit of eight."""
    _assert_the_reversing_half_is_present("second")
    _assert_the_reversing_action_is_unimodular_and_integral("second")
    _assert_the_cut_orbits("second", [8])


def test_the_stabilizer_has_its_reversing_half_at_the_third_type() -> None:
    r"""Type `{3,5}`: both levels realize determinant `-1`, with integral actions and orbits of two and six."""
    _assert_the_reversing_half_is_present("third")
    _assert_the_reversing_action_is_unimodular_and_integral("third")
    _assert_the_cut_orbits("third", [2, 6])


def test_the_stabilizer_has_its_reversing_half_at_the_fourth_type() -> None:
    r"""Type `{3,4}`: both levels realize determinant `-1`, with integral actions and one orbit of eight."""
    _assert_the_reversing_half_is_present("fourth")
    _assert_the_reversing_action_is_unimodular_and_integral("fourth")
    _assert_the_cut_orbits("fourth", [8])


def test_the_stabilizer_has_its_reversing_half_at_the_fifth_type() -> None:
    r"""Type `{5,5}`: both levels realize determinant `-1`, with integral actions and orbits of two and six."""
    _assert_the_reversing_half_is_present("fifth")
    _assert_the_reversing_action_is_unimodular_and_integral("fifth")
    _assert_the_cut_orbits("fifth", [2, 6])
