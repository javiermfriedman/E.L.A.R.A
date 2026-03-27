import { useState, useRef } from "react";
import { voiceRegistry } from "../../data/voiceRegistry";
import "./VoiceRegistry.css";

export default function VoiceRegistry({
  open,
  selectedVoiceId,
  onSelect,
  onClose,
}) {
  const [playingId, setPlayingId] = useState(null);
  const audioRef = useRef(null);

  function handlePlay(e, voice) {
    e.stopPropagation();

    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }

    if (playingId === voice.id) {
      setPlayingId(null);
      return;
    }

    const audio = new Audio(voice.previewUrl);
    audioRef.current = audio;
    audio.play();
    setPlayingId(voice.id);
    audio.addEventListener("ended", () => setPlayingId(null));
  }

  function handleSelect(voice) {
    if (audioRef.current) {
      audioRef.current.pause();
      setPlayingId(null);
    }
    onSelect(voice);
  }

  return (
    <div className={`voice-registry ${open ? "open" : ""}`}>
      <div className="vr-header">
        <div className="vr-header__title">◈ Voice Registry</div>
        <button className="vr-header__close" onClick={onClose}>
          ✕
        </button>
      </div>

      <div className="vr-sublabel">
        SELECT OPERATIVE VOICE — ELEVENLABS CATALOG
      </div>

      <div className="vr-list">
        {voiceRegistry.map((voice) => (
          <div
            key={voice.id}
            className={`vr-card ${selectedVoiceId === voice.id ? "selected" : ""}`}
            onClick={() => handleSelect(voice)}
          >
            <div className="vr-card__info">
              <div className="vr-card__top">
                <div className="vr-card__codename">{voice.codename}</div>
                <div className="vr-card__category">{voice.category}</div>
              </div>
              <div className="vr-card__desc">{voice.description}</div>
            </div>
            <button
              className={`vr-card__play ${playingId === voice.id ? "playing" : ""}`}
              onClick={(e) => handlePlay(e, voice)}
              title="Preview voice"
            >
              {playingId === voice.id ? "▐▐" : "▶"}
            </button>
          </div>
        ))}
      </div>

      <div className="vr-footer">
        {voiceRegistry.length} VOICES REGISTERED — CLASSIFIED
      </div>
    </div>
  );
}
