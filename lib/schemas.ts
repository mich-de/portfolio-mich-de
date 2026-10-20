import { z } from "zod";

export const contactFormSchema = z.object({
    name: z.string().min(2, { message: "Name must be at least 2 characters." }).max(100),
    email: z.string().email({ message: "Please enter a valid email address." }).max(254),
    message: z.string().min(10, { message: "Message must be at least 10 characters." }).max(5000),
});

export type ContactFormValues = z.infer<typeof contactFormSchema>;
