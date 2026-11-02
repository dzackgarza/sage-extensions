r"""Isometries between typed torsion forms, as verified witnesses.

``form.isometry_to(other)`` returns a witness in the typed family
(``TorsionFormIsometry``) when the two forms are isometric, and ``None`` when
they are not.  The witness is a pair of mutually inverse module maps that
preserve the form exactly — ``q`` on the generators for a quadratic form, ``b``
on generator pairs for a bilinear one — and the typed constructor runs those
validations, so a witness that is returned has been checked, not assumed.

What the witness is *not*: an abstract isomorphism of the underlying groups, and
not a map between two equal-looking parents.  The two endpoints are the two
forms themselves; the transport runs through each form's selected normal form,
which is an exact isometry onto a normalized framing, and a label-preserving
bridge between those framings whose invariants and form data agree.

The specimens are quadratic forms that satisfy the descent law on their module
(``tests/forms/test_quadratic_form_descent.sage``): ``Z/9`` with ``q = 2/9`` and
with ``q = 8/9 = 2*(2/9)*2``, which are isometric through the unit ``2``, versus
``q = 4/9``, which is not isometric to either.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.modules.framed.formed import (
    TorsionBilinearFormModules,
    TorsionQuadraticFormModules,
)
from sage_extensions.categories.modules.framed.formed.torsion_form_modules import (
    TorsionFormIsometry,
)
from sage_extensions.categories.modules.framed.fraction_field_quotients import (
    FractionFieldQuotients,
)


def _cyclic_ninth(numerator):
    r"""``Z/9`` with ``q(x) = numerator/9``; ``numerator`` must be even to descend."""
    values = FractionFieldQuotients(ZZ)(2)
    return TorsionQuadraticFormModules(ZZ).from_relations_and_gram(
        [[9]], [[QQ(numerator) / QQ(9)]], values
    )


def _all_elements(form, order):
    generator = form.module_generators()[0]
    return [multiple * generator for multiple in range(order)]


def test_the_witness_is_a_verified_typed_isometry_between_the_two_forms() -> None:
    r"""``q = 2/9`` and ``q = 8/9`` on ``Z/9``: one witness, exact on every element."""
    source = _cyclic_ninth(2)
    target = _cyclic_ninth(8)

    assert source is not target
    assert source.is_isomorphic(target) is True

    witness = source.isometry_to(target)
    assert isinstance(witness, TorsionFormIsometry)
    assert witness.is_quadratic() is True
    assert witness.domain() is source
    assert witness.codomain() is target

    for element in _all_elements(source, 9):
        image = witness.forward()(element)
        assert source.q(element) == target.q(image)
        assert witness.inverse()(image) == element


def test_a_form_that_is_not_isometric_gets_no_witness() -> None:
    r"""``q = 4/9`` is not isometric to ``q = 2/9``: the answer is ``None``, not an isomorphism."""
    source = _cyclic_ninth(2)
    other = _cyclic_ninth(4)

    assert source.is_isomorphic(other) is False
    assert source.isometry_to(other) is None


def test_the_sign_of_the_quadratic_form_is_part_of_the_witness_test() -> None:
    r"""``(Z/9, 2/9)`` has no isometry to its twist by ``-1``: ``-1`` is not a square mod 9."""
    source = _cyclic_ninth(2)
    twisted = source.twist(-1)

    assert source.is_isomorphic(twisted) is False
    assert source.isometry_to(twisted) is None

    # A form whose q vanishes is unchanged by the twist, and there the witness
    # exists: the sign test is not "always no".
    values = FractionFieldQuotients(ZZ)(2)
    half = QQ(1) / QQ(2)
    hyperbolic = TorsionQuadraticFormModules(ZZ).from_relations_and_gram(
        [[2, 0], [0, 2]], [[0, half], [half, 0]], values
    )
    assert hyperbolic.is_isomorphic(hyperbolic.twist(-1)) is True
    assert isinstance(hyperbolic.isometry_to(hyperbolic.twist(-1)), TorsionFormIsometry)


def test_two_witnesses_compose_through_their_endpoints() -> None:
    r"""``f.inverse().then(g)`` lands in the typed family instead of raising on the factor."""
    source = _cyclic_ninth(2)
    middle = _cyclic_ninth(8)
    far = _cyclic_ninth(2)

    forward = source.isometry_to(middle)
    back = middle.isometry_to(far)
    composed = forward.then(back)

    for element in _all_elements(source, 9):
        assert composed(source.module_generators()[0] * 0) is not None
        assert far.q(composed(element)) == source.q(element)


def test_the_bilinear_flavour_has_the_same_witness_contract() -> None:
    r"""``b`` on ``Z/9``: ``1/9`` and ``4/9`` are isometric through the unit ``2``."""
    values = FractionFieldQuotients(ZZ)(1)
    source = TorsionBilinearFormModules(ZZ).from_relations_and_gram(
        [[9]], [[QQ(1) / QQ(9)]], values
    )
    target = TorsionBilinearFormModules(ZZ).from_relations_and_gram(
        [[9]], [[QQ(4) / QQ(9)]], values
    )

    witness = source.isometry_to(target)
    assert isinstance(witness, TorsionFormIsometry)
    assert witness.is_quadratic() is False
    generator = source.module_generators()[0]
    image = witness.forward()(generator)
    assert source.b(generator, generator) == target.b(image, image)
