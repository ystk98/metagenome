# Overview
This document is record of procedure to create training (& others) datasets.

# Commands
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