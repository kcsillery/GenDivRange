import re

i = open("varver_selected.txt", "r")
o = open("varver_extract_output.tab", "w")

o.write("Varver\tPop_no\tPop_id\tPop_name\tLat\tLong\tn\tHo\tHe\tFis\tA\n")

for file in i:
    with open(file.split("\n")[0], "r", errors="ignore") as j:
        k = j.readlines()
        k_idx = 0
        pop_no = 1
        skip = 0
        for line in k:    # k: extract informations and output as table
            if "Subpopulation ID:" in line:
                pop_id = re.search("Subpopulation ID:(.*?)</th>", line).group(1)
            if "Population Name" in line:
                pop_name = re.search("(.*?)</td>", k[k_idx+2]).group(1)
            if "Sampling Position" in line:
                if re.search("([0-9.-]+),([0-9.-]+) ", k[k_idx+2]):
                    lat = re.search("([0-9.-]+),([0-9.-]+) ", k[k_idx+2]).group(1)
                    long = re.search("([0-9.-]+),([0-9.-]+) ", k[k_idx+2]).group(2)
                else:
                    skip = 1
                    lat = "NA"
                    long = "NA"
            if "Sampling Size" in line:
                if re.search("<td bgcolor=\"#ccffff\">([0-9.]+)</td>", line):
                    n = re.search("<td bgcolor=\"#ccffff\">([0-9.]+)</td>", line).group(1)
                else:
                    n = "NA"
                if re.search("<i>H</i>o</th><td bgcolor=\"#ccffff\">mean: ([0-9.]+)</td>", line):
                    Ho = re.search("<i>H</i>o</th><td bgcolor=\"#ccffff\">mean: ([0-9.]+)</td>", line).group(1)
                else:
                    Ho = "NA"
                if re.search("<i>H</i>e</th><td bgcolor=\"#ccffff\">mean: ([0-9.]+)</td>", line):
                    He = re.search("<i>H</i>e</th><td bgcolor=\"#ccffff\">mean: ([0-9.]+)</td>", line).group(1)
                else:
                    He = "NA"
                if re.search("<i>F</i><small>IS</small></th><td bgcolor=\"#ccffff\">mean: ([0-9.-]+)</td>", line):
                    Fis = re.search("<i>F</i><small>IS</small></th><td bgcolor=\"#ccffff\">mean: ([0-9.-]+)</td>", line).group(1)
                else:
                    Fis = "NA"
                if re.search("No. of allele</th><td bgcolor=\"#ccffff\">mean: ([0-9.]+)</td>", line):
                    A = re.search("No. of allele</th><td bgcolor=\"#ccffff\">mean: ([0-9.]+)</td>", line).group(1)
                else:
                    A = "NA"
            if "Other informations" in line and skip == 0:
                o.write(file.split("\n")[0] + "\t" + str(pop_no) + "\t" + pop_id + "\t" + pop_name + "\t" + lat + "\t" + long + "\t" + n + "\t" + Ho + "\t" + He + "\t" + Fis + "\t" + A + "\n")
                pop_no += 1
            
            k_idx += 1
                

i.close()
o.close()