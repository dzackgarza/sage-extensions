# Not under 10 minutes: from_derivation on S^2 read on the chart bumps (killed at 10 min, 2026-11-19).
from sage_extensions.all import *


def test_a_derivation_of_the_two_sphere_is_read_on_the_chart_bumps() -> None:
    r"""On $S^2$ the derivation $f \mapsto Vf$ of $V = x_1\partial_{x_1} + x_2\partial_{x_2}$ is read back as $V$.

    Under $y = x/|x|^2$ the scaling $x \mapsto \lambda x$ is $y \mapsto y/\lambda$, so
    $V = -(y_1\partial_{y_1} + y_2\partial_{y_2})$ on $U_S$.  The section is read on the
    functions $H_a x_a^i$ of the chart bumps (Lee, Prop. 2.25 and Prop. 8.15): component
    $2$ at $x = (2, 3)$ and $-1/4$ at $y = (1/4, 1/2)$.
    """
    sphere = SmoothManifolds().sphere(2)
    north = sphere.atlas()["U_N"]
    south = sphere.atlas()["U_S"]
    sections = sphere.tangent_bundle().sections()
    euler = sections.section(
        {
            "U_N": (north.coordinate(0), north.coordinate(1)),
            "U_S": (-south.coordinate(0), -south.coordinate(1)),
        }
    )

    recovered = sections.from_derivation(lambda function: euler(function))

    assert recovered.components()["U_N"][0](north.domain()((2, 3))) == RR(2)
    assert recovered.components()["U_S"][0](south.domain()((RR(1) / RR(4), RR(1) / RR(2)))) == RR(-1) / RR(4)
    assert recovered == euler
