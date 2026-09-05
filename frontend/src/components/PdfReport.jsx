import { jsPDF } from "jspdf";

// ---- Layout constants (tuned to match the FORGE GUARD DOCX) ----
const MARGIN = 20;
const FOOTER_RESERVE = 18; // space kept free at the bottom of every page for the footer
const HEADING_TO_ROW = 22; // gap from a section heading to its first row
const ROW_SPACING = 14; // vertical distance between two rows in the same section
const SECTION_GAP = 24; // gap from the last row of a section to the next heading

function PdfReport({ result }) {
  const generateReport = () => {
    const doc = new jsPDF("p", "mm", "a4");
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const contentWidth = pageWidth - MARGIN * 2;

    const status = result.status?.toLowerCase() || "unknown";
    const statusText = result.status?.toUpperCase() || "UNKNOWN";

    const riskScore =
      result.risk_score !== undefined && result.risk_score !== null
        ? `${result.risk_score}%`
        : "--";

    const faceMatch =
      result.face_match_score !== undefined &&
      result.face_match_score !== null
        ? `${result.face_match_score}%`
        : "--";

    const documentAuthenticity =
      result.document_authenticity !== undefined &&
      result.document_authenticity !== null
        ? `${result.document_authenticity}%`
        : "--";

    const today = new Date();
    const formattedDate = `${String(today.getDate()).padStart(2, "0")}/${String(
      today.getMonth() + 1
    ).padStart(2, "0")}/${today.getFullYear()}`;
    const formattedTime = `${String(today.getHours()).padStart(2, "0")}:${String(
      today.getMinutes()
    ).padStart(2, "0")}`;
    const formattedDateTime = `${formattedDate} ${formattedTime}`;

    // =========================
    // HEADER (page 1)
    // =========================
    let y = drawMainHeader(doc, pageWidth, formattedDateTime);

    // =========================
    // VERIFICATION STATUS
    // =========================
    y = ensureSpace(doc, y, pageWidth, pageHeight, 34, formattedDateTime);

    let statusColor = [47, 145, 88]; // verified: green
    if (status === "rejected") {
      statusColor = [205, 70, 65]; // rejected: red
    } else if (status !== "verified") {
      statusColor = [205, 160, 45]; // pending / unknown: amber
    }

    doc.setFillColor(...statusColor);
    doc.roundedRect(MARGIN, y, contentWidth, 34, 7, 7, "F");

    doc.setTextColor(255, 255, 255);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.text("VERIFICATION STATUS", MARGIN + 10, y + 17);

    fitText(doc, statusText, contentWidth * 0.45, 17, {
      x: pageWidth - MARGIN - 10,
      y: y + 22,
      align: "right",
    });

    y += 34 + 8; // gap before the risk score box

    // =========================
    // RISK SCORE
    // =========================
    y = ensureSpace(doc, y, pageWidth, pageHeight, 32, formattedDateTime);

    doc.setFillColor(246, 246, 248);
    doc.roundedRect(MARGIN, y, contentWidth, 32, 7, 7, "F");

    doc.setTextColor(35, 35, 35);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(12.5);
    doc.text("Risk Score", MARGIN + 10, y + 19);

    doc.setFontSize(15);
    doc.text(riskScore, pageWidth - MARGIN - 10, y + 19, { align: "right" });

    y += 32 + SECTION_GAP;

    // =========================
    // SECTIONS (auto-paginated)
    // =========================
    const sections = [
      {
        title: "PERSONAL INFORMATION",
        rows: [
          { label: "Name", value: result.name || "--" },
          { label: "Date of Birth", value: result.date_of_birth || "--" },
        ],
      },
      {
        title: "DOCUMENT INFORMATION",
        rows: [{ label: "Document ID", value: result.document_id || "--" }],
      },
      {
        title: "VERIFICATION DETAILS",
        rows: [
          { label: "Face Match", value: faceMatch },
          ...(result.document_authenticity !== undefined
            ? [
                {
                  label: "Document Authenticity",
                  value: documentAuthenticity,
                },
              ]
            : []),
        ],
      },
    ];

    sections.forEach((section) => {
      y = drawSection(doc, section, y, pageWidth, pageHeight, formattedDateTime);
    });

    // =========================
    // FOOTER (every page, added last so "Page X of Y" is accurate)
    // =========================
    finalizeFooters(doc, pageWidth, pageHeight);

    doc.save("FORGE_GUARD_Verification_Report.pdf");
  };

  return (
    <button className="pdf-button" onClick={generateReport}>
      Generate PDF Report
    </button>
  );
}

// Draws the big navy banner + report title used on page 1 only.
// Returns the y cursor where the first content block should start.
function drawMainHeader(doc, pageWidth, formattedDateTime) {
  doc.setFillColor(31, 43, 61);
  doc.rect(0, 0, pageWidth, 54, "F");

  doc.setTextColor(255, 255, 255);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(22);
  doc.text("FORGE GUARD", MARGIN, 19);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(11);
  doc.text("Document Verification System", MARGIN, 31);

  doc.setFontSize(9.5);
  doc.text("Generated:", pageWidth - MARGIN, 20, { align: "right" });
  doc.text(formattedDateTime, pageWidth - MARGIN, 27, { align: "right" });

  let y = 75;

  doc.setTextColor(35, 35, 35);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.text("DOCUMENT VERIFICATION REPORT", MARGIN, y);

  doc.setDrawColor(215, 215, 215);
  doc.setLineWidth(0.3);
  doc.line(MARGIN, y + 7, pageWidth - MARGIN, y + 7);

  return 95;
}

// Draws a compact banner at the top of continuation pages (page 2+).
// Shows the same generated date/time as page 1 instead of a
// "(continued)" label. Returns the y cursor where content should resume.
function drawContinuationHeader(doc, pageWidth, formattedDateTime) {
  doc.setFillColor(31, 43, 61);
  doc.rect(0, 0, pageWidth, 24, "F");

  doc.setTextColor(255, 255, 255);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(13);
  doc.text("FORGE GUARD", MARGIN, 15);

  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.text(`Generated: ${formattedDateTime}`, pageWidth - MARGIN, 15, {
    align: "right",
  });

  return 42;
}

// If `requiredHeight` won't fit before the footer reserve, starts a new
// page (with the continuation header) and returns the new y cursor.
// Otherwise returns y unchanged.
function ensureSpace(doc, y, pageWidth, pageHeight, requiredHeight, formattedDateTime) {
  if (y + requiredHeight > pageHeight - FOOTER_RESERVE) {
    doc.addPage();
    return drawContinuationHeader(doc, pageWidth, formattedDateTime);
  }
  return y;
}

// Draws a full section (heading + rows), breaking across pages if needed.
// If a section is split mid-way, the heading is repeated on the new page
// with a "(CONTINUED)" suffix so the reader keeps context.
function drawSection(doc, section, y, pageWidth, pageHeight, formattedDateTime) {
  // Keep the heading glued to at least its first row.
  y = ensureSpace(doc, y, pageWidth, pageHeight, HEADING_TO_ROW + 4, formattedDateTime);

  drawSectionHeading(doc, section.title, MARGIN, y, pageWidth);
  let rowY = y + HEADING_TO_ROW;

  section.rows.forEach((row, index) => {
    if (index > 0 && rowY + ROW_SPACING > pageHeight - FOOTER_RESERVE) {
      doc.addPage();
      const contY = drawContinuationHeader(doc, pageWidth, formattedDateTime);
      drawSectionHeading(
        doc,
        `${section.title} (CONTINUED)`,
        MARGIN,
        contY,
        pageWidth
      );
      rowY = contY + HEADING_TO_ROW;
    }

    drawRow(doc, row.label, row.value, MARGIN, rowY, pageWidth);
    rowY += ROW_SPACING;
  });

  // Cursor for the next section: back off the trailing ROW_SPACING and
  // apply the standard inter-section gap.
  return rowY - ROW_SPACING + SECTION_GAP;
}

function drawSectionHeading(doc, title, margin, y, pageWidth) {
  doc.setTextColor(35, 35, 35);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(13);

  doc.text(title, margin, y);

  doc.setDrawColor(215, 215, 215);
  doc.setLineWidth(0.3);
  doc.line(margin, y + 6, pageWidth - margin, y + 6);
}

function drawRow(doc, label, value, margin, y, pageWidth) {
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10.5);
  doc.setTextColor(100, 112, 132);
  doc.text(label, margin, y);

  doc.setFont("helvetica", "bold");
  doc.setTextColor(35, 35, 35);

  // Shrink the value if it's long enough to risk overlapping the label
  // (e.g. long names, long document IDs).
  const maxValueWidth = pageWidth - margin * 2 - doc.getTextWidth(label) - 15;
  fitText(doc, String(value), maxValueWidth, 10.5, {
    x: pageWidth - margin,
    y,
    align: "right",
  });
}

// Draws text right-aligned at (x, y), shrinking the font size (down to a
// reasonable floor) until it fits within maxWidth instead of overlapping
// neighboring content.
function fitText(doc, text, maxWidth, startSize, { x, y, align }) {
  let size = startSize;
  const minSize = startSize * 0.6;

  doc.setFontSize(size);
  while (doc.getTextWidth(text) > maxWidth && size > minSize) {
    size -= 0.5;
    doc.setFontSize(size);
  }

  doc.text(text, x, y, { align });
}

// Adds the confidentiality line + "Page X of Y" to every page. Done last
// so the total page count is known.
function finalizeFooters(doc, pageWidth, pageHeight) {
  const totalPages = doc.internal.getNumberOfPages();

  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);

    doc.setTextColor(25, 25, 25);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8.5);
    doc.text(
      "Generated by FORGE GUARD Document Verification System \u2022 Confidential Verification Report",
      pageWidth / 2,
      pageHeight - 8,
      { align: "center" }
    );

    doc.setFontSize(8);
    doc.setTextColor(120, 120, 120);
    doc.text(`Page ${i} of ${totalPages}`, pageWidth - MARGIN, pageHeight - 3, {
      align: "right",
    });
  }
}

export default PdfReport;
