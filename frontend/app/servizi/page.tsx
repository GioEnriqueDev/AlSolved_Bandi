"use client";

import CinematicBackground from "@/components/CinematicBackground";
import Navbar from "@/components/Navbar";
import Link from "next/link";
import { Search, FileText, Users, Rocket, ArrowRight, CheckCircle } from "lucide-react";

const services = [
    {
        icon: Search,
        title: "Ricerca Bandi",
        subtitle: "Monitoraggio Intelligente",
        description: "I nostri algoritmi scansionano ogni giorno 500+ fonti istituzionali: MIMIT, Invitalia, regioni, camere di commercio. Nessuna opportunità sfugge al nostro radar.",
        features: [
            "Aggiornamenti ogni 6 ore",
            "Alert personalizzati via email",
            "Filtri per settore ATECO",
        ],
        color: "primary",
    },
    {
        icon: FileText,
        title: "Analisi Requisiti",
        subtitle: "AI-Powered Extraction",
        description: "L'intelligenza artificiale legge le 50-100 pagine di documentazione del bando in 30 secondi. Estrae scadenze, budget massimi, criteri di esclusione e requisiti nascosti.",
        features: [
            "Report sintetico di 1 pagina",
            "Checklist requisiti pronta",
            "Score di compatibilità aziendale",
        ],
        color: "blue",
    },
    {
        icon: Users,
        title: "Consulenza Strategica",
        subtitle: "Expert Advisory",
        description: "Un team dedicato di consulenti certificati ti affianca dalla candidatura all'erogazione. Scriviamo noi la domanda, presentiamo noi i documenti.",
        features: [
            "Project Manager dedicato",
            "Business Plan incluso",
            "Assistenza fino all'erogazione",
        ],
        color: "emerald",
    },
    {
        icon: Rocket,
        title: "Accelerazione",
        subtitle: "Fast Track Service",
        description: "Per le aziende che non possono aspettare. Priorità massima, team dedicato, risposta garantita in 48h dalla pubblicazione del bando.",
        features: [
            "Candidatura in 5 giorni",
            "Linea diretta con consulenti",
            "Success Fee ridotto",
        ],
        color: "purple",
    },
];

const colorMap: Record<string, string> = {
    primary: "bg-primary/10 text-primary",
    blue: "bg-blue-100 text-blue-600",
    emerald: "bg-emerald-100 text-emerald-600",
    purple: "bg-purple-100 text-purple-600",
};

export default function ServiziPage() {
    return (
        <>
            <Navbar />
            <CinematicBackground />
            <main className="min-h-screen text-gray-900 pt-20">

                {/* Hero */}
                <section className="relative py-32 px-6 overflow-hidden">
                    <div className="relative z-10 max-w-4xl mx-auto text-center">
                        <h1 className="text-5xl md:text-7xl font-black tracking-tighter uppercase mb-6 text-gray-900">
                            I Nostri Servizi
                        </h1>
                        <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
                            Dalla scoperta del bando perfetto alla ricezione del bonifico.<br className="hidden md:block" />
                            <span className="text-primary font-semibold">Ti seguiamo in ogni step.</span>
                        </p>
                    </div>
                </section>

                {/* Services Grid */}
                <section className="py-24 px-6 border-t border-gray-200 bg-white/50 backdrop-blur-sm">
                    <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-8">
                        {services.map((service, index) => (
                            <div
                                key={index}
                                className="p-8 bg-white rounded-3xl border border-gray-200 hover:border-gray-300 hover:shadow-lg transition-all group shadow-sm"
                            >
                                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-6 ${colorMap[service.color]}`}>
                                    <service.icon className="w-7 h-7" />
                                </div>
                                <div className="text-xs font-bold tracking-[0.2em] text-gray-500 uppercase mb-2">{service.subtitle}</div>
                                <h3 className="text-2xl font-bold mb-4 text-gray-900">{service.title}</h3>
                                <p className="text-gray-600 leading-relaxed mb-6">{service.description}</p>
                                <ul className="space-y-3">
                                    {service.features.map((feature, i) => (
                                        <li key={i} className="flex items-center gap-3 text-sm text-gray-600">
                                            <CheckCircle className="w-4 h-4 text-primary" />
                                            {feature}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>
                </section>

                {/* CTA */}
                <section className="py-24 px-6 bg-gray-50 border-t border-gray-200">
                    <div className="max-w-3xl mx-auto text-center">
                        <h2 className="text-3xl md:text-4xl font-bold mb-6 text-gray-900">Pronto a vincere il tuo primo bando?</h2>
                        <p className="text-gray-600 text-lg mb-10">
                            Parla con un nostro consulente. La prima analisi è gratuita e senza impegno.
                        </p>
                        <Link href="/contatti">
                            <button className="px-10 py-5 bg-primary text-white rounded-full font-black text-lg uppercase tracking-widest hover:scale-105 transition-transform shadow-lg shadow-primary/20 flex items-center gap-3 mx-auto">
                                Richiedi Consulenza Gratuita <ArrowRight className="w-6 h-6" />
                            </button>
                        </Link>
                    </div>
                </section>

            </main>
        </>
    );
}
