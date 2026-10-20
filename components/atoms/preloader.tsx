"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLanguage } from "@/context/language-provider";
import logoSymbol from "@/public/assets/logo_symbol_transparent.png";
import Image from "next/image";

export function Preloader() {
    const [isLoading, setIsLoading] = useState(true);
    useLanguage();

    useEffect(() => {
        // Prevent scrolling while loading
        document.body.style.overflow = "hidden";

        const timer = setTimeout(() => {
            setIsLoading(false);
            document.body.style.overflow = "";
        }, 2000); // 2 seconds minimum loading time for the animation

        return () => {
            clearTimeout(timer);
            document.body.style.overflow = "";
        };
    }, []);

    return (
        <AnimatePresence mode="wait">
            {isLoading && (
                <motion.div
                    className="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-background"
                    initial={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5, ease: "easeInOut" }}
                >
                    {/* Infinite symbol animation */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.5 }}
                        className="relative w-32 h-32"
                    >
                        <motion.div
                            className="w-full h-full"
                            animate={{ rotate: 360 }}
                            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                        >
                            <Image
                                src={logoSymbol}
                                alt="Loading..."
                                fill
                                className="object-contain"
                                priority
                            />
                        </motion.div>

                        {/* Glow effect */}
                        <div className="absolute inset-0 blur-2xl bg-primary/20 rounded-full" />
                    </motion.div>

                    {/* Text reveal */}
                    <motion.div
                        className="mt-8 flex flex-col items-center gap-2"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <h1 className="text-2xl font-bold tracking-widest">
                            <span className="font-sans text-foreground">MDE</span>
                            <span className="font-display font-light text-foreground glitch-hover" data-text="ANGELIS">ANGELIS</span>
                        </h1>
                        <motion.div
                            className="h-0.5 bg-primary/50"
                            initial={{ width: 0 }}
                            animate={{ width: "100%" }}
                            transition={{ duration: 1.5, ease: "easeInOut" }}
                        />
                        <p className="text-sm text-muted-foreground uppercase tracking-[0.2em] text-[10px]">
                            Portfolio 2026
                        </p>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
