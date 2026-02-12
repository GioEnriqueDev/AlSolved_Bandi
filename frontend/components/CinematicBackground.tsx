"use client";

import { useEffect, useRef } from "react";

// ─── PlayStation-Style Magenta Silk Waves ───
// Multi-layered, glossy canvas animation with ambient bloom

interface WaveLayer {
    yOffset: number;
    amplitude: number;
    frequency: number;
    speed: number;
    color: string;
    fillColor: string;
    thickness: number;
    glossy: boolean;
    phase: number;
}

const WAVE_LAYERS: WaveLayer[] = [
    // Layer 0: Deep base — widest, slowest
    {
        yOffset: 80, amplitude: 200, frequency: 0.0004, speed: 0.3,
        color: "rgba(173, 20, 87, 0.08)", fillColor: "rgba(173, 20, 87, 0.03)",
        thickness: 240, glossy: false, phase: 0,
    },
    // Layer 1: Mid magenta — main visible wave
    {
        yOffset: 40, amplitude: 150, frequency: 0.0007, speed: 0.5,
        color: "rgba(233, 30, 99, 0.12)", fillColor: "rgba(233, 30, 99, 0.04)",
        thickness: 160, glossy: true, phase: 1.2,
    },
    // Layer 2: Vivid pink — accent wave
    {
        yOffset: 0, amplitude: 100, frequency: 0.0012, speed: 0.8,
        color: "rgba(255, 46, 99, 0.18)", fillColor: "rgba(255, 46, 99, 0.06)",
        thickness: 100, glossy: true, phase: 2.4,
    },
    // Layer 3: Hot pink highlight — fast, thin
    {
        yOffset: -30, amplitude: 60, frequency: 0.002, speed: -0.6,
        color: "rgba(255, 46, 99, 0.14)", fillColor: "rgba(255, 46, 99, 0.03)",
        thickness: 50, glossy: true, phase: 3.8,
    },
    // Layer 4: Cool blue contrast — very subtle
    {
        yOffset: -60, amplitude: 180, frequency: 0.0003, speed: 0.2,
        color: "rgba(100, 130, 255, 0.04)", fillColor: "rgba(100, 130, 255, 0.015)",
        thickness: 220, glossy: false, phase: 5.0,
    },
    // Layer 5: Shimmer pink — ultra thin, fast
    {
        yOffset: 10, amplitude: 40, frequency: 0.003, speed: 1.2,
        color: "rgba(255, 80, 130, 0.1)", fillColor: "rgba(255, 80, 130, 0.02)",
        thickness: 30, glossy: true, phase: 0.7,
    },
];

export default function CinematicBackground() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const mouseRef = useRef({ x: 0.5, y: 0.5 });
    const rafRef = useRef<number>(0);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            mouseRef.current = {
                x: e.clientX / window.innerWidth,
                y: e.clientY / window.innerHeight,
            };
        };
        window.addEventListener("mousemove", handleMouseMove, { passive: true });
        return () => window.removeEventListener("mousemove", handleMouseMove);
    }, []);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d", { alpha: false });
        if (!ctx) return;

        let time = 0;
        let w = 0;
        let h = 0;

        const resize = () => {
            const dpr = Math.min(window.devicePixelRatio, 2);
            w = window.innerWidth;
            h = window.innerHeight;
            canvas.width = w * dpr;
            canvas.height = h * dpr;
            canvas.style.width = `${w}px`;
            canvas.style.height = `${h}px`;
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        };

        const drawWave = (layer: WaveLayer, t: number) => {
            const centerY = h * 0.55;
            const step = 4;

            // Compute wave path
            ctx.beginPath();
            ctx.moveTo(-10, centerY + layer.yOffset + layer.amplitude);

            for (let x = -10; x <= w + 10; x += step) {
                const y = centerY + layer.yOffset
                    + Math.sin(x * layer.frequency + t * layer.speed + layer.phase) * layer.amplitude
                    + Math.sin(x * layer.frequency * 0.5 + t * layer.speed * 0.7 + layer.phase * 0.3) * (layer.amplitude * 0.4)
                    + Math.sin(x * layer.frequency * 2.3 + t * layer.speed * 0.3) * (layer.amplitude * 0.15);
                ctx.lineTo(x, y);
            }

            // Fill to bottom
            ctx.lineTo(w + 10, h + 10);
            ctx.lineTo(-10, h + 10);
            ctx.closePath();
            ctx.fillStyle = layer.fillColor;
            ctx.fill();

            // Stroke the wave line
            ctx.beginPath();
            ctx.moveTo(-10, centerY);
            for (let x = -10; x <= w + 10; x += step) {
                const y = centerY + layer.yOffset
                    + Math.sin(x * layer.frequency + t * layer.speed + layer.phase) * layer.amplitude
                    + Math.sin(x * layer.frequency * 0.5 + t * layer.speed * 0.7 + layer.phase * 0.3) * (layer.amplitude * 0.4)
                    + Math.sin(x * layer.frequency * 2.3 + t * layer.speed * 0.3) * (layer.amplitude * 0.15);
                ctx.lineTo(x, y);
            }
            ctx.strokeStyle = layer.color;
            ctx.lineWidth = layer.thickness;
            ctx.lineCap = "round";
            ctx.stroke();

            // Glossy highlight — thin white line on crests
            if (layer.glossy) {
                ctx.beginPath();
                for (let x = -10; x <= w + 10; x += step) {
                    const y = centerY + layer.yOffset
                        + Math.sin(x * layer.frequency + t * layer.speed + layer.phase) * layer.amplitude
                        + Math.sin(x * layer.frequency * 0.5 + t * layer.speed * 0.7 + layer.phase * 0.3) * (layer.amplitude * 0.4)
                        + Math.sin(x * layer.frequency * 2.3 + t * layer.speed * 0.3) * (layer.amplitude * 0.15);
                    if (x === -10) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.strokeStyle = "rgba(255, 255, 255, 0.18)";
                ctx.lineWidth = 1.5;
                ctx.stroke();

                // Secondary gloss — offset
                ctx.beginPath();
                for (let x = -10; x <= w + 10; x += step) {
                    const y = centerY + layer.yOffset - 2
                        + Math.sin(x * layer.frequency + t * layer.speed + layer.phase) * layer.amplitude
                        + Math.sin(x * layer.frequency * 0.5 + t * layer.speed * 0.7 + layer.phase * 0.3) * (layer.amplitude * 0.4)
                        + Math.sin(x * layer.frequency * 2.3 + t * layer.speed * 0.3) * (layer.amplitude * 0.15);
                    if (x === -10) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
                ctx.lineWidth = 3;
                ctx.stroke();
            }
        };

        const drawAmbientBloom = (t: number) => {
            // Magenta bloom — left
            const grad1 = ctx.createRadialGradient(
                w * 0.15 + Math.sin(t * 0.2) * 80, h * 0.45, 0,
                w * 0.15 + Math.sin(t * 0.2) * 80, h * 0.45, w * 0.4
            );
            grad1.addColorStop(0, "rgba(255, 46, 99, 0.06)");
            grad1.addColorStop(0.5, "rgba(233, 30, 99, 0.02)");
            grad1.addColorStop(1, "rgba(255, 46, 99, 0)");
            ctx.fillStyle = grad1;
            ctx.fillRect(0, 0, w, h);

            // Purple bloom — right
            const grad2 = ctx.createRadialGradient(
                w * 0.85 + Math.cos(t * 0.15) * 60, h * 0.35, 0,
                w * 0.85 + Math.cos(t * 0.15) * 60, h * 0.35, w * 0.35
            );
            grad2.addColorStop(0, "rgba(180, 50, 220, 0.04)");
            grad2.addColorStop(0.6, "rgba(140, 30, 180, 0.01)");
            grad2.addColorStop(1, "rgba(180, 50, 220, 0)");
            ctx.fillStyle = grad2;
            ctx.fillRect(0, 0, w, h);

            // Warm center glow
            const grad3 = ctx.createRadialGradient(
                w * 0.5, h * 0.5, 0,
                w * 0.5, h * 0.5, w * 0.5
            );
            grad3.addColorStop(0, "rgba(255, 200, 220, 0.03)");
            grad3.addColorStop(1, "rgba(255, 200, 220, 0)");
            ctx.fillStyle = grad3;
            ctx.fillRect(0, 0, w, h);
        };

        const animate = () => {
            time += 0.004;

            // Clear with light background
            ctx.fillStyle = "#F8FAFC";
            ctx.fillRect(0, 0, w, h);

            // Ambient bloom (behind waves)
            drawAmbientBloom(time);

            // Apply global blur for silk effect
            ctx.save();
            ctx.filter = "blur(30px)";

            // Draw waves back to front
            for (let i = 0; i < WAVE_LAYERS.length; i++) {
                drawWave(WAVE_LAYERS[i], time);
            }

            ctx.restore();

            // Draw the top two waves again without blur for crisp glossy highlights
            ctx.save();
            ctx.filter = "blur(1px)";
            for (let i = 2; i < 4; i++) {
                // Only draw the glossy highlight part
                const layer = WAVE_LAYERS[i];
                const centerY = h * 0.55;
                const step = 4;

                ctx.beginPath();
                for (let x = -10; x <= w + 10; x += step) {
                    const y = centerY + layer.yOffset
                        + Math.sin(x * layer.frequency + time * layer.speed + layer.phase) * layer.amplitude
                        + Math.sin(x * layer.frequency * 0.5 + time * layer.speed * 0.7 + layer.phase * 0.3) * (layer.amplitude * 0.4)
                        + Math.sin(x * layer.frequency * 2.3 + time * layer.speed * 0.3) * (layer.amplitude * 0.15);
                    if (x === -10) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.strokeStyle = "rgba(255, 255, 255, 0.12)";
                ctx.lineWidth = 1;
                ctx.stroke();
            }
            ctx.restore();

            // Vignette overlay
            const vignette = ctx.createRadialGradient(
                w * 0.5, h * 0.5, w * 0.2,
                w * 0.5, h * 0.5, w * 0.8
            );
            vignette.addColorStop(0, "rgba(248, 250, 252, 0)");
            vignette.addColorStop(1, "rgba(226, 232, 240, 0.3)");
            ctx.fillStyle = vignette;
            ctx.fillRect(0, 0, w, h);

            rafRef.current = requestAnimationFrame(animate);
        };

        resize();
        window.addEventListener("resize", resize);
        animate();

        return () => {
            window.removeEventListener("resize", resize);
            cancelAnimationFrame(rafRef.current);
        };
    }, []);

    const mx = mouseRef.current;
    const parallaxX = (mx.x - 0.5) * 15;
    const parallaxY = (mx.y - 0.5) * 15;

    return (
        <div
            className="fixed inset-0 -z-10 overflow-hidden"
            style={{
                transform: `translate(${parallaxX}px, ${parallaxY}px) scale(1.05)`,
                willChange: "transform",
            }}
        >
            <canvas
                ref={canvasRef}
                className="absolute inset-0 w-full h-full"
            />
        </div>
    );
}
