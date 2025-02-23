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
        
        # Convert Release Date to datetime, coercing errors to NaT
        df["Release Date"] = pd.to_datetime(df["Release Date"], errors='coerce')
        
        # Extract year from Release Date (will be NaN for invalid dates)
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
        # Warn about missing or invalid data
        if df["Avg. eBay Sell Price"].isna().any():
            st.warning("There are rows with missing Avg. eBay Sell Price. These will be excluded from price-based filters.")
        if df["Sales Volume"].isna().any():
            st.warning("There are rows with missing Sales Volume. These will be excluded from sales volume-based filters.")
        invalid_dates = df[df["Release Date"].isna()]
        if not invalid_dates.empty:
            st.warning(f"There are {len(invalid_dates)} rows with invalid release dates. These have been set to NaT.")
        
        # Proceed with the dashboard
        st.title("Funko Pop Figure Dashboard")
        
        # Sidebar filters
        st.sidebar.header("Filters")
        
        # Filter for Release Year range
        min_year = int(df["Release Year"].min(skipna=True))
        max_year = int(df["Release Year"].max(skipna=True))
        selected_years = st.sidebar.slider(
            "Select release year range",
            min_year,
            max_year,
            (min_year, max_year),
            help="Slide to select the range of release years to include."
        )
        
        # Checkbox to include figures with unknown release years
        include_unknown_years = st.sidebar.checkbox("Include figures with unknown release years", value=True)
        
        # Filter for Avg. eBay Sell Price range
        min_price = float(df["Avg. eBay Sell Price"].min())
        max_price = float(df["Avg. eBay Sell Price"].max())
        selected_price = st.sidebar.slider(
            "Select price range",
            min_price,
            max_price,
            (min_price, max_price),
            help="Slide to select the range of average eBay sell prices to include."
        )
        
        # Filter for Sales Volume range
        min_volume = int(df["Sales Volume"].min())
        max_volume = int(df["Sales Volume"].max())
        selected_volume = st.sidebar.slider(
            "Select sales volume range",
            min_volume,
            max_volume,
            (min_volume, max_volume),
            help="Slide to select the range of sales volumes to include."
        )
        
        # Apply filters
        if include_unknown_years:
            year_filter = (df["Release Year"].between(selected_years[0], selected_years[1])) | df["Release Year"].isna()
        else:
            year_filter = df["Release Year"].between(selected_years[0], selected_years[1])
        
        price_filter = df["Avg. eBay Sell Price"].between(selected_price[0], selected_price[1])
        volume_filter = df["Sales Volume"].between(selected_volume[0], selected_volume[1])
        
        filtered_df = df[year_filter & price_filter & volume_filter]
        
        # Check if filtered data is empty
        if filtered_df.empty:
            st.info("No data matches the selected filters. Try adjusting the filters or including unknown release years.")
        else:
            # Display metrics based on filtered data
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
            
            # Optional: Show the filtered data table with relevant columns
            if st.checkbox("Show filtered data", help="Check to display the entire filtered dataset."):
                st.subheader("Filtered Data")
                relevant_columns = ["Figure Name", "Funko Category", "Avg. eBay Sell Price", "Sales Volume", "Release Year", "Market Capitalization"]
                display_df = filtered_df[relevant_columns].copy()
                display_df["Release Year"] = display_df["Release Year"].fillna("Unknown")
                st.dataframe(display_df, use_container_width=True)