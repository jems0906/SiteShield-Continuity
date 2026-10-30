from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AlarmImport(BaseModel):
    id: str
    source_record_id: str
    asset_id: str
    occurred_at: datetime
    classification: str
    summary: str
    raw_event: dict = Field(default_factory=dict)

    @field_validator("occurred_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("occurred_at must include a timezone")
        return value


class WorkCompletion(BaseModel):
    completion_record: str = Field(min_length=8, max_length=4000)
    vendor_assessment: str = Field(min_length=3, max_length=1000)
    repair_evidence_reference: str = Field(min_length=3, max_length=160)


class Acceptance(BaseModel):
    functional_retest: bool
    coverage_reviewed: bool
    notes: str = Field(min_length=8, max_length=1000)


class Decision(BaseModel):
    prompt: str
    decision: str
    owner: str