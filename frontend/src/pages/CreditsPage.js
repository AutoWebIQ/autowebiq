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

  const axiosConfig = {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [packagesRes, userRes] = await Promise.all([
        axios.get(`${API}/credits/packages`),
        axios.get(`${API}/auth/me`, axiosConfig)
      ]);
      setPackages(packagesRes.data);
      setUser(userRes.data);
    } catch (error) {
      toast.error('Failed to load packages');
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (packageData) => {
    try {
      const orderRes = await axios.post(`${API}/credits/create-order`, {
        package_id: packageData.id
      }, axiosConfig);

      const options = {
        key: orderRes.data.key_id,
        amount: orderRes.data.amount,
        currency: orderRes.data.currency,
        order_id: orderRes.data.order_id,
        name: 'Optra AI',
        description: packageData.name,
        handler: async function (response) {
          try {
            await axios.post(`${API}/credits/verify-payment`, {
              order_id: response.razorpay_order_id,
              payment_id: response.razorpay_payment_id,
              signature: response.razorpay_signature
            }, axiosConfig);
            
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
            <span>Optra AI</span>
          </div>
          <div className="credits-badge" data-testid="current-credits">
            <CreditCard size={16} />
            <span>{user.credits} Credits</span>
          </div>
        </div>
      </nav>

      <div className="credits-content">
        <div className="credits-header">
          <h1 data-testid="credits-title">Buy Credits</h1>
          <p data-testid="credits-subtitle">Use credits for AI messages. Different models cost different credits per message.</p>
          <div className="model-costs-info">
            <p><strong>Credit Costs:</strong></p>
            <ul>
              <li>Claude 4.5 Sonnet (200k): 5 credits/message</li>
              <li>Claude 4.5 Sonnet - 1M (PRO): 10 credits/message</li>
              <li>GPT-5 (Beta): 8 credits/message</li>
              <li>Claude 4.0 Sonnet: 4 credits/message</li>
            </ul>
          </div>
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
                <li><CheckCircle size={16} /> ~{Math.floor(pkg.credits / 5)} websites (avg)</li>
                <li><CheckCircle size={16} /> All AI models supported</li>
                <li><CheckCircle size={16} /> Download & preview</li>
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
      </div>
    </div>
  );
};

export default CreditsPage;
