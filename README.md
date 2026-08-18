# HA HYEMIN — Portfolio

AI · Software Engineer. 에이전트 평가, 데이터 파이프라인, 개발 하네스를 만듭니다.

**웹 포트폴리오** → [`index.html`](index.html) (단일 파일, 외부 요청 없음)

| | 프로젝트 | 내용 |
|---|---|---|
| 01 | Data Tool Harness | 자연어 요구사항으로 검수 도구를 생성·검증·배포하는 하네스 |
| 02 | Legal Agent Benchmark | 법령·판례를 직접 찾아 답하는 능력을 항목 단위로 채점하는 벤치마크 |
| 03 | Patent VQA Dataset | 특허 도면과 텍스트를 연결한 학습용 VQA 데이터 구축 |
| 04 | DayCourse | 일정 공동 편집과 사진 공유를 묶은 웹 서비스 |

## 구조

```
index.html              배포용 결과물 — 폰트·이미지·도해를 모두 내장한 단일 HTML
src/ha-editorial.html   레이아웃 · CSS · 스크립트 템플릿
src/build_editorial.py  본문 데이터 + 빌더 (폰트 서브셋·이미지 base64 내장)
src/assets/             사진, 로고, 구조도 원본
```

## 빌드

```bash
cd src && python3 build_editorial.py     # → src/dist/ha-editorial.html
```

빌드할 때 Google Fonts 에서 필요한 글자만 받아 파일에 심습니다. 결과물은 외부 요청이 없어
그대로 어디서든 열립니다.

## 연락

[GitHub](https://github.com/aehyemin) · [LinkedIn](https://www.linkedin.com/in/%ED%98%9C%EB%AF%BC-%ED%95%98-487780324) · [Blog](https://blog.naver.com/recordmyrecord)
