import { notFound } from "next/navigation";
import BandoDetailClient from "@/components/BandoDetailClient";
import path from "path";
import fs from "fs";

// Helper to read bandi from JSON file at build time
async function getBandi() {
    const filePath = path.join(process.cwd(), "public", "bandi.json");
    try {
        const fileContents = fs.readFileSync(filePath, "utf8");
        return JSON.parse(fileContents);
    } catch (error) {
        console.error("Error reading bandi.json:", error);
        return [];
    }
}

export async function generateStaticParams() {
    const bandi = await getBandi();

    return bandi.map((bando: any) => ({
        id: bando.id.toString(),
    }));
}

export default async function BandoPage({ params }: { params: { id: string } }) {
    const bandi = await getBandi();
    const bando = bandi.find((b: any) => b.id.toString() === params.id);

    if (!bando) {
        notFound();
    }

    return <BandoDetailClient bando={bando} />;
}
