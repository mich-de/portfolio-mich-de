"use server";

import { headers } from "next/headers";
import { contactFormSchema } from "@/lib/schemas";

export type ActionState = {
    success?: boolean;
    errors?: { [key: string]: string[] };
    message?: string;
};

const rateLimitMap = new Map<string, { count: number; resetAt: number }>();
const RATE_LIMIT_WINDOW = 60_000; // 1 minute
const RATE_LIMIT_MAX = 3;

function checkRateLimit(ip: string): boolean {
    const now = Date.now();
    const entry = rateLimitMap.get(ip);
    if (!entry || now > entry.resetAt) {
        rateLimitMap.set(ip, { count: 1, resetAt: now + RATE_LIMIT_WINDOW });
        return true;
    }
    if (entry.count >= RATE_LIMIT_MAX) return false;
    entry.count++;
    return true;
}

export async function sendContactMessage(prevState: ActionState, formData: FormData): Promise<ActionState> {
    const headersList = await headers();
    const ip = headersList.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";

    if (!checkRateLimit(ip)) {
        return {
            success: false,
            message: "Too many requests. Please wait before sending another message.",
        };
    }

    const rawData = {
        name: formData.get("name"),
        email: formData.get("email"),
        message: formData.get("message"),
    };

    const validatedFields = contactFormSchema.safeParse(rawData);

    if (!validatedFields.success) {
        return {
            success: false,
            errors: validatedFields.error.flatten().fieldErrors,
            message: "Please fix the errors below.",
        };
    }

    console.log("Server Action Received:", validatedFields.data);

    await new Promise((resolve) => setTimeout(resolve, 1000));

    return {
        success: true,
        message: "Message sent successfully!",
    };
}
