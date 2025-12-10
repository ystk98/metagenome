# Overview
This doctument is record of environment construction.

# TOC

# Environment setup
## Command
- 2025-12-09 install pyenv
```shell
  # Install pyenv
  yasutake@luna:/nfs_share/yasutake/projects/metagenome$ git clone https://github.com/pyenv/pyenv.git ~/.pyenv
  yasutake@luna:/nfs_share/yasutake/projects/metagenome$ cd ~/.pyenv && src/configure && make -C src
  
  echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
  echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
  echo 'eval "$(pyenv init -)"' >> ~/.bashrc
  
  source ~/.bashrc

  # Install python 3.11.13 (failed!)
  yasutake@luna:/nfs_share/yasutake/projects/metagenome$ pyenv install 3.11.13
  Downloading Python-3.11.13.tar.xz...
  -> https://www.python.org/ftp/python/3.11.13/Python-3.11.13.tar.xz
  Installing Python-3.11.13...
  Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/yasutake/.pyenv/versions/3.11.13/lib/python3.11/bz2.py", line 17, in <module>
      from _bz2 import BZ2Compressor, BZ2Decompressor
  ModuleNotFoundError: No module named '_bz2'
  WARNING: The Python bz2 extension was not compiled. Missing the bzip2 lib?
  Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/yasutake/.pyenv/versions/3.11.13/lib/python3.11/curses/__init__.py", line 13, in <module>
      from _curses import *
  ModuleNotFoundError: No module named '_curses'
  WARNING: The Python curses extension was not compiled. Missing the ncurses lib?
  Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/yasutake/.pyenv/versions/3.11.13/lib/python3.11/ctypes/__init__.py", line 8, in <module>
      from _ctypes import Union, Structure, Array
  ModuleNotFoundError: No module named '_ctypes'
  WARNING: The Python ctypes extension was not compiled. Missing the libffi lib?
  Traceback (most recent call last):
  File "<string>", line 1, in <module>
  ModuleNotFoundError: No module named 'readline'
  WARNING: The Python readline extension was not compiled. Missing the GNU readline lib?
  Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/yasutake/.pyenv/versions/3.11.13/lib/python3.11/sqlite3/__init__.py", line 57, in <module>
      from sqlite3.dbapi2 import *
  File "/home/yasutake/.pyenv/versions/3.11.13/lib/python3.11/sqlite3/dbapi2.py", line 27, in <module>
      from _sqlite3 import *
  ModuleNotFoundError: No module named '_sqlite3'
  WARNING: The Python sqlite3 extension was not compiled. Missing the SQLite3 lib?
  Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/yasutake/.pyenv/versions/3.11.13/lib/python3.11/tkinter/__init__.py", line 38, in <module>
      import _tkinter # If this fails your Python may not be configured for Tk
      ^^^^^^^^^^^^^^^
  ModuleNotFoundError: No module named '_tkinter'
  WARNING: The Python tkinter extension was not compiled and GUI subsystem has been detected. Missing the Tk toolkit?
  Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/home/yasutake/.pyenv/versions/3.11.13/lib/python3.11/lzma.py", line 27, in <module>
      from _lzma import *
  ModuleNotFoundError: No module named '_lzma'
  WARNING: The Python lzma extension was not compiled. Missing the lzma lib?
  Installed Python-3.11.13 to /home/yasutake/.pyenv/versions/3.11.13
```
- 2025-12-10 Install uv
```shell
  yasutake@luna:/nfs_share/yasutake/projects/metagenome$ curl -LsSf https://astral.sh/uv/install.sh | sh
  downloading uv 0.9.16 x86_64-unknown-linux-gnu
  no checksums to verify
  installing to /home/yasutake/.local/bin
  uv
  uvx
  everything's installed!
  yasutake@luna:/nfs_share/yasutake/projects/metagenome$ source ~/.bashrc
```
- 2025-12-10 Create hyena environment
```shell
  yasutake@luna:/nfs_share/yasutake/projects/metagenome$ uv venv hyena --python 3.11

  # submodule hyena-dna
  yasutake@luna:/nfs_share/yasutake/projects/metagenome$ git submodule add https://github.com/HazyResearch/hyena-dna.git external/hyena-dna
  yasutake@luna:/nfs_share/yasutake/projects/metagenome$ git submodule update --init --recursive

  # Install libs
  (hyena) yasutake@luna:/nfs_share/yasutake/projects/metagenome$ uv pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118
  (hyena) yasutake@luna:/nfs_share/yasutake/projects/metagenome$ uv pip install packaging ninja setuptools wheel
  (hyena) yasutake@luna:/nfs_share/yasutake/projects/metagenome$ uv pip install flash-attn --no-build-isolation
  Using Python 3.11.14 environment at: hyena
  Resolved 12 packages in 70ms
    × Failed to build `flash-attn==2.8.3`
    ├─▶ The build backend returned an error
    ╰─▶ Call to `setuptools.build_meta:__legacy__.build_wheel` failed (exit status: 1)

        [stdout]


        torch.__version__  = 2.1.0+cu118



        [stderr]

        A module that was compiled using NumPy 1.x cannot be run in
        NumPy 2.3.3 as it may crash. To support both 1.x and 2.x
        versions of NumPy, modules must be compiled with NumPy 2.0.
        Some module may need to rebuild instead e.g. with 'pybind11>=2.12'.

        If you are a user of the module, the easiest solution will be to
        downgrade to 'numpy<2' or try to upgrade the affected module.
        We expect that some modules will need time to support NumPy 2.

        Traceback (most recent call last):  File "<string>", line 11, in <module>
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/setuptools/build_meta.py", line 432, in build_wheel
            return _build(['bdist_wheel'])
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/setuptools/build_meta.py", line 423, in _build
            return self._build_with_temp_dir(
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/setuptools/build_meta.py", line 404, in _build_with_temp_dir
            self.run_setup()
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/setuptools/build_meta.py", line 512, in run_setup
            super().run_setup(setup_script=setup_script)
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/setuptools/build_meta.py", line 317, in run_setup
            exec(code, locals())
          File "<string>", line 22, in <module>
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/torch/__init__.py", line 1382, in <module>
            from .functional import *  # noqa: F403
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/torch/functional.py", line 7, in <module>
            import torch.nn.functional as F
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/torch/nn/__init__.py", line 1, in <module>
            from .modules import *  # noqa: F403
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/torch/nn/modules/__init__.py", line 35, in <module>
            from .transformer import TransformerEncoder, TransformerDecoder, \
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/torch/nn/modules/transformer.py", line 20, in <module>
            device: torch.device = torch.device(torch._C._get_default_device()),  # torch.device('cpu'),
        /nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/torch/nn/modules/transformer.py:20: UserWarning: Failed to initialize NumPy: _ARRAY_API not found (Triggered internally at ../torch/csrc/utils/tensor_numpy.cpp:84.)
          device: torch.device = torch.device(torch._C._get_default_device()),  # torch.device('cpu'),
        /nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/torch/utils/cpp_extension.py:28: UserWarning: pkg_resources is deprecated as an API. See https://setuptools.pypa.io/en/latest/pkg_resources.html. The pkg_resources package is slated for removal as early as 2025-11-30. Refrain from using
        this package or pin to Setuptools<81.
          from pkg_resources import packaging  # type: ignore[attr-defined]
        Traceback (most recent call last):
          File "<string>", line 11, in <module>
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/setuptools/build_meta.py", line 432, in build_wheel
            return _build(['bdist_wheel'])
                  ^^^^^^^^^^^^^^^^^^^^^^^
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/setuptools/build_meta.py", line 423, in _build
            return self._build_with_temp_dir(
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/setuptools/build_meta.py", line 404, in _build_with_temp_dir
            self.run_setup()
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/setuptools/build_meta.py", line 512, in run_setup
            super().run_setup(setup_script=setup_script)
          File "/nfs_share/yasutake/projects/metagenome/hyena/lib/python3.11/site-packages/setuptools/build_meta.py", line 317, in run_setup
            exec(code, locals())
          File "<string>", line 174, in <module>
        RuntimeError: FlashAttention is only supported on CUDA 11.7 and above.  Note: make sure nvcc has a supported version by running nvcc -V.

        hint: This usually indicates a problem with the package or the build environment.
  (hyena) yasutake@luna:/nfs_share/yasutake/projects/metagenome$ uv pip install "numpy<2"
  uv pip install https://github.com/Dao-AILab/flash-attention/releases/download/v2.5.6/flash_attn-2.5.6+cu118torch2.1cxx11abiFALSE-cp311-cp311-linux_x86_64.whl --no-build-isolation # use developer's build and avoid compling with luna's cuda11.6
  (hyena) yasutake@luna:/nfs_share/yasutake/projects/metagenome$ uv pip install -r requirements.txt # This requirements is hyena-dna's one without torchtext
```
- 2025-12-11 Create hyena environment at luna
```shell
  yasutake@luna:/nfs_share/yasutake/projects/metagenome$ mv /nfs_share/yasutake/projects/metagenome ~/research/projects/
  yasutake@luna:~/research/projects/metagenome$ uv venv hyena --python 3.11
  (hyena) yasutake@luna:~/research/projects/metagenome$ uv pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118
  (hyena) yasutake@luna:~/research/projects/metagenome$ uv pip install -r requirements/hyena.txt
  (hyena) yasutake@luna:~/research/projects/metagenome$ echo "$(pwd)/external/hyena-dna" > hyena/lib/python3.11/site-packages/hyena_dna_path.pth # add external/hyena-dna path in hyena environment
```
<!-- - 2025-12-10 Create mamba environment
```shell
  yasutake@luna:/nfs_share/yasutake/projects/metagenome$ uv venv mamba --python 3.11
  (mamba) yasutake@luna:/nfs_share/yasutake/projects/metagenome$ uv pip install torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu121
  (mamba) yasutake@luna:/nfs_share/yasutake/projects/metagenome$ uv pip install packaging
  (mamba) yasutake@luna:/nfs_share/yasutake/projects/metagenome$ uv pip install setuptools wheel
  (mamba) yasutake@luna:/nfs_share/yasutake/projects/metagenome$ uv pip install --no-build-isolation "mamba-ssm[causal-conv1d]"
  (mamba) yasutake@luna:/nfs_share/yasutake/projects/metagenome$ python -c "import torch; import mamba_ssm; print(f'Mamba version: {mamba_ssm.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0)}')"
      Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "/nfs_share/yasutake/projects/metagenome/mamba/lib/python3.11/site-packages/mamba_ssm/__init__.py", line 3, in <module>
          from mamba_ssm.ops.selective_scan_interface import selective_scan_fn, mamba_inner_fn
      File "/nfs_share/yasutake/projects/metagenome/mamba/lib/python3.11/site-packages/mamba_ssm/ops/selective_scan_interface.py", line 20, in <module>
          import selective_scan_cuda
      ImportError: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.32' not found (required by /nfs_share/yasutake/projects/metagenome/mamba/lib/python3.11/site-packages/selective_scan_cuda.cpython-311-x86_64-linux-gnu.so)
  (mamba) yasutake@luna:/nfs_share/yasutake/projects/metagenome$ uv cache clean
  (mamba) yasutake@luna:/nfs_share/yasutake/projects/metagenome$ uv pip uninstall mamba-ssm causal-conv1d
  (mamba) yasutake@luna:/nfs_share/yasutake/projects/metagenome$ uv pip install --no-cache-dir --no-build-isolation --no-binary mamba-ssm --no-binary causal-conv1d "mamba-ssm[causal-conv1d]"
  uv pip freeze > requirements/mamba.txt
``` -->