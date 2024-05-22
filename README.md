# IMGW Precipitation Analysis Project

Welcome to Precipitation Analysis Project! This project focuses on downloading and preprocessing the IMGW precipitation data and producing the suitable analysis in a form of plots and metrics.

### Project structure
* data/ - template directory for storing the downloaded and preprocessed data
* outputs/ - template directory for storing the plots, reports and data produced by the pipeline
* src/ - source code

### Conda environment
To create the environment, when running the project for the first time, run below command from the main project directory:
```sh
conda env create -f env.yml
```
(Optional) Alternatively, to install locked environment, run below command from the main project directory:
```sh
conda-lock install --name spi-env conda-lock.yml
```
To update the environment run, run below command from the main project directory:
```sh
conda env update -f env.yml --prune
```
To activate the environment, run:
```sh
conda activate spi-env
```

### Running data preprocessing pipeline
To run the data download/preprocess pipeline, activate conda environment and run below command from the main project directory:
```sh
python imgw_pipeline.py --start-year {start_year} --end-year {end_year} [--download-data]
```
By default, 1990 is used as a start year and 2020 is used as an end year. Download data (`--download-data`) flag is
optional, and it implies whether the data should be downloaded and unzipped before running the pipeline. If the unzipped
data is present in default location (`data/interim`), this flag should be skipped to save time.



   
   
   

