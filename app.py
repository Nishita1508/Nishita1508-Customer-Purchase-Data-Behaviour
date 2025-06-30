import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_purchase_data(file):
    # Load and clean data
    df = pd.read_excel(file.name)  # Use .name for Gradio file object
    df = df.dropna(subset=["CustomerID"])
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # Summary metrics
    total_revenue = df["TotalPrice"].sum()
    top_products = df.groupby("Description")["Quantity"].sum().sort_values(ascending=False).head(5)
    top_customers = df.groupby("CustomerID")["TotalPrice"].sum().sort_values(ascending=False).head(5)

    # RFS Calculation
    ref_date = df["InvoiceDate"].max()
    rfs = df.groupby("CustomerID").agg({
        "InvoiceDate": lambda x: (ref_date - x.max()).days,
        "InvoiceNo": "nunique",
        "TotalPrice": "sum"
    }).reset_index()
    rfs.columns = ["CustomerID", "Recency", "Frequency", "Spend"]
    rfs["R"] = pd.cut(rfs["Recency"].rank(method="first"), bins=3, labels=[3,2,1]).astype(int)
    rfs["F"] = pd.cut(rfs["Frequency"].rank(method="first"), bins=3, labels=[1,2,3]).astype(int)

    # Heatmap
    plt.figure(figsize=(6, 4))
    heatmap_data = rfs.pivot_table(index="F", columns="R", values="Spend", aggfunc="mean")
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="YlGnBu")
    plt.title("Avg Spend by Recency & Frequency")
    plt.tight_layout()
    heatmap_fig = plt.gcf()
    plt.close()

    # Monthly revenue chart
    df["Month"] = df["InvoiceDate"].dt.to_period("M")
    monthly = df.groupby("Month")["TotalPrice"].sum()
    plt.figure(figsize=(6, 4))
    monthly.plot(kind="line", marker="o", title="Monthly Revenue Trend")
    plt.ylabel("Revenue")
    plt.tight_layout()
    trend_fig = plt.gcf()
    plt.close()


    # tOP 5 Country bar chart
    # country_revenue = customer_data.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False).head(5)
    country_revenue = df.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False).head(5)

    plt.bar(country_revenue.index,country_revenue.values, color='orange')
    plt.xlabel('Country')
    plt.ylabel('Revenue')
    plt.title('Top 5 Countries by Revenue')
    plt.xticks(rotation=45)
    plt.tight_layout()
    bar_fig = plt.gcf()
    plt.close()


   
    # Get top 10 products by revenue
    top10_products = df.groupby('Description')['TotalPrice'].sum().sort_values(ascending=False).head(10)

    # Plot
    plt.figure(figsize=(8, 8))
    plt.pie(top10_products.values,
            labels=top10_products.index,
            autopct='%1.1f%%',
            startangle=140,
            colors=plt.cm.Paired.colors)

    plt.title('Top 10 Products by Revenue')
    plt.axis('equal')  
    pie_fig = plt.gcf()

    plt.tight_layout()



    return (
        f"💰 Total Revenue: ₹{total_revenue:,.2f}",
        top_products.to_string(),
        top_customers.to_string(),
        heatmap_fig,
        trend_fig,
        bar_fig,
        pie_fig,

    )

demo = gr.Interface(
    fn=analyze_purchase_data,
    inputs=gr.File(file_types=[".xlsx", ".xls"], label="Upload Excel File"),
    outputs=[
        gr.Text(label="Total Revenue"),
        gr.Text(label="Top 5 Products"),
        gr.Text(label="Top 5 Customers"),
        gr.Plot(label="R-F Heatmap"),
        gr.Plot(label="Monthly Revenue Trend"),
        gr.Plot(label="Top 5 Country Bar Chart "),
        gr.Plot(label="Top 10 Products by Revenue "),


    ],
    title="Customer Purchase Behavior Dashboard",
    description="Upload your transaction Excel file to explore key business insights!"
)

demo.launch(share=True)

# demo.launch(server_port=7861)  # or any other unused port


