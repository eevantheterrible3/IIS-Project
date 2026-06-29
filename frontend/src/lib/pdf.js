import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";

const fmtInt = (n) => Number(n || 0).toLocaleString("en-US");
const fmtCost = (n) => `$${Number(n || 0).toFixed(4)}`;

export async function exportDashboardPdf(data) {
    const doc = new jsPDF("p", "mm", "a4");
    const margin = 10;

    // Header
    doc.setFontSize(16);
    doc.text("Analitika potrosnje LLM-a", margin, 14);
    doc.setFontSize(9);
    doc.setTextColor(120);
    doc.text(`Generisano: ${new Date().toLocaleString()}`, margin, 20);
    doc.setTextColor(0);

    const s = data?.summary || {};

    // Summary table
    doc.setFontSize(13);
    doc.text("Pregled", margin, 30);
    autoTable(doc, {
        startY: 34,
        head: [["Metrika", "Vrednost"]],
        body: [
            ["Ukupno generisanja", fmtInt(s.total_generations)],
            ["Ukupno tokena", fmtInt(s.total_tokens)],
            ["Ulazni tokeni", fmtInt(s.prompt_tokens)],
            ["Izlazni tokeni", fmtInt(s.completion_tokens)],
            ["Procenjeni trosak", fmtCost(s.estimated_cost)],
            ["Prosecna latencija (ms)", fmtInt(Math.round(s.avg_latency_ms))],
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
            head: [["Tip dokumenta", "Generisanja", "Tokeni", "Trosak"]],
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
            head: [["Datum", "Tip", "Model", "Dokument", "Tokeni", "Trosak"]],
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
