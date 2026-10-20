"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

export function CursorGlow() {
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
    const [isVisible, setIsVisible] = useState(false);
    const [isHovering, setIsHovering] = useState(false);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            setMousePosition({ x: e.clientX, y: e.clientY });
            setIsVisible(true);
        };

        const handleMouseLeave = () => {
            setIsVisible(false);
        };

        // Detect hover on interactive elements
        const handleMouseOver = (e: MouseEvent) => {
            const target = e.target as HTMLElement;
            const isInteractive = target.closest('a, button, [role="button"], input, [data-magnetic]');
            setIsHovering(!!isInteractive);
        };

        window.addEventListener("mousemove", handleMouseMove);
        document.body.addEventListener("mouseleave", handleMouseLeave);
        document.addEventListener("mouseover", handleMouseOver);

        return () => {
            window.removeEventListener("mousemove", handleMouseMove);
            document.body.removeEventListener("mouseleave", handleMouseLeave);
            document.removeEventListener("mouseover", handleMouseOver);
        };
    }, []);

    // Don't render on touch devices
    if (typeof window !== "undefined" && "ontouchstart" in window) {
        return null;
    }

    return (
        <motion.div
            className="pointer-events-none fixed inset-0 z-30 overflow-hidden hidden md:block"
            initial={{ opacity: 0 }}
            animate={{ opacity: isVisible ? 1 : 0 }}
            transition={{ duration: 0.3 }}
        >
            {/* Outer glow - larger and softer */}
            <motion.div
                className="absolute rounded-full"
                style={{
                    width: isHovering ? 500 : 400,
                    height: isHovering ? 500 : 400,
                    background: "radial-gradient(circle, rgba(251, 146, 60, 0.06) 0%, transparent 70%)",
                    x: mousePosition.x - (isHovering ? 250 : 200),
                    y: mousePosition.y - (isHovering ? 250 : 200),
                }}
                transition={{
                    type: "spring",
                    damping: 25,
                    stiffness: 150,
                    mass: 0.5
                }}
            />
            {/* Inner accent glow - smaller and more vibrant */}
            <motion.div
                className="absolute rounded-full"
                style={{
                    width: isHovering ? 200 : 150,
                    height: isHovering ? 200 : 150,
                    background: "radial-gradient(circle, rgba(251, 146, 60, 0.12) 0%, transparent 60%)",
                    x: mousePosition.x - (isHovering ? 100 : 75),
                    y: mousePosition.y - (isHovering ? 100 : 75),
                }}
                transition={{
                    type: "spring",
                    damping: 35,
                    stiffness: 250,
                    mass: 0.3
                }}
            />
        </motion.div>
    );
}
