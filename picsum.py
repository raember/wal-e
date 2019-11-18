from io import BytesIO
from typing import Tuple, List

import requests
from PIL import Image as PILImg
from PIL.Image import Image
from urllib3.util import parse_url
from urllib3.util.url import Url


class Info:
    _img_id: int
    _author: str
    _width: int
    _height: int
    _url: str
    _download_url: str

    def __init__(self, data: dict):
        self._img_id = int(data['id'])
        self._author = data['author']
        self._width = data['width']
        self._height = data['height']
        self._url = data['url']
        self._download_url = data['download_url']

    @property
    def id(self) -> int:
        return self._img_id

    @property
    def author(self) -> str:
        return self._author

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def url(self) -> str:
        return self._url

    @property
    def download_url(self) -> str:
        return self._download_url

    def __str__(self):
        return f"{self.id} ({self.width}x{self.height}) {self.author}"


class PicsumPhotos:
    @staticmethod
    def _get_path(width: int = 0, height: int = 0, img_id: int = -1, info: bool = False, list: bool = False) -> str:
        if list:
            return '/v2/list'
        elif img_id != -1:
            if info:
                return f"/id/{img_id}/info"
            else:
                return f"/id/{img_id}/{width}/{height}"
        else:
            return f"/{width}/{height}"

    @staticmethod
    def _get_query(grayscale: bool = False, blur: int = 0, page: int = 0, limit: int = 0) -> str:
        queries = []
        if grayscale:
            queries.append('grayscale')
        if blur > 0:
            if blur > 10:
                print("Blur value cannot exceed 10")
                blur = 10
            queries.append(f"blur={blur}")
        if page != 1:
            queries.append(f"page={page}")
        if limit != 30:
            queries.append(f"limit={limit}")
        return '&'.join(queries)

    @staticmethod
    def get_image(width: int, height: int, img_id: int = -1, grayscale: bool = False, blur: int = 0) -> Tuple[
        int, Image]:
        resp = requests.request('GET', Url(
            scheme='https',
            host='picsum.photos',
            path=PicsumPhotos._get_path(width, height, img_id),
            query=PicsumPhotos._get_query(grayscale, blur)
        ))
        url = parse_url(resp.url)
        img_id = int(url.path.split('/')[2])
        return img_id, PILImg.open(BytesIO(resp.content))

    @staticmethod
    def get_info(img_id: int) -> Info:
        resp = requests.request('GET', Url(
            scheme='https',
            host='picsum.photos',
            path=PicsumPhotos._get_path(img_id=img_id, info=True)
        ))
        return Info(resp.json())

    @staticmethod
    def get_list(page: int = 1, limit: int = 30) -> List[Info]:
        resp = requests.request('GET', Url(
            scheme='https',
            host='picsum.photos',
            path=PicsumPhotos._get_path(list=True),
            query=PicsumPhotos._get_query(page=page, limit=limit)
        ))
        infos = []
        for entry in resp.json():
            infos.append(Info(entry))
        return infos
