"use client";

import { useEffect, useState, useCallback } from "react";
import { GrantCard } from "@/components/GrantCard";
import { Loader2, RefreshCw } from "lucide-react";
import NeonLogo from "@/components/ui/NeonLogo";
import FilterBar from "@/components/FilterBar";

import CinematicBackground from "@/components/CinematicBackground";
import Navbar from "@/components/Navbar";
import type { Bando } from "@/lib/types";

export default function Home() {
  const [bandi, setBandi] = useState<Bando[]>([]);
  const [loading, setLoading] = useState(true);

  // Pagination State
  const [page, setPage] = useState(1);
  const pageSize = 12; // 12 cards per page (3x4 or 2x6)
  const [hasMore, setHasMore] = useState(true);

  // Filters State
  const [search, setSearch] = useState("");
  const [region, setRegion] = useState("");
  const [status, setStatus] = useState("");

  const fetchBandi = useCallback(async () => {
    setLoading(true);
    try {
      // STATIC MODE: Fetch from JSON and filter client-side
      // BasePath is /AlSolved_Bandi, so we need to include it in manual fetches
      const basePath = process.env.NODE_ENV === "production" ? "/AlSolved_Bandi" : "";
      const res = await fetch(`${basePath}/bandi.json`);
      if (!res.ok) throw new Error("Failed to load static data");

      let data = await res.json();

      // Client-side Filtering
      if (search) {
        const lowerSearch = search.toLowerCase();
        data = data.filter((b: Bando) =>
          b.title.toLowerCase().includes(lowerSearch) ||
          (b.marketing_text && b.marketing_text.toLowerCase().includes(lowerSearch))
        );
      }

      if (region && region !== "") {
        data = data.filter((b: Bando) => {
          // simple check against regions array or string
          const r = JSON.stringify(b.ai_analysis?.regions || b.ai_analysis?.regione || "").toLowerCase();
          return r.includes(region.toLowerCase());
        });
      }

      if (status === "attivi") {
        data = data.filter((b: Bando) => {
          const expired = b.ai_analysis?.is_expired;
          return expired !== true && expired !== "true";
        });
      } else if (status === "scaduti") {
        data = data.filter((b: Bando) => {
          const expired = b.ai_analysis?.is_expired;
          return expired === true || expired === "true";
        });
      }

      // Pagination
      const start = (page - 1) * pageSize;
      const end = start + pageSize;
      const paginatedData = data.slice(start, end);

      setBandi(paginatedData);
      setHasMore(end < data.length);

    } catch (e) {
      console.error(e);
      // Fallback to empty
      setBandi([]);
    } finally {
      setLoading(false);
    }
  }, [page, search, region, status]);

  // Debounce Search & Reset Page
  useEffect(() => {
    // When filters change, reset to page 1
    // This effect runs on filter change. We need a separate logic to not reset on page change.
    // Actually, simple way: when search/region/status changes, setPage(1).
  }, [search, region, status]);

  // Trigger Fetch
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchBandi();
    }, 300);
    return () => clearTimeout(timer);
  }, [fetchBandi]);

  // Handlers for Filters to reset page
  const handleSearch = (val: string) => { setSearch(val); setPage(1); };
  const handleRegion = (val: string) => { setRegion(val); setPage(1); };
  const handleStatus = (val: string) => { setStatus(val); setPage(1); };

  return (
    <>
      <Navbar />
      <CinematicBackground />
      <main className="min-h-screen text-gray-900 p-8 pt-24">
        {/* Header */}
        <div className="max-w-7xl mx-auto mb-8 flex flex-col md:flex-row justify-between items-center gap-6 border-b border-gray-200 pb-8">
          <div className="flex flex-col gap-4">
            <NeonLogo size="lg" />
            <p className="mt-2 text-gray-500 font-light pl-2">
              Monitoraggio bandi e finanza agevolata in tempo reale.
            </p>
          </div>
          <button
            onClick={() => { setPage(1); fetchBandi(); }}
            className="flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary/90 rounded-full font-bold text-sm uppercase tracking-wide transition-all shadow-md hover:shadow-lg shadow-primary/20 text-white"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Aggiorna DB
          </button>
        </div>

        {/* Filter Bar */}
        <FilterBar
          onSearchChange={handleSearch}
          onRegionChange={handleRegion}
          onStatusChange={handleStatus}
        />

        {/* Grid */}
        <div className="max-w-7xl mx-auto pb-20">
          {loading && bandi.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-gray-400">
              <Loader2 className="w-12 h-12 animate-spin mb-4 text-primary" />
              <p>Caricamento Bandi...</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
                {bandi.map((bando: Bando) => (
                  <GrantCard key={bando.id} bando={bando} />
                ))}
              </div>

              {/* Pagination Controls */}
              <div className="flex items-center justify-center gap-4">
                <button
                  disabled={page === 1 || loading}
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  className="px-6 py-3 rounded-full bg-white border border-gray-200 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-bold uppercase text-xs tracking-wider shadow-sm text-gray-700"
                >
                  Precedente
                </button>

                <span className="text-sm font-light text-gray-500">
                  Pagina <b className="text-gray-900">{page}</b>
                </span>

                <button
                  disabled={!hasMore || loading}
                  onClick={() => setPage(p => p + 1)}
                  className="px-6 py-3 rounded-full bg-primary hover:bg-primary/90 text-white shadow-md hover:shadow-lg shadow-primary/20 disabled:opacity-50 disabled:shadow-none disabled:bg-gray-300 disabled:cursor-not-allowed transition-all font-bold uppercase text-xs tracking-wider"
                >
                  Successiva
                </button>
              </div>
            </>
          )}

          {!loading && bandi.length === 0 && (
            <div className="text-center py-20 text-gray-500">
              Nessun bando trovato con questi criteri.
            </div>
          )}
        </div>
      </main>
    </>
  );
}
