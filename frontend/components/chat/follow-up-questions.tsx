'use client'

import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { MessageCircle, ArrowRight } from 'lucide-react'

interface FollowUpQuestionsProps {
  questions: string[]
  onQuestionClick: (question: string) => void
  disabled?: boolean
}

export function FollowUpQuestions({ questions, onQuestionClick, disabled }: FollowUpQuestionsProps) {
  if (!questions || questions.length === 0) {
    return null
  }

  return (
    <Card className="p-3 glass-light bg-gradient-to-r from-blue-500/5 to-purple-500/5 border-blue-400/10 dark:border-blue-400/10 light:border-blue-300/30 light:from-blue-50 light:to-purple-50 rounded-2xl animate-fade-in backdrop-blur-xl mt-3">
      <div className="flex items-center gap-1.5 mb-2">
        <MessageCircle className="h-3.5 w-3.5 text-blue-400 dark:text-blue-400 light:text-blue-600" />
        <h3 className="text-xs font-semibold text-blue-400/90 dark:text-blue-400/90 light:text-blue-700 font-montserrat">
          Follow-up Questions
        </h3>
      </div>
      
      <div className="space-y-1.5">
        {questions.map((question, index) => (
          <Button
            key={index}
            variant="ghost"
            className="w-full justify-start text-left h-auto py-2 px-2.5 hover:glass-dark rounded-xl transition-all duration-200 group border border-transparent hover:border-white/10 dark:hover:border-white/10 light:hover:border-black/10 text-xs"
            onClick={() => onQuestionClick(question)}
            disabled={disabled}
          >
            <div className="flex items-start gap-2 w-full">
              <span className="text-[10px] font-bold text-blue-400/60 dark:text-blue-400/60 light:text-blue-600 mt-0.5 shrink-0 glass-light rounded-full w-4 h-4 flex items-center justify-center">
                {index + 1}
              </span>
              <span className="text-xs leading-relaxed flex-1 text-foreground/70 dark:text-foreground/70 light:text-gray-700 font-poppins">
                {question}
              </span>
              <ArrowRight className="h-3 w-3 text-blue-400/40 dark:text-blue-400/40 light:text-blue-600 group-hover:text-blue-400 group-hover:translate-x-0.5 transition-all shrink-0 mt-0.5" />
            </div>
          </Button>
        ))}
      </div>
    </Card>
  )
}
