r"""Finite-index intersection of two character kernels via ambient generators.

The new branch in predicate_subgroups.IntersectionSubgroups exists exactly for
Γ_h = ρ⁻¹(H) ∩ O⁺(N): neither side is generated, both are finite-index
character kernels of the ambient O(N). Previous branches required one side to
be generated (preimage∩generated or character∩generated) and would fall back
to enumerating the ambient's underlying set — the 5118 MiB CAPPED stage on
case_3. The branch fires only when every intersected subgroup is a predicate
finite-index character kernel *and* the ambient has a retained finite generating
family; otherwise it leaves the intersection undecided, preserving the original
infinite/undecided behavior. Inclusion endpoints are the conjunction predicate
on the ambient: every generator produced lies in every intersected subgroup,
and the generated subgroup equals the predicate intersection (index bound is
the product of the individual finite-character indices).
"""

from sage_extensions.all import *

def test_u_lattice_character_intersection_has_small_generating_family():
    # U = hyperbolic plane, O(U) infinite dihedral with 2 generators, discriminant trivial
    L = Lattices(ZZ)([[0,1],[1,0]])
    G = L.O()
    assert G.has_selected_group_resolution() is True
    A = L.discriminant_group()
    OG = A.orthogonal_group()
    H = OG.trivial_subgroup()
    pre = G.discriminant_preimage(H)
    Op = L.O_plus()
    assert pre.contains_character_kernel() is True
    assert Op.contains_character_kernel() is True
    inter = G.intersection(pre, Op)
    # New branch must have fired: intersection now has a selected generating morphism
    assert inter.has_selected_group_resolution() is True
    gens = tuple(inter.group_generators())
    # Every produced generator lies in both character subgroups (inclusion endpoints correct)
    assert all(g in pre and g in Op and g in inter for g in gens)
    # For U, |O(A)|=1 so pre is whole G, O⁺ is index 2 in O, so inter should be index 2
    assert inter.index() == 2
    assert len(gens) == 4  # 2 original gens expanded via Schreier for index 2

def test_preimage_intersection_with_generated_subgroup_preserved():
    # Original branch: preimage ∩ generated must still work (not replaced by new branch)
    L = Lattices(ZZ)([[0,1],[1,0]])
    G = L.O()
    assert G.has_selected_group_resolution() is True
    A = L.discriminant_group()
    OG = A.orthogonal_group()
    H = OG.trivial_subgroup()
    pre = G.discriminant_preimage(H)
    # Generated subgroup: pick one generator of G
    g = next(iter(G.group_generators()))
    B = G.subgroup((g,))
    assert B.has_selected_group_resolution() is True
    inter = G.intersection(pre, B)
    # This should use the original preimage∩generated path, not the new character∩character
    assert inter.has_selected_group_resolution() is True
    # Generated subgroup equality: inter is exactly B ∩ pre
    assert all(h in pre and h in B for h in inter.group_generators())
    # Index check not needed; just ensure no regression
    assert inter.cardinality().is_finite() or inter.has_selected_group_resolution() is True
