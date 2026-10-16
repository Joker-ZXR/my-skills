"""Export this Windows user's standalone skills into the Git-managed plugin."""
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLUGIN = ROOT / "plugins" / "my-skills"
HOME_DIR = Path.home()
SOURCES = [HOME_DIR / ".codex/skills", HOME_DIR / ".agents/skills"]
LIBRARY = HOME_DIR / ".codex/skill-libraries/Awesome-Journal-Skills"
SKIP = {
    ".git", ".gitignore", ".gitattributes", ".gitmodules", ".github",
    ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".runtime", ".DS_Store", ".tabbit-dance-managed",
}
SECRET = re.compile(
    rb"gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|"
    rb"sk-(?:proj-)?[A-Za-z0-9_-]{32,}|"
    rb"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"
)


def ignored(folder, names):
    return [n for n in names if n in SKIP or n.endswith((".pyc", ".pyo"))
            or n == ".env" or n.startswith(".env.")
            or Path(n).suffix.lower() in {".pem", ".key", ".pfx", ".p12"}
            or (Path(folder).name == "bggg-creator-image2ppt" and n == "projects")]


def replace_once(path, old, new):
    text = path.read_text(encoding="utf-8-sig")
    if text.count(old) != 1:
        raise ValueError(f"Source changed; review portability patch: {path.name}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def main():
    if len(sys.argv) != 2 or not re.fullmatch(r"\d+\.\d+\.\d+", sys.argv[1]):
        raise SystemExit("Usage: python sync-skills.py 1.0.1")
    version = sys.argv[1]
    skills = sorted((p for root in SOURCES if root.is_dir() for p in root.iterdir()
                     if not p.name.startswith(".") and (p / "SKILL.md").is_file()),
                    key=lambda p: p.name)
    if not skills or len({p.name for p in skills}) != len(skills):
        raise ValueError("No skills found, or duplicate source folder names")
    if any(p.name == "awesome-journal-skills" for p in skills) and not (LIBRARY / "catalog.json").is_file():
        raise ValueError(f"Required journal library is missing: {LIBRARY}")

    # Stage and inspect the complete export before replacing the generated copy.
    with tempfile.TemporaryDirectory(prefix=".export-", dir=ROOT) as temp:
        staged = Path(temp) / "my-skills"
        for source in skills:
            shutil.copytree(source, staged / "skills" / source.name, ignore=ignored)
        if any(p.name == "awesome-journal-skills" for p in skills):
            shutil.copytree(LIBRARY, staged / "resources/Awesome-Journal-Skills", ignore=ignored)
            replace_once(staged / "skills/awesome-journal-skills/SKILL.md",
                         "`C:/Users/Administrator/.codex/skill-libraries/Awesome-Journal-Skills`",
                         "`../../resources/Awesome-Journal-Skills` (resolve this path relative to this SKILL.md directory)")
        chart = staged / "skills/publication-chart-skill/SKILL.md"
        if chart.exists():
            replace_once(chart, "## Installed Windows runtime", "## Runtime setup on the current computer")
            replace_once(chart,
                         "A dedicated environment is available at `C:/Users/Administrator/.codex/skills/publication-chart-skill/.venv/Scripts/python.exe`. Use it for generation and the bundled helper when no project-specific interpreter has been selected. Its `pubtab.exe` is in the same `Scripts` directory.",
                         "Select an existing project Python environment, or create an environment outside the plugin cache. Check the dependencies below before generation. Virtual environments are not included in this plugin. Locate the pubtab CLI in the selected environment.")
            replace_once(chart, "The environment contains `pubfig==0.3.0` and `pubtab` from upstream commit",
                         "The source computer used `pubfig==0.3.0` and `pubtab` from upstream commit")
            replace_once(chart,
                         "Helvetica is unavailable on this machine. For English plots, use",
                         "Check available fonts on the current computer. If Helvetica is unavailable and Arial is installed, for English plots use")
            replace_once(chart, "use the installed `Microsoft YaHei` font in both.",
                         "use `Microsoft YaHei` when installed, or another available Chinese font, in both.")
        manifest = {"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
                    "name": "my-skills", "version": version,
                    "description": "Joker-ZXR personal research skills",
                    "author": {"name": "Joker-ZXR"}}
        (staged / "plugin.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        files = sorted(p for p in staged.rglob("*") if p.is_file())
        digest = hashlib.sha256()
        for path in files:
            if path.stat().st_size >= 100 * 1024 * 1024:
                raise ValueError(f"File is too large for a normal GitHub push: {path.relative_to(staged)}")
            data = path.read_bytes()
            if SECRET.search(data):
                raise ValueError(f"Possible credential; inspect before publishing: {path.relative_to(staged)}")
            digest.update(path.relative_to(staged).as_posix().encode())
            digest.update(hashlib.sha256(data).digest())
        # Only the generated plugin directory inside this repository can be replaced.
        expected = ROOT.resolve() / "plugins" / "my-skills"
        if PLUGIN.resolve() != expected or PLUGIN.is_symlink():
            raise ValueError("Unexpected export target")
        PLUGIN.parent.mkdir(exist_ok=True)
        if PLUGIN.exists():
            shutil.rmtree(PLUGIN)
        shutil.move(str(staged), str(PLUGIN))
    report = {"version": version, "skills": len(skills), "files": len(files),
              "bundle_sha256": digest.hexdigest(),
              "sources": [{"name": p.name, "path": str(p)} for p in skills],
              "journal_library": str(LIBRARY)}
    (ROOT / "export-report.local.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = ["# Included skills", "", "| Skill | Source directory |", "|---|---|"]
    rows += [f"| {p.name} | {'~/.agents/skills' if '.agents' in p.parts else '~/.codex/skills'} |" for p in skills]
    (ROOT / "SKILLS.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Exported {len(skills)} skills, {len(files)} files, version {version}")
    print(f"Plugin directory: {PLUGIN}")


if __name__ == "__main__":
    main()
