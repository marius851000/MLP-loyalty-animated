import sys
from xml.etree import ElementTree
import subprocess

res = "2000"

arg = sys.argv
if len(sys.argv) < 4:
    print("usage: export.py <layer label> <source svg> <output png>")

layer_name = sys.argv[1]
source_svg = sys.argv[2]
output_png = sys.argv[3]

tree = ElementTree.parse(source_svg)
root = tree.getroot()

ids_to_render = []
found_something = False
for group in root.findall("{http://www.w3.org/2000/svg}g"):
    if group.attrib["{http://www.inkscape.org/namespaces/inkscape}label"] == layer_name:
        found_something = True
        for element in group.iter():
            if "id" in element.attrib:
                ids_to_render.append(element.attrib["id"])
        break

if not found_something:
    raise BaseException("no group with id {} found in {}".format(layer_name, source_svg))

command = ["inkscape", source_svg, "-o", output_png, "-j", "-C", "-w", res, "-h", res]

if len(ids_to_render) == 0:
    raise BaseException("found nothing to render !")

i_value = "--export-id="
for id in ids_to_render:
    i_value += id + ";"
i_value = i_value[0:-1]

command.append(i_value)
subprocess.check_call(command)
