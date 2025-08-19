"use client";

import { useEffect, useState } from "react";
import {
  testDataLakeConnection,
  getDataLakeRoot,
  DataLakeHealth,
  DataLakeRoot,
} from "./api";

export default function Home() {
  const [connectionStatus, setConnectionStatus] = useState<
    "loading" | "connected" | "error"
  >("loading");
  const [healthData, setHealthData] = useState<DataLakeHealth | null>(null);
  const [rootData, setRootData] = useState<DataLakeRoot | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function testConnection() {
      try {
        setConnectionStatus("loading");
        setError("");

        // Test health endpoint
        const health = await testDataLakeConnection();
        setHealthData(health);

        // Test root endpoint
        const root = await getDataLakeRoot();
        setRootData(root);

        setConnectionStatus("connected");
      } catch (err) {
        setConnectionStatus("error");
        setError(err instanceof Error ? err.message : "Unknown error");
      }
    }

    testConnection();
  }, []);

  return (
    <main className="min-h-screen bg-bg p-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-text mb-2">
            Fire IoT Dashboard
          </h1>
          <p className="text-muted">
            Full MSA: DataLake, ControlTower, StaticManagement, Alert
          </p>
        </header>

        {/* Connection Status */}
        <section className="bg-card text-text rounded-2xl shadow-card border border-border p-4 mb-6">
          <header className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">DataLake Connection</h2>
            <span
              className={`inline-flex items-center rounded-xl px-2.5 py-1 text-xs font-semibold ${
                connectionStatus === "connected"
                  ? "bg-ok/15 text-ok"
                  : connectionStatus === "error"
                  ? "bg-emergency/15 text-emergency"
                  : "bg-muted/15 text-muted"
              }`}
            >
              {connectionStatus === "loading"
                ? "Connecting..."
                : connectionStatus === "connected"
                ? "Connected"
                : "Error"}
            </span>
          </header>

          {connectionStatus === "loading" && (
            <p className="text-muted">Testing connection to DataLake...</p>
          )}

          {connectionStatus === "connected" && healthData && (
            <div className="space-y-2">
              <p className="text-sm">
                <strong>Health:</strong> {healthData.status}
              </p>
              <p className="text-sm">
                <strong>Service:</strong> {healthData.service}
              </p>
              {rootData && (
                <p className="text-sm">
                  <strong>Message:</strong> {rootData.message}
                </p>
              )}
            </div>
          )}

          {connectionStatus === "error" && (
            <div className="space-y-2">
              <p className="text-sm text-emergency">
                <strong>Error:</strong> {error}
              </p>
              <p className="text-sm text-muted">
                Make sure DataLake is running on port 8084
              </p>
            </div>
          )}
        </section>

        <div className="grid gap-4 md:grid-cols-3">
          <section className="bg-card text-text rounded-2xl shadow-card border border-border p-4">
            <header className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold">Active Alerts</h2>
              <span className="inline-flex items-center rounded-xl px-2.5 py-1 text-xs font-semibold bg-emergency/15 text-emergency">
                12
              </span>
            </header>
            <button className="inline-flex items-center gap-2 rounded-xl px-4 py-2 font-medium bg-primary text-primary-fg hover:opacity-90">
              View all
            </button>
          </section>

          <section className="bg-card text-text rounded-2xl shadow-card border border-border p-4">
            <header className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold">System Status</h2>
              <span className="inline-flex items-center rounded-xl px-2.5 py-1 text-xs font-semibold bg-ok/15 text-ok">
                Healthy
              </span>
            </header>
            <button className="inline-flex items-center gap-2 rounded-xl px-4 py-2 font-medium bg-transparent text-text border border-border hover:bg-card">
              Details
            </button>
          </section>

          <section className="bg-card text-text rounded-2xl shadow-card border border-border p-4">
            <header className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold">Data Processing</h2>
              <span className="inline-flex items-center rounded-xl px-2.5 py-1 text-xs font-semibold bg-warn/15 text-warn">
                Warning
              </span>
            </header>
            <button className="inline-flex items-center gap-2 rounded-xl px-4 py-2 font-medium bg-transparent text-text border border-border hover:bg-card">
              Monitor
            </button>
          </section>
        </div>
      </div>
    </main>
  );
}
