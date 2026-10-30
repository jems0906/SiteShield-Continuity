from datetime import datetime, timedelta, timezone

from app.models import AlarmEvent, Asset, WorkOrder
from app.services.alarm_metrics import build_metrics, reconcile_event


def test_same_source_is_idempotent_and_distinct_activation_is_not_duplicate(client):
    _, factory = client
    with factory() as db:
        db.add(Asset(id="D-1", category="Door contact", owner="Ops", inspection_date="2026-10-01", status="Operational", site="Demo", availability=1, monitored_days=30))
        time = datetime.now(timezone.utc)
        first = {"id": "E-1", "source_record_id": "SRC-1", "asset_id": "D-1", "occurred_at": time, "classification": "unresolved", "summary": "Activation"}
        duplicate = {**first, "id": "E-2", "source_record_id": "SRC-2"}
        distinct = {**first, "id": "E-3", "source_record_id": "SRC-3", "occurred_at": time + timedelta(minutes=4)}
        row_one = reconcile_event(db, first)
        row_duplicate = reconcile_event(db, duplicate)
        row_redelivery = reconcile_event(db, first)
        row_distinct = reconcile_event(db, distinct)
        db.commit()
        assert row_duplicate.classification == "duplicate"
        assert row_duplicate.duplicate_of == "E-1"
        assert row_redelivery.id == "E-1"
        assert row_distinct.classification == "unresolved"
        assert db.query(AlarmEvent).count() == 3


def test_equivalent_timezone_offsets_match_as_duplicate(client):
    _, factory = client
    with factory() as db:
        first = {"id": "E-1", "source_record_id": "SRC-1", "asset_id": "D-1", "occurred_at": datetime.fromisoformat("2026-10-01T10:00:00+02:00"), "classification": "unresolved", "summary": "Activation"}
        same_instant = {**first, "id": "E-2", "source_record_id": "SRC-2", "occurred_at": datetime.fromisoformat("2026-10-01T08:00:00+00:00")}
        reconcile_event(db, first)
        second = reconcile_event(db, same_instant)
        assert second.classification == "duplicate"
        assert second.duplicate_of == "E-1"


def test_reconciliation_requires_timezone_aware_timestamp(client):
    _, factory = client
    with factory() as db:
        payload = {"id": "E-1", "source_record_id": "SRC-1", "asset_id": "D-1", "occurred_at": datetime(2026, 10, 1), "classification": "unresolved", "summary": "Activation"}
        try:
            reconcile_event(db, payload)
        except ValueError as exc:
            assert "timezone" in str(exc)
        else:
            raise AssertionError("Naive timestamps must be rejected")


def test_metrics_exclude_duplicate_ingestion_and_report_comparable_rate(client):
    _, factory = client
    with factory() as db:
        db.add(Asset(id="D-1", category="Door contact", owner="Ops", inspection_date="2026-10-01", status="Operational", site="Demo", availability=0.9, monitored_days=30))
        now = datetime.now(timezone.utc)
        db.add_all([
            AlarmEvent(id="E-1", source_record_id="S-1", asset_id="D-1", occurred_at=now, classification="actionable", summary="One", raw_event={}),
            AlarmEvent(id="E-2", source_record_id="S-2", asset_id="D-1", occurred_at=now, classification="duplicate", summary="One", duplicate_of="E-1", raw_event={}),
            AlarmEvent(id="E-3", source_record_id="S-3", asset_id="D-1", occurred_at=now, classification="nuisance", summary="Two", raw_event={}),
        ])
        db.commit()
        result = build_metrics(db, 30)
        assert result["event_count"] == 2
        assert result["duplicate_records_excluded"] == 1
        assert result["repeat_events"] == 1
        assert result["repeat_events_per_monitored_device_day"] == round(1 / 30, 4)
        assert result["device_availability_percent"] == 90
        assert result["monitored_device_days"] == 30
        assert result["simulated_comparison"]["is_constructed_fixture"] is True
        assert result["simulated_comparison"]["window_days_each"] == 7
        short_window = build_metrics(db, 7)
        assert short_window["monitored_device_days"] == 7
        assert short_window["repeat_events_per_monitored_device_day"] == round(1 / 7, 4)


def test_accepted_repair_closes_prior_unresolved_event(client):
    _, factory = client
    with factory() as db:
        now = datetime.now(timezone.utc)
        db.add(Asset(id="D-1", category="Door contact", owner="Ops", inspection_date="2026-10-01", status="Operational", site="Demo", availability=1, monitored_days=30))
        db.add(AlarmEvent(id="E-1", source_record_id="S-1", asset_id="D-1", occurred_at=now - timedelta(days=2), classification="unresolved", summary="Fault", raw_event={}))
        db.add(WorkOrder(id="WO-1", asset_id="D-1", title="Repair", scope="Approved", accountable_owner="Owner", scheduled_window="Window", vendor_acknowledgment="Yes", status="accepted", acceptance_criteria=[], opened_at=now - timedelta(days=3), accepted_at=now - timedelta(days=1)))
        db.commit()
        assert build_metrics(db, 30)["unresolved_faults"] == 0