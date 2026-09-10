import { useState } from "react";
import "./App.css";
import VerificationResult from "./components/VerificationResult";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (selectedFile) {
      setFile(selectedFile);
      setResult(null);
      setError("");
    }
  };

  const handleVerify = async () => {
    if (!file) {
      setError("Please select a document first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/verify-document",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error("Verification request failed.");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(
        "Could not connect to the backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>Document Verification</h1>
        <p>AI-Powered Document Verification Dashboard</p>
      </header>

      <main className="dashboard">

        {/* Upload Section */}
        <section className="upload-card">
          <h2>Upload Document</h2>
          <p>Select a document to begin verification.</p>

          <label className="upload-box">
            <span>📄</span>

            <strong>
              {file ? file.name : "Choose a document"}
            </strong>

            <small>
              {file
                ? `${(file.size / 1024 / 1024).toFixed(2)} MB`
                : "PDF, JPG or PNG"}
            </small>

            <input
              type="file"
              accept=".pdf,.jpg,.jpeg,.png"
              onChange={handleFileChange}
            />
          </label>

          <button
            className="verify-button"
            onClick={handleVerify}
            disabled={!file || loading}
          >
            {loading ? "Verifying..." : "Verify Document"}
          </button>

          {error && <p className="error">{error}</p>}
        </section>

        {/* Result Section */}
        <VerificationResult result={result}
        loading={loading} 
        />
      </main>
    </div>
  );
}

export default App;