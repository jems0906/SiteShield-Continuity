import { useEffect, useState } from 'react'
import {
  Activity, AlarmClock, ArrowDownRight, ArrowUpRight, BadgeCheck, BookOpen,
  Boxes, BriefcaseBusiness, Check, ChevronDown, ClipboardCheck, CloudSun,
  FileClock, FileText, Gauge, Handshake, LayoutDashboard, Menu, ShieldCheck,
  Siren, Users, X,
} from 'lucide-react'
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { getJson, postJson, type Asset, type EventRecord, type Exercise, type Finding, type Handoff, type Metrics, type Role, type WorkOrder } from './api/client'

type Section = 'Overview' | 'Asset register' | 'Security audits' | 'Alarm analysis' | 'Vendor work' | 'Shift handoff' | 'Continuity & exercises' | 'Awareness library'
type IconType = typeof LayoutDashboard

const navigation: { name: Section; icon: IconType }[] = [
  { name: 'Overview', icon: LayoutDashboard },
  { name: 'Asset register', icon: Boxes },
  { name: 'Security audits', icon: ClipboardCheck },
  { name: 'Alarm analysis', icon: Activity },
  { name: 'Vendor work', icon: Handshake },
  { name: 'Shift handoff', icon: FileClock },
  { name: 'Continuity & exercises', icon: CloudSun },
  { name: 'Awareness library', icon: BookOpen },
]

const awareness = [
  { title: 'Accurate reporting', tag: 'RECORDS', copy: 'Record what was observed, when it occurred, and what is not yet known. Separate direct observation from interpretation; preserve the original event record.' },
  { title: 'Confidentiality', tag: 'DATA CARE', copy: 'Use only approved case references. Avoid personal details, floor plans, access credentials, device endpoints, and sensitive images in routine maintenance notes.' },
  { title: 'Escalation', tag: 'DECISIONS', copy: 'Escalate through authorized employer channels when safety, service continuity, or monitoring coverage is uncertain. Record who made the decision and when.' },
  { title: 'Handoff quality', tag: 'SHIFT CHANGE', copy: 'State open items, accountable next owner, deadlines, temporary arrangements, and explicit acknowledgement. Do not describe an unverified mitigation as completed.' },
]

const trend = [
  { week: 'Oct 01', total: 0 }, { week: 'Oct 05', total: 1 }, { week: 'Oct 09', total: 2 },
  { week: 'Oct 13', total: 3 }, { week: 'Oct 17', total: 2 }, { week: 'Oct 21', total: 2 }, { week: 'Oct 25', total: 1 },
]

function App() {
  const [section, setSection] = useState<Section>('Overview')
  const [role, setRole] = useState<Role>('leadership')
  const [mobileNav, setMobileNav] = useState(false)
  const [assets, setAssets] = useState<Asset[]>([])
  const [events, setEvents] = useState<EventRecord[]>([])
  const [findings, setFindings] = useState<Finding[]>([])
  const [orders, setOrders] = useState<WorkOrder[]>([])
  const [handoffs, setHandoffs] = useState<Handoff[]>([])
  const [exercises, setExercises] = useState<Exercise[]>([])
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [apiError, setApiError] = useState(false)
  const [notice, setNotice] = useState('')

  async function refresh(nextRole = role) {
    try {
      const [assetRows, eventRows, findingRows, orderRows, handoffRows, exerciseRows, metricRows] = await Promise.all([
        getJson<Asset[]>('/assets', nextRole), getJson<EventRecord[]>('/alarms', nextRole),
        getJson<Finding[]>('/audits', nextRole), getJson<WorkOrder[]>('/work-orders', nextRole),
        getJson<Handoff[]>('/handoffs', nextRole), getJson<Exercise[]>('/exercises', nextRole),
        getJson<Metrics>('/alarms/metrics', nextRole),
      ])
      setAssets(assetRows); setEvents(eventRows); setFindings(findingRows); setOrders(orderRows)
      setHandoffs(handoffRows); setExercises(exerciseRows); setMetrics(metricRows); setApiError(false)
    } catch {
      setApiError(true)
    }
  }

  useEffect(() => { void refresh() }, [role])

  async function acknowledgeHandoff(id: string) {
    try {
      await postJson(`/handoffs/${id}/acknowledge`, role)
      setNotice('Handoff acknowledgement recorded.');
      await refresh()
    } catch { setNotice('This role cannot acknowledge the handoff.') }
  }

  const exercise = exercises[0]
  const current = new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileNav ? 'sidebar-open' : ''}`}>
        <div className="brand-lockup">
          <div className="brand-mark"><ShieldCheck size={22} strokeWidth={2.2} /></div>
          <div><strong>SiteShield</strong><span>CONTINUITY</span></div>
          <button className="icon-button mobile-close" aria-label="Close navigation" onClick={() => setMobileNav(false)}><X size={18} /></button>
        </div>
        <div className="workspace-switch"><div className="workspace-glyph">N</div><div><span>WORKSPACE</span><strong>North Site · Demo</strong></div><ChevronDown size={15} /></div>
        <p className="nav-caption">ASSURANCE DESK</p>
        <nav aria-label="Primary navigation">
          {navigation.map(({ name, icon: Icon }) => <button key={name} className={`nav-link ${section === name ? 'active' : ''}`} onClick={() => { setSection(name); setMobileNav(false) }}><Icon size={17} strokeWidth={1.8} /><span>{name}</span>{name === 'Security audits' && findings.some((item) => item.result === 'fail') && <i className="nav-dot" />}</button>)}
        </nav>
        <div className="sidebar-bottom">
          <div className="coverage-note"><div className="coverage-icon"><BadgeCheck size={16} /></div><div><strong>Coverage intact</strong><span>All demo systems monitored</span></div></div>
          <div className="profile-row"><div className="avatar">{role[0].toUpperCase()}</div><div><strong>{roleLabel(role)}</strong><span>DEMO PERMISSION</span></div><ChevronDown size={14} /></div>
        </div>
      </aside>
      {mobileNav && <button className="scrim" aria-label="Close navigation" onClick={() => setMobileNav(false)} />}

      <main className="main-area">
        <header className="topbar">
          <div className="crumb"><button className="icon-button mobile-menu" aria-label="Open navigation" onClick={() => setMobileNav(true)}><Menu size={19} /></button><span>North Site</span><span className="crumb-slash">/</span><strong>{section}</strong></div>
          <div className="top-actions"><span className="demo-chip"><span /> SYNTHETIC DEMO</span><label className="role-select"><Users size={15} /><span className="sr-only">Demo role</span><select value={role} onChange={(event) => setRole(event.target.value as Role)} aria-label="Demo role"><option value="leadership">Leadership view</option><option value="analyst">Analyst view</option><option value="reviewer">Reviewer view</option><option value="vendor">Vendor view</option></select><ChevronDown size={13} /></label><span className="today-label">{current}</span></div>
        </header>
        <div className="page-content">
          {apiError && <div className="api-banner"><span>The API is unavailable. Start the backend and seed the synthetic profile to load workspace records.</span><button onClick={() => void refresh()}>Retry</button></div>}
          {notice && <button className="toast" onClick={() => setNotice('')}><Check size={15} />{notice}<X size={14} /></button>}
          {section === 'Overview' && <Overview assets={assets} events={events} findings={findings} orders={orders} metrics={metrics} onNavigate={setSection} />}
          {section === 'Asset register' && <AssetRegister assets={assets} />}
          {section === 'Security audits' && <AuditView findings={findings} />}
          {section === 'Alarm analysis' && <AlarmView events={events} metrics={metrics} />}
          {section === 'Vendor work' && <WorkView orders={orders} role={role} onRefresh={() => refresh()} onNotice={setNotice} />}
          {section === 'Shift handoff' && <HandoffView handoffs={handoffs} onAcknowledge={acknowledgeHandoff} role={role} />}
          {section === 'Continuity & exercises' && <ContinuityView exercise={exercise} />}
          {section === 'Awareness library' && <AwarenessView />}
          <footer className="page-footer"><span>SiteShield Continuity <b>·</b> assurance and preparedness</span><span>Fictional data only <b>·</b> Not an alarm controller</span></footer>
        </div>
      </main>
    </div>
  )
}

function roleLabel(role: Role) { return ({ analyst: 'Case analyst', reviewer: 'Assurance reviewer', vendor: 'Service vendor', leadership: 'Read-only leadership' })[role] }

function PageTitle({ eyebrow, title, copy, action }: { eyebrow: string; title: string; copy: string; action?: React.ReactNode }) {
  return <div className="page-title"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="page-description">{copy}</p></div>{action && <div className="title-action">{action}</div>}</div>
}

function MetricCard({ label, value, detail, icon: Icon, tone = 'green' }: { label: string; value: string; detail: string; icon: IconType; tone?: string }) {
  return <article className="metric-card"><div className={`metric-icon ${tone}`}><Icon size={18} /></div><p>{label}</p><strong>{value}</strong><span>{detail}</span></article>
}

function Overview({ assets, events, findings, orders, metrics, onNavigate }: { assets: Asset[]; events: EventRecord[]; findings: Finding[]; orders: WorkOrder[]; metrics: Metrics | null; onNavigate: (section: Section) => void }) {
  const doorOrder = orders.find((order) => order.asset_id === 'DOOR-014')
  const counts = events.reduce<Record<string, number>>((acc, event) => { acc[event.classification] = (acc[event.classification] ?? 0) + 1; return acc }, {})
  return <>
    <PageTitle eyebrow="THURSDAY · ASSURANCE SNAPSHOT" title="Good morning, team." copy="A clear view of equipment health, open corrective work, and continuity readiness." action={<button className="button-secondary" onClick={() => onNavigate('Continuity & exercises')}><FileText size={16} /> View exercise report</button>} />
    <div className="callout-banner"><div className="callout-icon"><ShieldCheck size={20} /></div><div><strong>Coverage remains enabled across all {assets.length} fictional assets</strong><span>Door-contact case closed after vendor repair, functional retest, and monitoring coverage review.</span></div><span className="callout-status"><Check size={14} /> REVIEWED</span></div>
    <div className="metric-grid">
      <MetricCard label="DEVICE AVAILABILITY" value={`${metrics?.device_availability_percent ?? 99.3}%`} detail="Mean across registered demo assets" icon={Gauge} tone="green" />
      <MetricCard label="REPEAT EVENT RATE" value={`${metrics?.repeat_events_per_monitored_device_day ?? '0.10'}`} detail="Repeat events / monitored device-day" icon={Activity} tone="blue" />
      <MetricCard label="UNRESOLVED FAULTS" value={String(metrics?.unresolved_faults ?? 1)} detail="Current synthetic observation window" icon={Siren} tone="amber" />
      <MetricCard label="OPEN AUDIT ACTIONS" value={String(findings.filter((item) => item.status !== 'closed').length)} detail="Assigned corrective actions" icon={ClipboardCheck} tone="coral" />
    </div>
    <div className="section-heading"><div><h2>Assurance activity</h2><p>Constructed fixtures · matched 30-day observation windows</p></div><button className="text-button" onClick={() => onNavigate('Alarm analysis')}>Open event analysis <ArrowUpRight size={15} /></button></div>
    <div className="dashboard-grid">
      <section className="panel chart-panel"><div className="panel-heading"><div><h3>Event history</h3><span>Classified synthetic records · Oct 2026</span></div><span className="mini-label">SIMULATED</span></div><div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><AreaChart data={trend} margin={{ top: 12, right: 12, left: -20, bottom: 0 }}><defs><linearGradient id="eventFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#2a7b65" stopOpacity={0.22} /><stop offset="100%" stopColor="#2a7b65" stopOpacity={0.01} /></linearGradient></defs><CartesianGrid vertical={false} stroke="#e9ede7" /><XAxis dataKey="week" axisLine={false} tickLine={false} tick={{ fill: '#88928b', fontSize: 11 }} /><YAxis allowDecimals={false} axisLine={false} tickLine={false} tick={{ fill: '#88928b', fontSize: 11 }} /><Tooltip contentStyle={{ border: '1px solid #e4e9e2', borderRadius: 6, boxShadow: '0 8px 24px #17251d12' }} /><Area type="monotone" dataKey="total" stroke="#26765f" strokeWidth={2.5} fill="url(#eventFill)" /></AreaChart></ResponsiveContainer></div><div className="chart-note"><span>Historical volume is a fixture, not an achieved reduction.</span><span>{metrics?.window_days ?? 30}-day window</span></div></section>
      <section className="panel classification-panel"><div className="panel-heading"><div><h3>Classification split</h3><span>Retained records in current snapshot</span></div><AlarmClock size={17} className="quiet-icon" /></div><div className="classification-list">{[['Actionable', counts.actionable ?? 1, 'class-actionable'], ['Nuisance', counts.nuisance ?? 3, 'class-nuisance'], ['Duplicates', counts.duplicate ?? 1, 'class-duplicate'], ['Scheduled tests', counts.scheduled_test ?? 1, 'class-test'], ['Unresolved', counts.unresolved ?? 1, 'class-open']].map(([label, count, className]) => <div className="class-row" key={label as string}><span className={`class-dot ${className}`} /><span>{label}</span><strong>{count}</strong></div>)}</div><div className="classification-foot"><Check size={14} /> Duplicate ingestion is retained separately from repeated activations.</div></section>
    </div>
    <div className="section-heading lower-heading"><div><h2>Cases needing attention</h2><p>Evidence-led maintenance and accountability</p></div><button className="text-button" onClick={() => onNavigate('Vendor work')}>All work orders <ArrowUpRight size={15} /></button></div>
    <section className="panel case-row"><div className="case-symbol"><Activity size={18} /></div><div className="case-copy"><span className="case-id">CASE · DOOR-014</span><strong>Recurring door-contact fault</strong><span>Repair accepted · functional retest passed · coverage reviewed</span></div><div className="case-meta"><span className="status-pill status-green">{doorOrder?.status ?? 'accepted'}</span><small>{events.filter((event) => event.asset_id === 'DOOR-014').length} synthetic event records</small></div><button className="icon-button case-open" aria-label="Open work orders" onClick={() => onNavigate('Vendor work')}><ArrowUpRight size={17} /></button></section>
    <p className="simulated-note"><ArrowDownRight size={14} /> Before/after counts in this workspace are constructed fixtures. Lower event volume alone does not establish improved security.</p>
  </>
}

function DataTable({ headers, children }: { headers: string[]; children: React.ReactNode }) {
  return <div className="table-scroll"><table><thead><tr>{headers.map((header) => <th key={header}>{header}</th>)}</tr></thead><tbody>{children}</tbody></table></div>
}

function AssetRegister({ assets }: { assets: Asset[] }) {
  return <><PageTitle eyebrow="INVENTORY · FICTIONAL SITES" title="Asset register" copy="Generic equipment inventory, ownership, inspection date, and current status." action={<span className="count-chip">{assets.length} registered assets</span>} /><section className="panel table-panel"><DataTable headers={['ASSET', 'CATEGORY', 'ACCOUNTABLE OWNER', 'LAST INSPECTION', 'STATUS', 'AVAILABILITY']}>
    {assets.map((asset) => <tr key={asset.id}><td><strong className="table-primary">{asset.id}</strong><small>{asset.site}</small></td><td>{asset.category}</td><td>{asset.owner}</td><td>{asset.inspection_date}</td><td><span className="status-pill status-green"><span className="status-dot" />{asset.status}</span></td><td>{(asset.availability * 100).toFixed(1)}%</td></tr>)}
  </DataTable><div className="table-footnote">Generic fictional identifiers only. No real device endpoints, credentials, coverage maps, or network details.</div></section><div className="inline-alert"><ShieldCheck size={17} /><span>Asset states are for maintenance coordination. This workspace cannot issue device commands or change alarm configuration.</span></div></>
}

function AuditView({ findings }: { findings: Finding[] }) {
  return <><PageTitle eyebrow="CONTROL CHECKS · CORRECTIVE ACTIONS" title="Security audits" copy="Checklist observations linked to evidence references, priority, owner, and corrective follow-up." action={<span className="count-chip">{findings.length} findings</span>} /><div className="audit-summary"><div><span>PASS</span><strong>{findings.filter((item) => item.result === 'pass').length}</strong></div><div><span>FAIL</span><strong>{findings.filter((item) => item.result === 'fail').length}</strong></div><div><span>NOT APPLICABLE</span><strong>{findings.filter((item) => item.result === 'not_applicable').length}</strong></div><p>Checklist responses are documented; N/A requires a recorded rationale.</p></div><section className="panel table-panel"><DataTable headers={['FINDING / ASSET', 'CHECKLIST OBSERVATION', 'RESULT', 'PRIORITY', 'OWNER', 'CORRECTIVE ACTION']}>
    {findings.map((item) => <tr key={item.id}><td><strong className="table-primary">{item.id}</strong><small>{item.asset_id} · {item.status}</small></td><td className="wrap-cell">{item.checklist_item}<small>Evidence: {item.evidence_reference ?? 'Not provided'}</small></td><td><span className={`result-pill result-${item.result}`}>{item.result.replace('_', ' ')}</span></td><td>{item.priority}</td><td>{item.owner}</td><td className="wrap-cell">{item.corrective_action}</td></tr>)}
  </DataTable><div className="table-footnote">Evidence is recorded as text references only; the application does not accept arbitrary evidence uploads.</div></section></>
}

function AlarmView({ events, metrics }: { events: EventRecord[]; metrics: Metrics | null }) {
  const labels: Record<string, string> = { actionable: 'Confirmed actionable', nuisance: 'Confirmed nuisance', duplicate: 'Duplicate ingestion', scheduled_test: 'Scheduled test', unresolved: 'Unresolved' }
  return <><PageTitle eyebrow="EVENT RECONCILIATION · MATCHED WINDOWS" title="Alarm analysis" copy="Retain raw synthetic records while distinguishing duplicates from distinct activations." action={<span className="mini-label">DEMO DATA</span>} /><div className="metric-grid compact-grid"><MetricCard label="EVENTS IN WINDOW" value={String(metrics?.event_count ?? events.length)} detail={`${metrics?.window_days ?? 30}-day observation window`} icon={Activity} /><MetricCard label="DUPLICATE RECORDS" value={String(metrics?.duplicate_records_excluded ?? 0)} detail="Retained, excluded from activation counts" icon={FileText} tone="blue" /><MetricCard label="ACTIONABLE EVENTS" value={String(metrics?.confirmed_actionable_events ?? 0)} detail="Confirmed distinct activations" icon={Siren} tone="coral" /><MetricCard label="AVAILABILITY" value={`${metrics?.device_availability_percent ?? 0}%`} detail="Mean across registered assets" icon={Gauge} tone="green" /></div><section className="panel table-panel"><div className="panel-heading panel-heading-inset"><div><h3>Raw event ledger</h3><span>Original source IDs and classifications are preserved</span></div></div><DataTable headers={['EVENT / SOURCE', 'ASSET', 'OCCURRED AT', 'CLASSIFICATION', 'SUMMARY', 'RECONCILIATION']}>
    {events.map((event) => <tr key={event.id}><td><strong className="table-primary">{event.id}</strong><small>{event.source_record_id}</small></td><td>{event.asset_id}</td><td>{new Date(event.occurred_at).toLocaleString()}</td><td><span className={`result-pill result-${event.classification}`}>{labels[event.classification] ?? event.classification}</span></td><td className="wrap-cell">{event.summary}</td><td>{event.duplicate_of ? `Duplicate of ${event.duplicate_of}` : 'Distinct record'}</td></tr>)}
  </DataTable></section><div className="comparison-strip"><div><span>MATCHED WINDOW · BEFORE</span><strong>{metrics?.simulated_comparison.before_distinct_activations ?? 4} distinct activations</strong><small>{metrics?.simulated_comparison.before_duplicate_records ?? 1} duplicate ingestion record</small></div><div className="comparison-arrow"><ArrowDownRight size={17} /></div><div><span>MATCHED WINDOW · AFTER</span><strong>{metrics?.simulated_comparison.after_distinct_activations ?? 0} distinct activations</strong><small>{metrics?.simulated_comparison.after_duplicate_records ?? 0} duplicate ingestion records</small></div><p>{metrics?.simulated_comparison.note ?? 'Constructed fixtures only; not achieved alarm reduction.'} Both windows: {metrics?.simulated_comparison.window_days_each ?? 7} days.</p></div><section className="definition-grid"><div><strong>Repeat events / monitored device-day</strong><span>{metrics?.definitions.rate ?? 'Distinct non-duplicate activations after the first activation for an asset, divided by monitored device-days in the same window.'}</span></div><div><strong>Availability & time to repair</strong><span>Availability: {metrics?.definitions.availability ?? 'Mean reported asset availability over the observation window.'} Time to repair: {metrics?.mean_time_to_repair_hours == null ? 'No accepted repairs in this window.' : `${metrics.mean_time_to_repair_hours} hours mean from documented fault opening to reviewer acceptance.`}</span></div></section><div className="warning-banner"><Siren size={18} /><div><strong>Event volume is not a security outcome.</strong><span>Any improvement claim requires a successful functional retest and documented review that monitoring coverage remains intact. No alarms are suppressed and no thresholds or controls are changed here.</span></div></div></>
}

function WorkView({ orders, role, onRefresh, onNotice }: { orders: WorkOrder[]; role: Role; onRefresh: () => void; onNotice: (text: string) => void }) {
  const [completionRecord, setCompletionRecord] = useState('')
  const [retestPassed, setRetestPassed] = useState(false)
  const [coverageReviewed, setCoverageReviewed] = useState(false)
  const [reviewNotes, setReviewNotes] = useState('')
  async function acknowledge(id: string) {
    try { await postJson(`/work-orders/${id}/acknowledge`, role); onNotice('Vendor work acknowledged.'); onRefresh() }
    catch { onNotice('This role cannot acknowledge this work order.') }
  }
  async function complete(id: string) {
    try {
      await postJson(`/work-orders/${id}/complete`, role, {
        completion_record: completionRecord,
        vendor_assessment: 'Fictional vendor assessment recorded by demo role.',
        repair_evidence_reference: 'TEXT-REF-DEMO',
      })
      setCompletionRecord('')
      onNotice('Vendor completion record submitted.')
      onRefresh()
    } catch { onNotice('Complete the text record and confirm the work order is acknowledged.') }
  }
  async function accept(id: string) {
    try {
      await postJson(`/work-orders/${id}/accept`, role, { functional_retest: retestPassed, coverage_reviewed: coverageReviewed, notes: reviewNotes })
      onNotice('Reviewer acceptance recorded.')
      onRefresh()
    } catch { onNotice('Acceptance requires completed work, a successful functional retest, and coverage review.') }
  }
  return <>
    <PageTitle eyebrow="ACCOUNTABILITY · APPROVED SCOPE" title="Vendor work" copy="Scheduled work, vendor acknowledgement, completion evidence, and reviewer acceptance." action={<span className="count-chip">{orders.length} work orders</span>} />
    {orders.map((order) => <section className="panel work-order-panel" key={order.id}>
      <div className="work-order-header"><div><p className="eyebrow">{order.id} · {order.asset_id}</p><h2>{order.title}</h2></div><span className="status-pill status-green"><Check size={13} /> {order.status}</span></div>
      <div className="work-grid"><div><span className="field-label">ACCOUNTABLE OWNER</span><strong>{order.accountable_owner}</strong></div><div><span className="field-label">SCHEDULED WINDOW</span><strong>{order.scheduled_window}</strong></div><div><span className="field-label">REVIEWER ACCEPTANCE</span><strong>{order.reviewer_acceptance}</strong></div></div>
      <div className="work-section"><span className="field-label">APPROVED SCOPE OF WORK</span><p>{order.scope}</p></div>
      <div className="diagnostic-grid"><div><span className="field-label">DIAGNOSTIC HYPOTHESIS</span><p>{order.diagnostic.hypothesis || 'Not recorded'}</p></div><div><span className="field-label">VENDOR ASSESSMENT</span><p>{order.diagnostic.vendor_assessment || 'Pending vendor assessment'}</p></div></div>
      {order.completion_record && <div className="work-section"><span className="field-label">COMPLETION RECORD</span><p>{order.completion_record}</p></div>}
      {order.functional_retest.notes && <div className="work-section acceptance-section"><div><span className="field-label">ACCEPTANCE & RETEST</span><p>{order.functional_retest.notes}</p></div><div className="acceptance-stamps"><span><Check size={13} /> FUNCTIONAL RETEST PASSED</span><span><Check size={13} /> COVERAGE REVIEWED</span><span><Check size={13} /> REVIEWER ACCEPTED</span></div></div>}
      <div className="criteria-list"><span className="field-label">ACCEPTANCE CRITERIA</span>{order.acceptance_criteria.map((criterion) => <span key={criterion}><Check size={14} />{criterion}</span>)}</div>
      {role === 'vendor' && order.status === 'scheduled' && <button className="button-primary" onClick={() => void acknowledge(order.id)}><Handshake size={16} /> Acknowledge scheduled work</button>}
      {role === 'vendor' && order.status === 'in_progress' && <div className="vendor-completion"><label htmlFor={`completion-${order.id}`} className="field-label">TEXT-ONLY COMPLETION RECORD</label><textarea id={`completion-${order.id}`} value={completionRecord} onChange={(event) => setCompletionRecord(event.target.value)} minLength={8} maxLength={4000} placeholder="Summarize the fictional work completed and factual observations." /><button className="button-primary" disabled={completionRecord.trim().length < 8} onClick={() => void complete(order.id)}><Check size={15} /> Submit completion record</button></div>}
      {role === 'reviewer' && order.status === 'completed' && <div className="review-acceptance"><span className="field-label">INDEPENDENT REVIEW · REQUIRED BEFORE ACCEPTANCE</span><label><input type="checkbox" checked={retestPassed} onChange={(event) => setRetestPassed(event.target.checked)} /> Functional retest completed successfully</label><label><input type="checkbox" checked={coverageReviewed} onChange={(event) => setCoverageReviewed(event.target.checked)} /> Monitoring coverage reviewed and unchanged</label><textarea value={reviewNotes} onChange={(event) => setReviewNotes(event.target.value)} minLength={8} maxLength={1000} placeholder="Reviewer notes and evidence references" /><button className="button-primary" disabled={!retestPassed || !coverageReviewed || reviewNotes.trim().length < 8} onClick={() => void accept(order.id)}><BadgeCheck size={15} /> Accept completed work</button></div>}
    </section>)}
    <p className="simulated-note"><BriefcaseBusiness size={15} /> Repair evidence is represented by fictional text references. There is no upload endpoint or access to confidential cases.</p>
  </>
}

function HandoffView({ handoffs, onAcknowledge, role }: { handoffs: Handoff[]; onAcknowledge: (id: string) => void; role: Role }) {
  return <><PageTitle eyebrow="SHIFT TRANSFER · ACCOUNTABILITY" title="Shift handoff" copy="Open incidents, unresolved defects, work in progress, and explicit next-owner acknowledgement." />{handoffs.map((handoff) => <section className="panel handoff-panel" key={handoff.id}><div className="handoff-heading"><div><p className="eyebrow">{handoff.id}</p><h2>{handoff.shift}</h2></div><span className={`status-pill ${handoff.acknowledged_by ? 'status-green' : 'status-amber'}`}>{handoff.acknowledged_by ? `Acknowledged by ${handoff.acknowledged_by}` : 'Awaiting acknowledgement'}</span></div><div className="handoff-grid">{[['OPEN INCIDENTS', handoff.open_incidents], ['UNRESOLVED DEFECTS', handoff.unresolved_defects], ['WORK IN PROGRESS', handoff.work_in_progress], ['TEMPORARY ARRANGEMENTS', handoff.temporary_arrangements]].map(([heading, items]) => <div className="handoff-item" key={heading as string}><span className="field-label">{heading}</span>{(items as string[]).map((text) => <p key={text}>{text}</p>)}</div>)}</div><div className="handoff-bottom"><div><span className="field-label">NEXT OWNER</span><strong>{handoff.next_owner}</strong></div>{!handoff.acknowledged_by && role !== 'vendor' && <button className="button-primary" onClick={() => onAcknowledge(handoff.id)}><Check size={15} /> Acknowledge handoff</button>}</div></section>)}</>
}

function ContinuityView({ exercise }: { exercise?: Exercise }) {
  if (!exercise) return <PageTitle eyebrow="RESILIENCE · TABLETOP" title="Continuity & exercises" copy="No exercise fixture loaded. Seed the synthetic profile to view the facilitated scenario." />
  const impact = exercise.business_impact
  return <><PageTitle eyebrow="RESILIENCE · DISCUSSION-BASED EXERCISE" title="Continuity & exercises" copy="Fictional storm-related site-access disruption and vendor outage. Facilitated discussion only; not an actual emergency response." action={<span className="mini-label">TABLETOP · NOT LIVE</span>} /><section className="panel exercise-banner"><div className="exercise-icon"><CloudSun size={21} /></div><div><p className="eyebrow">{exercise.id}</p><h2>{exercise.title}</h2><span>Scenario discussion · decisions are recorded as exercise outputs, not operational instructions.</span></div></section><div className="continuity-grid"><section className="panel continuity-panel"><div className="panel-heading"><div><h3>Business impact analysis</h3><span>Recovery needs and dependencies</span></div></div><DefinitionList values={impact} /></section><section className="panel continuity-panel"><div className="panel-heading"><div><h3>Scenario timeline</h3><span>Facilitator injects</span></div></div><div className="timeline">{exercise.timeline.map((item) => <div className="timeline-item" key={item.time}><span>{item.time}</span><p>{item.inject}</p></div>)}</div></section></div><div className="continuity-grid"><section className="panel continuity-panel"><div className="panel-heading"><div><h3>Decision & communications</h3><span>Approved alternatives and draft messages</span></div></div>{exercise.decisions.map((decision) => <div className="decision-card" key={decision.prompt}><span className="field-label">{decision.prompt}</span><p>{decision.decision}</p><small>Owner · {decision.owner}</small></div>)}{exercise.communications.map((message) => <div className="message-draft" key={message.audience}><span className="field-label">DRAFT · {message.audience}</span><p>“{message.draft}”</p></div>)}</section><section className="panel continuity-panel"><div className="panel-heading"><div><h3>After-action improvements</h3><span>Findings linked to accountable follow-up</span></div></div>{exercise.findings.map((finding) => <p className="finding-note" key={finding}><FileText size={15} />{finding}</p>)}{exercise.improvements.map((improvement) => <div className="improvement-row" key={improvement.action}><div><strong>{improvement.action}</strong><span>{improvement.owner} · due {improvement.due}</span></div><span className="status-pill status-amber">{improvement.status}</span></div>)}</section></div><section className="panel mitigation-panel"><div className="mitigation-icon"><Users size={18} /></div><div><span className="field-label">SEPARATE INCIDENT-MITIGATION TABLETOP</span><h3>Practice calm communication and safe escalation</h3><p>A fictional visitor becomes upset during a service delay. Discuss calm, respectful communication, maintaining safety, notifying authorized responders under employer procedures, and recording observable facts with timestamps.</p><small>No tactical confrontation advice. This is not de-escalation certification, a substitute for employer procedures, or real-world crisis-management experience.</small></div></section></>
}

function DefinitionList({ values }: { values: Record<string, string | string[]> }) {
  const labels: Record<string, string> = { critical_processes: 'Critical processes', dependencies: 'Dependencies', recovery_priorities: 'Recovery priorities', approved_alternatives: 'Approved alternatives', escalation: 'Decision / escalation' }
  return <div className="definition-list">{Object.entries(values).map(([key, value]) => <div key={key}><strong>{labels[key] ?? key.replaceAll('_', ' ')}</strong><span>{Array.isArray(value) ? value.join(' · ') : value}</span></div>)}</div>
}

function AwarenessView() {
  return <><PageTitle eyebrow="FIELD NOTES · QUICK REFERENCE" title="Awareness library" copy="Short reminders for clear, confidential, accountable maintenance coordination." /><div className="awareness-grid">{awareness.map((item, index) => <article className="awareness-item" key={item.title}><div className="awareness-top"><span>0{index + 1}</span><span>{item.tag}</span></div><h2>{item.title}</h2><p>{item.copy}</p><div className="awareness-rule" /></article>)}</div><section className="awareness-reminder"><ShieldCheck size={18} /><p>Use established employer reporting and emergency procedures. This workspace supports documentation and preparedness; it does not operate alarms or replace professional direction.</p></section></>
}

export default App