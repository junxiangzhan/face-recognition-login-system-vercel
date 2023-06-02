from .CutPics import CutPics
from .BuildDB import BuildDB
from .Recognizer import Recognizer

FILENAME = '.\\__temp__\\temp'

class Database:
    db: BuildDB
    re: Recognizer

    def __init__(self) -> None:
        self.db = BuildDB()
        self.re = Recognizer()

    def cut_pics(self, username, pics) -> None:
        cp = CutPics(username)

        cp.cut(pics)

        self.db.label(username)
        self.db.build()

    def recognize(self, username, image) -> bool:
        image.save(FILENAME)
        
        is_pass, pass_name = self.re.recognize(FILENAME)

        return is_pass and pass_name == username