# picasso-robotics 로드맵
기준일 2026-11-11.

## 이 문서를 읽는 법

각 제품 절은 네 가지 상태 어휘로 작업을 분류한다.

- **최근 완료**: 기본 브랜치(default branch)에 병합된 작업.
- **지금·다음**: 명명된 다음 단계 작업.
- **보류 (재개 조건)**: 명시된 재개 조건이 충족될 때까지 미룬 작업, 또는 확약 없는 후보.
- **설계상 하지 않음**: 의도적으로 제외한 항목.

이 조직의 어떤 소프트웨어도 실제 로봇·PLC·상용 MES 에 연결된 적이 없다. picasso 의 어댑터 넷 중 어느 것도 실제 하드웨어에 붙여 보지 못했다(한계 C-3). 로봇은 에뮬레이터 `mimic`, 설비는 셀 대역, 상위 시스템은 로컬 Mock MES 다. 각 항목은 근거 문서로 연결되고, 연결된 문서의 수치와 이 문서가 다를 때는 연결된 문서가 우선한다.

2026-11-10에 저장소들이 개인 계정에서 조직으로 옮기며 `picasso-ops`는 `mission-ops`, `picasso-narrator`는 `incident-narrator`, `koshchei`는 `incident-recovery`로 이름이 바뀌었다. 2026-11-11에는 네 저장소(`picasso`, `mission-ops`, `incident-narrator`, `incident-recovery`)의 문서·빌드·코드 이름을 새 이름으로 바꿨고, 옛 이름은 기록(옛 PR·커밋 인용, ADR, 변경 이력, 계획 문서, 편지)에만 남는다. 이 문서는 조직의 저장소 이름을 쓴다.

## 제품 간 경계

| 저장소 | 역할 | 연결 방식 |
| --- | --- | --- |
| `picasso` | 로봇 표준 인터페이스 계약, 케이퍼빌리티 협상, 공통 실행, 기종별 어댑터, 레지스트리 | 이 조직의 다른 저장소를 빌드에서 참조하지 않는다. [picasso-robotics/picasso](https://github.com/picasso-robotics/picasso) |
| `mission-ops` | 미션 정의와 상위 작업 지시 매핑, 영속 작업 수락, 공유 자원 조정, 운영 UI | 고정 커밋의 picasso 를 git 서브모듈과 Gradle 복합 빌드로 라이브러리처럼 쓴다. [picasso-robotics/mission-ops](https://github.com/picasso-robotics/mission-ops) |
| `incident-narrator` | picasso 인시던트 번들의 원인 설명과 검증된 근거 인용, `incident-recovery` 진단 요청의 대응 권고 | picasso 가 내보낸 파일(`handoff/narrator/`)을 읽고, 진단은 Temporal 액티비티 `diagnose`(큐 `narrator-tq`, 진단 계약 0.6)로 받는다. picasso 는 이 저장소를 부르지 않는다. [picasso-robotics/incident-narrator](https://github.com/picasso-robotics/incident-narrator) |
| `incident-recovery` | 로봇 셀의 단일 고장을 첫 증상부터 해결까지 하나의 에피소드로 추적하는 결정적 상태기계 | picasso 번들과 작업 응답 파일을 읽고 picasso 승인 엔드포인트 `POST /approvals`(버전 4)로 제안을 승인한다. 진단은 `incident-narrator` 에 맡긴다. [picasso-robotics/incident-recovery](https://github.com/picasso-robotics/incident-recovery) |
| `factory-runtime` | picasso 라이브러리의 포트를 실제 로봇·PLC·AMR 드라이버에 배선해 신규 공장에 배포하는 실행 프로세스 | 아직 커밋이 없는 빈 저장소다. [picasso-robotics/factory-runtime](https://github.com/picasso-robotics/factory-runtime) |

공유 계약은 picasso 계약 버전 0.10.0, 내보내기 `schemaVersion` 6(5 와 6 을 함께 읽는 소비자가 있다), 승인 엔드포인트 버전 4, 작업 응답 내보내기(`job-responses.jsonl`) 줄마다 `schemaVersion` 1, 진단 계약 0.6 이다.

## 지금 진행 중인 흐름

- `incident-narrator` 측정 기준선 이동: 측정 기준선은 계약 0.9.0 / 내보내기 schema 5 픽스처에 있고, 0.10.0 세트는 픽스처로 들어와 있다. 다음 실측 때 0.10.0 으로 옮긴다.

## 제품별 로드맵

### picasso

이기종 모바일 로봇(휴머노이드·4족 보행)과 상위 시스템 사이의 표준 인터페이스 계약과 미들웨어 PoC 다. 로봇의 차이와 운영 변경을 표준 계약, 케이퍼빌리티 프로파일, 실행 근거로 다룬다. 기종별 코드는 어댑터로 격리하고 공통 실행 구조를 공유한다. `mimic` 으로 실제 하드웨어 없이 계약과 장애 상황을 시험하고, 프로파일·바인딩 변경의 영향을 `registry` 에서 확인한다. 명령·조회는 gRPC, 상태·이벤트·스트리밍은 MQTT 다. Kotlin, Gradle, JDK 21, 모듈 16개다. 실제 어댑터는 넷(Unitree G1, Boston Dynamics Spot, Agility Digit, Boston Dynamics Orbit 플릿)이다.

**최근 완료** (날짜는 병합일; 2026-11-10 이전 PR 은 옛 개인 저장소에 있다)
- 미들웨어 접합부 분리: AdmissionGate, RemedyDesk, IncidentLog 추출 (2026-09-30).
- 소모된 승인 기록, 운영자 결정 기록, 작업 응답 외부 형식과 승인 호스트 버전 4 (2026-10-01~03). ADR 46~48.
- 레지스트리 리비전 수명주기: 어댑터 제품·빌드 REST, 리비전 시험 실행기, 리비전 제출·활성화·바인딩 (2026-10-07). ADR 49.
- 노드 기반 미션 정의와 버전 고정 (2026-10-08).
- 재시작 뒤 `Middleware.resume` 리빌드 (2026-10-09).
- 판정 기록 (2026-10-14). ADR 50.
- 권한 경계 셋 (2026-10-13, ADR 51).
- 작업 허가 포트·발행 게이트 (2026-10-14, ADR 52).
- 건너뛴 대상의 재작업 (2026-10-18, ADR 53).
- 시계 어긋남 탐지 (2026-10-19).
- 취소·결과 불확실·리빌드 수정과 로봇 퇴역 포트 (2026-11-01~04).
- 소비자·호스트 경로에서 잠금 걷어내기: 비동기 업링크 큐, 호스트 잠금 분리, `IssuingRobotPort`·`PrefetchingFleetPort`·`IssuingFleetPort` (2026-11-05~07).
- 계약 0.10.0 `FaultObservability` (2026-11-05).
- 한계 레지스터 항목 닫기: Orbit CLI와 주기 재탐색, MQTT 관측 구독기, 다이제스트 범위, 관측 불가 원장에서 게이트 검사 6 ERROR, 보존 상한, adapter-host 세션 nonce (2026-11-07).
- 조직 이전과 README 주소 갱신 (2026-11-10).
- 문서 속 저장소 이름 반영: 링크 글자와 본문 속 이름을 새 이름으로 바꿈 (2026-11-11).

**지금·다음**
- 열린 PR 은 없다.
- 상태가 「제안 · 짓지 않음」인 설계 명세 둘은 소비자 PR 이 올 때만 구현한다(ADR 9): 이웃 시스템 디스패치·공간 소유 설계(구현 PR 의 첫 작업은 기체별 후보 거름), 운영 콘솔 수명주기 설계(변경 후보 넷, 결정 아님).
- 스스로 풀 수 있는 내부 오픈 항목 20개가 한계 레지스터에 있다. 예: 인시던트·승인 원장 영속화, adapter-host 가 한 번에 작업 하나만 실행, 승인 호스트를 배포할 수 없음.

**보류 (재개 조건)**
- 한계 레지스터의 오픈 항목은 50개(내부 20 · 외부 30)이고, 의도적 제외 37개(그중 수요 없음 21개)는 이 합계에 넣지 않는다. [limits.md](https://github.com/picasso-robotics/picasso/blob/main/docs/limits.md)
- 수요 없음(소유자 결정 2026-11-04, 이전의 「소비자 대기」 하위 범주를 폐지하고 옮김): 소비자(`incident-narrator`, `mission-ops`, 상위 시스템)가 요청하면 다시 연다. 예: 내보내기에 미션·설정 버전과 결정자 싣기, 분기·병렬 미션, 미션 정의 JSON Schema 파일, 일반화·다중 대상 재작업.
- 외부 항목은 실제 하드웨어·현장·표준의 사실이 생기면 다시 연다. 예: 실제 로봇·HIL 검증(C-3), 현장 시계 어긋남, 타임아웃 예산과 `maxAge`, Orbit 장애 범위, 통로와 바닥의 현장 소유.

**설계상 하지 않음** (설계 명세 §1.3, 한계 레지스터 §1)
- 전역 디스패치·경로·다중 로봇 경합(그래서 계약에 동시성 정책 어휘가 없다).
- E-stop 같은 안전 기능(ADR 32), 물리 시뮬레이션.
- 인증·인가(신뢰 네트워크 전제), 감사 로그의 암호학적 부인 방지, 다중 사이트 배포.
- picasso 와 `incident-recovery` 안의 프로덕션 하드웨어 싱크.

### mission-ops

상위 시스템(MES/WMS)의 외부 작업 지시를 로봇 미션으로 연결하고 작업 요청·실행·결과 회신의 전체 흐름을 운영하는 PoC 다. picasso 위에 있다. 모듈: `ui`(React/Vite 운영 화면), `ops-service`(운영 API, 외부 작업 지시 계약, 영속 작업 요청·결과·ACK, 공유 스테이션 조정), `mission-host`(picasso 를 쓰는 실행 호스트: 미션 검증, 모의 실행, 실행 복원), `site`(registry·mimic·셀 대역을 띄우는 로컬 사이트 런처), `e2e`(통합 시험), `load`(부하 측정 하네스, 빌드와 CI 밖). Kotlin, Spring Boot, JDK 21, Postgres, UI 는 Node 22 다.

**최근 완료**
- 부하 지점 수정과 기체 늘려 재기: 작업 요청 검색에 trigram 인덱스(V24, `pg_trgm`) 추가, 실행 호스트 pump의 기록 문장을 합쳐 pump당 DB 문장 약 42% 감소, 하네스에 기체 100·200 시나리오(`pumpscale`)와 벽시계 표본기 추가, 실측에 따라 수신 미확인 집계 질의와 심장박동 주기(5초·만료 30초) 유지 (2026-11-11).
- 빌드 이름 변경: `rootProject.name`을 `mission-ops`로 변경 (2026-11-11).
- 서브모듈 올림: `picasso` 서브모듈을 `3b5d6c5` 에서 `51d8230` 으로 올림, 계약 0.10.0 에 맞춰 시험 기대값 갱신, `site` 런처가 레지스트리 링크 비우기를 잠금 밖에서 하도록 고침, CI gradle 작업을 `ubuntu-latest` 로 되돌림 (2026-11-11).
- 문서 정비: `docs/reference.md` 의 재작업 폼 설명을 지금 동작에 맞추고 `README` 복제 경로를 `cd mission-ops` 로 정정, 문서의 링크 글자와 본문 속 이름을 새 이름으로 바꿈 (2026-11-11).
- 조직 이전: 서브모듈 URL·문서 링크를 조직 주소로 바꿈, CI gradle 작업을 `ubuntu-24.04` 로 고정 (2026-11-10).
- 퇴역 로봇에 새 명령 막기: registry 진단 읽기(`RetirementPort`)와 `GET /host/retirements` (2026-11-02).
- picasso 서브모듈을 `3b5d6c5` 까지 올림 (2026-11-02).
- 증언 종결의 확인 행 영속화로 재시작 뒤에도 로봇 배정 제외가 유지됨, 시작 복원에 실패한 실행을 운영자가 종결 (2026-10-20).
- 작업 요청 상태 가드 수정, 스테이션의 「호스트 도달 불가」와 「작업 허가 대기」 구분 (2026-10-20).
- 건너뛴 대상 재작업 UI (2026-10-19).
- 장애 수락 API·UI와 사이트 제어 상실 장애 주입 E2E (2026-10-16~17).
- 스테이션 틱과 실행 목록 부하 지점 수정, 끝난 실행을 호스트가 잊고 저널로 재제출 거부 (2026-10-14~15).

**지금·다음** (HA 권한 설계 명세, [2026-10-14-ha-authority-design.md](https://github.com/picasso-robotics/mission-ops/blob/main/docs/superpowers/specs/2026-10-14-ha-authority-design.md))
- `restore()` 와 잔여 상태 검사의 세대 비교를 1단계로 옮긴다.
- 실행 상태 버전은 확정 후보이며 열 이름은 아직 없다.
- 기체 200에서 일하는 pump p95가 425 ms로 주기 250 ms를 넘으며, 다음 병목은 `picasso` `Middleware.sync`(기체마다의 상태 읽기)와 응답마다의 기록 문장이다.

**보류 (재개 조건)**
- 2단계 분할: 단일 활성 구성이 측정한 수치를 못 버틸 때 연다.
- 유휴 로봇 배정 방식과 공유 자원 조정 방식: 2단계에서 정한다.
- 하위 송신자 세대 열: `adapter-host` 펜싱을 구현할 때 더한다.
- 구간 예약 포트: 소비자와 같은 PR 에서 만든다.
- 로봇 → 제어 도메인 해석: YAGNI 로 보류, 조건 없음.

**설계상 하지 않음**
- 인증 생략 PoC 이며 이 기계 밖에서 쓰지 않는다. 콜백은 루프백만.
- 리더 선출, 리스 행, 샤딩, 합의, 다중 사이트·전역 디스패치(HA 명세 §11). 운영·호스트 다중 인스턴스는 지원하지도 검증하지도 않는다.
- 물리적 정확히 한 번, 안전, 실제 하드웨어·상용 연동, 순서 보장 콜백, MES 쪽 취소는 보장하지 않는다([guarantees.md](https://github.com/picasso-robotics/mission-ops/blob/main/docs/guarantees.md)).
- 미션에 자유 DAG·분기·임의 코드 없음.

### incident-narrator

picasso 아래에 있는 LLM 설명 계층 PoC 다. picasso 가 이미 판정한 인시던트 번들을 읽어 원인 후보와 검증된 인용을 쓴다. 판정하지 않는다. 사용 경로 셋: picasso 인시던트 번들 파일, `incident-recovery` 의 진단 요청(계산된 후보 하나를 권하거나 에스컬레이션), `mission-ops` 의 스테이션 근거 파일(상태를 바꾸는 호출 없음). LLM 은 `explainer` 한 곳에서 인시던트마다 한 번만 부른다. Python 3.11 이상. 실제 실행에는 외부 Khala/Nexus 서비스와 `NEXUS_TOKEN` 이 필요하다. 유일한 역방향 호출은 기본으로 꺼진 승인 시도(`--approve`)이고 자격은 picasso 가 정한다.

**최근 완료**
- 진단 워커와 권고 측정 (2026-10-01).
- 승인 엔드포인트 버전 4 읽기와 `instanceId`·`executionId` 기록 (2026-10-03).
- `incident-recovery` 의 이전 저장소 `koshei` 에서 Khala 까지 처음 끝까지 실행, 결과 ESCALATED (2026-10-04).
- 프로덕션 수신기와 진단 워커가 `search_text` 를 보냄 (2026-10-07).
- 내보내기 schema 5 와 6 을 함께 받음 (2026-10-08).
- 파일 기반 공유 스테이션 근거 설명 경로 (2026-10-12).
- GitHub Actions CI (2026-10-13).
- 재시작으로 다시 열린 인시던트를 재발로 두 번 세지 않음 (2026-10-18).
- Apache License 2.0 (2026-10-18).
- picasso 계약 0.10.0 픽스처와 시험 (2026-11-05).
- 조직 이전 (2026-11-10).
- 문서 속 저장소 이름 반영: 링크 글자와 본문 속 이름을 새 이름으로 바꿈 (2026-11-11).
- 빌드 이름 변경: `pyproject.toml` 패키지 이름을 `incident-narrator`로 변경, 이미 설치한 `.venv`는 옛 배포판을 지우고 다시 설치 필요 (2026-11-11).

**지금·다음**
- 프로덕션 `search_text` 의 효과를 다시 잰다. 측정 도구는 아직 옛 요청을 보내며, 기준선을 옮길지는 다음 측정 설계 문서가 정한다. [STATE.md](https://github.com/picasso-robotics/incident-narrator/blob/main/STATE.md)
- 다음 실측 때 측정 기준선을 0.10.0 세트로 옮긴다.

**보류 (재개 조건)**
- 자동 승인 자격 범위 좁히기: 이 저장소에 그것을 쓰는 소비자가 생기면 근거를 갖고 다시 묻는다.
- 진단 응답에 부분 검색 실패 싣기: 계약 버전을 올려야 하고 `incident-recovery` 쪽이 정한다.
- 파일 내보내기를 `registry` 로 옮기기: 승격 조건 셋 중 하나가 생기면.

**설계상 하지 않음** ([BOUNDARY.md](https://github.com/picasso-robotics/incident-narrator/blob/main/BOUNDARY.md))
- 상태 판정, 대안 생성, 로봇 직접 명령, 알림 심각도, 모니터링·탐지, 자동 승인 자격 결정.
- 조치를 기술하지 않는다. 승인은 제안을 가리키기만 한다.
- 운영자 질의 클라이언트(2026-09-23 일부러 제외).
- 스테이션 경로는 파일 입력·파일 출력만: 운영 UI 표시, 자원 해제, 재실행, 안전 제어 없음.
- 이웃 저장소에 쓰지 않는다. 요청은 `correspondence/` 로 보낸다.

### incident-recovery

로봇 셀의 단일 고장(에피소드)을 첫 증상부터 해결까지 추적하는 결정적 상태기계다. `:core` 는 순수 결정적 코어(상태기계, 전이 함수, 정책 표, 후보, 진단 검증), `:runtime` 은 Temporal 셸(`EpisodeWorkflow`, 액티비티, `EpisodeStore`, 감시기), `:host` 는 워커·감시기·CLI, `:api` 는 Spring Boot `/api/episodes`, `ui/` 는 Vite/React 에피소드 화면, `policy/active.yaml` 은 정책 표 v1. JDK 21. picasso 승인 엔드포인트가 루프백 전용이라 단일 머신 PoC 다. 2026-10-05 에 이전 저장소 `koshei` 에서 떼어 내 새 이력으로 시작했다.

**최근 완료**
- `koshei` 에서 분리, host·api·ui 모듈과 문서 (2026-10-05).
- 공통 용어 사전에 맞춘 문장·그림 정리, 내부 식별자 이름 바꾸기(R1 1단계) (2026-10-06).
- README 한국어판(영어판은 `README.en.md`), 번들·에피소드 예시와 그림 (2026-10-06).
- 번들 읽기와 진단 스냅숏이 picasso 내보내기 schema 6 을 받음 (2026-11-05).
- 예시를 picasso 최신 main 으로 갱신, 설계 문서와 KDoc 정정 (2026-11-05).
- Testcontainers 올림: Testcontainers 를 1.21.4 로 올려 Docker Engine 29 에서 시험이 돎 (2026-11-11).
- 이름 변경: 패키지 `dev.picasso.recovery.*`, 환경 변수 `RECOVERY_*`, 작업 큐 `incident-recovery-episode-tq`, 데이터베이스 `incident_recovery`, 헤더 `X-Recovery-Operator` 변경, 외부 계약 이름과 동작 유지, 이전 데이터베이스 옮기지 않음, 실제 Temporal과 `picasso` 참조 승인 호스트로 승인부터 결과 통보까지 다시 돌려 확인 (2026-11-11).

**지금·다음** (설계 문서 §16·§19, [2026-09-27-episode-outer-loop-design.md](https://github.com/picasso-robotics/incident-recovery/blob/main/docs/design/2026-09-27-episode-outer-loop-design.md))
- 명시된 다음 목록은 없다. 계획 C 에 남은 것: 현재 시각 기준 `revalidate`(실시간 원장 읽기 필요), 「분명히 보내지 않음」을 코어에 알리기, 드리프트 입력, DONE 의 뜻.
- 계약 이름 바꾸기는 소유자 결정으로 보류 중(R1 다음 단계).

**보류 (재개 조건)**
- 사용자 결정으로 미룬 것(2026-10-04): 정책 관리(git·DB 포인터·CLI), `SAGA_ACTION` 조치와 자식 사가, 감시기 로그 화면, API 용 읽기 전용 DB 역할, `ensureSchema` 열 검사, DISPATCH_PENDING·REVALIDATING 재생 이력, 전체 감사 필드와 품질 이력 연결(품질 시스템 결정이 먼저).
- `APPROVE_REMEDY` 자동 승인은 v1 에서 꺼져 있다. 세 조건이 모두 성립하면 사용자가 다시 정한다: 채점 사례 측정에서 깨끗한 권고가 충분히 자주 맞음, 검색 저하 상태가 진단 응답에 실리고 그때의 진단을 깨끗하다고 보지 않음, 배포 호스트와 증분 원장 읽기.
- 실시간 재검증: picasso 의 증분 원장 조회를 기다린다. 그때까지 늘 UNKNOWN.
- 실제 배포 호스트: 별도 배포 저장소에 두며 실제 현장이 생길 때 만든다.

**설계상 하지 않음** (설계 문서 §1)
- 안전 시스템, 즉시 대응 계층, 로봇 직접 명령(picasso 제안을 가리키기만 한다), picasso 호스팅과 `pump()` 실행, `reassign` 호출, 진단 내부, 세계 상태 저장, 운영자가 그리는 절차.
- LLM 은 조치를 기술하지 않는다. 거부는 기본으로 에스컬레이션한다.

### factory-runtime

picasso 라이브러리의 포트를 실제 로봇·PLC·AMR 드라이버에 배선해 신규 공장에 배포하는 실행 프로세스의 자리다. 공개 저장소이며 아직 커밋이 없다.

**보류 (재개 조건)**
- 작업은 시작하지 않았다. picasso 와 `incident-recovery` 는 둘 다 프로덕션 하드웨어 싱크를 설계상 두지 않고, `incident-recovery` 의 실제 배포 호스트는 실제 현장이 생길 때 별도 배포 저장소에 만든다고 적혀 있다.

## 결정 대기

- `incident-recovery` 설계 문서 §19 「사용자가 정할 것」:
  - A 다섯째 후보와 작업 응답을 인입 입력으로 쓸지.
  - D 카드 순서와 WITHHELD 의 비교 진단.
  - E picasso 쪽 변경 ②~④.
  - F DONE 의 뜻(조치 완료인가 작업 지시 완료인가).
- `incident-recovery` 설계 문서 §19 「기다리는 것」 가운데 사용자가 정할 것:
  - `unknowns.what` 열거값.
  - `PROPOSAL_CHANGED` 를 재진단 목록에 넣을지.
- `APPROVE_REMEDY` 자동 승인 다시 켜기: 세 조건이 성립한 뒤 사용자가 정한다(`incident-narrator` 와 `incident-recovery` 문서 양쪽에 적혀 있다).
- picasso 와 `mission-ops` 에는 소유자 결정을 기다리는 항목이 적혀 있지 않다.

## 이 문서의 갱신

각 단계를 병합할 때 이 문서를 갱신한다. 시험 개수 같은 수치는 이 문서에 쓰지 않으며 각 저장소의 CI 가 기준이다.
