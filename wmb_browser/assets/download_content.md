# Introduction

This page explains the analysis files we used in the manuscript. Analysis files can be grouped into mainly three catagories:

1. Metadata and for snmC, snm3C and MERFISH dataset, containing information such as cell subclass annotation, brain region information and TSNE/UMAP coordinates.
2. Integration result between snmC-scRNA, snmC-snATAC, snmC-MERFISH and snm3C-MERFISH.
3. Processed result for figure reproduction, such as DMRs and BigWig tracks.
4. Single-cell files

# Metadata

### Experiment Metadata and Cell Taxonomy

<details>
  <summary>CEMBA.mC.Metadata.csv, CEMBA.m3C.Metadata.csv</summary>
  
  <b>Description</b>
  Metadata for snmC-seq and snm3C-deq dataset 
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/mCseq3/mouse/processed/other/CEMBA.mC.Metadata.csv.tar">CEMBA.mC.Metadata.csv</a></li>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/m3C-seq/mouse/processed/other/CEMBA.m3C.Metadata.csv.tar">CEMBA.m3C.Metadata.csv</a></li>
  </ul>
  
  <b>Column Names</b>
  <ul>
    <li>mCCCFrac: Used as the estimation of the upper bound of bisulfite non-conversion rate.</li>
    <li>mCGFrac, mCHFrac: Global mCG and mCH(A, C, T) methylation level of the nuclei.</li>
    <li>InputReads, FinalmCReads: Raw input reads number and reads number after filtering.</li>
    <li>MajorRegion,SubRegion, DissectionRegion, CEMBARegion: Brain regions at different resolution. Check Extended Data Figure1 for more information.</li>
    <li>NeuroTransmitters, Class, SubClass: Cell type annotation after integration with AIBS 10X RNA taxonomy at different resolution.</li>
    <li>CellGroup: Cell clusters after iterative clustering. (4,673 cell groups for snmC and 2,363 cell groups for snm3C)</li>
    <li>Plate, Col384, Row384: When sorting single nuclei to 384-well plate, information about which plate and where in that plate the nuclei comes from.</li>
    <li>Slice: Which brain slice the nuclei comes from when doing teh brain dissection; Check Extended Data Figure for more information.</li>
    <li>Sample: Sample name.</li>
    <li>Technology: Technology used, snmC-seq2, snmC-seq3 or snm3C-seq.</li>
    <li>PassBasicQC: If the nuclei passed our basic quality control.</li>
    <li>PlateNormCov: Plate-normalized cell coverage, used to filer abnormal clusters. Calculated by final mC reads of each cell divided by the average final reads of cells from the same 384-well plate.</li>
  </ul>
  
</details>

<details>
  <summary>CEMBA.mC.Coordinates.csv, CEMBA.m3C.Coordinates.csv</summary>
  
  <b>Description</b>
  Whole brain TSNE/UMAP coordinates aftern snmC and snm3C integration; For mC dataset, it also includes MajorRegion TSNE/UMAP coordinates at cell level.
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/mCseq3/mouse/processed/other/CEMBA.mC.Coordinates.csv.tar">CEMBA.mC.Coordinates.csv</a></li>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/m3C-seq/mouse/processed/other/CEMBA.m3C.Coordinates.csv.tar">CEMBA.m3C.Coordinates.csv</a></li>
  </ul>
  
  <b>Column Names</b>
  <ul>
    <li>mc_all_tsne_0, mc_all_tsne_1: TSNE coordinates of whole-dataset snmC-snm3C integration , example plot Fig 2b.</li>
    <li>mc_all_umap_0, mc_all_umap_1: UMAP coordinates of whole-dataset snmC-snm3C integration.</li>
    <li>mr_tsne_0, mr_tsne_1: TSNE coordinates of snmC-snm3C integration by major region, example plot Extended Data Figure 4.</li>
    <li>mr_umap_0, mr_umap_1: UMAP coordinates of snmC-snm3C integration by major region.</li>
  </ul>
  
</details>

<details>
  <summary>CEMBA.mC.CellGroup.Coordinates.csv, CEMBA.m3C.CellGroup.Coordinates.csv</summary>
  
  <b>Description</b>

  Whole brain TSNE/UMAP coordinates aftern snmC and snm3C integration at cell group level. For mC dataset, it also includes MajorRegion TSNE/UMAP coordinates at cell group level
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/other/CEMBA.mC.CellGroup.Coordinates.csv.tar">CEMBA.mC.CellGroup.Coordinates.csv</a></li>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/m3C-seq/mouse/processed/other/CEMBA.m3C.CellGroup.Coordinates.csv.tar">CEMBA.m3C.CellGroup.Coordinates.csv</a></li>
  </ul>
  
  <b>Column Names</b>
  <ul>
    <li>mc_all_tsne_0,mc_all_tsne_1: Centroids TSNE coordinates of cells in each cell group after whole-dataset snmC-snm3C integration , example plot Fig 2a.</li>
    <li>mc_all_umap_0,mc_all_umap_1: Centroids UMAP coordinates of cells in each cell group after whole-dataset snmC-snm3C integration.</li>
    <li>cell_counts: Cell number in each cell group, used to plot size of the dots.</li>
  </ul>
  
</details>

<details>
  <summary>MERFISH.GenePanel.txt</summary>
  
  <b>Description</b>

  Genes included in our CEMBA MERFISH gene penel. 
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/scell/mCseq3/mouse/processed/other/MERFISH.GenePanel.csv.tar">MERFISH.GenePanel.txt</a></li>
  
</details>


# Integration

### Integration Results

<details>
  <summary>mC-m3C.CellGroup.Integration.csv</summary>
  
  <b>Description</b>

  Integration result of snmC-seq and snm3C-seq. Cellgroup to cellgroup relationship.
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/other/mC-m3C.CellGroup.Integration.csv.tar">mC-m3C.CellGroup.Integration.csv</a></li>
  </ul>
  
  <b>Column Names</b>
  <ul>
    li>mC.CellGroup: mC cell group; Note, 4607 unique cell groups included here, some small mC cell groups found no good match in the 3C dataset.</li>
    <li>m3C.CellGroup: Matched m3C cell groups for each mC group.</li>
  </ul>
  
</details>

<details>
  <summary>mC-ATAC.Integration.csv</summary>
  
  <b>Description</b>

  Integration result of snmC-seq and snATAC-seq. Cellgroup to cells relationship.
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/mCseq3/mouse/processed/other/mC-ATAC.Integration.csv.tar">mC-ATAC.Integration.csv</a></li>
  </ul>
  
  <b>Column Names</b>
  <ul>
    <li>mC.CellGroup: mC cell group</li>
    <li>ATAC.Cells: Matched ATAC cells for each mC cell group.</li>
  </ul>
  
</details>

<details>
  <summary>CEMBA.mC-MERFISH.Integration.Metadata.csv, CEMBA.m3C-MERFISH.Integration.Metadata.csv</summary>
  
  <b>Description</b>

  Integration result of snmC-seq&MERFISH and snm3C-seq&MERFISH. Cell to cell to relationship.
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/mCseq3/mouse/processed/other/CEMBA.mC-MERFISH.Integration.Metadata.csv.tar">CEMBA.mC-MERFISH.Integration.Metadata.csv</a></li>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/m3C-seq/mouse/processed/other/CEMBA.m3C-MERFISH.Integration.Metadata.csv.tar">CEMBA.m3C-MERFISH.Integration.Metadata.csv</a></li>
  </ul>
  
  <b>Column Names</b>
  <ul>
    <li>merfish_cell: Corresponding merfish cell for each mC/m3C nuclei</li>
    <li>standard_center_x, standard_center_y: Imputed spatial coordinates for the mC/m3C nuclei</li>
    <li>sample: sample name; note that spatial coordinates means their coordinated on each sample</li>
    <li>MajorRegion, SubRegion: Brain regions at different resolution</li>
    <li>NeuroTransmitters, Class, SubClass: Cell type annotation after integration with AIBS 10X RNA taxonomy at the different resolution</li>
  </ul>
  
</details>


<details>
  <summary>CEMBA.mC-AIBS_MERFISH.Integration.Metadata.csv</summary>
  
  <b>Description</b>

  Integration result of snmC-seq and AIBS whole mouse brain MERFISH dataset. Cell to cell relationship.
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/mCseq3/mouse/processed/other/CEMBA.mC-AIBS_MERFISH.Integration.Metadata.csv.tar">CEMBA.mC-AIBS_MERFISH.Integration.Metadata.csv</a></li>
  </ul>
  
  <b>Column Names</b>
  <ul>
    <li>merfish_cell: matched merfish cell for mC nuclei</li>
    <li>global3D_0, global3D_1: Imputed spatial coordinates for the mC nuclei</li>
    <li>Merfish_slice: Merfish slice ID, in total of 54 merfish slices from aterior to posterior; note that spatial coordinates means their coordinated on each merfish slice</li>
    <li>MajorRegion,SubRegion: Brain regions at different resolution</li>
    <li>NeuroTransmitters, Class, SubClass: Cell type annotation after integration with AIBS 10X RNA taxonomy at the different resolution</li>
  </ul>
  
</details>



# Processed Result

<details>
  <summary>TotalGeneDMRTF.NNZCorrRecords.All.Filtered.csv</summary>
  
  <b>Description</b>

  Gene Regulatory Network result. From Figure 5.
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/reconstruction/mCseq3/mouse/processed/other/TotalGeneDMRTF.NNZCorrRecords.All.Filtered.csv.tar">TotalGeneDMRTF.NNZCorrRecords.All.Filtered.csv</a></li>
  </ul>
  
  <b>Column Names</b>
  <ul>
    <li>gene, gene_name: Gene Ensembl ID (vm23) and gene name</li>
    <li>tf, tf_name: TF Ensembl ID (vm23) and gene name</li>
    <li>dmr: DMR group ID</li>
    <li>loop: Cis-loop ID</li>
    <li>gene-dmr-corr: Person correlation between gene mCH and DMR mCG level among neuronal cell groups</li>
    <li>gene-dot-corr: Person correlation between gene mCH and contact strength among neuronal cell groups</li>
    <li>tf-dmr-corr: Person correlation between TF mCH and DMR mCG level among neuronal cell groups</li>
    <li>gene-tf-corr: Person correlation between gene and TF mCH level among neuronal cell groups</li>
    <li>final-corr: average correlation between gene-dmr-tf</li>
  </ul>
  
</details>

<details>
  <summary>mc_bigwig</summary>
  
  <b>Description</b>

  Subclass pseudo-bulk mCH and mCG fraction tracks.
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/other/">mc_bigwig</a></li>
  </ul>
  
</details>

<details>
  <summary>atac_bigwig</summary>
  
  <b>Description</b>

  Subclass pseudo-bulk ATAC CPM track.
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/sci_ATACseq/mouse/processed/other/">atac_bigwig</a></li>
  </ul>
  
</details>

<details>
  <summary>m3c_bigwig</summary>
  
  <b>Description</b>

  Subclass pseudo-bulk compartment score and domain probability tracks.
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/m3C-seq/mouse/processed/other/">m3c_bigwig</a></li>
  </ul>
  
</details>


<details>
  <summary>CEMBA.snmC.mcds</summary>
  
  <b>Description</b>

  snmC dataset cell-by-gene/5kb/100kb mCH and mCG normalized fraction
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/counts/CEMBA.snmC.mcds.tar.gz">CEMBA.snmC.mcds</a></li>
  </ul>
  
</details>


<details>
  <summary>CEMBA.snmC.L4RegionAgg.zarr</summary>
  
  <b>Description</b>

  cell-group-by-gene/100kb mCH and mCG normalized fraction.
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/counts/CEMBA.snmC.L4RegionAgg.tar.gz">CEMBA.snmC.L4RegionAgg.zarr</a></li>
  </ul>
  
</details>


<details>
  <summary>CEMBA.snmC.L4Region.AIBS_TENX.log1pCPM.zarr</summary>
  
  <b>Description</b>

  cell-group-by-gene RNA log1p(CPM)
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/counts/CEMBA.snmC.L4Region.AIBS_TENX.log1pCPM.tar.gz">CEMBA.snmC.L4Region.AIBS_TENX.log1pCPM.zarr</a></li>
  </ul>
  
</details>

<details>
  <summary>CEMBA.snmC.AllGroupedDMRs.mCGATACQnorm.zarr</summary>
  
  <b>Description</b>

  cell-group-by-DMR mCG quantile normalized fraction and ATAC quantile normalized counts
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/counts/CEMBA.snmC.AllGroupedDMRs.mCGATACQnorm.tar.gz">CEMBA.snmC.AllGroupedDMRs.mCGATACQnorm.zarr</a></li>
  </ul>
  
</details>

<details>
  <summary>TotalWatershedCell.BasicFilter.zarr</summary>
  
  <b>Description</b>

  CEMBA MERFISH dataset cell-by-gene RNA raw count
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/mCseq3/mouse/processed/counts/MERFISH.TotalWatershedCell.BasicFilter.tar.gz">TotalWatershedCell.BasicFilter.zarr</a></li>
  </ul>
  
</details>

<details>
  <summary>m3c_mcool</summary>
  
  <b>Description</b>

  Subclass pseudo-bulk imputed 10K resolution 3C matrix, imputed 100K resolution 3C matrix and raw 10K resolution 3C matrix. Only cis contacts are kept.
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/cellgroup/m3C-seq/mouse/processed/counts/">m3c_mcool</a></li>
  </ul>
  
</details>


# Singel-cell files

<details>
  <summary>snmC-seq.single-cell.files</summary>
  
  <b>Description</b>

  single-cell Fastq, Bam and AllC files for snmC-seq dataset.
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/mCseq/mouse/">snmC-seq.single-cell.files</a></li>
  </ul>
  
</details>

<details>
  <summary>snm3C-seq.single-cell.files</summary>
  
  <b>Description</b>

  single-cell Fastq, Bam and AllC files for snm3C-seq dataset.
  
  <b>Download Links</b>
  <ul>
  <li><a href="https://data.nemoarchive.org/biccn/grant/u19_cemba/ecker/epigenome/sncell/m3C-seq/mouse/">snm3C-seq.single-cell.files</a></li>
  </ul>
  
</details>
