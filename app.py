import streamlit as st
import pandas as pd
import plotly.express as px

# Title for the Streamlit app
st.title("Top Cities for Financial Independence in the U.S. & Canada")

# Load the embedded Excel file automatically
@st.cache_data
def load_data():
    file_path = "Col_Sal_Cities_US_Can.xlsx"  # Ensure this file is in the same directory
    data = pd.read_excel(file_path, sheet_name="City")

    # Clean and format the City column
    data = data.dropna(subset=['City'])  # Drop rows where 'City' is NaN
    data['City'] = data['City'].astype(str).str.strip().str.title()  # Convert to string and clean text

    # Extract short city names for display
    data['City_Short'] = data['City'].apply(lambda x: x.split(',')[0])

    return data

data = load_data()

# Add title and instructions
st.write("### Instructions for Using the Tool")

instructions = """
- This tool helps identify the most suitable **U.S. & Canadian cities** for pursuing FI during the accumulation phase.
- Select your **current city** from the dropdown menu above the graph.
- The graph maps **percentage differences** in salaries and cost of living (COL) relative to your selected city.
- The **red dashed line** serves as a benchmark:
   - Cities **above the red line** may provide better opportunities for pursuing financial independence.
   - Cities **on the red line** have equivalent percentage differences in both salaries and COL (e.g., a 10% higher salary but also a 10% higher COL).
   - Cities **below the red line** may provide worse opportunities for pursuing financial independence.
Example: With San Diego as the reference, San Francisco has a 30.5% higher average salary, while its cost of living is only 13.6% higher. Pursuing FI in San Francisco is likely to be easier, on average, than in San Diego.
- Data on salaries and cost of living is from **Numbeo (2023)**.
"""
st.write(instructions)  # Add instructions above the dropdown menu

# Create a dropdown for selecting the reference city
city_options = sorted(data['City'].unique())  # Ensure cities are sorted alphabetically

# Set default index to "San Diego, CA, United States" if it exists in the list
default_city = "San Diego, Ca, United States"
default_index = city_options.index(default_city) if default_city in city_options else 0

reference_city = st.selectbox(
    "Select Reference City:",
    options=city_options,  # Sorted list of cities
    index=default_index  # Default selection to "San Diego, CA, United States"
)

# Calculate salary and cost of living differences
def calculate_differences(data, reference_city):
    ref_data = data[data['City'] == reference_city].iloc[0]
    data['Sal_Diff_%'] = ((data['Salary'] - ref_data['Salary']) / ref_data['Salary']) * 100
    data['Col_Diff_%'] = ((data['COL 2023'] - ref_data['COL 2023']) / ref_data['COL 2023']) * 100
    return data

data = calculate_differences(data, reference_city)

# Create scatter plot with red dashed benchmark line
def create_scatter_plot(data, reference_city):
    # Calculate dynamic axis limits
    x_min, x_max = data['Col_Diff_%'].min(), data['Col_Diff_%'].max()
    y_min, y_max = data['Sal_Diff_%'].min(), data['Sal_Diff_%'].max()
    x_margin = (x_max - x_min) * 0.1
    y_margin = (y_max - y_min) * 0.1

    # Create scatter plot
    fig = px.scatter(
        data,
        x='Col_Diff_%',
        y='Sal_Diff_%',
        text='City_Short',
        hover_data={'City': True, 'Col_Diff_%': ':.1f', 'Sal_Diff_%': ':.1f'},
        labels={
            'Col_Diff_%': 'Cost of Living Difference (%)',
            'Sal_Diff_%': 'Salary Difference (%)',
        },
        title=f"Cost of Living vs Salary Comparison (Reference: {reference_city})",
        template="plotly_dark",
    )

    # Add red benchmark line
    fig.add_shape(
        type="line",
        x0=-1000, x1=1000,
        y0=-1000, y1=1000,
        line=dict(color="red", dash="dash", width=2),
    )

    # Add dashed lines for x=0 and y=0
    fig.add_shape(
        type="line",
        x0=0, x1=0,
        y0=y_min - y_margin, y1=y_max + y_margin,
        line=dict(color="white", dash="dash", width=2),
    )
    fig.add_shape(
        type="line",
        x0=x_min - x_margin, x1=x_max + x_margin,
        y0=0, y1=0,
        line=dict(color="white", dash="dash", width=2),
    )

    # Customize gridlines
    fig.update_xaxes(
        range=[x_min - x_margin, x_max + x_margin],
        gridcolor="rgba(255, 255, 255, 0.2)",
        showgrid=True,
        zeroline=False,
        tickmode="linear",
        dtick=(x_max - x_min) / 5,
    )
    fig.update_yaxes(
        range=[y_min - y_margin, y_max + y_margin],
        gridcolor="rgba(255, 255, 255, 0.2)",
        showgrid=True,
        zeroline=False,
        tickmode="linear",
        dtick=(y_max - y_min) / 5,
    )

    # Customize bubble size and legend
    fig.update_traces(
        marker=dict(size=13, line=dict(width=2, color='DarkSlateGrey')),
        textposition='top center'
    )
    fig.update_layout(
        height=600,
        width=900,
        legend=dict(
            title=dict(font=dict(color="white")),
            font=dict(color="white"),
            bgcolor="rgba(0, 0, 0, 0)",
        ),
        title=dict(
            text=f"Cost of Living vs Salary Comparison (Reference: {reference_city})",
            font=dict(size=20, color="white"),
        ),
        margin=dict(l=40, r=40, t=50, b=5),
        paper_bgcolor='black',
        plot_bgcolor='black',
    )

    return fig

# Display the plot
scatter_plot = create_scatter_plot(data, reference_city)
st.plotly_chart(scatter_plot, use_container_width=True)







