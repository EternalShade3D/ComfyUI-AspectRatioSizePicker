import sys, struct, zlib, json, os

def extract_png_text_chunks(path):
    with open(path, "rb") as f:
        assert f.read(8) == b"\x89PNG\r\n\x1a\n"
        texts = {}
        while True:
            hdr = f.read(8)
            if len(hdr) < 8:
                break
            ln = struct.unpack(">I", hdr[:4])[0]
            typ = hdr[4:8].decode("latin1")
            data = f.read(ln)
            f.read(4)
            if typ in ("tEXt", "iTXt", "zTXt"):
                if typ == "tEXt":
                    key, _, txt = data.partition(b"\x00")
                    texts[key.decode("latin1")] = txt.decode("utf-8", "replace")
                elif typ == "iTXt":
                    key, rest = data.split(b"\x00", 1)
                    comp = rest[0]
                    tail = rest[1:]
                    _, tail = tail.split(b"\x00", 1)
                    _, txt = tail.split(b"\x00", 1)
                    texts[key.decode("latin1")] = (
                        zlib.decompress(txt).decode("utf-8", "replace") if comp == 1
                        else txt.decode("utf-8", "replace"))
                else:
                    key, rest = data.split(b"\x00", 1)
                    texts[key.decode("latin1")] = zlib.decompress(rest).decode("utf-8", "replace")
            if typ == "IEND":
                break
    return texts

def summarize_prompts(workflow_text):
    obj = json.loads(workflow_text)
    nodes = obj.get("nodes", [])
    out = []
    for n in nodes:
        t = n.get("type") or n.get("class_type") or ""
        wv = n.get("widgets_values")
        if not wv:
            continue
        tl = t.lower()
        if "textgenerate" in tl:
            out.append(("TextGenerate (LLM output)", wv[0] if wv else ""))
        elif "cliptextencode" in tl:
            out.append(("CLIPTextEncode", wv[0] if wv else ""))
        elif "stringconstantmultiline" in tl or "primitivestringmultiline" in tl:
            # only show if it looks like a prompt (long-ish, has words)
            val = wv[0] if wv else ""
            if isinstance(val, str) and len(val) > 40:
                out.append((t, val))
        elif "stringconcatenate" in tl:
            # joined final string often in first slot after inputs
            joined = "".join(str(x) for x in wv if isinstance(x, str))
            if len(joined) > 40:
                out.append((t + " (concatenated)", joined))
    return out

def main(path):
    texts = extract_png_text_chunks(path)
    print(f"\n===== {os.path.basename(path)} =====")
    if "workflow" in texts:
        print("[workflow metadata present]")
        for label, val in summarize_prompts(texts["workflow"]):
            print(f"\n--- {label} ---")
            print(val[:2000])
    elif "prompt" in texts:
        print("[prompt metadata only]")
        print(texts["prompt"][:3000])
    else:
        print("NO workflow/prompt metadata in this PNG (likely a screenshot or re-saved image).")

if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
