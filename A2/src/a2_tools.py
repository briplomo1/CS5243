"""Provided A2 infrastructure helpers; no graded algorithms live here."""

from __future__ import annotations
import hashlib
import json
from pathlib import Path
import imageio.v3 as iio
import matplotlib.pyplot as plt
import numpy as np
from cs5243.data import find_course_root, find_repository_root


def assignment_paths() -> dict[str, Path]:
    root=find_repository_root(__file__); assignment=find_course_root(__file__)/"A2"
    return {"root":root,"assignment":assignment,"assets":assignment/"data",
            "figures":assignment/"outputs"/"figures","tables":assignment/"outputs"/"tables",
            "images":assignment/"outputs"/"images","extension":assignment/"outputs"/"extension"}


def ensure_output_directories() -> dict[str, Path]:
    paths=assignment_paths()
    for key in ("figures","tables","images","extension"): paths[key].mkdir(parents=True,exist_ok=True)
    return paths


def verify_asset_hashes() -> list[str]:
    root=assignment_paths()["assets"]; problems=[]
    for line in (root/"SHA256SUMS").read_text(encoding="utf-8").splitlines():
        expected,relative=line.split(maxsplit=1); path=root/relative.strip()
        if not path.is_file(): problems.append(f"Missing asset: {relative}")
        elif hashlib.sha256(path.read_bytes()).hexdigest()!=expected: problems.append(f"Checksum mismatch: {relative}")
    return problems


verify_asset_checksums=verify_asset_hashes


def load_images() -> dict[str,np.ndarray]:
    return {p.name:iio.imread(p) for p in sorted((assignment_paths()["assets"]/"images").glob("*.*"))}


def to_float01(image: np.ndarray) -> np.ndarray:
    a=np.asarray(image)
    if a.dtype==np.uint8: return (a.astype(np.float32)/255).astype(np.float32)
    if a.dtype==np.uint16: return (a.astype(np.float32)/65535).astype(np.float32)
    return np.clip(a.astype(np.float32),0,1)


def save_rgb(path: str|Path, image: np.ndarray) -> Path:
    target=Path(path); target.parent.mkdir(parents=True,exist_ok=True)
    iio.imwrite(target,np.round(np.clip(image,0,1)*255).astype(np.uint8)); return target


def save_json(path: str|Path, value: dict) -> Path:
    target=Path(path); target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8"); return target


def axes_grid(rows:int,columns:int,scale:float=3.0):
    return plt.subplots(rows,columns,figsize=(scale*columns,scale*rows),squeeze=False)
