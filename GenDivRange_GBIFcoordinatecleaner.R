# ============================================================================== .
# =  GenDivRange: cleaning gbif coordinates                            2025/02 = .
# =                                                                            = .
# =  input:   gbif downloads, for each species stored as zip files             = .
# =           file names: species + gbif key like "Abies alba - 2685484.zip"   = . 
# =  output:  data.frame of cleaned coordinates for each species as rds file   = .
# =           file names: species + ".rds" like "Abies alba.rds"               = .
# =  authors: Michael Nobis (michael.nobis@wsl.ch)                             = .
# =           Priscila Rodriguez  (priscila.rodriguez@ulpgc.es)                = .
# =           Yohhann Chauvier (yohann.chauvier@wsl.ch                         = .
# ============================================================================== .

# initialization --------------------------------------------------------------- ----

  setwd(dirname(rstudioapi::getSourceEditorContext()$path)) # RStudio only
  inPath  <- ".//output//downloads_gbif//"
  outPath <- ".//output//coordinates_cleaned//"
  
  library(CoordinateCleaner)
  library(data.table)
  library(doMC)

# list of zip files and species names from file names -------------------------- ----
# note that these zip files contain the data and the request itself (date + request parameters)

  inFiles <- list.files(inPath, ".zip", full.names = FALSE)
  taxa <- plyr::ldply(strsplit(inFiles, " "), rbind)
  taxa <- paste(taxa[,1], taxa[,2])       
  
# coordinate cleaning with loop over species ----------------------------------- ----
  
  # registerDoMC(cores=10)
  # foreach (i=1:length(taxa),.packages=c("CoordinateCleaner")) %dopar% {

  for (i in 1:length(taxa)) { # use normal loop in case of RAM issues
    # species coordinates already processed?
    if (!file.exists(paste0(outPath, taxa[i],".rds")))  {
      
      # unzip and read GBIF download
      tmp_dir <- paste0(".//tmp//", taxa[i])
      dir.create(tmp_dir)
      unzip(paste0(inPath, inFiles[i]), exdir = tmp_dir)
      unzip(list.files(tmp_dir, ".zip", full.names = TRUE)[1], 'occurrence.txt', exdir = tmp_dir)
      
      # # # get DOI
      # library(rgbif)
      # library(stringr)
      # dl_meta  <- readRDS(list.files(tmp_dir, ".rds", full.names = TRUE))
      # citation <- gbif_citation(occ_download_meta(dl_meta))$download
      # doi      <- substr(citation, str_locate(citation, "doi.org")[1,1],
      #                              str_locate(citation, "Accessed")[1,1]-2)

      # read gbif occurrence.txt and convert some column types
      tab <- fread(paste0(tmp_dir,"//occurrence.txt"), quote = "")
      
      tab$decimalLatitude=as.numeric(tab$decimalLatitude)
      tab$decimalLongitude=as.numeric(tab$decimalLongitude)
      tab$coordinateUncertaintyInMeters=as.numeric(tab$coordinateUncertaintyInMeters)

      # check coordinates out of range
      tab$decimalLatitude[abs(tab$decimalLatitude)>90] <- NA
      tab$decimalLatitude[abs(tab$decimalLongitude)>180] <- NA
      tab <- tab[!is.na(tab$decimalLatitude) & !is.na(tab$decimalLongitude),]
      
      if (!nrow(tab)==0){
          
        # filter duplicated coordinates; there are often many duplicates and this
        # often significantly reduces the runtime of clean_coordinates() afterwards
        sel <- which(duplicated(tab[, c("decimalLongitude","decimalLatitude")]))
        if (!identical(sel,integer(0))) { tab <- tab[-sel,] }

        # CoordinateCleaner part
        flags=try(clean_coordinates(x=tab,lon="decimalLongitude",lat="decimalLatitude",
                                    countries="countryCode",species="species",
                                    tests=c("capitals","centroids","equal","gbif",
                                            "institutions","zeros")))
        tab <- tab[flags$.summary,]
  
        # Coordinate uncertainty
        prec.ok <- sum(tab$coordinateUncertaintyInMeters/1000<=5,na.rm=TRUE)
        if(prec.ok>nrow(tab)*0.8) {
          sel <- which(tab$coordinateUncertaintyInMeters>5000)
          if (!identical(sel,integer(0))) {
            tab <- tab[-sel,]
          }
        } else {
          sel <- which(tab$coordinateUncertaintyInMeters>10000)
          if (!identical(sel,integer(0))) {
            tab <- tab[-sel,]
          }
        }
        
        # Basis of records (keep only "natural" records)
        BR <- c("HUMAN_OBSERVATION", "LITERATURE", "MATERIAL_SAMPLE",
                "MATERIAL_CITATION", "OBSERVATION","MACHINE_OBSERVATION")
        sel <- which(tab$basisOfRecord %in% BR)
        if (!identical(sel,integer(0))) { tab <- tab[sel,] }

        # Check degreeOfEstablishment
        DOE <- c("managed", "captive", "cultivated", "released",
                 "unestablished", "failing")
        sel <- which(tab$basisOfRecord %in% DOE)
        if (!identical(sel,integer(0))) { tab <- tab[-sel,] }
        
        # Absences
        sel <- which(tab$individualCount == 0)
        if (!identical(sel,integer(0))) { tab <- tab[-sel,] }
        
        # Save cleaned coordinates
        if (!nrow(tab)==0){
          saveRDS(tab, file = paste0(outPath, taxa[i], ".rds"))
        }
  
        # remove variables
        rm("tab"); rm("flags"); rm("sel"); gc()
        
      }
      
      # delete tmp_dir
      unlink(tmp_dir, recursive = TRUE)

    }  
  }  
  
# EOF
