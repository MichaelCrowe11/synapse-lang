# Tutorial Script: Installation and Setup

**Episode 2 of Synapse Fundamentals Series**  
**Duration:** 10 minutes  
**Difficulty:** Beginner  

## 📝 Script

### HOOK (0:00 - 0:20)

[Screen shows terminal with installation in progress]

**Presenter:** "Ready to join the quantum computing revolution? In just 10 minutes, you'll have Synapse Language running on your machine and be ready to write your first quantum-enhanced program."

[Quick montage of successful installations on different operating systems]

### INTRODUCTION (0:20 - 1:00)

**Presenter:** "Welcome back to Synapse Fundamentals! I'm Michael Crowe, and today we're getting you set up with everything you need to start programming in Synapse.

By the end of this episode, you'll have:
• Synapse Language installed and working
• The VS Code extension configured
• A working development environment
• Your first program running successfully

Let's dive in!"

### MAIN CONTENT (1:00 - 8:30)

#### Section 1: System Requirements (1:00 - 1:30)

[Screen shows requirements checklist]

**Presenter:** "First, let's make sure your system is ready. Synapse works on:"

**On Screen:**
- ✅ **Windows 10/11** (x64)
- ✅ **macOS 10.15+** (Intel or Apple Silicon)  
- ✅ **Linux** (Ubuntu 18.04+, CentOS 7+, or equivalent)
- ✅ **Python 3.8+** (we'll check this together)
- ✅ **4GB RAM minimum** (8GB+ recommended for quantum simulations)

**Presenter:** "Don't worry if you're not sure about your Python version - I'll show you how to check."

#### Section 2: Python Installation Check (1:30 - 3:00)

[Screen shows terminal/command prompt]

**Presenter:** "Let's start by checking if you have Python installed. Open your terminal - that's Command Prompt on Windows, Terminal on Mac and Linux."

**On Screen Commands:**
```bash
python --version
# or try:
python3 --version
```

[Show example outputs for different scenarios]

**If Python 3.8+ is installed:**
```
Python 3.9.7
```

**If Python is not installed or too old:**
```
'python' is not recognized as an internal or external command
# or
Python 2.7.16
```

**Presenter:** "If you don't have Python 3.8+, don't worry! Head to python.org and download the latest version. I recommend Python 3.9 or 3.10 for the best Synapse experience."

[Screen shows python.org download page briefly]

**Important for Windows users:**
**Presenter:** "Windows users, make sure to check 'Add Python to PATH' during installation - this is crucial!"

#### Section 3: Installing Synapse Language (3:00 - 4:30)

[Screen returns to terminal]

**Presenter:** "Now for the exciting part - installing Synapse! It's as simple as one command:"

```bash
pip install synapse-lang
```

[Show real installation progress]

**Presenter:** "This downloads Synapse and all its dependencies. You'll see packages like NumPy, SciPy, and SymPy being installed - these power Synapse's scientific computing capabilities."

**If installation issues occur:**

```bash
# If you get permission errors on Mac/Linux:
pip install --user synapse-lang

# If pip isn't found:
python -m pip install synapse-lang

# For Python 3 specifically:
pip3 install synapse-lang
```

**Presenter:** "The installation typically takes 2-3 minutes depending on your internet connection."

#### Section 4: Verification (4:30 - 5:30)

[Screen shows verification commands]

**Presenter:** "Let's verify everything installed correctly:"

```bash
python -c "import synapse_lang; print('Synapse version:', synapse_lang.__version__)"
```

[Show successful output]
```
Synapse version: 2.0.0
```

**Presenter:** "Perfect! Now let's test the core features:"

```bash
python -c "
import synapse_lang
print('✓ Core language loaded')
print('✓ Tensor engine available:', synapse_lang.TENSOR_AVAILABLE)  
print('✓ Uncertainty engine available:', synapse_lang.UNCERTAINTY_AVAILABLE)
print('✓ Symbolic engine available:', synapse_lang.SYMBOLIC_AVAILABLE)
"
```

**Presenter:** "If you see checkmarks, congratulations - Synapse is ready to go!"

#### Section 5: VS Code Extension (5:30 - 7:00)

[Screen shows VS Code installation]

**Presenter:** "While you can write Synapse in any text editor, I highly recommend the VS Code extension for the best experience."

**Steps shown on screen:**

1. **Install VS Code** (if not already installed)
   - Visit code.visualstudio.com
   - Download for your operating system

2. **Install Synapse Extension**
   - Open VS Code
   - Click Extensions (Ctrl+Shift+X)
   - Search "Synapse Language"
   - Click Install

[Show extension features]

**Presenter:** "The extension gives you:"
- **Syntax highlighting** - Beautiful code colors
- **IntelliSense** - Auto-completion for keywords and functions
- **Code snippets** - Quick templates for common patterns
- **Error detection** - Catch issues before running
- **Integrated terminal** - Run Synapse directly in VS Code

#### Section 6: First Program Test (7:00 - 8:30)

[Screen shows VS Code with new file]

**Presenter:** "Let's create your first Synapse program to make sure everything works!"

**Create file:** `hello_synapse.syn`

```synapse
# Your first Synapse program!
print("Hello, Synapse Language!")

# Test uncertainty quantification
uncertain measurement = 42.3 ± 0.5
print(f"Uncertain value: {measurement}")

# Test parallel execution  
parallel greetings:
    branch english: print("Hello!")
    branch spanish: print("¡Hola!")
    branch french: print("Bonjour!")
```

**Run the program:**
```bash
synapse hello_synapse.syn
```

[Show expected output]
```
Hello, Synapse Language!
Uncertain value: 42.30 ± 0.50
Hello!
¡Hola!
Bonjour!
```

**Presenter:** "Beautiful! Your first quantum-enhanced program is running!"

### TROUBLESHOOTING (8:30 - 9:30)

[Screen shows common issues and solutions]

**Presenter:** "Let's quickly cover common setup issues:"

**Problem 1: 'synapse' command not found**
```bash
# Solution: Use Python module syntax
python -m synapse_lang hello_synapse.syn
```

**Problem 2: Import errors**
```bash
# Solution: Check Python path
pip show synapse-lang
# Reinstall if needed
pip uninstall synapse-lang
pip install synapse-lang
```

**Problem 3: VS Code extension issues**
- Reload VS Code window (Ctrl+Shift+P → "Reload Window")
- Check if file extension is .syn or .synapse
- Verify extension is enabled

**Presenter:** "If you encounter any other issues, join our Discord community - the link is in the description. Our community is incredibly helpful!"

### CONCLUSION (9:30 - 10:00)

**Presenter:** "Congratulations! You now have Synapse Language fully set up and ready for quantum-enhanced scientific computing.

In the next episode, we'll write your first real Synapse program together - we'll explore variables, basic operations, and create a simple uncertainty analysis.

Don't forget to subscribe if you found this helpful, and join our Discord community for support and discussions.

Thanks for watching, and I'll see you in the next episode!"

[End screen with related videos]

---

## 🎬 Production Notes

### Screen Recordings Needed:
- [ ] Fresh Python installation on Windows/Mac/Linux
- [ ] Terminal commands on all three platforms
- [ ] VS Code extension installation process
- [ ] First program creation and execution
- [ ] Common error scenarios and fixes

### Visual Elements:
- [ ] Installation progress bars and success indicators
- [ ] Side-by-side OS comparison where relevant
- [ ] Checkmark animations for successful steps
- [ ] Error message examples with solutions

### Key Emphasis Points:
1. **Simplicity** - "Just one command"
2. **Cross-platform** - Works everywhere  
3. **Verification** - Always test installation
4. **Community support** - Help is available
5. **Ready to code** - Excitement for next episode

### Potential Issues to Address:
- Python version conflicts (2.7 vs 3.x)
- PATH environment variable issues
- Permission problems on different OS
- Firewall/antivirus interference
- Network connectivity issues

### Call-to-Action Strategy:
- Primary: Try installation yourself
- Secondary: Join Discord for help
- Tertiary: Subscribe for next episode
- Follow-up: Share installation success

### Next Episode Teaser:
"Next time, we'll build a climate model with uncertainty analysis in just 20 lines of Synapse code!"