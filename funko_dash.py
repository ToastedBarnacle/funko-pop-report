import streamlit as st
import pandas as pd

# Function to load and preprocess the data, cached for performance
@st.cache_data
def load_data():
    """
    Load the Funko Pop CSV data, rename columns, and calculate derived metrics.
    Returns the processed DataFrame.
    """
    df = pd.read_csv("funko_data.csv")
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
    return df

# Load the data
df = load_data()

# Set the dashboard title
st.title("Funko Pop Figure Dashboard")

# Sidebar filters
st.sidebar.header("Filters")

# Filter for Release Year range
min_year = int(df["Release Year"].min())
max_year = int(df["Release Year"].max())
selected_years = st.sidebar.slider(
    "Select release year range",
    min_year,
    max_year,
    (min_year, max_year),
    help="Slide to select the range of release years to include."
)

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

# Filter the DataFrame based on selected ranges
filtered_df = df[
    (df["Release Year"] >= selected_years[0]) &
    (df["Release Year"] <= selected_years[1]) &
    (df["Avg. eBay Sell Price"] >= selected_price[0]) &
    (df["Avg. eBay Sell Price"] <= selected_price[1]) &
    (df["Sales Volume"] >= selected_volume[0]) &
    (df["Sales Volume"] <= selected_volume[1])
]

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

# Optional: Show the filtered data table if the user wants to see it
if st.checkbox("Show filtered data", help="Check to display the entire filtered dataset."):
    st.subheader("Filtered Data")
    st.dataframe(filtered_df, use_container_width=True)