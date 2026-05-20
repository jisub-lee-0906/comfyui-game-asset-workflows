0. 배경 투명화 워크플로우

1. 프롬프팅 불필요

2. 검증된 Danbooru CSV 태그 메모

이 workflow는 프롬프트를 사용하지 않습니다. 루트 `danbooru_tag.csv`는 upstream 단계에서 유용하지만, alpha 생성 단계에는 시각적으로 승인된 source image만 넣어야 합니다.

Alpha 규칙: 생성 후 실루엣과 가장자리 정리를 확인합니다. 여기서 태그를 추가해 alpha 결함을 해결하려고 하지 않습니다.

