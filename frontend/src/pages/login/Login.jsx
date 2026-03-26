import { useState } from "react";
import { login, register } from "../../services/api";
import { useElara } from "../../context/ElaraContext";
import "./Login.css";

export default function Login({ onLogin }) {
  const { saveToken } = useElara();
  const [tab, setTab] = useState("login");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({ username: "", password: "", confirm: "" });

  function handleChange(e) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setError("");
  }

  async function handleSubmit(e) {
    e.preventDefault();

    if (!form.username || !form.password) {
      setError("⚠ ALL FIELDS REQUIRED");
      return;
    }

    if (tab === "register" && form.password !== form.confirm) {
      setError("⚠ PASSWORD MISMATCH — RETRY");
      return;
    }

    setLoading(true);
    setError("");

    try {
      if (tab === "register") {
        await register(form.username, form.password);
        // Auto-login after register
      }

      const data = await login(form.username, form.password);
      saveToken(data.access_token);
      onLogin();
    } catch (err) {
      setError(`⚠ ${err.message.toUpperCase()}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-page__grid" />
      <div className="login-page__corner login-page__corner--tl" />
      <div className="login-page__corner login-page__corner--tr" />
      <div className="login-page__corner login-page__corner--bl" />
      <div className="login-page__corner login-page__corner--br" />

      <div className="login-card">
        <div className="login-card__header">
          <div className="login-card__logo">◈ CLASSIFIED SYSTEM ◈</div>
          <div className="login-card__title" data-text="E.L.A.R.A">
            E.L.A.R.A
          </div>
          <div className="login-card__subtitle">
            Enhanced Laughter &amp; Absurdity Response Agent
          </div>
        </div>

        <div className="login-card__divider">AUTHORIZATION REQUIRED</div>

        <div className="login-tabs">
          <button
            className={`login-tabs__btn ${tab === "login" ? "active" : ""}`}
            onClick={() => {
              setTab("login");
              setError("");
            }}
          >
            [ ACCESS ]
          </button>
          <button
            className={`login-tabs__btn ${tab === "register" ? "active" : ""}`}
            onClick={() => {
              setTab("register");
              setError("");
            }}
          >
            [ ENLIST ]
          </button>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="login-form__field">
            <label className="login-form__label">Operative ID</label>
            <div className="login-form__input-wrap">
              <span className="login-form__prefix">▸</span>
              <input
                className="login-form__input"
                type="text"
                name="username"
                placeholder="enter codename..."
                value={form.username}
                onChange={handleChange}
                autoComplete="off"
                spellCheck="false"
              />
            </div>
          </div>

          <div className="login-form__field">
            <label className="login-form__label">Auth Sequence</label>
            <div className="login-form__input-wrap">
              <span className="login-form__prefix">▸</span>
              <input
                className="login-form__input"
                type="password"
                name="password"
                placeholder="enter passphrase..."
                value={form.password}
                onChange={handleChange}
              />
            </div>
          </div>

          {tab === "register" && (
            <div className="login-form__field">
              <label className="login-form__label">Confirm Sequence</label>
              <div className="login-form__input-wrap">
                <span className="login-form__prefix">▸</span>
                <input
                  className="login-form__input"
                  type="password"
                  name="confirm"
                  placeholder="confirm passphrase..."
                  value={form.confirm}
                  onChange={handleChange}
                />
              </div>
            </div>
          )}

          {error && <div className="login-form__error">{error}</div>}

          <button
            className="login-form__submit"
            type="submit"
            disabled={loading}
          >
            <span>
              {loading
                ? "⌗ AUTHENTICATING..."
                : tab === "login"
                  ? "⌗ INITIATE ACCESS"
                  : "⌗ ENLIST OPERATIVE"}
            </span>
          </button>
        </form>

        <div className="login-card__footer">
          FRIEDMAN POWERED v1.0.0 — EYES ONLY — UNAUTHORIZED ACCESS PROHIBITED
        </div>
      </div>
    </div>
  );
}
