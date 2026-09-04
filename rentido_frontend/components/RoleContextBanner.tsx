'use client';

import React from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  Wrench, 
  PackagePlus, 
  FolderClock, 
  Sparkles, 
  Lock, 
  ExternalLink,
  ArrowRight
} from 'lucide-react';
import { isAdminUser, isOwnerUser, isRenterUser, getRoleBadgeInfo, AuthUser } from '@/lib/auth';

interface RoleContextBannerProps {
  user: AuthUser | null;
  onOpenAdminPortal?: () => void;
  onOpenOwnerStudio?: () => void;
  onOpenRenterDashboard?: () => void;
  onOpenTrustModal?: () => void;
}

export default function RoleContextBanner({
  user,
  onOpenAdminPortal,
  onOpenOwnerStudio,
  onOpenRenterDashboard,
  onOpenTrustModal,
}: RoleContextBannerProps) {
  if (!user) return null;

  const isAdmin = isAdminUser(user);
  const isOwner = isOwnerUser(user);
  const isRenter = isRenterUser(user);

  if (isAdmin) {
    return (
      <div className="bg-purple-900 text-white py-3 px-4 border-b border-purple-800 text-xs">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="p-1.5 rounded-lg bg-purple-800 text-purple-200">
              <Wrench className="w-4 h-4" />
            </span>
            <div>
              <span className="font-bold">Platform Governance Mode:</span>
              <span className="text-purple-200 ml-1.5">
                Signed in as Super Admin ({user.email}). Overseeing Escrow Vault (₹85,000), 8 verified equipment listings, and double-blind OTP fleet.
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={onOpenAdminPortal}
              className="px-3 py-1.5 bg-purple-700 hover:bg-purple-600 text-white font-bold rounded-lg transition-colors cursor-pointer flex items-center gap-1"
            >
              <span>Admin Deck</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <a
              href="http://127.0.0.1:8000/admin/"
              target="_blank"
              rel="noreferrer"
              className="px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white font-medium rounded-lg transition-colors flex items-center gap-1"
            >
              <span>Django Admin</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (isOwner) {
    return (
      <div className="bg-emerald-950 text-white py-3 px-4 border-b border-emerald-800 text-xs">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="p-1.5 rounded-lg bg-emerald-800 text-emerald-200">
              <PackagePlus className="w-4 h-4" />
            </span>
            <div>
              <span className="font-bold">Equipment Host Mode:</span>
              <span className="text-emerald-200 ml-1.5">
                Signed in as Equipment Owner ({user.email}). Rent out cinema cameras, drones & gear with full replacement protection & double-entry escrow payouts.
              </span>
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={onOpenOwnerStudio}
              className="px-3 py-1.5 bg-emerald-700 hover:bg-emerald-600 text-white font-bold rounded-lg transition-colors cursor-pointer flex items-center gap-1"
            >
              <span>Manage Portfolio & Payouts</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Renter View Banner
  return (
    <div className="bg-indigo-950 text-white py-3 px-4 border-b border-indigo-800 text-xs">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <span className="p-1.5 rounded-lg bg-indigo-800 text-indigo-200">
            <Lock className="w-4 h-4" />
          </span>
          <div>
            <span className="font-bold">Verified Renter Mode:</span>
            <span className="text-indigo-200 ml-1.5">
              Signed in as {user.email}. Security deposits are protected by Rentido Escrow and automatically released upon verified return.
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={onOpenRenterDashboard}
            className="px-3 py-1.5 bg-indigo-700 hover:bg-indigo-600 text-white font-bold rounded-lg transition-colors cursor-pointer flex items-center gap-1"
          >
            <span>My Rentals & Handover OTPs</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
