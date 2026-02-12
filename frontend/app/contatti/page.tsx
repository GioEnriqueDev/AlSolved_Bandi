"use client";

import CinematicBackground from "@/components/CinematicBackground";
import Navbar from "@/components/Navbar";
import { Mail, Phone, MapPin, Send, CheckCircle } from "lucide-react";
import { useState, type FormEvent } from "react";

export default function ContattiPage() {
    const [formData, setFormData] = useState({
        azienda: "",
        email: "",
        settore: "",
        messaggio: "",
    });
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();

        const subject = encodeURIComponent(`Richiesta consulenza da ${formData.azienda || "Nuovo contatto"}`);
        const body = encodeURIComponent(
            `Azienda: ${formData.azienda}\nEmail: ${formData.email}\nSettore: ${formData.settore || "Non specificato"}\n\nMessaggio:\n${formData.messaggio}`
        );

        window.location.href = `mailto:info@alsolved.it?subject=${subject}&body=${body}`;
        setSubmitted(true);
    };

    return (
        <>
            <Navbar />
            <CinematicBackground />
            <main className="min-h-screen text-gray-900 pt-20">

                {/* Hero */}
                <section className="relative py-32 px-6 overflow-hidden">
                    <div className="relative z-10 max-w-4xl mx-auto text-center">
                        <h1 className="text-5xl md:text-7xl font-black tracking-tighter uppercase mb-6 text-gray-900">
                            Contattaci
                        </h1>
                        <p className="text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
                            Hai un progetto in mente? Un bando che ti interessa?<br className="hidden md:block" />
                            <span className="text-primary font-semibold">Parliamone.</span> La prima consulenza è gratuita.
                        </p>
                    </div>
                </section>

                {/* Contact Form + Info */}
                <section className="py-24 px-6 border-t border-gray-200 bg-white/50 backdrop-blur-sm">
                    <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-16">

                        {/* Form */}
                        <div>
                            <h2 className="text-2xl font-bold mb-6 text-gray-900">Richiedi una Consulenza</h2>

                            {submitted ? (
                                <div className="p-8 rounded-2xl bg-emerald-50 border border-emerald-200 text-center">
                                    <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
                                    <h3 className="text-xl font-bold text-emerald-800 mb-2">Richiesta Inviata!</h3>
                                    <p className="text-emerald-600">Il tuo client email dovrebbe aprirsi con tutti i dettagli compilati. Rispondiamo entro 24 ore.</p>
                                    <button
                                        onClick={() => setSubmitted(false)}
                                        className="mt-4 text-sm text-emerald-600 underline hover:text-emerald-800"
                                    >
                                        Invia un&apos;altra richiesta
                                    </button>
                                </div>
                            ) : (
                                <form className="space-y-6" onSubmit={handleSubmit}>
                                    <div>
                                        <label className="block text-sm font-bold text-gray-600 mb-2">Nome Azienda *</label>
                                        <input
                                            type="text"
                                            placeholder="Es. Rossi S.r.l."
                                            required
                                            value={formData.azienda}
                                            onChange={(e) => setFormData({ ...formData, azienda: e.target.value })}
                                            className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:border-primary focus:outline-none transition-colors shadow-sm"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-bold text-gray-600 mb-2">Email *</label>
                                        <input
                                            type="email"
                                            placeholder="mario@rossi.it"
                                            required
                                            value={formData.email}
                                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                            className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:border-primary focus:outline-none transition-colors shadow-sm"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-bold text-gray-600 mb-2">Settore</label>
                                        <select
                                            className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 focus:border-primary focus:outline-none transition-colors shadow-sm"
                                            value={formData.settore}
                                            onChange={(e) => setFormData({ ...formData, settore: e.target.value })}
                                        >
                                            <option value="">Seleziona settore...</option>
                                            <option value="manifattura">Manifattura</option>
                                            <option value="agricoltura">Agricoltura</option>
                                            <option value="digitale">Digitale/IT</option>
                                            <option value="energia">Energia/Green</option>
                                            <option value="commercio">Commercio</option>
                                            <option value="altro">Altro</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-bold text-gray-600 mb-2">Messaggio</label>
                                        <textarea
                                            rows={4}
                                            placeholder="Descrivi brevemente la tua esigenza o il bando che ti interessa..."
                                            value={formData.messaggio}
                                            onChange={(e) => setFormData({ ...formData, messaggio: e.target.value })}
                                            className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:border-primary focus:outline-none transition-colors resize-none shadow-sm"
                                        />
                                    </div>
                                    <button
                                        type="submit"
                                        className="w-full px-8 py-4 bg-primary text-white rounded-full font-bold uppercase tracking-wider hover:bg-primary/90 transition-colors flex items-center justify-center gap-3 shadow-lg shadow-primary/20"
                                    >
                                        Invia Richiesta <Send className="w-5 h-5" />
                                    </button>
                                </form>
                            )}
                        </div>

                        {/* Contact Info */}
                        <div>
                            <h2 className="text-2xl font-bold mb-6 text-gray-900">Informazioni di Contatto</h2>
                            <div className="space-y-6">
                                <div className="flex items-start gap-4">
                                    <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center shrink-0">
                                        <Mail className="w-5 h-5 text-primary" />
                                    </div>
                                    <div>
                                        <div className="font-bold mb-1 text-gray-900">Email</div>
                                        <a href="mailto:info@alsolved.it" className="text-gray-600 hover:text-primary transition-colors">
                                            info@alsolved.it
                                        </a>
                                    </div>
                                </div>
                                <div className="flex items-start gap-4">
                                    <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center shrink-0">
                                        <Phone className="w-5 h-5 text-blue-600" />
                                    </div>
                                    <div>
                                        <div className="font-bold mb-1 text-gray-900">Telefono</div>
                                        <a href="tel:+390123456789" className="text-gray-600 hover:text-primary transition-colors">
                                            +39 012 345 6789
                                        </a>
                                    </div>
                                </div>
                                <div className="flex items-start gap-4">
                                    <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center shrink-0">
                                        <MapPin className="w-5 h-5 text-emerald-600" />
                                    </div>
                                    <div>
                                        <div className="font-bold mb-1 text-gray-900">Sede Operativa</div>
                                        <p className="text-gray-600">
                                            Milano, Italia<br />
                                            Operativi su tutto il territorio nazionale
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div className="mt-12 p-6 bg-white border border-gray-200 rounded-2xl shadow-sm">
                                <div className="text-sm font-bold text-gray-500 uppercase tracking-wide mb-2">Orari</div>
                                <p className="text-gray-900 font-medium">Lun - Ven: 9:00 - 18:00</p>
                                <p className="text-gray-500 text-sm mt-2">Rispondiamo entro 24 ore lavorative</p>
                            </div>
                        </div>

                    </div>
                </section>

            </main>
        </>
    );
}
