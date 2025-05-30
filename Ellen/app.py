import os, re, base64, pandas as pd, plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# ──────────────── Load Data ────────────────
DATA_DIR = "csv_data/wta_womens_tour"
df_all = pd.concat(
    [pd.read_csv(os.path.join(DATA_DIR, f), low_memory=False)
     for f in os.listdir(DATA_DIR) if f.endswith(".csv")],
    ignore_index=True,
)
df_all["Date"] = pd.to_datetime(df_all["Date"], errors="coerce")
for col in ["B365W", "B365L"]:
    df_all[col] = pd.to_numeric(df_all[col], errors="coerce")
df_all = df_all.dropna(subset=["B365W", "B365L", "WRank", "LRank"])

# ──────────────── Tier Parser ────────────────
def parse_event_tier(row):
    tname = str(row.get("Tournament", "")).lower()
    if any(s in tname for s in ["australian open", "roland garros", "wimbledon", "us open"]):
        return 6, "Grand Slam"
    if "wta finals" in tname or "tour championships" in tname or row.get("tourney_level") == "F":
        return 5, "WTA Finals"

    tier_raw = str(row.get("Tier", "")).strip()
    m = re.match(r"^wta\s*(\d+)$", tier_raw, flags=re.I)
    if m:
        n = int(m.group(1))
        if n >= 1000: return 4, "WTA 1000"
        if n >= 500: return 3, "WTA 500"
        return 2, "WTA 250"

    series = str(row.get("Series", "")).lower()
    if "1000" in series or "mandatory" in series or "premier 5" in series:
        return 4, "WTA 1000"
    if "500" in series or series == "premier":
        return 3, "WTA 500"
    if "250" in series or "international" in series:
        return 2, "WTA 250"
    if "125" in series:
        return 1, "125 / ITF"

    code = str(row.get("tourney_level", "")).upper()
    if code == "M": return 4, "WTA 1000"
    if code == "P": return 3, "WTA 500"
    if code in {"I", "B"}: return 2, "WTA 250"

    tier_map_txt = {"tier i": (4, "WTA 1000"),
                    "tier ii": (3, "WTA 500"),
                    "tier iii": (2, "WTA 250"),
                    "tier iv": (1, "125 / ITF")}
    if tier_map_txt.get(tier_raw.lower()):
        return tier_map_txt[tier_raw.lower()]
    if tier_raw.lstrip("-").isdigit():
        n = abs(int(tier_raw))
        return {1: (4, "WTA 1000"),
                2: (3, "WTA 500"),
                3: (2, "WTA 250"),
                4: (1, "125 / ITF")}.get(n, (1, "125 / ITF"))

    return 1, "125 / ITF"

df_all[["TierSize", "TierCat"]] = df_all.apply(parse_event_tier, axis=1, result_type="expand")

# ──────────────── Images (from docs/assets/img) ────────────────
def encode_image(file_path):
    with open(file_path, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

surface_images = {
    "Hard":  "../docs/assets/img/hard.jpeg",
    "Clay":  "../docs/assets/img/clay.jpg",
    "Grass": "../docs/assets/img/grass.jpg",
}
surface_bg = {s.lower(): "data:image/jpeg;base64," +
              base64.b64encode(open(p, "rb").read()).decode()
              for s, p in surface_images.items()}

TIER_LOGOS = {
    "Grand Slam": {
        "australian": "../docs/assets/img/ao.png",
        "roland":     "../docs/assets/img/rg.png",
        "wimbledon":  "../docs/assets/img/wimbledon.png",
        "us open":    "../docs/assets/img/usopen.png"
    },
    "WTA 1000": "../docs/assets/img/logo-wta1000-black-1.png",
    "WTA 500":  "../docs/assets/img/wta500.png",
    "WTA 250":  "../docs/assets/img/wta250.png",
    "WTA Finals": "../docs/assets/img/wtafinals.png",
    "125 / ITF":  "../docs/assets/img/wta125.png"
}

# ──────────────── Dash App ────────────────
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server
app.title = "WTA Underdogs vs Top-10"

app.layout = html.Div([
    html.H2("🎾 Underdog Wins vs Top-10 (WTA)", style={"textAlign": "center", "marginTop": 20}),
    html.Label("Year:"),
    dcc.Slider(
        id="year-input",
        min=df_all["Date"].dt.year.min(),
        max=df_all["Date"].dt.year.max(),
        step=1,
        value=2024,
        marks={y: str(y) for y in range(2005, 2025)},
        tooltip={"placement": "bottom"}
    ),
    html.Br(),
    html.Label("Surface:"),
    dcc.Dropdown(
        id="surface-dropdown",
        options=[{"label": s, "value": s} for s in ["Hard", "Clay", "Grass"]],
        placeholder="Select Surface",
    ),
    html.Br(),
    html.Label("Top-10 Opponent (optional):"),
    dcc.Dropdown(id="player-dropdown", placeholder="Select a player", clearable=True),
    html.Div(id="summary-text", style={"color": "teal", "marginTop": 20, "fontWeight": "bold"}),
    dcc.Graph(id="underdog-plot", config={"displayModeBar": False}),
], style={"width": "85%", "margin": "0 auto"})

# ──────────────── Callbacks ────────────────
@app.callback(
    Output("player-dropdown", "options"),
    Input("year-input", "value"),
)
def populate_top10(year):
    if not year:
        return []
    y = df_all[df_all["Date"].dt.year == int(year)]
    tops = pd.concat([
        y[y["WRank"] <= 10][["Winner", "WRank"]],
        y[y["LRank"] <= 10][["Loser", "LRank"]].rename(columns={"Loser": "Winner", "LRank": "WRank"})
    ])
    names = tops.sort_values("WRank")["Winner"].dropna().drop_duplicates().head(10)
    return [{"label": n, "value": n} for n in names]

@app.callback(
    Output("summary-text", "children"),
    Input("year-input", "value"),
    Input("surface-dropdown", "value"),
    Input("player-dropdown", "value"),
)
def update_summary_text(year, surface, opponent):
    if not year or not surface:
        return "Please select a year and a surface."
    msg = f"\U0001F3BE Showing underdog wins vs Top-10 players on **{surface}** courts in **{year}**."
    if opponent:
        msg += f" Filtered by matches against **{opponent}**."
    return msg

@app.callback(
    Output("underdog-plot", "figure"),
    Input("year-input", "value"),
    Input("surface-dropdown", "value"),
    Input("player-dropdown", "value"),
)
def make_chart(year, surface, opponent):
    if not year or not surface:
        return px.scatter(title="Select year and surface")

    df = df_all[
        (df_all["Date"].dt.year == int(year)) &
        (df_all["Surface"].str.lower() == surface.lower()) &
        (((df_all["WRank"] <= 10) & (df_all["LRank"].between(11, 100))) |
         ((df_all["LRank"] <= 10) & (df_all["WRank"].between(11, 100))))
    ].copy()

    if df.empty:
        return px.scatter(title="No matches found")

    df["Underdog"], df["Odds"] = zip(*df.apply(
        lambda r: (r["Winner"], r["B365W"]) if r["WRank"] > r["LRank"]
        else (r["Loser"], r["B365L"]), axis=1))
    df["Won"]    = df["Winner"] == df["Underdog"]
    df["Return"] = df["Odds"].where(df["Won"], 0)
    df["UDRank"] = df.apply(lambda r: r["WRank"] if r["Won"] else r["LRank"], axis=1)

    if opponent:
        df = df[df["Loser"] == opponent]
    if df.empty:
        return px.scatter(title="No matches with that filter")

    agg = df.groupby("Underdog", as_index=False).agg(
        AvgRank=("UDRank", "mean"),
        AvgReturn=("Return", "mean"),
        TierSize=("TierSize", "max"),
        TierCat=("TierCat", "max")
    )

    fig = px.scatter(
        agg, x="AvgRank", y="AvgReturn",
        size=[30] * len(agg),
        hover_name="Underdog",
        title=f"Underdog vs Top-10 on {surface} • {year}"
    )
    fig.update_traces(marker=dict(opacity=0))

    for _, row in agg.iterrows():
        tier = row["TierCat"]
        x, y = row["AvgRank"], row["AvgReturn"]
        logo_path = None
        if tier == "Grand Slam":
            tournaments = df_all[df_all["Winner"] == row["Underdog"]]["Tournament"].dropna().unique()
            t_match = next((t for t in tournaments if any(k in t.lower() for k in TIER_LOGOS["Grand Slam"])), None)
            if t_match:
                logo_key = next((k for k in TIER_LOGOS["Grand Slam"] if k in t_match.lower()), None)
                if logo_key:
                    logo_path = TIER_LOGOS["Grand Slam"][logo_key]
        else:
            logo_path = TIER_LOGOS.get(tier)

        if logo_path and os.path.exists(logo_path):
            fig.add_layout_image(dict(
                source=encode_image(logo_path),
                xref="x", yref="y",
                x=x, y=y,
                sizex=3, sizey=0.6,
                xanchor="center", yanchor="middle",
                layer="above"
            ))

    fig.update_layout(
        xaxis_title="Average Rank (1 = best)",
        yaxis_title="Average Return on $1 Stake (Bet365)",
        xaxis_autorange="reversed",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        images=[{
            "source": surface_bg.get(surface.strip().lower()),
            "xref": "paper", "yref": "paper",
            "x": 0, "y": 1, "sizex": 1, "sizey": 1,
            "xanchor": "left", "yanchor": "top",
            "layer": "below", "sizing": "stretch",
            "opacity": 0.5,
        }] if surface_bg.get(surface.strip().lower()) else [],
    )
    return fig

# ──────────────── Run Server ────────────────
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8080)
