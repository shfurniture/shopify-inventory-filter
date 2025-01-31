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

    # Normalize column names
    df_master.columns = df_master.columns.str.strip().str.lower()
    df_vendor.columns = df_vendor.columns.str.strip().str.lower()

    # Ensure necessary columns exist
    required_columns = ["variant sku", "title", "image src"]
    missing_columns = [col for col in required_columns if col not in df_vendor.columns]
    if missing_columns:
        st.error(f"Error: The Vendor CSV is missing required columns: {', '.join(missing_columns)}. Please check your CSV format.")
        st.stop()

    # Identify new SKUs that are NOT in the master inventory
    new_sku_list = df_vendor.loc[~df_vendor["variant sku"].isin(df_master["variant sku"]), "variant sku"].unique()
    new_skus_df = df_vendor[df_vendor["variant sku"].isin(new_sku_list)].copy()

    # Generate unique handles for similar products
    def generate_handle(name):
        return name.lower().replace(" ", "-").replace("/", "-").replace("&", "and")

    unique_titles = list(new_skus_df["title"].unique())
    grouped_titles = {}
    for title in unique_titles:
        similar = difflib.get_close_matches(title, unique_titles, cutoff=0.8)
        key_title = similar[0] if similar else title
        if key_title not in grouped_titles:
            grouped_titles[key_title] = []
        grouped_titles[key_title].append(title)

    handle_map = {title: generate_handle(base_title) for base_title, similar_titles in grouped_titles.items() for title in similar_titles}
    new_skus_df["handle"] = new_skus_df["title"].map(handle_map)

    # Format title and blank out variant rows where needed
    first_occurrences = new_skus_df.groupby("handle").head(1).index
    new_skus_df.loc[~new_skus_df.index.isin(first_occurrences), ["title", "body (html)", "vendor", "product category", "tags", "published"]] = ""

    # Assign Image Position based on Handle
    new_skus_df["image position"] = new_skus_df.groupby("handle").cumcount() + 1
    
    # Reorder columns to match Shopify's format
    shopify_columns = [
        "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type", "Tags", "Published", 
        "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value", "Option3 Name", "Option3 Value", 
        "Variant SKU", "Variant Grams", "Variant Inventory Tracker", "Variant Inventory Qty", 
        "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price", "Variant Compare At Price", 
        "Variant Requires Shipping", "Variant Taxable", "Variant Barcode", "Image Src", "Image Position", 
        "Image Alt Text", "Gift Card", "SEO Title", "SEO Description", "Google Shopping / Google Product Category"
    ]

    # Keep only columns that exist in both Shopify and the export
    available_columns = [col for col in shopify_columns if col.lower() in new_skus_df.columns]
    missing_shopify_columns = [col for col in shopify_columns if col.lower() not in new_skus_df.columns]
    
    if missing_shopify_columns:
        st.warning(f"Warning: The exported file is missing some expected Shopify columns: {', '.join(missing_shopify_columns)}")
    
    new_skus_df = new_skus_df[available_columns]

    # Save the formatted output
    new_skus_file = "new_skus_for_upload.csv"
    new_skus_df.to_csv(new_skus_file, index=False)

    st.success("New SKUs extracted successfully! Shopify format applied with proper image handling.")
    st.download_button("Download New SKUs CSV", new_skus_df.to_csv(index=False), "new_skus_for_upload.csv", "text/csv")
