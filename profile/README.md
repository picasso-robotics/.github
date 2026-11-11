<div align="center">

<img alt="picasso — Heterogeneous Robot Middleware" src="https://raw.githubusercontent.com/picasso-robotics/picasso/main/docs/assets/logo.png" width="480">

# picasso-robotics

**이기종 로봇 표준 인터페이스 계약 및 운영 변경 체계**

</div>

공장에서 휴머노이드나 4족 보행 같은 **이기종 모바일 로봇**(heterogeneous mobile robot)에 작업을 지시할 때 기종마다 할 수 있는 동작이 다르고, 응답을 받았다고 실제 작업이 끝났다고 볼 수 없으며, 로봇이나 인터페이스를 바꿀 때 기존 미션에 미칠 영향을 미리 알아야 합니다.
중심 저장소 `picasso`는 이 차이를 **표준 계약**(standard contract), **케이퍼빌리티 프로파일**(capability profile), **실행 근거**(execution evidence)로 다루는 로봇 미들웨어 PoC 입니다.
기종별 코드는 어댑터로 격리하고 공통 실행 구조를 공유합니다.
에뮬레이터 `mimic`으로 실제 하드웨어 없이 계약과 장애 상황을 시험하고, 프로파일·바인딩 변경의 영향은 `registry`에서 확인합니다.
나머지 저장소는 `picasso`를 둘러싼 운영, 설명, 복구 계층입니다.

저장소 사이의 결합은 공개 계약과 내보낸 파일로만 이루어집니다.
`picasso`의 빌드와 코드는 다른 저장소를 참조하지 않습니다.
`mission-ops`는 고정 커밋의 `picasso`를 git 서브모듈로 라이브러리처럼 씁니다.
`incident-narrator`와 `incident-recovery`는 `picasso`가 내보낸 파일인 **인시던트 번들**(incident bundle)과 **작업 응답**(`JobResponse`), 승인 엔드포인트, 진단 계약으로만 연결됩니다.
`picasso`는 `incident-narrator`를 부르지 않습니다.
공유 계약은 `picasso` 계약 버전 0.10.0, 내보내기 `schemaVersion` 6, 승인 엔드포인트 버전 4, 진단 계약 0.6입니다.

> **검증 범위**: 이 조직의 어떤 소프트웨어도 실제 로봇·PLC·상용 MES 에 연결한 적이 없습니다.
> `picasso`의 실제 어댑터 넷(Unitree G1, Boston Dynamics Spot, Agility Digit, Boston Dynamics Orbit 플릿) 중 어느 것도 실제 하드웨어에 붙여 보지 못했습니다(한계 C-3).
> 로봇은 에뮬레이터 `mimic`, 설비는 셀 대역, 상위 시스템은 로컬 Mock MES 로 대신합니다.
> 벤더 인터페이스 조사와 대역 시험은 실제 SDK 연결, 현장 성능, 산업 안전 검증을 대신하지 않습니다.

---

## 1. 저장소 구성

| 저장소 | 역할 | 라이선스 |
| :--- | :--- | :--- |
| [picasso-robotics/picasso](https://github.com/picasso-robotics/picasso) | 로봇 표준 인터페이스 계약, 케이퍼빌리티 협상, 공통 실행, 기종별 어댑터, 리비전·바인딩 변경 관리 레지스트리 | Apache-2.0 |
| [picasso-robotics/mission-ops](https://github.com/picasso-robotics/mission-ops) | 상위 시스템(MES·WMS)의 외부 작업 지시를 로봇 미션에 연결하고 작업 요청부터 실행·결과 회신까지 운영. 영속 작업 수락, 공유 자원 조정, 운영 UI | Apache-2.0 |
| [picasso-robotics/incident-narrator](https://github.com/picasso-robotics/incident-narrator) | picasso 가 이미 판정한 인시던트 번들을 읽어 원인 후보와 검증된 근거 인용을 쓰는 LLM 설명 계층. 판정하지 않으며 LLM 은 인시던트마다 한 번만 부른다. `incident-recovery` 의 진단 요청에는 계산된 후보 하나를 권하거나 에스컬레이션한다 | Apache-2.0 |
| [picasso-robotics/incident-recovery](https://github.com/picasso-robotics/incident-recovery) | 로봇 셀의 단일 고장을 첫 증상부터 해결까지 하나의 에피소드로 추적하는 결정적 상태기계. Temporal 셸 안에 순수하고 결정적인 코어를 둔다. 단일 머신 PoC | PolyForm Noncommercial 1.0.0 |
| [picasso-robotics/factory-runtime](https://github.com/picasso-robotics/factory-runtime) | picasso 라이브러리의 포트를 실제 로봇·PLC·AMR 드라이버에 배선해 신규 공장에 배포하는 실행 프로세스의 자리. 아직 커밋이 없다 | — |

저장소별 최근 완료, 다음 작업, 어떤 조건에서 무엇을 미루는지, 설계상 하지 않는 것은 [ROADMAP.md](https://github.com/picasso-robotics/.github/blob/main/ROADMAP.md)에 있습니다.
저장소들이 2026-11-10 에 이 조직으로 옮기며 이름이 바뀌었고, 각 저장소 문서는 새 이름을 쓰지만 기록과 빌드·패키지 이름, `incident-recovery` 의 프로젝트 이름(`koshchei`)에는 옛 이름이 남아 있습니다.

---

## 2. 지금까지 확인한 것

1. **기종 차이의 격리**: 표준 계약·프로파일과 기종별 어댑터를 나눕니다.
   실제 어댑터 넷이 같은 계약 위에 있고, `mimic`의 시드와 가상 클록, 결함 주입으로 장애를 시험합니다. 실제 하드웨어 연결은 아닙니다.
2. **수락·응답·실제 완료의 구분**: `picasso`는 실행 상태와 태스크 상태를 나누고 근거 등급과 효과 대조로 결과를 정합니다.
   로봇이 끝났다고 해도 설비 확인이 없으면 `UNVERIFIED`로 남기고, 셀 장치가 확인하면 물리 완료로 봅니다. 확인하지 못한 케이퍼빌리티는 `UNKNOWN`으로 남깁니다.
3. **변경 영향의 사전 확인**: 리비전·바인딩·의존 원장·변경 계획으로 프로파일이나 어댑터를 바꿀 때 영향을 봅니다.
   소비자나 진행 중 태스크가 남아 있으면 케이퍼빌리티 제거 계획의 제거 단계가 거부됩니다. 계약 검사는 CI 와 `registry`가 같은 구현을 씁니다. 한계 레지스터에 오픈 항목 50개(내부 20 · 외부 30)를 해결 조건과 함께 둡니다([한계 레지스터](https://github.com/picasso-robotics/picasso/blob/main/docs/limits.md)).
4. **운영 흐름의 로컬 검증**: `mission-ops`는 PostgreSQL, `picasso` `registry`·`mimic`, 셀 대역, 실행 호스트, 운영 API, React UI 로 된 로컬 스택에서 작업 요청부터 결과 회신까지의 흐름을 검증합니다.
   소유 관리와 설비 신호 확인은 안전 PLC 나 장비 쪽 펜싱을 대신하지 않습니다.
5. **저장소를 가로지른 실제 실행**: 분리 전 이전 저장소 `koshei`에서 실제 서비스로 두 번 실행했습니다.
   한 번은 Temporal 진단 워커와 Khala/Nexus 를 거친 진단으로, 인용 13개가 검증되었고 권고는 ESCALATE, 에피소드 결과는 ESCALATED 였습니다. 다른 한 번(2026-10-04)은 `picasso` 참조 호스트를 상대로 운영자가 조치를 승인해 `picasso`가 APPROVED 로 응답했지만, 연결된 작업 응답에 `operatorRequired`가 있어 에피소드가 UNKNOWN_OUTCOME 으로 전이했습니다. 각각 한 번의 실행이라 지연 시간, 품질, 안정성을 일반화하지 않습니다.
6. **설명과 판정의 분리**: `incident-narrator`는 별도 저장소이고 판정하지 않으며 조치를 기술하지 않습니다.
   승인은 계산된 제안을 가리키기만 하고, 승인 시도는 기본으로 꺼져 있으며 자격은 `picasso`가 정합니다. 검증된 인용이 원인 분석의 타당성까지 보장하지는 않습니다.

---

## 3. 기술 스택

- `picasso`: Kotlin, Gradle, JDK 21, 모듈 16개. 명령·조회는 gRPC, 상태·이벤트·스트리밍은 MQTT.
- `mission-ops`: Kotlin, Spring Boot, JDK 21, PostgreSQL, React/Vite UI(Node 22).
- `incident-recovery`: Kotlin, JDK 21, Temporal, Spring Boot API, Vite/React UI.
- `incident-narrator`: Python 3.11 이상, Temporal 워커, 외부 Khala/Nexus 검색·인용 검증 서비스.
- 시험: Testcontainers 와 Docker 로 PostgreSQL 같은 의존 서비스를 띄웁니다.

---

<sub>이 조직의 저장소는 이기종 로봇 운영을 위한 참조 구현 PoC 이며, 각 저장소 README 와 한계 레지스터에 검증 범위와 한계를 적습니다.</sub>
