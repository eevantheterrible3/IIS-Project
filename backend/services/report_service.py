from io import BytesIO
from datetime import datetime, timezone

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from repositories.workflow_instance_repository import WorkflowInstanceRepository
from repositories.workflow_instance_step_repository import WorkflowInstanceStepRepository

pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

HEADER_BG = colors.HexColor("#4F46E5")
HEADER_FG = colors.white
ROW_ALT = colors.HexColor("#F9FAFB")
GRID_COLOR = colors.HexColor("#E5E7EB")
FONT = "DejaVu"
FONT_BOLD = "DejaVu-Bold"


def _fmt_duration(delta):
    total_seconds = int(delta.total_seconds())
    if total_seconds < 0:
        return "-"
    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    if days > 0:
        return f"{days}d {hours}h"
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


class ReportService:
    def __init__(self, db):
        self.instance_repo = WorkflowInstanceRepository(db)
        self.step_repo = WorkflowInstanceStepRepository(db)

    async def generate_workflow_report(self) -> BytesIO:
        instances = await self.instance_repo.get_all()

        all_steps = []
        for inst in instances:
            steps = await self.step_repo.get_by_instance(inst.instance_id)
            all_steps.append((inst, steps))

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=20 * mm, rightMargin=20 * mm,
            topMargin=20 * mm, bottomMargin=20 * mm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle", parent=styles["Title"],
            fontName=FONT_BOLD, fontSize=20, spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle", parent=styles["Normal"],
            fontName=FONT, fontSize=10, textColor=colors.grey, spaceAfter=16,
        )
        section_style = ParagraphStyle(
            "SectionHeader", parent=styles["Heading2"],
            fontName=FONT_BOLD, fontSize=13, spaceBefore=18, spaceAfter=8,
        )
        cell_style = ParagraphStyle(
            "Cell", parent=styles["Normal"],
            fontName=FONT, fontSize=8, leading=10,
        )

        elements = []

        elements.append(Paragraph("Workflow Instances Report", title_style))
        elements.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            subtitle_style,
        ))

        total = len(instances)
        completed = sum(1 for i in instances if i.completed_at is not None)
        in_progress = sum(1 for i in instances if i.completed_at is None and i.current_step_id is not None)
        not_started = total - completed - in_progress

        total_steps = sum(len(steps) for _, steps in all_steps)
        completed_steps = sum(
            sum(1 for s in steps if s.status == "completed")
            for _, steps in all_steps
        )
        avg_progress = 0
        if total_steps > 0:
            avg_progress = sum(
                s.progress for _, steps in all_steps for s in steps
            ) / total_steps

        unique_docs = len({i.document_id for i in instances})

        elements.append(Paragraph("Summary", section_style))
        summary_data = [
            ["Metric", "Value"],
            ["Total instances", str(total)],
            ["Completed", str(completed)],
            ["In progress", str(in_progress)],
            ["Not started", str(not_started)],
            ["Documents in workflows", str(unique_docs)],
            ["Total steps", str(total_steps)],
            ["Completed steps", str(completed_steps)],
            ["Average progress", f"{avg_progress:.0f}%"],
        ]
        elements.append(self._build_table(summary_data, [250, 250]))

        elements.append(Paragraph("By Workflow", section_style))
        wf_stats = {}
        for inst in instances:
            name = inst.workflow.name if inst.workflow else "N/A"
            if name not in wf_stats:
                wf_stats[name] = {"total": 0, "completed": 0, "in_progress": 0}
            wf_stats[name]["total"] += 1
            if inst.completed_at is not None:
                wf_stats[name]["completed"] += 1
            elif inst.current_step_id is not None:
                wf_stats[name]["in_progress"] += 1

        wf_data = [["Workflow", "Instances", "Completed", "In Progress"]]
        for name, s in wf_stats.items():
            wf_data.append([name, str(s["total"]), str(s["completed"]), str(s["in_progress"])])
        elements.append(self._build_table(wf_data, [200, 100, 100, 100]))

        elements.append(Paragraph("Instance Details", section_style))
        header_style = ParagraphStyle(
            "HeaderCell", parent=styles["Normal"],
            fontName=FONT_BOLD, fontSize=9, leading=11, textColor=HEADER_FG,
        )
        detail_data = [[
            Paragraph("Document", header_style),
            Paragraph("Workflow", header_style),
            Paragraph("Current Step", header_style),
            Paragraph("In Step", header_style),
            Paragraph("Total Duration", header_style),
            Paragraph("Status", header_style),
        ]]
        now = datetime.now()
        for inst, steps in all_steps:
            doc_name = inst.document.name if inst.document else "N/A"
            wf_name = inst.workflow.name if inst.workflow else "N/A"
            step_name = inst.current_step.name if inst.current_step else "-"
            status = "Completed" if inst.completed_at else "In Progress"

            total_duration = _fmt_duration(now - inst.started_at) if inst.started_at else "-"

            current_step_obj = None
            for s in steps:
                if s.action_id == inst.current_step_id:
                    current_step_obj = s
                    break
            if current_step_obj:
                step_since = current_step_obj.updated_at or current_step_obj.created_at
                in_step_duration = _fmt_duration(now - step_since) if step_since else "-"
            else:
                in_step_duration = "-"

            detail_data.append([
                Paragraph(doc_name, cell_style),
                Paragraph(wf_name, cell_style),
                Paragraph(step_name, cell_style),
                Paragraph(in_step_duration, cell_style),
                Paragraph(total_duration, cell_style),
                Paragraph(status, cell_style),
            ])

        col_widths = [85, 85, 78, 60, 70, 77]
        elements.append(self._build_table(detail_data, col_widths))

        if any(steps for _, steps in all_steps):
            elements.append(Paragraph("Steps by Instance", section_style))
            for inst, steps in all_steps:
                if not steps:
                    continue
                doc_name = inst.document.name if inst.document else inst.instance_id[:8]
                wf_name = inst.workflow.name if inst.workflow else ""
                elements.append(Paragraph(
                    f"{doc_name} — {wf_name}",
                    ParagraphStyle("SubHead", parent=styles["Normal"], fontName=FONT, fontSize=9, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#374151")),
                ))

                step_data = [["Step", "Status", "Progress", "Assigned To"]]
                for s in steps:
                    action_name = s.action.name if s.action else "N/A"
                    assigned = (
                        f"{s.assigned_user.name} {s.assigned_user.last_name}"
                        if s.assigned_user else "-"
                    )
                    step_data.append([action_name, s.status, f"{s.progress}%", assigned])
                elements.append(self._build_table(step_data, [160, 100, 80, 140]))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    def _build_table(self, data, col_widths):
        table = Table(data, colWidths=col_widths, repeatRows=1)
        style_commands = [
            ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), HEADER_FG),
            ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
            ("FONTNAME", (0, 1), (-1, -1), FONT),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, GRID_COLOR),
        ]
        for i in range(1, len(data)):
            if i % 2 == 0:
                style_commands.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
        table.setStyle(TableStyle(style_commands))
        return table
