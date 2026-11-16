r"""The declared category graph is what the source writes, and nothing else.

``AGENTS.md`` reads a change to a category's placement on the declared graph:
breadth, depth, the declarations that are shortcuts, the cycles that owe a
2-cell.  Importing the preamble does not answer that -- it gives the classes
Sage joined, with computed supercategories already flattened -- so the graph is
read from the source with ``ast``, and these tests assert what it says about
four things a reader relies on:

- the chain a leaf inherits along, and that it ends at a category that declares
  nothing, so no category is left resting on a level the tree does not present;
- a refined category, which is a vertex of its own and declares the vertex with
  one refinement fewer;
- an axiom category's extra supercategory, which is the mathematics the axiom
  is for (a finite digraph is a finite set; a finite set is countable);
- a declaration written as a local expression, which states no edge, because a
  reader that guessed where it lands would put an edge in the graph that nobody
  wrote.

Nothing here counts calls or measures time: the subject is the declaration, and
the assertion is the same one the reader makes at the line it came from.
"""

from sage_extensions.all import *  # noqa: F401,F403


def test_a_leaf_inherits_along_the_chain_the_source_declares():
    r"""A Weyl chamber complex is a chamber system, which is a set, which is an object.

    Each step is the source's: ``chamber_complexes.py`` returns
    ``[ChamberSystems()]``, ``chamber_systems.py`` returns ``[Sets()]``, and
    ``set_categories.py`` returns ``[Objects()]``.  The chain is what a leaf
    gets its operations from without restating any of them, so the test asks for
    the whole path and not only the first edge.
    """
    graph = declared_category_graph()

    assert graph.declares("WeylChamberComplexes") == frozenset({"ChamberSystems"})
    assert graph.declares("ChamberSystems") == frozenset({"Sets"})
    assert graph.declares("Sets") == frozenset({"Objects"})


def test_a_category_that_declares_nothing_is_where_every_path_ends():
    r"""``Objects`` declares no supercategory, and every declared category reaches one.

    A category whose ``super_categories`` returns ``[]`` declares nothing above
    it; every other vertex has a path down to such a vertex, or the declaration
    graph has a cycle and no level to inherit from.  The reader reports a
    vertex with no such path as depth ``-1``, so none may appear.
    """
    graph = declared_category_graph()

    assert graph.declares("Objects") == frozenset()
    assert graph.supercategories_of("Objects") == frozenset()
    assert -1 not in graph.depths().values()


def test_a_refined_category_declares_the_category_with_one_refinement_fewer():
    r"""A finite digraph is a finite set, and a finite set is countable.

    ``Digraphs`` declares ``Sets().Finite()``: the vertex is ``Sets.Finite`` and
    not ``Sets``, so the edge lands one refinement above the set it is also an
    object of.  ``Sets.Finite`` declares ``Sets`` -- that is what the refinement
    adjoins -- and, through the axiom's own ``extra_super_categories``,
    ``Sets.Countable``, which is the mathematics of being finite.  ``Even`` is
    the tree's own refinement rather than Sage's axiom: ``Lattices().Even()``
    and the vertex it names read the same way, and it declares ``Lattices``.
    """
    graph = declared_category_graph()

    assert graph.declares("Digraphs") == frozenset({"Sets.Finite"})
    assert graph.supercategories_of("Sets.Finite") >= frozenset({"Sets"})
    assert graph.declares("Sets.Finite") == frozenset({"Sets.Countable"})
    assert graph.supercategories_of("Lattices.Even") == frozenset({"Lattices"})


def test_a_declaration_written_as_a_local_expression_states_no_edge():
    r"""``SliceCategory`` returns ``[self.base_category()]``, which names no category.

    The edge is not written down: it is whatever the slice is being taken over.
    The reader records the expression and reports the class as computing its
    declaration, because a graph that placed ``SliceCategory`` under a guessed
    category would state a forgetful functor nobody asserted.
    """
    graph = declared_category_graph()

    assert graph.declares("SliceCategory") == frozenset()
    assert "SliceCategory" in graph.computed()
