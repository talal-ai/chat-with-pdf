'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Send, Loader2, Paperclip, X } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

interface ChatInputProps {
  onSendMessage: (message: string, files?: File[]) => void
  loading: boolean
  disabled?: boolean
  apiUrl?: string
}

export function ChatInput({ onSendMessage, loading, disabled, apiUrl = 'http://localhost:8000/api/v1' }: ChatInputProps) {
  const [input, setInput] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if ((!input.trim() && selectedFiles.length === 0) || loading || disabled) return
    
    if (selectedFiles.length > 0) {
      // Upload files first
      setUploading(true)
      try {
        const formData = new FormData()
        selectedFiles.forEach(file => {
          formData.append('files', file)
        })

        const response = await fetch(`${apiUrl}/upload/multiple`, {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          throw new Error('Upload failed')
        }

        const result = await response.json()
        
        if (result.errors && result.errors.length > 0) {
          toast({
            title: "Some files failed to upload",
            description: result.errors.map((e: any) => `${e.filename}: ${e.error}`).join(', '),
            variant: "destructive",
          })
        }

        if (result.successful > 0) {
          toast({
            title: "Files uploaded successfully",
            description: `${result.successful} file(s) uploaded`,
          })
        }
      } catch (error) {
        toast({
          title: "Upload failed",
          description: error instanceof Error ? error.message : "Failed to upload files",
          variant: "destructive",
        })
      } finally {
        setUploading(false)
        setSelectedFiles([])
      }
    }
    
    if (input.trim()) {
      onSendMessage(input.trim())
      setInput('')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    const validFiles = files.filter(file => {
      const ext = file.name.toLowerCase().split('.').pop()
      const validExtensions = ['pdf', 'txt', 'doc', 'docx', 'md']
      const maxSize = 10 * 1024 * 1024 // 10MB
      
      if (!validExtensions.includes(ext || '')) {
        toast({
          title: "Invalid file type",
          description: `${file.name} is not supported. Use PDF, TXT, DOC, DOCX, or MD files.`,
          variant: "destructive",
        })
        return false
      }
      
      if (file.size > maxSize) {
        toast({
          title: "File too large",
          description: `${file.name} exceeds 10MB limit.`,
          variant: "destructive",
        })
        return false
      }
      
      return true
    })
    
    setSelectedFiles(prev => [...prev, ...validFiles].slice(0, 5)) // Max 5 files
    
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
  }

  useEffect(() => {
    if (!loading && !uploading) {
      inputRef.current?.focus()
    }
  }, [loading, uploading])

  return (
    <div className="space-y-2">
      {/* Selected files display */}
      {selectedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2 max-w-4xl mx-auto">
          {selectedFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center gap-2 glass-light border-white/20 rounded-lg px-3 py-1.5 text-xs font-poppins"
            >
              <Paperclip className="h-3 w-3 text-blue-400" />
              <span className="text-foreground/80 max-w-[150px] truncate">
                {file.name}
              </span>
              <span className="text-foreground/50">
                ({(file.size / 1024).toFixed(1)}KB)
              </span>
              <button
                onClick={() => removeFile(index)}
                className="text-red-400 hover:text-red-300"
                type="button"
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex gap-3 max-w-4xl mx-auto">
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.txt,.doc,.docx,.md"
          onChange={handleFileSelect}
          className="hidden"
        />
        
        <Button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={loading || disabled || uploading || selectedFiles.length >= 5}
          size="icon"
          className="shrink-0 h-14 w-14 rounded-2xl glass-light hover:glass border-white/20 dark:border-white/20 light:border-black/20 hover:border-purple-400/50 transition-all duration-300 disabled:opacity-50"
          title="Attach files (PDF, TXT, DOC, DOCX, MD)"
        >
          <Paperclip className="h-5 w-5 text-purple-500" />
        </Button>
      <Input
        ref={inputRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about AAOIFI Standards..."
        disabled={loading || disabled}
        className="flex-1 glass-light border-white/20 dark:border-white/20 light:border-black/20 rounded-2xl px-6 py-6 text-base placeholder:text-foreground/40 dark:placeholder:text-foreground/40 light:placeholder:text-gray-500 focus:border-blue-400/50 focus:ring-2 focus:ring-blue-400/20 transition-all duration-300 text-foreground font-poppins"
      />
      <Button
        type="submit"
        disabled={loading || (!input.trim() && selectedFiles.length === 0) || disabled || uploading}
        size="icon"
        className="shrink-0 h-14 w-14 rounded-2xl glass-light hover:glass border-white/20 dark:border-white/20 light:border-black/20 hover:border-blue-400/50 transition-all duration-300 disabled:opacity-50"
      >
        {loading || uploading ? (
          <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
        ) : (
          <Send className="h-5 w-5 text-blue-500" />
        )}
      </Button>
    </form>
    </div>
  )
}
