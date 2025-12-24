import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide")

st.title("🛒 E-Commerce & Retail Analytics Dashboard")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Verdana', sans-serif;
    }
    [data-testid="stMetricValue"] {
        font-size: 36px !important;
        font-weight: bold;
        color: #00CC96;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("This dashboard uses **Data Engineering** to visualize sales performance.")

# --- 2. DATA LOADING & CLEANING ---
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
    
    # Text Beautification
    df['Description'] = df['Description'].str.title()
    
    return df

with st.spinner('Running ETL Pipeline...'):
    df = load_data()

# ==============================================================================
# LAYOUT CONTAINERS
# ==============================================================================
kpi_container = st.container()
st.divider()
products_container = st.container()
st.divider()
trend_container = st.container()
st.divider()
controls_container = st.container()

# ==============================================================================
# LOGIC & RENDERING
# ==============================================================================

# --- STEP 1: RENDER CONTROLS ---
with controls_container:
    st.subheader("⚙️ Controls & Distribution")
    
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        all_countries = sorted(df['Country'].unique())
        country_options = ["Select All"] + all_countries
        selected_country_option = st.selectbox("Filter by Country", options=country_options, index=0)
    
    with col_filter2:
        min_date = df['InvoiceDate'].min()
        max_date = df['InvoiceDate'].max()
        start_date, end_date = st.date_input("Filter by Date Range", value=[min_date, max_date], min_value=min_date, max_value=max_date)

    # APPLY FILTER
    filtered_df = df.copy()
    if selected_country_option != "Select All":
        filtered_df = filtered_df[filtered_df['Country'] == selected_country_option]
        
    filtered_df = filtered_df[
        (filtered_df['InvoiceDate'].dt.date >= start_date) & 
        (filtered_df['InvoiceDate'].dt.date <= end_date)
    ]
    
    if filtered_df.empty:
        st.error("No data available for these filters.")
        st.stop()

    # --- PIE CHART ---
    st.markdown("##### Revenue Share by Country")
    country_revenue = filtered_df.groupby('Country')['Revenue'].sum().reset_index()
    
    fig_pie = px.pie(
        country_revenue, 
        values='Revenue', 
        names='Country',
        hole=0.6,
        color_discrete_sequence=px.colors.qualitative.Prism,
    )
    
    fig_pie.update_traces(
        textposition='inside', 
        textinfo='none',
        hovertemplate = "<b>%{label}</b><br>Revenue: £%{value:,.0f}<br>Share: %{percent}"
    )
    
    fig_pie.update_layout(
        height=500,
        font=dict(family="Verdana", size=14),
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05, font=dict(size=14))
    )
    st.plotly_chart(fig_pie, use_container_width=True)


# --- STEP 2: FILL TOP SECTIONS ---

conn = sqlite3.connect(':memory:')
filtered_df.to_sql('retail', conn, index=False, if_exists='replace')

# A) KPI SECTION
with kpi_container:
    st.subheader("📊 Key Performance Indicators")
    total_revenue = filtered_df['Revenue'].sum()
    total_orders = filtered_df['Invoice'].nunique()
    avg_order_value = total_revenue / total_orders

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"£{total_revenue:,.0f}")
    c2.metric("Total Orders", f"{total_orders:,}")
    c3.metric("Avg. Order Value", f"£{avg_order_value:.2f}")

# B) TOP PRODUCTS
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
        color_continuous_scale='Viridis',
        labels={'Total_Revenue': 'Total Revenue (£)', 'Description': 'Product Name'}
    )
    
    fig_bar.update_layout(
        yaxis={'categoryorder':'total ascending'}, 
        showlegend=False, 
        height=400,
        font=dict(family="Verdana", size=14),
        # DÜZELTME BURADA: title=None yerine boş string ve margin ayarı
        title_text='', 
        margin=dict(t=0, l=0, r=0, b=0) 
    )
    
    fig_bar.update_traces(
        hovertemplate="<b>%{y}</b><br>Revenue: £%{x:,.0f}"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# C) TREND CHART
with trend_container:
    st.subheader("📈 Revenue Trend Over Time")
    
    # Veriyi hazırla
    daily_sales = filtered_df.set_index('InvoiceDate').resample('D')['Revenue'].sum().reset_index()

    # Grafiği oluştur
    fig_line = px.line(
        daily_sales, 
        x='InvoiceDate', 
        y='Revenue',
        height=400,
    )
    
    # Tarih sınırlarını (ilk ve son veriyi) bul
    min_date = daily_sales['InvoiceDate'].min()
    max_date = daily_sales['InvoiceDate'].max()

    fig_line.update_layout(
        font=dict(family="Verdana", size=14),
        xaxis_title="Date",
        yaxis_title="Revenue (£)",
        title_text='',
        margin=dict(t=10, l=0, r=0, b=0),
        # EKSEN AYARLARI (Sihirli Kısım Burası)
        xaxis=dict(
            range=[min_date, max_date], # Görüntüyü tam verinin başladığı ve bittiği yere odaklar
            fixedrange=True # 🔒 KİLİT: Sağa sola kaydırmayı (pan) ve zoom'u kapatır.
        ),
        yaxis=dict(
            fixedrange=True # İstersen Y eksenini de (yukarı-aşağı) kilitleriz
        )
    )
    
    fig_line.update_traces(
        line=dict(width=3, color='#00CC96'),
        hovertemplate="<b>Date:</b> %{x|%d %b %Y}<br><b>Revenue:</b> £%{y:,.0f}"
    )
    st.plotly_chart(fig_line, use_container_width=True)