"""
Plot a stacked frequency distribution of 2 groups. For more than 3 groups, use plot_stacked_multiple.py.
TODO: Please check whether the width of a bar changes correctly.
"""


import matplotlib.pyplot as plt
import numpy as np
import os as os
import pandas as pd
import seaborn as sns


def plot_stacked_distribution(dataset,x_val1,y_val1,label_1,
                              color_1,x_val2,y_val2,bottom,label_2,
                              color_2,bar_width,plt_title,x_label,y_label,save_result):
    """
    Plots the distribution of males and females per condition using a stacked bar plot.

    Parameters:
    data (dict): A dictionary containing the data with keys 'S.No.', 'Subtype', 
                 'Male (no_of_unique_patients)', and 'Female (no_of_unique_patients)'.

    Returns:
    None
    """
    
    # Set plot size
    plt.figure(figsize=(12, 8))

    # Create the stacked bar plot
    bar_width = 0.4
    p1 = plt.bar(dataset[x_val1], dataset[y_val1], label=label_1, color=color_1, width=bar_width)
    p2 = plt.bar(dataset[x_val1], dataset[y_val1], bottom=dataset[bottom], label=label_2, color=color_2, width=bar_width)

    # Add titles and labels
    plt.title(plt_title, fontsize=16)
    plt.xlabel(x_label, fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    plt.xticks(rotation=45)

    # Add legend
    plt.legend()

    # Remove gridlines
    plt.grid(False)
    
    sns.despine()
    
    # Annotate bars with the counts
    for bar in p1:
        plt.annotate(f'{int(bar.get_height())}', 
                     xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()), 
                     xytext=(0, 5), 
                     textcoords='offset points', 
                     ha='center', va='bottom', 
                     fontsize=12, color='white')
    
    for bar in p2:
        plt.annotate(f'{int(bar.get_height() - bar.get_y())}', 
                     xy=(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height()), 
                     xytext=(0, 5), 
                     textcoords='offset points', 
                     ha='center', va='bottom', 
                     fontsize=12, color='white')

    # Show the plot
    plt.tight_layout()
    
    plt.savefig(f'{save_result}.pdf')
    
    plt.show()
