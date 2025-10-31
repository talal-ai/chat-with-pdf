'use client'

import { useState, useRef, useEffect } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { ChatMessage } from './chat-message'
import { ChatInput } from './chat-input'
import { TypingIndicator } from './typing-indicator'
import { WelcomeMessage } from './welcome-message'
import { FollowUpQuestions } from './follow-up-questions'
import { ToneSelector, ResponseTone } from './tone-selector'
import { ConversationsSidebar } from './conversations-sidebar'
import { SettingsDialog } from '@/components/settings/settings-dialog'
import { ThemeToggle } from '@/components/theme-toggle'
import { Trash2, Settings, Download, MessageSquare, Menu } from 'lucide-react'
import axios from 'axios'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{ page: number; content: string }>
  followUpQuestions?: string[]
  timestamp: Date
}

interface ChatInterfaceProps {
  apiUrl?: string
}

const DEFAULT_API_URL = process.env.NEXT_PUBLIC_API_URL 
  ? `${process.env.NEXT_PUBLIC_API_URL}/chat`
  : 'http://localhost:8000/api/v1/chat'

export function ChatInterface({ apiUrl = DEFAULT_API_URL }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentApiUrl, setCurrentApiUrl] = useState(apiUrl)
  const [selectedTone, setSelectedTone] = useState<ResponseTone>("conversational")
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]')
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight
      }
    }
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const sendMessage = async (message: string) => {
    if (!message.trim() || loading) return

    const userMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(currentApiUrl, {
        message: message,
        tone: selectedTone,
        conversation_id: currentConversationId,
        conversation_history: messages.map(msg => ({
          role: msg.role,
          content: msg.content
        }))
      })

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources,
        followUpQuestions: response.data.follow_up_questions || [],
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Update conversation ID if it was just created
      if (response.data.metadata?.conversation_id) {
        setCurrentConversationId(response.data.metadata.conversation_id)
      }
    } catch (error) {
      console.error('Error:', error)
      setError('Sorry, there was an error processing your request. Please try again.')
      
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const clearConversation = () => {
    setMessages([])
    setCurrentConversationId(null)
    setError(null)
  }

  const createNewConversation = () => {
    setMessages([])
    setCurrentConversationId(null)
    setError(null)
  }

  const loadConversation = async (conversationId: number) => {
    try {
      const baseUrl = currentApiUrl.replace('/chat', '')
      const response = await axios.get(`${baseUrl}/conversations/${conversationId}`)
      const conversation = response.data
      
      // Load messages from conversation
      if (conversation.messages && Array.isArray(conversation.messages)) {
        const loadedMessages: Message[] = conversation.messages.map((msg: any) => ({
          role: msg.role,
          content: msg.content,
          sources: msg.sources,
          followUpQuestions: msg.follow_up_questions,
          timestamp: new Date(msg.timestamp || Date.now())
        }))
        setMessages(loadedMessages)
      }
      
      setCurrentConversationId(conversationId)
      setSidebarOpen(false)
    } catch (error) {
      console.error('Failed to load conversation:', error)
      setError('Failed to load conversation')
    }
  }

  const exportConversation = () => {
    const conversationText = messages.map(msg => 
      `${msg.role.toUpperCase()}: ${msg.content}\n`
    ).join('\n')
    
    const blob = new Blob([conversationText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `aaoifi-chat-${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex h-screen bg-background relative overflow-hidden">
      {/* Animated background orbs */}
      <div className="absolute top-20 left-10 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse-slow pointer-events-none" />
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse-slow pointer-events-none" style={{ animationDelay: '1s' }} />

      {/* Conversations Sidebar */}
      <ConversationsSidebar
        apiUrl={currentApiUrl}
        currentConversationId={currentConversationId}
        onSelectConversation={loadConversation}
        onNewConversation={createNewConversation}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

  {/* Main Chat Area */}
  <div className="flex-1 flex flex-col relative z-10 md:ml-96">
        {/* Header */}
        <div className="glass-dark border-b border-white/10 dark:border-white/10 light:border-black/10 backdrop-blur-xl">
          <div className="flex items-center justify-between p-3">
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSidebarOpen(!sidebarOpen)}
                title="Toggle conversations"
                className="md:hidden rounded-full glass-light hover:glass border-white/10 transition-all duration-200 h-9 w-9"
              >
                <Menu className="h-4 w-4" />
              </Button>
              <div>
                <h1 className="text-base font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent font-montserrat">
                  AAOIFI Standards Chatbot
                </h1>
                <p className="text-[10px] text-foreground/60 font-poppins">
                  {currentConversationId ? `Conversation #${String(currentConversationId).slice(0, 8)}` : 'Ask questions about Sharia Standards'}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <ThemeToggle />
              <Button
                variant="outline"
                size="icon"
                onClick={exportConversation}
                disabled={messages.length === 0}
                title="Export conversation"
                className="rounded-full glass-light hover:glass border-white/10 transition-all duration-200 h-9 w-9"
              >
                <Download className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={clearConversation}
                disabled={messages.length === 0}
                title="Clear conversation"
                className="rounded-full glass-light hover:glass border-white/10 transition-all duration-200 hover:border-red-500/30 h-9 w-9"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
              <SettingsDialog
                apiUrl={currentApiUrl}
                onApiUrlChange={setCurrentApiUrl}
              />
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-hidden">
          <ScrollArea ref={scrollAreaRef} className="h-full">
            <div className="p-4 space-y-4">
              {messages.length === 0 ? (
                <WelcomeMessage onQuestionClick={sendMessage} />
              ) : (
                messages.map((message, index) => (
                  <div key={index}>
                    <ChatMessage
                      role={message.role}
                      content={message.content}
                      sources={message.sources}
                      timestamp={message.timestamp}
                      isStreaming={index === messages.length - 1 && message.role === 'assistant' && loading}
                    />
                    {message.role === 'assistant' && message.followUpQuestions && message.followUpQuestions.length > 0 && (
                      <FollowUpQuestions
                        questions={message.followUpQuestions}
                        onQuestionClick={sendMessage}
                        disabled={loading}
                      />
                    )}
                  </div>
                ))
              )}
              
              {loading && <TypingIndicator />}
              
              {error && (
                <div className="flex justify-center animate-fade-in">
                  <Card className="glass-dark border-red-500/30 max-w-md rounded-2xl backdrop-blur-xl">
                    <div className="p-3 text-center">
                      <p className="text-xs text-red-300 font-poppins">{error}</p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setError(null)}
                        className="mt-2 rounded-full glass-light border-white/10 hover:border-red-500/30 transition-all duration-200 text-xs h-7 font-poppins"
                      >
                        Dismiss
                      </Button>
                    </div>
                  </Card>
                </div>
              )}
            </div>
          </ScrollArea>
        </div>

        {/* Input Area */}
        <div className="glass-dark border-t border-white/10 p-3 backdrop-blur-xl">
          <ToneSelector 
            selectedTone={selectedTone} 
            onToneChange={setSelectedTone}
          />
          <ChatInput
            onSendMessage={sendMessage}
            loading={loading}
            disabled={!!error}
            apiUrl={apiUrl}
          />
        </div>
      </div>
    </div>
  )
}
