import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import get_db
from app.models.recordings import Recording


def test_audio(recording_id: int):
    db = next(get_db())
    try:
        recording = db.query(Recording).filter(Recording.id == recording_id).first()
        if not recording:
            print(f"No recording found with id {recording_id}")
            return

        filename = f"test_output_{recording.call_sid}_{recording.track}.wav"
        with open(filename, "wb") as f:
            f.write(recording.audio)

        print(f"Saved to {filename} — open it in any audio player")
    finally:
        db.close()


if __name__ == "__main__":
    recording_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    test_audio(recording_id)