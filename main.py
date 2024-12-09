# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
from scipy.constants import value

# Data Preprocessing
sales = pd.read_excel('./data/coffee_shop_sales.xlsx')
sales['transaction_total'] = sales['unit_price'] * sales['transaction_qty']

# Initialize the app
app = Dash()

# App layout
app.layout = [
    html.H1('Coffee Shop Sales Dashboard'),
    html.H2('Store Analysis'),
    dcc.Dropdown(sales.store_location.unique(),
                 'Lower Manhattan',
                 id='location-dropdown'),

    dcc.Dropdown(['Daily', 'Weekly'],
                 'Daily',
                 id='time-dropdown'),

    dcc.Graph(id='main-graph'),

    dcc.DatePickerRange(
        id='date-range',
        min_date_allowed=sales.transaction_date.min(),
        max_date_allowed=sales.transaction_date.max(),
        start_date=sales.transaction_date.min(),
        end_date=sales.transaction_date.max()
    ),

    html.H2('Item Analysis'),
    dcc.Input(
        id='top-n',
        type='number',
        value=5,
        max=sales.product_category.nunique()
    ),
    dcc.Graph(id='item-graph'),
]


@callback(
    Output('main-graph', 'figure'),
    Output('item-graph', 'figure'),
    Input('location-dropdown', 'value'),
    Input('time-dropdown', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'),
    Input('top-n', 'value')
)
def update_graph(location, time, start_date, end_date, top_n):
    sales_main = sales.copy()

    # Filter by location
    sales_main = sales_main[sales_main.store_location == location]

    # Filter by date
    sales_main = sales_main[(sales_main.transaction_date >= start_date) &
                                    (sales_main.transaction_date <= end_date)]

    # Group by date
    if time == 'Weekly':
        # Change transaction dates with a weekly range to the start of the week
        sales_main['transaction_date'] = sales_main['transaction_date'].dt.to_period('W').dt.to_timestamp()
    main_sales = sales_main.groupby('transaction_date')['transaction_total'].sum()

    # Create the main graph
    main_fig = px.line(main_sales, title='Daily Sales')

    # Create the item graph
    sales_item = sales.copy()

    # Calculate top-n categories
    top_cat = sales_item.groupby('product_category')['transaction_qty'].sum().nlargest(top_n)
    # Only need an 'other' category if there are more categories than top-n
    if top_n < sales_item['product_category'].nunique():
        # Sum categories not included in top-n
        other_qty = sales_item[~sales_item['product_category'].isin(top_cat.index)]['transaction_qty'].sum()
        # Convert to DataFrame for Plotly
        top_cat = top_cat.to_frame().reset_index()
        top_cat.loc[len(top_cat.index)] = ['Other', other_qty]
    else:
        top_cat = top_cat.to_frame().reset_index()

    # Create the pie chart
    item_fig = px.pie(top_cat, values='transaction_qty', names='product_category', title=f'Top {top_n} Categories')

    # Return the figures
    return main_fig, item_fig
# Run the app
if __name__ == '__main__':
    app.run(debug=True)
