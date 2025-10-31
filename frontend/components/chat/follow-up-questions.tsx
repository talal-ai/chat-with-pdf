'use client'

import { MessageCircle } from 'lucide-react'

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
    <div className="mt-3 md:mt-4 w-full">
      {/* Header */}
      <div className="flex items-center gap-2 mb-2 px-1">
        <MessageCircle className="h-3.5 w-3.5 text-blue-400 shrink-0" />
        <span className="text-xs font-semibold text-blue-400 font-montserrat">
          Continue the conversation:
        </span>
      </div>
      
      {/* Questions List */}
      <div className="flex flex-col gap-2 w-full">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onQuestionClick(question)}
            disabled={disabled}
            className="
              group relative w-full text-left
              glass-light hover:glass
              border border-white/10 hover:border-blue-400/30
              rounded-xl p-3
              transition-all duration-200
              disabled:opacity-50 disabled:cursor-not-allowed
              touch-manipulation
              overflow-hidden
            "
          >
            {/* Question content */}
            <div className="flex items-start gap-2.5 w-full">
              {/* Number badge */}
              <span className="
                shrink-0 mt-0.5
                flex items-center justify-center
                w-5 h-5 rounded-full
                bg-blue-500/20 text-blue-400
                text-[10px] font-bold
              ">
                {index + 1}
              </span>
              
              {/* Question text */}
              <span className="
                flex-1 min-w-0
                text-xs leading-relaxed
                text-foreground/80
                font-poppins
                break-words
                pr-2
              ">
                {question}
              </span>
              
              {/* Hover arrow indicator */}
              <span className="
                shrink-0 mt-0.5
                text-blue-400/40 group-hover:text-blue-400
                transition-all duration-200
                group-hover:translate-x-1
                text-lg
              ">
                →
              </span>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
