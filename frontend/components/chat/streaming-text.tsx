'use client'

import { useEffect, useState } from 'react'

interface StreamingTextProps {
  text: string
  speed?: number // milliseconds per word
  onComplete?: () => void
}

export function StreamingText({ text, speed = 50, onComplete }: StreamingTextProps) {
  const [displayedWords, setDisplayedWords] = useState<string[]>([])
  const words = text.split(' ')

  useEffect(() => {
    let currentIndex = 0
    setDisplayedWords([])

    const interval = setInterval(() => {
      if (currentIndex < words.length) {
        setDisplayedWords(prev => [...prev, words[currentIndex]])
        currentIndex++
      } else {
        clearInterval(interval)
        if (onComplete) onComplete()
      }
    }, speed)

    return () => clearInterval(interval)
  }, [text, speed, onComplete, words])

  return (
    <span>
      {displayedWords.map((word, index) => (
        <span
          key={index}
          className="word-stream"
          style={{ animationDelay: `${index * 0.05}s` }}
        >
          {word}{' '}
        </span>
      ))}
    </span>
  )
}
