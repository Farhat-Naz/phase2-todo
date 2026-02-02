'use client';

/**
 * VoiceInput Component - Voice command interface for todos
 * Provides microphone button with real-time feedback and language selection
 * Follows patterns from ui.skill.md and voice.skill.md
 *
 * Features:
 * - Microphone button with toggle state
 * - Pulsing animation when listening
 * - Real-time transcript display
 * - Language selector (English / Urdu)
 * - Success/error feedback
 * - Browser support detection
 * - Accessible with ARIA labels
 * - Mobile responsive
 */

import { useState } from 'react';
import { useVoice } from '@/hooks/useVoice';
import { Button } from '@/components/ui/Button';
import { cn } from '@/lib/utils';

/**
 * Microphone icon component
 */
function MicrophoneIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
      />
    </svg>
  );
}

/**
 * Microphone off icon component
 */
function MicrophoneOffIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
      />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"
      />
    </svg>
  );
}

/**
 * Globe/Language icon component
 */
function GlobeIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"
      />
    </svg>
  );
}

/**
 * Check circle icon for success
 */
function CheckCircleIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
  );
}

/**
 * VoiceInput component props
 */
interface VoiceInputProps {
  className?: string;
}

/**
 * Main VoiceInput component
 */
export function VoiceInput({ className }: VoiceInputProps) {
  const {
    isListening,
    transcript,
    error,
    language,
    isSupported,
    result,
    startVoice,
    stopVoice,
    setLanguage,
  } = useVoice();

  const [showLanguageSelector, setShowLanguageSelector] = useState(false);

  // Don't render if browser doesn't support speech recognition
  if (!isSupported) {
    return null;
  }

  /**
   * Handle microphone button click
   */
  const handleMicClick = () => {
    if (isListening) {
      stopVoice();
    } else {
      startVoice();
    }
  };

  /**
   * Handle language selection
   */
  const handleLanguageChange = (newLanguage: 'en-US' | 'ur-PK') => {
    setLanguage(newLanguage);
    setShowLanguageSelector(false);

    // If currently listening, restart with new language
    if (isListening) {
      stopVoice();
      setTimeout(() => startVoice(newLanguage), 100);
    }
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Voice control buttons */}
      <div className="flex items-center gap-3">
        {/* Microphone button */}
        <Button
          onClick={handleMicClick}
          variant={isListening ? 'danger' : 'primary'}
          size="lg"
          className={cn(
            'relative',
            isListening && 'animate-pulse'
          )}
          aria-label={isListening ? 'Stop listening' : 'Start voice command'}
        >
          {isListening ? (
            <>
              <MicrophoneOffIcon className="h-5 w-5" />
              <span className="ml-2">Stop Listening</span>
              {/* Pulsing ring animation */}
              <span className="absolute inset-0 rounded-lg border-2 border-white animate-ping opacity-75" />
            </>
          ) : (
            <>
              <MicrophoneIcon className="h-5 w-5" />
              <span className="ml-2">Voice Command</span>
            </>
          )}
        </Button>

        {/* Language selector button */}
        <div className="relative">
          <Button
            onClick={() => setShowLanguageSelector(!showLanguageSelector)}
            variant="outline"
            size="lg"
            aria-label="Select language"
            className="flex items-center gap-2"
          >
            <GlobeIcon className="h-5 w-5" />
            <span className="hidden sm:inline">
              {language === 'en-US' ? 'English' : 'اردو'}
            </span>
          </Button>

          {/* Language dropdown */}
          {showLanguageSelector && (
            <div className="absolute top-full mt-2 right-0 z-10 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg overflow-hidden min-w-[140px]">
              <button
                onClick={() => handleLanguageChange('en-US')}
                className={cn(
                  'w-full px-4 py-2.5 text-left transition-colors',
                  'hover:bg-gray-100 dark:hover:bg-gray-700',
                  language === 'en-US' && 'bg-primary-50 dark:bg-primary-900 text-primary-600 dark:text-primary-300'
                )}
              >
                <span className="font-medium">English</span>
              </button>
              <button
                onClick={() => handleLanguageChange('ur-PK')}
                className={cn(
                  'w-full px-4 py-2.5 text-left transition-colors',
                  'hover:bg-gray-100 dark:hover:bg-gray-700',
                  language === 'ur-PK' && 'bg-primary-50 dark:bg-primary-900 text-primary-600 dark:text-primary-300'
                )}
                dir="rtl"
              >
                <span className="font-medium">اردو</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Real-time transcript display */}
      {isListening && transcript && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border-2 border-blue-200 dark:border-blue-700 rounded-lg p-4 animate-slide-up">
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-0.5">
              <div className="h-3 w-3 bg-blue-500 rounded-full animate-pulse" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
                Listening...
              </p>
              <p className="text-base text-blue-800 dark:text-blue-200 break-words">
                {transcript}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Success feedback */}
      {result && result.success && (
        <div className="bg-success-light dark:bg-success-dark/20 border border-success dark:border-success-dark rounded-lg p-4 animate-slide-up">
          <div className="flex items-start gap-3">
            <CheckCircleIcon className="h-5 w-5 text-success dark:text-success-light flex-shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-success-dark dark:text-success-light">
                {result.message}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error feedback */}
      {error && (
        <div className="bg-error-light dark:bg-error-dark/20 border border-error dark:border-error-dark rounded-lg p-4 animate-slide-up">
          <div className="flex items-start gap-3">
            <svg
              className="h-5 w-5 text-error dark:text-error-light flex-shrink-0 mt-0.5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-error-dark dark:text-error-light">
                {error}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Help text */}
      {!isListening && !result && !error && (
        <div className="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            <span className="font-medium text-gray-900 dark:text-gray-100">
              {language === 'en-US' ? 'Try saying:' : 'کہنے کی کوشش کریں:'}
            </span>
          </p>
          <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
            {language === 'en-US' ? (
              <>
                <li>• "Add todo: Buy groceries"</li>
                <li>• "Complete: Buy groceries"</li>
                <li>• "Mark as high priority: Buy groceries"</li>
                <li>• "Remove priority: Buy groceries"</li>
              </>
            ) : (
              <>
                <li>• "نیا کام: گروسری خریدیں"</li>
                <li>• "مکمل کریں: گروسری خریدیں"</li>
                <li>• "اہم بنائیں: گروسری خریدیں"</li>
                <li>• "ترجیح ہٹائیں: گروسری خریدیں"</li>
              </>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
