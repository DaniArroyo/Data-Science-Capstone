# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),

                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                {'label': 'All Sites', 'value': 'AllSites'},                                                 
                                                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                             ],
                                             value='AllSites', 
                                             placeholder="Please select a launch site here.",
                                             searchable=True,
                                ),
                                html.Br(),

                                html.Div(dcc.Graph(id='success-pie-chart')),                               
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                
                                dcc.RangeSlider(id='payload-slider',
                                min=0, max=10000, step=1000,
                                value=[min_payload, max_payload],
                                marks={
                                    0: "0 kg",
                                    2500: "2500 kg",
                                    5000: "5000 kg",
                                    7500: "7500 kg",
                                    10000: "10000 kg",
                                    },
                                ),

                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])



@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value"),
) 
def render_pie_chart(site_selection):
    if site_selection == 'AllSites':
        df_success = spacex_df[(spacex_df['class'] == 1)]
        plot_df = df_success.groupby(['Launch Site']).size().reset_index()
        plot_df = plot_df.rename(columns={0:'count'})
        fig = px.pie(plot_df, names="Launch Site", values="count")
        fig.update_layout(title="Total Succesful Launches by Site")
        return fig

    else: 
        new_df = spacex_df.loc[spacex_df["Launch Site"] == site_selection]
        fig = px.pie(new_df, names="class")
        fig.update_layout(title=f"Total Succesful Launches from Site: {site_selection}")
        return fig
    
    

@app.callback(
Output("success-payload-scatter-chart", "figure"),
[Input("site-dropdown", "value"), 
Input("payload-slider", "value")]
)
def render_scatter_plot(site_selection, payload_range):

    range_df = spacex_df.loc[
        (spacex_df["Payload Mass (kg)"] > payload_range[0]) & 
        (spacex_df["Payload Mass (kg)"] < payload_range[1])
    ]

    if site_selection == 'AllSites':
        fig = px.scatter(range_df, x="Payload Mass (kg)", y="class", color="Booster Version Category")
        fig.update_layout(title="Correlation Between Payload and Succes for All Launch Sites")
        return fig

    else:
        scatter_df = range_df.loc[range_df["Launch Site"] == site_selection]
        fig = px.scatter(scatter_df, x="Payload Mass (kg)", y="class", color="Booster Version Category")
        fig.update_layout(title=f"Correlation Between Payload and Succes from Launch Site: {site_selection}")
        return fig


# Run the app
if __name__ == '__main__':
    app.run_server()