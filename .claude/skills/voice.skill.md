# Voice Recognition and Command Processing Skill

Reusable logic for speech-to-text recognition, natural language intent classification, and command mapping for voice-controlled Todo operations.

## Purpose

This skill provides consistent patterns for:
- **Speech Recognition**: Convert voice input to text using Web Speech API
- **Intent Classification**: Map natural language commands to application actions
- **Command Mapping**: Translate intents to executable Todo operations

## Usage Context

**Used by:**
- Voice Agent (voice input processing)
- Urdu Agent (Urdu language voice commands)

**When to apply:**
- Implementing voice input functionality
- Adding voice command support to UI components
- Processing Urdu language voice commands
- Classifying user intent from natural language
- Mapping voice commands to API calls

## Core Patterns

### 1. Speech Recognition (Web Speech API)

```typescript
// Speech recognition configuration
interface SpeechRecognitionConfig {
  language: string;           // 'en-US', 'ur-PK'
  continuous: boolean;        // Continuous listening
  interimResults: boolean;    // Show interim results
  maxAlternatives: number;    // Number of alternatives
}

// Recognition result
interface RecognitionResult {
  transcript: string;         // Recognized text
  confidence: number;         // Confidence score (0-1)
  isFinal: boolean;          // Is final result
  alternatives?: string[];    // Alternative transcripts
}

// Speech recognition hook for React
function useSpeechRecognition(config: SpeechRecognitionConfig) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    // Check browser support
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setError('Speech recognition not supported in this browser');
      return;
    }

    // Initialize recognition
    const recognition = new SpeechRecognition();
    recognition.lang = config.language;
    recognition.continuous = config.continuous;
    recognition.interimResults = config.interimResults;
    recognition.maxAlternatives = config.maxAlternatives;

    // Event handlers
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      const result = event.results[event.results.length - 1];
      const transcript = result[0].transcript;
      const confidence = result[0].confidence;

      setTranscript(transcript);

      // Trigger callback with result
      if (result.isFinal && onResult) {
        onResult({
          transcript,
          confidence,
          isFinal: true,
          alternatives: Array.from(result)
            .slice(1)
            .map(alt => alt.transcript)
        });
      }
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('Speech recognition error:', event.error);
      setError(event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [config.language]);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setError(null);
      setTranscript('');
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const resetTranscript = () => {
    setTranscript('');
  };

  return {
    isListening,
    transcript,
    error,
    startListening,
    stopListening,
    resetTranscript,
    isSupported: !!recognitionRef.current
  };
}
```

### 2. Intent Classification

```typescript
// Intent types for Todo application
enum TodoIntent {
  CREATE_TODO = 'create_todo',
  COMPLETE_TODO = 'complete_todo',
  UNCOMPLETE_TODO = 'uncomplete_todo',
  DELETE_TODO = 'delete_todo',
  LIST_TODOS = 'list_todos',
  FILTER_COMPLETED = 'filter_completed',
  FILTER_PENDING = 'filter_pending',
  SEARCH_TODO = 'search_todo',
  UNKNOWN = 'unknown'
}

// Intent classification result
interface ClassifiedIntent {
  intent: TodoIntent;
  confidence: number;
  entities: Record<string, string>;  // Extracted entities
  rawText: string;
}

// Intent classification patterns (regex-based)
const INTENT_PATTERNS = {
  // Create todo patterns
  [TodoIntent.CREATE_TODO]: [
    /^(?:add|create|new|make)\s+(?:todo|task|item)?\s*:?\s*(.+)$/i,
    /^(?:todo|task|item)?\s*:?\s*(.+)$/i,  // Implicit create
    /^(?:i need to|i have to|i should|i want to)\s+(.+)$/i,
    /^(?:remind me to)\s+(.+)$/i
  ],

  // Complete todo patterns
  [TodoIntent.COMPLETE_TODO]: [
    /^(?:complete|finish|done|mark as done)\s+(?:todo|task|item)?\s*:?\s*(.+)$/i,
    /^(?:i (?:finished|completed|did))\s+(.+)$/i,
    /^(?:check off|tick)\s+(.+)$/i
  ],

  // Uncomplete todo patterns
  [TodoIntent.UNCOMPLETE_TODO]: [
    /^(?:uncomplete|unfinish|mark as pending|mark as incomplete)\s+(?:todo|task|item)?\s*:?\s*(.+)$/i,
    /^(?:uncheck|untick)\s+(.+)$/i
  ],

  // Delete todo patterns
  [TodoIntent.DELETE_TODO]: [
    /^(?:delete|remove|cancel)\s+(?:todo|task|item)?\s*:?\s*(.+)$/i,
    /^(?:get rid of|throw away)\s+(.+)$/i
  ],

  // List todos patterns
  [TodoIntent.LIST_TODOS]: [
    /^(?:show|list|display|view|get)\s+(?:all\s+)?(?:my\s+)?(?:todos|tasks|items)$/i,
    /^(?:what are my|what's on my)\s+(?:todo list|task list)$/i,
    /^(?:todos|tasks|items)$/i
  ],

  // Filter completed patterns
  [TodoIntent.FILTER_COMPLETED]: [
    /^(?:show|list|display|view)\s+(?:all\s+)?(?:completed|finished|done)\s+(?:todos|tasks|items)$/i,
    /^(?:what have i|what did i)\s+(?:complete|finish|do)$/i
  ],

  // Filter pending patterns
  [TodoIntent.FILTER_PENDING]: [
    /^(?:show|list|display|view)\s+(?:all\s+)?(?:pending|incomplete|unfinished|active)\s+(?:todos|tasks|items)$/i,
    /^(?:what do i need to|what should i)\s+(?:do|complete)$/i
  ],

  // Search todo patterns
  [TodoIntent.SEARCH_TODO]: [
    /^(?:search|find|look for)\s+(?:todo|task|item)?\s*:?\s*(.+)$/i,
    /^(?:where is|do i have)\s+(.+)$/i
  ]
};

// Urdu intent patterns (Roman Urdu transliteration)
const URDU_INTENT_PATTERNS = {
  [TodoIntent.CREATE_TODO]: [
    /^(?:نیا|اضافہ کریں|بنائیں)\s+(.+)$/i,  // Urdu script
    /^(?:naya|shamil karen|banayein)\s+(?:kaam|todo)?\s*:?\s*(.+)$/i,  // Roman Urdu
    /^(?:mujhe|mujhay)\s+(.+)\s+(?:karna hai|karni hai)$/i
  ],

  [TodoIntent.COMPLETE_TODO]: [
    /^(?:مکمل|ختم)\s+(.+)$/i,  // Urdu script
    /^(?:mukammal|khatam|complete)\s+(?:karen|karo)?\s*:?\s*(.+)$/i,  // Roman Urdu
    /^(?:maine|mein ne)\s+(.+)\s+(?:kar liya|kiya)$/i
  ],

  [TodoIntent.DELETE_TODO]: [
    /^(?:حذف کریں|ہٹائیں)\s+(.+)$/i,  // Urdu script
    /^(?:delete|hatayein|mitayein)\s+(?:karen|karo)?\s*:?\s*(.+)$/i,  // Roman Urdu
  ],

  [TodoIntent.LIST_TODOS]: [
    /^(?:دکھائیں|فہرست)\s*(?:کام|todos)?$/i,  // Urdu script
    /^(?:dikhayein|list|sab)\s+(?:kaam|todos|tasks)?$/i,  // Roman Urdu
    /^(?:mere|meray)\s+(?:kaam|todos)\s+(?:dikhao|batao)$/i
  ],

  [TodoIntent.FILTER_COMPLETED]: [
    /^(?:مکمل|ختم شدہ)\s+(?:کام|todos)\s+(?:دکھائیں)?$/i,  // Urdu script
    /^(?:mukammal|complete)\s+(?:kaam|todos)\s+(?:dikhao|dikhayein)?$/i  // Roman Urdu
  ],

  [TodoIntent.FILTER_PENDING]: [
    /^(?:باقی|نامکمل)\s+(?:کام|todos)\s+(?:دکھائیں)?$/i,  // Urdu script
    /^(?:baqi|pending|namukammal)\s+(?:kaam|todos)\s+(?:dikhao|dikhayein)?$/i  // Roman Urdu
  ]
};

// Intent classifier
function classifyIntent(
  text: string,
  language: 'en' | 'ur' = 'en'
): ClassifiedIntent {
  const normalizedText = text.trim().toLowerCase();
  const patterns = language === 'ur' ? URDU_INTENT_PATTERNS : INTENT_PATTERNS;

  // Try to match against patterns
  for (const [intent, regexList] of Object.entries(patterns)) {
    for (const regex of regexList) {
      const match = normalizedText.match(regex);
      if (match) {
        // Extract entities from capture groups
        const entities: Record<string, string> = {};
        if (match[1]) {
          entities.title = match[1].trim();
        }

        return {
          intent: intent as TodoIntent,
          confidence: 0.9,  // High confidence for regex match
          entities,
          rawText: text
        };
      }
    }
  }

  // No pattern matched - return unknown intent
  return {
    intent: TodoIntent.UNKNOWN,
    confidence: 0.0,
    entities: {},
    rawText: text
  };
}

// Advanced: ML-based intent classification (optional)
// This would use a trained model for better accuracy
async function classifyIntentML(text: string): Promise<ClassifiedIntent> {
  // This is a placeholder for ML-based classification
  // In production, you might use:
  // - TensorFlow.js with a trained model
  // - API call to backend NLP service
  // - Third-party NLU service (Dialogflow, Wit.ai, etc.)

  // For now, fall back to pattern-based classification
  return classifyIntent(text);
}
```

### 3. Command Mapping

```typescript
// Command execution result
interface CommandResult {
  success: boolean;
  message: string;
  data?: any;
}

// Todo operations interface
interface TodoOperations {
  createTodo: (title: string) => Promise<any>;
  completeTodo: (titleOrId: string) => Promise<any>;
  uncompleteTodo: (titleOrId: string) => Promise<any>;
  deleteTodo: (titleOrId: string) => Promise<any>;
  listTodos: () => Promise<any[]>;
  filterCompleted: () => Promise<any[]>;
  filterPending: () => Promise<any[]>;
  searchTodos: (query: string) => Promise<any[]>;
}

// Command mapper
class VoiceCommandMapper {
  constructor(private operations: TodoOperations) {}

  async executeCommand(intent: ClassifiedIntent): Promise<CommandResult> {
    try {
      switch (intent.intent) {
        case TodoIntent.CREATE_TODO:
          return await this.handleCreateTodo(intent);

        case TodoIntent.COMPLETE_TODO:
          return await this.handleCompleteTodo(intent);

        case TodoIntent.UNCOMPLETE_TODO:
          return await this.handleUncompleteTodo(intent);

        case TodoIntent.DELETE_TODO:
          return await this.handleDeleteTodo(intent);

        case TodoIntent.LIST_TODOS:
          return await this.handleListTodos();

        case TodoIntent.FILTER_COMPLETED:
          return await this.handleFilterCompleted();

        case TodoIntent.FILTER_PENDING:
          return await this.handleFilterPending();

        case TodoIntent.SEARCH_TODO:
          return await this.handleSearchTodo(intent);

        case TodoIntent.UNKNOWN:
          return {
            success: false,
            message: "I didn't understand that command. Please try again."
          };

        default:
          return {
            success: false,
            message: "Command not supported yet."
          };
      }
    } catch (error) {
      return {
        success: false,
        message: `Error executing command: ${error.message}`
      };
    }
  }

  private async handleCreateTodo(intent: ClassifiedIntent): Promise<CommandResult> {
    const title = intent.entities.title;

    if (!title) {
      return {
        success: false,
        message: "Please specify what todo to create."
      };
    }

    const todo = await this.operations.createTodo(title);

    return {
      success: true,
      message: `Created todo: "${title}"`,
      data: todo
    };
  }

  private async handleCompleteTodo(intent: ClassifiedIntent): Promise<CommandResult> {
    const titleOrId = intent.entities.title;

    if (!titleOrId) {
      return {
        success: false,
        message: "Please specify which todo to complete."
      };
    }

    // Find and complete the todo
    const todo = await this.operations.completeTodo(titleOrId);

    return {
      success: true,
      message: `Completed todo: "${titleOrId}"`,
      data: todo
    };
  }

  private async handleUncompleteTodo(intent: ClassifiedIntent): Promise<CommandResult> {
    const titleOrId = intent.entities.title;

    if (!titleOrId) {
      return {
        success: false,
        message: "Please specify which todo to mark as incomplete."
      };
    }

    const todo = await this.operations.uncompleteTodo(titleOrId);

    return {
      success: true,
      message: `Marked as incomplete: "${titleOrId}"`,
      data: todo
    };
  }

  private async handleDeleteTodo(intent: ClassifiedIntent): Promise<CommandResult> {
    const titleOrId = intent.entities.title;

    if (!titleOrId) {
      return {
        success: false,
        message: "Please specify which todo to delete."
      };
    }

    await this.operations.deleteTodo(titleOrId);

    return {
      success: true,
      message: `Deleted todo: "${titleOrId}"`
    };
  }

  private async handleListTodos(): Promise<CommandResult> {
    const todos = await this.operations.listTodos();

    return {
      success: true,
      message: `You have ${todos.length} todos`,
      data: todos
    };
  }

  private async handleFilterCompleted(): Promise<CommandResult> {
    const todos = await this.operations.filterCompleted();

    return {
      success: true,
      message: `You have ${todos.length} completed todos`,
      data: todos
    };
  }

  private async handleFilterPending(): Promise<CommandResult> {
    const todos = await this.operations.filterPending();

    return {
      success: true,
      message: `You have ${todos.length} pending todos`,
      data: todos
    };
  }

  private async handleSearchTodo(intent: ClassifiedIntent): Promise<CommandResult> {
    const query = intent.entities.title;

    if (!query) {
      return {
        success: false,
        message: "Please specify what to search for."
      };
    }

    const todos = await this.operations.searchTodos(query);

    return {
      success: true,
      message: `Found ${todos.length} matching todos`,
      data: todos
    };
  }
}
```

### 4. Complete Voice Command Flow

```typescript
'use client';

import { useState } from 'react';
import { useSpeechRecognition } from './speech-recognition';
import { classifyIntent } from './intent-classifier';
import { VoiceCommandMapper } from './command-mapper';

interface VoiceCommandHandlerProps {
  language: 'en-US' | 'ur-PK';
  todoOperations: TodoOperations;
}

export function useVoiceCommands({
  language,
  todoOperations
}: VoiceCommandHandlerProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<CommandResult | null>(null);

  // Initialize command mapper
  const commandMapper = new VoiceCommandMapper(todoOperations);

  // Speech recognition configuration
  const {
    isListening,
    transcript,
    error: speechError,
    startListening,
    stopListening,
    resetTranscript
  } = useSpeechRecognition({
    language,
    continuous: false,
    interimResults: true,
    maxAlternatives: 3,
    onResult: async (recognitionResult) => {
      // Only process final results
      if (!recognitionResult.isFinal) return;

      setIsProcessing(true);

      try {
        // Step 1: Classify intent
        const langCode = language.startsWith('ur') ? 'ur' : 'en';
        const intent = classifyIntent(recognitionResult.transcript, langCode);

        // Step 2: Execute command
        const commandResult = await commandMapper.executeCommand(intent);

        // Step 3: Set result
        setResult(commandResult);
      } catch (error) {
        setResult({
          success: false,
          message: `Error processing command: ${error.message}`
        });
      } finally {
        setIsProcessing(false);
        resetTranscript();
      }
    }
  });

  const startVoiceCommand = () => {
    setResult(null);
    startListening();
  };

  const stopVoiceCommand = () => {
    stopListening();
  };

  return {
    isListening,
    isProcessing,
    transcript,
    result,
    error: speechError,
    startVoiceCommand,
    stopVoiceCommand
  };
}

// Example component usage
export function VoiceCommandButton() {
  const {
    isListening,
    isProcessing,
    transcript,
    result,
    error,
    startVoiceCommand,
    stopVoiceCommand
  } = useVoiceCommands({
    language: 'en-US',
    todoOperations: {
      createTodo: async (title) => {
        // API call to create todo
        return fetch('/api/todos', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ title })
        }).then(res => res.json());
      },
      // ... other operations
    }
  });

  return (
    <div>
      <button
        onClick={isListening ? stopVoiceCommand : startVoiceCommand}
        disabled={isProcessing}
      >
        {isListening ? '🛑 Stop' : '🎤 Voice Command'}
      </button>

      {transcript && (
        <p className="text-gray-600">
          Listening: {transcript}
        </p>
      )}

      {isProcessing && (
        <p className="text-blue-600">Processing command...</p>
      )}

      {result && (
        <div className={result.success ? 'text-green-600' : 'text-red-600'}>
          {result.message}
        </div>
      )}

      {error && (
        <p className="text-red-600">Error: {error}</p>
      )}
    </div>
  );
}
```

## Implementation Checklist

When implementing voice commands, ensure:

- [ ] Web Speech API browser support is checked before initialization
- [ ] Appropriate language code is set ('en-US', 'ur-PK')
- [ ] Microphone permissions are requested from the user
- [ ] Visual feedback is provided during listening/processing
- [ ] Interim results are shown for better UX (optional)
- [ ] Final transcripts are processed with intent classification
- [ ] Confidence scores are checked before executing commands
- [ ] Error handling covers speech recognition failures
- [ ] Multi-language support is properly configured
- [ ] Command execution results are displayed to the user
- [ ] State management prevents concurrent voice commands

## Language Support

### English (en-US)
- **Commands**: "Add todo: Buy groceries", "Complete todo: Buy groceries", "Show all todos"
- **Patterns**: Imperative and declarative forms
- **Alternatives**: Multiple phrasings for same intent

### Urdu (ur-PK)
- **Script Support**: Both Urdu script (اردو) and Roman Urdu (transliteration)
- **Commands**: "نیا کام: دودھ خریدیں" or "naya kaam: doodh khareedein"
- **RTL Handling**: Proper right-to-left text display
- **Patterns**: Natural Urdu language patterns

## Security Considerations

1. **Microphone Permissions**: Always request user consent before accessing microphone
2. **Privacy**: Speech data should not be logged or transmitted without consent
3. **API Security**: Voice commands should use same authentication as manual input
4. **Input Validation**: Validate extracted entities before executing commands
5. **Rate Limiting**: Prevent abuse through rapid voice command execution

## Browser Support

Web Speech API support:
- ✅ Chrome/Edge (desktop and Android)
- ✅ Safari (iOS and macOS)
- ❌ Firefox (limited support)
- ⚠️ Check `window.SpeechRecognition` or `window.webkitSpeechRecognition`

## Best Practices

1. **User Feedback**: Provide visual/audio feedback during all stages
2. **Error Recovery**: Allow users to retry failed commands
3. **Fallback UI**: Provide manual input option when voice fails
4. **Noise Handling**: Filter out background noise and low-confidence results
5. **Context Awareness**: Consider recent actions to disambiguate commands
6. **Accessibility**: Ensure voice commands complement, not replace, traditional input
7. **Testing**: Test with various accents, speaking speeds, and environments
8. **Performance**: Debounce interim results to avoid excessive processing

## Testing Considerations

- Test with different accents and speaking styles
- Test in noisy environments
- Test with low confidence scores
- Test intent classification edge cases
- Test command execution failures
- Test browser compatibility
- Mock Web Speech API in unit tests
- Test Urdu language patterns thoroughly

## Integration Points

- **Web Speech API**: Browser native speech recognition
- **Todo API**: Backend API for CRUD operations
- **Better Auth**: User authentication for command execution
- **State Management**: React state or global state (Zustand, Redux)
- **UI Components**: Visual feedback during voice interaction

## Advanced Features (Optional)

### 1. Context-Aware Commands
```typescript
// Track recent commands to disambiguate
const context = {
  lastCreatedTodo: 'Buy groceries',
  lastAction: 'create'
};

// Command: "Complete it" -> Complete the last created/mentioned todo
```

### 2. Multi-Step Commands
```typescript
// Handle complex commands with multiple steps
// "Add three todos: Buy milk, Call mom, Finish report"
```

### 3. Natural Language Processing (NLP)
```typescript
// Use advanced NLP for better intent extraction
// Third-party services: Dialogflow, Wit.ai, LUIS, Rasa
```

### 4. Voice Feedback (Text-to-Speech)
```typescript
const speak = (text: string, lang: string = 'en-US') => {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  window.speechSynthesis.speak(utterance);
};

// Provide audio confirmation
speak("Todo created successfully");
```

## Performance Optimization

1. **Debounce Interim Results**: Avoid excessive processing
2. **Cache Intent Patterns**: Compile regex patterns once
3. **Lazy Load Voice Module**: Load only when user enables voice
4. **Background Processing**: Use Web Workers for heavy NLP (if needed)
5. **Optimistic UI**: Update UI before API confirmation

## Accessibility

- Provide keyboard shortcuts as alternative to voice
- Ensure screen reader compatibility
- Support both voice and manual input simultaneously
- Clear visual indicators for voice state
- Error messages should be both visual and audible (optional)
