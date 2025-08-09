import streamlit as st
import pandas as pd

st.title("Shopify CSV Merger – Update Old with New Data")

# Upload files
old_file = st.file_uploader("Upload OLD Shopify CSV", type=['csv'])
new_file = st.file_uploader("Upload NEW Shopify CSV", type=['csv'])

if old_file and new_file:
    try:
        old_df = pd.read_csv(old_file, encoding='utf-8', dtype=str)
        new_df = pd.read_csv(new_file, encoding='utf-8', dtype=str)
    except UnicodeDecodeError:
        old_df = pd.read_csv(old_file, encoding='latin1', dtype=str)
        new_df = pd.read_csv(new_file, encoding='latin1', dtype=str)

    # Strip column names
    old_df.columns = old_df.columns.str.strip()
    new_df.columns = new_df.columns.str.strip()

    if 'Handle' not in old_df.columns or 'Handle' not in new_df.columns:
        st.error(f""" 'Handle' column not found.
        
         Columns in OLD file: {list(old_df.columns)}
        Columns in NEW file: {list(new_df.columns)}

        Make sure the column is exactly named 'Handle' (case-sensitive and no extra spaces).
        """)
    else:
        # Combine both files
        # Remove old rows that have the same Handle + Option1 Value (to simulate a unique product variant)
        merge_cols = ['Handle', 'Option1 Value'] if 'Option1 Value' in old_df.columns else ['Handle'] 

        # Drop overlapping rows in old_df
        merged_df = old_df.copy() # Create a copy to avoid modifying the original DataFrame

         # Drop rows with matching Handle + Option1 Value
        merged_df = merged_df[~merged_df[merge_cols].apply(tuple, axis=1).isin(  new_df[merge_cols].apply(tuple, axis=1))]

        # Concatenate the new data (will overwrite duplicates)
        final_df = pd.concat([merged_df, new_df], ignore_index=True)

        st.success("Merge complete. Download the updated CSV below:")

        # Download merged CSV
        csv = final_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Merged CSV", csv, "updated_shopify.csv", "text/csv")

        # Optional preview
        st.subheader("Preview (first 10 rows)")
        st.dataframe(final_df.head(10))

else:
    st.info("Please upload both OLD and NEW Shopify CSV files to proceed.")
