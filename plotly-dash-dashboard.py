# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

launch_sites = spacex_df['Launch Site'].unique()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]


# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', 
                                            options=dropdown_options,
                                            value='ALL',
                                            placeholder='Select a Launch Site here',
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)

                                dcc.RangeSlider(id='payload-slider',
                                                min=0,
                                                max=10000,
                                                step=1000,
                                                marks={i: str(i) for i in range(0, 10001, 1000)},
                                                value=[min_payload, max_payload]
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        total_success = spacex_df['class'].sum()
        total_failures = len(spacex_df) - total_success

        fig = px.pie(
            names=['Success', 'Failure'],
            values=[total_success, total_failures],
            title='Total Success Launches'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        failure_count = filtered_df[filtered_df['class'] == 0].shape[0]

        fig = px.pie(
            names=['Success', 'Failure'],
            values=[success_count, failure_count],
            title=f'Success/Failure Launches for {entered_site}'
        )

    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, selected_payload_range):
    # Filter DataFrame based on selected launch site
    if selected_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]

    # Convert payload_mass_kg to numeric type (if not already)
    filtered_df['payload_mass_kg'] = pd.to_numeric(filtered_df['Payload Mass (kg)'], errors='coerce')

    # Filter DataFrame based on selected payload range
    filtered_df = filtered_df[
        (filtered_df['payload_mass_kg'] >= selected_payload_range[0]) &
        (filtered_df['payload_mass_kg'] <= selected_payload_range[1])
    ]

    # Create scatter plot
    fig = px.scatter(filtered_df,
                     x='payload_mass_kg',
                     y='class',
                     color='Booster Version Category',
                     title='Payload vs. Launch Outcome',
                     labels={'payload_mass_kg': 'Payload Mass (kg)', 'class': 'Launch Outcome'},
                     category_orders={'class': [0, 1]}
                     )

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
