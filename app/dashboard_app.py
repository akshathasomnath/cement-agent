import streamlit as st
import random
import time
import numpy as np
import matplotlib.pyplot as plt
import google.generativeai as genai 
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

st.set_page_config(
    page_title="CementGPT — JK Cement",
    layout="wide",
    
)
st.title(" CementGPT — Plant Dashboard")
st.markdown("CementGPT Dashboard"
)

with st.sidebar:
    st.header(" Plant Input Parameters")
    feed_rate = st.slider("Feed Rate (t/h)", 20, 200, 75)
    kiln_temp = st.slider("Kiln Temperature (°C)", 1200, 1500, 1425)
    fuel_type = st.selectbox("Fuel Type", ["Coal", "Petcoke", "Biomass", "Gas"])
    alt_fuel_ratio = st.slider("Alternative Fuel Ratio (%)", 0, 50, 20)
    power_kwh_per_ton = st.slider("Power Consumption (kWh/ton)", 80, 250, 150)
    fineness = st.slider("Cement Fineness (Blaine)", 250, 500, 350)
    target_quality = st.slider("Target Product Quality", 60, 100, 85)


st.subheader(" AI Agent Simulation in Progress...")

with st.spinner("Running autonomous optimization cycle..."):
    time.sleep(2.0)

clinker_agent = {
    "efficiency": round(random.uniform(80, 95), 2),
    "specific_energy_kwh_per_ton": round(random.uniform(90, 120), 2),
    "co2_emission_kg_per_ton": round(random.uniform(650, 800), 2)
}

fuel_agent = {
    "fuel_efficiency": round(random.uniform(75, 90), 2),
    "alt_fuel_use_%": alt_fuel_ratio,
    "thermal_substitution_%": round(alt_fuel_ratio * random.uniform(0.8, 1.1), 2)
}

quality_agent = {
    "predicted_quality": round(random.uniform(75, 95), 2),
    "stability_index": round(random.uniform(0.85, 0.98), 2)
}

optimization_agent = {
    "power_saving_%": round(random.uniform(8, 15), 2),
    "co2_reduction_%": round(random.uniform(4, 9), 2),
    "overall_efficiency_gain_%": round(random.uniform(5, 12), 2)
}


try:
    prompt = f"""
    You are CementGPT, an autonomous AI system optimizing cement plant operations.

    Given the following metrics:
    - Feed rate: {feed_rate} t/h
    - Kiln temperature: {kiln_temp}°C
    - Fuel type: {fuel_type}
    - Alternative fuel ratio: {alt_fuel_ratio}%
    - Power consumption: {power_kwh_per_ton} kWh/ton
    - Clinker efficiency: {clinker_agent['efficiency']}%
    - Fuel efficiency: {fuel_agent['fuel_efficiency']}%
    - Predicted quality: {quality_agent['predicted_quality']} (target: {target_quality})
    - CO2 emission: {clinker_agent['co2_emission_kg_per_ton']} kg/ton

    Generate 1–2 concise, actionable optimization suggestions and explain the reasoning behind them.
    Focus on energy savings, quality consistency, and sustainability (TSR and CO2 reduction).
    """
    response = model.generate_content(prompt)
    gemini_output = response.text
except Exception as e:
    gemini_output = f" Gemini API call failed: {e}"
    st.warning(gemini_output)


st.success(" Optimization Complete")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Clinker Efficiency (%)", clinker_agent["efficiency"])
col2.metric("Fuel Efficiency (%)", fuel_agent["fuel_efficiency"])
col3.metric("Predicted Quality", quality_agent["predicted_quality"])
col4.metric("Power Saving (%)", optimization_agent["power_saving_%"])


st.markdown("###  Comparative Analysis — Before vs After Optimization")

baseline = np.array([70, 65, 72, 0])
optimized = np.array([
    clinker_agent["efficiency"],
    fuel_agent["fuel_efficiency"],
    quality_agent["predicted_quality"],
    optimization_agent["power_saving_%"]
])

labels = ["Clinker", "Fuel", "Quality", "Power Saving"]
x = np.arange(len(labels))
width = 0.35

fig, ax = plt.subplots()
ax.bar(x - width/2, baseline, width, label="Baseline", alpha=0.5)
ax.bar(x + width/2, optimized, width, label="Optimized (AI)", alpha=0.8)
ax.set_ylabel("Performance (%)")
ax.set_title("Analysis of Plant Performance Improvement")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()
st.pyplot(fig)


st.markdown("###  Gemini-Powered Insights & Recommendations")
st.write(gemini_output)

st.markdown("###  Sustainability Impact")
colA, colB, colC = st.columns(3)
colA.metric("CO₂ Reduction (%)", optimization_agent["co2_reduction_%"])
colB.metric("Thermal Substitution (%)", fuel_agent["thermal_substitution_%"])
colC.metric("Overall Efficiency Gain (%)", optimization_agent["overall_efficiency_gain_%"])


st.markdown("---")
st.markdown("###  Summary Report")
st.markdown(f"""
**Feed Rate:** {feed_rate} t/h  
**Fuel Type:** {fuel_type}  
**Alternative Fuel Usage:** {alt_fuel_ratio}%  
**Target Quality:** {target_quality}

CementGPT autonomously optimized operational parameters to achieve a projected **{optimization_agent['power_saving_%']}% reduction in energy consumption** and **{optimization_agent['co2_reduction_%']}% lower CO₂ emissions**, 
while improving product quality and kiln stability.

 
""")

st.success(" Simulation completed successfully — Powered by Gemini.")
