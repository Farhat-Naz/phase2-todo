'use client';

/**
 * useVoice Hook - Voice command processing for Todo operations
 * Integrates Web Speech API with Todo CRUD operations
 * Follows patterns from voice.skill.md and api.skill.md
 *
 * Features:
 * - Voice recognition with English and Urdu support
 * - Auto-parse transcript into todo actions
 * - Create todos from voice commands
 * - Complete todos by title with fuzzy matching
 * - Automatic stop after command execution
 * - Browser support detection
 * - Error handling with user-friendly messages
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import {
  VoiceRecognitionService,
  parseVoiceCommand,
  findTodoByTitle,
  isSpeechRecognitionSupported,
  type VoiceLanguage,
  type RecognitionResult,
} from '@/lib/voice';
import { useTodos } from '@/hooks/useTodos';
import { Todo } from '@/types/todo';

/**
 * Voice command execution result
 */
interface CommandResult {
  success: boolean;
  message: string;
  todo?: Todo;
}

/**
 * useVoice hook return type
 */
interface UseVoiceReturn {
  // State
  isListening: boolean;
  transcript: string;
  error: string | null;
  language: VoiceLanguage;
  isSupported: boolean;
  result: CommandResult | null;

  // Methods
  startVoice: (lang?: VoiceLanguage) => void;
  stopVoice: () => void;
  setLanguage: (lang: VoiceLanguage) => void;
}

/**
 * Main hook for voice command processing
 */
export function useVoice(): UseVoiceReturn {
  // Voice recognition state
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [language, setLanguage] = useState<VoiceLanguage>('en-US');
  const [result, setResult] = useState<CommandResult | null>(null);

  // Check browser support
  const isSupported = isSpeechRecognitionSupported();

  // Voice recognition service
  const voiceServiceRef = useRef<VoiceRecognitionService | null>(null);

  // Todo operations
  const { todos, createTodo, toggleComplete, togglePriority } = useTodos();

  /**
   * Initialize voice recognition service
   */
  useEffect(() => {
    if (isSupported) {
      voiceServiceRef.current = new VoiceRecognitionService();
    }

    return () => {
      if (voiceServiceRef.current) {
        voiceServiceRef.current.stopListening();
      }
    };
  }, [isSupported]);

  /**
   * Execute voice command
   */
  const executeCommand = useCallback(
    async (finalTranscript: string) => {
      setError(null);
      setResult(null);

      // Parse voice command
      const command = parseVoiceCommand(finalTranscript, language);

      if (command.action === 'unknown') {
        const errorMsg = language === 'en-US'
          ? "I didn't understand that command. Try 'add todo: buy milk' or 'complete: buy milk'"
          : "میں سمجھ نہیں پایا۔ 'نیا کام: دودھ خریدیں' یا 'مکمل کریں: دودھ خریدیں' کوشش کریں";

        setError(errorMsg);
        setResult({
          success: false,
          message: errorMsg,
        });
        return;
      }

      // Execute create action
      if (command.action === 'create' && command.title) {
        try {
          const newTodo = await createTodo({ title: command.title });

          if (newTodo) {
            const successMsg = language === 'en-US'
              ? `Created: "${command.title}"`
              : `بنایا گیا: "${command.title}"`;

            setResult({
              success: true,
              message: successMsg,
              todo: newTodo,
            });
          } else {
            const errorMsg = language === 'en-US'
              ? 'Failed to create todo'
              : 'ٹاسک بنانے میں ناکامی';

            setError(errorMsg);
            setResult({
              success: false,
              message: errorMsg,
            });
          }
        } catch (err) {
          const errorMsg = language === 'en-US'
            ? 'Error creating todo'
            : 'ٹاسک بنانے میں خرابی';

          setError(errorMsg);
          setResult({
            success: false,
            message: errorMsg,
          });
        }
        return;
      }

      // Execute complete action
      if (command.action === 'complete' && command.title) {
        // Find todo by title (fuzzy match)
        const matchedTodo = findTodoByTitle(todos, command.title);

        if (!matchedTodo) {
          const errorMsg = language === 'en-US'
            ? `Todo not found: "${command.title}"`
            : `ٹاسک نہیں ملا: "${command.title}"`;

          setError(errorMsg);
          setResult({
            success: false,
            message: errorMsg,
          });
          return;
        }

        // Skip if already completed
        if (matchedTodo.completed) {
          const infoMsg = language === 'en-US'
            ? `Already completed: "${matchedTodo.title}"`
            : `پہلے سے مکمل: "${matchedTodo.title}"`;

          setResult({
            success: true,
            message: infoMsg,
            todo: matchedTodo,
          });
          return;
        }

        // Toggle completion
        try {
          await toggleComplete(matchedTodo.id);

          const successMsg = language === 'en-US'
            ? `Completed: "${matchedTodo.title}"`
            : `مکمل کیا: "${matchedTodo.title}"`;

          setResult({
            success: true,
            message: successMsg,
            todo: matchedTodo,
          });
        } catch (err) {
          const errorMsg = language === 'en-US'
            ? 'Error completing todo'
            : 'ٹاسک مکمل کرنے میں خرابی';

          setError(errorMsg);
          setResult({
            success: false,
            message: errorMsg,
          });
        }
        return;
      }

      // Execute set high priority action
      if (command.action === 'set_high_priority' && command.title) {
        // Find todo by title (fuzzy match)
        const matchedTodo = findTodoByTitle(todos, command.title);

        if (!matchedTodo) {
          // "Did you mean?" suggestions
          const suggestions = todos
            .filter(t => !t.completed)
            .slice(0, 3)
            .map(t => t.title)
            .join(', ');

          const errorMsg = language === 'en-US'
            ? `Todo not found: "${command.title}". ${suggestions ? `Did you mean: ${suggestions}?` : ''}`
            : `ٹاسک نہیں ملا: "${command.title}". ${suggestions ? `کیا آپ کا مطلب: ${suggestions}؟` : ''}`;

          setError(errorMsg);
          setResult({
            success: false,
            message: errorMsg,
          });
          return;
        }

        // Skip if already high priority
        if (matchedTodo.priority === 'high') {
          const infoMsg = language === 'en-US'
            ? `Already high priority: "${matchedTodo.title}"`
            : `پہلے سے اہم: "${matchedTodo.title}"`;

          setResult({
            success: true,
            message: infoMsg,
            todo: matchedTodo,
          });
          return;
        }

        // Set high priority
        try {
          await togglePriority(matchedTodo.id, 'high');

          const successMsg = language === 'en-US'
            ? `Marked as high priority: "${matchedTodo.title}"`
            : `اہم بنایا: "${matchedTodo.title}"`;

          setResult({
            success: true,
            message: successMsg,
            todo: matchedTodo,
          });
        } catch (err) {
          const errorMsg = language === 'en-US'
            ? 'Failed to update priority'
            : 'ترجیح اپ ڈیٹ کرنے میں ناکامی';

          setError(errorMsg);
          setResult({
            success: false,
            message: errorMsg,
          });
        }
        return;
      }

      // Execute set normal priority action
      if (command.action === 'set_normal_priority' && command.title) {
        // Find todo by title (fuzzy match)
        const matchedTodo = findTodoByTitle(todos, command.title);

        if (!matchedTodo) {
          // "Did you mean?" suggestions
          const suggestions = todos
            .filter(t => t.priority === 'high')
            .slice(0, 3)
            .map(t => t.title)
            .join(', ');

          const errorMsg = language === 'en-US'
            ? `Todo not found: "${command.title}". ${suggestions ? `Did you mean: ${suggestions}?` : ''}`
            : `ٹاسک نہیں ملا: "${command.title}". ${suggestions ? `کیا آپ کا مطلب: ${suggestions}؟` : ''}`;

          setError(errorMsg);
          setResult({
            success: false,
            message: errorMsg,
          });
          return;
        }

        // Skip if already normal priority
        if (matchedTodo.priority === 'normal') {
          const infoMsg = language === 'en-US'
            ? `Already normal priority: "${matchedTodo.title}"`
            : `پہلے سے نارمل: "${matchedTodo.title}"`;

          setResult({
            success: true,
            message: infoMsg,
            todo: matchedTodo,
          });
          return;
        }

        // Set normal priority
        try {
          await togglePriority(matchedTodo.id, 'normal');

          const successMsg = language === 'en-US'
            ? `Priority removed: "${matchedTodo.title}"`
            : `ترجیح ہٹائی: "${matchedTodo.title}"`;

          setResult({
            success: true,
            message: successMsg,
            todo: matchedTodo,
          });
        } catch (err) {
          const errorMsg = language === 'en-US'
            ? 'Failed to update priority'
            : 'ترجیح اپ ڈیٹ کرنے میں ناکامی';

          setError(errorMsg);
          setResult({
            success: false,
            message: errorMsg,
          });
        }
        return;
      }
    },
    [language, todos, createTodo, toggleComplete, togglePriority]
  );

  /**
   * Start voice recognition
   */
  const startVoice = useCallback(
    (lang?: VoiceLanguage) => {
      if (!voiceServiceRef.current) {
        setError('Speech recognition not supported in this browser');
        return;
      }

      const selectedLanguage = lang || language;
      setLanguage(selectedLanguage);
      setTranscript('');
      setError(null);
      setResult(null);

      voiceServiceRef.current.startListening(selectedLanguage, {
        onResult: (recognitionResult: RecognitionResult) => {
          // Update transcript in real-time
          setTranscript(recognitionResult.transcript);

          // Execute command when final result is received
          if (recognitionResult.isFinal) {
            executeCommand(recognitionResult.transcript);
          }
        },
        onError: (errorMessage: string) => {
          setError(errorMessage);
          setIsListening(false);
        },
        onEnd: () => {
          setIsListening(false);
        },
      });

      setIsListening(true);
    },
    [language, executeCommand]
  );

  /**
   * Stop voice recognition
   */
  const stopVoice = useCallback(() => {
    if (voiceServiceRef.current) {
      voiceServiceRef.current.stopListening();
    }
    setIsListening(false);
  }, []);

  /**
   * Update listening state based on voice service
   */
  useEffect(() => {
    const interval = setInterval(() => {
      if (voiceServiceRef.current) {
        const listening = voiceServiceRef.current.isListening();
        if (listening !== isListening) {
          setIsListening(listening);
        }
      }
    }, 100);

    return () => clearInterval(interval);
  }, [isListening]);

  return {
    isListening,
    transcript,
    error,
    language,
    isSupported,
    result,
    startVoice,
    stopVoice,
    setLanguage,
  };
}
