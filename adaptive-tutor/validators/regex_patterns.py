import re

# ── Allowlists ────────────────────────────────────────────────────────────────

ALLOWED_CITATION_DOMAINS = re.compile(
    r"^https?://([a-z0-9\-]+\.)?(wikipedia\.org|khanacademy\.org|britannica\.com|"
    r"explorehealthcareers\.org|sciencedirect\.com|pubmed\.ncbi\.nlm\.nih\.gov|"
    r"scholar\.google\.com)(\/|$)",
    re.IGNORECASE,
)

CONCEPT_ID = re.compile(r"^[a-z][a-z_]{2,40}$")

# ── Security blocklist ────────────────────────────────────────────────────────

_INJECTION_PATTERNS = [
    r"<script[\s>]",
    r"javascript\s*:",
    r"onerror\s*=",
    r"data\s*:\s*text/html",
    r"on\w+\s*=\s*['\"]",
    r"<iframe[\s>]",
    r"<object[\s>]",
    r"<embed[\s>]",
]

_PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|prior)\s+instructions?",
    r"\bsystem\s*:",
    r"you\s+are\s+now\s+",
    r"disregard\s+.{0,30}\s+instructions?",
    r"act\s+as\s+if\s+you",
    r"pretend\s+you\s+(are|were)\s+",
    r"your\s+new\s+role\s+is",
    r"forget\s+(everything|all)\s+(you|your)",
]

_PII_PATTERNS = [
    r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",  # email
    r"\b(\+\d{1,3}[\s\-]?)?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}\b",  # phone
]

_INAPPROPRIATE_PATTERNS = [
    r"\b(kill yourself|kys)\b",
    r"\b(self[\s\-]?harm)\b",
    r"\bhow to (make|build|create|construct) (a )?(bomb|weapon|poison|explosive)\b",
]

_COMPILED_BLOCKLISTS: list[re.Pattern] = [
    re.compile(p, re.IGNORECASE)
    for p in (
        _INJECTION_PATTERNS
        + _PROMPT_INJECTION_PATTERNS
        + _PII_PATTERNS
        + _INAPPROPRIATE_PATTERNS
    )
]


def check_blocklist(text: str) -> tuple[bool, str | None]:
    """Return (is_clean, matched_pattern_description). is_clean=True means safe."""
    for pattern in _COMPILED_BLOCKLISTS:
        m = pattern.search(text)
        if m:
            return False, pattern.pattern
    return True, None


def is_allowed_url(url: str) -> bool:
    return bool(ALLOWED_CITATION_DOMAINS.match(url))


def is_valid_concept_id(concept_id: str) -> bool:
    return bool(CONCEPT_ID.match(concept_id))
