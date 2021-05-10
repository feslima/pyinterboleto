
from pathlib import Path
from typing import TypedDict, Union

PathType = Union[str, Path]


class RequestConfigs(TypedDict):
    conta_inter: str
    cert: PathType
    key: PathType
