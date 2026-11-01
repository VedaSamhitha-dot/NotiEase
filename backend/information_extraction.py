import re

MONTHS = (
    r"January|February|March|April|May|June|July|August|"
    r"September|October|November|December|"
    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
)

DATE_PATTERN = re.compile(
    rf"\b(?:"
    rf"\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{MONTHS})\.?,?\s+\d{{4}}|"
    rf"(?:{MONTHS})\.?\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}|"
    rf"\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}}"
    rf")\b",
    re.IGNORECASE,
)

AMOUNT_PATTERN = re.compile(
    r"(?:₹\s?\d[\d,]*(?:\.\d{1,2})?|"
    r"\bRs\.?\s?\d[\d,]*(?:\.\d{1,2})?|"
    r"\bINR\s?\d[\d,]*(?:\.\d{1,2})?)",
    re.IGNORECASE,
)

DEADLINE_CUES = (
    "by", "before", "on or before", "no later than",
    "deadline", "last date", "due on", "until",
    "upto", "up to", "till",
)

EVENT_CUES = (
    "scheduled for", "will be held", "is being held",
    "to be held", "takes place", "will take place",
    "organizing", "organising", "conducting",
    "workshop on", "seminar on", "event on", "exam on",
    "meeting on", "session on", "held on",
)

ELIGIBILITY_CUES = (
    "eligible", "eligibility", "must have", "minimum",
    "at least", "should have", "only students",
    "students with", "who have", "criteria",
)

ACTION_CUES = (
    "register", "apply", "submit", "bring", "carry",
    "contact", "pay", "upload", "attend", "visit",
    "send", "fill", "report",
)

CONSEQUENCE_CUES = (
    "will not be accepted", "not be accepted",
    "will be rejected", "will be cancelled",
    "will be disqualified", "otherwise",
    "failing to", "failure to", "late",
)


def clean_notice(text):
    """Remove a leading NOTICE label and normalize whitespace."""
    text = re.sub(r"^\s*NOTICE\s*:\s*", "", str(text), flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text):
    """Split text into sentence-like chunks."""
    return [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+|\n+", text)
        if part.strip()
    ]


def unique(items):
    """Remove duplicate items while preserving their original order."""
    result = []
    seen = set()

    for item in items:
        item = item.strip(" \t\n.,;:")
        key = item.casefold()

        if item and key not in seen:
            seen.add(key)
            result.append(item)

    return result


def has_cue(text, cues):
    text = text.casefold()
    return any(cue in text for cue in cues)


def extract_information(notice):
    """
    Extract common details from a college notice.

    Returns event_dates, deadlines, amounts, eligibility,
    required_actions, consequences, and summary.
    """
    text = clean_notice(notice)
    sentences = split_sentences(text)

    event_dates = []
    deadlines = []
    amounts = []
    eligibility = []
    required_actions = []
    consequences = []

    for sentence in sentences:
        sentence_lower = sentence.casefold()

        # Extract and classify dates.
        for match in DATE_PATTERN.finditer(sentence):
            date_text = match.group(0)
            before_date = sentence_lower[:match.start()]
            after_date = sentence_lower[match.end():]

            if (
                has_cue(before_date, DEADLINE_CUES)
                or has_cue(after_date, DEADLINE_CUES)
            ):
                deadlines.append(date_text)
            elif (
                has_cue(before_date, EVENT_CUES)
                or has_cue(after_date, EVENT_CUES)
            ):
                event_dates.append(date_text)
            else:
                # Keep dates visible even if the wording is ambiguous.
                event_dates.append(date_text)

        # Extract amounts.
        amounts.extend(
            match.group(0)
            for match in AMOUNT_PATTERN.finditer(sentence)
        )

        # Eligibility sentences should not also be listed as actions.
        is_eligibility = has_cue(sentence_lower, ELIGIBILITY_CUES)

        if is_eligibility:
            eligibility.append(sentence)
        elif has_cue(sentence_lower, ACTION_CUES):
            required_actions.append(sentence)

        # Extract consequences.
        if has_cue(sentence_lower, CONSEQUENCE_CUES):
            consequences.append(sentence)

    # Build a concise summary from the first action and eligibility sentence.
    summary_parts = []

    if required_actions:
        summary_parts.append(required_actions[0])

    if eligibility:
        summary_parts.append(eligibility[0])

    summary = " ".join(summary_parts) or (
        sentences[0] if sentences else ""
    )

    return {
        "event_dates": unique(event_dates),
        "deadlines": unique(deadlines),
        "amounts": unique(amounts),
        "eligibility": unique(eligibility),
        "required_actions": unique(required_actions),
        "consequences": unique(consequences),
        "summary": summary,
    }