// Rentido Backend API Service Connector

export const API_BASE_URL = typeof window !== 'undefined' 
  ? '/api' 
  : (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api');

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon?: string;
}

export interface Listing {
  id: number;
  title: string;
  description: string;
  rental_price: string;
  pricing_model: string;
  security_deposit: string;
  city: string;
  area: string;
  pincode: string;
  is_delivery_available: boolean;
  is_self_pickup_available: boolean;
  status: string;
  asset_name?: string;
  owner_email?: string;
  owner_tier?: string;
  owner_trust_score?: number;
  image_url?: string;
}

export interface PricingBreakdown {
  units: number;
  base_rental_amount: string;
  surge_multiplier: string;
  discount_amount: string;
  coupon_code: string | null;
  coupon_message: string | null;
  platform_fee: string;
  delivery_fee: string;
  security_deposit_amount: string;
  total_amount_paid: string;
  owner_payout_amount: string;
}

export async function fetchCategories(): Promise<Category[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/categories/`, { cache: 'no-store' });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || data || [];
  } catch (err) {
    console.warn('API offline or unreachable, using fallback categories', err);
    return [];
  }
}

export async function fetchListings(city?: string): Promise<Listing[]> {
  try {
    const url = city ? `${API_BASE_URL}/listings/?city=${encodeURIComponent(city)}` : `${API_BASE_URL}/listings/`;
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || data || [];
  } catch (err) {
    console.warn('API offline, using fallback listings', err);
    return [];
  }
}

export async function validateCoupon(
  code: string,
  listingId: number,
  startDatetime: string,
  endDatetime: string
) {
  const res = await fetch(`${API_BASE_URL}/coupons/validate/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      code,
      listing_id: listingId,
      start_datetime: startDatetime,
      end_datetime: endDatetime,
    }),
  });
  return await res.json();
}

export async function loginUser(email: string, password: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json().catch(() => ({ detail: 'Invalid response from server' }));
    if (!res.ok) {
      return {
        error: true,
        detail: data.detail || data.non_field_errors?.[0] || 'Invalid email or password',
      };
    }
    return data;
  } catch (err: any) {
    return {
      error: true,
      detail: 'Network error: could not connect to authentication server. Please verify backend service is running.',
    };
  }
}

export async function fetchTrustProfile(token: string) {
  const res = await fetch(`${API_BASE_URL}/trust/me/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return await res.json();
}

export async function fetchUnreadNotifications(token: string) {
  const res = await fetch(`${API_BASE_URL}/notifications/unread-count/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return await res.json();
}

export async function createAsset(token: string, assetData: any) {
  const res = await fetch(`${API_BASE_URL}/assets/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(assetData),
  });
  return await res.json();
}

export async function createListing(token: string, listingData: any) {
  const res = await fetch(`${API_BASE_URL}/listings/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(listingData),
  });
  return await res.json();
}

export async function fetchOwnerAssets(token: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/assets/`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: 'no-store',
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || data || [];
  } catch (err) {
    console.warn('Could not fetch owner assets', err);
    return [];
  }
}

export async function fetchOwnerListings(token: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/listings/my-listings/`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: 'no-store',
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || data || [];
  } catch (err) {
    console.warn('Could not fetch owner listings', err);
    return [];
  }
}

export async function fetchOwnerEarnings(token: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/payments/ledger/owner-summary/`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: 'no-store',
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (err) {
    console.warn('Could not fetch owner earnings', err);
    return null;
  }
}

export async function requestOwnerPayout(token: string) {
  const res = await fetch(`${API_BASE_URL}/payments/ledger/request-payout/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  });
  return await res.json();
}

