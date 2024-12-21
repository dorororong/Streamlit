import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import font_manager

# Ensure the font path is correct if you have placed the font file in your project directory
font_path = 'font/NanumGothic-Bold.ttf'
font_manager.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'NanumGothic'

# Sample data
labels = ['에이', '비', '씨', '디디']
sizes = [15, 30, 45, 10]


# Plotting bar chart
fig, ax = plt.subplots()
ax.bar(labels, sizes)


# Title in Korean to test the font
ax.set_title('테스트 차트') 

# Display the plot in Streamlit
st.pyplot(fig)