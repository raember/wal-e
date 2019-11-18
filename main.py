#!/usr/bin/env python3
import logging
import os
from optparse import OptionParser
from typing import Tuple, Optional

import pywal
from PIL import Image as PILImage
from PIL.Image import Image

from picsum import PicsumPhotos
from xrandr import XRandr

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(name)8s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)
logging.getLogger("urllib3").setLevel(logging.ERROR)

log = logging.getLogger('wal-e')
XDG_PICTURES_DIR = os.getenv('XDG_PICTURES_DIR', '.')
if XDG_PICTURES_DIR == '.':
    log.warning("Couldn't get default folder for pictures. Using current folder as base.")
WALL_DIR = f"{XDG_PICTURES_DIR}/wallpapers"


def get_file_path(width: int, height: int, img_id: int) -> str:
    return f'{WALL_DIR}/{img_id}_{width}x{height}.jpg'


def save(img: Image, width: int, height: int, img_id: int) -> str:
    path = get_file_path(width, height, img_id)
    if not os.path.exists(WALL_DIR):
        os.mkdir(WALL_DIR)
    if not os.path.exists(path):
        with open(path, 'w') as fp:
            img.save(fp, 'jpeg')
    return path


def load(width: int, height: int, img_id: int) -> Optional[Image]:
    path = get_file_path(width, height, img_id)
    if os.path.exists(path):
        return PILImage.open(path)
    else:
        return None


def get_resolution(resolution: str = None) -> Tuple[int, int]:
    if resolution is not None:
        width, height = resolution.split('x')
    else:
        width, height = XRandr.get_resolution()
    return width, height


def get_image(width: int, height: int, img_id: int, random: bool) -> Tuple[int, Image]:
    if random:
        return PicsumPhotos.get_image(width, height)
    elif img_id is not None:
        img = load(width, height, img_id)
        if img is None:
            return PicsumPhotos.get_image(width, height, img_id)
        return img_id, img
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-r", "--random", dest="random", action="store_true",
                      help="Takes a random wallpaper")
    parser.add_option("-i", "--id", dest="img_id", default=None,
                      help="Use wallpaper identified by the id")
    parser.add_option("-x", "--resolution", dest="resolution", default=None,
                      help="Assume specific resolution (i.e. '1920x1200') instead of asking xrandr")
    (opt, args) = parser.parse_args()
    width, height = get_resolution(opt.resolution)
    if not opt.random and opt.img_id is None:
        raise NotImplementedError()
    opt.img_id, img = get_image(width, height, opt.img_id, opt.random)
    path = save(img, width, height, opt.img_id)

    if opt.img_id is not None:
        info = PicsumPhotos.get_info(opt.img_id)
        log.info(info)

    image = pywal.image.get(path)
    colors = pywal.colors.get(image)
    colors['alpha'] = '50'
    pywal.sequences.send(colors)
    pywal.export.every(colors)
    pywal.reload.env()
    pywal.wallpaper.change(image)
    # info_list = PicsumPhotos.get_list()
