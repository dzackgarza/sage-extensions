# The two-rings lemma: refuted

## The lemma

> **Lemma.** Let $M$ be an owned smooth manifold and $U$ a chart of $M$ whose domain is
> $M$. Then the ring of functions on $U$ and the ring of smooth functions on $M$ are one
> object: `M.atlas()[U].function_ring() is M.smooth_functions()`.

Its hypotheses are exactly the ones a derivation's value meets when it must become a
component: the same manifold, the same coordinate field, the same regularity, and a chart
whose domain is the manifold.  Its conclusion is what the repair of item 2 needs — a value
of a derivation on a coordinate would be a component of the chart's ring without being
re-raised.

The smallest case that tests it: the plane $\mathbb{R}^2$ with its one chart `U`, where
`U.domain() is plane` holds (measured true), against the same identity on a chart whose
domain is proper, where the rings must of course differ.

## Verdict: REFUTED

Measured on `2cffb27`, in the image rootfs:

    plane = SmoothManifolds()(2, "R^2"); chart = plane.chart("U", "x y")
    chart.domain() is plane                                  True
    chart.function_ring() is plane.smooth_functions()        False
    chart.function_ring() is chart.function_ring()           True     (stable)
    plane.smooth_functions() is plane.smooth_functions()     True     (stable)
    C(Infinity, plane, plane.coordinate_field())             the same object as
                                                             plane.smooth_functions()  True
    C(Infinity, plane, plane.coordinate_field()) twice        the same object            True
    chart.function_ring().domain() is plane.smooth_functions().domain()                  True
    chart.function_ring().codomain() is plane.smooth_functions().codomain()              True
    chart.function_ring().differentiability() == plane.smooth_functions().differentiability()
                                                             +Infinity, +Infinity       True

So every component the constructor is keyed by agrees — the same domain object, the same
codomain object, the same regularity — and the two rings are nevertheless two stable,
distinct objects.  The refutation is therefore sharper than "the cache misses": a direct
call `C(Infinity, plane, field)` reproduces `smooth_functions()` exactly, so the *chart's*
ring is built with some argument that differs without differing in domain, codomain or
regularity, or by a route that does not reach the same cached construction at all.  Which
one is not isolated here, and that isolation is the first step of the repair rather than a
consequence of this lemma.

The executable statement of the refutation, which is red on this head and therefore not
landed:

    assert plane.atlas()["U"].function_ring() is plane.smooth_functions()   # False

## What this changes

Item 2's route A is not unblocked by making the rings coincide *by hypothesis*: they do
not, and the manifold whose chart covers it still carries two algebras.  The repair is at
the constructor — one key, one object — and until it exists the re-raising in
`from_derivation` stays necessary.

Sources: the ring is built in `sage_extensions/categories/manifolds.py`
(`_manifold_function_ring`) through `C(Infinity, domain, field)` in
`sage_extensions/categories/functions/real_functions.py` (`_differentiability_class`,
cached by `(regularity, id(domain), id(codomain))`); the readings above are of this
tree's own printed evidence, not of a textbook, so no page is cited for them.
