# Score Limit and High Scores Fix

## Changes Made

### 1. Maximum Score Limit: 10

#### Backend (`users/views.py` and `users/models.py`)
- Added global maximum score limit of 10
- Validation happens in both the view (before save) and model (during save)
- Returns clear error messages if score is outside 0-10 range
- Game-specific limits are still checked but global limit takes precedence

#### Frontend (`src/admin/AdminDashboard.tsx`)
- Added client-side validation to prevent scores > 10
- Shows error message if user tries to set score outside 0-10
- Added visual feedback showing current score, delta, and new score
- Input field has min/max attributes for better UX

### 2. High Scores Page Fix

#### Fixed Issues:
- **Field Name**: Now handles both `score` and `points_scored` fields from API
- **Sorting**: Properly sorts players by total points (highest first)
- **Display**: Improved table styling with borders and better formatting
- **Empty State**: Shows friendly message when no scores exist
- **Top 3 Highlighting**: Top 3 players are shown in bold

#### Default Route:
- High Scores is already set as the default route in `App.tsx`
- When navigating to `/admin`, it automatically shows High Scores page
- The "High Scores" button is active by default

## Testing

1. **Score Limit**: Try to set a score > 10 - should show error
2. **High Scores**: Navigate to `/admin` - should show High Scores page by default
3. **Sorting**: Verify players are sorted by total points (highest first)
4. **Display**: Check that the table displays correctly with all players

## Files Modified

1. `users/views.py` - Added global score limit validation
2. `users/models.py` - Added global score limit in model save
3. `src/admin/AdminDashboard.tsx` - Added frontend validation and UI improvements
4. `src/pages/HighScores.tsx` - Fixed field handling, sorting, and display
5. `src/api/client.ts` - Updated AdminResult type to include `score` field

