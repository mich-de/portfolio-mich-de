"use client";

import React from "react";
import { useLanguage } from "@/context/language-provider";
import { Button } from "@/components/ui/button";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export function LanguageSwitch() {
    const { language, setLanguage } = useLanguage();

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="w-[3rem] px-0">
                    <span className="uppercase font-bold">{language}</span>
                    <span className="sr-only">Toggle language</span>
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => setLanguage("it")}>
                    🇮🇹 Italiano
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setLanguage("en")}>
                    🇬🇧 English
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
}
