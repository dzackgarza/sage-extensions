# Constructor architecture

A public constructor denotes an object or morphism in the `lean-categories` catalogue. `lean-cas-dsl` reads that declaration, its typed input and its structural route; a leaf can only answer a registered computation on an input form. Research presents the resulting language in experiments and notebooks and may supply opaque computational implementations. It does not define a second category, constructor identity, property classifier or operation surface. This is the architecture of [INTENT.md](https://github.com/dzackgarza/research/blob/main/INTENT.md) and the replacement map in `lean-cas-dsl/specs/computational-core.md` §3.

## Construction ownership

| Mathematical input | Formal owner and datum | Kernel and leaf boundary |
| --- | --- | --- |
| A named set such as `Fin n` | `lean-categories/LeanCategories/Catalogue/Semantics/Foundation/Objects.lean`: `obj.sets.fin` denotes `Fin n`, with `n : ℕ` | The kernel reads the registered object at its typed parameter. A leaf may implement an operation on a declared input form. |
| A property of an existing object | A catalogue classifier and its predicate, for example `clf.sets.finite` in `Foundation/Finiteness.lean` | The kernel uses the classifier to form the refined type. A leaf does not decide which objects have the property. |
| Cardinality | `Foundation/Cardinality.lean`: `card : Core(Sets) ⥤ Discrete Cardinal`, registered once as `fun.sets.cardinality` and presented as `cardinality` on `Sets` | The kernel composes registered structural routes to this functor; a leaf returns an answer in the declared result form. Cardinal comparison morphisms belong to the distinct preorder category on `Cardinal`. |
| A product, coproduct, pullback or other universal construction | The formal cone, cocone, legs and mediator, registered at the relevant category and diagram shape | The kernel retains those maps in its typed result. A leaf's apex alone cannot supply or certify them. |
| A selected module, form, algebra or subgroup construction | The catalogue's dependent input, actual maps, category and structural functors | The kernel retains the selected construction and resolves operations along the registered functors. A leaf may compute an answer to a resulting request. |

`lean-cas-dsl/specs/computational-core.md` §3 assigns the old `sage-categories` dynamic-class construction, initializer threading, target-state grafting and MRO ordering no Lean replacement. A selected functor acts as the explicit term `F(X)`. Registered comparison cells resolve distinct routes; Python inheritance order does not. `sage-categories` remains a source of requirements and possibly private implementations, not a second public constructor runtime.

A construction states its defining data and laws at the formal owner. It does not establish a leaf's correctness. The permanent `lean-cas-dsl` acceptance assertions, whose expected values are independent of leaves, are the only evidence about computations. A local research specimen can expose a wiring defect, but it cannot alter the formal meaning or count as leaf acceptance.

## Research migration

`sage_extensions/owned_category.py` still supplies `_owned_implementation_bases`, `ConstructionContract`, `_construction_contract`, `_mor_construction_contract` and `_object_of`. The first orders Python providers; the contracts inspect implementation signatures; `_object_of` instantiates a selected `ObjectType`. These are transitional implementation facts, not a semantic source. `Algebras(R)._call_(module, multiplication)` and `FormModules(R)._call_(form)` state mathematical inputs; their Python initializer chains are a different concern. A migration compares the actual retained modules, forms, maps and universal data against the formal declarations before removing a caller of the old route.

The first complete layer is `Sets` under [research #606](https://github.com/dzackgarza/research/issues/606), including finite and countable sets, orders, powersets, cardinality, ordinals and the stated limits and colimits. Later layers and deletion of shared transitional machinery remain with [#384](https://github.com/dzackgarza/research/issues/384). A published `sage-categories` finite-set example is a useful source specimen, but does not replace the set layer. The published dependency pin is not evidence that a research constructor has moved.

For each construction, record its formal category and declaration, typed input and hypotheses, actual selected structure functors, retained object and arrow data, kernel request and result form, and the research callers to migrate. When the formal input is absent, keep the precise mathematical requirement at its upstream owner. Preserve the existing mathematical specimens; terminal execution follows `DEV-58`.

A module retains its scalar action and selected base ring; a formed module retains the underlying module, form and associated maps; an algebra retains its module, multiplication and chosen unit when one is part of the input. A subgroup retains its ambient group and monomorphism, whose image under the group-to-set functor is the underlying set inclusion. For a limit, retain the diagram, cone and mediator; an apex with the expected size does not determine them. These are the data to compare in `Algebras(R)`, `FormModules(R)`, `Subgroups` and the set constructions before replacing their research consumers.

The historical changes below identify data that a migration must preserve:

| Inspected change | Required mathematical distinction |
| --- | --- |
| `7bbf7e60c` added a `BiproductLattices.ParentMethods.__init__` forwarding `summands` and `biproduct_factors`; `d59eb8ef0` removed it and ordered providers by `_derived_construction_parameters` | The biproduct has selected summands and factors. The formal construction and kernel result must retain them without a leaf forwarding constructor. |
| `70104eaf6` changed localized-module construction from `Category.join(placement)` to `owned_category_join(placement)` | A category join and a selected construction route are different data. Retain the localization map and its module structure, not the provider order that happened to initialize them. |
| `144ba1883` removed the explicit `ModuleMorphism` base and stored lower arrow from `MultiplicativeAlgebraMorphism` | Arrow structure comes from its Mor category and selected functors. A Python class base does not establish the corresponding formal morphism. |
| `09215fd7e` separated algebra framing from module framing; `e8866fb1f` repaired losses involving selected lifts, bilinear pullbacks and framed-module queries | Similar names or common endpoints do not identify selected modules, forms, resolutions or maps. Follow each retained datum and arrow. |

Those diffs are source evidence about the old implementation. They do not establish a passing current session or prove that a formal replacement is complete.

## Exact-name lattice input

`categories/_lattice.py::_lattice` accepts forms, tensors, free modules, named input, ranks and row data; these are different mathematical input forms. Its exact-name branch currently recognizes `U` and `H` through `_hyperbolic_plane_gram_tensor` and `_lattice_from_gram_tensor`. Keep that branch distinct from the finite crystallographic Cartan-type parser. An exact-name registration must reject duplicate names and any name already accepted by that parser, so it cannot silently change the meaning of `A2` or another descriptor. `CartanType_abstract` input retains its own route.

The named input may remain a private research input adapter while its consumers use the transitional preamble. When presented in the final language, the name must resolve to an upstream declared object or construction on its exact mathematical data. A string registry can select a local computational presentation; it cannot register a new category, constructor law or accepted result. Its source and loaded-module scope are useful diagnostics, not semantic evidence.
