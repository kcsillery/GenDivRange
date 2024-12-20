GenDivRange is a database for open access geo-referenced genetic diversity data. Visit www.gendivrange.org for further information.

This repository contains scripts that were used to extract, clean and filter data for creating the database.

**GenDivRange_cleaning.ipynb:**\
Author: Haonan Yang\
Python script to check/do:\
- sample size must be integer\
- He and Ho between 0 and 1\
- number of populations at least 5\
- check if 4 letter species code is unique\
- add the country name to Geog_1\
- extract from EOL the common name, and short overview of the species, species URL in EOL\
- calculate number of loci for varver and macropopgen data\
- create easy taxonomy (14 categories) based on EOL taxonomy\
- get BIOM from WWF database

**GenDivRange_fishing.py:**\
Author: Haonan Yang\
Pyhon script to extract data from www.fishbase.de

**GenDivRange_filtering_gbif_observations.R**\
Authors: Priscila Rodrigez and Yohann Chauvier\
Cleaning and filtering the GBIF observations using a customized version of the CoordinateCleaner package.

**varver_*:**\
Author: Tin Hang Hung\
Series of Python scripts to extract, clean, integrate data from the VarVer database.

**doi_search.py:**\
Python script to reverse look up the DOI of published studies from VarVer with the CrossRef title with a minimum Levenshtein ratio match of 0.9 using unibiAPC (\url{doi.org/10.4119/UNIBI/UB.2014.18}).
