'use client';

import React, { useState } from 'react';
import { X, LogIn, Lock, Mail, ShieldCheck, UserCheck, CheckCircle2 } from 'lucide-react';
import { loginUser } from '@/lib/api';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (userData: any, token: string) => void;
}

export default function AuthModal({ isOpen, onClose, onSuccess }: AuthModalProps) {
  if (!isOpen) return null;

  const [email, setEmail] = useState('admin@rentido.com');
  const [password, setPassword] = useState('adminpassword123');
  const [activeRole, setActiveRole] = useState<'admin' | 'owner' | 'renter'>('admin');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const selectRole = (role: 'admin' | 'owner' | 'renter') => {
    setActiveRole(role);
    setError('');
    if (role === 'admin') {
      setEmail('admin@rentido.com');
      setPassword('adminpassword123');
    } else if (role === 'owner') {
      setEmail('rajesh.camera@rentido.com');
      setPassword('ownerpassword123');
    } else if (role === 'renter') {
      setEmail('ananya.renter@rentido.com');
      setPassword('renterpassword123');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const data = await loginUser(email.trim(), password);
      if (data.access && data.user) {
        onSuccess(data.user, data.access);
        onClose();
      } else {
        setError(data.detail || 'Invalid email or password. Please verify credentials.');
      }
    } catch (err: any) {
      setError('Unable to reach authentication server. Ensure backend is running on 127.0.0.1:8000.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div 
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm cursor-pointer"
    >
      <div className="relative w-full max-w-md bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden cursor-default">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gray-50/70">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 text-white flex items-center justify-center shadow-md shadow-indigo-200">
              <LogIn className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-black text-gray-950 text-base tracking-tight">Sign In to Rentido</h3>
              <p className="text-xs text-gray-600">Access your escrow bookings & trust badge</p>
            </div>
          </div>
          <button 
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white border border-gray-200 flex items-center justify-center text-gray-700 hover:text-gray-950 hover:bg-gray-100 cursor-pointer transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* 1-Click Demo Accounts Quick Selector */}
        <div className="px-6 pt-5 pb-1">
          <div className="text-[11px] font-bold uppercase tracking-wider text-gray-500 mb-2">
            Quick 1-Click Demo Account:
          </div>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => selectRole('admin')}
              className={`py-2 px-2.5 rounded-xl text-xs font-bold border transition-all cursor-pointer text-center ${
                activeRole === 'admin'
                  ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm shadow-indigo-200'
                  : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
              }`}
            >
              🛡️ Admin
            </button>
            <button
              type="button"
              onClick={() => selectRole('owner')}
              className={`py-2 px-2.5 rounded-xl text-xs font-bold border transition-all cursor-pointer text-center ${
                activeRole === 'owner'
                  ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm shadow-indigo-200'
                  : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
              }`}
            >
              📷 Owner
            </button>
            <button
              type="button"
              onClick={() => selectRole('renter')}
              className={`py-2 px-2.5 rounded-xl text-xs font-bold border transition-all cursor-pointer text-center ${
                activeRole === 'renter'
                  ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm shadow-indigo-200'
                  : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
              }`}
            >
              🎒 Renter
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-gray-400 absolute left-3.5 top-3.5" />
              <input 
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-xs font-medium text-gray-900 outline-none focus:border-indigo-500 focus:bg-white transition-colors"
                placeholder="name@example.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-gray-400 absolute left-3.5 top-3.5" />
              <input 
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-xs font-medium text-gray-900 outline-none focus:border-indigo-500 focus:bg-white transition-colors"
                placeholder="••••••••"
              />
            </div>
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 font-medium">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3.5 px-4 rounded-xl text-xs shadow-md shadow-indigo-200 hover:shadow-lg transition-all cursor-pointer disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {loading ? (
              <span>Authenticating...</span>
            ) : (
              <>
                <UserCheck className="w-4 h-4" />
                <span>Sign In as {activeRole.charAt(0).toUpperCase() + activeRole.slice(1)}</span>
              </>
            )}
          </button>

        </form>

      </div>
    </div>
  );
}
