r"""The discriminant action of a lattice reflection, and what asking it costs.

``discriminant_representation`` takes an isometry of ``L`` to its action on the
discriminant form ``A_L = L^#/L``.  For the reflection in a root ``r`` that
action is a function of the reflection's own matrix: a class ``x`` of ``A_L``
moves to ``x A^{-1}``, where ``A`` is the matrix of ``s_r`` in the lattice's
framing, and the reflection is a function of the line of ``r``, so nothing about
the form's presentation has to be derived again to write the action down.

The specimen is the one #522 is about: Sterk's twelve reflections at the first
Enriques cusp, on the reduction ``U(2) + E8(-2)`` of ``T_En``
(H. Sterk, *Compactifications of the period space of Enriques surfaces, Part I*,
Math. Z. 207 (1991), §4.3.5, p. 19), whose discriminant form is elementary
two-primary of rank ten.

A cost contract is stated by the suite's per-test call ceiling (20 s,
``src/sage_extensions/testing/suite_budget.py``), not by a stopwatch in an
assertion.  What these tests assert is that the action *is* the action — the
identity takes the identity, a product of reflections takes the product of the
actions, a reflection takes an involution — at a specimen whose size makes the
per-question presentation of the form's module maps the thing the ceiling
refuses.  The actions of a hundred and fifty-six reflections, on this specimen,
are what one walk over Sterk's cusp asks.
"""

from sage_extensions.all import *


def _first_cusp():
    r"""Return ``U(2) + E8(-2)`` as a hyperbolic lattice with Sterk's twelve roots.

    The twelve are read in ``T_En`` and dropped onto the reduction at ``e``: the
    ``U(2) + E8(-2)`` part orthogonal to the unimodular plane's generator, by
    keeping the coordinates of Sterk's own labels.
    """
    lattice = NamedLattices.SEn
    roots = tuple(Sterk.sterks_in_TEn()["Sterk_1"])
    labels = ("ep", "fp") + tuple(f"a{index}" for index in range(1, 9))
    transported = tuple(
        lattice([int(root.to_vector()(label)) for label in labels]) for root in roots
    )
    return lattice, transported


def test_the_discriminant_action_of_the_identity_and_of_a_reflection() -> None:
    r"""The identity acts as the identity, and a reflection as an involution.

    Every one of Sterk's twelve roots is a root of the cusp lattice, so each of
    the twelve reflections is an isometry of it and each action is an involution
    of the discriminant form.  The identity isometry's action is the group's
    identity, which is the statement that ``rho`` has the whole of ``O(L)`` as
    its domain and not only the reflections.
    """
    lattice, transported = _first_cusp()
    K = HyperbolicLattices(ZZ)(lattice)
    rho = K.discriminant_representation()
    form_group = rho.codomain()
    one = form_group.one()

    assert rho(K.Aut().one()) == one
    for root in transported:
        image = rho(K.reflection(root))
        assert image * image == one
        assert image != one


def test_the_discriminant_action_is_a_homomorphism_on_the_twelve_reflections() -> None:
    r"""The action of a composite is the composite of the actions.

    This is the statement ``rho`` is a group homomorphism, asked of products
    whose factors are reflections the walk itself uses: a route that wrote the
    action out of the isometry's matrix would be wrong at one of these products
    if the dual action were taken in the wrong frame or without the inverse.
    """
    lattice, transported = _first_cusp()
    K = HyperbolicLattices(ZZ)(lattice)
    rho = K.discriminant_representation()
    reflections = tuple(K.reflection(root) for root in transported)

    products = tuple(
        (left, right)
        for left in reflections[:3]
        for right in reflections[3:6]
    )
    assert all(rho(left * right) == rho(left) * rho(right) for left, right in products)


def test_the_discriminant_actions_of_the_roots_the_walk_asks_about() -> None:
    r"""A hundred and fifty-six reflections' actions, and each one an involution.

    The twelve roots and the hundred and forty-four images of the twelve under
    the twelve reflections are what the walk at this cusp sifts: every root it
    reaches is such an image, since the reflections act on the roots.  Asking
    for their actions is the walk's own question budget, so the ceiling the
    suite enforces is the contract this test states.
    """
    lattice, transported = _first_cusp()
    K = HyperbolicLattices(ZZ)(lattice)
    rho = K.discriminant_representation()
    form_group = rho.codomain()
    one = form_group.one()
    reflections = tuple(K.reflection(root) for root in transported)
    moved = tuple(
        reflection(root) for reflection in reflections for root in transported
    )

    actions = tuple(rho(reflection) for reflection in reflections) + tuple(
        rho(K.reflection(root)) for root in moved
    )
    assert cardinal(sum(1 for _ in actions)) == cardinal(156)
    assert all(action * action == one for action in actions)
