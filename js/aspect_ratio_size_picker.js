// ComfyUI-AspectRatioSizePicker frontend extension
// Widen the node so the aspect-ratio dropdown, long-edge slider, and the
// "info" text output are not visually cropped. The Python node only declares
// inputs/outputs; node sizing lives in the frontend, so it is handled here.
import { app } from "/scripts/app.js";

const TARGET_WIDTH = 480;

app.registerExtension({
  name: "EternalShade3D.AspectRatioSizePicker",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "AspectRatioSizePicker") return;

    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;
      // Floor the node width so the dropdown + slider + info text fit.
      if (this.size[0] < TARGET_WIDTH) {
        this.size[0] = TARGET_WIDTH;
      }
      return r;
    };

    // After execution the "info" STRING output preview widget appears;
    // make sure it spans the full node width instead of being clipped.
    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function () {
      const r = onExecuted ? onExecuted.apply(this, arguments) : undefined;
      for (const w of this.widgets || []) {
        if (w.name === "info" || (w.type === "string" && w.name !== "info")) {
          if (typeof w.computeSize === "function") {
            w.width = Math.max(w.width || 0, TARGET_WIDTH - 20);
          }
        }
      }
      return r;
    };
  },
});
