from app.maindash import app

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, State, callback, callback_context, dash_table

def get_tag_checklist(df):
    # split df by date: 2 month old or newer
    df = df[df["Last Measured Date"] >= (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")].copy()
    df_old = df[df["Last Measured Date"] < (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")].copy()

    df.sort_values(by=["Last Measured Date"], inplace=True, ascending=False)
    df_old.sort_values(by=["Last Measured Date"], inplace=True, ascending=False)

    all_tag_list = list(df["Tag Number"])
    all_tag_list.sort()
    all_tag_list_group = list(np.array_split(all_tag_list, 6))

    old_tag_list = list(df_old["Tag Number"])
    old_tag_list.sort()

    def make_child(i):
        return html.Div(
                style={'width':'15%', 'height':'100%', 'float':'left'},
                children=[
                    dcc.Checklist(
                        all_tag_list_group[i],
                        className=f'checkbox_1',
                        id=f'tag-checklist-new-{i}',
                        style={'label':{'color':'red'}, 'box': {'shape':'round'}},
                    ),
                ]
            )
    all_tag_checklists = [make_child(i) for i in range(6)]

    tag_checklist = html.Div([
        html.Div(all_tag_checklists), # [ dcc.Checklist(["All"], [], id="all-checklist-new", style={'label':{'color':'red'}, 'box': {'shape':'round'}}, inline=True), ]
        html.Br(style={'clear':'both'}),
        html.P(),
        #dbc.Button("Show Old MEA Tags:", id="collapse-button-show-old-tags", n_clicks=0, color="primary", className="mb-3"),
        #dbc.Collapse(
        html.H5("Old MEA Tags (>2 months):"),
        dcc.Checklist(old_tag_list, [], id="tag-checklist-old", inline=True),
        #    id="collapse",
        #    is_open=False,
        #    style={"visibility": "visible"},
        #),
        dcc.Checklist(all_tag_list+old_tag_list, [], id="tag-checklist", inline=True), #, style={"visibility": "hidden"}, inline=True),
    ])

    return tag_checklist

#@app.callback(
#    Output("collapse", "is_open"),
#    [Input("collapse-button-show-old-tags", "n_clicks")],
#    [State("collapse", "is_open")],
#)
#def toggle_collapse_old_tags(n, is_open):
#    print(n, is_open)
#    if n:
#        return not is_open
#    return is_open

# @app.callback(
#     [Output(f"tag-checklist-new-{i}", "value") for i in range(6)] + [Output("all-checklist-new", "value")],
#     [Input(f"tag-checklist-new-{i}", "value") for i in range(6)] + [Input("all-checklist-new", "value")],
#     [State("tag-checklist", "options")],
# )
# def sync_checklists(selected, mea_tags):
#     ctx = callback_context
#     input_id = ctx.triggered[0]["prop_id"].split(".")[0]
# 
#     cites_selected, all_selected = selected[:-1], selected[-1]
#     if input_id == "tag-checklist-new":
#         all_selected = ["All"] if set(cities_selected) == set(mea_tags) else []
#     else:
#         cities_selected = mea_tags if all_selected else []
#     return cities_selected, all_selected
# 
# @app.callback(
#     Output("tag-checklist-old", "value"),
#     Output("all-checklist-old", "value"),
#     Input("tag-checklist-old", "options"),
#     Input("tag-checklist-old", "value"),
#     Input("all-checklist-old", "value"),
# )
# def sync_checklists(mea_tags, cities_selected, all_selected):
#     ctx = callback_context
#     input_id = ctx.triggered[0]["prop_id"].split(".")[0]
#     if input_id == "tag-checklist-old":
#         all_selected = ["All"] if set(cities_selected) == set(mea_tags) else []
#     else:
#         cities_selected = mea_tags if all_selected else []
#     return cities_selected, all_selected

@app.callback(
    Output("tag-checklist", "value"),
    [Input(f"tag-checklist-new-{i}", "value") for i in range(6)]+[Input("tag-checklist-old", "value")],
)
def merge_checklists(*selected):
    tags = []
    for sel in selected:
        if sel is not None:
            tags.extend(sel)
    return tags

