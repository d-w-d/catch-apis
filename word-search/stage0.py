"""
STAGE 0 of Pipeline
Extract data from remote html and upload into postgres DB
"""

import re
import os
from time import sleep
from typing import List
from bs4 import BeautifulSoup, element
from requests import Response, request
from models.small_body import SmallBody


# Compute dirname of this file
dirname: str = os.path.dirname(os.path.realpath(__file__))

# Define path to data dir
dataDirPath = dirname + '/mpcdata'

# Test data dir exists called 'mpcdata'
isDataDir: bool = os.path.isdir(dataDirPath)

# If data dir does not exist, create it
if not isDataDir:
    print("Data directory %s does not exist. Creating ..." % dataDirPath)
    sleep(1)
    try:
        os.mkdir(dataDirPath)
    except OSError:
        print("Creation of the directory %s failed" % dataDirPath)
    else:
        print("Successfully created the directory %s " % dataDirPath)


# Compute path to raw-html file
raw_html_file: str = dataDirPath + '/raw_mpc.html'

# Test if raw-html file exists:
isRawFile: bool = os.path.isfile(raw_html_file)

# Define var to hold raw html text
html: str

# If raw-html doesn't exist, then save it; else read from file
if not isRawFile:
    # Fetch html and save to file
    url: str = 'https://www.minorplanetcenter.net/iau/lists/MPNames.html'
    req: Response = request('get', url)
    html = req.content.decode('ascii')
    with open(raw_html_file, 'w') as f:
        f.write(html)
else:
    print("Retrieving html from previously saved file...")
    with open(raw_html_file, 'r') as f:
        html = f.read()

# Parse raw html
soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')

# By inspection, we know target content is in a single <pre> element
preTag: element.Tag = soup.find('pre')
target_content: str = preTag.text
target_content_lines: List[str] = target_content.split('\n')


# Parse lines of text; convert to csv-style lines
small_bodies: List[SmallBody] = []
print(">>> Parsing html...")
for i, line in enumerate(target_content_lines):

    #################################################################################
    # Extract units from lines in html; example Line (spaces made dashes):
    # '--(12059)-du-Chatelet--------------du-Châtelet-'
    # '---(785)-Zwetana-----------------------Zwetana'
    # Notice the pesky multi-space gap between non-accented name and accented name
    #################################################################################

    try:
        # Split the pesky multi-space gap
        # E.g. temp1 <=== ['--(12059)-du-Chatelet', 'du-Châtelet']
        temp1 = re.split(r'\s{6,}', line)

        # Find first occurence of chars in parentheses
        # E.g. number <=== ['12059'][0]
        number: str = re.findall(r'\(([^)]+)\)', temp1[0])[0]

        # Find unaccented name:
        # E.g. unaccentedName  <=== 'du-Chatelet'
        unaccentedName = re.sub(r'\s*\(([^)]+)\)\s', '', temp1[0])

        # Find accented name:
        # E.g. unaccentedName <=== 'du-Chatelet'
        accentedName = temp1[1]

        # Save items to list of SmallBody entries
        small_bodies.append(
            SmallBody(
                numid=int(number),
                accented=accentedName,
                unaccented=unaccentedName
            )
        )
    except:
        # Print lines that don't work or conform to above pattern
        print('Failed Line: >>>'+line+'<<<')


# Save cleaned data to csv file
output_file: str = dataDirPath + "/minor_planets_names.csv"
print(">>> Saving parsed html...")
with open(output_file, 'w') as f:
    f.write("numid,unaccented,accented\n")
    for sb in small_bodies:
        if sb.accented and sb.unaccented and sb.numid:
            f.write(str(sb.numid)+","+sb.accented+","+sb.unaccented+"\n")
