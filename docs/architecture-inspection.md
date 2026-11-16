# Inspecting the declared architecture

The category graph the source declares is the surface a change to a placement is
read on: an edge `C -> D` asserts a forgetful functor, and the shape of the graph
around the node a change lands in is what says whether that step is one step.
`just category-graph` reads the graph out of the source with `ast`, so it answers
on a tree that does not currently import, and the views below print it.

This page and the tool it documents are ported from `dzackgarza/research`, from
`docs/architecture-inspection.md` and
`src/dzack_research/utilities/category_graph.py` at commit `d62f344542`.  The
live-survey tools that page also documents -- `just placement`,
`just refactor-survey`, `just tags`, `just preamble-complexity` and
`just preamble-megadoc` -- are the research session's own and are not part of
this repository.  Every view here reads this tree's source, and none of them
needs a session that loads.

The graph is one-dimensional: a 0-cell per category, a 1-cell per declaration,
no 2-cells.  So `H_1` is the whole cycle space, and a generator is a pair of
paths the graph asserts are equal, which is a coherence obligation and never a
proof that one is missing.  A reported edge is a statement the source makes;
whether it is the mathematics is read by a mathematician against the category's
own definition, and no view here decides it.

## Choose the evidence

| Question | Command | Evidence and limit |
| --- | --- | --- |
| What ancestry does the source declare? | `just category-graph` (the default `table` view), `just category-graph json`, `just category-graph slice` | Python declarations and the axiom edges Sage's join supplies; a declaration computed from a local expression is recorded as written, not resolved |
| Who declares a given supercategory? | `just category-graph by-supercategory` | Each name and its claimants, most-claimed first: a large group is one claim made many times |
| Which categories name a Sage category? | `just category-graph foreign` | An owned category whose supercategory is named in `sage.*`; empty is a fact about the tree, not a failure |
| What is mechanically wrong? | `just category-graph audit` | A supercategory name nothing defines, a declaration computed from a local expression, a category declaring its own name over other data, and a directed cycle.  None of these needs a reading of the objects |
| How wide and how deep is the graph? | `just category-graph shape` | Breadth (unfactored declarations into a node), depth, the pieces apart from the largest, and the declarations the transitive reduction drops as shortcuts |
| Where do objects reach a fallback assertion? | `just category-graph routes`, `--operation NAME` | For each object operation whose definition ends in an assertion: where it is defined and overridden, and the topmost categories with no override, hook definition or case of the definition above them |
| What does each operation on objects build, and where is the result placed? | `just category-graph constructions`, `--select CATEGORY` | Every public object, element and morphism operation whose source builds an object, followed through module functions, category methods and category application; each line states the category the result is placed in and the property of an input that changes it |
| Which objects are placed in the wrong property subcategory? | `just category-graph properties` | For each property axiom: the categories under it, the construction sites that place a result under it from a property of an input, and the construction sites that place by no property at all |
| What is the literal graph? | `just category-graph dot`, `just category-graph-svg` | One edge per declared supercategory, drawn; `.tmp/category-graph/declared-graph.{dot,svg}` |
| Which cycles owe a 2-cell? | `just category-graph cells` | Graph homology, the 2-connected blocks, a minimum cycle basis, and each generator classified as a computed axiom join or as a witness for review |

The `audit`, `shape`, `cells` and `topology` views use Sage's graph, homology and
poset libraries; the recipes run those under Sage's interpreter and the rest
under plain Python.  Every view reads Python source and does not preparse
`.sage` files.  A parser failure names the file and stops the report; decorators,
generated classes and receiver-dependent dispatch are recorded as what they
are -- a lead for a reader, not a proved edge.

## Read the declarations, and the group a change lands in

`just category-graph by-supercategory` is the surface to read after any change to
a placement: find the group the change lands in and read the whole group, not
the row it adds.  A category claiming a supercategory two or more levels up
duplicates a path that already exists, and `just category-graph shape` names
each declaration the transitive reduction drops -- the shortcut edge on its own
line, and beside it the longer path that reaches the same category.

A shortcut is not automatically wrong -- the longer path may say something the
short one does not -- but it is a claim that the two composites are the same
functor, and the graph records no proof of that.

## Find where objects reach an operation's fallback assertion

```sh
just category-graph routes --operation cardinality
```

`Sets().cardinality` answers for the objects its cases cover and through the
`_cardinality_decision` hook; every other object reaches its closing assertion
unless a category above it overrides `cardinality`.  The view names the owner,
its hooks, the categories below it that define the operation or a hook, the
classes outside the category graph that realize it for the objects they build,
and then the topmost categories whose objects still reach the fallback, with the
number of categories below each: an override at one of them covers everything
beneath it.  Without `--operation` the view ranks every operation whose body
asserts by that count.

The reading is of source, so a realization class answers only for the objects it
constructs, and an operation whose body answers everywhere is not listed.  A
construction that declares only its parameter -- a slice declares the category it
is taken over -- inherits every operation of every category it is applied to, and
is listed under each of them.

## Read what each construction places its result in

```sh
just category-graph constructions --select Sets --select PowerSets
```

Each line is a construction and the category the source places its result in.
Read it as mathematics.  Under `PowerSets`, `X.from_predicate(predicate)` is an
object of `Sets().Subobjects(base)`, that is of `SetSubobjectCategory`; that
category declares a local expression and no property axiom, so a subset of a
finite set is not placed finite by this route, and its cardinality reaches the
fallback assertion of `Sets().cardinality` above.  The line says where the source
puts the result and which property of an input changes that; it does not decide
which placement is right, and the reader does.

`just category-constructions` adds the live survey to the same view: for a
method whose source builds nothing the trace can follow, it calls the category's
example object and reads the category off the returned value's class.  That
needs a session that loads, and it is the only view here that does.

## Cycles, and what they are not

`just category-graph cells` computes the homology of the undirected declaration
graph, its 2-connected blocks, and a minimum cycle basis.  A cycle means two
routes between the same two categories, and only a named pair of functors with a
required equality makes it a coherence question.  Generators inside one base
category are listed separately as computed axiom joins -- Sage applies an axiom
to every supercategory, so those routes are the same inclusion -- and the rest
are listed for review.  A large block is the region where declarations form a
mesh, and that is where the reading is needed.

`just category-graph topology` computes a chosen complex of a selected slice
instead -- `--complex graph` keeps isolated vertices and reports graph cycles,
`--complex flag` fills every clique, `--complex order` takes chains as simplices
and needs a cycle-free relation:

```sh
just category-graph topology --select 'OwnedGroups*' --direction up --complex graph --max-vertices 40
```

None of these invariants is an architecture score.  A contractible complex can
come from a single greatest element and hide the interval a reviewer wants.

## Slice the relation

Edges run from a more structured category to a supercategory.  `--direction up`
takes the chosen vertices and their supercategories, `down` takes their
descendants, `both` the union, and `--between LOWER UPPER` a closed interval.
Selectors take globs:

```sh
just category-graph slice --select 'Lattices*' --direction up
just category-graph slice --between Modules Objects
just category-graph json --output .tmp/graph.json
```

`slice` answers with a JSON document -- the vertices, the edges with the
declaration each comes from, and the declarations themselves -- so a change to
the graph can be diffed against a saved one instead of read.  A slice whose
relation has a cycle cannot be presented as a partial order, and `audit` is
where that is reported.
