#!/usr/bin/env python3

import requests
import os
import difflib
from dotenv import load_dotenv

def compare(seq1, seq2):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio()

load_dotenv()
API_URL = os.getenv("LIBRARY_API_URL")    
gametypes = ["rpg", "wargame", "cardgame", "boardgame"]

def is_library_id(eid):
	valid = True
	try:
		int(eid[1:])
	except:
		valid = False
		
	if eid[0] in ["R", "B", "W", "C"]:
		return valid
	else:
		return False

def query(name, gametype = ""):

    data = []
    selection = [gametype] if gametype else gametypes

    for gt in selection:
        r = requests.get(API_URL+"?sheet="+gt+"s")
        data += r.json()

    results = []
    
    for e in data:
    
        bulk_searchable = e["name"].lower()+" "+e["franchise"].lower()
        discard=False
        
        for word in name.split(" "):
            if word.lower() not in bulk_searchable:
                discard=True
                
        if not discard: 
            results += [e]
        
    for e in results:
        e["accuracy"] = compare(e["name"], name)

    # sort e by accuracy ratio
    sortedresults = sorted(results, key=lambda d: d["accuracy"])

    return(results)

def make_query_string(results):

    count = len(results)

    out = "```\n"
    out += "ID".ljust(5) + "Name".ljust(30) + "Franchise" +"\n"
    out += "-"*55 +"\n"
    for r in results:
    
        count -= 1
        out += r["id"].ljust(5)
        out += (r["name"][:26] + '... ') if len(r["name"]) > 29 else r["name"].ljust(30)
        out += ((r["franchise"][:17]+'...') if len(r["franchise"])>20 else r["franchise"])+"\n"

        if len(out) > 1500:
            break

    out += "```"
    if len(results) == 1:
        out += "**1 item found**"    
    elif len(results) == 0:
        out = "**No items found**. Try a more general query."
    else:
        out += "**"+str(len(results))+" items found**"
        
    if count != 0:
        out += " ("+str(count)+" results hidden)"
    return out

def get_entry(eid):
    
    code = eid[0]

    gametype = [gt for gt in gametypes if (gt[0] == code.lower())][0]

    r = requests.get(API_URL+"/search?sheet="+gametype+"s&id="+eid)

    return(r.json())
    
