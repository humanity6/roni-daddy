# Requirements

## 📱 End-to-End User Journey (Web App + Vending Machine)

> "There is a lot more work involved than you think…"
> 
> 
> This is a step-by-step guide to help you fully understand the user flow, the responsibilities on both ends (your platform and the manufacturer), and the technical communication bridge required.
> 

---

### 🔁 **User Interface (Web App) Journey**

The mobile-responsive web app launches when the user scans a QR code from the vending machine. Below are the sequential screens:

1. **QR Code → Launch Web App**
    
    • QR code on machine links to `example.com?session_id=XYZ`
    
    • Opens in mobile browser
    
2. **Select Phone Brand**
3. **Select Phone Model and Color**
4. **Display Back View of Selected Phone**
5. **Choose One of 7 Templates**
6. **Upload Image(s) or Text**
    
    • Optional: Enhance with AI using integrated button
    
7. **Preview on Phone Bac**
    
    • Show print preview
    
    • Option to retry
    
8. **Retry with New Prompt / Access Previous Images**
9. **Send Selected Design to Machine for Printing**
10. **Queue Screen (Job Processing)**
11. **Final Screen → "Your Cover is Ready!"**

---

### 🔄 **3-Step System Communication Flow**

### 1. **QR Code → Web Platform (Initial Connection)**

- The vending machine displays a dynamic QR code (with session ID).
- Customer scans the QR and lands on your web platform.
- Design is created and enhanced via your AI tools (no vending machine connection yet).
- User finalizes their design on the mobile browser.

### 2. **Web Platform → Vending Machine**

- On “Submit” or “Pay”:
    - Web app sends image + metadata to vending machine software (via LAN, cloud API, or webhook).
    - Simultaneously, it triggers the vending machine to activate the card reader.

### 3. **Payment → Print Confirmation**

- Customer completes payment (tap/swipe).
- Payment confirmation is received:
    - Printer begins printing.
    - Confirmation appears on both:
        - User’s phone
        - Machine’s screen

---

### 🧩 What You Control

- AI-enhanced **image generation logic**
- **Frontend UX** and design tools
- **API keys and backend system**
- Web-to-machine **communication triggers**

---

### 🏭 What the Manufacturer Supports

1. Dynamic QR generator linking to your URL with session ID
2. Ability to **receive print job (image + metadata)** from your server
3. Card reader:
    - Triggered by your platform
    - Sends **payment success** confirmation
4. API/Webhook bridge to **sync status** with machine screen

---

### 🎨 AI-Enhanced Design Modes

| Mode | Features |
| --- | --- |
| **1. Classic Photo** | Auto-enhance, 1-tap filters (Retro, Glow, Monochrome) |
| **2. Film Strip** | Best order suggestion, uniform tone, auto-crop |
| **3. Frame Me Up** | Subject detection, theme suggestions, face alignment |
| **4. Retro Remix** | Fonts/colors per decade (70s–Y2K), slogan recommendation |
| **5. Mood Match** | Emotion detection or vibe picker, matched layouts |
| **6. GlitchPop FX** | Glitch overlays, masking, intensity control |
| **7. Toon Me** *(NEW)* | Turn photo into cartoon (Anime, Pixar, Comic), theme selector |

---

### 📦 Deliverables

- ✅ Mobile-responsive **web app**
- ✅ Secure **backend + API**
- ✅ **Windows** vending integration (SDK-based)
- ✅ 7 custom **AI-enhanced templates**
- ✅ **Visual & brand styling** guidelines
- ✅ Technical documentation
- ✅ Source code handover + basic deployment support

---

### ⚡ Why This Model Works

### 1. **Centralized & Updatable**

- All logic lives on your web platform
- Easier to iterate, no need to update machine firmware

### 2. **Keeps Machine Simple**

- Just handles:
    - QR display
    - Print job execution
    - Card reader activation

### 3. **Secure and Scalable**

- Your platform controls logic, API keys, design tools
- Easily works across multiple machine types or vendors

### 4. **Future-Proof and Flexible**

- Scale to more locations with no core changes
- Add new AI features or templates anytime

---

### 🛠 Requirements

### ✅ **From Your Web Platform**

- Session tracking per QR scan
- Image editor + AI tools
- Secure payment processing
- API/webhook to notify machine:
    - Image ready
    - Payment confirmed

### ✅ **From Manufacturer (China)**

- Dynamic QR generation (with session/machine ID)
- Ability to receive image + print command
- Trigger card reader remotely and confirm payment
- Sync machine screen status to reflect progress

---

### 🧾 Bottom Line

This setup is not just **feasible** — it’s **smart** and **strategic**.

> You own the magic, the UX, and the brand.
> 
> 
> The vending machine just executes print + payment — the way modern connected retail is done.
> 

---

### 🖥 On-Screen Machine Flow Summary

1. **QR Code Displayed**
2. **User Scans → Mobile Browser Opens**
3. **User Uploads Photo, Edits with AI, Finalizes Design**
4. **Web Prompts Payment → Machine Card Reader Activated**
5. **Payment Confirmed → Printing Starts**
6. **Machine Screen Displays:**
    - Payment Confirmation
    - Live Job Queue
    - “Cover is Ready” screen

---

Let me know when you’ve read and understood this. I’ll be happy to help refine or implement any part.