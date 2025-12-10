#!/bin/bash
set -e

cd "$(dirname "$0")" || exit

OUT_DIR="../../data/gtdb"

LOG_DIR="logs"
LOG_FILE="${LOG_DIR}/$(date +%Y-%m-%d)_download.log"

URL_BASE="https://data.ace.uq.edu.au/public/gtdb/data/releases/release226/226.0/"
URL_REPS=${URL_BASE}"genomic_files_reps/gtdb_genomes_reps_r226.tar.gz"

# mkdir -p "$OUT_DIR"
mkdir -p "$LOG_DIR"

log() {
    echo "$1" | tee -a "$LOG_FILE"
}

log "Downloading GTDB representative genomes..." # High priority
wget -c --show-progress -a "$LOG_FILE" -P "$OUT_DIR" "$URL_REPS"
log "Priority download complete."

log "Downloading all GTDB files except genomic_files_all/..."
wget -r -c -np -nd --show-progress -a "$LOG_FILE" \
  -R "index.html*" \
  -X "genomic_files_all" \
  -P "$OUT_DIR" \
  "$URL_BASE"
log "All downloads complete!"