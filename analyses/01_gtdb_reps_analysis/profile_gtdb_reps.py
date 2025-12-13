import yaml
import argparse
from pathlib import Path
from datetime import datetime
import logging
import gzip
from multiprocessing import Pool
from tqdm import tqdm
import pandas as pd


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata_bac", default="../../data/gtdb/226.0/bac120_metadata_r226.tsv.gz")
    parser.add_argument("--metadata_ar", default="../../data/gtdb/226.0/ar53_metadata_r226.tsv.gz")
    parser.add_argument("--genome_dir", default="../../data/gtdb/226.0/genomic_files_reps/gtdb_genomes_reps_r226/database/")
    parser.add_argument("--n_workers", type=int, default=32)
    return parser.parse_args()


def load_metadata(path_bac, path_ar):
    """
    Load & concatenate bacterial & archaeal metadata.
    
    :param path_bac: Path to metadata of bacteria
    :param path_ar: Path to metadata of archaea
    """
    log.info("Loading metadata...")
    df_bac = pd.read_csv(path_bac, sep='\t', dtype=str)
    df_ar = pd.read_csv(path_ar, sep='\t', dtype=str)

    df = pd.concat([df_bac, df_ar], ignore_index=True)
    log.info(f"Bacterial genomes in metadata: {len(df_bac)}")
    log.info(f"Archaeal genomes in metadata: {len(df_ar)}")
    log.info(f"Total genomes in metadata: {len(df)}")

    return df


def get_file_path(accession, genome_dir):
    """
    Get genome file (.fna.gz) path with specific GTDB accession.
    
    :param accession: GTDB accession of genome
    :param genome_dir: Base directory path
    """
    accession = accession.replace("GB_", "").replace("RS_", "") # remove prefix
    
    try:
        source, acc = accession.split('_')
        num = acc.split('.')[0]
        p1, p2, p3 = num[0:3], num[3:6], num[6:9]
    except Exception:
        return None

    tgt_dir = Path(genome_dir)/source/p1/p2/p3
    files = list(tgt_dir.glob(f"{accession}*genomic.fna.gz"))

    return files[0] if files else None


def get_single_genome_info(args: tuple):
    """
    Wrapper function to get single information for multi-processing
    
    :param args: Tuple containing (accession, genome_dir)
    """
    accession, genome_dir = args
    path = get_file_path(accession, genome_dir)
    result = {
        "accession": accession, 
        "local_file_path": None, 
        "file_status": "missing",
        "plasmid_count": None
    }
    if path is None:
        return result # initial value if file not found

    # count plasmid number in header
    plasmid_count = 0
    try:
        with gzip.open(path, 'rt') as f:
            for line in f:
                if line.startswith('>'):
                    if 'plasmid' in line.lower():
                        plasmid_count += 1               
        result.update({
            "local_file_path": str(path), 
            "file_status": "found", 
            "plasmid_count": plasmid_count
        })
    except Exception:
        result["file_status"] = "error"

    return result


def main():
    args = parse_args()
    args.metadata_bac = str(Path(args.metadata_bac).resolve())
    args.metadata_ar = str(Path(args.metadata_ar).resolve())
    args.genome_dir = str(Path(args.genome_dir).resolve())

    # Output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_dir = Path.cwd()/"out"/timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir/"config.yaml", 'w') as f:
        yaml.dump(vars(args), f, default_flow_style=False)

    # Logging
    file_handler = logging.FileHandler(out_dir/"profile.log")
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)

    # load metadata
    df = load_metadata(args.metadata_bac, args.metadata_ar)
    accessions = df["accession"].tolist()

    task_args = [(acc, args.genome_dir) for acc in accessions]
    log.info(f"Start processing {len(task_args)} genomes with {args.n_workers} workers...")
    
    # Count 'plasmids'
    with Pool(args.n_workers) as pool:
        imap = pool.imap_unordered(get_single_genome_info, task_args)
        results = list(tqdm(imap, total=len(task_args)))

    df_res = pd.DataFrame(results)

    # Merge & N_ratio
    log.info("Merging results...")
    df_ex = pd.merge(df, df_res, on="accession", how="left")
    ambiguous = pd.to_numeric(df_ex['ambiguous_bases'], errors='coerce')
    genome_size = pd.to_numeric(df_ex['genome_size'], errors='coerce')
    df_ex['N_ratio'] = ambiguous/genome_size

    # Taxonomy
    log.info("Splitting taxonomy into columns...")
    tax_cols = ["domain", "phylum", "class", "order", "family", "genus", "species"]
    df_tax = df_ex['gtdb_taxonomy'].str.split(';', expand=True)
    if df_tax.shape[1] == 7:
        df_tax.columns = tax_cols
        df_ex = pd.concat([df_ex, df_tax], axis=1)
    else:
        log.warning("Taxonomy column format was unexpected. Skipping split.")

    # Output
    out_path = out_dir/"metadata_ex.tsv"
    df_ex.to_csv(out_path, sep='\t', index=False)
    log.info(f"Done. Saved to {out_path}")

if __name__ == "__main__":
    main()