import re

o = open("varver_filter.txt","r", encoding="utf8")
p = open("varver_filter_doi.csv","w", encoding="utf8")

p.write("File,Species,Title\n")

for file in o:
    file = file.split("\n")[0]
    with open(file, "r", encoding="utf8", errors="ignore") as f:
        body = f.readlines()
        if "Title" in body[30]:
            start = body[30].find("\">") + len("\">")
            end = body[30].find("</a>", start)
            title = body[30][start:end].replace(","," ")
        else:
            title = "title not found"
        if "Species" in body[5]:
            start = body[5].find("\">") + len("\">")
            end = body[5].find("</a>", start)
            species = body[5][start:end]      
        else:
            species = "species not found"
        
        p.write(','.join([file,species,title])+"\n")

o.close()
p.close()