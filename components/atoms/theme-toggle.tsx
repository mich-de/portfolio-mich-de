"use client";

import { useSyncExternalStore, useCallback, useRef } from "react";
import { useTheme } from "next-themes";
import { motion, AnimatePresence } from "framer-motion";

function useHydrated() {
    return useSyncExternalStore(
        () => () => { },
        () => true,
        () => false
    );
}

export function ThemeToggle() {
    const { setTheme, resolvedTheme } = useTheme();
    const mounted = useHydrated();
    const btnRef = useRef<HTMLButtonElement>(null);

    const toggle = useCallback(() => {
        setTheme(resolvedTheme === "dark" ? "light" : "dark");
    }, [resolvedTheme, setTheme]);

    if (!mounted) {
        return (
            <div className="w-10 h-10 rounded-full bg-muted animate-pulse" />
        );
    }

    const isDark = resolvedTheme === "dark";

    return (
        <button
            ref={btnRef}
            onClick={toggle}
            className="relative w-10 h-10 rounded-full bg-secondary hover:bg-secondary/80 transition-colors flex items-center justify-center overflow-hidden group"
            aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
        >
            {/* Orbital ring */}
            <motion.div
                className="absolute inset-[-4px] rounded-full border border-primary/20"
                animate={{
                    rotate: [0, 360],
                    scale: [1, 1.15, 1],
                    opacity: [0.3, 0.6, 0.3],
                }}
                transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "linear",
                }}
            />
            <motion.div
                className="absolute inset-[-8px] rounded-full border border-accent/10"
                animate={{
                    rotate: [360, 0],
                    scale: [1, 1.1, 1],
                    opacity: [0.15, 0.4, 0.15],
                }}
                transition={{
                    duration: 5,
                    repeat: Infinity,
                    ease: "linear",
                }}
            />

            {/* Icon */}
            <AnimatePresence mode="wait" initial={false}>
                {isDark ? (
                    <motion.svg
                        key="moon"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="w-5 h-5 text-primary relative z-10"
                        initial={{ rotate: -90, scale: 0, opacity: 0 }}
                        animate={{ rotate: 0, scale: 1, opacity: 1 }}
                        exit={{ rotate: 90, scale: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: "easeInOut" }}
                    >
                        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                    </motion.svg>
                ) : (
                    <motion.svg
                        key="sun"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="w-5 h-5 text-primary relative z-10"
                        initial={{ rotate: 90, scale: 0, opacity: 0 }}
                        animate={{ rotate: 0, scale: 1, opacity: 1 }}
                        exit={{ rotate: -90, scale: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: "easeInOut" }}
                    >
                        <circle cx="12" cy="12" r="5" />
                        <line x1="12" y1="1" x2="12" y2="3" />
                        <line x1="12" y1="21" x2="12" y2="23" />
                        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                        <line x1="1" y1="12" x2="3" y2="12" />
                        <line x1="21" y1="12" x2="23" y2="12" />
                        <line x1="4.22" y1="19.78" x2="5.64" y2="5.64" />
                        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
                    </motion.svg>
                )}
            </AnimatePresence>

            {/* Glow burst on hover */}
            <div className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 transition-all duration-500 bg-primary/10 blur-md scale-125 group-hover:scale-150" />
        </button>
    );
}
