'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Menu, X, MessageSquare, Settings, Download, Trash2 } from 'lucide-react'

interface MobileNavProps {
  onClearConversation: () => void
  onExportConversation: () => void
  onOpenSettings: () => void
  hasMessages: boolean
}

export function MobileNav({ 
  onClearConversation, 
  onExportConversation, 
  onOpenSettings, 
  hasMessages 
}: MobileNavProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {/* Mobile Menu Button */}
      <Button
        variant="outline"
        size="icon"
        className="md:hidden fixed top-3 right-3 z-40 h-10 w-10 rounded-full glass-light hover:glass border-white/10 transition-all duration-200 touch-manipulation"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </Button>

      {/* Mobile Menu Overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div 
            className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            onClick={() => setIsOpen(false)}
          />
          <Card className="absolute top-16 right-3 w-64 z-50 p-3 shadow-2xl">
            <div className="space-y-2">
              <div className="flex items-center gap-2 mb-3 pb-2 border-b border-white/10">
                <MessageSquare className="h-4 w-4 text-blue-400" />
                <h3 className="font-semibold text-sm">Menu</h3>
              </div>
              
              <Button
                variant="outline"
                className="w-full justify-start h-10 touch-manipulation"
                onClick={() => {
                  onOpenSettings()
                  setIsOpen(false)
                }}
              >
                <Settings className="h-4 w-4 mr-3" />
                Settings
              </Button>
              
              <Button
                variant="outline"
                className="w-full justify-start h-10 touch-manipulation"
                onClick={() => {
                  onExportConversation()
                  setIsOpen(false)
                }}
                disabled={!hasMessages}
              >
                <Download className="h-4 w-4 mr-3" />
                Export Chat
              </Button>
              
              <Button
                variant="outline"
                className="w-full justify-start h-10 text-destructive hover:text-destructive touch-manipulation"
                onClick={() => {
                  onClearConversation()
                  setIsOpen(false)
                }}
                disabled={!hasMessages}
              >
                <Trash2 className="h-4 w-4 mr-3" />
                Clear Chat
              </Button>
            </div>
          </Card>
        </div>
      )}
    </>
  )
}
