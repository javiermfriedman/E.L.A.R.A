import { useEffect } from "react";
import "./AccessGranted.css";

export default function AccessGranted({ onComplete }) {
  useEffect(() => {
    const timer = setTimeout(onComplete, 2800);
    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <div className="ag">
      <div className="ag__lines">
        {Array.from({ length: 12 }).map((_, i) => (
          <div
            key={i}
            className="ag__line"
            style={{ animationDelay: `${i * 0.06}s` }}
          />
        ))}
      </div>
      <div className="ag__content">
        <div className="ag__status">VERIFYING CREDENTIALS...</div>
        <div className="ag__text" data-text="ACCESS GRANTED">
          ACCESS GRANTED
        </div>
        <div className="ag__sub">WELCOME, OPERATIVE</div>
        <div className="ag__bar">
          <div className="ag__bar-fill" />
        </div>
        <div className="ag__code">
          {[
            "IDENTITY: CONFIRMED",
            "CLEARANCE: LEVEL 7",
            "LOADING E.L.A.R.A. LOCAL SERVER..",
          ].map((line, i) => (
            <div
              key={i}
              className="ag__code-line"
              style={{ animationDelay: `${0.4 + i * 0.3}s` }}
            >
              {line}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
