'use client'

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Card } from '@/components/ui/card'
import { FileText, Copy, ExternalLink, Star } from 'lucide-react'
import { useState } from 'react'

interface SourceDetailProps {
  source: {
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
  isOpen: boolean
  onClose: () => void
}

export function SourceDetailModal({ source, isOpen, onClose }: SourceDetailProps) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = async () => {
    try {
      const textToCopy = `${source.content}${source.context_after || ''}`
      await navigator.clipboard.writeText(textToCopy)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const getRelevanceLabel = (score: number) => {
    if (score >= 0.9) return { label: 'Highly Relevant', color: 'bg-green-500' }
    if (score >= 0.7) return { label: 'Very Relevant', color: 'bg-blue-500' }
    if (score >= 0.5) return { label: 'Relevant', color: 'bg-yellow-500' }
    return { label: 'Somewhat Relevant', color: 'bg-gray-500' }
  }

  const relevance = getRelevanceLabel(source.score || 0)

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh]">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <DialogTitle className="text-xl">Source Details</DialogTitle>
              <DialogDescription className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                <span>{source.source_file || 'AAOIFI Standards'} • Page {source.page}</span>
              </DialogDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={copyToClipboard}
                title="Copy content"
              >
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4">
          {/* Metadata Cards */}
          <div className="grid grid-cols-3 gap-2">
            <Card className="p-3">
              <div className="text-xs text-muted-foreground mb-1">Relevance</div>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${relevance.color}`} />
                <span className="text-sm font-medium">{relevance.label}</span>
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                Score: {((source.score || 0) * 100).toFixed(1)}%
              </div>
            </Card>

            <Card className="p-3">
              <div className="text-xs text-muted-foreground mb-1">Position</div>
              <div className="text-sm font-medium">
                #{source.metadata?.retrieval_position || 'N/A'}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                In search results
              </div>
            </Card>

            <Card className="p-3">
              <div className="text-xs text-muted-foreground mb-1">Content Length</div>
              <div className="text-sm font-medium">
                {source.metadata?.full_content_length || 'N/A'} chars
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {source.metadata?.has_full_content ? 'Complete' : 'Excerpt'}
              </div>
            </Card>
          </div>

          {/* Technical Details */}
          {source.chunk_id && (
            <Card className="p-3 bg-muted/50">
              <div className="flex items-center justify-between">
                <div className="text-xs text-muted-foreground">Chunk ID</div>
                <Badge variant="outline" className="font-mono text-xs">
                  {source.chunk_id}
                </Badge>
              </div>
            </Card>
          )}

          {/* Content */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-semibold">Excerpt</h3>
              {copied && (
                <Badge variant="outline" className="text-xs">
                  Copied!
                </Badge>
              )}
            </div>
            <ScrollArea className="h-[300px]">
              <Card className="p-4 bg-muted/30">
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {source.content}
                  </p>
                  {source.context_after && (
                    <>
                      <div className="my-2 border-t border-border pt-2">
                        <div className="text-xs text-muted-foreground mb-1">
                          Additional Context:
                        </div>
                      </div>
                      <p className="text-sm leading-relaxed whitespace-pre-wrap text-muted-foreground">
                        {source.context_after}
                      </p>
                    </>
                  )}
                </div>
              </Card>
            </ScrollArea>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-2 border-t">
            <div className="text-xs text-muted-foreground">
              Referenced from page {source.page} of the source document
            </div>
            <Button variant="outline" size="sm">
              <ExternalLink className="h-3 w-3 mr-1" />
              View in PDF
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
