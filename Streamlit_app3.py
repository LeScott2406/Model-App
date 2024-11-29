#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import numpy as np
import requests
import io

# Raw URL of the file (GitHub raw URL)
file_url = 'https://raw.githubusercontent.com/LeScott2406/Model-App/main/value_added_model.xlsx'

# Download the file content
response = requests.get(file_url)

# Read the file into a pandas DataFrame
file_content = io.BytesIO(response.content)
data = pd.read_excel(file_content)

# Replace NaNs with 0 in the entire DataFrame
data.fillna(0, inplace=True)

# Streamlit app setup
st.set_page_config(page_title="Player Model Score", layout="wide")
st.title("Player Model Score")

# Filters on the sidebar
st.sidebar.header('Filters')

# Position filter (multiple selection)
position_filter = st.sidebar.multiselect('Select Position', data['Position'].unique(), default=data['Position'].unique())

# Age filter (slider)
age_filter = st.sidebar.slider('Select Age Range', int(data['Age'].min()), int(data['Age'].max()), (int(data['Age'].min()), int(data['Age'].max())))

# Usage filter (slider)
usage_filter = st.sidebar.slider('Select Usage Range', 0, 90, (0, 90))

# Tier filter (dropdown, multiple selection)
tier_filter = st.sidebar.multiselect('Select Tier', data['Tier'].unique(), default=data['Tier'].unique())

# Cascading League filter based on selected Tier
filtered_leagues = data[data['Tier'].isin(tier_filter)]['League'].unique()
league_filter = st.sidebar.multiselect('Select League', filtered_leagues, default=filtered_leagues)

# Model score filter (dropdown)
model_score_filter = st.sidebar.selectbox('Select Model Score', options=[col for col in data.columns if 'Score (0-100)' in col])

# Filter data
filtered_data = data[
    (data['Age'] >= age_filter[0]) & (data['Age'] <= age_filter[1]) &
    (data['Usage'] >= usage_filter[0]) & (data['Usage'] <= usage_filter[1]) &
    (data['Tier'].isin(tier_filter)) &
    (data['League'].isin(league_filter))
]

if position_filter:
    filtered_data = filtered_data[filtered_data['Position'].isin(position_filter)]

# Sort the filtered data based on the selected model score
filtered_data_sorted = filtered_data.sort_values(by=model_score_filter, ascending=False)

# Display the filtered table with specific columns
st.dataframe(filtered_data_sorted[['Player', 'Team', 'Position', 'Age', 'Usage', model_score_filter]])
