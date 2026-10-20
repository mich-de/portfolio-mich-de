"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import { useLanguage } from "@/context/language-provider";

// Interest data - using custom 3D icons from /assets/
const interestData = {
    it: [
        {
            id: "informatica",
            icon: "/assets/icon_home.png", // Computer/home icon
            title: "Informatica",
            modalTitle: "Informatica & Architetture",
            description: "Architetture, sistemi e sicurezza",
            content: `
        <p>L'informatica è il mio linguaggio naturale. Non mi limito a utilizzare gli strumenti, ma cerco di comprenderne i meccanismi profondi. Dalle architetture dei sistemi distribuiti alla sicurezza informatica, ogni aspetto è una sfida intellettuale.</p>
        <p>Mi affascina progettare soluzioni scalabili e robuste, ottimizzando le risorse e garantendo la continuità operativa. Per me, un sistema informatico ben progettato è un'opera d'arte funzionale.</p>
      `
        },
        {
            id: "tecnologia",
            icon: "/assets/icon_tech.png",
            title: "Tecnologia",
            modalTitle: "Frontiera Tecnologica",
            description: "Hardware, IoT e innovazione",
            content: `
        <p>Vivo immerso nell'innovazione. Seguo costantemente l'evoluzione dell'hardware e del software, dai processori di nuova generazione ai dispositivi IoT che rendono le nostre case intelligenti.</p>
        <p>La tecnologia non è solo gadget, ma uno strumento per migliorare la qualità della vita. Sperimento con domotica, wearable tech e realtà aumentata per esplorare come il digitale possa fondersi armoniosamente con il fisico.</p>
      `
        },
        {
            id: "programmazione",
            icon: "/assets/icon_programming.png",
            title: "Programmazione",
            modalTitle: "Arte del Codice",
            description: "Clean Code e Best Practices",
            content: `
        <p>Scrivere codice è come comporre musica: richiede tecnica, creatività e struttura. Sono uno sviluppatore appassionato di Clean Code e Best Practices.</p>
        <p>I miei linguaggi e framework di riferimento includono JavaScript (React, Node.js), Python per automazione e AI, e CSS moderno per UI spettacolari. Amo risolvere problemi algoritmici complessi e trasformare idee astratte in software funzionante.</p>
      `
        },
        {
            id: "ai",
            icon: "/assets/icon_ai.png",
            title: "Intelligenza Artificiale",
            modalTitle: "AI & Machine Learning",
            description: "LLM, reti neurali e etica AI",
            content: `
        <p>L'Intelligenza Artificiale è la rivoluzione del nostro tempo. Studio i Large Language Models, le reti neurali e le applicazioni generative che stanno ridefinendo la creatività e il lavoro.</p>
        <p>Mi interesso non solo agli aspetti tecnici, ma anche all'etica dell'AI e al suo impatto sociale. Utilizzo strumenti AI quotidianamente per potenziare la produttività ed esplorare nuove frontiere creative.</p>
      `
        },
        {
            id: "viaggi",
            icon: "/assets/icon_travel.png",
            title: "Viaggi",
            modalTitle: "Esplorazione Globale",
            description: "Scoprire il mondo e nuove culture",
            content: `
        <p>Viaggiare è l'unica cosa che compri e che ti rende più ricco. Ogni destinazione è un'opportunità per uscire dalla comfort zone e vedere il mondo con occhi diversi.</p>
        <p>Amo sia le metropoli frenetiche che i paesaggi naturali incontaminati. Ogni viaggio è documentato con foto e appunti, costruendo un bagaglio di esperienze che influenza anche il mio approccio al lavoro e alla vita.</p>
      `
        },
        {
            id: "passeggiate",
            icon: "/assets/icon_walks.png",
            title: "Passeggiate",
            modalTitle: "Walking & Thinking",
            description: "Debugging mentale e chiarezza",
            content: `
        <p>Solvitur ambulando: camminando si risolve. Le lunghe passeggiate sono il mio metodo preferito per il debugging mentale. Immerso nella natura o tra le vie cittadine, trovo chiarezza e nuove idee.</p>
        <p>È un momento di disconnessione digitale e riconnessione con il mondo reale, essenziale per mantenere l'equilibrio e la creatività.</p>
      `
        },
        {
            id: "lettura",
            icon: "/assets/icon_reading.png",
            title: "Lettura",
            modalTitle: "Biblioteca Mentale",
            description: "Life-long Learning",
            content: `
        <p>I libri sono portali verso altre menti. La mia libreria spazia dalla saggistica tecnica alla fantascienza speculativa, dalla filosofia alla biografia di grandi innovatori.</p>
        <p>Credo nell'apprendimento continuo (Life-long Learning) e la lettura è il carburante principale per la mia crescita personale e professionale.</p>
      `
        },
        {
            id: "musica",
            icon: "/assets/icon_music.png",
            title: "Musica",
            modalTitle: "Soundscapes & Ritmo",
            description: "Produzione e sound design",
            content: `
        <p>La musica è matematica emotiva. Ascolto una vasta gamma di generi, dall'elettronica ambient al jazz, cercando sempre sonorità che stimolino l'immaginazione.</p>
        <p>Mi diletto anche nella produzione musicale digitale, esplorando sintetizzatori e sound design. La musica accompagna ogni mia sessione di coding, dettando il ritmo del flusso di lavoro.</p>
      `,
            links: [
                { label: "Spotify", icon: "/assets/icon_music_spotify.png", href: "https://open.spotify.com/intl-it/artist/3OucxkLy5uqnpSEHavZbpe", color: "#1DB954" },
                { label: "Apple Music", icon: "/assets/icon_music_applemusic.png", href: "https://music.apple.com/us/artist/mdeangelis/1796261710", color: "#FC3C44" },
                { label: "YouTube", icon: "/assets/icon_social_youtube.png", href: "https://music.youtube.com/watch?v=KHAmgXV0C3E&si=NrSRWKvDqQhWrx_g", color: "#FF0000" },
                { label: "SoundCloud", icon: "/assets/icon_music_soundcloud.png", href: "https://soundcloud.com/mdeangelis", color: "#FF5500" }
            ]
        },
        {
            id: "cultura",
            icon: "/assets/icon_culture.png",
            title: "Cultura",
            modalTitle: "Arte & Storia",
            description: "Musei, cinema e pensiero laterale",
            content: `
        <p>La tecnologia senza cultura è vuota. Mi nutro di arte, cinema, teatro e storia per comprendere il contesto umano in cui operiamo.</p>
        <p>Visitare musei, assistere a mostre e approfondire periodi storici mi aiuta a sviluppare un pensiero laterale fondamentale per l'innovazione creativa.</p>
      `
        },
        {
            id: "amici",
            icon: "/assets/icon_friends.png",
            title: "Amici",
            modalTitle: "Connessioni Autentiche",
            description: "La famiglia che scegliamo",
            content: `
        <p>In un mondo iperconnesso digitalmente, il valore di un abbraccio, di una risata condivisa e di una presenza fisica è inestimabile.</p>
        <p>Investo tempo ed energia nelle relazioni, organizzando incontri e mantenendo viva la rete sociale reale. Gli amici sono la famiglia che ci scegliamo.</p>
      `
        },
        {
            id: "cibo",
            icon: "/assets/icon_food.png",
            title: "Buon Cibo",
            modalTitle: "Gastronomia & Gusto",
            description: "Cultura commestibile",
            content: `
        <p>Il cibo è cultura commestibile. Sono un appassionato gourmet che ama esplorare ristoranti e trattorie alla ricerca di sapori autentici.</p>
        <p>Mi piace anche cucinare, sperimentando ricette e tecniche. La cucina, come il codice, richiede ingredienti di qualità, processi precisi e un tocco di creatività personale.</p>
      `
        },
        {
            id: "vini",
            icon: "/assets/icon_wine.png",
            title: "Vini",
            modalTitle: "Enologia & Passione",
            description: "Vitigni, terroir e degustazioni",
            content: `
        <p>Il vino è poesia imbottigliata. La mia passione enologica mi porta a studiare vitigni, terroir e tecniche di vinificazione.</p>
        <p>Amo partecipare a degustazioni e visitare cantine, scoprendo le storie dei produttori. Un buon calice è il compagno perfetto per una conversazione profonda o un momento di relax.</p>
      `
        },
        {
            id: "conversazioni",
            icon: "/assets/icon_conversation.png",
            title: "Conversazioni",
            modalTitle: "Dialettica & Scambio",
            description: "Dibattiti e confronti costruttivi",
            content: `
        <p>Le grandi idee nascono dal confronto. Adoro le lunghe conversazioni notturne, i dibattiti costruttivi e lo scambio di punti di vista.</p>
        <p>Saper ascoltare è importante quanto saper parlare. Cerco sempre interlocutori che possano sfidare le mie convinzioni e arricchire la mia visione del mondo.</p>
      `
        },
        {
            id: "lingue",
            icon: "/assets/icon_languages.png",
            title: "Lingue",
            modalTitle: "Poliglotta",
            description: "Italiano, Inglese e oltre",
            content: `
        <p>Ogni lingua è una diversa visione della realtà. Parlo fluentemente Italiano e Inglese, e mi diverto a esplorare le basi di altre lingue.</p>
        <p>Imparare una lingua significa aprire una porta verso una nuova cultura, un nuovo modo di pensare e nuove opportunità di connessione umana.</p>
      `
        }
    ],
    en: [
        {
            id: "informatica",
            icon: "/assets/icon_home.png",
            title: "Computer Science",
            modalTitle: "Computer Science & Architectures",
            description: "Architectures, systems and security",
            content: `
        <p>Computer science is my native language. I don't just use tools; I seek to understand their deep mechanisms. From distributed systems architectures to cybersecurity, every aspect is an intellectual challenge.</p>
        <p>I'm fascinated by designing scalable and robust solutions, optimizing resources and ensuring operational continuity. For me, a well-designed computer system is a functional work of art.</p>
      `
        },
        {
            id: "tecnologia",
            icon: "/assets/icon_tech.png",
            title: "Technology",
            modalTitle: "Technology Frontier",
            description: "Hardware, IoT and innovation",
            content: `
        <p>I live immersed in innovation. I constantly follow the evolution of hardware and software, from next-generation processors to IoT devices that make our homes smart.</p>
        <p>Technology is not just gadgets, but a tool to improve quality of life. I experiment with home automation, wearable tech and augmented reality to explore how digital can harmoniously merge with physical.</p>
      `
        },
        {
            id: "programmazione",
            icon: "/assets/icon_programming.png",
            title: "Programming",
            modalTitle: "The Art of Code",
            description: "Clean Code and Best Practices",
            content: `
        <p>Writing code is like composing music: it requires technique, creativity and structure. I'm a developer passionate about Clean Code and Best Practices.</p>
        <p>My reference languages and frameworks include JavaScript (React, Node.js), Python for automation and AI, and modern CSS for spectacular UIs. I love solving complex algorithmic problems and turning abstract ideas into working software.</p>
      `
        },
        {
            id: "ai",
            icon: "/assets/icon_ai.png",
            title: "Artificial Intelligence",
            modalTitle: "AI & Machine Learning",
            description: "LLMs, neural networks and AI ethics",
            content: `
        <p>Artificial Intelligence is the revolution of our time. I study Large Language Models, neural networks and generative applications that are redefining creativity and work.</p>
        <p>I'm interested not only in technical aspects, but also in AI ethics and its social impact. I use AI tools daily to boost productivity and explore new creative frontiers.</p>
      `
        },
        {
            id: "viaggi",
            icon: "/assets/icon_travel.png",
            title: "Travel",
            modalTitle: "Global Exploration",
            description: "Discovering the world and new cultures",
            content: `
        <p>Travel is the only thing you buy that makes you richer. Every destination is an opportunity to step out of the comfort zone and see the world with different eyes.</p>
        <p>I love both frenetic metropolises and pristine natural landscapes. Every trip is documented with photos and notes, building a wealth of experiences that also influences my approach to work and life.</p>
      `
        },
        {
            id: "passeggiate",
            icon: "/assets/icon_walks.png",
            title: "Walking",
            modalTitle: "Walking & Thinking",
            description: "Mental debugging and clarity",
            content: `
        <p>Solvitur ambulando: it is solved by walking. Long walks are my favorite method for mental debugging. Immersed in nature or among city streets, I find clarity and new ideas.</p>
        <p>It's a moment of digital disconnection and reconnection with the real world, essential for maintaining balance and creativity.</p>
      `
        },
        {
            id: "lettura",
            icon: "/assets/icon_reading.png",
            title: "Reading",
            modalTitle: "Mental Library",
            description: "Life-long Learning",
            content: `
        <p>Books are portals to other minds. My library ranges from technical nonfiction to speculative science fiction, from philosophy to biographies of great innovators.</p>
        <p>I believe in continuous learning (Life-long Learning) and reading is the main fuel for my personal and professional growth.</p>
      `
        },
        {
            id: "musica",
            icon: "/assets/icon_music.png",
            title: "Music",
            modalTitle: "Soundscapes & Rhythm",
            description: "Production and sound design",
            content: `
        <p>Music is emotional mathematics. I listen to a wide range of genres, from ambient electronica to jazz, always looking for sounds that stimulate the imagination.</p>
        <p>I also dabble in digital music production, exploring synthesizers and sound design. Music accompanies every coding session, setting the rhythm of the workflow.</p>
      `,
            links: [
                { label: "Spotify", icon: "/assets/icon_music_spotify_v6.png", href: "https://open.spotify.com/intl-it/artist/3OucxkLy5uqnpSEHavZbpe", color: "#1DB954" },
                { label: "Apple Music", icon: "/assets/icon_music_applemusic.png", href: "https://music.apple.com/us/artist/mdeangelis/1796261710", color: "#FC3C44" },
                { label: "YouTube", icon: "/assets/icon_social_youtube.png", href: "https://music.youtube.com/watch?v=KHAmgXV0C3E&si=NrSRWKvDqQhWrx_g", color: "#FF0000" },
                { label: "SoundCloud", icon: "/assets/icon_music_soundcloud.png", href: "https://soundcloud.com/mdeangelis", color: "#FF5500" }
            ]
        },
        {
            id: "cultura",
            icon: "/assets/icon_culture.png",
            title: "Culture",
            modalTitle: "Art & History",
            description: "Museums, cinema and lateral thinking",
            content: `
        <p>Technology without culture is empty. I nourish myself with art, cinema, theater and history to understand the human context in which we operate.</p>
        <p>Visiting museums, attending exhibitions and exploring historical periods helps me develop lateral thinking fundamental to creative innovation.</p>
      `
        },
        {
            id: "amici",
            icon: "/assets/icon_friends.png",
            title: "Friends",
            modalTitle: "Authentic Connections",
            description: "The family we choose",
            content: `
        <p>In a digitally hyperconnected world, the value of a hug, a shared laugh and physical presence is priceless.</p>
        <p>I invest time and energy in relationships, organizing gatherings and keeping the real social network alive. Friends are the family we choose.</p>
      `
        },
        {
            id: "cibo",
            icon: "/assets/icon_food.png",
            title: "Good Food",
            modalTitle: "Gastronomy & Taste",
            description: "Edible culture",
            content: `
        <p>Food is edible culture. I'm a passionate gourmet who loves exploring restaurants and trattorias in search of authentic flavors.</p>
        <p>I also enjoy cooking, experimenting with recipes and techniques. Cooking, like code, requires quality ingredients, precise processes and a touch of personal creativity.</p>
      `
        },
        {
            id: "vini",
            icon: "/assets/icon_wine.png",
            title: "Wines",
            modalTitle: "Enology & Passion",
            description: "Grape varieties, terroir and tastings",
            content: `
        <p>Wine is bottled poetry. My enological passion leads me to study grape varieties, terroir and winemaking techniques.</p>
        <p>I love attending tastings and visiting wineries, discovering the stories of producers. A good glass is the perfect companion for a deep conversation or a moment of relaxation.</p>
      `
        },
        {
            id: "conversazioni",
            icon: "/assets/icon_conversation.png",
            title: "Conversations",
            modalTitle: "Dialectics & Exchange",
            description: "Debates and constructive discussions",
            content: `
        <p>Great ideas are born from confrontation. I love long nighttime conversations, constructive debates and exchange of viewpoints.</p>
        <p>Knowing how to listen is as important as knowing how to speak. I always seek interlocutors who can challenge my beliefs and enrich my worldview.</p>
      `
        },
        {
            id: "lingue",
            icon: "/assets/icon_languages.png",
            title: "Languages",
            modalTitle: "Polyglot",
            description: "Italian, English and beyond",
            content: `
        <p>Each language is a different vision of reality. I speak Italian and English fluently, and I enjoy exploring the basics of other languages.</p>
        <p>Learning a language means opening a door to a new culture, a new way of thinking and new opportunities for human connection.</p>
      `
        }
    ]
};

type Interest = typeof interestData.it[0];

const expandText = (isIt: boolean) => isIt ? "Scopri di più" : "Discover more";
const listenText = (isIt: boolean) => isIt ? "Ascolta le mie produzioni:" : "Listen to my productions:";

// Bento grid size mapping - larger cards for featured items
const getBentoSize = (index: number): string => {
    // First 4 items are "featured" with larger sizes
    if (index === 0) return "col-span-2 row-span-2"; // Informatica - large
    if (index === 1) return "col-span-1 row-span-2"; // Tecnologia - tall
    if (index === 2) return "col-span-1 row-span-1"; // Programmazione
    if (index === 3) return "col-span-2 row-span-1"; // AI - wide
    if (index === 7) return "col-span-2 row-span-1"; // Musica - wide (has links)
    return "col-span-1 row-span-1"; // Standard
};

// Interest Card Component with Spotlight Effect
function InterestCard({
    interest,
    onClick,
    index,
    isIt
}: {
    interest: Interest;
    onClick: () => void;
    index: number;
    isIt: boolean;
}) {
    const bentoSize = getBentoSize(index);
    const isLarge = bentoSize.includes("col-span-2") || bentoSize.includes("row-span-2");

    // Handle mouse move for spotlight effect
    const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        e.currentTarget.style.setProperty("--mouse-x", `${x}%`);
        e.currentTarget.style.setProperty("--mouse-y", `${y}%`);
    };

    return (
        <motion.div
            className={`${bentoSize} interesse-card spotlight-card p-5 card-3d flex flex-col items-center justify-center text-center group cursor-pointer relative overflow-hidden`}
            onClick={onClick}
            onMouseMove={handleMouseMove}
            whileHover={{ scale: 1.02, y: -4 }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: 40, scale: 0.95 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, margin: "-30px" }}
            transition={{
                duration: 0.5,
                delay: index * 0.04,
                type: "spring",
                stiffness: 100,
                damping: 15
            }}
        >
            {/* Gradient border on hover */}
            <div className="absolute inset-0 rounded-[inherit] p-px bg-gradient-to-br from-primary/0 via-primary/0 to-primary/0 group-hover:from-primary/30 group-hover:via-accent/20 group-hover:to-primary/30 transition-all duration-500 -z-10" />

            {/* Inner glow */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary/0 to-accent/0 group-hover:from-primary/5 group-hover:to-accent/5 transition-all duration-500 rounded-[inherit]" />

            {/* 3D Icon with enhanced animation */}
            <motion.div
                className={`relative ${isLarge ? 'w-20 h-20 mb-5' : 'w-14 h-14 mb-3'} transition-all duration-300`}
                whileHover={{ rotate: [0, -5, 5, 0], scale: 1.15 }}
                transition={{ duration: 0.5 }}
            >
                <Image
                    src={interest.icon}
                    alt={interest.title}
                    fill
                    className="object-contain drop-shadow-lg group-hover:drop-shadow-[0_8px_16px_rgba(251,146,60,0.3)] transition-all duration-300"
                    sizes={isLarge ? "80px" : "56px"}
                />
            </motion.div>

            <h3
                className={`${isLarge ? 'text-lg' : 'text-base'} font-semibold text-foreground mb-1 group-hover:text-primary transition-colors duration-300`}
            >
                {interest.title}
            </h3>
            <p className={`${isLarge ? 'text-sm' : 'text-xs'} text-muted-foreground line-clamp-2 group-hover:text-muted-foreground/80 transition-colors`}>
                {interest.description}
            </p>

            {/* "Click to expand" indicator for large cards */}
            {isLarge && (
                <motion.div
                    className="absolute bottom-3 right-3 flex items-center gap-1 text-xs text-muted-foreground/50 group-hover:text-primary/70 transition-colors"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                >
                    <span className="hidden sm:inline">{expandText(isIt)}</span>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                </motion.div>
            )}
        </motion.div>
    );
}

// Interest Modal Component
function InterestModal({
    isOpen,
    onClose,
    interest,
    isIt
}: {
    isOpen: boolean;
    onClose: () => void;
    interest: Interest | null;
    isIt: boolean;
}) {
    if (!interest) return null;

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    className="fixed inset-0 z-50 flex items-center justify-center p-4"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.2 }}
                >
                    {/* Backdrop */}
                    <motion.div
                        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                        onClick={onClose}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                    />

                    {/* Modal Content — dramatic entrance */}
                    <motion.div
                        className="relative z-10 w-full max-w-lg max-h-[85vh] overflow-y-auto bg-card border border-border/50 rounded-2xl shadow-2xl"
                        initial={{ scale: 0.7, rotateY: -15, y: 40, opacity: 0 }}
                        animate={{ scale: 1, rotateY: 0, y: 0, opacity: 1 }}
                        exit={{ scale: 0.7, rotateY: 15, y: 40, opacity: 0 }}
                        transition={{ type: "spring", damping: 20, stiffness: 260 }}
                        onClick={(e) => e.stopPropagation()}
                        style={{ perspective: 1000 }}
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between p-6 border-b border-border">
                            <div className="flex items-center gap-4">
                                <div className="relative w-12 h-12">
                                    <Image
                                        src={interest.icon}
                                        alt={interest.modalTitle}
                                        fill
                                        className="object-contain"
                                        sizes="48px"
                                    />
                                </div>
                                <h2
                                    className="text-xl font-bold text-foreground glitch-hover"
                                    data-text={interest.modalTitle}
                                >
                                    {interest.modalTitle}
                                </h2>
                            </div>
                            <button
                                onClick={onClose}
                                className="w-9 h-9 flex items-center justify-center rounded-full bg-muted hover:bg-primary hover:text-primary-foreground transition-colors"
                                aria-label="Close modal"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Body */}
                        <div
                            className="p-6 text-muted-foreground leading-relaxed [&_p]:mb-4 [&_p:last-child]:mb-0"
                            dangerouslySetInnerHTML={{ __html: interest.content }}
                        />

                        {/* Music Links (if applicable) */}
                        {interest.links && (
                            <div className="px-6 pb-6 pt-2 border-t border-border mt-2">
                                <p className="text-sm font-semibold text-foreground mb-4">🎧 {listenText(isIt)}</p>
                                <div className="grid grid-cols-2 gap-4">
                                    {interest.links.map((link) => (
                                        <a
                                            key={link.label}
                                            href={link.href}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="interesse-card card-3d flex flex-col items-center justify-center p-4 group transition-all"
                                            style={{
                                                "--primary": link.color
                                            } as React.CSSProperties}
                                        >
                                            <div className="relative w-10 h-10 mb-2 transition-transform duration-300 group-hover:scale-110">
                                                <Image
                                                    src={link.icon}
                                                    alt={link.label}
                                                    fill
                                                    className="object-contain drop-shadow-md"
                                                    sizes="40px"
                                                />
                                            </div>
                                            <span className="text-sm font-semibold text-foreground group-hover:text-primary transition-colors">
                                                {link.label}
                                            </span>
                                        </a>
                                    ))}
                                </div>
                            </div>
                        )}
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}

// Main Interests Section
export function InterestsSection() {
    const { language } = useLanguage();
    const [selectedInterest, setSelectedInterest] = useState<Interest | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const isIt = language === "it";
    const interests = isIt ? interestData.it : interestData.en;
    const itxt = { title: isIt ? "I Miei Interessi" : "My Interests", desc: isIt ? "Passioni che alimentano la mia creatività e guidano il mio percorso professionale e personale." : "Passions that fuel my creativity and guide my professional and personal journey." };

    useEffect(() => {
        document.body.style.overflow = isModalOpen ? "hidden" : "";
        return () => { document.body.style.overflow = ""; };
    }, [isModalOpen]);

    const openModal = (interest: Interest) => {
        setSelectedInterest(interest);
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
    };

    return (
        <section id="interests" className="px-6">
            <div className="section-container container mx-auto max-w-6xl">
                {/* Section Header */}
                <motion.div
                    className="text-center mb-16"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                >
                    <div className="flex items-center justify-center gap-3 mb-4">
                        <Image
                            src="/assets/icon_section_passions.png"
                            alt=""
                            width={48}
                            height={48}
                            className="object-contain"
                        />
                        <h2 className="heading-2">
                            {itxt.title}
                        </h2>
                    </div>
                    <p className="text-muted-foreground max-w-2xl mx-auto">
                        {itxt.desc}
                    </p>
                </motion.div>

                {/* Bento Interest Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 auto-rows-[minmax(140px,auto)]">
                    {interests.map((interest, index) => (
                        <InterestCard
                            key={interest.id}
                            interest={interest}
                            onClick={() => openModal(interest)}
                            index={index}
                            isIt={isIt}
                        />
                    ))}
                </div>
            </div>

            {/* Modal */}
            <InterestModal
                isOpen={isModalOpen}
                onClose={closeModal}
                interest={selectedInterest}
                isIt={isIt}
            />
        </section>
    );
}
