'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Key, CheckCircle, AlertCircle, Info } from 'lucide-react'
import Image from 'next/image'
import axios from 'axios'

interface ApiKeys {
  openai: string
  anthropic: string
  tavily: string
  usda: string
}

interface ApiKeyValidation {
  openai: boolean
  anthropic: boolean
  tavily: boolean
  usda: boolean
}

export default function Setup() {
  const router = useRouter()
  const [apiKeys, setApiKeys] = useState<ApiKeys>({
    openai: '',
    anthropic: '',
    tavily: '',
    usda: ''
  })
  const [validation, setValidation] = useState<ApiKeyValidation>({
    openai: false,
    anthropic: false,
    tavily: false,
    usda: false
  })
  const [isValidating, setIsValidating] = useState(false)
  const [showPasswords, setShowPasswords] = useState({
    openai: false,
    anthropic: false,
    tavily: false,
    usda: false
  })

  // Removed localStorage persistence for security - API keys must be entered fresh each time

  const validateApiKeys = async (keys: ApiKeys) => {
    setIsValidating(true)
    const newValidation: ApiKeyValidation = {
      openai: keys.openai.startsWith('sk-') && keys.openai.length > 20,
      anthropic: keys.anthropic.startsWith('sk-ant-') && keys.anthropic.length > 20,
      tavily: keys.tavily.startsWith('tvly-') && keys.tavily.length > 20,
      usda: keys.usda.length > 10, // USDA keys are typically alphanumeric
    }
    
    setValidation(newValidation)
    setIsValidating(false)
  }

  const handleInputChange = (provider: keyof ApiKeys, value: string) => {
    const newKeys = { ...apiKeys, [provider]: value }
    setApiKeys(newKeys)
    
    // Debounced validation
    setTimeout(() => validateApiKeys(newKeys), 500)
  }

  // Removed separate handleSave function - now integrated into handleProceed

  const handleProceed = async () => {
    const allValid = Object.values(validation).every(valid => valid)
    if (!allValid) {
      alert('⚠️ Please provide valid API keys for all services before proceeding.')
      return
    }

    try {
      // Send API keys directly to backend
      const response = await axios.post('/api/configure-keys', {
        openai_api_key: apiKeys.openai,
        anthropic_api_key: apiKeys.anthropic,
        tavily_api_key: apiKeys.tavily,
        usda_api_key: apiKeys.usda
      })
      
      // Check the response status
      const { status, message } = response.data
      
      if (status === 'success' || status === 'partial') {
        // Mark as configured for this session only
        if (typeof window !== 'undefined') {
          sessionStorage.setItem('apiKeysConfigured', 'true')
        }
        
        // Always proceed to chat, regardless of partial success
        router.push('/chat')
      } else {
        alert(`❌ Failed to configure API keys: ${message}`)
      }
    } catch (error) {
      console.error('Error configuring API keys:', error)
      if (axios.isAxiosError(error)) {
        if (error.response) {
          alert(`❌ Server error: ${error.response.data?.detail || error.response.statusText}`)
        } else {
          alert('❌ Error connecting to backend. Please check if the server is running.')
        }
      } else {
        alert(`❌ Unexpected error: ${error}`)
      }
    }
  }

  const togglePasswordVisibility = (provider: keyof ApiKeys) => {
    setShowPasswords(prev => ({
      ...prev,
      [provider]: !prev[provider]
    }))
  }

  const allKeysValid = Object.values(validation).every(valid => valid)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="container mx-auto max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="p-3 bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg">
              <Image src="/save-icon.png" alt="S.A.V.E. Icon" width={80} height={80} className="text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-800">S.A.V.E. (Certification Challenge Prototype)</h1>
          </div>
          <p className="text-gray-600">Configure your API keys to get started</p>
        </div>

        {/* API Keys Configuration */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center space-x-2 mb-6">
            <Key className="h-5 w-5 text-blue-500" />
            <h2 className="text-xl font-semibold text-gray-800">API Keys Setup</h2>
          </div>

          <div className="space-y-6">
            {/* OpenAI */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                OpenAI API Key
                <span className="text-red-500 ml-1">*</span>
              </label>
              <div className="relative">
                <input
                  type={showPasswords.openai ? 'text' : 'password'}
                  value={apiKeys.openai}
                  onChange={(e) => handleInputChange('openai', e.target.value)}
                  placeholder="sk-..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-20 text-gray-900 bg-white"
                />
                <div className="absolute right-2 top-2 flex items-center space-x-1">
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('openai')}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    👁️
                  </button>
                  {validation.openai ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : apiKeys.openai && (
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  )}
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Used for embeddings and some language models. Get yours at{' '}
                <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                  OpenAI Platform
                </a>
              </p>
            </div>

            {/* Anthropic */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Anthropic Claude API Key
                <span className="text-red-500 ml-1">*</span>
              </label>
              <div className="relative">
                <input
                  type={showPasswords.anthropic ? 'text' : 'password'}
                  value={apiKeys.anthropic}
                  onChange={(e) => handleInputChange('anthropic', e.target.value)}
                  placeholder="sk-ant-..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-20 text-gray-900 bg-white"
                />
                <div className="absolute right-2 top-2 flex items-center space-x-1">
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('anthropic')}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    👁️
                  </button>
                  {validation.anthropic ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : apiKeys.anthropic && (
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  )}
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Primary AI model for the agent. Get yours at{' '}
                <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                  Anthropic Console
                </a>
              </p>
            </div>

            {/* Tavily */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tavily Search API Key
                <span className="text-red-500 ml-1">*</span>
              </label>
              <div className="relative">
                <input
                  type={showPasswords.tavily ? 'text' : 'password'}
                  value={apiKeys.tavily}
                  onChange={(e) => handleInputChange('tavily', e.target.value)}
                  placeholder="tvly-..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-20 text-gray-900 bg-white"
                />
                <div className="absolute right-2 top-2 flex items-center space-x-1">
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('tavily')}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    👁️
                  </button>
                  {validation.tavily ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : apiKeys.tavily && (
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  )}
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Web search capabilities. Get yours at{' '}
                <a href="https://tavily.com/" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                  Tavily
                </a>
              </p>
            </div>

            {/* USDA */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                USDA Food Data Central API Key
                <span className="text-red-500 ml-1">*</span>
              </label>
              <div className="relative">
                <input
                  type={showPasswords.usda ? 'text' : 'password'}
                  value={apiKeys.usda}
                  onChange={(e) => handleInputChange('usda', e.target.value)}
                  placeholder="Your USDA API key..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-20 text-gray-900 bg-white"
                />
                <div className="absolute right-2 top-2 flex items-center space-x-1">
                  <button
                    type="button"
                    onClick={() => togglePasswordVisibility('usda')}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    👁️
                  </button>
                  {validation.usda ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : apiKeys.usda && (
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  )}
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Nutritional data from USDA. Get yours at{' '}
                <a href="https://api.nal.usda.gov/fdc/v1" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                  USDA Food Data Central
                </a>
              </p>
            </div>
          </div>

          {/* Info Box */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start space-x-2">
              <Info className="h-5 w-5 text-blue-500 mt-0.5" />
              <div className="text-sm text-blue-700">
                <p className="font-medium mb-1">Security Notice:</p>
                <p>API keys are only stored temporarily for this session and are never saved permanently. You will need to re-enter them each time you use the application.</p>
              </div>
            </div>
          </div>

          {/* Action Button */}
          <div className="mt-6">
            <button
              onClick={handleProceed}
              disabled={!allKeysValid || isValidating}
              className="w-full px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isValidating ? 'Validating Keys...' : 'Configure & Start Chat →'}
            </button>
          </div>
          
          {!allKeysValid && (
            <p className="text-center text-red-500 text-sm mt-2">
              ⚠️ All API keys must be valid to proceed
            </p>
          )}
        </div>
      </div>
    </div>
  )
}