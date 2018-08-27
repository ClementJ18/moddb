from .objects import *
from .enums import *

from typing import List, Union

class Client:
    def search(self, query : str, category : SearchCategory, **filters) -> List[Thumbnail]:
        pass
