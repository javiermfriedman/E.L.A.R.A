from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from starlette import status

from app.dependencies import db_dependency, user_dependency
from app.models.recordings import Recordings
from app.schemas.recordings import RecordingsResponse

router = APIRouter(
    prefix="/recordings",
    tags=["recordings"],
)


@router.get("/", response_model=list[RecordingsResponse])
async def get_recordings(db: db_dependency, user: user_dependency):
    recordings = (
        db.query(Recordings)
        .filter(Recordings.user_id == user["id"])
        .order_by(Recordings.created_at.desc())
        .all()
    )
    return recordings


@router.get("/{recording_id}/audio", response_class=Response)
async def get_recording_audio(
    recording_id: int,
    db: db_dependency,
    user: user_dependency,
):
    recording = (
        db.query(Recordings)
        .filter(
            Recordings.id == recording_id,
            Recordings.user_id == user["id"],
        )
        .first()
    )
    if not recording:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")
    return Response(
        content=recording.audio,
        media_type="audio/wav",
        headers={"Content-Disposition": f'inline; filename="recording-{recording_id}.wav"'},
    )
