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
        className="md:hidden"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
      </Button>

      {/* Mobile Menu Overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div 
            className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            onClick={() => setIsOpen(false)}
          />
          <Card className="absolute top-4 right-4 w-64 p-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2 mb-4">
                <MessageSquare className="h-5 w-5" />
                <h3 className="font-semibold">Menu</h3>
              </div>
              
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => {
                  onOpenSettings()
                  setIsOpen(false)
                }}
              >
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => {
                  onExportConversation()
                  setIsOpen(false)
                }}
                disabled={!hasMessages}
              >
                <Download className="h-4 w-4 mr-2" />
                Export Chat
              </Button>
              
              <Button
                variant="outline"
                className="w-full justify-start text-destructive hover:text-destructive"
                onClick={() => {
                  onClearConversation()
                  setIsOpen(false)
                }}
                disabled={!hasMessages}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Clear Chat
              </Button>
            </div>
          </Card>
        </div>
      )}
    </>
  )
}
