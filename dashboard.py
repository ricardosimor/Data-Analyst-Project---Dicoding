import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st
import altair as alt
from babel.numbers import format_currency

st.set_page_config(layout="wide")


# LOAD DATA
ecommerce_df = pd.read_csv("ecommerce.csv", delimiter=",")
datetime_columns = ["purchase_time"]
ecommerce_df.sort_values(by="purchase_time", inplace=True)
ecommerce_df.reset_index(inplace=True)


# HELPER FUNCTION

# KEY METRICS
# 1.Total Revenue
def make_total_revenue(df):
    total_revenue = df.groupby(by='product_category').agg({
        'price' : 'sum'
    }) 
    total_revenue = total_revenue.reset_index()
    total_revenue.rename(columns = {'price' : 'total'
    }, inplace = True)
    return total_revenue

# 2. Total Produk Yang Terjual
def make_product_sold(df):
    product_sold = df[df['order_status'].isin(['shipped', 'delivered'])] \
                    .groupby('product_category') \
                    .agg({'order_id': 'nunique'}) \
                    .reset_index()
    product_sold.rename(columns = {'order_id' : 'total'
    }, inplace = True)
    return product_sold

# 3. Total Transaksi
def make_total_orders(df):
    total_orders = df.groupby(by='product_category').agg({
        'order_id' : 'count'
    }) 
    total_orders = total_orders.reset_index()
    total_orders.rename(columns = {'order_id' : 'total'
    }, inplace = True)
    return total_orders

def format_number(num):
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    else:
        return str(int(num))


# TREN TOTAL ORDER 
def make_monthly_order(df):
    monthly_orders = df.groupby('order_month').agg(
        total_delivered = ('order_status', lambda x: (x == 'delivered').sum()),
        total_canceled = ('order_status', lambda x: (x == 'delivered').sum())
        ).reset_index()
    return monthly_orders


# FUNCTION ANALISIS
# Kategori Produk Penjualan Tertinggi
def make_best_product(df):
    best_product = df.groupby('product_category').agg(
        {'order_id': 'count'}).sort_values(by='order_id', ascending=False).reset_index().rename(columns={'order_id': 'total_order'})
    return best_product

# Early Delivery dan Review Score
def make_ontimegroup(df):
    early_delivered = df[(df['order_status'] == 'delivered') & (df['delivery_delay'] <= 0)]
    ontimegroup = early_delivered.groupby('delivery_delay').agg({
        'review_score' : 'mean'
    }).sort_values(by='delivery_delay', ascending=False).reset_index().rename(columns={'delivery_delay' : 'delivery_time'})
    return ontimegroup

# Delivery Delay dan Review Score
def make_lategroup(df):
    delivered_delay = df[(df['order_status'] == 'delivered') & (df['delivery_delay'] >= 0)]
    late_group = delivered_delay.groupby('delivery_delay').agg({
        'review_score' : 'mean'
    }).sort_values(by='delivery_delay', ascending=True).reset_index().rename(columns={'delivery_delay' : 'delivery_time'})
    return late_group

# Metode Pembayaran terbanyak digunakan
def make_mostpayment(df):
    most_payment = df.groupby('payment_type').agg({
        'order_id': 'count'
        }).sort_values(by='order_id', ascending=False).reset_index().rename(columns={'order_id' : 'total_order'})
    return most_payment

# Product Category Paling Profit
def make_product_profit(df):
    product_profit = df.groupby('product_category').agg({
        'price': 'sum',
        'freight_cost': 'sum'
        }).reset_index()
    product_profit['profit'] = product_profit['price'] - product_profit['freight_cost']
    product_profit = product_profit.sort_values(by='profit', ascending=False)
    return product_profit


# FILTER DATA
min_date = ecommerce_df['purchase_time'].min()
max_date = ecommerce_df['purchase_time'].max()

with st.sidebar:
    st.image('ecommerce.png')

    start_date = st.date_input(
        label='Waktu Awal', min_value = min_date,
        value = min_date
    )
    end_date = st.date_input(
        label='Waktu Akhir', min_value = max_date,
        value=max_date
    )
main_df = ecommerce_df[
    (ecommerce_df['purchase_time'] >= str(start_date)) &
    (ecommerce_df['purchase_time'] <= str(end_date))
    ]



# INPUT DATA KE FUNCTION
total_revenue = make_total_revenue(main_df)
total_product_sold = make_product_sold(main_df)
total_orders = make_total_orders(main_df)
tren_monthly = make_monthly_order(main_df)
product_best= make_best_product(main_df)
cepat_antar = make_ontimegroup(main_df)
lambat_antar = make_lategroup(main_df)
metode_pembayaran = make_mostpayment(main_df)
profit_product = make_product_profit(main_df)




# DASHBOARD   
st.header("Brazillian E-Commerce Dashboard :sparkles:")

st.subheader('Overview')
col1, col2, col3, col4 = st.columns(4)

# Key Metrics Section
with col1:
    total_revenue_sm = total_revenue['total'].sum()
    st.metric("Total Revenue", value=format_number(total_revenue_sm))

with col2:
    total_product_sm = total_product_sold['total'].sum()
    st.metric("Total Product Sold", value=format_number(total_product_sm))

with col3:
    total_orders_sm = total_orders['total'].sum()
    st.metric("Total Orders", value=format_number(total_orders_sm))

with col4:
    st.markdown(
        "<div style='text-align:center; font-weight:bold; font-size:20px;'>Metode Pembayaran</div>",
        unsafe_allow_html=True
    )
    metode_pembayaran = metode_pembayaran.reset_index(drop=True)
    max_order = metode_pembayaran['total_order'].max()
    metode_pembayaran['Progress'] = metode_pembayaran['total_order']
    metode_pembayaran['payment_type'] = metode_pembayaran['payment_type'].replace({
    'credit_card': 'Kartu Kredit',
    'boleto': 'Boleto (Virtual)',
    'voucher': 'Voucher',
    'debit_card': 'Kartu Debit'
    })
    metode_pembayaran['Jumlah'] = metode_pembayaran['total_order'].apply(lambda x: f"{x:,}".replace(",", "."))
    table_data = metode_pembayaran[['payment_type', 'Progress']].rename(
        columns={'payment_type': 'Payment Type'}
    )

    st.markdown(
    """
    <style>
    .stDataFrame {width: 100% !important;}
    </style>
    """,
    unsafe_allow_html=True
    )
    
    st.dataframe(table_data, hide_index=True, use_container_width=True)


# VISUALIZE DATA
# Tren Total Order Bulan/Year
st.subheader("Tren Total Order")
fig, ax = plt.subplots(figsize = (20,8))
ax.plot(tren_monthly['order_month'], tren_monthly['total_delivered'], label = 'Delivered')
ax.plot(tren_monthly['order_month'], tren_monthly['total_canceled'], label = 'Canceled')

ax.set_title(None)
ax.set_xlabel('Waktu (Bulan/Tahun)', fontsize = 12)
ax.set_ylabel('Jumlah', fontsize=12)
ax.legend()
ax.set_xticks(range(0, len(tren_monthly['order_month']), 2))
ax.tick_params(rotation=0)
st.pyplot(fig)

# Tren Total Order Bulan/Year
st.subheader("Top Kategori Produk Terlaris")
product_best['product_category'] = (product_best['product_category']
.str.replace('_', ' ')
.str.title()
)
top_n = st.slider("Pilih jumlah kategori", 5, 30, 10, key='product_best')
fig, ax = plt.subplots(figsize=(12, top_n * 0.5))
sns.barplot(
data=product_best.head(top_n),
x='total_order',
y='product_category',
palette='Blues_r',
ax=ax
)
ax.set_title(None)
ax.set_xlabel('Jumlah Pembelian', fontsize=12)
ax.set_ylabel('')  

# Tambahkan label pada bar dengan format ribuan dan efek stroke
for container in ax.containers:
    labels = [f"{int(v):,}".replace(",", ".") for v in container.datavalues]
    for bar, label in zip(container.patches, labels):
        ax.annotate(
            label,
            (bar.get_width() - (bar.get_width() * 0.02),  # sedikit geser ke kiri
            bar.get_y() + bar.get_height() / 2),
            ha='right', va='center',
            color='white',
            fontsize=11,
            fontweight='bold',
            path_effects=[pe.withStroke(linewidth=2, foreground='black')]
        )
st.pyplot(fig)

st.subheader("Delivery Time and Review Score")
col1, col2 = st.columns([1,1])

with col1:
    st.markdown("<div style='text-align:center; font-weight:bold; font-size:20px;'>Early Delivery</div>", unsafe_allow_html=True)
    cepat_antar['delivery_time'] = cepat_antar['delivery_time'].abs()
    fig, ax = plt.subplots(figsize = (12,5))
    ax.plot(cepat_antar['delivery_time'], cepat_antar['review_score'], color = 'green')
    ax.set_title(None)
    ax.set_xlabel('Hari')
    ax.set_ylabel('Rata-Rata Review Score')
    ax.tick_params(rotation=0)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0)
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
    st.pyplot(fig)

with col2:
    st.markdown("<div style='text-align:center; font-weight:bold; font-size:20px;'>Delay Delivery</div>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize = (12,5))
    ax.plot(lambat_antar['delivery_time'], lambat_antar['review_score'], color='red')
    ax.set_title(None)
    ax.set_xlabel('Hari')
    ax.set_ylabel('')
    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.tick_params(rotation=0)
    st.pyplot(fig)

st.subheader('Kategori Produk Profit Tertinggi')
profit_product['product_category'] = (profit_product['product_category']
.str.replace('_', ' ')
.str.title()
)
top_n = st.slider("Pilih jumlah kategori", 5, 30, 10, key='profit_slider')
fig, ax = plt.subplots(figsize=(12, top_n * 0.5))
sns.barplot(
data=profit_product.head(top_n),
x='profit',
y='product_category',
hue='product_category', 
palette='Blues_r',
ax=ax
)
ax.set_title(None)
ax.set_xlabel('Jumlah Pembelian', fontsize=12)
ax.set_ylabel('')  

# Tambahkan label pada bar dengan format ribuan dan efek stroke
for container in ax.containers:
    labels = [f"{int(v):,}".replace(",", ".") for v in container.datavalues]
    for bar, label in zip(container.patches, labels):
        ax.annotate(
            label,
            (bar.get_width() - (bar.get_width() * 0.02),  # sedikit geser ke kiri
             bar.get_y() + bar.get_height() / 2),
            ha='right', va='center',
            color='white',
            fontsize=11,
            fontweight='bold',
            path_effects=[pe.withStroke(linewidth=2, foreground='black')]
        )
st.pyplot(fig)

