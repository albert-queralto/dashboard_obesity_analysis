import pandas as pd
import numpy as np
import holoviews as hv
from holoviews import opts
hv.extension('bokeh')

from itertools import cycle
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LogAxis, Span, HoverTool
from bokeh.transform import factor_cmap, cumsum

from bokeh.palettes import BuRd5, BuRd7

# Dictionary of the variables and their actual names
variables_dict = {
    'family_history_with_overweight': 'Family with overweight',
    'gender': 'Gender',
    'hypertension': 'High blood pressure',
    'heart_disease': 'Heart disease',
    'diabetes': 'Diabetes',
    'nobeyesdad': 'Obesity class',
    'age_group': 'Age group',
    'age': 'Age',
}

# Tools to be displayed with the plot
TOOLS = "hover,save,pan,box_zoom,reset,wheel_zoom"

# Width and height of the plot
width_crosstab = 700
height_crosstab = 550
width_sankey = 800
height_sankey = 600


def break_text(text: str, max_length: int) -> str:
    """
    Breaks the text into two lines if the length of the text is greater than
    the max_length.

    Parameters:
    -----------
    text: str
        Text to be broken into two lines.
    max_length: int

    Returns:
    --------
    str
        Text broken into two lines.
    """
    if len(text) <= max_length:
        return text
    else:
        break_index = text.rfind(' ', 0, max_length)
        if break_index == -1:
            break_index = max_length

        line1 = text[:break_index].strip()
        line2 = text[break_index:].strip()

        return f"{line1}\n{line2}"

def create_sankey_df(
        df: pd.DataFrame,
        filter_variables: list
    ) -> pd.DataFrame:
    """
    Creates a dataframe to be used to build the Sankey plot.

    Parameters:
    -----------
    df: pd.DataFrame
        DataFrame containing the data.
    filter_variables: list
        List of variables to be used to filter the columns.

    Returns:
    --------
    pd.DataFrame
        DataFrame containing the data preprocessed to build the plot.
    """
    filtered_df = df[['gender', 'family_history_with_overweight', 'hypertension', 'heart_disease', 'diabetes', 'nobeyesdad', 'age_group']]
    grouped_df = filtered_df.groupby(['gender', 'family_history_with_overweight', 'hypertension', 'heart_disease', 'diabetes', 'nobeyesdad', 'age_group']).size().reset_index(name='counts')

    # Creates a dataframe for the Sankey plot
    sankey_df = pd.DataFrame()

    for filter_variable in filter_variables:
        # Creates a first level grouping by the filter variable and gender
        gender_variable_df = grouped_df.groupby(by=[filter_variable, 'gender'])['counts'].sum().reset_index()
        gender_variable_df['filter_variable'] = filter_variable

        # Renames the columns to be used in the Sankey plot
        gender_variable_df.columns = ['source', 'target', 'value', 'filter_variable']

        # Concatenate the dataframes
        sankey_df = pd.concat([sankey_df, gender_variable_df], axis=0)
        sankey_df.reset_index(drop=True, inplace=True)
        
        # Creates a second level grouping by the age groups and the gender
        age_gender_df = grouped_df.groupby(by=['gender', 'age_group'])['counts'].sum().reset_index()
        age_gender_df.sort_values(by='age_group', inplace=True)
        age_gender_df['filter_variable'] = filter_variable

        # Renames the columns to be used in the Sankey plot
        age_gender_df.columns = ['source', 'target', 'value', 'filter_variable']

        # Concatenate the dataframes
        sankey_df = pd.concat([sankey_df, age_gender_df], axis=0)
        sankey_df.reset_index(drop=True, inplace=True)
        
        # Creates a third level grouping by the obesity category and age groups
        obesity_age_df = grouped_df.groupby(by=['age_group', 'nobeyesdad'])['counts'].sum().reset_index()
        obesity_age_df.sort_values(by='age_group', inplace=True)
        obesity_age_df['filter_variable'] = filter_variable

        # Renames the columns to be used in the Sankey plot
        obesity_age_df.columns = ['source', 'target', 'value', 'filter_variable']

        # Concatenate the dataframes
        sankey_df = pd.concat([sankey_df, obesity_age_df], axis=0)
        sankey_df.reset_index(drop=True, inplace=True)

    return sankey_df

def create_sankey_plot(
        df: pd.DataFrame, 
        filter_variable: str, 
    ) -> figure:
    """
    Builds a Sankey plot for the selected filter variable.
    The plot is based on the example from the Holoviews website:
    https://holoviews.org/gallery/demos/bokeh/energy_sankey.html

    Parameters:
    -----------
    df: pd.DataFrame
        DataFrame containing the data preprocessed to build the plot.
    filter_variable: str
        Variable to be used as a filter.

    Returns:
    --------
    figure
        Sankey plot.
    """
    filter_variables = [
        'family_history_with_overweight',
        'hypertension',
        'heart_disease',
        'diabetes'
    ]
    sankey_df = create_sankey_df(df, filter_variables)

    # Filters the dataframe with the data to build the Sankey plot using the 
    # filter variable column equal to the selected value and the connections label
    filtered_sankey_df = sankey_df[sankey_df['filter_variable'].isin(['connections', filter_variable])]
    filtered_sankey_df.reset_index(drop=True, inplace=True)

    # Defines a dimension for the data
    value_dim = hv.Dimension('value', unit='counts')

    # Creates the Sankey plot
    sankey_plot = hv.Sankey(
        data=filtered_sankey_df,
        kdims=['source', 'target'],
        vdims=[value_dim])

    # Defines the options for the Sankey plot
    sankey_plot.opts(
            title=f'Sankey diagram for {break_text(variables_dict[filter_variable], 100)}',
            width=width_sankey,
            height=height_sankey,
            label_text_font_size='12px',
            label_position='inner',
            node_color='source',
            cmap=BuRd7,
            edge_color='source',
            toolbar='right',
        )

    text_color = 'white'
    # Adds the categories to the plot
    variables_title = hv.Text(0.1,
            height_sankey * 0.87, f'{variables_dict[filter_variable]}',
            halign='center', valign='center').opts(
        opts.Text(text_font_size='14px',
                    text_color=text_color))
    gender_title = hv.Text(width_sankey * 0.415,
            height_sankey * 0.87, 'Gender',
            halign='center', valign='center').opts(
        opts.Text(text_font_size='14px',
                    text_color=text_color))
    age_group_title = hv.Text(width_sankey * 0.83, 
            height_sankey * 0.87, 'Age group',
            halign='center', valign='center').opts(
        opts.Text(text_font_size='14px',
                    text_color=text_color))
    obesity_title = hv.Text(width_sankey * 1.2, height_sankey * 0.87, 'Obesity class', 
            halign='center', valign='center').opts(
        opts.Text(text_font_size='14px', 
                    text_color=text_color))

    overlay = hv.Overlay([
        variables_title,
        gender_title,
        age_group_title,
        obesity_title, 
        sankey_plot])

    # Renders the Sankey plot
    fig = hv.render(overlay, backend='bokeh')

    # Defines additional options
    fig.toolbar.autohide = True
    fig.title.text_color = text_color
    fig.title.text_font_size = '16px'
    fig.title.align = 'center'
    fig.grid.grid_line_color = None
    fig.axis.axis_line_color = None
    fig.axis.major_label_standoff = 0
    fig.background_fill_color = None
    fig.border_fill_color = None
    fig.background_fill_alpha= 0.0
    fig.border_fill_alpha = 0.0

    return fig

def create_crosstab_dfs(
        df: pd.DataFrame,
        filter_variables: list
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Creates the dataframes to be used to build the Crosstab plot.

    Parameters:
    -----------
    df: pd.DataFrame
        DataFrame containing the data.
    filter_variables: list
        List of variables to be used to filter the columns.

    Returns:
    --------
    pd.DataFrame
        DataFrame containing the data preprocessed to build the plot.
    """
    filtered_df = df[['gender', 'family_history_with_overweight', 'hypertension', 'heart_disease', 'diabetes', 'nobeyesdad', 'age_group']]
    grouped_df = filtered_df.groupby(['gender', 'family_history_with_overweight', 'hypertension', 'heart_disease', 'diabetes', 'nobeyesdad', 'age_group']).size().reset_index(name='counts')

    # Creates the dataframes for the Crosstab plot
    crosstab_df = pd.DataFrame()
    totals_df = pd.DataFrame()
    for filter_variable in filter_variables:
        # Filters the dataframe with the data to build the Crosstab plot using the
        sub_df = grouped_df[[filter_variable, 'nobeyesdad', 'counts']]

        # Creates the crosstab dataframe for the selected filter variable
        variable_crosstab = pd.crosstab(
            sub_df[filter_variable],
            sub_df['nobeyesdad'],
            values=sub_df['counts'],
            aggfunc='sum',
            normalize="index"
        )

        # Creates the totals dataframe for the selected filter variable
        totals = pd.crosstab(sub_df[filter_variable],
            sub_df['nobeyesdad'],
            values=sub_df['counts'],
            aggfunc='sum',
            margins=True,
            normalize="columns").All

        # Transforms the totals series into a dataframe
        totals = pd.DataFrame(totals)

        # Adds a column with the filter variable
        variable_crosstab['filter_variable'] = filter_variable
        totals['filter_variable'] = filter_variable

        # Sets a name for the index and columns
        variable_crosstab.index.name = 'Variable Category'
        variable_crosstab.columns.name = 'Obesity Category'
        totals.index.name = 'Variable Category'

        # Concatenate the dataframes
        crosstab_df = pd.concat([crosstab_df, variable_crosstab], axis=0)
        totals_df = pd.concat([totals_df, totals], axis=0)

    return crosstab_df, totals_df

def create_crosstab_plot(
        df: pd.DataFrame, 
        filter_variable: str, 
    ) -> figure:
    """
    Builds a crosstab plot for the selected filter variable.
    The plot is based on the example from the Bokeh website:
    https://docs.bokeh.org/en/latest/docs/examples/topics/hierarchical/crosstab.html

    Parameters:
    -----------
    df: pd.DataFrame
        DataFrame containing the data preprocessed to build the plot.
    filter_variable: str
        Variable to be used as a filter.

    Returns:
    --------
    figure
        Crosstab plot.
    """
    filter_variables = [
        'family_history_with_overweight',
        'hypertension',
        'heart_disease',
        'diabetes'
    ]

    # Builds the dataframe to be used to build the Crosstab plot
    crosstab_df, totals_df = create_crosstab_dfs(df, filter_variables)

    # Filters the dataframes with the data to build the Crosstab plot using the 
    # filter variable column equal to the selected variable
    filtered_crosstab_df = crosstab_df[crosstab_df['filter_variable'] == filter_variable]
    filtered_totals_df = totals_df[totals_df['filter_variable'] == filter_variable]

    # Drops the filter_variable columns and transposes the crosstab dataframe
    filtered_crosstab_df.drop(columns=['filter_variable'], inplace=True)
    filtered_totals_df.drop(columns=['filter_variable'], inplace=True)
    transposed_df = filtered_crosstab_df.T
    source = ColumnDataSource(transposed_df)

    # Defines the categories to be used in the plot
    variable_categories = transposed_df.columns.tolist()

    # Sets the obesity categories
    obesity_categories = transposed_df.index.tolist()

    # Creates the figure
    fig = figure(
        x_range=(-0.06, 1.03),
        y_range=variable_categories,
        width=width_crosstab,
        height=height_crosstab,
        tools=TOOLS.strip("hover"),
        title=f'Crosstab for {break_text(variables_dict[filter_variable], 200)}',
        toolbar_location='right',
        toolbar_sticky=False,
        x_axis_location=None,
        outline_line_color=None
    )
    
    # Sets the color mapper
    color_mapper = factor_cmap(
        'Obesity Category',
        palette=BuRd5,
        factors=obesity_categories
    )

    # List to store the hover tools
    hover_tools = []

    # Creates the rectangles for the plot
    for i, category in enumerate(variable_categories):
        # Calculates the cumulative sum of the category
        left, right = cumsum(category, include_zero=True), cumsum(category)

        # Calculates the position of the texts
        source.data[f'right_text_position_{category}'] = np.cumsum(source.data[category])

        # Calculates the positions of the bars by shifing them vertically
        # using the same value for each category
        shift_value = i * (1 + 0.3) - 0.1 * (1 - i) + 0.4
        vertical_position = [shift_value] * len(source.data[category])
        source.data[f"vertical_position_{category}"] = vertical_position

        # Creates the obesity categories and percentages text for the hover tool
        source.data[f"percentage_{category}"] = [f"{percentage * 100:.1f} %" for percentage in source.data[category]]

        # Creates the hover tool
        hover = HoverTool()
        hover.tooltips = [
            ("Variable category", f"{category}"),
            ("Obesity category", "@{Obesity Category}"),
            ("Percentage", f"@{category}{{0.0 %}}")]
        hover.point_policy = "follow_mouse"

        # Creates the bars
        horizontal_bar = fig.hbar(
            y=f"vertical_position_{category}",
            left=left,
            right=right,
            height=0.4,
            color=color_mapper,
            source=source
        )

        # Creates a logarithmic axis for the bars
        xaxis = LogAxis()
        xaxis.axis_line_alpha = 0
        fig.add_layout(xaxis, 'below')

        # Renders the hover tools and adds them to the list
        hover.renderers = [horizontal_bar]
        hover_tools.append(hover)

        # Creates the text for the bars with the obesity categories
        fig.text(
            x=f'right_text_position_{category}',
            y=f"vertical_position_{category}",
            text="Obesity Category",
            text_align='center',
            text_baseline='bottom',
            text_font_size='12px',
            text_color='black',
            angle=3*np.pi/2,
            source=source
        )

    # Adds the hover tools to the plot
    fig.add_tools(*hover_tools)

    # Creates a ColumnDataSource for the totals bars
    totals_source = ColumnDataSource(filtered_totals_df)

    # Adds the y coordinates and colors for the totals bars
    totals_source.data['y'] = [0.75, 1.25]

    # Adds the right and height coordinates for the totals bars
    totals_source.data['right'] = [0, 0]
    totals_source.data['height'] = [0.4, 0.4]

    # Adds the colors for the totals bars
    totals_source.data['color'] = ["#65aedd", "#65aedd"]

    # Creates the totals bars
    total_bars = fig.hbar(
        y='y',
        left='All',
        right='right',
        height='height',
        color='color',
        source=totals_source
    )

    # Creates a hover tool for the totals bars
    hover_totals = HoverTool()
    hover_totals.tooltips = [
            ("Variable category", "@{Variable Category}"),
            ("Percentage", "@All{0.0 %}")
        ]
    hover_totals.point_policy = "follow_mouse"
    hover_totals.renderers = [total_bars]
    fig.add_tools(hover_totals)

    # Creates a descriptive text for the bars
    fig.text(
        x=-0.03,
        y=[0.3, 0.75, 1.25, 1.7],
        text=["Parcial", "Total",
            "Total" , "Parcial"],
        text_align='center',
        text_baseline='bottom',
        text_font_size='14px',
        text_color='white',
        angle=3*np.pi/2,
    )

    fig.text(
        x=-0.06,
        y=[0.53, 1.475],
        text=["No", "Yes"],
        text_align='center',
        text_baseline='bottom',
        text_font_size='16px',
        text_color='white',
        angle=3*np.pi/2,
    )

    # Adds a line to separate the two main groups
    hline = Span(location=1, dimension='width', line_color='white', line_width=1)
    fig.renderers.extend([hline])

    # Defines additional options
    text_color = 'white'
    fig.toolbar.autohide = True
    fig.title.text_color = text_color
    fig.title.text_font_size = '16px'
    fig.title.align = 'center'
    fig.grid.grid_line_color = None
    fig.axis.axis_line_color = None
    fig.axis.major_label_standoff = 0
    fig.background_fill_color = None
    fig.border_fill_color = None
    fig.background_fill_alpha= 0.0
    fig.border_fill_alpha = 0.0
    fig.yaxis.fixed_location = 0
    fig.axis.major_tick_line_color = None
    fig.axis.major_label_text_color = None
    fig.axis.axis_line_color = "white"
    fig.axis.axis_line_width = 2

    return fig