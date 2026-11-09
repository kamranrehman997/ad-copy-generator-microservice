import os

from anthropic import AsyncAnthropic

from app.models import AdCopyResponse, GeneratedVariations, ProductRequest
from app.page import fetch_page_text

_SYSTEM = """You write paid social ad copy for a single product.

Return exactly four variations, using these angles in this order:
1. Pain Point
2. Social Proof
3. Feature Focus
4. Urgency

Rules:
- Headline: about 40 characters, never more than 60.
- Primary text: about 125 characters, never more than 200.
- Call to action: a short imperative, such as "Shop now" or "See how it works".
- Use only facts present in the product details. Do not invent prices, discounts, awards, statistics, or testimonials.
- Write in the language of the product description.
"""


class GenerationError(Exception):
    pass


class MissingApiKeyError(GenerationError):
    pass


def _client() -> AsyncAnthropic:
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise MissingApiKeyError("ANTHROPIC_API_KEY is not set")
    return AsyncAnthropic()


def _prompt(request: ProductRequest, page_text: str | None) -> str:
    audience = (request.target_audience or "").strip() or "General Customers"
    lines = [
        f"Product name: {request.product_name}",
        f"Target audience: {audience}",
        f"Description: {request.description}",
    ]
    if request.product_url is not None:
        lines.append(f"Product URL: {request.product_url}")
    if page_text:
        lines.append(f"Text from the product page:\n{page_text}")
    return "\n".join(lines)


async def generate_ad_copy(request: ProductRequest) -> AdCopyResponse:
    page_text = None
    if request.product_url is not None:
        page_text = await fetch_page_text(str(request.product_url))

    message = await _client().messages.parse(
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        max_tokens=1500,
        system=_SYSTEM,
        messages=[{"role": "user", "content": _prompt(request, page_text)}],
        output_format=GeneratedVariations,
    )
    generated = message.parsed_output
    if generated is None or not generated.variations:
        raise GenerationError("The model did not return ad variations")

    audience = (request.target_audience or "").strip() or "General Customers"
    return AdCopyResponse(
        product_name=request.product_name,
        target_audience=audience,
        variations=generated.variations,
    )
