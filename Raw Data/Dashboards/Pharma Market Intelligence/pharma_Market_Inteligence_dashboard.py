import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import timedelta, date
import warnings
warnings.filterwarnings('ignore')

# --- Configuration ---
st.set_page_config(
    layout="wide", 
    page_title="لوحة الإدارة الاستراتيجية - تكلفة الحركة والمبيعات",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .strategic-kpi {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 5px 0;
    }
    
    .rtl-text {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    
    .expansion-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
    }
    
    .campaign-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        padding: 15px;
        border-radius: 10px;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Generation for Strategic Analysis ---
@st.cache_data
def generate_strategic_data():
    """Generate comprehensive pharmaceutical business data"""
    # Removed np.random.seed(42) to allow truly random data generation
    
    # Egyptian pharmaceutical companies with market positioning
    companies_data = {
        "Eva Pharma": {"market_share": 0.15, "expansion_budget": 2500000, "category": "Premium"},
        "Memphis Pharmaceuticals": {"market_share": 0.12, "expansion_budget": 2000000, "category": "Mid-Market"},
        "Sedico Pharmaceutical": {"market_share": 0.10, "expansion_budget": 1800000, "category": "Generic"},
        "Minapharm": {"market_share": 0.08, "expansion_budget": 1500000, "category": "Specialty"},
        "Delta Pharma": {"market_share": 0.07, "expansion_budget": 1200000, "category": "Premium"},
        "October Pharma": {"market_share": 0.06, "expansion_budget": 1000000, "category": "Mid-Market"},
        "Rameda Pharmaceuticals": {"market_share": 0.05, "expansion_budget": 800000, "category": "Generic"},
        "Adwia Pharmaceuticals": {"market_share": 0.04, "expansion_budget": 600000, "category": "Specialty"}
    }
    
    governorates = ["Cairo", "Giza", "Alexandria", "Mansoura", "Tanta", "Assiut", "Luxor", "Port Said"]
    
    # Product categories with strategic importance
    product_categories = {
        "Cardiovascular": {"market_size": 1200000000, "growth_rate": 0.12, "competition": "High"},
        "Diabetes": {"market_size": 800000000, "growth_rate": 0.15, "competition": "Medium"},
        "Respiratory": {"market_size": 600000000, "growth_rate": 0.08, "competition": "High"},
        "Oncology": {"market_size": 400000000, "growth_rate": 0.20, "competition": "Low"},
        "Dermatology": {"market_size": 300000000, "growth_rate": 0.10, "competition": "Medium"},
        "Pediatrics": {"market_size": 250000000, "growth_rate": 0.07, "competition": "High"}
    }
    
    # Campaign types and their effectiveness
    campaign_types = {
        "Digital Marketing": {"cost_multiplier": 0.8, "reach_multiplier": 1.5, "conversion": 0.25},
        "Medical Representative": {"cost_multiplier": 1.2, "reach_multiplier": 1.0, "conversion": 0.35},
        "Conference & Events": {"cost_multiplier": 1.8, "reach_multiplier": 0.7, "conversion": 0.45},
        "Scientific Publications": {"cost_multiplier": 1.0, "reach_multiplier": 0.8, "conversion": 0.30},
        "Key Opinion Leaders": {"cost_multiplier": 2.0, "reach_multiplier": 0.6, "conversion": 0.50}
    }
    
    data = []
    
    for i in range(800):  # Generate comprehensive dataset
        company = np.random.choice(list(companies_data.keys()))
        company_info = companies_data[company]
        
        governorate = np.random.choice(governorates)
        product_cat = np.random.choice(list(product_categories.keys()))
        product_info = product_categories[product_cat]
        
        campaign_type = np.random.choice(list(campaign_types.keys()))
        campaign_info = campaign_types[campaign_type]
        
        # Movement Cost Calculations
        if governorate in ["Cairo", "Giza"]:
            base_movement_cost = np.random.uniform(25, 45)
            market_potential = np.random.uniform(0.8, 1.0)
        elif governorate in ["Alexandria", "Port Said"]:
            base_movement_cost = np.random.uniform(20, 35)
            market_potential = np.random.uniform(0.6, 0.8)
        else:
            base_movement_cost = np.random.uniform(15, 28)
            market_potential = np.random.uniform(0.4, 0.6)
        
        # Strategic Metrics
        daily_visits = np.random.randint(6, 18)
        working_days = np.random.randint(20, 25)
        monthly_visits = daily_visits * working_days
        
        # Movement costs with strategic factors
        total_movement_cost = base_movement_cost * monthly_visits
        
        # Sales Performance
        base_conversion_rate = campaign_info["conversion"] * market_potential
        converted_visits = monthly_visits * base_conversion_rate
        
        # Product pricing based on category and company positioning
        if product_cat == "Oncology":
            unit_price = np.random.uniform(200, 500)
        elif product_cat == "Cardiovascular":
            unit_price = np.random.uniform(80, 180)
        elif product_cat == "Diabetes":
            unit_price = np.random.uniform(60, 150)
        else:
            unit_price = np.random.uniform(40, 120)
        
        # Adjust pricing by company category
        if company_info["category"] == "Premium":
            unit_price *= 1.3
        elif company_info["category"] == "Generic":
            unit_price *= 0.7
        
        units_per_visit = np.random.randint(8, 25)
        monthly_revenue = converted_visits * units_per_visit * unit_price
        
        # Strategic KPIs
        gross_profit_margin = np.random.uniform(0.35, 0.65)
        monthly_gross_profit = monthly_revenue * gross_profit_margin
        
        # Campaign Investment
        campaign_investment = total_movement_cost * campaign_info["cost_multiplier"]
        total_investment = total_movement_cost + campaign_investment
        
        # ROI Calculations
        net_profit = monthly_gross_profit - total_investment
        roi = (net_profit / total_investment) if total_investment > 0 else 0
        
        # Market Expansion Metrics
        market_penetration = np.random.uniform(0.02, 0.15)
        expansion_opportunity = product_info["growth_rate"] * market_potential
        
        # Customer Acquisition Cost
        cac = total_investment / converted_visits if converted_visits > 0 else 0
        
        # Customer Lifetime Value (estimated)
        clv = unit_price * units_per_visit * np.random.uniform(8, 24)  # 8-24 months retention
        
        # Strategic Score (composite metric)
        strategic_score = (
            (roi + 1) * 0.3 +  # ROI importance
            expansion_opportunity * 0.25 +  # Growth potential
            (clv / cac if cac > 0 else 0) * 0.2 +  # LTV/CAC ratio
            market_penetration * 0.15 +  # Current penetration
            company_info["market_share"] * 0.1  # Company strength
        )
        
        data.append([
            company, company_info["category"], company_info["market_share"],
            governorate, product_cat, campaign_type,
            daily_visits, working_days, monthly_visits,
            base_movement_cost, total_movement_cost,
            campaign_investment, total_investment,
            base_conversion_rate, converted_visits,
            unit_price, units_per_visit, monthly_revenue,
            gross_profit_margin, monthly_gross_profit,
            net_profit, roi, cac, clv,
            market_penetration, expansion_opportunity,
            strategic_score, product_info["market_size"],
            product_info["growth_rate"], product_info["competition"]
        ])
    
    columns = [
        "Company", "Company_Category", "Market_Share",
        "Governorate", "Product_Category", "Campaign_Type",
        "Daily_Visits", "Working_Days", "Monthly_Visits",
        "Cost_Per_Visit_EGP", "Total_Movement_Cost_EGP",
        "Campaign_Investment_EGP", "Total_Investment_EGP",
        "Conversion_Rate", "Converted_Visits",
        "Unit_Price_EGP", "Units_Per_Visit", "Monthly_Revenue_EGP",
        "Gross_Profit_Margin", "Monthly_Gross_Profit_EGP",
        "Net_Profit_EGP", "ROI", "CAC_EGP", "CLV_EGP",
        "Market_Penetration", "Expansion_Opportunity",
        "Strategic_Score", "Market_Size_EGP", "Growth_Rate", "Competition_Level"
    ]
    
    return pd.DataFrame(data, columns=columns)

# --- Strategic Analysis Functions ---
def calculate_expansion_recommendations(df):
    """Calculate market expansion recommendations"""
    expansion_analysis = df.groupby(["Governorate", "Product_Category"]).agg({
        "Strategic_Score": "mean",
        "ROI": "mean",
        "Market_Penetration": "mean",
        "Expansion_Opportunity": "mean",
        "Total_Investment_EGP": "sum",
        "Net_Profit_EGP": "sum"
    }).reset_index()
    
    # Calculate expansion priority score
    expansion_analysis["Expansion_Priority"] = (
        expansion_analysis["Strategic_Score"] * 0.4 +
        expansion_analysis["ROI"] * 0.3 +
        expansion_analysis["Expansion_Opportunity"] * 0.3
    )
    
    return expansion_analysis.sort_values("Expansion_Priority", ascending=False)

def campaign_effectiveness_analysis(df):
    """Analyze campaign effectiveness across different dimensions"""
    campaign_analysis = df.groupby("Campaign_Type").agg({
        "ROI": ["mean", "std"],
        "Conversion_Rate": "mean",
        "CAC_EGP": "mean",
        "CLV_EGP": "mean",
        "Strategic_Score": "mean"
    }).round(3)
    
    campaign_analysis.columns = ["ROI_Mean", "ROI_Std", "Avg_Conversion", "Avg_CAC", "Avg_CLV", "Strategic_Score"]
    campaign_analysis["LTV_CAC_Ratio"] = campaign_analysis["Avg_CLV"] / campaign_analysis["Avg_CAC"]
    
    return campaign_analysis.reset_index()

# --- Main Application ---
def main():
    # Header
    st.markdown("""
    <div class="main-header rtl-text">
        <h1>📊 لوحة الإدارة الاستراتيجية للصناعات الدوائية</h1>
        <h2>Strategic Pharmaceutical Business Intelligence Dashboard</h2>
        <p>تحليل شامل لتكلفة الحركة والمبيعات والتوسع والحملات التسويقية</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load comprehensive data
    df = generate_strategic_data()
    
    # Sidebar - Strategic Controls
    st.sidebar.markdown("## 🎛️ Strategic Control Panel")
    st.sidebar.markdown("### المرشحات الاستراتيجية")
    
    # Strategic Filters
    selected_companies = st.sidebar.multiselect(
        "الشركات / Companies",
        options=df["Company"].unique(),
        default=df["Company"].unique()[:4]
    )
    
    selected_categories = st.sidebar.multiselect(
        "فئات المنتجات / Product Categories",
        options=df["Product_Category"].unique(),
        default=df["Product_Category"].unique()
    )
    
    selected_governorates = st.sidebar.multiselect(
        "المحافظات / Governorates",
        options=df["Governorate"].unique(),
        default=df["Governorate"].unique()
    )
    
    # Strategic Metrics Thresholds
    st.sidebar.markdown("### 🎯 Strategic Thresholds")
    min_roi = st.sidebar.slider("Minimum ROI %", -50, 200, 10) / 100
    min_strategic_score = st.sidebar.slider("Minimum Strategic Score", 0.0, 2.0, 0.5)
    
    # Time Period
    st.sidebar.markdown("### 📅 Analysis Period")
    analysis_months = st.sidebar.selectbox("Analysis Period (Months)", [1, 3, 6, 12], index=2)
    
    # Filter data with validation
    filtered_df = df[
        (df["Company"].isin(selected_companies)) &
        (df["Product_Category"].isin(selected_categories)) &
        (df["Governorate"].isin(selected_governorates)) &
        (df["ROI"] >= min_roi) &
        (df["Strategic_Score"] >= min_strategic_score)
    ].copy()
    
    # Validate filtered data
    if len(filtered_df) == 0:
        st.error("⚠️ No data matches your current filter criteria. Please adjust your filters.")
        st.stop()
    
    # Scale data by analysis period
    scaling_factor = analysis_months
    financial_columns = ["Total_Movement_Cost_EGP", "Campaign_Investment_EGP", "Total_Investment_EGP", 
                        "Monthly_Revenue_EGP", "Monthly_Gross_Profit_EGP", "Net_Profit_EGP"]
    for col in financial_columns:
        if col in filtered_df.columns:
            filtered_df[col] = filtered_df[col] * scaling_factor
    
    # === STRATEGIC DASHBOARD ===
    
    # Executive Summary KPIs
    st.markdown("## 📈 Executive Strategic Dashboard")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_investment = filtered_df["Total_Investment_EGP"].sum()
        st.markdown(f"""
        <div class="strategic-kpi">
            <h3>Total Investment</h3>
            <h2>{total_investment:,.0f} EGP</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_revenue = filtered_df["Monthly_Revenue_EGP"].sum()
        st.markdown(f"""
        <div class="strategic-kpi">
            <h3>Total Revenue</h3>
            <h2>{total_revenue:,.0f} EGP</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_roi = filtered_df["ROI"].mean()
        st.markdown(f"""
        <div class="strategic-kpi">
            <h3>Average ROI</h3>
            <h2>{avg_roi:.1%}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_strategic_score = filtered_df["Strategic_Score"].mean()
        st.markdown(f"""
        <div class="strategic-kpi">
            <h3>Strategic Score</h3>
            <h2>{avg_strategic_score:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        market_coverage = len(filtered_df["Governorate"].unique())
        st.markdown(f"""
        <div class="strategic-kpi">
            <h3>Market Coverage</h3>
            <h2>{market_coverage} Markets</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Strategic Analysis Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Strategic Overview", "🚀 Expansion Analysis", "📢 Campaign Effectiveness", 
        "💰 Financial Performance", "🗺️ Geographic Intelligence"
    ])
    
    with tab1:
        st.markdown("### Strategic Performance Matrix")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # ROI vs Strategic Score scatter
            fig1 = px.scatter(
                filtered_df, 
                x="Strategic_Score", 
                y="ROI",
                size="Total_Investment_EGP",
                color="Product_Category",
                hover_data=["Company", "Governorate"],
                title="Strategic Score vs ROI Performance"
            )
            fig1.add_hline(y=avg_roi, line_dash="dash", line_color="red", 
                          annotation_text=f"Avg ROI: {avg_roi:.1%}")
            fig1.add_vline(x=avg_strategic_score, line_dash="dash", line_color="red",
                          annotation_text=f"Avg Strategic Score: {avg_strategic_score:.2f}")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Investment Efficiency
            efficiency_df = filtered_df.groupby("Company").agg({
                "Total_Investment_EGP": "sum",
                "Net_Profit_EGP": "sum",
                "Strategic_Score": "mean"
            }).reset_index()
            efficiency_df["Investment_Efficiency"] = efficiency_df["Net_Profit_EGP"] / efficiency_df["Total_Investment_EGP"]
            
            fig2 = px.bar(
                efficiency_df.sort_values("Investment_Efficiency", ascending=False),
                x="Company",
                y="Investment_Efficiency",
                color="Strategic_Score",
                title="Investment Efficiency by Company"
            )
            fig2.update_xaxes(tickangle=45)
            st.plotly_chart(fig2, use_container_width=True)
        
        # Strategic Recommendations
        st.markdown("### 💡 Strategic Recommendations")
        
        top_performers = filtered_df.nlargest(5, "Strategic_Score")[["Company", "Product_Category", "Governorate", "Strategic_Score", "ROI"]]
        bottom_performers = filtered_df.nsmallest(5, "Strategic_Score")[["Company", "Product_Category", "Governorate", "Strategic_Score", "ROI"]]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏆 Top Strategic Performers")
            st.dataframe(top_performers, use_container_width=True)
        
        with col2:
            st.markdown("#### ⚠️ Areas Requiring Attention")
            st.dataframe(bottom_performers, use_container_width=True)
    
    with tab2:
        st.markdown("### 🚀 Market Expansion Analysis")
        
        expansion_df = calculate_expansion_recommendations(filtered_df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Expansion Priority Matrix
            fig3 = px.scatter(
                expansion_df,
                x="Market_Penetration",
                y="Expansion_Opportunity",
                size="Net_Profit_EGP",
                color="Expansion_Priority",
                hover_data=["Governorate", "Product_Category"],
                title="Market Expansion Priority Matrix"
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Top Expansion Opportunities
            top_expansion = expansion_df.head(10)
            fig4 = px.bar(
                top_expansion,
                x="Expansion_Priority",
                y="Governorate",
                color="Product_Category",
                orientation="h",
                title="Top 10 Expansion Opportunities"
            )
            st.plotly_chart(fig4, use_container_width=True)
        
        # Expansion Investment Recommendations
        st.markdown("#### 💰 Recommended Expansion Investments")
        
        expansion_budget = st.number_input("Available Expansion Budget (EGP)", min_value=100000, value=5000000, step=100000)
        
        # Calculate recommended investments
        total_priority_score = expansion_df["Expansion_Priority"].sum()
        expansion_df["Recommended_Investment"] = (expansion_df["Expansion_Priority"] / total_priority_score) * expansion_budget
        expansion_df["Expected_ROI"] = expansion_df["ROI"] * (expansion_df["Recommended_Investment"] / expansion_df["Total_Investment_EGP"])
        
        investment_recommendations = expansion_df[["Governorate", "Product_Category", "Expansion_Priority", 
                                                 "Recommended_Investment", "Expected_ROI"]].head(10)
        
        st.dataframe(investment_recommendations, use_container_width=True)
    
    with tab3:
        st.markdown("### 📢 Campaign Effectiveness Analysis")
        
        campaign_analysis = campaign_effectiveness_analysis(filtered_df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Campaign ROI Comparison
            fig5 = px.bar(
                campaign_analysis,
                x="Campaign_Type",
                y="ROI_Mean",
                error_y="ROI_Std",
                color="Strategic_Score",
                title="Campaign ROI Performance"
            )
            fig5.update_xaxes(tickangle=45)
            st.plotly_chart(fig5, use_container_width=True)
        
        with col2:
            # LTV/CAC Analysis
            fig6 = px.scatter(
                campaign_analysis,
                x="Avg_CAC",
                y="Avg_CLV",
                size="Avg_Conversion",
                color="Campaign_Type",
                title="Customer Acquisition vs Lifetime Value"
            )
            # Add LTV/CAC = 3 line (minimum viable ratio)
            max_cac = campaign_analysis["Avg_CAC"].max()
            fig6.add_trace(go.Scatter(x=[0, max_cac], y=[0, max_cac*3], 
                                    mode="lines", name="LTV/CAC = 3:1", line=dict(dash="dash")))
            st.plotly_chart(fig6, use_container_width=True)
        
        # Campaign Optimization Recommendations
        st.markdown("#### 🎯 Campaign Optimization Matrix")
        
        # Create campaign performance matrix
        campaign_matrix = filtered_df.groupby(["Campaign_Type", "Product_Category"]).agg({
            "ROI": "mean",
            "Conversion_Rate": "mean",
            "Strategic_Score": "mean",
            "Total_Investment_EGP": "sum"
        }).reset_index()
        
        # Create pivot table for heatmap
        roi_pivot = campaign_matrix.pivot(index="Product_Category", columns="Campaign_Type", values="ROI")
        
        fig7 = px.imshow(
            roi_pivot,
            title="ROI Heatmap: Product Category vs Campaign Type",
            color_continuous_scale="RdYlGn",
            aspect="auto"
        )
        st.plotly_chart(fig7, use_container_width=True)
    
    with tab4:
        st.markdown("### 💰 Financial Performance Deep Dive")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Movement Cost vs Revenue Analysis
            if len(filtered_df) > 0:
                fig8 = px.scatter(
                    filtered_df,
                    x="Total_Movement_Cost_EGP",
                    y="Monthly_Revenue_EGP",
                    color="Company_Category",
                    size="Strategic_Score",
                    title="Movement Cost vs Revenue Relationship"
                )
                
                # Add trendline only if we have sufficient data
                if len(filtered_df) > 5:
                    try:
                        # Remove any NaN or infinite values
                        clean_df = filtered_df.dropna(subset=["Total_Movement_Cost_EGP", "Monthly_Revenue_EGP"])
                        clean_df = clean_df[np.isfinite(clean_df["Total_Movement_Cost_EGP"]) & 
                                          np.isfinite(clean_df["Monthly_Revenue_EGP"])]
                        
                        if len(clean_df) > 5:
                            coeffs = np.polyfit(clean_df["Total_Movement_Cost_EGP"], 
                                               clean_df["Monthly_Revenue_EGP"], 1)
                            trendline_y = np.poly1d(coeffs)(clean_df["Total_Movement_Cost_EGP"])
                            
                            fig8.add_trace(go.Scatter(
                                x=clean_df["Total_Movement_Cost_EGP"],
                                y=trendline_y,
                                mode="lines",
                                name="Trend Line",
                                line=dict(color="red", dash="dash")
                            ))
                    except Exception as e:
                        st.warning(f"Could not generate trendline: {str(e)}")
                
                st.plotly_chart(fig8, use_container_width=True)
            else:
                st.warning("No data available for the selected filters.")
        
        with col2:
            # Profit Margin Analysis
            margin_analysis = filtered_df.groupby("Product_Category").agg({
                "Gross_Profit_Margin": "mean",
                "Monthly_Gross_Profit_EGP": "sum",
                "Net_Profit_EGP": "sum"
            }).reset_index()
            
            fig9 = px.bar(
                margin_analysis,
                x="Product_Category",
                y="Gross_Profit_Margin",
                color="Net_Profit_EGP",
                title="Profit Margins by Product Category"
            )
            fig9.update_xaxes(tickangle=45)
            st.plotly_chart(fig9, use_container_width=True)
        
        # Financial Summary Table
        st.markdown("#### 📊 Financial Performance Summary")
        
        financial_summary = filtered_df.groupby("Company").agg({
            "Total_Investment_EGP": "sum",
            "Monthly_Revenue_EGP": "sum",
            "Monthly_Gross_Profit_EGP": "sum",
            "Net_Profit_EGP": "sum",
            "ROI": "mean",
            "Strategic_Score": "mean"
        }).round(2)
        
        financial_summary["Revenue_Growth_Potential"] = financial_summary["Monthly_Revenue_EGP"] * (1 + financial_summary["Strategic_Score"]/10)
        financial_summary = financial_summary.sort_values("Net_Profit_EGP", ascending=False)
        
        st.dataframe(financial_summary, use_container_width=True)
    
    with tab5:
        st.markdown("### 🗺️ Geographic Intelligence")
        
        # Geographic Performance Analysis
        geo_analysis = filtered_df.groupby("Governorate").agg({
            "Total_Investment_EGP": "sum",
            "Monthly_Revenue_EGP": "sum",
            "Net_Profit_EGP": "sum",
            "Market_Penetration": "mean",
            "Strategic_Score": "mean",
            "Company": "nunique"
        }).reset_index()
        
        geo_analysis["Revenue_per_Investment"] = geo_analysis["Monthly_Revenue_EGP"] / geo_analysis["Total_Investment_EGP"]
        geo_analysis = geo_analysis.sort_values("Strategic_Score", ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Geographic Revenue Distribution
            fig10 = px.pie(
                geo_analysis,
                values="Monthly_Revenue_EGP",
                names="Governorate",
                title="Revenue Distribution by Governorate"
            )
            st.plotly_chart(fig10, use_container_width=True)
        
        with col2:
            # Market Penetration vs Performance
            fig11 = px.scatter(
                geo_analysis,
                x="Market_Penetration",
                y="Strategic_Score",
                size="Monthly_Revenue_EGP",
                color="Net_Profit_EGP",
                hover_data=["Governorate"],
                title="Market Penetration vs Strategic Performance"
            )
            st.plotly_chart(fig11, use_container_width=True)
        
        # Geographic Expansion Strategy
        st.markdown("#### 🎯 Geographic Expansion Strategy")
        
        st.dataframe(geo_analysis, use_container_width=True)
        
        # Market Priority Recommendations
        high_potential = geo_analysis[
            (geo_analysis["Market_Penetration"] < 0.1) & 
            (geo_analysis["Strategic_Score"] > geo_analysis["Strategic_Score"].median())
        ]
        
        if not high_potential.empty:
            st.markdown("##### 🚀 High Potential, Low Penetration Markets:")
            st.dataframe(high_potential[["Governorate", "Market_Penetration", "Strategic_Score", "Revenue_per_Investment"]], use_container_width=True)
    
    # === ADVANCED ANALYTICS SECTION ===
    st.markdown("---")
    st.markdown("## 🔬 Advanced Strategic Analytics")
    
    # Advanced Analytics Tabs
    adv_tab1, adv_tab2, adv_tab3 = st.tabs([
        "🤖 Predictive Modeling", "🎯 Resource Optimization", "📊 Competitive Intelligence"
    ])
    
    with adv_tab1:
        st.markdown("### 🔮 Predictive Performance Models")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue Prediction Model
            st.markdown("#### Revenue Forecasting")
            
            # Simple linear regression for demonstration
            from sklearn.linear_model import LinearRegression
            import warnings
            warnings.filterwarnings('ignore')
            
            # Prepare features for prediction
            feature_columns = ["Total_Investment_EGP", "Market_Penetration", "Strategic_Score"]
            
            # Clean data for modeling
            model_df = filtered_df[feature_columns + ["Monthly_Revenue_EGP"]].dropna()
            
            if len(model_df) > 10:  # Ensure sufficient data
                try:
                    X = model_df[feature_columns]
                    y = model_df["Monthly_Revenue_EGP"]
                    
                    model = LinearRegression()
                    model.fit(X, y)
                    
                    # Predict next period
                    predictions = model.predict(X)
                    model_df = model_df.copy()
                    model_df["Predicted_Revenue"] = predictions
                    model_df["Revenue_Variance"] = model_df["Monthly_Revenue_EGP"] - predictions
                    
                    # Plot actual vs predicted
                    fig12 = px.scatter(
                        model_df,
                        x="Monthly_Revenue_EGP",
                        y="Predicted_Revenue",
                        title="Actual vs Predicted Revenue"
                    )
                    # Add perfect prediction line
                    max_revenue = max(model_df["Monthly_Revenue_EGP"].max(), model_df["Predicted_Revenue"].max())
                    min_revenue = min(model_df["Monthly_Revenue_EGP"].min(), model_df["Predicted_Revenue"].min())
                    fig12.add_trace(go.Scatter(x=[min_revenue, max_revenue], y=[min_revenue, max_revenue], 
                                             mode="lines", name="Perfect Prediction", line=dict(dash="dash", color="red")))
                    st.plotly_chart(fig12, use_container_width=True)
                    
                    # Model performance metrics
                    from sklearn.metrics import r2_score, mean_absolute_error
                    r2 = r2_score(y, predictions)
                    mae = mean_absolute_error(y, predictions)
                    
                    st.metric("Model R² Score", f"{r2:.3f}")
                    st.metric("Mean Absolute Error", f"{mae:,.0f} EGP")
                    
                except Exception as e:
                    st.error(f"Could not build prediction model: {str(e)}")
                    st.info("Try adjusting your filters to include more data points.")
            else:
                st.warning("Insufficient data for predictive modeling. Please adjust filters to include more records.")
        
        with col2:
            # Strategic Score Prediction
            st.markdown("#### Strategic Performance Forecasting")
            
            # Scenario Analysis
            st.markdown("##### Scenario Planning")
            
            scenario = st.selectbox("Select Scenario", [
                "Conservative Growth (+5%)",
                "Moderate Growth (+15%)",
                "Aggressive Growth (+30%)",
                "Market Expansion (+50%)"
            ])
            
            growth_rates = {
                "Conservative Growth (+5%)": 1.05,
                "Moderate Growth (+15%)": 1.15,
                "Aggressive Growth (+30%)": 1.30,
                "Market Expansion (+50%)": 1.50
            }
            
            growth_factor = growth_rates[scenario]
            
            # Apply scenario to key metrics
            scenario_df = filtered_df.copy()
            scenario_df["Scenario_Investment"] = scenario_df["Total_Investment_EGP"] * growth_factor
            scenario_df["Scenario_Revenue"] = scenario_df["Monthly_Revenue_EGP"] * (growth_factor ** 0.8)  # Revenue grows slower than investment
            scenario_df["Scenario_ROI"] = (scenario_df["Scenario_Revenue"] - scenario_df["Scenario_Investment"]) / scenario_df["Scenario_Investment"]
            
            # Scenario comparison chart
            scenario_summary = pd.DataFrame({
                "Metric": ["Total Investment", "Total Revenue", "Average ROI"],
                "Current": [
                    filtered_df["Total_Investment_EGP"].sum(),
                    filtered_df["Monthly_Revenue_EGP"].sum(),
                    filtered_df["ROI"].mean()
                ],
                "Scenario": [
                    scenario_df["Scenario_Investment"].sum(),
                    scenario_df["Scenario_Revenue"].sum(),
                    scenario_df["Scenario_ROI"].mean()
                ]
            })
            
            fig13 = px.bar(
                scenario_summary.melt(id_vars="Metric", var_name="Period", value_name="Value"),
                x="Metric",
                y="Value",
                color="Period",
                barmode="group",
                title=f"Current vs {scenario}"
            )
            st.plotly_chart(fig13, use_container_width=True)
    
    with adv_tab2:
        st.markdown("### ⚡ Resource Optimization Engine")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Investment Allocation Optimizer")
            
            # Budget allocation optimization
            total_budget = st.number_input("Total Available Budget (EGP)", min_value=500000, value=10000000, step=500000)
            
            # Calculate optimal allocation based on strategic score and ROI
            optimization_df = filtered_df.groupby(["Product_Category", "Governorate"]).agg({
                "Strategic_Score": "mean",
                "ROI": "mean",
                "Total_Investment_EGP": "mean"
            }).reset_index()
            
            # Optimization score (combination of strategic score and ROI)
            optimization_df["Optimization_Score"] = (
                optimization_df["Strategic_Score"] * 0.6 + 
                optimization_df["ROI"] * 0.4
            )
            
            # Allocate budget proportionally to optimization scores
            total_opt_score = optimization_df["Optimization_Score"].sum()
            optimization_df["Recommended_Budget"] = (optimization_df["Optimization_Score"] / total_opt_score) * total_budget
            optimization_df["Budget_Efficiency"] = optimization_df["Recommended_Budget"] / optimization_df["Total_Investment_EGP"]
            
            # Top 10 recommended allocations
            top_allocations = optimization_df.nlargest(10, "Recommended_Budget")
            
            fig14 = px.treemap(
                top_allocations,
                path=["Product_Category", "Governorate"],
                values="Recommended_Budget",
                color="Optimization_Score",
                title="Optimal Budget Allocation"
            )
            st.plotly_chart(fig14, use_container_width=True)
        
        with col2:
            st.markdown("#### Campaign Resource Optimization")
            
            # Campaign budget optimization
            campaign_budget = st.number_input("Campaign Budget (EGP)", min_value=100000, value=2000000, step=100000)
            
            campaign_opt = filtered_df.groupby("Campaign_Type").agg({
                "ROI": "mean",
                "Conversion_Rate": "mean",
                "Strategic_Score": "mean",
                "Campaign_Investment_EGP": "mean"
            }).reset_index()
            
            # Campaign efficiency score
            campaign_opt["Campaign_Efficiency"] = (
                campaign_opt["ROI"] * 0.4 +
                campaign_opt["Conversion_Rate"] * 0.3 +
                campaign_opt["Strategic_Score"] * 0.3
            )
            
            total_campaign_efficiency = campaign_opt["Campaign_Efficiency"].sum()
            campaign_opt["Recommended_Campaign_Budget"] = (campaign_opt["Campaign_Efficiency"] / total_campaign_efficiency) * campaign_budget
            
            fig15 = px.pie(
                campaign_opt,
                values="Recommended_Campaign_Budget",
                names="Campaign_Type",
                title="Optimal Campaign Budget Distribution"
            )
            st.plotly_chart(fig15, use_container_width=True)
            
            st.dataframe(campaign_opt[["Campaign_Type", "Campaign_Efficiency", "Recommended_Campaign_Budget"]], use_container_width=True)
    
    with adv_tab3:
        st.markdown("### 🏆 Competitive Intelligence Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Market Share Analysis")
            
            # Company market share and performance
            competitive_analysis = filtered_df.groupby("Company").agg({
                "Market_Share": "first",
                "Monthly_Revenue_EGP": "sum",
                "Strategic_Score": "mean",
                "ROI": "mean",
                "Total_Investment_EGP": "sum"
            }).reset_index()
            
            competitive_analysis["Revenue_Market_Share"] = competitive_analysis["Monthly_Revenue_EGP"] / competitive_analysis["Monthly_Revenue_EGP"].sum()
            competitive_analysis["Efficiency_Ratio"] = competitive_analysis["Revenue_Market_Share"] / competitive_analysis["Market_Share"]
            
            fig16 = px.scatter(
                competitive_analysis,
                x="Market_Share",
                y="Revenue_Market_Share",
                size="Strategic_Score",
                color="ROI",
                hover_data=["Company"],
                title="Market Share vs Revenue Share"
            )
            # Add diagonal line for perfect correlation
            fig16.add_trace(go.Scatter(x=[0, 0.2], y=[0, 0.2], 
                                     mode="lines", name="Perfect Correlation", line=dict(dash="dash")))
            st.plotly_chart(fig16, use_container_width=True)
        
        with col2:
            st.markdown("#### Competitive Positioning Matrix")
            
            # BCG-style matrix: Strategic Score vs Market Share
            fig17 = px.scatter(
                competitive_analysis,
                x="Strategic_Score",
                y="Market_Share",
                size="Monthly_Revenue_EGP",
                color="Company",
                title="Strategic Position Matrix"
            )
            
            # Add quadrant lines
            avg_strategic = competitive_analysis["Strategic_Score"].mean()
            avg_market_share = competitive_analysis["Market_Share"].mean()
            
            fig17.add_hline(y=avg_market_share, line_dash="dash", line_color="gray")
            fig17.add_vline(x=avg_strategic, line_dash="dash", line_color="gray")
            
            # Add quadrant labels
            fig17.add_annotation(x=avg_strategic*1.2, y=avg_market_share*1.2, text="Stars", showarrow=False)
            fig17.add_annotation(x=avg_strategic*0.8, y=avg_market_share*1.2, text="Question Marks", showarrow=False)
            fig17.add_annotation(x=avg_strategic*1.2, y=avg_market_share*0.8, text="Cash Cows", showarrow=False)
            fig17.add_annotation(x=avg_strategic*0.8, y=avg_market_share*0.8, text="Dogs", showarrow=False)
            
            st.plotly_chart(fig17, use_container_width=True)
        
        # Competitive Intelligence Summary
        st.markdown("#### 📈 Competitive Intelligence Summary")
        
        # Identify competitive advantages and threats
        competitive_summary = competitive_analysis.sort_values("Efficiency_Ratio", ascending=False)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("##### 🥇 Market Leaders")
            leaders = competitive_summary.head(3)[["Company", "Market_Share", "Strategic_Score"]]
            st.dataframe(leaders, use_container_width=True)
        
        with col2:
            st.markdown("##### 🚀 High Efficiency Players")
            efficient = competitive_summary.nlargest(3, "Efficiency_Ratio")[["Company", "Efficiency_Ratio", "ROI"]]
            st.dataframe(efficient, use_container_width=True)
        
        with col3:
            st.markdown("##### ⚠️ Underperformers")
            underperformers = competitive_summary.tail(3)[["Company", "Strategic_Score", "ROI"]]
            st.dataframe(underperformers, use_container_width=True)
    
    # === STRATEGIC RECOMMENDATIONS ENGINE ===
    st.markdown("---")
    st.markdown("## 🎯 Strategic Recommendations Engine")
    
    rec_col1, rec_col2 = st.columns(2)
    
    with rec_col1:
        st.markdown("### 💡 Immediate Action Items")
        
        # Generate actionable recommendations
        recommendations = []
        
        try:
            # ROI-based recommendations
            low_roi = filtered_df[filtered_df["ROI"] < 0.1]
            if not low_roi.empty:
                recommendations.append({
                    "Priority": "High",
                    "Category": "Performance",
                    "Action": f"Review {len(low_roi)} underperforming operations with ROI < 10%",
                    "Impact": "Cost Optimization"
                })
            
            # High potential markets
            strategic_threshold = filtered_df["Strategic_Score"].quantile(0.75) if len(filtered_df) > 4 else filtered_df["Strategic_Score"].mean()
            high_potential = filtered_df[
                (filtered_df["Strategic_Score"] > strategic_threshold) &
                (filtered_df["Market_Penetration"] < 0.1)
            ]
            if not high_potential.empty:
                recommendations.append({
                    "Priority": "Medium",
                    "Category": "Expansion",
                    "Action": f"Invest in {len(high_potential)} high-potential, low-penetration markets",
                    "Impact": "Revenue Growth"
                })
            
            # Campaign optimization
            if not campaign_analysis.empty and len(campaign_analysis) > 0:
                best_campaign = campaign_analysis.loc[campaign_analysis["ROI_Mean"].idxmax(), "Campaign_Type"]
                recommendations.append({
                    "Priority": "Medium",
                    "Category": "Marketing",
                    "Action": f"Reallocate budget towards {best_campaign} campaigns",
                    "Impact": "Marketing Efficiency"
                })
            
            # Geographic focus
            if not geo_analysis.empty and len(geo_analysis) > 0:
                top_geo = geo_analysis.loc[geo_analysis["Revenue_per_Investment"].idxmax(), "Governorate"]
                recommendations.append({
                    "Priority": "Low",
                    "Category": "Geographic",
                    "Action": f"Strengthen presence in {top_geo} - highest revenue per investment",
                    "Impact": "Market Dominance"
                })
            
            # If no specific recommendations, add general ones
            if not recommendations:
                recommendations.append({
                    "Priority": "Medium",
                    "Category": "General",
                    "Action": "Continue monitoring current performance metrics",
                    "Impact": "Maintain Performance"
                })
        
        except Exception as e:
            st.warning(f"Could not generate some recommendations: {str(e)}")
            recommendations.append({
                "Priority": "High",
                "Category": "Data Quality",
                "Action": "Review data quality and filter settings",
                "Impact": "Improved Analytics"
            })
        
        rec_df = pd.DataFrame(recommendations)
        st.dataframe(rec_df, use_container_width=True)
    
    with rec_col2:
        st.markdown("### 📊 Strategic Metrics Dashboard")
        
        # Key strategic metrics
        strategic_metrics = {
            "Market Efficiency Score": filtered_df["Strategic_Score"].mean(),
            "Investment ROI": filtered_df["ROI"].mean(),
            "Market Coverage": len(filtered_df["Governorate"].unique()) / len(df["Governorate"].unique()),
            "Campaign Diversity": len(filtered_df["Campaign_Type"].unique()),
            "Product Portfolio Balance": 1 - (filtered_df.groupby("Product_Category")["Monthly_Revenue_EGP"].sum().std() / filtered_df.groupby("Product_Category")["Monthly_Revenue_EGP"].sum().mean()),
            "Geographic Concentration": 1 - (filtered_df.groupby("Governorate")["Monthly_Revenue_EGP"].sum().std() / filtered_df.groupby("Governorate")["Monthly_Revenue_EGP"].sum().mean())
        }
        
        metrics_df = pd.DataFrame(list(strategic_metrics.items()), columns=["Metric", "Score"])
        metrics_df["Score"] = metrics_df["Score"].round(3)
        metrics_df["Performance"] = metrics_df["Score"].apply(
            lambda x: "Excellent" if x > 0.8 else "Good" if x > 0.6 else "Average" if x > 0.4 else "Poor"
        )
        
        fig18 = px.bar(
            metrics_df,
            x="Score",
            y="Metric",
            color="Performance",
            orientation="h",
            title="Strategic Performance Scorecard"
        )
        st.plotly_chart(fig18, use_container_width=True)
    
    # === DATA EXPORT AND REPORTING ===
    st.markdown("---")
    st.markdown("## 📥 Strategic Reports & Data Export")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        # Executive Summary Report
        if st.button("📊 Generate Executive Summary"):
            executive_summary = {
                "Analysis_Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Total_Investment": filtered_df["Total_Investment_EGP"].sum(),
                "Total_Revenue": filtered_df["Monthly_Revenue_EGP"].sum(),
                "Overall_ROI": filtered_df["ROI"].mean(),
                "Strategic_Score": filtered_df["Strategic_Score"].mean(),
                "Markets_Covered": len(filtered_df["Governorate"].unique()),
                "Companies_Analyzed": len(filtered_df["Company"].unique()),
                "Top_Performing_Product": filtered_df.groupby("Product_Category")["ROI"].mean().idxmax(),
                "Best_Market": filtered_df.groupby("Governorate")["Strategic_Score"].mean().idxmax(),
                "Recommended_Action": recommendations[0]["Action"] if recommendations else "Continue monitoring"
            }
            
            summary_df = pd.DataFrame([executive_summary])
            csv_summary = summary_df.to_csv(index=False)
            st.download_button(
                label="📄 Download Executive Summary",
                data=csv_summary,
                file_name=f"executive_summary_{datetime.date.today()}.csv",
                mime="text/csv"
            )
    
    with export_col2:
        # Detailed Analytics Export
        if st.button("📈 Export Detailed Analytics"):
            detailed_export = filtered_df[[
                "Company", "Governorate", "Product_Category", "Campaign_Type",
                "Total_Investment_EGP", "Monthly_Revenue_EGP", "Net_Profit_EGP",
                "ROI", "Strategic_Score", "Market_Penetration", "Expansion_Opportunity"
            ]]
            
            csv_detailed = detailed_export.to_csv(index=False)
            st.download_button(
                label="📊 Download Detailed Data",
                data=csv_detailed,
                file_name=f"strategic_analytics_{datetime.date.today()}.csv",
                mime="text/csv"
            )
    
    with export_col3:
        # Strategic Recommendations Export
        if st.button("🎯 Export Recommendations"):
            if recommendations:
                rec_export = pd.DataFrame(recommendations)
                csv_recommendations = rec_export.to_csv(index=False)
                st.download_button(
                    label="💡 Download Recommendations",
                    data=csv_recommendations,
                    file_name=f"strategic_recommendations_{datetime.date.today()}.csv",
                    mime="text/csv"
                )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 20px;">
        <h4>🏥 Strategic Pharmaceutical Business Intelligence Platform</h4>
        <p>Comprehensive Analysis of Movement Costs, Sales Performance, Market Expansion & Campaign Effectiveness</p>
        <p style="direction: rtl;">منصة الذكاء التجاري الاستراتيجي للصناعات الدوائية - تحليل شامل لتكلفة الحركة والأداء والتوسع</p>
        <p><strong>Powered by Advanced Analytics & Strategic Intelligence</strong></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()