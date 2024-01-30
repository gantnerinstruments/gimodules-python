'''
File: how_to_interact_with_Q_station.py
Author: aljo

Created on: 18. January 2024
Last changed: 23. January 2024

Description:
Tutorial Projekt made for Clients of Gantert Instruments 
'''

import os
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from datetime import timedelta
import datetime as dt 
import plotly.graph_objs as go


# local module
from gimodules.cloudconnect.cloud_request import CloudRequest
import gimodules.py_q_station_connect_cloud.py_q_station_connect_cloud as Qstation 

########################## constants & variables 
GI_LOGO = 'assets/gi-logo.png'
DOCS_URL = 'https://analytics.gi-cloud.io/docs/'

# Get a list of script names that start with the prefix "example_"
script_folder = 'gimodules/tutorial_examples/code_examples_from_benoit'
filtered_scripts = [script for script in os.listdir(script_folder) if script.startswith("example_")]



########################## Helper Functions

## cloud functions
def get_stream_metadata(url, user, pw,): 
    cloud = CloudRequest()
    cloud.login(url, user, pw,)
        
    streams_and_variables = {}
    for s in cloud.streams: 
        var_names = cloud.find_var(cloud.streams[s].name).keys()
        streams_and_variables[cloud.streams[s].name] = [v.split('__')[1] for v in var_names]
    return streams_and_variables, cloud.login_token



def get_data_from_cloud_datastream(token, stream, variable):
    cloud = CloudRequest()
    cloud.login_token = token
    data = cloud.get_data(stream, variable)
    return data

## local functions


def connect_to_q_station(controller_IP, dll_path):
    #Initialisation of a buffer connection
    conn=Qstation.ConnectGIns(dll_path)
    conn.bufferindex=int(0)
    conn.init_connection(str(controller_IP))
    c_name = conn.read_controller_name()
    c_serial_number = conn.read_serial_number()
    c_sample_rate = conn.read_sample_rate()
    c_channel_names = conn.read_channel_names()
    c_number_of_channels = conn.read_channel_count()
    return c_name, c_serial_number, c_sample_rate, c_channel_names, c_number_of_channels


def read_q_station_stream_buffer(controller_IP, dll_path): 
    conn=Qstation.ConnectGIns(dll_path)
    conn.bufferindex=int(0)
    conn.init_connection(str(controller_IP))
    c_channel_names = conn.read_channel_names()
    buffer = conn.yield_buffer()
    buffer_result = []
    stop_counter = 0
    
    
    for i in range(1, 9999999): 
        res = next(buffer)
        if len(res) != 0:
            buffer_result = res
            #print("break", buffer_result)
            break
        stop_counter += 1
        if stop_counter > 1000:
        
            #print("stop", buffer_result)
            break
    return buffer_result, c_channel_names


def create_q_station_table(buffer_data, c_channel_names): 
    channel_data = []
    if len(buffer_data) == 0: 
        channel_data = [{'Channel index': i, 'Channel name': c_channel_names[i], 'Channel value': None} for i in c_channel_names.keys()]
    else: 
        channel_data = [{'Channel index': i, 'Channel name': c_channel_names[i], 'Channel value': buffer_data[0][i]} for i in c_channel_names.keys()] 
    return channel_data
    

########################## Basic Components 
header = dbc.Row([
                dbc.Col([
                    html.Img(src=GI_LOGO, style={"height" : "50px"}),
                ]),
                dbc.Col([
                    html.H2("Hands on Python Tutorial"),
                    html.Span("Learn how to use Python to connect to your Q.Station and to the GI.Cloud."),
                    html.Br(),
                    html.Span("For more information visit the "), 
                    html.A("Gantner Docs", href=DOCS_URL, target="_blank", style={"color" : "#0053a5"})
                ]),
            ],justify="between", style={"padding" : "10px", "border-bottom" : "1px solid #d6d6d6"}, class_name="pb-4")


body = dbc.Row([
    dbc.Col([
        #dcc.Tabs(id="tabs-styled-with-inline", value='page_dash_cloud_example', vertical=True, children=[
        dcc.Tabs(id="tabs-styled-with-inline", value='page_connect_local_to_q_station', vertical=True, children=[
            dcc.Tab(label='How to use Cloud Analytics', value='page_dash_cloud_example', style={"border-top" : "0px solid"}),
            dcc.Tab(label='Connect to Q.Station via Cloud', value='page_connect_cloud_to_q_station'),
            dcc.Tab(label='Connect to Q.Station via LAN', value='page_connect_local_to_q_station'),
            dcc.Tab(label='How to create advanced Charts', value='page_advanced_code_preview'),
            dcc.Tab(label='More Code examples', value='page_code_preview')
        ])
    ], width=3),  
    dbc.Col(
        [
            html.H3("Welcome to the Gantner Docs"),
            html.P("Choose your first tutorial."),
        ],
        id='tabs-content-inline',
        width=9,  
        className="pt-4"
    )
], justify="center")


########################## Application Setup


external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Gothic+A1&display=swap',
     dbc.themes.BOOTSTRAP
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions=True
app.css.config.serve_locally = True
app.layout = dbc.Container([
   header,
   body,
   
], style={"margin" : "0", "padding" : "0", 'font-family': 'Gothic A1'})



########################## Callbacks
@app.callback(Output('tabs-content-inline', 'children'),
              Input('tabs-styled-with-inline', 'value'))
def render_content(tab):
    if tab == 'page_dash_cloud_example':
        return page_dash_cloud_example
    elif tab == 'page_connect_cloud_to_q_station':
        return page_connect_dash_to_cloud
    elif tab == 'page_connect_local_to_q_station':
        return page_connect_local_to_q_station
    elif tab == 'page_advanced_code_preview':
        return page_advanced_code_preview
    elif tab == 'page_code_preview':
        return page_code_preview



########################## Navigation Tabs Content
########################## page_dash_cloud_example
basic_dash_script = """
# Run this app with `python app.py` and

from dash import Dash, dcc, html

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Hello World")
])

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=8050) # You need to use the host 0.0.0.0 and the port 8050
"""

page_dash_cloud_example =  dbc.Row([
    html.H3("How to use Cloud Analytics"),
    html.P("The following steps will guide you through the process of creating a Cloud Analytics app."),
    html.P("1. Open the Jupyter Lab in your GI.Cloud."),
    html.Img(src='assets/select-jupyter-lab.png'),
    html.P("2. Create a new Python script."),
    html.Img(src='assets/add-script.png'),
    html.P("3. Copy the following code snippet into your script."),
    html.Div([
        dcc.Markdown(children=f"""```python{basic_dash_script}```""", ),
    ], className="border border-primary rounded p-3"), 
    html.P("4. Open a new terminal."),
    html.Img(src='assets/run-terminal.png'),
    html.P("5. Run the following command: python app.py"),
    html.Img(src='assets/run-app.png'),
    html.P("6. Now click on the analytics Tab to open the app in your browser."),
    html.Img(src='assets/hello-world.png'),
])



########################## page_dash_cloud_example

# Store cloud data 
# - streamnames 
# - variables 
gi_streams_and_variables = dcc.Store(id="gi-data", data=None)



# Store session tokens 
# - auth token
# - refresh token 
gi_cloud_token = dcc.Store(id='gi-token', data=None)



cloud_login_component = dbc.Row([
    html.H3("Login to your cloud account"),
    dbc.Label("Cloud URL", width=12),
    dbc.Col([
        dcc.Input(id="cloud-url", type="text", placeholder="wwww.my-gi-cloud.com"),
    ], width=12),
    dbc.Label("Username", width=12),
        dbc.Col([
            dcc.Input(id="cloud-username", type="text", placeholder="Username"),
        ], width=12),
    dbc.Label("Password", width=12),
    dbc.Col([
            dcc.Input(id="cloud-password", type="password"),
        ], width=12),
    dbc.Col([
        dbc.Button('Login', id='cloud-login-btn', n_clicks=0, style={"background-color" : "#0053a5"}, className="mt-3"),
    ] , width=12),            
], className="mb-4")

# component callback 
@app.callback(
        Output('gi-token', 'data'),
        Output('gi-data', 'data'),
        Output('cloud-datastream', 'options'),
        Output('cloud-datastream', 'value'),  
        Input('cloud-login-btn', 'n_clicks'),
        State('cloud-url', 'value'),
        State('cloud-username', 'value'),
        State('cloud-password', 'value')) 
def cloud_login_component_callback(n_clicks, url, user, pw):
    if n_clicks > 0:
        stream_and_variables, token = get_stream_metadata(url, user, pw)
        return token, stream_and_variables, list(stream_and_variables.keys()),  list(stream_and_variables.keys())[0]
    # default return
    return None, None, [], "no datastream available"

# Update Dropdown after selecting a stream
@app.callback(Output('cloud-datastream-variables', 'options'),
              Input('cloud-datastream', 'value'),
              State('gi-data', 'data'))
def update_datastream_variables(datastream, data):
    if datastream is None or data is None:
        return []
    return [{'label': var, 'value': var} for var in data[datastream]]


cloud_stream_data_component = dbc.Row([
    html.H3("Select your Q.Station datastream"),
    dbc.Label("Streamname", width=1),
    dbc.Col([
        dcc.Dropdown(id="cloud-datastream", placeholder="no datastream available"),
    ], width=12),
    dbc.Label("Stream variables", width=12),
    dbc.Col([
        dcc.Dropdown(id="cloud-datastream-variables", placeholder="no variables available"),
    ], width=12),
    dbc.Button('Display Data', id='cloud-display-data-btn', n_clicks=0, style={"background-color" : "#0053a5"}, className="mt-3")
], className="mb-4")


# component callback
@app.callback(Output('cloud-chart-container', 'children'),
                Input('cloud-display-data-btn', 'n_clicks'),
                State('cloud-datastream', 'value'),
                State('cloud-datastream-variables', 'value'),
                State('cloud-url', 'value'),
                State('cloud-username', 'value'),
                State('cloud-password', 'value'))
def create_chart_callback(n_clicks, datastream, variable, url, user, pw):
    if n_clicks > 0:
        if datastream is None: 
            return [html.P("No datastream selected. Please select a datastream.")]
        
        if variable is None:
            return [html.P("No variable selected. Please select a variable.")]
        
        if url is None:
            return [html.P("No cloud url provided. Please provide a cloud url.")]
        
        if user is None:
            return [html.P("No username provided. Please provide a username.")]
        
        if pw is None:
            return [html.P("No password provided. Please provide a password.")]
        
        # prepare data for request
        cloud = CloudRequest()
        cloud.login(url, user, pw)
        stream_id = cloud.streams[datastream].id
        var_index = cloud.stream_variabels[f"{datastream}__{variable}"].index

        # use the last timestamp as end date and the last timestamp minus one day as start date
        end_date = dt.datetime.utcfromtimestamp((float(cloud.streams[datastream].last_ts)/1000)).strftime('%Y-%m-%d %H:%M:%S')
        start_date = (dt.datetime.utcfromtimestamp(float(cloud.streams[datastream].last_ts) / 1000) - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

        # get data from cloud
        df = cloud.get_var_data(stream_id, [var_index], start_date, end_date, 'MINUTE').set_index('Time')
  
        return [dcc.Graph(
                id='line-chart',
                figure={
                    'data': [
                        go.Scatter(
                            x=df.index,
                            y=df[df.columns[0]],
                            mode='lines+markers',
                            name='Line Chart'
                        )
                    ],
                    'layout': go.Layout(
                        title='Line Chart',
                        xaxis={'title': 'Time'},
                        yaxis={'title': 'Values'}
                    )
                }
            )]
        
    return []



page_connect_dash_to_cloud = dbc.Row([
        # stores 
        gi_streams_and_variables,
        gi_cloud_token,
        # components
        cloud_login_component, 
        cloud_stream_data_component,
        html.Div(id="cloud-chart-container", children=[])
    ])



########################## page_connect_local_to_q_station
page_connect_local_to_q_station = dbc.Row([
        dbc.Row([
            html.H3("Connect to Q.Station via LAN"),
            html.P("For connection with the Q.Station via LAN, the Q.Station needs to be connected to the same network as your computer. You also need the dll File from GI to communicate with your Q.station"),
            html.P("You can download the dll file from the GI support website."),
            dbc.Row([
                    dbc.Label("Enter the full path to utility dll."),

                    dcc.Input(id="gins-utility", type="text", placeholder="C:\\Program Files\\Gantner Instruments\\GINS-Utility\\GINS-Utility.dll", value="C:\\Users\\aljo\\Downloads\\ginsapy-0.1.0\\ginsapy-0.1.0\\giutility\\giutility_x64.dll"),
    
                ], className="mb-3"),
        ]),

        dbc.Row([
            html.H3("Enter Q Station Parameters"),
            html.P("Enter the IP address of the Q Station controller.", className="m-0 p-0"),
            dbc.Form([
                dbc.Row([
                    dbc.Label("Q Station Controller IP", width=8),
                    dbc.Col([
                        dcc.Input(id="q-station-ip", type="text", placeholder="192.168.178.80", value="192.168.178.80"),
                    ], width=10)
                ], className="mb-3" ),
                # dbc.Row([
                #     dbc.Label("Q Station Channel Number", width=8),
                #     dbc.Col([
                #               dcc.Input(id="q_station_channel_nb", type="text", placeholder="8"),
                #     ], width=10)
                # ], className="mb-3"),
                # dbc.Row([
                #     dbc.Label("Q Station Buffer Index", width=8),
                #     dbc.Col([
                #         dcc.Input(id="q_station_buffer_index", type="text", placeholder="0"),
                #     ], width=10)
                # ], className="mb-3"),
                dbc.Button('Connect to Q.Station', id='connect-to-q-station', n_clicks=0, style={"background-color" : "#0053a5"}, className="mt-3"),
            ])
        ]),

        html.Div(id="q-station-connection", children=[]),
        ])

# component callback
@app.callback(Output('q-station-connection', 'children'),
              Input('connect-to-q-station', 'n_clicks'),
              State('q-station-ip', 'value'),
              State('gins-utility', 'value'))



def connect_to_q_station_callback(n_clicks, ip, dll_path):
    if n_clicks > 0:
        if ip is None: 
            return [html.P("No IP address provided. Please provide an IP address.")]
        
        if dll_path is None:
            return [html.P("No dll path provided. Please provide a dll path.")]
        
        # connect to Q.Station
        c_name, c_serial_number, c_sample_rate, c_channel_names, c_number_of_channels = connect_to_q_station(ip, os.path.abspath(dll_path))

        result = [
            html.P(f"Connected to Q.Station {c_name}."),
            html.P(f"Serial number: {c_serial_number}"),
            html.P(f"Sample rate: {c_sample_rate}"),
            html.P(f"Number of channels: {c_number_of_channels}")
        ]
        
        buffer_data, c_channel_names = read_q_station_stream_buffer(ip, os.path.abspath(dll_path))
        channel_data = create_q_station_table(buffer_data, c_channel_names)

        table = dash_table.DataTable(
            data=channel_data,
            columns=[{'name': col, 'id': col} for col in channel_data[0].keys()],
            style_table={'overflowX': 'auto', 'padding': '1em'},
            id = 'q-station-table',
        )
        result.append(table)
        update = dcc.Interval(id='graph-update', interval= 2000, n_intervals=0) #todo aljo change to 2000 
        result.append(update)
        
        return result
    return []


# component callback
@app.callback(Output('q-station-table', 'data'), 
            Input('graph-update', 'n_intervals'),
            State('q-station-ip', 'value'),
            State('gins-utility', 'value'))

def update_chart_callback(n_intervals, ip, dll_path):

    # connect to Q.Station
    buffer_data, c_channel_names = read_q_station_stream_buffer(ip, os.path.abspath(dll_path))
    channel_data = create_q_station_table(buffer_data, c_channel_names)
    return channel_data





########################## page_advanced_code_preview
example_chart_1 = """
import matplotlib.pyplot as plt
import seaborn as sns

# Set Seaborn style
sns.set_style("whitegrid")

# Adjust data by dividing by 400
adjusted_data = df['PRdc']
weights = adjusted_data.values

# Create initial plot with a larger figure size
fig, ax1 = plt.subplots(figsize=(15, 8))

# Histogram with sum of values per bin on the primary Y-axis (ax1)
ax1.hist(adjusted_data, weights=weights, bins=16, edgecolor='black', alpha=0.7, label='Sum per bin')
ax1.set_xlabel('PRdc')
ax1.set_ylabel('count', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.legend(loc='upper left')
#ax1.set_ylim([0, 4000])  # Setting y1-axis scaling from 0 to 10000


# Create secondary Y-axis (ax2)
ax2 = ax1.twinx()
# Cumulative distribution on the secondary Y-axis (ax2)
ax2.hist(adjusted_data, weights=weights, bins=16, edgecolor='black', alpha=0.7, cumulative=True, histtype='step', label='Cumulative sum', color='red')
ax2.set_ylabel('Cumulative Sum nPmpp-MID4-OTF21', color='red')
ax2.tick_params(axis='y', labelcolor='red')
ax2.legend(loc='upper right')

# Title for the plot
plt.title('Histogram and Cumulative Distribution with Adjusted Data')

# Display the plot
plt.show()

"""

example_chart_2 = """

import plotly.express as px

if 'Matrix' in choose_chart.value:
    fig = px.scatter_matrix(df,
        dimensions=[
            'Pdc', 'Idc', 'Vdc', 'nIdc_1', 'nIdc_2', 'nIdc_3',
       'nIdc_4', 'nIdc_5', 'nIdc_6'
        ],
        color=color_w.value,
        title="MIDx matrix plot",
        color_continuous_scale='Viridis',
        range_color=[0, 36],
        )

    fig.update_layout(
        dragmode='select',
        width=1200,
        height=1200,
        hovermode='closest',
    )
    fig.update_traces(diagonal_visible=False)
    fig.show()

"""


page_advanced_code_preview = dbc.Row([
    html.H3("Advanced Python Code Snippet Example"),

    html.Div([
        dcc.Markdown(children=f"""```python{example_chart_1}```""", ),
    ], className="border border-primary rounded p-3"), 
    html.Img(src='assets/example_chart_1.png'),
    
    html.Div([
        dcc.Markdown(children=f"""```python{example_chart_2}```""", ),
    ], className="border border-primary rounded p-3"), 
    html.Img(src='assets/example_chart_2.png'),
])



########################## page_code_preview
page_code_preview = dbc.Col([
        html.H3("Python Code Snippet Example"),
        html.P("Select a script to display its content.", className="m-0 p-0"),
        html.P("The content of the script will be displayed in a code block.", className="m-0 p-0"),
        html.P("You can copy the code and paste it in your own script.", className="m-0 p-0"),
        html.P("You can also run the script by clicking on the 'Run script' button.", className="m-0 p-0 mb-3"),
        dcc.Dropdown(
            id='script-dropdown',
            options=[
               {'label': script, 'value': script} for script in filtered_scripts
            ],
            value=None,  # Initially, no script selected
            placeholder="Select a script"
        ),
        html.Div([
            dcc.Markdown(id='output-markdown'),
        ], className="border border-primary rounded p-3")#, 
        #dbc.Button('Run script', n_clicks=0, style={"background-color" : "#0053a5"}, className="mt-3"),
    ])


# component callback

@app.callback(
    Output('output-markdown', 'children'),
    [Input('script-dropdown', 'value')]
)
def update_output(selected_script):
    if selected_script is None:
        return "Please select a script."

    script_path = os.path.join(script_folder, selected_script)
    
    try:
        with open(script_path, 'r') as file:
            script_content = file.read()
        return f'''```python{script_content}```'''	
    except FileNotFoundError:
        return f"Script '{selected_script}' not found."



###########################Server 
def run():
    app.run_server(debug=False)
    #app.run_server(host="0.0.0.0", port=8050) # You need to use the host 0.0.0.0 and the port 8050