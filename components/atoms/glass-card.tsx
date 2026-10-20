import { cn } from "@/lib/utils";
import React from "react";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode;
    hoverEffect?: boolean;
}

export function GlassCard({
    children,
    className,
    hoverEffect = true,
    ...props
}: GlassCardProps) {
    return (
        <div
            className={cn(
                "relative overflow-hidden rounded-xl border border-white/10 bg-white/5 backdrop-blur-md",
                "shadow-[0_8px_32px_0_rgba(31,38,135,0.07)]",
                "dark:border-white/5 dark:bg-black/10",
                hoverEffect && "transition-all duration-300 hover:bg-white/10 hover:shadow-[0_8px_32px_0_rgba(31,38,135,0.15)] hover:scale-[1.01]",
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
}
