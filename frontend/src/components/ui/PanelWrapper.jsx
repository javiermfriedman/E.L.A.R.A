import "./PanelWrapper.css";

export default function PanelWrapper({
  title,
  glow = false,
  action = null,
  onAction = null,
  noPad = false,
  children,
}) {
  return (
    <div className={`panel ${glow ? "panel--glow" : ""}`}>
      <div className="panel__titlebar">
        <div className="panel__title-left">
          <div className="panel__indicator" />
          <div className="panel__title">{title}</div>
        </div>
        {action && (
          <button className="panel__action" onClick={onAction}>
            {action}
          </button>
        )}
      </div>
      <div className={`panel__content ${noPad ? "panel__content--noPad" : ""}`}>
        {children}
      </div>
    </div>
  );
}
