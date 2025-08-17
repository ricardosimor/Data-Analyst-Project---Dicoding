import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')


# Helper Function
def total_revenue_df(df):
    total_revenue = df.groupby(by='product_category_name').agg({
        'price' : 'sum'
    }) 
    total_revenue = total_revenue.reset_index()
    total_revenue.rename(columns = {'price' : 'total'
    }, inplace = True)
    return total_revenue

def product_sold_df(df):
    product_sold = df[df['order_status'] == 'delivered'].groupby(by='product_category_name').agg({
        'order_id':'nunique'
    }) 
    product_sold = product_sold.reset_index()
    product_sold.rename(columns = {'order_id' : 'total'
    }, inplace = True)
    return product_sold

def total_orders_df(df):
    total_orders = df.groupby(by='product_category_name').agg({
        'order_id' : 'nunique'
    }) 
    total_orders = total_orders.reset_index()
    total_orders.rename(columns = {'order_id' : 'total'
    }, inplace = True)
    return total_orders

def create_bestreviews_df(df):
    best_reviews = df.groupby(by='product_category_name').agg({
        'order_id' : "nunique",
        'review_score' : "mean"
    }).sort_values(by='review_score', ascending=False)
    return best_reviews


def create_worstreviews_df(df):
    worst_reviews = df.groupby(by='product_category_name').agg({
        'order_id' : "nunique",
        'review_score' : "mean"
    }).sort_values(by='review_score', ascending=True)
    return worst_reviews

def create_high_order_2018_df(df):
    high_order_2018 = df[df['order_year'] == 2018].groupby(by='product_category_name').agg({
        'order_id' : 'nunique',
        'price' : 'sum'
    }).sort_values(by='order_id', ascending=False)
    return high_order_2018

def create_rfm_df(df):
    rfm_df = df.groupby(by = 'customer_id', as_index=False).agg({
    'order_delivered_customer_date' : 'max',
    'order_id' : 'nunique',
    'price' : 'sum'
    })
    rfm_df.columns = ['customer_id', 'max_order_timestamp', 'frequency', 'monetary']
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
    rfm_df['max_order_timestamp'] = pd.to_datetime(rfm_df['max_order_timestamp'])
    rfm_df['max_order_timestamp'] = rfm_df['max_order_timestamp'].dt.date
    recent_date = df['order_delivered_customer_date'].max().date()
    rfm_df = rfm_df[rfm_df['max_order_timestamp'].notna()]
    rfm_df['recency'] = rfm_df['max_order_timestamp'].apply(lambda x: (recent_date - x).days)
    rfm_df.drop('max_order_timestamp', axis=1, inplace=True)
    return rfm_df

#Load Data
all_orders_df = pd.read_csv("all_orders_df.csv")

datetime_columns = ["order_delivered_customer_date"]
all_orders_df.sort_values(by="order_delivered_customer_date", inplace=True)
all_orders_df.reset_index(inplace=True)

for column in datetime_columns:
    all_orders_df[column] = pd.to_datetime(all_orders_df[column])

# Filter Data
min_date = all_orders_df['order_delivered_customer_date'].min()
max_date = all_orders_df['order_delivered_customer_date'].max()

with st.sidebar:
    st.image('ecommerce.png')

    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value = min_date,
        max_value = max_date,
        value = [min_date, max_date]
    )
main_df = all_orders_df[(all_orders_df['order_delivered_customer_date'] >= str(start_date)) &
                                            (all_orders_df['order_delivered_customer_date'] <= str(end_date))]

total_revenue = total_revenue_df(main_df)
total_orders = total_orders_df(main_df)
product_sold = product_sold_df(main_df)
product_bestreviews = create_bestreviews_df(main_df)
product_worstreviews = create_worstreviews_df(main_df)
product_highorder = create_high_order_2018_df(main_df)
rfm_df = create_rfm_df(main_df)

    
st.header("E-Commerce Dashboard :sparkles:")

st.subheader('Operational Highlights')
col1, col2, col3 = st.columns(3)
 
with col1:
    total_revenue_sm = total_revenue['total'].sum()
    st.metric("Total Revenue", value=total_revenue_sm)

with col2:
    total_product_sm = product_sold['total'].sum()
    st.metric("Product Sold", value=total_product_sm)

with col3:
    total_orders_sm = total_orders['total'].sum()
    st.metric("Total Orders", value=total_orders_sm)

st.subheader("Category Product With Best Review & Worst Review")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(y="product_category_name", x="review_score", data=product_bestreviews.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Score Review", fontsize=30)
ax[0].set_title("Best Review Category Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(y="product_category_name", x="review_score", data=product_worstreviews.head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].invert_xaxis()
ax[1].set_xlabel("Score Review", fontsize=30)
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Review Category Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
st.pyplot(fig)


st.subheader("Category Product With High Order")
fig, ax = plt.subplots(figsize = (20,10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x = 'order_id',
    y = 'product_category_name',
    data = product_highorder.head(10).sort_values(by = 'order_id', ascending=False),
    palette = colors,
    ax=ax
)
ax.set_title(None)
ax.set_xlabel('Order', fontsize=30)
ax.set_ylabel(None)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
st.pyplot(fig)

st.subheader('Best Customer Based on RFM Parameters')
col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric('Average Recency (Days)', value=avg_recency)
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric('Average Frequency', value=avg_frequency)
with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "USD", locale='pt_BR')
    st.metric("Average Monetary", value=avg_monetary)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
 
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=20)
ax[0].tick_params(axis='x', labelsize=20, rotation=50)
 
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=20)
ax[1].tick_params(axis='x', labelsize=20, rotation=50)
 
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=20)
ax[2].tick_params(axis='x', labelsize=20, rotation=50)
 
st.pyplot(fig)