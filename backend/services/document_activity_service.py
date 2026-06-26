# services/document_activity_report_service.py

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from repositories.document_repository import DocumentRepository
from repositories.activity_repository import ActivityRepository
from repositories.permission_repository import PermissionRepository


class DocumentActivityReportService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        activity_repository: ActivityRepository,
        permission_repository: PermissionRepository,
    ):
        self.document_repository = document_repository
        self.activity_repository = activity_repository
        self.permission_repository = permission_repository

    async def generate_report(self, document_id: str) -> BytesIO | None:
        document = await self.document_repository.get_document_details(document_id)

        if document is None:
            return None

        activities = await self.activity_repository.get_document_activities(document_id)

        project_members = await self.permission_repository.get_project_members_with_roles(
            document.project_id
        )

        user_roles = {}

        for work in project_members:
            if work.user and work.role:
                user_roles[work.user.user_id] = work.role.name.lower()

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)

        width, height = A4
        margin = 50
        y = height - 50

        def draw_text(text, x, current_y, font="Helvetica", size=10, color=colors.black):
            pdf.setFont(font, size)
            pdf.setFillColor(color)
            pdf.drawString(x, current_y, str(text))

        def shorten(text, max_length=45):
            text = str(text or "")

            if len(text) <= max_length:
                return text

            return text[:max_length - 3] + "..."

        def get_user_name(activity):
            if not activity.user:
                return "Unknown user"

            full_name = f"{activity.user.name or ''} {activity.user.last_name or ''}".strip()

            if full_name:
                return full_name

            return activity.user.email or "Unknown user"

        def get_user_role(activity):
            if not activity.user:
                return "-"

            role = user_roles.get(activity.user.user_id)

            if not role:
                return "not_project_member"

            return role

        def get_activity_value(activity_type):
            return activity_type.value if hasattr(activity_type, "value") else str(activity_type)

        def get_activity_text(activity_type):
            value = get_activity_value(activity_type)
            normalized = value.lower()

            if "view" in normalized:
                return "Viewed document"

            if "update" in normalized:
                return "Updated document"

            if "create" in normalized:
                return "Created document"

            if "delete" in normalized:
                return "Deleted document"

            return value

        def get_activity_date(activity):
            if not activity.date:
                return "-"

            return activity.date.strftime("%d.%m.%Y. %H:%M")

        def activity_contains(activity, keyword):
            value = get_activity_value(activity.type)
            return keyword in value.lower()

        def get_last_activity_date():
            dates = [activity.date for activity in activities if activity.date]

            if not dates:
                return "-"

            return max(dates).strftime("%d.%m.%Y. %H:%M")

        def draw_footer():
            pdf.setFont("Helvetica", 8)
            pdf.setFillColor(colors.HexColor("#9ca3af"))
            pdf.drawString(
                margin,
                30,
                "Generated automatically by Document Management system.",
            )

        def draw_table_header():
            nonlocal y

            pdf.setFillColor(colors.HexColor("#f3f4f6"))
            pdf.rect(margin, y - 8, width - 2 * margin, 24, fill=True, stroke=False)

            draw_text("User", margin + 10, y, "Helvetica-Bold", 10, colors.HexColor("#111827"))
            draw_text("Role", margin + 150, y, "Helvetica-Bold", 10, colors.HexColor("#111827"))
            draw_text("Activity", margin + 270, y, "Helvetica-Bold", 10, colors.HexColor("#111827"))
            draw_text("Date", margin + 390, y, "Helvetica-Bold", 10, colors.HexColor("#111827"))

            y -= 28

        def check_page_space(required_space=70):
            nonlocal y

            if y < required_space:
                draw_footer()
                pdf.showPage()
                y = height - 50
                draw_table_header()

        views_count = sum(
            1 for activity in activities
            if activity_contains(activity, "view")
        )

        updates_count = sum(
            1 for activity in activities
            if activity_contains(activity, "update")
        )

        # Title
        draw_text(
            "Document Activity Report",
            margin,
            y,
            "Helvetica-Bold",
            18,
            colors.HexColor("#111827"),
        )

        y -= 30

        # Document info box
        pdf.setFillColor(colors.HexColor("#f9fafb"))
        pdf.rect(margin, y - 118, width - 2 * margin, 130, fill=True, stroke=False)

        pdf.setStrokeColor(colors.HexColor("#e5e7eb"))
        pdf.rect(margin, y - 118, width - 2 * margin, 130, fill=False, stroke=True)

        project_name = document.project.name if document.project else "-"

        draw_text("Document:", margin + 15, y - 5, "Helvetica-Bold", 10, colors.HexColor("#374151"))
        draw_text(shorten(document.name, 65), margin + 110, y - 5)

        draw_text("Project:", margin + 15, y - 25, "Helvetica-Bold", 10, colors.HexColor("#374151"))
        draw_text(shorten(project_name, 65), margin + 110, y - 25)

        draw_text("Document ID:", margin + 15, y - 45, "Helvetica-Bold", 10, colors.HexColor("#374151"))
        draw_text(document.document_id, margin + 110, y - 45, "Helvetica", 9, colors.HexColor("#6b7280"))

        draw_text("Total activities:", margin + 15, y - 65, "Helvetica-Bold", 10, colors.HexColor("#374151"))
        draw_text(str(len(activities)), margin + 110, y - 65)

        draw_text("Last activity:", margin + 15, y - 85, "Helvetica-Bold", 10, colors.HexColor("#374151"))
        draw_text(get_last_activity_date(), margin + 110, y - 85)

        draw_text("Views:", margin + 15, y - 105, "Helvetica-Bold", 10, colors.HexColor("#374151"))
        draw_text(str(views_count), margin + 110, y - 105)

        draw_text("Updates:", margin + 250, y - 105, "Helvetica-Bold", 10, colors.HexColor("#374151"))
        draw_text(str(updates_count), margin + 320, y - 105)

        y -= 155

        # Activities section
        draw_text("Activities", margin, y, "Helvetica-Bold", 13, colors.HexColor("#111827"))
        y -= 25

        if not activities:
            pdf.setFillColor(colors.HexColor("#f9fafb"))
            pdf.rect(margin, y - 30, width - 2 * margin, 40, fill=True, stroke=False)

            pdf.setStrokeColor(colors.HexColor("#e5e7eb"))
            pdf.rect(margin, y - 30, width - 2 * margin, 40, fill=False, stroke=True)

            draw_text(
                "No activities recorded for this document.",
                margin + 15,
                y - 7,
                "Helvetica",
                10,
                colors.HexColor("#6b7280"),
            )
        else:
            activities = sorted(
                activities,
                key=lambda activity: activity.date or datetime.min,
                reverse=True,
            )

            draw_table_header()

            for activity in activities:
                check_page_space()

                user_name = shorten(get_user_name(activity), 20)
                user_role = shorten(get_user_role(activity), 20)
                activity_text = shorten(get_activity_text(activity.type), 22)
                activity_date = get_activity_date(activity)

                pdf.setStrokeColor(colors.HexColor("#e5e7eb"))
                pdf.line(margin, y + 10, width - margin, y + 10)

                draw_text(user_name, margin + 10, y)
                draw_text(user_role, margin + 150, y, "Helvetica", 10, colors.HexColor("#6b7280"))
                draw_text(activity_text, margin + 270, y, "Helvetica", 10, colors.HexColor("#374151"))
                draw_text(activity_date, margin + 390, y, "Helvetica", 10, colors.HexColor("#6b7280"))

                y -= 26

        draw_footer()

        pdf.save()
        buffer.seek(0)

        return buffer