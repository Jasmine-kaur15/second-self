# SecondSelf: Problem Statement

Every notes app fails the same way: you capture hundreds of notes, bookmarks, PDFs, and ideas — and then you never find them again. Information goes in, but nothing comes back out. Notes sit in folders nobody re-reads. Bookmarks pile up unread. Knowledge doesn't compound.

**Goal:** Build an end-to-end system where you can capture anything (a note, a link, a file), have AI automatically classify and file it, auto-link it to related knowledge, render it as a live interactive graph you can explore, and — most importantly — ask it any question in plain English and get an answer synthesized from your own accumulated knowledge. Then deploy it to a public URL anyone can open.

Not a notes app. Not a chatbot. A brain that organizes itself and answers for you.

## Final System (what you're building over 4 weeks)

Capture any note/link/file 
↓ 
AI classifies & files it (PARA method) 
↓ 
AI auto-links it to related notes (embeddings) 
↓ 
Everything renders as a live, interactive, hoverable graph 
↓ 
Ask it anything in plain English → answer pulled from YOUR notes 
↓ 
Deployed on a public URL anyone can open

## Week-by-Week Problem Statements

Each week is a self-contained problem. Build it, test it on real data (your own notes — not test data), and each week's output becomes the next week's input.

### Week 1 — The Archivist: "Capture Everything, Lose Nothing"
**Problem:** You have no single place to put things. Ideas, links, and notes scatter across apps, browser tabs, and your memory. Build the foundation: one command that captures anything into one place.

**Build:**
1. Set up the project structure from scratch (`raw/`, `wiki/`).
2. Write a Python capture script that takes any note, link, or file and saves it into `raw/` with a timestamp, unique ID, and raw content.
3. Test it on 10+ real pieces of your own scattered information.

**Deliverable:** A working capture script. `raw/` folder populated with 10+ real items.

### Week 2 — The Librarian: "Teach AI to Organize For You"
**Problem:** A pile of raw captures is still a mess. Manual tagging never happens. Make the AI do the filing — and make it notice when two notes are about the same thing and link them automatically.

**Build:**
1. **Auto-Classify:** Write a function that sends any raw capture to a free LLM and gets back a PARA category, tags, and a one-line summary.
2. **Auto-Link:** Compute embeddings for each note. Compare each new capture against existing notes. When content is related, auto-insert a link between them.

**Deliverable:** A pipeline that auto-classifies raw captures with PARA and auto-links related notes.

### Week 3 — The Cartographer: "Visualize the Brain"
**Problem:** Your knowledge is now organized and linked — but you can't see it. Turn the wiki into something you can actually look at, explore, and watch think.

**Build:**
1. **Graph Data Model:** Write a script that reads every note and its links to build a nodes-and-edges representation. Export to JSON.
2. **Interactive Graph:** Use a JS graph library to render notes as nodes, links as edges, with hover popups and drag/zoom functionality.

**Deliverable:** Your wiki converted to a graph and rendered as an interactive visual brain.

### Week 4 — The Oracle: "Ask It Anything, Ship It Public"
**Problem:** A visual brain is beautiful, but the real payoff is answers. Wire up natural-language search over everything you know — then package the whole thing into one deployable product.

**Build:**
1. **Ask Your Brain:** Build a single `ask()` function combining embeddings (for retrieval), the wiki (source content), and an LLM (to synthesize answers).
2. **UI & Deployment:** Assemble the interactive graph and the search bar into one Streamlit app. Deploy to a free platform (Streamlit Cloud / HF Spaces).

**Deliverable:** Full pipeline working end to end in the deployed app with a public URL.
