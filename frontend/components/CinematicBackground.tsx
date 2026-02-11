"use client";

import { useEffect, useRef, useState } from "react";

export default function CinematicBackground() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [mousePos, setMousePos] = useState({ x: 0.5, y: 0.5 });

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            setMousePos({
                x: e.clientX / window.innerWidth,
                y: e.clientY / window.innerHeight,
            });
        };
        window.addEventListener("mousemove", handleMouseMove);
        return () => window.removeEventListener("mousemove", handleMouseMove);
    }, []);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        let animationId: number;
        let time = 0;

        const resize = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };

        const drawWave = (
            yOffset: number,
            amplitude: number,
            frequency: number,
            speed: number,
            color: string,
            thickness: number,
            showGloss: boolean = false
        ) => {
            // Main Soft Wave
            ctx.beginPath();
            ctx.moveTo(0, canvas.height / 2);

            for (let x = 0; x < canvas.width; x += 3) {
                const y =
                    canvas.height / 2 +
                    yOffset +
                    Math.sin(x * frequency + time * speed) * amplitude +
                    Math.sin(x * frequency * 0.5 + time * speed * 0.3) * (amplitude * 0.5);

                ctx.lineTo(x, y);
            }

            ctx.strokeStyle = color;
            ctx.lineWidth = thickness;
            ctx.lineCap = "round";
            ctx.stroke();

            // Glossary Peak (The PlayStation "Silk" Look)
            if (showGloss) {
                ctx.beginPath();
                ctx.moveTo(0, canvas.height / 2);

                for (let x = 0; x < canvas.width; x += 3) {
                    const y =
                        canvas.height / 2 +
                        yOffset +
                        Math.sin(x * frequency + time * speed) * amplitude +
                        Math.sin(x * frequency * 0.5 + time * speed * 0.3) * (amplitude * 0.5);

                    ctx.lineTo(x, y);
                }

                ctx.strokeStyle = "rgba(255, 255, 255, 0.25)"; // Pure white peak
                ctx.lineWidth = 2; // Thin glossy line
                ctx.stroke();
            }
        };

        const animate = () => {
            time += 0.003; // Even slower for elegance
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Background Light Beams (Very Subtle)
            ctx.save();
            ctx.globalCompositeOperation = "screen";
            ctx.filter = "blur(80px)";

            // Magenta Bloom 1
            ctx.beginPath();
            ctx.arc(canvas.width * 0.2 + Math.sin(time) * 100, canvas.height * 0.5, 300, 0, Math.PI * 2);
            ctx.fillStyle = "rgba(255, 46, 99, 0.03)";
            ctx.fill();

            // Blue Bloom 1
            ctx.beginPath();
            ctx.arc(canvas.width * 0.8 + Math.cos(time) * 100, canvas.height * 0.4, 400, 0, Math.PI * 2);
            ctx.fillStyle = "rgba(100, 150, 255, 0.02)";
            ctx.fill();
            ctx.restore();

            // Draw Sony-style waves with layered gloss
            ctx.filter = "blur(35px)"; // Silk-like softness

            // Base Layer: Deep Pink
            drawWave(
                Math.sin(time * 0.15) * 60,
                140,
                0.0007,
                0.8,
                "rgba(255, 46, 99, 0.12)",
                180
            );

            // Middle Layer: Vivid Magenta + Gloss
            drawWave(
                Math.cos(time * 0.2) * 40 + 20,
                100,
                0.0012,
                1.4,
                "rgba(255, 46, 99, 0.18)", // More vibrant
                100,
                true // Show glossy peak
            );

            // Top Layer: Pure Pink + Gloss (Fast but small)
            drawWave(
                Math.sin(time * 0.25) * 30 - 30,
                60,
                0.002,
                -1.2,
                "rgba(255, 46, 99, 0.1)",
                60,
                true
            );

            // Contrast Layer: Cool Blue
            drawWave(
                Math.cos(time * 0.1) * 50 - 60,
                180,
                0.0005,
                0.5,
                "rgba(100, 150, 255, 0.05)",
                200
            );

            ctx.filter = "none";
            animationId = requestAnimationFrame(animate);
        };

        resize();
        window.addEventListener("resize", resize);
        animate();

        return () => {
            window.removeEventListener("resize", resize);
            cancelAnimationFrame(animationId);
        };
    }, []);

    const parallaxX = (mousePos.x - 0.5) * 20;
    const parallaxY = (mousePos.y - 0.5) * 20;

    return (
        <>
            {/* Background Layer with Parallax - Ultra Clean Premium Finish */}
            <div
                className="fixed inset-0 -z-40 overflow-hidden bg-[#F8FAFC]"
                style={{ transform: `translate(${parallaxX}px, ${parallaxY}px) scale(1.1)` }}
            >
                {/* 
                   Cinematic Fallback: Layered Gradients to simulate depth and professional lighting.
                */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#F8FAFC] via-white to-[#F1F5F9]" />

                {/* Simulated Ambient Light from top-left */}
                <div className="absolute -top-[20%] -left-[10%] w-[100vw] h-[100vh] bg-gradient-radial from-primary/5 via-transparent to-transparent opacity-60 blur-[150px]" />

                {/* Subtle depth layer */}
                <div className="absolute bottom-[-10%] right-[-10%] w-[80vw] h-[80vh] bg-gradient-radial from-blue-400/5 via-transparent to-transparent opacity-40 blur-[120px]" />

                {/* Vertical Light Glimmer */}
                <div className="absolute inset-0 bg-[linear-gradient(90deg,transparent_0%,rgba(255,255,255,0.4)_50%,transparent_100%)] opacity-20" />
            </div>

            {/* Sony Waves Canvas - Now with glossy silk highlights */}
            <canvas
                ref={canvasRef}
                className="fixed inset-0 -z-20 pointer-events-none opacity-[0.85]"
            />

            {/* Premium Finish: Subtle Lens Dirt/Grain & Vignette */}
            <div className="fixed inset-0 -z-10 pointer-events-none">
                <div className="absolute inset-0 bg-gradient-radial from-transparent via-transparent to-slate-200/40" />
                {/* Almost invisible grain for high-end feel */}
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.02] mix-blend-overlay" />
            </div>
        </>
    );
}
