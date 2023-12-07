# Introduction

This page explains the analysis files we used in the manuscript. Analysis files can be grouped into mainly three catagories:

1. Metadata and for snmC, snm3C and MERFISH dataset, containing information such as cell subclass annotation, brain region information and TSNE/UMAP coordinates.
2. Integration result between snmC-scRNA, snmC-snATAC, snmC-MERFISH and snm3C-MERFISH.
3. Processed result for figure reproduction, such as DMRs and BigWig tracks.
4. Single-cell files

# Metadata: Experiment Metadata and Cell Taxonomy

## CEMBA.mC.Metadata.csv, CEMBA.m3C.Metadata.csv

* **Description:** Metadata for snmC-seq and snm3C-deq dataset 
* **Download Links:** [CEMBA.mC.Metadata.csv](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/mCseq3/mouse/processed/other/CEMBA.mC.Metadata.csv.tar), [CEMBA.m3C.Metadata.csv](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/m3C-seq/mouse/processed/other/CEMBA.m3C.Metadata.csv.tar)
* **Column Names:**
    * mCCCFrac: Used as the estimation of the upper bound of bisulfite non-conversion rate.
    * mCGFrac, mCHFrac: Global mCG and mCH(A, C, T) methylation level of the nuclei.
    * InputReads, FinalmCReads: Raw input reads number and reads number after filtering.
    * MajorRegion,SubRegion, DissectionRegion, CEMBARegion: Brain regions at different resolution. Check Extended Data Figure1 and Supplementary Table 1 for more information.
    * NeuroTransmitters, Class, SubClass: Cell type annotation after integration with AIBS 10X RNA taxonomy at different resolution.
    * CellGroup: Cell clusters after iterative clustering. (4,673 cell groups for snmC and 2,363 cell groups for snm3C)
    * Plate, Col384, Row384: When sorting single nuclei to 384-well plate, information about which plate and where in that plate the nuclei comes from.
    * Slice: Which brain slice the nuclei comes from when doing teh brain dissection; Check Extended Data Figure 1 for more information.
    * Sample: Sample name.
    * Technology: Technology used, snmC-seq2, snmC-seq3 or snm3C-seq.
    * PassBasicQC: If the nuclei passed our basic quality control.
    * PlateNormCov: Plate-normalized cell coverage, used to filer abnormal clusters. Calculated by final mC reads of each cell divided by the average final reads of cells from the same 384-well plate.
  
## CEMBA.mC.Coordinates.csv, CEMBA.m3C.Coordinates.csv

* **Description:**   Whole brain TSNE/UMAP coordinates aftern snmC and snm3C integration; For mC dataset, it also includes MajorRegion TSNE/UMAP coordinates at cell level.
* **Download Links:** [CEMBA.mC.Coordinates.csv](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/mCseq3/mouse/processed/other/CEMBA.mC.Coordinates.csv.tar), [CEMBA.m3C.Coordinates.csv](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/m3C-seq/mouse/processed/other/CEMBA.m3C.Coordinates.csv.tar)
* **Column Names:**
    * mc_all_tsne_0, mc_all_tsne_1: TSNE coordinates of whole-dataset snmC-snm3C integration , example plot Fig 2b.
    * mc_all_umap_0, mc_all_umap_1: UMAP coordinates of whole-dataset snmC-snm3C integration.
    * mr_tsne_0, mr_tsne_1: TSNE coordinates of snmC-snm3C integration by major region, example plot Extended Data Figure 4.
    * mr_umap_0, mr_umap_1: UMAP coordinates of snmC-snm3C integration by major region.


## CEMBA.mC.CellGroup.Coordinates.csv, CEMBA.m3C.CellGroup.Coordinates.csv

* **Description:**   Whole brain TSNE/UMAP coordinates aftern snmC and snm3C integration at cell group level. For mC dataset, it also includes MajorRegion TSNE/UMAP coordinates at cell group level
* **Download Links:** [CEMBA.mC.CellGroup.Coordinates.csv](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/other/CEMBA.mC.CellGroup.Coordinates.csv.tar), [CEMBA.m3C.CellGroup.Coordinates.csv](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/m3C-seq/mouse/processed/other/CEMBA.m3C.CellGroup.Coordinates.csv.tar)
* **Column Names:**
    * mc_all_tsne_0,mc_all_tsne_1: Centroids TSNE coordinates of cells in each cell group after whole-dataset snmC-snm3C integration , example plot Fig 2a.
    * mc_all_umap_0,mc_all_umap_1: Centroids UMAP coordinates of cells in each cell group after whole-dataset snmC-snm3C integration.
    * cell_counts: Cell number in each cell group, used to plot size of the dots.


## MERFISH.GenePanel.csv

* **Description:**   Genes included in our CEMBA MERFISH gene penel.
* **Download Links:** [MERFISH.GenePanel.csv](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/scell/mCseq3/mouse/processed/other/MERFISH.GenePanel.csv.tar)



# Integration: Integration Results

## mC-m3C.CellGroup.Integration.csv
* **Description:**   Integration result of snmC-seq and snm3C-seq. Cellgroup to cellgroup relationship.
* **Download Links:** [mC-m3C.CellGroup.Integration.csv](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/other/mC-m3C.CellGroup.Integration.csv.tar)
* **Column Names:**
    * mC.CellGroup: mC cell group; Note, 4607 unique cell groups included here, some small mC cell groups found no good match in the 3C dataset.
    * m3C.CellGroup: Matched m3C cell groups for each mC group.


## mC-ATAC.Integration.csv
* **Description:**   Integration result of snmC-seq and snATAC-seq. Cellgroup to cells relationship.
* **Download Links:** [mC-ATAC.Integration.csv](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/mCseq3/mouse/processed/other/mC-ATAC.Integration.csv.tar)
* **Column Names:**
    * mC.CellGroup: mC cell group
    * ATAC.Cells: Matched ATAC cells for each mC cell group.


## CEMBA.mC-MERFISH.Integration.Metadata.csv, CEMBA.m3C-MERFISH.Integration.Metadata.csv
* **Description:**   Integration result of snmC-seq&MERFISH and snm3C-seq&MERFISH. Cell to cell to relationship.
* **Download Links:** [CEMBA.mC-MERFISH.Integration.Metadata.csv](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/mCseq3/mouse/processed/other/CEMBA.mC-MERFISH.Integration.Metadata.csv.tar),[CEMBA.m3C-MERFISH.Integration.Metadata.csv](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/m3C-seq/mouse/processed/other/CEMBA.m3C-MERFISH.Integration.Metadata.csv.tar)
* **Column Names:**
    * merfish_cell: Corresponding merfish cell for each mC/m3C nuclei
    * standard_center_x, standard_center_y: Imputed spatial coordinates for the mC/m3C nuclei
    * sample: sample name; note that spatial coordinates means their coordinated on each sample
    * MajorRegion, SubRegion: Brain regions at different resolution
    * NeuroTransmitters, Class, SubClass: Cell type annotation after integration with AIBS 10X RNA taxonomy at the different resolution

## CEMBA.mC-AIBS_MERFISH.Integration.Metadata.csv
* **Description:**   Integration result of snmC-seq and AIBS whole mouse brain MERFISH dataset. Cell to cell relationship.
* **Download Links:** [CEMBA.mC-AIBS_MERFISH.Integration.Metadata.csv](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/mCseq3/mouse/processed/other/CEMBA.mC-AIBS_MERFISH.Integration.Metadata.csv.tar)
* **Column Names:**
    * merfish_cell: matched merfish cell for mC nuclei
    * global3D_0, global3D_1: Imputed spatial coordinates for the mC nuclei
    * Merfish_slice: Merfish slice ID, in total of 54 merfish slices from aterior to posterior; note that spatial coordinates means their coordinated on each merfish slice
    * MajorRegion,SubRegion: Brain regions at different resolution
    * NeuroTransmitters, Class, SubClass: Cell type annotation after integration with AIBS 10X RNA taxonomy at the different resolution



# Processed Result

## TotalGeneDMRTF.NNZCorrRecords.All.Filtered.csv
* **Description:**   Gene Regulatory Network result. Result from Figure 5.
* **Download Links:** [TotalGeneDMRTF.NNZCorrRecords.All.Filtered.csv](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/reconstruction/mCseq3/mouse/processed/other/TotalGeneDMRTF.NNZCorrRecords.All.Filtered.csv.tar)
* **Column Names:**
    * gene, gene_name: Gene Ensembl ID (vm23) and gene name
    * tf, tf_name: TF Ensembl ID (vm23) and gene name
    * dmr: DMR group ID
    * loop: Cis-loop ID
    * gene-dmr-corr: Person correlation between gene mCH and DMR mCG level among neuronal cell groups
    * gene-dot-corr: Person correlation between gene mCH and contact strength among neuronal cell groups
    * tf-dmr-corr: Person correlation between TF mCH and DMR mCG level among neuronal cell groups
    * gene-tf-corr: Person correlation between gene and TF mCH level among neuronal cell groups
    * final-corr: average correlation between gene-dmr-tf


## mc_bigwig
* **Description:**   Subclass pseudo-bulk mCH and mCG fraction tracks. Note that mCH tracks are very large and whill takes a long time to download.
* **Download Links:** [mc_bigwig](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/other/)

## atac_bigwig
* **Description:**   Subclass pseudo-bulk ATAC CPM track.
* **Download Links:** [atac_bigwig](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/sci_ATACseq/mouse/processed/other/)

## m3c_bigwig
* **Description:**   Subclass pseudo-bulk compartment score and domain probability tracks.
* **Download Links:** [m3c_bigwig](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/m3C-seq/mouse/processed/other/)

## CEMBA.snmC.mcds
* **Description:**   snmC dataset cell-by-gene/5kb/100kb mCH and mCG normalized fraction
* **Download Links:** [CEMBA.snmC.mcds](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/counts/CEMBA.snmC.mcds.tar.gz)


## CEMBA.snmC.L4RegionAgg.zarr
* **Description:**   cell-group-by-gene/100kb mCH and mCG normalized fraction.
* **Download Links:** [CEMBA.snmC.L4RegionAgg.zarr](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/counts/CEMBA.snmC.L4RegionAgg.tar.gz)


## CEMBA.snmC.L4Region.AIBS_TENX.log1pCPM.zarr
* **Description:**   cell-group-by-gene RNA log1p(CPM)
* **Download Links:** [CEMBA.snmC.L4Region.AIBS_TENX.log1pCPM.zarr](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/counts/CEMBA.snmC.L4Region.AIBS_TENX.log1pCPM.tar.gz)


## CEMBA.snmC.AllGroupedDMRs.mCGATACQnorm.zarr
* **Description:**   cell-group-by-DMR mCG quantile normalized fraction and ATAC quantile normalized counts
* **Download Links:** [CEMBA.snmC.AllGroupedDMRs.mCGATACQnorm.zarr](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/counts/CEMBA.snmC.AllGroupedDMRs.mCGATACQnorm.tar.gz)

## TotalWatershedCell.BasicFilter.zarr
* **Description:**   CEMBA MERFISH dataset cell-by-gene RNA raw count
* **Download Links:** [TotalWatershedCell.BasicFilter.zarr](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/counts/MERFISH.TotalWatershedCell.BasicFilter.tar.gz)

## m3c_mcool
* **Description:**   Subclass pseudo-bulk imputed 10K resolution 3C matrix, imputed 100K resolution 3C matrix and raw 10K resolution 3C matrix. Only cis contacts are kept.
* **Download Links:** [m3c_mcool](https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/m3C-seq/mouse/processed/counts/)


# Single-cell files

## snmC-seq.single-cell.files
* **Description:**  The silgle-cell Fastq, Bam and ALLC files for snmC data can be downloaded from GEO. We have two GEO super series, one for the [original 2021 paper](https://www.nature.com/articles/s41586-020-03182-8), the other for the remaining new data in this paper. Also, for each cell, the GEO sample ID and GEO series ID can be found in Smaple Information Table below.
* **Download Links:** [GEO super series for 2021 paper](https://www.ncbi.xyz/geo/query/acc.cgi?acc=GSE132489), [GEO super series for new data in this paper](https://www.ncbi.xyz/geo/query/acc.cgi?acc=GSE213262), [mC Smaple Information Table](https://drive.google.com/file/d/16uwHMac0zTcTy6VeJObi6tUNpki5RnJA/view?usp=sharing)
* **Column Names:**
  * Sample_geo_accession: GEO sample ID for each cell
  * geo_series: GEO series ID with certain number of cells

## snm3C-seq.single-cell.files
* **Description:**  The silgle-cell Fastq, Contact and ALLC files for snm3C data can be downloaded from NeMo and GEO. The 3C cells included for the [original 2021 paper](https://www.nature.com/articles/s41586-020-03182-8) are in GEO, the remaining data in this paper are in NeMo. Also, for each cell, the download path on NeMo can be found in this m3C Smaple Information Table below. 

* **Download Links:** [GEO series for 3C files in 2021 paper](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE156683), [m3C Smaple Information Table](https://drive.google.com/file/d/149nviDEyLxrdlfXe_14eitFMa8bCX6Ed/view?usp=sharing)
* **Column Names:**
  * fastq_files: NeMo download path for single-cell fastq files
  * contact_files: NeMo download path for single-cell contact files
  * allc_files: NeMo download path for single-cell allc files
