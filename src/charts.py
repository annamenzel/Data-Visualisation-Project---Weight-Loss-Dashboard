# functions that build figures

import pandas as pd
import plotly.graph_objects as go


# ------ ADD CONSTANTS  ------
CATEGORY_ORDER = [
    "Meat",
    "Fish & Seafood",
    "Dairy & Eggs",
    "Veggies & Plant Protein",
    "Fruits",
    "Grains & Carbs",
    "Nuts & Seeds",
]

CATEGORY_SYMBOLS = {
    "Meat": "circle",
    "Fish & Seafood": "triangle-up",
    "Dairy & Eggs": "square",
    "Veggies & Plant Protein": "diamond",
    "Fruits": "star",
    "Grains & Carbs": "cross",
    "Nuts & Seeds": "x",
}

CATEGORY_COLORS = {
    "Meat": "#9F0042",                    # muted red
    "Fish & Seafood": "#3288BD",          # muted blue
    "Dairy & Eggs": "#FFCB1D",            # egg yellow
    "Veggies & Plant Protein": "#59A991", # teal green
    "Fruits": "#D63E4F",                  # grass green
    "Grains & Carbs": "#F4A731",          # bright orange
    "Nuts & Seeds": "#A8C455",            # lighter red
}

DEFAULT_GREY = "#B8B8B8"
FADED_GREY = "#B8B8B8"
SELECTED_COLOR = "#191A26"

MACRO_COLORS = {
    "Protein": "#453A79",  # purple
    "Carbs": "#F0DD97",    # beige
    "Fat": "#F46D43",      # orange
    "Fiber": "#ABDEA4",    # green
}

DONUT_GREY = "#D1D5DB"

# ------ HELPER FUNCTIONS ------
def _apply_common_layout(fig: go.Figure, title: str) -> go.Figure:
    wrapped_title = f"<span style='white-space:normal'>{title}</span>"

    fig.update_layout(
        title=dict(
            text=wrapped_title,
            x=0.02,
            xanchor="left",
            font=dict(size=18),
        ),
        template="plotly_white",
        margin=dict(t=60),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(size=12),
        hovermode="closest",
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#E5E7EB",
        zeroline=False,
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#E5E7EB",
        zeroline=False,
    )

    hoverlabel = dict(
        bgcolor="white",
        bordercolor="#11a8b5",
        font=dict(color="#0f2747", size=12),
    )

    return fig

def _range_with_padding(series: pd.Series, padding_ratio: float = 0.12) -> list[float]:
    min_val = series.min()
    max_val = series.max()

    if min_val == max_val:
        padding = max(abs(min_val) * padding_ratio, 1)
    else:
        padding = (max_val - min_val) * padding_ratio

    return [max(0, min_val - padding), max_val + padding]

def _category_color(category: str) -> str:
    return CATEGORY_COLORS.get(category, DEFAULT_GREY)

# ------ PLOT 1: Scatter (top left) ------

# Comparison of Foods based on Protein and Calories per 100 kcal

def create_protein_calorie_scatter(
    df: pd.DataFrame,
    selected_categories: list[str] | None = None,
    selected_food_id: int | None = None,
) -> go.Figure:
    """
    Scatterplot:
    x = calories per 100g
    y = protein per 100 kcal

    Default:
    all foods grey, categories distinguished by marker shape.

    If categories are selected:
    selected categories are highlighted in one color.

    If one food is selected:
    selected food is strongly highlighted, foods from the same category are lightly highlighted.
    """

    selected_categories = selected_categories or []

    fig = go.Figure()

    selected_food_category = None

    if selected_food_id is not None and selected_food_id in df["fdc_id"].values:
        selected_food_category = df.loc[
            df["fdc_id"] == selected_food_id, "final_category"
        ].iloc[0]

    for category in CATEGORY_ORDER:
        category_df = df[df["final_category"] == category].copy()

        if selected_food_id is not None:
            category_df = category_df[category_df["fdc_id"] != int(selected_food_id)]

        if category_df.empty:
            continue

        # Default styling
        color = DEFAULT_GREY
        opacity = 0.75
        size = 10
        line_color = "white"
        line_width = 0

        if selected_categories:
            if category in selected_categories:
                color = _category_color(category)
                opacity = 0.95
                size = 11

            else:
                color = FADED_GREY
                opacity = 0.15
                size = 8

        if selected_food_category is not None:
            if category == selected_food_category or category in selected_categories:
                color = _category_color(category)
                opacity = 0.9
                size = 11
            else:
                color = FADED_GREY
                opacity = 0.10
                size = 8

        fig.add_trace(
            go.Scatter(
                x=category_df["calories"],
                y=category_df["protein_per_100_kcal"],
                mode="markers",
                name=category,
                customdata=category_df[
                    [
                        "fdc_id",
                        "base_food",
                        "final_category",
                        "calories",
                        "protein",
                        "carbs",
                        "fat",
                        "fiber",
                        "sugar",
                        "sodium",
                        "fat_loss_score",
                    ]
                ],
                marker=dict(
                    symbol=CATEGORY_SYMBOLS.get(category, "circle"),
                    size=size,
                    color=color,
                    opacity=opacity,
                    line=dict(color=line_color, width=line_width),
                ),
                hovertemplate=(
                    "<b>%{customdata[1]}</b><br>"
                    "Category: %{customdata[2]}<br>"
                    "Calories: %{customdata[3]:.1f} kcal / 100g<br>"
                    "Protein: %{customdata[4]:.1f} g / 100g<br>"
                    "Carbs: %{customdata[5]:.1f} g / 100g<br>"
                    "Fat: %{customdata[6]:.1f} g / 100g<br>"
                    "Fiber: %{customdata[7]:.1f} g / 100g<br>"
                    "Sugar: %{customdata[8]:.1f} g / 100g<br>"
                    "Sodium: %{customdata[9]:.1f} mg / 100g<br>"
                    "Fat Loss Score: %{customdata[10]:.2f}"
                    "<extra></extra>"
                ),
            )
        )

    # Strong selected food marker on top
    if selected_food_id is not None and selected_food_id in df["fdc_id"].values:
        food_df = df[df["fdc_id"] == selected_food_id]

        fig.add_trace(
            go.Scatter(
                x=food_df["calories"],
                y=food_df["protein_per_100_kcal"],
                mode="markers",
                name="Selected food",
                customdata=food_df[
                    [
                        "fdc_id",
                        "food_name",
                        "final_category",
                        "calories",
                        "protein",
                        "carbs",
                        "fat",
                        "fiber",
                        "sugar",
                        "sodium",
                        "fat_loss_score",
                    ]
                ],
                marker=dict(
                    symbol=CATEGORY_SYMBOLS.get(selected_food_category, "circle"),
                    size=13,
                    color=SELECTED_COLOR,
                    opacity=1,
                    line=dict(color="black", width=0),
                ),
                hovertemplate=(
                    "<b>%{customdata[1]}</b><br>"
                    "Category: %{customdata[2]}<br>"
                    "Calories: %{customdata[3]:.1f} kcal / 100g<br>"
                    "Protein: %{customdata[4]:.1f} g / 100g<br>"
                    "Carbs: %{customdata[5]:.1f} g / 100g<br>"
                    "Fat: %{customdata[6]:.1f} g / 100g<br>"
                    "Fiber: %{customdata[7]:.1f} g / 100g<br>"
                    "Sugar: %{customdata[8]:.1f} g / 100g<br>"
                    "Sodium: %{customdata[9]:.1f} mg / 100g<br>"
                    "Fat Loss Score: %{customdata[10]:.2f}"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )

    fig.update_layout(
        dragmode="select",
        legend_title_text="Food category",
    )

    fig.update_xaxes(title_text="Calories per 100g")
    fig.update_yaxes(title_text="Protein per 100 kcal")

    fig = _apply_common_layout(
        fig,
        "Which foods give the most protein for the fewest calories?",
    )

    fig.update_layout(showlegend=False)

    if selected_categories:
        zoom_df = df[df["final_category"].isin(selected_categories)]

        if not zoom_df.empty:
            fig.update_xaxes(
                range=_range_with_padding(zoom_df["calories"])
            )
            fig.update_yaxes(
                range=_range_with_padding(zoom_df["protein_per_100_kcal"])
            )

    return fig

# ------ PLOT 2: Dot (bottom left) ------

# Macro-Comparison of Food Categories

def create_macro_comparison_dotplot(
    df: pd.DataFrame,
    selected_macro: str = "protein",
    selected_categories: list[str] | None = None,
    selected_food_id: int | None = None,
) -> go.Figure:

    selected_categories = selected_categories or []

    allowed_macros = ["protein", "carbs", "fat", "fiber", "sugar", "calories"]

    if selected_macro not in allowed_macros:
        selected_macro = "protein"

    fig = go.Figure()

    selected_food_category = None

    if selected_food_id is not None and int(selected_food_id) in df["fdc_id"].values:
        selected_food_category = df.loc[
            df["fdc_id"] == int(selected_food_id),
            "final_category"
        ].iloc[0]

    customdata_cols = [
        "fdc_id",
        "food_name",
        "final_category",
        "protein",
        "carbs",
        "fat",
        "fiber",
        "sugar",
        "calories",
        "fat_loss_score",
    ]

    hovertemplate = (
        "<b>%{customdata[1]}</b><br>"
        "Category: %{customdata[2]}<br>"
        "Protein: %{customdata[3]:.1f} g<br>"
        "Carbs: %{customdata[4]:.1f} g<br>"
        "Fat: %{customdata[5]:.1f} g<br>"
        "Fiber: %{customdata[6]:.1f} g<br>"
        "Sugar: %{customdata[7]:.1f} g<br>"
        "Calories: %{customdata[8]:.1f} kcal<br>"
        "Fat Loss Score: %{customdata[9]:.2f}"
        "<extra></extra>"
    )

    for category in CATEGORY_ORDER:
        category_df = df[df["final_category"] == category].copy()

        if selected_food_id is not None:
            category_df = category_df[category_df["fdc_id"] != int(selected_food_id)]

        if category_df.empty:
            continue

        color = DEFAULT_GREY
        opacity = 0.75
        size = 10

        # Category filter (grey system only)
        if selected_categories:
            if category in selected_categories:
                color = "#6F6F6F"  # darker grey
                opacity = 0.9
                size = 11
            else:
                color = FADED_GREY
                opacity = 0.2
                size = 8

        # Selected food mode
        if selected_food_category is not None:
            if category == selected_food_category:
                color = "#6F6F6F"  # still grey, not colored
                opacity = 0.9
                size = 11
            elif selected_categories and category in selected_categories:
                color = "#6F6F6F"
                opacity = 0.7
                size = 10
            else:
                color = FADED_GREY
                opacity = 0.15
                size = 8

        fig.add_trace(
            go.Scatter(
                x=[category] * len(category_df),
                y=category_df[selected_macro],
                mode="markers",
                name=category,
                customdata=category_df[customdata_cols],
                marker=dict(
                    symbol=CATEGORY_SYMBOLS.get(category, "circle"),
                    size=size,
                    color=color,
                    opacity=opacity,
                    line=dict(width=0),
                ),
                hovertemplate=hovertemplate,
            )
        )

    if selected_food_id is not None and int(selected_food_id) in df["fdc_id"].values:
        food_df = df[df["fdc_id"] == int(selected_food_id)]

        fig.add_trace(
            go.Scatter(
                x=food_df["final_category"],
                y=food_df[selected_macro],
                mode="markers",
                name="Selected food",
                customdata=food_df[customdata_cols],
                marker=dict(
                    symbol=CATEGORY_SYMBOLS.get(selected_food_category, "circle"),
                    size=13,
                    color=SELECTED_COLOR,
                    opacity=1,
                    line=dict(width=0),
                ),
                hovertemplate=hovertemplate,
                showlegend=False,
            )
        )

    fig.update_yaxes(title_text=f"{selected_macro.capitalize()} per 100g")

    fig = _apply_common_layout(
        fig,
        f"How do foods compare by {selected_macro}?",
    )

    fig.update_layout(showlegend=False)

    if selected_categories:
        zoom_df = df[df["final_category"].isin(selected_categories)]

        if not zoom_df.empty:
            fig.update_yaxes(range=_range_with_padding(zoom_df[selected_macro]))

    return fig

# ------ PLOT 3: Bar Plot (top right) ------

# Ranking of Food Categories Best for Weight Loss

def create_category_ranking_bar(
    df: pd.DataFrame,
    selected_categories: list[str] | None = None,
    selected_food_id: int | None = None,
) -> go.Figure:
    """
    Horizontal bar chart:
    Ranking of food categories by average fat loss score.
    """

    selected_categories = selected_categories or []

    category_summary = (
        df.groupby("final_category", as_index=False)
        .agg({
            "fat_loss_score": "mean",
            "calories": "mean",
            "protein": "mean",
            "carbs": "mean",
            "fat": "mean",
            "fiber": "mean",
            "sugar": "mean",
        })
        .sort_values("fat_loss_score", ascending=True)
    )

    selected_food_category = None

    if selected_food_id is not None and selected_food_id in df["fdc_id"].values:
        selected_food_category = df.loc[
            df["fdc_id"] == selected_food_id,
            "final_category"
        ].iloc[0]

    colors = []

    for category in category_summary["final_category"]:
        color = DEFAULT_GREY

        if selected_categories:
            if category in selected_categories:
                color = "#6F6F6F"  # darker grey for selected categories
            else:
                color = FADED_GREY

        if selected_food_category is not None:
            food_category_is_active = (
                    not selected_categories
                    or selected_food_category in selected_categories
            )

            if food_category_is_active and category == selected_food_category:
                color = SELECTED_COLOR

        colors.append(color)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=category_summary["fat_loss_score"],
            y=category_summary["final_category"],
            orientation="h",
            marker=dict(
                color=colors,
                line=dict(color="white", width=1),
            ),
            customdata=category_summary[
                [
                    "calories",
                    "protein",
                    "carbs",
                    "fat",
                    "fiber",
                    "sugar",
                ]
            ],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Average Fat Loss Score: %{x:.2f}<br>"
                "Avg Calories: %{customdata[0]:.1f} kcal<br>"
                "Avg Protein: %{customdata[1]:.1f} g<br>"
                "Avg Carbs: %{customdata[2]:.1f} g<br>"
                "Avg Fat: %{customdata[3]:.1f} g<br>"
                "Avg Fiber: %{customdata[4]:.1f} g<br>"
                "Avg Sugar: %{customdata[5]:.1f} g"
                "<extra></extra>"
            ),
            text=category_summary["fat_loss_score"].round(1),
            textposition="inside",
            insidetextanchor="end",
            textfont=dict(color="white", size=11),
        )
    )

    fig.update_xaxes(title_text="Average Fat Loss Score")

    fig = _apply_common_layout(
        fig,
        "Which food categories perform best for fat loss?",
    )

    fig.update_layout(
        showlegend=False,
    )

    return fig

# ------ PLOT 4: Bar Plot  (middle right) ------

# Top 10 Foods for Weight Loss per Category

def create_top_foods_bar(
    df: pd.DataFrame,
    selected_categories: list[str] | None = None,
    selected_food_id: int | None = None,
    top_n: int = 10,
) -> go.Figure:
    selected_categories = selected_categories or []

    chart_df = df.copy()
    selected_food_category = None

    # Find selected food category if a food is selected
    if selected_food_id is not None and selected_food_id in df["fdc_id"].values:
        selected_food_category = df.loc[
            df["fdc_id"] == selected_food_id,
            "final_category"
        ].iloc[0]

    # Main filtering logic
    if selected_categories:
        chart_df = chart_df[chart_df["final_category"].isin(selected_categories)]
    elif selected_food_category is not None:
        chart_df = chart_df[chart_df["final_category"] == selected_food_category]

    # Safety fallback if filtering accidentally returns nothing
    if chart_df.empty:
        chart_df = df.copy()

    top_df = (
        chart_df.sort_values("fat_loss_score", ascending=False)
        .head(top_n)
        .copy()
    )

    colors = []

    for _, row in top_df.iterrows():
        category = row["final_category"]

        if selected_food_id is not None and row["fdc_id"] == selected_food_id:
            colors.append(SELECTED_COLOR)
        elif selected_categories:
            if category == selected_food_category:
                colors.append(_category_color(category))
            else:
                colors.append(DEFAULT_GREY)
        elif selected_food_category is not None:
            colors.append(_category_color(category))
        else:
            colors.append(DEFAULT_GREY)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=top_df["base_food"],
            y=top_df["fat_loss_score"],
            marker=dict(
                color=colors,
                line=dict(color="white", width=1),
            ),
            customdata=top_df[
                [
                    "fdc_id",
                    "base_food",
                    "final_category",
                    "calories",
                    "protein",
                    "carbs",
                    "fat",
                    "fiber",
                    "sugar",
                    "sodium",
                ]
            ],
            hovertemplate=(
                "<b>%{customdata[1]}</b><br>"
                "Category: %{customdata[2]}<br>"
                "Fat Loss Score: %{y:.2f}<br>"
                "Calories: %{customdata[3]:.1f} kcal / 100g<br>"
                "Protein: %{customdata[4]:.1f} g / 100g<br>"
                "Carbs: %{customdata[5]:.1f} g / 100g<br>"
                "Fat: %{customdata[6]:.1f} g / 100g<br>"
                "Fiber: %{customdata[7]:.1f} g / 100g<br>"
                "Sugar: %{customdata[8]:.1f} g / 100g<br>"
                "Sodium: %{customdata[9]:.1f} mg / 100g"
                "<extra></extra>"
            ),
            text=top_df["fat_loss_score"].round(1),
            textposition="inside",
            textfont=dict(color="white", size=10),
        )
    )

    title = "Which foods rank highest for fat loss?"

    if selected_categories:
        title = "Top 10 foods in selected categories"
    elif selected_food_category is not None:
        title = f"Top 10 foods in {selected_food_category}"

    fig.update_xaxes(
        title_text="",
        tickangle=-30,
    )

    fig.update_yaxes(title_text="Fat Loss Score")

    fig = _apply_common_layout(fig, title)

    fig.update_layout(
        showlegend=False,
        margin=dict(l=45, r=20, t=45, b=70),
    )

    return fig

# ------ PLOT 5: Donut Chart (bottom right) ------

# Macro-Nutrient Composition per 100g per Food

def create_macro_donut(
    df: pd.DataFrame,
    selected_food_id: int | None = None,
) -> go.Figure:
    """
    Donut chart:
    Shows macro composition for one selected food.

    If no food is selected, show a neutral placeholder donut.
    """

    fig = go.Figure()

    # Empty/default state
    if selected_food_id is None or selected_food_id not in df["fdc_id"].values:
        fig.add_trace(
            go.Pie(
                labels=["Select a food"],
                values=[1],
                hole=0.65,
                marker=dict(colors=[DONUT_GREY]),
                textinfo="label",
                hoverinfo="skip",
                sort=False,
            )
        )

        fig.update_layout(
            title="Select a food to see its macro composition",
            template="plotly_white",
            margin=dict(l=20, r=20, t=70, b=30),
            showlegend=False,
            annotations=[
                dict(
                    text="No food<br>selected",
                    x=0.5,
                    y=0.5,
                    font_size=14,
                    showarrow=False,
                )
            ],
        )

        return fig

    food = df[df["fdc_id"] == selected_food_id].iloc[0]

    labels = ["Protein", "Carbs", "Fat", "Fiber"]
    values = [
        food["protein"],
        food["carbs"],
        food["fat"],
        food["fiber"],
    ]

    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.65,
            marker=dict(colors=[MACRO_COLORS[label] for label in labels]),
            textinfo="none",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "%{value:.1f} g per 100g<br>"
                "%{percent}"
                "<extra></extra>"
            ),
            sort=False,
        )
    )

    fig.update_layout(
        title=f"Macro composition: {food['base_food']}",
        template="plotly_white",
        margin=dict(l=20, r=20, t=70, b=30),
        showlegend=True,
        legend_title_text="Macro",
        annotations=[
            dict(
                text=(
                    f"<b>{food['calories']:.0f}</b><br>"
                    "kcal / 100g<br>"
                    f"Score: {food['fat_loss_score']:.1f}"
                ),
                x=0.5,
                y=0.5,
                font_size=13,
                showarrow=False,
            )
        ],
    )

    return fig