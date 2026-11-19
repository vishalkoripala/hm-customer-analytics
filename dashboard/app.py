import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="H&M Customer Analytics",
    page_icon="📊",
    layout="wide"
)

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

RFM_FILE = DATA_DIR / "customer_rfm.tsv.gz"
CLUSTER_FILE = DATA_DIR / "customer_clusters_final.csv.gz"

CLUSTER_NAMES = {
    737932: "High-Value Frequent Customers",
    1325946: "Inactive / Low-Value Customers",
    332505: "Recent Low-Frequency Customers",
    652544: "Regular High-Frequency Customers",
    781725: "Moderate-Activity Customers"
}

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data(show_spinner="Loading the complete customer dataset...")
def load_data():

    rfm = pd.read_csv(
        RFM_FILE,
        sep="\x01",
        header=None,
        names=[
            "customer_id",
            "recency",
            "frequency",
            "monetary"
        ],
        dtype={
            "customer_id": "string",
            "recency": "int32",
            "frequency": "int32",
            "monetary": "float32"
        }
    )

    clusters = pd.read_csv(
        CLUSTER_FILE,
        dtype={
            "customer_id": "string",
            "cluster_id": "int32"
        }
    )

    data = rfm.merge(
        clusters,
        on="customer_id",
        how="inner",
        validate="one_to_one"
    )

    return data


ANALYTICS_DIR = Path(__file__).parent / "data"


@st.cache_data(show_spinner="Loading Hive analytics...")
def load_sales_analytics():
    files = {
        "monthly": "monthly_trends.csv",
        "channels": "channel_distribution.csv",
        "categories": "product_categories.csv",
        "ages": "age_groups.csv",
        "articles": "top_articles.csv"
    }

    return {
        key: pd.read_csv(ANALYTICS_DIR / filename)
        for key, filename in files.items()
    }


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

st.title("H&M Customer Analytics Dashboard")
st.caption("Big Data Analytics | RFM-Based Customer Segmentation with Apache Mahout K-Means")

try:
    df = load_data()
except Exception as e:
    st.error(f"Unable to load dataset: {e}")
    st.stop()

if len(df) != 1_362_281:
    st.warning(
        f"Expected 1,362,281 customers, but loaded {len(df):,}. "
        "Please verify the source files."
    )

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Dashboard Navigation")

page = st.sidebar.selectbox(
    "Choose a Dashboard Module",
    [
        "Dataset Overview",
        "Customer Segmentation",
        "RFM Analysis",
        "Customer Explorer",
        "Business Insights",
        "Sales & Transaction Analytics"
    ]
)

st.sidebar.markdown("---")
st.sidebar.metric("Customers Loaded", f"{len(df):,}")
st.sidebar.metric("Number of Clusters", df["cluster_id"].nunique())

# --------------------------------------------------
# DATASET OVERVIEW
# --------------------------------------------------

if page == "Dataset Overview":

    st.header("Dataset Overview")

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Customers", f"{len(df):,}")
    c2.metric("Total Clusters", df["cluster_id"].nunique())
    c3.metric("Average Purchase Frequency (Transactions per Customer)", f"{df['frequency'].mean():.2f}")

    st.subheader("Customer RFM Data Preview")

    st.dataframe(
        df.head(20),
        width='stretch'
    )

    st.subheader("RFM Summary Statistics")

    st.dataframe(
        df[["recency", "frequency", "monetary"]].describe(),
        width='stretch'
    )

    st.subheader("Dataset Information")

    st.write({
        "Total Records": len(df),
        "Unique Customers": df["customer_id"].nunique(),
        "Missing Values": int(df.isnull().sum().sum()),
        "RFM Features": ["Recency", "Frequency", "Monetary"],
        "Clustering Algorithm": "Mahout K-Means",
        "Number of Clusters": 5
    })


# --------------------------------------------------
# CUSTOMER SEGMENTATION
# --------------------------------------------------

elif page == "Customer Segmentation":

    st.header("Customer Segmentation")

    cluster_counts = (
        df["cluster_id"]
        .value_counts()
        .rename_axis("cluster_id")
        .reset_index(name="customers")
    )

    cluster_counts["segment"] = cluster_counts["cluster_id"].map(
        CLUSTER_NAMES
    )

    cluster_counts["percentage"] = (
        cluster_counts["customers"] / len(df) * 100
    )

    c1, c2 = st.columns(2)

    with c1:
        fig = px.pie(
            cluster_counts,
            names="segment",
            values="customers",
            title="Customer Distribution by Segment",
            hole=0.4
        )
        st.plotly_chart(fig, width='stretch')

    with c2:
        fig = px.bar(
            cluster_counts,
            x="segment",
            y="customers",
            color="segment",
            title="Customer Count by Segment",
            text="customers"
        )
        fig.update_layout(showlegend=False)
        fig.update_xaxes(tickangle=-25)
        st.plotly_chart(fig, width='stretch')

    st.subheader("Cluster Distribution")

    st.dataframe(
        cluster_counts[
            ["cluster_id", "segment", "customers", "percentage"]
        ].style.format({
            "customers": "{:,.0f}",
            "percentage": "{:.2f}%"
        }),
        width='stretch'
    )


# --------------------------------------------------
# RFM ANALYSIS
# --------------------------------------------------

elif page == "RFM Analysis":

    st.header("RFM Analysis")

    st.write(
        "RFM represents Recency, Frequency and Monetary Value. "
        "These features were engineered from the historical transaction data."
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Average Recency", f"{df['recency'].mean():.2f} days")
    c2.metric("Average Frequency", f"{df['frequency'].mean():.2f}")
    c3.metric("Average Monetary Value", f"{df['monetary'].mean():.4f}")

    st.subheader("RFM Feature Distributions")

    feature = st.selectbox(
        "Select an RFM Feature",
        ["recency", "frequency", "monetary"]
    )

    fig = px.histogram(
        df,
        x=feature,
        nbins=60,
        title=f"Distribution of {feature.capitalize()}",
        marginal="box"
    )

    st.plotly_chart(fig, width='stretch')

    st.subheader("RFM Metrics by Segment")

    summary = df.groupby("cluster_id").agg(
        customers=("customer_id", "count"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean")
    ).reset_index()

    summary["segment"] = summary["cluster_id"].map(CLUSTER_NAMES)

    st.dataframe(
        summary,
        width='stretch'
    )

    scatter_data = df.sample(
        min(30000, len(df)),
        random_state=42
    ).copy()

    scatter_data["cluster_label"] = scatter_data["cluster_id"].astype(str)

    fig = px.scatter(
        scatter_data,
        x="recency",
        y="frequency",
        color="cluster_label",
        title="Recency vs Frequency by Cluster",
        opacity=0.5
    )

    st.plotly_chart(fig, width='stretch')


# --------------------------------------------------
# CUSTOMER EXPLORER
# --------------------------------------------------

elif page == "Customer Explorer":

    st.header("Customer Explorer")

    customer_id = st.text_input(
        "Enter Customer ID",
        placeholder="Paste the complete customer ID"
    ).strip()

    if customer_id:

        result = df.loc[df["customer_id"] == customer_id]

        if result.empty:
            st.error("Customer ID not found.")
        else:

            customer = result.iloc[0]

            st.success("Customer found!")

            c1, c2, c3 = st.columns(3)

            c1.metric("Recency", f"{customer['recency']} days")
            c2.metric("Frequency", f"{customer['frequency']}")
            c3.metric("Monetary", f"{customer['monetary']:.5f}")

            cluster_id = int(customer["cluster_id"])

            st.subheader("Customer Segment")

            st.info(
                f"Cluster ID: {cluster_id}\n\n"
                f"Segment: {CLUSTER_NAMES.get(cluster_id, 'Unknown')}"
            )

            st.write("Customer Details")

            st.dataframe(
                result,
                width='stretch'
            )

    else:
        st.info("Enter a customer ID to explore its RFM profile and segment.")


# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------

elif page == "Business Insights":

    st.header("Business Insights")

    summary = df.groupby("cluster_id").agg(
        customers=("customer_id", "count"),
        avg_recency=("recency", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean")
    ).reset_index()

    summary["segment"] = summary["cluster_id"].map(CLUSTER_NAMES)

    for _, row in summary.iterrows():

        with st.expander(
            f"{row['segment']} — {int(row['customers']):,} Customers"
        ):

            st.write(f"**Cluster ID:** {int(row['cluster_id'])}")
            st.write(f"**Average Recency:** {row['avg_recency']:.2f} days")
            st.write(f"**Average Frequency:** {row['avg_frequency']:.2f}")
            st.write(f"**Average Monetary:** {row['avg_monetary']:.5f}")

            if row["cluster_id"] == 737932:
                st.write(
                    "Potential strategy: loyalty rewards, exclusive offers "
                    "and premium customer retention."
                )

            elif row["cluster_id"] == 1325946:
                st.write(
                    "Potential strategy: reactivation campaigns and "
                    "personalized promotional offers."
                )

            elif row["cluster_id"] == 332505:
                st.write(
                    "Potential strategy: product discovery campaigns and "
                    "recommendations to encourage repeat purchases."
                )

            elif row["cluster_id"] == 652544:
                st.write(
                    "Potential strategy: cross-selling, personalized "
                    "recommendations and loyalty programs."
                )

            elif row["cluster_id"] == 781725:
                st.write(
                    "Potential strategy: targeted promotions and "
                    "engagement campaigns."
                )


# --------------------------------------------------
# SALES ANALYTICS
# --------------------------------------------------

elif page == "Sales & Transaction Analytics":

    st.header("Sales & Transaction Analytics")
    st.caption(
        "Transaction-level summaries generated using Apache Hive "
        "from the H&M dataset."
    )

    try:
        sales_data = load_sales_analytics()
        monthly = sales_data["monthly"].copy()
        channels = sales_data["channels"].copy()
        categories = sales_data["categories"].copy()
        ages = sales_data["ages"].copy()
        articles = sales_data["articles"].copy()

        monthly["month"] = pd.to_datetime(monthly["month"])
        monthly = monthly.sort_values("month")

        total_transactions = int(monthly["transactions"].sum())
        total_sales = monthly["sales_value"].sum()

        m1, m2, m3 = st.columns(3)
        m1.metric("Dated Transactions", f"{total_transactions:,}")
        m2.metric("Total Sales Value", f"{total_sales:,.2f}")
        m3.metric("Months Analyzed", f"{len(monthly):,}")

        st.caption(
            "Sales values use the normalized price values supplied in the "
            "original dataset; they are not INR."
        )

        # Monthly trends
        st.subheader("Monthly Transaction Trends")

        c1, c2 = st.columns(2)

        with c1:
            fig = px.line(
                monthly,
                x="month",
                y="transactions",
                markers=True,
                title="Monthly Transaction Volume"
            )
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Number of Transactions"
            )
            st.plotly_chart(fig, width="stretch")

        with c2:
            fig = px.line(
                monthly,
                x="month",
                y="sales_value",
                markers=True,
                title="Monthly Sales Value"
            )
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Normalized Sales Value"
            )
            st.plotly_chart(fig, width="stretch")

        st.dataframe(monthly, width="stretch")

        # Sales channel distribution
        st.subheader("Sales Channel Distribution")

        channels["channel"] = channels["sales_channel_id"].map(
            {1: "Channel 1", 2: "Channel 2"}
        ).fillna(channels["sales_channel_id"].astype(str))

        c1, c2 = st.columns(2)

        with c1:
            fig = px.pie(
                channels,
                names="channel",
                values="transactions",
                hole=0.4,
                title="Transactions by Sales Channel"
            )
            st.plotly_chart(fig, width="stretch")

        with c2:
            fig = px.bar(
                channels,
                x="channel",
                y="transactions",
                text="transactions",
                title="Transaction Count by Channel"
            )
            fig.update_layout(
                xaxis_title="Sales Channel",
                yaxis_title="Transactions"
            )
            st.plotly_chart(fig, width="stretch")

        st.dataframe(channels, width="stretch")

        # Product categories
        st.subheader("Product Category Analysis")

        top_categories = categories.nlargest(10, "transactions")

        fig = px.bar(
            top_categories.sort_values("transactions"),
            x="transactions",
            y="product_type_name",
            orientation="h",
            text="transactions",
            title="Top 10 Product Types by Transactions"
        )
        fig.update_layout(
            xaxis_title="Transactions",
            yaxis_title="Product Type"
        )
        st.plotly_chart(fig, width="stretch")
        st.dataframe(categories, width="stretch")

        # Age group analysis
        st.subheader("Age-Group Purchasing Patterns")

        age_order = [
            "Below 20", "20-29", "30-39", "40-49",
            "50-59", "60 and above", "Unknown"
        ]
        ages["age_group"] = pd.Categorical(
            ages["age_group"],
            categories=age_order,
            ordered=True
        )
        ages = ages.sort_values("age_group")

        c1, c2 = st.columns(2)

        with c1:
            fig = px.bar(
                ages,
                x="age_group",
                y="transactions",
                text="transactions",
                title="Transactions by Age Group"
            )
            fig.update_layout(
                xaxis_title="Age Group",
                yaxis_title="Transactions"
            )
            st.plotly_chart(fig, width="stretch")

        with c2:
            fig = px.bar(
                ages,
                x="age_group",
                y="sales_value",
                text="sales_value",
                title="Sales Value by Age Group"
            )
            fig.update_layout(
                xaxis_title="Age Group",
                yaxis_title="Normalized Sales Value"
            )
            st.plotly_chart(fig, width="stretch")

        st.dataframe(ages, width="stretch")

        # Top-selling articles
        st.subheader("Top 10 Selling Articles")

        articles["article_label"] = (
            articles["product_name"].astype(str)
            + " ("
            + articles["article_id"].astype(str)
            + ")"
        )

        fig = px.bar(
            articles.sort_values("transactions"),
            x="transactions",
            y="article_label",
            orientation="h",
            text="transactions",
            title="Top 10 Articles by Purchase Count"
        )
        fig.update_layout(
            xaxis_title="Transactions",
            yaxis_title="Article"
        )
        st.plotly_chart(fig, width="stretch")

        st.dataframe(
            articles.drop(columns=["article_label"]),
            width="stretch"
        )

    except Exception as e:
        st.error(f"Unable to load Hive analytics exports: {e}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.sidebar.markdown("---")
st.sidebar.caption("H&M Big Data Analytics Project")
st.sidebar.caption("Hadoop | Hive | Apache Mahout | Streamlit")
