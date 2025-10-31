'use client'

import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ChevronDown, ChevronUp, Copy, ExternalLink, Info } from 'lucide-react'
import { formatDate } from '@/lib/utils'
import { SourceDetailModal } from './source-detail-modal'
import { StreamingText } from './streaming-text'

interface Source {
  page: number
  content: string
  score?: number
  chunk_id?: string
  source_file?: string
  context_after?: string
  metadata?: {
    full_content_length?: number
    retrieval_position?: number
    has_full_content?: boolean
  }
}

interface ChatMessageProps {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  timestamp?: Date
  isStreaming?: boolean
}

// Helper function to categorize source relevance
const getRelevanceTier = (score?: number): { tier: string; color: string; description: string } => {
  if (!score || score <= 0) {
    return { tier: 'Unknown', color: 'bg-gray-500', description: 'Relevance not scored' }
  }
  
  if (score >= 0.8) {
    return { 
      tier: 'Highly Relevant', 
      color: 'bg-green-500', 
      description: 'Strong semantic match with your question' 
    }
  } else if (score >= 0.65) {
    return { 
      tier: 'Relevant', 
      color: 'bg-blue-500', 
      description: 'Good contextual relevance' 
    }
  } else {
    return { 
      tier: 'Supplementary', 
      color: 'bg-yellow-500', 
      description: 'Additional context that may be helpful' 
    }
  }
}

export function ChatMessage({ role, content, sources, timestamp, isStreaming = false }: ChatMessageProps) {
  const [showSources, setShowSources] = useState(false)
  const [copied, setCopied] = useState(false)
  const [selectedSource, setSelectedSource] = useState<Source | null>(null)
  const [streamingComplete, setStreamingComplete] = useState(!isStreaming)

  useEffect(() => {
    if (!isStreaming) {
      setStreamingComplete(true)
    }
  }, [isStreaming])

  // Sort sources by relevance score (highest first)
  const sortedSources = sources 
    ? [...sources].sort((a, b) => {
        const scoreA = a.score ?? 0
        const scoreB = b.score ?? 0
        return scoreB - scoreA
      })
    : []

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  return (
    <div className={`flex ${role === 'user' ? 'justify-end' : 'justify-start'} mb-3 md:mb-4 ${role === 'user' ? 'animate-slide-in-left' : 'animate-slide-in-right'} w-full`}>
      <div className={`max-w-[90%] md:max-w-3xl ${role === 'user' ? 'order-2' : 'order-1'}`}>
        <Card className={`${
          role === 'user' 
            ? 'glass-light bg-gradient-to-br from-blue-500/20 to-purple-500/20 border-blue-400/30 shadow-lg shadow-blue-500/10 dark:from-blue-500/20 dark:to-purple-500/20 light:from-blue-100 light:to-purple-100 light:border-blue-300' 
            : 'glass-dark border-white/10 shadow-xl shadow-black/20 dark:border-white/10 light:border-black/20 light:bg-white/90'
        } rounded-2xl overflow-hidden backdrop-blur-xl transform hover:scale-[1.01] transition-all duration-200`}>
          <CardContent className="p-3 md:p-4">
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <div className="prose prose-sm max-w-none dark:prose-invert break-words overflow-wrap-anywhere">
                  {role === 'assistant' && isStreaming && !streamingComplete ? (
                    <StreamingText 
                      text={content} 
                      speed={50}
                      onComplete={() => setStreamingComplete(true)}
                    />
                  ) : (
                      <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      h1: ({ children }) => <h1 className="text-base md:text-lg font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent font-montserrat break-words">{children}</h1>,
                      h2: ({ children }) => <h2 className="text-sm md:text-base font-bold mb-1.5 text-foreground font-montserrat break-words">{children}</h2>,
                      h3: ({ children }) => <h3 className="text-xs md:text-sm font-bold mb-1.5 text-foreground font-montserrat break-words">{children}</h3>,
                      p: ({ children }) => <p className="mb-2 text-xs md:text-sm leading-relaxed text-foreground/90 font-poppins break-words">{children}</p>,
                      ul: ({ children }) => <ul className="mb-2 ml-3 md:ml-4 list-disc text-xs md:text-sm text-foreground/90 space-y-0.5 font-poppins break-words">{children}</ul>,
                      ol: ({ children }) => <ol className="mb-2 ml-3 md:ml-4 list-decimal text-xs md:text-sm text-foreground/90 space-y-0.5 font-poppins break-words">{children}</ol>,
                      li: ({ children }) => <li className="mb-0.5 text-xs md:text-sm leading-relaxed text-foreground/90 font-poppins break-words">{children}</li>,
                      strong: ({ children }) => <strong className="font-bold bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent break-words">{children}</strong>,
                      em: ({ children }) => <em className="italic text-foreground/80 break-words">{children}</em>,
                      code: ({ children }) => <code className="glass-light px-1 md:px-1.5 py-0.5 rounded-lg text-xs font-mono text-blue-300 border border-blue-400/20 break-all">{children}</code>,
                      blockquote: ({ children }) => <blockquote className="border-l-4 border-blue-500/50 pl-2 md:pl-3 italic text-muted-foreground mb-2 glass-light rounded-r-lg py-1.5 break-words">{children}</blockquote>,
                      hr: () => <hr className="my-2 md:my-3 border-white/20" />,
                    }}
                  >
                    {content}
                  </ReactMarkdown>
                  )}
                </div>
                {timestamp && (
                  <p className="text-[10px] opacity-50 mt-2 flex items-center gap-1.5 font-poppins">
                    <span className="inline-block w-1 h-1 rounded-full bg-blue-400 animate-pulse-slow"></span>
                    {formatDate(timestamp)}
                  </p>
                )}
              </div>
              {role === 'assistant' && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={copyToClipboard}
                  className="h-6 w-6 md:h-8 md:w-8 rounded-full glass-light hover:glass border-white/10 opacity-70 hover:opacity-100 transition-all duration-200 shrink-0"
                  title={copied ? 'Copied!' : 'Copy message'}
                >
                  <Copy className={`h-3 w-3 md:h-3.5 md:w-3.5 ${copied ? 'text-green-400' : ''}`} />
                </Button>
              )}
            </div>
            
            {sources && sources.length > 0 && streamingComplete && (
              <div className="mt-3 md:mt-4 pt-3 md:pt-4 border-t border-white/10">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowSources(!showSources)}
                  className="h-6 md:h-7 px-2 md:px-2.5 text-xs rounded-full glass-light hover:glass border-white/10 transition-all duration-200 font-poppins touch-manipulation"
                >
                  {showSources ? (
                    <>
                      <ChevronUp className="h-3 w-3 mr-1" />
                      Hide Sources
                    </>
                  ) : (
                    <>
                      <ChevronDown className="h-3 w-3 mr-1" />
                      View {sources.length} Source{sources.length > 1 ? 's' : ''}
                    </>
                  )}
                </Button>
                
                {showSources && (
                  <div className="mt-2 md:mt-3 space-y-2 animate-fade-in">
                    {/* Relevance explanation */}
                    <div className="text-[10px] text-blue-300/80 glass-light rounded-lg md:rounded-xl p-2 border border-blue-400/20 font-poppins">
                      <strong className="text-blue-200">Sources ranked by relevance:</strong> Higher scores indicate stronger semantic similarity.
                    </div>
                    
                    {sortedSources.map((source, index) => {
                      const relevance = getRelevanceTier(source.score)
                      
                      return (
                        <div 
                          key={index} 
                          className="glass-dark rounded-lg md:rounded-xl p-2 md:p-3 hover:glass-light transition-all duration-200 border border-white/10 transform hover:scale-[1.01] animate-scale-in touch-manipulation"
                          style={{ animationDelay: `${index * 0.05}s` }}
                        >
                          <div className="flex items-start md:items-center justify-between mb-2 gap-2">
                            <div className="flex items-center gap-1 md:gap-1.5 flex-wrap flex-1 min-w-0">
                              <Badge variant="outline" className="text-[10px] font-medium glass-light border-blue-400/30 rounded-full px-1 md:px-1.5 py-0.5 font-poppins shrink-0">
                                #{index + 1}
                              </Badge>
                              <Badge variant="outline" className="text-[10px] glass-light border-purple-400/30 rounded-full px-1 md:px-1.5 py-0.5 font-poppins shrink-0">
                                Page {source.page}
                              </Badge>
                              {source.score !== undefined && source.score > 0 && (
                                <>
                                  <Badge variant="secondary" className="text-[10px] glass-light border-green-400/30 rounded-full px-1 md:px-1.5 py-0.5 font-poppins shrink-0">
                                    {(source.score * 100).toFixed(0)}% match
                                  </Badge>
                                  <div className="flex items-center gap-1 shrink-0">
                                    <div className={`h-1.5 w-1.5 rounded-full ${relevance.color} animate-pulse-slow`} />
                                    <span className="text-[10px] font-medium text-foreground/70 font-poppins truncate">
                                      {relevance.tier}
                                    </span>
                                  </div>
                                </>
                              )}
                            </div>
                            <div className="flex items-center gap-0.5 shrink-0">
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-5 w-5 md:h-6 md:w-6 rounded-lg glass-light hover:glass border-white/10 transition-all duration-200"
                                onClick={() => setSelectedSource(source)}
                                title={relevance.description}
                              >
                                <Info className="h-3 w-3" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-5 w-5 md:h-6 md:w-6 rounded-lg glass-light hover:glass border-white/10 transition-all duration-200"
                                onClick={() => window.open(`#page-${source.page}`, '_blank')}
                                title="Open in PDF"
                              >
                                <ExternalLink className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                          <p className="text-[11px] text-foreground/70 leading-relaxed line-clamp-2 md:line-clamp-3 font-poppins">
                            {source.content}
                          </p>
                          {source.source_file && (
                            <div className="text-[10px] text-blue-300/60 mt-1.5 italic font-poppins truncate">
                              {source.source_file}
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Source Detail Modal */}
      {selectedSource && (
        <SourceDetailModal
          source={selectedSource}
          isOpen={!!selectedSource}
          onClose={() => setSelectedSource(null)}
        />
      )}
    </div>
  )
}
