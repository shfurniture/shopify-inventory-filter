import streamlit as st
import pandas as pd

# Function to load and compare SKUs
def process_sku_file(uploaded_file, previous_file):
    if uploaded_file is None:
        return None, "Please upload a file."
    
    # Read uploaded file
    df = pd.read_csv(uploaded_file)
    
    # Standardize column names
    column_mapping = {
        "Variant SKU": "SKU",
        "Title": "Product Title",
        "Body (HTML)": "Description",
        "Vendor": "Supplier",
        "Product Category": "Category",
        "Option1 Name": "Option Name",
        "Option1 Value": "Option Value",
        "Variant Price": "Price",
        "Status": "Product Status"
    }
    df.rename(columns=column_mapping, inplace=True)
    
    # Extract SKU column
    if "SKU" not in df.columns:
        return None, "Column 'SKU' not found in uploaded file."
    
    new_skus = df[["SKU"]].dropna()
    
    # If a previous file exists, filter out existing SKUs
    if previous_file is not None:
        prev_df = pd.read_csv(previous_file)
        if "SKU" in prev_df.columns:
            old_skus = set(prev_df["SKU"].dropna())
            new_skus = df[~df["SKU"].isin(old_skus)]
    else:
        new_skus = df
    
    # Define new structure based on required export format
    new_columns = ["SKU", "Product Title", "Description", "Supplier", "Category", "Option Name", "Option Value", "Price", "Product Status"]
    
    new_skus = new_skus[new_columns] if all(col in new_skus.columns for col in new_columns) else None
    
    return new_skus, "Processing completed." if new_skus is not None else "Invalid column structure."

# Streamlit UI
st.title("Shopify SKU Filter and Export")

uploaded_file = st.file_uploader("Upload Shopify Product CSV", type=["csv"])
previous_file = st.file_uploader("Upload Previous Inventory CSV (Optional)", type=["csv"])

if uploaded_file:
    filtered_data, message = process_sku_file(uploaded_file, previous_file)
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
