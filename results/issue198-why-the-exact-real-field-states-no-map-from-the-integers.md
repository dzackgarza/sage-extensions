# Why `RR.coerce_map_from(ZZ)` cannot be built, and what does not reach it

Status: diagnosis only.  No repair is landed; the two hooks that look right are
measured not to reach the failure, and the two repairs that would are named with
what each costs.

## The measurement

On `c3ff64d`, in the image rootfs:

    QQ.coerce_map_from(ZZ)   -> CallableConvertMap, _category_for None
    RR.coerce_map_from(ZZ)   -> ValueError: Integer Ring is not in Category of sets

The traceback of the second: `Parent.coerce_map_from` copies the map, `Map.__copy__`
rebuilds its parent, `Map.parent()` calls `homset.Hom(D, C, self._category_for)`,
and `Hom` refuses an endpoint.  `Hom(ZZ, QQ, Sets())` fails the same way, so this
is not about the exact real field's arithmetic: it is about what `Sets()` contains.

## What `Sets()` contains, and why owned parents are not in it

`Sets()` is a Sage *singleton* category, so its membership is
`Category_singleton.__contains__`, which is built by
`Category_contains_method_by_parent_class(cls())` -- a check **by the object's
class**, against the category's parent class, not against the category graph.
Measured for all three owned rings:

    isinstance(ZZ, Sets().parent_class)   False
    isinstance(QQ, Sets().parent_class)   False
    isinstance(RR, Sets().parent_class)   False

while `ZZ.category().is_subcategory(Sets())` is **True** for each of them.  So the
graph says they are sets and the class check says they are not, and `Hom` asks the
class check.

`QQ.coerce_map_from(ZZ)` works anyway, which is the reason this defect hid: the
map it returns was built with its parent already in place, so copying it rebuilds
nothing.  The exact real field's map is built fresh on the call, so its copy is
where the Hom is asked.

## Two hooks that do not reach it

- Returning the callable `_owned_ring_from_integer` from
  `ExactRealField._coerce_map_from_` for the integer sources: the callable is
  returned (measured) and Sage still copies a map and still asks the Hom.
- Returning the owned morphism `RR.as_ZZ_algebra().algebra_structure_morphism()`:
  the same ValueError.  The owned morphism's `parent()` still rebuilds a Hom, so
  an owned Mor is not the way out while its Homset descends from Sage's.

Neither is landed: each is a two-line change that leaves the failure exactly where
it was.

## The two repairs that would reach it

**Make an owned parent an instance of `Sets().parent_class`.**  That is what the
owned category of sets states as its "required runtime root edge": every owned set
parent should also be a Sage set parent at the implementation boundary.  The graph
edge is there (`OwnedRings.super_categories` names `Sets()`), and the class is what
is missing.  The cost is in `refine`: the mixin for `Sets.ParentMethods` has to
reach every owned parent's class, and that is the change the tree has so far
deliberately not made for *all* parents -- it does it for the Mor classes
(`_super_categories_for_classes`) and not for objects.

**Give the coercion a map whose parent is already built.**  Cheaper in appearance,
but it needs the owned Homset to avoid Sage's `Hom`, and the measurement above says
the owned morphism's parent does not: `RngMor`'s parent is a Homset whose own
construction asks the same question.  That has to be fixed first, and it is a
question about the Mor layer rather than about the reals.

The first is the statement the mathematics makes and it fixes every owned ring at
once; the second is narrower and depends on a layer that is not yet clear of the
same check.

## The mechanism, read from the source of the check

`Sets()` is a Sage singleton, so `x in Sets()` is
`Category_singleton.__contains__`, which is
`Category_contains_method_by_parent_class(cls())`, whose `__call__` is, from
`sage/categories/category_singleton.pyx:70-77`:

    y = x
    return PyType_IsSubtype(<type>((y._category or y.category()).parent_class),
                            self._parent_class_of_category)

So the question is whether the **parent class of the object's own category** is a
subtype of `Sets().parent_class`.  Measured on `25d2190`:

    Sage's QQ   in Sets()  True    isinstance(QQ, Sets().parent_class)  True
    Sage's ZZ   in Sets()  True    isinstance(ZZ, Sets().parent_class)  False
    owned ZZ    in Sets()  False   isinstance(ZZ, Sets().parent_class)  False
    owned QQ    in Sets()  False   isinstance(QQ, Sets().parent_class)  False
    owned RR    in Sets()  False   isinstance(RR, Sets().parent_class)  False

Sage's own integer ring passes without being an instance of that class, so the
test is on the category's parent class, not on the object's; every owned parent
fails it, whatever its graph says.  The owned root's docstring
(`sage_extensions/owned_category.py:44-52`) already names this relation as the
reason Sage's `Sets()` is a super category of the owned root -- but the graph edge
does not make the tree's `parent_class` a subtype of Sage's, which is what the
check reads.

## Two more attempts that do not reach it

- `CallableConvertMap(source, self, _owned_ring_from_integer, parent_as_first_arg=True)`
  returned from `ExactRealField._coerce_map_from_` for an owned integer source:
  `RR.coerce_map_from(ZZ)` still raises the same `ValueError`.  The map is returned
  and Sage still copies it through `Map.parent()`.
- The owned morphism `RR.as_ZZ_algebra().algebra_structure_morphism()`: the same.

## What is left

One repair, and it is at the root: the owned categories' `parent_class` has to
derive from `SageSets().parent_class`, so that
`type((x._category or x.category()).parent_class)` is a subtype of it for every
owned parent.  Sage builds `parent_class` from `ParentMethods` of the super
categories (`Category._make_named_class`), not from their `parent_class`es, so
this is a change to `_make_named_class` in `sage_extensions/owned_category.py` --
a change to the class of **every owned parent**, and therefore one that needs its
own turn with a broad gate over the owned graph, not a corner of one.

## Correction, 2026-11-19: the table above measured the wrong relation

The predicate in `category_singleton.pyx:75` is a **subtype** test on the parent
class of the object's own category:

    PyType_IsSubtype(<type>((x._category or x.category()).parent_class),
                     Sets().parent_class)

The table in the earlier section reports `isinstance(parent, Sets().parent_class)`,
which is the instance relation and not the one the check asks.  Measured again, on
`f9f4e69`, with the subtype test the check actually makes:

    sage ZZ   issubclass(ZZ.category().parent_class, Sets().parent_class)   True
    sage QQ   issubclass(QQ.category().parent_class, Sets().parent_class)   True
    owned ZZ  issubclass(ZZ.category().parent_class, Sets().parent_class)   False
    owned QQ  issubclass(QQ.category().parent_class, Sets().parent_class)   False
    owned RR  issubclass(RR.category().parent_class, Sets().parent_class)   False

So the substance of the earlier reading stands -- the graph says an owned parent is
a set and the class does not -- and the table's column was the wrong measurement.

## Where the base is lost

`parent_class` is `dynamic_class(name, tuple(getattr(cat, "parent_class") for cat in
self._super_categories_for_classes), ...)` (`sage/categories/category.py:1615`), so
the named `Sets.parent_class` reaches an owned parent only through
`_super_categories_for_classes`.  For `OwnedRings()` that list **does** name Sage's
`Sets_with_category`, and yet `OwnedRings().parent_class` does not carry
`Sets.parent_class`: its chain holds `Sets.ParentMethods` (the plain nested class,
from the owned `Sets` level) and never the named class.

The owned `Sets` is where the edge is lost: measured,
`OwnedSets()._super_categories_for_classes` is `['Category of represented
mathematical objects']` -- the owned `Objects()` alone -- although
`OwnedSets().super_categories()` is `[Objects(), SageSets()]`.  Sage sets that
attribute as a side effect of `_all_super_categories` (`category.py:869-877`, a C3
merge of the super categories' lists), and for this category Sage's `Sets()` does
not survive the merge into the list of parents that build classes.

That is the site: an owned category's `parent_class` has to derive from the named
`Sets.parent_class`, and the owned `Sets`' own class list is where it can be added
-- a change to the class of every owned parent, since every owned category inherits
the root's class.  It is not landed: it needs its own turn and a gate over the
owned graph, and this turn spent its budget on a chain-of-charts repair in the
module #198 contracts.

## Attempt, 2026-11-19: the base added at the class, and the recursion it hits

The repair the previous section names was tried.  `OwnedCategoryMixin._make_named_class`
builds `parent_class` from `_owned_implementation_bases(category, provider_names)` --
not from the super categories' named classes -- so the place a base can be added is
that list, and `_bases_of_a_sage_sets_parent` appended `Sets().parent_class` after
it (last, so every owned level keeps its methods ahead of it).

It does not run.  `RR.coerce_map_from(ZZ)` and every construction that builds an
owned parent class raise

    RecursionError: maximum recursion depth exceeded

with the recursion inside the owned linearization:

    owned_category.py:1122  _make_named_class
    owned_category.py:1048  _make_named_class
    owned_category.py:738   _owned_implementation_bases
    owned_category.py:718   _declared_category_linearization
    owned_category.py:709   linearize   (repeating)

A guard on the lookup of `Sets().parent_class` (a module-level cache plus a
re-entry flag) does not stop it: the loop is in the linearization of the owned
implementation bases, which reaches `parent_class` of a level again once the base
list has changed.  The patch is reverted, and the site is now known to be two
things, not one: the base list *and* `_declared_category_linearization`, which has
to be able to linearize a level whose named class derives from a Sage one without
re-entering itself.

## Measured the same day: the remaining #198 residues are not observable

The two decisions still listed as residues -- a determinant of degree four or more
with mixed signs, and a semidefinite quadratic whose linear part leaves the range of
its quadratic part -- can only turn a *refusal for want of a decision* into a
*refusal by decision*.  They are not wrong answers, and nothing a caller can ask
distinguishes them: `trivialized_by` refuses in both.  Measured on the plane with a
frame whose determinant is `x^2 + y` (semidefinite part, linear part outside its
range, zero at the origin): the frame is refused.  So those residues are quality of
the message, not correctness, and a red test for them would have to assert printed
text, which this tree's tests do not do.
