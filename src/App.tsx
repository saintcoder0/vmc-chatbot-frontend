import { useEffect, useState } from "react";

type DbPing = { ok: boolean };

type Complaint = {
  id: number;
  phone: string;
  category: string;
  description: string;
  ward: string | null;
  address: string | null;
  status: string;
  created_at: string;
};

type Property = {
  property_id: number;
  owner_name: string;
  address: string;
  tax_amount: number;
  due_date: string;
  status: string;
};

type Tab = "overview" | "complaints" | "properties";

export const App = () => {
  const [dbStatus, setDbStatus] = useState<"unknown" | "ok" | "error">("unknown");
  const [activeTab, setActiveTab] = useState<Tab>("overview");
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loadingComplaints, setLoadingComplaints] = useState(false);
  const [complaintsError, setComplaintsError] = useState<string | null>(null);
  const [properties, setProperties] = useState<Property[]>([]);
  const [loadingProperties, setLoadingProperties] = useState(false);
  const [propertiesError, setPropertiesError] = useState<string | null>(null);

  useEffect(() => {
    // Check backend DB health
    fetch("http://localhost:8001/db/ping")
      .then((res) => {
        if (!res.ok) throw new Error("bad status");
        return res.json() as Promise<DbPing>;
      })
      .then(() => setDbStatus("ok"))
      .catch(() => setDbStatus("error"));
  }, []);

  useEffect(() => {
    if (activeTab !== "complaints") return;
    setLoadingComplaints(true);
    setComplaintsError(null);

    fetch("http://localhost:8001/admin/complaints")
      .then((res) => {
        if (!res.ok) throw new Error("failed");
        return res.json() as Promise<Complaint[]>;
      })
      .then((data) => setComplaints(data))
      .catch(() => setComplaintsError("Could not load complaints."))
      .finally(() => setLoadingComplaints(false));
  }, [activeTab]);

  useEffect(() => {
    if (activeTab !== "properties") return;
    setLoadingProperties(true);
    setPropertiesError(null);

    fetch("http://localhost:8001/admin/properties")
      .then((res) => {
        if (!res.ok) throw new Error("failed");
        return res.json() as Promise<Property[]>;
      })
      .then((data) => setProperties(data))
      .catch(() => setPropertiesError("Could not load properties."))
      .finally(() => setLoadingProperties(false));
  }, [activeTab]);

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1 className="logo">VMC Dashboard</h1>
        <nav>
          <button
            className={`nav-item ${activeTab === "overview" ? "nav-item-active" : ""}`}
            onClick={() => setActiveTab("overview")}
          >
            Overview
          </button>
          <button
            className={`nav-item ${activeTab === "complaints" ? "nav-item-active" : ""}`}
            onClick={() => setActiveTab("complaints")}
          >
            Complaints
          </button>
          <button
            className={`nav-item ${activeTab === "properties" ? "nav-item-active" : ""}`}
            onClick={() => setActiveTab("properties")}
          >
            Properties
          </button>
        </nav>
      </aside>

      <main className="content">
        <header className="topbar">
          <h2>
            {activeTab === "overview"
              ? "Admin Overview"
              : activeTab === "complaints"
              ? "WhatsApp Complaints"
              : "Property Tax Accounts"}
          </h2>
          <span className="badge">Hackathon Prototype</span>
        </header>

        {activeTab === "overview" && (
          <section className="cards">
            <div className="card">
              <h3>Backend status</h3>
              <p>FastAPI server should be running on port 8001.</p>
            </div>

            <div className="card">
              <h3>Database connection</h3>
              {dbStatus === "unknown" && <p>Checking /db/ping…</p>}
              {dbStatus === "ok" && <p className="ok">Connected ✅</p>}
              {dbStatus === "error" && (
                <p className="error">
                  Not reachable ❌ — ensure MySQL is running and backend `DATABASE_URL` is correct.
                </p>
              )}
            </div>

            <div className="card">
              <h3>Workflow image</h3>
              <p>Use this panel to showcase your system architecture or chatbot flow.</p>
              <img
                className="workflow-image"
                src="https://dummyimage.com/600x260/0f172a/38bdf8&text=VMC+WhatsApp+Chatbot+Workflow"
                alt="VMC WhatsApp Chatbot workflow"
              />
            </div>
          </section>
        )}

        {activeTab === "complaints" && (
          <section className="card">
            <h3>Recent WhatsApp complaints</h3>
            {loadingComplaints && <p>Loading complaints…</p>}
            {complaintsError && <p className="error">{complaintsError}</p>}
            {!loadingComplaints && !complaintsError && complaints.length === 0 && (
              <p>No complaints yet. Send a WhatsApp message with the complaint format to create one.</p>
            )}
            {!loadingComplaints && complaints.length > 0 && (
              <div className="table-wrapper">
                <table className="table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Phone</th>
                      <th>Category</th>
                      <th>Status</th>
                      <th>Ward</th>
                      <th>Created at</th>
                    </tr>
                  </thead>
                  <tbody>
                    {complaints.map((c) => (
                      <tr key={c.id}>
                        <td>{c.id}</td>
                        <td>{c.phone}</td>
                        <td>{c.category}</td>
                        <td>{c.status}</td>
                        <td>{c.ward ?? "-"}</td>
                        <td>{new Date(c.created_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}

        {activeTab === "properties" && (
          <section className="card">
            <h3>Property tax accounts</h3>
            {loadingProperties && <p>Loading properties…</p>}
            {propertiesError && <p className="error">{propertiesError}</p>}
            {!loadingProperties && !propertiesError && properties.length === 0 && (
              <p>No properties yet. Run the seed script to add examples.</p>
            )}
            {!loadingProperties && properties.length > 0 && (
              <div className="table-wrapper">
                <table className="table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Owner</th>
                      <th>Address</th>
                      <th>Tax amount</th>
                      <th>Due date</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {properties.map((p) => (
                      <tr key={p.property_id}>
                        <td>{p.property_id}</td>
                        <td>{p.owner_name}</td>
                        <td>{p.address}</td>
                        <td>₹ {p.tax_amount.toFixed(2)}</td>
                        <td>{new Date(p.due_date).toLocaleDateString()}</td>
                        <td>{p.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
};

