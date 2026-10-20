"use client";

import React from "react";

interface SectionDividerProps {
    variant?: "wave" | "angle" | "curve" | "fade";
    flip?: boolean;
    className?: string;
}

export function SectionDivider({
    variant = "wave",
    flip = false,
    className = ""
}: SectionDividerProps) {
    const baseClasses = `w-full overflow-hidden leading-[0] ${flip ? 'rotate-180' : ''} ${className}`;

    if (variant === "wave") {
        return (
            <div className={baseClasses}>
                <svg
                    className="relative block w-full h-[60px] md:h-[80px]"
                    viewBox="0 0 1200 120"
                    preserveAspectRatio="none"
                >
                    <path
                        d="M321.39,56.44c58-10.79,114.16-30.13,172-41.86,82.39-16.72,168.19-17.73,250.45-.39C823.78,31,906.67,72,985.66,92.83c70.05,18.48,146.53,26.09,214.34,3V0H0V27.35A600.21,600.21,0,0,0,321.39,56.44Z"
                        className="fill-background"
                    />
                </svg>
            </div>
        );
    }

    if (variant === "angle") {
        return (
            <div className={baseClasses}>
                <svg
                    className="relative block w-full h-[40px] md:h-[60px]"
                    viewBox="0 0 1200 120"
                    preserveAspectRatio="none"
                >
                    <path
                        d="M1200 120L0 16.48V0h1200v120z"
                        className="fill-background"
                    />
                </svg>
            </div>
        );
    }

    if (variant === "curve") {
        return (
            <div className={baseClasses}>
                <svg
                    className="relative block w-full h-[50px] md:h-[70px]"
                    viewBox="0 0 1200 120"
                    preserveAspectRatio="none"
                >
                    <path
                        d="M600,112.77C268.63,112.77,0,65.52,0,7.23V120H1200V7.23C1200,65.52,931.37,112.77,600,112.77Z"
                        className="fill-background"
                    />
                </svg>
            </div>
        );
    }

    // Fade gradient divider
    return (
        <div className={`w-full h-16 md:h-24 bg-gradient-to-b from-transparent via-border/20 to-transparent ${className}`} />
    );
}

// Inverted version for section tops
export function SectionDividerTop({
    variant = "wave",
    className = ""
}: Omit<SectionDividerProps, 'flip'>) {
    return <SectionDivider variant={variant} flip className={className} />;
}
