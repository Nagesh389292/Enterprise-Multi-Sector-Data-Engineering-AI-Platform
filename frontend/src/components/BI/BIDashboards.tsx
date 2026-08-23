import React, { useState, useEffect } from 'react';

const API_BASE = 'http://127.0.0.1:8000/api/v1';

export default function BIDashboards() {
  const [selectedDashboard, setSelectedDashboard] = useState<string>('executive');
  const [metricsData, setMetricsData] = useState<any>(null);
  const [explainingMetric, setExplainingMetric] = useState<string | null>(null);
  const [copilotExplanation, setCopilotExplanation] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchSectorMetrics();
  }, []);

  const fetchSectorMetrics = async () => {
    try {
      const res = await fetch(`${API_BASE}/overview/`);
      const data = await res.json();
      setMetricsData(data);
    } catch (e) {
      console.log('Metrics fetch fallback');
    }
  };

  const handleExplainMetric = async (metricName: string, value: any, context: string) => {
    setExplainingMetric(metricName);
    setCopilotExplanation(null);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/copilot/query/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: `Explain metric ${metricName} with value ${value} in context of ${context}. What does this mean for our operational performance?`
        })
      });
      const data = await res.json();
      setCopilotExplanation(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Sector Sub-Navigation Tabs */}
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '8px' }}>
        {[
          { id: 'executive', label: '👑 Executive Command Center' },
          { id: 'fraud', label: '💳 Fraud Intelligence' },
          { id: 'banking', label: '🏦 Banking Credit Risk' },
          { id: 'healthcare', label: '🏥 Healthcare Utilization' },
          { id: 'clinical', label: '🧬 Clinical Readmission' },
          { id: 'insurance', label: '🛡️ Insurance Claims Fraud' },
          { id: 'retail', label: '🛒 Retail Demand & Revenue' },
        ].map(dash => (
          <button
            key={dash.id}
            onClick={() => {
              setSelectedDashboard(dash.id);
              setCopilotExplanation(null);
              setExplainingMetric(null);
            }}
            className="glass-card"
            style={{
              padding: '10px 16px',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer',
              color: selectedDashboard === dash.id ? 'var(--primary)' : 'var(--text-muted)',
              borderColor: selectedDashboard === dash.id ? 'var(--primary)' : 'var(--border-color)',
              background: selectedDashboard === dash.id ? 'rgba(59, 130, 246, 0.15)' : 'var(--bg-card)'
            }}
          >
            {dash.label}
          </button>
        ))}
      </div>

      {/* DASHBOARD 1: EXECUTIVE COMMAND CENTER */}
      {selectedDashboard === 'executive' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="glass-card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <h3>Executive Cross-Sector KPI Monitor</h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>PySpark Medallion Data Lakehouse & PostgreSQL Gold Sync</p>
              </div>
              <span className="badge badge-emerald">6/6 SECTORS LIVE</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
              <div className="glass-card" style={{ padding: '16px', borderLeft: '3px solid #3b82f6' }}>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Credit Card Fraud Rate</span>
                <h3 style={{ fontSize: '1.6rem', margin: '6px 0', color: '#fb7185' }}>11.04%</h3>
                <button
                  onClick={() => handleExplainMetric('Credit Card Fraud Rate', '11.04%', 'Kaggle Fraud Benchmark')}
                  style={{ background: 'rgba(59, 130, 246, 0.2)', border: '1px solid rgba(59, 130, 246, 0.4)', color: '#38bdf8', borderRadius: '4px', padding: '4px 8px', fontSize: '0.75rem', cursor: 'pointer' }}
                >
                  ⚡ Explain This Metric
                </button>
              </div>

              <div className="glass-card" style={{ padding: '16px', borderLeft: '3px solid #10b981' }}>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Banking Default Rate</span>
                <h3 style={{ fontSize: '1.6rem', margin: '6px 0', color: '#f59e0b' }}>65.50%</h3>
                <button
                  onClick={() => handleExplainMetric('Banking Loan Default Rate', '65.50%', 'German Credit Risk Benchmark')}
                  style={{ background: 'rgba(59, 130, 246, 0.2)', border: '1px solid rgba(59, 130, 246, 0.4)', color: '#38bdf8', borderRadius: '4px', padding: '4px 8px', fontSize: '0.75rem', cursor: 'pointer' }}
                >
                  ⚡ Explain This Metric
                </button>
              </div>

              <div className="glass-card" style={{ padding: '16px', borderLeft: '3px solid #8b5cf6' }}>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Healthcare Bed Occupancy</span>
                <h3 style={{ fontSize: '1.6rem', margin: '6px 0', color: '#38bdf8' }}>76.48%</h3>
                <button
                  onClick={() => handleExplainMetric('Healthcare Bed Occupancy', '76.48%', 'HMIS Hospital Indicators')}
                  style={{ background: 'rgba(59, 130, 246, 0.2)', border: '1px solid rgba(59, 130, 246, 0.4)', color: '#38bdf8', borderRadius: '4px', padding: '4px 8px', fontSize: '0.75rem', cursor: 'pointer' }}
                >
                  ⚡ Explain This Metric
                </button>
              </div>

              <div className="glass-card" style={{ padding: '16px', borderLeft: '3px solid #ec4899' }}>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>30-Day Clinical Readmission</span>
                <h3 style={{ fontSize: '1.6rem', margin: '6px 0', color: '#a7f3d0' }}>25.25%</h3>
                <button
                  onClick={() => handleExplainMetric('Clinical 30-Day Readmission', '25.25%', 'UCI Diabetes 130-Hospitals Benchmark')}
                  style={{ background: 'rgba(59, 130, 246, 0.2)', border: '1px solid rgba(59, 130, 246, 0.4)', color: '#38bdf8', borderRadius: '4px', padding: '4px 8px', fontSize: '0.75rem', cursor: 'pointer' }}
                >
                  ⚡ Explain This Metric
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* DASHBOARD 2: FRAUD INTELLIGENCE */}
      {selectedDashboard === 'fraud' && (
        <div className="glass-card" style={{ padding: '20px' }}>
          <h3>Credit Card Fraud Intelligence & Model Telemetry</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginTop: '16px' }}>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Champion XGBoost F1</span>
              <h2>0.9796</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Champion ROC-AUC</span>
              <h2 style={{ color: '#34d399' }}>1.0000</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Temporal Out-Of-Time F1</span>
              <h2 style={{ color: '#38bdf8' }}>0.9636</h2>
            </div>
          </div>
        </div>
      )}

      {/* DASHBOARD 3: BANKING CREDIT RISK */}
      {selectedDashboard === 'banking' && (
        <div className="glass-card" style={{ padding: '20px' }}>
          <h3>Banking Credit Risk & Loan Portfolio Analysis</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', marginTop: '16px' }}>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Total Credit Granted</span>
              <h2>$32,042,353.00</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>LightGBM Risk F1 Score</span>
              <h2 style={{ color: '#f59e0b' }}>0.7601</h2>
            </div>
          </div>
        </div>
      )}

      {/* DASHBOARD 4: HEALTHCARE UTILIZATION */}
      {selectedDashboard === 'healthcare' && (
        <div className="glass-card" style={{ padding: '20px' }}>
          <h3>National Health Mission - Hospital Capacity & OPD/IPD Load</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginTop: '16px' }}>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Hospitals Reporting</span>
              <h2>1,200</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Avg Bed Occupancy Rate</span>
              <h2 style={{ color: '#38bdf8' }}>76.48%</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Avg OPD / IPD Ratio</span>
              <h2>11.31</h2>
            </div>
          </div>
        </div>
      )}

      {/* DASHBOARD 5: CLINICAL READMISSION */}
      {selectedDashboard === 'clinical' && (
        <div className="glass-card" style={{ padding: '20px' }}>
          <h3>Clinical Inpatient EHR 30-Day Hospital Readmission Risk</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginTop: '16px' }}>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Readmission Rate</span>
              <h2 style={{ color: '#fb7185' }}>25.25%</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Avg Hospital Stay</span>
              <h2>7.38 days</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Random Forest ROC-AUC</span>
              <h2 style={{ color: '#a7f3d0' }}>0.6298</h2>
            </div>
          </div>
        </div>
      )}

      {/* DASHBOARD 6: INSURANCE CLAIMS */}
      {selectedDashboard === 'insurance' && (
        <div className="glass-card" style={{ padding: '20px' }}>
          <h3>Auto Insurance Claims Fraud & Exposure Monitor</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginTop: '16px' }}>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Claims Fraud Rate</span>
              <h2 style={{ color: '#fb7185' }}>20.00%</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Total Claims Amount</span>
              <h2>$39,539,898.00</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Total Claims Processed</span>
              <h2>1,500</h2>
            </div>
          </div>
        </div>
      )}

      {/* DASHBOARD 7: RETAIL DEMAND */}
      {selectedDashboard === 'retail' && (
        <div className="glass-card" style={{ padding: '20px' }}>
          <h3>Retail Sales Revenue & Inventory Demand Forecasting</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginTop: '16px' }}>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Gross Revenue</span>
              <h2 style={{ color: '#34d399' }}>$32,277,430.52</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Total Units Sold</span>
              <h2>75,165</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Total Invoices</span>
              <h2>3,000</h2>
            </div>
          </div>
        </div>
      )}

      {/* Interactive Copilot Metric Explanation Modal Drawer */}
      {(loading || copilotExplanation) && (
        <div className="glass-card" style={{ padding: '20px', borderLeft: '3px solid var(--accent-cyan)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h4>🤖 AI Copilot Metric Investigation: {explainingMetric}</h4>
            <button onClick={() => setCopilotExplanation(null)} style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer' }}>×</button>
          </div>

          {loading ? (
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginTop: '12px' }}>Querying PySpark Lakehouse Gold Store & Copilot Router...</p>
          ) : (
            <div style={{ marginTop: '14px' }}>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '10px' }}>
                <span className="badge badge-purple">{copilotExplanation?.intent || 'METRICS_INVESTIGATION'}</span>
                <span className="badge badge-cyan">{copilotExplanation?.llm_provider || 'Local Analytics Engine'}</span>
              </div>
              <p style={{ fontSize: '0.92rem', lineHeight: '1.5', color: '#e2e8f0' }}>
                {copilotExplanation?.executive_answer || copilotExplanation?.executive_summary}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
