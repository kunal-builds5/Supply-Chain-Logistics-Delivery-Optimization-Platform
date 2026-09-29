import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Supply Chain Analytics Platform",
    layout="wide"
)

# 2. Comprehensive CSS Rules Fixing Selectbox & Dropdown Contrast
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');

    /* Global Font & Main Canvas Setup */
    html, body, .stApp, [data-testid="stHeader"], [data-testid="stSidebar"] {
        background-color: #0e0e10 !important;
        color: #ffffff !important;
        font-family: 'Times New Roman', Times, serif !important;
    }

    /* Force Header & Text Elements to White */
    h1, h2, h3, h4, h5, h6, p, span, label, li {
        color: #ffffff !important;
        font-family: 'Times New Roman', Times, serif !important;
    }

    /* ========================================================= */
    /* FIX FOR SELECTBOX & DROPDOWN CONTRAST (HIGH VISIBILITY)   */
    /* ========================================================= */
    
    /* 1. Target the Selectbox Box Container */
    div[data-baseweb="select"] {
        background-color: #1e1e24 !important;
        border: 1px solid #444450 !important;
        border-radius: 6px !important;
    }

    /* 2. Force Selected Text inside the Box to Bright White */
    div[data-baseweb="select"] * {
        color: #ffffff !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        background-color: transparent !important;
    }

    /* 3. Target the Dropdown List Menu Popover */
    div[data-baseweb="popover"], ul[role="listbox"] {
        background-color: #1e1e24 !important;
        border: 1px solid #444450 !important;
    }

    /* 4. Target Individual Options inside Dropdown Menu */
    li[role="option"] {
        background-color: #1e1e24 !important;
        color: #ffffff !important;
    }

    /* 5. Highlight Option on Hover */
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: #2a2a35 !important;
        color: #ffffff !important;
    }

    /* Metric Cards Styling */
    [data-testid="stMetric"] {
        background-color: #1a1a1e !important;
        border: 1px solid #2d2d35 !important;
        border-radius: 8px !important;
        padding: 16px !important;
    }

    [data-testid="stMetricValue"] * {
        color: #ffffff !important;
        font-size: 32px !important;
        font-weight: bold !important;
    }

    [data-testid="stMetricLabel"] * {
        color: #b0b3c6 !important;
        font-size: 14px !important;
    }

    /* Sidebar Customization */
    [data-testid="stSidebar"] {
        background-color: #141418 !important;
        border-right: 1px solid #2d2d35 !important;
    }

    /* Fixed Sidebar Footer for Name */
    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        font-family: 'Times New Roman', Times, serif !important;
        font-size: 16px !important;
        font-weight: bold !important;
        color: #ffffff !important;
    }

    hr {
        border-color: #2d2d35 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Database Initialization
@st.cache_data
def init_and_load_data():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    
    csv_table_mapping = {
        "1_warehouses_large.csv": "warehouses",
        "2_suppliers_large.csv": "suppliers",
        "3_products_large.csv": "products",
        "4_inventory_large.csv": "inventory",
        "5_orders_large.csv": "orders",
        "6_order_items_large.csv": "order_items",
        "7_carriers_large.csv": "carriers",
        "8_shipments_large.csv": "shipments",
        "9_delivery_tracking_large.csv": "delivery_tracking",
        "10_returns_damages_large.csv": "returns_damages"
    }
    
    for csv_file, table_name in csv_table_mapping.items():
        try:
            df = pd.read_csv(csv_file)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
        except Exception:
            pass

    shipments_df = pd.read_sql("""
        SELECT 
            s.shipment_id, s.order_id, s.carrier_id, c.carrier_name, c.transport_mode,
            s.origin_city, s.destination_city, s.distance_km, s.shipping_cost_inr,
            dt.promised_delivery_date, dt.actual_delivery_date, dt.delay_days, dt.delay_reason,
            dt.delivery_status, dt.customer_satisfaction_score, o.total_amount_inr, o.priority_level
        FROM shipments s
        JOIN carriers c ON s.carrier_id = c.carrier_id
        JOIN delivery_tracking dt ON s.shipment_id = dt.shipment_id
        JOIN orders o ON s.order_id = o.order_id
    """, conn)
    
    inventory_df = pd.read_sql("""
        SELECT 
            i.inventory_id, i.warehouse_id, w.warehouse_name, w.city AS warehouse_city,
            p.product_name, p.category, i.stock_on_hand, i.allocated_stock, i.available_stock,
            i.reorder_level, i.damaged_stock, i.inventory_value_inr
        FROM inventory i
        JOIN warehouses w ON i.warehouse_id = w.warehouse_id
        JOIN products p ON i.sku_id = p.sku_id
    """, conn)
    
    return shipments_df, inventory_df

try:
    shipments_df, inventory_df = init_and_load_data()
except Exception as e:
    st.error(f"Error loading database context: {e}")
    st.stop()

# 4. Clean Navigation Sidebar
st.sidebar.title("Supply Chain OS")
st.sidebar.caption("Logistics & Warehouse Intelligence")

nav_selection = st.sidebar.radio(
    "Navigation Menu",
    [
        "Executive Logistics Dashboard",
        "Delivery Delay & Carrier Performance",
        "Warehouse Inventory Analytics",
        "Real-Time Delay Risk Simulator"
    ]
)

st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-footer">Abhishek</div>', unsafe_allow_html=True)

# 5. Universal High-Contrast Plotly Theme
dark_chart_layout = dict(
    font=dict(family="Times New Roman", size=13, color="#ffffff"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(font=dict(color="#ffffff", size=12)),
    xaxis=dict(
        showgrid=True, gridwidth=1, gridcolor="#22222a",
        tickfont=dict(color="#ffffff"), title_font=dict(color="#ffffff")
    ),
    yaxis=dict(
        showgrid=True, gridwidth=1, gridcolor="#22222a",
        tickfont=dict(color="#ffffff"), title_font=dict(color="#ffffff")
    )
)

# --- PAGE 1: Executive Logistics Dashboard ---
if nav_selection == "Executive Logistics Dashboard":
    st.title("Executive Logistics Control Center")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Active Shipments", f"{len(shipments_df):,}")
    col2.metric("On-Time Delivery Rate", f"{(shipments_df['delay_days'] == 0).mean() * 100:.1f}%")
    col3.metric("Avg Delivery Delay", f"{shipments_df['delay_days'].mean():.2f} Days")
    col4.metric("Total Freight Spend", f"₹{shipments_df['shipping_cost_inr'].sum():,.2f}")
    
    st.markdown("---")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Shipping Cost vs Distance Trajectory")
        fig1 = px.scatter(
            shipments_df, x='distance_km', y='shipping_cost_inr',
            color='transport_mode', hover_data=['origin_city', 'destination_city'],
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig1.update_layout(**dark_chart_layout)
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_b:
        st.subheader("Primary Causes of Logistics Delays")
        fig2 = px.pie(
            shipments_df['delay_reason'].value_counts().reset_index(), 
            values='count', names='delay_reason', hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig2.update_layout(**dark_chart_layout)
        fig2.update_traces(textinfo='percent+label', textfont_color="#ffffff", marker=dict(line=dict(color='#0e0e10', width=2)))
        st.plotly_chart(fig2, use_container_width=True)

# --- PAGE 2: Carrier Performance ---
elif nav_selection == "Delivery Delay & Carrier Performance":
    st.title("Carrier Reliability & Route Diagnostics")
    st.markdown("---")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("Average Delay by Transport Mode")
        mode_delay = shipments_df.groupby('transport_mode')['delay_days'].mean().reset_index()
        fig3 = px.bar(mode_delay, x='transport_mode', y='delay_days', color='transport_mode',
                      color_discrete_sequence=px.colors.qualitative.Safe)
        fig3.update_layout(**dark_chart_layout)
        st.plotly_chart(fig3, use_container_width=True)

    with col_c2:
        st.subheader("Customer Satisfaction vs Delay Days")
        fig4 = px.box(shipments_df, x='customer_satisfaction_score', y='delay_days', 
                      color_discrete_sequence=['#38bdf8'])
        fig4.update_layout(**dark_chart_layout)
        st.plotly_chart(fig4, use_container_width=True)

# --- PAGE 3: Warehouse Inventory Analytics ---
elif nav_selection == "Warehouse Inventory Analytics":
    st.title("Warehouse Inventory & Stock Levels")
    st.markdown("---")
    
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.subheader("Stock Valuation by Category")
        cat_val = inventory_df.groupby('category')['inventory_value_inr'].sum().reset_index()
        fig5 = px.bar(cat_val, x='category', y='inventory_value_inr', color='category',
                      color_discrete_sequence=px.colors.qualitative.Vivid)
        fig5.update_layout(**dark_chart_layout)
        st.plotly_chart(fig5, use_container_width=True)

    with col_w2:
        st.subheader("Available Stock vs Reorder Level")
        fig6 = px.scatter(inventory_df, x='reorder_level', y='available_stock', color='category',
                          color_discrete_sequence=px.colors.qualitative.Dark24)
        fig6.update_layout(**dark_chart_layout)
        st.plotly_chart(fig6, use_container_width=True)

# --- PAGE 4: Delay Risk Simulator ---
elif nav_selection == "Real-Time Delay Risk Simulator":
    st.title("Predictive Shipment Delay Simulator")
    st.markdown("---")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    dist_input = col_s1.slider("Shipment Distance (km)", 100, 2500, 850)
    mode_input = col_s2.selectbox("Transport Mode", ['Road', 'Air', 'Rail', 'Express Highway'])
    priority_input = col_s3.selectbox("Order Priority", ['Standard', 'Express', 'Urgent'])
    
    base_delay = 0.5 + (1.2 if dist_input > 1200 else 0) + (1.0 if mode_input == 'Road' else 0)
    if priority_input == 'Urgent':
        base_delay *= 0.5
        
    st.markdown("---")
    st.markdown(f"### Estimated Shipment Transit Delay: **{round(base_delay, 1)} Days**")
