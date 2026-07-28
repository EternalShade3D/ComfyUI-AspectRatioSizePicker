// ComfyUI-AspectRatioSizePicker frontend extension
// - Widens the node so the dropdown / slider / info text are not cropped.
// - When the "invert" toggle is flipped, the aspect-ratio dropdown labels
//   swap to their inverted equivalents (4:3 -> 3:4, 16:9 -> 9:16) so the
//   user immediately sees the orientation they selected.
import { app } from "/scripts/app.js";

const TARGET_WIDTH = 560;

const NORMAL = [
  "1:1 (Square)",
  "4:3 (Standard)",
  "3:2 (Classic 35mm Film)",
  "5:4 (Large Format)",
  "16:9 (Widescreen)",
  "16:10 (Widescreen)",
];
const INVERTED = [
  "1:1 (Square)",
  "3:4 (Standard)",
  "2:3 (Classic 35mm Film)",
  "4:5 (Large Format)",
  "9:16 (Widescreen)",
  "10:16 (Widescreen)",
];

// Swap the aspect-ratio dropdown options/value to match the invert state.
function swapAspectOptions(node, invert) {
  const w = node.widgets && node.widgets.find((x) => x.name === "aspect_ratio");
  if (!w) return;
  const list = invert ? INVERTED : NORMAL;
  // Find which canonical index the current value came from.
  let idx = NORMAL.indexOf(w.value);
  if (idx === -1) idx = INVERTED.indexOf(w.value);
  if (idx === -1) idx = 0;
  w.options.values = list.slice();
  w.value = list[idx];
  if (w.callback) w.callback(w.value);
}

app.registerExtension({
  name: "EternalShade3D.AspectRatioSizePicker",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "AspectRatioSizePicker") return;

    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
      // Floor the node width so the dropdown + slider + info text fit.
      if (this.size[0] < TARGET_WIDTH) this.size[0] = TARGET_WIDTH;

      // Make the invert toggle flip the visible dropdown labels.
      const inv = this.widgets && this.widgets.find((x) => x.name === "invert");
      const ar = this.widgets && this.widgets.find((x) => x.name === "aspect_ratio");
      if (inv && ar) {
        const initInvert = !!inv.value;
        // Ensure the dropdown starts on the correct orientation set.
        if (initInvert !== (INVERTED.indexOf(ar.value) !== -1)) {
          swapAspectOptions(this, initInvert);
        }
        const origCb = inv.callback;
        inv.callback = (v) => {
          if (origCb) origCb(v);
          swapAspectOptions(this, !!v);
        };
      }
      return r;
    };

    // Keep the info STRING output widget wide so text is not clipped.
    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function () {
      const r = onExecuted ? onExecuted.apply(this, arguments) : undefined;
      for (const w of this.widgets || []) {
        if (w.name === "info" || (w.type === "string" && w.name !== "info")) {
          w.width = Math.max(w.width || 0, TARGET_WIDTH - 20);
        }
      }
      return r;
    };
  },
});
