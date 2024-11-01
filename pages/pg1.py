
import numpy as np
import plotly.express as px
import dash
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
# from get_data import fetch_data_from_postgres
from get_data import fetch_data_from_postgres
dash.register_page(__name__, path='/', name='Home')

#Read Data
def read_data():
    data = fetch_data_from_postgres()
    data1 = data.set_index('datetime')
    return data1

data = read_data()

#Options for Dropdown Filters
year_option = [{'label': html.Span([Year], style={'color': 'white'}), 'value':Year} for Year in data.index.year.unique()]
year_option.append({'label':html.Span(["All"], style={'color': 'white'}), 'value':'all'}) 
area_option = [{'label': html.Span([Area], style={'color': 'white'}), 'value': Area} for Area in data['area_name'].unique()]
area_option.append({'label':html.Span(["All"], style={'color': 'white'}), 'value':'all'})
crime_option = [{'label': html.Span([Crime], style={'color': 'white'}), 'value': Crime} for Crime in data['crime_cat'].unique()]
crime_option.append({'label':html.Span(["All"], style={'color': 'white'}), 'value':'all'})

layout = html.Div(
    children=[
        dbc.Row(
            [
                html.Div("Filter by Year, Location or Type of Crime:",className="dropdown-heading"),
                dbc.Col(
                    [
                        dcc.Dropdown(
                        id = 'year-filter',
                        options = year_option,
                        value =2020,
                        clearable = False,
                        searchable = False,
                        className = 'dropdown')
                    ]
                ),
                dbc.Col(
                    [
                    dcc.Dropdown(
                    id = 'premis-filter',
                    options = area_option,
                    value= 'Wilshire',
                    clearable = False,
                    searchable = False,
                    className = 'dropdown'), 
                    ]
                ),
                dbc.Col(
                    [
                    dcc.Dropdown(
                    id='crime-filter',
                    options = crime_option,
                    value= 'Larceny',
                    clearable = False,
                    searchable = False,
                    className = 'dropdown'),  
                    ]
                )
            ], className='droprow'
        ),
        
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                             html.Div([
                                 dcc.Tabs(id="tabs-graph", value='tab-1', children=[
                            dcc.Tab(label='Hourly Data', value='tab-1',className = "Tabs"),
                            dcc.Tab(label='Weekly Data', value='tab-2',className= "Tabs"),
                            dcc.Tab(label='Monthly Data', value='tab-3',className= "Tabs"),
                        ], style= {"height" :"fit-content"}),
                        html.Div(id='tabs-content')
                             ]
                                 
                     )),
                        dbc.Col(
                            html.Div( id = "GenderPie", className="piechart"
                    )
                        )
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                id = "DescentBar"
                        ),width=7),
                        dbc.Col(
                            html.Div(
                                id = "AgeHist"
                            ),width=5
                        )
                    ]
                )
                
        ],
        ), 
    ]
) 


@callback(
    Output("GenderPie", "children"),
    [Input("year-filter", "value"),
     Input("premis-filter", "value"),
     Input("crime-filter", "value")
     ],
)
def update_charts(Year,Area,Crime):
    if Year == 'all':
        filtered_data = data
    else:
        filtered_data = data.loc[data.index.year == Year]
    filtered_data = filtered_data[filtered_data['area_name']== Area]
    filtered_data = filtered_data[filtered_data['crime_cat']== Crime]
    gender_data = filtered_data['vict_sex']
    gender_counts = gender_data.value_counts().reset_index()
    gender_counts.columns = ['Category', 'Values']
    bar = px.pie(gender_counts, values='Values', names='Category', hole=0.3,color_discrete_sequence=['#CDE8E5','#E1AFD1','#EEF7FF'])
    bar.update_layout(title={
        'text': 'Gender Distributon of Victims',
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 24}
    },)
    bar.update_traces(hoverlabel=dict(
            bgcolor='white',
            font_size=14,
            font_color='black'
        ))
    return html.Div([
            dcc.Graph(
                id='pie-chart',
                figure=bar
            )
        ])


@callback(
    Output("DescentBar", "children"),
    [Input("year-filter", "value"),
     Input("premis-filter", "value"),
     Input("crime-filter", "value")],
)
def update_charts(Year,Area,Crime):
    if Year == 'all':
        filtered_data = data
    else:
        filtered_data = data.loc[data.index.year == Year]
    filtered_data = filtered_data[filtered_data['area_name']== Area]
    filtered_data = filtered_data[filtered_data['crime_cat']== Crime]
    descent_data = filtered_data['vict_descent']
    descent_counts = descent_data.value_counts().reset_index()
    descent_counts.columns = ['Category', 'Values']
    descent_counts = descent_counts.sort_values(by='Values', ascending=True)
    bibar = px.bar(descent_counts, 
             x='Values', 
             y='Category', 
             orientation='h',
             text='Values',
             )

# Update layout for better visuals
    bibar.update_layout(
        title={
            'text': 'Number of Crimes against particular race',
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        xaxis_title='Count',
        yaxis_title='Victim Ethinicity',
        template='plotly_white',
        xaxis=dict(
            showgrid=False,  # Remove x-axis grid lines
            tickfont=dict(size=14),  # Increase x-axis tick font size
            titlefont=dict(size=18),  # Increase x-axis title font size
        ),
        yaxis=dict(
            showgrid=False,  # Remove y-axis grid lines
            tickfont=dict(size=14),  # Increase y-axis tick font size
            titlefont=dict(size=18),  # Increase y-axis title font size
        ),
    )
    bibar.update_traces(textposition='outside',marker=dict(color='#4D869C'),hovertemplate='Age: %{x}<br>Count: %{y}<extra></extra>',hoverlabel=dict(
            bgcolor='white',
            font_size=14,
            font_color='black'
        ))
    return html.Div([
            dcc.Graph(
                id='desc-bar',
                figure=bibar
            )
        ])

@callback(
    Output("AgeHist", "children"),
    [Input("year-filter", "value"),
     Input("premis-filter", "value"),
     Input("crime-filter", "value")],
)
def update_charts(Year,Area,Crime):
    if Year == 'all':
        filtered_data = data
    else:
        filtered_data = data.loc[data.index.year == Year]
    filtered_data = filtered_data[filtered_data['area_name']== Area]
    filtered_data = filtered_data[filtered_data['crime_cat']== Crime]

    filtered_data.loc[filtered_data['vict_age'].astype('int')<=0,'vict_age']=np.nan
    age_sorted = filtered_data['vict_age'].dropna().astype('int').sort_values()
    barscene = px.histogram(age_sorted,
                   nbins = 50,
                   title='Distribution of Age of Victim',
                   labels={'value': 'Age'},
                  )
    
    barscene.update_layout(
    title={
        'text': 'Distribution of Age of Victim',
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font': {'size': 24}
    },
    xaxis_title='Age',
    yaxis_title='Count',
    xaxis=dict(
        showgrid=False, 
        tickfont=dict(size=14),  
        titlefont=dict(size=18), 
        linecolor='#151515', 
        linewidth=1  
    ),
    yaxis=dict(
        showgrid=False,  
        tickfont=dict(size=14), 
        titlefont=dict(size=18),
        showline=True,
        linecolor='#151515', 
        linewidth=1 
    ),
    template='plotly_white',
    bargap=0.1,
    showlegend=False,
)

    barscene.update_traces(marker=dict(color='#7AB2B2'),hovertemplate='Age: %{x}<br>Count: %{y}<extra></extra>',hoverlabel=dict(
            bgcolor='white',
            font_size=14,
            font_color='black'
        ))
    
    return html.Div([
            dcc.Graph(
                id='age-hist',
                figure=barscene
            )
        ])


@callback(
        Output('tabs-content', 'children'),
              [Input('tabs-graph', 'value'),Input("year-filter", "value"),Input("premis-filter", "value"),
     Input("crime-filter", "value")]
              )
def render_content(tab,Year,Area,Crime):
    if tab == 'tab-1':
        if Year == 'all':
            filtered_data = data
        else:
            filtered_data = data.loc[data.index.year == Year]
        filtered_data = filtered_data[filtered_data['area_name']== Area]
        filtered_data = filtered_data[filtered_data['crime_cat']== Crime]
        hourly_data = filtered_data.groupby(filtered_data.index.hour).count()['dr_no'].reset_index()
        scatter = px.bar(hourly_data, x='datetime',y='dr_no',
            color='dr_no',color_continuous_scale=px.colors.sequential.Teal,text='dr_no')
        scatter.update_layout(
            title={
                'text': 'Total Number of Cases Reported at each hour From 2020-2024',
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 24}
            },
            xaxis_title='Time (24hr format)',
            yaxis_title='Count',
            template='plotly_white',
            xaxis=dict(
                showgrid=False,  
                tickfont=dict(size=14),  
                titlefont=dict(size=18),  
            ),
            yaxis=dict(
                showgrid=False,  
                tickfont=dict(size=14),  
                titlefont=dict(size=18),  
            ),coloraxis_showscale=False
        )
        scatter.update_traces(textposition='inside',hovertemplate='Time: %{x}<br>Count: %{y}<extra></extra>',hoverlabel=dict(
                bgcolor='white',
                font_size=14,
                font_color='black'
            ),marker=dict(
                showscale=False 
            ))
        return html.Div([
            dcc.Graph(
                id='graph-1-tabs-dcc',
               figure = scatter
            )
        ])
    elif tab == 'tab-2':
        if Year == 'all':
            filtered_data = data
        else:
            filtered_data = data.loc[data.index.year == Year]
        filtered_data = filtered_data[filtered_data['area_name']== Area]
        filtered_data = filtered_data[filtered_data['crime_cat']== Crime]
        count_crime = filtered_data.groupby(by=["day"]).size().reset_index(name="Count")
        fig1 = px.bar(count_crime, y='day',x='Count',
             color='day',color_discrete_sequence=['#EEF7FF'],color_discrete_map={count_crime['day'][0]:'#CDE8E5'},
            category_orders={'day':['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']},
           text='Count')
        fig1.update_layout(
            title={
                'text': 'Total Number of Cases Reported on Each Day From 2020-2024',
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 24}
            },
            xaxis_title='Count',
            yaxis_title='Day',
            template='plotly_white',
            xaxis=dict(
                showgrid=False,  
                tickfont=dict(size=14), 
                titlefont=dict(size=18), 
            ),
            yaxis=dict(
                showgrid=False, 
                tickfont=dict(size=14),
                titlefont=dict(size=18),
            ),
            showlegend=False,
        )
        fig1.update_traces(textposition='inside',hoverlabel=dict(
                bgcolor='white',
                font_size=14,
                font_color='black'
            ))
        return html.Div([
            dcc.Graph(
                id='graph-2-tabs-dcc',
                figure=fig1
            )
        ])
    
    elif tab == 'tab-3':
        if Year == 'all':
            filtered_data = data
        else:
            filtered_data = data.loc[data.index.year == Year]
        filtered_data = filtered_data[filtered_data['area_name']== Area]
        filtered_data = filtered_data[filtered_data['crime_cat']== Crime]
        trend_month = filtered_data.resample('M')['dr_no'].count().iloc[:-1]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=trend_month.index, y=trend_month.values,
                                line=dict(color='#4D869C', width=3), mode='lines+markers'))

        fig2.update_layout(
            title={
                'text': 'Monthly Cases Trend Across the Years From 2020-2024',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24},
            },
            xaxis=dict(
                showgrid=True,  # Remove x-axis grid lines
                tickfont=dict(size=14),  # Increase x-axis tick font size
                titlefont=dict(size=18)  # Increase x-axis title font size
            ),
            yaxis=dict(
                showgrid=True,  # Remove y-axis grid lines
                tickfont=dict(size=14),  # Increase y-axis tick font size
                titlefont=dict(size=18),  # Increase y-axis title font size
                title={'text': 'Number of Cases Reported', 'font': {'size': 20}},  # Y-axis label font size
            ),
            template='plotly_white',  # Change background to white
        )

        # Customize tooltips
        fig2.update_traces(
            hovertemplate='Date: %{x}<br>Cases: %{y}<extra></extra>',  # Better tooltip
            hoverlabel=dict(
                bgcolor='white',
                font_size=14,
                font_color='black'
            )
        )

        return html.Div([
            dcc.Graph(
                id='graph-3-tabs-dcc',
                figure=fig2
            )
        ])