import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request
from sqlalchemy import func, select

from app.database import async_session
from app.models.roast import Roast
from app.schemas.roast import (
    RepoMetadata,
    RoastFeedItem,
    RoastFeedResponse,
    RoastRequest,
    RoastResponse,
    RoastResult,
    RoastSubmitResponse,
)
from app.services import analyzer, github
from app.services.roaster import generate_roast

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# Simple in-memory rate limiter: {ip: [timestamps]}
_rate_limits: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_MAX = 10
_RATE_LIMIT_WINDOW = 60  # seconds


def _check_rate_limit(ip: str) -> bool:
    now = time.time()
    timestamps = _rate_limits[ip]
    # Clean old entries
    _rate_limits[ip] = [t for t in timestamps if now - t < _RATE_LIMIT_WINDOW]
    return len(_rate_limits[ip]) < _RATE_LIMIT_MAX


def _record_request(ip: str) -> None:
    _rate_limits[ip].append(time.time())


async def _update_status(
    roast_id: str,
    status: str,
    error_message: str | None = None,
    **kwargs,
) -> None:
    async with async_session() as session:
        result = await session.execute(select(Roast).where(Roast.id == roast_id))
        roast = result.scalar_one_or_none()
        if roast:
            roast.status = status
            if error_message is not None:
                roast.error_message = error_message
            for key, value in kwargs.items():
                setattr(roast, key, value)
            await session.commit()


async def process_roast(roast_id: str) -> None:
    try:
        # Get roast details
        async with async_session() as session:
            result = await session.execute(select(Roast).where(Roast.id == roast_id))
            roast = result.scalar_one_or_none()
            if not roast:
                return
            owner = roast.repo_owner
            name = roast.repo_name
            brutality_level = roast.brutality_level

        # Step 1: Fetch metadata
        await _update_status(roast_id, "analyzing")
        metadata = await github.fetch_repo_metadata(owner, name)

        async with async_session() as session:
            result = await session.execute(select(Roast).where(Roast.id == roast_id))
            roast = result.scalar_one_or_none()
            if roast:
                roast.repo_metadata = json.dumps(metadata.model_dump())
                await session.commit()

        # Step 2: Analyze repo
        analysis = await analyzer.analyze_repo(owner, name, metadata)

        async with async_session() as session:
            result = await session.execute(select(Roast).where(Roast.id == roast_id))
            roast = result.scalar_one_or_none()
            if roast:
                roast.analysis_result = json.dumps(analysis)
                await session.commit()

        # Step 3: Generate roast
        await _update_status(roast_id, "roasting")
        roast_result = await generate_roast(
            owner, name, metadata, analysis, brutality_level
        )

        # Step 4: Save results and mark complete
        now = datetime.now(timezone.utc).isoformat()
        async with async_session() as session:
            result = await session.execute(select(Roast).where(Roast.id == roast_id))
            roast_record = result.scalar_one_or_none()
            if roast_record:
                roast_record.roast_result = json.dumps(roast_result.model_dump())
                roast_record.overall_score = roast_result.overall_score
                roast_record.letter_grade = roast_result.letter_grade
                roast_record.status = "complete"
                roast_record.completed_at = now
                await session.commit()

    except Exception as e:
        logger.exception("Failed to process roast %s", roast_id)
        await _update_status(roast_id, "failed", error_message=str(e))


@router.post("/roast", status_code=202, response_model=RoastSubmitResponse)
async def submit_roast(request: Request, body: RoastRequest):
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait a moment.",
            headers={"Retry-After": "60"},
        )
    _record_request(client_ip)

    # Parse owner/repo from URL
    url = body.repo_url.rstrip("/")
    parts = url.replace("https://github.com/", "").split("/")
    owner, name = parts[0], parts[1]

    # Verify repo exists
    exists = await github.verify_repo(owner, name)
    if not exists:
        raise HTTPException(
            status_code=404,
            detail="Repository not found. Make sure it exists and is public.",
        )

    # Create roast record
    roast_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    async with async_session() as session:
        roast = Roast(
            id=roast_id,
            repo_url=url,
            repo_owner=owner,
            repo_name=name,
            brutality_level=body.brutality_level,
            status="pending",
            created_at=now,
        )
        session.add(roast)
        await session.commit()

    # Launch background task
    asyncio.create_task(process_roast(roast_id))

    return RoastSubmitResponse(
        id=roast_id,
        status="pending",
        repo_url=url,
        repo_owner=owner,
        repo_name=name,
        brutality_level=body.brutality_level,
        created_at=now,
    )


@router.get("/roast/{roast_id}", response_model=RoastResponse)
async def get_roast(roast_id: str):
    async with async_session() as session:
        result = await session.execute(select(Roast).where(Roast.id == roast_id))
        roast = result.scalar_one_or_none()

    if not roast:
        raise HTTPException(status_code=404, detail="Roast not found")

    return RoastResponse(
        id=roast.id,
        status=roast.status,
        repo_url=roast.repo_url,
        repo_owner=roast.repo_owner,
        repo_name=roast.repo_name,
        brutality_level=roast.brutality_level,
        error_message=roast.error_message,
        repo_metadata=(
            RepoMetadata(**json.loads(roast.repo_metadata))
            if roast.repo_metadata
            else None
        ),
        roast_result=(
            RoastResult(**json.loads(roast.roast_result))
            if roast.roast_result
            else None
        ),
        overall_score=roast.overall_score,
        letter_grade=roast.letter_grade,
        created_at=roast.created_at,
        completed_at=roast.completed_at,
    )


@router.get("/roasts/recent", response_model=RoastFeedResponse)
async def get_recent_roasts(
    limit: int = Query(default=20, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
):
    async with async_session() as session:
        # Count total completed roasts
        count_result = await session.execute(
            select(func.count(Roast.id)).where(Roast.status == "complete")
        )
        total = count_result.scalar() or 0

        # Fetch page
        result = await session.execute(
            select(Roast)
            .where(Roast.status == "complete")
            .order_by(Roast.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        roasts = result.scalars().all()

    items = []
    for r in roasts:
        roast_data = json.loads(r.roast_result) if r.roast_result else {}
        metadata = json.loads(r.repo_metadata) if r.repo_metadata else {}

        items.append(
            RoastFeedItem(
                id=r.id,
                repo_url=r.repo_url,
                repo_owner=r.repo_owner,
                repo_name=r.repo_name,
                brutality_level=r.brutality_level,
                overall_score=r.overall_score or 0,
                letter_grade=r.letter_grade or "F",
                top_burns=roast_data.get("top_burns", []),
                repo_metadata=RepoMetadata(**metadata),
                completed_at=r.completed_at or "",
            )
        )

    return RoastFeedResponse(
        roasts=items,
        total=total,
        limit=limit,
        offset=offset,
    )
