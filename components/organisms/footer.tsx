"use client";

import React from "react";
import Link from "next/link";
import { useLanguage } from "@/context/language-provider";
import { motion } from "framer-motion";

const footerLinks = [
    { href: "#home", labelIt: "Home", labelEn: "Home" },
    { href: "#about", labelIt: "Chi Sono", labelEn: "About" },
    { href: "#interests", labelIt: "Interessi", labelEn: "Interests" },
    { href: "#contatti", labelIt: "Contatti", labelEn: "Contact" },
];

export function Footer() {
    const { language } = useLanguage();
    const currentYear = new Date().getFullYear();

    return (
        <footer className="relative py-12 border-t border-border/50 bg-background overflow-hidden">
            {/* Subtle gradient overlay */}
            <div className="absolute inset-0 -z-10">
                <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-primary/5 to-transparent" />
            </div>

            <div className="container mx-auto px-6">
                <div className="flex flex-col md:flex-row items-center justify-between gap-8">

                    {/* Logo and Brand */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="flex flex-col items-center md:items-start gap-2"
                    >
                        <Link href="#home" className="group flex items-center gap-2">
                            <span className="text-xl font-bold text-foreground">
                                <span className="font-sans">MDE</span>
                                <span className="font-display font-light glitch-hover" data-text="ANGELIS">ANGELIS</span>
                            </span>
                        </Link>
                        <p className="text-xs text-muted-foreground">
                            IT Professional & Technology Enthusiast
                        </p>
                    </motion.div>

                    {/* Navigation Links */}
                    <motion.nav
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="flex flex-wrap justify-center gap-6"
                    >
                        {footerLinks.map((link, index) => (
                            <Link
                                key={index}
                                href={link.href}
                                className="text-sm text-muted-foreground hover:text-primary transition-colors duration-200 relative group"
                            >
                                {language === "it" ? link.labelIt : link.labelEn}
                                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary group-hover:w-full transition-all duration-300" />
                            </Link>
                        ))}
                    </motion.nav>

                    {/* Back to top button */}
                    <motion.button
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                        className="group flex items-center gap-2 px-4 py-2 rounded-full border border-border/50 bg-background/50 hover:border-primary/50 hover:bg-primary/5 transition-all duration-300"
                        aria-label="Scroll to top"
                    >
                        <svg
                            className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors transform group-hover:-translate-y-0.5 duration-300"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                        </svg>
                        <span className="text-xs text-muted-foreground group-hover:text-primary transition-colors">
                            {language === "it" ? "Torna su" : "Back to top"}
                        </span>
                    </motion.button>
                </div>

                {/* Divider */}
                <div className="my-8 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

                {/* Copyright */}
                <motion.div
                    initial={{ opacity: 0 }}
                    whileInView={{ opacity: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.3 }}
                    className="flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-muted-foreground"
                >
                    <p className="flex items-center gap-1.5">
                        <span>© {currentYear}</span>
                        <span className="font-bold text-foreground">
                            <span className="font-sans">MDE</span>
                            <span className="font-display font-light glitch-hover" data-text="ANGELIS">ANGELIS</span>
                        </span>
                        <span className="hidden sm:inline">•</span>
                        <span className="hidden sm:inline">
                            {language === "it" ? "Tutti i diritti riservati" : "All rights reserved"}
                        </span>
                    </p>

                    <p className="flex items-center gap-1.5">
                        <span>{language === "it" ? "Fatto con" : "Made with"}</span>
                        <motion.span
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ duration: 1, repeat: Infinity, repeatDelay: 1 }}
                            className="text-red-500"
                        >
                            ❤️
                        </motion.span>
                        <span>{language === "it" ? "e passione per la tecnologia" : "and passion for technology"}</span>
                    </p>
                </motion.div>
            </div>
        </footer>
    );
}
