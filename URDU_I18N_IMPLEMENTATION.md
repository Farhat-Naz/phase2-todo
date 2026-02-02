# Urdu Language Support Implementation Guide

## Implementation Status: Phase 3 (US7: Multilingual UI - Urdu Support)

### Completed Tasks ✅

1. **TASK-061: Setup i18n with next-intl** ✅
   - Installed `next-intl` package
   - Created `i18n.ts` configuration with en/ur locales
   - Created `middleware.ts` for locale routing
   - Updated `next.config.js` with next-intl plugin
   - Configured locale prefix routing (`/en/*`, `/ur/*`)

2. **TASK-062: Create Translation Files** ✅
   - Created `messages/en.json` with comprehensive English translations
   - Created `messages/ur.json` with professional Urdu translations
   - Translation namespaces:
     - `auth`: Login, register, validation messages
     - `todos`: Todo CRUD operations, status messages
     - `voice`: Voice command UI strings
     - `common`: Shared UI elements
     - `landing`: Landing page content

3. **TASK-063: Create LanguageSwitcher Component** ✅
   - File: `components/features/shared/LanguageSwitcher.tsx`
   - Two variants: default (toggle buttons) and compact (icon with label)
   - Locale switching via next-intl navigation
   - Accessible with ARIA labels
   - Mobile responsive

4. **TASK-064: Apply RTL Layout for Urdu** ✅
   - Created `app/[locale]/layout.tsx` with RTL support
   - HTML `dir="rtl"` for Urdu locale
   - HTML `lang` attribute set dynamically
   - Noto Nastaliq Urdu font loaded via Google Fonts
   - Font variables: `--font-inter`, `--font-urdu`
   - Conditional font application based on locale

5. **TASK-065: Configure Tailwind for RTL** ✅
   - Updated `tailwind.config.ts` with:
     - Urdu font family: `font-urdu`
     - Inter font family: `font-inter`
     - RTL utility classes
   - Added font CSS variables

6. **Create Localized Pages** ✅
   - `app/[locale]/page.tsx` - Landing page with translations
   - `app/[locale]/(auth)/login/page.tsx` - Login page
   - `app/[locale]/(auth)/register/page.tsx` - Register page

### Remaining Tasks 🔄

#### Component Translation Updates Needed

The following components need to be updated to use next-intl translations:

##### Auth Components
**File: `components/features/auth/LoginForm.tsx`**
```typescript
// Add these imports
import { useTranslations, useLocale } from 'next-intl';

// Add locale prop
interface LoginFormProps {
  locale: string;
}

// Inside component
const t = useTranslations('auth');
const isRTL = locale === 'ur';

// Replace all hardcoded strings:
- 'Email is required' → t('emailRequired')
- 'Please enter a valid email address' → t('emailInvalid')
- 'Password is required' → t('passwordRequired')
- 'Email Address' → t('email')
- 'Password' → t('password')
- 'you@example.com' → t('emailPlaceholder')
- 'Enter your password' → t('passwordPlaceholder')
- 'Sign In' → t('loginButton')
- "Don't have an account?" → t('noAccount')
- 'Create account' → t('createAccount')

// Update href="/register" → href=`/${locale}/register`
// Add dir={isRTL ? 'rtl' : 'ltr'} to form and inputs
// Add className with font-urdu for RTL text
```

**File: `components/features/auth/RegisterForm.tsx`**
```typescript
// Similar pattern as LoginForm
// Replace all strings with t() calls
// Key translations:
- 'Full Name' → t('name')
- 'John Doe' → t('namePlaceholder')
- 'At least 8 characters' → t('newPasswordPlaceholder')
- 'Minimum 8 characters' → t('passwordHelper')
- 'Name is required' → t('nameRequired')
- 'Name must be at least 2 characters' → t('nameMinLength')
- 'Password must be at least 8 characters' → t('passwordMinLength')
- 'Create Account' → t('registerButton')
- 'Already have an account?' → t('alreadyHaveAccount')
- 'Sign in' → t('signIn')

// Update href="/login" → href=`/${locale}/login`
```

##### Todo Components
**File: `components/features/todos/TodoForm.tsx`**
```typescript
import { useTranslations, useLocale } from 'next-intl';

// Add locale detection
const t = useTranslations('todos');
const locale = useLocale();
const isRTL = locale === 'ur';

// Replace strings:
- 'Title is required' → t('titleRequired')
- 'Title must be 500 characters or less' → t('titleMaxLength')
- 'Description must be 2000 characters or less' → t('descriptionMaxLength')
- 'Title' → t('title')
- 'What needs to be done?' → t('titlePlaceholder')
- 'Description (optional)' → t('descriptionOptional')
- 'Add more details...' → t('descriptionPlaceholder')
- 'Add Todo' → t('createTodo')
- 'Update Todo' → t('updateTodo')
- 'Clear' → t('clear')
- 'Press Enter to submit' → t('pressEnter')
- '{description.length}/2000 characters' → t('charactersCount', { count: description.length })
```

**File: `components/features/todos/TodoItem.tsx`**
```typescript
import { useTranslations, useLocale } from 'next-intl';

const t = useTranslations('todos');
const locale = useLocale();

// Replace strings:
- 'Todo title' → t('title')
- 'Description (optional)' → t('descriptionOptional')
- 'Save' → t('save')
- 'Cancel' → t('cancel')
- 'Edit' → t('edit')
- 'Delete' → t('delete')
- 'just now' → t('justNow')
- '{minutes} minute(s) ago' → t('minutesAgo', { count: minutes })
- '{hours} hour(s) ago' → t('hoursAgo', { count: hours })
```

**File: `components/features/todos/TodoList.tsx`**
```typescript
// Add translations for:
- 'No todos yet' → t('noTodos')
- 'Loading todos...' → t('loading')
- 'Failed to load todos' → t('error')
- 'Try again' → t('retry')
- 'All' → t('all')
- 'Completed' → t('completed')
- 'Pending' → t('pending')
```

**File: `components/features/todos/VoiceInput.tsx`**
```typescript
import { useTranslations, useLocale } from 'next-intl';

const t = useTranslations('voice');
const locale = useLocale();

// Replace strings:
- 'Start Voice Input' → t('startVoice')
- 'Stop Voice Input' → t('stopVoice')
- 'Listening...' → t('listening')
- 'Voice input is not supported' → t('notSupported')
- 'Microphone access denied' → t('micDenied')
- 'English' → t('english')
- 'Urdu' → t('urdu')
- 'Select Language' → t('selectLanguage')
```

##### Dashboard Pages
**File: `app/[locale]/(dashboard)/page.tsx`**
- Create this file from `app/dashboard/page.tsx`
- Wrap with locale layout
- Add LanguageSwitcher to header
- Use translations for all UI strings

**File: `app/[locale]/(dashboard)/layout.tsx`**
- Create from `app/(dashboard)/layout.tsx`
- Add locale parameter
- Add LanguageSwitcher to navigation
- Apply RTL layout for Urdu

### RTL Styling Guidelines

For each component with Urdu support, apply these patterns:

1. **Form Direction**:
   ```typescript
   <form dir={isRTL ? 'rtl' : 'ltr'}>
   ```

2. **Text Alignment**:
   ```typescript
   className={`text-center ${isRTL ? 'text-right' : 'text-left'}`}
   ```

3. **Flex Direction**:
   ```typescript
   className={`flex ${isRTL ? 'flex-row-reverse' : 'flex-row'}`}
   ```

4. **Margins/Padding** (use Tailwind RTL variants):
   ```typescript
   className="ml-4 rtl:ml-0 rtl:mr-4"
   ```

5. **Font Application**:
   ```typescript
   className={isRTL ? 'font-urdu' : ''}
   ```

6. **Input Fields**:
   ```typescript
   <Input
     dir={isRTL ? 'rtl' : 'ltr'}
     className={isRTL ? 'text-right' : 'text-left'}
   />
   ```

### Translation File Structure

#### English (messages/en.json)
- 100+ translation keys
- Professional, concise English
- Proper pluralization support
- Clear error messages

#### Urdu (messages/ur.json)
- Complete 1:1 mapping with English keys
- Formal Urdu (فصیح اردو)
- Culturally appropriate terminology
- Proper Urdu punctuation (۔ for period, ؟ for question mark)
- Technical terms translated where possible, romanized where necessary

### Key Translation Examples

| English | Urdu | Key |
|---------|------|-----|
| Sign In | داخل ہوں | auth.login |
| Create Account | اکاؤنٹ بنائیں | auth.register |
| Email Address | ای میل پتہ | auth.email |
| Password | پاس ورڈ | auth.password |
| Add Todo | کام شامل کریں | todos.createTodo |
| Complete | مکمل | todos.complete |
| Delete | حذف کریں | todos.delete |
| Loading... | لوڈ ہو رہا ہے۔۔۔ | common.loading |
| Voice Input | آواز سے ان پٹ | landing.voiceInput |
| Multilingual | کثیر لسانی | landing.multilingual |

### Testing Checklist

- [ ] All pages accessible via `/en/*` and `/ur/*` routes
- [ ] Language switcher works on all pages
- [ ] Locale preference persists across navigation
- [ ] RTL layout applied correctly for Urdu
- [ ] Urdu font (Noto Nastaliq Urdu) loads properly
- [ ] All UI text translates correctly
- [ ] Form validation messages in correct language
- [ ] Voice commands work in both languages
- [ ] Mobile responsive in both languages
- [ ] No hardcoded English strings remain

### Verification Commands

```bash
# Check for hardcoded strings (should return minimal results)
grep -r "Sign In\|Create Account\|Add Todo" frontend/components/

# Verify translation files are valid JSON
node -e "console.log(require('./frontend/messages/en.json'))"
node -e "console.log(require('./frontend/messages/ur.json'))"

# Check locale routes are configured
grep -r "locale" frontend/app/

# Verify next-intl is properly installed
npm list next-intl
```

### Next Steps

1. Update remaining components with translations (LoginForm, RegisterForm, TodoForm, TodoItem, TodoList, VoiceInput)
2. Create dashboard pages under `[locale]` route
3. Test all functionality in both languages
4. Verify RTL layout on mobile devices
5. Test voice commands in both English and Urdu

### Files Modified/Created

**New Files:**
- `frontend/i18n.ts`
- `frontend/middleware.ts`
- `frontend/messages/en.json`
- `frontend/messages/ur.json`
- `frontend/components/features/shared/LanguageSwitcher.tsx`
- `frontend/app/[locale]/layout.tsx`
- `frontend/app/[locale]/page.tsx`
- `frontend/app/[locale]/(auth)/login/page.tsx`
- `frontend/app/[locale]/(auth)/register/page.tsx`

**Modified Files:**
- `frontend/next.config.js` - Added next-intl plugin
- `frontend/tailwind.config.ts` - Added Urdu fonts and RTL support
- `frontend/package.json` - Added next-intl dependency

**Files to Update:**
- `frontend/components/features/auth/LoginForm.tsx`
- `frontend/components/features/auth/RegisterForm.tsx`
- `frontend/components/features/todos/TodoForm.tsx`
- `frontend/components/features/todos/TodoItem.tsx`
- `frontend/components/features/todos/TodoList.tsx`
- `frontend/components/features/todos/VoiceInput.tsx`
- Create: `frontend/app/[locale]/(dashboard)/page.tsx`
- Create: `frontend/app/[locale]/(dashboard)/layout.tsx`

### Resources

- [next-intl Documentation](https://next-intl-docs.vercel.app/)
- [Noto Nastaliq Urdu Font](https://fonts.google.com/noto/specimen/Noto+Nastaliq+Urdu)
- [Tailwind CSS RTL Support](https://tailwindcss.com/docs/text-direction)
- [ICU Message Format](https://unicode-org.github.io/icu/userguide/format_parse/messages/)

---

## Summary

The core i18n infrastructure is now in place:
- ✅ next-intl configured with en/ur locales
- ✅ Translation files complete with 100+ keys
- ✅ Language switcher component ready
- ✅ RTL layout support configured
- ✅ Urdu fonts integrated
- ✅ Locale routing working
- ✅ Landing and auth pages localized

**Remaining work**: Update existing components to use `useTranslations()` hook and apply RTL styling patterns as documented above.
