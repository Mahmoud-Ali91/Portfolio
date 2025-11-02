import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from io import BytesIO
import openpyxl

# --- Session State Initialization ---
if 'clients_df' not in st.session_state:
    st.session_state.clients_df = pd.DataFrame(columns=[
        "Client_ID", "Client_Name", "Client_Type", "Zone", "Contact_Frequency_Days", "Visit_Notes"
    ])
if 'interactions_df' not in st.session_state:
    st.session_state.interactions_df = pd.DataFrame(columns=[
        "Interaction_ID", "Client_ID", "Rep_ID", "Timestamp", "Notes", "Units_Sold", 
        "Delivery_Time_Hours", "Distance_Km", "Fuel_Cost_EGP", "Fixed_Cost_EGP"
    ])
if 'reps_df' not in st.session_state:
    st.session_state.reps_df = pd.DataFrame(columns=["Rep_ID", "Rep_Name", "Zone"])

# --- Configuration Data ---
CONFIG = {
    "company": "NilePharma",
    "client_types": {
        "Doctor": {"weight": 1.0, "unit_price_range": (40, 100), "dist_success": 0.8},
        "Pharmacy": {"weight": 0.7, "unit_price_range": (50, 150), "dist_success": 0.9},
        "Hospital": {"weight": 1.5, "unit_price_range": (200, 500), "dist_success": 0.95},
        "Distributor": {"weight": 1.2, "unit_price_range": (100, 300), "dist_success": 0.85}
    },
    "zones": {
        "Cairo": {"type": "Urban", "cost_multiplier": 1.2, "dist_efficiency": 0.95, "visit_prob": 0.25},
        "Giza": {"type": "Urban", "cost_multiplier": 1.1, "dist_efficiency": 0.90, "visit_prob": 0.20},
        "Alexandria": {"type": "Urban", "cost_multiplier": 1.0, "dist_efficiency": 0.85, "visit_prob": 0.15},
        "Port Said": {"type": "Urban", "cost_multiplier": 1.0, "dist_efficiency": 0.80, "visit_prob": 0.10},
        "Mansoura": {"type": "Rural", "cost_multiplier": 0.9, "dist_efficiency": 0.70, "visit_prob": 0.10},
        "Tanta": {"type": "Rural", "cost_multiplier": 0.9, "dist_efficiency": 0.65, "visit_prob": 0.10},
        "Assiut": {"type": "Rural", "cost_multiplier": 0.8, "dist_efficiency": 0.60, "visit_prob": 0.05},
        "Luxor": {"type": "Rural", "cost_multiplier": 0.7, "dist_efficiency": 0.55, "visit_prob": 0.05}
    },
    "fuel_cost_per_km": 5.0,
    "fixed_cost_per_visit": 20.0,
    "delivery_time_range_hours": (0.5, 2.0),
    "units_sold_per_visit": (5, 15),
    "logistics_cost_factor": 0.2
}

# --- Streamlit Page Configuration ---
st.set_page_config(
    layout="wide",
    page_title="لوحة تحكم مندوبي الدواء | Medical Rep Control Dashboard",
    page_icon="👨‍⚕️",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Improved UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        font-family: 'Cairo', sans-serif;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #34e89e 0%, #0f3443 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        font-family: 'Cairo', sans-serif;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .rtl-text {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        font-family: 'Cairo', sans-serif;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    .section-header {
        font-family: 'Cairo', sans-serif;
        font-weight: 700;
        font-size: 1.5em;
        color: #2a5298;
        margin-top: 20px;
    }
    .nav-bar {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .stAlert {
        font-family: 'Cairo', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# --- Plotly Theme ---
PLOTLY_THEME = dict(
    font=dict(family="Cairo, sans-serif", size=12),
    title_font=dict(size=14),
    margin=dict(l=30, r=30, t=30, b=30),
    colorway=px.colors.qualitative.Plotly
)

# --- Data Generation for Testing ---
@st.cache_data
def generate_sample_data(n_clients=100, n_reps=20, n_interactions=1000):
    np.random.seed(42)
    clients = pd.DataFrame({
        "Client_ID": [f"C{i+1}" for i in range(n_clients)],
        "Client_Name": [f"Client_{i+1}" for i in range(n_clients)],
        "Client_Type": np.random.choice(list(CONFIG["client_types"].keys()), n_clients, 
                                      p=[0.3, 0.3, 0.2, 0.2]),
        "Zone": np.random.choice(
            list(CONFIG["zones"].keys()), n_clients, 
            p=[CONFIG["zones"][z]["visit_prob"] for z in CONFIG["zones"]]
        ),
        "Contact_Frequency_Days": np.random.randint(3, 15, n_clients),
        "Visit_Notes": [f"Notes for client {i+1}" for i in range(n_clients)]
    })
    reps = pd.DataFrame({
        "Rep_ID": [f"R{i+1}" for i in range(n_reps)],
        "Rep_Name": [f"Rep_{i+1}" for i in range(n_reps)],
        "Zone": np.random.choice(
            list(CONFIG["zones"].keys()), n_reps, 
            p=[CONFIG["zones"][z]["visit_prob"] for z in CONFIG["zones"]]
        )
    })
    # Generate interactions with balanced distribution across timeframes
    timestamps = []
    for _ in range(n_interactions):
        r = np.random.random()
        if r < 0.4:  # 40% today
            timestamps.append(datetime.now() - timedelta(hours=np.random.randint(0, 24)))
        elif r < 0.7:  # 30% last 7 days
            timestamps.append(datetime.now() - timedelta(days=np.random.randint(1, 7)))
        else:  # 30% last 30 days
            timestamps.append(datetime.now() - timedelta(days=np.random.randint(7, 30)))
    
    interactions = pd.DataFrame({
        "Interaction_ID": [f"I{i+1}" for i in range(n_interactions)],
        "Client_ID": np.random.choice(clients["Client_ID"], n_interactions),
        "Rep_ID": np.random.choice(reps["Rep_ID"], n_interactions),
        "Timestamp": timestamps,
        "Notes": [f"Visit note {i+1}" for i in range(n_interactions)],
        "Units_Sold": np.random.randint(*CONFIG["units_sold_per_visit"], n_interactions),
        "Delivery_Time_Hours": np.random.uniform(*CONFIG["delivery_time_range_hours"], n_interactions),
        "Distance_Km": np.random.uniform(5, 50, n_interactions),
        "Fuel_Cost_EGP": np.random.uniform(5, 50, n_interactions) * CONFIG["fuel_cost_per_km"],
        "Fixed_Cost_EGP": CONFIG["fixed_cost_per_visit"]
    })
    return clients, reps, interactions

# --- Data Upload ---
def upload_data():
    with st.sidebar.expander("📂 رفع البيانات | Data Upload", expanded=True):
        with st.progress(0, text="جاري التحضير... | Preparing..."):
            clients_file = st.sidebar.file_uploader("رفع ملف العملاء (CSV) | Upload Clients CSV", type="csv")
            reps_file = st.sidebar.file_uploader("رفع ملف المندوبين (CSV) | Upload Reps CSV", type="csv")
            
            if clients_file:
                with st.spinner("جاري رفع بيانات العملاء... | Uploading clients data..."):
                    try:
                        st.session_state.clients_df = pd.read_csv(clients_file)
                        if not all(col in st.session_state.clients_df.columns for col in 
                                  ["Client_ID", "Client_Name", "Client_Type", "Zone", "Contact_Frequency_Days"]):
                            st.sidebar.error("ملف العملاء يجب أن يحتوي على الأعمدة: Client_ID, Client_Name, Client_Type, Zone, Contact_Frequency_Days")
                        else:
                            st.sidebar.success("تم رفع بيانات العملاء بنجاح | Clients data uploaded successfully")
                    except Exception as e:
                        st.sidebar.error(f"خطأ في رفع ملف العملاء: {str(e)}")
            
            if reps_file:
                with st.spinner("جاري رفع بيانات المندوبين... | Uploading reps data..."):
                    try:
                        st.session_state.reps_df = pd.read_csv(reps_file)
                        if not all(col in st.session_state.reps_df.columns for col in ["Rep_ID", "Rep_Name", "Zone"]):
                            st.sidebar.error("ملف المندوبين يجب أن يحتوي على الأعمدة: Rep_ID, Rep_Name, Zone")
                        else:
                            st.sidebar.success("تم رفع بيانات المندوبين بنجاح | Reps data uploaded successfully")
                    except Exception as e:
                        st.sidebar.error(f"خطأ في رفع ملف المندوبين: {str(e)}")
            
            if st.sidebar.button("📊 توليد بيانات تجريبية | Generate Sample Data", key="generate_data"):
                with st.spinner("جاري توليد بيانات تجريبية... | Generating sample data..."):
                    for i in range(100):
                        st.progress(i + 1, text=f"توليد البيانات... {i+1}%")
                        clients, reps, interactions = generate_sample_data(n_interactions=1000)
                        st.session_state.clients_df = clients
                        st.session_state.reps_df = reps
                        st.session_state.interactions_df = interactions
                    st.sidebar.success("تم توليد بيانات تجريبية بنجاح | Sample data generated successfully")

# --- Mini CRM ---
def render_crm():
    with st.expander("📋 إدارة العملاء | Mini CRM", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='section-header'>إضافة/تحرير عميل | Add/Edit Client</div>", unsafe_allow_html=True)
            client_id = st.text_input("معرف العميل | Client ID", value=f"C{len(st.session_state.clients_df)+1}")
            client_name = st.text_input("اسم العميل | Client Name")
            client_type = st.selectbox("نوع العميل | Client Type", list(CONFIG["client_types"].keys()))
            zone = st.selectbox("المنطقة | Zone", list(CONFIG["zones"].keys()))
            contact_freq = st.number_input("تكرار التواصل (أيام) | Contact Frequency (Days)", min_value=1, value=7)
            visit_notes = st.text_area("ملاحظات الزيارة | Visit Notes")
            
            if st.button("إضافة/تحديث العميل | Add/Update Client", key="add_client"):
                with st.spinner("جاري تحديث العميل... | Updating client..."):
                    new_client = pd.DataFrame({
                        "Client_ID": [client_id], "Client_Name": [client_name], "Client_Type": [client_type],
                        "Zone": [zone], "Contact_Frequency_Days": [contact_freq], "Visit_Notes": [visit_notes]
                    })
                    st.session_state.clients_df = pd.concat([st.session_state.clients_df, new_client]).drop_duplicates(subset="Client_ID", keep="last")
                    st.success("تم إضافة/تحديث العميل بنجاح | Client added/updated successfully")
        
        with col2:
            st.markdown("<div class='section-header'>سجل التفاعلات | Interaction Log</div>", unsafe_allow_html=True)
            interaction_id = f"I{len(st.session_state.interactions_df)+1}"
            client_id = st.selectbox("اختر العميل | Select Client", st.session_state.clients_df["Client_ID"])
            rep_id = st.selectbox("اختر المندوب | Select Rep", st.session_state.reps_df["Rep_ID"])
            notes = st.text_area("ملاحظات التفاعل | Interaction Notes")
            units_sold = st.number_input("الوحدات المباعة | Units Sold", min_value=0, value=0)
            delivery_time = st.number_input("وقت التوصيل (ساعات) | Delivery Time (Hours)", min_value=0.0, value=1.0)
            distance_km = st.number_input("المسافة (كم) | Distance (Km)", min_value=0.0, value=10.0)
            
            if st.button("إضافة تفاعل | Add Interaction", key="add_interaction"):
                with st.spinner("جاري إضافة التفاعل... | Adding interaction..."):
                    fuel_cost = distance_km * CONFIG["fuel_cost_per_km"]
                    interaction = pd.DataFrame({
                        "Interaction_ID": [interaction_id], "Client_ID": [client_id], "Rep_ID": [rep_id],
                        "Timestamp": [datetime.now()], "Notes": [notes], "Units_Sold": [units_sold],
                        "Delivery_Time_Hours": [delivery_time], "Distance_Km": [distance_km],
                        "Fuel_Cost_EGP": [fuel_cost], "Fixed_Cost_EGP": [CONFIG["fixed_cost_per_visit"]]
                    })
                    st.session_state.interactions_df = pd.concat([st.session_state.interactions_df, interaction])
                    st.success("تم إضافة التفاعل بنجاح | Interaction added successfully")

# --- Sidebar Filters ---
def render_sidebar():
    with st.sidebar.expander("🎛️ لوحة التحكم | Control Panel", expanded=True):
        selected_reps = st.multiselect(
            "المندوبين | Reps", 
            st.session_state.reps_df["Rep_Name"].unique(),
            default=st.session_state.reps_df["Rep_Name"].unique()[:2],
            help="اختر مندوبين لتحليل أدائهم | Select reps to analyze their performance"
        )
        selected_zones = st.multiselect(
            "المناطق | Zones", 
            list(CONFIG["zones"].keys()),
            default=list(CONFIG["zones"].keys())[:2],
            help="اختر المناطق لتصفية البيانات | Select zones to filter data"
        )
        selected_client_types = st.multiselect(
            "أنواع العملاء | Client Types",
            list(CONFIG["client_types"].keys()),
            default=list(CONFIG["client_types"].keys())[:2],
            help="اختر أنواع العميل | Select client types"
        )
        timeframe = st.selectbox(
            "الإطار الزمني | Timeframe",
            ["يومي | Daily", "أسبوعي | Weekly", "شهري | Monthly"],
            help="اختر الفترة الزمنية للتحليل | Select timeframe for analysis"
        )
        movement_scenario = st.selectbox(
            "سيناريو الحركة | Movement Scenario",
            ["الوضع الحالي | Current State", "توسع مكثف (+50%) | High-Intensity (+50%)", 
             "انكماش (-50%) | Low-Intensity (-50%)", "مسارات محسنة | Optimized Routes"],
            help="اختر سيناريو لمحاكاة الحركة | Select a movement scenario for simulation"
        )
        custom_visit_change = st.slider(
            "تغيير مخصص لتكرار الزيارات (%) | Custom Visit Frequency Change (%)", 
            -50, 50, 0,
            help="اضبط تكرار الزيارات لمحاكاة مخصصة | Adjust visit frequency for custom simulation"
        )
    
    return selected_reps, selected_zones, selected_client_types, timeframe, movement_scenario, custom_visit_change

# --- Navigation Bar ---
def render_navigation():
    st.markdown("""
    <div class="nav-bar">
        <div style="display: flex; justify-content: space-around; font-family: 'Cairo', sans-serif;">
            <a href="#summary" style="color: #2a5298; text-decoration: none;">ملخص | Summary</a>
            <a href="#crm" style="color: #2a5298; text-decoration: none;">CRM</a>
            <a href="#reports" style="color: #2a5298; text-decoration: none;">تقارير | Reports</a>
            <a href="#visualizations" style="color: #2a5298; text-decoration: none;">لوحة القيادة | Dashboard</a>
            <a href="#simulations" style="color: #2a5298; text-decoration: none;">محاكاة | Simulations</a>
            <a href="#export" style="color: #2a5298; text-decoration: none;">تصدير | Export</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Executive Summary ---
def render_executive_summary(filtered_interactions):
    st.markdown("<a name='summary'></a>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>📈 ملخص تنفيذي | Executive Summary</div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    total_visits = len(filtered_interactions)
    active_clients = filtered_interactions["Client_ID"].nunique()
    rep_utilization = (total_visits / (st.session_state.reps_df["Rep_ID"].nunique() * 20)) * 100 if total_visits > 0 else 0
    avg_dist_efficiency = filtered_interactions["Dist_Efficiency"].mean() if "Dist_Efficiency" in filtered_interactions.columns else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>إجمالي الزيارات | Total Visits</h3>
            <h2>{total_visits}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>العملاء النشطين | Active Clients</h3>
            <h2>{active_clients}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>استغلال المندوبين | Rep Utilization</h3>
            <h2>{rep_utilization:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>كفاءة التوزيع | Distribution Efficiency</h3>
            <h2>{avg_dist_efficiency:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)

# --- Reporting ---
def generate_reports(filtered_interactions, timeframe):
    st.markdown("<a name='reports'></a>", unsafe_allow_html=True)
    with st.expander(f"📊 تقارير {timeframe} | {timeframe} Reports", expanded=True):
        # Cost per Visit
        cost_per_visit = filtered_interactions.groupby("Rep_ID").agg({
            "Total_Cost_EGP": "mean",
            "Logistics_Cost_EGP": "mean"
        }).reset_index()
        cost_per_visit = cost_per_visit.merge(st.session_state.reps_df[["Rep_ID", "Rep_Name"]], on="Rep_ID")
        
        # Visits per Rep
        visits_per_rep = filtered_interactions.groupby("Rep_ID").size().reset_index(name="Visits")
        visits_per_rep = visits_per_rep.merge(st.session_state.reps_df[["Rep_ID", "Rep_Name"]], on="Rep_ID")
        
        # Missed Targets
        clients = st.session_state.clients_df.copy()
        clients["Last_Visit"] = clients["Client_ID"].map(
            filtered_interactions.groupby("Client_ID")["Timestamp"].max()
        )
        clients["Days_Since_Last_Visit"] = (datetime.now() - clients["Last_Visit"]).dt.days.fillna(999)
        missed_targets = clients[clients["Days_Since_Last_Visit"] > clients["Contact_Frequency_Days"]]
        
        # Time Spent vs. Value Returned
        time_vs_value = filtered_interactions.groupby("Rep_ID").agg({
            "Delivery_Time_Hours": "sum",
            "Revenue_EGP": "sum",
            "Net_Profit_EGP": "sum"
        }).reset_index()
        time_vs_value["Value_Per_Hour"] = time_vs_value["Revenue_EGP"] / time_vs_value["Delivery_Time_Hours"].replace(0, np.nan)
        time_vs_value = time_vs_value.merge(st.session_state.reps_df[["Rep_ID", "Rep_Name"]], on="Rep_ID")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='section-header'>التكلفة لكل زيارة | Cost per Visit</div>", unsafe_allow_html=True)
            st.dataframe(cost_per_visit[["Rep_Name", "Total_Cost_EGP", "Logistics_Cost_EGP"]], use_container_width=True)
        
        with col2:
            st.markdown("<div class='section-header'>الزيارات لكل مندوب | Visits per Rep</div>", unsafe_allow_html=True)
            st.dataframe(visits_per_rep[["Rep_Name", "Visits"]], use_container_width=True)
        
        st.markdown("<div class='section-header'>الأهداف المفقودة | Missed Targets</div>", unsafe_allow_html=True)
        st.dataframe(missed_targets[["Client_Name", "Client_Type", "Zone", "Days_Since_Last_Visit"]], use_container_width=True)
        
        st.markdown("<div class='section-header'>الوقت المستغرق مقابل القيمة | Time Spent vs. Value</div>", unsafe_allow_html=True)
        st.dataframe(time_vs_value[["Rep_Name", "Delivery_Time_Hours", "Revenue_EGP", "Value_Per_Hour"]], use_container_width=True)

# --- Visualizations ---
def render_visualizations(filtered_interactions):
    st.markdown("<a name='visualizations'></a>", unsafe_allow_html=True)
    with st.expander("📈 لوحة القيادة الإدارية | Managerial Dashboard", expanded=True):
        if filtered_interactions.empty:
            st.error("⚠️ لا توجد بيانات لعرض الرسوم البيانية | No data for visualizations", icon="🚨")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='section-header'>التكلفة مقابل الإيرادات | Cost vs. Revenue</div>", unsafe_allow_html=True)
            fig = px.scatter(
                filtered_interactions.groupby("Rep_ID").agg({
                    "Total_Cost_EGP": "sum",
                    "Units_Sold": "sum",
                    "Revenue_EGP": "sum"
                }).reset_index().merge(st.session_state.reps_df[["Rep_ID", "Rep_Name"]], on="Rep_ID"),
                x="Total_Cost_EGP", y="Revenue_EGP", color="Rep_Name", size="Units_Sold",
                title="التكلفة مقابل الإيرادات | Cost vs. Revenue",
                hover_data=["Rep_Name", "Units_Sold"]
            )
            fig.update_layout(**PLOTLY_THEME)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("<div class='section-header'>الزيارات لكل منطقة | Visits per Zone</div>", unsafe_allow_html=True)
            fig = px.bar(
                filtered_interactions.groupby("Zone").size().reset_index(name="Visits"),
                x="Zone", y="Visits", title="الزيارات لكل منطقة | Visits per Zone",
                color="Zone"
            )
            fig.update_layout(**PLOTLY_THEME)
            st.plotly_chart(fig, use_container_width=True)
        
        # Additional Analytical Charts
        st.markdown("<div class='section-header'>الإيرادات حسب نوع العميل | Revenue by Client Type</div>", unsafe_allow_html=True)
        revenue_by_client = filtered_interactions.groupby("Client_Type")["Revenue_EGP"].sum().reset_index()
        fig = px.bar(
            revenue_by_client,
            x="Client_Type", y="Revenue_EGP",
            title="الإيرادات حسب نوع العميل | Revenue by Client Type",
            color="Client_Type"
        )
        fig.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<div class='section-header'>كفاءة التكلفة حسب المنطقة | Cost Efficiency by Zone</div>", unsafe_allow_html=True)
        cost_eff = filtered_interactions.groupby("Zone").agg({
            "Total_Cost_EGP": "sum",
            "Net_Profit_EGP": "sum"
        }).reset_index()
        fig = go.Figure(data=[
            go.Bar(name="التكلفة | Cost", x=cost_eff["Zone"], y=cost_eff["Total_Cost_EGP"]),
            go.Bar(name="صافي الربح | Net Profit", x=cost_eff["Zone"], y=cost_eff["Net_Profit_EGP"])
        ])
        fig.update_layout(
            barmode="group", title="كفاءة التكلفة حسب المنطقة | Cost Efficiency by Zone",
            **PLOTLY_THEME
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<div class='section-header'>اتجاه الإيرادات | Revenue Trend Over Time</div>", unsafe_allow_html=True)
        revenue_trend = filtered_interactions.groupby(filtered_interactions["Timestamp"].dt.date)["Revenue_EGP"].sum().reset_index()
        fig = px.line(
            revenue_trend,
            x="Timestamp", y="Revenue_EGP",
            title="اتجاه الإيرادات اليومي | Daily Revenue Trend",
            markers=True
        )
        fig.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<div class='section-header'>تفاعل العملاء حسب تكرار الزيارات | Client Engagement by Visit Frequency</div>", unsafe_allow_html=True)
        actual_vs_expected = filtered_interactions.merge(
            st.session_state.clients_df[["Client_ID", "Client_Type", "Contact_Frequency_Days"]], 
            on="Client_ID"
        )
        actual_vs_expected = actual_vs_expected.groupby("Client_Type").agg({
            "Client_ID": "count",
            "Contact_Frequency_Days": "mean"
        }).reset_index().rename(columns={"Client_ID": "Actual_Visits"})
        actual_vs_expected["Expected_Visits"] = 30 / actual_vs_expected["Contact_Frequency_Days"]
        fig = go.Figure(data=[
            go.Bar(name="الزيارات الفعلية | Actual Visits", x=actual_vs_expected["Client_Type"], y=actual_vs_expected["Actual_Visits"]),
            go.Bar(name="الزيارات المتوقعة | Expected Visits", x=actual_vs_expected["Client_Type"], y=actual_vs_expected["Expected_Visits"])
        ])
        fig.update_layout(
            barmode="group", title="تفاعل العملاء حسب تكرار الزيارات | Client Engagement by Visit Frequency",
            **PLOTLY_THEME
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<div class='section-header'>توزيع التكاليف حسب المنطقة | Zone Cost Distribution</div>", unsafe_allow_html=True)
        cost_dist = filtered_interactions.groupby("Zone").agg({
            "Fuel_Cost_EGP": "sum",
            "Fixed_Cost_EGP": "sum",
            "Logistics_Cost_EGP": "sum"
        }).reset_index()
        fig = px.pie(
            cost_dist.melt(id_vars="Zone", value_vars=["Fuel_Cost_EGP", "Fixed_Cost_EGP", "Logistics_Cost_EGP"], 
                          var_name="Cost_Type", value_name="Cost"),
            values="Cost", names="Cost_Type", facet_col="Zone",
            title="توزيع التكاليف حسب المنطقة | Zone Cost Distribution"
        )
        fig.update_layout(**PLOTLY_THEME)
        st.plotly_chart(fig, use_container_width=True)

# --- Strategy Simulation ---
def render_strategy_simulation(filtered_interactions, movement_scenario, custom_visit_change):
    st.markdown("<a name='simulations'></a>", unsafe_allow_html=True)
    with st.expander("🧠 محاكاة الاستراتيجيات | Strategy Simulation", expanded=False):
        sim_interactions = filtered_interactions.copy()
        visit_multiplier = 1.0
        if movement_scenario == "توسع مكثف (+50%) | High-Intensity (+50%)":
            visit_multiplier = 1.5
        elif movement_scenario == "انكماش (-50%) | Low-Intensity (-50%)":
            visit_multiplier = 0.5
        elif movement_scenario == "مسارات محسنة | Optimized Routes":
            sim_interactions["Distance_Km"] *= 0.8
        if custom_visit_change != 0:
            visit_multiplier = 1 + (custom_visit_change / 100)
        
        if visit_multiplier != 1.0:
            sim_interactions["Units_Sold"] *= visit_multiplier
            sim_interactions["Delivery_Time_Hours"] *= visit_multiplier
            sim_interactions["Distance_Km"] *= visit_multiplier
            sim_interactions["Fuel_Cost_EGP"] = sim_interactions["Distance_Km"] * CONFIG["fuel_cost_per_km"]
            sim_interactions["Total_Cost_EGP"] = sim_interactions["Fuel_Cost_EGP"] + sim_interactions["Fixed_Cost_EGP"]
            sim_interactions["Logistics_Cost_EGP"] = sim_interactions["Fuel_Cost_EGP"] * CONFIG["logistics_cost_factor"]
            sim_interactions["Revenue_EGP"] = sim_interactions.apply(
                lambda row: row["Units_Sold"] * np.random.uniform(*CONFIG["client_types"][row["Client_Type"]]["unit_price_range"]) * 
                            row["Dist_Success"] * row["Dist_Efficiency"], axis=1
            )
            sim_interactions["Net_Profit_EGP"] = sim_interactions["Revenue_EGP"] - (
                sim_interactions["Total_Cost_EGP"] + sim_interactions["Logistics_Cost_EGP"]
            )
        
        st.markdown("<div class='section-header'>إعادة تخصيص المناطق | Reassign Zones</div>", unsafe_allow_html=True)
        rep_id = st.selectbox("اختر المندوب | Select Rep", st.session_state.reps_df["Rep_ID"], key="reassign_rep")
        new_zone = st.selectbox("المنطقة الجديدة | New Zone", list(CONFIG["zones"].keys()), key="reassign_zone")
        
        if st.button("محاكاة إعادة التخصيص | Simulate Reassignment", key="simulate_reassign"):
            with st.spinner("جاري محاكاة إعادة التخصيص... | Simulating reassignment..."):
                sim_reps = st.session_state.reps_df.copy()
                sim_reps.loc[sim_reps["Rep_ID"] == rep_id, "Zone"] = new_zone
                st.success(f"تم محاكاة إعادة تخصيص {rep_id} إلى {new_zone} | Reassignment simulated")
                st.dataframe(sim_reps[["Rep_ID", "Rep_Name", "Zone"]], use_container_width=True)
        
        st.markdown("<div class='section-header'>إعادة توزيع العملاء | Reallocate Clients</div>", unsafe_allow_html=True)
        client_id = st.selectbox("اختر العميل | Select Client", st.session_state.clients_df["Client_ID"], key="reallocate_client")
        new_rep_id = st.selectbox("مندوب جديد | New Rep", st.session_state.reps_df["Rep_ID"], key="reallocate_rep")
        
        if st.button("محاكاة إعادة التوزيع | Simulate Reallocation", key="simulate_reallocate"):
            with st.spinner("جاري محاكاة إعادة التوزيع... | Simulating reallocation..."):
                sim_interactions = sim_interactions.copy()
                sim_interactions.loc[sim_interactions["Client_ID"] == client_id, "Rep_ID"] = new_rep_id
                st.success(f"تم محاكاة إعادة توزيع {client_id} إلى {new_rep_id} | Reallocation simulated")
                st.dataframe(sim_interactions[["Interaction_ID", "Client_ID", "Rep_ID", "Timestamp"]], use_container_width=True)
        
        st.markdown("<div class='section-header'>نتائج المحاكاة | Simulation Results</div>", unsafe_allow_html=True)
        sim_summary = pd.DataFrame({
            "القياس | Metric": ["إجمالي التكلفة | Total Cost", "إجمالي الإيرادات | Total Revenue", 
                               "صافي الربح | Net Profit", "كفاءة التوزيع | Dist Efficiency"],
            "الحالي | Current": [
                filtered_interactions["Total_Cost_EGP"].sum(),
                filtered_interactions["Revenue_EGP"].sum(),
                filtered_interactions["Net_Profit_EGP"].sum(),
                filtered_interactions["Dist_Efficiency"].mean() if "Dist_Efficiency" in filtered_interactions.columns else 0
            ],
            "المحاكاة | Simulated": [
                sim_interactions["Total_Cost_EGP"].sum(),
                sim_interactions["Revenue_EGP"].sum(),
                sim_interactions["Net_Profit_EGP"].sum(),
                sim_interactions["Dist_Efficiency"].mean() if "Dist_Efficiency" in sim_interactions.columns else 0
            ]
        })
        st.dataframe(sim_summary, use_container_width=True)

# --- Data Export ---
def render_data_export(filtered_interactions):
    st.markdown("<a name='export'></a>", unsafe_allow_html=True)
    with st.expander("📥 تصدير البيانات | Data Export", expanded=False):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        export_data = filtered_interactions.merge(
            st.session_state.clients_df[["Client_ID", "Client_Name", "Client_Type", "Zone"]], 
            on="Client_ID"
        ).merge(st.session_state.reps_df[["Rep_ID", "Rep_Name"]], on="Rep_ID")
        
        csv_data = export_data[["Rep_Name", "Client_Name", "Client_Type", "Zone", "Timestamp", 
                                "Units_Sold", "Total_Cost_EGP", "Revenue_EGP", "Net_Profit_EGP", "Dist_Efficiency"]].to_csv(index=False)
        st.download_button(
            label="📊 تنزيل البيانات (CSV) | Download Data (CSV)",
            data=csv_data,
            file_name=f"rep_dashboard_{timestamp}.csv",
            mime="text/csv",
            key="download_csv"
        )
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            export_data[["Rep_Name", "Client_Name", "Client_Type", "Zone", "Timestamp", 
                         "Units_Sold", "Total_Cost_EGP", "Revenue_EGP", "Net_Profit_EGP", "Dist_Efficiency"]].to_excel(writer, index=False)
        excel_data = output.getvalue()
        st.download_button(
            label="📊 تنزيل البيانات (Excel) | Download Data (Excel)",
            data=excel_data,
            file_name=f"rep_dashboard_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_excel"
        )

# --- Main Function ---
def main():
    st.markdown("""
    <div class="main-header rtl-text">
        <h1>👨‍⚕️ لوحة تحكم مندوبي الدواء</h1>
        <h2>Medical Representative Control Dashboard</h2>
        <p>إدارة المندوبين وتتبع الأداء وتحسين تكاليف الحركة والتوزيع | Manage Reps, Track Performance, Optimize Movement & Distribution Costs</p>
    </div>
    """, unsafe_allow_html=True)
    
    render_navigation()
    upload_data()
    
    if st.session_state.clients_df.empty or st.session_state.reps_df.empty:
        st.error("⚠️ يرجى رفع بيانات العملاء والمندوبين أو توليد بيانات تجريبية | Please upload clients and reps data or generate sample data", icon="🚨")
        return
    
    selected_reps, selected_zones, selected_client_types, timeframe, movement_scenario, custom_visit_change = render_sidebar()
    
    # Filter interactions
    filtered_interactions = st.session_state.interactions_df[
        (st.session_state.interactions_df["Rep_ID"].isin(
            st.session_state.reps_df[st.session_state.reps_df["Rep_Name"].isin(selected_reps)]["Rep_ID"]
        )) &
        (st.session_state.interactions_df["Client_ID"].isin(
            st.session_state.clients_df[st.session_state.clients_df["Zone"].isin(selected_zones)]["Client_ID"]
        )) &
        (st.session_state.interactions_df["Client_ID"].isin(
            st.session_state.clients_df[st.session_state.clients_df["Client_Type"].isin(selected_client_types)]["Client_ID"]
        ))
    ].copy()
    
    if timeframe == "يومي | Daily":
        filtered_interactions = filtered_interactions[
            filtered_interactions["Timestamp"].dt.date == datetime.now().date()
        ]
    elif timeframe == "أسبوعي | Weekly":
        filtered_interactions = filtered_interactions[
            filtered_interactions["Timestamp"] >= datetime.now() - timedelta(days=7)
        ]
    
    if filtered_interactions.empty:
        st.error("⚠️ لا توجد بيانات تطابق المرشحات | No data matches filters", icon="🚨")
        return
    
    # Add distribution metrics and calculate costs/revenue
    try:
        filtered_interactions = filtered_interactions.merge(
            st.session_state.clients_df[["Client_ID", "Client_Type", "Zone"]], on="Client_ID", how="left"
        )
        filtered_interactions["Dist_Success"] = filtered_interactions["Client_Type"].map(
            lambda x: CONFIG["client_types"][x]["dist_success"] if x in CONFIG["client_types"] else 0.8
        )
        filtered_interactions["Dist_Efficiency"] = filtered_interactions["Zone"].map(
            lambda x: CONFIG["zones"][x]["dist_efficiency"] if x in CONFIG["zones"] else 0.7
        )
        filtered_interactions["Total_Cost_EGP"] = filtered_interactions["Fuel_Cost_EGP"] + filtered_interactions["Fixed_Cost_EGP"]
        filtered_interactions["Logistics_Cost_EGP"] = filtered_interactions["Fuel_Cost_EGP"] * CONFIG["logistics_cost_factor"]
        filtered_interactions["Revenue_EGP"] = filtered_interactions.apply(
            lambda row: row["Units_Sold"] * np.random.uniform(*CONFIG["client_types"][row["Client_Type"]]["unit_price_range"]) * 
                        row["Dist_Success"] * row["Dist_Efficiency"], axis=1
        )
        filtered_interactions["Net_Profit_EGP"] = filtered_interactions["Revenue_EGP"] - (
            filtered_interactions["Total_Cost_EGP"] + filtered_interactions["Logistics_Cost_EGP"]
        )
    except KeyError as e:
        st.error(f"خطأ في البيانات: العمود {str(e)} مفقود. تحقق من بيانات العملاء أو المندوبين | Data error: Column {str(e)} missing. Check clients or reps data.", icon="🚨")
        return
    
    render_executive_summary(filtered_interactions)
    st.markdown("<a name='crm'></a>", unsafe_allow_html=True)
    render_crm()
    generate_reports(filtered_interactions, timeframe)
    render_visualizations(filtered_interactions)
    render_strategy_simulation(filtered_interactions, movement_scenario, custom_visit_change)
    render_data_export(filtered_interactions)

if __name__ == "__main__":
    main()