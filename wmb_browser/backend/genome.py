import numpy as np
import pandas as pd

ENCODE_BLACKLIST_PATH = "/ref/blacklist/mm10-blacklist.v2.bed.gz"
GENCODE_MM10_vm23 = "/ref/mm10/gencode/biccn/modified_gencode.vM23.primary_assembly.annotation.gene.flat.tsv.gz"
MM10_TF_GENE_TABLE_PATH = "/ref/SCENIC/allTFs_mm.gene_info.csv"
MM10_MAIN_CHROM_SIZES_PATH = "/ref/mm10/mm10.main.chrom.sizes"


class MM10GenomeRef:
    def __init__(self):
        self.ENCODE_BLACKLIST_PATH = ENCODE_BLACKLIST_PATH
        self.GENCODE_MM10_vm23 = GENCODE_MM10_vm23
        self.TF_GENE_TABLE_PATH = MM10_TF_GENE_TABLE_PATH
        self.MAIN_CHROM_SIZES_PATH = MM10_MAIN_CHROM_SIZES_PATH

        self._gene_meta = None
        self._gene_id_to_name = None
        self._gene_name_to_id = None
        self._gene_id_base_to_name = None
        self._gene_name_to_id_base = None
        self._tf_gene_table = None
        self._get_gene_id_name_dict()
        return

    def get_gene_metadata(self):
        if self._gene_meta is None:
            self._gene_meta = pd.read_csv(self.GENCODE_MM10_vm23, sep="\t", index_col="gene_id")
        return self._gene_meta

    def get_gene_bed(self):
        df = self.get_gene_metadata().reset_index()
        df = df[["chrom", "start", "end", "gene_id", "strand"]].copy()
        return df
    
    def get_gene_region(self, gene):
        if gene.startswith("ENSMUSG"):
            gene_id = gene
        else:
            gene_id = self.gene_name_to_id(gene)
        chrom, start, end = self.get_gene_metadata().loc[gene_id, ["chrom", "start", "end"]]
        return f'{chrom}:{start}-{end}'

    def _get_gene_id_name_dict(self):
        self._gene_id_to_name = self.get_gene_metadata()["gene_name"].to_dict()

        self._gene_name_to_id = {v: k for k, v in self._gene_id_to_name.items()}
        self._gene_id_base_to_name = {k.split(".")[0]: v for k, v in self._gene_id_to_name.items()}
        self._gene_id_base_to_id = {k.split(".")[0]: k for k in self._gene_id_to_name.keys()}
        self._gene_name_to_id_base = {v: k for k, v in self._gene_id_base_to_name.items()}
        return

    def gene_id_to_name(self, gene_id, allow_nan=True):
        try:
            return self._gene_id_to_name[gene_id]
        except KeyError as e:
            try:
                return self._gene_id_base_to_name[gene_id]
            except KeyError:
                if allow_nan:
                    return np.nan
                else:
                    raise e

    def gene_name_to_id(self, gene_name, allow_nan=True):
        try:
            return self._gene_name_to_id[gene_name]
        except KeyError as e:
            if allow_nan:
                return np.nan
            else:
                raise e

    def gene_name_to_id_base(self, gene_name, allow_nan=True):
        try:
            return self._gene_name_to_id_base[gene_name]
        except KeyError as e:
            if allow_nan:
                return np.nan
            else:
                raise e

    def gene_id_base_to_id(self, gene_id_base, allow_nan=True):
        try:
            return self._gene_id_base_to_id[gene_id_base]
        except KeyError as e:
            if allow_nan:
                return np.nan
            else:
                raise e

    def get_tf_gene_table(self):
        if self._tf_gene_table is None:
            self._tf_gene_table = pd.read_csv(self.TF_GENE_TABLE_PATH)
        return self._tf_gene_table

    def get_tf_gene_ids(self):
        return pd.Index(self.get_tf_gene_table()["gene_id"].unique())

    def get_tf_gene_names(self):
        return pd.Index(self.get_tf_gene_table()["gene_name"].unique())

    def get_tf_motif_table(self):
        df = pd.read_csv(self.CISTARGET_MGI_MOTIF_TF_TABLE_PATH, sep="\t")
        return df


mm10 = MM10GenomeRef()
