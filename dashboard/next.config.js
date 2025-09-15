/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_GATEWAY_URL: process.env.NEXT_PUBLIC_API_GATEWAY_URL || 'http://localhost:4000',
    NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || 'pk_test_51RkUYkQ6s74Bq3bW4Nrjoce3QPjYvC3GLL9iNqn0L85CdzMfDFPuNnHmr8VRXkZ2J57RSqoCG8jl1EbhUQqIEHHB00Hec9MITh',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:4000/api/gateway/:path*',
      },
    ];
  },
};

module.exports = nextConfig;