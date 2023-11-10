import pathlib
import pandas as pd
import dash_daq as daq
import math

import dash
from dash import dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO
import dash_cytoscape as cyto

from utilities.ont import get_cytoscape_elements
from utilities.ont import get_sparql_query_results

# --------------------------------------------------
# ontology configuration details
#
# location of directory 'data'
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

# ontology names
ontologies_df = pd.read_csv(DATA_PATH.joinpath("ontologies.csv"))
ontology_names_as_list = ontologies_df["Name"].unique()

# ontology specific sparql queries
queries_list = pd.DataFrame()
df_query_results = ontologies_df.copy()

# ontology specific cytoscape data elements
ontology_view_elements = []

# ticker names
tickers_as_list = ['BTC', 'ETH', 'BNB', 'XRP']

# --------------------------------------------------
# bootstrap formatting
#
# format colors: primary, secondary, success, info, warning, danger, light, dark, link
# p-2 mb-2 text-left
title_format = "bg-light text-primary text-left"
footer_format = "bg-light text-primary text-left"
accordian_format = "bg-dark text-secondary text-center"
accordian_item_format = "bg-light text-link text-center"
textarea_format = "bg-light text-link text-left"
tab_active_format = "bg-dark text-secondary text-center"
tab_inactive_format = "bg-light text-primary text-center"
view_control_panel_format = "bg-light text-primary text-center"

# --------------------------------------------------
# instantiate the dash server
#
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SKETCHY, dbc_css])
app.config.suppress_callback_exceptions = True

####################################################################################################################
# top container
#
top_container = \
    dbc.Row(
        [
            dbc.Col(
                [
                    # html.Img(src='/assets/brandeis-logo.png', style={'height': '15%'}),
                ],
                width=2,
            ),
            dbc.Col(
                [

                    html.H1("Semantic Web Dashboard", style={"font-weight": "bold"}, className=title_format),
                ],
                width=10,
            ),
        ]
    )

####################################################################################################################
# bottom container
#
bottom_container = \
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Img(src='/assets/brandeis-logo.png', style={'height': '15%'}),
                ],
                width=2,
            ),
            dbc.Col(
                [

                    html.H6("Developed by Brandeis University International Business School",
                            className=footer_format)
                ],
                width=10,
            ),
        ]
    )

####################################################################################################################
# sidebar container
#
sidebar_container = html.Div(
    [
        dbc.Accordion(
            [
                dbc.AccordionItem(
                    [
                        html.P("Select Ontology",
                               className=accordian_item_format,
                               style={"font-weight": "bold"}),
                        dcc.Dropdown(
                            id="ontology-select",
                            placeholder="Select",
                            options=[{"label": i, "value": i} for i in ontology_names_as_list],
                        ),
                        html.Br(),
                        html.P("Description",
                               className=accordian_item_format,
                               style={"text-decoration": "underline", "font-weight": "bold"}),
                        dcc.Markdown(
                            id="ontology-description",
                            children=[],
                            className=accordian_item_format
                        ),
                        html.Br(),
                        html.P("Endpoint",
                               className=accordian_item_format,
                               style={"text-decoration": "underline", "font-weight": "bold"}),
                        dcc.Markdown(
                            id="ontology-endpoint",
                            children=[],
                            className=accordian_item_format
                        ),
                        html.Br(),
                        html.P("Select SPARQL Query",
                               className=accordian_item_format,
                               style={"font-weight": "bold"}),
                        dcc.Dropdown(
                            id="sparql-query-select",
                            disabled=True,
                            options=[{"label": i, "value": i} for i in ontology_names_as_list],
                        ),
                        html.Br(),
                        html.Div(
                            id="submit-button-div",
                            children=[
                                dbc.Button(
                                    id="submit-button",
                                    children="Submit SPARQL Query",
                                    n_clicks=0,
                                    disabled=True,
                                    style={'width': '100%'},
                                ),
                            ],
                        ),
                    ],
                    title="Ontology",
                    className=accordian_item_format,
                ),
                dbc.AccordionItem(
                    [
                        ThemeChangerAIO(aio_id="theme"),
                    ],
                    title="Theme",
                    className=accordian_item_format
                ),
            ],
            start_collapsed=False, always_open=True, flush=True,
            className=accordian_format
        ),
    ],
)

####################################################################################################################
# body container
# view tab
#
body_container_view = \
    dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            html.Br(),
                            html.P("Control Panel", className=accordian_item_format),
                            dcc.Dropdown(
                                id='ontology-view-update-layout',
                                value='grid',
                                clearable=False,
                                options=[
                                    {'label': name.capitalize(), 'value': name}
                                    for name in ['random', 'grid', 'circle', 'concentric', 'breadthfirst']
                                ],
                            ),
                        ],
                    ),
                ],
                className=view_control_panel_format,
                width=1,
            ),
            dbc.Col(
                [
                    cyto.Cytoscape(
                        id='ontology-view',
                        elements=ontology_view_elements,
                        style={'width': '100%', 'height': '1000px'},
                    )
                ],
                width=10,
            ),
        ]
    )


@app.callback(
    Output('ontology-view', 'layout'),
    Input('ontology-view-update-layout', 'value'))
def update_layout(layout):
    return {'name': layout}


####################################################################################################################
# body container
# query tab
#
body_container_query = \
    html.Div(
        [
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [                              
                            dbc.Row(
                                [
                                    dbc.Col(
                                                [
                                                    html.P("Select Cryptocurrency", className=accordian_item_format, style={"font-weight": "bold"}),
                                                    dcc.Dropdown(
                                                        id='crypto-select-dropdown',
                                                        options=[{'label': crypto, 'value': crypto} for crypto in tickers_as_list],
                                                        value=tickers_as_list,  # Default to all selected, or choose a subset
                                                        multi=True  # Allows selecting multiple cryptocurrencies
                                                    ),
                                                ],
                                                width=4,  # Adjust width as needed
                                            )
                                ]
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.P(" ",
                                                   className=accordian_item_format,
                                                   ),
                                        ],
                                        width=12,
                                    ),
                                ]
                            ),
                            dbc.Row(
                                [   
                                    dbc.Col(
                                        [
                                            html.P("Date Range",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}
                                                   ),
                                            dcc.DatePickerRange(
                                                id='date-range-picker-select',
                                                clearable=True,
                                                disabled=True,
                                            ),
                                        ],
                                        width=2,
                                        style={
                                            'background-color': 'var(--bs-light)',
                                            'border-style': 'solid',
                                            'border-width': 'thin'
                                        }
                                    ),
                                    dbc.Col(
                                        [
                                            html.P("Precision",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}
                                                   ),
                                            daq.NumericInput(
                                                id='precision-select',
                                                label="Number of Decimal Points",
                                                labelPosition='bottom',
                                                value=2,
                                                min=0,
                                                max=6,
                                                disabled=True
                                            ),
                                        ],
                                        width=2,
                                        style={
                                            'background-color': 'var(--bs-light)',
                                            'border-style': 'solid',
                                            'border-width': 'thin'
                                        }
                                    ),
                                    dbc.Col(
                                        [
                                            html.P("Select Graph Type",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}),
                                            dcc.Dropdown(
                                                id="graph-type-dropdown",
                                                options=[
                                                    {'label': 'Line', 'value': 'line'},
                                                    {'label': 'Bar', 'value': 'bar'},
                                                    {'label': 'Scatter', 'value': 'scatter'},
                                                    {'label': 'Histogram', 'value': 'histogram'}
                                                ],
                                                #disabled=True,
                                                value='Select',
                                                clearable=False
                                            )
                                        ],
                                        width=2,
                                        style={
                                            'background-color': 'var(--bs-light)',
                                            'border-style': 'solid',
                                            'border-width': 'thin'
                                        }
                                    )
                                ],
                            )
                        ],
                        title="Parameters",
                    ),
                    dbc.AccordionItem(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.P("Text",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}
                                                   ),
                                            dcc.Textarea(
                                                id='sparql-query-text',
                                                value='',
                                                cols='4',
                                                disabled=True,
                                                style={'width': '100%', 'height': 200},
                                                className=textarea_format
                                            ),
                                        ],
                                        width=6,
                                    ),
                                    dbc.Col(
                                        [
                                            html.P("Template",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}
                                                   ),
                                            dcc.Textarea(
                                                id='sparql-query-template-text',
                                                value='',
                                                cols='4',
                                                disabled=True,
                                                style={'width': '100%', 'height': 200},
                                                className=textarea_format
                                            ),
                                        ],
                                        width=6,
                                    ),
                                ],
                            )

                        ],
                        title="Query",
                    ),
                    dbc.AccordionItem(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        [
                                            html.P("Chart",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}
                                                   ),
                                            dcc.Graph(
                                                id="query-results-chart"
                                            )
                                        ],
                                        width=6,
                                    ),
                                    dbc.Col(
                                        [
                                            html.P("Table",
                                                   className=accordian_item_format,
                                                   style={"font-weight": "bold"}
                                                   ),
                                            dash_table.DataTable(
                                                id='query-results-table',
                                                data=df_query_results.to_dict('records'),
                                                columns=[{'id': c, 'name': c} for c in ontologies_df.columns],

                                                page_current=0,
                                                page_size=25,
                                                fixed_rows={'headers': True},

                                                style_cell={'textAlign': 'left'},
                                                style_as_list_view=True,

                                                row_deletable=False,
                                                editable=False,
                                                filter_action="native",
                                                sort_action="native",
                                                style_table={"overflowX": "auto", 'overflowY': 'auto'},
                                                export_format="csv",
                                            )
                                        ],
                                        width=6,
                                    ),
                                ],
                            )
                        ],
                        title="Query Results",
                    ),

                ],
                start_collapsed=False, always_open=True, flush=True,
            ),
        ],
    )

####################################################################################################################
# body container
#
tab_view = dbc.Tab(
    body_container_view, label="View",
    label_class_name=tab_inactive_format,
    active_label_class_name=tab_active_format,
)
tab_query = dbc.Tab(
    body_container_query, label="Query",
    label_class_name=tab_inactive_format,
    active_label_class_name=tab_active_format,
)
body_container = dbc.Card(
    dbc.Tabs([tab_query, tab_view])
)

####################################################################################################################
# layout
#
app.layout = dbc.Container(
    [
        top_container,
        dbc.Row(
            [
                dbc.Col(
                    [
                        sidebar_container,
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        body_container,
                    ],
                    width=10,
                ),
            ]
        ),
        bottom_container,
    ],
    fluid=True,
)


####################################################################################################################
# callbacks
#
@app.callback(
    Output("ontology-description", "children"),
    Output("ontology-endpoint", "children"),
    Output("sparql-query-select", "options"),
    Output("sparql-query-select", "disabled"),
    [Input("ontology-select", "value")]
)
def ontology_select_dropdown_selected(ontology_selected):
    if ontology_selected is None:
        return '', '', [{"label": i, "value": i} for i in ontology_names_as_list], True

    # get attributes regarding the selected ontology
    df = ontologies_df.query(f'Name == "{ontology_selected}"')
    ontology_description = df['Description'].unique()[0]
    ontology_endpoint = df['Endpoint'].unique()[0]
    sparql_query_file = df['Sparql'].unique()[0]
    sparql_query_df = pd.read_csv(DATA_PATH.joinpath(sparql_query_file))
    query_name_list = sparql_query_df['Name'].unique()
    sparql_query_options = []
    for q in query_name_list:
        sparql_query_options.append({'label': q, 'value': q})

    return ontology_description, ontology_endpoint, sparql_query_options, False


@app.callback(
    Output("sparql-query-template-text", "value"),
    Output("sparql-query-template-text", "disabled"),
    Output("submit-button", "disabled"),
    Output("date-range-picker-select", "disabled"),
    Output("precision-select", "disabled"),
    [Input("sparql-query-select", "value")],
    [State("ontology-select", "value")]
)
def sparql_query_select_dropdown_selected(query_selected, ontology_selected):
    if ontology_selected is None or query_selected is None:
        return ('', True, True,
                True,
                True,
                )

    df = ontologies_df.query(f'Name == "{ontology_selected}"')
    sparql_query_file = df['Sparql'].unique()[0]
    sparql_query_df = pd.read_csv(DATA_PATH.joinpath(sparql_query_file))
    sparql_query_df.query(f'Name == "{query_selected}"', inplace=True)
    sparql_query_template = sparql_query_df['Sparql'].unique()[0]

    # determine which of the parameters control are needed for this query

    return (sparql_query_template, False, False,
            False,
            False)


@app.callback(
    Output("sparql-query-text", "value"),
    Output("sparql-query-text", "disabled"),
    Output("query-results-table", "data"),
    Output("query-results-table", "columns"),
    Output("ontology-view", "elements"),
    Output("query-results-chart", "figure"),
    [Input("submit-button", "n_clicks"), 
     Input("graph-type-dropdown", "value"),
     Input("crypto-select-dropdown", "value")],
    [State("ontology-endpoint", "children"),
     State("sparql-query-template-text", "value"),
     State("date-range-picker-select", "start_date"),
     State("date-range-picker-select", "end_date"),
     State("precision-select", "value")
     ]
)
def submit_button_selected(n_clicks, graph_type, selected_cryptos, ontology_endpoint, sparql_query_template,
                           start_date, end_date, precision):
    import plotly.express as px
    figure = px.line(x=['a', 'b', 'c', 'd'], y=[1, 2, 2, 1], title='placeholder figure')

    if n_clicks == 0 or ontology_endpoint is None or sparql_query_template is None:
        data = ontologies_df.to_dict('records')
        columns = [{'id': c, 'name': c} for c in ontologies_df.columns]
        return '', True, data, columns, ontology_view_elements, figure

    sparql_query_text = sparql_query_template

    # replace according to meta tags
    
    start_tag, end_tag = "<<", ">>"
    start_index = 0
    while True:
        idx_1 = sparql_query_template.find(start_tag, start_index)
        if idx_1 == -1:
            break
        idx_2 = sparql_query_template.find(end_tag, start_index + len(start_tag))
        if idx_2 == -1:
            break
        tag = sparql_query_template[idx_1 + len(start_tag): idx_2]
        name_value = tag.split(':')

        if name_value[1].strip() == 'start_date':
            sparql_query_text = sparql_query_text.replace(name_value[0], start_date)
        elif name_value[1].strip() == 'end_date':
            sparql_query_text = sparql_query_text.replace(name_value[0], end_date)
        elif name_value[1].strip() == 'precision':
            sparql_query_text = sparql_query_text.replace('precision', str(math.pow(10, precision)))
        start_index = idx_2
        

    results_table, results_columns, results_df = get_sparql_query_results(ontology_endpoint, sparql_query_text)

    filtered_columns = set(['date'])
    filtered_columns.update(col for col in results_df.columns if any(crypto in col for crypto in selected_cryptos))

    # Convert the set back to a list and create the filtered DataFrame
    filtered_df = results_df[list(filtered_columns)].copy()

    for col in filtered_df.columns:
        if col == 'date':
            continue
        ma_col_name = col + '_20d_ma'
        diff_col_name = col + '_diff'
        filtered_df.loc[:, ma_col_name] = filtered_df[col].rolling(window=20).mean()
        filtered_df.loc[:, diff_col_name] = filtered_df[col].astype(float) - filtered_df[ma_col_name].astype(float)

    data = []
    for col in filtered_df.columns:
        if col == 'date':
            continue
        
        # Plot for daily price
        if '_20d_ma' not in col and '_diff' not in col:
            daily_price_trace = dict(
                type=graph_type,  # Assuming you want a line plot for daily prices
                x=filtered_df['date'],
                y=filtered_df[col],
                name=col,
            )
            data.append(daily_price_trace)
        
        # Corresponding 20-day moving average plot
        if '_20d_ma' in col:
            moving_avg_trace = dict(
                type="line",  # Line plot for moving averages
                x=filtered_df['date'],
                y=filtered_df[col],
                name=col,
                #line=dict(dash='dash')  # Dashed line for the moving average
            )
            data.append(moving_avg_trace)

        # Corresponding difference plot
        if '_diff' in col:
            #colors = ['green' if diff>0 else 'red' for diff in filtered_df[col]]
            diff_trace = dict(
                type="bar",  # Bar plot for the difference
                x=filtered_df['date'],
                y=filtered_df[col],
                name=col,
            )
            data.append(diff_trace)


    layout = {"title": "Results", "dragmode": "select", "showlegend": True, "autosize": True}
    figure = dict(data=data, layout=layout)

    cytoscape_elements = get_cytoscape_elements(ontology_endpoint)

    return sparql_query_text, False, results_table, results_columns, cytoscape_elements, figure


##############################################
# Run the server
#
if __name__ == "__main__":
    app.run_server(debug=True)
