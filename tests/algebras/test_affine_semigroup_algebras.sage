r"""The semigroup algebra of an affine monoid.

Every test takes its names from the session: the suite's lint (TL01) admits no
module import beside it, so the algebra categories are the session's
``AffineSemigroupAlgebras``, ``FreeAlgebras`` and ``SymmetricAlgebras`` and the
coefficient ring is the session's ``ZZ``.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_linearly_independent_semigroup_generators_give_the_polynomial_algebra() -> None:
    r"""An injective degree map N^2 -> Z^2 has zero toric ideal."""
    algebra = AffineSemigroupAlgebras(ZZ)(((1, 0), (0, 1)), names=("x", "y"))

    assert algebra in AffineSemigroupAlgebras(ZZ)
    assert algebra in FreeAlgebras(ZZ)
    assert algebra in SymmetricAlgebras(ZZ)
    assert algebra.algebra_generating_set().cardinality() == 2
    coordinates = algebra.affine_semigroup_generator_coordinates()
    assert tuple(
        tuple(int(value) for value in coordinates[label])
        for label in coordinates.index_set()
    ) == ((1, 0), (0, 1))
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    assert x * y == y * x
    assert x != y


def test_semigroup_algebra_of_the_monoid_generated_by_e1_e2_and_their_sum_satisfies_z_equals_xy() -> None:
    r"""In ``ZZ[S]`` for ``S = <(1,0), (0,1), (1,1)>`` the monomials multiply by adding exponents.

    Since ``(1,1) = (1,0) + (0,1)`` in ``S``, the generator ``z = t^(1,1)`` equals
    ``xy``; since ``S = NN^2`` the algebra is the polynomial ring in ``x, y``.
    Derivation: ``t^a t^b = t^(a+b)`` in a semigroup algebra.
    """
    algebra = AffineSemigroupAlgebras(ZZ)(((1, 0), (0, 1), (1, 1)), names=("x", "y", "z"))
    x = algebra.algebra_generator("x")
    y = algebra.algebra_generator("y")
    z = algebra.algebra_generator("z")

    assert z == x * y
    assert z * z == x**2 * y**2
    assert z != x
    assert x != y
    assert x * y == y * x
    assert x + y != z


def test_a_semigroup_algebra_keeps_its_identity_after_a_polynomial_ring_is_built() -> None:
    r"""``QQ[S]``'s identity and augmentation are arrows of its own ``Mor``.

    ``QQ[S]`` for ``S = <(1,0), (0,1)>`` is a free algebra and a finitely
    presented algebra at once, and the pair has two Mor families:
    ``QQ[S].Mor(QQ[S])`` is the graded-algebra Mor of the join category, while
    the selected resolution keeps its degree-zero arrow in the unital-algebra
    Mor of the pair.  That arrow belongs to the resolution's owner: the
    resolution is keyed by ``algebra_framing_owner()``, a category, and
    ``UnitalAlgebraMorCategoryConstruction.fixed_category_class_for`` reads the
    domain's own arrow class for it.

    The augmentation of the algebra belongs to the algebra, and the library
    answers it in the algebra's own Mor: ``algebra_framing_morphism`` returns
    ``self.Mor(self).identity()`` when the framing source is the algebra itself,
    which is what a free algebra is.  So that arrow is the identity of
    ``QQ[S].Mor(QQ[S])`` and is drawn from it.
    """
    QQ.polynomial_ring("y")
    algebra = AffineSemigroupAlgebras(QQ)(((1, 0), (0, 1)),)
    generator = algebra.algebra_generator(next(iter(algebra.algebra_generating_set())))

    identity = algebra.Mor(algebra).identity()
    assert identity(generator) == generator
    augmentation = algebra.algebra_framing_morphism()
    assert augmentation.parent() is algebra.Mor(algebra)
    assert augmentation in algebra.Mor(algebra)
    assert augmentation == identity
    assert augmentation(generator) == generator
    assert augmentation(generator * generator) == generator * generator


def test_the_generating_module_of_a_semigroup_algebra_is_the_module_it_was_built_on() -> None:
    r"""The module answers on the free side whichever construction came first.

    ``generating_module`` is declared twice for ``QQ[S]``: by
    ``SymmetricAlgebras.ParentMethods``, which returns the module the algebra
    was built on, and by
    ``AlgebrasWithChosenFinitePresentation.ParentMethods``, which reads
    ``presentation_ring()``.  ``QQ[S]`` reached as the free algebra on its
    generators keeps its resolution truncated in degree zero, so the presented
    declaration has no presentation to read; the two declarations do not agree
    and the free one is the answer.  Building ``QQ[y]`` first is the history
    that used to put the presented declaration ahead of it.
    """
    QQ.polynomial_ring("y")
    algebra = AffineSemigroupAlgebras(QQ)(((1, 0), (0, 1)),)

    assert (
        algebra.generating_module().module_generating_set()
        is algebra.algebra_generating_set()
    )
    assert algebra.generating_module() is algebra.generating_module()
