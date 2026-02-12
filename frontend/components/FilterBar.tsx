"use client";

import { Search, MapPin } from "lucide-react";
import { useState } from "react";

interface FilterBarProps {
    onSearchChange: (value: string) => void;
    onRegionChange: (value: string) => void;
    onStatusChange: (status: string) => void;
}

const REGIONS = [
    "Nazionale", "Abruzzo", "Basilicata", "Calabria", "Campania",
    "Emilia-Romagna", "Friuli-Venezia Giulia", "Lazio", "Liguria",
    "Lombardia", "Marche", "Molise", "Piemonte", "Puglia",
    "Sardegna", "Sicilia", "Toscana", "Trentino-Alto Adige",
    "Umbria", "Valle d'Aosta", "Veneto",
];

export default function FilterBar({
    onSearchChange,
    onRegionChange,
    onStatusChange,
}: FilterBarProps) {
    const [activeStatus, setActiveStatus] = useState("");

    const handleStatus = (s: string) => {
        setActiveStatus(s);
        onStatusChange(s);
    };

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

            {/* Region Select */}
            <div className="relative w-full md:w-1/4">
                <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                <select
                    className="w-full bg-white border border-gray-200 rounded-xl py-3 pl-12 pr-4 text-gray-900 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 appearance-none cursor-pointer hover:bg-gray-50 transition-colors shadow-sm"
                    onChange={(e) => onRegionChange(e.target.value)}
                    defaultValue=""
                >
                    <option value="" className="bg-white text-gray-900">Tutte le Regioni</option>
                    {REGIONS.map(r => (
                        <option key={r} value={r} className="bg-white text-gray-900">{r}</option>
                    ))}
                </select>
                <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400 text-xs">▼</div>
            </div>

            {/* Status Toggles */}
            <div className="flex gap-2 w-full md:w-auto">
                {[
                    { value: "", label: "Tutti" },
                    { value: "attivi", label: "Attivi" },
                    { value: "scaduti", label: "Scaduti" },
                ].map((btn) => (
                    <button
                        key={btn.value}
                        onClick={() => handleStatus(btn.value)}
                        className={`px-4 py-2 rounded-lg font-bold text-xs uppercase transition-all ${activeStatus === btn.value
                            ? "bg-primary/10 text-primary border border-primary/20"
                            : "bg-white text-gray-500 border border-gray-200 hover:bg-gray-50 hover:text-gray-900 shadow-sm"
                            }`}
                    >
                        {btn.label}
                    </button>
                ))}
            </div>
        </div>
    );
}
