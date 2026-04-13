/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    serverActions: {
      allowedOrigins: ['178-104-87-224.nip.io'],
    },
  },
}

module.exports = nextConfig
