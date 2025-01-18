# Mengimpor Library yang Dibutuhkan Untuk Pembuatan Dashboard

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Membuat Function Helper Sekaligus Menyiapkan DataFrame

def by_city_df_function(all_dataset_df):
    by_city_df = all_dataset_df.groupby(by="customer_city").customer_id.nunique().reset_index()
    by_city_df.rename(columns={"customer_id": "customer_count"}, inplace=True)

    return by_city_df

def by_state_df_function(all_dataset_df):
    by_state_df = all_dataset_df.groupby(by="customer_state").customer_id.nunique().reset_index()
    by_state_df.rename(columns={"customer_id": "customer_count"}, inplace=True)

    return by_state_df

def monthly_orders_df_function(all_dataset_df):
    latest_year_df = all_dataset_df[all_dataset_df['order_delivered_customer_date'].dt.year == 2018]
    monthly_orders_df = latest_year_df.resample(rule="M", on="order_delivered_customer_date").agg({
          "order_id": "nunique",
          "price": "sum"
    })
    monthly_orders_df.index = monthly_orders_df.index.strftime("%B")
    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "total_revenue"
    }, inplace=True)

    return monthly_orders_df

def sum_of_product_category_df_function(all_dataset_df):
    sum_of_product_category_df = all_dataset_df.groupby(by="product_category_name_english").agg({
        "order_id": "count"
    }).rename(columns={"order_id": "total_sales"}). sort_values(by="total_sales", ascending=False)

    return sum_of_product_category_df

def rfm_analysis_df_function(all_dataset_df):
    rfm_analysis_df = all_dataset_df.groupby(by="customer_id", as_index=False).agg({
        "order_delivered_customer_date": "max",
        "order_id": "nunique",
        "price": "sum"
    }).rename(columns={
        "order_delivered_customer_date": "recency_date",
        "order_id": "frequency",
        "price": "monetary"
    })

    rfm_analysis_df.columns = ["customer_id", "recency_date", "frequency", "monetary"]

    rfm_analysis_df["recency_date"] = rfm_analysis_df["recency_date"].dt.date
    recent_date = all_dataset_df["order_delivered_customer_date"].dt.date.max()
    rfm_analysis_df["recency"] = rfm_analysis_df["recency_date"].apply(lambda x: (recent_date - x).days)

    rfm_analysis_df.drop(columns="recency_date", axis=1, inplace=True)

    return rfm_analysis_df

# Memuat Berkas main_data.csv (Berkas yang Sudah Dibersihkan Pada Tahap Sebelumnya)

all_dataset_df = pd.read_csv("dashboard/main_data.csv")

# Membuat Komponen Filter 

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_dataset_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_dataset_df.reset_index(inplace=True)

for column in datetime_columns:
    all_dataset_df[column] = pd.to_datetime(all_dataset_df[column])

min_date = all_dataset_df["order_purchase_timestamp"].min()
max_date = all_dataset_df["order_purchase_timestamp"].max()

with st.sidebar:

  start_date, end_date = st.date_input(
      label="Rentang Waktu",
      min_value=min_date,
      max_value=max_date,
      value=[min_date, max_date]
  )

main_df = all_dataset_df[(all_dataset_df["order_purchase_timestamp"] >= str(start_date)) &
                        (all_dataset_df["order_purchase_timestamp"] <= str(end_date))]

by_city_df = by_city_df_function(main_df)
by_state_df = by_state_df_function(main_df)
monthly_orders_df = monthly_orders_df_function(main_df)
sum_of_product_category_df = sum_of_product_category_df_function(main_df)
rfm_analysis_df = rfm_analysis_df_function(main_df)

# Memasukkan Visualisasi Data ke dalam Dashboard

# Visualisasi Data 1: Demografi Pelanggan Berdasarkan Kota dan Negara Bagian

st.header("Proyek Analisis Data: E-Commerce Public Dataset :sparkles:")

st.subheader("Demografi Pelanggan Berdasarkan Kota dan Negara Bagian")

col1, col2 = st.columns(2)

with col1:
    colors = ["#FF8C00", "#FFEF96", "#FFEF96", "#FFEF96", "#FFEF96"]

    fig, ax = plt.subplots(figsize=(8, 4))

    sns.barplot(
        x="customer_city",
        y="customer_count",
        data=by_city_df.sort_values(by="customer_count", ascending=False).head(5),
        palette=colors,
        ax=ax
    )
    ax.set_title("Demografi Pelanggan Berdasarkan Kota", loc="center", fontsize=17)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis="x", labelsize=10)
    ax.tick_params(axis="y", labelsize=8)
    st.pyplot(fig)

with col2:
    colors = ["#FF8C00", "#FFEF96", "#FFEF96", "#FFEF96", "#FFEF96"]

    fig, ax = plt.subplots(figsize=(8, 4))

    sns.barplot(
        x="customer_state",
        y="customer_count",
        data=by_state_df.sort_values(by="customer_count", ascending=False).head(5),
        palette=colors,
        ax=ax
    )
    ax.set_title("Demografi Pelanggan Berdasarkan Negara Bagian", loc="center", fontsize=17)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis="x", labelsize=10)
    ax.tick_params(axis="y", labelsize=8)
    st.pyplot(fig)

# Visualisasi Data 2: Performa Penjualan dan Kinerja Pendapatan Per Bulan (2018)

st.subheader("Performa Penjualan dan Kinerja Pendapatan Per Bulan (2018)")

col1, col2 = st.columns(2)

with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Performa Penjualan Per Bulan (2018)", value=total_orders)

with col2:
    total_revenue = format_currency(monthly_orders_df.total_revenue.sum(), "AUD", locale="es_CO")
    st.metric("Kinerja Pendapatan Per Bulan (2018)", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_delivered_customer_date"],
    monthly_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#FF8C00"
)
ax.tick_params(axis="y", labelsize=10)
ax.tick_params(axis="x", labelsize=10)

st.pyplot(fig)

# Visualisasi Data 3: Katagori Produk Paling Banyak dan Paling Sedikit Terjual

st.subheader("Katagori Produk Paling Banyak dan Paling Sedikit Terjual")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))

colors = ["#FF8C00", "#FFEF96", "#FFEF96", "#FFEF96", "#FFEF96"]

sns.barplot(x="total_sales", y="product_category_name_english", data=sum_of_product_category_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Jumlah Penjualan", fontsize=14)
ax[0].set_title("Katagori Produk Paling Banyak Terjual", loc="center", fontsize=18)
ax[0].tick_params(axis="y", labelsize=14)
ax[0].tick_params(axis="x", labelsize=12)

sns.barplot(x="total_sales", y="product_category_name_english", data=sum_of_product_category_df.sort_values(by="total_sales", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Jumlah Penjualan", fontsize=14)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Katagori Produk Paling Sedikit Terjual", loc="center", fontsize=18)
ax[1].tick_params(axis="y", labelsize=14)
ax[1].tick_params(axis="x", labelsize=12)

st.pyplot(fig)

# Visualisasi Data 4: Analisis RFM (Recency, Frequency dan Monetary)

st.subheader("Analisis RFM (Recency, Frequency dan Monetary)")

col1, col2, col3 = st.columns(3)

with col1:
    mean_recency = round(rfm_analysis_df.recency.mean(), 1)
    st.metric("Rata-Rata Recency (Hari)", value=mean_recency)

with col2:
    mean_frequency = round(rfm_analysis_df.frequency.mean(), 2)
    st.metric("Rata-Rata Frequency (Transaksi)", value=mean_frequency)

with col3:
    mean_frequency = format_currency(rfm_analysis_df.monetary.mean(), "R$", locale="pt_BR")
    st.metric("Rata-Rata Monetary (Total Pembelanjaan)", value=mean_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(38, 10))
colors = ["#FF8C00", "#FF8C00", "#FF8C00", "#FF8C00", "#FF8C00"]

sns.barplot(y="recency", x="customer_id", data=rfm_analysis_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Customer ID", fontsize=20)
ax[0].set_title("Recency (Hari)", loc="center", fontsize=22)
ax[0].tick_params(axis="x", rotation=100, labelsize=18)
ax[0].tick_params(axis="y", labelsize=15)

sns.barplot(y="frequency", x="customer_id", data=rfm_analysis_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Customer ID", fontsize=20)
ax[1].set_title("Frequency (Transaksi)", loc="center", fontsize=22)
ax[1].tick_params(axis="x", rotation=90, labelsize=18)
ax[1].tick_params(axis="y", labelsize=15)

sns.barplot(y="monetary", x="customer_id", data=rfm_analysis_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("Customer ID", fontsize=20)
ax[2].set_title("Monetary (Total Pembelanjaan)", loc="center", fontsize=22)
ax[2].tick_params(axis="x", rotation=80, labelsize=18)
ax[2].tick_params(axis="y", labelsize=15)

st.pyplot(fig)

st.caption("Copyright (c) Muhammad Adib 2025")