import requests
import re

i = open("species_list.txt", "r")    # a text file with species name for each line
o = open("output.tsv", "w")     # this will be the output file

o.write("Species\tEnvironment\n")

my_list = ["freshwater", "marine", "pelagic"]   # change this list to include all defined vocabs

for line in i:

    sp = line.split("\n")[0]    # write species to first column
    o.write(sp + "\t")
    
    sp_clean = sp.replace(" ", "-")    # replace space to hyphen
    url = "https://www.fishbase.de/summary/" + sp_clean + ".html"
    html = requests.get(url)
    
    if html.ok:
        s = html.text     # this is the HTML for the webpage
        start = "<!-- start Environment / Climate / Range -->"
        end = "<!-- start Distribution -->"
        target = s[s.find(start)+len(start):s.rfind(end)]   # this extracts the Environment partition
        target = target.lower()
        
        matched_vocabs = []
        
        for vocab in my_list:
            if vocab in target:
                matched_vocabs.append(vocab)
        
        o.write(",".join(matched_vocabs))  # write these matched keywords to second column
        o.write("\n")
        
    else:
        o.write("HTML not found\n")   # write no return if HTML does not exist
    