"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

interface NeonLogoProps {
    className?: string;
    size?: "sm" | "md" | "lg";
}

export default function NeonLogo({
    className,
    size = "md",
}: NeonLogoProps) {
    const [isVisible, setIsVisible] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    const sizes = {
        sm: { icon: 32, text: "text-xl", gap: "gap-2" },
        md: { icon: 40, text: "text-2xl", gap: "gap-3" },
        lg: { icon: 56, text: "text-4xl", gap: "gap-4" },
    };

    useEffect(() => {
        // Trigger entrance animation after mount
        const timer = setTimeout(() => setIsVisible(true), 100);
        return () => clearTimeout(timer);
    }, []);

    return (
        <div
            ref={containerRef}
            className={cn(
                "flex items-center relative group",
                sizes[size].gap,
                className
            )}
        >
            {/* Hover Glow Aura */}
            <div className="absolute -inset-4 rounded-2xl bg-[#FF2E63]/0 group-hover:bg-[#FF2E63]/8 blur-2xl transition-all duration-700 pointer-events-none" />

            {/* SVG Icon */}
            <svg
                width={sizes[size].icon}
                height={sizes[size].icon}
                viewBox="0 0 48 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className={cn(
                    "relative z-10 transition-transform duration-500 ease-out",
                    "group-hover:scale-105",
                    isVisible ? "opacity-100" : "opacity-0"
                )}
                style={{
                    filter: "drop-shadow(0 0 6px rgba(255, 46, 99, 0.3))",
                    transitionDelay: "200ms",
                }}
            >
                <defs>
                    <linearGradient id="bubble-gradient" x1="8" y1="6" x2="32" y2="32">
                        <stop offset="0%" stopColor="#FF2E63" />
                        <stop offset="100%" stopColor="#E91E63" />
                    </linearGradient>
                    <filter id="neon-glow" x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="2" result="blur" />
                        <feMerge>
                            <feMergeNode in="blur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                {/* Front bubble — magenta */}
                <path
                    d="M8 10C8 7.79086 9.79086 6 12 6H28C30.2091 6 32 7.79086 32 10V22C32 24.2091 30.2091 26 28 26H16L10 32V26H12C9.79086 26 8 24.2091 8 22V10Z"
                    stroke="url(#bubble-gradient)"
                    strokeWidth="2.5"
                    fill="rgba(255, 46, 99, 0.12)"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    filter="url(#neon-glow)"
                    className="neon-logo-bubble"
                    style={{
                        strokeDasharray: 200,
                        strokeDashoffset: isVisible ? 0 : 200,
                        transition: "stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)",
                    }}
                />

                {/* Back bubble — dark gray */}
                <path
                    d="M16 18C16 15.7909 17.7909 14 20 14H36C38.2091 14 40 15.7909 40 18V30C40 32.2091 38.2091 34 36 34H32V40L26 34H20C17.7909 34 16 32.2091 16 30V18Z"
                    stroke="#6B7280"
                    strokeWidth="2.5"
                    fill="rgba(107, 114, 128, 0.06)"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="neon-logo-bubble-back"
                    style={{
                        strokeDasharray: 200,
                        strokeDashoffset: isVisible ? 0 : 200,
                        transition: "stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1) 0.15s",
                    }}
                />
            </svg>

            {/* Text */}
            <div className="relative z-10">
                <span
                    className={cn(
                        "font-black tracking-[0.15em] uppercase transition-all duration-700",
                        sizes[size].text,
                        isVisible ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-2"
                    )}
                    style={{
                        background: "linear-gradient(135deg, #1F2937 0%, #111827 40%, #FF2E63 100%)",
                        WebkitBackgroundClip: "text",
                        WebkitTextFillColor: "transparent",
                        backgroundClip: "text",
                        transitionDelay: "400ms",
                    }}
                >
                    ALSOLVED
                </span>

                {/* Subtle magenta glow behind text */}
                <span
                    className={cn(
                        "font-black tracking-[0.15em] uppercase absolute inset-0 pointer-events-none transition-opacity duration-1000",
                        sizes[size].text,
                        isVisible ? "opacity-40" : "opacity-0"
                    )}
                    style={{
                        color: "#FF2E63",
                        filter: "blur(10px)",
                        transitionDelay: "600ms",
                    }}
                    aria-hidden
                >
                    ALSOLVED
                </span>
            </div>
        </div>
    );
}
