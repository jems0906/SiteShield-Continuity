import pytest
from fastapi import HTTPException

from conftest import auth_context
from app.models import WorkOrder
from app.services.work_order_workflow import accept_work_order


def test_acceptance_requires_completed_work_and_successful_retest(client):
    _, factory = client
    with factory() as db:
        order = WorkOrder(id="WO-1", asset_id="D-1", title="Repair", scope="Approved scope", accountable_owner="Owner", scheduled_window="Window", vendor_acknowledgment="Yes", status="in_progress", acceptance_criteria=[])
        with pytest.raises(HTTPException) as pending:
            accept_work_order(db, order, "reviewer", {"functional_retest": True, "coverage_reviewed": True})
        assert pending.value.status_code == 409
        order.status = "completed"
        with pytest.raises(HTTPException) as no_retest:
            accept_work_order(db, order, "reviewer", {"functional_retest": False, "coverage_reviewed": True})
        assert no_retest.value.status_code == 422
        with pytest.raises(HTTPException) as no_coverage:
            accept_work_order(db, order, "reviewer", {"functional_retest": True, "coverage_reviewed": False})
        assert no_coverage.value.status_code == 422
        accept_work_order(db, order, "reviewer", {"functional_retest": True, "coverage_reviewed": True, "notes": "Three checks passed"})
        assert order.status == "accepted"
        assert order.reviewer_acceptance == "accepted"
        assert order.functional_retest["passed"] is True


def test_vendor_cannot_see_unassigned_confidential_case(client):
    client_api, factory = client
    headers, cookies = auth_context(factory, "vendor")
    response = client_api.get("/api/work-orders", headers=headers, cookies=cookies)
    assert response.status_code == 200
    assert response.json() == []


def test_only_reviewer_can_accept_work(client):
    client_api, factory = client
    headers, cookies = auth_context(factory, "analyst", write=True)
    response = client_api.post("/api/work-orders/WO-1/accept", json={"functional_retest": True, "coverage_reviewed": True, "notes": "Retest evidence reviewed"}, headers=headers, cookies=cookies)
    assert response.status_code == 403


def test_vendor_work_order_transition_requires_acknowledgement_and_records_completion(client):
    client_api, factory = client
    with factory() as db:
        db.add(WorkOrder(id="WO-VISIBLE", asset_id="D-1", title="Scheduled inspection", scope="Routine inspection", accountable_owner="Owner", scheduled_window="Window", vendor_acknowledgment="Pending", status="scheduled", acceptance_criteria=[], vendor_visible=True))
        db.commit()
    headers, cookies = auth_context(factory, "vendor", write=True)
    completion = {"completion_record": "Inspection completed and returned to owner.", "vendor_assessment": "No defect observed during this fictional inspection.", "repair_evidence_reference": "TEXT-REF-01"}
    premature = client_api.post("/api/work-orders/WO-VISIBLE/complete", json=completion, headers=headers, cookies=cookies)
    assert premature.status_code == 409
    acknowledged = client_api.post("/api/work-orders/WO-VISIBLE/acknowledge", headers=headers, cookies=cookies)
    assert acknowledged.status_code == 200
    completed = client_api.post("/api/work-orders/WO-VISIBLE/complete", json=completion, headers=headers, cookies=cookies)
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert completed.json()["diagnostic"]["repair_evidence_reference"] == "TEXT-REF-01"
    reviewer_headers, reviewer_cookies = auth_context(factory, "reviewer", write=True)
    reviewer_cannot_edit_completion = client_api.post("/api/work-orders/WO-VISIBLE/complete", json=completion, headers=reviewer_headers, cookies=reviewer_cookies)
    assert reviewer_cannot_edit_completion.status_code == 403


def test_alarm_import_rejects_timezone_naive_timestamp(client):
    client_api, factory = client
    headers, cookies = auth_context(factory, "analyst", write=True)
    response = client_api.post("/api/alarms/import", headers=headers, cookies=cookies, json={"id": "E-1", "source_record_id": "SRC-1", "asset_id": "D-1", "occurred_at": "2026-10-01T10:00:00", "classification": "unresolved", "summary": "Activation"})
    assert response.status_code == 422