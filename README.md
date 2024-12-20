**GenDivRange is a database for open access geo-referenced genetic diversity data. Visit www.gendivrange.org for further information.

This repository contains scripts that were used to extract, clean and filter data for creating the database.**

**GenDivRange_cleaning.ipynb:**

Python script to check/do:\
sample size must be integer\
He and Ho between 0 and 1\
number of populations at least 5\
check if 4 letter species code is unique\
data extraction from fishbase\
add the country name to Geog_1\
extract from EOL the common name, and short overview of the species, species URL in EOL\
calculate number of loci for varver and macropopgen data\
create easy taxonomy (14 categories) based on EOL taxonomy\
get BIOM from WWF database\


**GenDivRange_fishing.py:**

Pyhon script to extract data from www.fishbase.de\


**GenDivRange_filtering_gbif_observations.R**

Cleaning and filtering the GBIF observations using a customized version of the CoordinateCleaner package.\

**varver_*:**

Series of Python scripts to extract, clean, integrate data from the VarVer database.\
