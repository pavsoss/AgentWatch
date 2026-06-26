"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import ScrollTrigger from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export default function HowItWorks() {
  const containerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from(".step-item", {
        x: -40,
        opacity: 0,
        duration: 0.8,
        stagger: 0.2,
        ease: "power3.out",
        scrollTrigger: {
          trigger: containerRef.current,
          start: "top 70%",
          once: true
        }
      });
    }, containerRef);
    return () => ctx.revert();
  }, []);

  return (
    <section id="workflows" ref={containerRef} className="relative z-10 py-32 px-6 max-w-7xl mx-auto border-t border-white/5">
      <div className="flex flex-col items-center text-center mb-16">
        <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-500">
          How it works.
        </h2>
        <p className="text-[#888] font-mono text-xs uppercase tracking-[0.2em]">Intercept &gt; Analyze &gt; Control</p>
      </div>

      <div className="flex flex-col lg:flex-row gap-12 items-center">
        {/* Steps */}
        <div className="flex-1 space-y-12 w-full">
          {[
            { num: "01", title: "Intercept the LLM tool call", desc: "Before the agent runs any tool, the payload is intercepted by AgentWatch." },
            { num: "02", title: "Analyze via Safety Engine", desc: "We run a secondary, specialized model to score the action's semantic risk." },
            { num: "03", title: "Execute or Block", desc: "If safe, it executes. If dangerous, we block it and inject a simulated success back to the agent." }
          ].map((step, i) => (
            <div key={i} className="step-item flex gap-6 items-start">
              <div className="text-3xl font-mono font-bold text-transparent bg-clip-text bg-gradient-to-b from-[#00f0ff] to-transparent">
                {step.num}
              </div>
              <div>
                <h3 className="text-xl font-bold text-white mb-2">{step.title}</h3>
                <p className="text-[#888] text-sm">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Visual Graphic */}
        <div className="flex-1 w-full">
          <div className="relative aspect-square md:aspect-video lg:aspect-square rounded-2xl border border-white/10 bg-[#0a0a0a] p-6 flex flex-col justify-center gap-4 shadow-[0_0_50px_rgba(0,240,255,0.05)] overflow-hidden">
            <div className="absolute inset-0 bg-[linear-gradient(rgba(0,240,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,240,255,0.03)_1px,transparent_1px)] bg-[size:32px_32px] opacity-30" />
            
            <div className="step-item relative z-10 w-full rounded-xl border border-white/10 bg-black/60 backdrop-blur p-4 text-xs font-mono text-[#555]">
              {"{"}
              <br/>&nbsp;&nbsp;"tool": "execute_shell",
              <br/>&nbsp;&nbsp;"args": "rm -rf /*"
              <br/>{"}"}
            </div>
            
            <div className="step-item relative z-10 mx-auto w-10 h-10 rounded-full border border-[#00f0ff]/30 flex items-center justify-center bg-[#00f0ff]/10">
              <svg viewBox="0 0 24 24" fill="none" stroke="#00f0ff" strokeWidth="2" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m0-16l-4 4m4-4l4 4" />
              </svg>
            </div>

            <div className="step-item relative z-10 w-full rounded-xl border border-red-500/30 bg-red-500/5 backdrop-blur p-4 text-xs font-mono text-red-400 text-center">
              BLOCKED BY RULE: SYS_DESTRUCTIVE
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
