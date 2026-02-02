# ADR-003: Voice Command Architecture for Multilingual Priority Management

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-07
- **Feature:** 006-high-priority
- **Context:** The application must support hands-free priority management via voice commands in both English and Urdu (ur-PK). Users need to toggle task priority using natural language commands while the application disambiguates intent and matches todo titles with tolerance for speech recognition errors. The solution must work client-side without external API dependencies, maintain low latency (<1s), and gracefully degrade when voice APIs are unavailable.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Establishes voice interaction patterns
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - LLM-based NLU, keyword matching, external services
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects multilingual support, UX, client architecture
-->

## Decision

We will implement a **client-side pattern-based voice command system** using the Web Speech API with regex-based intent classification and Levenshtein distance fuzzy matching for entity extraction, supporting both English and Urdu (ur-PK) voice inputs without external dependencies.

**Components of this decision:**

- **Speech Recognition**:
  - API: Web Speech API (`webkitSpeechRecognition`)
  - Languages: English (`en-US`) and Urdu (`ur-PK`) with explicit `recognition.lang` switching
  - Mode: Non-continuous, single-command capture per interaction
  - Fallback: Manual text input when Web Speech API unavailable (Firefox, Safari partial support)

- **Intent Classification**:
  - **Pattern Matching**: Regex-based intent extraction using predefined patterns
  - **English Patterns**:
    - SET_HIGH: `/mark (as )?high priority:?\s*(.+)/i`, `/set priority high:?\s*(.+)/i`, `/prioritize:?\s*(.+)/i`
    - REMOVE_PRIORITY: `/remove priority:?\s*(.+)/i`, `/set priority normal:?\s*(.+)/i`
  - **Urdu Patterns**:
    - SET_HIGH: `/اہم بنائیں:?\s*(.+)/`, `/ترجیح دیں:?\s*(.+)/`
    - REMOVE_PRIORITY: `/ترجیح ہٹائیں:?\s*(.+)/`, `/عام بنائیں:?\s*(.+)/`
  - **Processing**: Client-side regex matching (no server round-trip, <10ms latency)

- **Entity Extraction (Todo Title Matching)**:
  - **Fuzzy Matching**: Levenshtein distance algorithm with 80% similarity threshold
  - **Disambiguation**: Show selection UI when multiple matches found (>1 todo with >80% similarity)
  - **Error Handling**: Clear error messages for no matches, with retry and manual fallback options

- **RTL (Right-to-Left) Support**:
  - Urdu UI elements rendered with `dir="rtl" lang="ur"`
  - Layout: RTL-aware flex/grid for Urdu text and icons
  - Fallback: RTL detection based on language selection

- **Browser Compatibility**:
  - **Full Support**: Chrome, Edge (Web Speech API with ur-PK)
  - **Partial Support**: Firefox, Safari (limited Urdu recognition, fallback to manual input)
  - **Feature Detection**: Check for `webkitSpeechRecognition` availability, show/hide microphone button

## Consequences

### Positive

- **Zero External Dependencies**: No API keys, no third-party NLU services, no recurring costs, no network latency
- **Low Latency**: Client-side processing achieves <800ms end-to-end (100ms transcription + <10ms matching + <50ms UI update)
- **Privacy-Preserving**: Voice data never leaves client browser, no cloud transcription services
- **Bilingual Support**: English and Urdu voice commands work seamlessly with explicit language switching
- **Offline-Capable**: Pattern matching works without internet (after initial page load)
- **Simple Implementation**: Regex patterns are easy to add, modify, and test without ML infrastructure
- **Predictable Behavior**: Deterministic matching (no ML randomness), easier debugging and testing

### Negative

- **Limited NLU**: Cannot handle complex variations, paraphrasing, or novel phrasings (only matches predefined patterns)
- **Brittle Regex**: Typos, accents, or unexpected phrasing cause match failures (80% threshold helps but isn't perfect)
- **No Context Awareness**: Cannot understand "mark the last one as high priority" (requires explicit title matching)
- **Accent Sensitivity**: Web Speech API transcription quality varies by user accent (especially for Urdu speakers)
- **Browser Limitations**: Firefox and Safari have limited/no ur-PK support, requiring manual fallback
- **Maintenance Overhead**: Adding new patterns requires manual regex updates (no automatic learning)
- **Scalability Concerns**: Pattern list grows linearly with voice commands (manageable for 10-20 commands, unwieldy at 100+)

## Alternatives Considered

### Alternative A: LLM-Based Intent Classification (OpenAI, Claude)
**Approach**: Send voice transcript to LLM API for intent extraction and entity recognition

**Why Rejected**:
- **Latency**: 200-500ms API round-trip + 100-300ms LLM inference = 300-800ms additional delay
- **Cost**: $0.0001-0.001 per command = $10-100/month for 100k commands (cost scales with usage)
- **API Dependency**: Requires API keys, fails when service is down, network required
- **Privacy Concerns**: Voice transcripts sent to third-party servers (user data leaves client)
- **Over-Engineering**: Simple priority commands don't need full natural language understanding
- **Unpredictability**: LLM responses can be non-deterministic, harder to test and debug

### Alternative B: Keyword-Only Matching (No Regex)
**Approach**: Match keywords like "high priority" and "remove priority" without entity extraction

**Why Rejected**:
- **Ambiguity**: "high priority" without todo title is unclear (which todo?)
- **False Positives**: User says "I need high priority" (statement, not command) → misinterpreted as command
- **No Disambiguation**: Cannot extract todo title from command
- **Poor UX**: Requires separate step to select todo after voice command (two-step interaction)
- **Brittle**: Slight variations ("make it high priority") fail to match

### Alternative C: Custom ML Model (TensorFlow, spaCy)
**Approach**: Train custom NLP model for intent classification and entity extraction

**Why Rejected**:
- **Complexity**: Requires training data, ML infrastructure, model hosting, and continuous retraining
- **Latency**: Model inference adds 50-200ms, deployment/bundling adds complexity
- **Bundle Size**: TensorFlow.js models add 5-10MB to bundle (unacceptable for web app)
- **Training Data**: No labeled dataset for priority commands in English/Urdu (would need to create)
- **Maintenance Burden**: Model retraining, versioning, and monitoring require dedicated ML infrastructure
- **Over-Engineering**: MVP doesn't justify ML complexity for 5-10 simple voice commands

### Alternative D: External Speech-to-Text Service (Google Cloud, AWS Transcribe)
**Approach**: Use cloud-based transcription with better multilingual support

**Why Rejected**:
- **Privacy**: Voice audio uploaded to third-party cloud services
- **Latency**: Network round-trip adds 150-300ms (not counting transcription time)
- **Cost**: $0.006-0.024 per minute of audio = ~$0.10-0.40 per month for 100 commands (low but not free)
- **Dependency**: Requires API keys, credentials management, and error handling for service outages
- **Complexity**: More moving parts than Web Speech API (authentication, retry logic, rate limiting)
- **Not Significantly Better**: Web Speech API already has good English/Urdu support in Chrome/Edge

### Alternative E: Server-Side Intent Processing (FastAPI Endpoint)
**Approach**: Send voice transcript to backend for pattern matching and entity extraction

**Why Rejected**:
- **Latency**: Additional 50-150ms network round-trip for simple regex operations
- **Unnecessary Load**: Server resources wasted on client-capable processing
- **Network Dependency**: Voice commands fail when offline or on poor networks
- **Scaling Costs**: Server must handle intent classification load (CPU/memory overhead)
- **Complexity**: Requires new API endpoint, authentication, error handling, and deployment coordination

## References

- Feature Spec: `specs/006-high-priority/spec.md` (User Story 3: Voice Commands)
- Research: `specs/006-high-priority/research.md` (Section 5: Voice Command Recognition, Section 11: Urdu Localization)
- Constitution: `.specify/memory/constitution.md` (Section 6: Voice Command Support)
- Implementation Plan: `specs/006-high-priority/plan.md` (pending)
- Related ADRs: ADR-002 (Frontend UX Pattern)
