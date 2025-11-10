# Score Update Fix (500 Internal Server Error)

## Issue
When trying to update a score via PUT `/api/admin/results/<result_id>/`, the server was returning a 500 Internal Server Error.

## Root Causes
1. **Serializer save method**: The admin_user and verified_by_admin fields weren't being set correctly before saving
2. **Game validation**: The GameResult model validates that points_scored is within game limits, which could cause errors if not handled properly
3. **Error handling**: Insufficient error details made debugging difficult

## Fixes Applied

### 1. Serializer Save Method (`users/serializers.py`)
- Fixed the `save()` method to properly handle admin_user and verified_by_admin
- Now calls parent save first, then sets admin fields, then saves again with update_fields
- This ensures all fields are properly saved in the correct order

### 2. View Error Handling (`users/views.py`)
- Added pre-validation check for score limits before attempting to save
- Returns proper 400 error if score is outside game limits (instead of 500)
- Added detailed error messages including min/max points and provided score
- Improved exception handling with traceback logging
- Refreshes serializer data after save to ensure all fields are included in response

### 3. Data Mapping
- Ensured `score` field is properly mapped to `points_scored` in `to_internal_value()`
- Added type checking to prevent errors with non-dict data

## Testing

1. **Try updating a score** in the admin dashboard
2. **Check server logs** for detailed error messages if it still fails
3. **Verify the score is within game limits** - if the game has min_points=0 and max_points=100, make sure your score is between those values

## Common Issues

### Score Outside Game Limits
If you get a 400 error with message about score limits:
- Check the game's min_points and max_points
- Ensure your score is within those bounds
- The error response will include the allowed range

### Still Getting 500 Error
If you still get a 500 error:
1. Check the server logs for the full traceback
2. The error response should now include a `detail` field with the error message
3. In DEBUG mode, it will also include the full traceback

## Next Steps

After this fix:
- Score updates should work properly
- You'll get clear error messages if validation fails
- Admin fields (admin_user, verified_by_admin) will be properly set

