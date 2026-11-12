# Local additions in 1.0.2

The existing 37 skills and their resources are retained unchanged.

| Source | Added skills |
|---|---|
| Local standalone skills | `caveman`, `mri-dataset-analysis`, `standardize-mri-nifti` |
| [KeWang0622/MRFoundry](https://github.com/KeWang0622/MRFoundry), installed skill version 0.14.0 | `deep-learning-recon`, `diffusion-mri`, `mri-hardware`, `mri-reconstruction`, `mri-research`, `mri-research-workflow`, `pulse-sequence-design` |

MRFoundry is distributed under the [MIT license](resources/licenses/MRFoundry-LICENSE). Its scripts, references and templates are included. The local skill copies were installed using `npx skills add KeWang0622/MRFoundry --skill '*' -a codex -g -y`.

Portability changes in the packaged copies:

- MRFoundry command paths resolve relative to the installed skill directory and its siblings, rather than a project-local `.agents/skills` directory.
- `mri-dataset-analysis` saves processing scripts under the current project root rather than the source computer's fixed home path.
- Historical dataset paths in reference documents remain examples; they are not bundled datasets or required directories.

Python environments and external MRI tools are set up on the destination machine as needed. System skills and official plugin caches are not included; install the corresponding official plugins on that machine for their tools and integrations.
