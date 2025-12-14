import os
import yaml
import gzip
import logging
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict, Tuple
import hydra
from omegaconf import DictConfig, OmegaConf
import multiprocessing
import math
import random
from itertools import groupby
from functools import partial
import numpy as np
import pandas as pd
from Bio.Seq import Seq


log = logging.getLogger(__name__)


class GenomeSampler():
    """Initializes the GenomeSampler.

    Args:
        cfg (DictConfig): Hydra configuration object containing dataset parameters.
    """
    def __init__(self, cfg: DictConfig):
        self.min_len = cfg.dataset.min_len
        self.max_len = cfg.dataset.max_len
        self.expected_contig_len = (self.min_len + self.max_len)/2 # for coverage-based sampling
        self.decay = cfg.dataset.decay
        # self.plasmid_action = cfg.dataset.plasmid_action
        # self.plasmid_label_name = cfg.dataset.plasmid_label_name

    def parse_fasta(self, file_path: Path) -> Dict[str, List]:
        """Parses a FASTA file and handles plasmid logic.

        Args:
            file_path (Path): Path to the gzipped FASTA file.

        Returns:
            Dict[str, List]: A dictionary where keys are sequence IDs and values are 
            lists containing [sequence_string, probability_map, is_plasmid_flag].
        """
        seqdict = {}
        try:
            with gzip.open(file_path, 'rt') as f:
                fasta_iter = (x[1] for x in groupby(f, key=lambda line: line[0] == ">"))
                
                for header_obj in fasta_iter:
                    header_line = str(header_obj.__next__()).strip()
                    header_id = header_line[1:].split()[0] # e.g. ">NC_000913.3 Escherichia coli..." -> "NC_000913.3"
                    
                    seq_lines = fasta_iter.__next__()
                    seq = "".join(s.strip() for s in seq_lines)

                    # # Plasmid Check
                    # is_plasmid = "plasmid" in header_line.lower()
                    # if is_plasmid:
                    #     if self.plasmid_action == "exclude":
                    #         continue # Skip
                    #     elif self.plasmid_action == "separate_label":
                    #         seqdict[header_id] = [seq, np.ones(len(seq)), True] # ?
                    #         continue
                
                    seqdict[header_id] = [seq, np.ones(len(seq)), False] # sequence, prob. map, is_plasmid

        except Exception as e:
            log.warning(f"Error parsing {file_path}: {e}")
            return {}

        return seqdict

    def sample_from_genome(
            self, 
            row: Tuple, 
            num_contigs: int
    ) -> pd.DataFrame:
        """Samples contigs from a genome based on target coverage.

        Args:
            row (Tuple): A row from the manifest DataFrame
            num_contigs (int): Number of contigs to generate

        Returns:
            pd.DataFrame: A DataFrame containing generated contigs 
            with columns ['sequence', 'label', 'local_file_path'].
        """
        path = getattr(row, "local_file_path")

        record_dict = self.parse_fasta(path)
        contig_list = []
        keys = list(record_dict.keys())
        attempts = 0
        
        # Sampling
        while len(contig_list) < num_contigs:
            attempts += 1
            if attempts > num_contigs*5:
                log.warning(
                    f"Max attempts reached for {path}. \
                    Generated {len(contig_list)}/{num_contigs*5}"
                )
                break

            seq_id = random.choice(keys)
            seq_data = record_dict[seq_id]
            
            genome = Seq(seq_data[0])
            genome_len = len(genome)
            prob_map = seq_data[1]
            # is_plasmid = seq_data[2]
            
            if genome_len < self.min_len: # ?
                continue

            # Sample contig length
            sample_len = random.randint(self.min_len, min(genome_len, self.max_len))
            half_len = sample_len/2
            
            # Sample start index
            min_idx = math.floor(half_len)
            max_idx = genome_len - math.ceil(half_len)
            
            if min_idx >= max_idx:
                start = 0
                stop = genome_len
            else:
                # 確率マップに基づいて中心点を選択
                reg_factor = np.sum(prob_map[min_idx:max_idx])
                p_dist = prob_map[min_idx:max_idx]/reg_factor
                
                base_idx = np.random.choice(range(min_idx, max_idx), p=p_dist)
                start = base_idx - math.floor(half_len)
                stop = base_idx + math.ceil(half_len)

            # 3. Generate contig from genome
            contig = genome[start:stop]

            strand = "+"
            original_start = start
            original_end = stop

            # Skip if contig contain "N"
            if "N" in contig.upper():
                continue

            # Reverse Complement
            if random.random() < 0.5:
                contig = contig.reverse_complement()
                strand = "-" # If reversed, make strand "-"
            
            # Decay probability
            prob_map[start:stop] *= self.decay
            
            # 4. ラベル決定
            # if is_plasmid and self.plasmid_action == "separate_label":
            #     label_id = self.plasmid_label_id
            
            contig_list.append({
                "sequence": str(contig),
                "label": getattr(row, 'species'),
                "local_file_path": str(path), 
                "header": seq_id, 
                "start": original_start, 
                "end": original_end, 
                "strand": strand
            })

        return pd.DataFrame(contig_list)


@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg: DictConfig):
    log.info(f"Start Dataset Generation in: {os.getcwd()}")
    log.info(f"Config:\n{OmegaConf.to_yaml(cfg)}")
    
    # 0. Fix seed
    random.seed(cfg.process.seed)
    np.random.seed(cfg.process.seed)

    # 1. Load manifest
    manifest_path = Path(cfg.paths.manifest)
    if not manifest_path.exists():
        log.error(f"Manifest not found at {manifest_path}")
        return

    df = pd.read_csv(manifest_path)
    log.info(f"Loaded manifest with {len(df)} genomes.")

    # 3. Worker
    sampler = GenomeSampler(cfg)
    tasks = list(df.itertuples(index=False)) # df is slow by Picklization

    # Calculate num_contigs
    max_genome_size = df["genome_size"].max()

    def calculate_num_contigs(coverage: float):
        total_bases = max_genome_size*coverage
        return int(total_bases/sampler.expected_contig_len)
    
    num_contigs_train = calculate_num_contigs(cfg.dataset.coverage_train)
    num_contigs_val = calculate_num_contigs(cfg.dataset.coverage_val)

    # 4. Generate training & validation dataset
    def run_generation(tasks, num_contigs, mode):
        """
        Wrapper function for multiprocessing
        """
        log.info(f"Generating {mode} dataset (Contigs={num_contigs})...")
        func = partial(sampler.sample_from_genome, num_contigs=num_contigs)
        with multiprocessing.Pool(cfg.process.num_workers) as p:
            results = list(tqdm(p.imap(func, tasks), total=len(tasks), desc=mode))
        df_result = pd.concat(results, ignore_index=True)
        return df_result

    # Training dataset
    df_train = run_generation(tasks, num_contigs_train, "Train")
    out_train = Path(cfg.paths.out_train)
    df_train.to_parquet(out_train, index=False)
    log.info(f"Train dataset saved: {out_train} (shape: {df_train.shape})")

    # Validation dataset
    df_val = run_generation(tasks, num_contigs_val, "Validation")
    out_val = Path(cfg.paths.out_val)
    df_val.to_parquet(out_val, index=False)
    log.info(f"Validation dataset saved: {out_val} (shape: {df_val.shape})")


if __name__ == "__main__":
    main()