import { cn } from "@/lib/utils";
import React from "react";

interface GradientTextProps extends React.HTMLAttributes<HTMLSpanElement> {
    children: React.ReactNode;
    from?: string;
    via?: string;
    to?: string;
}

export function GradientText({
    children,
    className,
    from = "from-indigo-500",
    via = "via-purple-500",
    to = "to-pink-500",
    ...props
}: GradientTextProps) {
    return (
        <span
            className={cn(
                "bg-gradient-to-r bg-clip-text text-transparent animate-gradient-x",
                from,
                via,
                to,
                className
            )}
            {...props}
        >
            {children}
        </span>
    );
}
