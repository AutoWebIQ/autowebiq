import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { toast } from 'sonner';
import { CreditCard, CheckCircle, ArrowLeft, Sparkles } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CreditsPage = () => {
  const navigate = useNavigate();
  const [packages, setPackages] = useState([]);
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user') || '{}'));
  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState([]);
  const [creditSummary, setCreditSummary] = useState(null);
  const [pricing, setPricing] = useState(null);
  const [activeTab, setActiveTab] = useState('buy'); // 'buy', 'history', 'pricing'

  const getAxiosConfig = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
    withCredentials: true
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [packagesRes, userRes, transactionsRes, summaryRes, pricingRes] = await Promise.all([
        axios.get(`${API}/credits/packages`),
        axios.get(`${API}/auth/me`, getAxiosConfig()),
        axios.get(`${API}/credits/transactions?limit=20`, getAxiosConfig()),
        axios.get(`${API}/credits/summary`, getAxiosConfig()),
        axios.get(`${API}/credits/pricing`)
      ]);
      setPackages(packagesRes.data);
      setUser(userRes.data);
      setTransactions(transactionsRes.data.transactions || []);
      setCreditSummary(summaryRes.data);
      setPricing(pricingRes.data);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (packageData) => {
    try {
      const orderRes = await axios.post(`${API}/credits/create-order`, {
        package_id: packageData.id
      }, getAxiosConfig());

      const options = {
        key: orderRes.data.key_id,
        amount: orderRes.data.amount,
        currency: orderRes.data.currency,
        order_id: orderRes.data.order_id,
        name: 'AutoWebIQ',
        description: packageData.name,
        handler: async function (response) {
          try {
            await axios.post(`${API}/credits/verify-payment`, {
              order_id: response.razorpay_order_id,
              payment_id: response.razorpay_payment_id,
              signature: response.razorpay_signature
            }, getAxiosConfig());
            
            toast.success('Credits added successfully!');
            fetchData();
          } catch (error) {
            toast.error('Payment verification failed');
          }
        },
        prefill: {
          name: user.username,
          email: user.email
        },
        theme: {
          color: '#0ea5e9'
        }
      };

      const razorpay = new window.Razorpay(options);
      razorpay.open();
    } catch (error) {
      toast.error('Failed to initiate payment');
    }
  };

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <div className="credits-page-container" data-testid="credits-page">
      <nav className="dashboard-nav">
        <div className="nav-content">
          <Button
            data-testid="back-to-dashboard-btn"
            variant="ghost"
            onClick={() => navigate('/dashboard')}
          >
            <ArrowLeft className="mr-2" /> Back to Dashboard
          </Button>
          <div className="logo">
            <Sparkles className="logo-icon" />
            <span>AutoWebIQ</span>
          </div>
          <div className="credits-badge" data-testid="current-credits">
            <CreditCard size={16} />
            <span>{user.credits} Credits</span>
          </div>
        </div>
      </nav>

      <div className="credits-content">
        {/* Credit Summary Card */}
        {creditSummary && (
          <div className="credit-summary-card" style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '24px',
            borderRadius: '12px',
            marginBottom: '24px',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px'
          }}>
            <div>
              <div style={{ opacity: 0.9, fontSize: '14px' }}>Current Balance</div>
              <div style={{ fontSize: '32px', fontWeight: 'bold' }}>{creditSummary.current_balance}</div>
            </div>
            <div>
              <div style={{ opacity: 0.9, fontSize: '14px' }}>Total Spent</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{creditSummary.total_spent}</div>
            </div>
            <div>
              <div style={{ opacity: 0.9, fontSize: '14px' }}>Total Refunded</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4ade80' }}>{creditSummary.total_refunded}</div>
            </div>
            <div>
              <div style={{ opacity: 0.9, fontSize: '14px' }}>Total Purchased</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{creditSummary.total_purchased}</div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div style={{ 
          borderBottom: '2px solid #e5e7eb', 
          marginBottom: '24px',
          display: 'flex',
          gap: '16px'
        }}>
          {['buy', 'history', 'pricing'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                padding: '12px 24px',
                background: 'none',
                border: 'none',
                borderBottom: activeTab === tab ? '3px solid #667eea' : '3px solid transparent',
                color: activeTab === tab ? '#667eea' : '#666',
                fontWeight: activeTab === tab ? 'bold' : 'normal',
                cursor: 'pointer',
                fontSize: '16px',
                textTransform: 'capitalize'
              }}
            >
              {tab === 'buy' ? 'Buy Credits' : tab === 'history' ? 'Transaction History' : 'Pricing Table'}
            </button>
          ))}
        </div>

        {/* Buy Credits Tab */}
        {activeTab === 'buy' && (
          <>
            <div className="credits-header">
              <h1 data-testid="credits-title">Buy Credits</h1>
              <p data-testid="credits-subtitle">Use credits for AI messages and multi-agent builds. Dynamic pricing based on agents used.</p>
            </div>

            <div className="packages-grid" data-testid="packages-grid">
              {packages.map(pkg => (
                <Card key={pkg.id} className="package-card" data-testid={`package-card-${pkg.id}`}>
                  <div className="package-header">
                    <h3 data-testid={`package-name-${pkg.id}`}>{pkg.name}</h3>
                    <div className="package-price" data-testid={`package-price-${pkg.id}`}>
                      <span className="currency">₹</span>
                      <span className="amount">{pkg.price / 100}</span>
                    </div>
                  </div>
                  <div className="package-credits" data-testid={`package-credits-${pkg.id}`}>
                    <CreditCard size={24} className="credits-icon" />
                    <span className="credits-amount">{pkg.credits} Credits</span>
                  </div>
                  <ul className="package-features">
                    <li><CheckCircle size={16} /> {pkg.credits} AI credits</li>
                    <li><CheckCircle size={16} /> ~{Math.floor(pkg.credits / 5)} chat messages</li>
                    <li><CheckCircle size={16} /> ~{Math.floor(pkg.credits / 25)} full builds</li>
                    <li><CheckCircle size={16} /> All models supported</li>
                  </ul>
                  <Button
                    data-testid={`buy-package-btn-${pkg.id}`}
                    className="w-full package-buy-btn"
                    onClick={() => handlePurchase(pkg)}
                  >
                    Buy Now
                  </Button>
                </Card>
              ))}
            </div>
          </>
        )}

        {/* Transaction History Tab */}
        {activeTab === 'history' && (
          <div>
            <h2 style={{ marginBottom: '16px', fontSize: '24px', fontWeight: 'bold' }}>Transaction History</h2>
            {transactions.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '48px', color: '#666' }}>
                No transactions yet
              </div>
            ) : (
              <div style={{ 
                background: 'white',
                borderRadius: '8px',
                overflow: 'hidden',
                border: '1px solid #e5e7eb'
              }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead style={{ background: '#f9fafb' }}>
                    <tr>
                      <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Date</th>
                      <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Type</th>
                      <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600' }}>Operation</th>
                      <th style={{ padding: '12px', textAlign: 'right', fontWeight: '600' }}>Amount</th>
                      <th style={{ padding: '12px', textAlign: 'center', fontWeight: '600' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((txn, idx) => (
                      <tr key={txn.id} style={{ borderTop: idx > 0 ? '1px solid #e5e7eb' : 'none' }}>
                        <td style={{ padding: '12px' }}>
                          {new Date(txn.created_at).toLocaleString()}
                        </td>
                        <td style={{ padding: '12px' }}>
                          <span style={{
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '12px',
                            fontWeight: '500',
                            background: txn.type === 'refund' ? '#dcfce7' : txn.type === 'purchase' ? '#dbeafe' : '#fee2e2',
                            color: txn.type === 'refund' ? '#166534' : txn.type === 'purchase' ? '#1e40af' : '#991b1b'
                          }}>
                            {txn.type}
                          </span>
                        </td>
                        <td style={{ padding: '12px', color: '#666' }}>
                          {txn.operation || txn.reason || txn.type}
                        </td>
                        <td style={{ 
                          padding: '12px', 
                          textAlign: 'right',
                          fontWeight: 'bold',
                          color: txn.amount > 0 ? '#16a34a' : '#dc2626'
                        }}>
                          {txn.amount > 0 ? '+' : ''}{txn.amount}
                        </td>
                        <td style={{ padding: '12px', textAlign: 'center' }}>
                          <span style={{
                            padding: '4px 8px',
                            borderRadius: '12px',
                            fontSize: '11px',
                            fontWeight: '500',
                            background: txn.status === 'completed' ? '#dcfce7' : txn.status === 'pending' ? '#fef3c7' : '#fee2e2',
                            color: txn.status === 'completed' ? '#166534' : txn.status === 'pending' ? '#92400e' : '#991b1b'
                          }}>
                            {txn.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Pricing Table Tab */}
        {activeTab === 'pricing' && pricing && (
          <div>
            <h2 style={{ marginBottom: '16px', fontSize: '24px', fontWeight: 'bold' }}>Dynamic Pricing Table</h2>
            <p style={{ marginBottom: '24px', color: '#666' }}>
              AutoWebIQ uses dynamic pricing based on agents used, models, and complexity. Multi-agent builds get 10% discount when using 4+ agents.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
              {/* Agent Costs */}
              <div style={{ background: 'white', borderRadius: '8px', padding: '20px', border: '1px solid #e5e7eb' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px', color: '#667eea' }}>
                  Per-Agent Costs
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {Object.entries(pricing.agent_costs).map(([agent, cost]) => (
                    <div key={agent} style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      padding: '8px',
                      background: '#f9fafb',
                      borderRadius: '4px'
                    }}>
                      <span style={{ textTransform: 'capitalize', fontWeight: '500' }}>{agent} Agent</span>
                      <span style={{ fontWeight: 'bold', color: '#667eea' }}>{cost} credits</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Model Costs */}
              <div style={{ background: 'white', borderRadius: '8px', padding: '20px', border: '1px solid #e5e7eb' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px', color: '#764ba2' }}>
                  Per-Model Costs
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {Object.entries(pricing.model_costs).map(([model, cost]) => (
                    <div key={model} style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      padding: '8px',
                      background: '#f9fafb',
                      borderRadius: '4px'
                    }}>
                      <span style={{ fontWeight: '500' }}>{model}</span>
                      <span style={{ fontWeight: 'bold', color: '#764ba2' }}>{cost} credits</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Example Builds */}
            <div style={{ marginTop: '24px', background: '#f0f9ff', borderRadius: '8px', padding: '20px', border: '1px solid #bae6fd' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>Example Build Costs</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
                <div>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>Simple Landing Page</div>
                  <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>Planner + Frontend + Testing</div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0284c7' }}>~17 credits</div>
                </div>
                <div>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>With Custom Images</div>
                  <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>+ Image Agent</div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0284c7' }}>~29 credits</div>
                </div>
                <div>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>Full-Stack App</div>
                  <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>All agents + 10% discount</div>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0284c7' }}>~32 credits</div>
                </div>
              </div>
            </div>

            <div style={{ marginTop: '16px', padding: '12px', background: '#fef3c7', borderRadius: '8px', fontSize: '14px', color: '#92400e' }}>
              <strong>Note:</strong> {pricing.note}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CreditsPage;
