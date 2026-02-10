"use client";

import Link from "next/link";
import NeonLogo from "@/components/ui/NeonLogo";
import CinematicBackground from "@/components/CinematicBackground";
import Navbar from "@/components/Navbar";
import { ArrowRight } from "lucide-react";

export default function LandingPage() {
    return (
        <>
            <Navbar />
            <main className="min-h-screen text-foreground overflow-x-hidden selection:bg-primary/20 selection:text-black">

                {/* --- HERO SECTION (Cinematic - Light) --- */}
                <section className="relative h-screen flex flex-col items-center justify-center text-center px-4 overflow-hidden">

                    {/* Cinematic Background Component (Updated for Light Theme) */}
                    <CinematicBackground />

                    <div className="relative z-10 flex flex-col items-center gap-8">
                        <NeonLogo size="lg" className="scale-150 mb-4" />

                        <h1 className="text-6xl md:text-8xl font-black tracking-tighter uppercase leading-[0.9] max-w-5xl drop-shadow-sm text-gray-900">
                            Il Futuro della <br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-gray-900 via-gray-700 to-gray-500">Finanza Agevolata</span>
                        </h1>

                        <p className="text-xl md:text-2xl text-gray-600 max-w-3xl font-medium tracking-wide leading-relaxed">
                            La piattaforma B2B che trasforma i bandi in opportunità concrete. <br className="hidden md:block" />
                            Dati istituzionali, precisione chirurgica, zero burocrazia.
                        </p>

                        <div className="flex flex-col sm:flex-row gap-6 mt-8">
                            <Link href="/catalogo">
                                <button className="px-10 py-5 bg-gray-900 text-white rounded-full font-black text-lg uppercase tracking-widest hover:scale-105 transition-transform shadow-lg shadow-gray-900/20 flex items-center gap-3">
                                    Esplora Bandi <ArrowRight className="w-6 h-6" />
                                </button>
                            </Link>
                            <button className="px-10 py-5 rounded-full font-bold text-lg uppercase tracking-widest border border-gray-300 hover:bg-gray-50 hover:border-gray-400 transition-all text-gray-600">
                                Soluzioni Enterprise
                            </button>
                        </div>
                    </div>
                </section>

                {/* --- THE METHOD (Rockstar Grid - Light) --- */}
                <section className="py-32 bg-white border-t border-gray-100 relative z-10">
                    <div className="max-w-7xl mx-auto px-6">
                        <div className="grid md:grid-cols-3 gap-0 border border-gray-200 bg-gray-50 divide-y md:divide-y-0 md:divide-x divide-gray-200 rounded-3xl overflow-hidden shadow-sm">

                            {/* Metric 1 */}
                            <div className="p-12 hover:bg-white transition-colors group cursor-default">
                                <h3 className="text-sm font-bold tracking-[0.2em] text-gray-400 uppercase mb-4">Coverage</h3>
                                <div className="text-5xl font-black text-gray-900 mb-2 group-hover:text-primary transition-colors">100%</div>
                                <p className="text-gray-500 font-medium">Fonti Nazionali & Regionali scansionate in tempo reale.</p>
                            </div>

                            {/* Metric 2 */}
                            <div className="p-12 hover:bg-white transition-colors group cursor-default">
                                <h3 className="text-sm font-bold tracking-[0.2em] text-gray-400 uppercase mb-4">Precision</h3>
                                <div className="text-5xl font-black text-gray-900 mb-2 group-hover:text-primary transition-colors">&gt; 98%</div>
                                <p className="text-gray-500 font-medium">Accuracy nell'estrazione dei requisiti tramite Llama 3.</p>
                            </div>

                            {/* Metric 3 */}
                            <div className="p-12 hover:bg-white transition-colors group cursor-default">
                                <h3 className="text-sm font-bold tracking-[0.2em] text-gray-400 uppercase mb-4">Compliance</h3>
                                <div className="text-5xl font-black text-gray-900 mb-2 group-hover:text-primary transition-colors">ISO</div>
                                <p className="text-gray-500 font-medium">Processi auditabili e reportistica Enterprise-ready.</p>
                            </div>

                        </div>
                    </div>
                </section>

                {/* --- LIVE FEED PREVIEW --- */}
                <section className="py-24 flex flex-col items-center bg-gradient-to-b from-white to-gray-50 border-b border-gray-200">
                    <h2 className="text-4xl md:text-5xl font-black tracking-tighter mb-12 uppercase text-gray-900">Opportunità in Evidenza</h2>
                    <Link href="/catalogo" className="group flex items-center gap-3 text-primary font-bold tracking-[0.2em] uppercase hover:text-gray-900 transition-colors text-lg">
                        Accesso al Database <ArrowRight className="w-5 h-5 group-hover:translate-x-2 transition-transform" />
                    </Link>
                </section>

            </main>
        </>
    );
}
