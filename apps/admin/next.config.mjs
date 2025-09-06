/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost', 'storyqr.ru', 'sqra.ru'],
  },
  env: {
    NEXT_PUBLIC_ADMIN_API_BASE_URL: process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL,
    NEXT_PUBLIC_PUBLIC_BASE_URL: process.env.NEXT_PUBLIC_PUBLIC_BASE_URL,
    NEXT_PUBLIC_SHORT_BASE_URL: process.env.NEXT_PUBLIC_SHORT_BASE_URL,
  },
  async rewrites() {
    return [
      {
        source: '/admin-api/:path*',
        destination: `${process.env.NEXT_PUBLIC_ADMIN_API_BASE_URL || 'http://localhost:8080/admin-api/v1'}/:path*`,
      },
    ];
  },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Robots-Tag',
            value: 'noindex, nofollow',
          },
        ],
      },
    ];
  },
};

export default nextConfig;


