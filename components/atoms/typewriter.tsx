"use client";

import React, { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

interface TypewriterProps {
    text: string;
    speed?: number;
    delay?: number;
    className?: string;
    cursorClassName?: string;
    showCursor?: boolean;
}

export function Typewriter({
    text,
    speed = 50,
    delay = 500,
    className,
    cursorClassName,
    showCursor = true,
}: TypewriterProps) {
    const [displayText, setDisplayText] = useState("");
    const [isTyping, setIsTyping] = useState(false);

    useEffect(() => {
        const startTimeout = setTimeout(() => {
            setIsTyping(true);
            let currentIndex = 0;

            const interval = setInterval(() => {
                if (currentIndex < text.length) {
                    setDisplayText(text.substring(0, currentIndex + 1));
                    currentIndex++;
                } else {
                    clearInterval(interval);
                    setIsTyping(false);
                }
            }, speed);

            return () => clearInterval(interval);
        }, delay);

        return () => clearTimeout(startTimeout);
    }, [text, speed, delay]);

    return (
        <span className={cn("inline-block", className)}>
            {displayText}
            {showCursor && (
                <span
                    className={cn(
                        "inline-block w-[3px] h-[1.2em] bg-primary ml-1 align-middle animate-pulse",
                        !isTyping && "opacity-0",
                        cursorClassName
                    )}
                />
            )}
        </span>
    );
}
