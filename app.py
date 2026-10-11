import streamlit as st
import pandas as pd
import plotly.express as px

# Configure the Streamlit page
st.set_page_config(page_title="Doctor Business Dashboard", layout="wide")

st.title("📊 Doctor Average Business Dashboard")

# --- FILE UPLOAD COMPONENT ---
uploaded_file = st.file_uploader("Upload your Excel Data File to begin", type=["xlsx", "xls"])

@st.cache_data
def process_data(file):
    # Read the uploaded Excel file directly from memory
    df = pd.read_excel(file) 
    
    # --- Robust Data Cleaning ---
    # 1. Convert everything to string to safely remove commas
    df['Average Business'] = df['Average Business'].astype(str).str.replace(',', '', regex=False)
    
    # 2. Force conversion to numeric, turn invalid parsing into NaN, then fill NaNs with 0
    df['Average Business'] = pd.to_numeric(df['Average Business'], errors='coerce').fillna(0)
    
    # Define custom binning logic
    def categorize_business(val):
        if val == 0:
            return "0 (No Business)"
        elif 0 < val <= 500:
            return "0 to 500"
        elif 500 < val <= 1000:
            return "500 to 1000"
        elif 1000 < val <= 2500:
            return "1000 to 2500"
        elif 2500 < val <= 4999:
            return "2500 to 4999"
        else:
            return "5000+"
            
    df['Business Range'] = df['Average Business'].apply(categorize_business)
    
    # Define categorical order for consistent charting
    range_order = ["0 (No Business)", "0 to 500", "500 to 1000", "1000 to 2500", "2500 to 4999", "5000+"]
    df['Business Range'] = pd.Categorical(df['Business Range'], categories=range_order, ordered=True)
    
    return df

# --- DASHBOARD LOGIC ---
# Only run the dashboard if a file has been uploaded
if uploaded_file is not None:
    
    df = process_data(uploaded_file)
    
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Dashboard Filters")
    
    # Filter by MSR
    msr_list = df['MSR'].dropna().unique().tolist()
    selected_msr = st.sidebar.multiselect("Select MSR", msr_list, default=msr_list)
    
    # Filter by Headquarters
    hq_list = df['Headquarters'].dropna().unique().tolist()
    selected_hq = st.sidebar.multiselect("Select Headquarters", hq_list, default=hq_list)
    
    # Apply filters
    filtered_df = df[
        (df['MSR'].isin(selected_msr)) & 
        (df['Headquarters'].isin(selected_hq))
    ]
    
    # Optional text search for specific Doctor/Customer Name
    search_name = st.sidebar.text_input("Search Doctor / Customer Name")
    if search_name:
        filtered_df = filtered_df[filtered_df['Doctor / Customer Name'].str.contains(search_name, case=False, na=False)]
    
    # --- VISUALIZATION ---
    st.subheader("Distribution of Doctors by Average Business Range")
    
    if not filtered_df.empty:
        # Aggregate data for the bar chart
        chart_data = filtered_df['Business Range'].value_counts().reset_index()
        chart_data.columns = ['Business Range', 'Doctor Count']
        chart_data = chart_data.sort_values('Business Range')
        
        # Plotly Bar Chart
        fig = px.bar(
            chart_data, 
            x='Business Range', 
            y='Doctor Count',
            text='Doctor Count',
            color='Business Range',
            color_discrete_sequence=px.colors.sequential.Blues_r,
            labels={"Doctor Count": "Number of Doctors", "Business Range": "Average Business Bracket"}
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Number of Doctors")
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")
    
    # --- DATA TABLE ---
    st.subheader("Filtered Data Details")
    st.dataframe(
        filtered_df[['MSR', 'Headquarters', 'Doctor / Customer Name', 'Average Business', 'Business Range']], 
        use_container_width=True,
        hide_index=True
    )

else:
    # Message shown when no file is uploaded yet
    st.info("👆 Please upload your Excel data file using the uploader above to view the dashboard.")