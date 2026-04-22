"""
This script is used to launch the sequence of steps to run the bot.
"""
import os
import subprocess
import sys
import time

_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
_JARVIS_AUDIO = os.path.join(_REPO_ROOT, "jarvis_audio")
TRACK_URI = "spotify:track:0G0SPViSDa3ajAkzna1bZD"  
SPOTIFY_VOLUME = 40  # 0–100 — low enough so J.A.R.V.I.S. is heard over the music

def set_spotify_volume(volume: int):
    """Set Spotify's volume via AppleScript (macOS only)."""
    subprocess.run([
        "osascript", "-e",
        f'tell application "Spotify" to set sound volume to {volume}'
    ])

def open_spotify():
    if sys.platform == "darwin":  # macOS
        # Open Spotify with the track URI
        subprocess.Popen(["open", TRACK_URI])
        set_spotify_volume(90)

    print("Opening Spotify and playing 'Should I Stay or Should I Go' by The Clash...")


def play_saved_audio(filepath, background=False):
    """Play an MP3 file using macOS's built-in afplay command. Skips empty/missing files."""
    if not os.path.isfile(filepath) or os.path.getsize(filepath) == 0:
        print(f"⚠️  Skipping {os.path.basename(filepath)} (missing or empty)")
        return
    if background:
        subprocess.Popen(["afplay", filepath])
    else:
        subprocess.run(["afplay", filepath])

def fake_terminal_output():
    """Open a new Terminal window and print cinematic boot sequence diagnostics."""
    import tempfile, os
    lines = [
        "[BOOT]    J.A.R.V.I.S. kernel v4.7.12-arc .................. LOADED",
        "[SYS]     Allocating neural-net co-processors ............... OK",
        "[SYS]     Mounting /stark/home/lab .......................... OK",
        "[NET]     Secure uplink to Stark Industries ................. ESTABLISHED",
        "[CRYPTO]  AES-512 handshake ................................. VERIFIED",
        "[HW]      Arc reactor interface ............................. STABLE  (3.2 GW)",
        "[DIAG]    Running self-diagnostics .......................... PASS  (137 modules)",
        "[AI]      Loading language model weights .................... OK  (8.4 GB)",
        "[AI]      Initialising Silero VAD analyser .................. OK",
        "[AUDIO]   Deepgram STT pipeline ............................. ONLINE",
        "[AUDIO]   ElevenLabs TTS voice (George) ..................... ONLINE",
        "[AUDIO]   Echo cancellation ................................. ACTIVE",
        "[WEBRTC]  STUN/TURN negotiation ............................. READY",
        "[WEBRTC]  Signalling server on :8000 ....................... LISTENING",
        "[VITE]    Frontend dev server on :5741 ..................... COMPILED",
        "[SEC]     Perimeter scan .................................... CLEAR",
        "[SYS]     All subsystems nominal. Awaiting command, sir.",
    ]

    # Write a temp shell script so we avoid AppleScript quoting issues
    script = "#!/bin/bash\nclear\n"
    for line in lines:
        script += f'sleep 0.$(( RANDOM % 14 + 5 ))\n'
        script += f"echo '{line}'\n"
    script += "# self-cleanup\nrm -- \"$0\"\n"

    fd, path = tempfile.mkstemp(suffix=".sh")
    with os.fdopen(fd, "w") as f:
        f.write(script)
    os.chmod(path, 0o755)

    subprocess.Popen([
        "osascript", "-e",
        f'''tell app "Terminal"
            activate
            do script "{path}"
        end tell'''
    ])

def start_dev_server():
    print("Starting E.L.A.R.A. backend server in new terminal...")
    subprocess.Popen([
        "osascript", "-e",
        '''tell app "Terminal"
            activate
            do script "cd /Users/javierfriedman/Code/E.L.A.R.A/backend && ngrok http 8000"
        end tell'''
    ])
    subprocess.Popen([
        "osascript", "-e",
        '''tell app "Terminal"
            activate
            do script "cd /Users/javierfriedman/Code/E.L.A.R.A/backend && /Users/javierfriedman/Code/E.L.A.R.A/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000"
        end tell'''
    ])

    subprocess.Popen([
        "osascript", "-e",
        '''tell app "Terminal"
            activate
            do script "cd /Users/javierfriedman/Code/E.L.A.R.A/frontend && npm run dev"
        end tell'''
    ])

    # Poll until both servers are ready
    import urllib.request, urllib.error
    backend_up = False
    frontend_up = False

    for attempt in range(35):
        time.sleep(1)

        if not backend_up:
            try:
                urllib.request.urlopen("http://localhost:8000")
                backend_up = True
            except urllib.error.HTTPError:
                # 404 etc. means the server IS responding — it's up
                backend_up = True
            except Exception as e:
                print(f"  ⏳ Waiting for backend... (attempt {attempt+1}, {e.__class__.__name__})")

        if backend_up and not frontend_up:
            try:
                urllib.request.urlopen("http://localhost:5173/")
                frontend_up = True
            except urllib.error.HTTPError:
                frontend_up = True
            except Exception as e:
                print(f"  ⏳ Waiting for frontend on :5741... (attempt {attempt+1}, {e.__class__.__name__})")


        if backend_up:
            print("✅ Backend ready!")
        if frontend_up:
            print("✅ Frontend ready!")

        if backend_up and frontend_up:
            time.sleep(1.5)
            browser = "Arc"
            subprocess.Popen(["open", "-a", browser, "http://localhost:5173"])
            break
    else:
        print("❌ Servers never became ready — check the Terminal windows for errors.")
    
if __name__ == "__main__":
    start_dev_server()  
