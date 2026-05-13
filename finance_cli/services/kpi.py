"""KPI evidence extraction services."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from finance_cli.providers.fuzzy_terms import best_fuzzy_term, has_fuzzy_term
from finance_cli.services.filings import read_filing_section
from finance_cli.services.transcripts import read_transcript, search_transcripts


DEFAULT_KPI_METRICS = [
    "arr",
    "net_new_arr",
    "large_customers",
    "million_plus_transactions",
    "emerging_products",
    "nrr",
    "revenue_growth",
    "operating_margin",
    "fcf_margin",
    "rpo",
]

KPI_FUZZY_THRESHOLD = 90.0


@dataclass(frozen=True)
class KpiSpec:
    key: str
    label: str
    keywords: tuple[str, ...]
    value_kind: str


@dataclass(frozen=True)
class KpiKeywordMatch:
    term: str
    score: float
    method: str


KPI_SPECS: dict[str, KpiSpec] = {
    "arr": KpiSpec("arr", "Annual Recurring Revenue", ("arr", "annual recurring revenue"), "money"),
    "net_new_arr": KpiSpec("net_new_arr", "Net New ARR", ("net new arr",), "money"),
    "large_customers": KpiSpec(
        "large_customers",
        "Large Customers",
        ("$100k+ arr customers", "100k+ arr customers", "large customers"),
        "number",
    ),
    "million_plus_transactions": KpiSpec(
        "million_plus_transactions",
        "$1M+ Net New ACV Transactions",
        ("$1 million+ net new acv", "1 million+ net new acv", "$1m+"),
        "number",
    ),
    "emerging_products": KpiSpec(
        "emerging_products",
        "Emerging Products Contribution",
        ("emerging products",),
        "percent",
    ),
    "nrr": KpiSpec(
        "nrr",
        "Net Retention Rate",
        ("net retention", "dollar-based net retention", "dbnrr", "nrr"),
        "percent",
    ),
    "revenue_growth": KpiSpec("revenue_growth", "Revenue Growth", ("revenue", "top-line"), "percent"),
    "operating_margin": KpiSpec("operating_margin", "Operating Margin", ("operating margin",), "percent"),
    "fcf_margin": KpiSpec(
        "fcf_margin",
        "Free Cash Flow Margin",
        ("free cash flow margin", "fcf margin"),
        "percent",
    ),
    "rpo": KpiSpec("rpo", "Remaining Performance Obligations", ("remaining performance obligations", "rpo"), "money"),
}

_SENTENCE_ABBREVIATIONS = (
    "a.m.",
    "p.m.",
    "approx.",
    "corp.",
    "dr.",
    "e.g.",
    "etc.",
    "i.e.",
    "inc.",
    "incl.",
    "ltd.",
    "mr.",
    "mrs.",
    "ms.",
    "no.",
    "u.k.",
    "u.s.",
    "vs.",
)


def extract_kpis(
    symbol: str,
    *,
    source: str = "transcripts",
    metrics: list[str] | None = None,
    limit: int = 30,
    quarter: str = "latest",
    form: str = "10-K",
) -> dict[str, Any]:
    """Extract KPI evidence from supported company research documents."""
    normalized = symbol.strip().upper()
    wanted = _resolve_metrics(metrics)
    documents = _load_documents(normalized, source=source, quarter=quarter, form=form)
    all_kpis = _extract_from_documents(documents, wanted, limit=10_000)
    kpis = all_kpis[:limit]
    return {
        "symbol": normalized,
        "source": source,
        "metrics": [spec.key for spec in wanted],
        "documents": [_document_meta(document, doc_ref=index) for index, document in enumerate(documents)],
        "kpis": kpis,
        "count": len(kpis),
        "total_count": len(all_kpis),
        "truncated": len(kpis) < len(all_kpis),
        "warnings": _missing_metric_warnings(wanted, all_kpis),
    }


def kpi_history(
    symbol: str,
    *,
    source: str = "transcripts",
    metrics: list[str] | None = None,
    limit: int = 4,
    per_document_limit: int = 20,
) -> dict[str, Any]:
    """Extract KPI evidence across recent documents."""
    normalized = symbol.strip().upper()
    wanted = _resolve_metrics(metrics)
    if source != "transcripts":
        return {
            "symbol": normalized,
            "source": source,
            "history": [],
            "count": 0,
            "warnings": ["kpi.history first pass supports source=transcripts only"],
        }
    search = search_transcripts(normalized, limit=limit)
    history = []
    for item in search.get("transcripts", []):
        document = _transcript_document(normalized, url=item["url"], quarter=item.get("quarter") or "latest")
        kpis = _extract_from_documents([document], wanted, limit=per_document_limit)
        history.append({
            "documents": [_document_meta(document, doc_ref=0)],
            "kpis": kpis,
            "count": len(kpis),
        })
    return {
        "symbol": normalized,
        "source": source,
        "metrics": [spec.key for spec in wanted],
        "history": history,
        "count": len(history),
    }


def extract_kpi_evidence(text: str, *, metrics: list[str] | None = None, source_document: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Extract KPI evidence from plain text. Exposed for focused tests and reuse."""
    specs = _resolve_metrics(metrics)
    document = source_document or {}
    rows = []
    seen: set[tuple[str, str]] = set()
    for sentence in _sentences(text):
        normalized_sentence = _normalize_for_match(sentence)
        for spec in specs:
            match = _match_spec(normalized_sentence, spec)
            if match is None:
                continue
            value = _preferred_value(sentence, spec)
            if value is None:
                continue
            key = (spec.key, sentence[:220])
            if key in seen:
                continue
            seen.add(key)
            row = {
                "metric": spec.key,
                "value": _public_value(value),
                "period": _period_from_text(sentence) or document.get("period") or document.get("quarter"),
                "evidence": sentence,
                "confidence": _confidence(sentence, spec, match=match),
                "matched_term": match.term,
                "match_score": match.score,
                "match_method": match.method,
            }
            related = _related_values(sentence, value)
            if related:
                row["related"] = related
            if "doc_ref" in document:
                row["doc_ref"] = document["doc_ref"]
            elif document:
                row["source_document"] = document
            rows.append(row)
    return rows


def _load_documents(symbol: str, *, source: str, quarter: str, form: str) -> list[dict[str, Any]]:
    source_key = source.strip().lower()
    documents: list[dict[str, Any]] = []
    if source_key in {"transcripts", "transcript", "both"}:
        documents.append(_transcript_document(symbol, quarter=quarter))
    if source_key in {"filings", "filing", "both"}:
        documents.extend(_filing_documents(symbol, form=form))
    if not documents:
        raise ValueError("source must be one of: transcripts, filings, both")
    return documents


def _transcript_document(symbol: str, *, url: str | None = None, quarter: str = "latest") -> dict[str, Any]:
    data = read_transcript(symbol, url=url, quarter=quarter, max_chars=0, include_turns=True)
    transcript = data.get("transcript", {})
    prepared_text = "\n\n".join(turn.get("text", "") for turn in data.get("prepared_remarks", []))
    text = "\n\n".join(part for part in [data.get("summary"), prepared_text or data.get("text")] if part)
    return {
        "kind": "transcript",
        "symbol": symbol,
        "title": transcript.get("title"),
        "quarter": transcript.get("quarter"),
        "period": transcript.get("quarter"),
        "published_at": transcript.get("published_at"),
        "url": transcript.get("url"),
        "source": data.get("source"),
        "text": text,
    }


def _filing_documents(symbol: str, *, form: str) -> list[dict[str, Any]]:
    documents = []
    for section in ["business", "mda", "financial_statements"]:
        data = read_filing_section(symbol=symbol, form=form, section=section, max_chars=0)
        filing = data.get("filing", {})
        documents.append({
            "kind": "filing",
            "symbol": symbol,
            "title": f"{filing.get('company')} {filing.get('form')} {section}",
            "section": section,
            "period": filing.get("period_of_report"),
            "published_at": filing.get("filing_date"),
            "url": filing.get("filing_url") or filing.get("homepage_url"),
            "source": data.get("source"),
            "text": data.get("text", ""),
        })
    return documents


def _extract_from_documents(documents: list[dict[str, Any]], specs: list[KpiSpec], *, limit: int) -> list[dict[str, Any]]:
    rows = []
    for index, document in enumerate(documents):
        rows.extend(
            extract_kpi_evidence(
                document.get("text", ""),
                metrics=[spec.key for spec in specs],
                source_document=_document_meta(document, doc_ref=index),
            )
        )
    return rows[:limit]


def _resolve_metrics(metrics: list[str] | None) -> list[KpiSpec]:
    keys = metrics or DEFAULT_KPI_METRICS
    specs = []
    for key in keys:
        normalized = key.strip().lower()
        if not normalized:
            continue
        if normalized not in KPI_SPECS:
            choices = ", ".join(KPI_SPECS)
            raise ValueError(f"unsupported metric '{key}'. Choose from: {choices}")
        specs.append(KPI_SPECS[normalized])
    return specs


def _matches_spec(sentence: str, spec: KpiSpec) -> bool:
    return _match_spec(sentence, spec) is not None


def _match_spec(sentence: str, spec: KpiSpec) -> KpiKeywordMatch | None:
    if spec.key == "arr" and has_fuzzy_term(sentence, ("net new arr",), threshold=KPI_FUZZY_THRESHOLD):
        return None
    for keyword in spec.keywords:
        if _keyword_matches(sentence, keyword):
            return KpiKeywordMatch(term=keyword, score=100.0, method="exact")
    fuzzy = best_fuzzy_term(sentence, spec.keywords)
    if fuzzy.score >= KPI_FUZZY_THRESHOLD:
        return KpiKeywordMatch(term=fuzzy.term, score=fuzzy.score, method=f"fuzzy:{fuzzy.scorer}")
    return None


def _keyword_matches(sentence: str, keyword: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(keyword).replace(r"\ ", r"\s+") + r"(?![a-z0-9])"
    return re.search(pattern, sentence) is not None


def _preferred_value(sentence: str, spec: KpiSpec) -> dict[str, Any] | None:
    values = _all_values(sentence)
    kind = spec.value_kind
    if spec.key == "rpo":
        return _rpo_value(sentence, values)
    if kind == "number":
        numeric_values = [
            value for value in values
            if value["kind"] == "number"
            and not _looks_like_date_or_year(value, sentence)
            and not _is_threshold_value(value, sentence)
        ]
        if spec.key == "large_customers":
            near_customer = _value_near_keyword(sentence, numeric_values, ("customers", "large customers"))
            if near_customer:
                return near_customer
            return None
        if spec.key == "million_plus_transactions":
            near_transaction = _value_near_keyword(sentence, numeric_values, ("transactions", "net new acv"))
            if near_transaction:
                return near_transaction
            return None
        if numeric_values:
            return numeric_values[0]
    for value in values:
        if value["kind"] == kind and not _is_threshold_value(value, sentence):
            return value
    return None


def _rpo_value(sentence: str, values: list[dict[str, Any]]) -> dict[str, Any] | None:
    lowered = sentence.lower()
    if not re.search(r"\b(?:rpo|remaining performance obligations)\b", lowered):
        return None
    if not re.search(
        r"\b(?:rpo|remaining performance obligations)\b.{0,80}\b(?:was|were|totaled|amounted to|represents?)\b",
        lowered,
    ):
        return None
    metric_position = min(
        position
        for position in [
            lowered.find("rpo"),
            lowered.find("remaining performance obligations"),
        ]
        if position >= 0
    )
    candidates = []
    for value in values:
        if value["kind"] != "money" or _is_threshold_value(value, sentence):
            continue
        position = lowered.find(str(value.get("raw", "")).strip().lower())
        if position >= metric_position:
            candidates.append((position, value))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]


def _all_values(sentence: str) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    occupied: list[tuple[int, int]] = []
    patterns = [
        ("money", re.compile(r"\$[\d,]+(?:\.\d+)?\s*(?:billion|million|thousand|bn|mm|m|b|k)?\+?", re.I)),
        ("percent", re.compile(r"\b\d+(?:\.\d+)?%")),
        ("duration", re.compile(r"\b\d+(?:\.\d+)?\s*(?:months?|years?)\b", re.I)),
        ("number", re.compile(r"\b(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*(?:billion|million|thousand|bn|mm|m|b|k)?\+?", re.I)),
    ]
    for kind, pattern in patterns:
        for match in pattern.finditer(sentence):
            if _overlaps(match.span(), occupied):
                continue
            occupied.append(match.span())
            raw = match.group(0)
            values.append({
                "raw": raw,
                "kind": kind,
                "number": _numeric_value(raw),
                "unit": _unit(raw, kind),
            })
    return values


def _public_value(value: dict[str, Any]) -> dict[str, Any]:
    public = {
        "raw": str(value.get("raw") or "").strip(),
        "number": value.get("number"),
    }
    if value.get("kind") == "money":
        public["currency"] = "USD"
    return public


def _related_values(sentence: str, primary_value: dict[str, Any]) -> list[dict[str, Any]]:
    primary_raw = str(primary_value.get("raw") or "").strip()
    values: list[dict[str, Any]] = []
    seen = {primary_raw}
    for value in _all_values(sentence):
        raw = str(value.get("raw") or "").strip()
        if not raw or raw in seen:
            continue
        seen.add(raw)
        role = _related_role(sentence, value)
        if role is None:
            continue
        item = {"v": raw, "r": role}
        desc = _related_desc(sentence, value, role)
        if desc:
            item["desc"] = desc
        values.append(item)
    return values


def _related_role(sentence: str, value: dict[str, Any]) -> str | None:
    raw = str(value.get("raw") or "").strip()
    lowered = sentence.lower()
    raw_lower = raw.lower()
    position = lowered.find(raw_lower)
    window = lowered[max(0, position - 90):position + len(raw_lower) + 90] if position >= 0 else lowered

    if re.search(r"\b\d+(?:\.\d+)?%", raw):
        if re.search(r"\b(?:year over year|y/y|yoy)\b", window):
            return "yoy"
        if re.search(r"\b(?:quarter over quarter|q/q|qoq)\b", window):
            return "qoq"
        if re.search(r"\b(?:of|from|contributed|represent(?:s|ed)?|mix)\b", window):
            return "mix"
        return "pct"
    if value.get("kind") == "duration":
        return "window"
    if _is_threshold_value(value, sentence):
        return "threshold"
    if value.get("kind") == "number" and not _looks_like_date_or_year(value, sentence):
        if re.search(r"\b(?:customers?|transactions?|deals?)\b", window):
            return "count"
    if value.get("kind") == "money":
        if re.search(r"\b(?:recognize|recognized|remaining balance|next|over)\b", window):
            return "window_value"
    return None


def _related_desc(sentence: str, value: dict[str, Any], role: str) -> str | None:
    lowered = sentence.lower()
    raw = str(value.get("raw") or "").strip().lower()
    position = lowered.find(raw)
    window = lowered[max(0, position - 80):position + len(raw) + 80] if position >= 0 else lowered
    if role == "threshold":
        if "arr customer" in window or "arr customers" in window:
            return "ARR customers"
        if "net new acv" in window:
            return "net new ACV"
        if "customer" in window:
            return "customers"
        if "transaction" in window:
            return "transactions"
    if role == "count":
        if "customer" in window:
            return "customers"
        if "transaction" in window:
            return "transactions"
        if "deal" in window:
            return "deals"
    if role == "window_value" and "recognize" in window:
        return "revenue recognition"
    return None


def _numeric_value(raw: str) -> float | None:
    match = re.search(r"\d[\d,]*(?:\.\d+)?", raw)
    if not match:
        return None
    number = float(match.group(0).replace(",", ""))
    lower = raw.lower()
    multiplier = 1.0
    if any(unit in lower for unit in ["billion", "bn"]):
        multiplier = 1_000_000_000.0
    elif re.search(r"\bb\b", lower):
        multiplier = 1_000_000_000.0
    elif any(unit in lower for unit in ["million", "mm"]):
        multiplier = 1_000_000.0
    elif re.search(r"\bm\b", lower):
        multiplier = 1_000_000.0
    elif any(unit in lower for unit in ["thousand"]):
        multiplier = 1_000.0
    elif re.search(r"\d\s*k\+?$", lower):
        multiplier = 1_000.0
    if "%" in raw:
        return number
    return number * multiplier


def _unit(raw: str, kind: str) -> str:
    if kind == "percent":
        return "%"
    if kind == "duration":
        return "duration"
    lower = raw.lower()
    for unit in ["billion", "million", "thousand", "bn", "mm", "m", "b", "k"]:
        if re.search(rf"{re.escape(unit)}\+?$", lower) or re.search(rf"\b{re.escape(unit)}\b", lower):
            return unit
    return "count" if kind == "number" else "currency"


def _overlaps(span: tuple[int, int], occupied: list[tuple[int, int]]) -> bool:
    return any(span[0] < existing[1] and existing[0] < span[1] for existing in occupied)


def _looks_like_date_or_year(value: dict[str, Any], sentence: str = "") -> bool:
    number = value.get("number")
    if not isinstance(number, (int, float)):
        return False
    if 1900 <= number <= 2100 or str(value.get("raw", "")).strip().endswith(","):
        return True
    if 1 <= number <= 31 and re.search(
        r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b",
        sentence,
        re.I,
    ):
        return True
    return False


def _is_threshold_value(value: dict[str, Any], sentence: str) -> bool:
    raw = str(value.get("raw", "")).strip().lower()
    lowered = sentence.lower()
    threshold_context = ("customer", "arr customer", "transaction", "net new acv")
    if "+" in raw:
        return any(context in lowered for context in threshold_context)
    if value.get("kind") != "money":
        return False
    number = value.get("number")
    if not isinstance(number, (int, float)) or number > 1_000_000:
        return False
    position = lowered.find(raw)
    if position < 0:
        return False
    window = lowered[max(0, position - 80):position + len(raw) + 80]
    has_threshold_language = re.search(
        r"\b(?:more than|greater than|at least|over|above|minimum|threshold|definition|versus|vs\.?)\b",
        window,
    )
    has_threshold_context = re.search(
        r"\b(?:customers?|core customers?|arr customers?|transactions?|deals?|acv)\b",
        window,
    )
    return bool(has_threshold_language and has_threshold_context)


def _value_near_keyword(sentence: str, values: list[dict[str, Any]], keywords: tuple[str, ...]) -> dict[str, Any] | None:
    if not values:
        return None
    lowered = sentence.lower()
    keyword_positions = [lowered.find(keyword) for keyword in keywords if lowered.find(keyword) >= 0]
    if not keyword_positions:
        fuzzy = best_fuzzy_term(lowered, keywords)
        if fuzzy.score >= KPI_FUZZY_THRESHOLD and len(values) == 1:
            return values[0]
        return None
    scored = []
    for value in values:
        raw = str(value.get("raw", "")).strip()
        position = lowered.find(raw.lower())
        if position < 0:
            continue
        scored.append((min(abs(position - keyword_position) for keyword_position in keyword_positions), value))
    if not scored:
        return None
    scored.sort(key=lambda item: item[0])
    return scored[0][1]


def _sentences(text: str) -> list[str]:
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean:
        return []
    protected = _protect_sentence_abbreviations(clean)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z$0-9])", protected)
    return [_restore_sentence_abbreviations(part.strip()) for part in parts if len(part.strip()) >= 20]


def _protect_sentence_abbreviations(text: str) -> str:
    protected = text
    for abbreviation in _SENTENCE_ABBREVIATIONS:
        protected = re.sub(
            re.escape(abbreviation),
            lambda match: match.group(0).replace(".", "<DOT>"),
            protected,
            flags=re.I,
        )
    return protected


def _restore_sentence_abbreviations(text: str) -> str:
    return text.replace("<DOT>", ".")


def _normalize_for_match(text: str) -> str:
    return text.lower().replace("\u00a0", " ")


def _period_from_text(text: str) -> str | None:
    quarter = re.search(r"\bQ([1-4])\s*(?:FY)?\s*(20\d{2})\b", text, re.I)
    if quarter:
        return f"Q{quarter.group(1)} {quarter.group(2)}"
    fiscal = re.search(r"\bFY\s*(20\d{2})\b", text, re.I)
    if fiscal:
        return f"FY {fiscal.group(1)}"
    year = re.search(r"\bfiscal year\s+(20\d{2})\b", text, re.I)
    if year:
        return f"FY {year.group(1)}"
    return None


def _confidence(sentence: str, spec: KpiSpec, *, match: KpiKeywordMatch | None = None) -> str:
    normalized = _normalize_for_match(sentence)
    metric_match = match or _match_spec(normalized, spec)
    has_metric = metric_match is not None
    has_value = _preferred_value(sentence, spec) is not None
    if has_metric and has_value and len(sentence) < 500 and metric_match and metric_match.score >= 95:
        return "medium"
    if has_metric and has_value:
        return "low"
    return "very_low"


def _document_meta(document: dict[str, Any], *, doc_ref: int | None = None) -> dict[str, Any]:
    meta = {
        key: value
        for key, value in document.items()
        if key in {"kind", "symbol", "title", "quarter", "section", "period", "published_at", "url", "source"}
    }
    if doc_ref is not None:
        meta = {"doc_ref": doc_ref, **meta}
    return meta


def _missing_metric_warnings(specs: list[KpiSpec], kpis: list[dict[str, Any]]) -> list[str]:
    found = {row["metric"] for row in kpis}
    return [f"no evidence found for {spec.key}" for spec in specs if spec.key not in found]
