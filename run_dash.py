import sys

from dash import Dash, dcc, html, Input, Output, State, callback, callback_context, dash_table

from app.maindash import app# , cache, long_callback_manager 
from app.views.tag_selection import get_tag_checklist
from app.analyze import create_histogram_dataframe, plot_impedance_progress_px, plot_empty_px
from app.load_data import data


# import from google spread sheet
catalogue = data["catalogue"]
impedances = data["impedances"]
mea_tags = data["mea tags"]

# ---------------------------- App ----------------------------

tag_checklist = get_tag_checklist(catalogue)

app.layout = html.Div([
    html.H3("MiV-MEA Impedance Dashboard"),
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

])

# ---------------------- Callbacks ---------------------------

#@app.callback(
#    Output("selected-tags", "children"),
#    Input("tag-checklist", "value"),
#)
#def display_selected_tags(tags):
#    return ", ".join(tags)

@app.callback(
    Output("selected-tags-tbl", "data"),
    Input("tag-checklist", "value"),
)
def display_selected_tags_table(tags):
    if len(tags) == 0:
        # return empty table with headers same as 'catalogue'
        return catalogue.iloc[0:0].to_dict('records')
    else:
        return catalogue[catalogue["Tag Number"].isin(tags)].sort_values(by="Last Measured Date").to_dict('records')

@app.callback(
    Output("selected-impedances-tbl", "data"),
    Input("tag-checklist", "value"),
)
def display_selected_tags_table(tags):
    if len(tags) == 0:
        # return empty table with headers same as 'impedances'
        return impedances.iloc[0:0].to_dict('records')
    else:
        return impedances[impedances["Tag Number"].isin(tags)].sort_values(by="Measured Date").to_dict('records')

@app.long_callback(
    output=[Output("graph-abs", "figure"), Output("graph-rel", "figure"), Output("graph-mean", "figure")], 
    inputs=Input("tag-checklist", "value"),
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
        return plot_impedance_progress_px(df)


if __name__ == "__main__":
    app.run_server(debug=True)
