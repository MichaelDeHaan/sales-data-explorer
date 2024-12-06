# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px

# Data Preprocessing
sales = pd.read_excel('./data/coffee_shop_sales.xlsx')
sales['transaction_total'] = sales['unit_price'] * sales['transaction_qty']

# Initialize the app
app = Dash()

# App layout
app.layout = [
    html.H1('Coffee Shop Sales Dashboard'),
    dcc.Dropdown(sales.store_location.unique(), 'Lower Manhattan', id='location-dropdown'),
    dcc.Graph(id='main-graph')
]

@callback(
    Output('main-graph', 'figure'),
    Input('location-dropdown', 'value')
)

def update_graph(value):
    filtered_sales = sales.copy()

    # Filter by Location
    filtered_sales = filtered_sales[filtered_sales.store_location == value]

    # Group by Date
    daily_sales = filtered_sales.groupby('transaction_date')['transaction_total'].sum()

    # Create the plot
    fig = px.line(daily_sales, title='Daily Sales')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)