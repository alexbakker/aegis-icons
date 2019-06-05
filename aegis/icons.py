import io
import json
import os
import pkg_resources
import re
import secrets
from collections import OrderedDict

import cairosvg
import xmltodict

# https://github.com/simple-icons/simple-icons/blob/f69ea6f28a3c864c79421e962103ebebbda7bb70/scripts/utils.js#L6-L15
def icon_title_to_name(title):
    title = title.lower()

    expr = [
        (r"\+", "plus", 0),
        (r"^\.", "dot-", 1),
        (r"\.$", "-dot", 1),
        (r"\.", "-dot-", 0),
        (r"^&", "and-", 1),
        (r"&$", "-and", 1),
        (r"&", "-and-", 0),
        (r"[ !’]", "", 0)
    ]

    for e in expr:
        title = re.sub(e[0], e[1], title, count=e[2])

    return title

class Icon:
    def __init__(self, title, filename, svg):
        self.title = title
        self.filename = filename
        self.svg = svg

    def get_xml(self):
        return xmltodict.unparse(self.svg, pretty=True)

    def render_png(self):
        res = io.BytesIO()
        cairosvg.svg2png(bytestring=self.get_xml(), write_to=res, output_width=800, output_height=800)
        return res.getvalue()

class IconGenerator:
    def __init__(self):
        self._icon_dir = os.path.join(pkg_resources.resource_filename(__name__, "simple-icons"))
        with io.open(os.path.join(self._icon_dir, "_data", "simple-icons.json"), "r") as f:
            self._icons = json.load(f)["icons"]

    def generate(self, icon):
        title = icon["title"]
        name = icon_title_to_name(title) + ".svg"
        filename = os.path.join(self._icon_dir, "icons", name)
        with io.open(filename, "r") as f:
            xml = xmltodict.parse(f.read())

        svg = OrderedDict()
        for key, val in xml["svg"].items():
            if key == "path":
                svg["circle"] = {
                    "@cx": 12,
                    "@cy": 12,
                    "@r": 12,
                    "@fill": "#" + icon["hex"]
                }
                val["@transform"] = "translate(4.8, 4.8) scale(0.6)"
                val["@fill"] = "white"
            svg[key] = val

        xml["svg"] = svg
        return Icon(title, name, xml)

    def generate_random(self):
        return self.generate(secrets.choice(self._icons))

    def generate_all(self):
        for icon in self._icons:
            yield self.generate(icon)
