r"""A functor composes with the next one when it lands in that one's domain refinement.

The de Rham functor takes values in *supercommutative alternating* differential
graded algebras, and the graded cohomology functor is defined on differential
graded algebras.  Landing in a subcategory is landing in the category, so ``H^*
o DR`` is a functor between the outer categories.  What is still refused is a
genuine mismatch: values in a category that is not contained in the next
functor's domain, such as the same construction over another base ring.
"""

from sage_extensions.all import *  # noqa: F401,F403
from sage_extensions.categories.abstract_categories.cat import Cat
from sage_extensions.categories.algebras.algebras import Algebras
from sage_extensions.categories.algebras.differential_graded_algebras import (
    DifferentialGradedAlgebras,
)

import pytest


def test_the_de_rham_functor_composes_with_cohomology_through_its_refinement() -> None:
    r"""``DR`` lands in a subcategory of the cohomology functor's domain."""
    de_rham = Algebras(QQ).Associative().Unital().Commutative().de_rham()
    cohomology = DifferentialGradedAlgebras(QQ).cohomology_algebra()

    # Not equal: the de Rham functor states the stronger codomain, and that
    # refinement is contained in the category the cohomology functor starts at.
    assert de_rham.codomain() is not cohomology.domain()
    assert de_rham.codomain().is_subcategory(cohomology.domain())

    composite = Cat().compose(cohomology, de_rham)
    assert composite.domain() is de_rham.domain()
    assert composite.codomain() is cohomology.codomain()

    # The refinement is inhabited by the de Rham functor's own values: a
    # polynomial algebra is an object of its domain, and its de Rham algebra is
    # an object of the refined codomain that the cohomology functor reads.
    polynomial = QQ["x,y"]
    assert polynomial in de_rham.domain()
    assert de_rham(polynomial) in de_rham.codomain()


def test_a_codomain_that_is_not_contained_in_the_domain_is_still_refused() -> None:
    r"""``H^*`` over ``ZZ`` cannot follow a de Rham functor that lands over ``QQ``."""
    de_rham_over_qq = Algebras(QQ).Associative().Unital().Commutative().de_rham()
    cohomology_over_zz = DifferentialGradedAlgebras(ZZ).cohomology_algebra()

    assert not de_rham_over_qq.codomain().is_subcategory(
        cohomology_over_zz.domain()
    )
    with pytest.raises(ValueError):
        Cat().compose(cohomology_over_zz, de_rham_over_qq)
