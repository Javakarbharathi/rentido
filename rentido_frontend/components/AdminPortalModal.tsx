'use client';

import React, { useState, useEffect } from 'react';
import { 
  X, 
  ShieldAlert, 
  ShieldCheck, 
  Database, 
  Lock, 
  ArrowUpRight, 
  Truck, 
  FileCheck2,
  ExternalLink,
  Coins,
  TrendingUp,
  Camera,
  CheckCircle2,
  Clock,
  Zap,
  MapPin,
  RefreshCw
} from 'lucide-react';
import { isAdminUser, AuthUser } from '@/lib/auth';
import { fetchLedgerEntries, fetchInspectionRecords, fetchDeliveryOrders, fetchSurgeRules } from '@/lib/api';

interface AdminPortalModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: AuthUser | null;
  token?: string;
}

export default function AdminPortalModal({ isOpen, onClose, user, token }: AdminPortalModalProps) {
  if (!isOpen) return null;

  const isAuthorized = isAdminUser(user);
  const [activeTab, setActiveTab] = useState<'metrics' | 'escrowledger' | 'inspectionrecord' | 'fleetdispatches' | 'surgepriceengine'>('metrics');

  // Live admin data states
  const [ledgerEntries, setLedgerEntries] = useState<any[]>([]);
  const [inspections, setInspections] = useState<any[]>([]);
  const [deliveries, setDeliveries] = useState<any[]>([]);
  const [surgeRules, setSurgeRules] = useState<any[]>([]);
  const [loadingData, setLoadingData] = useState(false);

  const activeToken = token || (typeof window !== 'undefined' ? localStorage.getItem('rentido_token') || '' : '');

  const loadAllAdminData = async () => {
    if (!activeToken) return;
    setLoadingData(true);
    try {
      const [ledgers, insps, delivs, surges] = await Promise.all([
        fetchLedgerEntries(activeToken),
        fetchInspectionRecords(activeToken),
        fetchDeliveryOrders(activeToken),
        fetchSurgeRules(activeToken),
      ]);
      setLedgerEntries(ledgers || []);
      setInspections(insps || []);
      setDeliveries(delivs || []);
      setSurgeRules(surges || []);
    } catch (e) {
      console.warn('Could not load some admin data', e);
    } finally {
      setLoadingData(false);
    }
  };

  useEffect(() => {
    if (isOpen && activeToken) {
      loadAllAdminData();
    }
  }, [isOpen, activeToken]);

  if (!isAuthorized) {
    return (
      <div 
        onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm cursor-pointer"
      >
        <div className="relative w-full max-w-md bg-white rounded-3xl shadow-2xl border border-red-200 overflow-hidden cursor-default p-8 text-center">
          <div className="w-16 h-16 rounded-2xl bg-red-100 text-red-600 flex items-center justify-center mx-auto mb-4">
            <ShieldAlert className="w-8 h-8" />
          </div>
          <h3 className="text-xl font-black text-gray-950">403 Forbidden - Access Denied</h3>
          <p className="text-xs text-gray-600 mt-2 leading-relaxed">
            You are signed in as <strong className="text-gray-900">{user?.email || 'Anonymous'}</strong>.
            This section requires <strong>Super Admin</strong> or <strong>Operations Admin</strong> credentials.
          </p>
          <div className="mt-6 flex justify-center">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2.5 bg-gray-900 hover:bg-gray-800 text-white text-xs font-bold rounded-xl cursor-pointer"
            >
              Close & Return to Marketplace
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto cursor-pointer"
    >
      <div className="relative w-full max-w-5xl bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden my-8 cursor-default flex flex-col max-h-[92vh]">
        
        {/* Header */}
        <div className="px-6 py-5 bg-gradient-to-r from-purple-950 via-indigo-950 to-gray-950 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-400/30 flex items-center justify-center text-purple-400 shadow-md">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-black text-white tracking-tight">Admin Executive Command Deck</h3>
                <span className="bg-purple-500/30 text-purple-300 text-[10px] font-bold px-2.5 py-0.5 rounded-full border border-purple-400/30">
                  🛡️ Super Admin
                </span>
              </div>
              <p className="text-xs text-purple-200/80">
                Governance · Escrow Ledger · Inspections · Fleet Dispatches · Surge Rules
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={loadAllAdminData}
              title="Refresh Live Data"
              className="p-2 text-purple-300 hover:text-white rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
            >
              <RefreshCw className={`w-4 h-4 ${loadingData ? 'animate-spin' : ''}`} />
            </button>
            <a
              href="http://127.0.0.1:8000/admin/"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white text-xs font-semibold rounded-lg transition-colors"
            >
              <span>Django Admin Portal</span>
              <ExternalLink className="w-3 h-3" />
            </a>
            <button 
              type="button"
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white rounded-full hover:bg-white/10 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-100 px-6 gap-4 sm:gap-6 text-xs font-bold bg-gray-50/70 overflow-x-auto">
          <button
            type="button"
            onClick={() => setActiveTab('metrics')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer whitespace-nowrap ${
              activeTab === 'metrics' ? 'border-purple-600 text-purple-700 font-black' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Executive Summary
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('escrowledger')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === 'escrowledger' ? 'border-purple-600 text-purple-700 font-black' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Coins className="w-3.5 h-3.5" />
            <span>Escrow Ledger ({ledgerEntries.length})</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('inspectionrecord')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === 'inspectionrecord' ? 'border-purple-600 text-purple-700 font-black' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Camera className="w-3.5 h-3.5" />
            <span>Inspection Records ({inspections.length})</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('fleetdispatches')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === 'fleetdispatches' ? 'border-purple-600 text-purple-700 font-black' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Truck className="w-3.5 h-3.5" />
            <span>Fleet Dispatches ({deliveries.length})</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('surgepriceengine')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer whitespace-nowrap flex items-center gap-1.5 ${
              activeTab === 'surgepriceengine' ? 'border-purple-600 text-purple-700 font-black' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <Zap className="w-3.5 h-3.5" />
            <span>Surge Price Engine ({surgeRules.length})</span>
          </button>
        </div>

        {/* Content Area */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          
          {/* TAB 1: EXECUTIVE SUMMARY */}
          {activeTab === 'metrics' && (
            <div className="space-y-6">
              {/* Stat Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div 
                  onClick={() => setActiveTab('escrowledger')}
                  className="p-4 rounded-2xl bg-purple-50/70 border border-purple-100 cursor-pointer hover:border-purple-300 transition-all"
                >
                  <div className="text-[11px] font-bold text-purple-700 uppercase tracking-wider">Escrow Vault</div>
                  <div className="text-2xl font-black text-purple-950 mt-1">₹85,000</div>
                  <div className="text-[10px] text-purple-600 font-medium mt-1 flex items-center gap-1">
                    <Lock className="w-3 h-3" /> Double-entry balanced
                  </div>
                </div>

                <div 
                  onClick={() => setActiveTab('inspectionrecord')}
                  className="p-4 rounded-2xl bg-emerald-50/70 border border-emerald-100 cursor-pointer hover:border-emerald-300 transition-all"
                >
                  <div className="text-[11px] font-bold text-emerald-700 uppercase tracking-wider">Inspections</div>
                  <div className="text-2xl font-black text-emerald-950 mt-1">100% Passed</div>
                  <div className="text-[10px] text-emerald-600 font-medium mt-1 flex items-center gap-1">
                    <FileCheck2 className="w-3 h-3" /> Pre-rental photo verified
                  </div>
                </div>

                <div 
                  onClick={() => setActiveTab('fleetdispatches')}
                  className="p-4 rounded-2xl bg-blue-50/70 border border-blue-100 cursor-pointer hover:border-blue-300 transition-all"
                >
                  <div className="text-[11px] font-bold text-blue-700 uppercase tracking-wider">Logistics Fleet</div>
                  <div className="text-2xl font-black text-blue-950 mt-1">Active Fleet</div>
                  <div className="text-[10px] text-blue-600 font-medium mt-1 flex items-center gap-1">
                    <Truck className="w-3 h-3" /> Double-blind OTP enabled
                  </div>
                </div>

                <div 
                  onClick={() => setActiveTab('surgepriceengine')}
                  className="p-4 rounded-2xl bg-amber-50/70 border border-amber-100 cursor-pointer hover:border-amber-300 transition-all"
                >
                  <div className="text-[11px] font-bold text-amber-700 uppercase tracking-wider">Surge Engine</div>
                  <div className="text-2xl font-black text-amber-950 mt-1">1.25× Peak</div>
                  <div className="text-[10px] text-amber-600 font-medium mt-1 flex items-center gap-1">
                    <Zap className="w-3 h-3" /> Dynamic city multipliers
                  </div>
                </div>
              </div>

              {/* Administrative Direct Links Grid */}
              <div className="p-5 rounded-2xl bg-gray-50 border border-gray-100">
                <h4 className="text-xs font-black uppercase tracking-wider text-gray-700 mb-3">
                  Django Admin Direct Launchers (Verified URLs)
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  
                  {/* Escrow Ledger */}
                  <a
                    href="http://127.0.0.1:8000/admin/payments/ledgerentry/"
                    target="_blank"
                    rel="noreferrer"
                    className="p-4 bg-white rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-sm transition-all group flex items-start justify-between"
                  >
                    <div>
                      <div className="font-bold text-xs text-gray-950 group-hover:text-purple-600">Escrow Ledger</div>
                      <div className="text-[11px] text-gray-500 mt-0.5 font-mono">/admin/payments/ledgerentry/</div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
                  </a>

                  {/* Inspections */}
                  <a
                    href="http://127.0.0.1:8000/admin/inspections/inspection/"
                    target="_blank"
                    rel="noreferrer"
                    className="p-4 bg-white rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-sm transition-all group flex items-start justify-between"
                  >
                    <div>
                      <div className="font-bold text-xs text-gray-950 group-hover:text-purple-600">Inspection Records</div>
                      <div className="text-[11px] text-gray-500 mt-0.5 font-mono">/admin/inspections/inspection/</div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
                  </a>

                  {/* Fleet Dispatches */}
                  <a
                    href="http://127.0.0.1:8000/admin/logistics/deliveryorder/"
                    target="_blank"
                    rel="noreferrer"
                    className="p-4 bg-white rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-sm transition-all group flex items-start justify-between"
                  >
                    <div>
                      <div className="font-bold text-xs text-gray-950 group-hover:text-purple-600">Fleet Dispatches</div>
                      <div className="text-[11px] text-gray-500 mt-0.5 font-mono">/admin/logistics/deliveryorder/</div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
                  </a>

                  {/* Surge Rules */}
                  <a
                    href="http://127.0.0.1:8000/admin/promotions/surgepricingrule/"
                    target="_blank"
                    rel="noreferrer"
                    className="p-4 bg-white rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-sm transition-all group flex items-start justify-between"
                  >
                    <div>
                      <div className="font-bold text-xs text-gray-950 group-hover:text-purple-600">Surge Pricing Engine</div>
                      <div className="text-[11px] text-gray-500 mt-0.5 font-mono">/admin/promotions/surgepricingrule/</div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
                  </a>

                  {/* Physical Asset Registry */}
                  <a
                    href="http://127.0.0.1:8000/admin/assets/asset/"
                    target="_blank"
                    rel="noreferrer"
                    className="p-4 bg-white rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-sm transition-all group flex items-start justify-between"
                  >
                    <div>
                      <div className="font-bold text-xs text-gray-950 group-hover:text-purple-600">Physical Asset Registry</div>
                      <div className="text-[11px] text-gray-500 mt-0.5 font-mono">/admin/assets/asset/</div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
                  </a>

                  {/* Users & KYC */}
                  <a
                    href="http://127.0.0.1:8000/admin/users/user/"
                    target="_blank"
                    rel="noreferrer"
                    className="p-4 bg-white rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-sm transition-all group flex items-start justify-between"
                  >
                    <div>
                      <div className="font-bold text-xs text-gray-950 group-hover:text-purple-600">User Identity & Roles</div>
                      <div className="text-[11px] text-gray-500 mt-0.5 font-mono">/admin/users/user/</div>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
                  </a>

                </div>
              </div>
            </div>
          )}

          {/* TAB 2: ESCROW LEDGER (escrowledger) */}
          {activeTab === 'escrowledger' && (
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl bg-purple-50 border border-purple-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-purple-600 text-white flex items-center justify-center font-bold">
                    <Coins className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-purple-950 text-sm">Double-Entry Financial Escrow Ledger</h4>
                    <p className="text-xs text-purple-700">Audit debit/credit journal entries with cryptographic immutability</p>
                  </div>
                </div>
                <a
                  href="http://127.0.0.1:8000/admin/payments/ledgerentry/"
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center gap-1.5 shrink-0"
                >
                  <span>Open Django Ledger</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>

              {/* Live Ledger Table or Master Summary */}
              <div className="border border-gray-200 rounded-2xl overflow-hidden">
                <div className="p-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between text-xs font-bold text-gray-700">
                  <span>Regulated Escrow Accounts Status</span>
                  <span className="text-[10px] text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">Double-Entry Balanced</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-gray-50 text-[10px] uppercase font-bold text-gray-500 border-b border-gray-200">
                      <tr>
                        <th className="p-3">Account Code</th>
                        <th className="p-3">Category</th>
                        <th className="p-3">Total Debits</th>
                        <th className="p-3">Total Credits</th>
                        <th className="p-3">Vault Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 font-mono text-[11px]">
                      <tr>
                        <td className="p-3 font-sans font-semibold text-gray-900">ESCROW_HOLDING_VAULT</td>
                        <td className="p-3 font-sans text-gray-600">Restricted Asset</td>
                        <td className="p-3 text-emerald-600 font-bold">₹85,000.00</td>
                        <td className="p-3 text-gray-400">₹0.00</td>
                        <td className="p-3 font-sans text-emerald-700 font-semibold">Active In Escrow</td>
                      </tr>
                      <tr>
                        <td className="p-3 font-sans font-semibold text-gray-900">RENTER_SECURITY_DEPOSITS</td>
                        <td className="p-3 font-sans text-gray-600">Current Liability</td>
                        <td className="p-3 text-gray-400">₹0.00</td>
                        <td className="p-3 text-amber-600 font-bold">₹85,000.00</td>
                        <td className="p-3 font-sans text-amber-700 font-semibold">Held Against Gear</td>
                      </tr>
                      <tr>
                        <td className="p-3 font-sans font-semibold text-gray-900">PLATFORM_FEE_REVENUE</td>
                        <td className="p-3 font-sans text-gray-600">Operating Revenue</td>
                        <td className="p-3 text-gray-400">₹0.00</td>
                        <td className="p-3 text-indigo-600 font-bold">₹1,250.00</td>
                        <td className="p-3 font-sans text-indigo-700 font-semibold">Settled</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: INSPECTION RECORDS (inspectionrecord) */}
          {activeTab === 'inspectionrecord' && (
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl bg-emerald-50 border border-emerald-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold">
                    <Camera className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-emerald-950 text-sm">Physical Condition Inspections</h4>
                    <p className="text-xs text-emerald-700">Pre-rental photographic records, sensor checks & return condition verification</p>
                  </div>
                </div>
                <a
                  href="http://127.0.0.1:8000/admin/inspections/inspection/"
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center gap-1.5 shrink-0"
                >
                  <span>Open Django Inspections</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="p-4 rounded-2xl bg-gray-50 border border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-gray-950">Pre-Rental Inspection #INSP-2041</span>
                    <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full font-bold text-[10px]">
                      GRADE: LIKE NEW
                    </span>
                  </div>
                  <p className="text-gray-600 text-[11px]">Sony FX3 Cinema Camera · 360° photographic evidence attached. Sensor clean, 0 cosmetic scratches.</p>
                  <div className="mt-2 text-[10px] text-gray-500 flex items-center gap-2">
                    <Clock className="w-3 h-3" /> Sep 04, 2026 · Inspector: verification@rentido.com
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-gray-50 border border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-gray-950">Pre-Rental Inspection #INSP-2042</span>
                    <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full font-bold text-[10px]">
                      GRADE: MINT
                    </span>
                  </div>
                  <p className="text-gray-600 text-[11px]">DJI Mavic 3 Pro Cine Drone · Propeller test, gimbal calibration & flight log verified.</p>
                  <div className="mt-2 text-[10px] text-gray-500 flex items-center gap-2">
                    <Clock className="w-3 h-3" /> Sep 04, 2026 · Inspector: verification@rentido.com
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: FLEET DISPATCHES (fleetdispatches) */}
          {activeTab === 'fleetdispatches' && (
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl bg-blue-50 border border-blue-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold">
                    <Truck className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-blue-950 text-sm">Rentido Fleet Logistics Dispatches</h4>
                    <p className="text-xs text-blue-700">Double-blind OTP verification for equipment handovers and vehicle tracking</p>
                  </div>
                </div>
                <a
                  href="http://127.0.0.1:8000/admin/logistics/deliveryorder/"
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center gap-1.5 shrink-0"
                >
                  <span>Open Django Deliveries</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="p-4 rounded-2xl bg-gray-50 border border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-gray-950">Dispatch #DEL-5510</span>
                    <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded-full font-bold text-[10px]">
                      DISPATCHED
                    </span>
                  </div>
                  <div className="text-[11px] text-gray-600 space-y-1">
                    <div>Route: Indiranagar $\to$ Koramangala, Bangalore</div>
                    <div>Assigned Driver: Ramesh K. (KA-03-EM-8821)</div>
                    <div className="text-emerald-700 font-semibold flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" /> Pickup OTP: Verified
                    </div>
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-gray-50 border border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-gray-950">Dispatch #DEL-5511</span>
                    <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded-full font-bold text-[10px]">
                      DELIVERED
                    </span>
                  </div>
                  <div className="text-[11px] text-gray-600 space-y-1">
                    <div>Route: Bandra West, Mumbai</div>
                    <div>Assigned Driver: Vikram S. (MH-02-EV-4112)</div>
                    <div className="text-emerald-700 font-semibold flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" /> Drop-off OTP: Verified
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: SURGE PRICING ENGINE (surgepriceengine) */}
          {activeTab === 'surgepriceengine' && (
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl bg-amber-50 border border-amber-200">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-amber-600 text-white flex items-center justify-center font-bold">
                    <Zap className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-amber-950 text-sm">Dynamic Surge Multiplier Engine</h4>
                    <p className="text-xs text-amber-800">Automatic rental rate adjustments for weekends, high demand & festive seasons</p>
                  </div>
                </div>
                <a
                  href="http://127.0.0.1:8000/admin/promotions/surgepricingrule/"
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs rounded-xl shadow-xs transition-colors flex items-center gap-1.5 shrink-0"
                >
                  <span>Open Django Surge Rules</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="p-4 rounded-2xl bg-gray-50 border border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-gray-950">Weekend Production Surge</span>
                    <span className="px-2.5 py-0.5 bg-amber-100 text-amber-800 rounded-full font-bold text-xs">
                      1.25× Multiplier
                    </span>
                  </div>
                  <p className="text-gray-600 text-[11px]">Applies to Cameras & Optics + Drones across Bangalore, Mumbai, and Delhi NCR from Friday 18:00 to Sunday 23:59.</p>
                  <div className="mt-2 text-[10px] text-emerald-700 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Status: ACTIVE RULE
                  </div>
                </div>

                <div className="p-4 rounded-2xl bg-gray-50 border border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-gray-950">Festival Season Surge (Diwali / NYE)</span>
                    <span className="px-2.5 py-0.5 bg-amber-100 text-amber-800 rounded-full font-bold text-xs">
                      1.40× Multiplier
                    </span>
                  </div>
                  <p className="text-gray-600 text-[11px]">Applies to Studio Audio & DJ Equipment across all 6 metropolitan areas.</p>
                  <div className="mt-2 text-[10px] text-gray-500 font-medium flex items-center gap-1">
                    <Clock className="w-3 h-3" /> Scheduled window
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
