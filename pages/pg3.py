import pandas as pd
import numpy as np
import plotly.express as px
import datetime as dt
import dash
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
from get_data import fetch_data_from_postgres, fetch_filter_options

dash.register_page(__name__, name='Crime')

years, areas, crime_categories, genders, descents = fetch_filter_options()

options = [{'label': html.Span([Year], style={'color': 'white'}), 'value':Year} for Year in years]
# options.append({'label':html.Span(["All"], style={'color': 'white'}), 'value':'all'}) 

gender_option = [{'label': html.Span([Premis], style={'color': 'white'}), 'value': Premis} for Premis in genders]

descent_option = [{'label': html.Span([Crime], style={'color': 'white'}), 'value': Crime} for Crime in descents]

layout = html.Div(
    children=[
        dbc.Row(
            [
                html.Div("Filter by Year, Gender or Ethinicity of Victim:",className="dropdown-heading"),
                dbc.Col(
                    [
                        dcc.Dropdown(
                        id = 'year-filter',
                        options = options,
                        value =2020,
                        clearable = False,
                        searchable = False,
                        className = 'dropdown')
                    ]
                ),
                dbc.Col(
                    [
                    dcc.Dropdown(
                    id = 'gender-filter',
                    options = gender_option,
                    value= 'Male',
                    clearable = False,
                    searchable = False,
                    className = 'dropdown'), 
                    ]
                ),
                dbc.Col(
                    [
                    dcc.Dropdown(
                    id='descent-filter',
                    options = descent_option,
                    value= 'Black',
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
                             html.Div(
                                 id='premis'
                     )),
                        dbc.Col(
                            html.Div(
                                id='weapon'
                    )
                        )
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div(
                                id='part1'
                        ))
                    ]
                ),
                dbc.Row(
                    [
                            dbc.Col(
                            html.Div(
                                id='part2'
                            )
                        )
                    ]
                )
                
        ]
        ), 
    ]
)


@callback(
    Output("premis", "children"), #the output is the scatterchart
    [Input("year-filter", "value"),Input("gender-filter", "value"),
     Input("descent-filter", "value")], #the input is the year-filter
)
def update_charts(Year,Gender,Descent):
    # if Year == 'all':
    #     filtered_data = data_copy
    # else:
    #     filtered_data = data_copy.loc[data_copy.index.year == Year] #the graph/dataframe will be filterd by "Year"
    # filtered_data = filtered_data.loc[filtered_data['vict_sex'] == Gender]
    # filtered_data = filtered_data.loc[filtered_data['vict_descent'] == Descent] 
    filtered_data = fetch_data_from_postgres(
    year=Year,
    gender=Gender,
    descent=Descent
    )
    top_10_premise = filtered_data['premis_desc'].value_counts().head(10).reset_index()
    top_10_premise.columns =['Premis Desc','Count']
    fig10 = px.bar(top_10_premise.sort_values(by='Count'), 
             x='Count', 
             y='Premis Desc', 
             orientation='h',
             text='Count',
             )
    fig10.update_layout(
        title={
            'text': 'Top 10 Location by Crime',
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        xaxis_title='Count',
        yaxis_title='Location',
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
    fig10.update_traces(textposition='inside',marker=dict(color='#00ADB5'),hoverlabel=dict(
            bgcolor='white',
            font_size=14,
            font_color='black'
        ))

    return html.Div([
            dcc.Graph(
                id='premis-loc',
                figure=fig10
            )
        ])

@callback(
    Output("weapon", "children"),
    [Input("year-filter", "value"),
     Input("gender-filter", "value"),
     Input("descent-filter", "value")],
)
def update_charts(Year,Gender,Descent):
    filtered_data = fetch_data_from_postgres(
    year=Year,
    gender=Gender,
    descent=Descent
    )
    top_10_weapon = filtered_data['weapon_desc'].value_counts().head(10).reset_index()
    top_10_weapon.columns =['Weapon Desc','Count']
    fig11 = px.bar(top_10_weapon.sort_values(by='Count'), 
             x='Count', 
             y='Weapon Desc', 
             orientation='h',
             text='Count',
             )

# Update layout for better visuals
    fig11.update_layout(
        title={
            'text': 'Top 10 Weapon Used In Crime',
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        xaxis_title='Count',
        yaxis_title='Weapon',
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
    fig11.update_traces(textposition='inside',marker=dict(color='#00ADB5'),hoverlabel=dict(
        bgcolor='white',
        font_size=14,
        font_color='black'
    ))

    return html.Div([
            dcc.Graph(
                id='weapon-loc',
                figure=fig11
            )
        ])


@callback(
    Output("part1", "children"),
    [Input("year-filter", "value"),
     Input("gender-filter", "value"),
     Input("descent-filter", "value")],
)
def update_charts(Year,Gender,Descent):
    filtered_data = fetch_data_from_postgres(
    year=Year,
    gender=Gender,
    descent=Descent,
    part='1'
    )
    data_subset1 = filtered_data.groupby(["area_name",'crime_cat']).count()['dr_no'].reset_index()
    data_subset1.columns=['AREA NAME','CRIME CATEGORY','COUNT']
    fig7 = px.scatter(
    data_subset1, #dataframe
    y="CRIME CATEGORY", #x
    x="AREA NAME", #y
    size="COUNT", #bubble size
    color="COUNT",#bubble color
    color_continuous_scale=['#BBE1FA','#3282B8','#0F4C75','#1B262C'], #color theme
)
    fig7.update_layout(
        title={
            'text': 'Offences by Location Part 1',
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        xaxis_title='AREA NAME',
        yaxis_title='CRIME CATEGORY',
        template='plotly_white',
        xaxis=dict(
            showgrid=True,  # Remove x-axis grid lines
            tickfont=dict(size=14),  # Increase x-axis tick font size
            titlefont=dict(size=18),  # Increase x-axis title font size
        ),
        yaxis=dict(
            showgrid=True,  # Remove y-axis grid lines
            tickfont=dict(size=14),  # Increase y-axis tick font size
            titlefont=dict(size=18),  # Increase y-axis title font size
        ),
    )
    fig7.update_traces(hovertemplate='Count: %{marker.size}<extra></extra>',hoverlabel=dict(
        bgcolor='white',
        font_size=14,
        font_color='black'
    ))
    return html.Div([
            dcc.Graph(
                id='part1-loc',
                figure=fig7
            )
        ])

@callback(
    Output("part2", "children"),
    [Input("year-filter", "value"),
     Input("gender-filter", "value"),
     Input("descent-filter", "value")],
)
def update_charts(Year,Gender,Descent):

    filtered_data = fetch_data_from_postgres(
    year=Year,
    gender=Gender,
    descent=Descent,
    part='2'
    )
    data_subset2 = filtered_data.groupby(["area_name",'crime_cat']).count()['dr_no'].reset_index()
    data_subset2.columns=['AREA NAME','CRIME CATEGORY','COUNT']
    fig8 = px.scatter(
    data_subset2, #dataframe
    y="CRIME CATEGORY", #x
    x="AREA NAME", #y
    size="COUNT", #bubble size
    color="COUNT",#bubble color
    color_continuous_scale=['#BBE1FA','#3282B8','#0F4C75','#1B262C'], #color theme
)
    fig8.update_layout(
        title={
            'text': 'Offences by Location Part 2',
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        xaxis_title='AREA NAME',
        yaxis_title='CRIME CATEGORY',
        template='plotly_white',
        xaxis=dict(
            showgrid=True,  # Remove x-axis grid lines
            tickfont=dict(size=14),  # Increase x-axis tick font size
            titlefont=dict(size=18),  # Increase x-axis title font size
        ),
        yaxis=dict(
            showgrid=True,  # Remove y-axis grid lines
            tickfont=dict(size=14),  # Increase y-axis tick font size
            titlefont=dict(size=18),  # Increase y-axis title font size
        ),
    )
    fig8.update_traces(hovertemplate='Count: %{marker.size}<extra></extra>',hoverlabel=dict(
            bgcolor='white',
            font_size=14,
            font_color='black'
        ))
    return html.Div([
            dcc.Graph(
                id='part2-loc',
                figure=fig8
            )
        ])