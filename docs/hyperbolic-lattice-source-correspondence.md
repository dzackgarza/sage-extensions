# Hyperbolic lattice source correspondence

These notes preserve the source correspondence and mathematical rationale from parent revision `c457e6b4aa087d447711b6cc374a212b72ef5051`, with original source line numbers. Their relocation does not certify the whole algorithm.

## `src/sage_extensions/categories/hyperbolic_lattices.py`

### `Module`

Lines 447–447:

: Sentinel for "the cell at the controlling vector has not been asked for yet".

### `_filtered_vinal_class._FilteredVinAl.cell`

Lines 815–817:

``FundCone`` is cutting the cell itself and asks the layer
enumeration on the way; the walk has written no root yet, so
the cell is not cut and there is nothing to cache.

Lines 840–846:

One lineality direction: the primitive vector of v0^perp
orthogonal to every normal.  The normals are independent,
because their Gram factored, so together with v0 they have
rank n-1 and the kernel below is a line; its primitive
generator is integral, orthogonal to the normals and to v0,
and of positive square, because it lies in the positive
definite v0^perp.

Lines 855–861:

The frame of the normals and m generates v0^perp up to a
finite index, and the index is paid in coset
representatives: a vector of v0^perp is written in the
frame's coordinates only after its representative is added.
The representatives are the integer points of the
parallelepiped of the frame's coordinates in a basis of
v0^perp, the same construction as the engine's own W.

Lines 869–871:

The frame lies in v0^perp, so its coordinates in a basis of
v0^perp are integral; a fractional entry means the frame is
not what the construction above says it is.

### `_filtered_vinal_class._FilteredVinAl.Roots_decomposed_into`

Lines 1018–1020:

The integers t with q(m)(alpha + t)^2 <= remaining: the
square-root bound is a floor of the real root, so each
end is extended while the exact inequality still holds.

### `_filtered_vinal_class._FilteredVinAl._layer_constraints`

Lines 1113–1117:

One family -- the walls, the normals, the offset and the
lineality direction -- and its Gram matrix is the whole of the
pairings this method reads: the wall-by-normal block is the rows
of the constraints, and the last two columns are their
right-hand sides.

### `_filtered_vinal_class._FilteredVinAl._cone_combinations`

Lines 1203–1207:

Every cut the enumeration keeps is one of these rows, with its
right-hand side and the two running sums that make it a bound on
the current level: what the coefficients already chosen spend of
it, and what the ones below the current level spend at their
floors.

### `HyperbolicLattices.ParentMethods._full_chamber_vertices`

Lines 1802–1806:

The full group's chamber is the restricted walk with the filter
that admits every root: the enumeration of §4.1 in the cell's own
coordinates, and the candidate test of :meth:`_FilteredVinAl.
IsNewRoot`, are the same questions the engine answers, and both
answer them for the walls listed here.

### `HyperbolicLattices.ParentMethods.subgroup_fundamental_chamber`

Lines 1945–1951:

The algorithm asks about the same root repeatedly, once per
decomposition it belongs to, and membership in a subgroup of
infinite index is not cheap; the answers are memoised for the one
call.  A caller whose subgroup has its own decidable criterion
should pass it to `fundamental_chamber(admits_root=...)` instead:
that is the path `subgroup_cusp_chamber` takes, with the discriminant
criterion of the stabilizer's image.

### `HyperbolicLattices.ParentMethods.subgroup_cusp_chamber`

Lines 2040–2040:

The finite discriminant-image subgroup the given generators build.

Lines 2049–2051:

One sift per distinct root: the algorithm asks about the same root
once per decomposition it belongs to, while the answer depends only
on the root's coordinates.

Lines 2060–2074:

The anchor: the vertex of the full chamber furthest from the light
cone at which the subgroup still leaves a cell.  The layers of the
walk are indexed by the height \(b(a,v_0)\), and with
\(a=W+mv_0\) that height runs over \(b(W,v_0)+m\,q(v_0)\): an
arithmetic progression whose step is the controlling vector's own
square, so a vertex of larger square resolves the same height
range in fewer layers, and each layer's candidates grow with the
height it is at.  A vertex whose cell does not span leaves the walk
without coordinates to enumerate in, so the vertex taken is the
first, in decreasing square, at which the subgroup admits at least
\(\operatorname{rank}(v_0^\perp)-1\) of the walls through it; if
there is none, the one admitting most.  Every vertex of the full
chamber is a valid controlling vector (Vinberg 1972, §3.2, the
construction after Proposition 3, p. 27), so the choice changes
only the cost.

Lines 2081–2083:

An ideal vertex is not a point of the hyperbolic space, and
a vertex whose walls are not a Z-basis of its orthogonal
complement leaves the walk's own cell condition unsatisfied.

### `HyperbolicLattices.ParentMethods.isotropic_elements_below_height`

Lines 2184–2187:

The framing coordinates arrive in the engine ring, so the divisibility test and
the reconstruction are engine arithmetic, and the candidate is read back as
integers: ``coordinate // square`` is a quotient of engine integers by the
engine image of ``square``, which is what makes the reconstruction integral.
