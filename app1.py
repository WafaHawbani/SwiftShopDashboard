#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import plotly.express as px
import dash
from dash import  html, dcc, Input, Output, State, dash_table
from dash.dcc import Download


# In[ ]:


#EDA
df = pd.read_csv(r"C:\Users\wafah\Downloads\AssesmentTest\swiftshop_sales_data.csv")


# In[ ]:


df.head()


# In[ ]:


df.info()


# In[ ]:


df.describe()


# In[ ]:


df.isnull().sum()


# In[ ]:


#Handle missing values
df['customer_rating'] = df['customer_rating'].fillna(0)
df['customer_region'] = df['customer_region'].fillna('Unknown')
df['payment_method'] = df['payment_method'].fillna('Unknown')
df.isnull().sum()


# In[ ]:


df['order_date'] = pd.to_datetime(df['order_date']) #to be date type


# In[ ]:


df.info()


# In[ ]:


#Extra columns
df['year'] = df['order_date'].dt.year
df['month'] = df['order_date'].dt.month
df['month_year'] = df['order_date'].astype(str).str[:7]
df['profit'] = (df['total_amount'] * 0.1).round(2)


# In[ ]:


df.head()


# In[ ]:


#KIP'S 
monthly_sales = df.groupby('month_year')['total_amount'].sum().reset_index()
avg_BY_REG = df.groupby('customer_region')['total_amount'].mean().round(3).reset_index()
avg_BY_REG.rename(columns={'total_amount': 'avg_total_amount'}, inplace=True)
top_PROD = df.groupby('product_name')['quantity'].sum().sort_values(ascending=False).reset_index()
top_CATG = df.groupby('category')['quantity'].sum().sort_values(ascending=False).reset_index()
avg_RAT_CATG = df[df['customer_rating'] > 0].groupby('category')['customer_rating'].mean().round(1).reset_index()


# In[ ]:


print(monthly_sales)
print(avg_BY_REG)
print(top_PROD)
print(top_CATG)
print(avg_RAT_CATG)


# In[ ]:


#FIGURE- 1
fig1 = px.line(monthly_sales, x='month_year', y='total_amount',
                  title='<b>Sales Over Time</b>',
                  labels={'month_year': 'month', 'total_amount': 'Sales'},
              hover_data=['total_amount'])
fig1.show()


# In[ ]:


#FIGURE- 2
fig2 = px.pie(df.groupby('category')['total_amount'].sum().reset_index(),
                 values='total_amount', names='category',
                 title='<b> Product Category Performance </b>',hole=0.4)
fig2.show()


# In[ ]:


#FIGURE -3
fig3 = px.histogram(df[df['customer_rating'] > 0], 
                       x='customer_rating',
                       title='<b> Customer Rating Distribution </b>',
                       nbins=5, hover_data=['customer_rating']) 
fig3.update_layout(bargap=0.2,xaxis_showgrid=True, yaxis_showgrid=True, xaxis_gridcolor='lightgray', yaxis_gridcolor='lightgray')
fig3.show()


# In[ ]:


#This defines the entire layout of the SwiftShop Sales Dashboard, including the title, top product chart, data filtering components (date picker, region dropdown, category dropdown), KPI display, various sales data visualizations (line chart, pie chart, histogram), a detailed sales data table, and a button to download the filtered data.
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('SwiftShop Sales Dashboard', style={'textAlign': 'center'}), #title
    dcc.Graph(id='top_products_bar_chart'), #TOP PRODUCTS chart
    #selection components
    html.Div([  
        dcc.DatePickerRange(
            id='date_picker',
            start_date=df['order_date'].min(),
            end_date=df['order_date'].max()
        ),
        dcc.Dropdown(
            id='region_dropdown',
            options=[{'label': region, 'value': region} for region in df['customer_region'].unique()],
            multi=True,
            placeholder="Select one or more regions",
            style={
        'width': '300px', 
        'fontSize': '16px' 
    }
        ),
        dcc.Dropdown(
            id='category_dropdown',
            options=[{'label': category, 'value': category} for category in df['category'].unique()],
            multi=True,
            placeholder="Select one or more Category",
            style={
        'width': '300px', 
        'fontSize': '16px' 
    }
        )
    ], style={'display': 'flex', 'gap': '20px', 'padding': '20px'}),
    
        html.P("KPI present a brief summary of financial performance, order count, and average rating", 
       style={'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '28px'}),
    # display KPI
    html.Div(id='kpi_cards', style={
        'display': 'flex',
        'justifyContent': 'space-around',
        'padding': '20px',
        'backgroundColor': '#f9f9f9'
    }),
   html.P("These charts present: Total sales per month, sales distribution across product categories, and the frequency of each rating (1 to 5)",
          style={'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '28px'}),

     # data visualization charts
    html.Div([
        dcc.Graph(id='sales_line_chart'),
        dcc.Graph(id='category_pie_chart'),
        dcc.Graph(id='rating_histogram'),
    ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px', 'padding': '20px','maxWidth': '1000px'}),

    # Sales data table
    html.P("This table shows the sales data corresponding to the date range, customer region, and product category chosen above",
       style={'textAlign': 'center', 'fontWeight': 'bold', 'fontSize': '28px'}),
    html.Div([
        html.H3("Sales Data Table"),
        dash_table.DataTable(
            id='sales_table',
            columns=[
            {'name': 'Order ID', 'id': 'order_id'},
            {'name': 'Order Date', 'id': 'order_date'},
            {'name': 'Product Name', 'id': 'product_name'},
            {'name': 'Category', 'id': 'category'},
            {'name': 'Customer Region', 'id': 'customer_region'},
            {'name': 'Total Amount', 'id': 'total_amount'},
            {'name': 'Customer Rating', 'id': 'customer_rating'},
            {'name': 'Year', 'id': 'year'},
            {'name': 'Month', 'id': 'month'},
            {'name': 'Month-Year', 'id': 'month_year'},
            {'name': 'Profit', 'id': 'profit'}
            ],
            style_table={'overflowX': 'auto'},
            page_size=10,
            style_cell={'textAlign': 'left'},
        )
    ], style={'padding': '20px'}),
    #for the data download button
  html.Div([
        html.P("Click to download", style={'marginRight': '10px', 'lineHeight': '36px'}), 
    html.Button("Download Data (csv)", id="btn_download", n_clicks=0),
    dcc.Download(id="download_data")
], style={'textAlign': 'center', 'padding': '20px'})
    
])


# In[ ]:


@app.callback(
    [Output('sales_line_chart', 'figure'),
     Output('category_pie_chart', 'figure'),
     Output('rating_histogram', 'figure'),
     Output('kpi_cards', 'children'),
     Output('sales_table', 'data'),
     Output('top_products_bar_chart', 'figure')],
    [Input('date_picker', 'start_date'),
     Input('date_picker', 'end_date'),
     Input('region_dropdown', 'value'),
     Input('category_dropdown', 'value')]
)
    # Filter the DF based on the selected date range, selected regions, and selected categories
def update_dashboard(start_date, end_date, selected_regions, selected_categories):

    filtered_df = df[(df['order_date'] >= start_date) & (df['order_date'] <= end_date)]

    if selected_regions:
        filtered_df = filtered_df[filtered_df['customer_region'].isin(selected_regions)]

    if selected_categories:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

    ##-----------------------------------
     #charts
    monthly_sales = filtered_df.groupby('month_year')['total_amount'].sum().reset_index()
    fig1 = px.line(monthly_sales, x='month_year', y='total_amount',
                   title='<b>Sales Over Time</b>',
                   labels={'month_year': 'Month', 'total_amount': 'Sales'},
                   hover_data=['total_amount'])


    fig2 = px.pie(filtered_df.groupby('category')['total_amount'].sum().reset_index(),
                  values='total_amount', names='category',
                  title='<b>Product Category Performance</b>', hole=0.4)


    fig3 = px.histogram(filtered_df[filtered_df['customer_rating'] > 0],
                         x='customer_rating',
                         title='<b>Customer Rating Distribution</b>',
                         nbins=5, hover_data=['customer_rating'])
    fig3.update_layout(bargap=0.2, xaxis_showgrid=True, yaxis_showgrid=True,
                      xaxis_gridcolor='lightgray', yaxis_gridcolor='lightgray')

    ##-----------------------------------
    # KPI
    total_sales = filtered_df['total_amount'].sum()

    avg_BY_REG = filtered_df.groupby('customer_region')['total_amount'].mean().round(3).reset_index()
    avg_BY_REG.rename(columns={'total_amount': 'avg_total_amount'}, inplace=True)
    best_region = avg_BY_REG.loc[avg_BY_REG['avg_total_amount'].idxmax()]


    top_PROD = filtered_df.groupby('product_name')['quantity'].sum().sort_values(ascending=False).reset_index()
    top_product = top_PROD.iloc[0]


    avg_RAT_CATG = filtered_df[filtered_df['customer_rating'] > 0].groupby('category')['customer_rating'].mean().round(1).reset_index()
    best_category_by_rating = avg_RAT_CATG.loc[avg_RAT_CATG['customer_rating'].idxmax()]

    top_CATG = filtered_df.groupby('category')['quantity'].sum().sort_values(ascending=False).reset_index()
    top_category = top_CATG.iloc[0]
    
    kpi_style = {
        'padding': '20px', 'borderRadius': '15px', 'color': 'white', 'textAlign': 'center',
        'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'width': '30%'
    }
    
    kpi_cards = [
        html.Div([
            html.H4("Total Sales"),
            html.H2(f"${total_sales:,.2f}")
        ], style={'padding': '10px', 'backgroundColor': '#e0f7fa', 'borderRadius': '10px'}),

        html.Div([
            html.H4("Region by Avg. Sales"),
            html.H2(f"{best_region['customer_region']}"),
            html.P(f"Avg. Sales: ${best_region['avg_total_amount']:,.2f}")
        ], style={'padding': '10px', 'backgroundColor': '#ffe0b2', 'borderRadius': '10px'}),

        html.Div([
            html.H4("Top Product"),
            html.H2(f"{top_product['product_name']}"),
            html.P(f"Quantity Sold: {top_product['quantity']}")
        ], style={'padding': '10px', 'backgroundColor': '#dcedc8', 'borderRadius': '10px'}),

        html.Div([
            html.H4("Top Category"),
            html.H2(f"{top_category['category']}"),
            html.P(f"Quantity Sold: {top_category['quantity']}")
        ], style={'padding': '10px', 'backgroundColor': '#ffcccb', 'borderRadius': '10px'}),

        html.Div([
            html.H4("Avg. Customer Rating by Category"),
            html.H2(f"{best_category_by_rating['category']}"),
            html.P(f"Avg. Rating: {best_category_by_rating['customer_rating']}")
        ], style={'padding': '10px', 'backgroundColor': '#c8e6c9', 'borderRadius': '10px'})
    ]

    #Table
    table_data = filtered_df[[
        'order_id', 'order_date', 'product_name', 'category',
        'customer_region', 'total_amount', 'customer_rating', 'month_year', 'month', 'year', 'profit'
    ]].to_dict('records')

    top_products = filtered_df.groupby('product_name')['profit'].sum().sort_values(ascending=False).head(10).reset_index()
    fig4 = px.bar(top_products, x='product_name', y='profit', title='Top 10 Products by Profit',
                  labels ={'product_name': 'Product', 'profit': 'Profit'})

    return fig1, fig2, fig3, kpi_cards, table_data, fig4



# In[ ]:


#This callback function is triggered when the download button is clicked.
@app.callback(
    Output("download_data", "data"),
    Input("btn_download", "n_clicks"),
    State('date_picker', 'start_date'),
    State('date_picker', 'end_date'),
    State('region_dropdown', 'value'),
    State('category_dropdown', 'value'),
    prevent_initial_call=True
)
def export_data(n_clicks, start_date, end_date, selected_regions, selected_categories):
  #Filter the DF based on the selected start and end dates, regions, and categories 
    filtered_df = df[(df['order_date'] >= start_date) & (df['order_date'] <= end_date)]

    if selected_regions:
        filtered_df = filtered_df[filtered_df['customer_region'].isin(selected_regions)]

    if selected_categories:
        filtered_df = filtered_df[filtered_df['category'].isin(selected_categories)]

    return dcc.send_data_frame(filtered_df.to_csv, filename="sales_data_table.csv", index=False)


# In[ ]:


if __name__ == '__main__':
    app.run(debug=True, port=1057)


# In[ ]:




