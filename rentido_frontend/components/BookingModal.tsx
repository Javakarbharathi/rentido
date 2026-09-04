'use client';

import React, { useState } from 'react';
import { 
  X, 
  ShieldCheck, 
  Calendar, 
  Truck, 
  Tag, 
  CheckCircle2, 
  Lock, 
  KeyRound,
  ArrowRight,
  AlertCircle
} from 'lucide-react';
import { Listing, validateCoupon, API_BASE_URL } from '@/lib/api';

interface BookingModalProps {
  listing: Listing | null;
  onClose: () => void;
  user: any;
  onOpenAuth: () => void;
}

export default function BookingModal({ listing, onClose, user, onOpenAuth }: BookingModalProps) {
  if (!listing) return null;

  // Rental duration state (default 2 days)
  const [days, setDays] = useState(2);
  const [fulfillment, setFulfillment] = useState<'SELF_PICKUP' | 'DRIVER_DELIVERY'>('DRIVER_DELIVERY');
  
  // Coupon state
  const [couponInput, setCouponInput] = useState('');
  const [appliedCoupon, setAppliedCoupon] = useState<any>(null);
  const [couponError, setCouponError] = useState('');
  const [couponLoading, setCouponLoading] = useState(false);

  // Booking completion state
  const [bookingSuccess, setBookingSuccess] = useState<any>(null);
  const [bookingLoading, setBookingLoading] = useState(false);

  // Financial calculations
  const dailyRate = parseFloat(listing.rental_price) || 1500;
  const deposit = parseFloat(listing.security_deposit) || 5000;
  const baseRent = dailyRate * days;
  const deliveryFee = fulfillment === 'DRIVER_DELIVERY' ? 150 : 0;
  const platformFee = 50;

  let discount = 0;
  if (appliedCoupon) {
    discount = parseFloat(appliedCoupon.discount_amount) || 0;
  }

  const effectiveRent = Math.max(baseRent - discount, 0);
  const totalPayable = effectiveRent + platformFee + deliveryFee + deposit;

  // Handle Coupon Apply
  const handleApplyCoupon = async () => {
    if (!couponInput.trim()) return;
    setCouponLoading(true);
    setCouponError('');

    const now = new Date();
    const start = new Date(now.getTime() + 24 * 60 * 60 * 1000).toISOString();
    const end = new Date(now.getTime() + (24 + days * 24) * 60 * 60 * 1000).toISOString();

    try {
      const res = await validateCoupon(couponInput.trim(), listing.id, start, end);
      if (res.valid) {
        setAppliedCoupon(res);
        setCouponError('');
      } else {
        setAppliedCoupon(null);
        setCouponError(res.message || 'Invalid coupon code');
      }
    } catch (err) {
      // Fallback for local preview if server offline
      if (couponInput.toUpperCase() === 'WELCOME20') {
        const disc = (baseRent * 0.2).toFixed(2);
        setAppliedCoupon({
          valid: true,
          coupon_code: 'WELCOME20',
          discount_amount: disc,
          message: `Coupon applied! You saved ₹${disc}`
        });
      } else {
        setCouponError('Invalid coupon code');
      }
    } finally {
      setCouponLoading(false);
    }
  };

  // Handle Simulated 1-Click Checkout
  const handleConfirmBooking = async () => {
    if (!user) {
      onOpenAuth();
      return;
    }

    setBookingLoading(true);
    // Simulate payment & booking creation
    setTimeout(() => {
      setBookingLoading(false);
      const generatedOtp = Math.floor(100000 + Math.random() * 900000).toString();
      setBookingSuccess({
        rentalId: Math.floor(1000 + Math.random() * 9000),
        otp: generatedOtp,
        totalPaid: totalPayable,
        depositHeld: deposit,
        dates: `${days} Days`,
        fulfillment: fulfillment === 'DRIVER_DELIVERY' ? 'Doorstep Delivery' : 'Self Pickup'
      });
    }, 1200);
  };

  return (
    <div 
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm overflow-y-auto cursor-pointer"
    >
      <div className="relative w-full max-w-xl bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden my-8 cursor-default">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gray-50/50">
          <div>
            <span className="text-[11px] uppercase font-bold tracking-wider text-indigo-600">Escrow Checkout</span>
            <h2 className="text-lg font-black text-gray-950 mt-0.5">{listing.title}</h2>
          </div>
          <button 
            onClick={onClose}
            className="w-9 h-9 rounded-full bg-white border border-gray-200 flex items-center justify-center text-gray-700 hover:text-gray-900 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {bookingSuccess ? (
          /* Booking Confirmation State */
          <div className="p-8 text-center">
            <div className="w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-4">
              <CheckCircle2 className="w-10 h-10" />
            </div>

            <h3 className="text-2xl font-black text-gray-950">Rental Booking Confirmed!</h3>
            <p className="text-sm text-gray-700 mt-1">
              Your payment of <strong className="text-gray-900">₹{bookingSuccess.totalPaid.toFixed(2)}</strong> has been processed.
              The security deposit of ₹{bookingSuccess.depositHeld.toFixed(2)} is securely locked in escrow.
            </p>

            {/* Handover OTP Card */}
            <div className="my-6 p-5 rounded-2xl bg-indigo-50/80 border border-indigo-100 text-center">
              <div className="flex items-center justify-center gap-2 text-indigo-900 font-bold text-xs uppercase tracking-wider mb-1">
                <KeyRound className="w-4 h-4 text-indigo-600" />
                <span>Your Secure Handover OTP</span>
              </div>
              <div className="text-4xl font-black text-indigo-700 tracking-widest my-2">
                {bookingSuccess.otp}
              </div>
              <p className="text-xs text-gray-700 max-w-sm mx-auto">
                Do not share this code until the equipment has been physically handed over to you and you have verified its operating condition.
              </p>
            </div>

            <button
              onClick={onClose}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3.5 px-6 rounded-2xl shadow-md shadow-indigo-300 transition-all cursor-pointer"
            >
              Done & View Active Bookings
            </button>
          </div>
        ) : (
          /* Interactive Booking Form */
          <div className="p-6 space-y-6">
            
            {/* Duration Selector */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-2">
                Rental Duration
              </label>
              <div className="grid grid-cols-4 gap-2">
                {[1, 2, 3, 7].map((d) => (
                  <button
                    key={d}
                    type="button"
                    onClick={() => setDays(d)}
                    className={`py-2.5 px-3 rounded-xl border text-xs font-bold transition-all cursor-pointer ${
                      days === d 
                        ? 'bg-indigo-600 border-indigo-600 text-white shadow-xs' 
                        : 'bg-white border-gray-200 text-gray-700 hover:border-indigo-300'
                    }`}
                  >
                    {d} {d === 1 ? 'Day' : 'Days'}
                  </button>
                ))}
              </div>
            </div>

            {/* Fulfillment Mode */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-2">
                Fulfillment & Delivery
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setFulfillment('DRIVER_DELIVERY')}
                  className={`p-3 rounded-xl border text-left flex items-start gap-2.5 transition-all cursor-pointer ${
                    fulfillment === 'DRIVER_DELIVERY'
                      ? 'bg-indigo-50/60 border-indigo-600 text-indigo-950'
                      : 'bg-white border-gray-200 text-gray-600 hover:border-indigo-200'
                  }`}
                >
                  <Truck className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                  <div>
                    <div className="text-xs font-bold text-gray-900">Doorstep Delivery</div>
                    <div className="text-[11px] text-gray-700">+₹150 (Fleet Dispatch)</div>
                  </div>
                </button>

                <button
                  type="button"
                  onClick={() => setFulfillment('SELF_PICKUP')}
                  className={`p-3 rounded-xl border text-left flex items-start gap-2.5 transition-all cursor-pointer ${
                    fulfillment === 'SELF_PICKUP'
                      ? 'bg-indigo-50/60 border-indigo-600 text-indigo-950'
                      : 'bg-white border-gray-200 text-gray-600 hover:border-indigo-200'
                  }`}
                >
                  <ShieldCheck className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                  <div>
                    <div className="text-xs font-bold text-gray-900">Self Pickup</div>
                    <div className="text-[11px] text-gray-700">Free · {listing.city} Hub</div>
                  </div>
                </button>
              </div>
            </div>

            {/* Coupon Code Input */}
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-2">
                Promo Code / Coupon
              </label>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Tag className="w-4 h-4 text-gray-400 absolute left-3.5 top-3" />
                  <input 
                    type="text"
                    value={couponInput}
                    onChange={(e) => setCouponInput(e.target.value.toUpperCase())}
                    placeholder="Try 'WELCOME20'"
                    className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-xs font-semibold uppercase text-gray-900 outline-none focus:border-indigo-500 focus:bg-white"
                  />
                </div>
                <button
                  type="button"
                  onClick={handleApplyCoupon}
                  disabled={couponLoading || !couponInput.trim()}
                  className="bg-gray-900 hover:bg-black text-white text-xs font-bold px-4 py-2.5 rounded-xl cursor-pointer disabled:opacity-50"
                >
                  {couponLoading ? 'Checking...' : 'Apply'}
                </button>
              </div>

              {appliedCoupon && (
                <div className="mt-2 text-xs font-semibold text-emerald-600 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>{appliedCoupon.message || `Code ${appliedCoupon.coupon_code} applied!`}</span>
                </div>
              )}

              {couponError && (
                <div className="mt-2 text-xs font-semibold text-red-700 flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{couponError}</span>
                </div>
              )}
            </div>

            {/* Price Breakdown Card */}
            <div className="p-4 rounded-2xl bg-gray-50 border border-gray-100 space-y-2 text-xs">
              <div className="flex justify-between text-gray-600">
                <span>Base Rent ({days} days × ₹{dailyRate})</span>
                <span className="font-semibold text-gray-900">₹{baseRent.toFixed(2)}</span>
              </div>

              {discount > 0 && (
                <div className="flex justify-between text-emerald-600 font-semibold">
                  <span>Coupon Discount ({appliedCoupon.coupon_code})</span>
                  <span>-₹{discount.toFixed(2)}</span>
                </div>
              )}

              <div className="flex justify-between text-gray-600">
                <span>Platform Service Fee</span>
                <span className="font-semibold text-gray-900">₹{platformFee.toFixed(2)}</span>
              </div>

              {deliveryFee > 0 && (
                <div className="flex justify-between text-gray-600">
                  <span>Doorstep Delivery Dispatch</span>
                  <span className="font-semibold text-gray-900">₹{deliveryFee.toFixed(2)}</span>
                </div>
              )}

              <div className="flex justify-between text-gray-600 pt-2 border-t border-gray-200">
                <span className="flex items-center gap-1">
                  <Lock className="w-3 h-3 text-emerald-600" />
                  <span>Refundable Security Deposit (Escrow)</span>
                </span>
                <span className="font-bold text-emerald-600">₹{deposit.toFixed(2)}</span>
              </div>

              <div className="flex justify-between items-baseline pt-2 border-t border-gray-200 text-sm font-black text-gray-950">
                <span>Total Amount Due Now</span>
                <span className="text-lg text-indigo-700">₹{totalPayable.toFixed(2)}</span>
              </div>
            </div>

            {/* Escrow Trust Guarantee */}
            <div className="flex items-start gap-2 text-[11px] text-gray-700 bg-emerald-50/60 border border-emerald-100 p-3 rounded-xl">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <span>
                Your ₹{deposit.toFixed(2)} deposit is locked in Rentido's double-entry escrow ledger. It is returned automatically to your source account upon return inspection approval.
              </span>
            </div>

            {/* Checkout Action Button */}
            <button
              type="button"
              onClick={handleConfirmBooking}
              disabled={bookingLoading}
              className="w-full bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 text-white font-bold py-3.5 px-6 rounded-2xl shadow-md shadow-indigo-300 hover:shadow-lg transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60"
            >
              <span>{bookingLoading ? 'Securing in Escrow...' : `Pay ₹${totalPayable.toFixed(2)} & Activate Rental`}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

          </div>
        )}

      </div>
    </div>
  );
}
