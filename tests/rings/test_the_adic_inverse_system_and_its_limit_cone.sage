r"""The adic inverse system of a completion, its limit cone, and the completion at (0).

For a ring $A$ and an ideal $I$, the inverse system $n \mapsto A/I^{n+1}$ carries
the adic transition maps $A/I^m \to A/I^n$ for $m \ge n$, and the cone from the
completion $A^\wedge$ over that system has the canonical projections as its
legs.  At the zero ideal every tier is $A$ itself, so the system is constant,
$A^\wedge = A$, and the completion map is an isomorphism onto it.
"""

from sage_extensions.all import *


def _the_gaussian_rationals_at_the_zero_ideal():
    r"""$QQ(i)$ completed at its zero ideal."""
    field = QuadraticField(-1, "a")
    return field, field.adic_completion(field.ideal(field.zero()))


def _the_rational_line_at_the_origin():
    r"""$QQ[x]$ completed at $(x)$, with its variable."""
    line = QQ["x"]
    x = line.algebra_generator("x")
    return line, x, line.adic_completion(line.ideal(x))


def _the_first_two_tiers(system):
    r"""The objects of the index category at $n = 0$ and $n = 1$, and the arrow between them.

    The index category is $NN^{op}$: the arrow $1 \to 0$ there is the
    inequality $0 \le 1$ of the poset, and it carries the transition
    $A/I^2 \to A/I$.
    """
    index = system.domain()
    poset = index.base_category()
    first = index(poset(NN(0)))
    second = index(poset(NN(1)))
    arrow = index.Mor(second, first)(poset.Mor(poset(NN(0)), poset(NN(1))).unique())
    return first, second, arrow


def test_the_inverse_system_of_a_completion_is_the_family_of_its_truncations() -> None:
    r"""The tiers are $A/I^{n+1}$ and the arrows between them are the adic transitions."""
    field, completion = _the_gaussian_rationals_at_the_zero_ideal()
    system = completion.adic_inverse_system()
    first, second, arrow = _the_first_two_tiers(system)

    assert system(first) is completion.adic_truncation(1)
    assert system(second) is completion.adic_truncation(2)
    transition = system(arrow)
    assert transition.domain() is completion.adic_truncation(2)
    assert transition.codomain() is completion.adic_truncation(1)

    # At the zero ideal $I^n = I = (0)$, so every tier is $A$ and every
    # transition is the identity of that one ring.
    assert completion.adic_truncation(1) is completion.adic_truncation(2)
    assert transition(completion.adic_truncation(2).one()) == completion.adic_truncation(1).one()


def test_the_limit_cone_of_the_completion_projects_onto_every_tier() -> None:
    r"""The cone has apex $A^\wedge$ and its leg at $n$ is the projection $A^\wedge \to A/I^{n+1}$."""
    field, completion = _the_gaussian_rationals_at_the_zero_ideal()
    system = completion.adic_inverse_system()
    cone = completion.adic_limit_cone()
    first, second, _ = _the_first_two_tiers(system)
    element = completion.completion_map()(field.algebra_generator("a"))

    assert cone.apex() is completion
    assert cone.diagram() is system
    assert cone.structure_morphism(first)(element) == completion.adic_projection(1)(element)
    assert cone.structure_morphism(second)(element) == completion.adic_projection(2)(element)


def test_the_completion_map_at_the_zero_ideal_is_an_isomorphism_onto_the_ring() -> None:
    r"""$A \to A^\wedge$ is an arrow of the core: $A^\wedge = A$ at $I = (0)$.

    Every power of the zero ideal is the zero ideal, so every tier is $A$ and
    the completion is $A$ itself presented as complete.  The map is therefore
    an isomorphism between the two presentations, and the construction builds
    it as one: it lies in the core, its inverse is an arrow back, and the two
    inverse equations hold.  Injectivity and surjectivity are answered by that
    placement, not by a claim the map carries.
    """
    field, completion = _the_gaussian_rationals_at_the_zero_ideal()
    completion_map = completion.completion_map()
    a = field.algebra_generator("a")

    assert completion_map.domain() is field
    assert completion_map.codomain() is completion
    assert completion_map in Rings().Core().Mor(field, completion)
    assert completion_map.is_injective() is True
    assert completion_map.is_surjective() is True
    assert completion_map(field.one()) == completion.one()
    assert completion_map.inverse()(completion_map(a)) == a
    assert completion_map(completion_map.inverse()(completion(a))) == completion(a)
    assert completion_map.inverse().inverse() == completion_map


def test_the_inverse_system_at_a_principal_ideal_is_not_constant() -> None:
    r"""At $I = (x)$ the tiers differ, and the transition $A/I^2 \to A/I$ is not the identity.

    $x$ is already zero in $QQ[x]/(x)$, while it is not zero in $QQ[x]/(x^2)$:
    a transition map that dropped the quotient would pass on the zero ideal,
    where every tier is the ring and every transition is its identity.
    """
    _, x, completion = _the_rational_line_at_the_origin()
    system = completion.adic_inverse_system()
    first, second, arrow = _the_first_two_tiers(system)
    first_tier = system(first)
    second_tier = system(second)
    transition = system(arrow)

    assert first_tier is completion.adic_truncation(1)
    assert second_tier is completion.adic_truncation(2)
    assert first_tier is not second_tier
    assert transition.domain() is second_tier
    assert transition.codomain() is first_tier
    assert transition(second_tier.quotient_map()(x)).is_zero()
    assert transition(second_tier.quotient_map()(x**2)).is_zero()
    assert not second_tier.quotient_map()(x).is_zero()


def test_the_limit_cone_at_a_principal_ideal_commutes_with_the_transitions() -> None:
    r"""The leg at $n+1$ followed by the transition is the leg at $n$, at $I = (x)$.

    The cone's legs are the canonical projections, so they carry $x$ to $x$ at
    the second tier and to zero at the first, and $\hat x^2 \ne 0$ in
    $QQ[[x]]$ while its image in $QQ[x]/(x^2)$ is zero.
    """
    _, x, completion = _the_rational_line_at_the_origin()
    system = completion.adic_inverse_system()
    cone = completion.adic_limit_cone()
    first, second, arrow = _the_first_two_tiers(system)
    image = completion.completion_map()(x)
    projected_second = cone.structure_morphism(second)(image)
    projected_first = cone.structure_morphism(first)(image)

    assert cone.apex() is completion
    assert cone.diagram() is system
    assert projected_first.is_zero()
    assert not projected_second.is_zero()
    assert (projected_second**2).is_zero()
    assert not (image**2).is_zero()
    assert system(arrow)(projected_second) == projected_first
    assert projected_second == completion.adic_projection(2)(image)
    assert projected_first == completion.adic_projection(1)(image)



def test_the_completion_at_the_zero_ideal_is_free_of_rank_one_over_the_ring() -> None:
    r"""$A^\wedge = A$ is free of rank one over $A$, framed on the unit.

    The completion of a field at its zero ideal is the field again, so read as
    an algebra over its source it is the free module on one generator, and its
    frame is $A^1 \to A^\wedge$ carrying the generator to $1$.  The defining
    polynomial's power basis is a basis over the coefficient field and over no
    other base, and it is not this rank.
    """
    field, completion = _the_gaussian_rationals_at_the_zero_ideal()
    frame = completion.framing_morphism()
    labels = frame.domain().module_generating_set()

    assert completion.base_ring() is field
    assert frame.domain() is field.free_module(1)
    assert labels.cardinality() == 1
    assert frame(frame.domain().module_generator(NN(0))) == completion.one()
    assert completion.module_generating_set().cardinality() == 1


def test_a_completion_states_whether_a_power_of_its_ideal_is_zero() -> None:
    r"""The completion is the ring exactly when a power of its ideal is zero.

    $I^n = (0)$ makes the $I$-adic topology discrete: $A$ is already complete
    and separated for it, so $A^\wedge = A$ and the completion map is an
    isomorphism, which the construction places in the core.  At $I = (x)$ no
    power of the ideal is zero -- $x^k \ne 0$ in $QQ[[x]]$ -- and the map is a
    ring homomorphism that is not an isomorphism.  The decision is the
    retained ideal's and its precision's, and it is what the placement
    follows.
    """
    field, completion = _the_gaussian_rationals_at_the_zero_ideal()
    line, _, line_completion = _the_rational_line_at_the_origin()

    assert completion.completion_defining_power_vanishes() is True
    assert line_completion.completion_defining_power_vanishes() is False
    assert completion.completion_map() in Rings().Core().Mor(field, completion)
    assert line_completion.completion_map() not in Rings().Core().Mor(line, line_completion)


def test_the_rank_one_basis_at_a_vanishing_power_is_not_read_off_an_engine() -> None:
    r"""Every completion at a vanishing power is free of rank one on its source.

    ``QQ``, ``QQ(i)`` and ``GF(5)`` completed at their zero ideals are one
    mathematical situation: the completion is the ring, so read over its
    source it is free on the unit and its frame is $R^1 \to A^\wedge$,
    $e_0 \mapsto 1$.  A decision made from the engine the two presentations
    share gives that basis to the number field and to neither the rationals
    nor the finite field; a decision made from the ideal's vanishing power
    gives it to all three.
    """
    for ring in (QQ, QuadraticField(-1, "a"), GF(5)):
        completion = ring.adic_completion(ring.ideal(ring.zero()))
        frame = completion.framing_morphism()

        assert completion.base_ring() is ring
        assert frame.domain() is ring.free_module(1)
        assert frame(frame.domain().module_generator(NN(0))) == completion.one()
        assert completion.module_generating_set().cardinality() == 1
