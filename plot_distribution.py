"""

General plotting code to plot a frequency distribution for the specified variable. Ensure that the dataset is sorted in descending order.
Future editions might have datasets sorted within the code.

"""

import matplotlib.pyplot as plt
import numpy as np
import os as os
import pandas as pd
import seaborn as sns

def plot_distribution(dataset,x_val,y_val,color_palette,
                              bar_width,plt_title,x_label,y_label,save_result):
    # Create DataFrame
    #patient_data = pd.DataFrame(data)
    
    # Set plot style
    sns.set(style="ticks")
    
    # Create bar plot
    plt.figure(figsize=(10, 6))
    plot = sns.barplot(x = x_val, y = y_val, data = dataset, palette = color_palette,width = bar_width)
    
    # Add title and labels
    plt.title(plt_title, fontsize=16)
    plt.xlabel(x_label, fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Annotate the bars with the patient count
    for p in plot.patches:
        plot.annotate(format(p.get_height(), '.0f'), 
                      (p.get_x() + p.get_width() / 2., p.get_height()), 
                      ha = 'center', va = 'center', 
                      xytext = (0, 9), 
                      textcoords = 'offset points')
    sns.despine()
    
    # Show plot
    plt.tight_layout()
    
    plt.savefig(f'{save_result}.pdf')
    
    plt.show()
