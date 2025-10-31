'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Settings, Save, RotateCcw, CheckCircle, AlertCircle, Brain, Trash2 } from 'lucide-react'
import axios from 'axios'

interface MemoryStats {
  enabled: boolean
  window_size: number
  current_messages: number
  conversation_pairs: number
  at_capacity: boolean
}

interface SettingsDialogProps {
  apiUrl: string
  onApiUrlChange: (url: string) => void
}

export function SettingsDialog({ apiUrl, onApiUrlChange }: SettingsDialogProps) {
  const [localApiUrl, setLocalApiUrl] = useState(apiUrl)
  const [saved, setSaved] = useState(false)
  
  // Memory control state
  const [memoryEnabled, setMemoryEnabled] = useState(true)
  const [memoryWindowSize, setMemoryWindowSize] = useState(5)
  const [memoryStats, setMemoryStats] = useState<MemoryStats | null>(null)
  const [memoryLoading, setMemoryLoading] = useState(false)
  const [memoryError, setMemoryError] = useState<string | null>(null)
  
  // Clear memory confirmation dialog state
  const [clearMemoryDialogOpen, setClearMemoryDialogOpen] = useState(false)

  // Fetch memory stats on dialog open
  useEffect(() => {
    fetchMemoryStats()
  }, [])

  const fetchMemoryStats = async () => {
    try {
      const baseUrl = apiUrl.replace('/chat', '')
      const response = await axios.get(`${baseUrl}/memory/settings`)
      const stats = response.data
      setMemoryStats(stats)
      setMemoryEnabled(stats.enabled)
      setMemoryWindowSize(stats.window_size)
      setMemoryError(null)
    } catch (error) {
      console.error('Failed to fetch memory stats:', error)
      setMemoryError('Failed to load memory settings')
    }
  }

  const updateMemorySettings = async () => {
    setMemoryLoading(true)
    setMemoryError(null)
    try {
      const baseUrl = apiUrl.replace('/chat', '')
      const response = await axios.post(`${baseUrl}/memory/settings`, {
        enabled: memoryEnabled,
        window_size: memoryWindowSize
      })
      setMemoryStats(response.data)
      setMemoryError(null)
    } catch (error) {
      console.error('Failed to update memory settings:', error)
      setMemoryError('Failed to update memory settings')
    } finally {
      setMemoryLoading(false)
    }
  }

  const handleClearMemoryClick = () => {
    setClearMemoryDialogOpen(true)
  }

  const handleClearMemoryConfirm = async () => {
    setMemoryLoading(true)
    setMemoryError(null)
    try {
      const baseUrl = apiUrl.replace('/chat', '')
      await axios.post(`${baseUrl}/memory/clear`)
      await fetchMemoryStats()
      setMemoryError(null)
      setClearMemoryDialogOpen(false)
    } catch (error) {
      console.error('Failed to clear memory:', error)
      setMemoryError('Failed to clear memory')
    } finally {
      setMemoryLoading(false)
    }
  }

  const handleClearMemoryCancel = () => {
    setClearMemoryDialogOpen(false)
  }

  const handleSave = () => {
    onApiUrlChange(localApiUrl)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const DEFAULT_RESET_URL = process.env.NEXT_PUBLIC_API_URL 
    ? `${process.env.NEXT_PUBLIC_API_URL}/chat`
    : 'http://localhost:8000/api/v1/chat'

  const handleReset = () => {
    setLocalApiUrl(DEFAULT_RESET_URL)
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="icon" title="Settings">
          <Settings className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[650px] max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Settings
          </DialogTitle>
          <DialogDescription>
            Configure your API settings and preferences.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* API Configuration */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">API Configuration</CardTitle>
              <CardDescription className="text-xs">
                Configure the backend API endpoint
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-1.5">
                <label htmlFor="api-url" className="text-xs font-medium">
                  API Endpoint
                </label>
                <Input
                  id="api-url"
                  value={localApiUrl}
                  onChange={(e) => setLocalApiUrl(e.target.value)}
                  placeholder="http://localhost:8000/api/v1/chat"
                  className="h-9 text-sm"
                />
                <p className="text-[10px] text-muted-foreground">
                  Enter the full URL to your backend API
                </p>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleReset}
                    className="h-8 text-xs"
                  >
                    <RotateCcw className="h-3 w-3 mr-1" />
                    Reset
                  </Button>
                </div>
                <Button
                  onClick={handleSave}
                  disabled={!localApiUrl.trim()}
                  size="sm"
                  className="h-8 text-xs"
                >
                  {saved ? (
                    <>
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Saved
                    </>
                  ) : (
                    <>
                      <Save className="h-3 w-3 mr-1" />
                      Save
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Status */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Connection Status</CardTitle>
            </CardHeader>
            <CardContent className="py-3">
              <div className="flex items-center gap-2 flex-wrap">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs">Connected to API</span>
                <Badge variant="outline" className="text-[10px] max-w-[250px] truncate">
                  {apiUrl}
                </Badge>
              </div>
            </CardContent>
          </Card>

          {/* Memory Control */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Brain className="h-4 w-4" />
                Conversation Memory
              </CardTitle>
              <CardDescription className="text-xs">
                Control how the AI remembers context from your conversation
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {memoryError && (
                <div className="flex items-center gap-2 text-sm text-destructive bg-destructive/10 p-2 rounded">
                  <AlertCircle className="h-4 w-4" />
                  {memoryError}
                </div>
              )}
              
              {/* Memory Toggle */}
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <label className="text-xs font-medium">Enable Memory</label>
                  <p className="text-[10px] text-muted-foreground">
                    Remember conversation context
                  </p>
                </div>
                <Button
                  variant={memoryEnabled ? "default" : "outline"}
                  size="sm"
                  onClick={() => {
                    setMemoryEnabled(!memoryEnabled)
                  }}
                  className="h-8 text-xs"
                >
                  {memoryEnabled ? "Enabled" : "Disabled"}
                </Button>
              </div>

              {/* Window Size Selector */}
              <div className="space-y-1.5">
                <label className="text-xs font-medium">Memory Window Size</label>
                <p className="text-[10px] text-muted-foreground">
                  Number of Q&A pairs to remember
                </p>
                <div className="grid grid-cols-4 gap-2">
                  {[2, 5, 10, 20].map((size) => (
                    <Button
                      key={size}
                      variant={memoryWindowSize === size ? "default" : "outline"}
                      size="sm"
                      onClick={() => setMemoryWindowSize(size)}
                      disabled={!memoryEnabled}
                      className="h-8 text-xs"
                    >
                      {size}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Memory Stats */}
              {memoryStats && (
                <div className="space-y-2 pt-2 border-t">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Current messages:</span>
                    <Badge variant="secondary">
                      {memoryStats.conversation_pairs} / {memoryStats.window_size} pairs
                    </Badge>
                  </div>
                  {memoryStats.at_capacity && (
                    <div className="flex items-center gap-2 text-xs text-amber-600 dark:text-amber-400">
                      <AlertCircle className="h-3 w-3" />
                      Memory at capacity - oldest messages will be removed
                    </div>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-1">
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleClearMemoryClick}
                  disabled={memoryLoading || !memoryStats || memoryStats.current_messages === 0}
                  className="h-8 text-xs"
                >
                  <Trash2 className="h-3 w-3 mr-1" />
                  Clear Memory
                </Button>
                <Button
                  onClick={updateMemorySettings}
                  disabled={memoryLoading}
                  size="sm"
                  className="h-8 text-xs"
                >
                  {memoryLoading ? (
                    "Updating..."
                  ) : (
                    <>
                      <Save className="h-3 w-3 mr-1" />
                      Apply
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Features */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Features</CardTitle>
            </CardHeader>
            <CardContent className="py-3">
              <div className="grid grid-cols-2 gap-2">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm">RAG-powered responses</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Fine-grained source citations</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Relevance-ranked sources</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Persistent conversations</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Contextual memory control</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Interactive follow-up questions</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className="text-sm">Export conversations</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </DialogContent>

      {/* Clear Memory Confirmation Dialog */}
      <Dialog open={clearMemoryDialogOpen} onOpenChange={setClearMemoryDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-amber-600 dark:text-amber-400">
              <AlertCircle className="h-5 w-5" />
              Clear Conversation Memory
            </DialogTitle>
            <DialogDescription className="pt-2">
              Are you sure you want to clear all conversation memory? This will remove the context from previous messages and cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-2 py-2">
            <div className="flex items-start gap-2 text-sm text-muted-foreground">
              <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <p>The AI will forget all previous context and start fresh.</p>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={handleClearMemoryCancel}
              disabled={memoryLoading}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleClearMemoryConfirm}
              disabled={memoryLoading}
              className="gap-2"
            >
              {memoryLoading ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-background border-t-transparent" />
                  Clearing...
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4" />
                  Clear Memory
                </>
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </Dialog>
  )
}
