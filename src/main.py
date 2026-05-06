from dash import Dash

from data_loader import load_dashboard_data
from charts import create_protein_calorie_scatter, create_macro_comparison_dotplot, create_category_ranking_bar, create_top_foods_bar, create_macro_donut
from layout import create_layout
from callbacks import register_callbacks

df = load_dashboard_data()

app = Dash(__name__)

app.title = "Fat Loss Dashboard"

app.layout = create_layout(df)
register_callbacks(app, df)

server = app.server

if __name__ == "__main__":

    app.run(debug=True)