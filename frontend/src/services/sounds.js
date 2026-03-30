const ctx = new (window.AudioContext || window.webkitAudioContext)();

function beep(frequency = 440, duration = 80, volume = 0.1, type = "square") {
  const oscillator = ctx.createOscillator();
  const gain = ctx.createGain();

  oscillator.connect(gain);
  gain.connect(ctx.destination);

  oscillator.type = type;
  oscillator.frequency.setValueAtTime(frequency, ctx.currentTime);
  gain.gain.setValueAtTime(volume, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(
    0.001,
    ctx.currentTime + duration / 1000,
  );

  oscillator.start(ctx.currentTime);
  oscillator.stop(ctx.currentTime + duration / 1000);
}

export function soundClick() {
  beep(600, 60, 0.08, "square");
}
export function soundConfirm() {
  beep(880, 120, 0.1, "sine");
}
export function soundAbort() {
  beep(220, 200, 0.12, "sawtooth");
}
export function soundPurge() {
  beep(150, 400, 0.15, "sawtooth");
}
export function soundError() {
  beep(180, 300, 0.1, "square");
}
export function soundLaunch() {
  beep(440, 100, 0.1, "square");
  setTimeout(() => beep(660, 100, 0.1, "square"), 100);
  setTimeout(() => beep(880, 200, 0.12, "sine"), 200);
}
