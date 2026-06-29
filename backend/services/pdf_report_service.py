import io

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_report_pdf(
    generated_at: str,
    generated_by: str,
    stats_total: int,
    stats_completed: int,
    stats_active: int,
    stats_late: int,
    proj_rows: list[dict],
    res_rows: list[dict],
    priority_counts: dict[str, int],
    unassigned_rows: list[dict],
    step_counts: dict[str, int] | None = None,
) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    W, H = A4

    def draw_section(title: str, y: float) -> float:
        y -= 25
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(HexColor("#374151"))
        c.drawString(50, y, title)
        y -= 4
        c.setStrokeColor(HexColor("#e5e7eb"))
        c.line(50, y, W - 50, y)
        return y - 12

    def draw_row(cols: list[tuple[float, str]], y: float, bold: bool = False, gray: bool = False) -> float:
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 8)
        if gray:
            c.setFillColor(HexColor("#f9fafb"))
            c.rect(50, y - 3, W - 100, 14, fill=1, stroke=0)
        c.setFillColor(HexColor("#6b7280") if bold else HexColor("#1f2937"))
        for x, text in cols:
            c.drawString(x, y, str(text)[:32])
        c.setStrokeColor(HexColor("#f3f4f6"))
        c.line(50, y - 4, W - 50, y - 4)
        return y - 15

    y = H - 50

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(HexColor("#111827"))
    c.drawString(50, y, "Project Realization Report")
    y -= 22
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#9ca3af"))
    c.drawString(50, y, f"Generated: {generated_at}   |   By: {generated_by}")
    y -= 45

    # Summary bar chart
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(HexColor("#374151"))
    c.drawString(50, y, "SUMMARY")
    y -= 4
    c.setStrokeColor(HexColor("#e5e7eb"))
    c.line(50, y, W - 50, y)
    y -= 100

    bars = [
        ("Total tasks", stats_total,     "#6b7280"),
        ("Completed",   stats_completed, "#22c55e"),
        ("Active",      stats_active,    "#f59e0b"),
        ("Late",        stats_late,      "#ef4444"),
    ]
    max_v = max(v for _, v, _ in bars) or 1
    bar_w, bar_gap, max_bar_h = 70, 25, 80
    bx = 50
    for label, value, color in bars:
        bh = max(3, value / max_v * max_bar_h)
        c.setFillColor(HexColor(color))
        c.rect(bx, y, bar_w, bh, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(HexColor("#374151"))
        c.drawCentredString(bx + bar_w / 2, y + bh + 5, str(value))
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#6b7280"))
        c.drawCentredString(bx + bar_w / 2, y - 14, label)
        bx += bar_w + bar_gap
    y -= 25

    # Projects
    y = draw_section("PROJECTS", y)
    y = draw_row([(50, "Project"), (210, "Manager"), (330, "Deadline"), (400, "Tasks"), (435, "Done"), (470, "Late"), (505, "Progress")], y, bold=True, gray=True)
    for r in proj_rows:
        old_y = y
        y = draw_row([(50, r["name"][:28]), (210, r["manager"][:18]), (330, r["deadline"]),
                      (400, r["total"]), (435, r["completed"]), (470, r["late"]), (505, f"{r['progress']}%")], y)
        if r["late"] > 0:
            c.setFillColor(HexColor("#ef4444"))
            c.setFont("Helvetica", 8)
            c.drawString(470, old_y, str(r["late"]))
        if y < 80:
            c.showPage(); y = H - 50

    # Resources
    y = draw_section("RESOURCE OVERVIEW", y)
    y = draw_row([(50, "Resource"), (190, "Type"), (310, "Tasks using it"), (400, "Total quantity"), (490, "Quantity in use")], y, bold=True, gray=True)
    for r in res_rows:
        y = draw_row([(50, r["name"]), (190, r["type"]), (310, r["count"]), (400, r["quantity"]), (490, r["quantity_used"])], y)
        if y < 80:
            c.showPage(); y = H - 50
    if not res_rows:
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#9ca3af"))
        c.drawString(50, y, "No resources assigned to tasks.")
        y -= 15

    # Tasks by workflow status
    if step_counts:
        y = draw_section("TASKS BY WORKFLOW STATUS", y)
        y = draw_row([(50, "Workflow Step"), (350, "Tasks"), (430, "% of total")], y, bold=True, gray=True)
        for step_name, cnt in sorted(step_counts.items(), key=lambda x: -x[1]):
            pct = round(cnt / (stats_total or 1) * 100)
            y = draw_row([(50, step_name[:40]), (350, cnt), (430, f"{pct}%")], y)
            if y < 80:
                c.showPage(); y = H - 50

    # Priority
    y = draw_section("TASKS BY PRIORITY", y)
    y = draw_row([(50, "Priority"), (200, "Tasks"), (300, "% of total")], y, bold=True, gray=True)
    total_for_pct = stats_total or 1
    for key, label, color in [("high", "High", "#dc2626"), ("medium", "Medium", "#d97706"), ("low", "Low", "#2563eb")]:
        cnt = priority_counts.get(key, 0)
        old_y = y
        y = draw_row([(50, label), (200, cnt), (300, f"{round(cnt / total_for_pct * 100)}%")], y)
        c.setFillColor(HexColor(color))
        c.setFont("Helvetica", 8)
        c.drawString(50, old_y, label)

    # Unassigned tasks
    y = draw_section("UNASSIGNED TASKS BY PROJECT", y)
    if unassigned_rows:
        y = draw_row([(50, "Project"), (250, "Task")], y, bold=True, gray=True)
        for r in unassigned_rows:
            y = draw_row([(50, r["project"][:28]), (250, r["task"][:35])], y)
            if y < 80:
                c.showPage(); y = H - 50
    else:
        c.setFont("Helvetica", 9)
        c.setFillColor(HexColor("#9ca3af"))
        c.drawString(50, y, "All tasks have an assigned user.")
        y -= 15

    c.save()
    buf.seek(0)
    return buf.read()
