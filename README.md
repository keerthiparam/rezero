# Wipe Certificate Generation System

A comprehensive data sanitization solution that securely wipes storage devices and generates cryptographically signed certificates as proof of sanitization completion.

[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com/23102097-9027s-projects/v0-wipe-certificate-generation)
[![Built with v0](https://img.shields.io/badge/Built%20with-v0.app-black?style=for-the-badge)](https://v0.app/chat/projects/Jrtp9FxhMfd)

## 🔒 Overview

This system provides enterprise-grade data sanitization for various storage devices including HDDs, SSDs, NVMe drives, and Android devices. Each sanitization process generates a cryptographically signed certificate that serves as tamper-proof evidence of secure data destruction.

## ✨ Features

- **Multi-Device Support**: HDDs, SATA/PCIe SSDs, NVMe drives, and Android devices
- **Cryptographic Certificates**: RSA-signed JSON certificates with verification data
- **Human-Readable Reports**: PDF certificates with QR codes for verification
- **Offline Operation**: Bootable ISO for air-gapped environments
- **CLI & GUI**: Command-line tools and desktop interface
- **Verification System**: Web-based certificate validation

## 🚀 Quick Start

### Prerequisites

- Linux development machine (Ubuntu/Debian recommended)
- Root access for device operations
- Test devices for safe development

### Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/your-username/wipe-certificate-generation.git
cd wipe-certificate-generation

# Install required tools
sudo apt update
sudo apt install hdparm nvme-cli blkdiscard shred lsblk jq openssl wkhtmltopdf qrencode

# Make CLI tool executable
chmod +x wipectl.sh
\`\`\`

### Basic Usage

\`\`\`bash
# Dry run (safe testing)
./wipectl.sh --dry /dev/sdX

# Live wipe (DESTRUCTIVE - use with caution)
./wipectl.sh --live /dev/sdX

# Generate certificate
python3 gen_cert.py /dev/sdX

# Sign certificate
openssl dgst -sha256 -sign signer.key -out cert.sig cert.json

# Verify certificate
openssl dgst -sha256 -verify signer.pub.pem -signature cert.sig cert.json
\`\`\`

## 📋 Supported Devices

### Storage Devices
- **HDDs**: ATA Secure Erase via hdparm
- **SATA SSDs**: ATA Secure Erase with cryptographic verification
- **NVMe SSDs**: Format with Secure Erase Settings (SES)
- **PCIe SSDs**: Vendor-specific secure erase commands

### Mobile Devices
- **Android (Non-rooted)**: Factory reset with encryption verification
- **Android (Service mode)**: ADB/Fastboot userdata wiping
- **iOS**: Guided secure erase process

## 🔐 Security Features

- **RSA Digital Signatures**: 3072-bit keys for certificate authenticity
- **Cryptographic Verification**: SHA-256 hashing of wiped sectors
- **Tamper Evidence**: Signed certificates prevent modification
- **Audit Trail**: Complete sanitization history and verification data

## 📁 Project Structure

\`\`\`
├── wipectl.sh              # Main CLI sanitization tool
├── gen_cert.py             # Certificate generation script
├── verify.sh               # Certificate verification script
├── signer.key              # RSA private key (test only)
├── signer.pub.pem          # RSA public key
├── docs/                   # Documentation and guides
├── test-devices/           # Device inventory and test results
├── scripts/                # Utility scripts
└── ui/                     # Desktop application (Tauri/Electron)
\`\`\`

## 🛠️ Development Workflow

1. **Setup**: Initialize test environment with disposable devices
2. **Development**: Create sanitization methods for each device type
3. **Testing**: Validate wipe effectiveness with forensic tools
4. **Certification**: Generate and sign completion certificates
5. **Verification**: Implement certificate validation system

## ⚠️ Safety Warnings

- **DESTRUCTIVE OPERATIONS**: All wipe operations permanently destroy data
- **TEST ENVIRONMENT ONLY**: Never run on production systems
- **EXPLICIT CONSENT**: Always require owner confirmation before wiping
- **BACKUP VERIFICATION**: Ensure no important data exists before proceeding

## 🧪 Testing & Validation

### Pre-Wipe Testing
\`\`\`bash
# Record sample data before wipe
dd if=/dev/sdX bs=4096 count=1 skip=0 of=before0.bin
sha256sum before0.bin
\`\`\`

### Post-Wipe Verification
\`\`\`bash
# Verify wipe effectiveness
dd if=/dev/sdX bs=4096 count=1 skip=0 of=after0.bin
sha256sum after0.bin

# Attempt data recovery (should fail)
photorec /dev/sdX
\`\`\`

## 📖 Documentation

- [Installation Guide](docs/installation.md)
- [Device-Specific Procedures](docs/devices.md)
- [Certificate Format Specification](docs/certificates.md)
- [Security Architecture](docs/security.md)
- [API Reference](docs/api.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Test thoroughly with disposable devices
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal & Compliance

- Ensure compliance with local data protection regulations
- Obtain proper authorization before sanitizing devices
- Maintain audit logs for compliance requirements
- Use HSM-based signing for production deployments

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/wipe-certificate-generation/issues)
- **Documentation**: [Project Wiki](https://github.com/your-username/wipe-certificate-generation/wiki)
- **Security**: Report security issues privately to security@yourcompany.com

## 🏗️ Roadmap

- [ ] HSM integration for production key management
- [ ] PKCS#7 certificate format support
- [ ] Blockchain anchoring for certificate immutability
- [ ] Mobile app for certificate verification
- [ ] Enterprise dashboard and reporting
- [ ] Integration with asset management systems

---

**⚠️ IMPORTANT**: This system performs irreversible data destruction. Always verify device ownership and obtain explicit consent before use. Test thoroughly in controlled environments before production deployment.
