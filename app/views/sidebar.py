
from app.maindash import app

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State, callback, callback_context, dash_table

BANNER_STYLE = {
    "height": "3rem",
    "margin-top": "1rem",
    "margin-left": "1rem",
}

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "1rem 1rem",
    "margin-top": "4rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-top": "0rem",
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "1rem 1rem",
}

def get_sidebar(df):
    sidebar = html.Div(
        [
            html.H5("Filter", style={"text-align":"center"}),
            html.Hr(),
            html.P(
                "(TODO): Filter by:", className="lead"
            ),
            html.P("last recorded date"),
            html.P("maker"),
            html.P("number of electrodes"),
        ],
        style=SIDEBAR_STYLE,
    )
    return sidebar
