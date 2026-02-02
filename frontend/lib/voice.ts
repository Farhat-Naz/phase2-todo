/**
 * Voice Recognition Service and Intent Parser
 * Implements Web Speech API wrapper with English and Urdu support
 * Follows patterns from voice.skill.md
 */

/**
 * Supported languages for voice recognition
 */
export type VoiceLanguage = 'en-US' | 'ur-PK';

/**
 * Voice command actions
 */
export type VoiceAction = 'create' | 'complete' | 'set_high_priority' | 'set_normal_priority' | 'unknown';

/**
 * Parsed voice command result
 */
export interface VoiceCommand {
  action: VoiceAction;
  title?: string;
}

/**
 * Speech recognition result
 */
export interface RecognitionResult {
  transcript: string;
  confidence: number;
  isFinal: boolean;
}

/**
 * Voice recognition event handlers
 */
export interface VoiceRecognitionHandlers {
  onResult?: (result: RecognitionResult) => void;
  onError?: (error: string) => void;
  onEnd?: () => void;
}

/**
 * Browser compatibility check for Web Speech API
 */
export function isSpeechRecognitionSupported(): boolean {
  if (typeof window === 'undefined') return false;

  const SpeechRecognition =
    (window as any).SpeechRecognition ||
    (window as any).webkitSpeechRecognition;

  return !!SpeechRecognition;
}

/**
 * Voice Recognition Service
 * Wrapper for Web Speech API with English and Urdu support
 */
export class VoiceRecognitionService {
  private recognition: any = null;
  private isActive = false;
  private handlers: VoiceRecognitionHandlers = {};

  constructor() {
    if (isSpeechRecognitionSupported()) {
      const SpeechRecognition =
        (window as any).SpeechRecognition ||
        (window as any).webkitSpeechRecognition;

      this.recognition = new SpeechRecognition();
      this.setupRecognition();
    }
  }

  /**
   * Setup speech recognition configuration
   */
  private setupRecognition() {
    if (!this.recognition) return;

    // Single command mode (stop after one recognition)
    this.recognition.continuous = false;

    // Show interim results for better UX
    this.recognition.interimResults = true;

    // Number of alternative transcripts
    this.recognition.maxAlternatives = 1;

    // Event handlers
    this.recognition.onresult = (event: any) => {
      const result = event.results[event.results.length - 1];
      const transcript = result[0].transcript;
      const confidence = result[0].confidence;
      const isFinal = result.isFinal;

      if (this.handlers.onResult) {
        this.handlers.onResult({
          transcript,
          confidence,
          isFinal,
        });
      }
    };

    this.recognition.onerror = (event: any) => {
      let errorMessage = 'Speech recognition error';

      switch (event.error) {
        case 'no-speech':
          errorMessage = 'No speech detected. Please try again.';
          break;
        case 'audio-capture':
          errorMessage = 'Microphone not found. Please check your device.';
          break;
        case 'not-allowed':
          errorMessage = 'Microphone access denied. Please enable microphone permissions.';
          break;
        case 'network':
          errorMessage = 'Network error. Please check your connection.';
          break;
        case 'aborted':
          errorMessage = 'Speech recognition aborted.';
          break;
        default:
          errorMessage = `Speech recognition error: ${event.error}`;
      }

      if (this.handlers.onError) {
        this.handlers.onError(errorMessage);
      }

      this.isActive = false;
    };

    this.recognition.onend = () => {
      this.isActive = false;

      if (this.handlers.onEnd) {
        this.handlers.onEnd();
      }
    };
  }

  /**
   * Start listening for voice input
   */
  startListening(language: VoiceLanguage, handlers: VoiceRecognitionHandlers) {
    if (!this.recognition) {
      if (handlers.onError) {
        handlers.onError('Speech recognition not supported in this browser');
      }
      return;
    }

    if (this.isActive) {
      return;
    }

    this.handlers = handlers;
    this.recognition.lang = language;

    try {
      this.recognition.start();
      this.isActive = true;
    } catch (error) {
      if (handlers.onError) {
        handlers.onError('Failed to start speech recognition');
      }
    }
  }

  /**
   * Stop listening
   */
  stopListening() {
    if (this.recognition && this.isActive) {
      this.recognition.stop();
      this.isActive = false;
    }
  }

  /**
   * Check if currently listening
   */
  isListening(): boolean {
    return this.isActive;
  }
}

/**
 * Parse voice command transcript into action and title
 * Supports English and Urdu patterns (both script and Roman)
 */
export function parseVoiceCommand(transcript: string, language: VoiceLanguage): VoiceCommand {
  const normalizedText = transcript.trim().toLowerCase();
  const isUrdu = language === 'ur-PK';

  // English patterns
  const englishCreatePatterns = [
    /^(?:add|create|new|make)\s+(?:todo|task|item)?\s*:?\s*(.+)$/i,
    /^(?:todo|task|item)\s*:?\s*(.+)$/i,
    /^(?:i need to|i have to|i should|i want to)\s+(.+)$/i,
    /^(?:remind me to)\s+(.+)$/i,
  ];

  const englishCompletePatterns = [
    /^(?:complete|finish|done|mark as done|mark done)\s+(?:todo|task|item)?\s*:?\s*(.+)$/i,
    /^(?:i (?:finished|completed|did))\s+(.+)$/i,
    /^(?:check off|tick)\s+(.+)$/i,
  ];

  const englishHighPriorityPatterns = [
    /^(?:mark|set)\s+(?:as\s+)?high\s+priority\s*:?\s*(.+)$/i,
    /^(?:make|flag)\s+(.+)\s+(?:as\s+)?(?:high\s+)?(?:priority|urgent|important)$/i,
    /^high\s+priority\s*:?\s*(.+)$/i,
  ];

  const englishNormalPriorityPatterns = [
    /^(?:remove|clear)\s+(?:high\s+)?priority\s*(?:from)?\s*:?\s*(.+)$/i,
    /^(?:mark|set)\s+(.+)\s+(?:as\s+)?(?:normal|regular)(?:\s+priority)?$/i,
    /^(?:unflag|demote)\s+(.+)$/i,
  ];

  // Urdu patterns (script and Roman)
  const urduCreatePatterns = [
    /^(?:نیا|اضافہ کریں|بنائیں)\s+(.+)$/i,  // Urdu script
    /^(?:naya|shamil karen|banayein|banao)\s+(?:kaam|todo|task)?\s*:?\s*(.+)$/i,  // Roman Urdu
    /^(?:mujhe|mujhay)\s+(.+)\s+(?:karna hai|karni hai)$/i,
  ];

  const urduCompletePatterns = [
    /^(?:مکمل|ختم)\s+(?:کریں)?\s*(.+)$/i,  // Urdu script
    /^(?:mukammal|khatam|complete)\s+(?:karen|karo|krain)?\s*:?\s*(.+)$/i,  // Roman Urdu
    /^(?:maine|mein ne)\s+(.+)\s+(?:kar liya|kiya)$/i,
  ];

  const urduHighPriorityPatterns = [
    /^(?:اہم|ضروری)\s+(?:بنائیں)?\s*:?\s*(.+)$/i,  // Urdu script: "اہم بنائیں"
    /^(?:aham|zaroori)\s+(?:banayein|karo|karen)?\s*:?\s*(.+)$/i,  // Roman Urdu
    /^(?:tarjeeh|priority)\s+(?:dein|do)\s+(.+)$/i,  // "ترجیح دیں"
  ];

  const urduNormalPriorityPatterns = [
    /^(?:ترجیح|اہمیت)\s+(?:ہٹائیں|ختم کریں)\s*:?\s*(.+)$/i,  // Urdu script: "ترجیح ہٹائیں"
    /^(?:tarjeeh|ahamiyat)\s+(?:hataein|khatam karen|hatao)\s*:?\s*(.+)$/i,  // Roman Urdu
    /^(?:normal|mamuli)\s+(?:banao|karen|banayein)\s+(.+)$/i,  // "نارمل بنائیں"
  ];

  // Select patterns based on language
  const createPatterns = isUrdu ? urduCreatePatterns : englishCreatePatterns;
  const completePatterns = isUrdu ? urduCompletePatterns : englishCompletePatterns;
  const highPriorityPatterns = isUrdu ? urduHighPriorityPatterns : englishHighPriorityPatterns;
  const normalPriorityPatterns = isUrdu ? urduNormalPriorityPatterns : englishNormalPriorityPatterns;

  // Try to match high priority patterns first (more specific)
  for (const pattern of highPriorityPatterns) {
    const match = normalizedText.match(pattern);
    if (match && match[1]) {
      return {
        action: 'set_high_priority',
        title: match[1].trim(),
      };
    }
  }

  // Try to match normal priority patterns
  for (const pattern of normalPriorityPatterns) {
    const match = normalizedText.match(pattern);
    if (match && match[1]) {
      return {
        action: 'set_normal_priority',
        title: match[1].trim(),
      };
    }
  }

  // Try to match create patterns
  for (const pattern of createPatterns) {
    const match = normalizedText.match(pattern);
    if (match && match[1]) {
      return {
        action: 'create',
        title: match[1].trim(),
      };
    }
  }

  // Try to match complete patterns
  for (const pattern of completePatterns) {
    const match = normalizedText.match(pattern);
    if (match && match[1]) {
      return {
        action: 'complete',
        title: match[1].trim(),
      };
    }
  }

  // No pattern matched
  return {
    action: 'unknown',
  };
}

/**
 * Find matching todo by title (fuzzy match)
 * Uses case-insensitive substring matching
 */
export function findTodoByTitle<T extends { id: string; title: string }>(
  todos: T[],
  searchTitle: string
): T | null {
  const normalizedSearch = searchTitle.toLowerCase();

  // First try exact match
  const exactMatch = todos.find(
    todo => todo.title.toLowerCase() === normalizedSearch
  );
  if (exactMatch) return exactMatch;

  // Then try substring match
  const substringMatch = todos.find(
    todo => todo.title.toLowerCase().includes(normalizedSearch)
  );
  if (substringMatch) return substringMatch;

  // Then try reverse: search term contains todo title
  const reverseMatch = todos.find(
    todo => normalizedSearch.includes(todo.title.toLowerCase())
  );
  if (reverseMatch) return reverseMatch;

  // No match found
  return null;
}
