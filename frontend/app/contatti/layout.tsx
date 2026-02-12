import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "Contatti | AlSolved — Richiedi Consulenza Gratuita",
    description: "Contatta AlSolved per una consulenza gratuita sulla finanza agevolata. Rispondiamo in 24 ore. Milano, Italia.",
};

export default function ContattiLayout({ children }: { children: React.ReactNode }) {
    return children;
}
