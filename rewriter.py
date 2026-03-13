"""
rewriter.py — Pure Python mood-based text transformation engine.
No ML, no magic. Just explicit linguistic rules.
"""

import re

# ---------------------------------------------------------------------------
# MOOD RULES
# Each mood has:
#   prefix    — text prepended to the sentence
#   suffix    — text appended
#   replacements — list of (pattern, replacement) pairs (regex)
#   transform — optional function applied to the whole string
# ---------------------------------------------------------------------------

MOOD_RULES = {
    "formal": {
        "prefix": "",
        "suffix": "",
        "replacements": [
            (r"\bI'm\b",        "I am"),
            (r"\bcan't\b",      "cannot"),
            (r"\bdon't\b",      "do not"),
            (r"\bwon't\b",      "will not"),
            (r"\bdidn't\b",     "did not"),
            (r"\bisn't\b",      "is not"),
            (r"\bit's\b",       "it is"),
            (r"\bthat's\b",     "that is"),
            (r"\bthanks\b",     "thank you"),
            (r"\bgot\b",        "received"),
            (r"\bget\b",        "obtain"),
            (r"\bkinda\b",      "somewhat"),
            (r"\bwanna\b",      "would like to"),
            (r"\bgonna\b",      "going to"),
            (r"\b(so|very)\b",  "exceedingly"),
            (r"\bOK\b",         "acceptable"),
            (r"\byeah\b",       "yes"),
            (r"\bnope\b",       "no"),
        ],
        "explanations": [
            "Expanded all contractions (e.g. can't → cannot).",
            "Replaced informal vocabulary with formal equivalents.",
            "Elevated register using neutral, professional phrasing.",
        ]
    },

    "friendly": {
        "prefix": "Hey! Just wanted to let you know — ",
        "suffix": " Hope that helps! 😊",
        "replacements": [
            (r"\bthank you\b",  "thanks so much"),
            (r"\bhello\b",      "hey there"),
            (r"\bgreetings\b",  "hi"),
            (r"\bcannot\b",     "can't"),
            (r"\bobtain\b",     "get"),
        ],
        "explanations": [
            "Added a warm, casual greeting prefix.",
            "Softened formal vocabulary to everyday words.",
            "Appended a friendly closing.",
        ]
    },

    "concise": {
        "prefix": "",
        "suffix": "",
        "replacements": [
            (r"\bI wanted to let you know that\b",      ""),
            (r"\bAs you may already be aware,?\b",      ""),
            (r"\bIn order to\b",                        "To"),
            (r"\bdue to the fact that\b",               "because"),
            (r"\bat this point in time\b",              "now"),
            (r"\bbasically\b",                          ""),
            (r"\bactually\b",                           ""),
            (r"\bI think that\b",                       ""),
            (r"\b(very|really|quite|rather)\b",         ""),
            (r"\bperiod of time\b",                     "period"),
            (r"\b\s{2,}\b",                             " "),   # collapse double spaces
        ],
        "explanations": [
            "Stripped filler phrases and hedge words.",
            "Collapsed verbose expressions to tight equivalents.",
            "Removed redundant qualifiers (very, really, quite).",
        ]
    },

    "angry": {
        "prefix": "Listen up — ",
        "suffix": " This needs to change. Now.",
        "replacements": [
            (r"\bplease\b",     ""),
            (r"\bkindly\b",     ""),
            (r"\bif possible\b",""),
            (r"\bperhaps\b",    ""),
            (r"\bmight\b",      "will"),
            (r"\bcould\b",      "must"),
            (r"\bwould like\b", "demand"),
            (r"\bgood\b",       "unacceptable"),
            (r"\bfine\b",       "not fine"),
            (r"\.",             "!"),
        ],
        "explanations": [
            "Removed softening words (please, kindly, perhaps).",
            "Escalated modal verbs (could → must).",
            "Replaced periods with exclamation marks.",
            "Added direct, urgent framing.",
        ]
    },

    "polite": {
        "prefix": "I hope you're doing well. I was wondering if ",
        "suffix": ", if that's alright with you? Thank you so much for your time.",
        "replacements": [
            (r"\bI want\b",     "I would appreciate it if"),
            (r"\bdo this\b",    "possibly assist with this"),
            (r"\bI need\b",     "I would kindly request"),
            (r"\bmust\b",       "might"),
            (r"\bimmediately\b","at your earliest convenience"),
            (r"\bnow\b",        "when you have a moment"),
        ],
        "explanations": [
            "Added polite, indirect framing prefix.",
            "Softened imperatives into requests.",
            "Replaced urgent language with considerate alternatives.",
        ]
    },

    "gen-z": {
        "prefix": "ok so ",
        "suffix": " fr fr 💀 no cap",
        "replacements": [
            (r"\b(very|really)\b",      "lowkey"),
            (r"\bgood\b",               "slay"),
            (r"\bgreat\b",              "bussin"),
            (r"\btrue\b",               "no cap"),
            (r"\bfriend\b",             "bestie"),
            (r"\bunderstand\b",         "get the vibe"),
            (r"\bI think\b",            "imo"),
            (r"\bhonestly\b",           "ngl"),
            (r"\bsurprising\b",         "it's giving main character"),
            (r"\bmeeting\b",            "the thing we had"),
            (r"\bproductive\b",         "actually served"),
            (r"\bnext steps\b",         "what we're doing next (slay)"),
        ],
        "explanations": [
            "Replaced standard vocabulary with Gen-Z slang.",
            "Added internet-native expressions (fr fr, no cap, bussin).",
            "Lowered register to casual online speech.",
        ]
    },

    "boomer": {
        "prefix": "",
        "suffix": "... GOD BLESS... SENT FROM MY IPAD",
        "transform": str.upper,
        "replacements": [
            (r"\.",  "..."),
            (r"\,",  ",,,"),
        ],
        "explanations": [
            "CONVERTED TEXT TO ALL CAPS.",
            "REPLACED PERIODS WITH ELLIPSES...",
            "APPENDED CLASSIC EMAIL SIGNATURE.",
        ]
    },

    "millennial": {
        "prefix": "Okay so I'm literally obsessed with the fact that ",
        "suffix": " ✨ adulting is hard but we love to see it lol",
        "replacements": [
            (r"\b(good|great)\b",       "iconic"),
            (r"\b(bad|terrible)\b",     "not it"),
            (r"\bis\b",                 "is giving"),
            (r"\b(amazing|awesome)\b",  "absolutely living for this"),
            (r"\bwork\b",               "hustle"),
            (r"\bmeeting\b",            "sync"),
            (r"\bproductive\b",         "super on-brand"),
        ],
        "explanations": [
            "Added millennial-coded prefix (literally, obsessed).",
            "Replaced adjectives with millennial equivalents (iconic, not it).",
            "Infused corporate-cool energy with '✨ adulting' suffix.",
        ]
    },
}

MOODS = [
    {"id": "formal",     "label": "Formal",     "icon": "👔", "desc": "Professional & structured"},
    {"id": "friendly",   "label": "Friendly",   "icon": "👋", "desc": "Warm & approachable"},
    {"id": "polite",     "label": "Polite",      "icon": "🙏", "desc": "Respectful & indirect"},
    {"id": "concise",    "label": "Concise",     "icon": "✂️",  "desc": "Minimalist & direct"},
    {"id": "angry",      "label": "Angry",       "icon": "🔥", "desc": "Stern & blunt"},
    {"id": "gen-z",      "label": "Gen-Z",       "icon": "💅", "desc": "Slang & chaos"},
    {"id": "boomer",     "label": "Boomer",      "icon": "👴", "desc": "Classic internet style"},
    {"id": "millennial", "label": "Millennial",  "icon": "🥑", "desc": "Corporate-cool energy"},
]

INTENSITY_LABELS = ["lightly", "moderately", "strongly"]


def apply_rules(text: str, mood: str, intensity: int = 1) -> dict:
    """
    Apply mood rules to text. Returns modified text + explanations.
    intensity: 0 = light (fewer replacements), 1 = medium, 2 = full
    """
    rules = MOOD_RULES.get(mood)
    if not rules:
        return {"modified": text, "explanations": ["Unknown mood."]}

    modified = text

    # Intensity controls how many replacements to apply
    replacements = rules["replacements"]
    if intensity == 0:
        replacements = replacements[:max(1, len(replacements) // 3)]
    elif intensity == 1:
        replacements = replacements[:max(2, len(replacements) * 2 // 3)]
    # intensity == 2 → all replacements

    for pattern, replacement in replacements:
        modified = re.sub(pattern, replacement, modified, flags=re.IGNORECASE)

    # Clean up extra whitespace from empty replacements
    modified = re.sub(r"\s{2,}", " ", modified).strip()
    modified = re.sub(r"^\s*,\s*", "", modified).strip()

    # Apply optional string transform (e.g. .upper() for Boomer)
    transform = rules.get("transform")
    if transform:
        modified = transform(modified)

    if intensity > 0 and rules.get("prefix"):
        modified = rules["prefix"] + modified
    if intensity > 0 and rules.get("suffix"):
        modified = modified + rules["suffix"]

    return {
        "modified": modified.strip(),
        "explanations": rules["explanations"],
    }


def word_diff(original: str, modified: str) -> list:
    """
    Compute a word-level diff between original and modified text.
    Returns list of dicts: {word, type} where type is 'same', 'added', or 'removed'.
    Uses LCS (Longest Common Subsequence).
    """
    old_words = original.split()
    new_words = modified.split()

    n, m = len(old_words), len(new_words)
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if old_words[i-1].lower() == new_words[j-1].lower():
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    result = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and old_words[i-1].lower() == new_words[j-1].lower():
            result.insert(0, {"word": new_words[j-1], "type": "same"})
            i -= 1; j -= 1
        elif j > 0 and (i == 0 or dp[i][j-1] >= dp[i-1][j]):
            result.insert(0, {"word": new_words[j-1], "type": "added"})
            j -= 1
        else:
            result.insert(0, {"word": old_words[i-1], "type": "removed"})
            i -= 1

    return result