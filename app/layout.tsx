import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { ThemeProvider } from "@/context/theme-provider";
import { LanguageProvider } from "@/context/language-provider";
import { cn } from "@/lib/utils";
import { ScrollProgress } from "@/components/atoms/scroll-progress";
import { CursorGlow } from "@/components/atoms/cursor-glow";
import { BackToTop } from "@/components/atoms/back-to-top";
import { Preloader } from "@/components/atoms/preloader";

const kamerik = localFont({
  src: "./fonts/kamerik.woff2",
  variable: "--font-kamerik",
  weight: "400",
  display: "swap",
});

const unitext = localFont({
  src: "./fonts/unitext.woff2",
  variable: "--font-unitext",
  weight: "400",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://mdeangelis.me"),
  title: {
    default: "MDEANGELIS | IT Professional & Visionary",
    template: "%s | MDEANGELIS"
  },
  description: "IT Professional, Technology Enthusiast & Music Producer. Exploring the digital world and real life with curiosity and passion.",
  keywords: ["IT Professional", "Technology", "Music Producer", "Developer", "mdeangelis", "Full Stack", "Software Engineer", "Italy"],
  authors: [{ name: "mdeangelis", url: "https://mdeangelis.me" }],
  creator: "mdeangelis",
  publisher: "mdeangelis",
  alternates: {
    canonical: "https://mdeangelis.me",
    languages: {
      "it-IT": "https://mdeangelis.me",
      "en-US": "https://mdeangelis.me",
    },
  },
  openGraph: {
    type: "website",
    locale: "it_IT",
    alternateLocale: "en_US",
    url: "https://mdeangelis.me",
    siteName: "MDEANGELIS",
    title: "MDEANGELIS | IT Professional & Visionary",
    description: "IT Professional, Technology Enthusiast & Music Producer. Exploring the digital world and real life with curiosity and passion.",
    images: [
      {
        url: "/assets/logo.jpg",
        width: 1200,
        height: 630,
        alt: "MDEANGELIS - IT Professional & Technology Enthusiast",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "MDEANGELIS | IT Professional & Visionary",
    description: "IT Professional, Technology Enthusiast & Music Producer.",
    images: ["/assets/logo.jpg"],
    creator: "@mdeangelis",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  verification: {
    // Add your verification codes when available
    // google: "your-google-verification-code",
  },
};

// JSON-LD Structured Data for Person/ProfilePage
const jsonLd = {
  "@context": "https://schema.org",
  "@type": "Person",
  name: "mdeangelis",
  url: "https://mdeangelis.me",
  image: "https://mdeangelis.me/assets/logo.jpg",
  jobTitle: "IT Professional",
  description: "IT Professional, Technology Enthusiast & Music Producer",
  sameAs: [
    "https://instagram.com/mdeangelis_official",
    "https://music.youtube.com/channel/UCYJ3e3Ho1Jv2o2NhuI3JO7A",
    "https://open.spotify.com/artist/3OucxkLy5uqnpSEHavZbpe",
    "https://soundcloud.com/mdeangelis",
  ],
  knowsAbout: ["Software Development", "Technology", "Music Production", "AI", "Programming"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="it" suppressHydrationWarning>
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased",
          kamerik.variable,
          unitext.variable
        )}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange={false}
        >
          <LanguageProvider>
            <Preloader />
            <ScrollProgress />
            <CursorGlow />
            {children}
            <BackToTop />
          </LanguageProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
