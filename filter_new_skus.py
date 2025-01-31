import pandas as pd
import streamlit as st
import os
import difflib

st.title("Shopify New SKU Filter")

st.header("Upload Master Inventory CSV (Existing SKUs - Shopify Export)")
master_file = st.file_uploader("Upload your current Shopify inventory CSV", type=["csv"], key="master")

st.header("Upload Vendor Inventory CSV (New File)")
uploaded_file = st.file_uploader("Upload Vendor Inventory CSV", type=["csv"], key="vendor")

if master_file and uploaded_file:
    df_master = pd.read_csv(master_file)
    df_vendor = pd.read_csv(uploaded_file)

    # 🔹 Normalize column names (strip spaces, convert to lowercase)
    df_master.columns = df_master.columns.str.strip().str.lower()
    df_vendor.columns = df_vendor.columns.str.strip().str.lower()

    # 🔹 Ensure necessary columns exist
    if "variant sku" not in df_vendor.columns or "variant sku" not in df_master.columns:
        st.error("Error: Both files must contain a 'Variant SKU' column. Please check your CSV format.")
    elif "title" not in df_vendor.columns:
        st.error("Error: The Vendor CSV must contain a 'Title' column. Please check your CSV format.")
    else:
        # Identify new SKUs that are NOT in the master inventory
        new_sku_list = df_vendor.loc[~df_vendor["variant sku"].isin(df_master["variant sku"]), "variant sku"].unique()

        # Keep all rows related to new SKUs
        new_skus_df = df_vendor[df_vendor["variant sku"].isin(new_sku_list)].copy()

        # Create an empty dictionary for handles
        handle_map = {}

        # Standardize product names and merge similar listings
        def generate_handle(name):
            return name.lower().replace(" ", "-").replace("/", "-").replace("&", "and")

        # Grouping similar product names
        unique_titles = list(new_skus_df["title"].unique())
        grouped_titles = {}

        for title in unique_titles:
            similar = difflib.get_close_matches(title, unique_titles, cutoff=0.8)
            key_title = similar[0] if similar else title
            if key_title not in grouped_titles:
                grouped_titles[key_title] = []
            grouped_titles[key_title].append(title)

        # Assigning handles and merging similar listings
        for base_title, similar_titles in grouped_titles.items():
            handle = generate_handle(base_title)
            for title in similar_titles:
                handle_map[title] = handle

        # Apply the generated handles
        new_skus_df["handle"] = new_skus_df["title"].map(handle_map)

        # Format title to reflect variant nature
        def format_title(title):
            return title.split(" ")[0] + " " + " ".join(title.split(" ")[1:3]) + " with different variants"

        new_skus_df["title"] = new_skus_df["title"].map(format_title)

        # Save the final processed CSV
        new_skus_file = "new_skus_for_upload.csv"
        new_skus_df.to_csv(new_skus_file, index=False)

        st.success("New SKUs extracted successfully! Handles assigned and similar listings merged.")
        st.download_button("Download New SKUs CSV", new_skus_df.to_csv(index=False), "new_skus_for_upload.csv", "text/csv")
