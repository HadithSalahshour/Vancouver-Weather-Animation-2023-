
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib import patheffects
from IPython.display import display, Image
import numpy as np

# Load the CSV file containing weather data
file_path = '/content/Vancouver 2023-01-01 to 2023-12-31.csv'  # Update with the actual path to your CSV file
weather_data = pd.read_csv(file_path)

# Function to categorize weather conditions
def categorize_condition(conditions):
    if "Snow" in conditions:
        return "Snowy"
    elif "Rain" in conditions:
        return "Rainy"
    elif "Overcast" in conditions:
        return "Overcast"
    elif "Partially cloudy" in conditions:
        return "Partially Cloudy"
    elif "Clear" in conditions:
        return "Clear"
    else:
        return "Other"

# Apply the categorization to the data
weather_data['Condition'] = weather_data['conditions'].apply(categorize_condition)

# Convert 'datetime' column to datetime type and extract month names
weather_data['datetime'] = pd.to_datetime(weather_data['datetime'])
weather_data['Month'] = weather_data['datetime'].dt.month_name()

# Group data by month and count occurrences of each condition
monthly_condition_counts = weather_data.groupby(['Month', 'Condition']).size().unstack(fill_value=0)

# Define color mapping for each weather condition
color_mapping = {
    'Clear': '#FFD700',            # Sunny yellow
    'Partially Cloudy': '#B0C4DE', # Soft blue-white for partial clouds
    'Overcast': '#A9A9A9',         # Dark grey for overcast
    'Rainy': '#4682B4',            # Soft blue for rain
    'Snowy': '#F5F5F5'             # Near white for snow
}

# Define the order of months for visualization
months_order = ["January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]

# Animation timing settings
display_time = 0.5  # Time to show each month's data in seconds
transition_time = 0.1  # Time for transitions between months in seconds
fps = 60  # Frames per second
display_frames = int(display_time * fps)  # Frames per month display
transition_frames = int(transition_time * fps)  # Frames per transition

# Set up the plot
fig, ax = plt.subplots(figsize=(8, 8))

# Function to interpolate between two sets of values
def interpolate_values(start_values, end_values, alpha):
    return start_values * (1 - alpha) + end_values * alpha

# Custom label function for pie chart percentages
def custom_label(pct, allvals):
    absolute = int(np.round(pct / 100. * np.sum(allvals)))
    return f"{absolute}%" if pct >= 1 else ''

# Initialize the pie chart
def init():
    ax.clear()
    ax.set_title('Weather Conditions in Vancouver')
    return ax

# Update function for the animation
def update(frame):
    ax.clear()

    # Determine current month and transition status
    month_index = frame // (display_frames + transition_frames)
    transition_phase = frame % (display_frames + transition_frames)

    month = months_order[month_index]
    current_data = monthly_condition_counts.loc[month]

    # Check if it's a display or transition phase
    if transition_phase < display_frames:  # Display current month
        display_data = current_data
    else:  # Transition to the next month
        next_month = months_order[(month_index + 1) % len(months_order)]
        next_data = monthly_condition_counts.loc[next_month]
        alpha = (transition_phase - display_frames) / transition_frames
        display_data = interpolate_values(current_data.values, next_data.values, alpha)

    # Plot the pie chart
    ax.pie(display_data, labels=[f"{label}" if val / sum(display_data) >= 0.01 else '' 
            for label, val in zip(current_data.index, display_data)],
           colors=[color_mapping[cond] for cond in current_data.index], 
           autopct=lambda pct: custom_label(pct, display_data),
           startangle=140, textprops={'color': 'white', 'weight': 'bold', 
           'path_effects': [patheffects.withStroke(linewidth=3, foreground='black')]},
           wedgeprops={'edgecolor': 'black', 'linewidth': 1.5})

    ax.set_title(f'Weather Conditions in Vancouver - {month}')

# Create the animation
total_frames = len(months_order) * (display_frames + transition_frames)
ani = FuncAnimation(fig, update, frames=total_frames, init_func=init, repeat=False, interval=1000 / fps)

# Save and display the animation as a GIF
gif_path = '/content/weather_animation_by_month_2023.gif'
ani.save(gif_path, writer=PillowWriter(fps=fps))
display(Image(gif_path))

# Provide a download link for the GIF
from google.colab import files
files.download(gif_path)
