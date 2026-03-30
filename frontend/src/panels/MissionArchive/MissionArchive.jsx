import { useState, useEffect } from "react";
import PanelWrapper from "../../components/ui/PanelWrapper";
import { getRecordings } from "../../services/api";
import FileModal from "./FileModal";
import "./MissionArchive.css";

function formatDate(dateStr) {
  const d = new Date(dateStr);
  return (
    d.toLocaleDateString("en-US", {
      year: "2-digit",
      month: "2-digit",
      day: "2-digit",
    }) +
    " · " +
    d.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
    })
  );
}

export default function MissionArchive({ refreshKey }) {
  const [recordings, setRecordings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    async function load() {
      const token = localStorage.getItem("elara_token");
      if (!token) return;
      try {
        const data = await getRecordings();
        setRecordings(data);
      } catch (err) {
        console.error("Failed to load recordings:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [refreshKey]);

  return (
    <>
      <PanelWrapper title="◈ Mission Archive">
        {loading ? (
          <div className="archive__empty">
            <div className="archive__empty-icon">⌛</div>
            Retrieving mission logs...
          </div>
        ) : recordings.length === 0 ? (
          <div className="archive__empty">
            <div className="archive__empty-icon">◎</div>
            No missions on record
          </div>
        ) : (
          <div className="archive__list">
            {recordings.map((rec) => (
              <div className="mission-card" key={rec.id}>
                <div className="mission-card__left">
                  <div className="mission-card__id">ID — {rec.id}</div>
                  <div className="mission-card__target">{rec.target_name}</div>
                  <div className="mission-card__date">
                    {formatDate(rec.created_at)}
                  </div>
                </div>
                <button
                  className="mission-card__btn"
                  onClick={() => setSelected(rec)}
                >
                  OPEN FILE
                </button>
              </div>
            ))}
          </div>
        )}
      </PanelWrapper>

      {selected && (
        <FileModal
          recording={selected}
          onClose={() => setSelected(null)}
          onDeleted={() => {
            setSelected(null);
            setRecordings((prev) => prev.filter((r) => r.id !== selected.id));
          }}
        />
      )}
    </>
  );
}