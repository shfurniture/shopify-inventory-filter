import streamlit as st
import pandas as pd

# Function to load and compare SKUs
def process_sku_file(shopify_file, vendor_file):
    if shopify_file is None or vendor_file is None:
        return None, "Please upload both files."
    
    # Read uploaded files
    shopify_df = pd.read_csv(shopify_file)
    vendor_df = pd.read_csv(vendor_file)
    
    # Standardize column names
    column_mapping_vendor = {
        "Title": "Title",
        "Body HTML": "Body (HTML)",
        "Variant SKU": "Variant SKU",
        "Variant Price": "Variant Price",
        "Status": "Status"
    }
    
    column_mapping_shopify = {
        "Handle": "Handle",
        "Title": "Title",
        "Body (HTML)": "Body (HTML)",
        "Variant SKU": "Variant SKU",
        "Variant Price": "Variant Price",
        "Status": "Status"
    }
    
    vendor_df.rename(columns=column_mapping_vendor, inplace=True)
    shopify_df.rename(columns=column_mapping_shopify, inplace=True)
    
    # Extract SKU column
    if "Variant SKU" not in shopify_df.columns or "Variant SKU" not in vendor_df.columns:
        return None, "Column 'Variant SKU' not found in one of the files."
    
    old_skus = set(shopify_df["Variant SKU"].dropna())
    new_skus = vendor_df[~vendor_df["Variant SKU"].isin(old_skus)]
    
    # Define new structure based on required export format
    new_columns = ["Handle", "Title", "Body (HTML)", "Variant SKU", "Variant Price", "Status"]
    
    new_skus = new_skus[new_columns] if all(col in new_skus.columns for col in new_columns) else None
    
    return new_skus, "Processing completed." if new_skus is not None else "Invalid column structure."

# Streamlit UI
st.title("Shopify SKU Filter and Export")

st.header("Upload Current Shopify Listings")
shopify_file = st.file_uploader("Upload the CSV file containing current Shopify product listings", type=["csv"])

st.header("Upload New Inventory from Vendor")
vendor_file = st.file_uploader("Upload the CSV file containing the new inventory received from the vendor", type=["csv"])

if shopify_file and vendor_file:
    filtered_data, message = process_sku_file(shopify_file, vendor_file)
    st.write(message)
    
    if filtered_data is not None:
        st.dataframe(filtered_data)
        
        # Allow user to download the filtered file
        csv = filtered_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download New SKUs CSV",
            data=csv,
            file_name="new_skus_export.csv",
            mime="text/csv"
        )
