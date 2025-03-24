import streamlit as st
import pandas as pd
import numpy as np
import requests
import io

# Streamlit app setup
st.set_page_config(page_title="Player Model Score", layout="wide")
st.title("Player Model Score")

# Caching the file download and loading process
@st.cache_data
def load_data():
    # Raw URL of the file (GitHub raw URL)
    file_url = 'https://github.com/LeScott2406/Model-App/raw/refs/heads/main/value_added_model%203.xlsx'

    # Download the file content
    response = requests.get(file_url)

    # Read the file into a pandas DataFrame
    file_content = io.BytesIO(response.content)
    data = pd.read_excel(file_content)

    # Replace NaNs with 0 in the entire DataFrame
    data.fillna(0, inplace=True)
    return data

# Load the data
data = load_data()

# Ensure 'Contract Expires' is converted to datetime and extract the year
if 'Contract Expires' in data.columns:
    data['Contract Expires'] = pd.to_datetime(data['Contract Expires'], errors='coerce')
    data.dropna(subset=['Contract Expires'], inplace=True)  # Drop invalid dates
    data['Contract Year'] = data['Contract Expires'].dt.year  # Extract year

# Filters on the sidebar
st.sidebar.header('Filters')

# Position filter (multiple selection)
position_filter = st.sidebar.multiselect('Select Position', data['Position'].unique(), default=data['Position'].unique())

# Age filter (slider)
age_filter = st.sidebar.slider('Select Age Range', int(data['Age'].min()), int(data['Age'].max()), (int(data['Age'].min()), int(data['Age'].max())))

# Usage filter (slider)
usage_filter = st.sidebar.slider('Select Usage Range', 0, 90, (0, 90))

# Contract Expires filter (slider)
if 'Contract Year' in data.columns:
    contract_min = int(data['Contract Year'].min())
    contract_max = int(data['Contract Year'].max())
    contract_filter = st.sidebar.slider('Select Contract Expiry Year', contract_min, contract_max, (contract_min, contract_max))

# Tier filter (dropdown, multiple selection)
tier_filter = st.sidebar.multiselect('Select Tier', data['Tier'].unique(), default=data['Tier'].unique())

# Cascading League filter based on selected Tier
filtered_leagues = data[data['Tier'].isin(tier_filter)]['League'].unique()
league_options = ["All"] + list(filtered_leagues)

league_filter = st.sidebar.multiselect('Select League', league_options, default="All")

# Apply league filter: if "All" is selected, include all leagues
if "All" in league_filter:
    selected_leagues = filtered_leagues  # Select all leagues
else:
    selected_leagues = league_filter

# Model score filter (dropdown)
model_score_filter = st.sidebar.selectbox('Select Model Score', options=[col for col in data.columns if 'Score (0-100)' in col])

# Apply filters
filtered_data = data[
    (data['Age'] >= age_filter[0]) & (data['Age'] <= age_filter[1]) &
    (data['Usage'] >= usage_filter[0]) & (data['Usage'] <= usage_filter[1]) &
    (data['Tier'].isin(tier_filter)) &
    (data['League'].isin(selected_leagues))
]

if 'Contract Year' in data.columns:
    filtered_data = filtered_data[
        (filtered_data['Contract Year'] >= contract_filter[0]) & (filtered_data['Contract Year'] <= contract_filter[1])
    ]

if position_filter:
    filtered_data = filtered_data[filtered_data['Position'].isin(position_filter)]

# Sort by model score
filtered_data_sorted = filtered_data.sort_values(by=model_score_filter, ascending=False)

# Display results
st.dataframe(filtered_data_sorted[['Player', 'Team', 'Position', 'Age', 'Usage', 'Contract Expires', model_score_filter]])
