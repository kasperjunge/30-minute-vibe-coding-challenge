# Test Plugins for Claude Plugin Marketplace

This directory contains two test plugins you can use to test your marketplace.

## 📦 Available Test Plugins

### 1. Simple Hello Plugin (`simple-hello-plugin.zip`)

**Size**: ~1.8 KB  
**Version**: 1.0.0  
**Components**: 1 command

A minimal "Hello World" plugin perfect for basic testing.

**Features:**
- `/greet` command that says hello to users
- Clean, simple structure
- Good for testing basic upload flow

**Plugin Structure:**
```
simple-hello-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── greet.md
└── README.md
```

---

### 2. Dev Tools Plugin (`dev-tools-plugin.zip`)

**Size**: ~7.3 KB  
**Version**: 2.1.0  
**Components**: 2 commands, 1 agent, 1 skill

A comprehensive plugin showcasing multiple component types.

**Features:**
- `/review` - Code review command
- `/gendocs` - Documentation generation command
- Test Specialist agent for testing workflows
- Code Reviewer skill for automated analysis
- Rich README with extensive documentation

**Plugin Structure:**
```
dev-tools-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── review.md
│   └── gendocs.md
├── agents/
│   └── test-specialist.md
├── skills/
│   └── code-reviewer/
│       └── SKILL.md
└── README.md
```

---

## 🧪 Testing Your Marketplace

### Step 1: Register an Account
1. Go to `/auth/register`
2. Create a test account
3. Log in

### Step 2: Upload Simple Plugin
1. Navigate to `/plugins/upload`
2. Upload `simple-hello-plugin.zip`
3. Verify:
   - ✅ Upload succeeds
   - ✅ Plugin appears on homepage
   - ✅ Plugin detail page shows correctly
   - ✅ README renders as markdown
   - ✅ Components section shows: 1 command

### Step 3: Upload Complex Plugin
1. Navigate to `/plugins/upload` again
2. Upload `dev-tools-plugin.zip`
3. Verify:
   - ✅ Upload succeeds
   - ✅ Plugin appears on homepage
   - ✅ Plugin detail page displays all info
   - ✅ README renders with formatting (headings, code blocks, lists)
   - ✅ Components section shows: 2 commands, 1 agent, 1 skill
   - ✅ Version history section appears

### Step 4: Test Search and Filtering
1. Go to homepage `/`
2. Search for "hello" - should find simple-hello plugin
3. Search for "development" - should find dev-tools plugin
4. Search for "testing" - should find dev-tools plugin
5. Try sorting by alphabetical
6. Try sorting by newest

### Step 5: Test My Plugins Page
1. Go to `/plugins/my-plugins`
2. Verify both plugins appear
3. Check that status shows "Published"
4. Verify latest version numbers display

### Step 6: Test User Profile
1. Go to `/users/@your-username`
2. Verify both plugins appear on your profile
3. Click through to plugin detail pages

### Step 7: Upload New Version (Version Management)
1. Edit `dev-tools-plugin/.claude-plugin/plugin.json`
2. Change version to `"2.2.0"`
3. Re-zip: `zip -r dev-tools-plugin-v2.zip dev-tools-plugin`
4. Upload the new version
5. Verify:
   - ✅ Version updates to 2.2.0
   - ✅ Version history shows both versions
   - ✅ Latest badge moves to new version

---

## ✅ Validation Checklist

### Upload Validation
- [ ] Valid plugins upload successfully
- [ ] Plugin without `.claude-plugin/plugin.json` is rejected
- [ ] Plugin with invalid JSON is rejected
- [ ] Duplicate plugin names (same author) are rejected
- [ ] Validation errors show clear messages

### Display & Navigation
- [ ] Plugins appear on homepage
- [ ] Search finds plugins by name and description
- [ ] Sorting (newest/alphabetical) works
- [ ] Pagination works for multiple plugins
- [ ] Plugin detail pages load correctly
- [ ] README markdown renders properly
- [ ] Component counts display accurately
- [ ] Version history shows all versions

### User Experience
- [ ] Navigation menu shows correct options when logged in
- [ ] My Plugins page lists user's plugins
- [ ] User profiles show their plugins
- [ ] Empty states display appropriately
- [ ] Error messages are helpful

### Data Integrity
- [ ] Files stored in correct directory structure
- [ ] Metadata extracted correctly from plugin.json
- [ ] README content extracted and stored
- [ ] Version management prevents downgrades
- [ ] is_latest flag managed correctly

---

## 🐛 Common Issues to Test

1. **Large Files**: Both plugins are small - consider testing with larger README files
2. **Special Characters**: Plugin names and descriptions with special chars
3. **Missing README**: Plugin without README.md (should handle gracefully)
4. **Empty Components**: Plugin with no commands/agents/skills (should show appropriate message)
5. **Concurrent Uploads**: Multiple users uploading simultaneously
6. **Same Plugin Name**: Different users with same plugin name (should be allowed)

---

## 📊 Expected Component Counts

### Simple Hello Plugin
- Commands: 1
- Agents: 0
- Skills: 0
- Hooks: 0
- MCP Servers: 0

### Dev Tools Plugin
- Commands: 2
- Agents: 1
- Skills: 1
- Hooks: 0
- MCP Servers: 0

---

## 🔄 Testing Version Updates

To test version management:

1. Upload `dev-tools-plugin.zip` (v2.1.0)
2. Modify version in plugin.json to 2.2.0
3. Re-zip and upload
4. Verify new version becomes latest
5. Try uploading v2.0.0 (should fail - downgrade prevention)

---

## 📝 Notes

- Both plugins follow the official Claude Code plugin structure
- All required fields in plugin.json are present
- README files include markdown formatting (headings, code blocks, lists)
- Component files follow the documented format
- Plugins are valid and would work in actual Claude Code

---

## 🎯 Success Criteria

Your marketplace is working correctly if:
- ✅ Both plugins upload without errors
- ✅ All plugin information displays accurately
- ✅ Search and filtering work as expected
- ✅ README markdown renders properly
- ✅ Component counts are accurate
- ✅ Version management works correctly
- ✅ User workflows are smooth and intuitive

