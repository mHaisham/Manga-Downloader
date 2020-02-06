from database import Database
from database.types import PathType

db = Database.get()


class PageModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    url = db.Column(db.String(), unique=True)
    link = db.Column(db.String())
    path = db.Column(PathType())

    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter_model.id'), nullable=False)

    def __init__(self, url, chapter_id, **kwargs):
        super(PageModel, self).__init__(**kwargs)

        self.url = url
        self.chapter_id = chapter_id

    def clean_dict(self) -> dict:
        model = vars(self).copy()
        del model['path']

        return model

    def to_dict(self) -> dict:
        model = vars(self).copy()

        return model

    @staticmethod
    def from_dict(d):
        model = PageModel()

        model.url = d['url']
        model.path = d['path']
        model.link = d['link']

        return model

    @staticmethod
    def create(page, **kwargs):
        model = PageModel.from_page(page)
        model.path = kwargs['path']
        model.link = kwargs['link']

        return model

    @staticmethod
    def from_page(page):
        model = PageModel()

        model.url = page.url

        return model
