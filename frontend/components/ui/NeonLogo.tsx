"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface NeonLogoProps {
    className?: string;
    size?: "sm" | "md" | "lg";
}

export default function NeonLogo({
    className,
    size = "md",
}: NeonLogoProps) {
    const sizes = {
        sm: { icon: 32, text: "text-xl", blur: "blur-[1px]" },
        md: { icon: 40, text: "text-2xl", blur: "blur-[1.5px]" },
        lg: { icon: 56, text: "text-4xl", blur: "blur-[2px]" },
    };

    return (
        <div className={cn("flex items-center gap-3 relative group", className)}>

            {/* Glow Effect Underlying */}
            <div className={cn(
                "absolute inset-0 bg-primary/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500",
                sizes[size].blur
            )} />

            {/* Animated SVG Icon with Neon Stroke */}
            <motion.svg
                width={sizes[size].icon}
                height={sizes[size].icon}
                viewBox="0 0 48 48"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 400, damping: 10 }}
                className="relative z-10"
            >
                <defs>
                    <filter id="glow-red" x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                {/* Pink Speech Bubble (Front) - Neon Style */}
                <motion.path
                    d="M8 10C8 7.79086 9.79086 6 12 6H28C30.2091 6 32 7.79086 32 10V22C32 24.2091 30.2091 26 28 26H16L10 32V26H12C9.79086 26 8 24.2091 8 22V10Z"
                    stroke="#F24E6B"
                    strokeWidth="2.5"
                    fill="transparent"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    style={{ filter: "url(#glow-red)" }}
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ pathLength: 1, opacity: 1 }}
                    transition={{ duration: 1.2, ease: "easeInOut" }}
                />

                {/* Fill animation for "ON" state */}
                <motion.path
                    d="M8 10C8 7.79086 9.79086 6 12 6H28C30.2091 6 32 7.79086 32 10V22C32 24.2091 30.2091 26 28 26H16L10 32V26H12C9.79086 26 8 24.2091 8 22V10Z"
                    fill="#F24E6B"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 0.2 }}
                    transition={{ delay: 1, duration: 0.5 }}
                />

                {/* Gray Speech Bubble (Back) - Neon Style */}
                <motion.path
                    d="M16 18C16 15.7909 17.7909 14 20 14H36C38.2091 14 40 15.7909 40 18V30C40 32.2091 38.2091 34 36 34H32V40L26 34H20C17.7909 34 16 32.2091 16 30V18Z"
                    stroke="#4B5563"
                    strokeWidth="2.5"
                    fill="transparent"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ pathLength: 1, opacity: 1 }}
                    transition={{ duration: 1.2, delay: 0.2, ease: "easeInOut" }}
                />
            </motion.svg>

            {/* Neon Text */}
            <div className="relative">
                {/* Main Text */}
                <motion.span
                    className={cn(
                        "font-bold tracking-widest text-white relative z-10",
                        sizes[size].text
                    )}
                    style={{
                        textShadow: "0 0 10px rgba(255,255,255,0.7), 0 0 20px rgba(255,255,255,0.5), 0 0 30px rgba(242,78,107,0.3)"
                    }}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.5 }}
                >
                    ALSOLVED
                </motion.span>

                {/* Flickering Clone for "broken neon" effect (Subtle) */}
                <motion.span
                    className={cn(
                        "font-bold tracking-widest text-[#F24E6B] absolute inset-0 z-0",
                        sizes[size].text
                    )}
                    style={{
                        filter: "blur(8px)",
                        opacity: 0.7
                    }}
                    animate={{
                        opacity: [0.6, 0.8, 0.6, 0.7, 0.6],
                    }}
                    transition={{
                        duration: 3,
                        repeat: Infinity,
                        repeatType: "reverse"
                    }}
                >
                    ALSOLVED
                </motion.span>
            </div>
        </div>
    );
}
