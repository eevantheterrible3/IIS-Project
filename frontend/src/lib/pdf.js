import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import html2canvas from "html2canvas";

const fmtInt = (n) => Number(n || 0).toLocaleString("en-US");
const fmtCost = (n) => `$${Number(n || 0).toFixed(4)}`;

/**
 * Export the analytics dashboard to a PDF: a visual snapshot of the dashboard
 * (KPIs + charts) followed by structured data tables.
 *
 * @param {HTMLElement} element - the dashboard container to snapshot
 * @param {object} data - DashboardResponse payload
 */
export async function exportDashboardPdf(element, data) {
    const doc = new jsPDF("p", "mm", "a4");
    const pageW = doc.internal.pageSize.getWidth();
    const pageH = doc.internal.pageSize.getHeight();
    const margin = 10;

    // Header
    doc.setFontSize(16);
    doc.text("Analitika potrošnje LLM-a", margin, 14);
    doc.setFontSize(9);
    doc.setTextColor(120);
    doc.text(`Generisano: ${new Date().toLocaleString()}`, margin, 20);
    doc.setTextColor(0);

    // Visual snapshot of the dashboard (charts + cards)
    if (element) {
        const canvas = await html2canvas(element, {
            scale: 2,
            backgroundColor: "#ffffff",
            useCORS: true,
            logging: false,
        });
        const imgData = canvas.toDataURL("image/png");
        const imgW = pageW - margin * 2;
        const imgH = (canvas.height * imgW) / canvas.width;

        // Multi-page: redraw the full image on each page at a negative Y offset so a
        // different vertical slice shows; the PDF page box clips the overflow. This is
        // the standard html2canvas->jsPDF pagination pattern (negative position is intentional).
        let position = 26;
        let heightLeft = imgH;
        doc.addImage(imgData, "PNG", margin, position, imgW, imgH);
        heightLeft -= pageH - position;
        while (heightLeft > 0) {
            doc.addPage();
            position = heightLeft - imgH; // == -(image height already shown)
            doc.addImage(imgData, "PNG", margin, position, imgW, imgH);
            heightLeft -= pageH;
        }
    }

    const s = data?.summary || {};

    // Summary table
    doc.addPage();
    doc.setFontSize(13);
    doc.text("Pregled", margin, 16);
    autoTable(doc, {
        startY: 20,
        head: [["Metrika", "Vrednost"]],
        body: [
            ["Ukupno generisanja", fmtInt(s.total_generations)],
            ["Ukupno tokena", fmtInt(s.total_tokens)],
            ["Ulazni tokeni", fmtInt(s.prompt_tokens)],
            ["Izlazni tokeni", fmtInt(s.completion_tokens)],
            ["Procenjeni trošak", fmtCost(s.estimated_cost)],
            ["Prosečna latencija (ms)", fmtInt(Math.round(s.avg_latency_ms))],
            ["Dokumenata", fmtInt(s.unique_documents)],
        ],
        styles: { fontSize: 9 },
        headStyles: { fillColor: [79, 70, 229] },
    });

    // Breakdown by document type
    const byType = data?.by_document_type || [];
    if (byType.length) {
        autoTable(doc, {
            startY: doc.lastAutoTable.finalY + 8,
            head: [["Tip dokumenta", "Generisanja", "Tokeni", "Trošak"]],
            body: byType.map((b) => [
                b.label,
                fmtInt(b.generations),
                fmtInt(b.total_tokens),
                fmtCost(b.estimated_cost),
            ]),
            styles: { fontSize: 9 },
            headStyles: { fillColor: [79, 70, 229] },
        });
    }

    // Recent generations
    const recent = data?.recent || [];
    if (recent.length) {
        autoTable(doc, {
            startY: doc.lastAutoTable.finalY + 8,
            head: [["Datum", "Tip", "Model", "Dokument", "Tokeni", "Trošak"]],
            body: recent.map((r) => [
                r.created_at ? new Date(r.created_at).toLocaleString() : "—",
                r.generation_type,
                r.model || "—",
                r.document_name || "—",
                fmtInt(r.total_tokens),
                r.estimated_cost != null ? fmtCost(r.estimated_cost) : "—",
            ]),
            styles: { fontSize: 8 },
            headStyles: { fillColor: [79, 70, 229] },
        });
    }

    doc.save("analitika-potrosnja.pdf");
}
