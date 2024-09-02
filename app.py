import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
import json
import re

# Configure the Generative AI API key
genai.configure(api_key=os.environ["API"])

# Function to get data from the Gemini model
def get_gemini_data(soft_drink):
    # Define the prompt for the model based on the user's input
    prompt = f"""
    Generate a JSON response containing the ingredients and associated health risks for the soft drink named "{soft_drink}".
    The JSON should have two main keys: 'ingredients' which lists all ingredients, and 'possible_health_risks' which is a list of objects containing 'ingredient' and 'associated_diseases' (a list of diseases that can be caused by that ingredient).
    Give response only if the input is a valid soft drink name. If the input is not a valid soft drink name, give an error messagein JSON.
    """

    # Generate content using the Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    # Extract JSON content using regex
    try:
        # Use a regex to find the JSON part in the response
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            return data
        else:
            st.error("Failed to find JSON in the response.")
            return None
    except Exception as e:
        st.error("Failed to extract and parse JSON from the Gemini API response. Please try again.")
        return None

# Streamlit app configuration
st.set_page_config(page_title="Soft Drink Health Risks", layout="wide", initial_sidebar_state="collapsed")

# Title and Input Section
st.title("🧃 Soft Drink Health Risks Analyzer")
st.subheader("Enter a soft drink name to analyze its ingredients and possible health risks.")

# Input form
with st.form(key='drink_form'):
    soft_drink = st.text_input("Enter Soft Drink Name")
    submit_button = st.form_submit_button(label='Analyze')

# API call and processing
if submit_button and soft_drink:
    data = get_gemini_data(soft_drink)
    
    if data:
        ingredients = data.get("ingredients", [])
        health_risks = data.get("possible_health_risks", [])

        # Ingredients Table
        st.markdown("### 🍹 **Ingredients**")
        ingredients_df = pd.DataFrame(ingredients, columns=["Ingredients"])
        st.table(ingredients_df)

        # Health Risks Table
        st.markdown("### ⚠️ **Possible Health Risks**")
        risks_data = [{"Ingredient": risk["ingredient"], "Associated Diseases": ", ".join(risk["associated_diseases"])} for risk in health_risks]
        risks_df = pd.DataFrame(risks_data)
        st.table(risks_df)

# Style the app
st.markdown(
    """
    <style>
    .stMarkdown {
        font-size: 18px;
        font-weight: 400;
    }
    .st-title {
        color: #FFA500;
    }
    </style>
    """,
    unsafe_allow_html=True
)
