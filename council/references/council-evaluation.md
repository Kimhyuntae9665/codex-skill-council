# Council Evaluation

Read when benchmarking Council or deciding whether to add more structure or modes. Do not run this protocol during every Council request. Preserve the full five-role model assignment plus GPT-6.1 Sol/max synthesis contract in the Council condition; proposed alternatives are separate explicitly named experiments.

## Start Small

Implement separate process/evidence reporting and minimal records first. Treat v1.1 (five GPT-5.6 Luna reviewers and GPT-5.6 Sol synthesis) and v1.2 (the mixed-model assignment) as different conditions; do not transfer old scores to the new contract. Then compare current Council against single `gpt-6.1-sol` at `max` on a small frozen case set. Use results to choose targeted changes, rather than adding every proposed mechanism first. Do not require JSON, role-output quotas, or a complete claim-ID ledger for this initial comparison.

Include conflicting sources, ambiguous goals, false premises, missing decisive information, and a plan constrained by resources or reversibility. Start with a few representative cases; a fixed run count is not evidence of statistical significance. Freeze the cases and scoring rules before reading the answers.

Both conditions receive the same preserved user request, frozen packet and raw evidence, date, permissions, and tool access. Preserve known answers or assessment criteria separately from the model inputs. Check packet fidelity against the original request so a misframed question is not mistaken for a successful answer. If live sources cannot be frozen, record source versions and access times and disclose the comparability limit.

Define comparable stopping/resource limits and record the actual resources used. Council's additional calls are part of its cost, not a free advantage to hide. Record advisor parallelism rather than describing all six model executions as sequential.

## Blind Scoring

Assign opaque answer IDs and hide the condition, model names, advisor table, and runtime ledger from the answer-quality evaluator. Neutralize workflow-identifying role names in the scoring copy using consistent anonymous labels, preserving substantive claims and attribution in the raw record. Retain recommendation, substantive reasons, evidence confidence, and unresolved claims; do not rewrite an answer to improve it. Score synthesis fidelity separately with access to the briefs. Do not award points just for length or process ceremony. Formatting or phrasing may still reveal the condition; record any remaining blinding limit.

Score:

- Material factual errors and unsupported decision-driving claims.
- Whether cited evidence supports the associated claim.
- False-premise detection and fidelity to the original goal and constraints.
- Appropriate uncertainty, conditional answers, and justified withholding.
- Important risks, useful alternatives, and executable recommendations.
- For Council: distorted advisor claims, omitted material minority warnings, and unwarranted increases in confidence during synthesis.

Ground scores in source evidence or predeclared criteria, not model preference. A human evaluator is useful; if an LLM scores, disclose its profile and treat its scores as fallible. Inspect disputed judgments against the sources. A synthesis model grading itself is not independent validation.

## Minimum Records

For each case and condition retain the original request, frozen packet/evidence, prompts, raw answers, exposed model/reasoning/tier settings, start/end times, retries/failures, actual token usage and cost if exposed, and scoring reasons. Mark unavailable fields unknown. Keep blind ID mapping separate from scoring inputs and restore the mapping only after blind scores are fixed.

Classify execution failures separately from low-quality or appropriately withheld answers. A legitimate `limited` brief, `None found` role finding, or evidence-based withheld recommendation is not automatically a failure. Report wall-clock time as well as usage; simultaneous advisors do not have additive wall-clock duration.

## Targeted Follow-Up

Use observed failures to select the next change:

- Status confused with reliability: improve process/evidence separation.
- Packet changes the problem: improve request-to-packet checks.
- Role repetition: clarify useful role-specific outcomes while retaining `Not applicable` with a reason.
- Unsupported important claims: strengthen selective claim-to-source links.
- Format or retry faults: design parsing and retry handling together; test migration before requiring JSON.
- Synthesis loses warnings: improve dispositions and the parent fidelity check.
- Little quality gain at substantial extra cost: narrow recommended use; evaluate any lighter workflow separately, never call it the unchanged Full Council.

If operational faults appear, test missing fields, duplicate roles, wrong profiles, timeouts with late results, and unavailable Sol in an isolated fixture set. Fixture expectations and document checks do not establish live runtime behavior. Do not claim a benchmark win, reliable recovery, or measured improvement without the corresponding results. Expand the case set when results are mixed; report uncertainty and limit conclusions to the cases evaluated.
