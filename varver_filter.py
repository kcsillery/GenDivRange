import glob

o = open("varver_filter.txt","w", encoding="utf8")
p = open("varver_output.csv","w", encoding="utf8")

for file in glob.glob("*.html"):
	with open(file, "r", encoding="utf8", errors="ignore") as f:
		body = f.readlines()
		if "Sampling Position" in body[12]:
			if "," in body[14]:         # if geo-referenced
				if body.count("<tr><th>Population Name</th>\n") > 4:     # if >=5 populations included
					o.write(file+"\n")

o.close()
