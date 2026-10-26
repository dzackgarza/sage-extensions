r"""A category endpoint retains its placement in Cat and the exact represented category."""

from sage_extensions.all import *  # noqa: F401,F403


def test_category_object_retains_ambient_cat_and_represented_category() -> None:
    represented = Sets()
    endpoint = CategoryObject(Cat(), represented)

    assert endpoint.category_of_categories() is Cat()
    assert endpoint.represented_category() is represented
