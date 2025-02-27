#This module is used for plotting of the hotspots distribution after computing the hotspot score and regions

library("data.table")
library("preprocessCore")
library("tidyr")
library("preprocessCore")
library("ggplot2")
library("dplyr")

#Module 4: Plot the hotspots score distribution

plot_hotspots <- function(input_hotspots_table) {
  
  input_hotspots_table %>% ggplot(aes(x = log_HS,fill = decile)) + geom_histogram(bins=500,color = 'black') 
  + theme_classic() + xlab('Log-scaled hotspot score') + ylab('Counts') 
  + guides(fill=guide_legend(title="Deciles"))
  
}
