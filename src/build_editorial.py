#!/usr/bin/env python3
"""
ha-editorial.html 빌드.

  PAGE 1  4개 프로젝트 공통 형식.
          이름·한줄 → 배경 → PROJECT STRUCTURE(중심) → 기술
  PAGE 2  구조를 반복하지 않고, 그중 가장 신경 쓴 한 단계를 확대한다.
          문제 → 원인 → 판단 → 구현 → 결과. 라벨은 프로젝트마다 다르다.

폰트는 실제 쓰인 글자만 서브셋으로 받아 base64 내장한다. 외부 요청 0건.
출력: dist/ha-editorial.html
"""
import base64
import html
import pathlib
import re
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).parent
DIST = HERE / "dist"
DIST.mkdir(exist_ok=True)
SRC = HERE / "ha-editorial.html"
PHOTO = HERE / "assets" / "portrait.jpg"


def img_uri(fname: str) -> str:
    """프로젝트 로고 등 부가 이미지를 data URI 로 — 외부 요청 0 유지."""
    p = HERE / "assets" / fname
    ext = p.suffix.lower()
    mime = {".png": "image/png", ".svg": "image/svg+xml"}.get(ext, "image/jpeg")
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode("ascii")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# ── 대표 비주얼 ───────────────────────────────────────────────────────────
# 실제 화면 캡처가 아니라 산출물을 도면풍으로 추상화한 그래픽.
# 같은 그래픽이 WORKS 목록의 호버 프리뷰로도 쓰인다.
VISUALS = {
    "p1": (
        '<svg viewBox="0 0 320 220" role="img" aria-label="특허 도면에서 QA 쌍을 만드는 흐름">'
        '<text x="16" y="24">FIG. 1 — PATENT DRAWING</text>'
        '<rect class="fig" x="16" y="38" width="104" height="86"/>'
        '<rect class="thin" x="30" y="52" width="76" height="58"/>'
        '<path class="hatch" d="M32 108 L104 56 M32 92 L88 56 M48 108 L104 72 M32 76 L72 56 M64 108 L104 88"/>'
        '<circle class="fig" cx="68" cy="81" r="15"/>'
        '<path class="fig" d="M68 66 L68 96 M53 81 L83 81"/>'
        '<path class="thin" d="M120 81 L138 81"/>'
        '<text x="124" y="76">110</text>'
        '<text x="16" y="142">REF. 110 / 112</text>'
        '<text x="150" y="24">DESCRIPTION</text>'
        '<path class="thin" d="M150 40 L232 40 M150 52 L224 52 M150 64 L232 64 M150 76 L206 76"/>'
        '<path class="acc" d="M150 90 L232 90"/>'
        '<text x="150" y="106">GROUNDED IN FIG. ONLY</text>'
        '<path class="thin" d="M240 62 L258 62 M252 57 L258 62 L252 67"/>'
        '<text x="266" y="24">QA</text>'
        '<path class="acc" d="M266 34 L266 126 M266 34 L274 34 M266 126 L274 126"/>'
        '<text x="280" y="48">Q</text>'
        '<path class="thin" d="M292 44 L312 44 M280 58 L312 58"/>'
        '<text x="280" y="84">A</text>'
        '<path class="thin" d="M292 80 L312 80 M280 94 L306 94 M280 108 L312 108"/>'
        '<path class="thin" d="M16 168 L304 168"/>'
        '<text x="16" y="186">FIGURE → DESCRIPTION → QA PAIR</text>'
        '<text x="16" y="202" class="cap">설명문을 중간 표현으로 두어 검증 가능하게 한다</text>'
        '</svg>'
    ),
    "p2": (
        '<svg viewBox="0 0 320 220" role="img" aria-label="에이전트가 법령을 검색해 근거를 모으는 흐름">'
        '<text x="16" y="24">QUESTION</text>'
        '<circle class="fig" cx="34" cy="86" r="13"/>'
        '<text x="16" y="122">AGENT</text>'
        '<path class="thin" d="M47 86 L110 52 M47 86 L110 86 M47 86 L110 120"/>'
        '<circle class="thin" cx="120" cy="52" r="10"/><text x="136" y="48">SEARCH</text>'
        '<circle class="thin" cx="120" cy="86" r="10"/><text x="136" y="82">READ</text>'
        '<circle class="thin" cx="120" cy="120" r="10"/><text x="136" y="116">RETRIEVE</text>'
        '<text x="198" y="28">§ STATUTE</text>'
        '<rect class="thin" x="198" y="34" width="46" height="34"/>'
        '<path class="thin" d="M204 44 L238 44 M204 52 L232 52 M204 60 L238 60"/>'
        '<path class="thin" d="M130 52 L196 50 M130 86 L242 74 M130 120 L242 88"/>'
        '<path class="acc" d="M258 62 L258 128 M258 62 L266 62 M258 128 L266 128"/>'
        '<text x="272" y="80">EVIDENCE</text>'
        '<path class="thin" d="M272 90 L312 90 M272 102 L304 102 M272 114 L312 114"/>'
        '<text x="16" y="148">RUBRIC 1,405</text>'
        '<path class="acc" d="M86 141 L86 151 M94 141 L94 151 M102 141 L102 151'
        ' M110 141 L110 151 M118 141 L118 151"/>'
        '<text x="132" y="148">LLM JUDGE</text>'
        '<path class="thin" d="M198 144 L246 144"/>'
        '<text x="252" y="148">SCORE</text>'
        '<path class="thin" d="M16 168 L304 168"/>'
        '<text x="16" y="186">SEARCH → EVIDENCE → ANSWER → JUDGE</text>'
        '<text x="16" y="202" class="cap">답변이 아니라 도구를 쓰는 궤적까지 채점한다</text>'
        '</svg>'
    ),
    "p3": (
        '<svg viewBox="0 0 320 220" role="img" aria-label="요구사항에서 배포까지 자동 검사가 걸린 파이프라인">'
        '<text x="16" y="24">REQUIREMENT</text>'
        '<rect class="thin" x="16" y="32" width="42" height="30"/>'
        '<path class="thin" d="M22 42 L52 42 M22 52 L46 52"/>'
        '<path class="fig" d="M16 100 L304 100"/>'
        '<rect class="thin" x="70" y="88" width="24" height="24"/>'
        '<rect class="thin" x="110" y="88" width="24" height="24"/>'
        '<text x="70" y="128">GENERATE</text>'
        '<text x="152" y="80">AUTOMATED CHECKS ×8</text>'
        '<path class="acc" d="M152 86 L152 114 M160 86 L160 114 M168 86 L168 114 M176 86 L176 114'
        ' M184 86 L184 114 M192 86 L192 114 M200 86 L200 114 M208 86 L208 114"/>'
        '<rect class="acc" x="238" y="88" width="24" height="24"/>'
        '<path class="acc" d="M244 100 L248 106 L257 92"/>'
        '<text x="238" y="128">DEPLOY</text>'
        '<text x="152" y="130">FAIL → STOP</text>'
        '<path class="acc" d="M250 116 L250 146 L38 146 L38 118"/>'
        '<path class="acc" d="M34 124 L38 116 L42 124"/>'
        '<text x="96" y="160">HUMAN REVIEW — 담당자 실사용 피드백</text>'
        '<path class="thin" d="M16 172 L304 172"/>'
        '<text x="16" y="190">REQUIREMENT → CHECK → DEPLOY → REVIEW</text>'
        '<text x="16" y="206" class="cap">규칙은 배포 게이트로, 피드백은 요구사항으로 되돌린다</text>'
        '</svg>'
    ),
    "p4": (
        '<svg viewBox="0 0 320 220" role="img" aria-label="두 사용자가 같은 일정을 동시에 편집하는 화면">'
        '<text x="16" y="24">USER A</text>'
        '<rect class="fig" x="16" y="32" width="112" height="106"/>'
        '<path class="thin" d="M16 48 L128 48"/>'
        '<path class="thin" d="M28 66 L46 66 M28 92 L46 92 M28 118 L46 118"/>'
        '<rect class="acc" x="56" y="58" width="60" height="18"/>'
        '<path class="thin" d="M56 86 L116 86 M56 112 L116 112"/>'
        '<text x="150" y="80">WS</text>'
        '<path class="acc" d="M146 92 L174 92"/>'
        '<circle class="accf" cx="160" cy="92" r="3"/>'
        '<text x="146" y="112">SYNCED</text>'
        '<text x="192" y="24">USER B</text>'
        '<rect class="fig" x="192" y="32" width="112" height="106"/>'
        '<path class="thin" d="M192 48 L304 48"/>'
        '<path class="thin" d="M204 66 L222 66 M204 92 L222 92 M204 118 L222 118"/>'
        '<rect class="acc" x="232" y="58" width="60" height="18"/>'
        '<path class="thin" d="M232 86 L292 86 M232 112 L292 112"/>'
        '<path class="thin" d="M16 168 L304 168"/>'
        '<text x="16" y="186">SHARED ITINERARY — REALTIME</text>'
        '<text x="16" y="202" class="cap">소켓 소유권을 컴포넌트 밖으로 옮긴 뒤</text>'
        '</svg>'
    ),
}

# ── 프로젝트 데이터 ───────────────────────────────────────────────────────
#   focus : PROJECT STRUCTURE 5단계 중 PAGE 2 가 확대하는 단계
PROJECTS = [
    {
        # 하네스를 첫 프로젝트로 — 협업 범위와 성과가 가장 뚜렷하다
        "id": "p1", "vis": "p3", "no": "01", "pc": "#7657FF", "pct": "#7657FF",
        "kick": "01 / FEATURED PROJECT",
        "name": ["Data", "Tool", "Harness"],
        "lead": "내부 배포 플랫폼을 몰라도, 자연어만으로 검수 도구를 만들고 "
                "배포와 권한 설정까지 할 수 있는 하네스입니다.",
        "background": [
            "데이터 검수 도구를 개발하면서 기능 구현보다 배포, 인증, 권한, "
            "외부 연동에 더 많은 시간이 들었습니다.",
            "도구마다 같은 병목이 반복됐고, 그 과정을 규칙으로 고정해 "
            "자동화하는 하네스를 개발했습니다.",
        ],
        "vis_svg": "dth-arch.svg", "arch": True,
        "pipe": [
            ("01", "요구사항 정의", "데이터 구축 담당자"),
            ("02", "도구 생성", "SCREEN + API"),
            ("03", "로컬 검증", "RUN & REVIEW"),
            ("04", "자동 검사", "8 GATES"),
            ("05", "배포 · 인증", "SSO / ACCESS"),
        ],
        "loop": "자연어로 요구사항을 정의하면, 하네스가 자동으로 도구를 생성해 사용자가 로컬에서 확인한 뒤, 검증하고 배포합니다.",
        "focus": "04",
        "_role": ["Harness Architecture", "Generation Spec",
                  "Verification Gates", "Deployment Automation"],
        "tech": ["Python", "FastAPI", "MySQL", "Docker", "Kubernetes"],

        "note_title": ["반복되는 배포 오류를", "자동 검증으로 전환"],
        "challenge": [
            "개발자와 비개발자가 오랜 기간 협업 필요",
            "담당자가 바뀌면 다음 도구 개발에서도 같은 문제 발생",
        ],
        "cause": [
            "외부 프록시 규격 충족과 내부 배포 플랫폼 사용의 어려움",
            "규칙이 사람의 기억에 의존",
        ],
        "fix": [
            "요구사항 정의 → 로컬 확인 → 배포 전 규칙 검사 → 배포 과정으로 고정",
            "<b>비개발자 분들과 직접 하네스를 쓰며 점진적으로 수정</b>",
        ],
        "decision": [
            ("out", "문서를 더 자세히 쓴다 — 이미 적어뒀는데도 반복됐음"),
            ("out", "검사 스크립트를 제공한다 — 실행해야 작동하므로 같은 문제"),
            ("pick", "규칙을 <b>배포 파이프라인 안으로</b> 옮김 — 생략할 수 있는 단계를 없앰"),
        ],
        "impl": [
            ("01", "Incident<br>log",
             "사고가 나면 원인을 먼저 기록합니다."),
            ("02", "Rule<br>contract",
             "기록된 원인을 규칙으로 고정합니다."),
            ("03", "Deploy<br>gate",
             "규칙을 자동 검사로 바꿔 배포 명령에 겁니다."),
        ],
        "res_lead": "자연어 요구사항 하나로 도구 생성부터 DB 연결, "
                    "내부 플랫폼 배포, 외부 인증 규격 충족까지 연결",
        "result": [("2~3주 → 3일", "검수 도구 1개 제작 기간", True),
                   ("2~3명 → 1명", "비개발자+개발자 협업 → 혼자 완결", True)],
    },
    {
        "id": "p2", "vis_svg": "lab-flow-h.svg", "wide_vis": True, "vis": "p2", "no": "02", "pc": "#FF5C9D", "pct": "#D6316F",
        "kick": "02 / PROJECT",
        "name": ["Legal", "Agent", "Benchmark"],
        "lead": "에이전트가 법령·판례를 직접 검색하고 근거 기반 답변을 생성하는지 "
                "평가하는 벤치마크입니다.",
        "background": "객관식 정답 여부만으로는 에이전트가 적절한 법적 근거를 찾고 "
                      "이를 바탕으로 추론하는 능력을 평가하기 어렵습니다.",
        "pipe": [
            ("01", "질의 선별", "GOLD SET"),
            ("02", "에이전트 실행", "TOOL-USE"),
            ("03", "검색 · 열람 · 추출", "LAW / CASE API"),
            ("04", "근거 채점", "RUBRIC"),
            ("05", "결과 분석", ""),
        ],
        "focus": "03",
        "_role": ["Benchmark Design", "Agent Pipeline",
                  "Rubric Design", "Model Evaluation"],
        "tech": ["Python", "LLM API", "Retrieval API", "LLM-as-Judge", "pytest"],

        "note_title": ["결론뿐 아니라", "근거와 과정까지 채점"],
        "labels": {"chal": "01 DATASET - 쟁점 기준 채점표",
                   "cause": "02 AGENTS - 질문만 주고 스스로 탐색",
                   "fix": "03 EVAL - 답의 점수와 근거의 진위를 따로 채점"},
        "challenge": [
            "실제 이용자의 법률상담 질문과, AI 가 쓰고 변호사가 검토·수정한 "
            "답변을 정답지로 사용",
            "정답지를 쟁점별로 묶어 채점표 생성 — <b>쟁점 · 법리 · 적용 · "
            "결론(IRAC) 항목마다 따로 채점</b> (총 1,271개 항목)",
        ],
        "cause": [
            "<u>정답도, 참고할 법령 목록도 주지 않음</u>"
            "(무엇을 찾을지부터 스스로 판단)",
            "도구 5종, 최대 30턴(법령·판례 검색, 문서 열람, 정보 추출, 답변 제출)",
            "검색 도구를 준 조건과 주지 않은 조건을 같은 환경에서 실행",
        ],
        "fix": [
            "채점표 항목마다 <b>맞으면 1, 아니면 0</b>",
            "답변이 인용한 조문·판례 <b>9,878건</b>을 공식 API 로 직접 조회해 "
            "실제로 있는지, 내용이 맞는지 확인",
            "인용 정확도는 점수에 섞지 않고 따로 보고",
        ],
        "res_lead": [
            "검색 도구를 주면 4개 모델 모두 답변 품질 상승"
            "(<b>0.744 → 0.794</b>, 두 조건 모두 답한 579문항 기준)",
            "가장 크게 오른 항목은 법리(<b>+0.087</b>), 결론(+0.027)의 3배 "
            "→ 결론보다 근거에서 차이가 남",
            "인용한 판례가 실제로 맞는 비율 <b>71% → 86%</b>, "
            "핵심 근거가 틀린 답변 <b>33% → 17%</b>",
            "인용 오류는 <u>없는 판례를 지어낸 경우가 아니라(5.6%)</u>, 실제 있는 "
            "조문·판례에 없는 내용을 갖다 붙인 것 → 번호만 대조해서는 안 걸러짐",
            "도구를 다루는 솜씨가 점수를 가름 → 검색해도 결과가 0건인 비율이 "
            "모델별 24~50%. 잘하는 모델은 0건이면 검색어를 바로 줄이고, "
            "못하는 모델은 같은 검색을 반복하다 턴을 다 씀",
        ],
        "limits": [
            "gemma 는 11문항에서 30턴을 다 쓰고 답을 못 냄(완주율 0.93). "
            "미답변을 0점으로 세면 −0.015 → 답이 나빠서가 아니라 끝까지 못 간 "
            "것이라, 점수는 완주율과 같이 봐야 함",
            "채점도 인용 판정도 LLM 이 함(사람 채점과 일치도 검증)",
            "정답지가 기준이라, 정답지보다 더 나은 답변은 가려내지 못함",
        ],

        "decision": [
            ("out", "예외만 던지게 수정 — 실패는 잡히지만 이유가 남지 않음"),
            ("out", "로그 플래그를 신뢰 — 이번 결함이 그 플래그를 속였음"),
            ("pick", "<b>본문이 모델에 닿는 경로를 하나로 제한</b>하고 그 경로를 측정 대상으로 삼음"),
        ],
        "impl": [
            ("01", "Storage<br>normalization",
             "저장 형식을 문자열로 정규화했습니다."),
            ("02", "Reference<br>enforcement",
             "참조 키가 없는 추출 호출은 거부합니다."),
            ("03", "Citation<br>audit",
             "없는 인용 3건 vs 어긋난 인용 98건 — 기억으로 답한 흔적."),
        ],
        "result": [],
    },
    {
        "id": "p3", "vis": "p1", "vis_svg": "pvqa-flow.svg",
        "arch": True, "no": "03", "pc": "#315CFF", "pct": "#315CFF",
        "kick": "03 / PROJECT",
        "name": ["Patent", "VQA", "Dataset"],
        "lead": "특허 도면과 본문을 연결해, 도면을 봐야 답할 수 있는 VQA 데이터를 구축했습니다.",
        "background": "모델의 도면 이해를 위한 Vision Understanding QA 데이터를 "
                      "특허 문서에서 합성했습니다.",
        "pipe": [
            ("01", "설명문 + QA 생성", "GEN"),
            ("02", "설명문 검증", "CTX JUDGE"),
            ("03", "QA 검증", "QA JUDGE"),
            ("04", "FINAL", "SFT DATASET", "acid"),
        ],
        # 02 에서 떨어지면 01 로 되돌아간다 — 스트립 아래 되돌림 화살표로 표시
        "retry": (2, "검증 실패 시 다시 생성"),
        "cmp": {
            "hd": "이미지 → QA 를 바로 생성하지 않은 이유",
            "a": "이미지 → QA 직접 생성",
            "b": "설명문을 중간 표현으로",
            "rows": [
                ("검증 근거",
                 "판정할 때마다 이미지를 다시 봐야 함 - <u>Vision 호출 비용, 판정자도 오독</u>",
                 "\u201c부품 A 는 은색?\u201d → 매번 이미지에서 확인",
                 "설명문이 근거 문서 - <b>텍스트끼리 대조해 자동 검증</b>",
                 "설명문에 \u201c부품 A 는 은색\u201d → 답이 설명문에 있나 자동 판정"),
                ("QA 일관성",
                 "호출마다 이미지 해석이 흔들려 <u>같은 도면 QA 끼리 모순</u>",
                 "QA1 \u201c부품 A 는 좌측\u201d · QA2 \u201c부품 A 는 하단\u201d",
                 "모든 QA 가 <b>같은 설명문에서 파생</b>돼 표현이 통일됨",
                 "설명문 \u201c부품 A 는 좌측 하단\u201d → 모든 QA 가 이 표현을 따름"),
                ("복구 방식",
                 "QA 를 하나씩 재생성 - <u>같은 원인을 여러 번 만남</u>",
                 "20개 QA 실패 → vision 재호출 20회",
                 "설명문 하나를 고치면 <b>파생 QA 세트가 함께 갱신</b>",
                 "설명문 1회 재작성 → 파생 QA 전체 자동 갱신"),
            ],
        },
        "focus": "03",
        "_role": ["Data Pipeline", "Synthetic Data Generation",
                  "Evaluation Design", "Quality Validation"],
        "tech": ["Python", "LLM", "FastAPI", "Pandas", "Docker"],

        "note_title": ["QA 판정 기준의", "grounding 오류"],
        "rubric": {
            "lead": "합성 샘플 중간 확인 결과, 판정 기준이 명백한 모순만 검출하고 "
                    "자료에 근거 없이 추측한 답변은 통과시켜 grounding 오류 발견",
            "bullets": [
                "SFT에서 모델에게 <b>환각을 정답으로 학습</b>시키는 패턴은 "
                "단순 노이즈로 감안하기 어려움",
                "특허 도면 VQA는 <b>grounding 이 과제의 본질</b>이므로 "
                "이 오류는 critical 에 가까운 문제",
            ],
            "before": {
                "hd": "BEFORE · 기존 QA 판정 기준",
                "q": "Q3. 사실 일치",
                "d": "답변이 자료와 명백히 모순되지 않는가. 매핑이나 관계가 정면 "
                     "충돌하거나, 자료에 없는 결함이나 인과를 단정 추가하면 No.",
            },
            "after": {
                "hd": "AFTER · 개선된 QA 판정 기준",
                "q": "Q3. 사실 일치",
                "d": "기존 조건에 더해, 아래 3항목 중 하나라도 추정이나 단정이 있으면 No.",
                "plus": [
                    "답변이 자료에 명시되거나 직접 확인 가능한 내용만으로 구성되는가",
                    "구조의 기능이나 의도, 목적을 단정하지 않는가",
                    "정량 표현이나 비교 기준이 자료에 근거를 두는가",
                ],
            },
            "cap": "재필터링 필요 논의 후, 루브릭의 grounding 축을 강화해 QA Judge "
                   "프롬프트를 개선하고 전체 데이터셋을 다시 판정",
            "metrics": [
                ("근거 부재 검출량", "×10", "기존 대비 약 10배 증가", True),
                ("놓쳤던 오류 검출률", "100%",
                 "기존 기준이 통과시켰지만 사람이 오류로 판정한 QA를 "
                 "10라운드 반복 실험에서 모두 검출", False),
                ("최종 학습 데이터", "40.3만 QA",
                 "원본 도면 587만 장 중 1.6%를 선별해 "
                 "특허 3.2만 건 · 도면 9.5만 장에서 합성", False),
            ],
        },
        "challenge": [
            "통과율 <b>97.85%</b> — 높다는 것 자체가 기준이 느슨하다는 신호였음",
        ],
        "cause": [
            "기존 기준은 <b>명백한 모순</b>만 걸렀음",
            "근거 없는 단정도 통과 — 학습에 쓰면 환각을 정답으로 가르치게 됨",
        ],
        "fix": [
            "판정 질문을 “모순이 없는가”에서 <b>“근거가 있는가”</b>로.",
            "같은 문항 25개를 <b>10라운드 반복</b>해 검증.",
        ],
        "decision": [
            ("out", "이미지에서 QA를 바로 생성 — 되돌릴 단위가 없음"),
            ("out", "전량 사람 검수 — 49만 건 규모에서 불가능"),
            ("pick", "판정 질문을 <b>“모순이 없는가”에서 “근거가 있는가”로</b> 바꿈"),
        ],
        "impl": [
            ("01", "Criterion<br>rewrite",
             "확인 가능한가 · 의도를 단정하지 않는가 · 정량 표현에 근거가 있는가"),
            ("02", "Repeat<br>10 rounds",
             "같은 문항 25개를 10라운드 반복 — 흔들림과 실제 개선을 가릅니다."),
            ("03", "Human<br>recheck",
             "새로 탈락한 항목 중 2건은 정답 라벨이 틀린 것으로 정정했습니다."),
        ],
        "result": [("0/40 → 40/40", "근거 부재 검출 · 25문항×10라운드", True),
                   ("2.15% → 20.48%", "전량 재판정 탈락률", False),
                   ("496K → 403K", "근거 없는 QA 18.7% 제외", False),
                   ("8.3%", "전체 대비 재판정 비용", False)],
    },
    {
        "id": "p4", "vis": "p4", "no": "04", "pc": "#93CDB6", "pct": "#2E8B68",
        "kick": "04 / PROJECT",
        "name": ["DayCourse"],
        "logo": "daycourse-logo.png",
        "shots": True,    # 개요 = 실제 화면 3컷
        "sock": True,     # 핵심 기여 = 소켓 구조 + 동기화 데모
        "lead": "약속의 시작부터 추억까지 — 일정을 함께 계획하고 사진까지 공유하는 "
                "웹 서비스입니다.",
        "background": "크래프톤 정글 6기 '나만의 무기 만들기'. 일정 관리와 사진 공유 "
                      "기능을 통합한 애플리케이션을 한 달 안에 기획부터 개발까지 완료했습니다.",
        "pipe": [
            ("01", "기획", "4인 / 1개월"),
            ("02", "UI 설계", "일정 · 지도"),
            ("03", "추천 연동", "지역 · 장소 · 코스"),
            ("04", "실시간 협업", "WEBSOCKET"),
            ("05", "배포", "EC2 / ACTIONS"),
        ],
        "focus": "04",
        "_role": ["UI / UX Design", "Frontend", "Realtime Cursor", "Drag & Drop"],
        "tech": ["React", "socket.io", "Express.js", "MySQL", "AWS S3 · EC2"],

        "note_title": ["WebSocket", "연결 구조 개선"],
        "challenge": [
            "기능별로 소켓을 따로 만들어 <b>연결 충돌</b>",
            "사람이 많을수록 화면이 느려지는 구조",
        ],
        "cause": [
            "소켓 lifecycle이 기능마다 분리돼 연결 중복",
            "마우스 위치는 발생 빈도가 곧 전송 빈도, 접속자 수만큼 증가",
        ],
        "fix": [
            "연결을 합치고 <b>이벤트 종류로 분기</b>",
            "마우스 위치에 <b>초당 80회 상한</b>",
        ],
        "decision": [
            ("out", "수신 측에서 중복을 걸러낸다 — 증상만 가림"),
            ("out", "기능마다 해제 로직을 넣는다 — 같은 실수가 반복"),
            ("pick", "<b>누가 연결을 소유하는가</b>와 <b>얼마나 자주 보내는가</b>의 문제로 봄"),
        ],
        "impl": [
            ("01", "Single<br>connection",
             "소켓 초기화 방식을 통합해 하나의 연결만 유지합니다."),
            ("02", "Event<br>routing",
             "이벤트 종류로 구분해 처리합니다."),
            ("03", "Rate<br>limit",
             "마우스 위치 전송을 초당 80회로 제한합니다."),
        ],
        "result": [("3 → 1", "소켓 연결 수", True),
                   ("80회 / 초", "마우스 위치 전송 상한", False),
                   ("3", "한 화면에서 동시 동작하는 실시간 기능", False)],
    },
]

# 딥다이브 블록 이름 — 4개 프로젝트 공통
LABELS = {"chal": "문제점", "cause": "원인", "fix": "해결 과정", "res": "성과"}
for _p in PROJECTS:
    _p["labels"] = {**LABELS, **_p.get("labels", {})}


# ── DayCourse — 대표 비주얼 자리에 들어가는 실시간 동기화 데모 ────────────
SHOTS = """<div class="shots rv">
        <figure class="sh">
          <img src="{{IMG:dc-region.jpg}}" alt="출발지들을 입력하면 중간 지점 주변 지역을 추천하는 화면">
          <figcaption><span class="m n">01</span><b>지역 추천</b>
            <span class="m d">출발지들의 중간 지점을 대중교통 소요시간으로 계산해 추천</span></figcaption>
        </figure>
        <figure class="sh">
          <img src="{{IMG:dc-plan.jpg}}" alt="여러 사용자가 같은 일정과 장소 목록을 함께 편집하는 화면">
          <figcaption><span class="m n">02</span><b>일정 동시 편집</b>
            <span class="m d">접속한 사람이 같은 화면에서 장소를 고르고 코스를 조율</span></figcaption>
        </figure>
        <figure class="sh">
          <img src="{{IMG:dc-album.jpg}}" alt="공유 앨범에서 사진이 키워드별로 분류된 화면">
          <figcaption><span class="m n">03</span><b>공유 앨범</b>
            <span class="m d">모임 사진을 모아 키워드별로 자동 분류</span></figcaption>
        </figure>
      </div>"""

SYNC_DEMO = """<div id="syncDemo">
        <div id="syRow">
          <div class="sy" data-side="a">
            <p class="m hd"><span class="dt" aria-hidden="true"></span>USER A<span class="rl">EDITING</span></p>
            <div class="rows">
              <div class="rw3"><span class="t">09:00</span><span class="ph"></span></div>
              <div class="rw3"><span class="t">11:00</span><span class="ph"></span></div>
              <div class="rw3"><span class="t">14:00</span><span class="ph"></span></div>
              <div class="cur" id="curA" aria-hidden="true"><span class="ar"></span><span class="nm">USER&nbsp;B</span></div>
              <button class="cd" id="syA"
                aria-label="USER A 일정 카드 — 드래그하거나 위아래 방향키로 시간대를 옮깁니다">
                <span class="gr" aria-hidden="true"></span>성수 카페<span class="tm" id="syTmA">09:00</span></button>
            </div>
          </div>
          <div id="syWire" aria-hidden="true">
            <span class="m">WS</span>
            <div class="wire"><i id="syDot"></i></div>
            <span class="m" id="syTag">SYNCED</span>
          </div>
          <div class="sy" data-side="b">
            <p class="m hd"><span class="dt" aria-hidden="true"></span>USER B<span class="rl">EDITING</span></p>
            <div class="rows">
              <div class="rw3"><span class="t">09:00</span><span class="ph"></span></div>
              <div class="rw3"><span class="t">11:00</span><span class="ph"></span></div>
              <div class="rw3"><span class="t">14:00</span><span class="ph"></span></div>
              <div class="cur" id="curB" aria-hidden="true"><span class="ar"></span><span class="nm">USER&nbsp;A</span></div>
              <button class="cd" id="syB"
                aria-label="USER B 일정 카드 — 드래그하거나 위아래 방향키로 시간대를 옮깁니다">
                <span class="gr" aria-hidden="true"></span>성수 카페<span class="tm" id="syTmB">09:00</span></button>
            </div>
          </div>
          <div class="sy chat">
            <p class="m hd"><span class="dt" aria-hidden="true"></span>CHAT<span class="rl">SHARED</span></p>
            <div class="log" id="syLog" aria-live="polite">
              <p class="ms a"><b>A</b>성수 카페 11시 어때?</p>
              <p class="ms b"><b>B</b>좋아, 그 시간으로 옮길게</p>
            </div>
            <form class="in" id="syForm" autocomplete="off">
              <button class="who" type="button" id="syWho"
                aria-label="보내는 사람 전환 — 지금은 A">A</button>
              <input id="syMsg" maxlength="40" placeholder="메시지를 입력해 보세요"
                aria-label="채팅 메시지">
              <button class="send" type="submit" aria-label="보내기">&#8629;</button>
            </form>
          </div>
        </div>
      </div>"""

SYNC_CAP = """<p class="m" id="syCap">실제 서비스 화면이 아니라 당시 구현한
        드래그·동기화 기능을 재현한 것입니다 · 예시 데이터</p>"""

# ── 소켓 구조 BEFORE / AFTER — 해결 과정 · 구현 위에 놓인다 ───────────────
SOCKET_DIAGRAM = """<div class="sockd rv">
              <div class="sd b">
                <p class="m hd">BEFORE</p>
                <div class="row"><span>일정 편집</span><span>마우스 위치</span><span>채팅</span></div>
                <div class="ln"><span>&#8595;</span><span>&#8595;</span><span>&#8595;</span></div>
                <div class="row s"><span>Socket</span><span>Socket</span><span>Socket</span></div>
              </div>
              <div class="sd a">
                <p class="m hd">AFTER</p>
                <div class="row s one"><span>Single Socket &middot; event type 로 분기</span></div>
                <div class="ln"><span>&#8595;</span><span>&#8595;</span><span>&#8595;</span></div>
                <div class="row"><span>일정 편집</span><span>마우스 위치</span><span>채팅</span></div>
              </div>
            </div>"""


def esc(t: str) -> str:
    return html.escape(t, quote=False)


def rich(t: str) -> str:
    """<b> 애시드 강조, <u> 주황 강조만 허용하는 가벼운 마크업."""
    t = html.escape(t, quote=False)
    for tag in ("b", "u"):
        t = t.replace(f"&lt;{tag}&gt;", f"<{tag}>").replace(f"&lt;/{tag}&gt;", f"</{tag}>")
    return t


def project_html(p: dict) -> str:
    L = p["labels"]
    style = f'style="--pc:{p["pc"]};--pct:{p["pct"]}"'
    full = " ".join(p["name"]).upper()
    focus = next(s for s in p["pipe"] if s[0] == p["focus"])

    # 프로젝트 이름은 한 줄로 — 단어마다 줄을 바꾸지 않는다
    name = f'<span class="cl"><span>{esc(" ".join(p["name"]))}</span></span>'
    logo = (f'<img class="pjLogo rv" src="{{{{IMG:{p["logo"]}}}}}" '
            f'alt="{esc(full)} 로고">' if p.get("logo") else "")
    def step_li(row):
        n, t, sub = row[0], row[1], row[2]
        tone = row[3] if len(row) > 3 else ""
        cls = "fs" + (" fc" if n == p["focus"] else "") + (f" {tone}" if tone else "")
        return (f'<li class="{cls}"><span class="n">{n}</span>'
                f'<span class="t kr">{esc(t)}</span><span class="s">{esc(sub)}</span></li>')
    steps = "".join(step_li(row) for row in p["pipe"])
    if p.get("retry"):
        # frm 단계에서 떨어지면 01 로 되돌아간다 — 두 눈금 사이를 U 자로 잇는다
        frm, note = p["retry"]
        steps += (f'<li class="fs rtn" data-from="{frm}">'
                  f'<span class="path"><span class="tx">{esc(note)}</span></span></li>')
    tech = " / ".join(esc(t) for t in p["tech"])

    note_title_plain = "<br>".join(esc(w) for w in p["note_title"])

    def bullets(items, cls=""):
        li = "".join(f'<li class="kr">{rich(t)}</li>' for t in items)
        return f'<ul class="bl{cls}">{li}</ul>'

    def lbl_html(text):
        """'01 DATASET - 쟁점 기준 채점표' → 칩 + 부제"""
        if " - " not in text:
            return esc(text)
        head, tail = text.split(" - ", 1)
        num, _, rest = head.partition(" ")
        return (f'<b><em>{esc(num)}</em> {esc(rest)}</b>'
                f'<i class="kr">{esc(tail)}</i>')

    chal_html = bullets(p["challenge"], " is")
    cause_html = bullets(p["cause"])
    fix_html = bullets(p["fix"])
    bg = p["background"]
    bg_html = (f'<ul class="bl bg kr">'
               + "".join(f"<li>{rich(t)}</li>" for t in bg) + "</ul>"
               if isinstance(bg, list)
               else f'<p class="txt kr">{esc(bg).replace(chr(10), "<br>")}</p>')
    cmp_html = ""
    if p.get("cmp"):
        C = p["cmp"]
        def cell(cls, txt, ex):
            return (f'<td class="{cls}">{rich(txt)}'
                    f'<span class="ex"><i>예</i>{rich(ex)}</span></td>')
        rows = "".join(
            f'<tr><th scope="row">{esc(k)}</th>'
            + cell("a", a, ax) + cell("b", b, bx) + '</tr>'
            for k, a, ax, b, bx in C["rows"])
        cmp_html = (f'<details class="cmpBlk rv"><summary>'
                    f'<span class="m k">{esc(C["hd"])}</span>'
                    f'<span class="more m">비교 보기</span></summary>'
                    f'<table class="cmp"><thead><tr>'
                    f'<td class="hd"></td>'
                    f'<th scope="col"><b>METHOD A</b><i>{esc(C["a"])}</i></th>'
                    f'<th scope="col" class="pick"><b>METHOD B · 적용</b>'
                    f'<i>{esc(C["b"])}</i></th></tr></thead>'
                    f'<tbody>{rows}</tbody></table></details>')

    rs = "".join(f'<li class="kr">{rich(t)}</li>' for t in p.get("reasons", []))
    reasons_html = (f'<div class="whyBlk rv"><p class="m k lbl">'
                    f'{esc(p["reasons_hd"])}</p><ul class="why">{rs}</ul></div>'
                    if p.get("reasons") else "")
    loop_html = (f'<p class="loopr"><span class="lp" aria-hidden="true">&#8594;</span>'
                 f'<span class="kr">{rich(p["loop"])}</span></p>'
                 if p.get("loop") else "")
    # 대표 비주얼: 정지 도면 대신 살아 있는 데모를 쓰는 프로젝트가 있다
    wide = p.get("shots") is True       # 실제 화면 3컷을 가로로 쓰는 프로젝트
    arch = p.get("arch") is True        # 구조도를 가로 전체로 펼치는 프로젝트
    noflow = p.get("noflow") is True    # 세로로 긴 구조도 — 단계 스트립 없이 크게
    wide_vis = p.get("wide_vis") is True  # 도면 칸을 넓게 쓰는 프로젝트
    portrait = p.get("vis_portrait") is True  # 세로로 긴 도면
    hero_cls = (" solo" if wide or arch else
                (" tv pv" if portrait else " tv") if noflow or wide_vis else "")
    intro_cls = " two" if arch else ""
    vis_ratio = ""
    if p.get("vis_svg"):
        vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"',
                       (HERE / "assets" / p["vis_svg"]).read_text(encoding="utf-8"))
        if vb:
            vis_ratio = f' style="aspect-ratio:{vb.group(1)}/{vb.group(2)}"'
    vis_inner = (
        import_svg(p["vis_svg"]) if p.get("vis_svg")
        else f'<img class="visImg" src="{{{{IMG:{p["vis_img"]}}}}}" '
             f'alt="{esc(full)} 구조도">' if p.get("vis_img")
        else VISUALS[p.get("vis", p["id"])])
    vis_html = "" if wide or arch else (
        f'<figure class="pjVis rv"{vis_ratio}><div class="fr">{vis_inner}</div></figure>')
    arch_html = f"""<div class="archBlk bare rv">
        <div class="archFig">{vis_inner}</div>
      </div>

      {cmp_html}""" if arch and p.get("cmp") else f"""<div class="archBlk rv">
        <div class="flowHd">
          <span class="m k">PROJECT STRUCTURE</span>
          <span class="m">{esc(full)}</span>
        </div>
        <div class="archFig">{vis_inner}</div>
        {loop_html}
      </div>""" if arch else ""
    struct_html = SHOTS if wide else arch_html if arch else "" if noflow else f"""<div class="flowBlk">
        <div class="flowHd">
          <span class="m k">PROJECT STRUCTURE</span>
          <span class="m">{esc(full)}</span>
        </div>
        <ol class="flow" style="--cols:{len(p['pipe'])}">{steps}</ol>
        {loop_html}
      </div>

      {reasons_html}"""
    fig_html = (f'<div class="ntFig rv">{SOCKET_DIAGRAM}</div>'
                f'<div class="pjWide rv">{SYNC_DEMO}</div>'
                f'{SYNC_CAP}') if p.get("sock") else ""
    res = "".join(
        f'<div class="rc{" hot" if hot else ""}"><div class="v">{esc(v)}</div>'
        f'<div class="lb">{esc(l)}</div></div>'
        for v, l, hot in p["result"])
    # 데모가 들어간 화면은 그 자체가 근거라 수치 줄을 따로 두지 않는다
    rl = p.get("res_lead")
    if isinstance(rl, list):
        res_lead = ('<ul class="bl rl kr">'
                    + "".join(f"<li>{rich(t)}</li>" for t in rl) + "</ul>")
    else:
        res_lead = f'<p class="resLead kr">{rich(rl)}</p>' if rl else ""
    # 루브릭을 고쳐 쓴 프로젝트 — 노트 본문을 BEFORE/AFTER 판정 기준 비교로 짠다
    rb_html = ""
    if p.get("rubric"):
        R = p["rubric"]
        rb_bul = "".join(f'<li class="kr">{rich(t)}</li>' for t in R["bullets"])
        plus = "".join(f'<li class="kr">{esc(t)}</li>' for t in R["after"]["plus"])
        mt = "".join(
            f'<div class="rc st{" hot" if hot else ""}">'
            f'<p class="m top">{esc(top)}'
            f'{"<em>핵심</em>" if hot else ""}</p>'
            f'<div class="v">{esc(v)}</div>'
            f'<p class="dsc kr">{esc(d)}</p></div>'
            for top, v, d, hot in R["metrics"])
        rb_html = f"""
      <p class="ntLead kr rv">{esc(R['lead'])}</p>
      <ul class="bl rv">{rb_bul}</ul>

      <div class="rbc rv">
        <div class="rb b">
          <p class="m hd">{esc(R['before']['hd'])}</p>
          <p class="q kr">{esc(R['before']['q'])}</p>
          <p class="cri kr">{esc(R['before']['d'])}</p>
        </div>
        <span class="rbA" aria-hidden="true">&#8594;</span>
        <div class="rb a">
          <p class="m hd">{esc(R['after']['hd'])}</p>
          <p class="q kr">{esc(R['after']['q'])}</p>
          <p class="cri kr">{esc(R['after']['d'])}</p>
          <ul class="plus">{plus}</ul>
        </div>
      </div>

      <p class="rbCap rv"><span class="lp" aria-hidden="true">&#8594;</span>
        <span class="kr">{esc(R['cap'])}</span></p>

      <div class="stRow rv">
        <div class="rw st">{mt}</div>
      </div>"""

    # 수치와 함께 읽어야 하는 조건들 — 성과 옆에 한계를 나란히 둔다
    lim = p.get("limits")
    lim_html = ('<div class="col ntLim"><p class="m lbl">한계</p>'
                '<ul class="bl lm kr">'
                + "".join(f"<li>{rich(t)}</li>" for t in lim) + "</ul></div>") if lim else ""
    res_html = "" if p.get("sock") or p.get("rubric") else (
        f'<div class="ntRes rv{" two" if lim else ""}">'
        f'<div class="col"><p class="m lbl">{esc(L["res"])}</p>'
        f'{res_lead}' + (f'<div class="rw">{res}</div>' if res else "") + '</div>'
        f'{lim_html}</div>')

    if p.get("note_svg"):
        # 핵심 기여를 글 나열이 아니라 띠 도해로 — 층마다 카드가 이어진다
        grid_html = f'<div class="noteFig rv">{import_svg(p["note_svg"])}</div>'
    elif p.get("bands"):
        # 세 층이 위에서 아래로 흐르는 배치 — 파이프라인 띠처럼 읽힌다
        def band(cls, label, items):
            li = "".join(f'<li class="kr">{rich(t)}</li>' for t in items)
            return (f'<div class="band {cls} rv"><div class="bhd">{lbl_html(label)}</div>'
                    f'<ul class="bl bnd">{li}</ul></div>')
        grid_html = ('<div class="bands">'
                     + band("chal", L["chal"], p["challenge"])
                     + band("cs", L["cause"], p["cause"])
                     + band("fx", L["fix"], p["fix"])
                     + '</div>')
    else:
        grid_html = rb_html if p.get("rubric") else f"""<div class="ntGrid">
        <div class="blk chal rv">
          <p class="m lbl{' two' if ' - ' in L['chal'] else ''}">{lbl_html(L['chal'])}</p>
          {chal_html}
        </div>
        <div class="blk cs rv">
          <p class="m lbl{' two' if ' - ' in L['cause'] else ''}">{lbl_html(L['cause'])}</p>
          {cause_html}
        </div>
        <div class="blk fx rv">
          <p class="m lbl{' two' if ' - ' in L['fix'] else ''}">{lbl_html(L['fix'])}</p>
          {fix_html}
        </div>
      </div>"""

    return f"""
<!-- ══════════ 05 — {p['no']} · PAGE 1 OVERVIEW — 1 화면 ══════════ -->
<section class="scr pj" id="{p['id']}" {style}>
  <div class="scrBody">
    <div class="pjBody">

      <div class="pjHero{hero_cls}">
        <div class="pjIntro{intro_cls}">
          <p class="m lbl rv">{esc(p['kick'])}</p>
          <div class="pjTitle">
            <h2 class="pjName d">{name}</h2>{logo}
          </div>
          <p class="lead kr rv">{esc(p['lead'])}</p>
          <div class="rv">
            <p class="m lbl">BACKGROUND</p>
            {bg_html}
          </div>
        </div>
        {vis_html}
      </div>

      {struct_html}

    </div>
  </div>

  <div class="scrBot">
    <span class="m">{esc(full)}</span>
    <span class="m">NEXT — {esc(focus[0])} {esc(focus[1])} 확대 ↓</span>
  </div>
</section>

<!-- ══════════ 05 — {p['no']} · PAGE 2 ENGINEERING NOTE — 1 화면 ══════════ -->
<section class="scr nt" id="{p['id']}n" {style}>
  <div class="scrBody">
    <div class="ntBody">

      <div class="ntHd">
        <p class="m lbl kcx rv">핵심 기여</p>
        <h3 class="ntTitle">{note_title_plain}</h3>
      </div>

      {grid_html}

      {fig_html}

      {res_html}

    </div>
  </div>

</section>
"""


# ── 폰트 ─────────────────────────────────────────────────────────────────
FAMILIES = [
    ("Sofia Sans Extra Condensed", "wght@800", True),
    ("Archivo", "wght@400;500;600;700;800", True),
    ("IBM Plex Mono", "wght@400;500;600", True),
    ("Noto Sans KR", "wght@400;500;700;800;900", False),
]

ASCII = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
         " .,:;!?'\"()[]{}/\\-_=+*&%#@$~^<>|`©↗↓→←✕§×·—–…“”")


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def used_chars(doc: str, latin_only: bool) -> str:
    txt = html.unescape(re.sub(r"<!--.*?-->", " ", doc, flags=re.S))
    chars = {c for c in txt if c.isprintable() and c not in "\n\r\t"}
    chars |= set(ASCII)
    if latin_only:
        chars = {c for c in chars if ord(c) < 0x2600 and not ("가" <= c <= "힣")}
    return "".join(sorted(chars))


def import_svg(name: str) -> str:
    """사용자가 그린 구조도 SVG 를 인라인용으로 손질한다.
    - :root 변수를 svg.own 로 좁힌다 (페이지의 --line 등을 덮지 않게)
    - 다크 모드 블록은 버린다 (본문은 라이트 고정)
    - 종이색은 프레임과 같은 흰색으로 맞춘다"""
    raw = (HERE / "assets" / name).read_text(encoding="utf-8")
    raw = re.sub(r"@media \(prefers-color-scheme: dark\) \{.*?\n    \}\n",
                 "", raw, flags=re.S)
    raw = raw.replace(":root {", "svg.own {", 1)
    raw = raw.replace("--paper:#f5f4ef", "--paper:#FFFFFF")
    # 루트 태그만 손댄다 — 안쪽 rect 의 width/height 를 건드리면 도면이 망가진다
    m = re.search(r"<svg\b[^>]*>", raw)
    root = m.group(0)
    fixed = re.sub(r'\s(width|height)="[\d.]+"', "", root)
    fixed = fixed.replace("<svg", '<svg class="own"', 1)
    return raw[:m.start()] + fixed + raw[m.end():]

def fonts_css(doc: str) -> str:
    out = []
    for fam, axis, latin, *alias in FAMILIES:
        name = alias[0] if alias else fam
        text = used_chars(doc, latin)
        q = urllib.parse.quote_plus(fam)
        url = (f"https://fonts.googleapis.com/css2?family={q}:{axis}"
               f"&text={urllib.parse.quote(text)}&display=swap")
        css = get(url).decode("utf-8")
        n, total = 0, 0
        for block in re.finditer(r"@font-face\s*\{(.*?)\}", css, re.S):
            body = block.group(1)
            m = re.search(r"src:\s*url\((https://[^)\s]+)\)", body)
            if not m:
                continue
            wm = re.search(r"font-weight:\s*(\d+)", body)
            weight = wm.group(1) if wm else "400"
            raw = get(m.group(1))
            total += len(raw)
            b64 = base64.b64encode(raw).decode("ascii")
            out.append(
                f"@font-face{{font-family:'{name}';font-style:normal;"
                f"font-weight:{weight};font-display:swap;"
                f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
            n += 1
            # 캡션 제목 전용 별칭 — 한글 800 이 없으면 900 으로 반올림돼 너무 굵어진다
            if fam == "Noto Sans KR" and weight == "800":
                out.append(
                    f"@font-face{{font-family:'Noto KR 800';font-style:normal;"
                    f"font-weight:800;font-display:swap;"
                    f"src:url(data:font/woff2;base64,{b64}) format('woff2')}}")
        print(f"  {name:30} {n} face(s)  {total/1024:6.1f} KB  ({len(text)} glyphs)")
    return "\n".join(out)


def main() -> None:
    doc = SRC.read_text(encoding="utf-8")

    print("프로젝트 섹션 생성…")
    doc = doc.replace("{{PROJECTS}}", "".join(project_html(p) for p in PROJECTS))

    print("호버 프리뷰 주입…")
    previews = ",".join(
        "'" + VISUALS[p.get("vis", p["id"])].replace("\\", "\\\\").replace("'", "\\'") + "'"
        for p in PROJECTS)
    doc = doc.replace("{{PREVIEWS}}", "[" + previews + "]")

    print("사진 내장…")
    doc = doc.replace(
        "{{PHOTO}}",
        "data:image/jpeg;base64," + base64.b64encode(PHOTO.read_bytes()).decode("ascii"))

    print("프로젝트 로고 내장…")
    doc = re.sub(r"\{\{IMG:([A-Za-z0-9._-]+)\}\}",
                 lambda m: img_uri(m.group(1)), doc)

    print("폰트 서브셋 내려받는 중…")
    doc = doc.replace("{{FONTS}}", fonts_css(doc))

    out = DIST / "ha-editorial.html"
    out.write_text(doc, encoding="utf-8")
    print(f"\n완료 → {out}  ({len(doc.encode('utf-8'))/1024:.0f} KB)")


if __name__ == "__main__":
    main()
