from dash import Dash, dcc, html, Input, Output, State, callback, callback_context, dash_table

def get_tag_checklist(df):
    tag_checklist = html.Div(
        [
            dcc.Checklist(["All"], [], id="all-checklist", inline=True),
            dcc.Checklist(df, [], id="tag-checklist", inline=True),
        ]
    )

