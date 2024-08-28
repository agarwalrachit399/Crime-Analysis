import numpy as np
import plotly.express as px
import dash
from dash import dcc, html, callback, Output, Input, ctx
import plotly.express as px
import dash_bootstrap_components as dbc
from location import get_coordinates, get_autocomplete_suggestions
# from get_data import fetch_data_from_postgres
from fetch_datas import fetch_and_clean_data
dash.register_page(__name__,name='Map')



data_copy = fetch_and_clean_data()
data_copy.set_index('datetime',inplace=True)

options = [{'label': html.Span([Year], style={'color': 'white'}), 'value':Year} for Year in data_copy.index.year.unique()]
options.append({'label':html.Span(["All"], style={'color': 'white'}), 'value':'all'}) 

layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div("Filter by Year, or Enter a location in LA:",className="dropdown-heading"),
                dbc.Row( children=[
                      dbc.Col([
                dcc.Dropdown(
                    id = 'year-filter',
                    options = options,
                    value =2020,
                    placeholder="Enter Year",
                    clearable = False,
                    searchable = False,
                    className = 'dropdown'
                )
                    ]),
                    dbc.Col([
                             dcc.Dropdown(
                                    id="location-autocomplete",
                                    options=[],
                                    placeholder="Enter Location",
                                    className='dropdown',
                                    multi=False,
                                    searchable=True,
                                    persistence=True
                                ),
                    ])
                ]
                  
                ),
                
            ],
            className='droprow row'
        ), #the dropdown function
        
        html.Div(
            id= 'map'
        )
    ]
) #Four graphs


@callback(
    Output("location-autocomplete", "options"),
    Input("location-autocomplete", "search_value"),
    Input("location-autocomplete", "value")
)
def update_location_options(search_value,value):
    if ctx.triggered_id == "location-autocomplete" and search_value:
        location_list = get_autocomplete_suggestions(search_value)
        return [{'label': html.Span([loc], style={'color': 'white'}), 'value': loc} for loc in location_list if search_value.lower() in loc.lower()]
    return [{'label': html.Span([value], style={'color': 'white'}), 'value': value}] if value else []

@callback(
    Output("map", "children"), #the output is the scatterchart
    [Input("year-filter", "value"), Input("location-autocomplete", "value")], #the input is the year-filter
)
def update_charts(Year,Location):
    print(Location)
    if Location is None:
        lat, lng = (34.0192298,-118.3023532)
    else:
        lat, lng = get_coordinates(Location)
    print(lat,lng) 
    filtered_data = data_copy.loc[data_copy.index.year == Year] #the graph/dataframe will be filterd by "Year"
    map = px.scatter_mapbox(
    filtered_data,
    lat="lat",
    lon="lon",
    hover_name="hover_desc",
    zoom=15,
    size = np.full(len(filtered_data),6),
    size_max = 8,
    center= {"lat": lat,"lon":lng},
    height= 900
    )
    map.update_layout(mapbox_style="open-street-map")
    map.update_traces(hovertemplate=data_copy['hover_desc'])
    return html.Div([
            dcc.Graph(
                id='crime-map',
                figure=map
            )
        ])

