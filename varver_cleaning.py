# This script from Henry documents how we filter, clean, and extract species data from Varver database.
# screen through all html files in the varver database to produce “varver_filter.txt”, which contains studies that have more than 4 populations
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

# extract the Species and Title of each filtered study from “varver_filter.txt”, to produce the “varver_filter_doi.csv”
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

# search for the DOI of the Titles listed in “varver_filter_doi.csv”, and only those with a DOI match will return the “varver_selected.txt”

import argparse
import csv
import json
from math import inf
import random
import sys
from time import sleep
from urllib.error import HTTPError
from urllib.parse import quote_plus, urlencode
from urllib.request import urlopen, Request

from Levenshtein import ratio, matching_blocks, editops

MATCH_DEFAULT = 0.9
ASK_DEFAULT = 0.8
COLORS_DEFAULT = True

TITLE_HEADER_WL = ["article title", "title"]

ARG_HELP_STRINGS = {
    "title_file": "",
    "match_threshold": "a float value determining the minimum Levenshtein ratio to accept a title match (default: " + str(MATCH_DEFAULT) + ")",
    "ask_threshold": "a float value determining the minimum Levenshtein ratio to accept a title match (default: " + str(ASK_DEFAULT) + ")",
    "ansi_colors": "Use colorised text for easier visual match recognition (default: " + str(COLORS_DEFAULT) + ")",
    "start": "Start from this line number",
    "end": "End at this line number"
}

L_JUST = 40
BREAK = "".join(["-" for i in range(80)])
CMP_COLORS = ["blue", "green", "yellow", "red"]
EMPTY_RESULT = {
    "crossref_title": "",
    "similarity": 0,
    "doi": ""
}
MAX_RETRIES_ON_ERROR = 3

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("title_file", help=ARG_HELP_STRINGS["title_file"])
    parser.add_argument("-m", "--match_threshold", type=float, default=0.9, help=ARG_HELP_STRINGS["match_threshold"])
    parser.add_argument("-a", "--ask_threshold", type=float, default=0.8, help=ARG_HELP_STRINGS["ask_threshold"])
    parser.add_argument("-c", "--colors", type=bool, default=COLORS_DEFAULT, help=ARG_HELP_STRINGS["ansi_colors"])
    parser.add_argument("--start", type=int, default=0, help=ARG_HELP_STRINGS["start"])
    parser.add_argument("--end", type=int, default=inf, help=ARG_HELP_STRINGS["end"])
    args = parser.parse_args()
    
    header = None
    additional_fields = ["doi", "similarity"]
    
    with open(args.title_file, "r", encoding="utf8") as f:
        reader = csv.DictReader(f)
        title_field = None
        for field in reader.fieldnames:
            if field.lower() in TITLE_HEADER_WL:
                print(colorise("Using column '" + field + "' as title column", "green"))
                title_field = field
                break
        else:
            print(colorise("ERROR: Could not find a column name which might denote a title column", "red"))
            sys.exit()
        header = reader.fieldnames
        for field in additional_fields:
            if field not in header:
                header.append(field)
        modified_lines = []
        ask_count = 0
        for line in reader:
            line["ask"] = False
            if reader.line_num < args.start or reader.line_num > args.end:
                continue
            print(BREAK)
            title = line[title_field]
            head = "line " + str(reader.line_num) + ", query title:"
            print(colorise(head.ljust(L_JUST) + "'" + title + "'", "blue"))
            ret = crossref_query_title(title)
            retries = 0
            while not ret['success'] and retries < MAX_RETRIES_ON_ERROR:
                retries += 1
                msg = "Error while querying CrossRef API ({}), retrying ({})...".format(ret["exception"], retries)
                print(colorise(msg, "red"))
                ret = crossref_query_title(title)
            result = ret["result"]
            msg_tail = "'{}' [{}]"
            msg_tail = msg_tail.format(result["crossref_title"], result["doi"])
            if result["similarity"] == 1.0:
                msg_head = "Perfect match found ({}):"
                msg_head = msg_head.format(round(result["similarity"], 2)).ljust(L_JUST)
                print(colorise(msg_head + msg_tail, "cyan"))
                line.update(result)
                line["ask"] = False
            elif result["similarity"] >= args.match_threshold:
                msg_head = "Good match found ({}):"
                msg_head = msg_head.format(round(result["similarity"], 2)).ljust(L_JUST)
                print(colorise(msg_head + msg_tail, "green"))
                line.update(result)
                line["ask"] = False
            elif result["similarity"] >= args.ask_threshold:
                msg_head = "Possible match found ({}):"
                msg_head = msg_head.format(round(result["similarity"], 2)).ljust(L_JUST)
                print(colorise(msg_head + msg_tail, "yellow"))
                line.update(result)
                line["line_num"] = reader.line_num
                line["ask"] = True
                ask_count += 1
            else:
                msg_head = "No match found, most similar was ({}):"
                msg_head = msg_head.format(round(result["similarity"], 2)).ljust(L_JUST)
                print(colorise(msg_head + msg_tail, "red"))
                line.update(EMPTY_RESULT)
                line["ask"] = False
            modified_lines.append(line)
        if ask_count > 0:
            print(BREAK)
            ask_msg = "{} matches found with a similarity between {} and {} will need manual confirmation:"
            ask_msg = ask_msg.format(ask_count, args.ask_threshold, args.match_threshold)
            print(colorise(ask_msg, "green"))
        for line in modified_lines:
            if line["ask"]:
                print(BREAK)
                query_t = line[title_field]
                xref_t = line["crossref_title"]
                # display matching segments in identical colors for easier recognition
                diff = matching_blocks(editops(query_t.lower(), xref_t.lower()), query_t, xref_t)
                query_print = query_t
                xref_print = xref_t
                # ANSI codes increase string length, so we need an offset to compensate
                offset = 0
                for i in range(len(diff)):
                    a, b, c = diff[i]
                    a += offset
                    b += offset
                    offset += 9
                    color = CMP_COLORS[i % len(CMP_COLORS)]
                    query_print = colorise_text_segment(query_print, a, a + c , color)
                    xref_print = colorise_text_segment(xref_print, b, b + c , color)
                query_head = colorise("line {}, query title:".format(line["line_num"]), "blue")
                xref_head = colorise("Possible match ({}):".format(round(line["similarity"], 2)), "yellow")
                print(query_head.ljust(L_JUST) + query_print)
                print(xref_head.ljust(L_JUST) + xref_print)
                answer = input("Do you want to accept the DOI for the match title? (y/n):")
                while answer not in ["y", "n"]:
                    answer = input("Please type 'y' or 'n':")
                if answer == "n":
                    line.update(EMPTY_RESULT)
                
        with open("out.csv", "w", encoding="utf8") as out:
            dialect = csv.excel
            dialect.quoting = csv.QUOTE_ALL
            writer = csv.DictWriter(out, header, extrasaction='ignore', dialect=dialect)
            writer.writeheader()
            writer.writerows(modified_lines)

def crossref_query_title(title):
    api_url = "https://api.crossref.org/works?"
    params = {"rows": "5", "query.bibliographic": title}
    url = api_url + urlencode(params, quote_via=quote_plus)
    print(url)
    request = Request(url)
    request.add_header("User-Agent", "OpenAPC DOI Importer (https://github.com/OpenAPC/openapc-de/blob/master/python/import_dois.py; mailto:openapc@uni-bielefeld.de)")
    try:
        ret = urlopen(request)
        content = ret.read()
        data = json.loads(content)
        items = data["message"]["items"]
        most_similar = EMPTY_RESULT
        for item in items:
            if "title" not in item:
                continue
            title = item["title"].pop()
            result = {
                "crossref_title": title,
                "similarity": ratio(title.lower(), params["query.bibliographic"].lower()),
                "doi": item["DOI"]
            }
            if most_similar["similarity"] < result["similarity"]:
                most_similar = result
        return {"success": True, "result": most_similar}
    except HTTPError as httpe:
        return {"success": False, "result": EMPTY_RESULT, "exception": httpe}
    time.sleep(1)
    
def colorise(text, color):
    return colorise_text_segment(text, 0, len(text), color)
    
def colorise_text_segment(text, start, end, color):
    ANSI_COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "cyan": "\033[96m"
    }
    if color not in ANSI_COLORS.keys():
        raise ValueError("Argument 'color' must be one of [" + ", ".join(ANSI_COLORS.keys()) + "]")
    s = ANSI_COLORS[color]
    e = "\033[0m"
    return text[:start] + s + text[start:end] + e + text[end:]
    
if __name__ == '__main__':
    main()


# Finally, extract from the HTML files that have a match in the “varver_selected”, and outputted all necessary information by regex as “varver_extract_output.tab”
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