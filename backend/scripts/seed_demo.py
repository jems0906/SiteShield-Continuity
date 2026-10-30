from datetime import datetime, timedelta, timezone

from app.database import SessionLocal
from app.models import AlarmEvent, Asset, AuditFinding, Exercise, Handoff, WorkOrder


def seed() -> None:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        if db.get(Asset, "DOOR-014"):
            print("Synthetic demo profile already present; no changes made.")
            return
        db.add_all([
            Asset(id="DOOR-014", category="Door contact", owner="Facilities assurance", inspection_date="2026-10-20", status="Operational; monitored", site="North Site", availability=0.982, monitored_days=30),
            Asset(id="READER-006", category="Access-control reader", owner="Access services", inspection_date="2026-10-18", status="Operational", site="North Site", availability=0.997, monitored_days=30),
            Asset(id="CAM-021", category="Camera", owner="Facilities assurance", inspection_date="2026-10-14", status="Operational", site="North Site", availability=0.994, monitored_days=30),
            Asset(id="PANEL-003", category="Alarm panel", owner="Security systems", inspection_date="2026-10-10", status="Operational", site="North Site", availability=0.999, monitored_days=30),
        ])
        db.add_all([
            AuditFinding(id="FIND-101", asset_id="DOOR-014", checklist_item="Contact registers consistently during a documented functional check", result="fail", evidence_reference="CASE-DOOR-014-OBS-01", priority="high", owner="Facilities assurance", corrective_action="Vendor inspection and approved repair; retain monitoring and verify function", status="accepted"),
            AuditFinding(id="FIND-102", asset_id="PANEL-003", checklist_item="Inspection record is current and attributable", result="pass", evidence_reference="CHECKLIST-2026-10", priority="routine", owner="Security systems", corrective_action="No action", status="closed"),
            AuditFinding(id="FIND-103", asset_id="CAM-021", checklist_item="Maintenance evidence is recorded without sensitive imagery", result="not_applicable", evidence_reference="N/A-PRIVACY", priority="routine", owner="Facilities assurance", corrective_action="Review on next scheduled audit", status="open"),
        ])
        for event_id, days_ago, classification, summary in [
            ("EV-201", 14, "nuisance", "Intermittent contact-state report"),
            ("EV-202", 13, "nuisance", "Intermittent contact-state report"),
            ("EV-203", 12, "actionable", "Door contact activation; inspection initiated"),
            ("EV-204", 11, "duplicate", "Duplicate upstream delivery retained for reconciliation"),
            ("EV-205", 10, "scheduled_test", "Documented scheduled functional test"),
            ("EV-206", 9, "unresolved", "Contact-state inconsistency; vendor diagnosis pending"),
            ("EV-207", 5, "scheduled_test", "Post-repair functional test passed; synthetic record"),
        ]:
            event_time = now - timedelta(days=days_ago)
            if event_id == "EV-204":
                event_time = now - timedelta(days=12)
                summary = "Door contact activation; inspection initiated"
            raw = {"synthetic": True, "source_record_id": f"SRC-{event_id}", "asset_id": "DOOR-014", "occurred_at": event_time.isoformat(), "classification": classification, "summary": summary}
            db.add(AlarmEvent(id=event_id, source_record_id=f"SRC-{event_id}", asset_id="DOOR-014", occurred_at=event_time, classification=classification, summary=summary, duplicate_of="EV-203" if event_id == "EV-204" else None, raw_event=raw))
        retest_time = now - timedelta(hours=20)
        db.add(AlarmEvent(id="EV-208", source_record_id="SRC-EV-208", asset_id="DOOR-014", occurred_at=retest_time, classification="scheduled_test", summary="Post-repair functional retest passed; synthetic record", raw_event={"synthetic": True, "source_record_id": "SRC-EV-208", "asset_id": "DOOR-014", "occurred_at": retest_time.isoformat(), "classification": "scheduled_test", "summary": "Post-repair functional retest passed; synthetic record"}))
        db.add(WorkOrder(
            id="WO-DOOR-014", asset_id="DOOR-014", title="Recurring contact fault: inspect and restore reliable reporting",
            scope="Inspect the fictional contact assembly, identify the cause of intermittent reports, complete the approved repair, document evidence, and return the asset to its approved monitored state. No bypass, suppression, threshold change, or disablement is authorized.",
            accountable_owner="Facilities assurance lead", scheduled_window="2026-10-24 09:00-11:00 UTC",
            vendor_acknowledgment="Acknowledged; work completed under approved scope", status="accepted",
            completion_record="Vendor recorded a loose internal termination, corrected it under the approved scope, and attached reference REPAIR-DOOR-014-02 (fictional text record; no upload endpoint).",
            acceptance_criteria=["Documented cause and repair evidence", "Successful functional retest", "Monitoring coverage reviewed and unchanged", "Reviewer acceptance recorded"],
            reviewer_acceptance="accepted",
            diagnostic={"repeated_activations": ["EV-201", "EV-202", "EV-203", "EV-206"], "hypothesis": "Intermittent connection at the contact assembly; diagnostic hypothesis only until vendor inspection.", "vendor_assessment": "Loose internal termination found during fictional inspection."},
            functional_retest={"passed": True, "coverage_reviewed": True, "notes": "Three consecutive functional checks passed; monitoring coverage remained enabled and unchanged. Synthetic fixture record.", "recorded_at": (now - timedelta(days=1)).isoformat()},
            opened_at=now - timedelta(days=18), accepted_at=now - timedelta(days=8),
            updated_at=now,
        ))
        db.add(WorkOrder(id="WO-READER-006", asset_id="READER-006", title="Scheduled reader inspection", scope="Complete the routine fictional inspection and return a text completion summary. No configuration change or access change is in scope.", accountable_owner="Access services lead", scheduled_window="2026-11-05 10:00-11:00 UTC", vendor_acknowledgment="Pending vendor acknowledgement", status="scheduled", completion_record="", acceptance_criteria=["Inspection checklist completed", "Completion summary provided"], reviewer_acceptance="pending", vendor_visible=True, opened_at=now))
        db.add(Handoff(id="HANDOFF-2026-10-29", shift="Day shift / 2026-10-29", open_incidents=["No active incident in this synthetic snapshot"], unresolved_defects=["None after accepted DOOR-014 work order"], work_in_progress=["Review next scheduled inspection for DOOR-014"], temporary_arrangements=["None; no alarm suppression or control bypass is in effect"], next_owner="Evening assurance lead", acknowledged_by=""))
        db.add(Exercise(
            id="EX-STORM-01", title="North Site access disruption: storm and vendor outage", scenario_type="discussion-based tabletop",
            timeline=[{"time": "T+00", "inject": "Severe weather disrupts normal site access; security-system vendor reports delayed availability."}, {"time": "T+15", "inject": "A critical process owner reports an access-dependent task due before the next shift."}, {"time": "T+30", "inject": "A public-facing status update is requested before facts are confirmed."}],
            decisions=[{"prompt": "Which process receives recovery priority?", "decision": "Prioritize the critical records service using the approved remote-work alternative.", "owner": "Continuity lead"}],
            communications=[{"audience": "Employees", "draft": "A weather-related access disruption is under assessment. Follow approved continuity instructions; do not travel to the site unless authorized."}, {"audience": "Vendor coordinator", "draft": "Please confirm service availability and the next update time through the approved contact channel."}],
            findings=["Vendor escalation contacts should be revalidated."], improvements=[{"action": "Confirm alternate work-location readiness", "owner": "Continuity lead", "due": "2026-11-15", "status": "open"}],
            business_impact={"critical_processes": ["Payroll processing", "Essential records access"], "dependencies": ["Approved remote workspace", "Identity service", "Vendor support"], "recovery_priorities": ["Protect employee safety", "Restore essential records workflow", "Resume noncritical work"], "approved_alternatives": ["Approved remote work", "Manual queue logging with later reconciliation"], "recovery_objectives": ["Payroll: 24-hour RTO / 1-business-day RPO (fictional tabletop target)", "Essential records: 8-hour RTO / 4-hour RPO (fictional tabletop target)"], "escalation": "Continuity lead decides on activation after consulting site leadership and vendor coordinator."},
        ))
        db.commit()
    print("Seeded synthetic SiteShield demo profile.")


if __name__ == "__main__":
    seed()