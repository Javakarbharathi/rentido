'use client';

import React, { useState } from 'react';
import { X, LogIn, Lock, Mail, ShieldCheck } from 'lucide-react';
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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const data = await loginUser(email, password);
      if (data.access) {
        onSuccess(data.user, data.access);
        onClose();
      } else {
        setError(data.detail || 'Invalid email or password');
      }
    } catch (err) {
      setError('Unable to reach authentication server. Ensure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const fillAdmin = () => {
    setEmail('admin@rentido.com');
    setPassword('adminpassword123');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
      <div className="relative w-full max-w-md bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gray-50/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 text-white flex items-center justify-center">
              <LogIn className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-gray-950 text-base">Sign In to Rentido</h3>
              <p className="text-xs text-gray-700">Access your escrow bookings & trust badge</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-white border border-gray-200 flex items-center justify-center text-gray-700 hover:text-gray-900 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-gray-400 absolute left-3.5 top-3" />
              <input 
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-xs font-medium text-gray-900 outline-none focus:border-indigo-500 focus:bg-white"
                placeholder="name@example.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-gray-400 absolute left-3.5 top-3" />
              <input 
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-xs font-medium text-gray-900 outline-none focus:border-indigo-500 focus:bg-white"
                placeholder="••••••••"
              />
            </div>
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-red-50 border border-red-100 text-xs text-red-700 font-semibold">
              {error}
            </div>
          )}

          {/* 1-Click Admin Demo Credentials Pill */}
          <button
            type="button"
            onClick={fillAdmin}
            className="w-full py-2 px-3 rounded-xl bg-indigo-50/70 border border-indigo-100 text-[11px] text-indigo-700 font-semibold hover:bg-indigo-100/70 transition-colors text-left flex items-center justify-between"
          >
            <span>👉 Click to autofill Superuser Demo Login</span>
            <span className="font-bold">admin@rentido.com</span>
          </button>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-4 rounded-xl text-xs shadow-md shadow-indigo-200 transition-all cursor-pointer disabled:opacity-60"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>

        </form>

      </div>
    </div>
  );
}
