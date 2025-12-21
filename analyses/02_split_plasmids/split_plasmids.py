import re
import gzip
from pathlib import Path
from tqdm import tqdm
import logging
import hydra
from omegaconf import DictConfig, OmegaConf
import pandas as pd
from Bio import SeqIO


log = logging.getLogger(__name__)


PLASMID_REGEX = re.compile(
    r"\bplasmids?\b|" # \b excludes "mycoplasmid"
    r"extrachromosomal|"
    r"\bInc[A-Z0-9]+[-_a-z0-9]*\b|" # Incompatibility group e.g. IncF, IncFII, IncP-1
    r"\bInc\s+group\b|" # e.g. Inc group
    r"\bp[A-Za-z]{2,}\d+|" # naming convention (p + <2 alphabets + number) e.g. pBR322, pXO1
    r"megaplasmid", 
    re.IGNORECASE
)
CHROMOSOME_REGEX = re.compile(
    r"\bchromosomes?\b|" # Chromosome
    r"complete\s+genome|" # Complete Genome
    r"main\s+genome", # Main Genome
    re.IGNORECASE
)


def classify_sequence(description):
    """Classify sequence type & its reason based on its header.
    """
    p_match = PLASMID_REGEX.search(description)
    if p_match:
        return "plasmid", f"match={p_match.group(0)}"
    c_match = CHROMOSOME_REGEX.search(description)
    if c_match:
        return "chromosome", f"match={c_match.group(0)}"
    return "unknown", "no_match"


def process_genome(
        file_path: Path, 
        target_dir: Path, 
        cfg: DictConfig
):
    """"Split single genome file into chromosome & plasmid.
    Args: 
        file_path (Path): Path to original genome file (.fna.gz)
        target_dir (Path): Directory path to output chromosome & plasmids
        cfg (DictConfig): Config
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    name = file_path.name
    for ext in ['.gz', '.fna', '.fa', '.fasta']:
        name = name.replace(ext, "")
    # file_name = file_path.name
    # stem = file_name.replace(".fna.gz", "").replace(".fna", "")

    chromosome_path = target_dir/f"{name}_chromosome.fna.gz"
    plasmid_path = target_dir/f"{name}_plasmid.fna.gz"
    if chromosome_path.exists(): # for resume function
        p_path_str = str(plasmid_path) if plasmid_path.exists() else None
        return "skipped", str(chromosome_path), p_path_str

    try:
        # Split
        records_chromosome, records_plasmid = [], []
        with gzip.open(file_path, 'rt') as f:
            for record in SeqIO.parse(f, "fasta"):
                seq_type, reason = classify_sequence(record.description)
                record.description += f" [seq_type={seq_type}] [class_reason={reason}]"
                if seq_type == "plasmid":
                    records_plasmid.append(record)
                elif seq_type == "chromosome":
                    records_chromosome.append(record)
                else: # unknown
                    if cfg.unknown_mode == "chromosome":
                        record.description += " [seq_type=unknown]"
                        records_chromosome.append(record)
                    elif cfg.unknown_mode == "discard":
                        pass
                    
        # Output
        c_path_str, p_path_str = None, None
        if records_chromosome:
            with gzip.open(chromosome_path, 'wt') as f:
                SeqIO.write(records_chromosome, f, "fasta")
            c_path_str = str(chromosome_path)
        if records_plasmid:
            with gzip.open(plasmid_path, 'wt') as f:
                SeqIO.write(records_plasmid, f, "fasta")
            p_path_str = str(plasmid_path)
            
        return "success", c_path_str, p_path_str

    except Exception as e:
        log.error(f"Error processing {file_path.name}: {e}")
        return "error", None, None


@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig):
    log.info("Starting Genome Split Process...")
    log.info(f"Config:\n{OmegaConf.to_yaml(cfg)}")

    # Path
    gtdb_dir = Path(cfg.paths.gtdb_dir).resolve()
    gtdb_split_dir = Path(cfg.paths.gtdb_split_dir).resolve()

    # Metadata
    log.info(f"Loading metadata from {cfg.paths.metadata}...")
    df = pd.read_csv(cfg.paths.metadata, sep='\t', low_memory=False)
    df = df[df["file_status"] == 'found']
    log.info(f"Target genomes to process: {len(df)}")

    # Perform splitting
    summary = []
    stats = {"success": 0, "skipped": 0, "error": 0}
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        accession = row['accession']
        
        original_path = Path(row['local_file_path']).resolve()
        rel_path = original_path.relative_to(gtdb_dir)
        target_dir = gtdb_split_dir/rel_path.parent

        status, c_path, p_path = process_genome(original_path, target_dir, cfg)
        stats[status] += 1
        if status in ["success", "skipped"] and c_path is not None:
            summary.append({
                "accession": accession, 
                "chromosome_path": c_path, 
                "plasmid_path": p_path
            })

    # Output summary
    summary_path = Path("split_summary.csv")
    pd.DataFrame(summary).to_csv(summary_path, index=False) # assume hydra.job.chdir: True

    log.info(f"Processing complete. Stats: {stats}")
    log.info(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()