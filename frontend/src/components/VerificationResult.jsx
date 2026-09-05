import PdfReport from "./PdfReport";

function VerificationResult({ result, loading }) {
  if (loading) {
    return (
      <section className="result-card">
        <h2>Verification Result</h2>

        <div className="verification-loading">
          <div className="spinner"></div>
          <h3>Verifying Document...</h3>
          <p>Please wait while the document is being analyzed.</p>
        </div>
      </section>
    );
  }

  if (!result) {
    return (
      <section className="result-card">
        <h2>Verification Result</h2>

        <div className="empty-result">
          <div className="empty-icon">📄</div>
          <h3>No Verification Yet</h3>
          <p>Upload a document and click Verify Document to see the result.</p>
        </div>
      </section>
    );
  }

  const status = result.status?.toLowerCase();

  const statusClass =
    status === "verified"
      ? "status-verified"
      : status === "rejected"
      ? "status-rejected"
      : "status-review";

  return (
    <section className="result-card">
      <h2>Verification Result</h2>

      {/* Verification Status */}
      <div className={`verification-status ${statusClass}`}>
        <div className="status-icon">
          {status === "verified"
            ? "✓"
            : status === "rejected"
            ? "✕"
            : "!"}
        </div>

        <div>
          <span>Verification Status</span>
          <strong>
            {result.status?.toUpperCase() || "UNKNOWN"}
          </strong>
        </div>
      </div>

      {/* Risk Score */}
      <div className="risk-score">
        <span>Risk Score</span>

        <strong>
          {result.risk_score !== undefined
            ? `${result.risk_score}%`
            : "--"}
        </strong>
      </div>

      {/* Personal Information */}
      <div className="result-section">
        <h3>👤 Personal Information</h3>

        <div className="result-row">
          <span>Name</span>
          <strong>{result.name || "--"}</strong>
        </div>

        <div className="result-row">
          <span>Date of Birth</span>
          <strong>{result.date_of_birth || "--"}</strong>
        </div>
      </div>

      {/* Document Information */}
      <div className="result-section">
        <h3>📄 Document Information</h3>

        <div className="result-row">
          <span>Document ID</span>
          <strong>{result.document_id || "--"}</strong>
        </div>

        {result.filename && (
          <div className="result-row">
            <span>File</span>
            <strong>{result.filename}</strong>
          </div>
        )}
      </div>

      {/* Verification Details */}
      <div className="result-section">
        <h3>🔐 Verification Details</h3>

        <div className="result-row">
          <span>Face Match</span>
          <strong>
            {result.face_match_score !== undefined
              ? `${result.face_match_score}%`
              : "--"}
          </strong>
        </div>

        <div className="result-row">
          <span>Document Authenticity</span>
          <strong>
            {result.document_authenticity !== undefined
              ? `${result.document_authenticity}%`
              : "--"}
          </strong>
        </div>
      </div>
      
      <PdfReport result={result} />
      
    </section>
  );
}

export default VerificationResult;