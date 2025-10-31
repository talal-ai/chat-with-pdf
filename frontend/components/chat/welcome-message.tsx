'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { BookOpen, Search, MessageSquare, FileText } from 'lucide-react'

const exampleQuestions = [
  "What are the key principles of Islamic banking?",
  "Explain the requirements for Sharia compliance",
  "What are the different types of Islamic financial contracts?",
  "How does AAOIFI ensure standardization in Islamic finance?"
]

const features = [
  {
    icon: BookOpen,
    title: "Comprehensive Knowledge",
    description: "Access to complete AAOIFI Sharia Standards"
  },
  {
    icon: Search,
    title: "Intelligent Search",
    description: "Find specific information with AI-powered search"
  },
  {
    icon: MessageSquare,
    title: "Natural Conversation",
    description: "Ask questions in natural language"
  },
  {
    icon: FileText,
    title: "Source Citations",
    description: "Get references to specific pages and sections"
  }
]

interface WelcomeMessageProps {
  onQuestionClick: (question: string) => void
}

export function WelcomeMessage({ onQuestionClick }: WelcomeMessageProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[300px] md:min-h-[400px] space-y-4 md:space-y-6 animate-fade-in p-3 md:p-4">
      {/* Header */}
      <div className="text-center space-y-3 md:space-y-4 animate-scale-in max-w-full">
        <div className="flex items-center justify-center space-x-2 mb-3 md:mb-4">
          <div className="w-10 h-10 md:w-12 md:h-12 glass-light rounded-2xl flex items-center justify-center border border-blue-400/30 shadow-lg shadow-blue-500/20 animate-pulse-slow">
            <BookOpen className="w-5 h-5 md:w-6 md:h-6 text-blue-400" />
          </div>
          <h1 className="text-xl md:text-3xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent font-montserrat leading-tight">
            AAOIFI Standards Chatbot
          </h1>
        </div>
        <p className="text-xs md:text-sm text-foreground/70 dark:text-foreground/70 light:text-gray-600 max-w-2xl leading-relaxed font-poppins px-2">
          Your intelligent assistant for AAOIFI Sharia Standards. Ask questions, 
          get detailed answers with source citations, and explore Islamic finance principles.
        </p>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-2 md:gap-3 w-full max-w-5xl">
        {features.map((feature, index) => (
          <Card 
            key={index} 
            className="text-center glass-dark border-white/10 rounded-lg md:rounded-xl hover:glass-light transition-all duration-200 transform hover:scale-105 active:scale-95 animate-scale-in backdrop-blur-xl touch-manipulation"
            style={{ animationDelay: `${index * 0.1}s` }}
          >
            <CardHeader className="pb-2 pt-2 md:pt-3 px-2 md:px-4">
              <div className="w-8 h-8 md:w-10 md:h-10 glass-light rounded-lg md:rounded-xl flex items-center justify-center mx-auto mb-2 border border-blue-400/20 shadow-md shadow-blue-500/10">
                <feature.icon className="w-4 h-4 md:w-5 md:h-5 text-blue-500 dark:text-blue-400" />
              </div>
              <CardTitle className="text-xs md:text-sm text-foreground dark:text-foreground light:text-gray-800 font-montserrat leading-tight">{feature.title}</CardTitle>
            </CardHeader>
            <CardContent className="pt-0 pb-2 md:pb-3 px-2 md:px-4">
              <CardDescription className="text-[10px] md:text-xs text-foreground/60 dark:text-foreground/60 light:text-gray-600 font-poppins leading-relaxed">
                {feature.description}
              </CardDescription>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Example Questions */}
      <div className="w-full max-w-3xl animate-fade-in px-2" style={{ animationDelay: '0.4s' }}>
        <h3 className="text-xs md:text-sm font-semibold mb-2 md:mb-3 text-center bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent font-montserrat">
          Try asking:
        </h3>
        <div className="grid gap-1.5 md:gap-2">
          {exampleQuestions.map((question, index) => (
            <button
              key={index}
              onClick={() => onQuestionClick(question)}
              className="text-left p-2.5 md:p-3 rounded-lg md:rounded-xl glass-dark border border-white/10 dark:border-white/10 light:border-black/20 hover:glass-light hover:border-blue-400/30 transition-all duration-200 text-xs md:text-sm transform hover:scale-[1.01] active:scale-95 hover:shadow-lg hover:shadow-blue-500/10 touch-manipulation"
            >
              <span className="text-foreground/80 dark:text-foreground/80 light:text-gray-700 font-poppins leading-relaxed">{question}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Status Badge */}
      <div className="flex items-center space-x-2 animate-fade-in px-2" style={{ animationDelay: '0.6s' }}>
        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse-slow shadow-lg shadow-green-500/50"></div>
        <Badge variant="outline" className="text-[10px] md:text-xs glass-light border-green-400/30 rounded-full px-2 md:px-3 py-1 font-poppins">
          Ready to help with AAOIFI Standards
        </Badge>
      </div>
    </div>
  )
}
