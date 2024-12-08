# image dithering script
# Almost entirely rewritten by Mond.
# 
# Originally © 2022 Roel Roscam Abbing, released as AGPLv3

import os
import argparse
import shutil
from PIL import Image
import logging
import numpy as np
import dither
import palette
import tomllib

IMAGE_EXTENSIONS = (".jpg", ".JPG", ".jpeg", ".png", ".gif", ".webp", ".tiff", ".bmp")

parser = argparse.ArgumentParser(
    """
    This script recursively traverses folders and creates dithered versions of the images it finds.
    These are stored in the same folder as the images in a folder called "dithers".
    """
)

parser.add_argument(
    "-d",
    "--directory",
    help="Set the directory to traverse",
)

parser.add_argument(
    "-rm",
    "--remove",
    help="Removes all the folders with dithers and their contents",
    action="store_true",
)

parser.add_argument(
    "-v",
    "--verbose",
    help="Print out more detailed information about what this script is doing",
    action="store_true",
)


def pick_color(category):
    """
    Picks a colored dithering palette based on the post category.
    """
    colors = {
        "low-tech": palette.Palette(
            [
                (30, 32, 40),
                (11, 21, 71),
                (57, 77, 174),
                (158, 168, 218),
                (187, 196, 230),
                (243, 244, 250),
            ]
        ),
        "obsolete": palette.Palette(
            [
                (9, 74, 58),
                (58, 136, 118),
                (101, 163, 148),
                (144, 189, 179),
                (169, 204, 195),
                (242, 247, 246),
            ]
        ),
        "high-tech": palette.Palette(
            [
                (86, 9, 6),
                (197, 49, 45),
                (228, 130, 124),
                (233, 155, 151),
                (242, 193, 190),
                (252, 241, 240),
            ]
        ),
        "grayscale": palette.Palette(
            [
                (25, 25, 25),
                (75, 75, 75),
                (125, 125, 125),
                (175, 175, 175),
                (225, 225, 225),
                (250, 250, 250),
            ]
        ),
    }
    if category.lower() not in colors:
        logging.warning(f"No category named '{category}' defined. Using default.")
    return colors.get(category.lower(), colors["grayscale"])


def dither_image(source_path, out_path, category="grayscale"):
    palette = pick_color(category)
    img = Image.open(source_path)

    if img.has_transparency_data:
        logging.info(f"Dithering transparent image {source_path}...")
        img.thumbnail((800, 800), Image.LANCZOS)
        alpha = img.getchannel("A")
        img = img.convert("RGB")
        raw = dither.apply_bayer(img, 96, 4)
        img_dithered = palette.create_PIL_png_from_rgb_array(raw)
        img_dithered.putalpha(alpha)
        img_dithered = img_dithered.convert("RGBA")
        img_dithered = img_dithered.convert("P")
    else:
        logging.info(f"Dithering image {source_path}...")
        img = img.convert("RGB")
        img.thumbnail((800, 800), Image.LANCZOS)
        raw = dither.apply_bayer(img, 96, 4)
        img_dithered = palette.create_PIL_png_from_rgb_array(raw)

    img_dithered.save(out_path, optimize=True)


def create_dithers(content_dir):
    directory = os.path.abspath(content_dir)
    if not os.path.isdir(directory):
        logging.critical(f"Path {directory} is not a directory or doesn't exist")
        return
    for root, dirs, files in os.walk(directory, topdown=True):
        logging.debug(f"Processing folder {root}")
        if root.endswith(("images", "dithers")):
            continue
        if not os.path.isfile(os.path.join(root, "index.md")):
            continue
        if not os.path.isdir(os.path.join(root, "images")):
            continue
        logging.info(f"Dithering images in {root}")

        dither_path = os.path.join(root, "images", "dithers")
        if not os.path.exists(dither_path):
            os.mkdir(dither_path)
            logging.info(f"📁 created at {dither_path}")

        category = parse_front_matter(os.path.join(root, "index.md"))

        images_path = os.path.join(root, "images")
        for fname in os.listdir(images_path):
            if not os.path.isfile(os.path.join(images_path, fname)):
                continue
            file_, ext = os.path.splitext(fname)
            if ext not in IMAGE_EXTENSIONS:
                continue
            source_path = os.path.join(images_path, fname)
            out_path = os.path.join(dither_path, file_ + "_dithered.png")
            if not os.path.exists(out_path):
                dither_image(source_path, out_path, category)
                logging.info(f"🖼  wrote {out_path}")
            else:
                logging.debug(f"Dithered version of {fname} found, skipping")


def delete_dithers(content_dir):
    path = os.path.abspath(content_dir)
    logging.info(f"Deleting 'dither' folders in {path} and below")
    for root, dirs, files in os.walk(path, topdown=True):
        dir = os.path.basename(os.path.normpath(root))
        if dir == "dithers":
            shutil.rmtree(root)
            logging.info(f"Removed {root}")


def parse_front_matter(md_path) -> str:
    with open(md_path) as f:
        contents = f.readlines()
        start = contents.index("+++\n")
        stop = contents.index("+++\n", start + 1)
        contents = "".join(contents[start + 1 : stop])
        preamble = tomllib.loads(contents)
        cats = preamble.get("categories")
        if not isinstance(cats, list):
            raise ValueError(f"Categories of value {cats}, not a list!")
        if not cats:
            return "grayscale"
        if 2 <= len(cats):
            raise ValueError(f"{md_path} has multiple categories!")
        if cats[0] == "":
            return "grayscale"
        return cats[0]


if __name__ == "__main__":
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if args.remove:
        delete_dithers(os.path.abspath(args.directory))
    else:
        logging.info(f"Dithering all images in {args.directory} and subfolders")
        create_dithers(os.path.abspath(args.directory))
