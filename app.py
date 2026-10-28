import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Online Retail Dashboard",page_icon="📊",layout="wide")

st.title("📊 Online Retail Sales Dashboard")
st.markdown("### Business Performance & Customer Insights")

try:
    df = pd.read_csv("cleaned_data.csv", encoding="latin1")

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df = df.dropna(subset=["CustomerID"])
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

    st.success("Dataset loaded successfully!")

    # Sidebar filter
    st.sidebar.header("Interactive Filters")

    countries = sorted(df["Country"].dropna().unique())

    selected_countries = st.sidebar.multiselect(
        "Select Country",
        countries,
        default=countries)

    filtered_df = df[df["Country"].isin(selected_countries)]

    # Date Range Filter
    st.sidebar.subheader("Select Date Range")

    min_date = df["InvoiceDate"].min().date()
    max_date = df["InvoiceDate"].max().date()

    date_range = st.sidebar.date_input("Choose Date Range",value=(min_date, max_date),min_value=min_date,max_value=max_date)
    
    # Executive Summary
    st.header("Executive Summary")

    revenue = filtered_df["TotalPrice"].sum()
    customers = filtered_df["CustomerID"].nunique()
    transactions = filtered_df["InvoiceNo"].nunique()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Revenue", f"£{revenue:,.2f}")
    col2.metric("Total Customers", f"{customers:,}")
    col3.metric("Total Transactions", f"{transactions:,}")

    # Monthly Sales
    st.header("Monthly Sales Trend")

    if not filtered_df.empty:
        monthly_sales = (filtered_df.set_index("InvoiceDate")["TotalPrice"].resample("MS").sum().reset_index())

        fig = px.line(monthly_sales,x="InvoiceDate",y="TotalPrice",title="Monthly Revenue",markers=True)

        st.plotly_chart(fig, use_container_width=True)

        # Top Countries
        st.header("Sales by Country")

        country_sales = (filtered_df.groupby("Country")["TotalPrice"].sum().sort_values(ascending=False).head(10).reset_index())

        fig2 = px.bar(country_sales,x="Country",y="TotalPrice",title="Top 10 Countries by Revenue")

        st.plotly_chart(fig2, use_container_width=True)

        # Chart 3: Top 10 Products
        st.header("Top 10 Products")

        product_sales = (filtered_df.groupby("Description")["TotalPrice"].sum().nlargest(10).reset_index())

        fig3 = px.bar(product_sales,x="TotalPrice",y="Description",orientation="h",title="Top 10 Products by Revenue")

        st.plotly_chart(fig3, use_container_width=True)

        # Chart 4: Sales by Day of Week
        st.header("Sales by Day of Week")

        daily_sales = filtered_df.copy()
        daily_sales["Day"] = daily_sales["InvoiceDate"].dt.day_name()

        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday", "Sunday"]

        weekday_sales = (daily_sales.groupby("Day")["TotalPrice"].sum().reindex(day_order, fill_value=0).reset_index())

        fig4 = px.bar(weekday_sales,x="Day",y="TotalPrice",title="Revenue by Day of Week")

        st.plotly_chart(fig4, use_container_width=True)

        # Chart 5: Top 10 Customers
        st.header("Top 10 Customers")

        customer_sales = (filtered_df.groupby("CustomerID")["TotalPrice"].sum().nlargest(10).reset_index())

        customer_sales["CustomerID"] = (customer_sales["CustomerID"].astype(str))

        fig5 = px.bar(customer_sales,x="CustomerID",y="TotalPrice",title="Top 10 Customers by Revenue")

        st.plotly_chart(fig5, use_container_width=True)

       #  Sales by Day of Week
        df["DayOfWeek"] = df["InvoiceDate"].dt.day_name()

        day_sales = df.groupby("DayOfWeek")["TotalPrice"].sum().reindex(["Monday", "Tuesday", "Wednesday", "Thursday","Friday", "Saturday", "Sunday"])

        st.subheader("📅 Sales by Day of Week")
        fig = px.bar(x=day_sales.index,y=day_sales.values,labels={"x": "Day", "y": "Total Sales"})
        st.plotly_chart(fig, use_container_width=True)
        
        # Key Findings
        st.header("Key Findings")

        best_country = (filtered_df.groupby("Country")["TotalPrice"].sum().idxmax())

        st.write(f"- Highest-revenue country in the selection: **{best_country}**")
        st.write(f"- Total revenue in the selected countries: **£{revenue:,.2f}**")

        # Top-Selling Product
        top_product = (df.groupby("Description")["TotalPrice"].sum().idxmax())
        st.write(f"- Top-Selling Product: {top_product}")

        # Best Sales Day
        df["DayOfWeek"] = df["InvoiceDate"].dt.day_name()
        best_day = df.groupby("DayOfWeek")["TotalPrice"].sum().idxmax()
        st.write(f"- Best Sales Day: {best_day}")

       # Top Customer
        top_customer = (df.groupby("CustomerID")["TotalPrice"].sum().idxmax())
        st.write(f"- Top Customer ID: {top_customer}")

       # Recommendations
        st.header("Recommendations")

        st.write("- Focus on countries generating the most revenue.")
        st.write("- Encourage repeat purchases through customer loyalty offers.")
        st.write("- Monitor monthly sales trends to plan inventory.")

    else:
        st.warning("No data available for the selected countries.")

except FileNotFoundError:
    st.error("cleaned_data.csv not found.""Please keep the CSV file in the same folder as app.py.")

except Exception as e:
    st.error(f"Something went wrong: {e}")