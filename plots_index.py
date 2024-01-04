import pandas as pd
from math import pi
from itertools import cycle
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, ColorBar, 
    LogColorMapper, FactorRange,
    Legend
)

from bokeh.transform import factor_cmap, cumsum
from bokeh.palettes import BuRd5, BuRd6, RdBu11

from utils import break_text

# Dictionary to map the variable names to the actual variable names
variables_dict = {
    'favc': 'Frequent consumption of caloric food',
    'gender': 'Gender',
    'age_group': 'Age group',
    'age': 'Age',
    'caec': 'Eats between meals',
    'fcvc': 'Consumption of vegetables',
    'ncp': 'Number of main meals',
    'ch2o': 'Water consumption',
    'nobeyesdad': 'Obesity class',
}

# Tools to be used in the plots
TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

# Width and height of the plots
width = 600
height = 300

def create_heatmap_fig(
        df: pd.DataFrame, 
        filter_variable: str, 
        obesity_category: str
    ) -> figure:
    """
    Creates a heatmap figure for the given filter variable and obesity category.

    Parameters:
    -----------
    df: pd.DataFrame
        Dataframe containing the data.
    filter_variable: str
        Variable to be used as the filter.
    obesity_category: str
        Obesity category to be used as the filter.

    Returns:
    --------
    figure
        Heatmap figure.
    """
    # Groups the dataframe by the given filter variable, age and obesity category
    # and calculates the size (counts) of each group
    grouped_df = df.groupby(
        ['nobeyesdad', 'age_group', filter_variable]
    ).size().unstack().reset_index()

    # Melts the dataframe to convert the columns into rows
    melted_df = pd.melt(
        grouped_df,
        id_vars=['nobeyesdad', 'age_group'],
        var_name=filter_variable, 
        value_name='counts'
    )
    melted_df.reset_index(inplace=True, drop=True)
    melted_df['counts'] = melted_df['counts'].fillna(0)

    # Filters the dataframe by the given obesity category
    category_df = melted_df[melted_df['nobeyesdad'] == obesity_category]

    # Creates a color mapper for the heatmap based on the max counts
    mapper = LogColorMapper(
        palette=RdBu11, 
        low=1, high=melted_df['counts'].max()
    )

    # Creates the x and y ranges for the heatmap
    x_range = [str(item) for item in melted_df['age_group'].unique()]
    y_range = [str(item) for item in melted_df[filter_variable].unique()]

    # Creates the figure
    source = ColumnDataSource(data=category_df)
    title = f'Heatmap for {obesity_category} by {variables_dict[filter_variable]}'
    fig = figure(
        title=f'{break_text(title, 200)}',
        x_range=x_range,
        y_range=y_range,
        width=width, height=height,
        x_axis_location="below",
        toolbar_location="right", tools=TOOLS, 
        toolbar_sticky=False,
        tooltips=[('Age group', '@age_group'), 
                (f'{variables_dict[filter_variable]}', f'@{filter_variable}'),
                ('Counts', '@counts')]
    )

    # Sets the properties of the figure
    text_color = 'white'
    fig.toolbar.autohide = True
    fig.xaxis.major_label_orientation = 0
    fig.title.text_color = text_color
    fig.title.text_font_size = '16px'
    fig.title.align = 'center'
    fig.xaxis.axis_label_text_color = text_color
    fig.yaxis.axis_label_text_color = text_color
    fig.xaxis.major_label_text_color = text_color
    fig.yaxis.major_label_text_color = text_color
    fig.grid.grid_line_color = None
    fig.axis.axis_line_color = None
    fig.axis.major_tick_out = 10
    fig.axis.axis_label_text_align = 'center'
    fig.axis.major_label_text_align = 'center'
    fig.axis.major_tick_line_color = None
    fig.axis.axis_label_text_font_size = "16px"
    fig.axis.major_label_text_font_size = "14px"
    fig.axis.major_label_standoff = 0
    fig.xaxis.axis_label = "Age Group"
    fig.yaxis.axis_label = f'{break_text(variables_dict[filter_variable], 30)}'
    fig.background_fill_color = None
    fig.border_fill_color = None
    fig.background_fill_alpha= 0.0
    fig.border_fill_alpha = 0.0

    fig.rect(x='age_group', y=filter_variable, 
            width=1, height=1, source=source, 
            fill_color={'field': 'counts', 'transform': mapper}, line_color=None)

    # Creates the color bar for the heatmap
    color_bar = ColorBar(color_mapper=mapper, location=(0, 0))
    color_bar.major_label_text_color = text_color
    color_bar.title_text_color = text_color
    color_bar.major_label_text_font_size = "14px"
    color_bar.background_fill_alpha = 0.0
    color_bar.background_fill_color = None
    
    fig.add_layout(color_bar, 'right')
    return fig

def create_bar_plot(
        df: pd.DataFrame, 
        filter_variable: str,
        obesity_category: str
    ) -> figure:
    """
    Creates a barplot figure for the given filter variable and obesity category.

    Parameters:
    -----------
    df: pd.DataFrame
        Dataframe containing the data.
    filter_variable: str
        Variable to be used as the filter.
    obesity_category: str
        Obesity category to be used as the filter.

    Returns:
    --------
    figure
        Barplot figure.
    """
    # Groups and melts the dataframe based on the obesity category, gender
    # and the given filter variable. If the filter variable is the gender
    # then the dataframe is not grouped by the filter variable
    if filter_variable == 'gender':
        grouped_df = df.groupby(
            ['nobeyesdad', 'gender']
        ).size().unstack().reset_index()
        melted_df = pd.melt(
            grouped_df, 
            id_vars=['nobeyesdad'], 
            var_name='gender', 
            value_name='counts'
        )
    else:
        grouped_df = df.groupby(
            ['nobeyesdad', 'gender', filter_variable]
        ).size().unstack().reset_index()
        melted_df = pd.melt(
            grouped_df, 
            id_vars=['nobeyesdad', 'gender'], 
            var_name=filter_variable, 
            value_name='counts'
        )

    melted_df.reset_index(inplace=True, drop=True)
    melted_df['counts'] = melted_df['counts'].fillna(0)

    # Creates the y_range in log scale using the max counts
    y_range = (0, melted_df['counts'].max() * 1.05)

    # Filters the dataframe by the given obesity category
    obesity_df = melted_df[melted_df['nobeyesdad'] == obesity_category]

    # Creates the figure based on the filter variable (gender or another variable)
    if filter_variable == 'gender':
        x = [gender for gender in obesity_df['gender'].unique()]
        source=ColumnDataSource(data=dict(x=x, counts=obesity_df['counts'].tolist()))
        title = f'Bar Plot for {variables_dict[filter_variable]} by {obesity_category}'
        fig = figure(
            x_range=x,
            y_range=y_range,
            width=width,
            height=height,
            title=f"{break_text(title, 200)}",
            toolbar_location="right",
            tools=TOOLS,
            toolbar_sticky=False,
            tooltips=[
                (f'Gender, {variables_dict[filter_variable]}', '@x'),
                ('Counts', '@counts')
        ])
    else:
        x = [(gender, break_text(str(variable_cat), 10))
                for gender in obesity_df['gender'].unique()
                for variable_cat in obesity_df[filter_variable].unique()]
        source=ColumnDataSource(data=dict(x=x, counts=obesity_df['counts'].tolist()))
        title = f'Grouped Bar Plot for {variables_dict[filter_variable]} by {obesity_category}'
        fig = figure(
            x_range=FactorRange(*x),
            y_range=y_range,
            width=width,
            height=height,
            title=f"{break_text(title, 200)}",
            toolbar_location="right",
            tools=TOOLS,
            toolbar_sticky=False,
            tooltips=[
                (f'Gender, {variables_dict[filter_variable]}', '@x'),
                ('Counts', '@counts')
        ])

    # Creates the color mapper for the barplot
    factors = [break_text(str(item), 10) for item in melted_df[filter_variable].unique()]
    color_mapper = factor_cmap('x', 
            palette=BuRd6,
            factors=factors, start=1)

    # Creates the barplot
    fig.vbar(x='x', top='counts', width=0.9, source=source, line_color="white",
        fill_color=color_mapper)

    # Sets the properties of the figure
    fig.toolbar.autohide = True
    fig.y_range.start = 0
    fig.x_range.range_padding = 0.1
    text_color = 'white'
    fig.xaxis.group_text_color = text_color
    fig.title.text_color = text_color
    fig.title.text_font_size = '16px'
    fig.title.align = 'center'
    fig.xaxis.major_label_orientation = 1
    fig.xaxis.axis_label_text_color = text_color
    fig.yaxis.axis_label_text_color = text_color
    fig.xaxis.major_label_text_color = text_color
    fig.yaxis.major_label_text_color = text_color
    fig.grid.grid_line_color = None
    fig.axis.axis_line_color = None
    fig.axis.major_tick_line_color = None
    fig.axis.major_tick_out = 10
    fig.axis.axis_label_text_align = 'center'
    fig.axis.major_label_text_align = 'center'
    fig.axis.axis_label_text_font_size = "16px"
    fig.xaxis.group_text_font_size = "14px"
    fig.axis.major_label_text_font_size = "14px"
    fig.axis.major_label_standoff = 0
    fig.xaxis.axis_label = f'{break_text(variables_dict[filter_variable], 100)}'
    fig.yaxis.axis_label = "Counts"
    fig.background_fill_color = None
    fig.border_fill_color = None
    fig.background_fill_alpha= 0.0
    fig.border_fill_alpha = 0.0

    return fig

def create_line_plot(df: pd.DataFrame, filter_variable: str) -> figure:
    """
    Creates a lineplot figure for the given filter variable and obesity category.

    Parameters:
    -----------
    df: pd.DataFrame
        Dataframe containing the data.
    filter_variable: str
        Variable to be used as the filter.
    obesity_category: str
        Obesity category to be used as the filter.

    Returns:
    --------
    figure
        Lineplot figure.
    """
    # Groups the dataframe by the obesity category, age and the given filter variable
    grouped_df = df.groupby(
        ['nobeyesdad', 'age', filter_variable]
    ).size().unstack().reset_index()
    grouped_df = grouped_df.fillna(0)

    # Creates the figure
    title = f'Line Plot for Obesity by Age'
    fig = figure(
        width=width,
        height=height,
        title=f"{break_text(title, 200)}",
        toolbar_location="right",
        tools=TOOLS,
        toolbar_sticky=False,
        tooltips=[('Age', '@x'), ('Counts', '@y')])

    # Creates the legend outside the plot
    fig.add_layout(Legend(), 'right')

    # Creates the color palette for the lineplot
    color_palette = cycle(BuRd5)

    # Creates the lineplot for each obesity category
    for _, obesity_category in enumerate(grouped_df['nobeyesdad'].unique()):
        # Filters the dataframe by the given obesity category
        subset_df = grouped_df[grouped_df['nobeyesdad'] == obesity_category]
        subset_df.reset_index(inplace=True, drop=True)
        
        # Calculates the sum of the counts for each age
        age_values = subset_df['age'].tolist()
        counts_sum = subset_df.drop(columns='nobeyesdad').sum(axis=1).tolist()

        # Builds the lineplot for each obesity category
        fig.line(
            x=age_values,
            y=counts_sum,
            line_width=2,
            legend_label=obesity_category,
            line_color=next(color_palette)
        )

    # Sets the properties of the figure
    fig.toolbar.autohide = True
    text_color = 'white'
    fig.title.text_color = text_color
    fig.title.text_font_size = '16px'
    fig.title.align = 'center'
    fig.xaxis.axis_label_text_color = text_color
    fig.yaxis.axis_label_text_color = text_color
    fig.xaxis.major_label_text_color = text_color
    fig.yaxis.major_label_text_color = text_color
    fig.grid.grid_line_color = None
    fig.axis.axis_line_color = None
    fig.axis.major_tick_line_color = None
    fig.axis.major_tick_out = 10
    fig.axis.axis_label_text_align = 'center'
    fig.axis.major_label_text_align = 'center'
    fig.axis.axis_label_text_font_size = "16px"
    fig.axis.major_label_text_font_size = "14px"
    fig.axis.major_label_standoff = 0
    fig.xaxis.axis_label = 'Age'
    fig.yaxis.axis_label = 'Counts'
    fig.background_fill_color = None
    fig.border_fill_color = None
    fig.background_fill_alpha = 0.0
    fig.border_fill_alpha = 0.0
    fig.legend.location = 'top_right'
    fig.legend.click_policy = 'hide'
    fig.legend.background_fill_alpha = 0.0
    fig.legend.label_standoff = 10

    return fig

def create_pie_chart_plot(df: pd.DataFrame, filter_variable: str) -> figure:
    """
    Creates a pie chart figure for the genders and the given filter variable.
    
    Parameters:
    -----------
    df: pd.DataFrame
        Dataframe containing the data.
    filter_variable: str
        Variable to be used as the filter.

    Returns:
    --------
    figure
        Pie chart figure.
    """
    if filter_variable == 'gender':
        filter_variable = 'nobeyesdad'

    # Groups the dataframe by filter variable and gender and calculates the
    # size (counts) of each group
    grouped_df = df.groupby(
        [filter_variable, 'gender']
    ).size().unstack().reset_index()

    # Melts the dataframe to convert the columns into rows
    melted_df = pd.melt(
        grouped_df,
        id_vars=[filter_variable], 
        var_name='gender', 
        value_name='counts'
    )
    melted_df.reset_index(inplace=True, drop=True)
    melted_df['counts'] = melted_df['counts'].fillna(0)

    # Groups the melted dataframe by gender and sums the counts
    melted_df = melted_df.groupby(['gender']).sum().reset_index()
    melted_df.drop(columns=filter_variable, inplace=True)

    # Creates the color palette for the pie chart
    color_palette = cycle(BuRd5)

    # Calculates the angles based on the counts, the color palette and percentages
    melted_df['angle'] = melted_df['counts'] / melted_df['counts'].sum() * 2 * pi
    melted_df['color'] = [next(color_palette) for _ in range(len(melted_df))]
    melted_df['percentage'] = round(
        (melted_df['counts'] / melted_df['counts'].sum()) * 100, 1).astype(str)
    melted_df['percentage'] = melted_df['percentage'].str.rstrip('0')

    # Creates the figure
    title = f'Pie Chart for {variables_dict[filter_variable]} by Gender'
    fig = figure(
        width=width,
        height=height,
        title=f"{break_text(title, 200)}",
        toolbar_location="right",
        tools=TOOLS,
        toolbar_sticky=False,
        tooltips=[(f'Gender', '@gender'),
                    ('Counts', '@counts'),
                    ('Percentage', '@percentage %')],
        x_range=(-0.5, 1.0),
    )

    # Creates the legend outside the plot
    fig.add_layout(Legend(), 'right')

    # Creates the pie chart
    fig.wedge(x=0.25, y=0.25, radius=0.35,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='gender',
            source=melted_df)

    # Sets the properties of the figure
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
    fig.legend.location = 'top_right'
    fig.legend.click_policy = 'hide'
    fig.legend.background_fill_alpha = 0.0

    return fig

