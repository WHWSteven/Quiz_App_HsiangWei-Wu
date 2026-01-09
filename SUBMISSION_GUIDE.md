# How to Submit Your Assignment

## Step 1: Prepare Your Files

Your project should include:
- All source code files (Python, JavaScript, HTML, CSS)
- `requirements.txt` files for Python dependencies
- `package.json` for Node.js dependencies
- Configuration files (if required)
- Database migration scripts (if any)

## Step 2: Remove Unnecessary Files

Before submitting, make sure to:
- ✅ Delete all `.md` documentation files (already done)
- ✅ Remove debug print statements (already done)
- ✅ Remove test files if not required (`test_saga.py`, `test_compensation.py`)
- ✅ Remove `__pycache__` folders (they will be regenerated)
- ✅ Remove `node_modules` folder (can be reinstalled with `npm install`)
- ✅ Remove `venv` folders (virtual environments should not be submitted)
- ✅ Remove database files (`.db` files) - they will be created on first run

## Step 3: Create a README.md (Optional but Recommended)

Create a simple README.md with:
- Project title
- Brief description
- How to run the project
- Required dependencies
- Port numbers used

Example:
```markdown
# Quiz App with Saga Pattern

A quiz application implementing the Saga Design Pattern for distributed transactions.

## Setup

1. Install Python dependencies: `pip install -r requirements.txt`
2. Install Node.js dependencies: `cd gateway && npm install`
3. Start Redis: `redis-server.exe redis-dev.conf`
4. Start services: See start_services_windows.ps1

## Services

- Gateway: http://localhost:8080
- Quiz Service: http://localhost:5000
- User Service: http://localhost:5001
- Saga Orchestrator: http://localhost:5002
```

## Step 4: Submission Methods

### Option A: ZIP File (Most Common)

1. **Select files to include:**
   - All source code
   - Configuration files
   - `requirements.txt` files
   - `package.json` files
   - README.md (if created)
   - Scripts (like `start_services_windows.ps1`)

2. **Exclude:**
   - `__pycache__` folders
   - `node_modules` folder
   - `venv` folders
   - `.db` database files
   - `.md` documentation files (except README.md)

3. **Create ZIP:**
   - Right-click on project folder
   - Select "Send to" → "Compressed (zipped) folder"
   - Or use: `Compress-Archive -Path "Quiz_App_HsiangWei Wu" -DestinationPath "Quiz_App_Submission.zip"`

4. **Submit:**
   - Upload to your course platform (Blackboard, Canvas, etc.)
   - Or email to your instructor

### Option B: Git Repository (If Required)

1. **Initialize Git (if not already):**
   ```bash
   git init
   git add .
   git commit -m "Initial submission"
   ```

2. **Create .gitignore:**
   ```
   __pycache__/
   *.pyc
   venv/
   node_modules/
   *.db
   instance/
   .env
   ```

3. **Push to GitHub/GitLab:**
   ```bash
   git remote add origin <repository-url>
   git push -u origin main
   ```

4. **Share repository link** with your instructor

### Option C: Cloud Storage (Google Drive, OneDrive, etc.)

1. Upload your project folder to cloud storage
2. Share the link with your instructor
3. Make sure sharing permissions allow viewing/downloading

## Step 5: Verify Before Submission

Before submitting, verify:
- ✅ All code files are present
- ✅ No debug print statements (already cleaned)
- ✅ No unnecessary documentation files (already deleted)
- ✅ Project can run (test locally first)
- ✅ All dependencies are listed in requirements.txt
- ✅ README.md explains how to run (if created)

## Step 6: Submission Checklist

- [ ] All source code files included
- [ ] requirements.txt files present
- [ ] package.json present (for Gateway)
- [ ] README.md created (optional but recommended)
- [ ] Unnecessary files removed (__pycache__, node_modules, venv, .db files)
- [ ] ZIP file created (if using Option A)
- [ ] File size is reasonable (< 50MB typically)
- [ ] Tested that project runs locally

## Common Submission Platforms

### Blackboard
1. Go to your course
2. Find "Assignments" section
3. Click on the assignment
4. Click "Browse My Computer" or "Attach File"
5. Select your ZIP file
6. Click "Submit"

### Canvas
1. Go to your course
2. Find "Assignments" in sidebar
3. Click on the assignment
4. Click "Submit Assignment"
5. Choose "File Upload"
6. Select your ZIP file
7. Click "Submit Assignment"

### Email Submission
1. Compose email to instructor
2. Attach ZIP file
3. Include:
   - Your name
   - Course name/number
   - Assignment name
   - Brief description
4. Send email

## Tips

1. **File Naming:** Use clear names like `Quiz_App_YourName_Assignment1.zip`
2. **File Size:** If ZIP is too large, exclude more files (node_modules, venv)
3. **Test First:** Always test your submission locally before submitting
4. **Backup:** Keep a backup copy of your submission
5. **Deadline:** Submit before the deadline to avoid late penalties

## Need Help?

If you encounter issues:
1. Check your course's submission guidelines
2. Contact your instructor
3. Verify file size limits
4. Test your ZIP file by extracting it

Good luck with your submission! 🎓
