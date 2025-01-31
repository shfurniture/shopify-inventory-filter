import pandas as pd
import streamlit as st
import os

st.title("Shopify New SKU Filter")

uploaded_file = st.file_uploader("Upload Vendor Inventory CSV", type=["csv"])

if uploaded_file:
    df_vendor = pd.read_csv(uploaded_file)
    
    master_inventory_file = "master_inventory.csv"

    if os.path.exists(master_inventory_file):
        df_master = pd.read_csv(master_inventory_file)
    else:
        df_master = pd.DataFrame(columns=["Variant SKU"])

    new_skus = df_vendor[~df_vendor["Variant SKU"].isin(df_master["Variant SKU"])]

    new_skus_file = "new_skus_for_upload.csv"
    new_skus.to_csv(new_skus_file, index=False)

    st.success("New SKUs extracted successfully!")
    st.download_button("Download New SKUs CSV", new_skus.to_csv(index=False), "new_skus_for_upload.csv", "text/csv")

    df_master = pd.concat([df_master, new_skus[["Variant SKU"]]], ignore_index=True).drop_duplicates()
    df_master.to_csv(master_inventory_file, index=False)