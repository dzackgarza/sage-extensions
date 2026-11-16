r"""The arrow type of a fixed Mor is the one its declared graph states.

The arrow type is generated once per family and key, from the first Mor that
asks for it, so what the key holds decides every later Mor's arrows.  A Mor's
arrows are the arrows of its own declared graph: the Mor classes its declared
supercategories select from their endpoints.  So two Mors of one family whose
endpoints select different classes are different theories, and each one's type
is the same whichever Mor the session asked for first.

Sage orders the parent classes of unrelated categories by the order the session
built them, so a row that has to see an order reads a fresh process; the runner
in ``conftest.py`` reports, for each Mor, the classes whose operations its
arrows carry and whether those are ``AlgebraMor``'s.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_the_de_rham_algebra_built_first_leaves_each_differential_graded_mor_its_own_arrows() -> None:
    r"""``DifferentialGradedAlgebras(ZZ)`` at ``Lambda(Q[1], x_0)`` then at ``Gamma(Z[x])``.

    The de Rham algebra is a framed algebra, so the algebra Mor its declared
    graph holds at ``Algebras(ZZ).Associative().Unital()`` is ``AlgebraMor``,
    the class whose arrows are built from generator images.  ``Gamma(Z[x])`` is
    not framed, so the algebra Mor there is the multiplicative one, whose
    arrows preserve multiplication and the unit and are not built from
    generator images.  Both algebras are objects of one category, so both Mors
    are Mors of one family, and a key that omitted the endpoints' selection
    gave whichever was built first the other's arrows.
    """
    de_rham_first = arrow_type_order_run(de_rham_first=True)

    assert de_rham_first.returncode == 0, de_rham_first.stderr
    assert de_rham_first.algebra_morphism_arrows["de_rham"] is True
    assert de_rham_first.algebra_morphism_arrows["divided_power"] is False


def test_the_divided_power_algebra_built_first_leaves_each_differential_graded_mor_its_own_arrows() -> None:
    r"""The same two algebras, asked for in the other order, are the same two theories.

    No order changes which algebra a domain is, so the de Rham Mor is an
    ``AlgebraMor`` here too and the divided-power Mor still is not.
    """
    divided_power_first = arrow_type_order_run(de_rham_first=False)

    assert divided_power_first.returncode == 0, divided_power_first.stderr
    assert divided_power_first.algebra_morphism_arrows["de_rham"] is True
    assert divided_power_first.algebra_morphism_arrows["divided_power"] is False


def test_each_differential_graded_mor_keeps_one_arrow_type_in_either_order() -> None:
    r"""The two sessions agree Mor by Mor, not each with whichever Mor it built first.

    Each Mor's type carries the operations of the Mor classes its own declared
    graph holds, and those classes are selected from its endpoints alone.
    """
    de_rham_first = arrow_type_order_run(de_rham_first=True)
    divided_power_first = arrow_type_order_run(de_rham_first=False)

    assert de_rham_first.returncode == 0, de_rham_first.stderr
    assert divided_power_first.returncode == 0, divided_power_first.stderr
    assert de_rham_first.arrow_types["de_rham"] == divided_power_first.arrow_types["de_rham"]
    assert de_rham_first.arrow_types["divided_power"] == divided_power_first.arrow_types["divided_power"]


def test_the_module_mor_and_the_slice_mor_of_one_algebra_keep_one_arrow_type() -> None:
    r"""``Modules(ZZ).Mor(Gamma(Z[x]))`` and ``AugmentedAlgebras(ZZ).Mor(Gamma(Z[x]))``.

    The pair the issue names: an augmented algebra is an algebra and a module,
    so these are two Mors over one object with two declared graphs, and each
    keeps the arrows of its own graph whichever of the two a session built
    first.
    """
    de_rham_first = arrow_type_order_run(de_rham_first=True)
    divided_power_first = arrow_type_order_run(de_rham_first=False)

    assert de_rham_first.returncode == 0, de_rham_first.stderr
    assert divided_power_first.returncode == 0, divided_power_first.stderr
    assert de_rham_first.arrow_types["module"] == divided_power_first.arrow_types["module"]
    assert de_rham_first.arrow_types["slice"] == divided_power_first.arrow_types["slice"]
