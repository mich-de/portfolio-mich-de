"use client";

import React, { useRef, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { useLanguage } from "@/context/language-provider";
import { motion, useInView } from "framer-motion";
import gsap from "gsap";

const socialLinks = [
    { href: "https://instagram.com/mdeangelis_official", icon: "icon_social_instagram.png", label: "Instagram", color: "from-pink-500 to-purple-600" },
    { href: "https://music.youtube.com/channel/UCYJ3e3Ho1Jv2o2NhuI3JO7A", icon: "icon_social_youtube.png", label: "YouTube Music", color: "from-red-500 to-red-600" },
    { href: "https://open.spotify.com/intl-it/artist/3OucxkLy5uqnpSEHavZbpe", icon: "icon_music_spotify.png", label: "Spotify", color: "from-green-500 to-green-600" },
    { href: "https://music.apple.com/us/artist/mdeangelis/1796261710", icon: "icon_music_applemusic.png", label: "Apple Music", color: "from-pink-500 to-red-500" },
    { href: "https://soundcloud.com/mich_de", icon: "icon_music_soundcloud.png", label: "SoundCloud", color: "from-orange-500 to-orange-600" },
];

// Animated gradient orb component
const GradientOrb = ({ className, delay = 0 }: { className?: string; delay?: number }) => (
    <motion.div
        className={`absolute rounded-full blur-3xl opacity-20 ${className}`}
        initial={{ scale: 0.8, opacity: 0 }}
        whileInView={{ scale: 1, opacity: 0.2 }}
        transition={{ duration: 1.5, delay }}
        viewport={{ once: true }}
    />
);

export function ContactSection() {
    const { language } = useLanguage();
    const txt = language === "it"
        ? { badge: "\uD83D\uDCC8 Connettiti", title: "Restiamo in Contatto", desc: "Seguimi sui social per restare aggiornato sui miei progetti e interessi.", follow: "Seguimi" }
        : { badge: "\uD83D\uDCC8 Connect", title: "Let's Connect", desc: "Follow me on social media to stay updated on my projects and interests.", follow: "Follow me" };
    const sectionRef = useRef<HTMLElement>(null);
    const titleRef = useRef<HTMLHeadingElement>(null);
    const isInView = useInView(sectionRef, { once: true, margin: "-100px" });

    useEffect(() => {
        if (isInView && titleRef.current) {
            gsap.fromTo(titleRef.current,
                { backgroundPosition: "0% 50%" },
                { backgroundPosition: "100% 50%", duration: 3, ease: "power1.inOut", repeat: -1, yoyo: true }
            );
        }
    }, [isInView]);

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.1, delayChildren: 0.2 }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 30, scale: 0.9 },
        visible: {
            opacity: 1,
            y: 0,
            scale: 1,
            transition: { type: "spring" as const, stiffness: 100, damping: 12 }
        }
    };

    return (
        <section
            ref={sectionRef}
            id="contatti"
            className="relative px-6 overflow-hidden"
        >
            {/* Background Effects — bigger, brighter */}
            <div className="absolute inset-0 -z-10">
                <GradientOrb className="w-[700px] h-[700px] bg-primary/40 top-0 left-1/4" delay={0} />
                <GradientOrb className="w-[600px] h-[600px] bg-accent/40 bottom-0 right-1/4" delay={0.3} />
                <GradientOrb className="w-[500px] h-[500px] bg-chart-3/30 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" delay={0.6} />
            </div>

            {/* Decorative grid lines */}
            <div className="absolute inset-0 -z-[5] opacity-[0.02]">
                <div className="absolute inset-0"
                    style={{
                        backgroundImage: `
                            linear-gradient(to right, var(--foreground) 1px, transparent 1px),
                            linear-gradient(to bottom, var(--foreground) 1px, transparent 1px)
                        `,
                        backgroundSize: '60px 60px'
                    }}
                />
            </div>

            <div className="section-container container mx-auto max-w-4xl text-center relative">
                {/* Heading with gradient animation */}
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="mb-12"
                >
                    <motion.span
                        initial={{ opacity: 0, scale: 0.5 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        className="inline-block mb-4 px-4 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium"
                    >
                        {txt.badge}
                    </motion.span>

                    <h2
                        ref={titleRef}
                        className="heading-2 mb-4 bg-gradient-to-r from-foreground via-primary to-foreground bg-[length:200%_100%] bg-clip-text"
                    >
                        {txt.title}
                    </h2>
                    <p className="text-muted-foreground max-w-xl mx-auto text-lg">
                        {txt.desc}
                    </p>
                </motion.div>

                {/* Social Cards Grid */}
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    whileInView="visible"
                    viewport={{ once: true }}
                    className="flex flex-wrap justify-center gap-6 mb-12"
                >
                    {socialLinks.map((social, index) => (
                        <motion.div key={index} variants={itemVariants}>
                            <Link
                                href={social.href}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="group relative flex items-center gap-4 px-8 py-5 rounded-2xl border border-border bg-card/50 backdrop-blur-sm overflow-hidden transition-all duration-300 hover:border-primary/60 hover:shadow-xl hover:shadow-primary/20 hover:-translate-y-2 hover:scale-[1.02]"
                            >
                                {/* Spotlight effect */}
                                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                                    <div className={`absolute inset-0 bg-gradient-to-r ${social.color} opacity-5`} />
                                </div>

                                {/* Glow ring on hover — bigger, brighter */}
                                <div className="absolute -inset-2 bg-gradient-to-r from-primary/30 to-accent/30 rounded-2xl blur-xl opacity-0 group-hover:opacity-70 transition-opacity duration-500 -z-10" />

                                <div className="relative z-10 flex items-center gap-4">
                                    <div className="p-2 rounded-xl bg-background/50 border border-border/50 group-hover:border-primary/30 transition-colors">
                                        <Image
                                            src={`/assets/${social.icon}`}
                                            width={28}
                                            height={28}
                                            alt={social.label}
                                            className="transition-transform duration-300 group-hover:scale-110"
                                        />
                                    </div>
                                    <div className="text-left">
                                        <span className="block font-semibold text-foreground group-hover:text-primary transition-colors">
                                            {social.label}
                                        </span>
                                        <span className="text-xs text-muted-foreground">
                                            {txt.follow}
                                        </span>
                                    </div>
                                </div>

                                {/* Arrow indicator */}
                                <motion.svg
                                    className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors ml-2"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                    initial={{ x: 0 }}
                                    whileHover={{ x: 3 }}
                                >
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                                </motion.svg>
                            </Link>
                        </motion.div>
                    ))}
                </motion.div>

                {/* Website Link with special styling */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.4 }}
                    className="relative pt-8"
                >
                    {/* Decorative line */}
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-px bg-gradient-to-r from-transparent via-border to-transparent" />

                    <a
                        href="https://mdeangelis.me"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="group inline-flex items-center gap-3 px-6 py-3 rounded-full border border-border/50 bg-background/30 backdrop-blur-sm hover:border-primary/50 hover:bg-primary/5 transition-all duration-300"
                    >
                        <div className="p-1.5 rounded-full bg-primary/10 group-hover:bg-primary/20 transition-colors">
                            <Image src="/assets/icon_contact_website.png" width={18} height={18} alt="" />
                        </div>
                        <span className="font-mono text-sm text-muted-foreground group-hover:text-foreground transition-colors">
                            MDEANGELIS.ME
                        </span>
                        <svg className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                    </a>
                </motion.div>
            </div>
        </section>
    );
}
