# 감리 보고서 (AUDIT.md)

AI 시대의 PR 리뷰어는 코드 자체뿐 아니라 "코드가 만들어지는 과정"까지 검증하는 감리(Day2-1 PDF, Ch.VI) 역할을
맡는다. 이 문서는 SampleOrderSystem 리포지토리 전체를 제3자 감리 관점에서 점검한 결과다.

> 개정 이력: 최초 작성(Phase 7 완료 시점, 커밋 `4627719`) → Phase 8~10 및 버그 수정 8건 반영
> 갱신(2026-07-15, 커밋 `621e061`) → Phase 11(CI/성능/View 테스트) 반영 갱신(2026-07-15,
> 커밋 `1c3f147`) → 정밀도/정합성 재점검 최종 갱신(2026-07-15, 이 커밋). 변경/추가된 절에는
> "(갱신)" 표기.
>
> 참고: 아래 커밋 수는 **이 문서를 갱신하는 커밋 직전** 기준 스냅샷이다. 이 문서 자체를
> 커밋하는 순간 총 커밋 수는 항상 1 증가하므로(자기 자신을 포함해 셀 수 없는 자기 참조
> 특성), 정확한 최신 수치는 `git log --oneline | wc -l`로 직접 확인하는 것이 원칙적으로
> 더 정확하다. 이는 의도적 오차이지 은폐가 아님을 명시한다.

## 1. 업무 수칙 준수 확인 (Commit 이력) (갱신)

- 이 문서 갱신 커밋 직전 기준 전체 커밋 29개 중 28개에 `Reviewed-by: jihoonlee91` 표기 확인.
  표기 없는 1건은 최초 스캐폴드 커밋(`Initialize SampleOrderSystem repository`)으로,
  문서/코드 변경이 없는 리포지토리 생성용 커밋이라 리뷰 대상이 아님 → 정상.
- Phase 1~11이 각각 최소 1개 이상의 커밋으로 분리되어 있으며, 커밋 메시지에 참조한 설계 문서
  (`docs/design/phaseN.md`)와 테스트 결과(`pytest N/N PASS`)가 명시되어 있음 → Agentic Engineering
  프로세스(설계→구현→검증→커밋) 준수 확인.
- 버그 수정 커밋(`fix: add sample data validation...`, `fix: prevent negative stock from concurrent
  insufficient-stock approvals`, `fix: block blank sample id/name, fix Korean table alignment`)에
  발견 경위(Safety Test / 재현 스크립트 / 사용자 신고)와 승인 근거가 `docs/REPORT.md`에 기록되어
  있음 → 정상.
- 리팩토링(`refactor: extract InvalidOrderStateError...`, `refactor: remove dead code...`)과
  기능 추가/성능 개선(`feat(phaseN)...`, `perf(phase10)...`)이 별도 커밋으로 분리되어 있어 변경
  이력 추적이 용이함 → 정상.
- Phase 10(JsonStore 캐싱), Phase 11(CI/배치쓰기/View 테스트)은 각각 설계 문서 작성 → 사용자
  승인(AskUserQuestion) → 구현 → 커밋 순서를 그대로 따름 → Phase 7 이후 절차 준수 확인.
- **(갱신)** Phase 11은 자체 채점("90~92점")에 대한 사용자의 "CI + 성능 + View 테스트 보강까지
  전부"라는 명시적 승인을 근거로 진행됨 → AI의 자기평가가 아니라 사용자 결정에 따라 추가 작업
  범위가 확정된 사례.

## 2. 설계도면/시방서 체크 (문서 vs 코드) (갱신)

| 문서 | 코드 위치 | 일치 여부 |
|---|---|---|
| PRD.md 기능 요구사항 1~6 | `app/controllers/*.py` 6개 컨트롤러 | ✅ 1:1 대응 |
| docs/design/phase1~7.md, phase9_ui.md, phase10_perf.md, phase11.md | 각 Phase 커밋의 diff | ✅ 설계 범위 내 구현 (편차는 REPORT.md에 기록) |
| docs/FEATURES/*.md | 각 컨트롤러의 검증/분기 로직 | ✅ 일치 (공백 ID/이름 차단 규칙 누락분을 이번 점검에서 발견·보완, 커밋 `370400b`) |
| CLAUDE.md 도메인 규칙 | OrderStatus 전이, 재고 즉시 소진, ceil 계산식, FIFO | ✅ 코드와 일치. 재고 이중 계산 버그 수정 이력이 "왜 이 불변식이 중요한가"와 함께 명시되어 있어 재발 방지 근거로 기능함 |
| README.md 예시 UI 화면 | `app/views/console_view.py` 실제 출력 | ✅ 손으로 옮겨 적은 예시가 아니라 실제 실행 결과를 캡처해 `diff`로 완전 일치 확인 후 반영(커밋 `f9feea1`) |

## 3. 자재(라이브러리/자료구조/알고리즘) 적절성

- 외부 라이브러리 없이 표준 라이브러리(`json`, `dataclasses`, `enum`, `math.ceil`, `unicodedata`)만
  사용 → 과도한 의존성 없음. `requirements.txt`는 테스트 도구(pytest)만을 위한 것이며 실행 자체에는
  불필요함을 README/CLAUDE.md에 명시 → 정상.
- 생산 큐는 리스트 기반 JSON 저장소로 FIFO를 구현(`find_all()[0]`을 꺼내고 삭제) → 규모상 적절하며
  과도한 자료구조(우선순위 큐 등) 도입 없음(Over-engineering 회피).
- 예외 클래스가 기능별로 분리되어 있으나(`DuplicateSampleError`, `InvalidSampleDataError`,
  `SampleNotFoundError`, `InvalidQuantityError`, `InvalidOrderStateError`), 상태 관련 예외
  (`InvalidOrderStateError`)는 공통 모듈로 통합되어 있어 불필요한 중복은 제거됨.
- **(갱신)** JsonStore는 1000건 규모 스트레스 테스트에서 쓰기 성능 저하가 확인되었고, 읽기는
  인메모리 캐싱으로 개선(Phase 10)했다. 쓰기는 처음엔 "여기까지만, 문서화하고 마무리"로 범위를
  제한했으나(Phase 10), 이후 사용자가 재검토를 요청해 Phase 11에서 `flush=False`+`flush()`
  배치 옵션으로 실제 해결(배치 삽입 1000건 기준 1.51s → 약 0.005s 실측, 반올림 표기로 인한
  과장 방지를 위해 소수점 4자리까지 REPORT.md에 원본 수치 기록). 인터랙티브 흐름은 안전을
  위해 매번 즉시 flush하는 기존 계약을 그대로 유지 → "일단 보류했던 결정도 재검토 요청이 오면
  다시 열어 해결한다"는 유연한 대응 사례.
- **(갱신)** 독립 SubAgent 코드 리뷰를 통해 `app/models/sample.py`의 `Sample` dataclass 및
  `Order` dataclass 일부 필드가 실제로는 어디서도 사용되지 않는 죽은 코드임을 발견, 사용자 승인 후
  삭제(커밋 `64ad34d`) → 자재(코드)의 불필요한 부분을 남겨두지 않음.

## 4. 코드 리뷰 (Clean Code 원칙)

- Model(`app/models/`): 순수 데이터(Enum), 로직 없음 → 확인. 미사용 dataclass는 삭제되어 현재는
  `OrderStatus` Enum만 존재.
- Repository(`app/repositories/`): CRUD/조회만 수행, 도메인 규칙 없음 → 확인. `JsonStore` 캐싱
  추가(Phase 10) 후에도 캐시 무효화/동기화는 Repository 내부에 캡슐화되어 Controller에는 영향 없음.
- Controller(`app/controllers/`): 도메인 규칙 전담, View/Repository 구체 구현에 비의존 → 확인.
- View(`app/views/console_view.py`): 입출력만 수행. **(갱신)** 한글/전각 문자 표시 너비를 고려한
  정렬 헬퍼(`display_width`, `visual_ljust`, `join_columns`)가 추가되었으나 이는 순수 함수로 분리되어
  있어 여전히 "출력 포맷팅"의 범주이며 도메인 로직 유입은 아님 → Clean Code 경계 유지 확인.
- 미사용 코드/import: 없음(SubAgent 감사 + grep으로 재확인, 중복 테스트 블록 1건도 발견 즉시 제거).
- **(갱신)** `MainController`는 테스트 커버리지를 높이기 위해 생성자에 의존성 주입을 추가하는
  리팩토링을 하지 않고, 기존 구조 그대로 `monkeypatch.chdir` + `input` 큐로 테스트했다(Phase 11)
  → 테스트 편의를 위해 불필요한 구조 변경을 하지 않는다는 원칙 유지.

## 5. 검증 이력 (Test / Verify) (갱신)

- 최종 테스트 스위트: 16개 파일, 90개 테스트 전부 PASS.
- 커버리지 측정(coverage) 결과 Model/Repository/Controller/MainController 계층 100% 도달
  (`app/` 전체 라인 기준 99%), `console_view.py`의 순수 출력 print 구문 일부만 의도적으로
  수동 E2E로 분리(설계상 결정, README/REPORT에 근거 기록).
- **(갱신)** GitHub Actions(`.github/workflows/test.yml`)로 push/PR 시 pytest가 원격에서도
  자동 실행되도록 구성, 실제 실행 결과 success 확인(Phase 11) → 로컬 Verify Harness에만
  의존하지 않는 이중 안전망 확보.
- Safety Test로 실제 크래시 버그(수율 0 → ZeroDivisionError)를 발견하고 수정함 → 안전성 검증 효과 입증.
- **(갱신)** 실제 재현 스크립트로 "동시 승인 시 재고 이중 계산" 버그(최종 재고가 음수로 떨어짐)를
  발견 → 근본 원인 분석(승인 시점 재고 미차감) → 수정 → 재현 스크립트 재실행으로 음수 재고 미발생
  확인. 단위 테스트만으로는 놓칠 뻔한 버그를 시나리오 기반 수동 검증으로 잡아낸 사례.
- **(갱신)** 독립 컨텍스트의 SubAgent(Agent 도구)를 투입해 본 세션과 별개로 코드베이스를 재검토,
  죽은 코드를 발견 → Day1 PDF의 "제3자 검증" 원칙을 실제로 적용한 사례.
- **(갱신)** 클린 클론 스모크 테스트(`git clone` 후 새 디렉터리에서 pytest 실행)로
  `requirements.txt` 누락을 발견·수정. 로컬 환경에 우연히 pytest가 이미 설치되어 있어 겉으로는
  문제없어 보였던 재현성 결함을 잡아낸 사례.
- **(갱신)** 1000건 규모 더미 주문 스트레스 테스트로 쓰기 성능 한계(약 18초/1000건 승인)를 발견 →
  읽기 캐싱으로 부분 개선 → 남은 한계는 문서화(§3 참고).
- **(갱신)** 실제 실행 화면을 캡처해 README 예시와 `diff`로 대조, 수기 작성 예시의 정렬 오차를
  발견·수정(완전 일치 확인).
- 전체 생애주기 E2E(등록→주문→승인/거절→모니터링→생산→출고→모니터링)를 콘솔에서 직접 실행하여
  Phase 8, Phase 9(UI 고도화 후), Phase 10(캐싱 후) 시점에 반복 확인.

## 6. 인지적 부채(Cognitive Debt) 점검 (갱신)

- 핵심 로직(재고 계산식: 승인 시 즉시 소진 + 생산 완료 시 `실생산량 - 부족분` 반영)에 대해 사용자가
  직접 설명을 요청하여 구두로 검증받음 → 코드 작성자(AI)만 이해하고 있는 상태가 아니라, 검토자
  (사용자)도 로직을 이해한 상태로 넘어감(인지적 부채 완화).
- 모든 Phase의 설계 문서에 "왜 이렇게 설계했는가"에 대한 해석(`docs/REPORT.md`의 "해석" 절)이 남아있어,
  추후 재검토 시에도 의사결정 배경을 복원할 수 있음.
- **(갱신)** 재고 이중 계산 버그처럼 "왜 이 불변식이 필요한가"를 잊으면 재발할 수 있는 규칙은
  CLAUDE.md 도메인 규칙 절에 재발 방지 목적으로 근거와 함께 명문화함 → 향후 이 코드를 다시 만지는
  사람(AI든 사람이든)이 같은 버그를 반복하지 않도록 인지적 부채를 코드가 아닌 문서로 이전함.
- **(갱신)** JsonStore 쓰기 성능 한계처럼 "고칠 수 있지만 지금은 안 고치기로 한" 결정도
  묻어두지 않고 CLAUDE.md에 근거·수치와 함께 명시 → 향후 요구사항(대량 데이터) 변경 시 이 문서만
  보고도 재검토 여부를 판단할 수 있음.

## 종합 판정 (갱신)

**승인 (제출 최종 상태 기준 재확인).** 문서-코드 일치, 커밋 프로세스 준수, 안전성/동시성/성능/
재현성/CI자동화 검증까지 전 범위에 걸쳐 확인되었으며, 발견된 모든 버그(크래시, 재고 이중 계산,
공백 ID, 정렬 오류, 의존성 명세 누락)는 사용자 승인 하에 수정 완료됨. 코드를 만든 주체(AI)가
아니라 검토·승인한 사람(jihoonlee91)이 최종 책임을 진다는 원칙에 따라 아래와 같이 도장을 남긴다.

```
위 감리 내용은 CLAUDE.md 및 각 Phase 설계 문서(Phase 1~11)에 근거하여 AI가 작성하였으며,
최종 검토 및 승인 책임은 사용자(jihoonlee91)에게 있습니다.
```
