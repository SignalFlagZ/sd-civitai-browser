import colorsys
from scripts.civsfz_shared import opts

def hex_color_hsl_to_rgb(h,s,l):
    # param order h,s,l not h,l,s
    if h > 1.0:
        h=max(min(h/360,1.0),0)
    if l > 1.0:
        l=max(min(l/100,1.0),0)
    if s > 1.0:
        s=max(min(s/100,1.0),0)
    (r, g, b) = colorsys.hls_to_rgb( h, l, s)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

def hex_color_hls_to_rgba(h, s, l, a=1.0):
    # param order h,s,l not h,l,s
    ret = hex_color_hsl_to_rgb(h, l, s)
    if a > 1.0:
        a = max(min(a / 100, 1.0), 0)
    return f"{ret}{int(a*255):02x}"

class BaseModelColors():
    colors = [
        {
            "name": "BASE",
            "label": "Background color for model names",
            "key": "civsfz_background_color_figcaption",
            "property": "--civsfz-background-color-figcaption",
            "color": hex_color_hsl_to_rgb(225, 15, 30),
        },
        {
            "name": "SD 1",
            "label": "Background color for SD1 models",
            "key": "civsfz_background_color_sd1",
            "property": "--civsfz-background-color-sd1",
            "color": hex_color_hsl_to_rgb(90, 70, 30),
        },
        {
            "name": "SD 2",
            "label": "Background color for SD2 models",
            "key": "civsfz_background_color_sd2",
            "property": "--civsfz-background-color-sd2",
            "color": hex_color_hsl_to_rgb(90, 60, 40),
        },
        {
            "name": "SD 3",
            "label": "Background color for SD3 models",
            "key": "civsfz_background_color_sd3",
            "property": "--civsfz-background-color-sd3",
            "color": hex_color_hsl_to_rgb(135, 70, 30),
        },
        {
            "name": "SD 3.",
            "label": "Background color for SD3.5 models",
            "key": "civsfz_background_color_sd35",
            "property": "--civsfz-background-color-sd35",
            "color": hex_color_hsl_to_rgb(150, 80, 40),
        },
        {
            "name": "SDXL",
            "label": "Background color for SDXL models",
            "key": "civsfz_background_color_sdxl",
            "property": "--civsfz-background-color-sdxl",
            "color": hex_color_hsl_to_rgb(15, 70, 40),
        },
        {
            "name": "Pony",
            "label": "Background color for Pony models",
            "key": "civsfz_background_color_pony",
            "property": "--civsfz-background-color-pony",
            "color": hex_color_hsl_to_rgb(15, 90, 40),
        },
        {
            "name": "Illustrious",
            "label": "Background color for Illustrious models",
            "key": "civsfz_background_color_illustrious",
            "property": "--civsfz-background-color-illustrious",
            "color": hex_color_hsl_to_rgb(15, 95, 50),
        },
        {
            "name": "Flux.1",
            "label": "Background color for Flux.1 models",
            "key": "civsfz_background_color_flux1",
            "property": "--civsfz-background-color-flux1",
            "color": hex_color_hsl_to_rgb(330, 80, 40),
        },
    ]

    def __init__(self) -> None:
        pass

    # for macros.jinja
    def name_property_dict(self):
        ret={}
        for d in self.colors:
            ret[d["name"]]=d["property"]
        # reverse order for sd3.
        return dict(reversed(list(ret.items())))

    def updateColor(self):
        for d in self.colors:
            d["color"] = opts.data[d["key"]]

# print(f"{BaseModelColors().name_property_dict()}")
