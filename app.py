import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SPACELAB])
server = app.server
sidebar = dbc.Nav(
            [   
        
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
            ],
            vertical=False,
            pills=True,
)

app.layout = dbc.Container([

    dbc.Row([
        dbc.Col(html.Div(
            [
                html.Img(src="assets/la_logo.png",
                         style={"width": "60px"})
            ]
            ),width=1),
             dbc.Col(html.Div(
            [
                html.H1("Los Angeles Crime Analytics",
                         style={'fontSize':"25px", 'textAlign':'initial'}),

            ]
            ),width=5),
        dbc.Col(html.Div(sidebar),width=5)

    ],className="custom_navbar"),
    dbc.Row(
        [
            dbc.Col(
                [    dash.page_container
                ])
        ]
    )
], fluid=True)


if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0', port=8080)