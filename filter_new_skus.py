import streamlit as st
import pandas as pd

# Function to load and compare SKUs
def process_sku_file(uploaded_file, previous_file):
    if uploaded_file is None:
        return None, "Please upload a file."
    
    # Read uploaded file
    df = pd.read_csv(uploaded_file)
    
    # Extract SKU column (assuming "Variant SKU" exists)
    if "Variant SKU" not in df.columns:
        return None, "Column 'Variant SKU' not found in uploaded file."
    
    new_skus = df[["Variant SKU"]].dropna()
    
    # If a previous file exists, filter out existing SKUs
    if previous_file is not None:
        prev_df = pd.read_csv(previous_file)
        if "Variant SKU" in prev_df.columns:
            old_skus = set(prev_df["Variant SKU"].dropna())
            new_skus = df[~df["Variant SKU"].isin(old_skus)]
    else:
        new_skus = df
    
    # Define new structure based on required export format
    new_columns = ["Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Type", "Tags", 
                   "Published", "Option1 Name", "Option1 Value", "Variant SKU", "Variant Price", "Status"]
    
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
