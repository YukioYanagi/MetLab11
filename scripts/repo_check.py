#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    print("Python 3.11+ is required (tomllib not found).")
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parent.parent
MAX_TRACKED_SIZE_BYTES = 1_000_000
FORBIDDEN_SUFFIXES = {".exe", ".dll", ".so"}
FORBIDDEN_PARTS = {".venv", "target", "__pycache__"}
ALLOWED_EDITIONS = {"2021", "2024"}


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def get_tracked_files() -> list[Path]:
    proc = run_git("ls-files", "-z")
    if proc.returncode != 0:
        raise RuntimeError(f"git ls-files failed: {proc.stderr.strip()}")
    rel_paths = [p for p in proc.stdout.split("\x00") if p]
    return [REPO_ROOT / p for p in rel_paths]


def parse_toml(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def check_repo_size(tracked_files: list[Path], failures: list[str], notes: list[str]) -> None:
    total_size = 0
    missing = []
    for file_path in tracked_files:
        if file_path.is_file():
            total_size += file_path.stat().st_size
        else:
            missing.append(str(file_path.relative_to(REPO_ROOT)))

    if missing:
        failures.append(f"Tracked paths missing on disk: {', '.join(missing[:5])}")

    notes.append(f"Tracked file size: {total_size} bytes")
    if total_size >= MAX_TRACKED_SIZE_BYTES:
        failures.append(f"Tracked files total size is {total_size} bytes (must be < 1_000_000).")


def check_forbidden_paths(tracked_files: list[Path], failures: list[str]) -> None:
    bad_files: list[str] = []
    for file_path in tracked_files:
        rel = file_path.relative_to(REPO_ROOT)
        rel_lower = rel.as_posix().lower()
        suffix = file_path.suffix.lower()
        parts_lower = {part.lower() for part in rel.parts}
        if suffix in FORBIDDEN_SUFFIXES:
            bad_files.append(rel_lower)
        if parts_lower & FORBIDDEN_PARTS:
            bad_files.append(rel_lower)
    if bad_files:
        unique = sorted(set(bad_files))
        failures.append(
            "Forbidden files/directories are tracked in git: "
            + ", ".join(unique[:20])
            + (" ..." if len(unique) > 20 else "")
        )


def check_go_mod_per_go_project(failures: list[str], notes: list[str]) -> None:
    go_files = [p for p in REPO_ROOT.rglob("*.go") if ".git" not in p.parts]
    if not go_files:
        notes.append("No Go files found; go.mod check skipped.")
        return

    missing_for: list[str] = []
    checked_dirs = set()
    for go_file in go_files:
        go_dir = go_file.parent
        if go_dir in checked_dirs:
            continue
        checked_dirs.add(go_dir)

        cur = go_dir
        found = False
        while True:
            if (cur / "go.mod").exists():
                found = True
                break
            if cur == REPO_ROOT:
                break
            cur = cur.parent
        if not found:
            missing_for.append(str(go_dir.relative_to(REPO_ROOT)))

    if missing_for:
        failures.append(
            "Go project directories without go.mod in their parent chain: "
            + ", ".join(sorted(missing_for))
        )


def check_cargo_edition_and_maturin(failures: list[str], notes: list[str]) -> None:
    cargo_files = [p for p in REPO_ROOT.rglob("Cargo.toml") if ".git" not in p.parts]
    if not cargo_files:
        notes.append("No Cargo.toml found; Rust checks skipped.")
        return

    for cargo_path in cargo_files:
        rel = cargo_path.relative_to(REPO_ROOT).as_posix()
        try:
            data = parse_toml(cargo_path)
        except Exception as exc:  # pragma: no cover
            failures.append(f"Cannot parse {rel}: {exc}")
            continue

        package = data.get("package", {})
        edition = str(package.get("edition", "")).strip()
        if edition not in ALLOWED_EDITIONS:
            failures.append(
                f"{rel}: package.edition must be one of {sorted(ALLOWED_EDITIONS)}, got '{edition or 'missing'}'."
            )

        text = cargo_path.read_text(encoding="utf-8", errors="ignore").lower()
        if "maturin" in text:
            pyproject = cargo_path.parent / "pyproject.toml"
            if not pyproject.exists():
                failures.append(
                    f"{rel}: detected maturin usage but missing {pyproject.relative_to(REPO_ROOT).as_posix()}."
                )


def check_prompt_log(failures: list[str]) -> None:
    prompt_log = REPO_ROOT / "PROMPT_LOG.md"
    if not prompt_log.exists():
        failures.append("PROMPT_LOG.md is missing.")
        return

    content = prompt_log.read_text(encoding="utf-8", errors="ignore")
    non_empty = [line.strip() for line in content.splitlines() if line.strip()]
    meaningful = [line for line in non_empty if not line.startswith("#")]
    if len(meaningful) < 3:
        failures.append("PROMPT_LOG.md must be filled (at least 3 meaningful non-header lines).")


def main() -> int:
    failures: list[str] = []
    notes: list[str] = []

    try:
        tracked_files = get_tracked_files()
    except Exception as exc:
        print(f"[FAIL] Cannot read git tracked files: {exc}")
        return 2

    check_repo_size(tracked_files, failures, notes)
    check_forbidden_paths(tracked_files, failures)
    check_go_mod_per_go_project(failures, notes)
    check_cargo_edition_and_maturin(failures, notes)
    check_prompt_log(failures)

    print("=== Repository policy check ===")
    for note in notes:
        print(f"[INFO] {note}")

    if failures:
        print("\n[FAIL] Policy check failed:")
        for idx, item in enumerate(failures, start=1):
            print(f"  {idx}. {item}")
        return 1

    print("\n[PASS] All repository policy checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

