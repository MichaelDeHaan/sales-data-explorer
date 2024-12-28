# Import packages
from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import model

# Data Preprocessing
sales = pd.read_excel('./data/coffee_shop_sales.xlsx')
sales['transaction_total'] = sales['unit_price'] * sales['transaction_qty']

# Initialize the app
app = Dash()

# App layout
app.layout = [
    html.H1('Coffee Shop Sales Dashboard'),
    html.Div([
        html.H2('Store Analysis'),
        # Dropdown for store location
        dcc.Dropdown(sales.store_location.unique(),
                     'Lower Manhattan',
                     id='location-dropdown'),

        # Dropdown for time period
        dcc.Dropdown(['Daily', 'Weekly'],
                     'Daily',
                     id='time-dropdown'),

        # Ratio to toggle prediction
        dcc.RadioItems(
            id='prediction-toggle',
            options=[
                {'label': 'Show Prediction', 'value': 'on'},
                {'label': 'Hide Prediction', 'value': 'off'}
            ],
            value='off'
        )
    ], id='analysis-options'),

    html.Div([
        # Main graph
        dcc.Graph(id='main-graph'),

        # Date range picker
        dcc.DatePickerRange(
            id='date-range',
            min_date_allowed=sales.transaction_date.min(),
            max_date_allowed=sales.transaction_date.max(),
            start_date=sales.transaction_date.min(),
            end_date=sales.transaction_date.max()
        )
    ], id='main-graph-container'),

    html.Div([
        html.H2('Item Analysis'),
        # Input for top-n categories
        dcc.Input(
            id='top-n-cat',
            type='number',
            value=5,
            max=sales.product_category.nunique()
        )
    ], className='analysis-options'),

    html.Div([
        # Category pie chart (by quantity)
        dcc.Graph(id='item-graph-qty'),

        # Category pie chart (by sales)
        dcc.Graph(id='item-graph-sales')
    ], id='item-graph-container')
]


@callback(
    Output('main-graph', 'figure'),
    Output('item-graph-qty', 'figure'),
    Output('item-graph-sales', 'figure'),
    Input('location-dropdown', 'value'),
    Input('time-dropdown', 'value'),
    Input('prediction-toggle', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'),
    Input('top-n-cat', 'value')
)
def update_graph(location, time, prediction, start_date, end_date, top_n):
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
    main_fig = px.line(main_sales, title='Daily Sales',
                       labels={'transaction_date': 'Date', 'transaction_total': 'Sales'})

    # Add prediction
    if prediction == 'on':
        y = model.generate_polynomial_fit(main_sales)
        main_fig.add_scatter(x=main_sales.index, y=y, mode='lines', name='Prediction')

    # Create the item graph
    sales_item = sales.copy()

    # Calculate top-n categories
    top_qty = sales_item.groupby('product_category')['transaction_qty'].sum().nlargest(top_n)
    top_sales = sales_item.groupby('product_category')['transaction_total'].sum().nlargest(top_n)

    # Only need an 'other' category if there are more categories than top-n
    if top_n < sales_item['product_category'].nunique():
        # Sum categories not included in top-n
        other_qty = sales_item[~sales_item['product_category'].isin(top_qty.index)]['transaction_qty'].sum()
        other_sales = sales_item[~sales_item['product_category'].isin(top_sales.index)]['transaction_total'].sum()
        # Convert to DataFrame for Plotly
        top_qty = top_qty.to_frame().reset_index()
        top_sales = top_sales.to_frame().reset_index()
        top_qty.loc[len(top_qty.index)] = ['Other', other_qty]
        top_sales.loc[len(top_sales.index)] = ['Other', other_sales]
    else:
        top_qty = top_qty.to_frame().reset_index()
        top_sales = top_sales.to_frame().reset_index()

    # Create the pie chart
    item_fig = px.pie(top_qty, values='transaction_qty', names='product_category',
                      title=f'Top {top_n} Categories by Quantity')
    sales_fig = px.pie(top_sales, values='transaction_total', names='product_category',
                       title=f'Top {top_n} Categories by Sales')

    # Return the figures
    return main_fig, item_fig, sales_fig


# Run the app
if __name__ == '__main__':
    app.run(debug=False)
