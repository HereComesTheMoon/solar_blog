import os
import argparse
from bs4 import BeautifulSoup


parser = argparse.ArgumentParser(
    """
    This script recursively traverses folders and enumerates the file size of all html pages and associated media.
    The calculated total file size is then added to the HTML page.
    """
)

parser.add_argument(
    "-d", "--directory", help="Set the directory to traverse", default="."
)

args = parser.parse_args()

for root, dirs, files in os.walk(os.path.abspath(args.directory)):
    for fname in files:
        if not fname.endswith(".html"):
            continue
        path = os.path.join(root, fname)
        print(f"Prettifying {path}")
        with open(path, "r") as f:
            prettier = BeautifulSoup(f.read(), "html.parser").prettify()
        with open(path, "w") as f:
            f.write(prettier)
