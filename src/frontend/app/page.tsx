'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Loader2, Coffee } from 'lucide-react'

export default function Home() {
  const router = useRouter()

  useEffect(() => {
    // Check if API keys are configured for this session only
    const configured = sessionStorage.getItem('apiKeysConfigured')
    
    if (configured) {
      // API keys are configured for this session, redirect to chat
      router.push('/chat')
    } else {
      // No API keys configured, redirect to setup
      router.push('/setup')
    }
  }, [router])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="text-center">
        <div className="flex items-center justify-center space-x-3 mb-4">
          <div className="p-3 bg-blue-500 rounded-lg">
            <Coffee className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-gray-800">S.A.V.E. (Certification Challenge Prototype)</h1>
        </div>
        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-500" />
        <p className="text-gray-600">Loading...</p>
      </div>
    </div>
  )
}