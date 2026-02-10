"use client";

import { useEffect, useRef, useState } from "react";
import Image from "next/image";

interface Particle {
    x: number;
    y: number;
    size: number;
    speedX: number;
    speedY: number;
    opacity: number;
    pulse: number;
}

interface FloatingShape {
    x: number;
    y: number;
    size: number;
    rotation: number;
    rotationSpeed: number;
    floatOffset: number;
    type: "hexagon" | "diamond" | "circle";
}

export default function CinematicBackground() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [mousePos, setMousePos] = useState({ x: 0.5, y: 0.5 });

    // Mouse parallax effect
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

    // Canvas particle animation
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        let animationId: number;
        let particles: Particle[] = [];
        let shapes: FloatingShape[] = [];
        let time = 0;

        const resize = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            initParticles();
            initShapes();
        };

        const initParticles = () => {
            particles = [];
            const numParticles = Math.floor((canvas.width * canvas.height) / 12000);
            for (let i = 0; i < numParticles; i++) {
                particles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    size: Math.random() * 2.5 + 0.5,
                    speedX: (Math.random() - 0.5) * 0.4,
                    speedY: (Math.random() - 0.5) * 0.4,
                    opacity: Math.random() * 0.6 + 0.2,
                    pulse: Math.random() * Math.PI * 2,
                });
            }
        };

        const initShapes = () => {
            shapes = [];
            for (let i = 0; i < 6; i++) {
                shapes.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    size: Math.random() * 80 + 40,
                    rotation: Math.random() * Math.PI * 2,
                    rotationSpeed: (Math.random() - 0.5) * 0.01,
                    floatOffset: Math.random() * Math.PI * 2,
                    type: ["hexagon", "diamond", "circle"][Math.floor(Math.random() * 3)] as any,
                });
            }
        };

        const drawHexagon = (x: number, y: number, size: number, rotation: number, opacity: number) => {
            ctx.save();
            ctx.translate(x, y);
            ctx.rotate(rotation);
            ctx.beginPath();
            for (let i = 0; i < 6; i++) {
                const angle = (Math.PI / 3) * i;
                const px = Math.cos(angle) * size;
                const py = Math.sin(angle) * size;
                if (i === 0) ctx.moveTo(px, py);
                else ctx.lineTo(px, py);
            }
            ctx.closePath();
            ctx.strokeStyle = `rgba(255, 46, 99, ${opacity * 0.6})`; // Slightly more transparent for light mode
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.restore();
        };

        const drawDiamond = (x: number, y: number, size: number, rotation: number, opacity: number) => {
            ctx.save();
            ctx.translate(x, y);
            ctx.rotate(rotation);
            ctx.beginPath();
            ctx.moveTo(0, -size);
            ctx.lineTo(size * 0.6, 0);
            ctx.lineTo(0, size);
            ctx.lineTo(-size * 0.6, 0);
            ctx.closePath();
            ctx.strokeStyle = `rgba(100, 150, 255, ${opacity * 0.6})`;
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.restore();
        };

        const drawFloatingCircle = (x: number, y: number, size: number, opacity: number) => {
            ctx.beginPath();
            ctx.arc(x, y, size, 0, Math.PI * 2);
            ctx.strokeStyle = `rgba(150, 100, 255, ${opacity * 0.6})`;
            ctx.lineWidth = 1;
            ctx.stroke();
        };

        const drawParticle = (p: Particle) => {
            const pulseOpacity = p.opacity + Math.sin(p.pulse) * 0.2;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 46, 99, ${pulseOpacity})`; // Keep primary color
            ctx.fill();

            // Enhanced glow - reduced for light mode to avoid muddy look
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2);
            const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size * 3);
            gradient.addColorStop(0, `rgba(255, 46, 99, ${pulseOpacity * 0.2})`);
            gradient.addColorStop(1, "rgba(255, 46, 99, 0)");
            ctx.fillStyle = gradient;
            ctx.fill();
        };

        const connectParticles = () => {
            for (let i = 0; i < particles.length; i++) {
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < 150) {
                        ctx.beginPath();
                        ctx.strokeStyle = `rgba(255, 46, 99, ${0.1 * (1 - distance / 150)})`;
                        ctx.lineWidth = 0.5;
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }
        };

        const animate = () => {
            time += 0.01;
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw floating shapes
            shapes.forEach((s) => {
                s.rotation += s.rotationSpeed;
                const floatY = Math.sin(time + s.floatOffset) * 20;
                // Reduced opacity logic for light/subtle look
                const opacity = 0.1 + Math.sin(time * 0.5 + s.floatOffset) * 0.1;

                if (s.type === "hexagon") drawHexagon(s.x, s.y + floatY, s.size, s.rotation, opacity);
                else if (s.type === "diamond") drawDiamond(s.x, s.y + floatY, s.size, s.rotation, opacity);
                else drawFloatingCircle(s.x, s.y + floatY, s.size, opacity);
            });

            // Draw particles
            particles.forEach((p) => {
                p.x += p.speedX;
                p.y += p.speedY;
                p.pulse += 0.03;

                if (p.x < 0) p.x = canvas.width;
                if (p.x > canvas.width) p.x = 0;
                if (p.y < 0) p.y = canvas.height;
                if (p.y > canvas.height) p.y = 0;

                drawParticle(p);
            });

            connectParticles();
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

    const parallaxX = (mousePos.x - 0.5) * 30;
    const parallaxY = (mousePos.y - 0.5) * 30;

    return (
        <>
            {/* Hero Background Image with Parallax & Overlay - LIGHT MODE ADJUSTMENTS */}
            <div
                className="fixed inset-0 -z-40 overflow-hidden bg-slate-50"
                style={{ transform: `translate(${parallaxX}px, ${parallaxY}px) scale(1.1)` }}
            >
                {/* 
                   Optional: Use a light texture or map background if available. 
                   For now, removing the specific hero-bg.png or making it significantly fainter/inverted if it was dark.
                   Using CSS gradients for a clean light look.
                */}
                <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-white to-slate-100" />
            </div>

            {/* Particle Canvas */}
            <canvas
                ref={canvasRef}
                className="fixed inset-0 -z-20 pointer-events-none opacity-60"
            />

            {/* Subtle Aurora Gradient Layers - LIGHT MODE: More pastel/subtle */}
            <div className="fixed inset-0 -z-30 overflow-hidden pointer-events-none">
                <div
                    className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120vw] h-[120vh] bg-gradient-radial from-primary/5 via-transparent to-transparent animate-aurora-slow rounded-full blur-[120px]"
                    style={{ transform: `translate(calc(-50% + ${parallaxX * 0.3}px), calc(-50% + ${parallaxY * 0.3}px))` }}
                />
                <div className="absolute bottom-0 right-0 w-[80vw] h-[80vh] bg-gradient-radial from-blue-400/5 via-transparent to-transparent animate-pulse-slow rounded-full blur-[100px]" />
            </div>

            {/* Scan Line Effect - Very Subtle on Light */}
            <div className="fixed inset-0 -z-15 pointer-events-none overflow-hidden opacity-30">
                <div className="absolute inset-0 bg-[repeating-linear-gradient(0deg,transparent,transparent_2px,rgba(0,0,0,0.02)_2px,rgba(0,0,0,0.02)_4px)]" />
            </div>

            {/* Film Grain Overlay - Dark Grain for Light Bg */}
            <div className="fixed inset-0 -z-10 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 mix-blend-multiply pointer-events-none" />

            {/* Vignette - Lighter, Inverse */}
            <div className="fixed inset-0 -z-5 bg-gradient-radial from-transparent via-transparent to-slate-200/50 pointer-events-none" />
        </>
    );
}
