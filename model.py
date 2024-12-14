import pandas as pd
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import LinearRegression

def generate_polynomial_fit(sales):
    sales_df = sales.to_frame().reset_index()
    sales_df['transaction_date_ordinal'] = sales_df['transaction_date'].apply(lambda x: x.toordinal())

    X = sales_df[['transaction_date_ordinal']]
    y = sales_df['transaction_total']

    # Generate polynomial features
    poly = PolynomialFeatures(degree=3, include_bias=False)

    # Fit and transform the data
    scale = StandardScaler()
    X = scale.fit_transform(X)
    poly_features = poly.fit_transform(X)
    poly_reg_model = LinearRegression().fit(poly_features, y)

    # Predict using the trained model
    y_pred = poly_reg_model.predict(poly_features)

    # Return the data
    return y_pred