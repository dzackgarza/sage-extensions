r"""The deciding inputs of this round, on one small object each."""
import traceback
from sage_extensions.all import *


def show(label, thunk):
    try:
        print(f"{label}: {thunk()!r}")
    except Exception:
        print(f"{label}: FAILED")
        traceback.print_exc()


# rho(Otilde(A_2)) is the identity, and O(A_A2) is bigger than it: the name of
# the image and the two orders that separate it from its target.
lattice = Lattices(ZZ)("A2")
stable = lattice.stable_orthogonal_group()
discriminant_group = lattice.discriminant_group().orthogonal_group()
image = stable.discriminant_image()
show("stable.description", lambda: stable.description())
show("O(A_L).order", lambda: discriminant_group.order())
show("image.order", lambda: image.order())
show("image.description", lambda: image.description())

# The stabilizer of the arithmetic cusp at the zero sublattice of <6>, and the
# flag stabilizer of GL_2(ZZ): the two callers that state no clause at 5b45523.
ambient = Lattices(ZZ)([[6]])
orthogonal = ambient.O()
subgroup = orthogonal.predicate_subgroup(
    lambda automorphism: True, lambda: "the whole orthogonal group"
)
cusp = next(iter(subgroup.cusps(rank=0)))
stabilizer = cusp.stabilizer()
show("cusp.representative", lambda: cusp.representative())
show("cusp.stabilizer.description", lambda: stabilizer.description())
show("cusp.stabilizer.order", lambda: stabilizer.order())

points = Sets.Δ[1]
plane = ZZ.free_module(points)
first, second = plane.module_generator(points(0)), plane.module_generator(points(1))
general_linear = plane.general_linear_group()
flag = FiniteOrderedSets()((plane.subobject_on(Set((first,))),))
flag_stabilizer = general_linear.flag_stabilizer(flag)
shear = general_linear({points(0): first, points(1): first + second})
swap = general_linear({points(0): second, points(1): first})
show("flag_stabilizer.description", lambda: flag_stabilizer.description())
show("flag_stabilizer contains the shear", lambda: flag_stabilizer.is_parent_of(shear))
show("flag_stabilizer contains the swap", lambda: flag_stabilizer.is_parent_of(swap))

# The image of a subgroup names that subgroup, and reads its description at
# read time only.
four, two = Groups.C(4), Groups.C(2)
generator = next(iter(four.group_generators()))
class_of_one = next(iter(two.group_generators()))
reduction = four.Mor(two)({generator: class_of_one})
source = four.subgroup((generator,))
projected = source.image_under(reduction)
show("image.description", lambda: projected.description())
show("image.order", lambda: projected.order())

# B cap Gamma: the character subgroup's condition is neither rendered nor read
# while the intersection is generated.
lattice_two = Lattices(ZZ)([[2, 0], [0, 2]])
group = lattice_two.O()
asked = []


class Words(str):
    def __new__(cls, words):
        instance = str.__new__(cls, words)
        instance.plain = words
        return instance

    def __call__(self):
        asked.append("read")
        return self.plain

    def __format__(self, specification):
        asked.append("rendered")
        return str.__format__(self, specification)


determinant_one = group.predicate_subgroup(
    lambda automorphism: automorphism.determinant() == 1,
    Words("det(g)=1"),
    character_data={"determinant_kernel": True},
    character_data_complete=True,
)
generated = group.subgroup((next(iter(group.group_generators())),))
intersection = group.intersection(determinant_one, generated)
asked.clear()
family = tuple(intersection.group_generators())
print("B cap Gamma asked of its operand's condition:", tuple(asked))
print("generators lie in both operands:", all(g in determinant_one and g in generated for g in family))

# The two groups of integral points state the words of their construction.
show("SL_2(ZZ).description", lambda: Groups.SL(2, ZZ).description())
show("Sp_2(ZZ).description", lambda: Groups.Sp(2, ZZ).description())
