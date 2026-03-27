import { useState, useEffect, useRef } from "react";
import PanelWrapper from "../../components/ui/PanelWrapper";
import { getAgents, createAgent } from "../../services/api";
import "./Agents.css";

function CreateAgentModal({ onClose, onAdded }) {
  const [form, setForm] = useState({
    name: "",
    description: "",
    system_prompt: "",
    first_message: "",
    voice_id: "zmcVlqmyk3Jpn5AVYcAL",
  });
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef();

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setError("");
  }

  function handleImage(e) {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  }

  async function handleSubmit() {
    if (
      !form.name ||
      !form.description ||
      !form.system_prompt ||
      !form.first_message ||
      !imageFile
    ) {
      setError("⚠ ALL FIELDS + IMAGE REQUIRED");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const fd = new FormData();
      fd.append("name", form.name);
      fd.append("description", form.description);
      fd.append("system_prompt", form.system_prompt);
      fd.append("first_message", form.first_message);
      fd.append("voice_id", form.voice_id);
      fd.append("image", imageFile);

      const newAgent = await createAgent(fd);
      onAdded(newAgent);
      onClose();
    } catch (err) {
      setError(`⚠ ${err.message.toUpperCase()}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal__header">
          <div className="modal__title">◈ Deploy New Agent</div>
          <button className="modal__close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal__body">
          {/* Image upload */}
          <div className="agent-modal__image-upload">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/webp"
              className="agent-modal__file-input"
              onChange={handleImage}
            />
            {imagePreview ? (
              <img
                src={imagePreview}
                className="agent-modal__preview"
                alt="preview"
              />
            ) : (
              <div
                className="agent-modal__preview-placeholder"
                onClick={() => fileInputRef.current.click()}
              >
                ＋
              </div>
            )}
            <div
              className="agent-modal__upload-label"
              onClick={() => fileInputRef.current.click()}
            >
              {imagePreview ? "[ change image ]" : "[ upload agent image ]"}
            </div>
          </div>

          {/* Name */}
          <div className="modal-field">
            <label className="modal-field__label">Agent Designation</label>
            <div className="modal-field__input-wrap">
              <span className="modal-field__prefix">▸</span>
              <input
                className="modal-field__input"
                type="text"
                name="name"
                placeholder="e.g. AGENT CHAOS..."
                value={form.name}
                onChange={handleChange}
                autoComplete="off"
                spellCheck="false"
              />
            </div>
          </div>

          {/* Description */}
          <div className="modal-field">
            <label className="modal-field__label">Persona Brief</label>
            <textarea
              className="modal-field__textarea"
              name="description"
              placeholder="short description of the agent's personality..."
              value={form.description}
              onChange={handleChange}
              spellCheck="false"
            />
          </div>

          {/* System prompt */}
          <div className="modal-field">
            <label className="modal-field__label">System Prompt</label>
            <textarea
              className="modal-field__textarea"
              name="system_prompt"
              placeholder="you are a prank caller who..."
              value={form.system_prompt}
              onChange={handleChange}
              spellCheck="false"
            />
          </div>

          {/* First message */}
          <div className="modal-field">
            <label className="modal-field__label">Opening Line</label>
            <textarea
              className="modal-field__textarea"
              name="first_message"
              placeholder="the first thing the agent says when the target picks up..."
              value={form.first_message}
              onChange={handleChange}
              spellCheck="false"
            />
          </div>

          {/* Voice ID */}
          <div className="modal-field">
            <label className="modal-field__label">Voice ID (ElevenLabs)</label>
            <div className="modal-field__input-wrap">
              <span className="modal-field__prefix">▸</span>
              <input
                className="modal-field__input"
                type="text"
                name="voice_id"
                placeholder="voice id..."
                value={form.voice_id}
                onChange={handleChange}
                autoComplete="off"
                spellCheck="false"
              />
            </div>
          </div>

          {error && <div className="modal__error">{error}</div>}
        </div>

        <div className="modal__footer">
          <button className="modal__btn modal__btn--cancel" onClick={onClose}>
            Abort
          </button>
          <button
            className="modal__btn modal__btn--confirm"
            onClick={handleSubmit}
            disabled={loading}
          >
            <span>{loading ? "Deploying..." : "⌗ Deploy Agent"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}

function AgentCard({ agent, selectedId, onSelect }) {
  const [expanded, setExpanded] = useState(false);
  const isSelected = selectedId === agent.id;

  return (
    <div
      className={`agent-card ${expanded ? "expanded" : ""} ${isSelected ? "selected" : ""}`}
    >
      {/* Header — always visible */}
      <button
        className="agent-card__header"
        onClick={() => setExpanded((e) => !e)}
      >
        {agent.image ? (
          <img
            src={`data:image/png;base64,${agent.image}`}
            alt={agent.name}
            className="agent-card__avatar"
          />
        ) : (
          <div className="agent-card__avatar-placeholder">🤖</div>
        )}

        <div className="agent-card__info">
          <div className="agent-card__name">{agent.name}</div>
          <div className="agent-card__status">READY FOR DEPLOYMENT</div>
        </div>

        <div className="agent-card__right">
          <div className="agent-card__badge">
            {isSelected ? "ACTIVE" : "STANDBY"}
          </div>
          <div className="agent-card__chevron">▼</div>
        </div>
      </button>

      {/* Slide-down body */}
      <div className={`agent-card__body ${expanded ? "open" : ""}`}>
        <div className="agent-card__body-inner">
          <div className="agent-card__field">
            <div className="agent-card__field-label">Persona Brief</div>
            <div className="agent-card__field-value">{agent.description}</div>
          </div>
          <div className="agent-card__field">
            <div className="agent-card__field-label">System Prompt</div>
            <div className="agent-card__field-value agent-card__field-value--prompt">
              {agent.system_prompt}
            </div>
          </div>
          <div className="agent-card__field">
            <div className="agent-card__field-label">Opening Line</div>
            <div className="agent-card__field-value">{agent.first_message}</div>
          </div>
        </div>

        <button
          className="agent-card__select-btn"
          onClick={() => onSelect(agent)}
        >
          {isSelected ? "✓ AGENT ACTIVE" : "⌗ SELECT AGENT"}
        </button>
      </div>
    </div>
  );
}

export default function Agents({ selectedId, onSelect }) {
  const [agents, setAgents] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const token = localStorage.getItem("elara_token");
      if (!token) return;
      try {
        const data = await getAgents();
        setAgents(data);
      } catch (err) {
        console.error("Failed to load agents:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  function handleAdded(newAgent) {
    setAgents((prev) => [...prev, newAgent]);
  }

  return (
    <>
      <PanelWrapper
        title="◈ Agents"
        action="+ Deploy Agent"
        onAction={() => setShowModal(true)}
      >
        {loading ? (
          <div className="agents__empty">
            <div className="agents__empty-icon">⌛</div>
            Loading agents...
          </div>
        ) : agents.length === 0 ? (
          <div className="agents__empty">
            <div className="agents__empty-icon">◎</div>
            No agents deployed
          </div>
        ) : (
          <div className="agents__list">
            {agents.map((agent) => (
              <AgentCard
                key={agent.id}
                agent={agent}
                selectedId={selectedId}
                onSelect={onSelect}
              />
            ))}
          </div>
        )}
      </PanelWrapper>

      {showModal && (
        <CreateAgentModal
          onClose={() => setShowModal(false)}
          onAdded={handleAdded}
        />
      )}
    </>
  );
}
