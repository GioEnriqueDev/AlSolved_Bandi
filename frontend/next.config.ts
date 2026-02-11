import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  reactCompiler: true,
  basePath: process.env.NODE_ENV === 'production' ? '/AlSolved_Bandi' : undefined,
  assetPrefix: process.env.NODE_ENV === 'production' ? '/AlSolved_Bandi/' : undefined,
  trailingSlash: true,
};

export default nextConfig;
