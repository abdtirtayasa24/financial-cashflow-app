import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
};

module.exports = {
  allowedDevOrigins: ['vm-9-64-ubuntu.pygora-dab.ts.net'],
}

export default nextConfig;
