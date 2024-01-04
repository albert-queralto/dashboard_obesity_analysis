import pandas as pd
import numpy as np
from itertools import cycle

from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, 
    Legend, LegendItem, HoverTool
)

from bokeh.palettes import BuRd7

from utils import break_text, scale, nth_root, custom_scale_radii, round_to_nearest

# Dictionary of the variables and their actual names
variables_dict = {
    'smoke': 'Smoking habit',
    'calc': 'Consumption of alcohol',
    'gender': 'Gender',
    'scc': 'Monitors caloric consumption',
    'faf': 'Physical activity',
    'tue': 'Time using technology devices',
    'mtrans': 'Transportation used',
    'nobeyesdad': 'Obesity class',
    'age_group': 'Age group',
    'age': 'Age',
}

# Tools to be displayed with the plot
TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

# Width and height of the plot
width_donut = 700
height_donut = 700

# Value of n for the nth root, number of points
n=4
num_points = 7

def create_donut_chart_plot(
        df: pd.DataFrame,
        filter_variable: str,
        binary_variable: str
    ) -> figure:
    """
    Creates a donut chart for the given variables. This plot is based on the
    code from the following link:
    https://docs.bokeh.org/en/latest/docs/examples/topics/pie/burtin.html

    Parameters:
    -----------
    df: pd.DataFrame
        DataFrame containing the data.
    filter_variable: str
        Variable to be used for filtering and showing the inner bars.
    binary_variable: str
        Variable used to create the two groups of the donut chart in the outer
        layer.

    Returns:
    --------
    figure
        Donut chart plot.
    """
    # Sorts the dataframe by the filter_variable to get the right order of the
    # bars in the inner layer
    df.sort_values(by=filter_variable, inplace=True)

    # Groups the dataframe by obesity categories, binary_variable and 
    # filter_variable and gets the counts for each group
    grouped_df = df.groupby(
        ['nobeyesdad', binary_variable, filter_variable]
    ).size().unstack().reset_index()
    grouped_df.fillna(0, inplace=True)

    # Sorts the dataframe by the binary_variable to get the right order of the
    # bars in the outer layer
    grouped_df.sort_values(by=binary_variable, inplace=True)
    grouped_df.reset_index(drop=True, inplace=True)

    # Gets the unique categories of the filter_variable (used for the inner layer)
    filter_variable_categories = df[filter_variable].unique().tolist()

    # Sets the colors for the binary_variable categories (used for the outer layer)
    colors_list = ['#a05d2f', '#fc9957']
    binary_variable_colors = {}
    for category, color in zip(grouped_df[binary_variable].unique(), colors_list):
        binary_variable_colors[category] = color

    # Calculates the angles for the outer and inner layers
    big_angle = (2 * np.pi + 0.05) / (len(grouped_df) + 1)
    angles = np.pi / 2 - 3 * big_angle / 2 - np.array(grouped_df.index) * big_angle

    # Stores the start and end angles for the inner layer
    grouped_df['start'] = angles
    grouped_df['end'] = angles + big_angle

    # Adds the colors for the outer layer and the alpha value
    grouped_df['colors'] = [binary_variable_colors[item] for item in grouped_df[binary_variable]]
    grouped_df['colors_with_alpha'] = [color + 'BF' for color in grouped_df['colors']]

    source = ColumnDataSource(data=grouped_df)

    # Calculates the minimum and maximum values for the nth root that will be
    # used to scale the counts
    min_val = nth_root(1E1, n)
    max_val = nth_root(3E5, n)

    # Creates the figure
    title = f'Donut Chart for {variables_dict[filter_variable]} by {variables_dict[binary_variable]}'
    fig = figure(
        width=width_donut,
        height=height_donut,
        title=f"{break_text(title, 200)}",
        toolbar_location="right",
        toolbar_sticky=False,
        match_aspect=True
    )

    # Sets the count limit and the scale factor for the radius
    count_limit = 40000
    scale_factor = 14.2

    # Generates a custom scale for the counts using the nth root
    counts = custom_scale_radii(n=n, count_limit=count_limit, num_points=num_points)

    # Transforms the counts to integers
    counts = counts.astype(int)

    # Rounds the counts to the nearest integer and converts them to strings
    # to be displayed in the circles
    str_counts = [str(round_to_nearest(item)) for item in counts]

    # Scales the counts to the minimum and maximum values and gets the radii
    radii = scale(counts, min_val, max_val, n)
    radii = np.nan_to_num(radii, nan=min_val)

    # Creates the outer layer of the donut chart
    big_plot = fig.annular_wedge(x=0, y=0, 
            inner_radius=min_val*scale_factor,
            outer_radius=scale(count_limit, min_val, max_val, n), 
            start_angle="start", end_angle="end",
            start_angle_units="rad", end_angle_units="rad",
            line_color="white", fill_color='colors_with_alpha', 
            source=source)

    # Generates the circles that divide the counts in intervals and adds the
    # values for the inner layer of the donut chart
    fig.circle(0, 0, radius=radii, fill_color=None, line_color="#f0e1d2")
    fig.text(
        x=0, y=radii+2, text=str_counts,
        text_font_size="12px", anchor="center",
        color='white'
    )

    # Sets the colors for bars in the inner layer of the donut chart
    color_cycle = cycle(BuRd7)

    # Calculates the angles to distribute the bars evenly in the inner layer
    small_angle = big_angle / 14

    # List to store the hover tools
    hover_tools = []

    # Iterates over the filter_variable categories to create the bars in the
    # inner layer
    for i, variable in enumerate(filter_variable_categories):
        # Calculates the start and end angles for each bar
        start = angles + (12.25 - 2 * i) * small_angle
        end = angles + (13.75 - 2 * i) * small_angle

        # Gets the color for the bar
        color = next(color_cycle)

        # Iterates over the counts for each bar to create the hover tools and
        # the bars
        for angle_idx, row in enumerate(grouped_df[variable]):
            # Creates the hover tools
            hover = HoverTool()
            hover.tooltips = [
                ("Category", f"{variable}"), 
                ("Count", f"{row}")]
            hover.point_policy = "follow_mouse"

            # Creates the annular wedge for the bar
            wedge = fig.annular_wedge(
                x=0, y=0, inner_radius=min_val*scale_factor, 
                outer_radius=scale(row, min_val, max_val, n), 
                start_angle=start[angle_idx], 
                end_angle=end[angle_idx], 
                color=color, 
                line_color=None, 
                legend_label=variable,
            )

            # Renders the hover tools and adds them to the list
            hover.renderers = [wedge]
            hover_tools.append(hover)

    # Adds the hover tools to the plot
    fig.add_tools(*hover_tools)

    # Gets the maximum value of the radii and adds a 3% margin to it
    r = max(radii) * 1.03

    # Calculates the x and y coordinates for the obesity categories
    xr = r * np.cos(angles + big_angle / 2)
    yr = r * np.sin(angles + big_angle / 2)

    # Rotates the obesity categories to be displayed in the right position
    rotation_angles = (angles + big_angle / 2 + 3 * np.pi / 2)

    # Adds the obesity categories to the plot
    fig.text(
        xr, yr, [" ".join(x.split()) for x in grouped_df.nobeyesdad],
        text_font_size="13px", anchor="center",
        angle=rotation_angles, color='white'
    )

    # Sets the plot properties
    fig.axis.axis_label = None
    fig.axis.visible = False
    fig.toolbar.autohide = True
    text_color = 'white'
    fig.title.text_color = text_color
    fig.title.text_font_size = '16px'
    fig.title.align = 'center'
    fig.grid.grid_line_color = None
    fig.axis.axis_line_color = None
    fig.background_fill_color = None
    fig.border_fill_color = None
    fig.background_fill_alpha = 0.0
    fig.border_fill_alpha = 0.0
    fig.legend.label_text_color = text_color
    fig.legend.title_text_color = text_color
    fig.legend.location = 'center'
    fig.legend.click_policy = 'hide'
    fig.legend.background_fill_alpha = 0.0
    fig.legend.glyph_height = 15
    fig.legend.glyph_width = 40
    fig.legend.title = variables_dict[filter_variable]
    fig.legend.border_line_color = None
    
    # Dynamically calculates the indices where the binary_variable changes
    change_indices = [idx for idx, (prev, curr) in enumerate(zip(grouped_df[binary_variable], grouped_df[binary_variable].shift(1))) if prev != curr]

    # Creates the legend items for the binary_variable categories
    legend_items = [
        LegendItem(label=f"{category}", renderers=[big_plot], index=i)
        for i, category in zip(change_indices, grouped_df[binary_variable].unique())
    ]

    # Adds the legend to the plot
    legend = Legend(items=legend_items, location="top_left", 
            orientation="horizontal", background_fill_alpha=0,
            border_line_color=None, label_text_color=text_color,
            title_text_color=text_color,
            title=f"{variables_dict[binary_variable]}")
    fig.add_layout(legend, 'center')

    return fig

