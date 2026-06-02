import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Smart Expense Analyzer",
    page_icon="💰",
    layout="wide"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
    <style>

    .main {
        padding-top: 1rem;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        font-size: 16px;
        font-weight: bold;
        background-color: #00E5FF;
        color: black;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #00c8e0;
        color: black;
    }

    .stMetric {
        background-color: #1C1F26;
        padding: 15px;
        border-radius: 12px;
    }

    </style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================

st.title("💰 Smart Expense Analyzer")

st.caption(
    "Track expenses • Monitor budgets • Discover spending patterns"
)

st.divider()

# =========================
# FILE NAME
# =========================

FILE_NAME = "expenses.csv"

# =========================
# SAFE CSV CREATION
# =========================

if not os.path.exists(FILE_NAME) or os.path.getsize(FILE_NAME) == 0:

    df = pd.DataFrame(
        columns=["Date", "Title", "Category", "Amount"]
    )

    df.to_csv(FILE_NAME, index=False)

# =========================
# SAFE CSV LOADING
# =========================

try:
    df = pd.read_csv(FILE_NAME)

except:
    df = pd.DataFrame(
        columns=["Date", "Title", "Category", "Amount"]
    )



# =========================
# DATA CLEANING
# =========================

if not df.empty:

    df["Amount"] = pd.to_numeric(
        df["Amount"],
        errors="coerce"
    )

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

# =========================
# INITIALIZE SESSION STATE
# =========================

if "title" not in st.session_state:
    st.session_state.title = ""

if "category" not in st.session_state:
    st.session_state.category = "Food"

if "amount" not in st.session_state:
    st.session_state.amount = 0.0

# =========================
# SIDEBAR INPUTS
# =========================

st.sidebar.header("➕ Add New Expense")

title = st.sidebar.text_input(
    "Expense Title",
    key="title"
)

category = st.sidebar.selectbox(
    "Category",
    [
        "Food",
        "Transport",
        "Entertainment",
        "Shopping",
        "Bills",
        "Health",
        "Education",
        "Other"
    ],
    key="category"
)

amount = st.sidebar.number_input(
    "Amount",
    min_value=0.0,
    format="%.2f",
    key="amount"
)

date = st.sidebar.date_input(
    "Expense Date"
)
# =========================
# BUDGET SETTINGS
# =========================

st.sidebar.divider()

st.sidebar.header("💰 Budget Settings")

monthly_budget = st.sidebar.number_input(
    "Monthly Budget (₹)",
    min_value=0.0,
    value=10000.0,
    step=500.0
)

# =========================
# CSV UPLOAD
# =========================

st.sidebar.divider()

st.sidebar.header("📂 Upload Expenses CSV")

uploaded_file = st.sidebar.file_uploader(
    "Choose a CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    try:

        uploaded_df = pd.read_csv(uploaded_file)

        required_columns = [
            "Date",
            "Title",
            "Category",
            "Amount"
        ]

        if all(
            col in uploaded_df.columns
            for col in required_columns
        ):

            uploaded_df.to_csv(
                FILE_NAME,
                index=False
            )

            st.sidebar.success(
                "CSV uploaded successfully!"
            )

        else:

            st.sidebar.error(
                "CSV must contain Date, Title, Category and Amount columns."
            )

    except Exception as e:

        st.sidebar.error(
            f"Error: {e}"
        )
# =========================
# ADD EXPENSE BUTTON
# =========================

if st.sidebar.button("Add Expense"):

    if title.strip() == "":

        st.sidebar.error("Please enter expense title.")

    else:

        new_expense = {
            "Date": str(date),
            "Title": title,
            "Category": category,
            "Amount": amount
        }

        df = pd.concat(
            [df, pd.DataFrame([new_expense])],
            ignore_index=True
        )

        df.to_csv(FILE_NAME, index=False)

        st.toast("Expense Added Successfully! ✅")

        # Reset fields
        st.session_state.title = ""
        st.session_state.category = "Food"
        st.session_state.amount = 0.0

        st.rerun()
# =========================
# METRICS SECTION
# =========================

st.subheader("📌 Expense Overview")

total_expenses = len(df)

total_amount = df["Amount"].sum() if not df.empty else 0

# =========================
# CURRENT MONTH SPENDING
# =========================

current_month = pd.Timestamp.today().month
current_year = pd.Timestamp.today().year

if not df.empty:

    current_month_df = df[
        (df["Date"].dt.month == current_month)
        &
        (df["Date"].dt.year == current_year)
    ]

    monthly_spent = current_month_df["Amount"].sum()

else:

    monthly_spent = 0

remaining_budget = monthly_budget - monthly_spent

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Expenses",
    total_expenses
)

col2.metric(
    "Total Spending",
    f"₹{total_amount:.2f}"
)

col3.metric(
    "Budget",
    f"₹{monthly_budget:.0f}"
)

col4.metric(
    "Remaining",
    f"₹{remaining_budget:.0f}"
)

# =========================
# BUDGET PROGRESS
# =========================

if monthly_budget > 0:

    usage_percent = monthly_spent / monthly_budget

    st.write(
        f"📊 Budget Used: {usage_percent * 100:.1f}%"
    )

    st.progress(
        min(usage_percent, 1.0)
    )

else:

    usage_percent = 0

# =========================
# BUDGET ALERTS
# =========================

if monthly_spent > monthly_budget:

    st.error(
        "🚨 Monthly budget exceeded!"
    )

elif usage_percent >= 0.8:

    st.warning(
        "⚠️ You have used more than 80% of your monthly budget."
    )

# =========================
# SPENDING FORECAST
# =========================

days_passed = pd.Timestamp.today().day

avg_daily_spending = (
    monthly_spent / max(days_passed, 1)
)

projected_spending = (
    avg_daily_spending * 30
)

st.info(
    f"📈 Projected Month-End Spending: ₹{projected_spending:.0f}"
)

if projected_spending > monthly_budget:

    st.error(
        "🚨 At your current spending rate, you may exceed your monthly budget."
    )

else:

    st.success(
        "✅ You are currently on track to stay within budget."
    )

st.divider()
# =========================
# CHARTS SECTION
# =========================

st.subheader("📊 Spending Analysis")

if df.empty:

    st.info(
        "📂 Add or upload expenses to view spending charts."
    )

else:
    if not df.empty:

    # Group category data
        category_data = (
            df.groupby("Category")["Amount"]
            .sum()
            .reset_index()
    )

    chart_col1, chart_col2 = st.columns(2)

    # =========================
    # PIE CHART
    # =========================

    with chart_col1:

        pie_chart = px.pie(
            category_data,
            names="Category",
            values="Amount",
            title="Category-wise Spending",
            hole=0.4
        )

        pie_chart.update_layout(
            template="plotly_dark"
        )

        st.plotly_chart(
            pie_chart,
            use_container_width=True
        )

    # =========================
    # BAR CHART
    # =========================

    with chart_col2:

        bar_chart = px.bar(
            category_data,
            x="Category",
            y="Amount",
            title="Expense Comparison by Category"
        )

        bar_chart.update_layout(
            template="plotly_dark"
        )

        st.plotly_chart(
            bar_chart,
            use_container_width=True
        )

# =========================
# MONTHLY ANALYSIS
# =========================

st.subheader("📅 Monthly Spending Trend")

if df.empty:

    st.info(
        "📈 Monthly trends will appear after adding expenses."
    )

else:

    # Extract month
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    # Extract day name
    df["Day"] = df["Date"].dt.day_name()

    monthly_data = (
        df.groupby("Month")["Amount"]
        .sum()
        .reset_index()
    )

    line_chart = px.line(
        monthly_data,
        x="Month",
        y="Amount",
        markers=True,
        title="Monthly Expense Trend"
    )

    line_chart.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        line_chart,
        use_container_width=True
    )
# =========================
# SMART INSIGHTS
# =========================

st.subheader("🧠 Smart Financial Insights")

if df.empty:

    st.info(
        "🧠 Insights will be generated automatically once expenses are added."
    )

else:

    insight_col1, insight_col2 = st.columns(2)

    # -------------------------
    # Highest Spending Category
    # -------------------------

    category_totals = (
        df.groupby("Category")["Amount"]
        .sum()
    )

    highest_category = category_totals.idxmax()
    highest_amount = category_totals.max()

    with insight_col1:

        st.info(
            f"""
            💸 Highest Spending Category

            **{highest_category}**

            Total Spent: ₹{highest_amount:.2f}
            """
        )

    # -------------------------
    # Average Expense
    # -------------------------

    average_expense = df["Amount"].mean()

    with insight_col2:

        st.success(
            f"""
            📊 Average Expense

            ₹{average_expense:.2f}
            """
        )

    # -------------------------
    # Largest Transaction
    # -------------------------

    if not df["Amount"].isna().all():

        largest_transaction = df.loc[
        df["Amount"].idxmax()
    ]


    st.warning(
        f"""
        🔥 Largest Expense

        {largest_transaction['Title']}
        (₹{largest_transaction['Amount']:.2f})
        """
    )


    # -------------------------
    # Weekend Spending Analysis
    # -------------------------

    weekend_spending = df[
        df["Day"].isin(
            ["Saturday", "Sunday"]
        )
    ]["Amount"].sum()

    weekday_spending = df[
        ~df["Day"].isin(
            ["Saturday", "Sunday"]
        )
    ]["Amount"].sum()

    if weekend_spending > weekday_spending:

        st.error(
            "⚠️ Most of your spending occurs during weekends."
        )

    else:

        st.success(
            "✅ Your spending is fairly balanced throughout the week."
        )

    # -------------------------
    # Spending Increase Analysis
    # -------------------------

    monthly_spending = (
        df.groupby("Month")["Amount"]
        .sum()
    )

    if len(monthly_spending) >= 2:

        current_month = monthly_spending.iloc[-1]
        previous_month = monthly_spending.iloc[-2]

        if previous_month > 0:

            if current_month > previous_month:

                increase = (
                    (current_month - previous_month)
                    / previous_month
                ) * 100

                st.error(
                    f"""
                    📈 Spending increased by
                    {increase:.1f}% compared to the previous month.
                    """
                )

            else:

                decrease = (
                    (previous_month - current_month)
                    / previous_month
                ) * 100

                st.success(
                    f"""
                    📉 Spending decreased by
                    {decrease:.1f}% compared to the previous month.
                    """
                )
# =========================
# RECENT EXPENSES
# =========================

st.subheader("🧾 Recent Expenses")

if df.empty:

    st.info("No expenses added yet.")

else:

    recent_df = df.sort_values(
        by="Date",
        ascending=False
    ).head(5)

   

    recent_df_display = recent_df.reset_index(
    drop=True
    )

    recent_df_display.index = (
    recent_df_display.index + 1
    )

    st.dataframe(
    recent_df_display,
    use_container_width=True
    )

    st.caption(
        f"Showing {len(recent_df)} most recent expenses."
    )

# =========================
# FULL DATA TABLE
# =========================

st.subheader("📋 All Expense Records")

if not df.empty:

    
    df_display = df.reset_index(
    drop=True
)

    df_display.index = (
    df_display.index + 1
)

    st.dataframe(
        df_display,
        use_container_width=True
)
# =========================
# DOWNLOAD CSV
# =========================

csv_data = df.to_csv(
    index=False
)

st.download_button(
    label="📥 Download Expenses CSV",
    data=csv_data,
    file_name="expenses.csv",
    mime="text/csv"
)    