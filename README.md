# 반도체 시료 생산주문관리 시스템

가상의 반도체 회사 "S-Semi"의 시료(Sample) 생산과 주문을 관리하는 콘솔 애플리케이션이다.
Agentic Engineering 방법론(문서 관리, Verify Harness, TDD, Clean Code, Commit 이력)을 적용하여 개발했다.

## 실행 방법

```
python main.py
```

## 테스트 / 검증

```
python -m pytest tests/     # 전체 단위 테스트 실행
python scripts/verify.py    # Verify Harness (Test Verify -> Compliance Verify)
```

## 주요 기능

| 메뉴 | 설명 |
|---|---|
| 1. 시료 관리 | 시료 등록/조회/검색 |
| 2. 시료 주문 | 고객 주문 접수 (RESERVED) |
| 3. 주문 승인/거절 | 재고 비교 후 즉시 출고 대기(CONFIRMED) 또는 생산 큐 등록(PRODUCING), 거절(REJECTED) |
| 4. 모니터링 | 상태별 주문 수(REJECTED 제외), 시료별 재고 상태(여유/부족/고갈) |
| 5. 생산 라인 | 생산 큐 FIFO 처리, 실생산량(ceil(부족분/수율))·생산시간 계산, 생산 완료 시 CONFIRMED 전환 |
| 6. 출고 처리 | CONFIRMED 주문 출고 실행 (RELEASE) |

## 예시 UI 화면

실제 실행 결과를 캡처한 화면이다(입력값은 `>` 뒤에 표시됨).

### 메인 메뉴
```
============================================================
 반도체 시료 생산주문관리 시스템
============================================================
[1] 시료 관리   [2] 시료 주문   [3] 주문 승인/거절
[4] 모니터링    [5] 생산 라인   [6] 출고 처리   [0] 종료
선택 >
```

### 시료 관리 - 목록 조회
```
------------------------------------------------------------
 [시료 관리]
[1] 시료 등록   [2] 시료 목록   [3] 시료 검색   [0] 뒤로
선택 > 2
ID      이름                  평균생산시간        수율      재고
S-001   실리콘 웨이퍼-8인치         0.5           0.92    480
S-003   SiC 파워기판-6인치        0.8           0.92    30
```

### 주문 승인/거절 (재고 충분 -> CONFIRMED, 재고 부족 -> PRODUCING)
```
------------------------------------------------------------
 [주문 승인/거절]
[1] 승인   [2] 거절   [0] 뒤로
주문번호          시료ID    고객명             수량      상태
ORD-0001      S-001   삼성전자 파운드리       200     RESERVED
ORD-0002      S-003   삼성전자 파운드리       200     RESERVED
선택 > 1
주문번호 > ORD-0001
승인 완료. 상태: CONFIRMED
------------------------------------------------------------
 [주문 승인/거절]
[1] 승인   [2] 거절   [0] 뒤로
주문번호          시료ID    고객명             수량      상태
ORD-0002      S-003   삼성전자 파운드리       200     RESERVED
선택 > 1
주문번호 > ORD-0002
승인 완료. 상태: PRODUCING
```

### 모니터링
```
------------------------------------------------------------
 [모니터링]
[1] 주문량 확인   [2] 재고량 확인   [0] 뒤로
선택 > 1
[상태별 주문 현황] (REJECTED 제외)
  RESERVED    0건
  CONFIRMED   1건
  PRODUCING   1건
  RELEASE     0건

선택 > 2
ID      이름                  재고      상태
S-001   실리콘 웨이퍼-8인치         280     여유
S-003   SiC 파워기판-6인치        30      부족
```

### 생산 라인
```
------------------------------------------------------------
 [생산 라인]
[1] 다음 항목 생산 처리   [2] 대기열 조회   [0] 뒤로
선택 > 2
순서    주문번호          시료ID    부족분     주문수량
1     ORD-0002      S-003   170     200
선택 > 1
생산 완료 - 주문 ORD-0002 / 시료 S-003 / 부족분 170 -> 실생산량 185 (예상 소요 148.00분)
```

## 프로젝트 구조

```
app/
  models/         # Sample, Order 등 순수 데이터 모델
  repositories/   # JSON 기반 CRUD 저장소
  controllers/    # 도메인 로직 (View에 비의존적, 단위 테스트 가능)
  views/          # 콘솔 입출력 전담
scripts/verify.py # Verify Harness
tests/            # pytest 단위 테스트
docs/             # PRD, PLAN, Phase별 설계 문서, 작업 보고서
data/             # 실행 시 자동 생성되는 JSON 데이터 (git 미포함)
```

## 문서

- [`docs/PRD.md`](docs/PRD.md): 전체 요구사항
- [`docs/PLAN.md`](docs/PLAN.md): Phase별 개발 계획 및 진행 상황(거시적 계획)
- [`docs/design/`](docs/design/README.md): Phase별 상세 설계 문서(세부 계획)
- [`docs/REPORT.md`](docs/REPORT.md): Phase별 AI 작업 보고서 (요청/해석/TDD 기록/체크리스트)
- [`docs/AUDIT.md`](docs/AUDIT.md): 감리 보고서 (커밋 이력/문서-코드 일치/Clean Code/검증 이력 점검)
- [`CLAUDE.md`](CLAUDE.md): 개발 프로세스 원칙 및 도메인 핵심 규칙

## 개발 프로세스

각 Phase는 다음 순서로 진행한다: 설계 문서 작성 → 사람 검토/승인 → TDD(RED→GREEN) 구현 →
Verify Harness(pytest + Compliance 체크) → 콘솔 E2E 수동 검증 → 작업 보고서 작성 → 커밋.

## 관련 리포지토리 (미션1 PoC)

- [ConsoleMVC-jihoonlee-23020975](https://github.com/jihoonlee91/ConsoleMVC-jihoonlee-23020975)
- [DataPersistence-jihoonlee-23020975](https://github.com/jihoonlee91/DataPersistence-jihoonlee-23020975)
- [DataMonitor-jihoonlee-23020975](https://github.com/jihoonlee91/DataMonitor-jihoonlee-23020975)
- [DummyDataGenerator-jihoonlee-23020975](https://github.com/jihoonlee91/DummyDataGenerator-jihoonlee-23020975)
