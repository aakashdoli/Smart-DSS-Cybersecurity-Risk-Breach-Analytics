import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Smart DSS – Cyber Risk in Port Vendor Management", layout="wide")
st.title("🔐 Smart DSS – Cybersecurity Risk & Breach Analytics")

# Tabs: Upload CSV | Manual Input
tab1, tab2 = st.tabs(["📂 Upload Breach Dataset", "✍️ Manual Risk Calculator"])

# ==============================
# 📂 TAB 1: Upload Dataset Mode
# ==============================
with tab1:
    uploaded_file = st.file_uploader("Upload your breach dataset (CSV)", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        st.subheader("📊 Raw Data")
        st.dataframe(df)

        # Ensure Records column is numeric
        df['Records'] = pd.to_numeric(df['Records'], errors='coerce')

        # Top 10 breaches
        top_breaches = df.sort_values(by='Records', ascending=False).head(10)
        st.subheader("🔥 Top 10 Largest Breaches")
        st.dataframe(top_breaches[['Entity', 'Year', 'Records', 'Method', 'Organization type']])

        # Pie chart: Method distribution
        method_counts = df['Method'].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(method_counts, labels=method_counts.index, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        st.subheader("🔍 Breach Methods Distribution")
        st.pyplot(fig1)

        # Bar chart: breaches per year
        if 'Year' in df.columns:
            records_by_year = df.groupby('Year')['Records'].sum().sort_index()
            fig2, ax2 = plt.subplots()
            records_by_year.plot(kind='bar', ax=ax2, color='skyblue')
            ax2.set_title("📈 Records Breached by Year")
            ax2.set_xlabel("Year")
            ax2.set_ylabel("Records Breached")
            st.pyplot(fig2)

        # Risk scoring logic
        def compute_risk_score(row):
            score = 0
            if row['Records'] > 1_000_000:
                score += 0.5
            elif row['Records'] > 100_000:
                score += 0.3
            elif row['Records'] > 10_000:
                score += 0.2
            else:
                score += 0.1

            method = str(row['Method']).lower()
            if 'hacked' in method or 'unauthorized' in method:
                score += 0.4
            elif 'poor security' in method or 'accidentally published' in method:
                score += 0.3
            else:
                score += 0.1

            try:
                if int(row['Year']) >= 2020:
                    score += 0.1
            except:
                pass

            return round(score, 2)

        def assign_risk_category(score):
            if score >= 0.7:
                return 'Critical'
            elif score >= 0.4:
                return 'Moderate'
            else:
                return 'Low'

        def mitigation_recommendation(row):
            if row['risk_category'] == 'Critical':
                return "🚨 Block access to core systems; re-evaluate"
            elif row['risk_category'] == 'Moderate':
                return "⚠️ Increase audit frequency; train vendor"
            else:
                return "✅ Maintain SLA; periodic monitoring"

        # Apply logic
        df['risk_score'] = df.apply(compute_risk_score, axis=1)
        df['risk_category'] = df['risk_score'].apply(assign_risk_category)
        df['mitigation_action'] = df.apply(mitigation_recommendation, axis=1)

        # Results
        st.subheader("🚦 Vendor Risk Classification")
        st.dataframe(df[['Entity', 'risk_score', 'risk_category']])

        st.subheader("🛡️ Vendor Risk Mitigation Recommendations")
        st.dataframe(df[['Entity', 'risk_category', 'mitigation_action']])

        st.subheader("📊 Risk Category Distribution")
        risk_counts = df['risk_category'].value_counts()
        st.bar_chart(risk_counts)
    else:
        st.warning("Please upload a CSV file with at least 'Entity', 'Records', 'Method', and 'Year' columns.")
import io
import pandas as pd
import streamlit as st

# ==============================
# ✍️ TAB 2: Manual Risk Calculator
# ==============================
with tab2:
    st.markdown("Enter multiple vendors below to calculate risk and generate a report.")

    if "vendor_entries" not in st.session_state:
        st.session_state.vendor_entries = []

    with st.form("add_vendor_form", clear_on_submit=True):
        vendor_name = st.text_input("Vendor Name", placeholder="e.g. SafeMarine")
        compliance_score = st.slider("Compliance Score (0 to 1)", 0.0, 1.0, 0.5, 0.05)
        num_incidents = st.number_input("Number of Incidents", min_value=0, step=1)
        critical_assets = st.number_input("Critical Assets Linked", min_value=0, step=1)
        add_vendor = st.form_submit_button("➕ Add Vendor")

    def compute_vendor_risk(vendor_name, compliance_score, num_incidents, critical_assets):
        score = 0
        score += 0.4 if compliance_score < 0.5 else 0.3 if compliance_score < 0.7 else 0.1
        score += 0.4 if num_incidents >= 3 else 0.3 if num_incidents == 2 else 0.2 if num_incidents == 1 else 0
        score += 0.3 if critical_assets >= 5 else 0.2 if critical_assets >= 3 else 0.1 if critical_assets >= 1 else 0

        risk_score = round(score, 2)
        category = "Critical" if risk_score >= 0.7 else "Moderate" if risk_score >= 0.4 else "Low"
        action = {
            "Critical": "🚨 Block access to core systems; re-evaluate",
            "Moderate": "⚠️ Increase audit frequency; train vendor",
            "Low": "✅ Maintain SLA; periodic monitoring"
        }[category]

        return {
            "Vendor Name": vendor_name,
            "Compliance Score": compliance_score,
            "Number of Incidents": num_incidents,
            "Critical Assets Linked": critical_assets,
            "Risk Score": risk_score,
            "Risk Category": category,
            "Mitigation Action": action
        }

    if add_vendor:
        if vendor_name.strip() == "":
            st.warning("Please enter a valid vendor name.")
        else:
            vendor_data = compute_vendor_risk(vendor_name, compliance_score, num_incidents, critical_assets)
            st.session_state.vendor_entries.append(vendor_data)
            st.success(f"Added vendor: {vendor_name}")

    if st.session_state.vendor_entries:
        st.subheader("📋 Current Vendor Risk Entries")
        vendor_df = pd.DataFrame(st.session_state.vendor_entries)
        st.dataframe(vendor_df)

        # Download button
        csv = vendor_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download All Vendor Risk Reports",
            data=csv,
            file_name="all_vendors_risk_report.csv",
            mime="text/csv"
        )
