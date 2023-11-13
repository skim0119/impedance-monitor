# MEA Impedance Dashboard

This repository build a dashboard for the experimental data.
Database is stored in private google drive (spreadsheet), and `plotly` is used for interactive graphs.
Lastly, `Dash` is used to build the reactive GUI.

## Pipeline

```mermaid
flowchart TD
    experiment["Experiment"]
    collect[("Impedance Collection")]

    proc1["fetch impedance database"]
    proc2["fetch MEA catalogue"]
    proc3["build interactive page"]
    proc4["deploy"]

    experiment --> collect
    collect -->|google oauth token| proc1
    collect -->|google oauth token| proc2
    proc1 --> proc3
    proc2 --> proc3
    proc3 -->|dash| proc4
```

> User need to setup 'credentials.json' in the root directory to use google drive API. See [here](https://developers.google.com/drive/api/v3/quickstart/python) for more details.
> First time running the code will require user to authorize the app to access google drive.
> Generated token.json' will be used for future access. It should not be commited to github for security reasons.
