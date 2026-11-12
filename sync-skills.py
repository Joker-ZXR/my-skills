"""Export standalone skills into the Git-managed plugin."""
import argparse
import hashlib
import json
import re
import shutil
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version")
    parser.add_argument("--add-only", action="store_true",
                        help="Keep all packaged skills and resources; add missing skills only")
    args = parser.parse_args()
    if not re.fullmatch(r"\d+\.\d+\.\d+", args.version):
        parser.error("version must use MAJOR.MINOR.PATCH")
    version = args.version
    skills = sorted((p for root in SOURCES if root.is_dir() for p in root.iterdir()
                     if not p.name.startswith(".") and (p / "SKILL.md").is_file()),
                    key=lambda p: p.name)
    if args.add_only:
        skills = [p for p in skills if not (PLUGIN / "skills" / p.name).exists()]
        if not skills:
            print("No new skills; existing package unchanged")
            return
    if not skills or len({p.name for p in skills}) != len(skills):
        raise ValueError("No skills found, or duplicate source folder names")
    if any(p.name == "awesome-journal-skills" for p in skills) and not (LIBRARY / "catalog.json").is_file():
        raise ValueError(f"Required journal library is missing: {LIBRARY}")

    # Stage and inspect the complete export before replacing the generated copy.
    with tempfile.TemporaryDirectory(prefix=".export-", dir=ROOT) as temp:
        staged = Path(temp) / "my-skills"
        if args.add_only and PLUGIN.exists():
            shutil.copytree(PLUGIN, staged)
        for source in skills:
            shutil.copytree(source, staged / "skills" / source.name, ignore=ignored)
            entry = staged / "skills" / source.name / "SKILL.md"
            if source.name == "mri-dataset-analysis":
                replace_once(entry,
                             "/home/siat/Task/Task_zxr/mri_foundation/pre_processing/data_pre/",
                             "<当前项目根目录>/pre_processing/data_pre/")
            if "# MRFoundry:" in entry.read_text(encoding="utf-8"):
                for doc in entry.parent.rglob("*.md"):
                    text = doc.read_text(encoding="utf-8")
                    doc.write_text(text.replace(".agents/skills/", "../"), encoding="utf-8")
                text = entry.read_text(encoding="utf-8")
                end = text.index("\n", text.index("# MRFoundry:"))
                note = ("\n\nResolve script paths relative to this SKILL.md's directory. "
                        "Sibling skills are under `../<skill-name>/`. Replace relative paths "
                        "in command examples with their resolved absolute paths before running "
                        "from a project directory; do not assume a project-local skill install.")
                entry.write_text(text[:end] + note + text[end:], encoding="utf-8")
        if any(p.name == "awesome-journal-skills" for p in skills):
            shutil.copytree(LIBRARY, staged / "resources/Awesome-Journal-Skills", ignore=ignored)
            replace_once(staged / "skills/awesome-journal-skills/SKILL.md",
                         "`C:/Users/Administrator/.codex/skill-libraries/Awesome-Journal-Skills`",
                         "`../../resources/Awesome-Journal-Skills` (resolve this path relative to this SKILL.md directory)")
        chart = staged / "skills/publication-chart-skill/SKILL.md"
        if any(p.name == "publication-chart-skill" for p in skills):
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
        if args.add_only and (staged / "plugin.json").exists():
            manifest = json.loads((staged / "plugin.json").read_text(encoding="utf-8"))
            manifest["version"] = version
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
    total = len(list((PLUGIN / "skills").glob("*/SKILL.md")))
    report = {"version": version, "skills": total, "added_skills": len(skills), "files": len(files),
              "bundle_sha256": digest.hexdigest(),
              "sources": [{"name": p.name, "path": str(p)} for p in skills],
              "journal_library": str(LIBRARY)}
    (ROOT / "export-report.local.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = ["# Included skills", "", "| Skill | Source directory |", "|---|---|"]
    if args.add_only and (ROOT / "SKILLS.md").exists():
        rows = (ROOT / "SKILLS.md").read_text(encoding="utf-8").rstrip().splitlines()
    rows += [f"| {p.name} | {'~/.agents/skills' if '.agents' in p.parts else '~/.codex/skills'} |" for p in skills]
    (ROOT / "SKILLS.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"Exported {total} skills ({len(skills)} from local sources), {len(files)} files, version {version}")
    print(f"Plugin directory: {PLUGIN}")


if __name__ == "__main__":
    main()
