# Changes

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
