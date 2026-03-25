```markdown
# Project Zero — Kids Personalised Storybook Service
## System Design v1 · Day 1

## What We're Building
A service where parents upload a child's photo + fill a form.
They receive a personalised PDF storybook in 24 hours.
Price: ₹200 per book.

## The Customer Journey
1. Parent lands on [Tally.so] order form
2. Uploads child's photo + name + age + theme
3. Payment via Razorpay (₹100)
4. n8n automation triggers
5. Claude API generates personalised story
6. Adobe Firefly generates character images
7. Canva assembles the PDF book
8. PDF delivered via email/WhatsApp

## Tech Stack
- Order Form: Tally.so (free)
- Payment: Razorpay
- Automation: n8n
- Story AI: Claude API (claude-sonnet-4-6)
- Image AI: Adobe Firefly Custom Models
- Book Layout: Canva AI
- Delivery: Gmail API / WhatsApp Business API

## Month 1 Build Schedule
- Day 01-03 → Image prompting + character generation
- Day 04-06 → Story generation via Claude API  
- Day 07    → Book layout in Canva
- Week 2    → Order form + Razorpay payment
- Week 3    → Full n8n automation pipeline
```