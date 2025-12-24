import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide")

st.title("🛒 E-Commerce & Retail Analytics Dashboard")
st.markdown("This dashboard uses **Data Engineering** to visualize sales performance.")

# --- 2. DATA LOADING & CLEANING (ETL Pipeline) ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/online_retail_II.csv", encoding="ISO-8859-1")
    
    # Cleaning
    df = df.dropna(subset=['Customer ID'])
    df = df[~df['Invoice'].astype(str).str.startswith('C')]
    df = df[(df['Quantity'] > 0) & (df['Price'] > 0)]
    
    # Exclude non-product items
    exclude_items = ['Manual', 'POSTAGE', 'DOTCOM POSTAGE', 'CRUK Commission', 'Discount']
    df = df[~df['Description'].isin(exclude_items)]
    
    # Transformation
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['Revenue'] = df['Quantity'] * df['Price']
    
    return df

with st.spinner('Running ETL Pipeline...'):
    df = load_data()

# ==============================================================================
# LAYOUT STRATEGY: VERTICAL STACK USING PLACEHOLDERS
# ==============================================================================
# Since the controls are at the bottom, we must define empty containers (placeholders)
# at the top first, so we can fill them later after the filter logic runs.

# 1. KPI Section (Top)
kpi_container = st.container()
st.divider()

# 2. Top Products Section (Middle)
products_container = st.container()
st.divider()

# 3. Trend Section (Middle)
trend_container = st.container()
st.divider()

# 4. Controls & Pie Chart Section (Bottom)
controls_container = st.container()


# ==============================================================================
# LOGIC & RENDERING (Bottom-Up Data Flow)
# ==============================================================================

# --- STEP 1: RENDER CONTROLS (At the visual bottom, but logical start) ---
with controls_container:
    st.subheader("⚙️ Controls & Distribution")
    
    # Layout for Controls: Country Select (Left) | Date Select (Right)
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        # Country Filter
        all_countries = sorted(df['Country'].unique())
        country_options = ["Select All"] + all_countries
        
        selected_country_option = st.selectbox(
            "Filter by Country",
            options=country_options,
            index=0 # Default to Select All
        )
    
    with col_filter2:
        # Date Filter
        min_date = df['InvoiceDate'].min()
        max_date = df['InvoiceDate'].max()
        
        start_date, end_date = st.date_input(
            "Filter by Date Range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

    # APPLY FILTER LOGIC
    filtered_df = df.copy()
    
    # Country Logic
    if selected_country_option != "Select All":
        filtered_df = filtered_df[filtered_df['Country'] == selected_country_option]
        
    # Date Logic
    filtered_df = filtered_df[
        (filtered_df['InvoiceDate'].dt.date >= start_date) & 
        (filtered_df['InvoiceDate'].dt.date <= end_date)
    ]
    
    if filtered_df.empty:
        st.error("No data available for these filters.")
        st.stop()

    # RENDER PIE CHART (Directly below filters)
    st.markdown("##### Revenue Share by Country")
    
    country_revenue = filtered_df.groupby('Country')['Revenue'].sum().reset_index()
    
    fig_pie = px.pie(
        country_revenue, 
        values='Revenue', 
        names='Country',
        hole=0.5,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    
    # CLEANING UP THE CHART UI:
    # textinfo='none' -> Hides the messy overlapping text labels.
    # The user can still see the percentage by hovering over the slices.
    fig_pie.update_traces(textposition='inside', textinfo='none')
    
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)


# --- STEP 2: FILL THE TOP PLACEHOLDERS (Backfilling) ---

# SQL Connection for Metrics
conn = sqlite3.connect(':memory:')
filtered_df.to_sql('retail', conn, index=False, if_exists='replace')

# A) FILL KPI SECTION
with kpi_container:
    st.subheader("📊 Key Performance Indicators")
    total_revenue = filtered_df['Revenue'].sum()
    total_orders = filtered_df['Invoice'].nunique()
    avg_order_value = total_revenue / total_orders

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"£{total_revenue:,.0f}")
    c2.metric("Total Orders", f"{total_orders:,}")
    c3.metric("Avg. Order Value", f"£{avg_order_value:.2f}")

# B) FILL PRODUCTS SECTION
with products_container:
    st.subheader("🏆 Top 5 Best-Selling Products")
    
    query_top_products = """
    SELECT Description, SUM(Revenue) as Total_Revenue
    FROM retail
    GROUP BY Description
    ORDER BY Total_Revenue DESC
    LIMIT 5
    """
    top_products_df = pd.read_sql(query_top_products, conn)

    fig_bar = px.bar(
        top_products_df, 
        x='Total_Revenue', 
        y='Description', 
        orientation='h', 
        color='Total_Revenue',
        color_continuous_scale='Viridis'
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, height=400)
    st.plotly_chart(fig_bar, use_container_width=True)

# C) FILL TREND SECTION
with trend_container:
    st.subheader("📈 Revenue Trend Over Time")
    
    daily_sales = filtered_df.set_index('InvoiceDate').resample('D')['Revenue'].sum().reset_index()

    fig_line = px.line(
        daily_sales, 
        x='InvoiceDate', 
        y='Revenue',
        height=400
    )
    st.plotly_chart(fig_line, use_container_width=True)