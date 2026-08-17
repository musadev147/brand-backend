from typing import Optional
from pydantic import BaseModel

class PromoBannerResponse(BaseModel):
    id: int
    title: str
    subtitle: str
    button_text: str
    redirect_to: str
    icon_name: Optional[str] = None
    background_gradient: Optional[str] = None
    sort_order: int

    model_config = {"from_attributes": True}
