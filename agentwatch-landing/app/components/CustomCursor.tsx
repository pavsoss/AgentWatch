"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

export default function CustomCursor() {
  const [mousePosition, setMousePosition] = useState({ x: -100, y: -100 });
  const [isHovering, setIsHovering] = useState(false);
  const [isClicking, setIsClicking] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Only run on non-touch devices
    if (window.matchMedia("(pointer: coarse)").matches) return;

    const updateMousePosition = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
      if (!isVisible) setIsVisible(true);
    };

    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      // Traverse up to check if a parent is clickable
      let current: HTMLElement | null = target;
      let clickable = false;
      
      while (current && current !== document.body) {
        if (
          window.getComputedStyle(current).cursor === "pointer" ||
          current.tagName.toLowerCase() === "a" ||
          current.tagName.toLowerCase() === "button" ||
          current.onclick !== null
        ) {
          clickable = true;
          break;
        }
        current = current.parentElement;
      }
      
      setIsHovering(clickable);
    };

    const handleMouseDown = () => setIsClicking(true);
    const handleMouseUp = () => setIsClicking(false);
    const handleMouseLeave = () => setIsVisible(false);
    const handleMouseEnter = () => setIsVisible(true);

    window.addEventListener("mousemove", updateMousePosition);
    window.addEventListener("mouseover", handleMouseOver);
    window.addEventListener("mousedown", handleMouseDown);
    window.addEventListener("mouseup", handleMouseUp);
    document.body.addEventListener("mouseleave", handleMouseLeave);
    document.body.addEventListener("mouseenter", handleMouseEnter);

    // Hide default cursor globally
    const style = document.createElement("style");
    style.innerHTML = `
      * { cursor: none !important; }
    `;
    document.head.appendChild(style);

    return () => {
      window.removeEventListener("mousemove", updateMousePosition);
      window.removeEventListener("mouseover", handleMouseOver);
      window.removeEventListener("mousedown", handleMouseDown);
      window.removeEventListener("mouseup", handleMouseUp);
      document.body.removeEventListener("mouseleave", handleMouseLeave);
      document.body.removeEventListener("mouseenter", handleMouseEnter);
      document.head.removeChild(style);
    };
  }, [isVisible]);

  // Hide on mobile/touch devices entirely
  if (typeof window !== "undefined" && window.matchMedia("(pointer: coarse)").matches) {
    return null;
  }

  return (
    <>
      {/* Outer trailing ring */}
      <motion.div
        className="fixed top-0 left-0 w-10 h-10 rounded-full border pointer-events-none z-[9998] flex items-center justify-center mix-blend-screen"
        animate={{
          x: mousePosition.x - 20,
          y: mousePosition.y - 20,
          scale: isClicking ? 0.8 : isHovering ? 1.8 : 1,
          opacity: isVisible ? 1 : 0,
          backgroundColor: isHovering ? "rgba(0, 240, 255, 0.1)" : "rgba(0, 0, 0, 0)",
          borderColor: isHovering ? "rgba(0, 240, 255, 0.8)" : "rgba(255, 255, 255, 0.2)",
        }}
        transition={{ 
          type: "spring", 
          stiffness: 150, 
          damping: 15, 
          mass: 0.6 
        }}
      >
        {/* Subtle inner glow when hovering */}
        <motion.div 
          className="w-full h-full rounded-full bg-[#00f0ff] blur-md pointer-events-none"
          animate={{
            opacity: isHovering ? 0.4 : 0
          }}
          transition={{ duration: 0.2 }}
        />
      </motion.div>

      {/* Center crisp dot */}
      <motion.div
        className="fixed top-0 left-0 w-2 h-2 rounded-full pointer-events-none z-[9999]"
        animate={{
          x: mousePosition.x - 4,
          y: mousePosition.y - 4,
          scale: isClicking ? 0.5 : isHovering ? 0 : 1,
          opacity: isVisible ? 1 : 0,
          backgroundColor: isHovering ? "#00f0ff" : "#ffffff",
        }}
        transition={{ 
          type: "spring", 
          stiffness: 800, 
          damping: 30, 
          mass: 0.1 
        }}
        style={{
          boxShadow: isHovering ? "0 0 10px #00f0ff" : "0 0 4px rgba(255,255,255,0.8)"
        }}
      />
    </>
  );
}
