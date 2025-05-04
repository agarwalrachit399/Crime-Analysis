import numpy as np
import plotly.express as px
import dash
from dash import dcc, html, callback, Output, Input, State, ctx
import dash_bootstrap_components as dbc
from location import get_locationiq_data
from get_data import fetch_data_from_postgres, fetch_filter_options

dash.register_page(__name__, name='Map')

# Fetch dropdown options
years, areas, crime_categories, genders, descents = fetch_filter_options()
options = [{'label': html.Span([Year], style={'color': 'white'}), 'value': Year} for Year in years]

layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div("Filter by Year, or Enter a location in LA:", className="dropdown-heading"),
                dbc.Row(children=[
                    dbc.Col([
                        dcc.Dropdown(
                            id='year-filter',
                            options=options,
                            value=2020,
                            placeholder="Enter Year",
                            clearable=False,
                            searchable=False,
                            className='dropdown'
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
                ])
            ],
            className='droprow row'
        ),

        # Hidden stores and debounce interval
        dcc.Store(id="search-buffer"),
        dcc.Store(id="location-data-store"),
        dcc.Interval(id="search-poll-interval", interval=700, n_intervals=0, disabled=True),

        html.Div(id='map')
    ]
)

# 👇 All-in-one callback for autocomplete + map + debounce
@callback(
    Output("location-autocomplete", "options"),
    Output("location-data-store", "data"),
    Output("search-buffer", "data"),
    Output("search-poll-interval", "disabled"),
    Output("map", "children"),
    Input("location-autocomplete", "search_value"),
    Input("search-poll-interval", "n_intervals"),
    Input("year-filter", "value"),
    Input("location-autocomplete", "value"),
    State("search-buffer", "data"),
    State("location-data-store", "data")
)
def unified_handler(search_value, _, year, selected_location, buffered_search, location_store):
    triggered = ctx.triggered_id

    options, store_data = dash.no_update, dash.no_update
    buffer, disable_timer = dash.no_update, True
    lat, lng = (34.0192298, -118.3023532)  # Default (USC area)

    if triggered == "location-autocomplete" and search_value:
        # User is typing
        return options, store_data, search_value, False, dash.no_update

    if triggered == "search-poll-interval" and buffered_search:
        # API Call on debounce
        location_list = get_locationiq_data(buffered_search)
        print("debounced_search", buffered_search)
        options = []
        store_data = {}

        for item in location_list:
            for desc, (lat_val, lon_val) in item.items():
                options.append({'label': html.Span([desc], style={'color': 'white'}), 'value': desc})
                store_data[desc] = {'lat': float(lat_val), 'lon': float(lon_val)}

        return options, store_data, dash.no_update, True, dash.no_update

    # Use selected location's coordinates if available
    if selected_location and selected_location in location_store:
        lat = location_store[selected_location]['lat']
        lng = location_store[selected_location]['lon']

    # Generate map
    filtered_data = fetch_data_from_postgres(year=year)
    map_fig = px.scatter_mapbox(
        filtered_data,
        lat="lat",
        lon="lon",
        hover_name="hover_desc",
        zoom=15,
        size=np.full(len(filtered_data), 6),
        size_max=8,
        center={"lat": lat, "lon": lng},
        height=900
    )
    map_fig.update_layout(mapbox_style="open-street-map")
    map_fig.update_traces(hovertemplate=filtered_data['hover_desc'])

    return options, store_data, buffer, disable_timer, html.Div([
        dcc.Graph(
            id='crime-map',
            figure=map_fig
        )
    ])
