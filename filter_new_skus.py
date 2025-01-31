import pandas as pd
import streamlit as st
import os

st.title("Shopify New SKU Filter")

st.header("Upload Master Inventory CSV (Existing SKUs - Shopify Export)")
master_file = st.file_uploader("Upload your current Shopify inventory CSV", type=["csv"], key="master")

st.header("Upload Vendor Inventory CSV (New File)")
uploaded_file = st.file_uploader("Upload Vendor Inventory CSV", type=["csv"], key="vendor")

if master_file and uploaded_file:
    df_master = pd.read_csv(master_file)
    df_vendor = pd.read_csv(uploaded_file)

    # 🔹 Normalize column names (remove spaces, fix case sensitivity)
    df_master.columns = df_master.columns.str.strip().str.lower()
    df_vendor.columns = df_vendor.columns.str.strip().str.lower()

    # 🔹 Ensure "variant sku" exists in both files
    if "variant sku" not in df_vendor.columns or "variant sku" not in df_master.columns:
        st.error("Error: Both files must contain a 'Variant SKU' column. Please check your CSV format.")

    # 🔹 Ensure "handle" exists in the Vendor CSV
    elif "handle" not in df_vendor.columns:
        st.error("Error: The Vendor CSV must contain a 'Handle' column. Please check your CSV format.")
    
    else:
        # Identify new SKUs that are NOT in the master inventory
        new_sku_list = df_vendor.loc[~df_vendor["variant sku"].isin(df_master["variant sku"]), "variant sku"].unique()

        # Debugging: Check if new_sku_list is empty
        if len(new_sku_list) == 0:
            st.warning("No new SKUs were found. Please check if the vendor file contains new products.")

        # Keep all rows related to new SKUs (ensures all images stay grouped)
        new_skus_df = df_vendor[df_vendor["variant sku"].isin(new_sku_list)]

        # Debugging: Ensure filtered dataset is not empty before saving
        if new_skus_df.empty:
            st.warning("Filtered dataset is empty. No SKUs were retained after filtering. Please check your files.")
        else:
            # Ensure all handles associated with new SKUs are included
            new_skus_df = df_vendor[df_vendor["handle"].isin(new_skus_df["handle"])]

            # Save and allow download
            new_skus_file = "new_skus_for_upload.csv"
            new_skus_df.to_csv(new_skus_file, index=False)

            st.success("New SKUs extracted successfully! Original format preserved.")
            st.download_button("Download New SKUs CSV", new_skus_df.to_csv(index=False), "new_skus_for_upload.csv", "text/csv")
