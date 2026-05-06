from __future__ import annotations

import pandas as pd
from dash import Input, Output, State, no_update, ctx

from charts import (
    create_category_ranking_bar,
    create_macro_comparison_dotplot,
    create_macro_donut,
    create_protein_calorie_scatter,
    create_top_foods_bar,
)


def register_callbacks(app, df: pd.DataFrame) -> None:

    @app.callback(
        Output("scatter-plot", "figure"),
        Output("macro-dot-plot", "figure"),
        Output("category-ranking-bar", "figure"),
        Output("top-foods-bar", "figure"),
        Input("category-selector", "value"),
        Input("macro-dropdown", "value"),
        Input("food-dropdown", "value"),
    )
    def update_category_and_macro(selected_categories, selected_macro, selected_food_id):
        selected_categories = selected_categories or []

        return (
            create_protein_calorie_scatter(df, selected_categories, selected_food_id),
            create_macro_comparison_dotplot(df, selected_macro, selected_categories, selected_food_id),
            create_category_ranking_bar(df, selected_categories, selected_food_id),
            create_top_foods_bar(df, selected_categories, selected_food_id),
        )

    @app.callback(
        Output("macro-donut", "figure"),
        Input("food-dropdown", "value"),
    )
    def update_donut(selected_food_id):
        return create_macro_donut(df, selected_food_id=selected_food_id)

    @app.callback(
        Output("food-dropdown", "value", allow_duplicate=True),
        Input("scatter-plot", "clickData"),
        State("food-dropdown", "value"),
        prevent_initial_call=True,
    )
    def update_food_from_scatter_click(click_data, current_food_id):
        return _toggle_food_selection(click_data, current_food_id)

    @app.callback(
        Output("food-dropdown", "value", allow_duplicate=True),
        Input("top-foods-bar", "clickData"),
        State("food-dropdown", "value"),
        prevent_initial_call=True,
    )
    def update_food_from_top_foods_click(click_data, current_food_id):
        return _toggle_food_selection(click_data, current_food_id)

    @app.callback(
        Output("food-dropdown", "value", allow_duplicate=True),
        Input("macro-dot-plot", "clickData"),
        State("food-dropdown", "value"),
        prevent_initial_call=True,
    )
    def update_food_from_dotplot_click(click_data, current_food_id):
        return _toggle_food_selection(click_data, current_food_id)

    @app.callback(
        Output("food-dropdown", "value", allow_duplicate=True),
        Input("category-selector", "value"),
        State("food-dropdown", "value"),
        prevent_initial_call=True,
    )
    def clear_food_if_category_removed(selected_categories, selected_food_id):
        selected_categories = selected_categories or []

        if selected_food_id is None:
            return no_update

        if not selected_categories:
            return None

        selected_food_category = df.loc[
            df["fdc_id"] == int(selected_food_id),
            "final_category"
        ].iloc[0]

        if selected_food_category not in selected_categories:
            return None

        return no_update

    @app.callback(
        Output("category-selector", "value"),
        Input("food-dropdown", "value"),
        State("category-selector", "value"),
        prevent_initial_call=True,
    )
    def add_food_category_to_selector(selected_food_id, selected_categories):
        selected_categories = selected_categories or []

        if ctx.triggered_id != "food-dropdown":
            return no_update

        if selected_food_id is None:
            return no_update

        selected_food_category = df.loc[
            df["fdc_id"] == int(selected_food_id),
            "final_category"
        ].iloc[0]

        if selected_food_category not in selected_categories:
            return selected_categories + [selected_food_category]

        return no_update


def _toggle_food_selection(click_data, current_food_id):
    if not click_data or "points" not in click_data:
        return no_update

    customdata = click_data["points"][0].get("customdata")

    if customdata is None:
        return no_update

    clicked_food_id = int(customdata[0])

    if current_food_id is not None and clicked_food_id == int(current_food_id):
        return None

    return clicked_food_id