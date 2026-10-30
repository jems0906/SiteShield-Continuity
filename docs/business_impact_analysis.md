# Business Impact Analysis

Fictional North Site scenario: storm-related access disruption coincides with delayed security-system vendor support. This is a planning exercise, not a live incident.

| Critical process | Impact if unavailable | Priority | Dependency | Approved alternative |
|---|---|---|---|---|
| Payroll processing | Missed internal processing deadline | High | Approved remote workspace, identity service | Approved remote work; maintain a reconciliation queue |
| Essential records access | Delays to time-sensitive records work | High | Identity service, records platform | Manual queue logging with later reconciliation |
| Noncritical onsite work | Temporary scheduling delay | Lower | Normal site access | Reschedule after site leadership review |

The continuity lead owns activation decisions after consultation with site leadership and the vendor coordinator. Employee safety is the first recovery priority. Fictional exercise-only planning targets are payroll RTO 24 hours / RPO 1 business day, and essential-records RTO 8 hours / RPO 4 hours. They are illustrative assumptions for this tabletop, not approved or binding operational objectives; actual targets require organization-specific impact analysis and approval.

Coordination requirements: confirm vendor service availability and next update time through approved channels; confirm the approved alternate-work arrangement; assign one accountable owner per recovery task; log decisions and timestamps; communicate only verified facts.