# ComfyUI-AspectRatioSizePicker
# Single-node aspect-ratio + long-edge + invert size picker for text-to-image.
# Outputs width / height (INT) to feed an Empty Latent Image node, plus an
# `info` STRING that shows the resolved size, orientation (PORTRAIT / LANDSCAPE
# / SQUARE semi-title), an inverted-ratio preview, and a reference list of
# common long-edge sizes in photography / video / social media.
#
# The dropdown offers BOTH orientations (e.g. "4:3 (Standard)" and
# "3:4 (Standard)") so the frontend can flip the visible label when invert is
# toggled, while the backend always resolves the correct dimensions.

# Each entry: display label -> (w, h) canonical ratio (w >= h by convention).
RATIOS = {
    "1:1 (Square)": (1, 1),
    # 4:3 family
    "4:3 (Standard)": (4, 3),
    "3:4 (Standard)": (3, 4),
    # 3:2 family
    "3:2 (Classic 35mm Film)": (3, 2),
    "2:3 (Classic 35mm Film)": (2, 3),
    # 5:4 family
    "5:4 (Large Format)": (5, 4),
    "4:5 (Large Format)": (4, 5),
    # 16:9 family
    "16:9 (Widescreen)": (16, 9),
    "9:16 (Widescreen)": (9, 16),
    # 16:10 family
    "16:10 (Widescreen)": (16, 10),
    "10:16 (Widescreen)": (10, 16),
}

# The 6 "base" orientations shown in the dropdown when invert is OFF.
ASPECT_OPTIONS = [
    "1:1 (Square)",
    "4:3 (Standard)",
    "3:2 (Classic 35mm Film)",
    "5:4 (Large Format)",
    "16:9 (Widescreen)",
    "16:10 (Widescreen)",
]

# Common long-edge sizes in photography, video and social media (reference only).
# Key = long-edge pixel value, value = what it is typically used for.
COMMON_LONG_EDGES = {
    720: "HD 720p",
    1080: "Full HD / Social base (IG, FB, TikTok, YT, X)",
    1200: "Facebook shared link / high-res social",
    1280: "HD video / YouTube thumbnail",
    1440: "QHD short edge",
    1920: "Full HD long edge / YouTube 1080p",
    2048: "Photo print @300dpi (~4x6 in)",
    2160: "4K short edge",
    2560: "QHD (1440p) long edge",
    3508: "A3 print @300dpi",
    3840: "4K UHD long edge",
    4096: "DCI 4K",
    5120: "5K",
    7680: "8K UHD",
}


class AspectRatioSizePicker:
    """
    Pick a target size from an aspect-ratio dropdown, a long-edge slider,
    and an invert toggle. Long edge always maps to the larger dimension.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "aspect_ratio": (
                    ASPECT_OPTIONS,
                    {"default": "1:1 (Square)"},
                ),
                "long_edge": (
                    "INT",
                    {"default": 1024, "min": 64, "max": 8192, "step": 8},
                ),
                "invert": (
                    "BOOLEAN",
                    {"default": False},
                ),
            }
        }

    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("width", "height", "info")
    FUNCTION = "pick"
    CATEGORY = "EternalShade3D"

    def pick(self, aspect_ratio, long_edge, invert):
        a, b = RATIOS[aspect_ratio]  # canonical (w, h) from the label
        base = f"{a}:{b}"
        if invert:
            a, b = b, a  # swap -> portrait/landscape flip
        flipped = f"{a}:{b}"

        if a >= b:
            width = long_edge
            height = round(long_edge * b / a)
        else:
            height = long_edge
            width = round(long_edge * a / b)

        # snap to multiple of 8 (ComfyUI latent alignment)
        width = max(8, (width // 8) * 8)
        height = max(8, (height // 8) * 8)

        # orientation semi-title
        if width > height:
            orient = "LANDSCAPE"
        elif height > width:
            orient = "PORTRAIT"
        else:
            orient = "SQUARE"

        # nearest common long-edge reference
        if long_edge in COMMON_LONG_EDGES:
            ref = COMMON_LONG_EDGES[long_edge]
        else:
            nearest = min(COMMON_LONG_EDGES, key=lambda k: abs(k - long_edge))
            ref = f"~{nearest} ({COMMON_LONG_EDGES[nearest]})"

        # inverted-ratio preview line
        if invert:
            ratio_line = f"{base}  ->  INVERTED  ->  {flipped}"
        else:
            ratio_line = f"{base}"

        info = (
            f"=== {orient} ===\n"
            f"{ratio_line}\n"
            f"Size: {width} x {height}\n"
            f"Long edge {long_edge} = {ref}\n"
            f"Common long edges: " + ", ".join(str(k) for k in COMMON_LONG_EDGES)
        )
        return (width, height, info)


NODE_CLASS_MAPPINGS = {
    "AspectRatioSizePicker": AspectRatioSizePicker,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AspectRatioSizePicker": "Aspect Ratio Size Picker",
}
