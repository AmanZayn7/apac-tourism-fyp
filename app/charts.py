"""Forecast-only plots with a fixed twelve-month axis and shared display values."""

import plotly.graph_objects as go

INK = "#1E4052"
PALETTE = ["#168B80", "#CB6247", "#6266AD"]


def style(fig, title, height=420):
    fig.update_layout(
        title=dict(text=title, font=dict(size=17, color=INK)),
        height=height,
        margin=dict(l=12, r=16, t=58, b=45),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", color=INK, size=12),
        hovermode="x unified",
        yaxis_title="Predicted monthly arrivals",
        legend=dict(orientation="h", y=-0.22),
    )
    fig.update_yaxes(gridcolor="#E1E7DF", rangemode="tozero", tickformat=",")
    return fig


def forecast_chart(frames, labels, accent, *, band=False, selected_month=None):
    """Each frame has exactly 12 future rows; category axis cannot invent a 13th tick."""
    fig = go.Figure()
    months = frames[0]["date"].dt.strftime("%b %Y").tolist() if frames else []
    colors = [accent] + [color for color in PALETTE if color != accent]
    if band and frames:
        frame = frames[0]
        fig.add_trace(
            go.Scatter(
                x=months,
                y=frame["upper"],
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=months,
                y=frame["lower"],
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(25,143,131,.13)",
                name="Historical error reference",
                hoverinfo="skip",
            )
        )
    for index, (frame, label) in enumerate(zip(frames, labels)):
        fig.add_trace(
            go.Scatter(
                x=frame["date"].dt.strftime("%b %Y"),
                y=frame["forecast_arrivals"],
                name=label,
                mode="lines+markers",
                line=dict(
                    color=colors[index % 3],
                    width=3 if index == 0 else 2,
                    dash=["solid", "dash", "dot"][index % 3],
                ),
                marker=dict(size=[11 if d == selected_month else 6 for d in frame["date"]]),
                hovertemplate="%{x}<br>%{y:,d} predicted arrivals<extra>%{fullData.name}</extra>",
            )
        )
    fig = style(fig, "Your twelve-month forecast")
    fig.update_xaxes(
        type="category",
        categoryorder="array",
        categoryarray=months,
        tickmode="array",
        tickvals=months,
        ticktext=[m.replace(" ", "<br>") for m in months],
        range=[-0.35, 11.35],
        fixedrange=True,
    )
    return fig


def ranking_chart(comparison, metric, label, selected, labels, accent):
    frame = comparison.sort_values(metric, ascending=metric != "r2")
    fig = go.Figure(
        go.Bar(
            x=frame[metric],
            y=frame["model"].map(labels),
            orientation="h",
            marker_color=[accent if m == selected else "#C8D7D9" for m in frame["model"]],
            hovertemplate="%{y}<br>%{x:,.2f}<extra></extra>",
        )
    )
    fig = style(fig, label, height=340)
    fig.update_layout(yaxis_title=None, xaxis_title=label, showlegend=False)
    fig.update_yaxes(autorange="reversed", rangemode="normal")
    return fig
