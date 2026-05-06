from dash import Dash

from src.data_loader import load_dashboard_data
from src.layout import create_layout
from src.callbacks import register_callbacks

df = load_dashboard_data()

app = Dash(__name__)

app.title = "Fat Loss Dashboard"

app.layout = create_layout(df)
register_callbacks(app, df)

server = app.server

if __name__ == "__main__":

    app.run(debug=True)