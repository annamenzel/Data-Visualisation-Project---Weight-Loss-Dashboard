from __future__ import annotations

from pathlib import Path
import pandas as pd


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "fat_loss_foods_dashboard_final.csv"


def load_dashboard_data() -> pd.DataFrame:
    """Load and prepare the final dashboard dataset."""

    df = pd.read_csv(DATA_PATH)

    # Drop only columns we do not need in the dashboard.
    # Keep fdc_id because we need it for click/selection callbacks.
    columns_to_drop = [
        "prep_preference",
        "fiber_capped",
        "category",
        "food_category_id",
    ]

    df = df.drop(columns=columns_to_drop, errors="ignore")

    # Ensure important numeric columns are numeric.
    numeric_cols = [
        "protein",
        "fat",
        "carbs",
        "calories",
        "fiber",
        "sodium",
        "sugar",
        "protein_per_100_kcal",
        "fiber_per_100_kcal",
        "sugar_per_100_kcal",
        "fat_loss_score",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Round only for display/readability.
    round_cols = [
        "protein",
        "fat",
        "carbs",
        "calories",
        "fiber",
        "sodium",
        "sugar",
        "protein_per_100_kcal",
        "fiber_per_100_kcal",
        "sugar_per_100_kcal",
        "fat_loss_score",
    ]

    for col in round_cols:
        if col in df.columns:
            df[col] = df[col].round(1)

    # Sort by score so the dataset has a meaningful default order.
    df = df.sort_values("fat_loss_score", ascending=False).reset_index(drop=True)

    return df