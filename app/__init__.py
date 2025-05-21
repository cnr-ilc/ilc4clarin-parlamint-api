from fastapi import FastAPI
from app.api import enrichment, analysis
from app.core.config import settings

app = FastAPI(
    title="ParlaMint API",
    description="API for enriching and analyzing parliamentary corpus in TEI-XML format",
    version="1.0.0",
    openapi_url=f"{settings.BASE_URL}/openapi.json",
    docs_url=f"{settings.BASE_URL}/docs",
    redoc_url=f"{settings.BASE_URL}/redoc",
)

app.include_router(enrichment.router, prefix=f"{settings.BASE_URL}/api")
app.include_router(analysis.router, prefix=f"{settings.BASE_URL}/api")
