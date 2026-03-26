import { useState, useEffect } from "react";
import PanelWrapper from "../../components/ui/PanelWrapper";
import { getContacts, createContact } from "../../services/api";
import "./Contacts.css";

function AddTargetModal({ onClose, onAdded }) {
  const [form, setForm] = useState({ name: "", phone_number: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setError("");
  }

  async function handleSubmit() {
    if (!form.name || !form.phone_number) {
      setError("⚠ ALL FIELDS REQUIRED");
      return;
    }
    setLoading(true);
    try {
      const newContact = await createContact(form.name, form.phone_number);
      onAdded(newContact);
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
          <div className="modal__title">◈ Register New Target</div>
          <button className="modal__close" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal__body">
          <div className="modal-field">
            <label className="modal-field__label">Target Codename</label>
            <div className="modal-field__input-wrap">
              <span className="modal-field__prefix">▸</span>
              <input
                className="modal-field__input"
                type="text"
                name="name"
                placeholder="enter target name..."
                value={form.name}
                onChange={handleChange}
                autoComplete="off"
                spellCheck="false"
              />
            </div>
          </div>

          <div className="modal-field">
            <label className="modal-field__label">Comms Channel (Phone)</label>
            <div className="modal-field__input-wrap">
              <span className="modal-field__prefix">▸</span>
              <input
                className="modal-field__input"
                type="tel"
                name="phone_number"
                placeholder="enter phone number..."
                value={form.phone_number}
                onChange={handleChange}
                autoComplete="off"
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
            <span>{loading ? "Registering..." : "⌗ Confirm Target"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Contacts({ selectedId, onSelect }) {
  const [contacts, setContacts] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      const token = localStorage.getItem("elara_token");
      if (!token) return;

      try {
        const data = await getContacts();
        setContacts(data);
      } catch (err) {
        console.error("Failed to load contacts:", err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  function handleAdded(newContact) {
    setContacts((prev) => [...prev, newContact]);
  }

  return (
    <>
      <PanelWrapper
        title="◈ Targets"
        action="+ Add Target"
        onAction={() => setShowModal(true)}
      >
        <div className="contacts">
          {loading ? (
            <div className="contacts__empty">
              <div className="contacts__empty-icon">⌛</div>
              Loading targets...
            </div>
          ) : contacts.length === 0 ? (
            <div className="contacts__empty">
              <div className="contacts__empty-icon">◎</div>
              No targets registered
            </div>
          ) : (
            <div className="contacts__list">
              {contacts.map((contact) => (
                <button
                  key={contact.id}
                  className={`contact-item ${selectedId === contact.id ? "selected" : ""}`}
                  onClick={() => onSelect(contact)}
                >
                  <div className="contact-item__left">
                    <div className="contact-item__name">{contact.name}</div>
                    <div className="contact-item__phone">
                      {contact.phone_number}
                    </div>
                  </div>
                  <div className="contact-item__badge">
                    {selectedId === contact.id ? "SELECTED" : "TARGET"}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </PanelWrapper>

      {showModal && (
        <AddTargetModal
          onClose={() => setShowModal(false)}
          onAdded={handleAdded}
        />
      )}
    </>
  );
}
