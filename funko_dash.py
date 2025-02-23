import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data(file_path):
    """
    Load and process the Funko Pop CSV data.
    
    Args:
        file_path (str): Path to the CSV file.
    
    Returns:
        tuple: (DataFrame or None, error message or None)
            - If successful: (processed DataFrame, None)
            - If an error occurs: (None, error message as string)
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Rename columns to user-friendly names
        df = df.rename(columns={
            "console-name": "Funko Category",
            "product-name": "Figure Name",
            "new-price": "Avg. eBay Sell Price",
            "sales-volume": "Sales Volume",
            "release-date": "Release Date"
        })
        
        # Convert Release Date to datetime and extract year
        df["Release Date"] = pd.to_datetime(df["Release Date"])
        df["Release Year"] = df["Release Date"].dt.year
        
        # Calculate Market Capitalization
        df["Market Capitalization"] = df["Sales Volume"] * df["Avg. eBay Sell Price"]
        
        return df, None
    except Exception as e:
        return None, str(e)

# Define the file path
file_path = "funko_data.csv"

# Check if the file exists and is not empty
if not os.path.exists(file_path):
    st.error(f"Error: {file_path} not found in the app directory.")
elif os.path.getsize(file_path) == 0:
    st.error(f"Error: {file_path} is empty.")
else:
    # Load and process the data
    df, error = load_data(file_path)
    if error:
        st.error(f"Error loading or processing data: {error}")
    else:
        # Proceed with the dashboard
        st.title("Funko Pop Figure Dashboard")
        
        # Display a preview of the loaded data (replace with your dashboard code)
        st.write("Data loaded successfully. Here is a preview:", df.head())
        
        # Add your dashboard components below, e.g., filters, charts, tables
        # Example:
        # st.subheader("Filter by Category")
        # category = st.selectbox("Select Funko Category", df["Funko Category"].unique())
        # filtered_df = df[df["Funko Category"] == category]
        # st.write(filtered_df)