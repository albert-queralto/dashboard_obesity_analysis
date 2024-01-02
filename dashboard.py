# The implementation of the dashboard is based on the following example:
# https://towardsdatascience.com/https-medium-com-radecicdario-next-level-data-visualization-dashboard-app-with-bokeh-flask-c588c9398f98
import pandas as pd
from flask import Flask, render_template, request
from bokeh.embed import components
from plots_index import create_heatmap_fig, create_bar_plot, create_line_plot, create_pie_chart_plot
from plots_page2 import create_donut_chart_plot
from plots_page3 import create_sankey_plot, create_crosstab_plot
from typing import Any

# Initialize the Flask application
app = Flask(__name__)

# Load the data
df = pd.read_parquet('final_dataset.parquet')

def update_plots_index(
        df: pd.DataFrame,
        filter_variable: str,
        obesity_category: str
    ) -> tuple:
    """
    Update the plots for the index page based on the selected filter variable
    and obesity category.

    Parameters:
    -----------
    df: pd.DataFrame
        DataFrame containing the data.
    filter_variable: str
        Variable to be used as a filter.
    obesity_category: str
        Obesity category to be used as a filter.

    Returns:
    --------
    tuple
        Tuple containing the heatmap, bar plot, line plot and pie chart.
    """
    return (
        create_heatmap_fig(df, filter_variable, obesity_category),
        create_bar_plot(df, filter_variable, obesity_category),
        create_line_plot(df, filter_variable),
        create_pie_chart_plot(df, filter_variable)
    )

def update_plots_page2(
        df: pd.DataFrame,
        filter_variable: str,
        binary_variable: str
    ) -> Any:
    """
    Update the plots for the page 2 based on the selected filter variable
    and binary variable.

    Parameters:
    -----------
    df: pd.DataFrame
        DataFrame containing the data.
    filter_variable: str
        Variable to be used as a filter.
    binary_variable: str
        Binary variable to be used as a filter.

    Returns:
    --------
    Any
        The donut chart.
    """
    return create_donut_chart_plot(df, filter_variable, binary_variable)

def update_plots_page3(
        df: pd.DataFrame,
        filter_variable: str
    ) -> Any:
    """
    Update the plots for the page 3 based on the filter_variable.

    Parameters:
    -----------
    df: pd.DataFrame
        DataFrame containing the data.
    filter_variable: str
        Variable to be used as a filter.

    Returns:
    --------
    Any
    """
    return (create_sankey_plot(df, filter_variable),
            create_crosstab_plot(df, filter_variable))


@app.route('/', methods=['GET', 'POST'])
def index() -> Any:
    """
    Index page of the dashboard.
    
    Returns:
    --------
    Any
        HTML template.
    """
    # Gets the selected variable from the dropdown menus in the index page
    selected_variable = request.form.get('dropdown-variable', 'ncp')
    selected_obesity = request.form.get('dropdown-obesity', 'Insufficient Weight')
    
    # Updates the plots based on the selected variable and obesity category
    plot_heatmap, plot_barplot, plot_line, plot_pie = update_plots_index(
        df=df,
        filter_variable=selected_variable, 
        obesity_category=selected_obesity)
    
    # Gets the script and div components of the plots
    script_heatmap, div_heatmap = components(plot_heatmap)
    script_barplot, div_barplot = components(plot_barplot)
    script_lineplot, div_lineplot = components(plot_line)
    script_pieplot, div_pieplot = components(plot_pie)

    # Renders the template
    return render_template(
        'index.html',
        script_heatmap=script_heatmap,
        div_heatmap=div_heatmap,
        script_barplot=script_barplot,
        div_barplot=div_barplot,
        script_lineplot=script_lineplot,
        div_lineplot=div_lineplot,
        script_pieplot=script_pieplot,
        div_pieplot=div_pieplot,
        selected_variable=selected_variable,
        selected_obesity=selected_obesity
    )

@app.route('/page2.html', methods=['GET', 'POST'])
def page2() -> Any:
    """
    Page 2 of the dashboard.
    
    Returns:
    --------
    Any
        HTML template.
    """
    # Gets the selected categorical and binary variables from the dropdown menus
    # in page 2
    selected_categorical = request.form.get('dropdown-categorical', 'mtrans')
    selected_binary = request.form.get('dropdown-binary', 'gender')
    
    # Updates the plots based on the selected categorical and binary variables
    plot_donut = update_plots_page2(
        df=df,
        filter_variable=selected_categorical, 
        binary_variable=selected_binary)
    
    # Gets the script and div components of the plots
    script_donut, div_donut = components(plot_donut)

    # Renders the template
    return render_template(
        'page2.html',
        script_donut=script_donut,
        div_donut=div_donut,
        selected_categorical=selected_categorical,
        selected_binary=selected_binary
    )

@app.route('/page3.html', methods=['GET', 'POST'])
def page3() -> Any:
    """
    Page 3 of the dashboard.
    
    Returns:
    --------
    Any
        HTML template.
    """
    # Gets the selected variable from the dropdown menu in page 3
    selected_variable = request.form.get('dropdown-variable', 'hypertension')
    
    # Updates the plots based on the selected variable
    plot_sankey, plot_crosstab = update_plots_page3(
        df=df,
        filter_variable=selected_variable)

    # Gets the script and div components of the plots
    script_sankey, div_sankey = components(plot_sankey)
    script_crosstab, div_crosstab = components(plot_crosstab)

    # Renders the template
    return render_template(
        'page3.html',
        script_sankey=script_sankey,
        div_sankey=div_sankey,
        script_crosstab=script_crosstab,
        div_crosstab=div_crosstab,
        selected_variable=selected_variable
    )


if __name__ == '__main__':
    app.run(port=5000, debug=True)