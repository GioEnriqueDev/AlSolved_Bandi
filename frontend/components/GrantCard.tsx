"use client";

import { MapPin, Calendar, ArrowRight, Sparkles } from "lucide-react";
import { format } from "date-fns";
import { it } from "date-fns/locale";
import Link from "next/link";
import { cn } from "@/lib/utils";

interface Bando {
    id: number;
    title: string;
    source_name: string;
    status: string;
    url: string;
    ingested_at: string;
    marketing_text?: string | null;
    ai_analysis?: {
        titolo_riassuntivo?: string;
        sintesi?: string;
        scadenza?: string;
        close_date?: string;
        data_chiusura?: string;
        regions?: string[];
        regione?: string;
        financial_max?: number;
        financial_min?: number;
        ateco_codes?: string;
        is_gold?: boolean;
        is_expired?: boolean | string;
    } | null;
}

// Mapping Solr IDs to region names (same as backend)
const SOLR_ID_TO_REGION: Record<string, string> = {
    "218": "Abruzzo", "219": "Basilicata", "220": "Calabria", "221": "Campania",
    "222": "Emilia-Romagna", "223": "Friuli-Venezia Giulia", "224": "Lazio",
    "225": "Liguria", "226": "Lombardia", "227": "Marche", "228": "Molise",
    "229": "Piemonte", "230": "Puglia", "231": "Sardegna", "232": "Sicilia",
    "233": "Toscana", "234": "Trentino-Alto Adige", "235": "Umbria",
    "236": "Valle d'Aosta", "237": "Veneto", "587": "Estero",
};

function getRegionNames(regions: string[] | string | undefined): string[] {
    if (!regions) return ["Nazionale"];
    const regionList = Array.isArray(regions) ? regions : [regions];
    const names: string[] = [];
    for (const r of regionList.slice(0, 4)) {
        const rStr = String(r).trim();
        if (SOLR_ID_TO_REGION[rStr]) {
            names.push(SOLR_ID_TO_REGION[rStr]);
        } else if (!rStr.match(/^\d+$/)) {
            names.push(rStr);
        }
    }
    return names.length > 0 ? names : ["Nazionale"];
}

function formatDeadline(analysis: Bando["ai_analysis"]): string | null {
    if (!analysis) return null;
    const dateStr = analysis.scadenza || analysis.close_date || analysis.data_chiusura;
    if (!dateStr || dateStr === "N/A") return null;
    try {
        const date = new Date(dateStr);
        if (!isNaN(date.getTime())) {
            return format(date, "dd MMM yyyy", { locale: it });
        }
        return dateStr.slice(0, 10);
    } catch {
        return dateStr.slice(0, 10);
    }
}

export function GrantCard({ bando }: { bando: Bando }) {
    const analysis = bando.ai_analysis;
    const regions = getRegionNames(analysis?.regions || analysis?.regione);
    const deadline = formatDeadline(analysis);
    const hasAteco = analysis?.ateco_codes && analysis.ateco_codes.length > 0;
    const isGold = analysis?.is_gold || hasAteco;

    // Status Logic
    const isExpiredV2 = analysis?.is_expired;

    // Fallback logic
    const deadlineDate = deadline ? new Date(analysis?.scadenza || analysis?.close_date || "") : null;
    const now = new Date();

    const isExpired = isExpiredV2 === true || isExpiredV2 === "true" || (deadlineDate && !isNaN(deadlineDate.getTime())
        ? deadlineDate.getTime() < now.getTime()
        : false);

    const isExpiringSoon = !isExpired && deadlineDate && !isNaN(deadlineDate.getTime())
        ? deadlineDate.getTime() < now.getTime() + (7 * 24 * 60 * 60 * 1000)
        : false;

    return (
        <div className={cn(
            "group relative overflow-hidden rounded-3xl border border-gray-200 backdrop-blur-md transition-all duration-300 flex flex-col h-full",
            isExpired
                ? "bg-gray-50 border-gray-200 opacity-60 hover:opacity-100 grayscale hover:grayscale-0"
                : "bg-white hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5 text-gray-900"
        )}>
            {/* Background Glow Effect - Light */}
            <div className="absolute inset-0 bg-gradient-to-b from-transparent to-gray-50/50 pointer-events-none" />

            {/* Content Container */}
            <div className="p-6 relative z-10 flex flex-col h-full">

                {/* Header: Title & Badges */}
                <div className="mb-4">
                    <div className="flex flex-wrap justify-between items-start gap-2 mb-2">
                        <div className="flex gap-2">
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-gray-100 text-gray-500 border border-gray-200">
                                {bando.source_name}
                            </span>

                            {/* Status Badge */}
                            {isExpired ? (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-red-50 text-red-500 border border-red-100">
                                    Scaduto
                                </span>
                            ) : isExpiringSoon ? (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-yellow-50 text-yellow-600 border border-yellow-100 animate-pulse">
                                    In Scadenza
                                </span>
                            ) : (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-emerald-50 text-emerald-600 border border-emerald-100">
                                    Attivo
                                </span>
                            )}
                        </div>

                        {isGold && (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-amber-50 text-amber-500 border border-amber-100 shadow-sm">
                                <Sparkles className="w-3 h-3" /> Gold
                            </span>
                        )}
                    </div>

                    <h3 className={cn(
                        "text-xl font-bold leading-tight line-clamp-2 transition-colors",
                        isExpired ? "text-gray-400" : "text-gray-900 group-hover:text-primary"
                    )}>
                        {analysis?.titolo_riassuntivo || bando.title}
                    </h3>
                </div>

                {/* Geographic Areas */}
                <div className="mb-4">
                    <div className="flex items-center gap-2 text-xs text-gray-500 mb-2 uppercase tracking-wide font-bold">
                        <MapPin className="w-3 h-3" />
                        <span>Aree geografiche</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {regions.map((region, idx) => (
                            <span
                                key={idx}
                                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600 border border-gray-200 hover:bg-gray-200 transition-colors"
                            >
                                {region}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Marketing Text / Description */}
                <div className="mb-6 flex-grow">
                    {bando.marketing_text ? (
                        <div className={cn(
                            "p-3 rounded-xl border-l-2",
                            isExpired ? "bg-gray-50 border-gray-300" : "bg-primary/5 border-primary/50"
                        )}>
                            <p className="text-sm text-gray-600 font-medium leading-relaxed line-clamp-3">
                                {bando.marketing_text}
                            </p>
                        </div>
                    ) : (
                        <p className="text-sm text-gray-500 line-clamp-3 leading-relaxed">
                            {analysis?.sintesi || "Analisi dettagliata in corso..."}
                        </p>
                    )}
                </div>

                {/* Footer: Deadline + Button */}
                <div className="pt-4 border-t border-gray-100 mt-auto">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                            <Calendar className="w-4 h-4 text-primary" />
                            <span className="text-xs font-bold uppercase tracking-wide">Scadenza:</span>
                        </div>
                        <span className={cn(
                            "text-sm font-bold",
                            isExpired ? "text-red-500" : "text-gray-900"
                        )}>
                            {deadline || "N/A"}
                        </span>
                    </div>

                    <Link
                        href={`/catalogo/${bando.id}`}
                        className={cn(
                            "w-full flex items-center justify-center gap-2 px-6 py-3 font-bold rounded-xl transition-all duration-300 uppercase tracking-wider text-sm",
                            isExpired
                                ? "bg-gray-100 text-gray-400 cursor-not-allowed hover:bg-gray-200"
                                : "bg-primary hover:bg-primary/90 text-white shadow-md hover:shadow-lg shadow-primary/30"
                        )}
                    >
                        {isExpired ? "Visualizza Archivio" : "Visualizza Bando"}
                        <ArrowRight className="w-4 h-4" />
                    </Link>
                </div>
            </div>
        </div>
    );
}
