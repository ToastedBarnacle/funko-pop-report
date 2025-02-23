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
        
        # Verify renaming worked
        if "Avg. eBay Sell Price" not in df.columns:
            st.error("Column 'new-price' not found or renamed incorrectly. Available columns: " + str(df.columns.tolist()))
            return None, "Column renaming failed"
        
        # Convert Release Date to datetime with "YYYY-MM-DD" format
        df["Release Date"] = pd.to_datetime(df["Release Date"], format='%Y-%m-%d', errors='coerce')
        df["Release Year"] = df["Release Date"].dt.year
        
        # Convert Avg. eBay Sell Price to numeric, handling potential formatting issues
        df["Avg. eBay Sell Price"] = pd.to_numeric(df["Avg. eBay Sell Price"].replace('[\$,]', '', regex=True), errors='coerce')
        
        # Convert Sales Volume to numeric
        df["Sales Volume"] = pd.to_numeric(df["Sales Volume"], errors='coerce')
        
        # Calculate Market Capitalization
        df["Market Capitalization"] = df["Sales Volume"] * df["Avg. eBay Sell Price"]
        
        # Filter out items with Sales Volume <= 1
        df = df[df["Sales Volume"] > 1]
        
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
    elif df is None:
        st.error("Data loading returned None. Check earlier errors.")
    else:
        # Check for missing or invalid data
        if df["Avg. eBay Sell Price"].isna().all():
            st.error("All Avg. eBay Sell Price values are missing or non-numeric after processing.")
        elif df["Avg. eBay Sell Price"].isna().any():
            st.warning(f"Some rows ({df['Avg. eBay Sell Price'].isna().sum()}) have missing or non-numeric Avg. eBay Sell Price values.")
        
        if df["Sales Volume"].isna().all():
            st.error("All Sales Volume values are missing or non-numeric after filtering.")
        elif df["Sales Volume"].isna().any():
            st.warning(f"Some rows ({df['Sales Volume'].isna().sum()}) have missing or non-numeric Sales Volume values.")
        
        if df["Release Date"].isna().any():
            st.warning(f"Some rows ({df['Release Date'].isna().sum()}) have invalid or missing Release Dates, set to NaT.")
        
        # Proceed with the dashboard if there’s usable data
        st.title("Funko Pop Figure Dashboard")
        
        # Sidebar filters
        st.sidebar.header("Filters")
        
        # Filter for Release Year range
        valid_years = df["Release Year"].dropna()
        if valid_years.empty:
            st.error("No valid release years found. Cannot set year filter.")
        else:
            min_year = int(valid_years.min())
            max_year = int(valid_years.max())
            selected_years = st.sidebar.slider(
                "Select release year range",
                min_year,
                max_year,
                (min_year, max_year),
                help="Slide to select the range of release years."
            )
        
        # Filter for Avg. eBay Sell Price range
        valid_prices = df["Avg. eBay Sell Price"].dropna()
        if valid_prices.empty:
            st.error("No valid Avg. eBay Sell Price values found after processing.")
        else:
            min_price = float(valid_prices.min())
            max_price = float(valid_prices.max())
            selected_price = st.sidebar.slider(
                "Select price range",
                min_price,
                max_price,
                (min_price, max_price),
                help="Slide to select the range of average eBay sell prices."
            )
        
        # Filter for Sales Volume range
        valid_volumes = df["Sales Volume"].dropna()
        if valid_volumes.empty:
            st.error("No valid Sales Volume values found after filtering.")
        else:
            min_volume = int(valid_volumes.min())
            max_volume = int(valid_volumes.max())
            selected_volume = st.sidebar.slider(
                "Select sales volume range",
                min_volume,
                max_volume,
                (min_volume, max_volume),
                help="Slide to select the range of sales volumes (minimum is 2 due to initial filter)."
            )
        
        # Apply filters
        filtered_df = df[
            df["Release Year"].between(selected_years[0], selected_years[1], inclusive='both') &
            df["Avg. eBay Sell Price"].between(selected_price[0], selected_price[1], inclusive='both') &
            df["Sales Volume"].between(selected_volume[0], selected_volume[1], inclusive='both')
        ]
        
        # Check if filtered data is empty
        if filtered_df.empty:
            st.info("No data matches the selected filters. Try adjusting the ranges.")
        else:
            # Display metrics and visualizations
            st.subheader("Number of Figures by Funko Category")
            category_counts = filtered_df["Funko Category"].value_counts()
            st.bar_chart(category_counts, use_container_width=True)
            
            st.subheader("Top 10 Figures by Market Capitalization")
            top_market_cap = filtered_df.sort_values(by="Market Capitalization", ascending=False).head(10)
            st.dataframe(
                top_market_cap[["Figure Name", "Funko Category", "Market Capitalization"]],
                use_container_width=True
            )
            
            st.subheader("Top 10 Figures by Sales Volume")
            top_sales_volume = filtered_df.sort_values(by="Sales Volume", ascending=False).head(10)
            st.dataframe(
                top_sales_volume[["Figure Name", "Funko Category", "Sales Volume"]],
                use_container_width=True
            )
            
            st.subheader("Top 10 Figures by Avg. eBay Sell Price")
            top_price = filtered_df.sort_values(by="Avg. eBay Sell Price", ascending=False).head(10)
            st.dataframe(
                top_price[["Figure Name", "Funko Category", "Avg. eBay Sell Price"]],
                use_container_width=True
            )
            
            # Optional: Show the filtered data table
            if st.checkbox("Show filtered data", help="Check to display the filtered dataset."):
                st.subheader("Filtered Data")
                relevant_columns = ["Figure Name", "Funko Category", "Avg. eBay Sell Price", 
                                   "Sales Volume", "Release Year", "Market Capitalization"]
                st.dataframe(filtered_df[relevant_columns], use_container_width=True)