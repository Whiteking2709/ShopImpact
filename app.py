import streamlit as st
import pandas as pd

from datetime import date

from database import initialize_database, get_categories

from calculations import (
    add_purchase,
    get_purchase_history,
    submit_category_request
)

from admin import (
    get_pending_requests,
    add_category,
    edit_category,
    approve_request,
    reject_request,
    get_all_categories
)

# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="ShopImpact",
    page_icon="🌱",
    layout="wide"
)

initialize_database()

# ==================================================
# SESSION STATE
# ==================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "last_purchase" not in st.session_state:
    st.session_state.last_purchase = None

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

if "tip_index" not in st.session_state:
    st.session_state.tip_index = 0

# ==================================================
# HIGH-CONTRAST DESIGN
# ==================================================

st.markdown("""
<style>

/* Main page */
.stApp {
    background-color: #F5F7F2;
    color: #17251C;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

/* Headings */
h1, h2, h3, h4 {
    color: #173D2A !important;
    font-weight: 700 !important;
}

p, li, label, span, div {
    color: inherit;
}

/* Normal text */
.stMarkdown, .stMarkdown p,
.stMarkdown li {
    color: #24352B !important;
}

/* Widget labels */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
.stSelectbox label,
.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stCheckbox label {
    color: #17251C !important;
    font-weight: 650 !important;
}

/* Text inputs and number inputs */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #17251C !important;
    border: 1.5px solid #718477 !important;
    border-radius: 8px !important;
    -webkit-text-fill-color: #17251C !important;
}

/* Dropdowns */
[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #17251C !important;
    border-color: #718477 !important;
}

[data-baseweb="select"] * {
    color: #17251C !important;
}

/* Dropdown menu */
[role="listbox"],
[role="option"] {
    background-color: #FFFFFF !important;
    color: #17251C !important;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    background-color: #1E5939 !important;
    color: #FFFFFF !important;
    border: 1px solid #1E5939 !important;
    border-radius: 8px !important;
    font-weight: 650 !important;
    min-height: 42px;
}

.stButton > button *,
.stFormSubmitButton > button * {
    color: #FFFFFF !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #16442B !important;
    border-color: #16442B !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #E6EEE5 !important;
}

[data-testid="stSidebar"] * {
    color: #173D2A !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    border: 1px solid #C8D5C9 !important;
    border-radius: 12px;
    padding: 18px;
}

[data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"] * {
    color: #173D2A !important;
}

/* Tables */
[data-testid="stDataFrame"] {
    background-color: #FFFFFF !important;
}

/* Alerts */
[data-testid="stAlert"] p {
    color: #17251C !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #173D2A !important;
    font-weight: 650 !important;
}

/* Dividers */
hr {
    border-color: #CCD7CC !important;
}

/* Tree illustration */
.tree-card {
    background: linear-gradient(145deg, #E4F0E2, #FFFFFF);
    border: 1px solid #B8CEB9;
    border-radius: 18px;
    padding: 28px;
    text-align: center;
}

.tree-emoji {
    font-size: 100px;
    line-height: 1.5;
    display: inline-block;
    animation: treeGrow 1.2s ease-out;
}

@keyframes treeGrow {
    0% {
        transform: scale(0.2);
        opacity: 0.2;
    }
    75% {
        transform: scale(1.1);
        opacity: 1;
    }
    100% {
        transform: scale(1);
    }
}

.tree-stage {
    color: #1E5939;
    font-size: 23px;
    font-weight: 700;
}

.tree-description {
    color: #344A38;
    font-size: 15px;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# HELPER FUNCTIONS
# ==================================================

def load_purchases():

    records = get_purchase_history()

    if not records:
        return pd.DataFrame()

    return pd.DataFrame([dict(row) for row in records])

def money(value):
    return f"₹{value:,.2f}"

def navigate(page):
    st.session_state.page = page
    st.rerun()

def get_tree_stage(purchase_count):

    if purchase_count == 0:
        return "🌱", "Seed", "Your tree is waiting for your first recorded purchase."

    elif purchase_count < 3:
        return "🌿", "Sprout", "Your tree has started growing."

    elif purchase_count < 6:
        return "🪴", "Young Plant", "Your tree is growing with your activity."

    elif purchase_count < 10:
        return "🌳", "Growing Tree", "Your tree is becoming stronger."

    else:
        return "🌲", "Full-Grown Tree", "You have reached the highest tree stage!"

# ==================================================
# LOAD DATA
# ==================================================

purchases_df = load_purchases()
categories = get_categories()

# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.title("🌱 ShopImpact")

    st.write("Shop consciously. Make better choices.")

    st.divider()

    navigation = [
        "Home",
        "Add Purchase",
        "History",
        "Greener Choices",
        "Eco Badges & Tips",
        "Analytics",
        "Administrator"
    ]

    selected_page = st.radio(
        "Navigation",
        navigation,
        index=navigation.index(st.session_state.page)
        if st.session_state.page in navigation else 0
    )

    if selected_page != st.session_state.page:
        st.session_state.page = selected_page
        st.rerun()

    st.divider()

    st.caption("IBCP Python Programming Project")

# ==================================================
# HOME DASHBOARD
# ==================================================

if st.session_state.page == "Home":

    st.title("Welcome to ShopImpact 🌱")

    st.write(
        "Track your everyday purchases and understand "
        "their estimated environmental impact."
    )

    st.divider()

    if not purchases_df.empty:

        purchases_df["purchase_date"] = pd.to_datetime(
            purchases_df["purchase_date"]
        )

        current_month = date.today().strftime("%Y-%m")

        monthly_df = purchases_df[
            purchases_df["purchase_date"].dt.strftime("%Y-%m")
            == current_month
        ]

        monthly_spending = monthly_df["price"].sum()
        monthly_impact = monthly_df["estimated_impact"].sum()

    else:
        monthly_spending = 0
        monthly_impact = 0

    st.subheader("Your Monthly Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Monthly Spending", money(monthly_spending))
    col2.metric("Estimated Impact", f"{monthly_impact:.2f} points")
    col3.metric("Total Purchases", len(purchases_df))

    st.divider()

    # TREE GROWTH

    st.subheader("Your Growing Tree 🌳")

    tree_emoji, tree_stage, tree_description = get_tree_stage(
        len(purchases_df)
    )

    st.markdown(
        f"""
        <div class="tree-card">
            <div class="tree-emoji">{tree_emoji}</div>
            <div class="tree-stage">{tree_stage}</div>
            <p class="tree-description">{tree_description}</p>
            <p class="tree-description">
                Purchases recorded: {len(purchases_df)}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Your tree grows as you record purchases. "
        "It represents participation in ShopImpact, "
        "not a measurement of environmental improvement."
    )

    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:

        st.subheader("Recent Purchases")

        if purchases_df.empty:
            st.info("You have not added any purchases yet.")

        else:

            recent = purchases_df.sort_values(
                "purchase_date",
                ascending=False
            ).head(5)

            st.dataframe(
                recent[
                    [
                        "product_name",
                        "category_name",
                        "price",
                        "purchase_date",
                        "estimated_impact"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

    with col2:

        st.subheader("Your Progress")

        count = len(purchases_df)

        if count >= 1:
            st.success("🌱 First Purchase Badge")
        else:
            st.info("Add your first purchase to earn a badge.")

        if count >= 5:
            st.success("🌿 Conscious Shopper Badge")

        if count >= 10:
            st.success("🌳 Responsible Shopper Badge")

    st.divider()

    if st.button("➕ Add Purchase", use_container_width=True):
        navigate("Add Purchase")

# ==================================================
# ADD PURCHASE
# ==================================================

elif st.session_state.page == "Add Purchase":

    st.title("Add a Purchase")

    st.write(
        "Enter the details of your purchase. "
        "ShopImpact will calculate its estimated impact."
    )

    st.divider()

    category_options = {
        row["category_name"]: row["category_id"]
        for row in categories
    }

    if not category_options:

        st.warning("No active categories are available.")

    else:

        with st.form("purchase_form"):

            product_name = st.text_input(
                "Product Name",
                placeholder="Example: Cotton T-shirt"
            )

            category_name = st.selectbox(
                "Product Category",
                list(category_options.keys())
            )

            price = st.number_input(
                "Amount Paid (₹)",
                min_value=0.0,
                value=0.0,
                step=50.0,
                help="Enter the actual price you paid. For example, enter 850 for a purchase costing ₹850."
            )

            st.caption(
                "Enter the amount in Indian Rupees. "
                "Example: ₹850 should be entered as 850."
            )

            brand = st.text_input(
                "Brand (Optional)",
                placeholder="Example: H&M"
            )

            purchase_date = st.date_input(
                "Purchase Date",
                value=date.today(),
                max_value=date.today()
            )

            submitted = st.form_submit_button(
                "Add Purchase",
                use_container_width=True
            )

            if submitted:

                if not product_name.strip():
                    st.error("Please enter a product name.")

                elif price <= 0:
                    st.error("Please enter a purchase amount greater than zero.")

                else:

                    try:

                        purchase_id, impact = add_purchase(
                            category_options[category_name],
                            product_name.strip(),
                            price,
                            brand.strip(),
                            purchase_date.isoformat()
                        )

                        st.session_state.last_purchase = {
                            "purchase_id": purchase_id,
                            "product_name": product_name,
                            "category_name": category_name,
                            "price": price,
                            "brand": brand,
                            "purchase_date": purchase_date,
                            "impact": impact
                        }

                        navigate("Purchase Result")

                    except Exception as error:
                        st.error(f"Unable to add purchase: {error}")

    st.divider()

    st.subheader("Missing Product Category?")

    st.write(
        "Submit a request if your product category is not available."
    )

    with st.form("missing_category_form"):

        missing_product = st.text_input(
            "Product Name",
            key="missing_product"
        )

        missing_category = st.text_input(
            "Category Name",
            key="missing_category"
        )

        knows_impact = st.checkbox(
            "I know the estimated impact value"
        )

        suggested_value = None

        if knows_impact:

            suggested_value = st.number_input(
                "Impact Value (0 to 1)",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.01
            )

        request_submitted = st.form_submit_button(
            "Submit Category Request"
        )

        if request_submitted:

            if not missing_product.strip() or not missing_category.strip():
                st.error("Please enter both product and category names.")

            else:

                try:

                    submit_category_request(
                        missing_product.strip(),
                        missing_category.strip(),
                        suggested_value
                    )

                    st.success(
                        "Your category request has been submitted."
                    )

                except Exception as error:
                    st.error(str(error))

# ==================================================
# PURCHASE RESULT
# ==================================================

elif st.session_state.page == "Purchase Result":

    st.title("Purchase Added Successfully! 🌱")

    purchase = st.session_state.last_purchase

    if purchase is None:

        st.info("No recent purchase is available.")

        if st.button("Back to Dashboard"):
            navigate("Home")

    else:

        st.success("Your purchase has been saved.")

        st.subheader("Purchase Details")

        col1, col2 = st.columns(2)

        with col1:

            st.write(f"**Product:** {purchase['product_name']}")
            st.write(f"**Category:** {purchase['category_name']}")
            st.write(f"**Brand:** {purchase['brand'] or 'Not specified'}")

        with col2:

            st.write(f"**Amount Paid:** {money(purchase['price'])}")
            st.write(
                f"**Date:** {purchase['purchase_date'].strftime('%d %B %Y')}"
            )

        st.divider()

        st.subheader("Estimated Environmental Impact")

        st.metric(
            "Impact Points",
            f"{purchase['impact']:.2f}"
        )

        st.caption(
            "This is a simplified estimated score, "
            "not a measured carbon footprint in kilograms."
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button("Back to Dashboard", use_container_width=True):
                navigate("Home")

        with col2:

            if st.button("View Purchase History", use_container_width=True):
                navigate("History")

# ==================================================
# PURCHASE HISTORY
# ==================================================

elif st.session_state.page == "History":

    st.title("Purchase History")

    st.write("View your recorded purchases.")

    st.divider()

    if purchases_df.empty:

        st.info("No purchases have been recorded yet.")

    else:

        history = purchases_df.sort_values(
            "purchase_date",
            ascending=False
        )

        st.dataframe(
            history,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        col1, col2 = st.columns(2)

        col1.metric(
            "Total Spending",
            money(purchases_df["price"].sum())
        )

        col2.metric(
            "Total Estimated Impact",
            f"{purchases_df['estimated_impact'].sum():.2f} points"
        )

# ==================================================
# GREENER CHOICES
# ==================================================

elif st.session_state.page == "Greener Choices":

    st.title("Greener Choices 🌿")

    st.write(
        "Explore alternatives that may help reduce "
        "the environmental impact of your purchases."
    )

    st.divider()

    category_names = [
        row["category_name"]
        for row in categories
    ]

    if category_names:

        selected_category = st.selectbox(
            "Choose a Product Category",
            category_names
        )

        selected_data = next(
            row for row in categories
            if row["category_name"] == selected_category
        )

        st.subheader("Recommended Alternative")

        st.success(
            selected_data["greener_alternative"]
            or "Consider reusable or second-hand alternatives."
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Reuse")

        st.write(
            "Consider second-hand products or reuse items "
            "you already own."
        )

    with col2:

        st.subheader("Buy Responsibly")

        st.write(
            "Look for durable products and avoid unnecessary purchases."
        )

# ==================================================
# ECO BADGES AND TIPS
# ==================================================

elif st.session_state.page == "Eco Badges & Tips":

    st.title("Eco Badges & Shopping Tips")

    st.write(
        "Track your progress and discover simple shopping tips."
    )

    st.divider()

    purchase_count = len(purchases_df)

    st.subheader("Your Eco Badges")

    col1, col2, col3 = st.columns(3)

    with col1:

        if purchase_count >= 1:
            st.success("🌱 First Purchase\n\nUnlocked")
        else:
            st.info("🌱 First Purchase\n\nLocked")

    with col2:

        if purchase_count >= 5:
            st.success("🌿 Conscious Shopper\n\nUnlocked")
        else:
            st.info("🌿 Conscious Shopper\n\nLocked")

    with col3:

        if purchase_count >= 10:
            st.success("🌳 Responsible Shopper\n\nUnlocked")
        else:
            st.info("🌳 Responsible Shopper\n\nLocked")

    st.divider()

    tips = [
        "Buy products that are durable and last longer.",
        "Consider repairing products before replacing them.",
        "Choose reusable bags instead of single-use bags.",
        "Consider buying second-hand clothing.",
        "Avoid buying products you do not really need.",
        "Look for products with less unnecessary packaging."
    ]

    st.subheader("Shopping Tip of the Day")

    st.info(tips[st.session_state.tip_index])

    if st.button("Show Another Tip"):

        st.session_state.tip_index = (
            st.session_state.tip_index + 1
        ) % len(tips)

        st.rerun()

# ==================================================
# ANALYTICS - PANDAS
# ==================================================

elif st.session_state.page == "Analytics":

    st.title("Shopping Analytics")

    st.write(
        "Understand your spending and estimated impact "
        "through your purchase data."
    )

    st.divider()

    if purchases_df.empty:

        st.info("Add purchases to start generating analytics.")

    else:

        purchases_df["purchase_date"] = pd.to_datetime(
            purchases_df["purchase_date"]
        )

        purchases_df["month"] = (
            purchases_df["purchase_date"]
            .dt.to_period("M")
            .astype(str)
        )

        st.subheader("Monthly Spending")

        monthly_spending = (
            purchases_df.groupby("month")["price"]
            .sum()
            .reset_index()
        )

        monthly_spending.columns = ["Month", "Total Spending"]

        st.dataframe(
            monthly_spending,
            use_container_width=True,
            hide_index=True
        )

        st.line_chart(
            monthly_spending.set_index("Month")
        )

        st.subheader("Month-on-Month Impact")

        monthly_impact = (
            purchases_df.groupby("month")["estimated_impact"]
            .sum()
            .reset_index()
        )

        monthly_impact.columns = ["Month", "Estimated Impact"]

        monthly_impact["Previous Month"] = (
            monthly_impact["Estimated Impact"].shift(1)
        )

        monthly_impact["Change (%)"] = (
            (
                monthly_impact["Estimated Impact"]
                - monthly_impact["Previous Month"]
            )
            / monthly_impact["Previous Month"].replace(0, pd.NA)
        ) * 100

        st.dataframe(
            monthly_impact.round(2),
            use_container_width=True,
            hide_index=True
        )

        if len(monthly_impact) >= 2:

            previous = monthly_impact.iloc[-2]["Estimated Impact"]
            latest = monthly_impact.iloc[-1]["Estimated Impact"]

            if previous > 0:

                change = ((latest - previous) / previous) * 100

                if change < 0:
                    st.success(
                        f"Estimated impact decreased by "
                        f"{abs(change):.2f}% compared with the previous month."
                    )

                elif change > 0:
                    st.warning(
                        f"Estimated impact increased by "
                        f"{change:.2f}% compared with the previous month."
                    )

                else:
                    st.info("Estimated impact remained unchanged.")

        st.line_chart(
            monthly_impact.set_index("Month")[["Estimated Impact"]]
        )

        st.subheader("Product-wise Analysis")

        product_analysis = (
            purchases_df.groupby("product_name")
            .agg(
                Total_Spending=("price", "sum"),
                Total_Impact=("estimated_impact", "sum"),
                Number_of_Purchases=("purchase_id", "count")
            )
            .reset_index()
            .sort_values("Total_Impact", ascending=False)
        )

        st.dataframe(
            product_analysis,
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(
            product_analysis.set_index("product_name")[["Total_Impact"]]
        )

        st.subheader("Category-wise Analysis")

        category_analysis = (
            purchases_df.groupby("category_name")
            .agg(
                Total_Spending=("price", "sum"),
                Total_Impact=("estimated_impact", "sum"),
                Number_of_Purchases=("purchase_id", "count")
            )
            .reset_index()
            .sort_values("Total_Impact", ascending=False)
        )

        st.dataframe(
            category_analysis,
            use_container_width=True,
            hide_index=True
        )

        st.bar_chart(
            category_analysis.set_index("category_name")[["Total_Impact"]]
        )

        st.caption(
            "Impact values are simplified estimates, "
            "not scientifically measured carbon emissions."
        )

# ==================================================
# ADMINISTRATOR
# ==================================================

elif st.session_state.page == "Administrator":

    st.title("Administrator Dashboard")

    if not st.session_state.admin_authenticated:

        st.subheader("Administrator Login")

        st.write(
            "This section is restricted to authorised administrators."
        )

        password = st.text_input(
            "Administrator Password",
            type="password"
        )

        if st.button("Login"):

            try:

                correct_password = st.secrets["admin"]["password"]

                if password == correct_password:

                    st.session_state.admin_authenticated = True
                    st.rerun()

                else:
                    st.error("Incorrect password.")

            except Exception:

                st.error(
                    "Password configuration not found. "
                    "Check your Streamlit secrets."
                )

    else:

        col1, col2 = st.columns([4, 1])

        with col1:
            st.success("Administrator access granted.")

        with col2:

            if st.button("Logout"):
                st.session_state.admin_authenticated = False
                st.rerun()

        st.divider()

        admin_tab1, admin_tab2, admin_tab3 = st.tabs([
            "Category Requests",
            "Manage Categories",
            "Add Category"
        ])

        with admin_tab1:

            st.subheader("Pending Category Requests")

            requests = get_pending_requests()

            if not requests:

                st.info("There are no pending requests.")

            else:

                for request in requests:

                    with st.expander(
                        f"{request['product_name']} - "
                        f"{request['category_name']}"
                    ):

                        st.write(
                            f"Suggested Impact: {request['suggested_value']}"
                        )

                        default_value = (
                            float(request["suggested_value"])
                            if request["suggested_value"] is not None
                            else 0.5
                        )

                        impact_value = st.number_input(
                            "Set Impact Value",
                            min_value=0.0,
                            max_value=1.0,
                            value=default_value,
                            step=0.01,
                            key=f"impact_{request['request_id']}"
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            if st.button(
                                "Approve Request",
                                key=f"approve_{request['request_id']}"
                            ):

                                try:

                                    approve_request(
                                        request["request_id"],
                                        impact_value
                                    )

                                    st.success("Request approved.")
                                    st.rerun()

                                except Exception as error:
                                    st.error(str(error))

                        with col2:

                            if st.button(
                                "Reject Request",
                                key=f"reject_{request['request_id']}"
                            ):

                                reject_request(
                                    request["request_id"],
                                    "Rejected by administrator"
                                )

                                st.success("Request rejected.")
                                st.rerun()

        with admin_tab2:

            st.subheader("Manage Existing Categories")

            all_categories = get_all_categories()

            if all_categories:

                category_options = {
                    row["category_name"]: row
                    for row in all_categories
                }

                selected_name = st.selectbox(
                    "Select Category",
                    list(category_options.keys())
                )

                selected = category_options[selected_name]

                with st.form("edit_category_form"):

                    new_impact = st.number_input(
                        "Impact Value",
                        min_value=0.0,
                        max_value=1.0,
                        value=float(selected["impact_value"]),
                        step=0.01
                    )

                    new_alternative = st.text_input(
                        "Greener Alternative",
                        value=selected["greener_alternative"] or ""
                    )

                    save_category = st.form_submit_button("Save Changes")

                    if save_category:

                        try:

                            edit_category(
                                selected["category_id"],
                                new_impact,
                                new_alternative
                            )

                            st.success("Category updated.")
                            st.rerun()

                        except Exception as error:
                            st.error(str(error))

        with admin_tab3:

            st.subheader("Add a New Product Category")

            with st.form("admin_add_category"):

                category_name = st.text_input("Category Name")

                impact_value = st.number_input(
                    "Impact Value",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.05,
                    step=0.01
                )

                alternative = st.text_input("Greener Alternative")

                submitted = st.form_submit_button("Add Category")

                if submitted:

                    try:

                        add_category(
                            category_name,
                            impact_value,
                            alternative
                        )

                        st.success("Category added successfully.")
                        st.rerun()

                    except Exception as error:
                        st.error(str(error))

# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "ShopImpact | Conscious Shopping Dashboard | IBCP"
)