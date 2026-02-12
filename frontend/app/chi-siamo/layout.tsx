import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "Chi Siamo | AlSolved — Finanza Agevolata",
    description: "Scopri chi è AlSolved: il partner strategico che trasforma i bandi pubblici in capitale reale per la tua azienda. AI, trasparenza e risultati.",
};

export default function ChiSiamoLayout({ children }: { children: React.ReactNode }) {
    return children;
}
