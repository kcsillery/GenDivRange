# ###################################################################################
# Filtering GBIF observations
#
# $Date: 2022-07-08
#
# Author: Prisciall Rodrigez Rodrigez, priscila.rodriguez@ulpgc.es and Yohann Chauvier, yohann.chauvier@wsl.ch
# Evolutionary Genetics Group
# Swiss Federal Research Institute WSL
# 
# Description: GBIF observations were downloaded for species present in GenDivRange and filtered with this script
#
# ###################################################################################

### ==================================================================
### Initialise system
### ==================================================================


# Cleaning
rm(list = ls()); graphics.off()

# max.print
options(max.print=500)

# Library
library(raster)
library(countrycode)
library(CoordinateCleaner)
library(foreach)
library(doMC)

# Setwd
setwd("/lud11/Origin_Alps_bis/Data/GenDivRange")

# Load Haonan's function
source("./functions/calculate_area_GBIF_IUCN.R")


### ==================================================================
### Preps'
### ==================================================================


# Which species obs. have I download?
gbif.csv=list.files("./yohann_gbif_obs/")
gbif.csv=gbif.csv[!grepl("cc_filtered",gbif.csv)]

# Which species obs have I already CC filtered?
obs.cc=list.files("./yohann_gbif_obs/cc_filtered/")
gbif.csv=gbif.csv[!gbif.csv%in%obs.cc]


### ==================================================================
### Filtered the GBIF observations (Priscilla's code)
### ==================================================================


# Start
registerDoMC(cores=20)
foreach (i=1:length(gbif.csv),.packages=c("raster","countrycode",
	"CoordinateCleaner","foreach","doMC")) %dopar%
{

	cat(gbif.csv[i],"...","\n")

	# Manual part
	mydat=read.csv2(paste0("./yohann_gbif_obs/",gbif.csv[i]))
	if (nrow(mydat)==0) {return(NULL)}
	mydat$decimalLatitude=as.numeric(as.character(mydat$decimalLatitude))
	mydat$decimalLongitude=as.numeric(as.character(mydat$decimalLongitude))
	mydat$countryCode=countrycode(mydat$countryCode,origin='iso2c',destination='iso3c')
	mydat=mydat[!is.na(mydat$decimalLongitude)|!is.na(mydat$decimalLongitude),]
	mydat=mydat[mydat$year>1945|is.na(mydat$year),]
	if (nrow(mydat)==0) {return(NULL)}
	rownames(mydat)=1:nrow(mydat)

	# CoordinateCleaner part
	flags=try(clean_coordinates(x=mydat,lon="decimalLongitude",lat="decimalLatitude",
		countries="countryCode",species="species",tests=c("capitals","centroids","equal","gbif",
			"institutions","zeros")))
	mydat=mydat[flags$.summary,]

	# Filter
	prec.ok=sum(mydat$coordinateUncertaintyInMeters/1000<=5,na.rm=TRUE)
	if(prec.ok>nrow(mydat)*0.8) {
		Selection=which(mydat$coordinateUncertaintyInMeters>5000)
		if (!identical(Selection,integer(0))) {
			mydat=mydat[-Selection,]
		}
	} else {
		Selection=which(mydat$coordinateUncertaintyInMeters>10000)
		if (!identical(Selection,integer(0))) {
			mydat=mydat[-Selection,]
		}
	}

	# Basis of records (keep only "natural" records)
	BR=c("HUMAN_OBSERVATION","LITERATURE","MATERIAL_SAMPLE","MATERIAL_CITATION",
		"OBSERVATION","MACHINE_OBSERVATION")
	Selection=which(mydat$basisOfRecord%in%BR)
	if (!identical(Selection,integer(0))) {mydat=mydat[Selection,]}

	# Absences
	Selection=which(mydat$individualCount==0)
	if (!identical(Selection,integer(0))) {mydat=mydat[-Selection,]}

	# Duplicated coordinates
	Selection=which(duplicated(mydat[,c("decimalLongitude","decimalLatitude")]))
	if (!identical(Selection,integer(0))) {mydat=mydat[-Selection,]}

	# Write
	if (!nrow(mydat)==0){
		write.csv(mydat,file=paste0("./yohann_gbif_obs/cc_filtered/",gbif.csv[i]))
	}
}


