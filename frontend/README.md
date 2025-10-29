# AAOIFI Standards Chatbot Frontend

A modern, responsive chat interface for the AAOIFI Standards RAG chatbot built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- 🤖 **AI-Powered Chat**: Intelligent responses using RAG (Retrieval-Augmented Generation)
- 📚 **Source Citations**: Get references to specific pages and sections
- 💬 **Conversation History**: Maintain context across multiple messages
- 📱 **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- 🎨 **Modern UI**: Built with shadcn/ui components and Tailwind CSS
- ⚙️ **Settings Panel**: Configure API endpoints and preferences
- 📤 **Export Conversations**: Download chat history as text files
- 🔄 **Real-time Updates**: Smooth animations and loading states

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui + Radix UI
- **Icons**: Lucide React
- **HTTP Client**: Axios

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm, yarn, or pnpm

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

3. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

### Backend Setup

Make sure your backend is running on `http://localhost:8000` before using the chat interface.

## Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Main chat page
├── components/            # React components
│   ├── chat/              # Chat-specific components
│   │   ├── chat-interface.tsx
│   │   ├── chat-message.tsx
│   │   ├── chat-input.tsx
│   │   ├── typing-indicator.tsx
│   │   └── welcome-message.tsx
│   ├── layout/            # Layout components
│   │   └── mobile-nav.tsx
│   ├── settings/          # Settings components
│   │   └── settings-dialog.tsx
│   └── ui/                # Reusable UI components
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── dialog.tsx
│       ├── toast.tsx
│       └── ...
├── hooks/                 # Custom React hooks
│   └── use-toast.ts
├── lib/                   # Utility functions
│   └── utils.ts
└── components.json        # shadcn/ui configuration
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Customization

### API Configuration

The chat interface connects to your backend API. You can configure the API endpoint through the settings panel or by modifying the default URL in `components/chat/chat-interface.tsx`.

### Styling

The app uses Tailwind CSS with a custom design system. Key files:
- `app/globals.css` - Global styles and CSS variables
- `tailwind.config.js` - Tailwind configuration
- `components/ui/` - Reusable component styles

### Components

All components are built with TypeScript and follow React best practices. They're fully customizable and can be easily modified to match your design requirements.

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Deploy automatically

### Other Platforms

The app can be deployed to any platform that supports Next.js:
- Netlify
- Railway
- DigitalOcean App Platform
- AWS Amplify

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the AAOIFI Standards RAG system.
