import './globals.css'
import type { Metadata } from 'next'
import { Poppins, Montserrat } from 'next/font/google'
import { Toaster } from '@/components/ui/toaster'

const poppins = Poppins({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-poppins',
  display: 'swap',
})

const montserrat = Montserrat({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--font-montserrat',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'AAOIFI Standards Chatbot',
  description: 'Ask questions about AAOIFI Sharia Standards',
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`min-h-screen bg-background font-sans antialiased ${poppins.variable} ${montserrat.variable}`}>
        {children}
        <Toaster />
      </body>
    </html>
  )
} 