import xml.etree.ElementTree as ET
import sys
import os

tree = ET.parse(sys.argv[1])
root = tree.getroot()

with open('queries.txt', 'w') as f:
    for child in root:
        if (child.tag == "topic"):
            for grand in child:
                if (grand.text == "416" or 
                    grand.text == "423" or
                    grand.text == "437" or
                    grand.text == "444" or
                    grand.text == "447"):
                    break
                if (grand.tag == "number"):
                        f.write(grand.text + '\n')
                if (grand.tag == "title"):
                    f.write(grand.text)