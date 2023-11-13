import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from collections import defaultdict

ANALYSIS_PATH = "analysis"

def create_histogram_dataframe(df, tags, pbar_update=None):
    bin_edges = np.array([0.0, 0.01, 0.1, 0.3, 0.5, 0.8, 1.0, 1.3, 1.6, 2.0, 2.5, 3.0])

    df1 = pd.DataFrame(columns=['date', 'tag', 'impedance', 'day in use'])

    if pbar_update is not None:
        max_count = df["Tag Number"].isin(tags).sum()
        count = 0
        pbar_update((count, max_count))

    for tag in tags:
        tag = str(tag)
        _df = df[df["Tag Number"] == tag]

        # Largest measured data
        first_recorded_date = _df["Measured Date"].min()

        for index, row in _df.iterrows():
            frequencies = np.array(row.iloc[4:15]).astype(np.int_)
            if frequencies.sum() == 0:
                continue
            x1 = np.random.uniform(np.repeat(bin_edges[:-1], frequencies), np.repeat(bin_edges[1:], frequencies))
            for x in x1:
                df1 = df1._append({
                    "date": row["Measured Date"],
                    "tag": row["Tag Number"],
                    "impedance": x,
                    "day in use": (row["Measured Date"] - first_recorded_date).days}, ignore_index=True)
            if pbar_update is not None:
                count += 1
                pbar_update((str(count), str(max_count)))
    return df1

def plot_empty_px(msg=""):
    import plotly.graph_objects as go
    

    fig = go.Figure()
    fig.update_layout(
        xaxis =  { "visible": False },
        yaxis = { "visible": False },
        annotations = [
            {   
                "text": msg,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 28
                }
            }
        ]
    )
    return fig

def plot_impedance_progress_px(df, active_count, vmin=0.01, vmax=5.0, safe_min_y=0.02, safe_max_y=1.8):
    import plotly.express as px
    range_y = (vmin, vmax)

    # Absolute
    ylabel = "Impedance (MOhms)"
    fig_abs = px.box(df, x="date", y="impedance", color="tag", labels={"impedance":ylabel}, log_y=True, range_y=range_y)
    fig_abs.update_xaxes(minor=dict(ticks="inside", showgrid=True))
    fig_abs.update_yaxes(minor=dict(ticks="inside", showgrid=True))
    fig_abs.add_hrect(y0=vmin, y1=safe_min_y, line_width=0, fillcolor="red", opacity=0.2)
    fig_abs.add_hrect(y0=safe_max_y, y1=vmax, line_width=0, fillcolor="red", opacity=0.2)

    # Relative
    fig_rel = px.box(df, x="day in use", y="impedance", color="tag", labels={"impedance":ylabel}, log_y=True, range_y=range_y)
    fig_rel.update_xaxes(minor=dict(ticks="inside", showgrid=True))
    fig_rel.update_yaxes(minor=dict(ticks="inside", showgrid=True))
    fig_rel.add_hrect(y0=vmin, y1=safe_min_y, line_width=0, fillcolor="red", opacity=0.2)
    fig_rel.add_hrect(y0=safe_max_y, y1=vmax, line_width=0, fillcolor="red", opacity=0.2)

    # Average
    df_mean = df.groupby(["day in use", "tag"])["impedance"].mean().to_frame(name="mean").reset_index()
    df_mean = pd.merge(df_mean, active_count, on=["day in use", "tag"])  # merge
    fig_mean = px.line(df_mean, x="day in use", y="mean", color="tag", labels={"mean":ylabel}, text="count", log_y=True, range_y=range_y, markers=True, title="(label is number of active channels: range 0.05MOhms to 2.0MOhms)")
    fig_mean.update_traces(textposition="top center")
    fig_mean.update_xaxes(minor=dict(ticks="inside", showgrid=True))
    fig_mean.update_yaxes(minor=dict(ticks="inside", showgrid=True))
    fig_mean.add_hrect(y0=vmin, y1=safe_min_y, line_width=0, fillcolor="red", opacity=0.2)
    fig_mean.add_hrect(y0=safe_max_y, y1=vmax, line_width=0, fillcolor="red", opacity=0.2)

    return fig_abs, fig_rel, fig_mean

#(Deprecated)
def plot_impedance_progress(df, name=None):
    fig, axes = plt.subplots(1, 1, figsize=(12, 6))
    axes.set_yscale('log')
    axes.set_ylim([0.005, 10.0])
    #axes[gidx].tick_params(axis='x', rotation=90)

    # Plot boxplot where x axis is date and y axis is impedance, and each box is a tag
    g = sns.boxplot(data=df, x="date", y="impedance", hue="tag", ax=axes)

    # Get xlim and fill green inbetween 0.1 and 1.0
    xlim = g.get_xlim()
    ylim = g.get_ylim()
    g.fill_between(xlim , 0.1, 1.0, color='g', alpha=0.2)
    g.fill_between(xlim , 1.0, 2.0, color='y', alpha=0.2)
    g.fill_between(xlim , 0.05, 0.1, color='y', alpha=0.2)
    g.fill_between(xlim , ylim[0], 0.05, color='r', alpha=0.2)
    g.fill_between(xlim , 2.0, ylim[1], color='r', alpha=0.2)
    # remove x labels
    #g.set(xticklabels=[])

    axes.set_ylabel("Impedance (MOhms)")

    plt.savefig(os.path.join(ANALYSIS_PATH, f"impedance_date_{name}.png"), dpi=300)
    plt.close()

    fig, axes = plt.subplots(1, 1, figsize=(10, 6), sharey=True)
    axes.set_yscale('log')
    axes.set_ylim([0.005, 10.0])
    #axes[gidx].tick_params(axis='x', rotation=90)

    # Plot boxplot where x axis is date and y axis is impedance, and each box is a tag
    g = sns.lineplot(data=df, x="day in use", y="impedance", hue="tag", ax=axes, marker='o')

    # Get xlim and fill green inbetween 0.1 and 1.0
    xlim = g.get_xlim()
    ylim = g.get_ylim()
    g.fill_between(xlim , 0.1, 1.0, color='g', alpha=0.2)
    g.fill_between(xlim , 1.0, 2.0, color='y', alpha=0.2)
    g.fill_between(xlim , 0.05, 0.1, color='y', alpha=0.2)
    g.fill_between(xlim , ylim[0], 0.05, color='r', alpha=0.2)
    g.fill_between(xlim , 2.0, ylim[1], color='r', alpha=0.2)
    # remove x labels
    #g.set(xticklabels=[])

    axes.set_ylabel("Impedance (MOhms)")

    plt.savefig(os.path.join(ANALYSIS_PATH, f"impedance_day_in_use_{name}.png"), dpi=300)

    return fig

if __name__ == '__main__':
    from gapi.tools import import_impedances_db
    from groups import TAG_GROUPS

    sample_range_name = 'Impedance Measurement!A3:P'
    data = import_impedances_db(sample_range_name)
    assert data is not None, "Failed to import data from Google Sheets"

    os.makedirs(ANALYSIS_PATH, exist_ok=True)

    # convert "Measured Date" column type to datetime
    data['Measured Date'] = pd.to_datetime(data['Measured Date'])

    # sort by 'Measured Date'
    data.sort_values(by=['Measured Date'], inplace=True)
    print(data.head())
    print(data.dtypes)

    groups = TAG_GROUPS.keys()
    for gidx, group in enumerate(groups):
        tags_interest = TAG_GROUPS[group]
        df1 = create_histogram_dataframe(data, tags_interest)
        #print(df1.head())

        # sort df1 by median for each tag
        #grouped = df1.loc[:, ["tag", "impedance"]].groupby("tag") \
        #            .median() \
        #            .sort_values(by="impedance", ascending=False)
        plot_impedance_progress(df1, group)

    sys.exit()

    # Create a boxplot for each unique Tag Number
    plt.figure(figsize=(10, 6))  # Set the size of the figure

    # Iterate over unique Tag Numbers
    for tag_number in data['Tag Number'].unique():
        # Filter the data for the current Tag Number
        filtered_data = data[data['Tag Number'] == tag_number]
        
        # Plot the boxplot
        sns.boxplot(x='Measured Date', y='Measured Data', data=filtered_data, width=0.6)
        
    # Adjust x-axis tick positions
    xtick_positions = range(len(data['Measured Date'].unique()))
    plt.xticks(xtick_positions, data['Measured Date'].unique(), rotation=90)

    # Set plot title and labels
    plt.title('Boxplot for Measured Data by Tag Number')
    plt.xlabel('Measured Date')
    plt.ylabel('Measured Data')

    # Show the plot
    plt.tight_layout()
    plt.show()
