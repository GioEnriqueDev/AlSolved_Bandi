"use client";

import CinematicBackground from "@/components/CinematicBackground";
import Navbar from "@/components/Navbar";
import { Users, Award, TrendingUp, Shield } from "lucide-react";

export default function ChiSiamoPage() {
    return (
        <>
            <Navbar />
            <CinematicBackground />
            <main className="min-h-screen text-gray-900 pt-20">

                {/* Hero */}
                <section className="relative py-32 px-6 overflow-hidden">
                    <div className="relative z-10 max-w-4xl mx-auto text-center">
                        <h1 className="text-5xl md:text-7xl font-black tracking-tighter uppercase mb-6 text-gray-900">
                            Chi Siamo
                        </h1>
                        <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
                            Non siamo broker. Non siamo intermediari. <br className="hidden md:block" />
                            Siamo il <span className="text-primary font-bold">partner strategico</span> che trasforma i bandi pubblici in capitale reale per la tua azienda.
                        </p>
                    </div>
                </section>

                {/* Mission */}
                <section className="py-24 px-6 bg-white border-t border-gray-200 shadow-sm">
                    <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-16 items-center">
                        <div>
                            <h2 className="text-3xl md:text-4xl font-bold mb-6 text-gray-900">
                                La Missione
                            </h2>
                            <p className="text-gray-600 text-lg leading-relaxed mb-6">
                                In Italia si <span className="text-primary font-bold">perdono miliardi di euro</span> ogni anno perché le aziende non conoscono, non capiscono, o non riescono ad accedere ai bandi pubblici.
                            </p>
                            <p className="text-gray-600 text-lg leading-relaxed">
                                AlSolved esiste per <span className="text-primary font-semibold">colmare questo gap</span>. Utilizziamo tecnologia proprietaria basata su AI per scansionare, analizzare e matchare le opportunità di finanziamento con le aziende che possono davvero vincerle.
                            </p>
                        </div>
                        <div className="grid grid-cols-2 gap-6">
                            <div className="p-6 bg-gray-50 rounded-2xl border border-gray-200 text-center">
                                <div className="text-4xl font-black text-primary mb-2">500+</div>
                                <div className="text-sm text-gray-500 uppercase tracking-wide">Fonti Monitorate</div>
                            </div>
                            <div className="p-6 bg-gray-50 rounded-2xl border border-gray-200 text-center">
                                <div className="text-4xl font-black text-primary mb-2">24/7</div>
                                <div className="text-sm text-gray-500 uppercase tracking-wide">Monitoraggio Attivo</div>
                            </div>
                            <div className="p-6 bg-gray-50 rounded-2xl border border-gray-200 text-center">
                                <div className="text-4xl font-black text-primary mb-2">30s</div>
                                <div className="text-sm text-gray-500 uppercase tracking-wide">Tempo Analisi AI</div>
                            </div>
                            <div className="p-6 bg-gray-50 rounded-2xl border border-gray-200 text-center">
                                <div className="text-4xl font-black text-primary mb-2">98%</div>
                                <div className="text-sm text-gray-500 uppercase tracking-wide">Accuracy Estrattiva</div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Values */}
                <section className="py-24 px-6 border-t border-gray-200 bg-gray-50">
                    <div className="max-w-6xl mx-auto">
                        <h2 className="text-3xl md:text-4xl font-bold mb-16 text-center text-gray-900">I Nostri Valori</h2>
                        <div className="grid md:grid-cols-4 gap-8">
                            <div className="text-center group">
                                <div className="w-16 h-16 bg-primary/10 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:bg-primary/20 transition-colors">
                                    <Shield className="w-8 h-8 text-primary" />
                                </div>
                                <h3 className="font-bold text-lg mb-2 text-gray-900">Trasparenza</h3>
                                <p className="text-gray-500 text-sm">Zero costi nascosti. Sai sempre cosa paghi e perché.</p>
                            </div>
                            <div className="text-center group">
                                <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:bg-blue-200 transition-colors">
                                    <TrendingUp className="w-8 h-8 text-blue-600" />
                                </div>
                                <h3 className="font-bold text-lg mb-2 text-gray-900">Risultati</h3>
                                <p className="text-gray-500 text-sm">Paghiamo sulle performance. Se non vinci, non ci devi nulla.</p>
                            </div>
                            <div className="text-center group">
                                <div className="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:bg-emerald-200 transition-colors">
                                    <Award className="w-8 h-8 text-emerald-600" />
                                </div>
                                <h3 className="font-bold text-lg mb-2 text-gray-900">Eccellenza</h3>
                                <p className="text-gray-500 text-sm">Team di esperti certificati con 10+ anni di esperienza.</p>
                            </div>
                            <div className="text-center group">
                                <div className="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:bg-purple-200 transition-colors">
                                    <Users className="w-8 h-8 text-purple-600" />
                                </div>
                                <h3 className="font-bold text-lg mb-2 text-gray-900">Partnership</h3>
                                <p className="text-gray-500 text-sm">Non sei un cliente. Sei un partner a lungo termine.</p>
                            </div>
                        </div>
                    </div>
                </section>

            </main>
        </>
    );
}
