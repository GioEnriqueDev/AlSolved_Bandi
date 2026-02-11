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
            thickness: number
        ) => {
            ctx.beginPath();
            ctx.moveTo(0, canvas.height / 2);

            for (let x = 0; x < canvas.width; x += 2) {
                // Multi-layered sine wave for organic feel
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
        };

        const animate = () => {
            time += 0.005; // Very slow and cinematic
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Add subtle blur to the waves
            ctx.filter = "blur(40px)";

            // Draw multiple overlapping Sony-style waves
            // Wave 1: Main Magenta
            drawWave(
                Math.sin(time * 0.2) * 50,
                100,
                0.001,
                1,
                "rgba(255, 46, 99, 0.15)", // Brighter Magenta
                120
            );

            // Wave 2: Subtle Blue/Dark contrast
            drawWave(
                Math.cos(time * 0.3) * 30 + 50,
                80,
                0.0015,
                -0.8,
                "rgba(100, 150, 255, 0.08)",
                100
            );

            // Wave 3: Deep Magenta
            drawWave(
                Math.sin(time * 0.1) * 40 - 50,
                120,
                0.0008,
                1.2,
                "rgba(255, 46, 99, 0.1)",
                150
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
            {/* Background Layer with Parallax */}
            <div
                className="fixed inset-0 -z-40 overflow-hidden bg-[#F8FAFC]"
                style={{ transform: `translate(${parallaxX}px, ${parallaxY}px) scale(1.05)` }}
            >
                {/* 
                   Using a CSS gradient as a high-quality fallback for the cinematic image.
                   It creates a professional, clean tech look.
                */}
                <div className="absolute inset-0 bg-gradient-to-br from-[#F8FAFC] via-white to-[#F1F5F9]" />

                {/* Abstract light beam */}
                <div className="absolute top-[-10%] left-[-10%] w-[60%] h-[60%] bg-magenta/5 blur-[120px] rounded-full animate-pulse-slow" />
            </div>

            {/* Sony Waves Canvas */}
            <canvas
                ref={canvasRef}
                className="fixed inset-0 -z-20 pointer-events-none opacity-80"
            />

            {/* Vignette & Grain */}
            <div className="fixed inset-0 -z-10 pointer-events-none">
                <div className="absolute inset-0 bg-gradient-radial from-transparent via-transparent to-slate-200/30" />
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.03] mix-blend-multiply" />
            </div>
        </>
    );
}
