# Overview
This document is record of procedure to create training (& others) datasets.

# 00_download_gtdb
## Objective
- Download GTDB release 226.0 representative genomes & other files to generate training dataset & other analysis
## Command
- 2025-12-11 Setup
```shell
    (hyena) yasutake@luna:~/research/projects/metagenome$ mkdir /nfs_share/yasutake/projects/metagenome/gtdb
    (hyena) yasutake@luna:~/research/projects/metagenome$ ln -s /nfs_share/yasutake/projects/metagenome/gtdb ./data/gtdb
```
- 2025-12-11 Download GTDB
```shell
    (hyena) yasutake@luna:~/research/projects/metagenome$ tmux new -s download
    yasutake@luna:~/research/projects/metagenome/analyses/00_download_gtdb$ bash download.sh
```

# 01_gtdb_reps_analysis
## Objective
- Determine genomes to include training dataset
## Method
- Generate concatenated & extended metadata
- Analyse metadata
## Command
- 2025-12-12 Unfreeze GTDB representative genomes
```shell
    (hyena) yasutake@luna:~/research/projects/metagenome/data/gtdb/226.0$ grep "gtdb_genomes_reps_r226.tar.gz" MD5SUM.txt | md5sum -c - # check whether file broken
    ./genomic_files_reps/gtdb_genomes_reps_r226.tar.gz: OK
    (hyena) yasutake@luna:~/research/projects/metagenome/data/gtdb$ tar -I pigz -xvf gtdb_genomes_reps_r226.tar.gz
```
- 2025-12-12 Get profile of gtdb representatives
```shell
    (hyena) yasutake@luna:~/research/projects/metagenome/analyses/01_gtdb_reps_analysis$ python profile_gtdb_reps.py 
```

# 02_generate_manifest
## Objective
- Generate manifest file to genedate training dataset
## Command
- 2025-12-14 Perform generation with isolated genomes only
```shell
    yasutake@luna:~/research/projects/metagenome$ python analyses/02_generate_manifest/generate_manifest.py 
```