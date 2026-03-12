"""
Optional load estimation module.

Estimates QPS, storage, and bandwidth from scale assumptions and requirements.
Can be used by the formatter or API to enrich the output.
"""

import re
from dataclasses import dataclass
from typing import Any


@dataclass
class LoadEstimate:
    """Rough load estimates for capacity planning."""

    qps_estimate: int
    qps_note: str
    storage_gb_estimate: int
    storage_note: str
    bandwidth_mbps_estimate: float
    bandwidth_note: str


def estimate_load(
    scale_assumptions: list[str],
    requirements_summary: str,
    default_qps: int = 1000,
    default_storage_gb: int = 100,
) -> LoadEstimate:
    """
    Produce a rough load estimate from scale assumptions and summary.
    Uses heuristics when no explicit numbers are found.
    """
    qps = default_qps
    storage_gb = default_storage_gb
    bandwidth_mbps = 100.0
    qps_note = "Default assumption; refine from scale_assumptions."
    storage_note = "Default assumption; refine from data volume."
    bandwidth_note = "Default assumption; refine from traffic."

    text = " ".join(scale_assumptions).lower() + " " + (requirements_summary or "").lower()
    # Heuristic: look for patterns like "X QPS", "X requests/sec", "X users", "X GB"
    qps_m = re.search(r"(\d+)\s*(?:qps|requests?/s|rps|req/s)", text, re.I)
    if qps_m:
        qps = int(qps_m.group(1))
        qps_note = "Derived from scale assumptions."
    users_m = re.search(r"(\d+)\s*(?:m|million|k|thousand)?\s*users?", text, re.I)
    if users_m:
        u = int(users_m.group(1))
        if "m" in text[users_m.start() : users_m.end() + 5] or "million" in text:
            u = u * 1_000_000
        elif "k" in text[users_m.start() : users_m.end() + 5] or "thousand" in text:
            u = u * 1_000
        if u > 0:
            qps = max(qps, u // 10000)  # rough: 0.01% of users active per second
            qps_note = "Derived from user scale."
    storage_m = re.search(r"(\d+)\s*(?:gb|tb|pb)", text, re.I)
    if storage_m:
        storage_gb = int(storage_m.group(1))
        if "tb" in text[storage_m.start() : storage_m.end() + 3]:
            storage_gb *= 1024
        elif "pb" in text[storage_m.start() : storage_m.end() + 3]:
            storage_gb *= 1024 * 1024
        storage_note = "Derived from scale assumptions."

    return LoadEstimate(
        qps_estimate=qps,
        qps_note=qps_note,
        storage_gb_estimate=storage_gb,
        storage_note=storage_note,
        bandwidth_mbps_estimate=bandwidth_mbps,
        bandwidth_note=bandwidth_note,
    )
