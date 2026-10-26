r"""Objects of Cat use Cat's declared object runtime type."""

from sage_extensions.all import *  # noqa: F401,F403


def test_category_objects_have_the_declared_cat_object_type() -> None:
    category = Cat()

    assert isinstance(Sets(), category.ObjectType)
    assert isinstance(category, category.ObjectType)
