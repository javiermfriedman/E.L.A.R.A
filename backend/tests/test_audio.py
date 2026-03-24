# test_audio.py
from app.database import get_db
from app.models.recordings import Recording

def test_audio(recording_id: int):
    with get_db() as db:
        recording = db.query(Recording).filter(Recording.id == recording_id).first()
        if not recording:
            print(f"No recording found with id {recording_id}")
            return

        filename = f"test_output_{recording.call_sid}_{recording.track}.wav"
        with open(filename, "wb") as f:
            f.write(recording.audio)
        
        print(f"Saved to {filename} — open it in any audio player")

test_audio(1)  # pass the id of a recording you want to check