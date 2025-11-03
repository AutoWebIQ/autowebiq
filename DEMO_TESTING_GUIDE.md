# Demo Account Testing Guide for AutoWebIQ

## Quick Access

**🌐 Application URL:** https://cdcd89af-3ae1-42bc-a5dd-bc0f091e8023.e1-us-east-azure.vercel-ai-testing.com

**📧 Demo Account (PostgreSQL):**
- Email: `demo@autowebiq.com`
- User ID: `5bb79c11-43aa-4c8b-bad7-348482c8b830`
- Credits: 1000
- Status: ✅ Created in PostgreSQL

---

## Testing Options

### Option 1: Sign Up with Firebase (Recommended)

**Steps:**
1. Go to: https://cdcd89af-3ae1-42bc-a5dd-bc0f091e8023.e1-us-east-azure.vercel-ai-testing.com
2. Click "Sign In" or "Get Started"
3. Choose "Sign in with Google" (Firebase OAuth)
4. Use any Google account
5. You'll be automatically logged in with starter credits

**Benefits:**
- Real authentication flow
- Fresh account
- All features available
- Starter credits provided

---

### Option 2: Use Demo Account (Backend Testing)

Since Firebase handles authentication in the frontend, you can test backend APIs directly:

**API Testing with Demo Account:**

```bash
# Get demo user info (replace with actual JWT token after login)
curl -X GET "https://autowebiq-1.preview.emergentagent.com/api/v2/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Check validation system
curl -X GET "https://autowebiq-1.preview.emergentagent.com/api/v2/validate/checks"

# Check health
curl -X GET "https://autowebiq-1.preview.emergentagent.com/api/health"
```

---

## Testing Workflow - Step by Step

### 1. **Landing Page Test**
```
✅ Check if landing page loads
✅ Check if "Get Started" button appears
✅ Check if navigation works
```

### 2. **Authentication Test**
```
✅ Click "Sign In"
✅ Sign in with Google (Firebase OAuth)
✅ Verify redirect to dashboard
✅ Check if user profile appears (top right)
```

### 3. **Dashboard Test**
```
✅ Check if dashboard loads
✅ Verify credits display
✅ Check "Create New Project" button
✅ View existing projects (if any)
```

### 4. **Create Project Test**
```
✅ Click "Create New Project"
✅ Enter project name: "My Coffee Shop"
✅ Enter description: "A modern coffee shop website"
✅ Click "Create" button
✅ Verify redirect to workspace
```

### 5. **Build Website Test**
```
✅ In workspace, enter prompt: "Create a beautiful coffee shop landing page with menu and contact form"
✅ Click "Send" or press Enter
✅ Watch for:
   - Loading indicator
   - AI response in chat
   - WebSocket real-time updates
   - Preview appears on right side
✅ Verify website renders in preview
```

### 6. **Validation Test** (NEW FEATURE!)
```
✅ After website is built, click "Validate" button (blue button in preview header)
✅ Wait for validation to complete (~3-5 seconds)
✅ Check validation modal appears with:
   - Overall score (0-100)
   - Status (EXCELLENT/GOOD/NEEDS IMPROVEMENT/POOR)
   - 9 individual checks with scores
   - Issues list for each check
   - Recommendations
✅ Click on each check to see details
✅ Click "Re-validate" to test again
✅ Click "Close" to dismiss modal
```

### 7. **Deploy to Vercel Test** (NEW FEATURE!)
```
✅ After website is built, click "Deploy to Vercel" button (purple button)
✅ Watch for:
   - "Deploying to Vercel..." toast
   - Progress indicator
   - Success message with URL
✅ Click "View Live" button (green)
✅ Verify website opens in new tab at Vercel URL
✅ Test the live website
```

### 8. **Credits Test**
```
✅ Check credits in dashboard
✅ Verify credits deducted after build
✅ Go to Credits page
✅ Check credit history/transactions
```

---

## Features to Test

### Core Features:
- ✅ Firebase Google OAuth login
- ✅ Dashboard with project list
- ✅ Create new project
- ✅ AI website generation
- ✅ Live preview in workspace
- ✅ Split-screen chat + preview
- ✅ Credit system

### New Features (Just Implemented):
- 🆕 **9-Point Validation**
  - Click "Validate" button
  - See comprehensive validation results
  - Review recommendations

- 🆕 **Vercel Deployment**
  - Click "Deploy to Vercel" button
  - Get live URL
  - Access deployed website

### Advanced Features:
- WebSocket real-time updates
- Multiple AI models (Claude, GPT, Gemini)
- Template selection
- Project history
- Credit transactions

---

## Sample Prompts to Test

### For Building Websites:
1. "Create a landing page for a tech startup with hero section, features, and pricing"
2. "Build a portfolio website for a photographer with gallery"
3. "Make a restaurant website with menu and reservation form"
4. "Create a SaaS product landing page with modern design"
5. "Build a blog homepage with recent posts grid"

### For Testing Validation:
- Try prompts that generate different quality levels
- Intentionally create pages with issues (missing alt text, no meta description)
- Build minimal vs comprehensive pages

---

## Expected Results

### Validation Scores:

**Excellent (90-100):**
- All HTML5 tags proper
- Complete meta tags
- Responsive design
- Accessible
- SEO optimized

**Good (75-89):**
- Minor issues (missing vendor prefixes, some optimization)
- Most checks passing
- Production-ready with minor tweaks

**Needs Improvement (60-74):**
- Several issues to fix
- Some checks failing
- Needs optimization

**Poor (0-59):**
- Major problems
- Multiple failed checks
- Significant fixes needed

### Deployment:
- Typical deploy time: 20-60 seconds
- URL format: `https://autowebiq-xxx.vercel.app`
- Live website accessible globally

---

## Troubleshooting

### Issue: Can't log in
**Solution:**
- Clear browser cache
- Try incognito mode
- Check if Firebase is blocked by firewall
- Use different Google account

### Issue: Build not working
**Solution:**
- Check credits balance
- Verify WebSocket connection (status indicator in workspace)
- Check console for errors (F12)
- Try a simpler prompt

### Issue: Validation not showing results
**Solution:**
- Build website first
- Check if project has generated code
- Verify backend health: curl https://autowebiq-1.preview.emergentagent.com/api/health
- Check browser console for errors

### Issue: Deploy button disabled
**Solution:**
- Build website first
- Ensure website rendered in preview
- Check if project has generated code
- Verify Vercel token configured

---

## Quick Test Commands

### Check Backend Health:
```bash
curl -s https://autowebiq-1.preview.emergentagent.com/api/health | python -m json.tool
```

### Check Validation System:
```bash
curl -s https://autowebiq-1.preview.emergentagent.com/api/v2/validate/checks | python -m json.tool
```

### Check Database Services:
```bash
/app/start_db_services.sh
```

---

## What to Look For

### ✅ Success Indicators:
- Green status indicators
- Smooth transitions
- Fast response times
- Clear error messages (if any)
- Professional UI/UX
- Responsive design
- Working buttons
- Real-time updates

### ❌ Issues to Report:
- Errors in console
- Broken layouts
- Slow loading (>5s)
- Failed API calls
- Non-responsive buttons
- Missing features
- Incorrect data

---

## Testing Checklist

```
[ ] Landing page loads
[ ] Sign in with Google works
[ ] Dashboard displays correctly
[ ] Can create new project
[ ] Workspace opens
[ ] Can send chat messages
[ ] AI responds with website
[ ] Preview shows website
[ ] Validate button works
[ ] Validation modal displays results
[ ] All 9 checks show scores
[ ] Deploy button works
[ ] Deployment completes successfully
[ ] Live URL accessible
[ ] Website works on deployed URL
[ ] Credits deducted correctly
[ ] Can navigate between pages
[ ] Can logout
[ ] Can login again
```

---

## Support & Feedback

### If You Find Issues:
1. Take screenshot
2. Note the steps to reproduce
3. Check browser console (F12) for errors
4. Note any error messages
5. Report with details

### Performance Benchmarks:
- Landing page load: < 2s
- Login: < 3s
- Website build: 10-30s (depends on complexity)
- Validation: 3-5s
- Deployment: 20-60s
- Page navigation: < 1s

---

## Demo Account Details (Backend)

**PostgreSQL:**
```
User ID: 5bb79c11-43aa-4c8b-bad7-348482c8b830
Email: demo@autowebiq.com
Name: Demo User
Credits: 1000
Created: October 31, 2025
```

**Note:** This is a backend user for API testing. For full UI testing, use Firebase Google OAuth (Option 1 above).

---

## Next Steps After Testing

1. Test all features systematically
2. Try different types of websites
3. Test validation on various quality levels
4. Deploy multiple websites
5. Check credit transactions
6. Test responsive design (mobile view)
7. Try different browsers
8. Report any issues found

---

**Happy Testing! 🚀**

If you encounter any issues or need assistance, let me know!
