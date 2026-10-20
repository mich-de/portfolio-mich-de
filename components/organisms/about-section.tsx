"use client";

import React from "react";
import Image from "next/image";
import profileImage from "@/public/assets/logo.jpg";
import { useLanguage } from "@/context/language-provider";
import { motion } from "framer-motion";
import { GlassCard } from "@/components/atoms/glass-card";
import { AnimatedCounter } from "@/components/atoms/animated-counter";

export function AboutSection() {


    const { t } = useLanguage();
    // We need to cast "about.bio" to an object since t() returns string | object
    // Fix: Cast to unknown first to avoid "Conversion of type 'string' to type... may be a mistake"
    const bio = t("about.bio") as unknown as { p1: string; p2: string; p3: string };
    const tags = t("about.tags") as unknown as string[];

    return (
        <section id="about" className="relative overflow-hidden px-6">
            <div className="section-container container mx-auto relative z-10">
                <motion.h2
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="heading-2 text-center mb-16"
                >
                    {t("about.title")}
                </motion.h2>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                    {/* Left Column: Image & Stats */}
                    <motion.div
                        initial={{ opacity: 0, x: -50 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className="relative"
                    >
                        {/* Profile Image with 3D Tilt Effect */}
                        <motion.div
                            className="relative w-full max-w-md mx-auto aspect-square rounded-2xl overflow-hidden border-4 border-white/10 shadow-2xl group perspective-1000"
                            whileHover={{
                                rotateY: 5,
                                rotateX: -5,
                                scale: 1.02,
                                transition: { duration: 0.3 }
                            }}
                            style={{ transformStyle: "preserve-3d" }}
                        >
                            {/* Glow ring around image */}
                            <div className="absolute -inset-2 bg-gradient-to-r from-primary/20 via-accent/20 to-primary/20 rounded-3xl blur-xl opacity-0 group-hover:opacity-60 transition-opacity duration-500 -z-10" />

                            <Image
                                src={profileImage}
                                alt="mdeangelis profile"
                                fill
                                placeholder="blur"
                                className="object-cover group-hover:scale-105 transition-transform duration-700"
                            />
                            {/* Subtle overlay on hover */}
                            <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                            {/* Badge */}
                            <motion.div
                                className="absolute bottom-4 right-4 bg-black/60 backdrop-blur-md px-4 py-2 rounded-full flex items-center gap-2 border border-white/10"
                                initial={{ y: 20, opacity: 0 }}
                                whileInView={{ y: 0, opacity: 1 }}
                                viewport={{ once: true }}
                                transition={{ delay: 0.5 }}
                            >
                                <Image src="/assets/icon_badge_visionary.png" width={24} height={24} alt="badge" />
                                <span className="text-white font-medium text-sm">{t("about.badge")}</span>
                            </motion.div>
                        </motion.div>

                        {/* Stats Cards */}
                        <div className="flex justify-center gap-4 mt-8">
                            {[
                                { target: 10, suffix: "+", label: t("about.stats.years"), delay: 0.2 },
                                { target: 50, suffix: "+", label: t("about.stats.projects"), delay: 0.3 },
                                { target: "∞", suffix: "", label: t("about.stats.curiosity"), delay: 0.4 }
                            ].map((stat, index) => (
                                <motion.div
                                    key={index}
                                    className="text-center px-6 py-4 rounded-xl bg-card/50 backdrop-blur-sm border border-border/50 hover:border-primary/50 hover:bg-primary/10 transition-all duration-300 group relative overflow-hidden"
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: stat.delay }}
                                    whileHover={{ y: -4, scale: 1.03 }}
                                >
                                    {/* Glow on hover */}
                                    <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-b from-primary/20 to-transparent blur-xl" />
                                    {typeof stat.target === "number" ? (
                                        <AnimatedCounter
                                            target={stat.target}
                                            suffix={stat.suffix}
                                            className="block text-3xl md:text-4xl font-bold text-primary group-hover:scale-125 transition-transform relative z-10"
                                        />
                                    ) : (
                                        <motion.span
                                            className="block text-3xl md:text-4xl font-bold text-primary relative z-10"
                                            animate={{ rotate: [0, 8, -8, 0], scale: [1, 1.1, 1] }}
                                            transition={{ duration: 2, repeat: Infinity, repeatDelay: 2 }}
                                        >
                                            {stat.target}
                                        </motion.span>
                                    )}
                                    <span className="text-xs md:text-sm text-muted-foreground mt-1 block relative z-10">{stat.label}</span>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>

                    {/* Right Column: Bio */}
                    <motion.div
                        initial={{ opacity: 0, x: 50 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="space-y-6"
                    >
                        <GlassCard className="p-10 border-l-[6px] border-l-primary bg-gradient-to-br from-primary/[0.08] to-transparent">
                            <p className="text-2xl font-medium italic text-foreground font-display leading-relaxed">&ldquo;{t("about.quote")}&rdquo;</p>
                        </GlassCard>

                        <div className="space-y-4 text-muted-foreground text-lg leading-relaxed">
                            <p>{bio.p1}</p>
                            <p>{bio.p2}</p>
                            <p>{bio.p3}</p>
                        </div>

                        <div className="pt-6">
                            <h4 className="text-xl font-semibold mb-4 flex items-center gap-2">
                                {t("about.interestsTitle")}
                                <Image src="/assets/icon_section_passions.png" width={24} height={24} alt="flame" />
                            </h4>
                            <div className="flex flex-wrap gap-2">
                                {tags.map((tag: string, index: number) => (
                                    <motion.span
                                        key={index}
                                        className="px-4 py-1.5 bg-primary/10 text-primary rounded-full text-sm font-medium border border-primary/20 hover:bg-primary/20 hover:scale-105 transition-all cursor-default"
                                        initial={{ opacity: 0, scale: 0.8 }}
                                        whileInView={{ opacity: 1, scale: 1 }}
                                        viewport={{ once: true }}
                                        transition={{ delay: index * 0.05 }}
                                    >
                                        {tag}
                                    </motion.span>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
}

