# The refusal code predates the returning row, so the regression is downstream of it

`issue381-the-divided-class-read-raises-at-tco.md` and
`issue381-neither-kernel-row-returns-on-this-head.md` both name `9ae39a1` as the
place the refusing read sits, on the grounds that it is a descendant of the
evidence commit `3a4a210` that recorded the row's return.  **That is wrong**, and
the source says so.

## What the history says

```
$ git log --oneline -S "does not separate this line's cusp" -- \
      src/sage_extensions/categories/group/predicate_subgroups.py
b6d7bd8 feat(lattices): decide the building incidence by divided classes (#585)

$ git log --oneline -S "line_cusps_by_key" -- ... (same file)
9ae39a1  b6d7bd8  0e5ac18
```

`b6d7bd8` is **17 Nov**, `0e5ac18` is **16 Nov**, and both are ancestors of
`3a4a210` (18 Nov), which is where the returning row's log was committed.  So the
key, the bucket lookup and this exact refusal were all in the tree when
`Otilde`'s row decided 569 160 edges.

`git show 9ae39a1 -- predicate_subgroups.py` shows the refusal hunk with **both**
a `-` and a `+` side -- `entry = line_cusps_by_key.get(...)`, the `len(candidates)
!= 1` test and the message -- moved out of `_divided_class_edges_per_plane` into
`_divided_class_edges_at_plane`.  A relocation, not an introduction.

## What follows

The returning row on `8c094f8` ran *with* the refusal and never hit an ambiguous
key; the rows on this head run with the same refusal and hit one at their first
record.  So what changed is not the read but what it is asked about -- one of:

* **which plane is drawn** as the split's source, and hence which coverings exist;
* **which flag is seeded** at that plane, i.e. what
  `transport_isotropic_object` places;
* **which lifts are registered**, and so what the composed class action is;
* or the **keys themselves**, if a cusp's class changed.

The commits after `8c094f8` that touch that path are the candidates:

| commit | what it changes |
| --- | --- |
| `591bb08` | the planes through a line now read the library's line orbits of `K_v`, not the port's vector classes -- the drawn plane changes |
| `346113d` | the transporter reads the row's own transports before the port -- the seeded flag can change |
| the `#603` parabolic commits | the pointed families and residue actions `_plane_parabolic_incidence_flags` reads |
| `9ae39a1` | relocation only, above |
| `a821465` | release of a plane's lift; memory, not values |

## Why there is no cheap oracle to bisect with

An oracle cheaper than a row run would have to reproduce the covering at the
source plane without the split.  Both leading candidates change exactly the datum
such an oracle would hold fixed -- `591bb08` the plane drawn, `346113d` the flag
seeded -- so the oracle would have to run the split's own first steps, which is
the row.  The bisect therefore costs one 33-minute run per candidate, and is not
done here.

## The claim that stands

Both kernel rows on this head build 189 721 planes and refuse at their first
relation record, that is measured twice
(`issue381-neither-kernel-row-returns-on-this-head.md`); the refusal is correct
given the key, and the key is equivocal at `T_Co` and injective everywhere the
suite can look.  What is retracted is only the *attribution* of the change to
`9ae39a1`.

No object is introduced: the key, the buckets and the refusal are the library's,
and every commit above is named by its subject line.
