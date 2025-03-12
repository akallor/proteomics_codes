import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_violinplot(data, x_val, y_val, plot_type='violin', color_palette='viridis', plot_width=0.8, plt_title='Distribution Plot', x_label='', y_label='', save_result=None):
    """
    Plots the distribution of data by a specified column using a violin plot (or boxplot).

    Parameters:
    data (pd.DataFrame): The dataset containing the data to plot.
    x_val (str): The column name for the x-axis.
    y_val (str): The column name for the y-axis.
    plot_type (str): The type of plot to create ('violin' or 'box'). Default is 'violin'.
    color_palette (str): The color palette to use for the plot. Default is 'viridis'.
    plot_width (float): The width of the plot elements (bars for boxplot, width for violinplot). Default is 0.8.
    plt_title (str): The title of the plot. Default is 'Distribution Plot'.
    x_label (str): The label for the x-axis. Default is an empty string.
    y_label (str): The label for the y-axis. Default is an empty string.
    save_result (str): The file name to save the plot. Default is None (won't save).

    Returns:
    None
    """
    # Set plot style
    sns.set(style="ticks")

    # Create the plot
    plt.figure(figsize=(12, 8))
    
    if plot_type == 'violin':
        sns.violinplot(x=x_val, y=y_val, data=data, palette=color_palette, width=plot_width)
    elif plot_type == 'box':
        sns.boxplot(x=x_val, y=y_val, data=data, palette=color_palette, width=plot_width)

    # Add title and labels
    plt.title(plt_title, fontsize=16)
    plt.xlabel(x_label, fontsize=14)
    plt.ylabel(y_label, fontsize=14)
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Remove gridlines
    sns.despine()
    
    # Show plot
    plt.tight_layout()
    
    # Save plot if save_result is provided
    if save_result:
        plt.savefig(f'{save_result}.pdf')
    
    plt.show()
