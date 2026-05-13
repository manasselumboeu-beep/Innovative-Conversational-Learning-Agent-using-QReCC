/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // In development, proxy /api/turn to the local Python FastAPI server
    if (process.env.NODE_ENV === "development") {
      return [
        {
          source: "/api/:path*",
          destination: `${process.env.PYTHON_API_URL || "http://localhost:8000"}/api/:path*`,
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
