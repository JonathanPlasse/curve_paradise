import numpy as np
from math import factorial
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure


def interpolate(x, coeffs, deg):
    return sum(
        c * x**i / factorial(i) for i, c in zip(reversed(range(deg + 1)), coeffs, strict=False)
    )


def calculate_profile(t, ts, js, init=[0, 0, 0]):
    profiles = [np.zeros_like(t) for _ in range(len(init) + 1)]

    for i, ji in enumerate(js):
        is_last = i == len(js) - 1
        mask = (t >= ts[i]) & (t < ts[i + 1]) if not is_last else t >= ts[i]
        poly = [ji, *init]
        for deg, profile in enumerate(profiles):
            profile[mask] = interpolate(t[mask] - ts[i], poly, deg=deg)
        if not is_last:
            init = [
                interpolate(ts[i + 1] - ts[i], poly, deg=deg) for deg in range(1, len(init) + 1)
            ]

    return profiles


# Initial parameter values
j0_init = 1
a_max_init = 1
v_max_init = 1
d_init = 1

# Create sliders
slider_j0 = Slider(start=0, end=5, value=j0_init, step=0.1, title="j0")
slider_a_max = Slider(start=0, end=5, value=a_max_init, step=0.1, title="a_max")
slider_v_max = Slider(start=0, end=5, value=v_max_init, step=0.1, title="v_max")
slider_d = Slider(start=0, end=5, value=d_init, step=0.1, title="d")


def get_data():
    j0 = slider_j0.value
    a_max = slider_a_max.value
    v_max = slider_v_max.value
    d = slider_d.value

    dt1_p = np.cbrt(d / (2 * j0))
    dt1_v = np.sqrt(v_max / j0)
    dt1_a = a_max / j0

    dt1 = min(dt1_p, dt1_v, dt1_a)

    dt3_p = -(3 * a_max) / (2 * j0) + np.sqrt(a_max**2 / j0**2 + 4 * d / a_max) / 2
    dt3_v = v_max / a_max - a_max / j0

    dt3 = min(dt3_p, dt3_v)

    # Not constrained by a_max or v_max
    # /\
    #   \/
    if dt1 == dt1_p:
        ts = [0, dt1, 3 * dt1]
        js = [j0, -j0, j0]
        duration = 4 * dt1
    # Constrained by v_max
    # /\_
    #    \/
    elif dt1 == dt1_v:
        dt2 = (d - 2 * j0 * dt1**3) / v_max
        ts = [0, dt1, 2 * dt1, 2 * dt1 + dt2, 3 * dt1 + dt2]
        js = [j0, -j0, 0, -j0, j0]
        duration = 4 * dt1 + dt2
    # Constrained by a_max
    #  _
    # / \
    #    \_/
    elif dt3 == dt3_p:
        ts = [0, dt1, dt1 + dt3, 3 * dt1 + dt3, 3 * dt1 + 2 * dt3]
        js = [j0, 0, -j0, 0, j0]
        duration = 4 * dt1 + 2 * dt3
    # Constrained by a_max and v_max
    #  _
    # / \_
    #     \_/
    else:
        dt2 = (
            2
            * (d / 2 - (3 * a_max**2) / (2 * j0) * dt3 - a_max * dt3**2 / 2 - a_max**3 / j0**2)
            / v_max
        )
        ts = [
            0,
            dt1,
            dt1 + dt3,
            2 * dt1 + dt3,
            2 * dt1 + dt3 + dt2,
            3 * dt1 + dt3 + dt2,
            3 * dt1 + 2 * dt3 + dt2,
        ]
        js = [j0, 0, -j0, 0, -j0, 0, j0]
        duration = 4 * dt1 + 2 * dt3 + dt2

    time = np.linspace(0, duration, 1000)
    j, a, v, p = calculate_profile(time, ts, js)
    return {
        "time": time,
        "position": p,
        "velocity": v,
        "acceleration": a,
        "jerk": j,
    }


source = ColumnDataSource(data=get_data())


# Define a callback function to update the data source
def update_data(attr, old, new):
    source.data = get_data()


# Link the callback to the slider value changes
slider_j0.on_change("value", update_data)
slider_a_max.on_change("value", update_data)
slider_v_max.on_change("value", update_data)
slider_d.on_change("value", update_data)

# Create a figure and plot the equation
plot_width = 400
plot_height = 400

plot_position = figure(title="Position", width=plot_width, height=plot_height)
plot_position.line(x="time", y="position", source=source, line_width=3)

plot_velocity = figure(title="Velocity", width=plot_width, height=plot_height)
plot_velocity.line(x="time", y="velocity", source=source, line_width=3)

plot_acceleration = figure(title="Acceleration", width=plot_width, height=plot_height)
plot_acceleration.line(x="time", y="acceleration", source=source, line_width=3)

plot_jerk = figure(title="Jerk", width=plot_width, height=plot_height)
plot_jerk.line(x="time", y="jerk", source=source, line_width=3)

# Display the plot with sliders

curdoc().add_root(
    column(
        slider_j0,
        slider_a_max,
        slider_v_max,
        slider_d,
        row(plot_position, plot_velocity, plot_acceleration, plot_jerk),
    ),
)
