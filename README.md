# 🛡️ Malicious Website Blocker Tool

> A real-time endpoint security tool that detects and blocks malicious & 
> phishing websites using VirusTotal API and system-level hosts file management.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square&logo=windows)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=flat-square)

---

## 📌 About

This tool was developed as part of a **Cyber Security Internship at Supraja Technologies**.  
It protects users from unknowingly accessing phishing or malware-infected websites by 
blocking them at the system level — before the browser even loads the page.

---

## 🚀 Features

- 🔍 **Real-time malicious URL detection** via VirusTotal API
- 🛑 **System-level domain blocking** through Windows hosts file
- 🔐 **OTP-based verification** before any blocking action (via email)
- 📁 **Bulk URL processing** from `.txt` or `.csv` files
- ✅ **Unblock websites** with a single click
- 🌓 **Dark/Light theme toggle** with ttkbootstrap
- 💾 **JSON-based config persistence** — remembers your email settings
- 🖥️ **Animated splash screen** on launch
- 📊 **Website reputation checker** — full VirusTotal report

---

## 🖼️ Screenshots

> <img width="259" height="299" alt="image" src="https://github.com/user-attachments/assets/ceee2d47-a9a3-4c85-8d4c-b9436f94edce" />


---

## 🛠️ Tools & Technologies

| Category | Technologies |
|---|---|
| Language | Python 3.8+ |
| GUI | Tkinter, ttkbootstrap |
| Security API | VirusTotal API v3 |
| Networking | requests, smtplib, ssl |
| Image Handling | Pillow (PIL) |
| Data Storage | JSON |
| Hardware Target | Windows hosts file |

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or above
- Windows OS (Administrator access required)
- VirusTotal API Key (free at virustotal.com)

### Install Dependencies
```bash
pip install ttkbootstrap requests pillow
```

### Run the Tool
```bash
# Must run as Administrator on Windows
python s3.py
```

---

## 📖 How It Works

1. User enters a URL manually or uploads a `.txt`/`.csv` file
2. Tool cleans and extracts the domain name
3. VirusTotal API checks the domain for malicious/suspicious flags
4. If flagged → OTP is sent to your email for verification
5. After OTP confirmation → domain is blocked via the system hosts file
6. Blocked domain redirects to `127.0.0.1` (local loopback — safe dead end)

---

## 🔒 Security & Ethics

> ⚠️ **DISCLAIMER**  
> This tool is developed strictly for **educational and authorized security 
> testing purposes only**.  
> Unauthorized use to block websites on systems without explicit permission 
> is illegal and unethical.  
> The authors take no responsibility for misuse of this tool.

---

## 👨‍💻 Developer

| Name | ID | Email |
|---|---|---|
| Pentu Harsha Vardhan | ST#IS#7500 | harshapentu@gmail.com |

---

## 🏢 Organization

**Supraja Technologies**  
📧 contact@suprajatechnologies.com

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
