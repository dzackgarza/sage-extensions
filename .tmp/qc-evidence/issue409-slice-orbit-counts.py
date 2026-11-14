from sage_extensions.all import *  # noqa: F401,F403

form = (Lattices(ZZ)([[0, 2], [2, 0]]) ** 2).discriminant_group()
group = form.orthogonal_group()
vector = next(iter(form.module_generators()))
orbit = group.orbit_of_element(vector)
print("split: |orbit| =", orbit.cardinality(), "|G| =", group.cardinality(),
      "|Stab| =", group.stabilizer_of_element(vector).cardinality())

form2 = Lattices(ZZ)([[3, 0], [0, 3]]).discriminant_bilinear_form()
group2 = form2.orthogonal_group()
vector2 = next(iter(form2.module_generators()))
orbit2 = group2.orbit_of_element(vector2)
print("ternary: |orbit| =", orbit2.cardinality(), "|G| =", group2.cardinality(),
      "|Stab| =", group2.stabilizer_of_element(vector2).cardinality())
