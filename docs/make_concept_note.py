from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import mm
from pathlib import Path

OUT=Path(__file__).resolve().parents[1]/'ThreadPilot_Concept_Note.pdf'
styles=getSampleStyleSheet()
NAVY=colors.HexColor('#07101C'); CYAN=colors.HexColor('#62E6D8'); INK=colors.HexColor('#1D2A3A'); MUTED=colors.HexColor('#68788C'); PALE=colors.HexColor('#EEF5F4')
styles.add(ParagraphStyle(name='TitleX',parent=styles['Title'],fontName='Helvetica-Bold',fontSize=27,leading=31,textColor=NAVY,spaceAfter=10))
styles.add(ParagraphStyle(name='SubX',parent=styles['Normal'],fontName='Helvetica',fontSize=10,leading=15,textColor=MUTED,spaceAfter=14))
styles.add(ParagraphStyle(name='H2X',parent=styles['Heading2'],fontName='Helvetica-Bold',fontSize=15,leading=19,textColor=NAVY,spaceBefore=10,spaceAfter=7))
styles.add(ParagraphStyle(name='BodyX',parent=styles['BodyText'],fontName='Helvetica',fontSize=9.5,leading=15,textColor=INK,spaceAfter=7))
styles.add(ParagraphStyle(name='SmallX',parent=styles['BodyText'],fontName='Helvetica',fontSize=8.2,leading=12,textColor=MUTED))
styles.add(ParagraphStyle(name='MonoX',parent=styles['BodyText'],fontName='Courier-Bold',fontSize=8.3,leading=12,textColor=NAVY))
styles.add(ParagraphStyle(name='HeadCell',parent=styles['BodyText'],fontName='Helvetica-Bold',fontSize=9.5,leading=12,textColor=colors.white,spaceAfter=0))

def footer(canvas,doc):
    canvas.saveState(); canvas.setFillColor(MUTED); canvas.setFont('Helvetica',7)
    canvas.drawString(18*mm,10*mm,'ThreadPilot - ArchScale Guild AS-01')
    canvas.drawRightString(192*mm,10*mm,f'{doc.page}')
    canvas.restoreState()

def P(t,sty='BodyX'): return Paragraph(t,styles[sty])

doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=17*mm,bottomMargin=16*mm,title='ThreadPilot Concept Note',author='Akash Kapoor')
story=[]
story += [P('THREADPILOT','MonoX'),P('Project Impact Intelligence','TitleX'),P('AS-01 - Kill the coordination black hole nightmare','SubX')]
call=Table([[P('<b>Core promise</b><br/>Turn fragmented project communication into a connected, evidence-backed project state: <b>change -> impact -> dependency -> approval -> blocker -> action -> memory.</b>','BodyX')]],colWidths=[174*mm])
call.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),PALE),('BOX',(0,0),(-1,-1),0.6,CYAN),('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,-1),11),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
story += [call,Spacer(1,7*mm)]
story += [P('The problem','H2X'),P('Architecture, interior design and construction work is distributed across people, messages, drawings and decisions. A single change can affect multiple disciplines and downstream work, while responsibility and consequence are easy to lose between handoffs. ThreadPilot adds a coordination-intelligence layer that makes those relationships visible and actionable.'),P('What the prototype demonstrates','H2X')]
rows=[['Capability','ThreadPilot implementation'],
['Stakeholder & role management','Seven project roles with responsibility/focus and routed-signal visibility.'],['Activity & change tracking','Persistent project messages across WhatsApp, Email, Site, Client, Supplier and Drawings.'],['Impact identification','Signals identify affected roles/workfaces and connect changes to downstream consequence.'],['Dependency management','Scenario impact graph and structured impact-chain stages.'],['Action tracking','P0/P1 action queue with owner, due time, reason and confirmation state.'],['Approval management','Explicit approval gates, including client bathroom sign-off and material substitution.'],['Coordination alerts','Critical/high/medium signals, blockers, conflict exceptions and project risk/readiness.'],['Project memory','PostgreSQL persistence plus an audit trail of important decisions and confirmations.']]
t=Table([[P(a,'HeadCell') if i==0 else P(a,'BodyX'),P(b,'HeadCell') if i==0 else P(b,'BodyX')] for i,(a,b) in enumerate(rows)],colWidths=[54*mm,120*mm],repeatRows=1)
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#DDE4EB')),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F8FAFC')]),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
story += [t,PageBreak(),P('How the demo works','H2X')]
flow=Table([[P('1. Evidence','MonoX'),P('2. Intelligence','MonoX'),P('3. Consequence','MonoX'),P('4. Decision','MonoX')],
[P('Capture an unstructured project update.','SmallX'),P('Classify signals and extract entities with explainable rules or optional LLM.','SmallX'),P('Trace affected stakeholders, dependencies, approval gates and blocked work.','SmallX'),P('Route an action; require human confirmation; write the decision to audit.','SmallX')]],colWidths=[43.5*mm]*4)
flow.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('BOX',(0,0),(-1,-1),0.5,CYAN),('INNERGRID',(0,0),(-1,-1),0.4,colors.HexColor('#DDE4EB')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
story += [flow,Spacer(1,7*mm),P('Riverside Residence scenario','H2X'),P('The seeded demo intentionally mirrors the coordination black hole: an MEP note flags an 80mm ceiling/sprinkler conflict; an earlier email references Rev 04 while Document Control establishes Rev 05 as the superseding issue; Site holds gypsum close-out to avoid rework; the Client requests a bathroom visual before final sign-off; and a supplier offers Shade 318 while Shade 312 is unavailable. ThreadPilot turns these fragments into signals, dependencies, actions and a decision sequence.'),P('Technical architecture','H2X')]
arch_rows=[['Layer','Technology'],['Web app','React 19.3 + TypeScript + Vite 8.2, responsive custom UI, Lucide icons, installable PWA manifest'],['API','FastAPI on Python 3.12 with typed Pydantic request/response models'],['Persistence','PostgreSQL 16 via SQLAlchemy 2.0; Alembic migration support'],['Intelligence','Explainable local evidence engine + optional OpenAI-compatible provider extraction'],['Delivery','Docker multi-stage image, Docker Compose local stack, Render Blueprint for public deployment'],['Quality','pytest smoke tests + deterministic evaluation harness + source-linked signals']]
arch=Table([[P(a,'HeadCell') if i==0 else P(a,'BodyX'),P(b,'HeadCell') if i==0 else P(b,'BodyX')] for i,(a,b) in enumerate(arch_rows)],colWidths=[37*mm,137*mm])
arch.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#DDE4EB')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
story += [arch,PageBreak(),P('Why the prototype is defensible','H2X'),P('<b>Evidence first.</b> Every generated signal keeps source message ids. A judge can open a signal and inspect the original project updates behind it.'),P('<b>Human in the loop.</b> Signals can be confirmed or dismissed. Recommended actions require explicit confirmation, and decisions are recorded in the audit trail.'),P('<b>Reliable demo behavior.</b> The configured LLM/API is the primary extraction path. If the provider is unavailable or returns invalid output, the deterministic local evidence engine becomes the reliability fallback, and the UI identifies which path produced the result.'),P('<b>Deployment ready.</b> The React production build is packaged with the FastAPI service, while PostgreSQL is externalized through environment configuration. Docker Compose provides the full local stack and Render Blueprint provisions the web service plus PostgreSQL.'),P('Judge walkthrough','H2X'),P('Open Overview -> show the technical blocker and approval gate -> open the Rev 05 signal -> inspect evidence and impact chain -> follow the Impact Graph -> confirm a P0 action -> capture a fresh project message -> preview intelligence -> save + route -> open Project Memory and show the audit event.'),Spacer(1,8*mm),P('Positioning','H2X'),P('ThreadPilot is intentionally a focused coordination-intelligence prototype rather than a full construction ERP. The showcased workflow is deterministic and reproducible, while the architecture leaves room for richer LLM extraction, external messaging integrations, graph persistence and production authentication in subsequent iterations.'),Spacer(1,6*mm),P('Prepared for ArchScale Guild Intern Technology Hackathon - AS-01','SmallX')]

doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
