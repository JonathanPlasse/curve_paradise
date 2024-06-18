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
j0 = 1
v_max = 1
d = 1

# Create sliders
slider_j0 = Slider(start=0, end=5, value=j0, step=0.1, title="j0")
slider_v_max = Slider(start=0, end=5, value=v_max, step=0.1, title="v_max")
slider_d = Slider(start=0, end=5, value=d, step=0.1, title="d")


def get_data():
    dt1_p = np.cbrt(slider_d.value / (2 * slider_j0.value))
    dt1_v = np.sqrt(slider_v_max.value / slider_j0.value)

    dt1 = min(dt1_p, dt1_v)

    if dt1 == dt1_p:
        ts = [0, dt1, 3 * dt1]
        js = [slider_j0.value, -slider_j0.value, slider_j0.value]
        duration = dt1 * 4
    elif dt1 == dt1_v:
        dt2 = (slider_d.value - 2 * slider_j0.value * dt1**3) / slider_v_max.value
        ts = [0, dt1, 2 * dt1, 2 * dt1 + dt2, 3 * dt1 + dt2]
        js = [slider_j0.value, -slider_j0.value, 0, -slider_j0.value, slider_j0.value]
        duration = dt1 * 4 + dt2

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
slider_v_max.on_change("value", update_data)
slider_d.on_change("value", update_data)

# Create a figure and plot the equation
plot_position = figure()
plot_position.line(x="time", y="position", source=source, line_width=3)

plot_velocity = figure()
plot_velocity.line(x="time", y="velocity", source=source, line_width=3)

plot_acceleration = figure()
plot_acceleration.line(x="time", y="acceleration", source=source, line_width=3)

plot_jerk = figure()
plot_jerk.line(x="time", y="jerk", source=source, line_width=3)

# Display the plot with sliders

curdoc().add_root(
    column(
        slider_j0,
        slider_v_max,
        slider_d,
        row(plot_position, plot_velocity, plot_acceleration, plot_jerk),
    ),
)
