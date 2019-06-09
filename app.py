# -*- coding: utf-8 -*-

import base64
import io

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
from scipy import stats


group_colors = {'negative': 'light blue',
                'test': 'green',
                'positive': 'red'
                }

app = dash.Dash(__name__)

default_study_data = pd.read_csv('study.csv')

app.layout = html.Div(className='', children=[
    html.Div(id='error-message'),
    html.Div(className='study-browser-banner', children='Animal Study Browser'),
    html.Div(className='container', children=[
        html.Div(className='row', children=[

            html.Div(className='six columns', children=[
                html.Em(id="dropdown-label"),
                dcc.Dropdown(
                    id='study-dropdown',
                )
            ]),
            html.Div(className='six columns', children=[

            ]),
        ]),
        html.Div(className='row', children=[

            html.Div(className='ten columns', children=[
                dcc.Graph(id='plot'
                          )
            ]),
            html.Div(className='two columns', children=[
                dcc.RadioItems(
                    id='chart-type',
                    options=[
                        {'label': 'Box Plot', 'value': 'box'},
                        {'label': 'Violin Plot', 'value': 'violin'}
                    ],
                    value='violin'
                ),

            ]),

        ]),
        html.Div(className='row', style={}, children=[

            html.Div(className='twelve columns', children=[
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                )
            ])
        ]),
    ])
])

@app.callback(Output('error-message', 'children'),
              [Input('upload-data', 'contents')])
def update_error(contents):
    if contents:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        study_data = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    else:
        study_data = default_study_data

    missing_columns = {'group_id', 'group_type', 'reading_value', 'study_id'}.difference(study_data.columns)

    if missing_columns:
        return html.Div(className='alert', children=['Missing columns: ' + str(missing_columns)])

    return None


@app.callback([Output('study-dropdown', 'options'),
               Output('study-dropdown', 'value'),
               Output("dropdown-label", 'children')],
              [Input('error-message', 'children')],
              [State('upload-data', 'contents'),
               ])
def update_dropdown(error_message, contents):
    if contents and not error_message:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        study_data = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    else:
        study_data = default_study_data

    options = []
    try:
        test_articles = study_data.test_article.unique()
    except AttributeError:
        studies = study_data.study_id.unique()
        dropdown_label = ["Study ID:"]
        for study in studies:
            options.append({'label': study, 'value': study})
    else:
        dropdown_label = ["Test Article:"]
        for test_article in test_articles:
            studies = study_data.study_id[study_data.test_article == test_article].unique()
            for study in studies:
                options.append({'label': "{} (study: {})".format(test_article, study), 'value': study})

    value = options[0]['value']

    return options, value, dropdown_label


@app.callback(Output('plot', 'figure'),
              [Input('chart-type', 'value'),
               Input('study-dropdown', 'value')],
              [State('upload-data', 'contents'),
               State('error-message', 'children')])
def update_output(chart_type, study, contents, error_message):

    if contents and not error_message:
        content_type, content_string = contents.split(',')
        print(content_type)
        decoded = base64.b64decode(content_string)
        study_data = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    else:
        study_data = default_study_data

    if study is None:
        study = study_data.study_id[0]
    study_data = study_data[study_data.study_id == study]

    #try:
    vehicle_readings = study_data['reading_value'][study_data["group_type"] == 'negative']
    #except KeyError:
    #    vehicle_readings = np.array()

    data_range = study_data['reading_value'].max() - study_data['reading_value'].min()

    test_stats = {}
    box_data = []
    violin_data = []
    for i, group_id in enumerate(study_data.group_id.unique()):
        try:
            group_name = study_data['group_name'][study_data.group_id == group_id].values[0]
        except KeyError:
            group_name = group_id

        #try:
        group_type = study_data['group_type'][study_data.group_id == group_id].values[0]
        #except KeyError:
        #    group_type = 'not specified'

        y_data = study_data['reading_value'][study_data.group_id == group_id]
        try:
            subject_ids = study_data['subject_id'][study_data.group_id == group_id]
        except KeyError:
            subject_ids = None

        t, p = stats.ttest_ind(vehicle_readings,
                           y_data)

        test_stats[group_id] = {'t': t, 'p': p, 'pf': 'p={:0.3f}'.format(p) if p >= 0.001 else 'p<0.001',
                            'astrix': '***' if p <= 0.001 else '**' if p <= 0.01 else '*' if p <= 0.05 else '',
                            'max_y': y_data.max(),
                            'index': i}

        box_data.append(
            go.Box(y=y_data,
                   name=group_name,
                   text=subject_ids,
                   hoveron="points",
                   boxmean=True,
                   showlegend=False,
                   boxpoints='all',
                   pointpos=0,
                   line={'color': group_colors.get(group_type, 'green')}
                   )
        )
        violin_data.append(
            go.Violin(y=y_data,
                      name=group_name,
                      text=subject_ids,
                      hoveron="points",
                      meanline={"visible": True},
                      showlegend=False,
                      points='all',
                      pointpos=0,
                      line={'color': group_colors.get(group_type, 'green')}
                      )
        )

    chart_data = {'box': box_data, 'violin': violin_data}

    if 'reading_name' in study_data.columns:
        reading_name = study_data['reading_name'].unique()[0]
    else:
        reading_name = None

    if not vehicle_readings.empty:
        ref_groups = set(study_data.group_id[study_data.group_type == 'positive'].unique())
        control_groups = set(study_data.group_id[study_data.group_type == 'negative'].unique())
        all_groups = set(study_data.group_id.unique())
        groups_to_annotate = all_groups - ref_groups - control_groups
        annotations = [
            dict(
                x=test_stats[group_id]['index'],
                y=test_stats[group_id]['max_y'] + data_range / (4 if chart_type == 'violin' else 10),
                text='{}<br>{}'.format(test_stats[group_id]['astrix'], test_stats[group_id]['pf']),
                showarrow=False,
            ) for group_id in groups_to_annotate
        ]
    else:
        annotations = None

    figure = go.Figure(
        data=chart_data[chart_type],
        layout=go.Layout(
            height=600,
            yaxis=dict(title=dict(text=reading_name,
                                  font=dict(
                                      family='"Open Sans", "HelveticaNeue", "Helvetica Neue",'
                                             ' Helvetica, Arial, sans-serif',
                                      size=12)
                                  ),
                       ),
            annotations=annotations
        )
    )

    return figure


def validate_data(df):
    if {'group_id', 'reading_value'}.difference(df.columns):
        return False

    return True


if __name__ == '__main__':
    app.run_server(debug=True)
