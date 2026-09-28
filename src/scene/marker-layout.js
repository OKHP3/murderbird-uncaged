const MARKER_SIZE = 38;
const MARKER_GAP = 10;
const EDGE_MARGIN = MARKER_SIZE / 2 + 5;

/**
 * Keep projected inspection buttons legible when their model anchors converge.
 * Returned x/y values are button centers; leader endpoints remain the original
 * projected anchors. Callers can continue rendering the same focusable buttons.
 */
export function layoutMarkers(markers, width, height, {
  size = MARKER_SIZE,
  gap = MARKER_GAP,
  margin = EDGE_MARGIN,
  } = {}) {
  const visible = markers
    .filter(marker => marker.visible !== false && Number.isFinite(marker.x) && Number.isFinite(marker.y))
    .map(marker => ({ ...marker, anchorX: marker.x, anchorY: marker.y }));
  if (!visible.length || width <= 0 || height <= 0) return [];

  const separated = visible.every((marker, index) => visible.slice(index + 1).every(other =>
    Math.abs(marker.anchorX - other.anchorX) >= size + gap
      || Math.abs(marker.anchorY - other.anchorY) >= size + gap));
  if (separated && visible.every(marker => marker.anchorX >= size / 2 && marker.anchorX <= width - size / 2
      && marker.anchorY >= size / 2 && marker.anchorY <= height - size / 2)) {
    return visible.map(marker => withLeader(marker, marker.anchorX, marker.anchorY));
  }

  const pitch = size + gap;
  const columns = Math.max(1, Math.floor((width - 2 * margin - size) / pitch) + 1);
  const rows = Math.max(1, Math.floor((height - 2 * margin - size) / pitch) + 1);
  const slots = [];
  for (let row = 0; row < rows; row += 1) {
    for (let column = 0; column < columns; column += 1) {
      slots.push({ x: margin + size / 2 + column * pitch, y: margin + size / 2 + row * pitch });
    }
  }
  const pending = [...visible].sort((a, b) => a.anchorY - b.anchorY || a.anchorX - b.anchorX || String(a.id).localeCompare(String(b.id)));
  const placed = [];
  for (const marker of pending) {
    const candidates = slots
      .filter(slot => !placed.some(other => Math.abs(slot.x - other.x) < pitch && Math.abs(slot.y - other.y) < pitch))
      .sort((a, b) => distanceSquared(a, marker) - distanceSquared(b, marker));
    const slot = candidates[0];
    if (!slot) break;
    placed.push(withLeader(marker, slot.x, slot.y));
  }
  return placed;
}

function distanceSquared(point, marker) {
  return (point.x - marker.anchorX) ** 2 + (point.y - marker.anchorY) ** 2;
}

function withLeader(marker, x, y) {
  const dx = marker.anchorX - x;
  const dy = marker.anchorY - y;
  return {
    ...marker,
    x,
    y,
    leaderLength: Math.hypot(dx, dy),
    leaderAngle: Math.atan2(dy, dx),
  };
}
