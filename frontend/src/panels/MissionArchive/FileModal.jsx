import { useState, useEffect, useRef } from "react";
import { getRecordingAudio } from "../../services/api";
import "./FileModal.css";

function TapeReel({ spinning }) {
  return (
    <div className="tape-reel">
      <div className={`tape-reel__outer ${spinning ? "spinning" : ""}`}>
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="tape-reel__spoke" />
        ))}
        <div className="tape-reel__hub" />
      </div>
    </div>
  );
}

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return (
    d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }) +
    " " +
    d.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
    })
  );
}

export default function FileModal({ recording, onClose }) {
  const [audioUrl, setAudioUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [playing, setPlaying] = useState(false);
  const [error, setError] = useState("");
  const audioRef = useRef(null);

  useEffect(() => {
    async function loadAudio() {
      try {
        const url = await getRecordingAudio(recording.id);
        setAudioUrl(url);
      } catch (err) {
        setError("AUDIO UNAVAILABLE");
        console.error("Audio load error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadAudio();

    return () => {
      if (audioUrl) URL.revokeObjectURL(audioUrl);
    };
  }, [recording.id]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    function handleEnded() {
      setPlaying(false);
    }
    audio.addEventListener("ended", handleEnded);
    return () => audio.removeEventListener("ended", handleEnded);
  }, [audioUrl]);

  function togglePlay() {
    const audio = audioRef.current;
    if (!audio) return;
    if (playing) {
      audio.pause();
      setPlaying(false);
    } else {
      audio.play();
      setPlaying(true);
    }
  }

  return (
    <div className="file-modal-overlay" onClick={onClose}>
      <div className="file-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="file-modal__header">
          <div className="file-modal__title">◈ Classified Mission File</div>
          <button className="file-modal__close" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Metadata */}
        <div className="file-modal__meta">
          <div className="file-modal__row">
            <div className="file-modal__key">Operation</div>
            <div className="file-modal__val file-modal__val--amber">
              ID-{recording.id}
            </div>
          </div>
          <div className="file-modal__row">
            <div className="file-modal__key">Target</div>
            <div className="file-modal__val">{recording.target_name}</div>
          </div>
          <div className="file-modal__row">
            <div className="file-modal__key">Comms</div>
            <div className="file-modal__val file-modal__val--dim">
              {recording.to_number}
            </div>
          </div>
          <div className="file-modal__row">
            <div className="file-modal__key">Mission Date</div>
            <div className="file-modal__val file-modal__val--dim">
              {formatDate(recording.created_at)}
            </div>
          </div>
        </div>

        {/* Tape deck */}
        <div className="tape-deck">
          {loading ? (
            <div className="tape-deck__loading">⌗ LOADING AUDIO INTEL...</div>
          ) : error ? (
            <div
              className="tape-deck__loading"
              style={{ color: "var(--color-red)" }}
            >
              {error}
            </div>
          ) : (
            <>
              <div className="tape-deck__reels">
                <TapeReel spinning={playing} />
                <div className="tape-deck__path">
                  <div className="tape-deck__path-line" />
                  <div className="tape-deck__path-label">TAPE</div>
                  <div className="tape-deck__path-line" />
                </div>
                <TapeReel spinning={playing} />
              </div>

              <div className="tape-deck__controls">
                <button
                  className="tape-deck__play"
                  onClick={togglePlay}
                  disabled={!audioUrl}
                >
                  {playing ? "▐▐" : "▶"}
                </button>
                <div
                  className={`tape-deck__status ${playing ? "tape-deck__status--playing" : ""}`}
                >
                  {playing ? "● PLAYING" : "● STOPPED"}
                </div>
              </div>

              {audioUrl && (
                <audio ref={audioRef} src={audioUrl} preload="auto" />
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="file-modal__footer">
          <div className="file-modal__footer-label">
            ELARA PRANK OPS — EYES ONLY
          </div>
          <div className="file-modal__footer-tag">CLASSIFIED</div>
        </div>
      </div>
    </div>
  );
}
