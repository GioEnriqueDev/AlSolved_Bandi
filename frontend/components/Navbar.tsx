"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import NeonLogo from "@/components/ui/NeonLogo";
import { Menu, X } from "lucide-react";
import { useState, useEffect } from "react";

const navLinks = [
    { href: "/", label: "Home" },
    { href: "/chi-siamo", label: "Chi Siamo" },
    { href: "/servizi", label: "Servizi" },
    { href: "/catalogo", label: "Bandi" },
];

export default function Navbar() {
    const pathname = usePathname();
    const [isScrolled, setIsScrolled] = useState(false);
    const [mobileOpen, setMobileOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => setIsScrolled(window.scrollY > 50);
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    return (
        <header
            className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${isScrolled ? "bg-white/90 backdrop-blur-xl border-b border-gray-200 shadow-sm" : "bg-transparent"
                }`}
        >
            <nav className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                {/* Logo */}
                <Link href="/">
                    <NeonLogo size="sm" />
                </Link>

                {/* Desktop Nav */}
                <div className="hidden md:flex items-center gap-8">
                    {navLinks.map((link) => (
                        <Link
                            key={link.href}
                            href={link.href}
                            className={`text-sm font-bold uppercase tracking-[0.15em] transition-colors hover:text-primary ${pathname === link.href ? "text-primary" : "text-gray-600 hover:text-gray-900"
                                }`}
                        >
                            {link.label}
                        </Link>
                    ))}
                    <Link href="/contatti">
                        <button className="px-6 py-2.5 bg-primary text-white rounded-full font-bold text-sm uppercase tracking-wider hover:bg-primary/90 transition-colors shadow-[0_0_20px_-5px_var(--primary)]">
                            Richiedi Consulenza
                        </button>
                    </Link>
                </div>

                {/* Mobile Toggle */}
                <button
                    className="md:hidden text-gray-900"
                    onClick={() => setMobileOpen(!mobileOpen)}
                >
                    {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                </button>
            </nav>

            {/* Mobile Menu */}
            {mobileOpen && (
                <div className="md:hidden bg-white/95 backdrop-blur-xl border-t border-gray-200 px-6 py-8 flex flex-col gap-6 shadow-xl">
                    {navLinks.map((link) => (
                        <Link
                            key={link.href}
                            href={link.href}
                            onClick={() => setMobileOpen(false)}
                            className={`text-lg font-bold uppercase tracking-[0.1em] ${pathname === link.href ? "text-primary" : "text-gray-700 hover:text-black"
                                }`}
                        >
                            {link.label}
                        </Link>
                    ))}
                    <Link href="/contatti" onClick={() => setMobileOpen(false)}>
                        <button className="w-full px-6 py-3 bg-primary text-white rounded-full font-bold text-sm uppercase tracking-wider">
                            Richiedi Consulenza
                        </button>
                    </Link>
                </div>
            )}
        </header>
    );
}
