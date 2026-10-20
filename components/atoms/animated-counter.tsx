"use client";

import { useEffect, useRef, useState } from "react";
import { useInView } from "react-intersection-observer";

interface AnimatedCounterProps {
    target: number | string;
    duration?: number;
    suffix?: string;
    prefix?: string;
    className?: string;
}

export function AnimatedCounter({
    target,
    duration = 2000,
    suffix = "",
    prefix = "",
    className = ""
}: AnimatedCounterProps) {
    const [count, setCount] = useState(0);
    const { ref, inView } = useInView({
        threshold: 0.5,
        triggerOnce: true
    });
    const hasAnimated = useRef(false);

    // Handle special cases like "∞" or "50+"
    const isNumeric = typeof target === "number" || /^\d+$/.test(String(target));
    const numericTarget = isNumeric ? Number(target) : 0;

    useEffect(() => {
        if (inView && !hasAnimated.current && isNumeric) {
            hasAnimated.current = true;
            const startTime = Date.now();
            const endTime = startTime + duration;

            const animate = () => {
                const now = Date.now();
                const progress = Math.min((now - startTime) / duration, 1);

                // Easing function (ease-out-cubic)
                const eased = 1 - Math.pow(1 - progress, 3);
                const currentCount = Math.floor(eased * numericTarget);

                setCount(currentCount);

                if (now < endTime) {
                    requestAnimationFrame(animate);
                } else {
                    setCount(numericTarget);
                }
            };

            requestAnimationFrame(animate);
        }
    }, [inView, numericTarget, duration, isNumeric]);

    return (
        <span ref={ref} className={className}>
            {prefix}
            {isNumeric ? count : target}
            {suffix}
        </span>
    );
}
