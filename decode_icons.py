#!/usr/bin/env python3
import base64
import hashlib
import json
from collections import defaultdict
from pathlib import Path

root = Path(__file__).resolve().parent
man = json.loads((root / "chunks" / "MANIFEST.json").read_text())
chunks_dir = root / "chunks"
groups = defaultdict(list)
for rec in man["chunks"]:
    png = rec["file"].split(".png.")[0] + ".png"
    groups[png].append(rec)
for png, recs in groups.items():
    recs = sorted(recs, key=lambda r: r["file"])
    parts = []
    for rec in recs:
        data = (chunks_dir / rec["file"]).read_text().strip()
        digest = hashlib.sha256(data.encode("ascii")).hexdigest()
        if digest != rec["sha256"] or len(data) != rec["len"]:
            raise SystemExit(
                f"chunk mismatch {rec['file']} got {digest} len {len(data)}"
            )
        parts.append(data)
    raw = base64.b64decode("".join(parts), validate=True)
    got = hashlib.sha256(raw).hexdigest()
    if got != man["files"][png]:
        raise SystemExit(f"{png} hash mismatch {got} != {man['files'][png]}")
    (root / png).write_bytes(raw)
    print("wrote", png, len(raw), got)
