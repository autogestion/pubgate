import os

__version__ = "0.3.4"

KEY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "storage")
MEDIA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "media")
LOGO = "https://user-images.githubusercontent.com/1098257/83571569-eb642700-a51f-11ea-8fca-c2b61798a4ce.png"


class BaseUrl:
    value = ''
