import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "Servizi | AlSolved — Finanza Agevolata",
    description: "Ricerca bandi AI, analisi requisiti, consulenza strategica e accelerazione. AlSolved ti segue dalla scoperta del bando al bonifico.",
};

export default function ServiziLayout({ children }: { children: React.ReactNode }) {
    return children;
}
