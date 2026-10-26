r"""The finite power-set functor on $\mathbf{Set}$, its composites, and the singleton transformation.

$P(X)$ is the set of finite subsets of $X$, so $|P(\{0, 1\})| = 4$ and
$|P(P(\{0, 1\}))| = 2^4 = 16$.  The singleton maps $\eta_X : X \to P(X)$,
$x \mapsto \{x\}$, form a natural transformation
$\mathrm{Id} \Rightarrow P$: for $f : X \to Y$,
$P(f)(\{x\}) = \{f(x)\}$.  A functor induces maps on each Mor set,
$\mathrm{Mor}(X, Y) \to \mathrm{Mor}(P X, P Y)$, $f \mapsto P(f)$, and on
each endomorphism monoid.  These are the definitions.
"""

from sage_extensions.all import *  # noqa: F401,F403


def _singletons():
    power = Sets().power_set_functor()
    transformations = IdentityFunctor(Sets()).natural_transformations_to(power)
    return transformations(lambda points: Sets().Mor(points, power(points))(lambda x: power(points)({x})))


def test_the_power_set_of_the_power_set_of_two_points_has_sixteen_elements() -> None:
    power = Sets().power_set_functor()
    two = Sets.Δ[1]

    assert power(two).cardinality() == cardinal(4)
    assert power(power(two)).cardinality() == cardinal(16)
    assert power.then(power)(two).cardinality() == cardinal(16)
    assert two.finite_subsets().finite_subsets().cardinality() == cardinal(16)


def test_the_singleton_maps_are_a_natural_transformation_into_the_power_set() -> None:
    power = Sets().power_set_functor()
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    doubling = Sets().Mor(two, three)(lambda x: three(2 * x))
    singletons = _singletons().transformation()

    assert singletons.component(two)(two(1)) == power(two)({two(1)})
    assert all(
        power(doubling)(singletons.component(two)(x)) == singletons.component(three)(doubling(x))
        for x in two
    )


def test_the_naturality_square_of_the_singleton_transformation_commutes() -> None:
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    doubling = Sets().Mor(two, three)(lambda x: three(2 * x))
    square = _singletons().transformation().naturality_square(doubling)

    assert square.left() == doubling


def test_the_power_set_functor_acts_on_a_mor_set() -> None:
    power = Sets().power_set_functor()
    two = Sets.Δ[1]
    three = Sets.Δ[2]
    doubling = Sets().Mor(two, three)(lambda x: three(2 * x))

    assert power.induced_mor_functor(two, three)(doubling) == power(doubling)


def test_the_power_set_functor_acts_on_an_endomorphism_monoid() -> None:
    power = Sets().power_set_functor()
    two = Sets.Δ[1]
    transposition = Sets().Mor(two, two)(lambda x: two(1) if x == 0 else two(0))

    assert power.induced_end_functor(two)(transposition) == power(transposition)


def test_the_identity_is_a_natural_isomorphism_of_the_power_set_functor() -> None:
    power = Sets().power_set_functor()
    two = Sets.Δ[1]
    identity = power.natural_isomorphism_to(
        power,
        lambda points: Sets().Mor(power(points), power(points)).identity(),
        lambda points: Sets().Mor(power(points), power(points)).identity(),
    )

    assert identity.forward().transformation().component(two)(power(two)({two(0)})) == power(two)({two(0)})


def test_the_power_set_functor_is_faithful() -> None:
    r"""$P(f)(\{x\}) = \{f(x)\}$, so $P(f)$ determines $f$."""
    assert Sets().power_set_functor().is_faithful()
