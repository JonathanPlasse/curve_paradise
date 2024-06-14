import numpy as np
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure


def cubic(x, a, b, c, d):
    return a / 6 * x**3 + b / 2 * x**2 + c * x + d


def quadratic(x, a, b, c):
    return a / 2 * x**2 + b * x + c


def linear(x, a, b):
    return a * x + b


def calculate_profile(t, j):
    a = np.zeros_like(t)
    v = np.zeros_like(t)
    p = np.zeros_like(t)

    t_1_4 = 1 / 4
    t_3_4 = 3 / 4

    a_1_4 = linear(t_1_4, j, 0)
    a_3_4 = linear(t_3_4 - t_1_4, -j, a_1_4)

    v_1_4 = quadratic(t_1_4, j, 0, 0)
    v_3_4 = quadratic(t_3_4 - t_1_4, -j, a_1_4, v_1_4)

    p_1_4 = cubic(t_1_4, j, 0, 0, 0)
    p_3_4 = cubic(t_3_4 - t_1_4, -j, a_1_4, v_1_4, p_1_4)

    mask_0 = t < t_1_4
    mask_1_4 = (t >= t_1_4) & (t < t_3_4)
    mask_3_4 = t >= t_3_4

    a[mask_0] = linear(t[mask_0], j, 0)
    a[mask_1_4] = linear(t[mask_1_4] - t_1_4, -j, a_1_4)
    a[mask_3_4] = linear(t[mask_3_4] - t_3_4, j, a_3_4)

    v[mask_0] = quadratic(t[mask_0], j, 0, 0)
    v[mask_1_4] = quadratic(t[mask_1_4] - t_1_4, -j, a_1_4, v_1_4)
    v[mask_3_4] = quadratic(t[mask_3_4] - t_3_4, j, a_3_4, v_3_4)

    p[mask_0] = cubic(t[mask_0], j, 0, 0, 0)
    p[mask_1_4] = cubic(t[mask_1_4] - t_1_4, -j, a_1_4, v_1_4, p_1_4)
    p[mask_3_4] = cubic(t[mask_3_4] - t_3_4, j, a_3_4, v_3_4, p_3_4)

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
    a, v, p = calculate_profile(time, slider_a.value)
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
