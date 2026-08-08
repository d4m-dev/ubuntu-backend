# -*- coding: utf-8 -*-
# Tên file: ubuntu-backend/api/astrology.py
from fastapi import APIRouter
from schemas.astrology_schemas import MatchRequest
from services.astrology_service import process_compatibility_match

router = APIRouter(
    prefix="/api/astrology",
    tags=["Advanced Bio Premium"]
)

@router.post("/match")
async def calculate_compatibility(data: MatchRequest):
    return process_compatibility_match(data)