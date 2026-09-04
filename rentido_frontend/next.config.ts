import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow dev connections from localhost and local network / VM host adapters
  allowedDevOrigins: ['192.168.56.1', 'localhost', '127.0.0.1'],
  // Do not redirect URLs ending with a slash to without a slash (prevents redirect loops with Django APPEND_SLASH)
  skipTrailingSlashRedirect: true,
  // Proxy all /api requests directly to Django backend preserving slashes
  async rewrites() {
    return [
      {
        source: '/api/:path*/',
        destination: 'http://127.0.0.1:8000/api/:path*/',
      },
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
