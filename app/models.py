from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ProductRequest(BaseModel):
    product_name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    target_audience: Optional[str] = "General Customers"
    product_url: Optional[HttpUrl] = None


class AdVariation(BaseModel):
    angle: str  # e.g., "Pain Point", "Social Proof", "Feature Focus", "Urgency"
    headline: str
    primary_text: str
    call_to_action: str


class AdCopyResponse(BaseModel):
    product_name: str
    target_audience: str
    variations: List[AdVariation]


class GeneratedVariations(BaseModel):
    """Schema sent to the model. Identity fields are filled from the request."""

    variations: List[AdVariation]
