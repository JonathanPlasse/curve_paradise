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


def calculate_profile(t, ts, js, init=(0, 0, 0)):
    a = np.zeros_like(t)
    v = np.zeros_like(t)
    p = np.zeros_like(t)

    ts = [0, 1 / 4, 3 / 4]

    a_0, v_0, p_0 = init

    for i, ji in enumerate(js):
        is_last = i == len(js) - 1
        mask = (t >= ts[i]) & (t < ts[i + 1]) if not is_last else t >= ts[i]
        poly = [ji, a_0, v_0, p_0]
        a[mask] = interpolate(t[mask] - ts[i], poly, deg=1)
        v[mask] = interpolate(t[mask] - ts[i], poly, deg=2)
        p[mask] = interpolate(t[mask] - ts[i], poly, deg=3)
        if not is_last:
            a_0 = interpolate(ts[i + 1] - ts[i], poly, deg=1)
            v_0 = interpolate(ts[i + 1] - ts[i], poly, deg=2)
            p_0 = interpolate(ts[i + 1] - ts[i], poly, deg=3)

    return a, v, p


# Initial parameter values
time = np.linspace(0, 1, 101)
a_init, b_init, c_init, d_init = 1, 0, 0, 0

# Create a ColumnDataSource with initial values

# Create sliders
slider_a = Slider(start=-5, end=5, value=a_init, step=0.1, title="a_max")
slider_b = Slider(start=-5, end=5, value=b_init, step=0.1, title="b_max")
slider_c = Slider(start=-5, end=5, value=c_init, step=0.1, title="c_max")
slider_d = Slider(start=-5, end=5, value=d_init, step=0.1, title="d_max")


def get_data():
    a, v, p = calculate_profile(
        time,
        [0, 1 / 4, 3 / 4],
        [slider_a.value, -slider_a.value, slider_a.value],
    )
    return {"time": time, "position": p, "velocity": v, "acceleration": a}


source = ColumnDataSource(data=get_data())


# Define a callback function to update the data source
def update_data(attr, old, new):
    source.data = get_data()


# Link the callback to the slider value changes
slider_a.on_change("value", update_data)
slider_b.on_change("value", update_data)
slider_c.on_change("value", update_data)
slider_d.on_change("value", update_data)

# Create a figure and plot the equation
plot_position = figure(x_range=(0, 1), y_range=(-1, 1))
plot_position.line(x="time", y="position", source=source, line_width=3)

plot_velocity = figure(x_range=(0, 1), y_range=(-1, 1))
plot_velocity.line(x="time", y="velocity", source=source, line_width=3)

plot_acceleration = figure(x_range=(0, 1), y_range=(-1, 1))
plot_acceleration.line(x="time", y="acceleration", source=source, line_width=3)

# Display the plot with sliders

curdoc().add_root(
    column(
        slider_a,
        slider_b,
        slider_c,
        slider_d,
        row(plot_position, plot_velocity, plot_acceleration),
    ),
)
