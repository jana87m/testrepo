from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px


spacex_df = pd.read_csv(
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
)

app = Dash(__name__)

launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]

min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

app.layout = html.Div([
    html.H1("SpaceX Launch Dashboard"),

    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    dcc.Graph(id='success-pie-chart'),

    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        value=[min_payload, max_payload],
        marks={i: str(i) for i in range(0, 10001, 1000)}
    ),

    dcc.Graph(id='success-payload-scatter-chart')
])

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
    Input(component_id='payload-slider', component_property='value')
)
def update_charts(entered_site, payload_range):  # <- FIXED: now takes 2 arguments
    if entered_site == 'ALL':
        pie_fig = px.pie(
            spacex_df, 
            names='Launch Site', 
            values='class',  # class = 1 for success, so sum gives number of successes
            title='Total Successful Launches by Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_fail_counts = filtered_df['class'].value_counts().reset_index()
        success_fail_counts.columns = ['class', 'count']
        success_fail_counts['class'] = success_fail_counts['class'].map({1: 'Success', 0: 'Failure'})
        pie_fig = px.pie(
            success_fail_counts,
            names='class',
            values='count',
            title=f'Success vs Failure for site {entered_site}'
        )

  
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site == 'ALL':
        scatter_fig = px.scatter(
            filtered_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title='Payload vs. Outcome for All Sites'
        )
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        scatter_fig = px.scatter(
            site_df, x='Payload Mass (kg)', y='class',
            color='Booster Version Category',
            title=f'Payload vs. Outcome for site {entered_site}'
        )

    return scatter_fig, pie_fig  


if __name__ == '__main__':
    app.run(debug=True, port=8051)
