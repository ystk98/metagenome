import os
from pathlib import Path
import logging
import hydra
from omegaconf import DictConfig, OmegaConf
import pandas as pd


log = logging.getLogger(__name__)


@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg: DictConfig):
    """
    Generate manifest of training dataset
    
    :param cfg: Config to generate manifest of training dataset
    :type cfg: DictConfig
    """

    out_dir = Path(os.getcwd()) # Execution directory created by Hydra
    log.info(f"Working directory: {out_dir}")
    log.info(f"Configuration:\n{OmegaConf.to_yaml(cfg)}")

    # 1. Load Data
    log.info("Loading metadata...")
    df = pd.read_csv(cfg.paths.metadata, sep='\t', low_memory=False)
    df = df[df["file_status"]=='found']
    log.info(f"Total genomes matched: {len(df)}")

    # 2. Filtering
    log.info(f"Filter Conditions:")
    log.info(f"  - Category: {cfg.filter.genome_category}")
    log.info(f"  - Tool: {cfg.filter.quality_tool}")
    log.info(f"  - Completeness >= {cfg.filter.min_completeness}")
    log.info(f"  - Contamination <= {cfg.filter.max_contamination}")
    
    col_completeness = f"{cfg.filter.quality_tool}_completeness"
    col_contamination = f"{cfg.filter.quality_tool}_contamination"

    target_categories = list(cfg.filter.genome_category)
    df = df[df['ncbi_genome_category'].isin(target_categories)]
    df = df[
        (df[col_completeness] >= cfg.filter.min_completeness) & 
        (df[col_contamination] <= cfg.filter.max_contamination)
    ]
    
    if len(df) == 0:
        log.warning("No genomes found. Exiting.")
        return
    else: 
        log.info(f"Genomes after filtering: {len(df)}")

    # Output
    out_path = out_dir/cfg.manifest_name
    out_cols = [
        # Essential information
        'accession', 'local_file_path', 

        # Quality
        'genome_size', 
        'contig_count', 'mean_contig_length', 
        'longest_contig', 'n50_contigs', 
        'plasmid_count', 

        f"{col_completeness}", 
        f"{col_contamination}", 

        # Label
        'gtdb_taxonomy', 
        'domain', 'phylum', 'class', 'order', 
        'family', 'genus', 'species', 
    ]
    df[out_cols].to_csv(out_path, index=False)
    
    log.info(f"Manifest saved to: {out_path} (n={len(df)})")


if __name__ == "__main__":
    main()