"use client";

import { useState } from "react";
import Link from "next/link";
import {
    ArrowLeft, MapPin, Calendar, Euro, Phone, ExternalLink,
    CheckCircle, FileText, Shield, Users, ChevronDown, ChevronUp,
    Sparkles, Cpu
} from "lucide-react";
import Navbar from "@/components/Navbar";

interface Bando {
    id: number;
    title: string;
    source_name: string;
    status: string;
    url: string;
    ingested_at: string;
    raw_content?: string;
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

// Mapping Solr IDs to region names (same as in GrantCard/Main)
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
    return regionList.map(r => SOLR_ID_TO_REGION[String(r)] || r).filter(Boolean);
}

export default function BandoDetailClient({ bando }: { bando: Bando }) {
    const [showTechnical, setShowTechnical] = useState(false);

    if (!bando) return null;

    const analysis = bando.ai_analysis || {};
    // Safely access properties with optional chaining in case analysis is partial
    const regions = getRegionNames(analysis.regions || analysis.regione);
    const hasAteco = analysis.ateco_codes && analysis.ateco_codes.length > 0;

    // Email CTA
    const consultEmail = "consulenza@alsolved.com";
    const emailSubject = encodeURIComponent(`Richiesta Consulenza: ${bando.title}`);
    const emailBody = encodeURIComponent(
        `Buongiorno,\n\nSono interessato al bando "${bando.title}" (ID: ${bando.id}).\n\nVorrei richiedere una consulenza per verificare i requisiti e l'iter di partecipazione.\n\nGrazie.`
    );

    return (
        <>
            <Navbar />
            <main className="min-h-screen bg-slate-50 text-gray-900 selection:bg-primary/20 pt-24 overflow-x-hidden">

                {/* Background Ambient Light */}
                <div className="fixed top-0 left-0 w-full h-[500px] bg-gradient-to-b from-white to-transparent pointer-events-none opacity-80" />

                {/* Navigation */}
                <div className="max-w-6xl mx-auto px-4 py-6 relative z-10">
                    <Link
                        href="/catalogo"
                        className="inline-flex items-center gap-2 text-gray-500 hover:text-primary transition-colors group font-medium"
                    >
                        <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                        Torna al Catalogo
                    </Link>
                </div>

                {/* Hero Section */}
                <section className="relative z-10">
                    <div className="max-w-6xl mx-auto px-4 pb-12">
                        {/* Badges */}
                        <div className="flex flex-wrap items-center gap-3 mb-6">
                            <span className="px-3 py-1 bg-gray-100 border border-gray-200 text-gray-600 text-xs font-bold uppercase tracking-wider rounded-full backdrop-blur-md">
                                {bando.source_name}
                            </span>
                            {hasAteco && (
                                <span className="px-3 py-1 bg-amber-50 border border-amber-100 text-amber-600 text-xs font-bold uppercase tracking-wider rounded-full flex items-center gap-1 shadow-sm">
                                    <Sparkles className="w-3 h-3" /> Certificato ATECO
                                </span>
                            )}
                        </div>

                        {/* Title */}
                        <h1 className="text-4xl md:text-5xl lg:text-6xl font-black text-gray-900 mb-8 leading-tight tracking-tight">
                            {analysis.titolo_riassuntivo || bando.title}
                        </h1>

                        {/* Layout: Main Content + Sidebar */}
                        <div className="grid lg:grid-cols-3 gap-8">

                            {/* Left: Main Content */}
                            <div className="lg:col-span-2 space-y-8">

                                {/* Marketing Text Box */}
                                {bando.marketing_text && (
                                    <div className="p-6 md:p-8 rounded-3xl bg-white border border-primary/20 shadow-lg shadow-primary/5 relative overflow-hidden group">
                                        <div className="absolute inset-0 bg-primary/5 opacity-50 group-hover:opacity-100 transition-opacity duration-500" />
                                        <div className="flex gap-4 relative z-10">
                                            <div className="p-3 bg-primary/10 rounded-full h-fit text-primary">
                                                <Cpu className="w-6 h-6 animate-pulse-slow" />
                                            </div>
                                            <div>
                                                <h3 className="text-primary font-bold uppercase tracking-wider text-sm mb-2">Analisi AlSolved</h3>
                                                <p className="text-xl md:text-2xl font-bold text-gray-800 leading-relaxed">
                                                    {bando.marketing_text}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Key Data Grid */}
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    {/* Regions */}
                                    <div className="p-5 rounded-2xl bg-white border border-gray-200 shadow-sm">
                                        <div className="flex items-center gap-2 text-gray-500 mb-3 text-xs font-bold uppercase tracking-wider">
                                            <MapPin className="w-4 h-4" /> Aree Geografiche
                                        </div>
                                        <div className="flex flex-wrap gap-2">
                                            {regions.slice(0, 3).map((r, i) => (
                                                <span key={i} className="px-2.5 py-1 bg-gray-100 rounded-lg text-sm text-gray-700 border border-gray-200">
                                                    {r}
                                                </span>
                                            ))}
                                            {regions.length > 3 && <span className="text-xs text-gray-400 self-center">+{regions.length - 3}</span>}
                                        </div>
                                    </div>

                                    {/* Financial */}
                                    <div className="p-5 rounded-2xl bg-white border border-gray-200 shadow-sm">
                                        <div className="flex items-center gap-2 text-gray-500 mb-3 text-xs font-bold uppercase tracking-wider">
                                            <Euro className="w-4 h-4" /> Agevolazione Max
                                        </div>
                                        <p className="text-xl font-bold text-emerald-600 drop-shadow-sm">
                                            {analysis.financial_max
                                                ? `€${(analysis.financial_max / 1000).toLocaleString('it-IT')}K`
                                                : "N/D"}
                                        </p>
                                    </div>

                                    {/* Deadline */}
                                    <div className="p-5 rounded-2xl bg-white border border-gray-200 shadow-sm">
                                        <div className="flex items-center gap-2 text-gray-500 mb-3 text-xs font-bold uppercase tracking-wider">
                                            <Calendar className="w-4 h-4" /> Scadenza
                                        </div>
                                        <p className="text-xl font-bold text-gray-900">
                                            {analysis.scadenza || analysis.close_date || "In fase di definizione"}
                                        </p>
                                    </div>
                                </div>

                                {/* Why Choose Us Detail */}
                                <div className="p-8 rounded-3xl bg-white border border-gray-200 shadow-sm">
                                    <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                                        <Shield className="w-6 h-6 text-primary" />
                                        La Garanzia AlSolved
                                    </h3>
                                    <div className="grid md:grid-cols-3 gap-6">
                                        {[
                                            { icon: FileText, title: "Pre-Fattibilità", desc: "Analisi gratuita requisiti in 24h" },
                                            { icon: CheckCircle, title: "Zero Errori", desc: "Software proprietario di controllo" },
                                            { icon: Users, title: "Supporto Totale", desc: "Dalla domanda alla rendicontazione" }
                                        ].map((item, i) => (
                                            <div key={i} className="text-center p-4 rounded-xl bg-gray-50 border border-gray-100 hover:border-primary/30 transition-colors">
                                                <item.icon className="w-8 h-8 mx-auto mb-3 text-primary opacity-80" />
                                                <h4 className="font-bold text-gray-900 mb-1">{item.title}</h4>
                                                <p className="text-xs text-gray-500">{item.desc}</p>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="mt-6 p-4 rounded-xl bg-primary/5 border border-primary/20 text-center">
                                        <p className="text-primary font-bold tracking-wide">
                                            🎯 Tasso di successo del 98% sulle pratiche presentate
                                        </p>
                                    </div>
                                </div>

                            </div>

                            {/* Right: Sticky Sidebar (Technical & CTA) */}
                            <div className="space-y-6">

                                {/* Sticky CTA Box */}
                                <div className="sticky top-24 space-y-6">

                                    <div className="p-6 rounded-3xl bg-white border border-gray-200 shadow-xl shadow-black/5">
                                        <h3 className="text-lg font-bold text-gray-900 mb-2">Interessato al Bando?</h3>
                                        <p className="text-sm text-gray-500 mb-6">Non perdere l'opportunità. Prenota una consulenza tecnica con i nostri esperti.</p>

                                        <a
                                            href={`mailto:${consultEmail}?subject=${emailSubject}&body=${emailBody}`}
                                            className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-primary hover:bg-primary/90 text-white font-bold rounded-xl transition-all duration-300 shadow-lg shadow-primary/30 hover:shadow-xl hover:shadow-primary/40 uppercase tracking-wider text-sm group"
                                        >
                                            <Phone className="w-4 h-4 group-hover:rotate-12 transition-transform" />
                                            Richiedi Consulenza
                                        </a>
                                    </div>

                                    {/* Technical Accordion */}
                                    <div className="rounded-2xl border border-gray-200 bg-white overflow-hidden shadow-sm">
                                        <button
                                            onClick={() => setShowTechnical(!showTechnical)}
                                            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
                                        >
                                            <span className="font-bold text-gray-500 text-sm uppercase tracking-wider">
                                                Dettagli Tecnici / Raw
                                            </span>
                                            {showTechnical ? (
                                                <ChevronUp className="w-4 h-4 text-gray-400" />
                                            ) : (
                                                <ChevronDown className="w-4 h-4 text-gray-400" />
                                            )}
                                        </button>

                                        {showTechnical && (
                                            <div className="p-4 border-t border-gray-100 bg-gray-50">
                                                <div className="prose prose-sm max-w-none text-gray-600">
                                                    {analysis.sintesi && <p className="mb-4">{analysis.sintesi}</p>}
                                                    {bando.raw_content && (
                                                        <div
                                                            className="max-h-60 overflow-y-auto text-xs font-mono bg-white p-2 rounded border border-gray-200"
                                                            dangerouslySetInnerHTML={{ __html: bando.raw_content }}
                                                        />
                                                    )}
                                                </div>
                                                <a
                                                    href={bando.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="mt-4 flex items-center gap-2 text-primary hover:underline text-xs"
                                                >
                                                    <ExternalLink className="w-3 h-3" />
                                                    Fonte Ufficiale
                                                </a>
                                            </div>
                                        )}
                                    </div>
                                </div>

                            </div>
                        </div>
                    </div>
                </section>

                {/* Mobile Floating CTA (only visible on small screens) */}
                <div className="lg:hidden fixed bottom-0 left-0 w-full p-4 bg-white/90 backdrop-blur-xl border-t border-gray-200 z-50">
                    <a
                        href={`mailto:${consultEmail}?subject=${emailSubject}&body=${emailBody}`}
                        className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-primary text-white font-bold rounded-xl shadow-lg shadow-primary/30 text-sm uppercase"
                    >
                        Richiedi Consulenza
                    </a>
                </div>

            </main>
        </>
    );
}
