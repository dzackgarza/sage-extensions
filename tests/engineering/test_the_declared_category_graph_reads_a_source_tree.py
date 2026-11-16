r"""The declared category graph, read from a source tree whose declarations are known.

``AGENTS.md`` reads a change to a category's placement on the declared graph:
breadth, depth, the declarations that are shortcuts, the cycles that owe a
2-cell.  The graph is read from the source with ``ast``, so it answers on a tree
that does not import, and what it answers is a claim about the source.

The subject of these tests is a toy tree written here, not this checkout: three
modules declaring nine categories, small enough that every vertex, every
declared supercategory and every edge can be written down beside it.  A test
over the live tree asserts that the reader happens to agree with today's source,
which a refactoring of the tree falsifies and a reader that guesses agrees with
by luck; over a tree written for it, the assertion is the declaration.

What the toy tree states, and what a reader of the graph must get from it:

- a declaration names the vertex it names, not the text of its expression:
  ``Sets().Connected()`` is the axiom vertex ``Sets.Connected``, and an alias
  import of ``Sets`` names ``Sets``;
- an axiom category is a vertex with one axiom more than the category enclosing
  it, and Sage's join supplies the edges from it to the categories it lies
  under -- so ``Paths.Connected`` declares both ``Paths`` and
  ``Objects.Connected``, which nobody wrote;
- a name bound by a function is the category that function returns, and a name
  bound by a parameter of the class declares no category at all;
- a base category named through an import alias is that category, so its edge is
  stated.

Nothing here counts calls or measures time.  The assertions are facts about the
graph, and the reader that reports them is the tool ``just category-graph``
runs.
"""

from sage_extensions.all import *  # noqa: F401,F403

import pytest


def _toy_tree():
    r"""Three modules of toy categories, and nothing else.

    ``objects.py`` declares the base, a property and an axiom; ``paths.py``
    refines the base and declares the same axiom one level up; ``aliases.py``
    names a Sage category through an alias, refines a category through a
    function, and declares its own parameter when it is given one.
    """
    return {
        "toys/objects.py": '''\
from sage.categories.category import Category
from sage.categories.category_with_axiom import CategoryWithAxiom
from sage.categories.sets_cat import Sets


class Objects(Category):
    """The base of the toy graph."""

    def super_categories(self):
        return [Sets()]

    class ParentMethods:
        def cardinality(self):
            """How many points there are."""
            if self in FiniteObjects():
                return self._number_of_points()
            assert False, "an infinite object has no cardinality"

    class Connected(CategoryWithAxiom):
        """Points that reach each other."""

        def extra_super_categories(self):
            return [Sets().Connected()]


class FiniteObjects(Category):
    """Finitely many points."""

    def super_categories(self):
        return [Objects()]

    class ParentMethods:
        def _number_of_points(self):
            return 0
''',
        "toys/paths.py": '''\
from sage.categories.category_with_axiom import CategoryWithAxiom

from .objects import FiniteObjects, Objects


class Paths(Objects):
    """A path: an object whose points reach each other."""

    def super_categories(self):
        return [Objects()]

    class Connected(CategoryWithAxiom):
        """The axiom again, declared one level up."""


class FinitePaths(Paths, FiniteObjects):
    """A path with finitely many points."""

    def super_categories(self):
        return [Paths(), FiniteObjects()]
''',
        "toys/aliases.py": '''\
from sage.categories.sets_cat import Sets as SageSets

from .objects import Objects
from .paths import FinitePaths


def ConnectedFinitePaths():
    return FinitePaths().Connected()


class Aliased(Objects):
    """A Sage category named through an alias, and a category named by a function."""

    def super_categories(self):
        return [SageSets(), ConnectedFinitePaths()]


class Sliced(Objects):
    """A construction that declares the category it is taken over."""

    def __init__(self, base=None):
        self._base = base

    def base(self):
        return self._base

    def super_categories(self):
        base = self.base()
        if base is None:
            return [Objects()]
        return [base]
''',
    }


@pytest.mark.parametrize(
    "view",
    (
        "table",
        "by-supercategory",
        "foreign",
        "audit",
        "shape",
        "cells",
        "json",
        "dot",
        "constructions",
        "routes",
    ),
)
def test_each_view_the_documentation_names_answers_on_a_tree_it_is_given(view):
    r"""Every view reads the tree it is handed, so a change can be read against it.

    ``AGENTS.md`` names the views ``by-supercategory``, ``foreign``, ``audit``,
    ``shape``, ``cells``, ``constructions`` and ``routes``, and a view that
    refuses the tree it is given cannot be read at all.  A view that answers is
    not thereby right; the tests below say what it must answer with.  One view
    per test, because each runs the tool as a process and the views that compute
    homology or cycles load Sage's libraries first.
    """
    report = declared_graph_report(_toy_tree(), "--format", view)

    assert report.exit_status == 0, f"the {view} view: {report.transcript}"


def test_a_declaration_names_the_vertex_it_names_and_where_that_name_comes_from():
    r"""Nine declarations, each with the supercategories its own source states.

    ``Sets().Connected()`` is the vertex ``Sets.Connected`` and not ``Sets``: an
    axiom is a category of its own.  ``SageSets`` is the alias of the Sage
    category ``Sets``, so it names ``Sets`` and no category of this tree.
    ``ConnectedFinitePaths()`` is the function's return, ``FinitePaths``
    refined by ``Connected``.  ``Sliced(base)`` is the branch where the class
    was given a parameter, and ``base`` there is a local expression that names
    no category: the reader records it rather than guessing where it lands.
    """
    document = declared_graph_document(_toy_tree(), "--format", "json")

    assert {
        row["vertex"]: [
            (supercategory["vertex"], supercategory["origin"])
            for supercategory in row["supercategories"]
        ]
        for row in document
    } == {
        "Objects": [("Sets", "sage")],
        "Objects.Connected": [("Sets.Connected", "sage")],
        "FiniteObjects": [("Objects", "owned")],
        "Paths": [("Objects", "owned")],
        "Paths.Connected": [],
        "FinitePaths": [("Paths", "owned"), ("FiniteObjects", "owned")],
        "Aliased": [("Sets", "sage"), ("FinitePaths.Connected", "owned")],
        "Sliced": [("Objects", "owned")],
        "Sliced(base)": [("base", "expression")],
    }


def test_an_axiom_vertex_declares_every_category_the_join_puts_it_under():
    r"""The written edges, and the edges Sage's join supplies, over the toy tree.

    Six edges are written.  ``Paths.Connected`` is written nowhere: it is the
    axiom ``Connected`` applied to ``Paths``, and it lies under ``Paths`` and,
    because ``Objects`` carries the same axiom, under ``Objects.Connected``;
    ``FinitePaths.Connected`` lies under the three categories above
    ``FinitePaths``.  A reader that reported only the written edges would leave
    every axiom category declaring nothing, and one that forgot to carry the
    axiom over a written edge would stop at ``Paths``.
    """
    document = declared_graph_document(
        _toy_tree(), "--format", "slice", "--select", "*", "--direction", "self"
    )

    assert {tuple(edge) for edge in document["edges"]} == {
        ("Objects.Connected", "Objects"),
        ("FiniteObjects", "Objects"),
        ("FiniteObjects.Connected", "FiniteObjects"),
        ("FiniteObjects.Connected", "Objects.Connected"),
        ("Paths", "Objects"),
        ("Paths.Connected", "Paths"),
        ("Paths.Connected", "Objects.Connected"),
        ("FinitePaths", "Paths"),
        ("FinitePaths", "FiniteObjects"),
        ("FinitePaths.Connected", "FinitePaths"),
        ("FinitePaths.Connected", "Paths.Connected"),
        ("FinitePaths.Connected", "FiniteObjects.Connected"),
        ("Aliased", "FinitePaths.Connected"),
        ("Sliced", "Objects"),
    }


def test_a_slice_up_from_a_category_is_the_diamond_it_inherits_along():
    r"""Up from ``FinitePaths``: the two categories it declares, and their one parent.

    The axiom vertices are refinements of categories in the slice rather than
    categories above it, so the slice is the diamond ``FinitePaths`` over
    ``Paths`` and ``FiniteObjects`` over ``Objects``, and the parameter branch
    ``Sliced(base)``, which declares nothing, is outside it.
    """
    document = declared_graph_document(
        _toy_tree(), "--format", "slice", "--select", "FinitePaths", "--direction", "up"
    )

    assert set(document["vertices"]) == {
        "FinitePaths",
        "Paths",
        "FiniteObjects",
        "Objects",
    }
    assert {tuple(edge) for edge in document["edges"]} == {
        ("FinitePaths", "Paths"),
        ("FinitePaths", "FiniteObjects"),
        ("Paths", "Objects"),
        ("FiniteObjects", "Objects"),
    }
