import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactCompiler: true,
  allowedDevOrigins: [
    '192.168.1.122',   // your current device IP
    '192.168.1.*',     // OR allow all devices on your network
  ],
};

export default nextConfig;
