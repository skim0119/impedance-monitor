import sys

import pandas as pd

from dash import Dash, dcc, html, Input, Output, State, callback, callback_context, dash_table

from app.maindash import app# , cache, long_callback_manager 
from app.views.tag_selection import get_tag_checklist
from app.views.sidebar import get_sidebar, CONTENT_STYLE, BANNER_STYLE
from app.analyze import create_histogram_dataframe, plot_impedance_progress_px, plot_empty_px
from app.load_data import data


# import from google spread sheet
catalogue = data["catalogue"]
impedances = data["impedances"]
mea_tags = data["mea tags"]

# ---------------------------- App ----------------------------

tag_checklist = get_tag_checklist(catalogue)
sidebar = get_sidebar(catalogue)

contents = html.Div([
    html.H5("MEA Impedance Statistics", style={"text-align":"center"}),
    html.Hr(),
    html.A("Link to data-table", href='https://docs.google.com/spreadsheets/d/1ilXTYVzPgkgflllW1U8HYPK_UBe_ebNuQeCdjzoNhCA/edit?usp=sharing', target="_blank"),
    html.H4("MEA-tag:"),
    tag_checklist,

    html.Hr(),
    html.H4("Results"),
    html.H5("Selected tags catalog info:"),
    #html.Div(id='selected-tags'),  # Selected list in textbox:
    dash_table.DataTable(catalogue.to_dict('records'), id='selected-tags-tbl'),

    html.H5("Impedance on each day:"),
    html.Progress(id="graph-progress"),
    dcc.Graph(id="graph-abs"),
    html.H5("Impedance relative to first day:"),
    dcc.Graph(id="graph-rel"),
    html.H5("Impedance mean:"),
    dcc.Graph(id="graph-mean"),

    html.H5("Selected tags impedance:"),
    dash_table.DataTable(impedances.to_dict('records'), id='selected-impedances-tbl'),

], style=CONTENT_STYLE)

banner = html.Div(
    id="banner",
    className="banner",
    children=[
        html.Img(src="https://miv-os.readthedocs.io/en/latest/_static/logo1.svg", style=BANNER_STYLE),
    ],
    style={"background-color": "#6262FF"},
)

app.layout = html.Div([
    banner,
    sidebar,
    contents
], id="app-container")

# ---------------------- Callbacks ---------------------------

#@app.callback(
#    Output("selected-tags", "children"),
#    Input("tag-checklist", "value"),
#)
#def display_selected_tags(tags):
#    return ", ".join(tags)

@app.callback(
    Output("selected-tags-tbl", "data"),
    Input("tag-checklist", "data"),
)
def display_selected_tags_table(tags):
    if len(tags) == 0:
        # return empty table with headers same as 'catalogue'
        df = catalogue.iloc[0:0]
    else:
        df = catalogue[catalogue["Tag Number"].isin(tags)].sort_values(by="Last Measured Date")
        df["Last Measured Date"] = pd.DatetimeIndex(df["Last Measured Date"]).strftime("%b %d, %Y")
    return df.to_dict('records')

@app.callback(
    Output("selected-impedances-tbl", "data"),
    Input("tag-checklist", "data"),
)
def display_selected_tags_table(tags):
    if len(tags) == 0:
        # return empty table with headers same as 'impedances'
        df = impedances.iloc[0:0]
    else:
        df = impedances[impedances["Tag Number"].isin(tags)].sort_values(by="Measured Date")
        df["Measured Date"] = pd.DatetimeIndex(df["Measured Date"]).strftime("%b %d, %Y")
    return df.to_dict('records')

@app.long_callback(
    output=[Output("graph-abs", "figure"), Output("graph-rel", "figure"), Output("graph-mean", "figure")], 
    inputs=Input("tag-checklist", "data"),
    progress=[
        Output("graph-progress", "value"),
        Output("graph-progress", "max"),
    ],
    running=[
        (
            Output("graph-progress", "style"),
            {"visibility": "visible"},
            {"visibility": "hidden"},
        ),
    ],
)
def generate_plot(set_progress, tags):
    if len(tags) == 0:
    #if True:
        # return empty plot
        msg = "No tag selected -- Please select"
        fig = plot_empty_px(msg)

        return fig, fig, fig
    else:
        df = create_histogram_dataframe(impedances, tags, set_progress)
        impedance_headers = ["0.1~0.3", "0.3~0.5", "0.5~0.8", "0.8~1.0", "1.0~1.3", "1.3~1.6", "1.6~2.0"]  # columns
        count = impedances[impedance_headers].astype(int).sum(axis=1)

        # new dataframe from impedance, with the column "Measured Date" and "Tag Number" as multi-index, and active_electrode_count as value
        active_electrode_count = pd.DataFrame({"date": impedances["Measured Date"], "tag": impedances["Tag Number"], "count": count})
        active_electrode_count["first day"] = active_electrode_count.groupby('tag')['date'].transform(lambda x: x.min())
        active_electrode_count["day in use"] = (active_electrode_count["date"] - active_electrode_count["first day"]).dt.days
        #active_electrode_count.set_index(["date", "tag"], inplace=True)
        #active_electrode_count.sort_index(inplace=True)
        return plot_impedance_progress_px(df, active_electrode_count)


if __name__ == "__main__":
    app.run_server("0.0.0.0", 8000, debug=True)
