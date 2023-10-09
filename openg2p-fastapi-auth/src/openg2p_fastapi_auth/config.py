from typing import List, Optional

from pydantic import BaseModel


class ApiAuthSettings(BaseModel):
    enabled: bool = False
    issuers: Optional[List[str]] = None
    audiences: Optional[List[str]] = None
    claim_name: Optional[str] = None
    claim_values: Optional[List[str]] = None
