import React, { useState, useEffect } from 'react';

const API_BASE = 'http://127.0.0.1:8000/api/v1';

export default function AnalyticsDashboard() {
  const [selectedEngine, setSelectedEngine] = useState<string>('forecasting');
  const [analyticsData, setAnalyticsData] = useState<any>(null);

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      const res = await fetch(`${API_BASE}/overview/`);
      const data = await res.json();
      setAnalyticsData(data);
    } catch (e) {
      console.log('Analytics data fetch fallback');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Sub-navigation */}
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '8px' }}>
        {[
          { id: 'forecasting', label: '📈 Healthcare & Retail Forecasting' },
          { id: 'segmentation', label: '🏦 Banking Customer Risk Clusters' },
          { id: 'claims_queue', label: '🛡️ Insurance Claims Anomaly Queue' },
          { id: 'calibration', label: '🧬 Clinical Risk Calibration & PR-AUC' },
          { id: 'fraud_anomaly', label: '💳 Fraud Trend Anomaly Detector' },
        ].map(engine => (
          <button
            key={engine.id}
            onClick={() => setSelectedEngine(engine.id)}
            className="glass-card"
            style={{
              padding: '10px 16px',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer',
              color: selectedEngine === engine.id ? 'var(--primary)' : 'var(--text-muted)',
              borderColor: selectedEngine === engine.id ? 'var(--primary)' : 'var(--border-color)',
              background: selectedEngine === engine.id ? 'rgba(59, 130, 246, 0.15)' : 'var(--bg-card)'
            }}
          >
            {engine.label}
          </button>
        ))}
      </div>

      {/* ENGINE 1: FORECASTING */}
      {selectedEngine === 'forecasting' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div className="glass-card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h4>🏥 Healthcare 7-Day Capacity Forecast</h4>
              <span className="badge badge-emerald">XGBoost Regressor</span>
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '6px 0 16px 0' }}>Model MAE: 11.60 | Series Horizon: 7 Days</p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '16px' }}>
              <div style={{ padding: '12px', background: 'rgba(0,0,0,0.3)', borderRadius: '6px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Current Occupancy</span>
                <h3 style={{ margin: '4px 0', color: '#38bdf8' }}>76.48%</h3>
              </div>
              <div style={{ padding: '12px', background: 'rgba(0,0,0,0.3)', borderRadius: '6px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>7-Day Forecast Avg</span>
                <h3 style={{ margin: '4px 0', color: '#34d399' }}>77.91%</h3>
              </div>
            </div>

            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>7-Day Forecast Trajectory:</span>
            <div style={{ display: 'flex', gap: '6px', marginTop: '8px' }}>
              {[78.2, 79.4, 79.0, 78.3, 73.9, 80.3, 76.2].map((val, idx) => (
                <div key={idx} style={{ flex: 1, padding: '6px', background: 'rgba(56, 189, 248, 0.1)', borderRadius: '4px', textAlign: 'center', fontSize: '0.75rem', fontWeight: 600 }}>
                  Day {idx + 1}<br/><span style={{ color: '#38bdf8' }}>{val}%</span>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h4>🛒 Retail 14-Period Demand Forecast</h4>
              <span className="badge badge-purple">XGBoost vs Moving Avg</span>
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '6px 0 16px 0' }}>MAE: 12.65 | MAE Baseline: 12.60</p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '16px' }}>
              <div style={{ padding: '12px', background: 'rgba(0,0,0,0.3)', borderRadius: '6px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Current Avg Quantity</span>
                <h3 style={{ margin: '4px 0' }}>25.05 units</h3>
              </div>
              <div style={{ padding: '12px', background: 'rgba(0,0,0,0.3)', borderRadius: '6px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Forecast Demand</span>
                <h3 style={{ margin: '4px 0', color: '#a7f3d0' }}>354.4 units</h3>
              </div>
            </div>

            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', background: 'rgba(0,0,0,0.4)', padding: '10px', borderRadius: '6px' }}>
              💡 <strong>Prescriptive Inventory Guidance:</strong> Maintain +15% safety stock buffer over next 14 periods.
            </p>
          </div>
        </div>
      )}

      {/* ENGINE 2: SEGMENTATION */}
      {selectedEngine === 'segmentation' && (
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <h3>Banking Customer Credit Risk Clusters</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>K-Means Clustering (k=3) & PCA Dimensionality Reduction</p>
            </div>
            <span className="badge badge-emerald">PCA Explained Var: 51.3%</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <div className="glass-card" style={{ padding: '16px', borderLeft: '3px solid #f43f5e' }}>
              <span className="badge badge-rose">Cluster 0 (625 Customers)</span>
              <h4 style={{ margin: '8px 0' }}>HIGH RISK COHORT</h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Avg Income: $81,096 | Avg Credit: $18,154</p>
              <p style={{ fontSize: '0.8rem', color: '#fb7185', fontWeight: 600, marginTop: '6px' }}>Default Rate: 76.16%</p>
            </div>

            <div className="glass-card" style={{ padding: '16px', borderLeft: '3px solid #f59e0b' }}>
              <span className="badge badge-amber">Cluster 1 (611 Customers)</span>
              <h4 style={{ margin: '8px 0' }}>MODERATE RISK COHORT</h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Avg Income: $84,538 | Avg Credit: $16,796</p>
              <p style={{ fontSize: '0.8rem', color: '#f59e0b', fontWeight: 600, marginTop: '6px' }}>Default Rate: 59.90%</p>
            </div>

            <div className="glass-card" style={{ padding: '16px', borderLeft: '3px solid #3b82f6' }}>
              <span className="badge badge-cyan">Cluster 2 (564 Customers)</span>
              <h4 style={{ margin: '8px 0' }}>PRIME LOAN COHORT</h4>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Avg Income: $83,417 | Avg Credit: $18,499</p>
              <p style={{ fontSize: '0.8rem', color: '#38bdf8', fontWeight: 600, marginTop: '6px' }}>Default Rate: 59.75%</p>
            </div>
          </div>
        </div>
      )}

      {/* ENGINE 3: CLAIMS QUEUE */}
      {selectedEngine === 'claims_queue' && (
        <div className="glass-card" style={{ padding: '20px' }}>
          <h3>Insurance Claims Fraud Anomaly Queue</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>Isolation Forest Anomaly Scoring (122 High Risk Claims Identified)</p>

          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)', textAlign: 'left' }}>
                <th style={{ padding: '10px' }}>Policy ID</th>
                <th style={{ padding: '10px' }}>Claim Amount</th>
                <th style={{ padding: '10px' }}>Incident Type</th>
                <th style={{ padding: '10px' }}>Anomaly Score</th>
                <th style={{ padding: '10px' }}>Risk Tier</th>
                <th style={{ padding: '10px' }}>Investigation Reason</th>
              </tr>
            </thead>
            <tbody>
              {[
                { id: 'POL-3431', amount: 94300, incident: 'Parked Car', score: 0.6904, tier: 'HIGH', reason: 'Severe claim amount anomaly relative to vehicle age' },
                { id: 'POL-4064', amount: 94660, incident: 'Single Vehicle Collision', score: 0.6869, tier: 'HIGH', reason: 'Severe claim amount anomaly relative to vehicle age' },
                { id: 'POL-3378', amount: 92852, incident: 'Parked Car', score: 0.6814, tier: 'HIGH', reason: 'Severe claim amount anomaly relative to vehicle age' },
                { id: 'POL-3935', amount: 94224, incident: 'Parked Car', score: 0.6805, tier: 'HIGH', reason: 'Severe claim amount anomaly relative to vehicle age' },
                { id: 'POL-3231', amount: 93636, incident: 'Vehicle Theft', score: 0.6788, tier: 'HIGH', reason: 'Severe claim amount anomaly relative to vehicle age' },
              ].map((row, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '10px', fontWeight: 600 }}>{row.id}</td>
                  <td style={{ padding: '10px', fontWeight: 600 }}>${row.amount.toLocaleString()}</td>
                  <td style={{ padding: '10px' }}>{row.incident}</td>
                  <td style={{ padding: '10px', color: '#fb7185', fontWeight: 600 }}>{row.score}</td>
                  <td style={{ padding: '10px' }}><span className="badge badge-rose">{row.tier}</span></td>
                  <td style={{ padding: '10px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>{row.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ENGINE 4: CLINICAL CALIBRATION */}
      {selectedEngine === 'calibration' && (
        <div className="glass-card" style={{ padding: '20px' }}>
          <h3>Clinical EHR Readmission Risk Calibration & PR-AUC</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginTop: '16px' }}>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>PR-AUC Metric</span>
              <h2 style={{ color: '#38bdf8' }}>0.4271</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Calibrated Decision Threshold</span>
              <h2 style={{ color: '#34d399' }}>0.1499</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>High-Risk Cohort Count</span>
              <h2 style={{ color: '#fb7185' }}>94 Patients</h2>
            </div>
          </div>
        </div>
      )}

      {/* ENGINE 5: FRAUD ANOMALY DETECTOR */}
      {selectedEngine === 'fraud_anomaly' && (
        <div className="glass-card" style={{ padding: '20px' }}>
          <h3>Credit Card Fraud Trend Rolling Anomaly Detector</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginTop: '16px' }}>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>7-Day Baseline Rate</span>
              <h2>11.27%</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Current Rate</span>
              <h2 style={{ color: '#34d399' }}>10.53%</h2>
            </div>
            <div style={{ padding: '14px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Pct Change vs Baseline</span>
              <h2 style={{ color: '#38bdf8' }}>-6.63%</h2>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
