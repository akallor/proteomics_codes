"""
Create a multiple stacked barplot (more than 2 groups). Ensure the data is prepared as per the required format.
TODO: Please provide an example of the dataset that can be used for creating this plot.
"""
import matplotlib.pyplot as plt
import numpy as np
import os as os
import pandas as pd
import seaborn as sns

def plot_stacked_multiple(dataset,color_palette,bar_width,
                          x_lab,y_lab,plt_title,legend_title):
    # Define colors
    colors = sns.color_palette(color_palette, n_colors = len(dataset.columns) - 1)

    # Set figure size
    plt.figure(figsize = (12, 6))

    # Initialize bottom values (to stack bars)
    bottom_values = [0] * len(dataset)

    # Iterate over each tissue type (column)
    for idx, tissue in enumerate(dataset.columns[1:]):  # Skip tumorType column
        plt.bar(dataset["tumorType"], dataset[tissue], bottom = bottom_values, label = tissue, color = colors[idx],width = bar_width)
        bottom_values += dataset[tissue]  # Update bottom values for stacking

    # Rotate x-axis labels
    plt.xticks(rotation = 45, ha = "right")

    # Set labels and title
    plt.xlabel(x_lab)
    plt.ylabel(y_lab)
    plt.title(plt_title)
    
    sns.despine()

    # Show legend and plot
    plt.legend(title = legend_title)
    plt.show()
