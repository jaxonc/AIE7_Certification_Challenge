'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Send, Bot, User, Loader2, Settings, ArrowLeft, Activity } from 'lucide-react'
import Image from 'next/image'
import axios from 'axios'

interface Message {
  id: string
  text: string
  sender: 'user' | 'agent'
  timestamp: Date
}

interface ProgressStep {
  step: string
  node: string
  timestamp: Date
}

interface AgentCapabilities {
  capabilities: string[]
  tools: string[]
  status: string
}

export default function Chat() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [progressSteps, setProgressSteps] = useState<ProgressStep[]>([])
  const [capabilities, setCapabilities] = useState<AgentCapabilities | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, progressSteps])

  useEffect(() => {
    const initializeApp = async () => {
      // Check if API keys are configured for this session only
      const configured = sessionStorage.getItem('apiKeysConfigured')
      
      if (!configured) {
        router.push('/setup')
        return
      }

      // Load agent capabilities on component mount
      const loadCapabilities = async () => {
        try {
          const response = await axios.get('/api/agent/capabilities')
          setCapabilities(response.data)
        } catch (error) {
          console.error('Failed to load agent capabilities:', error)
        }
      }
      loadCapabilities()

      // Add welcome message
      setMessages([{
        id: '1',
        text: '👋 Hello! I\'m SAVE. I can help you with UPC code validation, nutritional information, product searches, and more. Try asking me about a UPC code or food product!',
        sender: 'agent',
        timestamp: new Date()
      }])
    }

    initializeApp()
  }, [router])

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setIsLoading(true)
    setProgressSteps([])

    // Add immediate feedback
    setProgressSteps([{
      step: "Connecting to agent...",
      node: "connection",
      timestamp: new Date()
    }])

    try {
      let finalResponse = ''
      
      // Use EventSource for real-time progress tracking
      const ssePromise = new Promise<void>((resolve, reject) => {
        const directUrl = `http://localhost:8000/api/agent/chat/stream-sse?message=${encodeURIComponent(inputText)}`
        const eventSource = new EventSource(directUrl)

        eventSource.onopen = () => {
          console.log('✅ SSE connection opened')
        }

        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            
            if (data.type === 'progress') {
              setProgressSteps(prev => [...prev, {
                step: data.step,
                node: data.node,
                timestamp: new Date()
              }])
            } else if (data.type === 'response') {
              finalResponse = data.content
              eventSource.close()
              resolve()
            } else if (data.type === 'error') {
              eventSource.close()
              reject(new Error(data.content))
            }
          } catch (parseError) {
            console.warn('Failed to parse SSE data:', event.data, parseError)
          }
        }

        eventSource.onerror = (error) => {
          console.error('SSE connection error:', error)
          eventSource.close()
          reject(new Error('SSE connection failed'))
        }

        // Timeout after 60 seconds
        setTimeout(() => {
          if (eventSource.readyState !== EventSource.CLOSED) {
            eventSource.close()
            reject(new Error('SSE connection timeout'))
          }
        }, 60000)
      })

      await ssePromise

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: finalResponse || 'No response generated',
        sender: 'agent',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, agentMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: '❌ Sorry, I encountered an error. Please make sure the backend is running and try again.',
        sender: 'agent',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      // Don't clear progress steps immediately - let them be visible briefly
      setTimeout(() => setProgressSteps([]), 1000)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const formatMessage = (text: string) => {
    // Enhanced formatting for better readability
    const lines = text.split(/\n|\r\n|\r/); // Handle different line ending formats
    
    return lines.map((line, index) => {
      // Handle special formatting
      if (line.startsWith('##')) {
        // Main headings
        return (
          <div key={index} className="font-bold text-lg mb-2 mt-3 text-gray-800">
            {line.replace(/^##\s*/, '')}
          </div>
        );
      } else if (line.startsWith('###')) {
        // Sub headings
        return (
          <div key={index} className="font-semibold text-base mb-1 mt-2 text-gray-700">
            {line.replace(/^###\s*/, '')}
          </div>
        );
      } else if (line.startsWith('**') && line.endsWith('**')) {
        // Bold text
        return (
          <div key={index} className="font-semibold mb-1">
            {line.replace(/^\*\*|\*\*$/g, '')}
          </div>
        );
      } else if (line.startsWith('- ')) {
        // Bullet points
        return (
          <div key={index} className="ml-4 mb-1">
            • {line.replace(/^-\s*/, '')}
          </div>
        );
      } else if (line.trim() === '') {
        // Empty lines for spacing
        return <div key={index} className="h-2"></div>;
      } else {
        // Regular text
        return (
          <div key={index} className="mb-1">
            {line}
          </div>
        );
      }
    });
  }

  const handleReconfigure = () => {
    router.push('/setup')
  }

  // Removed loading check since we no longer store API keys locally

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto max-w-4xl h-screen flex flex-col">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-white rounded-lg">
                <Image src="/save-icon.png" alt="S.A.V.E. Icon" width={64} height={64} className="text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">S.A.V.E. (Certification Challenge Prototype)</h1>
                <p className="text-sm text-gray-600">
                  Status: {capabilities?.status === 'online' ? '🟢 Online' : '🔴 Offline'}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleReconfigure}
                className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-800 px-2 py-1 rounded hover:bg-gray-100"
              >
                <Settings className="h-4 w-4" />
                <span>API Keys</span>
              </button>
              <div className="text-right">
                <p className="text-xs text-gray-500">AI-Powered Food Assistant</p>
                <p className="text-xs text-gray-500">UPC • Nutrition • Search</p>
              </div>
            </div>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-hidden flex flex-col bg-white">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex items-start space-x-2 ${
                  message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  message.sender === 'user' 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {message.sender === 'user' ? <User size={16} /> : <Bot size={16} />}
                </div>
                <div className={`chat-bubble ${
                  message.sender === 'user' ? 'user-bubble' : 'agent-bubble'
                }`}>
                  <div className="text-sm">{formatMessage(message.text)}</div>
                  <div className={`text-xs mt-1 ${
                    message.sender === 'user' ? 'text-blue-200' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex items-start space-x-2">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                  <Bot size={16} />
                </div>
                <div className="chat-bubble agent-bubble">
                  <div className="space-y-2">
                    {progressSteps.length > 0 ? (
                      <div className="space-y-1">
                        {progressSteps.map((step, index) => {
                          // Get appropriate icon and color based on step content
                          const getStepIcon = (stepText: string) => {
                            if (stepText.includes('Analyzing') || stepText.includes('Starting')) {
                              return <Activity className="h-3 w-3 text-blue-500 animate-pulse" />
                            } else if (stepText.includes('AI agent') || stepText.includes('thinking')) {
                              return <Bot className="h-3 w-3 text-purple-500 animate-pulse" />
                            } else if (stepText.includes('UPC') || stepText.includes('validating')) {
                              return <Activity className="h-3 w-3 text-orange-500 animate-pulse" />
                            } else if (stepText.includes('USDA') || stepText.includes('database')) {
                              return <Activity className="h-3 w-3 text-green-500 animate-pulse" />
                            } else if (stepText.includes('web') || stepText.includes('Searching web')) {
                              return <Activity className="h-3 w-3 text-cyan-500 animate-pulse" />
                            } else if (stepText.includes('knowledge base') || stepText.includes('rag')) {
                              return <Activity className="h-3 w-3 text-indigo-500 animate-pulse" />
                            } else if (stepText.includes('Preparing') || stepText.includes('Finalizing')) {
                              return <Activity className="h-3 w-3 text-emerald-500 animate-pulse" />
                            }
                            return <Activity className="h-3 w-3 text-blue-500 animate-pulse" />
                          }
                          
                          return (
                            <div key={index} className="flex items-center space-x-2 text-sm">
                              {getStepIcon(step.step)}
                              <span className="text-gray-700">{step.step}</span>
                            </div>
                          )
                        })}
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2 text-sm">
                        <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
                        <span className="text-gray-700">Connecting to agent...</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex space-x-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about UPC codes, nutrition facts, or food products..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white"
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !inputText.trim()}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </button>
            </div>
            <div className="mt-2 text-xs text-gray-500">
              💡 Try: "What's are the ingredients for UPC 041548750927?" or "Tell me about hot chips upc 028400433303"
            </div>
          </div>
        </div>

        {/* Capabilities Sidebar (Optional) */}
        {capabilities && (
          <div className="bg-gray-50 border-t border-gray-200 p-4">
            <details className="text-sm">
              <summary className="cursor-pointer font-medium text-gray-700 hover:text-gray-900">
                🛠️ Agent Capabilities
              </summary>
              <div className="mt-2 space-y-1">
                {capabilities.capabilities.map((capability, index) => (
                  <div key={index} className="text-xs text-gray-600">
                    • {capability}
                  </div>
                ))}
              </div>
            </details>
          </div>
        )}
      </div>
    </div>
  )
}