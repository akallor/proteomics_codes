#This module computes hotspot scores from the normalized spectral counts matrix (together with their genomic ranges and coordinates)
#and derives the hotspot regions based on these scores. It then outputs two tables: a) Hotspots score and b) Hotspots regions

library("data.table")
library("preprocessCore")
library("tidyr")
library("fabricatr")

#Module 3: Generate hotspots score and hotspots regions

hotspots_score <- function(coverage_position_data,output_hotspots_table) 
  {
  
  cov_pos_df <- read.table(coverage_position_data,sep = '\t')
  
  #Derive hotspots score as Depth*No. of unique HLA alleles/Width
  #Non-zero members are only retained
  
  cov_pos_df$HS <- (cov_pos_df$Depth*cov_pos_df$`Number of HLA Alleles`)/(cov_pos_df$Width)
  
  cov_pos_nozero <- cov_pos_df[cov_pos_df$HS > 0,]
  
  #Log of hostpot score
  
  cov_pos_nozero$log_HS <- log10(cov_pos_nozero$HS)
  
  #Split the hotspot score vector into deciles 
  #split_quantile function is from fabricatr library
  
  cov_pos_nozero$decile <- split_quantile(cov_pos_nozero$log_HS,type = 10)
  
  #Derive region id for each chromosomal region 
  cov_pos_nozero$region_id <- sequence(rle(as.vector(cov_pos_nozero$CHR))$lengths)
  
  cov_pos_nozero$hotspot_id <- paste('R',cov_pos_nozero$CHR,'_',
                                     cov_pos_nozero$region_id,sep = '')
  
  write.table(cov_pos_nozero,file = paste(output_hotspots_table,'.tsv',
                                          sep = ''),row.names = FALSE,
              sep = '\t')
  
}
