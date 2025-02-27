#This module is used to compute coverage and output the genomic ranges object 
#using the normalized sample matrix

library("data.table")
library("preprocessCore")
library("tidyr")
library("preprocessCore")

#Module 2: Calculate coverage using BAM file and genomic ranges
#object

genomic_coverage <- function(input_BAM,input_spectral_counts,
                             input_HLA_bindings,canonical_peptides_features,
                             canonical_regions_coverage,canonical_positions) 
  {
  
  param <- ScanBamParam(what=c("qname"))
  alig = readGAlignments(input_BAM, param=param)
 
  
  # split splicing junctions peptides into separate ranges
  # and converting to Granges object
  dd_grlist <- grglist(alig, use.names=TRUE, use.mcols=TRUE, 
                       order.as.in.query=T, drop.D.ranges=T)
  dd = unlist(dd_grlist)
  # retrieving the meta data
  dd$`Ref ID` =  rep(seq(length(alig)), times=elementNROWS(dd_grlist))
  dd$id =  seq(length(dd))
  dd$name =  rep(elementMetadata(dd_grlist), 
                 times=elementNROWS(dd_grlist))$qname
  
  # read the normalized spectral count matrix
  normalized_counts <- fread(input_spectral_counts, sep='\t')
  samples <- colnames(normalized_counts)[seq(1, ncol(normalized_counts) - 1 )]
  normalized_counts[,'Normalized Spectral Counts Sum'] <- apply(normalized_counts[, ..samples], 
                                                                1, sum, na.rm=T)
  
  temp1 <- normalized_counts[,c("Peptide", 
                                'Normalized Spectral Counts Sum')]
  colnames(temp1) <- c('name', 'Normalized Spectral Counts Sum')
  temp2 <- as.data.table(dd$name)
  colnames(temp2) <- c('name')
  temp3 <- merge(temp2, temp1, by='name', sort=F)
  dd$`Normalized Spectral Counts Sum` = temp3$`Normalized Spectral Counts Sum`
  
  # read netMHCpan 4.1 predictions
  bindings <- fread(input_HLA_bindings, sep='\t')
  
  # keep binders
  bindings_f <- bindings[bindings$EL_Rank <= 2]
  alleles_df <- unique(bindings_f[,c("Peptide", "Allele")])
  colnames(alleles_df) <- c("name", "Allele")
  alleles_df <- merge(alleles_df, as.data.frame(dd[,c('name', 'id')])[,c('name', 'id')])
  alleles_df <- alleles_df[order(alleles_df$id),]
  
  # reduce the ranges and calculate coverage
  dd_duplicated <- rep(dd, times=round(dd$`Normalized Spectral Counts Sum`))
  cov <- GRanges(coverage(dd_duplicated))
  cov <- cov[cov$score != 0]
  
  # keep track between the coverage and the peptides
  overlaps_temp <- findOverlaps(cov, dd)
  overlaps <- as.data.frame(overlaps_temp)
  overlaps <- aggregate(subjectHits~queryHits, overlaps, paste, collapse=", ")
  cov$id = overlaps$subjectHits
  
  
  # get number of HLA Alleles for regions
  temp1 = as.data.table(overlaps_temp)
  colnames(temp1) = c("cov id", "id")
  temp2 <- as.data.table(alleles_df[, c("id", "Allele")])
  temp3 <- merge(temp1, temp2, by='id', sort=F, 
                 allow.cartesian=TRUE, all.x=T)
  temp4 <- aggregate(`Allele`~`cov id`, temp3, 
                     function (x) sum(!is.na(unique(x))),  na.action=NULL)
  
  cov$nHLA <- temp4$Allele
  cov$normalized_nHLA <- unlist(cov$nHLA) / width(cov)
  
  rm(list=c("temp1", "temp2", "temp3", "temp4"))
  
  # recover strand information
  temp1 = as.data.table(overlaps_temp)
  colnames(temp1) = c("cov id", "id")
  temp2 <- data.table(strand=as.vector(strand(dd)), id=dd$id)
  temp3 <- merge(temp1, temp2, by='id', sort=F)
  temp4 <- aggregate(strand~`cov id`, 
                     unique(temp3[, c("cov id", 'strand')]), 
                     function (x) paste(unique(x), sep=', ', collapse=', '))
  temp4[temp4$strand == '-, +', 'strand'] <- '+, -'
  
  # convert Genomic Ranges object to dataframe
  # to add unconventional strand information (+ or - or +, -)
  cov_df = as.data.frame(cov)
  cov_df$strand <- temp4$strand
  cols <- c("CHR", "Start", "End", "Width", "Strand", "Depth", "ID", 
            "HLA Alleles Count", "Normalized HLA Alleles Count")
  colnames(cov_df) <- cols
  cols <- c("CHR", "Start", "End", "Width", "Strand", "ID", "Depth", 
            "HLA Alleles Count", "Normalized HLA Alleles Count")
  cov_df <- cov_df[, cols]
  cov_df$width <- width(cov)
  
  dd_df <- as.data.frame(dd)
  colnames(dd_df) <- c("CHR", "start", "end", "width",	"strand", 
                       "Ref ID",	"ID", "Peptide",	
                       "Normalized Spectral Counts Sum")
  
  write.table(dd_df, sep='\t', file= paste(canonical_peptides_features,
                                           ".tsv",sep = ''), 
              row.names = FALSE, col.names = TRUE)
  write.table(cov_df, sep='\t', file= paste(canonical_regions_coverage,
                                            ".tsv",sep = ''), 
              row.names = FALSE, col.names = TRUE)
  
  rm(list=c("temp1", "temp2", "temp3", "temp4"))
  
  # convert to coverage to per position coverage
  cov_pos <- unlist(tile(cov, width=1))
  cov_pos$score <- cov[subjectHits(findOverlaps(cov_pos, cov))]$score
  cov_pos$id <- cov[subjectHits(findOverlaps(cov_pos, cov))]$id
  temp1 <- merge(data.table(id=subjectHits(findOverlaps(cov_pos, dd))), 
                 alleles_df, sort=F, allow.cartesian=TRUE, all.x=T)
  temp2 <- aggregate(Allele~id, temp1,  
                     function (x) sum(!is.na(unique(x))),  na.action=NULL)
  temp3 <- data.table(temp_id=seq(length(cov_pos)), id=cov_pos$id)
  temp4 <- temp3[, .(id = as.numeric(unlist(tstrsplit(id, ", ", fixed=TRUE)))), by = temp_id]
  temp5 <- merge(temp4, alleles_df, sort=F, 
                 allow.cartesian=TRUE, all.x=T)
  temp6 <- aggregate(Allele~temp_id, temp5,  
                     function (x) sum(!is.na(unique(x))),  na.action=NULL)
  cov_pos$nHLA <- temp6$Allele
  
  cov_pos_df <- as.data.frame(cov_pos)
  colnames(cov_pos_df) <- c("CHR", "Start", "End", "Width", "Strand", 
                            "Depth", "ID", "Number of HLA Alleles")
  write.table(cov_pos_df, sep='\t', 
              file= paste(canonical_regions_coverage,'.tsv',sep = ''), 
              row.names = FALSE, col.names = TRUE)
  
  rm(list=c("temp1", "temp2", "temp3", "temp4", "temp5", "temp6"))
  
}
