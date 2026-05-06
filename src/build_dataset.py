import pandas as pd
from pathlib import Path


# ------ SET ALL PATHS AND LOAD DATA ------
# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Load raw USDA files

# food tables
food_foundation = pd.read_csv(RAW_DIR / "food.csv")
food_sr = pd.read_csv(RAW_DIR / "food_sr_legacy.csv")
# nutrient information
food_nutrient_foundation = pd.read_csv(RAW_DIR / "food_nutrient.csv")
food_nutrient_sr = pd.read_csv(RAW_DIR / "food_nutrient_sr_legacy.csv", low_memory=False)
# shared lookup tables
nutrient = pd.read_csv(RAW_DIR / "nutrient.csv")
food_category = pd.read_csv(RAW_DIR / "food_category.csv")

# ------ EDA ------
# investigate tables: shapes + column names
print("food shape:", food_foundation.shape)
print("food_sr shape:", food_sr.shape)
print("food_nutrient shape:", food_nutrient_foundation.shape)
print("food_nutrient_sr shape:", food_nutrient_sr.shape)
print("nutrient shape:", nutrient.shape)
print("food_category shape:", food_category.shape)

print("Foundation food columns:", food_foundation.columns.tolist())
print("SR food columns:", food_sr.columns.tolist())
print()

print("Foundation food_nutrient columns:", food_nutrient_foundation.columns.tolist())
print("SR food_nutrient columns:", food_nutrient_sr.columns.tolist())
print()

print("Nutrient columns:", nutrient.columns.tolist())
print("Food category columns:", food_category.columns.tolist())
print()

print("Sample SR food rows:")
print(food_sr.head().to_string())

print("\nSample SR food_nutrient rows:")
print(food_nutrient_sr.head().to_string())

# combine foundation and sr table

food = pd.concat([food_foundation, food_sr], ignore_index=True)
food_nutrient = pd.concat([food_nutrient_foundation, food_nutrient_sr], ignore_index=True)

print("Combined food shape:", food.shape)
print("Combined food_nutrient shape:", food_nutrient.shape)
print("nutrient shape:", nutrient.shape)
print("food_category shape:", food_category.shape)

# search for nutrient search results
print("\nRelevant nutrient search results:")

keywords = ["Energy", "Protein", "Carbohydrate", "Fat", "Fiber", "Sodium", "Sugar"]

for keyword in keywords:
    print(f"\n--- Searching for: {keyword} ---")
    matches = nutrient[nutrient["name"].str.contains(keyword, case=False, na=False)]
    print(matches[["id", "name", "unit_name"]].to_string(index=False))


# ------ BUILD DATASET FOR DASHBOARD ------
# get chosen nutrient IDs
NUTRIENT_IDS = {
    1008: "calories",
    1003: "protein",
    1004: "fat",
    1005: "carbs",
    1079: "fiber",
    1093: "sodium",
    2000: "sugar",
}

important_ids = list(NUTRIENT_IDS.keys())

# Keep only the nutrients we need
filtered_nutrients = food_nutrient[
    food_nutrient["nutrient_id"].isin(important_ids)
].copy()

print("Filtered nutrient rows:", filtered_nutrients.shape)

# Pivot: one row per food, one column per nutrient
pivot = filtered_nutrients.pivot_table(
    index="fdc_id",
    columns="nutrient_id",
    values="amount",
    aggfunc="first"
).reset_index()

print("Pivot shape:", pivot.shape)

# Rename nutrient ID columns to readable names
pivot = pivot.rename(columns=NUTRIENT_IDS)

# Keep only food metadata we need
food_small = food[["fdc_id", "description", "food_category_id"]].copy()
food_small = food_small.rename(columns={"description": "food_name"})

# Merge food names
df = pd.merge(pivot, food_small, on="fdc_id", how="left")

# Merge category names
category_small = food_category[["id", "description"]].copy()
category_small = category_small.rename(columns={"description": "category"})

df = pd.merge(
    df,
    category_small,
    left_on="food_category_id",
    right_on="id",
    how="left"
)

# Drop redundant category ID column from category table
df = df.drop(columns=["id"])

print("Merged shape:", df.shape)
print("\nColumns after merge:")
print(df.columns.tolist())

print("\nFirst 10 rows:")
print(df.head(10).to_string())

# ------ CLEAN DATASET FOR DASHBOARD ------

# 1) keep only relevant categories for the dashboard
KEEP_CATEGORIES = [
    "Dairy and Egg Products",
    "Poultry Products",
    "Sausages and Luncheon Meats",
    "Fruits and Fruit Juices",
    "Pork Products",
    "Vegetables and Vegetable Products",
    "Nut and Seed Products",
    "Beef Products",
    "Finfish and Shellfish Products",
    "Legumes and Legume Products",
    "Cereal Grains and Pasta",
    "Snacks",
]

clean_df = df[df["category"].isin(KEEP_CATEGORIES)].copy()

# 2) drop rows missing critical values
clean_df = clean_df.dropna(subset=["calories", "protein", "category", "food_name"])

# 3) fill optional nutrients with 0
for col in ["fat", "carbs", "fiber", "sugar", "sodium"]:
    clean_df[col] = clean_df[col].fillna(0)

# 4) normalize food names
clean_df["food_name"] = clean_df["food_name"].str.lower().str.strip()

print("Rows after basic cleaning:", len(clean_df))

# 5) basic numeric filtering

clean_df = clean_df[clean_df["calories"] > 20]
clean_df = clean_df[clean_df["calories"] < 800]

clean_df = clean_df[clean_df["protein"] > 0]

# preventing weird fiber spikes
clean_df = clean_df[clean_df["fiber"] < 20]

print("Rows after numeric filtering:", len(clean_df))

# 6) ---------- derived metrics ----------

# cap fiber (prevents unrealistic influence)
clean_df["fiber_capped"] = clean_df["fiber"].clip(upper=10)

# efficiency metrics
clean_df["protein_per_100_kcal"] = clean_df["protein"] / clean_df["calories"] * 100
clean_df["fiber_per_100_kcal"] = clean_df["fiber_capped"] / clean_df["calories"] * 100
clean_df["sugar_per_100_kcal"] = clean_df["sugar"] / clean_df["calories"] * 100

# fat loss score
clean_df["fat_loss_score"] = (
    1.5 * clean_df["protein_per_100_kcal"]
    + 0.5 * clean_df["fiber_per_100_kcal"]
    - 1.0 * clean_df["sugar_per_100_kcal"]
    - (clean_df["calories"] / 150)
)

print("Metrics added. Sample:")
print(clean_df.head(5).to_string())

# 7) ---------- Remove unrealistic / unwanted foods ----------

excluded_terms = [
    "gelatins", "frog", "turtle", "emu", "grouse",
    "whale", "seal", "bear", "moose", "caribou",
    "liver", "kidney", "heart", "brain", "spleen", "gizzard",
    "blood", "retail parts", "by-product", "mechanically separated"
]

pattern = "|".join(excluded_terms)

clean_df = clean_df[
    ~clean_df["food_name"].str.contains(pattern, case=False, na=False)
].copy()

print("Rows after removing unrealistic foods:", len(clean_df))

# 8) create helper columns for duplicate handling
# Keep original food_name for display!
# base_food is only used to detect similar foods like:
# "fish, tuna, raw" and "fish, tuna, canned in water"

def get_base_food(name):
    if pd.isna(name):
        return name

    parts = [p.strip() for p in str(name).lower().split(",")]

    # preparation / form terms that should NOT define the core food
    prep_terms = {
        "raw", "cooked", "boiled", "steamed", "baked", "grilled", "fried",
        "roasted", "broiled", "braised", "sauteed", "stir-fried", "poached",
        "microwaved", "toasted", "frozen", "canned", "dried", "freeze-dried",
        "dry heat", "moist heat", "drained", "undrained"
    }

    cleaned_parts = [p for p in parts if p not in prep_terms]

    if len(cleaned_parts) == 0:
        return parts[0]

    if len(cleaned_parts) == 1:
        return cleaned_parts[0]

    # keep first two meaningful parts:
    # fish, tuna / egg, white / cheese, mozzarella
    return ", ".join(cleaned_parts[:2])


clean_df["base_food"] = clean_df["food_name"].apply(get_base_food)


# 9) Preparation preference
# Lower number = preferred when comparing similar foods
# Important: this is only a tie-break/helper, not the main ranking

def get_prep_preference(name):
    name = str(name).lower()

    if "raw" in name or "fresh" in name:
        return 0
    elif "plain" in name:
        return 1
    elif "cooked" in name or "boiled" in name or "steamed" in name or "dry heat" in name:
        return 2
    elif "frozen" in name:
        return 3
    elif "canned" in name:
        return 4
    elif "dried" in name or "freeze-dried" in name:
        return 5
    else:
        return 2  # neutral default


clean_df["prep_preference"] = clean_df["food_name"].apply(get_prep_preference)


# 10) Inspect duplicate groups if you want
print("\nSample duplicate groups:")
print(
    clean_df[["food_name", "base_food", "category", "fat_loss_score", "prep_preference"]]
    .sort_values(["base_food", "fat_loss_score"], ascending=[True, False])
    .head(20)
    .to_string(index=False)
)


# 11) Build dashboard dataset:
# top 30 unique foods per category
# uniqueness is based on base_food
# but displayed food_name stays the original full name

dashboard_parts = []

for category in KEEP_CATEGORIES:
    temp = clean_df[clean_df["category"] == category].copy()

    # Sort:
    # 1. best score first
    # 2. better preparation preference first
    # 3. lower sugar first
    # 4. higher protein first
    temp = temp.sort_values(
        by=["fat_loss_score", "prep_preference", "sugar", "protein"],
        ascending=[False, True, True, False]
    )

    # Keep only first occurrence of each base_food
    # This keeps the best version while preserving original food_name
    temp = temp.drop_duplicates(subset=["base_food"], keep="first")

    # Take top 30 unique foods in this category
    temp = temp.head(30)

    dashboard_parts.append(temp)

dashboard_df = pd.concat(dashboard_parts, ignore_index=True)


# 12) Optional: sort final dashboard nicely
dashboard_df = dashboard_df.sort_values(
    by=["category", "fat_loss_score"],
    ascending=[True, False]
).reset_index(drop=True)


print("\nRows in dashboard dataset:", len(dashboard_df))
print("Unique displayed food names in dashboard:", dashboard_df["food_name"].nunique())
print("Unique base foods in dashboard:", dashboard_df["base_food"].nunique())


print("\nTop 30 foods in dashboard dataset:")
print(
    dashboard_df[
        [
            "food_name",
            "base_food",
            "category",
            "calories",
            "protein",
            "fat",
            "carbs",
            "fiber",
            "sugar",
            "fat_loss_score",
        ]
    ]
    .sort_values("fat_loss_score", ascending=False)
    .head(30)
    .to_string(index=False)
)

#check top foods per category

for cat in dashboard_df["category"].unique():
    print(f"\n--- {cat} ---")
    print(
        dashboard_df[dashboard_df["category"] == cat][
            ["food_name", "calories", "protein", "sugar", "fat_loss_score"]
        ]
        .sort_values("fat_loss_score", ascending=False)
        .head(10)
        .to_string(index=False)
    )

# ------ SAVE DASHBOARD DATASET ------

dashboard_output_path = PROCESSED_DIR / "fat_loss_foods_dashboard_auto.csv"

#dashboard_df.to_csv(dashboard_output_path, index=False)

print(f"\nDashboard dataset saved to: {dashboard_output_path}")

# ------ COMPILE CATEGORIES IN FINAL DATASET ------

df = pd.read_csv(PROCESSED_DIR / "fat_loss_foods_dashboard_manual.csv", sep=";")
df.to_csv(dashboard_output_path, index=False)

df["final_category"] = None

def map_category(row):
    cat = row["category"]

    if cat in ["Poultry Products", "Pork Products", "Beef Products", "Sausages and Luncheon Meats"]:
        return "Meat"

    elif cat == "Finfish and Shellfish Products":
        return "Fish & Seafood"

    elif cat == "Dairy and Egg Products":
        return "Dairy & Eggs"

    elif cat == "Cereal Grains and Pasta":
        return "Grains & Carbs"

    elif cat == "Fruits and Fruit Juices":
        return "Fruits"

    elif cat in ["Vegetables and Vegetable Products", "Legumes and Legume Products"]:
        return "Veggies & Plant Protein"

    elif cat == "Nut and Seed Products":
        return "Nuts & Seeds"

    else:
        return "Other"

df["final_category"] = df.apply(map_category, axis=1)

def fix_snacks(row):
    name = row["food_name"].lower()

    # grains-based snacks
    if "popcorn" in name or "pretzel" in name or "granola" in name or "rice cracker" in name or "soy chips" in name or "tortilla chips" in name:
        return "Grains & Carbs"

    # meat snacks
    if "jerky" in name or "pork skins" in name or "beef sticks" in name:
        return "Meat"

    return row["final_category"]

df["final_category"] = df.apply(fix_snacks, axis=1)

df["final_category"].value_counts()

df.to_csv(PROCESSED_DIR / "fat_loss_foods_dashboard_final.csv", index=False)

print("Loaded manual dataset shape:", df.shape)
print("Columns:", df.columns.tolist())