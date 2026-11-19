# Item 2 (sections as derivations of the full C^infty(M)): the two routes, and what blocks each

Status: no repair landed.  Item 2 is the last one the review lists as not met, and the
two routes it names are both blocked on something this turn measured rather than guessed.

## Route A: widen admission to certified smooth objects carrying derivative data

The reviewer's suggestion.  What it needs: an element of `C^infty(M)` that is not given by
chart expressions but carries a derivative along every section, so that the action is
defined on it.

What was tried this turn: the *converse* direction of the identification, a construction
`SmoothSectionModules.from_derivation(derivation)` reading a section off its values on a
chart's coordinates -- the piece of `Gamma(TM) = Der(C^infty(M))` the tree did not have.
It works up to the point where the value of the derivation on a coordinate must be read as
a component.

Measured on `6ae2108`:

    AssertionError: cannot lower Generic morphism: From: 2-dimensional smooth manifold R^2
                    To: Real Field to an engine expression: it is a section of
                    C(Infinity, 2-dimensional smooth manifold R^2, RR) that is written
                    neither as a chart formula nor as a pointwise sum, ...

and the reason is structural: on the plane, `manifold.smooth_functions()` and
`chart.function_ring()` are **distinct objects** (`element_parent(value) is ring` is
False) even though the chart's domain is the manifold, while `_engine_vector_field` can
only lower a component that is an element of the chart's own ring.  A value produced by a
derivation lives in the former and has to be re-raised into the latter, and the re-raising
needs an engine formula it no longer carries once it has been wrapped.

That is a defect worth naming on its own: **the ring of functions on a manifold and the
ring of functions on a chart whose domain is the manifold are two objects for one algebra**,
and every adapter that crosses between them pays for it.  It blocks route A and it is the
next thing to repair.

## Route B: amend the issue's algebra clause

The acceptance comment says not to replace the full smooth-function algebra by the rational
expressions displaying the specimen.  The narrowing landed on 2026-11-19 admits exactly the
maps carrying chart expressions, and refuses an opaque callable at the algebra boundary; an
opaque callable cannot be differentiated, and the tree cannot even decide its smoothness
(the differentiability condition answers a proposition on any domain but the line).

An amendment would say: the algebra is the smooth functions *carried by chart expressions*,
and the action is total on it.  This connection cannot edit issues, so the amendment is a
request to the owner, not an action of this turn.

## Recommendation

Repair the two-rings defect first (a small, well-scoped change: make
`SmoothManifolds.smooth_functions()` return the chart's ring when the chart's domain is the
manifold, or make the re-raising accept a function on the manifold whose chart data the
chart can read).  Then route A becomes implementable, and the identification can be stated
both ways at least on a manifold presented by one chart.  Route B remains the honest
alternative if the algebra is meant to stay as it is.
