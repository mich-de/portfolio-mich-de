"use client";

import React, { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { LanguageSwitch } from "@/components/molecules/language-switch";
import { ThemeToggle } from "@/components/atoms/theme-toggle";
import { Button } from "@/components/ui/button";
import { Menu } from "lucide-react";
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from "@/components/ui/sheet";
import { useLanguage } from "@/context/language-provider";
import Image from "next/image";
import { motion } from "framer-motion";

export function Navbar() {
    const [isScrolled, setIsScrolled] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const [activeSection, setActiveSection] = useState("home");
    const { t } = useLanguage();

    // Handle scroll for transparency effect
    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 50);
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const navItems = useMemo(() => [
        { label: t("nav.home"), href: "#home", id: "home", icon: "icon_menu_home.png" },
        { label: t("nav.about"), href: "#about", id: "about", icon: "icon_menu_about.png" },
        { label: t("nav.interests"), href: "#interests", id: "interests", icon: "icon_menu_interests.png" },
        { label: t("nav.contact"), href: "#contatti", id: "contatti", icon: "icon_menu_contact.png" },
    ], [t]);

    // Track active section
    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        setActiveSection(entry.target.id);
                    }
                });
            },
            { threshold: 0.3, rootMargin: "-100px 0px -50% 0px" }
        );

        navItems.forEach((item) => {
            const element = document.getElementById(item.id);
            if (element) observer.observe(element);
        });

        return () => observer.disconnect();
    }, [navItems]);

    return (
        <header
            className={cn(
                "fixed top-0 left-0 right-0 z-50 transition-all duration-300 border-b",
                isScrolled
                    ? "bg-background/80 border-border/50 backdrop-blur-xl shadow-sm dark:bg-background/70 dark:border-border/30"
                    : "bg-transparent border-transparent"
            )}
        >
            <nav className="container mx-auto px-6 h-16 flex items-center justify-between">
                {/* Logo */}
                <Link href="/" className="text-xl font-bold tracking-tighter text-foreground hover:text-primary transition-colors flex items-center group">
                    <span className="font-sans">MDE</span><span className="font-display font-light glitch-hover" data-text="ANGELIS">ANGELIS</span>
                </Link>

                {/* Desktop Menu */}
                <div className="hidden md:flex items-center gap-6">
                    <ul className="flex gap-1">
                        {navItems.map((item) => (
                            <li key={item.href}>
                                <Link
                                    href={item.href}
                                    className={cn(
                                        "text-sm font-medium px-4 py-2 rounded-lg transition-all duration-200 flex items-center gap-2",
                                        activeSection === item.id
                                            ? "bg-primary/10 text-primary"
                                            : "hover:bg-muted text-foreground/80 hover:text-foreground"
                                    )}
                                >
                                    <Image
                                        src={`/assets/${item.icon}`}
                                        alt=""
                                        width={20}
                                        height={20}
                                        className="object-contain"
                                    />
                                    {item.label}
                                </Link>
                            </li>
                        ))}
                    </ul>
                    <div className="flex items-center gap-2 border-l pl-4 border-border">
                        <ThemeToggle />
                        <LanguageSwitch />
                    </div>
                </div>

                {/* Mobile Menu */}
                <div className="md:hidden flex items-center gap-2">
                    <ThemeToggle />
                    <LanguageSwitch />
                    <Sheet open={isOpen} onOpenChange={setIsOpen}>
                        <SheetTrigger asChild>
                            <Button variant="ghost" size="icon" aria-label="Toggle mobile menu">
                                <Menu className="h-6 w-6" />
                                <span className="sr-only">Toggle menu</span>
                            </Button>
                        </SheetTrigger>
                        <SheetContent side="right" className="w-[300px] sm:w-[400px]">
                            <SheetTitle className="sr-only">Navigation Menu</SheetTitle>
                            <nav className="flex flex-col gap-2 mt-8">
                                {navItems.map((item, index) => (
                                    <motion.div
                                        key={item.href}
                                        initial={{ opacity: 0, x: 20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: 0.1 + index * 0.1 }}
                                    >
                                        <Link
                                            href={item.href}
                                            onClick={() => setIsOpen(false)}
                                            className={cn(
                                                "text-lg font-medium py-3 px-4 rounded-xl transition-all flex items-center gap-3",
                                                activeSection === item.id
                                                    ? "bg-primary/10 text-primary"
                                                    : "hover:bg-muted"
                                            )}
                                        >
                                            <div className="relative w-6 h-6">
                                                <Image
                                                    src={`/assets/${item.icon}`}
                                                    alt=""
                                                    fill
                                                    className="object-contain"
                                                />
                                            </div>
                                            {item.label}
                                        </Link>
                                    </motion.div>
                                ))}
                            </nav>
                        </SheetContent>
                    </Sheet>
                </div>
            </nav>
        </header>
    );
}

