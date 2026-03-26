import { useState, useEffect, useRef } from "react";
import PanelWrapper from "../../components/ui/PanelWrapper";
import { getContacts, createContact } from "../../services/api";
import "./Contacts.css";

function AddTargetModal({ onClose, onAdded }) {
  const [form, setForm] = useState({ name: "", phone_number: "" });
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
    if (!form.name || !form.phone_number || !imageFile) {
      setError("⚠ ALL FIELDS + IMAGE REQUIRED");
      return;
    }
    setLoading(true);
    try {
      const fd = new FormData();
      fd.append("name", form.name);
      fd.append("phone_number", form.phone_number);
      fd.append("image", imageFile);

      const newContact = await createContact(fd);
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
          {/* Image upload */}
          <div className="modal-image-upload">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/webp"
              className="modal-image-upload__file"
              onChange={handleImage}
            />
            {imagePreview ? (
              <img
                src={imagePreview}
                className="modal-image-upload__preview"
                alt="preview"
              />
            ) : (
              <div
                className="modal-image-upload__placeholder"
                onClick={() => fileInputRef.current.click()}
              >
                ＋
              </div>
            )}
            <div
              className="modal-image-upload__label"
              onClick={() => fileInputRef.current.click()}
            >
              {imagePreview ? "[ change photo ]" : "[ upload target photo ]"}
            </div>
          </div>

          {/* Name */}
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

          {/* Phone */}
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
                  {contact.image ? (
                    <img
                      src={`data:image/png;base64,${contact.image}`}
                      alt={contact.name}
                      className="contact-item__avatar"
                    />
                  ) : (
                    <div className="contact-item__avatar-placeholder">👤</div>
                  )}
                  <div className="contact-item__info">
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
