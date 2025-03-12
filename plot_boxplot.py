"""
Plot boxplots for any given data distribution. Make sure the dataset to be analyzed has the following columns: "x_val","Min","Max","Mean","Median".
Please refer to "prepare_data_for_boxplot.py" for preparing the dataset in a compatible format.
TODO: In future "prepare_data_for_boxplot.py" will be integrated with this code.
"""
import matplotlib.pyplot as plt
import numpy as np
import os as os
import pandas as pd
import seaborn as sns

def plot_boxplot(dataset,x_val,y_val,box_width,
                          color_palette,plt_title,x_lab,y_lab):
    """
    Plots the data distribution by the specified x value using a boxplot.

    Parameters:
    data (dict): A dictionary containing the data with keys 'x_val', 'Min', 'Max', 'Mean', and 'Median'.

    Returns:
    None
    """
    # Create DataFrame
    #age_data = pd.DataFrame(data)
    
    # Prepare the data for boxplot
    boxplot_data = []
    for index, row in age_data.iterrows():
        min_val = row['Min']
        max_val = row['Max']
        median_val = row['Median']
        boxplot_data.append([min_val, median_val, max_val])
    
    # Convert to DataFrame suitable for seaborn
    boxplot_df = pd.DataFrame(boxplot_data, columns = ['Min', 'Median', 'Max'])
    boxplot_df[x_val] = age_data[x_val]
    
    # Melt the DataFrame for seaborn
    melted_df = pd.melt(boxplot_df, id_vars = [x_val], value_vars = ['Min', 'Median', 'Max'], var_name = 'Statistic', value_name = y_val)
    
    # Set plot style
    sns.set(style="ticks")
    
    # Create the boxplot
    plt.figure(figsize = (12, 8))
    sns.boxplot(x = x_val, y = y_val, data = melted_df,width = box_width,palette = color_palette)
    
    # Add title and labels
    plt.title(plt_title, fontsize = 16)
    plt.xlabel(x_lab, fontsize = 14)
    plt.ylabel(y_lab, fontsize = 14)
    plt.xticks(rotation = 45)
    sns.despine()
                            
    # Show the plot
    plt.tight_layout()
    plt.show()
