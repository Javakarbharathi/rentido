'use client';

import React, { useState, useEffect } from 'react';
import { 
  X, 
  KeyRound, 
  Clock, 
  ShieldCheck, 
  Truck, 
  CheckCircle2, 
  Lock, 
  Sparkles, 
  Share2, 
  ArrowRight,
  AlertCircle
} from 'lucide-react';
import { AuthUser, isRenterUser } from '@/lib/auth';
import { fetchUserRentals, verifyHandoverOTP, verifyReturnOTP } from '@/lib/api';

interface RenterDashboardModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: AuthUser | null;
  onBrowseGear?: () => void;
}

export default function RenterDashboardModal({
  isOpen,
  onClose,
  user,
  onBrowseGear,
}: RenterDashboardModalProps) {
  if (!isOpen) return null;

  const [activeTab, setActiveTab] = useState<'rentals' | 'escrow' | 'trust' | 'referrals'>('rentals');
  const [rentals, setRentals] = useState<any[]>([]);
  const [loadingRentals, setLoadingRentals] = useState(false);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [actionMsg, setActionMsg] = useState<{ id: number; text: string; type: 'success' | 'error' } | null>(null);

  const loadRentals = async () => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('rentido_token') : null;
    if (token) {
      setLoadingRentals(true);
      try {
        const res = await fetchUserRentals(token);
        setRentals(res || []);
      } catch (e) {
        console.warn('Could not load user rentals', e);
      } finally {
        setLoadingRentals(false);
      }
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadRentals();
    }
  }, [isOpen]);

  const handleVerifyHandover = async (rentalId: number, otp: string) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('rentido_token') : null;
    if (!token) return;
    setActionLoading(rentalId);
    setActionMsg(null);
    try {
      const res = await verifyHandoverOTP(token, rentalId, otp);
      if (res.ok) {
        setActionMsg({ id: rentalId, text: 'Handover verified! Rental is now ACTIVE.', type: 'success' });
        await loadRentals();
      } else {
        setActionMsg({ id: rentalId, text: res.detail || 'Handover verification failed.', type: 'error' });
      }
    } catch (err: any) {
      setActionMsg({ id: rentalId, text: 'Failed to verify handover OTP.', type: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  const handleVerifyReturn = async (rentalId: number, otp: string) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('rentido_token') : null;
    if (!token) return;
    setActionLoading(rentalId);
    setActionMsg(null);
    try {
      const res = await verifyReturnOTP(token, rentalId, otp);
      if (res.ok) {
        setActionMsg({ id: rentalId, text: 'Return verified! Rental COMPLETED & Escrow settlement triggered.', type: 'success' });
        await loadRentals();
      } else {
        setActionMsg({ id: rentalId, text: res.detail || 'Return verification failed.', type: 'error' });
      }
    } catch (err: any) {
      setActionMsg({ id: rentalId, text: 'Failed to verify return OTP.', type: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div 
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto cursor-pointer"
    >
      <div className="relative w-full max-w-2xl bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden my-8 cursor-default flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="px-6 py-5 bg-gradient-to-r from-blue-950 via-indigo-950 to-gray-950 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-300 shadow-md">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-black text-white tracking-tight">Renter Command Center</h3>
                <span className="bg-indigo-500/30 text-indigo-300 text-[10px] font-bold px-2 py-0.5 rounded-full border border-indigo-400/30">
                  Verified Renter
                </span>
              </div>
              <p className="text-xs text-indigo-200/80">
                Welcome, {user?.first_name || user?.email?.split('@')[0] || 'Renter'} · Protected by Double-Entry Escrow
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

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-100 px-6 gap-6 text-xs font-bold bg-gray-50/50">
          <button
            type="button"
            onClick={() => setActiveTab('rentals')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'rentals' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Active Rentals & OTPs
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('escrow')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'escrow' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Escrow Deposit Vault
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('trust')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'trust' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Trust Level & Benefits
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('referrals')}
            className={`py-3.5 border-b-2 transition-colors cursor-pointer ${
              activeTab === 'referrals' ? 'border-indigo-600 text-indigo-700' : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Refer & Earn
          </button>
        </div>

        {/* Tab Content */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          
          {/* Active Rentals Tab */}
          {activeTab === 'rentals' && (
            <div className="space-y-4">
              {loadingRentals ? (
                <div className="p-8 text-center text-xs font-semibold text-gray-500">
                  <div className="w-6 h-6 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                  Loading your rental reservations...
                </div>
              ) : rentals.length === 0 ? (
                <div className="p-8 text-center rounded-2xl bg-gray-50 border border-gray-200">
                  <ShieldCheck className="w-10 h-10 text-indigo-400 mx-auto mb-2" />
                  <h4 className="font-bold text-gray-900 text-sm">No Active Bookings Yet</h4>
                  <p className="text-xs text-gray-500 mt-1 max-w-sm mx-auto">
                    Browse our vetted catalog of cinema cameras, drones, and gear to place your first reservation with 100% escrow protection.
                  </p>
                </div>
              ) : (
                rentals.map((rental: any) => {
                  const isConfirmed = rental.status === 'CONFIRMED' || rental.status === 'PAYMENT_PENDING';
                  const isActive = rental.status === 'ACTIVE';
                  const isReturn = rental.status === 'RETURN_REQUESTED';
                  const isCompleted = rental.status === 'COMPLETED';

                  return (
                    <div key={rental.id} className="p-5 rounded-2xl bg-gray-50 border border-gray-200 space-y-3">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-gray-200">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-sm text-gray-950">
                              {rental.listing?.title || 'Equipment Rental'}
                            </span>
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                              isCompleted ? 'bg-emerald-100 text-emerald-800' :
                              isActive ? 'bg-indigo-100 text-indigo-800' :
                              isConfirmed ? 'bg-blue-100 text-blue-800' :
                              isReturn ? 'bg-amber-100 text-amber-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {rental.status_display || rental.status}
                            </span>
                          </div>
                          <div className="text-xs text-gray-500 mt-0.5">
                            Booking #{rental.id} · {rental.listing?.city || 'Bangalore'} ({rental.listing?.area || 'Hub'})
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-xs text-gray-500">Rental Period</div>
                          <div className="text-xs font-bold text-gray-900">
                            {rental.start_datetime ? rental.start_datetime.split('T')[0] : ''} – {rental.end_datetime ? rental.end_datetime.split('T')[0] : ''}
                          </div>
                        </div>
                      </div>

                      {/* Action Feedback Message */}
                      {actionMsg && actionMsg.id === rental.id && (
                        <div className={`p-3 rounded-xl text-xs font-semibold flex items-center gap-2 ${
                          actionMsg.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'
                        }`}>
                          <span>{actionMsg.type === 'success' ? '✓' : '⚠️'}</span>
                          <span>{actionMsg.text}</span>
                        </div>
                      )}

                      {/* Handover OTP Widget */}
                      {isConfirmed && rental.handover_otp && (
                        <div className="p-4 rounded-xl bg-white border border-indigo-100 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
                              <KeyRound className="w-5 h-5" />
                            </div>
                            <div>
                              <div className="text-xs font-bold text-gray-900">Secure Handover OTP</div>
                              <div className="text-[11px] text-gray-500">Share this code with the driver upon gear delivery to activate rental</div>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            <div className="flex items-center gap-2 bg-indigo-50 px-3 py-1.5 rounded-xl border border-indigo-200">
                              <span className="font-mono text-base font-black tracking-widest text-indigo-700">{rental.handover_otp}</span>
                            </div>
                            <button
                              type="button"
                              onClick={() => handleVerifyHandover(rental.id, rental.handover_otp)}
                              disabled={actionLoading === rental.id}
                              className="text-xs font-bold px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl transition-all cursor-pointer disabled:opacity-50 shadow-xs shrink-0"
                            >
                              {actionLoading === rental.id ? 'Verifying...' : 'Verify Handover'}
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Return OTP Widget */}
                      {(isActive || isReturn) && rental.return_otp && (
                        <div className="p-4 rounded-xl bg-white border border-amber-100 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
                              <KeyRound className="w-5 h-5" />
                            </div>
                            <div>
                              <div className="text-xs font-bold text-gray-900">Return Handover Secret OTP</div>
                              <div className="text-[11px] text-gray-500">Share this code with the driver upon gear return collection</div>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            <div className="flex items-center gap-2 bg-amber-50 px-3 py-1.5 rounded-xl border border-amber-200">
                              <span className="font-mono text-base font-black tracking-widest text-amber-700">{rental.return_otp}</span>
                            </div>
                            <button
                              type="button"
                              onClick={() => handleVerifyReturn(rental.id, rental.return_otp)}
                              disabled={actionLoading === rental.id}
                              className="text-xs font-bold px-3 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl transition-all cursor-pointer disabled:opacity-50 shadow-xs shrink-0"
                            >
                              {actionLoading === rental.id ? 'Completing...' : 'Verify Return & Complete'}
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Completed Rental & Escrow Release Widget */}
                      {isCompleted && (
                        <div className="p-4 rounded-xl bg-emerald-50/70 border border-emerald-200/80 flex flex-col sm:flex-row items-center justify-between gap-4">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center shrink-0">
                              <CheckCircle2 className="w-5 h-5" />
                            </div>
                            <div>
                              <div className="text-xs font-bold text-emerald-950">Rental Successfully Completed & Returned</div>
                              <div className="text-[11px] text-emerald-700">Gear condition verified intact. Refundable security deposit of ₹{rental.pricing_snapshot?.security_deposit_amount || '0.00'} released back to your bank account.</div>
                            </div>
                          </div>
                          <span className="bg-emerald-600 text-white text-[10px] font-bold px-3 py-1.5 rounded-full uppercase tracking-wider shrink-0 shadow-xs">
                            Escrow Settled ✓
                          </span>
                        </div>
                      )}

                      {/* Pricing & Escrow summary */}
                      <div className="flex items-center justify-between text-xs text-gray-600 px-1 pt-1">
                        <div className="flex items-center gap-1.5">
                          <Truck className="w-3.5 h-3.5 text-indigo-600" />
                          <span>Fulfillment: {rental.fulfillment_type_display || (rental.fulfillment_type === 'DRIVER_DELIVERY' ? 'Doorstep Delivery' : 'Self Pickup')}</span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span>Deposit: <strong className="text-emerald-700">₹{rental.pricing_snapshot?.security_deposit_amount || '0.00'}</strong></span>
                          <span>Paid: <strong className="text-gray-900">₹{rental.pricing_snapshot?.total_amount_paid || '0.00'}</strong></span>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}

              {/* Browse More Gear Action */}
              <div className="p-4 rounded-2xl bg-indigo-50/60 border border-indigo-100 flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold text-indigo-950">Looking to rent more high-end gear?</h4>
                  <p className="text-[11px] text-indigo-700">Drones, cinema cameras, lighting, laptops & e-bikes available across 6 cities.</p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    onClose();
                    if (onBrowseGear) onBrowseGear();
                  }}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-sm transition-all cursor-pointer flex items-center gap-1"
                >
                  <span>Explore Gear</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>

            </div>
          )}

          {/* Escrow Deposit Tab */}
          {activeTab === 'escrow' && (
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-start gap-3">
                <Lock className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-xs font-bold text-emerald-950">Double-Entry Security Deposit Guarantee</h4>
                  <p className="text-[11px] text-emerald-800 mt-1 leading-relaxed">
                    Your refundable deposits are locked in Rentido's regulated ledger vault. Neither owners nor third parties have direct access until physical handover is inspected and approved.
                  </p>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-gray-50 border border-gray-200">
                <div className="flex justify-between items-center mb-3">
                  <span className="text-xs font-bold text-gray-700">Active Refundable Deposit Held</span>
                  <span className="text-xl font-black text-emerald-700 font-mono">
                    ₹{rentals
                      .filter((r: any) => r.status !== 'COMPLETED' && r.status !== 'CANCELLED')
                      .reduce((sum: number, r: any) => sum + (parseFloat(r.pricing_snapshot?.security_deposit_amount) || 0), 0)
                      .toFixed(2)}
                  </span>
                </div>
                <div className="text-[11px] text-gray-500 space-y-1">
                  <div className="flex justify-between">
                    <span>Active Protected Reservations:</span>
                    <span className="font-semibold text-gray-800">
                      {rentals.filter((r: any) => r.status !== 'COMPLETED' && r.status !== 'CANCELLED').length} Rentals
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Deposit Release Condition:</span>
                    <span className="text-emerald-700 font-semibold">Automatic refund upon return OTP verification</span>
                  </div>
                </div>
              </div>

              {/* Itemized Deposit Status List */}
              <div className="space-y-2">
                <h5 className="text-xs font-bold uppercase tracking-wider text-gray-700">Reservation Escrow Ledger History</h5>
                {rentals.length === 0 ? (
                  <p className="text-xs text-gray-500 py-2">No escrow deposit transactions recorded yet.</p>
                ) : (
                  <div className="divide-y divide-gray-100 border border-gray-200 rounded-2xl overflow-hidden bg-white">
                    {rentals.map((r: any) => {
                      const isCompleted = r.status === 'COMPLETED';
                      const depositAmt = r.pricing_snapshot?.security_deposit_amount || '0.00';
                      return (
                        <div key={r.id} className="p-3.5 flex items-center justify-between hover:bg-gray-50/50">
                          <div>
                            <div className="font-bold text-xs text-gray-950">
                              {r.listing?.title || `Rental #${r.id}`}
                            </div>
                            <div className="text-[10px] text-gray-500 mt-0.5">
                              Booking #{r.id} · Status: <span className="font-semibold text-gray-700">{r.status_display || r.status}</span>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-xs font-black text-gray-900 font-mono">
                              ₹{depositAmt}
                            </div>
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full inline-block mt-0.5 ${
                              isCompleted ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                            }`}>
                              {isCompleted ? 'Refunded to Bank' : 'Locked in Escrow'}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}


          {/* Trust Score Tab */}
          {activeTab === 'trust' && (
            <div className="space-y-4">
              <div className="p-5 rounded-2xl bg-amber-50/70 border border-amber-200 text-center">
                <div className="text-[11px] font-bold uppercase tracking-wider text-amber-800">Your Current Trust Score</div>
                <div className="text-3xl font-black text-amber-950 my-1">150 / 1000</div>
                <div className="text-xs font-bold text-amber-700">Tier: Silver Verified Renter</div>
                <p className="text-[11px] text-amber-900/80 mt-2 max-w-md mx-auto leading-relaxed">
                  Complete on-time returns and zero-damage equipment rentals to increase your score to <strong>Gold (400+)</strong> for a <strong>20% security deposit reduction</strong>!
                </p>
              </div>

              <div className="space-y-2 text-xs">
                <div className="p-3.5 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-between">
                  <span>Phone & Email Identity Verified</span>
                  <span className="text-emerald-600 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> +50 pts
                  </span>
                </div>
                <div className="p-3.5 rounded-xl bg-gray-50 border border-gray-100 flex items-center justify-between">
                  <span>First Booking Successful Handover</span>
                  <span className="text-emerald-600 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> +100 pts
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Referrals Tab */}
          {activeTab === 'referrals' && (
            <div className="space-y-4">
              <div className="p-5 rounded-2xl bg-indigo-50 border border-indigo-100 text-center">
                <Share2 className="w-8 h-8 text-indigo-600 mx-auto mb-2" />
                <h4 className="text-sm font-black text-indigo-950">Refer Creators, Filmmakers & Freelancers</h4>
                <p className="text-xs text-indigo-700 mt-1 max-w-md mx-auto">
                  Share your referral link with peers. When they complete their first rental, both of you get <strong>₹500 rental credits</strong>!
                </p>
                <div className="mt-4 p-2 bg-white rounded-xl border border-indigo-200 flex items-center justify-between max-w-sm mx-auto">
                  <span className="text-xs font-mono font-bold text-indigo-900 pl-2">
                    rentido.com/r/{user?.email?.split('@')[0] || 'creator'}
                  </span>
                  <button
                    type="button"
                    onClick={() => navigator.clipboard?.writeText(`https://rentido.com/r/${user?.email?.split('@')[0] || 'creator'}`)}
                    className="px-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white text-[11px] font-bold rounded-lg cursor-pointer"
                  >
                    Copy
                  </button>
                </div>
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
