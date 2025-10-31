"use client";

import React from "react";
import { MessageSquare, Zap, BookOpen, Briefcase, GraduationCap } from "lucide-react";

export type ResponseTone = "conversational" | "concise" | "detailed" | "professional" | "simple";

interface ToneSelectorProps {
  selectedTone: ResponseTone;
  onToneChange: (tone: ResponseTone) => void;
}

const toneOptions = [
  {
    value: "conversational" as ResponseTone,
    label: "Chat",
    icon: MessageSquare,
    description: "Friendly & natural like ChatGPT",
    color: "bg-blue-500 hover:bg-blue-600",
  },
  {
    value: "concise" as ResponseTone,
    label: "Brief",
    icon: Zap,
    description: "Short & to the point",
    color: "bg-purple-500 hover:bg-purple-600",
  },
  {
    value: "detailed" as ResponseTone,
    label: "Detailed",
    icon: BookOpen,
    description: "Comprehensive explanations",
    color: "bg-green-500 hover:bg-green-600",
  },
  {
    value: "professional" as ResponseTone,
    label: "Formal",
    icon: Briefcase,
    description: "Business & consultant style",
    color: "bg-gray-700 hover:bg-gray-800",
  },
  {
    value: "simple" as ResponseTone,
    label: "Simple",
    icon: GraduationCap,
    description: "Easy to understand",
    color: "bg-orange-500 hover:bg-orange-600",
  },
];

export function ToneSelector({ selectedTone, onToneChange }: ToneSelectorProps) {
  return (
    <div className="flex flex-wrap gap-1 md:gap-1.5 mb-2 justify-center md:justify-start">
      {toneOptions.map((option) => {
        const Icon = option.icon;
        const isSelected = selectedTone === option.value;
        
        return (
          <button
            key={option.value}
            onClick={() => onToneChange(option.value)}
            className={`
              group relative flex items-center gap-1 md:gap-1.5 px-2 md:px-2.5 py-1 md:py-1 rounded-lg md:rounded-xl text-xs font-medium
              transition-all duration-200 transform hover:scale-105 active:scale-95 glass-light border
              min-h-[32px] md:min-h-[36px] touch-manipulation
              ${
                isSelected
                  ? "border-blue-400/50 bg-blue-500/20 text-blue-300 dark:text-blue-300 light:text-blue-700 light:bg-blue-200/50 shadow-lg shadow-blue-500/20"
                  : "border-white/10 dark:border-white/10 light:border-black/20 text-foreground/70 dark:text-foreground/70 light:text-gray-700 hover:border-white/20 hover:glass"
              }
            `}
            title={option.description}
          >
            <Icon className="w-3 h-3 md:w-3 md:h-3 flex-shrink-0" />
            <span className="font-poppins truncate">{option.label}</span>
            
            {/* Tooltip - hidden on mobile, shown on hover for desktop */}
            <div className="hidden md:block absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 
                          opacity-0 group-hover:opacity-100 transition-opacity duration-200
                          pointer-events-none z-50">
              <div className="glass-dark text-foreground text-[10px] rounded-lg py-1.5 px-2.5 whitespace-nowrap shadow-xl border border-white/10 backdrop-blur-xl font-poppins">
                {option.description}
                <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                  <div className="border-4 border-transparent border-t-gray-900/80"></div>
                </div>
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
}
