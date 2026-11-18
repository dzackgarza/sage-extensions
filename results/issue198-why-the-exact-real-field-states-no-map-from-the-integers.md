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
