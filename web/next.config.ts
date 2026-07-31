import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/", destination: "/La%20Silhouette.dc.html" }];
  },
};

export default nextConfig;
