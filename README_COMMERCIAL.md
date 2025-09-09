# Synapse Programming Language - Commercial Edition

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://synapse-lang.com)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE-PROPRIETARY)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)

**Synapse** is a revolutionary programming language for scientific computing with native support for parallel execution, uncertainty quantification, and quantum computing.

## 📋 License Requirements

This software requires a valid license for use:

- **Community Edition**: Free for personal/educational use (limited features)
- **Professional Edition**: $499/year for individual commercial use
- **Enterprise Edition**: $4,999/year for organizational use with full features

[**Get Your License →**](https://synapse-lang.com/pricing)

## 🚀 Quick Start

### 1. Installation

```bash
pip install synapse-lang
```

### 2. Activate Your License

```bash
# For evaluation (30-day trial)
synapse --request-trial

# For purchased licenses
synapse --activate-license YOUR-LICENSE-KEY
```

### 3. Verify License

```bash
synapse --license-info
```

## 💼 Edition Comparison

| Feature | Community | Professional | Enterprise |
|---------|-----------|--------------|------------|
| **Personal Use** | ✅ | ✅ | ✅ |
| **Commercial Use** | ❌ | ✅ | ✅ |
| **CPU Cores** | 4 | 16 | Unlimited |
| **Tensor Size** | 1,000 | 100,000 | Unlimited |
| **Parallel Branches** | 2 | 8 | Unlimited |
| **GPU Acceleration** | ❌ | ✅ | ✅ |
| **Quantum Computing** | ❌ | ❌ | ✅ |
| **JIT Compilation** | Limited | ✅ | ✅ |
| **Support** | Community | Email | Priority + SLA |
| **Custom Features** | ❌ | ❌ | ✅ |
| **Telemetry** | Required | Required | Optional |
| **Watermark** | Yes | No | No |
| **Price** | Free | $499/year | $4,999/year |

## 🎯 Use Cases by Edition

### Community Edition
- Learning and education
- Personal projects
- Academic research (with attribution)
- Open-source projects (non-commercial)

### Professional Edition
- Freelance work
- Small business applications
- Commercial research
- Production systems (small scale)

### Enterprise Edition
- Large-scale production systems
- High-performance computing
- Quantum algorithm development
- Mission-critical applications
- Custom feature development

## 🔧 Features

### Core Language Features
- ✨ Parallel execution with `parallel` blocks
- 📊 Uncertainty quantification with automatic error propagation
- 🧠 Scientific reasoning chains
- ⚛️ Quantum computing support (Enterprise)
- 🚀 GPU acceleration (Professional/Enterprise)
- ⚡ JIT compilation for performance

### Code Example

```python
# Parallel execution with uncertainty
uncertain measurement = 10.0 ± 0.1
uncertain velocity = 25.0 ± 0.5

parallel {
    branch physics: {
        momentum = measurement * velocity
        energy = 0.5 * measurement * velocity^2
    }
    branch statistics: {
        mean = average([measurement, velocity])
        std = std_dev([measurement, velocity])
    }
}

# Results automatically include uncertainty propagation
print(f"Momentum: {momentum}")  # Shows value ± uncertainty
```

## 📞 Support

### Community Edition
- GitHub Issues: https://github.com/synapse-lang/synapse/issues
- Community Forum: https://community.synapse-lang.com

### Professional Edition
- Email Support: support@synapse-lang.com
- Response Time: 24-48 hours

### Enterprise Edition
- Priority Support: enterprise@synapse-lang.com
- Phone Support: +1-555-SYNAPSE
- Response Time: 4 hours (SLA)
- Custom Development Available

## 🔒 License Activation

### Online Activation (Recommended)
```python
import synapse_lang

# Activate with license key
synapse_lang.activate_license("YOUR-LICENSE-KEY")

# Check license status
info = synapse_lang.get_license_info()
print(f"Edition: {info['type']}")
print(f"Expires: {info['expires']}")
```

### Offline Activation
For air-gapped systems, contact support@synapse-lang.com for offline activation.

## 📊 Telemetry and Privacy

- Community/Professional editions collect anonymous usage statistics
- Enterprise edition can disable telemetry
- No source code or personal data is collected
- See our [Privacy Policy](https://synapse-lang.com/privacy)

## 🚫 License Restrictions

### Community Edition
- No commercial use
- No production deployments
- Limited to 4 CPU cores
- Required attribution in outputs

### All Editions
- No reverse engineering
- No license key sharing
- No competitive product development
- No redistribution without permission

## 💳 Purchasing

### Individual/Small Business
Visit https://synapse-lang.com/pricing

### Enterprise/Volume Licensing
Contact sales@synapse-lang.com for:
- Volume discounts
- Site licenses
- Custom terms
- Training packages

## 🔄 Upgrades

Upgrade from Community to Professional/Enterprise:
```bash
synapse --upgrade-license YOUR-NEW-LICENSE-KEY
```

## ⚖️ Legal

This software is protected by copyright and licensed under proprietary terms.
See [LICENSE-PROPRIETARY](LICENSE-PROPRIETARY) for full terms.

For academic licensing, contact academic@synapse-lang.com with proof of affiliation.

## 🤝 Contributing

While Synapse is proprietary software, we welcome:
- Bug reports
- Feature requests
- Documentation improvements
- Community plugins (with approval)

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**© 2024 Michael Benjamin Crowe. All Rights Reserved.**

Synapse® is a registered trademark of Michael Benjamin Crowe.