#!/usr/bin/env python3
from cairosvg import svg2png
from random import randint

# Recolours the DU Gamers logo. Assumes that inputs are valid!
def colour_logo(background="default", tower="default", dice="default", pips="default"):

    # Load file
    with open("GamersLogo.svg", "r") as f:
        svg = f.read()

    # Yeah I know this is a total mess! Someone should do it cleaner, with actual SVG tag processing
    if background != "default":
        old_input = "<circle style=\"fill:#9f3036"
        new_input = "<circle style=\"fill:#"+background.lower()
        svg = svg.replace(old_input, new_input)

    if tower != "default":
        line="#ffffff;fill-opacity:1;stroke:none;stroke-width:0.264999;stroke-linecap:butt;stroke-linejoin:miter;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1\" inkscape:label=\"Tower\"/>"
        old_input = line
        new_input = line.replace("ffffff", tower.lower())
        svg = svg.replace(old_input, new_input)

    if dice != "default":
        line1="#dca948;fill-opacity:1;stroke:none;stroke-width:0.21518999;stroke-opacity:1\" inkscape:label=\"DiceR\"/>"
        line2="#dca948;fill-opacity:1;stroke:none;stroke-width:0.223216;stroke-opacity:1\" inkscape:label=\"DiceL\"/>"
        for line in [line1, line2]:
            old_input = line
            new_input = line.replace("dca948", dice.lower())
            svg = svg.replace(old_input, new_input)

    if pips != "default":
        line1="#ffffff;fill-opacity:1;stroke:none;stroke-width:0.26458299px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1\" inkscape:label=\"PipsR\"/>"
        line2="#ffffff;fill-opacity:1;stroke:none;stroke-width:0.26458299px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1\" inkscape:label=\"PipsL\"/>"
        for line in [line1, line2]:
            old_input = line
            new_input = line.replace("ffffff", pips.lower())
            svg = svg.replace(old_input, new_input)

    bytes = svg2png(svg)
    filename = "recolour.png"
    with open(filename, "wb") as f:
        f.write(bytes)
    return filename


def random_colour():
    c = ""
    for i in range(3):
        v = randint(0,255)
        c += hex(v).replace("0x","")
    return c

def random_recolour():
    colours = []
    for i in range(4):
        colours += [random_colour()]
    return colour_logo(colours[0], colours[1], colours[2], colours[3])

if __name__ == "__main__":
    recolour = random_recolour()