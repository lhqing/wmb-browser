## Introduction

This page explains the analysis files we used in the manuscript. Analysis files can be grouped into mainly three catagories:

1. Metadata and for snmC, snm3C and MERFISH dataset, containing information such as cell subclass annotation, brain region information and TSNE/UMAP coordinates.
2. Integration result between snmC-scRNA, snmC-snATAC, snmC-MERFISH and snm3C-MERFISH.
3. Processed result for figure reproduction, such as DMRs and BigWig tracks.
4. Single-cell files

## Metadata

### Experiment Metadata and Cell Taxonomy

#### File Names

- CEMBA.mC.Metadata.csv
- CEMBA.m3C.Metadata.csv

#### Description

Metadata for snmC-seq and snm3C-deq dataset

#### Column Names

- mCCCFrac: Used as the estimation of the upper bound of bisulfite non-conversion rate.
- mCGFrac, mCHFrac: Global mCG and mCH(A, C, T) methylation level of the nuclei.
- InputReads, FinalmCReads: Raw input reads number and reads number after filtering.
- MajorRegion,SubRegion, DissectionRegion, CEMBARegion: Brain regions at different resolution. Check Extended Data Figure1 for more information.
- NeuroTransmitters, Class, SubClass: Cell type annotation after integration with AIBS 10X RNA taxonomy at different resolution.
- CellGroup: Cell clusters after iterative clustering. (4,673 cell groups for snmC and 2,363 cell groups for snm3C)
- Plate, Col384, Row384: When sorting single nuclei to 384-well plate, information about which plate and where in that plate the nuclei comes from.
- Slice: Which brain slice the nuclei comes from when doing teh brain dissection; Check Extended Data Figure for more information.
- Sample: Sample name.
- Technology: Technology used, snmC-seq2, snmC-seq3 or snm3C-seq.
- PassBasicQC: If the nuclei passed our basic quality control.
- PlateNormCov: Plate-normalized cell coverage, used to filer abnormal clusters. Calculated by final mC reads of each cell divided by the average final reads of cells from the same 384-well plate.

#### File Names

- CEMBA.mC.Coordinates.csv
- CEMBA.m3C.Coordinates.csv

#### Describtion

Whole brain TSNE/UMAP coordinates aftern snmC and snm3C integration; For mC dataset, it also includes MajorRegion TSNE/UMAP coordinates at cell level.

#### Column Names

- mc_all_tsne_0, mc_all_tsne_1: TSNE coordinates of whole-dataset snmC-snm3C integration , example plot Fig 2b.
- mc_all_umap_0, mc_all_umap_1: UMAP coordinates of whole-dataset snmC-snm3C integration.
- mr_tsne_0, mr_tsne_1: TSNE coordinates of snmC-snm3C integration by major region, example plot Extended Data Figure 4.
- mr_umap_0, mr_umap_1: UMAP coordinates of snmC-snm3C integration by major region.

#### Names

- CEMBA.mC.CellGroup.Coordinates.csv
- CEMBA.m3C.CellGroup.Coordinates.csv

#### Describtion

Whole brain TSNE/UMAP coordinates aftern snmC and snm3C integration at cell group level. For mC dataset, it also includes MajorRegion TSNE/UMAP coordinates at cell group level.

#### Column Names

- mc_all_tsne_0,mc_all_tsne_1: Centroids TSNE coordinates of cells in each cell group after whole-dataset snmC-snm3C integration , example plot Fig 2a.
- mc_all_umap_0,mc_all_umap_1: Centroids UMAP coordinates of cells in each cell group after whole-dataset snmC-snm3C integration.
- cell_counts: Cell number in each cell group, used to plot size of the dots.

### File Name

MERFISH.GenePanel.txt

### Describtion

Genes included in our CEMBA MERFISH gene penel.

#### Folder Name

palette

#### Folder Describtion

Palette for Class, SubClass, MajorRegion, SubRegion, DissectionRegion, CCF region and Modality in csv format.

## Integration

### Integration Results

#### File Name

mC-m3C.CellGroup.Integration.csv

#### File Describtion

#### File Column Names

- mC.CellGroup: mC cell group; Note, 4607 unique cell groups included here, some small mC cell groups found no good match in the 3C dataset.
- m3C.CellGroup: Matched m3C cell groups for each mC group.

#### File Names

- mC-ATAC.Integration.csv

#### File Describtion

#### File Column Names

- mC.CellGroup: mC cell group
- ATAC.Cells: Matched ATAC cells for each mC cell group.

### File Names

- CEMBA.mC-MERFISH.Integration.Metadata.csv
- CEMBA.m3C-MERFISH.Integration.Metadata.csv

### File Describtion

### File Column Names

- merfish_cell: Corresponding merfish cell for each mC/m3C nuclei
- standard_center_x, standard_center_y: Imputed spatial coordinates for the mC/m3C nuclei
- sample: sample name; note that spatial coordinates means their coordinated on each sample
- MajorRegion, SubRegion: Brain regions at different resolution
- NeuroTransmitters, Class, SubClass: Cell type annotation after integration with AIBS 10X RNA taxonomy at the different resolution

#### File Name

CEMBA.mC-AIBS_MERFISH.Integration.Metadata.csv

#### File Describtion

#### File Column Names

- merfish_cell: matched merfish cell for mC nuclei
- global3D_0, global3D_1: Imputed spatial coordinates for the mC nuclei
- Merfish_slice: Merfish slice ID, in total of 54 merfish slices from aterior to posterior; note that spatial coordinates means their coordinated on each merfish slice
- MajorRegion,SubRegion: Brain regions at different resolution
- NeuroTransmitters, Class, SubClass: Cell type annotation after integration with AIBS 10X RNA taxonomy at the different resolution

## Processed Result

#### File Name:

TotalGeneDMRTF.NNZCorrRecords.All.Filtered.hdf

#### File Describtion

#### File Column Names

- gene, gene_name: Gene Ensembl ID (vm23) and gene name
- tf, tf_name: TF Ensembl ID (vm23) and gene name
- dmr: DMR group ID
- loop: Cis-loop ID
- gene-dmr-corr: Person correlation between gene mCH and DMR mCG level among neuronal cell groups
- gene-dot-corr: Person correlation between gene mCH and contact strength among neuronal cell groups
- tf-dmr-corr: Person correlation between TF mCH and DMR mCG level among neuronal cell groups
- gene-tf-corr: Person correlation between gene and TF mCH level among neuronal cell groups
- final-corr: average correlation between gene-dmr-tf

#### Folder Name:

CEMBA.snmC.mcds

#### Folder Describtion

snmC dataset cell-by-gene/5kb/100kb mCH and mCG normalized fraction

#### Folder Name:

CEMBA.snmC.L4RegionAgg.zarr

#### Folder Describtion

cell-group-by-gene/100kb mCH and mCG normalized fraction.

#### Folder Name:

CEMBA.snmC.L4Region.AIBS_TENX.log1pCPM.zarr

#### Folder Describtion

cell-group-by-gene RNA log1p(CPM)

#### Folder Name:

CEMBA.snmC.AllGroupedDMRs.mCGATACQnorm.zarr

#### Folder Describtion

cell-group-by-DMR mCG quantile normalized fraction and ATAC quantile normalized counts

#### Folder Name:

TotalWatershedCell.BasicFilter.zarr

#### Folder Describtion

CEMBA MERFISH dataset cell-by-gene RNA raw count

#### Folder Name

mc_bigwig

#### Folder Describtion

Subclass pseudo-bulk mCH and mCG fraction tracks.

#### Folder Name

atac_bigwig

#### Folder Describtion

Subclass pseudo-bulk ATAC CPM track.

#### Folder Name

m3c_bigwig

#### Folder Describtion

Subclass pseudo-bulk compartment score and domain probability tracks.

#### Folder Name

m3c_mcool

#### Folder Describtion

Subclass pseudo-bulk imputed 10K resolution 3C matrix, imputed 100K resolution 3C matrix and raw 10K resolution 3C matrix. Only cis contacts are kept.

## Singel-cell files

#### Folder Name

single-cell Fastq, Bam and AllC files for snmC-seq and snm3C-seq dataset.
