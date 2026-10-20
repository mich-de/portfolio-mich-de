"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { en, it, Dictionary } from "@/utils/dictionaries";

type Language = "en" | "it";

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
    dictionary: Dictionary;
    t: (key: string) => string; // Simple dot-notation accessor
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

function getInitialLanguage(): Language {
    if (typeof window !== "undefined") {
        const saved = localStorage.getItem("language") as Language;
        if (saved === "en" || saved === "it") return saved;
    }
    return "it";
}

export function LanguageProvider({ children }: { children: React.ReactNode }) {
    const [language, setLanguage] = useState<Language>(getInitialLanguage);

    const dictionary: Dictionary = language === "en" ? en : it;

    useEffect(() => {
        localStorage.setItem("language", language);
        document.documentElement.lang = language;
    }, [language]);

    const t = (path: string): string => {
        return path.split(".").reduce<Record<string, unknown> | string>((obj, key) => {
            return obj && typeof obj === "object" && key in obj ? (obj as Record<string, unknown>)[key] as string : path;
        }, dictionary as unknown as Record<string, unknown>) as string;
    };

    return (
        <LanguageContext.Provider value={{ language, setLanguage, dictionary, t }}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    const context = useContext(LanguageContext);
    if (context === undefined) {
        throw new Error("useLanguage must be used within a LanguageProvider");
    }
    return context;
}
