from __future__ import annotations

from dash import dcc, html
import pandas as pd

from charts import (
    create_category_ranking_bar,
    create_macro_comparison_dotplot,
    create_macro_donut,
    create_protein_calorie_scatter,
    create_top_foods_bar,
)

def info_tooltip(text: str) -> html.Div:
    return html.Div(
        className="info-tooltip",
        children=[
            html.Span("?", className="info-icon"),
            html.Div(text, className="info-tooltip-text"),
        ],
    )


def create_layout(df: pd.DataFrame) -> html.Div:
    category_options = [
        {"label": "All Categories", "value": "ALL"},
        *[
            {"label": category, "value": category}
            for category in sorted(df["final_category"].dropna().unique())
        ],
    ]

    macro_options = [
        {"label": "Protein", "value": "protein"},
        {"label": "Carbs", "value": "carbs"},
        {"label": "Fat", "value": "fat"},
        {"label": "Fiber", "value": "fiber"},
        {"label": "Sugar", "value": "sugar"},
        {"label": "Calories", "value": "calories"},
    ]

    food_options = [
        {
            "label": row["base_food"],
            "value": int(row["fdc_id"]),
        }
        for _, row in df.sort_values("base_food").iterrows()
    ]

    return html.Div(
        className="app-container",
        children=[
            html.Div(
                className="header",
                children=[
                    html.H1("Best Foods for Fat Loss Dashboard"),
                ],
            ),

            html.Div(
                className="controls-row",
                children=[
                    html.Div(
                        className="control-card",
                        children=[
                            html.Label("Filter by category"),
                            html.Div(
                                dcc.Checklist(
                                    id="category-selector",
                                    options=[
                                        {"label": "● Meat", "value": "Meat"},
                                        {"label": "▲ Fish & Seafood", "value": "Fish & Seafood"},
                                        {"label": "■ Dairy & Eggs", "value": "Dairy & Eggs"},
                                        {"label": "◆ Veggies & Plant Protein", "value": "Veggies & Plant Protein"},
                                        {"label": "★ Fruits", "value": "Fruits"},
                                        {"label": "✚ Grains & Carbs", "value": "Grains & Carbs"},
                                        {"label": "✕ Nuts & Seeds", "value": "Nuts & Seeds"},
                                    ],
                                    value=[],
                                    inline=True,
                                ),
                                className="category-checklist"
                            ),
                        ],
                    ),
                    html.Div(
                        className="control-card",
                        children=[
                            html.Label("Compare by macro"),
                            dcc.Dropdown(
                                id="macro-dropdown",
                                options=macro_options,
                                value="protein",
                                clearable=False,
                            ),
                        ],
                    ),
                    html.Div(
                        className="control-card",
                        children=[
                            html.Label("Select a food"),
                            dcc.Dropdown(
                                id="food-dropdown",
                                options=food_options,
                                placeholder="Choose a food...",
                                clearable=True,
                            ),
                        ],
                    ),
                ],
            ),

            html.Div(
                className="dashboard-grid",
                children=[
                    html.Div(
                        className="left-column",
                        children=[
                            html.Div(
                                className="chart-card",
                                children=[
                                    info_tooltip(
                                        "Shows calories per 100g against protein per 100 kcal. Foods higher up and further left are leaner protein sources."
                                    ),
                                    dcc.Graph(
                                        id="scatter-plot",
                                        className="graph-large",
                                        style={"height": "100%"},
                                        figure=create_protein_calorie_scatter(df),
                                        config={"displayModeBar": False, "responsive": True},
                                    )
                                ],
                            ),
                            html.Div(
                                className="chart-card",
                                children=[
                                    info_tooltip(
                                        "Compares all foods by the selected macro. Use this to see which categories are stronger in protein, carbs, fat, fiber, sugar, or calories."
                                    ),
                                    dcc.Graph(
                                        id="macro-dot-plot",
                                        className="graph-large",
                                        style={"height": "100%"},
                                        figure=create_macro_comparison_dotplot(df),
                                        config={"displayModeBar": False, "responsive": True},
                                    )
                                ],
                            ),
                        ],
                    ),

                    html.Div(
                        className="right-column",
                        children=[
                            html.Div(
                                className="chart-card",
                                children=[
                                    info_tooltip(
                                        "Ranks food categories by average Fat Loss Score. The score rewards protein and fiber density and penalizes sugar and calories."
                                    ),
                                    dcc.Graph(
                                        id="category-ranking-bar",
                                        className="graph-small",
                                        style={"height": "100%"},
                                        figure=create_category_ranking_bar(df),
                                        config={"displayModeBar": False, "responsive": True},
                                    )
                                ],
                            ),
                            html.Div(
                                className="chart-card",
                                children=[
                                    info_tooltip(
                                        "Shows the top foods based on Fat Loss Score for the currently selected categories."
                                    ),
                                    dcc.Graph(
                                        id="top-foods-bar",
                                        className="graph-small",
                                        style={"height": "100%"},
                                        figure=create_top_foods_bar(df),
                                        config={"displayModeBar": False, "responsive": True},
                                    )
                                ],
                            ),
                            html.Div(
                                className="chart-card",
                                children=[
                                    info_tooltip(
                                        "Shows the macro composition of the selected food per 100g. Hover over slices for exact values."
                                    ),
                                    dcc.Graph(
                                        id="macro-donut",
                                        className="graph-small",
                                        style={"height": "100%"},
                                        figure=create_macro_donut(df),
                                        config={"displayModeBar": False, "responsive": True},
                                    )
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )