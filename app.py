from __future__ import annotations

import html
import inspect
import io
import os
import re
from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity

try:
    import fitz
    import pytesseract
    from PIL import Image
except Exception:
    fitz = pytesseract = Image = None

st.set_page_config(page_title="ExamPredict AI", page_icon="📚", layout="wide")

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
BANK_FILE = DATA_DIR / "question_bank.csv"
COLUMNS = ["department", "course", "semester", "subject", "year", "question", "topic", "unit", "marks", "source"]
DEPARTMENTS = ["Computer Applications", "Computer Engineering", "Information Technology", "Electronics Engineering", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Management Studies", "Applied Sciences", "Other"]
COURSES = ["BCA", "MCA", "B.Tech", "M.Tech", "BBA", "MBA", "B.Sc", "M.Sc", "B.Com", "M.Com", "BA", "MA", "Diploma"]
SEMESTERS = [f"Semester {i}" for i in range(1, 13)]

# Works on both old and new Streamlit versions (use_container_width vs width="stretch")
_STRETCH = {"width": "stretch"} if "width" in inspect.signature(st.button).parameters else {"use_container_width": True}
_DF_STRETCH = {"width": "stretch"} if "width" in inspect.signature(st.dataframe).parameters else {"use_container_width": True}


# ---------- Helpers ----------
NEW_OPTION = "➕ Add new..."
ALL = "All"


def nat(value: str):
    """Natural sort so 'Semester 2' comes before 'Semester 10'."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", str(value))]


_ACCEPT_NEW = "accept_new_options" in inspect.signature(st.selectbox).parameters


def pick(label: str, defaults, existing, key: str, required_choice: bool = False) -> str:
    """Dropdown of defaults + everything already saved. You can also type a brand-new value.
    required_choice=True starts with nothing selected, so a value is never saved by accident."""
    options = sorted({clean(x) for x in list(defaults) + list(existing) if clean(x)}, key=nat)
    start = None if (required_choice or not options) else 0
    if _ACCEPT_NEW:
        # Newer Streamlit: just type the new name in the box and press Enter.
        choice = st.selectbox(label, options, index=start, key=f"{key}_sel", accept_new_options=True,
                              placeholder=f"Choose or type a new {label.lower()}")
        typed = clean(choice)
    else:
        # Older Streamlit: choose "Add new..." and a text box appears below.
        choice = st.selectbox(label, options + [NEW_OPTION], index=start, key=f"{key}_sel")
        if choice is None:
            return ""
        if choice != NEW_OPTION:
            return choice
        typed = clean(st.text_input(f"Type new {label.lower()} name", key=f"{key}_new"))
    # same name in different capitalisation = same entry (avoids duplicate subjects)
    return next((o for o in options if o.lower() == typed.lower()), typed)


# ---------- Storage ----------
def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def valid_year(value: object) -> bool:
    return bool(re.fullmatch(r"(?:19|20)\d{2}", clean(value)))


def load_bank() -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not BANK_FILE.exists():
        pd.DataFrame(columns=COLUMNS).to_csv(BANK_FILE, index=False, encoding="utf-8-sig")
    try:
        frame = pd.read_csv(BANK_FILE, dtype=str, keep_default_na=False)
    except Exception:
        st.error("Question Bank CSV could not be read. Keep a backup of data/question_bank.csv before replacing it.")
        return pd.DataFrame(columns=COLUMNS)
    for col in COLUMNS:
        if col not in frame.columns:
            frame[col] = ""
    return frame[COLUMNS].fillna("")


def save_rows(rows: list[dict]) -> int:
    if not rows:
        return 0
    old = load_bank()
    new = pd.DataFrame(rows)
    for col in COLUMNS:
        if col not in new:
            new[col] = ""
        new[col] = new[col].map(clean)
    new["year"] = new["year"].map(lambda x: x if valid_year(x) else "Unknown")
    new = new[new["question"].str.len() >= 8]
    if new.empty:
        return 0
    before = len(old)
    merged = pd.concat([old, new[COLUMNS]], ignore_index=True)
    merged["_dedupe"] = merged["question"].str.lower().str.replace(r"[^a-z0-9]+", " ", regex=True).str.strip()
    merged = merged.drop_duplicates(subset=["department", "course", "semester", "subject", "year", "_dedupe"])
    merged = merged.drop(columns="_dedupe")
    merged.to_csv(BANK_FILE, index=False, encoding="utf-8-sig")
    return len(merged) - before


def sample_rows() -> list[dict]:
    """Small DEMO dataset (3 subjects, 2 courses) so the screens can be shown without PDFs."""
    java = {
        "2022": ["Explain the features of object oriented programming in Java.", "What is inheritance? Explain types of inheritance with example.", "Differentiate between abstract class and interface.", "Explain exception handling in Java with example.", "What is multithreading? Explain thread life cycle."],
        "2023": ["Describe the main features of object oriented programming in Java.", "Explain inheritance and its types with suitable example.", "Write short notes on exception handling using try catch finally.", "Explain the difference between abstract class and interface.", "What are packages in Java? How are they created?"],
        "2024": ["Discuss object oriented programming features of Java.", "Define inheritance. Explain multilevel and hierarchical inheritance with example.", "Explain thread life cycle and thread synchronization.", "Explain exception handling with throw and throws keywords.", "Differentiate between String and StringBuffer."],
        "2025": ["Explain features of object oriented programming with Java examples.", "What is inheritance in Java? Explain its types.", "Compare abstract class and interface in Java.", "Explain multithreading and thread life cycle in Java.", "Explain exception handling in Java. 10 marks"],
    }
    dbms = {
        "2023": ["Explain normalization and its types with example.", "What is a transaction? Explain ACID properties.", "Differentiate between DBMS and file system."],
        "2024": ["Define normalization. Explain 1NF 2NF and 3NF with example.", "Explain ACID properties of a transaction.", "Explain the ER model with suitable diagram."],
        "2025": ["What is normalization? Explain different normal forms.", "Describe ACID properties in transaction management.", "Compare DBMS with file processing system."],
    }
    ds = {
        "2023": ["Explain stack and its operations with example.", "Write an algorithm for binary search.", "Differentiate between array and linked list."],
        "2024": ["What is a stack? Explain push and pop operations.", "Explain binary search algorithm with example.", "Explain types of linked list."],
        "2025": ["Explain stack data structure and its applications.", "Write binary search algorithm and its complexity.", "Compare array and linked list."],
    }
    sets = [
        ("Computer Applications", "BCA", "Semester 4", "Java Programming (Sample)", java),
        ("Computer Applications", "BCA", "Semester 4", "DBMS (Sample)", dbms),
        ("Computer Engineering", "B.Tech", "Semester 3", "Data Structures (Sample)", ds),
    ]
    rows = []
    for dept, course, sem, subject, papers in sets:
        for year, questions in papers.items():
            for q in questions:
                rows.append({"department": dept, "course": course, "semester": sem, "subject": subject, "year": year, "question": q, "topic": "", "unit": "", "marks": get_marks(q), "source": "Sample Demo"})
    return rows


# ---------- PDF text and OCR ----------
def configure_tesseract() -> bool:
    if pytesseract is None:
        return False
    configured = os.environ.get("TESSERACT_CMD", "").strip()
    candidates = [configured, r"C:\Program Files\Tesseract-OCR\tesseract.exe", r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            pytesseract.pytesseract.tesseract_cmd = candidate
            return True
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def extract_pdf(uploaded) -> tuple[str, str]:
    raw = uploaded.getvalue()
    text = ""
    try:
        reader = PdfReader(io.BytesIO(raw))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        pass
    if len(re.sub(r"\s", "", text)) >= 80:
        return text, "Text extraction"
    if fitz is None or pytesseract is None or Image is None:
        raise RuntimeError("This is a scanned PDF and the OCR libraries are missing. Install the packages from requirements.txt, or paste the questions manually.")
    if not configure_tesseract():
        raise RuntimeError("Tesseract OCR is not installed. Install it on Windows, or upload packages.txt on Streamlit Cloud. Until then, you can paste the questions manually.")
    pages = []
    doc = fitz.open(stream=raw, filetype="pdf")
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        try:
            page_text = pytesseract.image_to_string(image, lang="eng", config="--oem 3 --psm 6")
        except Exception:
            page_text = pytesseract.image_to_string(image, config="--oem 3 --psm 6")
        pages.append(page_text)
    result = "\n".join(pages)
    if len(result.strip()) < 25:
        raise RuntimeError("OCR could not read this scan clearly. Use a clearer PDF or paste the questions manually.")
    return result, "OCR (scanned PDF)"


# ---------- Question extraction (robust to messy headers, sub-parts and OCR noise) ----------
MONTHS = r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Sept|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
QUESTION_VERBS = r"(?:write|explain|define|describe|discuss|what|why|how|differentiate|compare|state|list|illustrate|give|distinguish|elaborate|evaluate|draw|derive|calculate|mention|justify|short\s+notes?|enumerate|identify|outline|summarize|summarise|classify|name|find|solve|prove|show|design|develop|implement|analyze|analyse|which|when|where|who|is|are|can|does|do)"
VERB_START_RE = re.compile(rf"^\s*{QUESTION_VERBS}\b", re.I)

# Header / instruction text that must never become a "question".
NOISE_PATTERNS = [
    r"Roll\W{0,3}\s*N[o0O]\b.{0,150}?Total\s*Pages?\s*:?\s*\d+",
    r"Roll\W{0,3}\s*N[o0O]\b\W{0,3}[A-Za-z0-9/\-\.]*",
    r"Total\s*Pages?\s*:?\s*\d+",
    rf"\b\d{{5,7}}\s+{MONTHS}[\s\-,/]*(?:19|20)\d{{2}}.{{0,220}}?Max(?:imum)?\.?\s*Marks\s*:?\s*\d+\s*\]?",
    r"Time\s*(?:Allowed)?\s*:?\s*\d+(?:\.\d+)?\s*Hours?\s*\]?",
    r"\[?\s*Max(?:imum)?\.?\s*Marks\s*:?\s*\d+\s*\]?",
    r"Instructions?\s*[:.\u00a2\u2022\-]?[^?]{0,450}?(?:in\s+short|in\s+detail)\.?",
    r"(?:\d\s*[.)]\s*)?It\s+is\s+compulsory\s+to\s+answer[^?]{0,300}?(?:in\s+short|in\s+detail)\.?",
    r"(?:\d\s*[.)]\s*)?Answer\s+(?:any\s+)?\w+\s+questions?\s+from\s+Part\W{0,3}[A-D]\s+in\s+detail\.?",
    r"(?:\d\s*[.)]\s*)?Attempt\s+(?:any\s+)?\w+\s+questions?[^?.]{0,120}\.",
    r"Different\s+sub\W?parts.{0,80}?adjacent\s+to\s+each\s+other\.?",
    r"\bPART\W{0,4}[A-D]\b",
    r"\bSECTION\W{0,3}[A-D]\b",
    r"\(\s*\d+(?:\.\d+)?\s*marks?\s*each\s*\)",
    r"Page\s*\d+\s*(?:of\s*\d+)?",
    r"[\\|]+",
    r"\(\s*\)",
]
NOISE_RES = [re.compile(p, re.I | re.S) for p in NOISE_PATTERNS]
REJECT_RE = re.compile(r"semester|max\.?\s*marks|roll\s*no|total\s*pages|\bBC[AG]-?\d|\btime\s*:|adjacent to each other|to be attempted|instructions?\b|compulsory", re.I)

MARKS_EACH_RE = re.compile(r"\(\s*(\d+)\s*[x\u00d7*]\s*(\d+(?:\.\d+)?)\s*=\s*\d+(?:\.\d+)?\s*\)", re.I)
MARKS_PAREN_RE = re.compile(r"[\(\[]\s*\d{1,2}(?:\.\d)?\s*marks?\s*[\)\]]", re.I)
SUB_RE = re.compile(r"\(\s*(?:[a-z]|i{2,3}|iv|vi{1,3}|ix)\s*\)", re.I)
QMARK_RE = re.compile(r"(?:(?<=\s)|^)(?:Q(?:uestion)?\.?\s*(\d{1,2})\b[.):\-]?|(\d{1,2})\s*[.)](?=\s))\s*", re.I)


def strip_noise(text: str) -> str:
    text = text.replace("\x0c", " ").replace("\r", " ")
    text = clean(text)
    for rx in NOISE_RES:
        text = rx.sub(" ", text)
    return clean(text)


def get_marks(question: str) -> str:
    m = re.search(r"(?<![\d.])(\d{1,2}(?:\.\d)?)\s*marks?\b", question, re.I) or re.search(r"\[\s*(\d{1,2})\s*\]\s*$", question)
    return m.group(1) if m else ""


def _tidy(q: str) -> str:
    q = clean(q)
    q = re.sub(r"^[\s\-\u2013\u2014:;.,)\]]+", "", q)
    q = re.sub(r"[\s\-\u2013\u2014:;,(\[]+$", "", q)
    return clean(q)


def _chunk_to_questions(chunk: str) -> list[tuple[str, str]]:
    per_marks = ""
    m = MARKS_EACH_RE.search(chunk)
    if m:
        per_marks = m.group(2).rstrip("0").rstrip(".") if "." in m.group(2) else m.group(2)
    chunk = MARKS_EACH_RE.sub(" ", chunk)
    chunk = clean(chunk)
    subs = list(SUB_RE.finditer(chunk))
    out: list[tuple[str, str]] = []
    if not subs:  # "A ... OR B ..." alternatives become separate questions (upper-case OR only)
        for piece in re.split(r"\s+OR\s+", chunk):
            q = _tidy(piece)
            if q:
                out.append((MARKS_PAREN_RE.sub("", q).strip(), get_marks(q) or per_marks))
        return out
    chunk = re.sub(r"\bOR\b", " ", chunk)
    if subs:
        stem = _tidy(re.sub(r"\b(?:following|below|given)\b", " ", chunk[:subs[0].start()], flags=re.I))
        if len(stem.split()) < 2:
            stem = ""
        for i, s in enumerate(subs):
            end = subs[i + 1].start() if i + 1 < len(subs) else len(chunk)
            part = _tidy(chunk[s.end():end])
            if len(part) < 4:
                continue
            q = part if (not stem or VERB_START_RE.match(part)) else f"{stem}: {part}"
            out.append((MARKS_PAREN_RE.sub("", q).strip(), get_marks(q) or per_marks))
    return out


def _valid(q: str) -> bool:
    if not (8 <= len(q) <= 700):
        return False
    if len(re.findall(r"[A-Za-z]{2,}", q)) < 2:
        return False
    if REJECT_RE.search(q):
        return False
    return True


def split_questions(raw: str) -> list[tuple[str, str]]:
    """Returns [(question_text, marks)]. Sub-parts (a)(b)(c) become separate questions."""
    text = strip_noise(raw)
    marks_found = list(QMARK_RE.finditer(text))
    results: list[tuple[str, str]] = []
    if marks_found:
        for i, m in enumerate(marks_found):
            end = marks_found[i + 1].start() if i + 1 < len(marks_found) else len(text)
            results.extend(_chunk_to_questions(text[m.end():end]))
    if not results:  # fallback: no numbering found, split into sentences
        for sent in re.split(r"(?<=[.?])\s+(?=[A-Z(])", text):
            sent = _tidy(sent)
            if sent.endswith("?") or (VERB_START_RE.match(sent) and len(sent) >= 20):
                results.append((sent, get_marks(sent)))
    final, seen = [], set()
    for q, marks in results:
        q = _tidy(q)
        key = re.sub(r"[^a-z0-9]+", " ", q.lower()).strip()
        if _valid(q) and key not in seen:
            seen.add(key)
            final.append((q, marks))
    return final[:400]


def get_year(filename: str, raw_text: str, manual_year: str) -> str:
    if valid_year(manual_year):
        return manual_year
    blob = filename + " " + raw_text[:4000]
    m = re.search(rf"{MONTHS}[\s\-,/]*((?:19|20)\d{{2}})(?!\d)", blob, re.I)
    if m:
        return m.group(1)
    m = re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)", blob)
    return m.group(1) if m else "Unknown"


# ---------- Similarity and ranking ----------
def norm_question(value: str) -> str:
    value = clean(value)
    # "Write short notes on: Types of streams" -> compare only "Types of streams", not the shared stem
    m = re.match(r"^([^:]{3,60}):\s*(.+)$", value)
    if m and VERB_START_RE.match(m.group(1)) and len(m.group(1).split()) <= 8:
        value = m.group(2)
    value = value.lower()
    value = re.sub(r"^(?:q(?:uestion)?\s*)?\d{1,2}\s*[.)]\s*", "", value)
    return re.sub(r"[^a-z0-9 ]", " ", value)


def cluster_questions(questions: list[str], threshold: float) -> list[list[int]]:
    if len(questions) <= 1:
        return [[i] for i in range(len(questions))]
    try:
        matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True).fit_transform([norm_question(q) for q in questions])
        similarity = cosine_similarity(matrix)
    except ValueError:
        return [[i] for i in range(len(questions))]
    groups: list[list[int]] = []
    assigned: set[int] = set()
    for i in range(len(questions)):
        if i in assigned:
            continue
        group = [i]
        assigned.add(i)
        for j in range(i + 1, len(questions)):
            if j not in assigned and float(similarity[i, j]) >= threshold:
                group.append(j)
                assigned.add(j)
        groups.append(group)
    return groups


def topic_words(questions: list[str]) -> str:
    counts = Counter()
    for q in questions:
        counts.update(w for w in re.findall(r"[a-zA-Z]{3,}", q.lower()) if w not in ENGLISH_STOP_WORDS)
    return ", ".join(word.title() for word, _ in counts.most_common(4)) or "-"


def analyze(frame: pd.DataFrame, threshold: float) -> list[dict]:
    if frame.empty:
        return []
    frame = frame.reset_index(drop=True).copy()
    years = sorted({y for y in frame.year.unique() if valid_year(y)})
    enough = len(years) >= 2  # repetition can only be measured with 2+ exam years
    output = []
    for indices in cluster_questions(frame.question.tolist(), threshold):
        group = frame.iloc[indices]
        year_list = sorted({y for y in group.year.unique() if valid_year(y)})
        times = len(group)
        marks_vals = [float(x) for x in group.marks if re.fullmatch(r"\d+(?:\.\d+)?", clean(x))]
        if enough:
            coverage = len(year_list) / len(years)
            latest = 1 if years[-1] in year_list else 0
            score = round(min(100, 65 * coverage + 20 * latest + 15 * min(times, 5) / 5), 1)
            if len(year_list) >= 2 and coverage >= 0.66:
                priority = "High"
            elif len(year_list) >= 2:
                priority = "Medium"
            else:
                priority = "Review"
        else:
            score, priority = None, "Review"
        representative = min(group.question.tolist(), key=lambda q: abs(len(q) - 90))
        output.append({
            "Priority": priority,
            "Question": representative,
            "Keywords": topic_words(group.question.tolist()),
            "Score": score,
            "Years": ", ".join(year_list) if year_list else "Unknown",
            "Times Seen": times,
            "Marks": ", ".join(sorted(set(x for x in group.marks if x))) or "-",
            "_marks": max(marks_vals) if marks_vals else 0.0,
        })
    order = {"High": 0, "Medium": 1, "Review": 2}
    output.sort(key=lambda r: (order[r["Priority"]], -(r["Score"] or 0), -r["Times Seen"], -r["_marks"]))
    for r in output:
        r.pop("_marks")
    return output


def render_results_table(results: list[dict]) -> str:
    """One aligned HTML table: fixed columns, wrapped text, works in light and dark theme."""
    esc = html.escape
    rows = []
    for n, r in enumerate(results, 1):
        cls = r["Priority"].lower()
        rows.append(
            f"<tr><td class='c'>{n}</td>"
            f"<td><div class='q'>{esc(r['Question'])}</div><div class='kw'>Keywords: {esc(r['Keywords'])}</div></td>"
            f"<td class='c'><span class='badge {cls}'>{esc(r['Priority'])}</span></td>"
            + (f"<td><div class='bar'><div style='width:{r['Score']}%'></div></div><b>{r['Score']}</b>/100</td>" if r["Score"] is not None
               else "<td><div class='bar'><div style='width:0%'></div></div><span style='opacity:.65'>needs 2+ years</span></td>") +
            f"<td class='c'>{r['Times Seen']}</td>"
            f"<td class='c'>{esc(r['Years'])}</td>"
            f"<td class='c'>{esc(r['Marks'])}</td></tr>"
        )
    head = "<tr><th>#</th><th>Question / Topic Pattern</th><th>Priority</th><th>Study Score</th><th>Times Seen</th><th>Years Appeared</th><th>Marks</th></tr>"
    return f"<div class='tw'><table class='rt'><thead>{head}</thead><tbody>{''.join(rows)}</tbody></table></div>"


# ---------- Interface ----------
st.markdown("""<style>
.hero {background:linear-gradient(115deg,#123b9a,#1765e8);padding:24px 28px;border-radius:16px;color:white;margin-bottom:18px;}
.hero h1,.hero p {color:white !important;margin:0 0 6px 0;}
.tw {overflow-x:auto;border:1px solid rgba(128,128,128,.3);border-radius:12px;}
table.rt {width:100%;border-collapse:collapse;table-layout:fixed;min-width:820px;font-size:0.93rem;}
table.rt th {background:rgba(23,101,232,.15);text-align:center;padding:10px 8px;font-weight:600;border-bottom:1px solid rgba(128,128,128,.3);}
table.rt th:nth-child(2) {text-align:left;}
table.rt td {padding:10px 8px;vertical-align:middle;border-bottom:1px solid rgba(128,128,128,.15);word-wrap:break-word;}
table.rt td.c {text-align:center;}
table.rt th:nth-child(1), table.rt td:nth-child(1) {width:44px;}
table.rt th:nth-child(2) {width:38%;}
table.rt th:nth-child(3) {width:92px;}
table.rt th:nth-child(4) {width:140px;}
table.rt th:nth-child(5) {width:80px;}
table.rt th:nth-child(6) {width:170px;}
table.rt th:nth-child(7) {width:70px;}
.q {font-weight:500;line-height:1.35;}
.kw {font-size:.8rem;opacity:.65;margin-top:3px;}
.badge {padding:3px 12px;border-radius:999px;font-size:.8rem;font-weight:700;color:#fff;display:inline-block;}
.badge.high {background:#d93025;} .badge.medium {background:#e8a317;} .badge.review {background:#7a8595;}
.bar {height:8px;border-radius:6px;background:rgba(128,128,128,.25);margin-bottom:4px;overflow:hidden;}
.bar div {height:100%;background:linear-gradient(90deg,#1765e8,#2bb673);}
</style>""", unsafe_allow_html=True)
st.markdown("<div class='hero'><h1>📚 ExamPredict AI</h1><p><b>Smart Previous-Year Question Paper Analyzer</b></p><p>For students across courses, departments and semesters · J.C. Bose University of Science &amp; Technology, YMCA, Faridabad</p></div>", unsafe_allow_html=True)

for key, default in (("staged_questions", None), ("flash", ""), ("results", None), ("raw_texts", {})):
    if key not in st.session_state:
        st.session_state[key] = default

if st.session_state.flash:
    st.success(st.session_state.flash)
    st.session_state.flash = ""

guide_tab, upload_tab, predict_tab, bank_tab = st.tabs(["🎓 Student Study Guide", "📤 Add Papers", "🎯 Detailed Analysis", "📚 Question Bank"])

# ----- Tab 0: student-facing guide (any course) -----
with guide_tab:
    st.subheader("Student Study Guide")
    st.caption("Choose your course, semester and subject to see what to study first, based on previous years' papers.")
    bank = load_bank()
    subj_counts = bank.groupby("course").subject.nunique().to_dict() if not bank.empty else {}
    all_courses = sorted(set(COURSES) | set(subj_counts), key=nat)

    def course_label(c: str) -> str:
        n = subj_counts.get(c, 0)
        return f"{c} ({n} subject{'s' if n != 1 else ''})" if n else f"{c} (no papers yet)"

    g1, g2, g3 = st.columns(3)
    s_course = g1.selectbox("Your course", all_courses, key="g_course", format_func=course_label)
    gpool = bank[bank.course == s_course] if not bank.empty else bank
    if gpool.empty:
        st.info(f"**{s_course}** has no papers yet. Go to the 'Add Papers' tab, select the course **{s_course}**, enter the subject and upload papers. They will appear here once added.")
        if subj_counts:
            st.caption("Courses with papers: " + ", ".join(sorted(subj_counts, key=nat)))
    else:
        s_sem = g2.selectbox("Semester", sorted(gpool.semester.unique(), key=nat), key="g_sem")
        gpool = gpool[gpool.semester == s_sem]
        s_subj = g3.selectbox("Subject", sorted(gpool.subject.unique(), key=nat), key="g_subj")
        subj_df = gpool[gpool.subject == s_subj]
        topic = clean(st.text_input("🔎 Search a topic (optional)", placeholder="e.g. inheritance, normalization", key="g_search"))
        g_rows = analyze(subj_df, 0.35)
        g_years = sorted({y for y in subj_df.year.unique() if valid_year(y)})
        if topic:
            g_rows = [r for r in g_rows if topic.lower() in r["Question"].lower() or topic.lower() in r["Keywords"].lower()]
        c1, c2, c3 = st.columns(3)
        c1.metric("Papers analysed (years)", len(g_years))
        c2.metric("Questions in bank", len(subj_df))
        c3.metric("High priority topics", sum(r["Priority"] == "High" for r in g_rows))
        if len(g_years) < 2:
            st.warning("This subject has data for only one year (or none), so repeated questions cannot be detected reliably. Add more papers in the 'Add Papers' tab.")
        if g_rows:
            st.markdown("##### Study first (most repeated at the top)")
            st.markdown(render_results_table(g_rows[:15]), unsafe_allow_html=True)
            if len(g_rows) > 15:
                st.caption(f"Top 15 of {len(g_rows)} patterns shown. Open the 'Detailed Analysis' tab for the full list.")
            st.download_button("⬇️ Download my study list (CSV)", pd.DataFrame(g_rows).to_csv(index=False).encode("utf-8-sig"), f"Study_Guide_{s_subj}.csv".replace(" ", "_"), "text/csv", key="g_download")
        else:
            st.info("No matching question found for this search." if topic else "No usable questions found for this subject.")
        st.info("This is a study-priority guide based only on previous papers. It does not guarantee that these questions will appear in the exam. Always cover the full syllabus.")
        st.caption("Your subject is not listed? Add your papers in the 'Add Papers' tab so everyone can benefit.")

# ----- Tab 1 -----
with upload_tab:
    st.subheader("Add previous-year question papers")
    st.caption("Choose the paper details, upload one or more PDFs, then review the extracted questions before saving. Leave 'Paper year' empty to detect the year from each PDF automatically (best when uploading several years at once).")
    existing = load_bank()
    left, right = st.columns(2)
    with left:
        department = pick("Department", DEPARTMENTS, existing.department, "u_dept")
        course = pick("Course", COURSES, existing.course, "u_course")
        semester = st.selectbox("Semester", SEMESTERS, key="u_sem")
    with right:
        subject = pick("Subject", [], existing.subject, "u_subj", required_choice=True)
        year = st.text_input("Paper year", placeholder="e.g. 2025", max_chars=4, key="u_year")
    pdfs = st.file_uploader("Upload previous-year PDF(s)", type=["pdf"], accept_multiple_files=True, key="u_pdfs")
    manual_text = st.text_area("Or paste questions manually (one question per line)", height=120, placeholder="Explain the features of object-oriented programming.\nWhat is inheritance in Java?", key="u_manual")
    submitted = st.button("Extract and preview questions", type="primary", key="u_submit", **_STRETCH)
    if submitted:
        if not clean(department) or not clean(course):
            st.error("Please enter the department and course names.")
        elif not clean(subject):
            st.error("Please enter the subject name.")
        elif clean(year) and not valid_year(year):
            st.error("Enter a valid year such as 2025.")
        elif not pdfs and not clean(manual_text):
            st.warning("Upload a PDF or paste questions first.")
        else:
            metadata = {"department": clean(department), "course": clean(course), "semester": semester, "subject": clean(subject)}
            staged = []
            raw_store = {}
            for pdf in pdfs or []:
                try:
                    raw_text, method = extract_pdf(pdf)
                    extracted = split_questions(raw_text)
                    detected_year = get_year(pdf.name, raw_text, clean(year))
                    raw_store[pdf.name] = raw_text
                    for question, q_marks in extracted:
                        staged.append({**metadata, "year": detected_year, "question": question, "topic": "", "unit": "", "marks": q_marks, "source": pdf.name})
                    st.info(f"{pdf.name}: {len(extracted)} question(s) extracted using {method}. Year detected: {detected_year}.")
                    if not extracted:
                        st.warning(f"No clear questions detected in {pdf.name}. Try a clearer scan or paste the questions manually.")
                except Exception as exc:
                    st.error(f"{pdf.name}: {exc}")
            for question in manual_text.splitlines():
                question = clean(question)
                question = re.sub(r"^\s*(?:\d{1,2}[.)]|[-•])\s*", "", question)
                if len(question) >= 12:
                    staged.append({**metadata, "year": clean(year) or "Unknown", "question": question, "topic": "", "unit": "", "marks": get_marks(question), "source": "Manual Entry"})
            if staged:
                st.session_state.staged_questions = staged
                st.session_state.raw_texts = raw_store
                st.success(f"{len(staged)} question(s) ready. Review them below before saving.")
    if st.session_state.staged_questions:
        st.markdown("#### Review extracted questions")
        st.caption("You can edit or delete incorrect OCR lines here. Nothing is saved until you press the save button.")
        edited = st.data_editor(pd.DataFrame(st.session_state.staged_questions), hide_index=True, num_rows="dynamic", key="question_review", **_DF_STRETCH,
                                column_config={"question": st.column_config.TextColumn("Question", width="large"), "year": st.column_config.TextColumn("Year", width="small")})
        if st.session_state.raw_texts:
            with st.expander("🔍 Show the raw text read from the PDF (use this if questions look wrong)"):
                for fname, txt in st.session_state.raw_texts.items():
                    st.markdown(f"**{fname}**")
                    st.text_area("Raw text", txt[:6000], height=200, key=f"raw_{fname}", label_visibility="collapsed")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("💾 Save reviewed questions", type="primary", key="u_save", **_STRETCH):
                count = save_rows(edited.to_dict("records"))
                st.session_state.staged_questions = None
                st.session_state.flash = f"Saved {count} new question(s). Existing Question Bank records preserved."
                st.rerun()
        with col_b:
            if st.button("Discard preview", key="u_discard", **_STRETCH):
                st.session_state.staged_questions = None
                st.rerun()

    with st.expander("🧪 Demo mode: load sample data (multiple subjects and courses)"):
        st.caption("For demo/testing only: 3 subjects, 2 courses. These are not real papers; the subject names end with '(Sample)'.")
        if st.button("Load sample demo data", key="u_sample"):
            n = save_rows(sample_rows())
            st.session_state.flash = f"Sample data loaded ({n} questions). Open the 'Student Study Guide' tab to see them."
            st.rerun()

# ----- Tab 2 -----
with predict_tab:
    st.subheader("Most repeated and important study topics")
    bank = load_bank()
    if bank.empty:
        st.info("Add previous-year papers first (or load the demo data). The analysis is more useful when papers from multiple years are added.")
    else:
        f1, f2, f3, f4 = st.columns(4)
        sel_dept = f1.selectbox("Department", [ALL] + sorted(bank.department.unique(), key=nat), key="p_dept")
        pool = bank if sel_dept == ALL else bank[bank.department == sel_dept]
        sel_course = f2.selectbox("Course", [ALL] + sorted(pool.course.unique(), key=nat), key="p_course")
        pool = pool if sel_course == ALL else pool[pool.course == sel_course]
        sel_sem = f3.selectbox("Semester", [ALL] + sorted(pool.semester.unique(), key=nat), key="p_sem")
        pool = pool if sel_sem == ALL else pool[pool.semester == sel_sem]
        ALL_SUBJECTS = "All subjects (separate report for each)"
        sel_subject = f4.selectbox("Subject", [ALL_SUBJECTS] + sorted(pool.subject.unique(), key=nat), key="p_subject")
        selected = pool if sel_subject == ALL_SUBJECTS else pool[pool.subject == sel_subject]
        keys = ["department", "course", "semester", "subject"]
        n_subjects = selected.groupby(keys).ngroups
        threshold = st.slider("How closely should questions match?", 0.25, 0.85, 0.35, 0.05, key="p_threshold", help="Lower values group loosely worded similar questions together. Higher values require closer wording.")
        st.caption(f"Selected: {len(selected)} question records across {n_subjects} subject(s).")
        if st.button("✨ Analyze study priorities", type="primary", key="p_analyze", **_STRETCH):
            sections = []
            for (dept_, course_, sem_, subj_), g in selected.groupby(keys):
                yrs = sorted({y for y in g.year.unique() if valid_year(y)})
                sections.append({"label": f"{subj_} · {course_} · {sem_}", "subject": subj_, "course": course_, "semester": sem_, "rows": analyze(g, threshold), "records": len(g), "years": len(yrs)})
            sections.sort(key=lambda s: (nat(s["course"]), nat(s["semester"]), nat(s["subject"])))
            st.session_state.results = {"sections": sections}

        data = st.session_state.results
        if data:
            sections = [s for s in data["sections"] if s["rows"]]
            if not sections:
                st.warning("No usable questions were found for this selection.")
            else:
                all_rows = [r for s in sections for r in s["rows"]]
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Subjects", len(sections))
                m2.metric("Questions analysed", sum(s["records"] for s in sections))
                m3.metric("Unique patterns", len(all_rows))
                m4.metric("High priority", sum(r["Priority"] == "High" for r in all_rows))
                view = st.radio("Show", ["All", "High", "Medium", "Review"], horizontal=True, key="p_view")
                for idx, sec in enumerate(sections):
                    rows = sec["rows"]
                    shown = rows if view == "All" else [r for r in rows if r["Priority"] == view]
                    with st.expander(f"📘 {sec['label']}  ·  {len(rows)} patterns  ·  {sec['years']} year(s)", expanded=(idx == 0 or len(sections) <= 3)):
                        if sec["years"] < 2:
                            st.warning("This subject has data for only one exam year (or none), so repetition is not reliable. Add papers from more years.")
                        if shown:
                            st.markdown(render_results_table(shown), unsafe_allow_html=True)
                        else:
                            st.info("No questions in this priority level.")
                        if len(rows) > 1:
                            chart = pd.DataFrame({"Score": [r["Score"] for r in rows[:10]]}, index=[f"{i}. {r['Question'][:35]}..." for i, r in enumerate(rows[:10], 1)])
                            st.markdown("##### Top 10 by study score")
                            st.bar_chart(chart)
                report = pd.DataFrame([{"Course": s["course"], "Semester": s["semester"], "Subject": s["subject"], **r} for s in sections for r in s["rows"]])
                st.download_button("⬇️ Download study-priority report (CSV)", report.to_csv(index=False).encode("utf-8-sig"), "ExamPredict_AI_Study_Report.csv", "text/csv", key="p_download")
                st.info("This score is a study-priority indicator based only on the papers in this Question Bank. It is not a probability or a guarantee that a question will appear in the next exam.")

# ----- Tab 3 -----
with bank_tab:
    st.subheader("Saved Question Bank")
    bank = load_bank()
    if bank.empty:
        st.info("No questions saved yet.")
    else:
        summary = (bank.assign(_valid=bank.year.where(bank.year.map(valid_year), ""))
                   .groupby(["department", "course", "semester", "subject"])
                   .agg(Questions=("question", "count"), Years=("_valid", lambda s: ", ".join(sorted({y for y in s if y}))))
                   .reset_index())
        with st.expander(f"📊 Subjects summary ({len(summary)} subject(s), {bank.course.nunique()} course(s))", expanded=True):
            st.dataframe(summary.rename(columns=str.title), hide_index=True, **_DF_STRETCH)
        a, b, c, d = st.columns(4)
        course_filter = a.selectbox("Course", [ALL] + sorted(bank.course.unique(), key=nat), key="b_course")
        semester_filter = b.selectbox("Semester", [ALL] + sorted(bank.semester.unique(), key=nat), key="b_sem")
        subject_filter = c.selectbox("Subject", [ALL] + sorted(bank.subject.unique(), key=nat), key="b_subject")
        year_filter = d.selectbox("Year", [ALL] + sorted(bank.year.unique(), reverse=True), key="b_year")
        view_df = bank.copy()
        for col, val in (("course", course_filter), ("semester", semester_filter), ("subject", subject_filter), ("year", year_filter)):
            if val != ALL:
                view_df = view_df[view_df[col] == val]
        st.caption(f"Showing {len(view_df)} question(s) out of {len(bank)} stored.")
        st.dataframe(view_df, hide_index=True, **_DF_STRETCH, column_config={"question": st.column_config.TextColumn("Question", width="large")})
        st.download_button("Download Question Bank CSV", bank.to_csv(index=False).encode("utf-8-sig"), "ExamPredict_AI_Question_Bank.csv", "text/csv", key="b_download")

    with st.expander("🛠️ Manage data: backup, restore, delete"):
        st.caption("Your data lives in data/question_bank.csv. Download a backup regularly. On free online hosting the file can reset after a restart, so you can restore it here.")
        up = st.file_uploader("Restore or import a Question Bank CSV", type=["csv"], key="b_import")
        if up is not None and st.button("Import CSV into Question Bank", key="b_import_btn"):
            try:
                inc = pd.read_csv(up, dtype=str, keep_default_na=False)
                missing = [c for c in ("course", "subject", "question") if c not in inc.columns]
                if missing:
                    st.error("CSV must contain these columns: " + ", ".join(missing))
                else:
                    for col, default in (("department", "Other"), ("semester", "Unknown"), ("year", "Unknown"), ("source", "Imported CSV")):
                        if col not in inc.columns:
                            inc[col] = default
                    n_new = save_rows(inc.to_dict("records"))
                    st.session_state.flash = f"Imported {n_new} new question(s)."
                    st.rerun()
            except Exception as exc:
                st.error(f"Could not import this CSV: {exc}")
        cur = load_bank()
        if not cur.empty:
            cur["_label"] = cur.subject + " · " + cur.course + " · " + cur.semester
            target = st.selectbox("Delete all saved questions of one subject", sorted(cur["_label"].unique(), key=nat), key="b_del_sel")
            sure = st.checkbox("Yes, delete permanently", key="b_del_ok")
            if st.button("🗑️ Delete subject data", key="b_del_btn", disabled=not sure):
                kept = cur[cur["_label"] != target].drop(columns="_label")
                kept.to_csv(BANK_FILE, index=False, encoding="utf-8-sig")
                st.session_state.flash = f"Deleted: {target}"
                st.rerun()


st.divider()
st.caption("ExamPredict AI · PDF extraction + OCR · TF-IDF · Cosine similarity · Transparent study-priority analysis")
