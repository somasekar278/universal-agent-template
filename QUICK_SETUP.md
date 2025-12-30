# Quick Setup - Make Template Generator Work Seamlessly

## 🎯 The Goal

Make it so when you run:
```bash
python template_generator.py --domain "anything"
```

The generated project **works immediately** with zero additional setup.

## ✅ One-Time Setup (Run These Commands)

### Easiest Way: Run Setup Script

```bash
cd "/Users/som.natarajan/SOTA Agent Framework"

# Mac/Linux
./setup.sh

# Windows
setup.bat
```

### Manual Setup (Alternative)

If the script doesn't work:

```bash
cd "/Users/som.natarajan/SOTA Agent Framework"

# Step 1: Install dependencies
pip install -r requirements.txt

# Step 2: Install framework
pip install -e .
```

**If you get permission errors, try:**
```bash
pip install --user -e .
```

**Or use a virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Mac/Linux
./setup.sh  # Run the script, or install manually
```

## 🚀 Now Generate Projects Seamlessly

After the one-time setup above, this works perfectly:

```bash
# Generate project
python template_generator.py --domain "trip_planner" --output ./trip_planner

# Navigate
cd trip_planner

# Run immediately - NO ADDITIONAL SETUP NEEDED!
python examples/example_usage.py
```

✅ **Works immediately!**
✅ **No import errors!**
✅ **Completely seamless!**

## 📦 Generated Projects Are Promotion-Ready

Each generated project now includes:
- ✅ `.gitignore` - Excludes framework clutter
- ✅ `README.md` - Complete documentation
- ✅ `requirements.txt` - All dependencies
- ✅ Tests - Ready to run
- ✅ Examples - Working code

**Push to its own repo:**
```bash
cd trip_planner
git init
git add .
git commit -m "Initial commit: Trip planner agent"
git remote add origin https://github.com/you/trip-planner.git
git push -u origin main
```

**No framework baggage included!** 🎉

## 🧪 Test It Works

```bash
cd "/Users/som.natarajan/SOTA Agent Framework"

# Generate a test project
python template_generator.py --domain "test" --output ./test_project

# Test it immediately
cd test_project
python examples/example_usage.py

# Should output:
# ✅ Agents loaded from config!
# 🤖 Executing agent...
# ✅ Agent completed!
```

## 📝 What Changed

### Before (Broken):
```bash
python template_generator.py --domain "x"
cd x
python examples/example_usage.py
# ❌ ModuleNotFoundError: No module named 'agents'
```

### After (Fixed):
```bash
# One-time setup
pip install -r requirements.txt && pip install -e .

# Then forever after:
python template_generator.py --domain "x"
cd x
python examples/example_usage.py
# ✅ Works perfectly!
```

## 🎯 For Users Cloning Your Repo

When someone clones `universal-agent-template`:

```bash
git clone https://github.com/somasekar278/universal-agent-template.git
cd universal-agent-template

# One-time setup
pip install -r requirements.txt
pip install -e .

# Generate their projects
python template_generator.py --domain "their_app"
cd their_app
python examples/example_usage.py  # Works!
```

## ✨ Benefits

1. **Seamless** - No manual imports, path hacks, or configuration
2. **Professional** - Generated projects are production-ready
3. **Promotable** - Each project can be its own repo
4. **Clean** - `.gitignore` excludes framework clutter
5. **Fast** - Generate and run in 30 seconds

## 🚨 Troubleshooting

### "No module named 'agents'"
→ Run: `pip install -e .` in framework directory

### "No module named 'pydantic'"  
→ Run: `pip install -r requirements.txt`

### Permission errors with pip
→ Use: `pip install --user -e .`
→ Or use a virtual environment

## 📊 Summary

**One-Time (30 seconds):**
```bash
cd "/Users/som.natarajan/SOTA Agent Framework"
pip install -r requirements.txt
pip install -e .
```

**Every Time (works seamlessly):**
```bash
python template_generator.py --domain "anything"
cd anything
python examples/example_usage.py  # Just works! ✅
```

---

**Ready?** Run the one-time setup commands above, then generate your trip_planner! 🚀

