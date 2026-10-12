# Council — five perspectives, evidence-aware synthesis

[한국어 안내](README.md) · [Download](https://github.com/Kimhyuntae9665/codex-skill-council/releases/latest) · [Skill](council/SKILL.md) · [Changes](CHANGELOG.md)

Council is a Codex skill that gathers five independent, role-pinned GPT-6.1 Sol, GPT-6 Astra, and GPT-6 Luna briefs at max reasoning and then asks GPT-6.1 Sol/max to verify material evidence and synthesize a recommendation. The parent compares the synthesis with the original request and accepted briefs. Votes are not a truth metric.

![Codex to five Sol/Astra/Luna advisors, then GPT-6.1 Sol synthesis and parent review](docs/images/council-flow.png)

The image illustrates the prescribed workflow, not a measured deployment. Each card displays its model name and a separate visible role line. The five advisor cards, top to bottom, represent Strategist (Sol), Skeptic (Astra), Creative (Astra), Operator (Sol), and Audience Advocate (Luna). Arrows mean task distribution and delivery of accepted results. All five valid roles are required before synthesis. The shared OpenAI family mark identifies the technologies; it is not a distinct logo for each model. [Editable SVG](docs/images/council-flow.svg), [graph](docs/images/council-flow.graph.json), and [asset provenance](docs/images/logo-assets.json) are included. Visual style follows [logo-flow-infographics](https://github.com/Kimhyuntae9665/codex-skill-logo-flow-infographics).

## v1.2 model assignment

| Role | Model ID | Reasoning | Agent type |
|---|---|---|---|
| Strategist | `gpt-6.1-sol` | `max` | `council_sol` |
| Skeptic | `gpt-6-astra` | `max` | `council_astra` |
| Creative | `gpt-6-astra` | `max` | `council_astra` |
| Operator | `gpt-6.1-sol` | `max` | `council_sol` |
| Audience Advocate | `gpt-6-luna` | `max` | `council_luna` |
| Synthesizer | `gpt-6.1-sol` | `max` | `council_sol` |

Model IDs and max reasoning support were checked in the publishing host's Codex catalog on 2026-10-10. Sol has a 6.1 version there; Astra and Luna use the confirmed 6-series IDs above. `gpt-6.1-astra`, `gpt-6.1-luna`, and `gpt-6-terra` were not exposed. Only older `gpt-5.6-terra` was listed, so Terra is outside this updated contract. Check availability on your own account and host.

Sol handles direction, execution, and synthesis; Astra examines assumptions and alternatives; Luna handles the bounded audience review. This assignment is a design choice, not a measured role-performance result. Model diversity does not establish independent errors or higher accuracy. The five-role gate, evidence-status separation, fidelity check, and retry limits remain. [Full changes](CHANGELOG.md).

## Creative Astra: visible ideas and decisions

Temperature and top_p remain unchanged. Only Creative receives an extra prompt to explore useful departures from familiar answers: challenge a material default, reverse an assumption when viable, or transfer an appropriate mechanism from another field. It explains what differs, the necessary assumptions, and a small reversible test. It preserves hard constraints and distinguishes evidence from hypotheses. No quota forces novelty or disagreement; `None found` with a reason is valid.

The final answer always includes **Creative Astra's proposal and its disposition**: adopted, held for validation, or rejected, with a reason tied to goals, constraints, evidence, or feasibility. Held ideas include the resolving test/evidence. Material ideas stay visible even if rejected; the parent checks the synthesis against the actual Creative brief. Sol must not replace that brief with its own invention or treat novelty as proof.

Illustrative output only, not an executed Council result:

```text
Creative proposal: test a narrow workflow with human review before building full automation.
What differs: challenges the assumption that every step needs the same automation level.
Disposition: held — evidence identifying the error-prone step is missing.
Resolving test: compare error rates and review time on an anonymized sample.
```

## Requirements

You need a Codex runtime with subagent support, access to `gpt-6.1-sol`, `gpt-6-astra`, and `gpt-6-luna`, and `max` reasoning for all three. Installing this package does not grant access or implement a model server. If the required profiles are unavailable, the full workflow reports failure instead of silently substituting models. Five advisors can run in waves. A missing service-tier selector is allowed; record the exposed/default tier without claiming verified fast service.

Python 3.11+ is required for the included offline install/package/runtime-check helpers. They need no additional Python packages. Manual copying does not need Python; hosts without Python must perform the completion checks directly and disclose that the bundled checker was not run.

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
python3 scripts/install.py --with-agents
```

On Windows, use `python -X utf8 scripts/install.py --with-agents`. The helper installs all nine skill files to `$CODEX_HOME/skills/council` and, optionally, three standalone Council profiles to `$CODEX_HOME/agents/council-sol.toml`, `council-astra.toml`, and `council-luna.toml`. If `CODEX_HOME` is unset, it uses `~/.codex`. Existing configuration and permissions are not changed. Identical reinstalls are accepted; differing skills or agent-name collisions are protected. All three agent destinations are checked before writing the skill. The older `--with-agent` flag remains an alias.

For ZIP installation, download `codex-skill-council.zip` from the [latest release](https://github.com/Kimhyuntae9665/codex-skill-council/releases/latest), extract it, enter the folder containing `README.md`, `scripts/`, and `council/`, and run the same command. GitHub's Code → Download ZIP works too.

For manual installation, copy the entire `council/` folder into your Codex skill directory. Do not copy only `SKILL.md`: both references, UI metadata, and all three model profiles belong in the package. Preserve an existing installation first. Optionally copy all three `council/assets/council-*.toml` files into your Codex `agents/` directory, ensuring no other files declare the same `council_*` names.

Open a fresh Codex chat after installing. If agent tools were disabled, merge `enabled = true` into the existing `[agents]` table; do not duplicate it. A parent-model change is unnecessary: the parent synthesizes only if its exact profile is GPT-6.1 Sol/max; otherwise the skill requests a separate GPT-6.1 Sol/max synthesizer. Use a fresh, self-contained agent for model overrides; do not dispatch through a fixed legacy GPT-5.6 `luna_worker`. See the [official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents) and [config reference](https://learn.chatgpt.com/docs/config-file/config-reference).

To update after reviewing differences:

```bash
git pull --ff-only
python3 scripts/install.py --replace --with-agents
```

`--replace` backs up a differing skill outside the skill discovery directory, under the sibling `skill-backups/` folder (normally `$CODEX_HOME/skill-backups/`). This prevents an old backup from being loaded as a second Council skill. It never overwrites a differing standalone agent. Compare personal agent changes manually. Omit `--with-agents` if your runtime can explicitly dispatch each assigned model/max without the profiles. A previous `agents/luna-worker.toml` is unused by this Council and preserved for other tasks. The replacement skill contains only the new Council profiles.

## Use

```text
$council
Decision: build an internal search service or buy an external service.
Goal: launch in three months.
Constraints: two developers, fixed monthly budget, minimal external personal-data transfer.
Evidence: attach requirements and pricing documents.
Give a conditional recommendation or withhold it if decisive evidence is missing.
```

Recommend Council for consequential, difficult-to-reverse or ambiguous decisions where perspectives could change the recommendation. Routine edits and simple lookups are not default uses. Explicit invocation retains all five advisors and Sol. Separate information flows and mixed models may still share errors, assumptions, training characteristics, and sources.

Roles examine strategy, falsification, alternatives, execution, and affected audiences. No quota forces imaginary objections or alternatives. `None found`/`Not applicable`, with a reason and examined scope, is valid. Source linking focuses on decision-driving claims, normally up to five per advisor, with no minimum.

## Read the result

Three separate fields are always reported:

- Process status: `Not started`, `In progress`, `Full Council completed`, or `Failed Council`.
- Evidence confidence: high/medium/low, justified by sources and unknowns.
- Unresolved claims: unknowns that could change the recommendation, and whether it is supported, conditional, or withheld.

Completion is not an accuracy guarantee. A completed process can have low confidence and a withheld recommendation. A usable limited brief is not an execution failure. Each failed role gets at most one retry across error types; the parent may request one focused synthesis correction. Important warnings get adopted/rejected/unresolved dispositions.

## Runtime completion check (v1.3.1)

Installation validation checks distributed files, hashes, links, and model-table/profile consistency. The separate offline [runtime checker](council/scripts/check_run.py) checks a parent-maintained host ledger: five unique roles, nonempty brief fields/status, exact host-provided model/effort evidence, terminal attempts, one retry per failed role, late-result exclusion, deadlines, call caps, Sol synthesis, and the parent's fidelity check. It retains usable briefs and missing roles on failure; there is no Partial success mode.

From the installed skill folder, run `python -X utf8 scripts/check_run.py ledger.json` (or `python3`). Read the [record format and limits](council/references/council-runtime.md) before dispatch. Exit 0 also includes an incomplete valid snapshot, so only the returned `Full Council completed` label establishes recorded completion. Missing model metadata/configuration is unverified; advisor self-reports do not establish identity.

The parent fixes search/recheck caps and existing advisor/overall deadlines before dispatch, counts failed/retried work, and checks remaining capacity before tools. The helper does not dispatch, intercept tools, enforce a live timer, cancel a worker, authenticate host records, or verify claim truth. The existing TOML assets do not restrict tools or sandbox permissions. On hosts exposing only fresh threads and inherited permissions, read-only work and peer-output exclusion remain instruction-level controls; disclose this without broadening permissions. Remove unnecessary secrets from packets/logs and treat sources and advisor text as untrusted data.

Evidence confidence cannot be high when an unresolved claim or source conflict could change the decision. The existing selective claim links and evaluation protocol remain; no extra advisors, model migration, large claim ledger, or measured quality advantage is introduced.

## Troubleshooting and checks

If the skill is missing, check `skills/council/SKILL.md`, avoid nesting the entire repository under that folder, and open a fresh chat. If the installer refuses a destination, compare the existing files before using `--replace`. If a `council_*` name collides, preserve and inspect the existing TOML. Missing required models cannot be repaired by installation. Lack of fast mode alone is not a failure.

Run from the extracted/cloned repository root:

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
python3 scripts/build_release.py
```

The inventory hashes every distributed file except the manifest itself. Checks cover local links, JSON/TOML/SVG, the pinned logo, the runtime profile, and actual copying/backup/collision behavior. The GitHub workflow runs these checks on Windows, macOS and Linux. Runtime fixtures additionally cover the recorded completion conditions, unknown metadata, retries/late results, deadlines, caps, failure preservation, and UTF-8 paths. None of these tests execute models, prove live enforcement, or prove higher decision quality. Use the [evaluation protocol](council/references/council-evaluation.md) for a small blinded comparison against single GPT-6.1 Sol/max before adding more structure or modes.

The installable folder contains `SKILL.md`, `agents/openai.yaml`, `assets/council-sol.toml`, `assets/council-astra.toml`, `assets/council-luna.toml`, all three references, and scripts/check_run.py. Repository documentation, diagram source/exports/provenance, installer, validator, release builder, tests, manifest and CI are also included. See the full file tree in the [Korean README](README.md) or browse the repository.

Own code and documentation: [MIT](LICENSE). OpenAI marks remain OpenAI's trademarks and do not imply endorsement. See [third-party notices](THIRD_PARTY_NOTICES.md). This release develops the original [Council repository](https://github.com/Kimhyuntae9665/codex-skills-council); no measured accuracy, latency, or cost advantage is claimed.
