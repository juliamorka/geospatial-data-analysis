# IMGW Precipitation Analysis Project

Welcome to Precipitation Analysis Project! This project focuses on downloading and preprocessing the IMGW precipitation data and producing the suitable analysis in a form of plots and metrics.

### Project structure
------------------------
* data/ - template directory for storing the downloaded and preprocessed data
* src/ - source code
 -----------------------

### Running data preprocessing pipeline
To run the data download/preprocess pipeline, activate conda environment and run below command from the main project directory:
```sh
python src/precip_data_scrapper.py --start-year {start_year} --end-year {end_year}
```
By default, 1990 is used as a start year and 2020 is used as an end year.



   
   
   

