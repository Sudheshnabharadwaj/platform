"""SLA service — dynamic calculations for ticket due dates and compliance statuses."""

from datetime import datetime, timedelta, timezone

# SLA Durations based on requirements:
# LOW = 48 hours, MEDIUM = 24 hours, HIGH = 8 hours, CRITICAL = 4 hours
SLA_DURATIONS: dict[str, timedelta] = {
    "LOW": timedelta(hours=48),
    "MEDIUM": timedelta(hours=24),
    "HIGH": timedelta(hours=8),
    "CRITICAL": timedelta(hours=4),
}


def get_sla_duration(priority: str) -> timedelta:
    """Return the timedelta duration for a priority string."""
    norm = (priority or "MEDIUM").strip().upper()
    return SLA_DURATIONS.get(norm, timedelta(hours=24))


def calculate_due_date(priority: str, start_time: datetime | None = None) -> datetime:
    """Calculate the due_at timestamp when a ticket is created."""
    base_time = start_time or datetime.now(timezone.utc)
    duration = get_sla_duration(priority)
    return base_time + duration


def evaluate_sla(
    priority: str,
    created_at: datetime,
    due_at: datetime,
    status: str,
) -> tuple[str, str]:
    """Calculate the current SLA status ('Normal', 'SLA Risk', 'SLA Breached') and human readable remaining time.

    Rules:
    - If ticket is RESOLVED or CLOSED, it is not an active breach.
    - If active and current time > due_at -> 'SLA Breached'.
    - If active and remaining time <= 25% of SLA duration -> 'SLA Risk'.
    - Otherwise -> 'Normal'.
    """
    norm_status = (status or "OPEN").strip().upper()
    if norm_status in ("RESOLVED", "CLOSED"):
        return "Normal", "Completed (Within SLA)"

    now = datetime.now(timezone.utc)
    # Ensure due_at has timezone
    if due_at.tzinfo is None:
        due_at = due_at.replace(tzinfo=timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    total_duration = due_at - created_at
    remaining = due_at - now
    remaining_secs = remaining.total_seconds()
    total_secs = max(total_duration.total_seconds(), 1.0)

    if remaining_secs <= 0:
        overdue_secs = abs(remaining_secs)
        hours = int(overdue_secs // 3600)
        minutes = int((overdue_secs % 3600) // 60)
        return "SLA Breached", f"Breached by {hours}h {minutes}m"

    if remaining_secs <= (0.25 * total_secs):
        hours = int(remaining_secs // 3600)
        minutes = int((remaining_secs % 3600) // 60)
        return "SLA Risk", f"{hours}h {minutes}m remaining (At Risk)"

    hours = int(remaining_secs // 3600)
    minutes = int((remaining_secs % 3600) // 60)
    return "Normal", f"{hours}h {minutes}m remaining"
