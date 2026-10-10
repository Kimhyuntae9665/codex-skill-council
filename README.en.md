# Council — five perspectives, evidence-aware synthesis

[한국어 안내](README.md) · [Download](https://github.com/Kimhyuntae9665/codex-skill-council/releases/latest) · [Skill](council/SKILL.md)

Council is a Codex skill that gathers five independent GPT-5.6 Luna/max briefs and then asks GPT-5.6 Sol/max to verify material evidence and synthesize a recommendation. The parent compares the synthesis with the original request and accepted briefs. Votes are not a truth metric.

![Codex to five Luna advisors, then Sol synthesis and parent review](docs/images/council-flow.png)

The image illustrates the prescribed workflow, not a measured deployment. The five Luna cards, top to bottom, represent Strategist, Skeptic, Creative, Operator, and Audience Advocate. Arrows mean task distribution and delivery of accepted results. All five valid roles are required before synthesis. The shared OpenAI family mark identifies the technologies; it is not a distinct logo for each model. [Editable SVG](docs/images/council-flow.svg), [graph](docs/images/council-flow.graph.json), and [asset provenance](docs/images/logo-assets.json) are included. Visual style follows [logo-flow-infographics](https://github.com/Kimhyuntae9665/codex-skill-logo-flow-infographics).

## Requirements

You need a Codex runtime with subagent support, access to `gpt-5.6-luna` and `gpt-5.6-sol`, and `max` reasoning for both. Installing this package does not grant access or implement a model server. If the required profiles are unavailable, the full workflow reports failure instead of silently substituting models. Five advisors can run in waves. A missing service-tier selector is allowed; record the exposed/default tier without claiming verified fast service.

Python 3.11+ is required only for the included offline install/check helpers. They need no additional Python packages. Manual copying does not need Python.

## Install

With Codex's `$skill-installer`, request installation from:

```text
$skill-installer Install https://github.com/Kimhyuntae9665/codex-skill-council/tree/main/council
Preserve an existing Council and compare it before replacing anything.
```

Or clone this repository and run the helper from its root:

```bash
git clone https://github.com/Kimhyuntae9665/codex-skill-council.git
cd codex-skill-council
python3 scripts/install.py --with-agent
```

On Windows, use `python -X utf8 scripts/install.py --with-agent`. The helper installs all five skill files to `$CODEX_HOME/skills/council` and, optionally, the standalone Luna profile to `$CODEX_HOME/agents/luna-worker.toml`. If `CODEX_HOME` is unset, it uses `~/.codex`. Existing configuration and permissions are not changed. Identical reinstalls are accepted; differing skills or agent-name collisions are protected.

For ZIP installation, download `codex-skill-council.zip` from the [latest release](https://github.com/Kimhyuntae9665/codex-skill-council/releases/latest), extract it, enter the folder containing `README.md`, `scripts/`, and `council/`, and run the same command. GitHub's Code → Download ZIP works too.

For manual installation, copy the entire `council/` folder into your Codex skill directory. Do not copy only `SKILL.md`: both references, UI metadata, and the worker profile belong in the package. Preserve an existing installation first. Optionally copy `council/assets/luna-worker.toml` into your Codex `agents/` directory, ensuring no other file declares `name = "luna_worker"`.

Open a fresh Codex chat after installing. If agent tools were disabled, merge `enabled = true` into the existing `[agents]` table; do not duplicate it. A parent-model change is unnecessary: the skill requests a separate Sol/max synthesizer when needed. See the [official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents) and [config reference](https://learn.chatgpt.com/docs/config-file/config-reference).

To update after reviewing differences:

```bash
git pull --ff-only
python3 scripts/install.py --replace --with-agent
```

`--replace` backs up a differing skill beside its destination before replacement. It never overwrites a differing standalone agent. Compare personal agent changes manually. Omit `--with-agent` if your runtime can explicitly dispatch Luna/max without the profile.

## Use

```text
$council
Decision: build an internal search service or buy an external service.
Goal: launch in three months.
Constraints: two developers, fixed monthly budget, minimal external personal-data transfer.
Evidence: attach requirements and pricing documents.
Give a conditional recommendation or withhold it if decisive evidence is missing.
```

Recommend Council for consequential, difficult-to-reverse or ambiguous decisions where perspectives could change the recommendation. Routine edits and simple lookups are not default uses. Explicit invocation retains all five advisors and Sol. Same-model agents have separate information flows, but may share errors.

Roles examine strategy, falsification, alternatives, execution, and affected audiences. No quota forces imaginary objections or alternatives. `None found`/`Not applicable`, with a reason and examined scope, is valid. Source linking focuses on decision-driving claims, normally up to five per advisor, with no minimum.

## Read the result

Three separate fields are always reported:

- Process status: `Not started`, `In progress`, `Full Council completed`, or `Failed Council`.
- Evidence confidence: high/medium/low, justified by sources and unknowns.
- Unresolved claims: unknowns that could change the recommendation, and whether it is supported, conditional, or withheld.

Completion is not an accuracy guarantee. A completed process can have low confidence and a withheld recommendation. A usable limited brief is not an execution failure. Each failed role gets at most one retry across error types; the parent may request one focused synthesis correction. Important warnings get adopted/rejected/unresolved dispositions.

## Troubleshooting and checks

If the skill is missing, check `skills/council/SKILL.md`, avoid nesting the entire repository under that folder, and open a fresh chat. If the installer refuses a destination, compare the existing files before using `--replace`. If `luna_worker` collides, preserve and inspect the existing TOML. Missing required models cannot be repaired by installation. Lack of fast mode alone is not a failure.

Run from the extracted/cloned repository root:

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py
```

The inventory hashes every distributed file except the manifest itself. Checks cover local links, JSON/TOML/SVG, the pinned logo, the runtime profile, and actual copying/backup/collision behavior. The GitHub workflow runs these checks on Windows, macOS and Linux. None of these tests execute models or prove higher decision quality. Use the [evaluation protocol](council/references/council-evaluation.md) for a small blinded comparison against single Sol/max before adding more structure or modes.

The installable folder contains `SKILL.md`, `agents/openai.yaml`, `assets/luna-worker.toml`, and both references. Repository documentation, diagram source/exports/provenance, installer, validator, release builder, tests, manifest and CI are also included. See the full file tree in the [Korean README](README.md) or browse the repository.

Own code and documentation: [MIT](LICENSE). OpenAI marks remain OpenAI's trademarks and do not imply endorsement. See [third-party notices](THIRD_PARTY_NOTICES.md). This release develops the original [Council repository](https://github.com/Kimhyuntae9665/codex-skills-council); no measured accuracy, latency, or cost advantage is claimed.
