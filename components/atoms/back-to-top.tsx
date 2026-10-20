"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ChevronUp } from "lucide-react";

export function BackToTop() {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const toggleVisibility = () => {
            if (window.scrollY > 500) {
                setIsVisible(true);
            } else {
                setIsVisible(false);
            }
        };

        window.addEventListener("scroll", toggleVisibility);

        return () => window.removeEventListener("scroll", toggleVisibility);
    }, []);

    const scrollToTop = () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    return (
        <motion.button
            onClick={scrollToTop}
            className="fixed bottom-8 right-8 z-50 w-12 h-12 rounded-full bg-primary text-primary-foreground shadow-lg hover:shadow-xl hover:scale-110 transition-all duration-300 flex items-center justify-center group"
            initial={{ opacity: 0, scale: 0 }}
            animate={{
                opacity: isVisible ? 1 : 0,
                scale: isVisible ? 1 : 0,
                y: isVisible ? 0 : 20
            }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            aria-label="Scroll to top"
        >
            <ChevronUp className="w-6 h-6 group-hover:-translate-y-0.5 transition-transform" />

            {/* Pulse ring */}
            <span className="absolute inset-0 rounded-full bg-primary/30 animate-ping opacity-75" />
        </motion.button>
    );
}
