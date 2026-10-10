---
name: council
description: Run a model-pinned Council with five independent GPT-5.6 Luna advisors at max reasoning and GPT-5.6 Sol at max reasoning for evidence-aware synthesis. Use for complex or consequential decisions, option comparisons, plans, and reviews where distinct perspectives could change the recommendation. Separate execution completion from evidence confidence.
---

# Council

Produce a practical answer only after a strict five-advisor review. The council is a decision process, not theater: gather independent briefs, verify the completion gate, then let Sol resolve disagreement and synthesize one recommendation.

## When To Use

Recommend Council when the stakes, difficulty of reversal, conflicting evidence, or competing interests make multiple perspectives useful. Routine edits and simple fact lookups are not default uses. An explicit request to run `$council` still uses the full contract below; never silently reduce the advisor count or replace the models. Same-model advisors provide separate information flows, not guaranteed independence of errors. Quality gains over a single model remain unverified without comparative evidence.

## Task Packet Check

Preserve the original user request beside the frozen packet. Separate user-stated goals and constraints from the parent's interpretations, assumptions, and unknowns. Before dispatch, compare the packet against the original for omitted constraints, unsupported premises, and a changed decision question. Resolve what the available context supports; ask only if a consequential ambiguity remains.

Every advisor may challenge the packet's framing and should record a material concern under `assumptions` or `data limits`. Do not force an answer to a false premise. Sol receives both the original request and the frozen packet. If the framing materially changes during the run, report the affected conclusions as conditional or withheld; do not silently rewrite the packet or count briefs on different questions as one complete run.

## Runtime Contract

For every explicit `$council` invocation:

1. Freeze one task packet containing the user request, goal, constraints, known evidence, as-of date when relevant, and authorization boundaries.
2. Dispatch exactly five fresh advisor threads. Use the `luna_worker` agent type when available, or an equivalent explicitly pinned profile with:
   - model: `gpt-5.6-luna`
   - reasoning effort: `max`
   - service tier: prefer `fast` only when the dispatch API explicitly supports it. Otherwise use the supported default or inherited tier; do not send unsupported parameters. Record the exposed tier (for example `priority`) or `not exposed` in the runtime ledger. Do not infer an actual tier from a requested tier or describe an inherited tier as verified fast service.
3. Give every advisor the same frozen task packet plus only its role-specific emphasis. Do not fork the full conversation, reveal another advisor's output, or let advisors debate each other.
4. Wait for all five terminal results. If the runtime cannot run five advisors concurrently, run them in waves without changing their prompts or sharing earlier results. Choose task-appropriate advisor and overall deadlines before dispatch. Record role, attempt ID, start/end time, terminal state, and available usage; record unavailable token or cost data as unknown.
5. Each failed role may be retried at most once with the same role and runtime profile. Confirm the previous attempt has ended or been cancelled before redispatch. Dispatch errors, timeouts, and malformed briefs share this per-role retry budget; do not add unlimited format-repair attempts or silently restart the whole Council to evade the budget. Select one valid terminal brief per role, log all attempts, and exclude late duplicate results from the gate. If any unique role still lacks a valid result, report `Failed Council`; do not silently simulate, substitute another model, or present a partial run as a full council.
6. After the five-of-five completion gate passes, synthesize with `gpt-5.6-sol` at `max` reasoning. Use the parent when it is already pinned to that profile; otherwise spawn a dedicated Sol synthesizer when the runtime supports explicit model selection.
7. If Luna/max or Sol/max is unavailable, state the missing model or reasoning capability and stop the full Council workflow instead of weakening the contract silently. A missing service-tier selector does not block Council when the model and reasoning profiles are available; disclose this runtime limitation.

Advisor threads inherit the parent's sandbox, approval, network, MCP, and skill access. Do not request broader permissions merely to improve an opinion. Keep advisory work read-only unless the original user request explicitly authorizes a scoped mutation and the parent assigns it.

## Advisor Roles

- Strategist: test long-term direction, strategic fit, opportunity cost, and second-order effects.
- Skeptic: falsify assumptions, expose blind spots, and describe downside and failure cases.
- Creative: find alternative frames, unconventional options, and sharper formulations within the constraints.
- Operator: turn the goal into executable sequencing, resources, dependencies, validation, and rollback steps.
- Audience Advocate: represent the customer, user, reader, employee, or investor; test trust, clarity, objections, and usability.

Keep the roles non-overlapping. When research is needed, assign distinct evidence lanes or questions instead of asking all five advisors to perform the same search. Report relevant findings within each role's emphasis; do not impose quotas for counterexamples, alternatives, or disagreement. `Not applicable` or `None found`, with the reason and scope examined in the user's language, is a valid finding. Do not invent risks or weaker alternatives to fill a role.

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
- every advisor used the Luna/max profile, and its requested or inherited service tier is recorded without claiming an unverified actual tier;
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

For decision-driving disagreements and material minority warnings, leave a short disposition: adopted, rejected with a reason, or unresolved, with the originating role. No minimum number of disagreements is required. The parent checks the synthesis against those briefs and the original request for distorted claims, omitted material warnings, and confidence unsupported by evidence before presenting it. If correction is needed, request a focused Sol correction and record the attempt; allow at most one such correction. If synthesis fails, or a material fidelity defect remains after the permitted correction, report `Failed Council`, even after five valid briefs. Do not add a standing extra reviewer by default. This check supports traceability; it is not independent proof of accuracy.

For financial, legal, medical, safety-critical, technical, or current product decisions, verify current facts before answering. For financial outputs, state that the result is research support rather than personal investment advice and include invalidation and risk controls.

## Process And Evidence Status

Always report these separately, with field labels in the user's language if appropriate:

- `Process status`: `Not started` before dispatch; `In progress` while running or a permitted correction is pending; `Full Council completed` only after the five-role gate, Sol synthesis, and parent fidelity check pass; `Failed Council` when aborted, required capabilities are unavailable, retries are exhausted, or a material fidelity defect remains after correction. State the failed stage. Repair a recoverable draft packet omission before dispatch rather than declaring a completed or terminally failed run.
- `Evidence confidence`: high, medium, or low, with a brief justification tied to source support and material unknowns. Before substantive assessment, use low and explain that evidence has not yet been assessed. Do not derive confidence from advisor counts or process completion.
- `Unresolved claims`: unknowns that could change the choice, or none with a brief explanation. State whether the recommendation is supported, conditional, or withheld.

A complete process can legitimately have low evidence confidence and a withheld recommendation. Insufficient evidence alone is not an execution failure. Never substitute fabricated certainty for a withheld answer.

## Recipes

Read `references/council-recipes.md` when the request matches a reusable prompt type. A recipe shapes the content only; it never changes the five-Luna completion gate or the Sol synthesis contract.

## Evaluate Before Expanding

When asked to benchmark Council or expand its workflow, read [references/council-evaluation.md](references/council-evaluation.md). Start with a small blinded comparison against single Sol/max before imposing JSON, strict role deliverables, a full claim ledger, or additional modes. This is an evaluation protocol, not a benchmark to run on every invocation. Do not claim performance improvements from static validation or one successful run.

## Output Shape

Keep the answer proportionate to the task. Always include the status block; recipes may add content but cannot omit it. Use the following compact default. Include the advisor table or detailed ledger when useful or requested, rather than repeating conclusions in multiple sections.

```markdown
**Conclusion**
[one practical answer, conditional recommendation, or reason to withhold]

Process status: [Not started / In progress / Full Council completed / Failed Council; failed stage if any]
Evidence confidence: [high / medium / low, and why]
Unresolved claims: [decision-changing unknowns, or none and why]

**Reasons And Disagreement**
[strongest evidence; material disagreements/warnings and their disposition, or none]

[what would invalidate the recommendation]

**Next Steps**
[only useful next actions, with no fixed count]

**Runtime Ledger**
[compact summary: five accepted roles, Sol profile, fidelity check, retries, elapsed time, available usage, and limits; retain attempt details for inspection]
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
