r"""The stabilizer of a Coble discriminant class, generated without enumerating the group.

``A = A_{T_Co}`` is the discriminant quadratic form of ``B.twist(2)`` with
``B = <1> + U + E8(-1)``: 2048 classes over ``Z/2``, whose ``q = 1`` fibre has
496 elements.  The point ``c`` below is a class of that fibre, ``[½ h̃_Co]`` in
the Coble marking.

The stabilizer of ``c`` in ``O(A, q)`` has order ``|O(A,q)| / |O(A,q).c|``, and
``stabilizer_generators`` produces it by Schreier's lemma over the orbit: with
one transversal word per orbit point, the generators ``t_y s t_{ys}^-1`` generate
the point stabilizer, and nothing enumerates the 46 998 591 897 600 elements of
the parent.  Two certificates are asserted here, both readable from the result:

* every returned generator fixes ``c`` and preserves ``q`` (checked by the
  form-preservation validator);
* the subgroup they generate has exactly the orbit-stabilizer order
  ``|O(A,q)| / |O(A,q).c|``.

The order certificate is the substantive one: equal order does not identify the
subgroup, so the *point* certificate is asserted separately on every generator
rather than inferred from the order.
"""

from sage_extensions.all import *  # noqa: F401,F403

_BASE = Lattices(ZZ)([[1]]) + Lattices(ZZ)("U") + Lattices(ZZ)("E8").twist(-1)
_FORM = _BASE.twist(2).discriminant_quadratic_form()
_GROUP = _FORM.orthogonal_group()
_VALUE_ONE = _FORM.value_module()(1)
_POINT = next(
    element
    for element in _FORM.elements()
    if _FORM.q(element) == _VALUE_ONE
)


def test_the_coble_class_has_the_recorded_orbit_and_stabilizer_order() -> None:
    r"""``|O(A,q)| = 46 998 591 897 600``, ``|O(A,q).c| = 496``, stabilizer ``94 755 225 600``."""
    assert int(_FORM.cardinality()) == 2048
    assert _FORM.q(_POINT) == _VALUE_ONE
    assert _GROUP.orbit_cardinality(_POINT) == 496
    assert int(_GROUP.order()) == 46998591897600
    assert int(_GROUP.order()) // _GROUP.orbit_cardinality(_POINT) == 94755225600


def test_stabilizer_generators_fix_the_point_and_generate_the_stabilizer() -> None:
    r"""Both certificates, on the generators the operation returns."""
    stabilizing = _GROUP.stabilizer_generators(_POINT)

    for generator in stabilizing:
        assert generator(_POINT) == _POINT
        assert generator.validate_form_preservation(check=True) is None
    # the family is a proper subset of the parent: no generator set of the whole
    # group fixes a point that the group moves
    assert _GROUP.subgroup_on(stabilizing).cardinality() == (
        _GROUP.order() // _GROUP.orbit_cardinality(_POINT)
    )
    assert _GROUP.subgroup_on(stabilizing).cardinality() != _GROUP.order()
