# The per-plane half: what the profile says and what it still needs

## Where the number came from

`results/issue381-the-transporter-is-a-coset.md`'s last section accounts the
`Otilde` row at `T_Co` for all 600 s:

    235 s   _im_rho_engine_and_section                 1 call
    405 s   _iter_splitting_isometries_in_im_rho_from_image  2138 calls, 0.190 s each
              of which tottime 166 s is inside that frame's own body

This note takes the second half, because it is paid 2137 times.

## What the committed profile does and does not show

It was taken with `sort_stats("cumulative").print_stats(40)`, so it ranks by
cumulative time and stores no `tottime` ranking.  What it does say about the
frame:

* `_iter_splitting_isometries_in_im_rho_from_image` — 2138 calls, 405.53 s
  cumulative, **166.46 s tottime**: two thirds of its cost is its own body, not
  its callees;
* `set_categories.__call__` — **2 821 498/1 046 332 calls, 190.89 s**, which is
  the category dispatch behind element construction, i.e. the same overhead
  pattern as the owned-ring arithmetic in `isotropic_lifts`, one layer up.

So the frame's cost is split roughly 166 s of its own arithmetic and 190 s of
category dispatch, and the profile cannot say which lines those are.

## The two candidates, stated so that one measurement separates them

The frame's body walks the `im rho`-orbit of a point breadth-first
(`_iter_splitting_isometries_in_im_rho_from_image`,
`orthogonal_quotients.py:2210`), and per reached point it

1. keys the point by `str(point)` (`keys = {str(point): 0}`), a string
   conversion of a GAP permutation; and
2. builds the next frontier with `libgap` calls and the setwise action
   `Set(List(x, y -> ImageElm(g, y)))`.

`str()` of a GAP object is the cheapest thing to be wrong about: it is one call
per reached point, and there are 2137 of them, so unless it costs tens of
milliseconds it is not the 166 s.  The honest position is that **neither
candidate has been measured**, and the profile that would measure them is one
`print_callees` call on that frame, which the committed log does not carry.

## What this note does not do

It does not introduce a mathematical object, define a new one, or change code:
the objects in play are `im rho`, its orbit on a point, and the double cosets,
all cited in that frame's docstring (Betten--Fripertinger--Kerber, *Algebraic
Combinatorics Via Finite Group Actions*, chapter "Double Cosets", the
orbit--coset bijection `U(gx) |-> UgG_x`).  The turn's product is the statement
that the remaining 405 s is two thirds frame body and one third category
dispatch, with the precise instrument named to divide it again.

## What the 166 s is: three or four GAP set-actions an edge

`print_callees` on the frame, at a 120 s cap:

    _iter_splitting_isometries_in_im_rho_from_image ->
        _im_rho_engine_and_section    1 call   0.000 s
        sage_getargspec               1 call   0.000 s
        inspect.isfunction            1 call   0.000 s

**Nothing.**  The frame's 166 s of `tottime` is reached through no Python call
at all, which leaves one place for it: the C-level `libgap` work in the
generator's body.  And the body
(`orthogonal_quotients.py:2290`-`:2313`) does, per edge of the orbit walk,

    image  = setwise_action(reached_point, generator)      # GAP Set(List(x, y -> ImageElm(g, y)))
    marker = str(image)
    if marker in keys: continue
    reached = generator * reached_element
    if setwise_action(point, reached) != image:            # <-- another set action
        reached = reached_element * generator
        assert setwise_action(point, reached) == image     # <-- and a third

so **three or four `Set(List(...))` actions per edge**, each building a list of
images and sorting it into a set, and two of the three exist only to determine
which product order carries the start to the image.

**The lever, stated without minting anything.**  The composition law is uniform:
if `generator * reached_element` carries the start to the image for one pair, it
does for every pair.  The order can therefore be settled once -- by the first
pair, or by two generators at the start -- and the per-edge re-derivation, one
or two of the three set-actions, drops out.  Nothing about the walk changes: the
points, the transversal and the orbit-coset bijection are
Betten--Fripertinger--Kerber's, cited in the frame's docstring, and the change
removes repeated evaluation of a fact that does not depend on the point.

**What is not yet measured**: the exact split of the three actions (how many
edges, how many generators), and whether `str(image)` matters beside them.  At
2137 points and a generator count in the dozens, three actions an edge is a
large multiple of one, so the order hoist is worth doing first and measuring
after.

## The hoist does not move the row, and the reason is the guard's frequency

`Otilde` at `T_Co`, 600 s cap, at the head that carries the order hoist:

    [Otilde] the row's route: divided-class ... (decided in 1.4 s)
    [  602.29s] Otilde: undecided: the row did not return inside its 600 s cap  [601.37s]

So the change is behaviour-preserving -- the small rows are byte-identical -- and
buys nothing at rank eleven.  The prediction in the last section ("two of the
three actions go, the row falls to about 250 s") was **wrong**, and the walk's
own body says why:

    image = setwise_action(reached_point, generator)
    marker = str(image)
    if marker in keys:
        continue                       # <-- every known image leaves here
    ... setwise_action(point, reached) ...   # <-- only for a NEW point

The composition check runs **once per new orbit point**, not once per edge: the
`continue` above it skips every edge whose image is already in the walk.  There
are 2137 new points and the walk visits 2137 x |generators| edges, so the check
was a fraction `1/|generators|` of the set-actions, and hoisting it removes that
fraction and no more.

**What the per-edge cost therefore is.**  One `setwise_action`
(`Set(List(x, y -> ImageElm(g, y)))`) per edge, which is the walk as written: to
reach a point it must act on the previous one.  Reducing it is not a hoist but a
change of representation -- carrying the reached point by a canonical key and
acting on the key rather than on the sorted set -- and that is a change to the
walk's data, not to its mathematics.  The points, the transversal and the
orbit-coset bijection are unchanged either way, and they are
Betten--Fripertinger--Kerber's, cited in the frame's docstring.

**Sixth correction in this record's cost model**, and the same lesson as the five
before it: the profile said "166 s in this frame", and the frame's *body*
contains both the per-edge action and the per-new-point check; reading which is
which before predicting was the missing step, not measuring after.

**Where that leaves the issue.**  The 405 s per-plane half is one GAP set-action
per edge of an orbit walk with 2137 points and generators in the dozens.  That is
inherent to acting on sorted sets, and the next change -- if there is one -- is
to stop doing that; nothing smaller will move the row inside its cap.

## Before rewriting the walk: the rank-two path has two fast routes ahead of it

`_yield_subgroup_isotropic_orbit_representatives` (`orthogonal_quotients.py:4724`)
does not go straight to the walk.  Per ambient representative it tries, in order:

    rank 1:  quotient.isotropic_line_stabilizer_image(representative)   -> words
             _line_orbit_from_divided_classes(subgroup, representative)  -> the divided classes
    rank 2:  _plane_orbit_from_odd_stabilizer(subgroup, representative)
             _plane_orbit_from_parabolic_stabilizer(subgroup, representative)
    then:    quotient.exact_isotropic_stabilizer_generators(...)  and the cost walk

The `T_Co` profile put 405 s in the walk, so at `T_Co` under `Otilde` **both
in-repo plane routes declined** and the fallback ran.  That makes the first
question not "how do we make the walk cheaper" but **why the two fast routes
decline there** -- and unlike the rewrite, that is one call per route on one
ambient representative, with a `None` or a tuple as the answer.

**Why this matters for the change I proposed last section.**  Rewriting the walk
to act on keys would make the fallback cheaper; making either fast route apply
would make the fallback unnecessary.  The second is smaller, is the shape the
line rows already use (the divided-class route, 527 keys in 3.96 s against 335 s
for one line by the old per-flag scan), and does not touch shared walk machinery
that four Coble row files depend on.

**The check, and it is bounded**: the ambient plane row of `T_Co`
(`isotropic_orbit_representatives(2)`, measured at 76 s in the same profile), one
representative, then each fast route called on it and timed.  A `None` from
`_plane_orbit_from_parabolic_stabilizer` names the declining hypothesis; a tuple
names a mis-routing in the caller instead, which would be a different bug and a
cheaper one.

**No object introduced**: the routes, the divided-class route and the parabolic
stabilizer are the library's own, and the fallback is the orbit--coset walk cited
in its docstring.

## The check: one route declines instantly, the other is the wall the docstring names

Taken at `T_Co`, port `991b88b0`:

    ambient plane orbits of O(T_Co)          1 orbit    24.98 s
    _plane_orbit_from_odd_stabilizer(first)  None (declined)   0.00 s
    _plane_orbit_from_parabolic_stabilizer   reaches libgap.FactorCosetAction(im_rho_perm, right_perm)
                                             and did not return inside 180 s

So the routing question is answered and the answer is **not** a mis-routing:

* the odd-stabilizer route declines at once -- its hypothesis simply does not hold
  at this lattice;
* the parabolic-stabilizer route runs, and its cost is GAP's `FactorCosetAction`
  on the finite image, i.e. exactly the double-coset enumeration that
  `_iter_splitting_isometries_in_im_rho_from_image`'s own docstring says "does
  not return at the Enriques size, while the orbit walk of the class set under
  the `im rho`-generators terminates".

**Which means the walk is not a fallback that should have been avoided: it is the
route the library chose because `FactorCosetAction` does not return.**  There is
no cheaper in-repo route to switch to; the two fast routes are (i) inapplicable
and (ii) the very enumeration the walk replaced.

**So the deferred rewrite is the remaining lever after all**, and this round's
value is that it says so on evidence rather than on the hope of avoiding a day's
work.  The next change is the one the last two sections described: carry the
reached point by a key and act on the key rather than on the GAP set, keeping
`FactorCosetAction` out of the path and the small rows' SHA-256 as the check.

**A note on the object rule.**  The orbit, the `im rho` action, the double cosets
and the orbit--coset bijection are all the library's own and cited in the frame's
docstring to Betten--Fripertinger--Kerber; `FactorCosetAction` is GAP's.  Nothing
here is a definition of mine.
