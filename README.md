# 🌍 GenDivRange

**GenDivRange** is an open-access database of geo-referenced genetic diversity data.

🔗 Visit **www.gendivrange.org** for more information about the database and its applications.

---

## 📦 Repository Overview

This repository contains scripts used to **extract, clean, and filter data** for building the GenDivRange database.

---

## 📁 Scripts

### `GenDivRange_coords_EOL_BIOME.ipynb`
**Author:** Haonan Yang  

Jupyter Notebook used to process and enrich species occurrence data. Main tasks include:

- Adding country names to the `Geog_1` field
- Extracting from **EOL (Encyclopedia of Life)**:
  - Common names  
  - Short species overviews  
  - Species URLs
- Creating a simplified taxonomy (14 categories) based on EOL taxonomy
- Assigning **biomes** using the WWF biome database

---

### `GenDivRange_fishing.py`
**Author:** Haonan Yang  

Python script for extracting species-related data from **FishBase**  
🔗 www.fishbase.de

---

### `varver_*`
**Author:** Tin Hang Hung  

Series of Python scripts to:

- Extract data from the **VarVer** database
- Clean and harmonize datasets
- Integrate VarVer data into the GenDivRange workflow

---

### `GenDivRange_GBIFcoordinatecleaner.R`
**Authors:** Michael Noblis, Priscila Rodriguez, and Yohann Chauvier  

R script for cleaning and filtering **GBIF** occurrence records using a customized version of the **CoordinateCleaner** package.

---

## 🛠️ Requirements

- Python (for `.py` scripts and Jupyter notebooks)
- R (for GBIF coordinate cleaning)
- Access to external databases (EOL, FishBase, VarVer, WWF biomes, GBIF)

---

## 📌 Notes

- Scripts are provided for transparency and reproducibility.
- Some external data sources may require internet access or specific usage permissions.
