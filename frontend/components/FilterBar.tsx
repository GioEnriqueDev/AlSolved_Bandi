"use client";

import { Search, Filter, MapPin } from "lucide-react";
import { useEffect, useState } from "react";

interface FilterBarProps {
    onSearchChange: (value: string) => void;
    onRegionChange: (value: string) => void;
    onStatusChange: (status: string) => void;
}

export default function FilterBar({
    onSearchChange,
    onRegionChange,
    onStatusChange,
}: FilterBarProps) {
    const [regions, setRegions] = useState<string[]>([]);
    const [loadingRegions, setLoadingRegions] = useState(true);

    // Fetch regions from API
    useEffect(() => {
        const fetchRegions = async () => {
            try {
                // In static export mode, we might want to hardcode or fetch from JSON if available
                // For now, keeping the fetch but handling failure gracefully as seen in original
                const res = await fetch("http://localhost:8000/regioni");
                if (res.ok) {
                    const data = await res.json();
                    setRegions(data);
                }
            } catch (e) {
                console.error("Failed to fetch regions:", e);
                // Fallback to default regions
                setRegions([
                    "Nazionale", "Lombardia", "Lazio", "Campania",
                    "Veneto", "Piemonte", "Emilia-Romagna", "Sicilia"
                ]);
            } finally {
                setLoadingRegions(false);
            }
        };
        fetchRegions();
    }, []);

    return (
        <div className="w-full max-w-7xl mx-auto mb-8 p-4 rounded-2xl border border-gray-200 bg-white/60 backdrop-blur-md shadow-lg shadow-black/5 flex flex-col md:flex-row gap-4 items-center">

            {/* Search Input */}
            <div className="relative w-full md:w-1/2">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                    type="text"
                    placeholder="Cerca per parola chiave (es. Digitalizzazione, Startups)..."
                    className="w-full bg-white border border-gray-200 rounded-xl py-3 pl-12 pr-4 text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all font-medium shadow-sm"
                    onChange={(e) => onSearchChange(e.target.value)}
                />
            </div>

            {/* Region Select - Dynamic from API */}
            <div className="relative w-full md:w-1/4">
                <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                <select
                    className="w-full bg-white border border-gray-200 rounded-xl py-3 pl-12 pr-4 text-gray-900 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 appearance-none cursor-pointer hover:bg-gray-50 transition-colors shadow-sm"
                    onChange={(e) => onRegionChange(e.target.value)}
                    defaultValue=""
                    disabled={loadingRegions}
                >
                    <option value="" className="bg-white text-gray-900">
                        {loadingRegions ? "Caricamento..." : "Tutte le Regioni"}
                    </option>
                    {regions.map(r => (
                        <option key={r} value={r} className="bg-white text-gray-900">{r}</option>
                    ))}
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400 text-xs">▼</div>
            </div>

            {/* Status Toggles */}
            <div className="flex gap-2 w-full md:w-auto">
                <button
                    onClick={() => onStatusChange("")}
                    className="px-4 py-2 rounded-lg bg-primary/10 text-primary border border-primary/20 font-bold text-xs uppercase hover:bg-primary/20 transition-all"
                >
                    Tutti
                </button>
                <button
                    onClick={() => onStatusChange("analyzed")}
                    className="px-4 py-2 rounded-lg bg-white text-gray-500 border border-gray-200 font-bold text-xs uppercase hover:bg-gray-50 hover:text-gray-900 transition-all shadow-sm"
                >
                    Analizzati
                </button>
            </div>
        </div>
    );
}
