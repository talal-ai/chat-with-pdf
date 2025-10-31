'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { MessageSquare, Trash2, Plus, X, Edit2, Check, AlertTriangle } from 'lucide-react'
import axios from 'axios'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

interface Conversation {
  id: number
  title: string
  created_at: string
  updated_at: string
}

interface ConversationsSidebarProps {
  apiUrl: string
  currentConversationId: number | null
  onSelectConversation: (id: number) => void
  onNewConversation: () => void
  isOpen: boolean
  onClose: () => void
}

export function ConversationsSidebar({
  apiUrl,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  isOpen,
  onClose
}: ConversationsSidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editTitle, setEditTitle] = useState('')
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [conversationToDelete, setConversationToDelete] = useState<number | null>(null)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    fetchConversations()
  }, [apiUrl, currentConversationId])

  const fetchConversations = async () => {
    try {
      setLoading(true)
      const baseUrl = apiUrl.replace('/chat', '')
      const response = await axios.get(`${baseUrl}/conversations`)
      setConversations(response.data)
    } catch (error) {
      console.error('Failed to fetch conversations:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteClick = (id: number, e: React.MouseEvent) => {
    e.stopPropagation()
    setConversationToDelete(id)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!conversationToDelete) return

    try {
      setDeleting(true)
      const baseUrl = apiUrl.replace('/chat', '')
      await axios.delete(`${baseUrl}/conversations/${conversationToDelete}`)
      setConversations(prev => prev.filter(c => c.id !== conversationToDelete))
      if (currentConversationId === conversationToDelete) {
        onNewConversation()
      }
      setDeleteDialogOpen(false)
      setConversationToDelete(null)
    } catch (error) {
      console.error('Failed to delete conversation:', error)
    } finally {
      setDeleting(false)
    }
  }

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false)
    setConversationToDelete(null)
  }

  const handleRename = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation()
    if (editingId === id) {
      try {
        const baseUrl = apiUrl.replace('/chat', '')
        await axios.patch(`${baseUrl}/conversations/${id}`, { title: editTitle })
        setConversations(prev =>
          prev.map(c => (c.id === id ? { ...c, title: editTitle } : c))
        )
        setEditingId(null)
      } catch (error) {
        console.error('Failed to rename conversation:', error)
      }
    } else {
      const conversation = conversations.find(c => c.id === id)
      if (conversation) {
        setEditTitle(conversation.title)
        setEditingId(id)
      }
    }
  }

  const handleCancelEdit = (e: React.MouseEvent) => {
    e.stopPropagation()
    setEditingId(null)
    setEditTitle('')
  }

  const handleNewChat = () => {
    onNewConversation()
    fetchConversations()
  }

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden backdrop-blur-sm"
          onClick={onClose}
        />
      )}

      <div
        className={`
          fixed top-0 left-0 h-full w-96 z-50
          glass-dark border-r border-white/10 dark:border-white/10 
          backdrop-blur-xl transition-transform duration-300 ease-in-out
          flex flex-col
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          md:translate-x-0
        `}
      >
        <div className="p-4 border-b border-white/10 dark:border-white/10">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-bold font-montserrat bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              Conversations
            </h2>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="md:hidden rounded-full h-8 w-8 hover:bg-white/10"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          <Button
            onClick={handleNewChat}
            className="w-full glass-light hover:glass border-white/10 rounded-xl transition-all duration-200 h-9 text-xs font-medium font-poppins text-foreground"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Conversation
          </Button>
        </div>

        <ScrollArea className="flex-1 px-4 py-2">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-400" />
            </div>
          ) : conversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <MessageSquare className="h-12 w-12 text-foreground/30 mb-3" />
              <p className="text-xs text-foreground/60">
                No conversations yet. Start a new chat!
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => !editingId && onSelectConversation(conversation.id)}
                  className={`
                    group p-2.5 rounded-xl cursor-pointer border
                    transition-all duration-200 max-w-full
                    ${
                      currentConversationId === conversation.id
                        ? 'glass border-blue-400/30 bg-blue-500/10'
                        : 'glass-light hover:glass border-white/10'
                    }
                  `}
                >
                  {editingId === conversation.id ? (
                    <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        className="flex-1 bg-white/5 border border-white/10 rounded-lg px-2 py-1 text-xs focus:outline-none focus:border-blue-400/50"
                        autoFocus
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') handleRename(conversation.id, e as any)
                          if (e.key === 'Escape') handleCancelEdit(e as any)
                        }}
                      />
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={(e) => handleRename(conversation.id, e)}
                        className="h-6 w-6 rounded-lg hover:bg-green-500/20"
                      >
                        <Check className="h-3 w-3 text-green-400" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={handleCancelEdit}
                        className="h-6 w-6 rounded-lg hover:bg-red-500/20"
                      >
                        <X className="h-3 w-3 text-red-400" />
                      </Button>
                    </div>
                  ) : (
                    <>
                      <h3 className="text-xs font-medium truncate mb-0.5 font-poppins">
                        {conversation.title}
                      </h3>
                      <div className="flex items-center justify-between">
                        <p className="text-[10px] text-foreground/50 font-poppins">
                          {new Date(conversation.updated_at).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric'
                          })}
                        </p>
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => handleRename(conversation.id, e)}
                            className="h-5 w-5 rounded-lg hover:bg-blue-500/20"
                          >
                            <Edit2 className="h-2.5 w-2.5 text-blue-400" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={(e) => handleDeleteClick(conversation.id, e)}
                            className="h-5 w-5 rounded-lg hover:bg-red-500/20"
                          >
                            <Trash2 className="h-2.5 w-2.5 text-red-400" />
                          </Button>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </ScrollArea>

        {/* Footer */}
        <div className="p-4 border-t border-white/10 dark:border-white/10">
          <p className="text-[10px] text-foreground/40 text-center">
            {conversations.length} conversation{conversations.length !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600 dark:text-red-400">
              <AlertTriangle className="h-5 w-5" />
              Delete Conversation
            </DialogTitle>
            <DialogDescription className="pt-2">
              Are you sure you want to delete this conversation? This action cannot be undone and all messages will be permanently lost.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2 sm:gap-0">
            <Button
              variant="outline"
              onClick={handleDeleteCancel}
              disabled={deleting}
              className="sm:mr-2"
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteConfirm}
              disabled={deleting}
              className="gap-2"
            >
              {deleting ? (
                <>
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-background border-t-transparent" />
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4" />
                  Delete Conversation
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
