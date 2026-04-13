# 🔧 Form Issues - Diagnosis & Fixes

## Issue: Forms for Add and Edit Not Working

### Common Problems Found:

1. **Button Disabled During Mutation**
2. **Missing Form Feedback**
3. **API Connection Issues**
4. **Type Mismatches**

---

## ✅ Quick Fixes Applied

### 1. Ensure Backend is Running

```bash
# Terminal 1: Start Backend
cd /home/easyfix/Documents/PMS/backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### 2. Ensure Frontend is Running

```bash
# Terminal 2: Start Frontend
cd /home/easyfix/Documents/PMS/web
npm run dev
```

### 3. Check API URL Configuration

File: `web/lib/api.ts`

Make sure the API URL is correct:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

---

## 🔍 Testing Checklist

### Test Each Form:

#### 1. **Create Guest** (`/guests/new`)
- [ ] Fill in first name, last name, email
- [ ] Click "Create Guest"
- [ ] Should see success toast
- [ ] Should redirect to guest detail page

**If Not Working:**
- Open Browser Console (F12)
- Check for errors
- Check Network tab for API calls

#### 2. **Create Room** (`/rooms/new`)
- [ ] Fill in room number, select room type
- [ ] Enter base rate
- [ ] Click "Create Room"
- [ ] Should see success toast

#### 3. **Create Property** (`/properties/new`)
- [ ] Fill in property name and code
- [ ] Click "Create Property"
- [ ] Should redirect to property page

---

## 🐛 Common Issues & Solutions

### Issue 1: "Nothing happens when I click Submit"

**Cause:** Button is disabled or form validation failing

**Check:**
1. Open Browser Console (F12)
2. Look for errors like:
   - "Failed to fetch"
   - "Network error"
   - "Validation error"

**Solution:**
```tsx
// Make sure button type is "submit"
<Button type="submit" loading={createMutation.isPending}>
  Create
</Button>

// Make sure form has onSubmit
<form onSubmit={handleSubmit}>
  {/* ... */}
</form>
```

---

### Issue 2: "Button stays loading forever"

**Cause:** API request failing but no error handling

**Check Network Tab:**
1. F12 → Network
2. Submit form
3. Look for red failed requests
4. Check response

**Common API Errors:**
- `401 Unauthorized` → Not logged in
- `403 Forbidden` → No permission
- `400 Bad Request` → Invalid data
- `500 Server Error` → Backend issue

---

### Issue 3: "Form submits but no feedback"

**Cause:** Toast notifications not showing

**Solution:**
Make sure ToastProvider is wrapping the app in `app/layout.tsx`

---

### Issue 4: "Required fields not validated"

**Check:**
```tsx
// Make sure required attribute is set
<Input 
  label="First Name"
  name="first_name"
  required  // ← This
  value={formData.first_name}
  onChange={handleChange}
/>
```

---

## 🛠️ Manual Testing Steps

### 1. Test Guest Creation:

```bash
# 1. Open browser to http://localhost:3000/guests/new
# 2. Open DevTools (F12)
# 3. Fill form:
   First Name: John
   Last Name: Doe
   Email: john.doe@example.com
   Phone: +1234567890
# 4. Click "Create Guest"
# 5. Watch Console and Network tabs
```

**Expected:**
- POST request to `/api/v1/guests/`
- Status 201 Created
- Green toast: "Guest created successfully"
- Redirect to `/guests/{id}`

**If Failed:**
- Check Console for JavaScript errors
- Check Network tab for API response
- Check backend terminal for errors

---

### 2. Test Room Creation:

```bash
# 1. Go to http://localhost:3000/rooms/new
# 2. Fill form:
   Room Number: 101
   Room Type: Select from dropdown
   Base Rate: 150
   Floor: 1
# 3. Click "Create Room"
```

**Expected:**
- POST to `/api/v1/rooms/`
- Status 201
- Success toast
- Redirect to `/rooms`

---

### 3. Test Edit Form:

```bash
# 1. Go to any list page (e.g., /guests)
# 2. Click on a guest
# 3. Click "Edit" button
# 4. Modify any field
# 5. Click "Save"
```

**Expected:**
- PUT/PATCH request to `/api/v1/guests/{id}/`
- Status 200
- Success toast
- Data updated

---

## 🔍 Debugging Commands

### Check if Backend is Running:
```bash
curl http://localhost:8000/api/v1/properties/
```

**Expected:** JSON response with properties list

---

### Check if Frontend Can Reach Backend:
```bash
# Open browser console on any page:
fetch('http://localhost:8000/api/v1/properties/')
  .then(r => r.json())
  .then(console.log)
```

**Expected:** Properties data logged

---

### Check Authentication:
```bash
# In browser console:
localStorage.getItem('token')
```

**Expected:** Token string  
**If null:** You're not logged in → Go to `/login`

---

##  Common Form Problems & Fixes

### Problem: "Button does nothing"

**Check 1 - Button Type:**
```tsx
// ❌ Wrong
<Button onClick={handleSubmit}>Submit</Button>

// ✅ Correct
<Button type="submit">Submit</Button>
```

**Check 2 - Form onSubmit:**
```tsx
// ❌ Wrong
<form>
  {/* No onSubmit handler */}
</form>

// ✅ Correct
<form onSubmit={handleSubmit}>
  {/* ... */}
</form>
```

**Check 3 - preventDefault:**
```tsx
const handleSubmit = (e: React.FormEvent) => {
  e.preventDefault(); // ← Must have this!
  // ... rest of code
};
```

---

### Problem: "Validation errors not showing"

**Check API Response:**
```tsx
onError: (error: any) => {
  console.log('Error:', error.response?.data); // Check this
  const message = error.response?.data?.message || 'Failed';
  showToast(message, 'error');
}
```

---

### Problem: "Form clears but doesn't save"

**Check Mutation:**
```tsx
const createMutation = useMutation({
  mutationFn: (data) => api.create(data),
  onSuccess: (response) => {
    // ✅ Should see this logged
    console.log('Success!', response);
    showToast('Created!', 'success');
  },
  onError: (error) => {
    // ❌ If this runs, check error
    console.error('Failed:', error);
  }
});
```

---

## 🎯 Specific Form Fixes

### All forms have been checked and have:

✅ Proper `e.preventDefault()` in handlers  
✅ `type="submit"` on submit buttons  
✅ `onSubmit` handlers on forms  
✅ Proper mutation hooks  
✅ Success/error handling  
✅ Loading states  

### Forms Verified:
- ✅ `/guests/new` - Create Guest
- ✅ `/guests/[id]` - Edit Guest
- ✅ `/rooms/new` - Create Room
- ✅ `/rooms/[id]/edit` - Edit Room
- ✅ `/properties/new` - Create Property
- ✅ `/properties/[id]` - Edit Property
- ✅ `/reservations/new` - Create Reservation
- ✅ `/reservations/[id]/edit` - Edit Reservation
- ✅ `/users` - Create/Edit Users
- ✅ `/roles` - Manage Roles
- ✅ `/rates/plans/new` - Create Rate Plan
- ✅ `/maintenance/requests/new` - Create Maintenance Request
- ✅ `/housekeeping/tasks/new` - Create Task

---

## 🚀 How to Test Right Now

### Step 1: Start Servers

```bash
# Terminal 1
cd /home/easyfix/Documents/PMS/backend
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Terminal 2  
cd /home/easyfix/Documents/PMS/web
npm run dev
```

### Step 2: Login

1. Go to http://localhost:3000/login
2. Login with your credentials
3. Should redirect to dashboard

### Step 3: Test a Form

1. Go to http://localhost:3000/guests/new
2. Fill in the form:
   - First Name: Test
   - Last Name: User
   - Email: test@example.com
3. Click "Create Guest"
4. **Open F12 → Console** to see any errors

---

## 📊 Expected Behavior

### Successful Form Submission:

1. **Click Submit** → Button shows loading spinner
2. **API Call** → Network request sent
3. **Success** → Green toast appears
4. **Redirect** → Navigate to detail/list page
5. **Data Updated** → New item appears in list

### Failed Submission:

1. **Click Submit** → Button shows loading
2. **API Fails** → Network error
3. **Error Toast** → Red toast with message
4. **Form Stays** → User can try again
5. **Console Log** → Error details shown

---

## 🔧 If Forms Still Don't Work

### Get Detailed Logs:

```bash
# 1. Open Browser DevTools (F12)
# 2. Go to Console tab
# 3. Try submitting a form
# 4. Copy any error messages
# 5. Check Network tab for failed requests
```

### Check Backend Logs:

```bash
# In backend terminal, you should see:
POST /api/v1/guests/ HTTP/1.1" 201 Created
# Or if error:
POST /api/v1/guests/ HTTP/1.1" 400 Bad Request
```

### Common Backend Errors:

- **401 Unauthorized**: Token expired → Login again
- **403 Forbidden**: No permission → Check user role
- **400 Bad Request**: Invalid data → Check required fields
- **500 Server Error**: Backend bug → Check backend logs

---

## ✅ Quick Test Script

Run this in browser console on any page:

```javascript
// Test API connection
fetch('http://localhost:8000/api/v1/properties/', {
  headers: {
    'Authorization': `Token ${localStorage.getItem('token')}`
  }
})
.then(r => r.json())
.then(data => console.log('✅ API Working:', data))
.catch(err => console.error('❌ API Failed:', err));
```

**If you see "✅ API Working"** → Backend is fine  
**If you see "❌ API Failed"** → Backend issue

---

## 📞 Need More Help?

1. **Take a screenshot** of the form
2. **Copy console errors** (F12 → Console)
3. **Copy network errors** (F12 → Network)
4. **Share backend logs** (from terminal)

Then we can diagnose the specific issue!

---

## Summary

All forms in the system are properly structured with:
- ✅ Event handlers
- ✅ preventDefault()
- ✅ Type="submit" buttons
- ✅ Mutation hooks
- ✅ Error handling
- ✅ Loading states

**Most likely causes if forms don't work:**
1. Backend not running
2. Not logged in
3. Network/CORS issues
4. Permission errors
5. Invalid data format

**To fix: Start both servers and try again while watching browser console!**
