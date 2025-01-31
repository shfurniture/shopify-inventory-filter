import pandas as pd
import streamlit as st
import os

st.title("Shopify New SKU Filter")

st.header("Upload Master Inventory CSV (Existing SKUs)")
master_file = st.file_uploader("Upload your current Shopify inventory CSV", type=["csv"], key="master")

st.header("Upload Vendor Inventory CSV (New File)")
uploaded_file = st.file_uploader("Upload Vendor Inventory CSV", type=["csv"], key="vendor")

if master_file and uploaded_file:
    df_master = pd.read_csv(master_file)
    df_vendor = pd.read_csv(uploaded_file)

    if "Variant SKU" not in df_vendor.columns or "Variant SKU" not in df_master.columns:
        st.error("CSV files must contain a 'Variant SKU' column.")
    else:
        new_skus = df_vendor[~df_vendor["Variant SKU"].isin(df_master["Variant SKU"])]

        new_skus_file = "new_skus_for_upload.csv"
        new_skus.to_csv(new_skus_file, index=False)

        st.success("New SKUs extracted successfully!")
        st.download_button("Download New SKUs CSV", new_skus.to_csv(index=False), "new_skus_for_upload.csv", "text/csv")
