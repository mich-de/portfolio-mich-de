"use client";

import { Navbar } from "@/components/organisms/navbar";
import { HeroSection } from "@/components/organisms/hero-section";
import { AboutSection } from "@/components/organisms/about-section";
import { InterestsSection } from "@/components/organisms/interests-section";
import { ContactSection } from "@/components/organisms/contact-section";
import { Footer } from "@/components/organisms/footer";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col overflow-x-hidden selection:bg-primary/20">
      <Navbar />
      <HeroSection />
      <AboutSection />
      <InterestsSection />
      <ContactSection />
      <Footer />
    </main>
  );
}
