import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide")

st.title("🛒 E-Commerce & Retail Analytics Dashboard")
st.markdown("""
This dashboard transforms raw sales data into actionable insights using **Data Engineering** and **Business Intelligence** techniques.
""")

# --- 2. DATA LOADING & CLEANING (ETL Pipeline) ---
@st.cache_data
def load_data():
    # Ingest raw data (Handling encoding for UCI dataset)
    df = pd.read_csv("data/online_retail_II.csv", encoding="ISO-8859-1")
    
    # 1. Basic Cleaning (Data Quality)
    # Remove rows with missing Customer IDs (Essential for segmentation)
    df = df.dropna(subset=['Customer ID'])
    # Exclude cancelled transactions (Invoices starting with 'C')
    df = df[~df['Invoice'].astype(str).str.startswith('C')]
    # Ensure Quantity and Price are positive to filter out bad data
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
    
    # 2. Advanced Cleaning (Business Logic)
    # Exclude non-product items like 'Manual', 'Postage' to avoid skewing revenue metrics
    exclude_items = ['Manual', 'POSTAGE', 'DOTCOM POSTAGE', 'CRUK Commission', 'Discount']
    df = df[~df['Description'].isin(exclude_items)]
    
    # 3. Data Transformation (Feature Engineering)
    # Convert 'InvoiceDate' to datetime objects for time-series analysis
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    # Calculate 'Revenue' (Quantity * Price) - Renamed from 'TotalLinePrice' for clarity
    df['Revenue'] = df['Quantity'] * df['Price']
    
    return df

# Execute the pipeline with a loading spinner
with st.spinner('Running ETL Pipeline... Processing data...'):
    df = load_data()

# --- 3. SQL ENGINE SETUP (In-Memory) ---
# Initialize an in-memory SQLite database
conn = sqlite3.connect(':memory:')
# Load the processed DataFrame into a SQL table named 'retail'
df.to_sql('retail', conn, index=False, if_exists='replace')

# --- 4. KEY PERFORMANCE INDICATORS (KPIs) ---
st.subheader("📊 Key Performance Indicators (KPIs)")

# Calculate Core Metrics
total_revenue = df['Revenue'].sum()
total_orders = df['Invoice'].nunique()
avg_order_value = total_revenue / total_orders

# Display Metrics in Columns
col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"£{total_revenue:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Avg. Order Value (AOV)", f"£{avg_order_value:.2f}")

st.divider()

# --- 5. VISUALIZATION & INSIGHTS ---

# A) Top 5 Best-Selling Products (SQL Query)
st.subheader("🏆 Top 5 Best-Selling Products")

query_top_products = """
SELECT Description, SUM(Revenue) as Total_Revenue
FROM retail
GROUP BY Description
ORDER BY Total_Revenue DESC
LIMIT 5
"""
top_products_df = pd.read_sql(query_top_products, conn)

# Create Horizontal Bar Chart
fig_bar = px.bar(
    top_products_df, 
    x='Total_Revenue', 
    y='Description', 
    orientation='h', 
    title="Top 5 Products by Revenue",
    color='Total_Revenue',
    color_continuous_scale='Viridis',
    labels={'Total_Revenue': 'Total Revenue (£)', 'Description': 'Product Name'}
)
# Fix the sort order to show the highest value at the top
fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_bar, use_container_width=True)

# B) Sales Trend Over Time (Time-Series Analysis)
st.subheader("📈 Daily Sales Trend")

# Resample data to Daily (D) frequency
daily_sales = df.set_index('InvoiceDate').resample('D')['Revenue'].sum().reset_index()

# Create Line Chart
fig_line = px.line(
    daily_sales, 
    x='InvoiceDate', 
    y='Revenue', 
    title="Revenue Trend Over Time",
    labels={'InvoiceDate': 'Date', 'Revenue': 'Daily Revenue (£)'}
)
st.plotly_chart(fig_line, use_container_width=True)