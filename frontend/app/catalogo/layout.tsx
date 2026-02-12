import type { Metadata } from "next";

export const metadata: Metadata = {
    title: "Catalogo Bandi | AlSolved — Database Finanza Agevolata",
    description: "Esplora il catalogo completo dei bandi pubblici italiani. Filtra per regione, stato e parole chiave. Aggiornato in tempo reale da AlSolved.",
};

export default function CatalogoLayout({ children }: { children: React.ReactNode }) {
    return children;
}
