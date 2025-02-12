GenDivRange is a database for open access geo-referenced genetic diversity data. Visit www.gendivrange.org for further information.

This repository contains scripts that were used to extract, clean and filter data for creating the database.

**GenDivRange_coords_EOL_BIOME.ipynb:**\
Author: Haonan Yang\
Python script to check/do:\
- add the country name to Geog_1\
- extract from EOL the common name, and short overview of the species, species URL in EOL\
- create easy taxonomy (14 categories) based on EOL taxonomy\
- get BIOME from WWF database

**GenDivRange_fishing.py:**\
Author: Haonan Yang\
Pyhon script to extract data from www.fishbase.de

**varver_*:**\
Author: Tin Hang Hung\
Series of Python scripts to extract, clean, integrate data from the VarVer database.

**doi_search.py:**\
Author: GenDivRange
Python script to reverse look up the DOI of published studies from VarVer with the CrossRef title with a minimum Levenshtein ratio match of 0.9 using unibiAPC (\url{doi.org/10.4119/UNIBI/UB.2014.18}).

**GenDivRange_GBIFcoordinatecleaner.R**\
Authors: Michael Noblis, Priscila Rodrigez and Yohann Chauvier\
Cleaning and filtering the GBIF observations using a customized version of the CoordinateCleaner package.
