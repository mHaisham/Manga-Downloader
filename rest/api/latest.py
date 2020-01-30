from flask_api import status
from flask_restful import Resource

from network.scrapers import Mangakakalot
from ..encoding import manga_link


class Latest(Resource):
    def get(self, i=1):

        mangakakalot = Mangakakalot()
        mangas = mangakakalot.get_latest(i)

        if mangas is None:
            return dict(message=f'Not found'), status.HTTP_404_NOT_FOUND

        latest = []
        for manga in mangas:
            d_manga = vars(manga)

            del d_manga['description']
            del d_manga['get_status']

            d_manga['link'] = manga_link(manga.title)

            latest.append(d_manga)

        return latest