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