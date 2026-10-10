---
name: council
description: Run five independent Council reviews with role-pinned GPT-6.1 Sol, GPT-6 Astra, and GPT-6 Luna at max reasoning, followed by GPT-6.1 Sol synthesis. Use for complex or consequential decisions, comparisons, plans, and reviews where distinct perspectives could change the recommendation. Separate execution completion from evidence confidence.
---

# Council

Produce a practical answer only after a strict five-advisor review. The council is a decision process, not theater: gather independent briefs, verify the completion gate, then let Sol resolve disagreement and synthesize one recommendation.

## When To Use

Recommend Council when the stakes, difficulty of reversal, conflicting evidence, or competing interests make multiple perspectives useful. Routine edits and simple fact lookups are not default uses. An explicit request to run `$council` still uses the full contract below; never silently reduce the advisor count or replace the models. Separate information flows and different model profiles do not guarantee independent errors; all advisors still share the packet and may share training or sources. Quality gains over a single model remain unverified without comparative evidence.

## Model Assignment

The v1.2 contract uses these exact profiles. The three optional TOML assets provide reusable agent types; each role still needs its own fresh thread.

| Role | Model ID | Reasoning | Optional agent type |
|---|---|---|---|
| Strategist | `gpt-6.1-sol` | `max` | `council_sol` |
| Skeptic | `gpt-6-astra` | `max` | `council_astra` |
| Creative | `gpt-6-astra` | `max` | `council_astra` |
| Operator | `gpt-6.1-sol` | `max` | `council_sol` |
| Audience Advocate | `gpt-6-luna` | `max` | `council_luna` |
| Synthesizer | `gpt-6.1-sol` | `max` | `council_sol` |

Use Sol for direction, execution, and synthesis; Astra for assumption challenges and alternative framing; Luna for a bounded audience-focused review. This is a design choice, not measured proof of role superiority. These IDs and `max` support were checked in the publishing host's Codex catalog on 2026-10-10; verify access in the executing host before dispatch. Do not invent `gpt-6.1-luna`, `gpt-6.1-astra`, or `gpt-6-terra` aliases. The catalog exposed only older `gpt-5.6-terra`, which is not part of this updated contract.

## Task Packet Check

Preserve the original user request beside the frozen packet. Separate user-stated goals and constraints from the parent's interpretations, assumptions, and unknowns. Before dispatch, compare the packet against the original for omitted constraints, unsupported premises, and a changed decision question. Resolve what the available context supports; ask only if a consequential ambiguity remains.

Every advisor may challenge the packet's framing and should record a material concern under `assumptions` or `data limits`. Do not force an answer to a false premise. Sol receives both the original request and the frozen packet. If the framing materially changes during the run, report the affected conclusions as conditional or withheld; do not silently rewrite the packet or count briefs on different questions as one complete run.

## Runtime Contract

For every explicit `$council` invocation:

1. Freeze one task packet containing the user request, goal, constraints, known evidence, as-of date when relevant, and authorization boundaries.
2. Dispatch exactly five fresh advisor threads with the role-specific model from the Model Assignment table. Use the matching installed `council_*` agent type when its exposed configuration matches, or a generic agent with an explicit model override. Do not use a fixed legacy `luna_worker` profile that would ignore the requested model. With `spawn_agent`, use `fork_turns: "none"` when selecting a model or reasoning override. Pin:
   - model: the exact ID assigned to that role above
   - reasoning effort: `max`
   - service tier: prefer `fast` only when the dispatch API explicitly supports it. Otherwise use the supported default or inherited tier; do not send unsupported parameters. Record the exposed tier (for example `priority`) or `not exposed` in the runtime ledger. Do not infer an actual tier from a requested tier or describe an inherited tier as verified fast service.
3. Give every advisor the same frozen task packet plus only its role-specific emphasis. Do not fork the full conversation, reveal another advisor's output, or let advisors debate each other.
4. Wait for all five terminal results. If the runtime cannot run five advisors concurrently, run them in waves without changing their prompts or sharing earlier results. Choose task-appropriate advisor and overall deadlines before dispatch. Record role, attempt ID, start/end time, terminal state, and available usage; record unavailable token or cost data as unknown.
5. Each failed role may be retried at most once with the same role and runtime profile. Confirm the previous attempt has ended or been cancelled before redispatch. Dispatch errors, timeouts, and malformed briefs share this per-role retry budget; do not add unlimited format-repair attempts or silently restart the whole Council to evade the budget. Select one valid terminal brief per role, log all attempts, and exclude late duplicate results from the gate. If any unique role still lacks a valid result, report `Failed Council`; do not silently simulate, substitute another model, or present a partial run as a full council.
6. After the five-of-five completion gate passes, synthesize with `gpt-6.1-sol` at `max` reasoning. Use the parent only when its exposed configuration confirms that exact model and effort; otherwise spawn a dedicated Sol synthesizer when the runtime supports explicit model selection, with no inherited conversation and the self-contained synthesis packet. A parent running GPT-6 Sol or GPT-5.6 Sol does not satisfy the GPT-6.1 Sol requirement.
7. If any assigned model/max profile is unavailable, state the missing model or reasoning capability and stop the full Council workflow instead of weakening the contract silently. A missing service-tier selector does not block Council when the model and reasoning profiles are available; disclose this runtime limitation.

Advisor threads inherit the parent's sandbox, approval, network, MCP, and skill access. Do not request broader permissions merely to improve an opinion. Keep advisory work read-only unless the original user request explicitly authorizes a scoped mutation and the parent assigns it.

## Advisor Roles

- Strategist: test long-term direction, strategic fit, opportunity cost, and second-order effects.
- Skeptic: falsify assumptions, expose blind spots, and describe downside and failure cases.
- Creative: find alternative frames, unconventional options, and sharper formulations within the constraints.
- Operator: turn the goal into executable sequencing, resources, dependencies, validation, and rollback steps.
- Audience Advocate: represent the customer, user, reader, employee, or investor; test trust, clarity, objections, and usability.

Keep the roles non-overlapping. When research is needed, assign distinct evidence lanes or questions instead of asking all five advisors to perform the same search. Report relevant findings within each role's emphasis; do not impose quotas for counterexamples, alternatives, or disagreement. `Not applicable` or `None found`, with the reason and scope examined in the user's language, is a valid finding. Do not invent risks or weaker alternatives to fill a role.

### Creative Astra Brief

Give only the Creative role this additional emphasis in its self-contained prompt. Keep the assigned Astra/max profile and existing sampling settings; do not set, request, or pretend to set temperature or top_p.

Explore useful departures from the familiar answer: question a material default assumption, reverse an assumption when that opens a viable option, or transfer a mechanism from another field when the analogy fits. These are exploration methods, not a quota or a requirement to disagree. Preserve hard user constraints; if an idea needs a constraint relaxed, label it conditional rather than silently changing the task. Do not invent facts, sources, gains, or novelty claims to make a suggestion look original.

Under the existing `recommendation` and `key reasons` fields, summarize the useful proposal(s), what concretely differs from the conventional approach, and why that difference may matter. Under `assumptions` and `facts vs inference`, identify the changed assumption and distinguish evidence from hypotheses. Include a small, reversible test and a success/failure observation in `what would change my mind`. No new result labels or minimum idea count are required. If no useful distinct proposal is found, say `None found` with the scope and reason; do not fabricate one.

## Advisor Prompt And Result

Give each advisor a self-contained prompt containing:

- its assigned role and unique emphasis;
- the frozen task packet;
- relevant source or tool instructions;
- a prohibition on reading peer outputs or writing shared Council artifacts;
- the required result schema.

Require every advisor to use the following literal English field labels exactly once. Write the field values in the user's language, but do not translate, rename, merge, or omit the labels:

- `role`
- `status`
- `recommendation`
- `key reasons`
- `risks`
- `assumptions`
- `facts vs inference`
- `evidence/sources`
- `confidence`
- `what would change my mind`
- `skills/tools used`
- `data limits`

Use `status: complete` when the brief is usable, even if its conclusion is uncertain. Use `status: limited` when the available data constrains the brief, and explain the limitation. A dispatch error, timeout, malformed result, duplicate role, or wrong runtime profile does not pass the completion gate.

Keep the existing labeled natural-language format; JSON and a new parser are not prerequisites. In `evidence/sources`, link only the decision-driving claims to a source location or label them as inference/unknown, normally no more than five per advisor and with no minimum. Include fewer when sufficient. Sol expands only material conflicts or claims needed for the final choice. A formal claim-ID ledger is optional.

## Completion Gate

Before Sol synthesis, confirm:

- exactly five unique roles each have one accepted valid terminal brief from their own fresh advisor thread; failed or superseded attempts are logged separately;
- every required role appears exactly once;
- every advisor used its role's exact Model Assignment profile at max reasoning, and its requested or inherited service tier is recorded without claiming an unverified actual tier;
- no advisor received a peer's output before finishing;
- every result follows the required schema and records data limits;
- material claims have evidence or are explicitly labeled as inference.

Check field presence, nonempty values, status, and role uniqueness directly; use a simple existing checker when available. Verify model and execution settings from runtime metadata or exposed configuration rather than the advisor's self-report alone, and disclose verification limits. A usable `limited` brief can pass the execution gate; missing decisive evidence must still constrain the recommendation.

Do not treat repeated use of the same source as independent corroboration. Do not use advisor votes as a truth metric. Gate completion establishes process compliance, not correctness.

## Sol Verification And Synthesis

Give Sol the preserved user request, frozen task packet, and all five accepted briefs only after the gate passes. Sol must:

1. identify the strongest evidence and arguments;
2. surface real disagreement and trace it to assumptions, goals, or evidence;
3. recheck material conflicts and time-sensitive claims with appropriate tools or primary sources;
4. distinguish verified facts, inference, and unresolved uncertainty;
5. choose the recommendation that best fits the goal and constraints rather than averaging opinions;
6. preserve important minority warnings and state what would invalidate the recommendation.

Always include a visible **Creative proposal and disposition** section in the final answer, translated into the user's language. Summarize the actual Creative Astra proposal without substituting Sol's own invention, explain what differs, and give a disposition: adopted, held for validation, or rejected. Explain the reason using the goal, constraints, evidence, or feasibility; do not discard an idea merely because it is unusual or reward it merely because it is unusual. A held proposal must state what evidence or small test would resolve it. A rejected proposal still remains visible with its reason. Retain all Creative proposals that materially change the recommendation or next experiment; omit redundant variations rather than the substantive option. When Creative found none, report that honestly with its reason. If Creative never returned a valid brief, state that its opinion is unavailable and retain the appropriate failure status.

For decision-driving disagreements and material minority warnings, leave a short disposition: adopted, rejected with a reason, or unresolved, with the originating role. No minimum number of disagreements is required. The parent checks the synthesis against those briefs and the original request for distorted claims, omitted material warnings, and confidence unsupported by evidence before presenting it. If correction is needed, request a focused Sol correction and record the attempt; allow at most one such correction. If synthesis fails, or a material fidelity defect remains after the permitted correction, report `Failed Council`, even after five valid briefs. Do not add a standing extra reviewer by default. This check supports traceability; it is not independent proof of accuracy.

The parent's fidelity check also confirms that the Creative section preserves the actual proposal and gives its disposition and reason; for held proposals, check that the resolving test/evidence is present. Novelty alone never increases evidence confidence.

For financial, legal, medical, safety-critical, technical, or current product decisions, verify current facts before answering. For financial outputs, state that the result is research support rather than personal investment advice and include invalidation and risk controls.

## Process And Evidence Status

Always report these separately, with field labels in the user's language if appropriate:

- `Process status`: `Not started` before dispatch; `In progress` while running or a permitted correction is pending; `Full Council completed` only after the five-role gate, Sol synthesis, and parent fidelity check pass; `Failed Council` when aborted, required capabilities are unavailable, retries are exhausted, or a material fidelity defect remains after correction. State the failed stage. Repair a recoverable draft packet omission before dispatch rather than declaring a completed or terminally failed run.
- `Evidence confidence`: high, medium, or low, with a brief justification tied to source support and material unknowns. Before substantive assessment, use low and explain that evidence has not yet been assessed. Do not derive confidence from advisor counts or process completion.
- `Unresolved claims`: unknowns that could change the choice, or none with a brief explanation. State whether the recommendation is supported, conditional, or withheld.

A complete process can legitimately have low evidence confidence and a withheld recommendation. Insufficient evidence alone is not an execution failure. Never substitute fabricated certainty for a withheld answer.

## Recipes

Read `references/council-recipes.md` when the request matches a reusable prompt type. A recipe shapes the content only; it never changes the five-role model assignment, completion gate, or GPT-6.1 Sol synthesis contract.

## Evaluate Before Expanding

When asked to benchmark Council or expand its workflow, read [references/council-evaluation.md](references/council-evaluation.md). Start with a small blinded comparison against single Sol/max before imposing JSON, strict role deliverables, a full claim ledger, or additional modes. This is an evaluation protocol, not a benchmark to run on every invocation. Do not claim performance improvements from static validation or one successful run.

## Output Shape

Keep the answer proportionate to the task. Always include the status block and Creative proposal/disposition section; recipes may add content but cannot omit either. Use the following compact default. Include the advisor table or detailed ledger when useful or requested, rather than repeating conclusions in multiple sections.

```markdown
**Conclusion**
[one practical answer, conditional recommendation, or reason to withhold]

Process status: [Not started / In progress / Full Council completed / Failed Council; failed stage if any]
Evidence confidence: [high / medium / low, and why]
Unresolved claims: [decision-changing unknowns, or none and why]

**Reasons And Disagreement**
[strongest evidence; material disagreements/warnings and their disposition, or none]

[what would invalidate the recommendation]

**Creative Proposal And Disposition**
[Creative Astra's actual idea and what differs, or None found/unavailable with reason]
[adopted / held for validation / rejected, and why; a held idea includes the resolving test/evidence]

**Next Steps**
[only useful next actions, with no fixed count]

**Runtime Ledger**
[compact summary: five accepted roles with each model/effort, GPT-6.1 Sol synthesis profile, fidelity check, retries, elapsed time, available usage, and limits; retain attempt details for inspection]
```

## Quality Rules

- Start with the conclusion.
- Keep advisor notes brief; do not create fictional dialogue.
- Prefer explicit tradeoffs over vague balance.
- Separate facts from inference and show uncertainty when data is incomplete.
- Preserve meaningful disagreement instead of forcing consensus.
- Use the user's language unless asked otherwise.
- Never describe model output as consciousness or guaranteed truth.
- Never claim `Full Council` unless the five-role gate, Sol synthesis, and parent fidelity check all passed. Do not describe completion as a reliability guarantee.
