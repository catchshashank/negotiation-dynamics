from pathlib import Path
import hashlib, json, subprocess
from datetime import datetime
import logging

def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def git_head_sha(repo_root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            text=True
        ).strip()
    except Exception:
        return None

def make_run_dirs(repo_root: Path, input_file: Path, runs_dir_name: str = "runs"):
    """
    input_file name like: 260215.csv or 260215.xlsx (YYMMDD)
    Creates: runs/2026-02-15/file__260215__<hash8>/{inputs,outputs,logs}
    """
    input_file = input_file.resolve()
    repo_root = repo_root.resolve()

    file_stem = input_file.stem  # "260215"
    # convert YYMMDD -> YYYY-MM-DD (assumes 2000-2099; adjust if you need 1900s)
    yy = int(file_stem[:2])
    mm = int(file_stem[2:4])
    dd = int(file_stem[4:6])
    run_date = datetime(2000 + yy, mm, dd).strftime("%Y-%m-%d")

    file_hash = sha256_file(input_file)
    short_hash = file_hash[:8]

    run_root = repo_root / runs_dir_name / run_date / f"file__{file_stem}__{short_hash}"
    inputs_dir  = run_root / "inputs"
    outputs_dir = run_root / "outputs"
    logs_dir    = run_root / "logs"
    figs_dir    = outputs_dir / "figures"

    for d in (inputs_dir, outputs_dir, logs_dir, figs_dir):
        d.mkdir(parents=True, exist_ok=True)

    return {
        "run_root": run_root,
        "inputs_dir": inputs_dir,
        "outputs_dir": outputs_dir,
        "logs_dir": logs_dir,
        "figs_dir": figs_dir,
        "file_hash": file_hash,
        "run_date": run_date,
        "file_stem": file_stem,
        "short_hash": short_hash
    }
