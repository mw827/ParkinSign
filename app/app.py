import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pickle
import matplotlib.pyplot as plt
from prep_input import preprocess,get_combined,get_vel,get_mean_var

import pandas as pd
import plotly.graph_objs as go

# Step 1. Launch the application
app = dash.Dash(__name__)

server=app.server

# Step 2. Import the dataset
filepath = 'data/forapp/C_001.txt'
data=preprocess(filepath)
# print(data.head())
features=pd.read_csv('data/processed/feature_name.csv')
df_combined=get_combined(data)
df_combined=get_vel(df_combined)
df_combined=get_mean_var(df_combined)
df=df_combined[features.columns]
# dropdown options
# features = st.columns[1:-1]
# patient=[i for i in range(1, 10)]
opts_1 = [{'label' : "Patient {}".format(i), 'value' : "C_00{}".format(i)} for i in range(1,16)]
opts_2= [{'label' : "Patient {}".format(i+15), 'value' : "H-00{}".format(i)} for i in range(1,58)]
opts=opts_1+opts_2
# print(opts)
# range slider options
# st['Date'] = pd.to_datetime(st.Date)
# dates = ['2015-02-17', '2015-05-17', '2015-08-17', '2015-11-17',
#          '2016-02-17', '2016-05-17', '2016-08-17', '2016-11-17', '2017-02-17']

static=data[data['TestID'] == 0]
dynamic=data[data['TestID']==1]
# Step 3. Create a plotly figure
trace_1 = go.Scatter(x = static.X, y = static.Y,
                    name = 'static',
                    line = dict(width = 2,
                                color = 'rgb(229, 151, 50)'))

trace_2 = go.Scatter(x = dynamic.X, y = dynamic.Y,
                        name = 'dynamic',
                        line = dict(width = 2,
                                    color = 'rgb(106, 181, 135)'))
# fig = go.Figure(data = [trace_1,trace_2], layout = layout)
layout = go.Layout(title = 'Writting Patterns Plot',autosize=False, 
    xaxis=go.layout.XAxis(
        title=go.layout.xaxis.Title(
            text='X',
            font=dict(
                # family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    ),
        yaxis=go.layout.YAxis(
        title=go.layout.yaxis.Title(
            text='Y',
            font=dict(
                # family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    ),
    width=500, height=500,
    margin=go.layout.Margin(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4
    ),
                   hovermode = 'closest')
fig = go.Figure(data = [trace_1,trace_2], layout = layout)

modelname = 'models/LR_with_top_features.pkl'
loaded_model = pickle.load(open(modelname, 'rb'))
result = round(loaded_model.predict_proba(df)[0,1],2)
if "forapp/C" in filepath:
    dia='Healthy'
else: 
    dia='Parkinson'

# Step 4. Create a Dash layout
app.layout = html.Div([
                # a header and a paragraph
                html.Div([
                    html.H1("Welcome to ParkinSign system!"),
                    html.P("This is the first easy step to get early diagnosis of Parkinson")
                         ],
                     style = {'padding' : '50px' ,
                              'backgroundColor' : '#3aaab2'}),
                html.Div([
                    html.P([
                    html.Label("Choose a person"),
                    dcc.Dropdown(id = 'opt', options = opts,
                                value = 'C_001')
                        ], style = {'width': '400px',
                                    'fontSize' : '20px',
                                    'padding-left' : '100px',
                                    'display': 'inline-block'})
                ]),

                html.Div("This person is classified as: {0}".format(dia),
                id = 'diag',
                style = {'fontSize' : '30px','padding-left' : '100px'}
                # style = {'padding' : '50px'}
                ),
                
                html.Div("The probability of this person having Parkinson's disease is: {0}".format(result),
                id = 'prob',
                style = {'fontSize' : '30px','padding-left' : '100px'}
                # style = {'padding' : '50px'}
                ),
                # adding a plot
                dcc.Graph(id = 'plot', figure = fig,style = {'padding-left':'100px'}),
                # dropdown

                      ])


# Step 5. Add callback functions
@app.callback(Output('plot', 'figure'),
             [Input('opt', 'value')])
def update_figure(input):
    filepath = 'data/forapp/'+input+'.txt'
    # print(filepath)
    data=preprocess(filepath)
    # print(data.head())
    df_combined=get_combined(data)
    df_combined=get_vel(df_combined)
    df_combined=get_mean_var(df_combined)
    df=df_combined[features.columns]


    static=data[data['TestID'] == 0]
    dynamic=data[data['TestID']==1]
    # filtering the data
    trace_1 = go.Scatter(x = static.X, y = static.Y,
                    name = 'static',
                    line = dict(width = 2,
                                color = 'rgb(229, 151, 50)'))

    trace_2 = go.Scatter(x = dynamic.X, y = dynamic.Y,
                            name = 'dynamic',
                            line = dict(width = 2,
                                        color = 'rgb(106, 181, 135)'))
    fig = go.Figure(data = [trace_1,trace_2], layout = layout)
    return fig

@app.callback(
    Output('prob', 'children'),
    [Input('opt', 'value')])
def update_value(input):
    filepath = 'data/forapp/'+input+'.txt'
    # print(filepath)
    data=preprocess(filepath)
    # print(data.head())
    df_combined=get_combined(data)
    df_combined=get_vel(df_combined)
    df_combined=get_mean_var(df_combined)
    df=df_combined[features.columns]
    result = round(loaded_model.predict_proba(df)[0,1],2)
    return "The probability of this person having Parkinson's disease is: {0}".format(result)

@app.callback(
    Output('diag', 'children'),
    [Input('opt', 'value')])
def update_value(input):
    filepath = 'data/forapp/'+input+'.txt'
    # print(filepath)
    data=preprocess(filepath)
    # print(data.head())
    df_combined=get_combined(data)
    df_combined=get_vel(df_combined)
    df_combined=get_mean_var(df_combined)
    df=df_combined[features.columns]
    result = round(loaded_model.predict_proba(df)[0,1],2)
    if "forapp/C" in filepath:
        dia='Healthy'
    else: 
        dia='Parkinson'
    return "This person is classified as: {0}".format(dia)

# Step 6. Add the server clause
if __name__ == '__main__':
    app.run_server(debug = True)