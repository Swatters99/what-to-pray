const express = require("express");
const cors = require("cors");
const OpenAI = require("openai");
require("dotenv").config();

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

// OpenAI Configuration
const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY, // API key loaded from .env
});

// API Route to Handle Requests
app.post("/generate-prayer", async (req, res) => {
    const { situation } = req.body;

    if (!situation) {
        return res.status(400).json({ error: "Please provide a situation." });
    }

    try {
        const response = await openai.chat.completions.create({
            model: "gpt-3.5-turbo",
            messages: [
                {
                    role: "user",
                    content: `
                    Based on the following situation: "${situation}", generate a thoughtful response that includes:
                    1. A relevant Bible verse with book, chapter, and verse number.
                    2. A Christian prayer reflecting the user's situation (4-6 sentences).
                    3. The name of a Patron Saint with a description of their patronage.
                    4. A prayer to this Patron Saint related to the user's situation.

                    Format the response clearly into sections:
                    - Bible Verse
                    - Prayer
                    - Patron Saint
                    - Prayer to the Patron Saint
                    `,
                },
            ],
            temperature: 0.9,
        });

        const prayerResponse = response.choices[0].message.content;
        res.json({ prayer: prayerResponse });
    } catch (error) {
        console.error("Error:", error);
        res.status(500).json({ error: "An error occurred while generating the prayer." });
    }
});

// Start the Server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
