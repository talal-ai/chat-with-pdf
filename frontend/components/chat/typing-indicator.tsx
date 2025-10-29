'use client'

export function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4 animate-slide-in-right">
      <div className="max-w-3xl">
        <div className="glass-dark border border-white/10 rounded-2xl p-4 backdrop-blur-xl">
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full typing-dot shadow-md shadow-blue-500/50"></div>
              <div className="w-2 h-2 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full typing-dot shadow-md shadow-purple-500/50"></div>
              <div className="w-2 h-2 bg-gradient-to-r from-pink-400 to-blue-400 rounded-full typing-dot shadow-md shadow-pink-500/50"></div>
            </div>
            <span className="text-xs text-foreground/60 font-medium font-poppins">AI is crafting your response...</span>
          </div>
        </div>
      </div>
    </div>
  )
}
