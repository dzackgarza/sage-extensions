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
