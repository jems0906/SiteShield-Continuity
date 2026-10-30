from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AlarmEvent, Asset
from app.models import WorkOrder

CLASSIFICATIONS = {
    "actionable",
    "nuisance",
    "duplicate",
    "scheduled_test",
    "unresolved",
}


def reconcile_event(session: Session, event: dict) -> AlarmEvent:
    occurred_at = event["occurred_at"]
    if occurred_at.tzinfo is None:
        raise ValueError("occurred_at must include a timezone")
    occurred_at = occurred_at.astimezone(timezone.utc)
    pending = [row for row in session.new if isinstance(row, AlarmEvent)]
    pending_source = next((row for row in pending if row.source_record_id == event["source_record_id"]), None)
    if pending_source:
        return pending_source
    existing = session.scalar(select(AlarmEvent).where(AlarmEvent.source_record_id == event["source_record_id"]))
    if existing:
        return existing
    pending_duplicate = next(
        (row for row in pending if row.asset_id == event["asset_id"] and row.occurred_at == occurred_at and row.summary == event["summary"]),
        None,
    )
    duplicate = session.scalar(
        select(AlarmEvent).where(
            AlarmEvent.asset_id == event["asset_id"],
            AlarmEvent.occurred_at == occurred_at,
            AlarmEvent.summary == event["summary"],
        )
    )
    duplicate = duplicate or pending_duplicate
    raw_event = event.get("raw_event") or {
        key: value.isoformat() if isinstance(value, datetime) else value
        for key, value in event.items()
    }
    row = AlarmEvent(
        id=event["id"],
        source_record_id=event["source_record_id"],
        asset_id=event["asset_id"],
        occurred_at=occurred_at,
        classification="duplicate" if duplicate else event["classification"],
        summary=event["summary"],
        duplicate_of=duplicate.id if duplicate else None,
        raw_event=raw_event,
    )
    session.add(row)
    return row


def build_metrics(session: Session, window_days: int = 30) -> dict:
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=window_days)
    events = session.scalars(select(AlarmEvent).where(AlarmEvent.occurred_at >= start)).all()
    counted = [row for row in events if row.classification != "duplicate"]
    activations = [row for row in counted if row.classification != "scheduled_test"]
    assets = session.scalars(select(Asset)).all()
    by_asset = Counter(row.asset_id for row in activations)
    monitored_device_days = sum(min(asset.monitored_days, window_days) for asset in assets)
    repeat_events = sum(max(count - 1, 0) for count in by_asset.values())
    actionable = sum(row.classification == "actionable" for row in counted)
    accepted_orders = session.scalars(
        select(WorkOrder).where(WorkOrder.accepted_at.is_not(None), WorkOrder.opened_at >= start)
    ).all()
    all_accepted_orders = session.scalars(select(WorkOrder).where(WorkOrder.accepted_at.is_not(None))).all()
    unresolved_assets = {
        event.asset_id
        for event in counted
        if event.classification == "unresolved"
        and not any(
            order.asset_id == event.asset_id
            and order.accepted_at is not None
            and order.accepted_at >= event.occurred_at
            for order in all_accepted_orders
        )
    }
    repair_hours = [
        (order.accepted_at - order.opened_at).total_seconds() / 3600
        for order in accepted_orders
        if order.accepted_at and order.opened_at
    ]
    return {
        "window_days": window_days,
        "window_start": start.isoformat(),
        "window_end": end.isoformat(),
        "event_count": len(counted),
        "repeat_events": repeat_events,
        "repeat_events_per_monitored_device_day": round(repeat_events / monitored_device_days, 4) if monitored_device_days else 0,
        "monitored_device_days": monitored_device_days,
        "device_availability_percent": round(sum(asset.availability for asset in assets) / len(assets) * 100, 1) if assets else 0,
        "unresolved_faults": len(unresolved_assets),
        "mean_time_to_repair_hours": round(sum(repair_hours) / len(repair_hours), 1) if repair_hours else None,
        "confirmed_actionable_events": actionable,
        "duplicate_records_excluded": len(events) - len(counted),
        "simulated_comparison": {
            "is_constructed_fixture": True,
            "window_days_each": 7,
            "before_distinct_activations": 4,
            "after_distinct_activations": 0,
            "before_duplicate_records": 1,
            "after_duplicate_records": 0,
            "note": "Matched 7-day counts are constructed demonstration fixtures, not achieved alarm reduction or security performance.",
        },
        "definitions": {
            "repeat_events": "Distinct non-duplicate activations after the first activation for an asset in the observation window.",
            "rate": "Repeat events divided by monitored device-days across the same observation window.",
            "availability": "Mean reported availability fraction across registered assets; synthetic fixture value.",
            "unresolved_faults": "Unique assets with an unresolved event not followed by a reviewer-accepted work order.",
            "time_to_repair": "Mean elapsed hours from documented opened_at to reviewer accepted_at for accepted repairs opened within this observation window.",
        },
    }