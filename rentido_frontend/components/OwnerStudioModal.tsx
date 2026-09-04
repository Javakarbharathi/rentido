'use client';

import React, { useState, useEffect } from 'react';
import { 
  X, 
  PackagePlus, 
  Layers, 
  Wallet, 
  CheckCircle2, 
  AlertCircle, 
  Camera, 
  ShieldCheck, 
  Sparkles,
  ArrowRight,
  TrendingUp,
  CreditCard,
  Building,
  Tag
} from 'lucide-react';
import { createAsset, createListing, fetchOwnerListings, fetchOwnerEarnings, requestOwnerPayout, addRole } from '@/lib/api';
import { isOwnerUser } from '@/lib/auth';

interface OwnerStudioModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: any;
  token: string;
  onOpenAuth: () => void;
  onListingCreated: () => void;
  onUserUpdated?: (user: any) => void;
}

const CATEGORIES = [
  { id: 1, name: 'Cameras & Optics', slug: 'cameras-optics' },
  { id: 2, name: 'Drones & Aerial Cinematography', slug: 'drones-aerial' },
  { id: 3, name: 'Laptops & Workstations', slug: 'laptops-workstations' },
  { id: 4, name: 'Studio Audio & DJ Sound', slug: 'audio-studio' },
  { id: 5, name: 'Gaming & VR Consoles', slug: 'gaming-vr' },
  { id: 6, name: 'Electric Mobility & E-Bikes', slug: 'electric-mobility' },
  { id: 7, name: 'Power Tools & Industrial', slug: 'power-tools' },
  { id: 8, name: 'Camping & Outdoor Expeditions', slug: 'camping-outdoor' },
];

const CITIES = ['Bangalore', 'Mumbai', 'Delhi', 'Hyderabad', 'Chennai', 'Pune'];

export default function OwnerStudioModal({
  isOpen,
  onClose,
  user,
  token,
  onOpenAuth,
  onListingCreated,
  onUserUpdated,
}: OwnerStudioModalProps) {
  const [activeTab, setActiveTab] = useState<'create' | 'portfolio' | 'earnings'>('create');

  // Form State
  const [name, setName] = useState('');
  const [brand, setBrand] = useState('');
  const [modelName, setModelName] = useState('');
  const [serialNumber, setSerialNumber] = useState('');
  const [categoryId, setCategoryId] = useState(1);
  const [condition, setCondition] = useState('GOOD');
  const [replacementValue, setReplacementValue] = useState('250000');
  
  const [listingTitle, setListingTitle] = useState('');
  const [description, setDescription] = useState('');
  const [rentalPrice, setRentalPrice] = useState('2500');
  const [securityDeposit, setSecurityDeposit] = useState('12000');
  const [city, setCity] = useState('Bangalore');
  const [area, setArea] = useState('Indiranagar');
  const [pincode, setPincode] = useState('560038');
  const [isDelivery, setIsDelivery] = useState(true);
  const [isPickup, setIsPickup] = useState(true);

  // Status & Feedback
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Data states
  const [myListings, setMyListings] = useState<any[]>([]);
  const [earnings, setEarnings] = useState<any>(null);
  const [payoutMsg, setPayoutMsg] = useState<string | null>(null);
  const [requestingPayout, setRequestingPayout] = useState(false);

  useEffect(() => {
    if (isOpen && token) {
      loadOwnerData();
    }
  }, [isOpen, token]);

  const loadOwnerData = async () => {
    if (!token) return;
    try {
      const [listRes, earnRes] = await Promise.all([
        fetchOwnerListings(token),
        fetchOwnerEarnings(token),
      ]);
      setMyListings(listRes || []);
      setEarnings(earnRes);
    } catch (e) {
      console.warn('Failed to load owner data', e);
    }
  };

  const autofillPreset = () => {
    setName('RED Komodo 6K Cinema Camera Kit');
    setBrand('RED Digital Cinema');
    setModelName('Komodo 6K');
    setSerialNumber(`SN-RED-${Math.floor(1000 + Math.random() * 9000)}`);
    setCategoryId(1);
    setCondition('LIKE_NEW');
    setReplacementValue('450000');
    setListingTitle('RED Komodo 6K Global Shutter Cinema Camera Kit');
    setDescription('Includes Canon RF to EF focal reducer, Outrigger handle, 2x 512GB CFast 2.0 cards, BP-975 batteries, and heavy-duty Pelican hard case.');
    setRentalPrice('3500');
    setSecurityDeposit('20000');
    setCity('Bangalore');
    setArea('Koramangala');
    setPincode('560034');
    setIsDelivery(true);
    setIsPickup(true);
    setErrorMsg(null);
    setSuccessMsg(null);
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !token) {
      onOpenAuth();
      return;
    }

    setSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      // 1. Register physical asset
      const assetPayload = {
        category: categoryId,
        name,
        brand,
        model_name: modelName,
        serial_number: serialNumber,
        condition,
        replacement_value: replacementValue,
      };

      const assetRes = await createAsset(token, assetPayload);
      if (assetRes.id) {
        // 2. Publish commercial listing
        const listingPayload = {
          asset_id: assetRes.id,
          title: listingTitle || name,
          description,
          rental_price: rentalPrice,
          pricing_model: 'DAILY',
          security_deposit: securityDeposit,
          city,
          area,
          pincode,
          is_delivery_available: isDelivery,
          is_self_pickup_available: isPickup,
          status: 'PUBLISHED',
        };

        const listingRes = await createListing(token, listingPayload);
        if (listingRes.id) {
          setSuccessMsg(`"${listingRes.title}" successfully published to the live marketplace!`);
          onListingCreated();
          loadOwnerData();
        } else {
          const detail = listingRes.detail || JSON.stringify(listingRes);
          if (detail.toLowerCase().includes('token') && detail.toLowerCase().includes('not valid')) {
            setErrorMsg('Your session has expired. Please sign in again to publish.');
            onOpenAuth();
          } else {
            setErrorMsg(detail);
          }
        }
      } else {
        const detail = assetRes.detail || JSON.stringify(assetRes);
        if (detail.toLowerCase().includes('token') && detail.toLowerCase().includes('not valid')) {
          setErrorMsg('Your session has expired. Please sign in again to publish.');
          onOpenAuth();
        } else {
          setErrorMsg(detail);
        }
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Error publishing listing. Please check API server.');
    } finally {
      setSubmitting(false);
    }
  };

  const handlePayoutRequest = async () => {
    if (!token) {
      onOpenAuth();
      return;
    }
    setRequestingPayout(true);
    setPayoutMsg(null);
    try {
      const res = await requestOwnerPayout(token);
      if (res && res.reference_id) {
        setPayoutMsg(`Payout of ₹${res.disbursed_amount} disbursed! Ref: ${res.reference_id}`);
        await loadOwnerData();
      } else {
        setPayoutMsg(res?.detail || res?.message || 'No pending balance available for payout.');
      }
    } catch (e: any) {
      setPayoutMsg(e.message || 'Payout request failed.');
    } finally {
      setRequestingPayout(false);
    }
  };

  const isAuthorized = isOwnerUser(user);
  const [activatingRole, setActivatingRole] = useState(false);
  const [roleError, setRoleError] = useState<string | null>(null);

  const handleActivateOwner = async () => {
    if (!token) {
      onOpenAuth();
      return;
    }
    setActivatingRole(true);
    setRoleError(null);
    try {
      const res = await addRole(token, 'OWNER');
      if (res.user) {
        if (onUserUpdated) onUserUpdated(res.user);
      } else {
        setRoleError(res.detail || 'Could not activate Owner role.');
      }
    } catch (err: any) {
      setRoleError('Failed to contact server to activate role.');
    } finally {
      setActivatingRole(false);
    }
  };

  if (!isOpen) return null;

  if (!isAuthorized) {
    return (
      <div 
        onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm cursor-pointer"
      >
        <div className="relative w-full max-w-md bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden cursor-default p-8 text-center">
          <div className="w-16 h-16 rounded-2xl bg-amber-100 text-amber-600 flex items-center justify-center mx-auto mb-4">
            <PackagePlus className="w-8 h-8" />
          </div>
          <h3 className="text-xl font-black text-gray-950">Equipment Host Role Required</h3>
          <p className="text-xs text-gray-600 mt-2 leading-relaxed">
            You are currently signed in as <strong className="text-gray-900">{user?.email || 'Guest'}</strong> (Verified Renter).
            Publishing equipment listings and receiving double-entry escrow payouts requires an <strong>Owner Profile</strong>.
          </p>
          {roleError && (
            <div className="mt-3 p-3 bg-red-50 text-red-700 text-xs rounded-xl font-medium">
              {roleError}
            </div>
          )}
          <div className="mt-6 space-y-2">
            <button
              type="button"
              onClick={handleActivateOwner}
              disabled={activatingRole}
              className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-md cursor-pointer disabled:opacity-60 transition-colors"
            >
              {activatingRole ? 'Activating Owner Profile...' : '✨ Activate Equipment Owner Role Now'}
            </button>
            <button
              type="button"
              onClick={() => {
                onClose();
                onOpenAuth();
              }}
              className="w-full py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-bold rounded-xl cursor-pointer transition-colors"
            >
              Switch to Owner Account (rajesh.camera@rentido.com)
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm cursor-pointer"
    >
      <div className="relative w-full max-w-3xl bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden max-h-[90vh] flex flex-col cursor-default">
        
        {/* Header */}
        <div className="px-6 py-5 bg-gradient-to-r from-gray-900 via-indigo-950 to-gray-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-400">
              <PackagePlus className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                Owner Studio & Portfolio
                <span className="bg-indigo-500/30 text-indigo-300 text-[10px] font-bold px-2 py-0.5 rounded-full border border-indigo-400/30">
                  Apex Host
                </span>
              </h3>
              <p className="text-xs text-gray-400">
                Register high-value assets, set escrow terms, and manage rental payouts.
              </p>
            </div>
          </div>

          <button 
            type="button"
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white rounded-full hover:bg-white/10 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-gray-100 bg-gray-50/50 px-6 pt-2">
          <button
            onClick={() => setActiveTab('create')}
            className={`flex items-center gap-2 px-4 py-3 text-xs font-bold border-b-2 transition-all cursor-pointer ${
              activeTab === 'create'
                ? 'border-indigo-600 text-indigo-600 bg-white rounded-t-lg'
                : 'border-transparent text-gray-500 hover:text-gray-900'
            }`}
          >
            <PackagePlus className="w-4 h-4" />
            <span>Publish New Listing</span>
          </button>

          <button
            onClick={() => setActiveTab('portfolio')}
            className={`flex items-center gap-2 px-4 py-3 text-xs font-bold border-b-2 transition-all cursor-pointer ${
              activeTab === 'portfolio'
                ? 'border-indigo-600 text-indigo-600 bg-white rounded-t-lg'
                : 'border-transparent text-gray-500 hover:text-gray-900'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>My Equipment ({myListings.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('earnings')}
            className={`flex items-center gap-2 px-4 py-3 text-xs font-bold border-b-2 transition-all cursor-pointer ${
              activeTab === 'earnings'
                ? 'border-indigo-600 text-indigo-600 bg-white rounded-t-lg'
                : 'border-transparent text-gray-500 hover:text-gray-900'
            }`}
          >
            <Wallet className="w-4 h-4" />
            <span>Earnings & Payouts</span>
          </button>
        </div>

        {/* Tab Content */}
        <div className="p-6 overflow-y-auto flex-1 text-gray-800 text-xs">
          
          {/* TAB 1: CREATE LISTING */}
          {activeTab === 'create' && (
            <form onSubmit={handleCreateSubmit} className="space-y-6">
              
              {/* Autofill Demo Banner */}
              <div className="flex items-center justify-between p-3.5 bg-indigo-50/80 border border-indigo-100 rounded-2xl">
                <div className="flex items-center gap-2.5">
                  <Sparkles className="w-4 h-4 text-indigo-600" />
                  <span className="text-xs text-indigo-950 font-medium">
                    Want to test quickly? Auto-populate with commercial cinema gear demo:
                  </span>
                </div>
                <button
                  type="button"
                  onClick={autofillPreset}
                  className="px-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg transition-colors cursor-pointer text-[11px]"
                >
                  ⚡ Autofill Cinema Gear
                </button>
              </div>

              {/* Section 1: Physical Asset Spec */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3 flex items-center gap-1.5">
                  <Tag className="w-3.5 h-3.5 text-indigo-600" />
                  Step 1: Physical Asset Registration & Verification
                </h4>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-gray-700 font-semibold mb-1">Equipment Name *</label>
                    <input
                      type="text"
                      required
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="e.g. Sony FX3 Cinema Camera"
                      className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-700 font-semibold mb-1">Category *</label>
                    <select
                      value={categoryId}
                      onChange={(e) => setCategoryId(Number(e.target.value))}
                      className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none cursor-pointer"
                    >
                      {CATEGORIES.map((c) => (
                        <option key={c.id} value={c.id}>{c.name}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-gray-700 font-semibold mb-1">Brand *</label>
                    <input
                      type="text"
                      required
                      value={brand}
                      onChange={(e) => setBrand(e.target.value)}
                      placeholder="e.g. Sony, DJI, Apple, Canon"
                      className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-700 font-semibold mb-1">Model Name *</label>
                    <input
                      type="text"
                      required
                      value={modelName}
                      onChange={(e) => setModelName(e.target.value)}
                      placeholder="e.g. ILME-FX3"
                      className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-700 font-semibold mb-1">Unique Serial Number *</label>
                    <input
                      type="text"
                      required
                      value={serialNumber}
                      onChange={(e) => setSerialNumber(e.target.value)}
                      placeholder="e.g. SN-SONY-998877"
                      className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none font-mono"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-700 font-semibold mb-1">Replacement Value (₹) *</label>
                    <input
                      type="number"
                      required
                      value={replacementValue}
                      onChange={(e) => setReplacementValue(e.target.value)}
                      placeholder="320000"
                      className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Section 2: Marketplace Terms */}
              <div className="pt-2 border-t border-gray-100">
                <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3 flex items-center gap-1.5">
                  <CreditCard className="w-3.5 h-3.5 text-indigo-600" />
                  Step 2: Rental Pricing, Escrow Deposit & Location
                </h4>

                <div className="space-y-3">
                  <div>
                    <label className="block text-gray-700 font-semibold mb-1">Commercial Listing Title *</label>
                    <input
                      type="text"
                      required
                      value={listingTitle}
                      onChange={(e) => setListingTitle(e.target.value)}
                      placeholder="e.g. Sony FX3 4K 120p Cinema Camera Kit"
                      className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none font-semibold text-gray-900"
                    />
                  </div>

                  <div>
                    <label className="block text-gray-700 font-semibold mb-1">Kit Details & Included Accessories *</label>
                    <textarea
                      required
                      rows={2}
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="Describe everything included: lenses, memory cards, chargers, top handle, cage..."
                      className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    <div>
                      <label className="block text-gray-700 font-semibold mb-1">Daily Rent (₹) *</label>
                      <input
                        type="number"
                        required
                        value={rentalPrice}
                        onChange={(e) => setRentalPrice(e.target.value)}
                        placeholder="2800"
                        className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold text-indigo-700"
                      />
                    </div>

                    <div>
                      <label className="block text-gray-700 font-semibold mb-1">Refundable Escrow Deposit (₹) *</label>
                      <input
                        type="number"
                        required
                        value={securityDeposit}
                        onChange={(e) => setSecurityDeposit(e.target.value)}
                        placeholder="15000"
                        className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none font-bold text-amber-800"
                      />
                    </div>

                    <div>
                      <label className="block text-gray-700 font-semibold mb-1">City *</label>
                      <select
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none cursor-pointer"
                      >
                        {CITIES.map((c) => (
                          <option key={c} value={c}>{c}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-gray-700 font-semibold mb-1">Neighborhood / Area *</label>
                      <input
                        type="text"
                        required
                        value={area}
                        onChange={(e) => setArea(e.target.value)}
                        placeholder="e.g. Indiranagar"
                        className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-gray-700 font-semibold mb-1">Pincode *</label>
                      <input
                        type="text"
                        required
                        value={pincode}
                        onChange={(e) => setPincode(e.target.value)}
                        placeholder="560038"
                        className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none font-mono"
                      />
                    </div>

                    <div className="flex items-center gap-4 pt-5">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={isDelivery}
                          onChange={(e) => setIsDelivery(e.target.checked)}
                          className="rounded text-indigo-600 focus:ring-indigo-500"
                        />
                        <span className="text-gray-700 font-medium">Logistics Delivery</span>
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={isPickup}
                          onChange={(e) => setIsPickup(e.target.checked)}
                          className="rounded text-indigo-600 focus:ring-indigo-500"
                        />
                        <span className="text-gray-700 font-medium">Self Pickup</span>
                      </label>
                    </div>
                  </div>
                </div>
              </div>

              {/* Feedback messages */}
              {successMsg && (
                <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>{successMsg}</span>
                </div>
              )}

              {errorMsg && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-red-800 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
                  <span>{errorMsg}</span>
                </div>
              )}

              {/* Submit Button */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-bold rounded-2xl shadow-lg shadow-indigo-200 flex items-center justify-center gap-2 transition-all cursor-pointer text-sm"
                >
                  {submitting ? 'Registering & Publishing...' : 'Publish Equipment to Live Marketplace'}
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>

            </form>
          )}

          {/* TAB 2: PORTFOLIO */}
          {activeTab === 'portfolio' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-gray-100">
                <h4 className="font-bold text-gray-900 text-sm">Your Active Rental Listings ({myListings.length})</h4>
                <button
                  onClick={() => setActiveTab('create')}
                  className="px-3 py-1.5 bg-indigo-50 text-indigo-700 font-bold rounded-xl hover:bg-indigo-100 transition-colors text-xs"
                >
                  + Add Another Item
                </button>
              </div>

              {myListings.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Layers className="w-8 h-8 mx-auto text-gray-300 mb-2" />
                  <p>You haven't listed any equipment yet.</p>
                  <button
                    onClick={() => setActiveTab('create')}
                    className="mt-3 px-4 py-2 bg-indigo-600 text-white font-bold rounded-xl text-xs"
                  >
                    Create Your First Listing
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {myListings.map((item) => (
                    <div key={item.id} className="p-4 bg-gray-50 border border-gray-200 rounded-2xl flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between gap-2 mb-1.5">
                          <span className="font-bold text-gray-900 text-sm">{item.title}</span>
                          <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                            {item.status}
                          </span>
                        </div>
                        <p className="text-gray-500 text-[11px] line-clamp-2 mb-3">{item.description}</p>
                      </div>

                      <div className="pt-2 border-t border-gray-200 flex items-center justify-between">
                        <div>
                          <span className="text-[10px] text-gray-700 block">Daily Rate</span>
                          <span className="font-bold text-indigo-700 text-sm">₹{item.rental_price}</span>
                        </div>
                        <div className="text-right">
                          <span className="text-[10px] text-gray-700 block">Escrow Deposit</span>
                          <span className="font-semibold text-gray-700">₹{item.security_deposit}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: EARNINGS & ESCROW PAYOUTS */}
          {activeTab === 'earnings' && (
            <div className="space-y-6">
              
              {/* Financial KPI Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-4 bg-indigo-50 border border-indigo-100 rounded-2xl">
                  <span className="text-[10px] uppercase font-bold text-indigo-700 block">Total Credited</span>
                  <span className="text-lg font-black text-indigo-950">
                    ₹{earnings ? earnings.total_earnings_credited : '0.00'}
                  </span>
                </div>

                <div className="p-4 bg-emerald-50 border border-emerald-100 rounded-2xl">
                  <span className="text-[10px] uppercase font-bold text-emerald-700 block">Disbursed</span>
                  <span className="text-lg font-black text-emerald-950">
                    ₹{earnings ? earnings.total_payout_settled : '0.00'}
                  </span>
                </div>

                <div className="p-4 bg-amber-50 border border-amber-100 rounded-2xl">
                  <span className="text-[10px] uppercase font-bold text-amber-700 block">Available Balance</span>
                  <span className="text-lg font-black text-amber-950">
                    ₹{earnings ? earnings.pending_payout_balance : '0.00'}
                  </span>
                </div>

                <div className="p-4 bg-purple-50 border border-purple-100 rounded-2xl">
                  <span className="text-[10px] uppercase font-bold text-purple-700 block">Escrow Deposits Held</span>
                  <span className="text-lg font-black text-purple-950">
                    ₹{earnings ? earnings.active_escrow_deposits : '0.00'}
                  </span>
                </div>
              </div>

              {/* Payout Action */}
              <div className="p-5 bg-gradient-to-r from-gray-900 to-indigo-950 text-white rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-4">
                <div>
                  <h5 className="font-bold text-white text-sm">Disburse Available Balance to Bank / UPI</h5>
                  <p className="text-xs text-gray-400 mt-0.5">
                    Settlements are recorded instantly into the double-entry accounting ledger.
                  </p>
                </div>

                <button
                  onClick={handlePayoutRequest}
                  disabled={requestingPayout}
                  className={`px-5 py-2.5 font-bold rounded-xl transition-all cursor-pointer shrink-0 text-xs shadow-md ${
                    requestingPayout
                      ? 'bg-emerald-700 text-emerald-200 cursor-not-allowed'
                      : 'bg-emerald-500 hover:bg-emerald-600 text-white shadow-emerald-900/50'
                  }`}
                >
                  {requestingPayout ? (
                    <span className="flex items-center gap-1.5">
                      <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin inline-block" />
                      Processing Payout...
                    </span>
                  ) : (
                    '⚡ Request Instant Payout'
                  )}
                </button>
              </div>

              {payoutMsg && (
                <div
                  className={`p-3.5 rounded-xl text-xs font-semibold flex items-center gap-2 ${
                    payoutMsg.includes('disbursed') || payoutMsg.includes('Successfully')
                      ? 'bg-emerald-50 border border-emerald-200 text-emerald-900'
                      : payoutMsg.includes('No pending')
                      ? 'bg-amber-50 border border-amber-200 text-amber-900'
                      : 'bg-rose-50 border border-rose-200 text-rose-900'
                  }`}
                >
                  <span>
                    {payoutMsg.includes('disbursed') || payoutMsg.includes('Successfully')
                      ? '✅'
                      : payoutMsg.includes('No pending')
                      ? 'ℹ️'
                      : '⚠️'}
                  </span>
                  <span>{payoutMsg}</span>
                </div>
              )}

              {/* Ledger Statement */}
              <div>
                <h5 className="font-bold text-gray-900 text-xs uppercase tracking-wider mb-2">
                  Recent Double-Entry Financial Ledger Records
                </h5>

                {earnings && earnings.recent_entries && earnings.recent_entries.length > 0 ? (
                  <div className="border border-gray-200 rounded-2xl overflow-hidden divide-y divide-gray-100">
                    {earnings.recent_entries.map((entry: any) => (
                      <div key={entry.id} className="p-3 flex items-center justify-between hover:bg-gray-50">
                        <div>
                          <span className="font-semibold text-gray-900 block">{entry.description}</span>
                          <span className="text-[10px] text-gray-700">{entry.timestamp.split('T')[0]} · Ref: {entry.reference_id}</span>
                        </div>
                        <span className="font-bold text-emerald-700 text-sm">
                          ₹{entry.amount}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-700 py-4 text-center">No ledger entries recorded yet.</p>
                )}
              </div>

            </div>
          )}

        </div>

      </div>
    </div>
  );
}
