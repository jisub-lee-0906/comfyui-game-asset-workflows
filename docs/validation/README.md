# 검증 기록 정책

이 폴더 아래의 날짜·unit 이름이 붙은 파일은 당시 실행의 역사적 증거입니다. canonical workflow가 이후 승인된 maintenance로 변경되더라도 과거 결과의 hash나 판정을 현재 값으로 덮어쓰지 않습니다.

현재 기준선은 다음 세 가지입니다.

1. `dependencies/canonical_hashes.json`
2. `python scripts/workflow_pack.py validate`
3. GitHub Actions `.github/workflows/ci.yml`

최신 실제 생성 smoke 증거는 `e2e_smoke_20260902.md`에 요약되어 있습니다.

과거 `unit1_static_inventory.json` 등의 SHA-256이 현재 canonical hash와 다를 수 있으며, 이는 그 파일을 현재 lockfile로 사용해야 한다는 뜻이 아닙니다. 새 maintenance 후에는 canonical hash lock과 CI를 갱신하고, 필요한 경우 새로운 날짜의 검증 기록을 추가합니다.

개인 PC의 절대 경로가 포함된 과거 기록은 당시 실행 환경을 설명하는 증거일 뿐 portable 설치 기본값이 아닙니다. 새 자동화 코드는 `INSTALL.md`의 환경 변수 계약을 따라야 합니다.
