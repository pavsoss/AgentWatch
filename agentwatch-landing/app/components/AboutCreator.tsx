"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import ScrollTrigger from "gsap/ScrollTrigger";
import Image from "next/image";

gsap.registerPlugin(ScrollTrigger);

export default function AboutCreator() {
  const sectionRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;

    const ctx = gsap.context(() => {
      gsap.from(".about-content", {
        y: 30,
        opacity: 0,
        duration: 0.8,
        stagger: 0.15,
        ease: "power3.out",
        scrollTrigger: { trigger: sectionRef.current, start: "top 80%", once: true },
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      id="about-creator"
      ref={sectionRef}
      className="relative py-20 px-6 border-t border-white/5"
    >
      <div className="max-w-4xl mx-auto">
        <div className="spotlight-card p-8 md:p-12 about-content">
          <div className="spotlight-card-inner flex flex-col md:flex-row items-center gap-8">
            <div className="shrink-0 relative">
              <Image
                src="https://github.com/sreerevanth.png"
                alt="Creator Avatar"
                width={120}
                height={120}
                className="rounded-full border border-[#e8ff47]/20"
                unoptimized
              />
              <span className="absolute bottom-2 right-2 w-4 h-4 rounded-full bg-[#e8ff47] border-2 border-[#0d0d0d] animate-pulse-glow" />
            </div>
            <div className="text-center md:text-left flex-1">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-[#e8ff47]/20 bg-[#e8ff47]/5 mb-4">
                <span
                  className="text-[10px] uppercase tracking-[0.2em] text-[#e8ff47]"
                  style={{ fontFamily: "var(--font-jetbrains)" }}
                >
                  About the Creator
                </span>
              </div>
              <h2
                className="font-bold mb-4 text-[#e5e2e1]"
                style={{
                  fontFamily: "var(--font-syne)",
                  fontSize: "clamp(1.5rem, 3vw, 2rem)",
                  lineHeight: 1.2,
                }}
              >
                Building tools for a safer AI future.
              </h2>
              {/* Placeholder text, user will provide the actual text */}
              <p className="text-[#b8b8b8] text-base leading-relaxed mb-6">
                [This is a placeholder. Please paste the description here once provided.]
                I created AgentWatch to ensure that autonomous AI systems can operate safely without causing catastrophic damage. Our goal is to provide developers with the peace of mind they need to deploy powerful agents in production environments.
              </p>
              
              <div className="flex flex-wrap items-center justify-center md:justify-start gap-4">
                <a
                  href="https://github.com/sreerevanth"
                  target="_blank"
                  rel="noreferrer"
                  className="btn-magnetic px-5 py-2.5 rounded-lg border border-white/15 text-[#e5e2e1] hover:border-[#e8ff47]/50 hover:text-[#e8ff47] text-sm font-medium transition-colors"
                >
                  Follow on GitHub
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
