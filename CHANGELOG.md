# Changes

## v1.3.1 — 2026-10-12

### 한국어

- 기존 독립 5역할, Sol/Astra/Luna 배치, max, 5/5 완료 계약을 유지하면서 작은 오프라인 런타임 완료 검사기를 추가했습니다.
- 호스트 기록/적용 설정에 근거한 모델·effort 확인, 필수 필드·상태, 역할/시도 중복, 종료 확인, 재시도·교정 한도, 늦은 결과, 역할별·전체 기한, 검색/검증 호출 한도를 검사합니다. 자기보고나 요청값을 실제 실행 근거로 간주하지 않습니다.
- 실패 시 유용한 결과·누락 역할·시도 기록을 보존하며 Partial 성공 모드는 추가하지 않습니다. 설치 검사와 런타임 검사를 분리하고 모델 표/설정의 불일치도 검사합니다.
- 읽기 전용/동료 격리의 지시문 수준 한계와 기록 신뢰 경계를 공개하고, 민감정보 최소화·비신뢰 자료 취급·간단한 근거 신뢰도 기준을 보완했습니다. 보안 설정은 변경하지 않습니다.
- 정상·오류·확인 불가·재시도·늦은 결과·시간/호출 한도·실패 자료 보존·UTF-8 경로 회귀 테스트를 기존 설치 테스트와 세 OS CI에 연결했습니다.

### English

- Add an offline host-ledger completion checker without changing the independent five-role/model/max contract.
- Check provenance, fields/status, unique attempts, confirmed termination, bounded retries/corrections, late results, deadlines, call caps, synthesis and parent fidelity. Retain failure evidence; never label four roles as Full.
- Extend package table/profile consistency checks and existing installation/three-OS tests. Document instruction-level sandbox/isolation limits and simple confidence criteria.

Fixture and installation checks do not establish live enforcement, model quality, or measured accuracy/latency/cost gains. The existing blinded evaluation protocol is unchanged; no model benchmark is run by these helpers.

## v1.3.0 — 2026-10-10

### 한국어

- Creative Astra에 가정 전환·다른 분야 원리 적용·작은 검증 실험 지침을 추가했습니다. temperature/top_p와 모델 구성은 변경하지 않습니다.
- 최종 답변에 실제 Creative 제안과 채택·보류·기각 이유를 표시합니다. 보류한 제안에는 판단을 해결할 근거·실험을 적고 부모가 원 검토 결과와 대조합니다.
- 제안이 없거나 검토가 실패했을 때 의견을 만들지 않고 그 상태를 표시합니다. 독창성·반례 개수는 강제하지 않습니다.
- README 흐름도에 모델명과 짧은 에이전트 역할을 두 줄로 표시해 같은 Astra 로고의 Skeptic/Creative를 구별합니다.
- 스킬 업데이트 백업을 검색 폴더 밖의 `skill-backups/`로 옮겨 구버전 중복 발견을 방지했습니다. 기존 개인 에이전트 설정은 계속 보호합니다.

### English

- Add Creative-only assumption reframing, suitable cross-domain mechanisms, and small reversible tests; do not change temperature, top_p, or model assignments.
- Preserve the actual Creative proposal in the final answer with adoption/hold/rejection reasons and resolving tests for held ideas. The parent verifies proposal fidelity; absence/failure is reported honestly.
- Add visible per-node role labels to the SVG/PNG flow and update both guides.
- Keep update backups outside skill discovery under `skill-backups/`, preserving older copies without duplicate discovery.

These are instruction, presentation, and installation changes. Tests do not demonstrate increased creative quality or decision accuracy.

## v1.2.0 — 2026-10-10

### 한국어

- 전략·실행 검토와 종합을 `gpt-6.1-sol/max`로 변경했습니다.
- 반례·대안 검토를 `gpt-6-astra/max`, 사용자 관점 검토를 `gpt-6-luna/max`로 변경했습니다.
- `luna_worker` 고정 프로필 대신 `council_sol`, `council_astra`, `council_luna` 설정 3개를 제공합니다. 각각의 검토는 별도의 새 에이전트에서 실행합니다.
- 설치 도구가 세 프로필의 파일·이름 충돌을 모두 사전 확인합니다. `--with-agents`를 사용하며 기존 `--with-agent`도 별칭으로 지원합니다. 기존 개인 설정과 구형 전역 Luna 프로필은 자동 덮어쓰기·삭제하지 않습니다.
- 한·영 README, 모델 표, 흐름도 PNG/SVG·그래프·출처 기록, 패키지 검사와 비교 평가 기준을 함께 갱신했습니다.
- 검토자 5명, 실행 완료와 근거 신뢰도의 분리, 소수 경고 보존, 부모의 종합 대조, 역할별 재시도 한도는 유지했습니다.

배포 호스트의 모델 목록에서 확인된 Astra/Luna의 ID는 6-series입니다. `6.1 Astra`, `6.1 Luna`, `6 Terra`를 임의로 만들지 않았으며 구형 `gpt-5.6-terra`는 기본 구성에서 제외했습니다. 모델 교체의 정확도·속도·비용 효과는 아직 비교 측정하지 않았습니다.

### English

- Use `gpt-6.1-sol/max` for strategy, execution review, and synthesis; `gpt-6-astra/max` for skepticism and alternatives; `gpt-6-luna/max` for audience advocacy.
- Replace the fixed legacy `luna_worker` asset with three Council-specific profiles. Every advisor still runs in its own fresh thread.
- Install/check all three profiles, preflight name and file collisions, preserve personal settings, and keep `--with-agent` as an alias for `--with-agents`.
- Update both READMEs, diagram exports/source/provenance, package checks, upgrade tests, and the single-model evaluation baseline.
- Preserve the five-role gate, process/evidence separation, minority-warning dispositions, parent fidelity check, and bounded retries.

Model IDs were confirmed in the publishing host's Codex catalog; availability varies by account and host. Unexposed 6.1 Astra/Luna or 6 Terra aliases are not used. No measured quality, speed, or cost gain is claimed for this model migration.

## v1.1.0 — 2026-10-10

Initial public package: five GPT-5.6 Luna/max reviewers and GPT-5.6 Sol/max synthesis, evidence-aware reporting, bilingual installation guides, logo flow diagram, portable installer, integrity checks, and three-OS CI.
