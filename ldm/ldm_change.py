from __future__ import annotations
from typing import List, Optional, Dict, Any, Union


from utils.util_pydantic import PydanticMixin,  dataclass, field

@dataclass
class Change(PydanticMixin):
    change_type: str = ""
    path: str = ""
    mpath: str = ""
    old_value: str = ""
    new_value: str = ""
    