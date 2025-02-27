#This module performs normalization of the spectral count data obtained from Fragpipe 
#during the second round search and outputs a normalized sample matrix

library("data.table")
library("preprocessCore")
library("tidyr")
library("preprocessCore")


#Module 1: Normalization

normalize <- function(peptide_input,peptide_output) {
  
  fh <- fread(peptide_input,sep = '\t')
  fh$`Spectral Count` <- as.numeric(fh$`Spectral Count`)
  sp_df <- spread(fh[, c('Peptide', 'Sample Name', 'Spectral Count')],
                  `Sample Name`, `Spectral Count`)
  sp_boxplot <- melt(setDT(sp_df),  id.vars = "Peptide", 
                     variable.name = "Spectral Count")
  cols <- colnames(sp_df)
  cols <- cols[seq(2,length(cols))]
  sp <- as.matrix(sp_df)[, cols]
  sp <- matrix(as.numeric(sp), ncol=ncol(sp))
  sp_n <- normalize.quantiles(sp, copy=F)
  sp_n_boxplot = as.data.frame(sp_n)
  sp_n_boxplot$Peptide = sp_df$Peptide
  sp_n_boxplot_2 = melt(setDT(sp_n_boxplot),  id.vars = "Peptide", 
                        variable.name = "Spectral Count")
  cols <- colnames(sp_df)
  cols <- cols[seq(2,length(cols))]
  cols <- c(cols, 'Peptide')
  colnames(sp_n_boxplot) <- cols
  par(mar = c(2,2,2,2))
  boxplot(value~`Spectral Count`, sp_boxplot, use.cols = F, 
          outline=FALSE, na.rm=T)
  boxplot(value~`Spectral Count`, sp_n_boxplot_2, use.cols = F, 
          outline=FALSE, na.rm=T)
  write.table(sp_n_boxplot, sep='\t', file = paste(peptide_output,
              ".tsv",sep = ""),row.names = FALSE, col.names = TRUE)
  
}
