from flask import Flask, render_template, request, send_file, jsonify
import os
import hashlib
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
PDF_FOLDER = "static/pdfs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ------------------------------------------------------------
# DATA
# ------------------------------------------------------------

VISUAL_EFFECTS = [
    "normal", "zoom", "left", "right",
    "top", "bottom", "flip", "zoom2"
]

TONE_THEMES = {
    "Adventure": "#f59e0b",
    "Funny": "#22c55e",
    "Dramatic": "#dc2626",
    "Mysterious": "#7c3aed",
    "Romantic": "#ec4899",
    "Sci-Fi": "#0891b2",
    "Horror": "#374151",
    "Fantasy": "#9333ea",
    "Superhero": "#2563eb",
}

TONE_STORIES = {
    "Adventure": [
        [
            "{c} begins an exciting journey through {s}.",
            "A mysterious challenge appears, and {c} decides to investigate.",
            "{c} travels deeper into {s} and discovers an important clue.",
            "A dangerous obstacle blocks the path, but {c} refuses to give up.",
            "{c} faces the biggest challenge of the journey.",
            "Using courage and creativity, {c} overcomes the challenge.",
            "{c} completes the adventure and returns with a new discovery.",
            "With the mystery solved, {c} becomes a legend in {s}."
        ],
        [
            "{c} discovers an ancient map hidden in {s}.",
            "The map points to a treasure no one has ever found.",
            "{c} recruits an unlikely team of allies.",
            "A rival tries to steal the map at midnight.",
            "{c} outsmarts the rival in a daring chase.",
            "The team deciphers the final clue together.",
            "They find the treasure — and something even more valuable.",
            "{c} returns to {s} as a hero."
        ],
    ],
    "Funny": [
        [
            "{c} starts a normal day in {s}, but something completely unexpected happens.",
            "{c} tries to solve the problem, but accidentally makes it even funnier.",
            "A silly misunderstanding creates chaos around {s}.",
            "{c} comes up with a funny plan to fix everything.",
            "The plan goes completely wrong, making everyone laugh.",
            "{c} finally finds a hilarious solution to the problem.",
            "Everyone celebrates while {c} realizes the adventure was actually fun.",
            "{c} promises never to speak of this day again. Everyone speaks of it daily."
        ],
        [
            "{c} accidentally becomes mayor of {s} for one day.",
            "The first decree: pizza for every meal.",
            "Chaos erupts when everyone takes it seriously.",
            "{c} tries to fix things with a 'serious speech'.",
            "The speech gets interrupted by runaway goats.",
            "A talent show saves the day somehow.",
            "{c} is declared 'Best Accidental Mayor Ever'.",
            "Everything goes back to normal... mostly."
        ],
    ],
    "Dramatic": [
        [
            "{c} faces a serious problem while living in {s}.",
            "An unexpected event changes everything for {c}.",
            "{c} struggles to find a way through the difficult situation.",
            "A painful truth is revealed, forcing {c} to make a difficult decision.",
            "{c} gathers courage and faces the biggest challenge.",
            "After an emotional struggle, {c} finally finds a way forward.",
            "The story ends with {c} learning an important life lesson.",
            "Years later, {c} understands why it all had to happen."
        ],
        [
            "{c} receives a letter that changes everything about life in {s}.",
            "An old friend returns with a dangerous secret.",
            "{c} must choose between family and duty.",
            "A storm forces everyone to confront the truth.",
            "Sacrifices are made that cannot be undone.",
            "{c} finds strength in an unexpected place.",
            "Forgiveness begins the long healing.",
            "A quiet sunrise marks a new chapter for {c}."
        ],
    ],
    "Mysterious": [
        [
            "{c} notices something strange happening in {s}.",
            "An unusual clue leads {c} toward a hidden secret.",
            "{c} discovers another mysterious clue.",
            "A strange message appears and creates even more questions.",
            "{c} follows the clues into a mysterious location.",
            "The hidden truth is finally revealed to {c}.",
            "{c} discovers the mystery was connected to the very beginning.",
            "One final clue suggests the story is far from over."
        ],
        [
            "A priceless artifact vanishes from the museum in {s}.",
            "{c} is the only witness — but remembers nothing.",
            "Strange symbols begin appearing around {c}.",
            "A secret society sends {c} an invitation.",
            "The invitation is a trap... or is it a test?",
            "{c} uncovers a hidden chamber beneath {s}.",
            "The thief is someone {c} never suspected.",
            "The artifact was protecting something far bigger."
        ],
    ],
    "Romantic": [
        [
            "{c} meets someone special while spending time in {s}.",
            "A small conversation creates an unexpected connection.",
            "{c} begins to realize that these moments mean something more.",
            "A misunderstanding creates an emotional distance.",
            "{c} decides to be honest about their feelings.",
            "The misunderstanding is resolved through an emotional conversation.",
            "{c} and their special friend begin a beautiful new chapter together.",
            "Under the lights of {s}, two hearts finally beat as one."
        ],
        [
            "{c} moves to {s} hoping for a fresh start.",
            "A chance encounter at a small café changes the plan.",
            "Long walks become the highlight of every day.",
            "An old flame reappears, stirring doubt.",
            "{c} must follow the heart, not the past.",
            "A heartfelt letter bridges the distance.",
            "Two worlds become one under the city lights.",
            "{c} realizes home was never a place — it is a person."
        ],
    ],
    "Sci-Fi": [
        [
            "{c} wakes from cryo-sleep as the ship arrives at {s}.",
            "Something on the scanners does not belong.",
            "{c} suits up for the first expedition outside.",
            "The crew finds ruins older than any known civilization.",
            "A signal pulses from deep beneath the surface.",
            "{c} decodes it: a warning... and an invitation.",
            "The ship's AI makes an impossible choice.",
            "{c} returns with knowledge that changes humanity forever."
        ],
    ],
    "Horror": [
        [
            "{c} inherits an old house at the edge of {s}.",
            "The locals refuse to talk about it after dark.",
            "Doors open by themselves on the first night.",
            "{c} finds a diary written in an unknown hand.",
            "The last entry is dated tomorrow.",
            "Shadows gather at the foot of the bed.",
            "{c} burns the diary and breaks the curse — or so it seems.",
            "On the drive back, the radio whispers {c}'s name."
        ],
    ],
    "Fantasy": [
        [
            "{c}, a humble apprentice, discovers a glowing rune in {s}.",
            "The rune marks {c} as the chosen of the Elders.",
            "A dragon attack reveals the rune's power.",
            "{c} must gather the three lost relics.",
            "A traitor in the council plots in secret.",
            "The final relic lies in the dragon's lair.",
            "{c} spares the dragon and gains a powerful ally.",
            "Light returns to {s} as a new legend is born."
        ],
    ],
    "Superhero": [
        [
            "{c} gains incredible powers during a strange accident in {s}.",
            "Hiding the secret identity proves harder than expected.",
            "A villain threatens to plunge {s} into darkness.",
            "{c} designs a suit and a codename overnight.",
            "The first rescue goes viral.",
            "The villain discovers {c}'s greatest weakness.",
            "Friends become allies in the final battle.",
            "{c} embraces the mask — and the responsibility."
        ],
    ],
}

TONE_DIALOGUES = {
    "Adventure": ["Here we go!", "Did you hear that?", "No turning back now.", "I have a plan...", "Trust me!", "Almost there!", "We did it!", "Same time next week?"],
    "Funny": ["Oops.", "That was NOT my fault.", "Wait... what?", "Genius plan incoming!", "Nailed it. Kinda.", "Why is everyone laughing?", "I am a genius!", "Best. Day. Ever."],
    "Dramatic": ["I cannot do this...", "I have to try.", "Not like this.", "This ends now.", "Forgive me.", "I will not run anymore.", "It is over.", "I will never forget."],
    "Mysterious": ["Who is there?", "That was not here before...", "Follow the clues.", "Nothing is what it seems.", "We are being watched.", "The truth is close.", "It all makes sense now...", "Case closed."],
    "Romantic": ["Hi... I mean, hello!", "Do you believe in fate?", "I have been thinking...", "It is not what it looks like!", "I need to tell you something.", "I am listening.", "Me too.", "To new beginnings."],
    "Sci-Fi": ["Systems online.", "That is impossible...", "Scanning sector 7.", "Engage the drive!", "We are not alone.", "Initiate protocol.", "Jump in 3... 2... 1...", "Welcome to the future."],
    "Horror": ["Did you hear that?", "We should leave. Now.", "It is getting closer...", "Do not look back.", "Run!", "It knows my name...", "Stay quiet.", "We survived. Barely."],
    "Fantasy": ["The prophecy speaks of you.", "Magic flows here.", "An ancient power awakens.", "Trust the blade.", "The dragon approaches!", "By the light of the Elders...", "The realm is saved.", "Our legend begins."],
    "Superhero": ["This city needs me.", "Not on my watch.", "I can handle this.", "Behind you!", "Time to suit up.", "For the people!", "Justice wins again.", "Another day saved."],
}

ART_DESCRIPTIONS = {
    "Comic Book": "Bold comic-book action with expressive poses and dramatic moments.",
    "Cartoon": "Bright cartoon visuals with playful expressions and fun movements.",
    "Anime": "Anime-inspired visuals with expressive characters and cinematic emotions.",
    "Manga": "Manga-inspired visuals with dramatic expressions, detailed backgrounds and strong emotions.",
    "Realistic": "Realistic visuals with natural environments, detailed characters and cinematic lighting.",
    "Noir": "High-contrast noir visuals with deep shadows, rain and dramatic lighting.",
    "Watercolor": "Soft watercolor visuals with gentle colors and dreamlike scenes.",
}

# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def seed_from(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)


def create_story(prompt, character, setting, tone, art_style, panels, seed=0):
    arcs = TONE_STORIES.get(tone, TONE_STORIES["Adventure"])
    arc = arcs[seed % len(arcs)]

    dialogues = TONE_DIALOGUES.get(
        tone, TONE_DIALOGUES["Adventure"]
    )

    art_description = ART_DESCRIPTIONS.get(
        art_style, ART_DESCRIPTIONS["Comic Book"]
    )

    final_scenes = []

    for i in range(panels):

        if i < len(arc):
            template = arc[i]
        else:
            template = "{c} continues the story through {s}."

        scene_text = template.format(
            c=character, s=setting
        )

        if i == 0 and prompt:
            scene_text += (
                " The main story idea is: " + prompt
            )

        final_scenes.append({
            "number": i + 1,
            "text": scene_text,
            "dialogue": dialogues[i % len(dialogues)],
            "art_description": art_description,
            "tone": tone,
            "art_style": art_style,
        })

    return final_scenes


def apply_effects(scenes):
    for i, scene in enumerate(scenes):
        scene["effect"] = VISUAL_EFFECTS[
            i % len(VISUAL_EFFECTS)
        ]
    return scenes

# ------------------------------------------------------------
# ROUTES
# ------------------------------------------------------------

@app.route("/api/preview")
def api_preview():
    """Real-time endpoint: returns scenes as JSON."""
    prompt = request.args.get("story_prompt", "")
    character = request.args.get("character", "Hero") or "Hero"
    setting = request.args.get("setting", "Unknown World") or "Unknown World"
    tone = request.args.get("tone", "Adventure")
    art_style = request.args.get("art_style", "Comic Book")

    try:
        panels = int(request.args.get("panels", 4))
    except (TypeError, ValueError):
        panels = 4

    panels = max(2, min(panels, 8))

    seed = seed_from(
        prompt + character + tone + setting
    )

    scenes = create_story(
        prompt, character, setting,
        tone, art_style, panels, seed
    )
    scenes = apply_effects(scenes)

    return jsonify({
        "scenes": scenes,
        "seed": seed,
        "theme": TONE_THEMES.get(tone, "#6d28d9"),
        "character": character,
    })


@app.route("/", methods=["GET", "POST"])
def home():
    comic = None

    if request.method == "POST":

        story_prompt = request.form.get("story_prompt", "")
        character = request.form.get("character", "Hero")
        setting = request.form.get("setting", "Unknown World")
        tone = request.form.get("tone", "Adventure")
        art_style = request.form.get("art_style", "Comic Book")
        layout = request.form.get("layout", "grid2")

        try:
            panels = int(request.form.get("panels", 4))
        except (TypeError, ValueError):
            panels = 4

        panels = max(2, min(panels, 8))

        image_file = request.files.get("image")
        image_path = None

        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            image_file.save(
                os.path.join(UPLOAD_FOLDER, filename)
            )
            image_path = "uploads/" + filename

        seed = seed_from(
            story_prompt + character + tone + setting
        )

        scenes = create_story(
            story_prompt, character, setting,
            tone, art_style, panels, seed
        )
        scenes = apply_effects(scenes)

        comic = {
            "story_prompt": story_prompt,
            "character": character,
            "setting": setting,
            "tone": tone,
            "art_style": art_style,
            "layout": layout,
            "panels": panels,
            "seed": seed,
            "theme": TONE_THEMES.get(tone, "#6d28d9"),
            "image": image_path,
            "scenes": scenes,
        }

    return render_template("index.html", comic=comic)


@app.route("/export-pdf", methods=["POST"])
def export_pdf():

    character = request.form.get("character", "Hero")
    setting = request.form.get("setting", "Unknown World")
    tone = request.form.get("tone", "Adventure")
    art_style = request.form.get("art_style", "Comic Book")
    story_prompt = request.form.get("story_prompt", "")

    try:
        panels = int(request.form.get("panels", 4))
    except (TypeError, ValueError):
        panels = 4

    panels = max(2, min(panels, 8))

    try:
        seed = int(request.form.get("seed", 0))
    except (TypeError, ValueError):
        seed = 0

    image_path = request.form.get("image_path")

    theme = TONE_THEMES.get(tone, "#6d28d9")

    scenes = create_story(
        story_prompt, character, setting,
        tone, art_style, panels, seed
    )

    pdf_path = os.path.join(
        PDF_FOLDER, "comiccraft_comic.pdf"
    )

    pdf = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # TITLE
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawCentredString(
        width / 2, height - 50, "ComicCraft"
    )

    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(
        width / 2, height - 70,
        "Create  -  Imagine  -  Explore"
    )

    y = height - 110

    for scene in scenes:

        if y < 200:
            pdf.showPage()
            y = height - 60

        # Panel border
        pdf.setLineWidth(2)
        pdf.setStrokeColor(HexColor("#111827"))
        pdf.rect(45, y - 150, width - 90, 135)

        # Themed header bar
        pdf.setFillColor(HexColor(theme))
        pdf.rect(45, y - 40, width - 90, 25,
                 stroke=0, fill=1)

        pdf.setFillColor(HexColor("#ffffff"))
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(
            55, y - 33,
            "SCENE %d  -  %s" % (
                scene["number"], tone.upper()
            )
        )

        # Scene text (wrapped)
        pdf.setFillColor(HexColor("#111827"))
        pdf.setFont("Helvetica", 10)

        words = scene["text"].split()
        line = ""
        text_y = y - 62

        for word in words:
            test_line = (line + " " + word).strip()
            if pdf.stringWidth(
                test_line, "Helvetica", 10
            ) < 250:
                line = test_line
            else:
                pdf.drawString(60, text_y, line)
                text_y -= 14
                line = word

        if line:
            pdf.drawString(60, text_y, line)
            text_y -= 14

        # Dialogue bubble
        pdf.setFont("Helvetica-Oblique", 9)
        pdf.setFillColor(HexColor("#4b5563"))
        pdf.drawString(
            60, text_y - 6,
            '"%s"' % scene["dialogue"]
        )

        pdf.setFont("Helvetica", 8)
        pdf.setFillColor(HexColor("#9ca3af"))
        pdf.drawString(
            60, y - 140,
            scene["art_description"][:60]
        )

        # Image
        if image_path:
            full_image_path = os.path.join(
                "static", image_path
            )
            if os.path.exists(full_image_path):
                try:
                    pdf.drawImage(
                        ImageReader(full_image_path),
                        width - 235, y - 140,
                        width=150, height=100,
                        preserveAspectRatio=True,
                        anchor="c"
                    )
                except Exception:
                    pass

        y -= 170

    # FOOTER
    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(HexColor("#111827"))
    pdf.drawCentredString(
        width / 2, 25,
        "Character: %s | Setting: %s | "
        "Tone: %s | Art Style: %s" % (
            character, setting, tone, art_style
        )
    )

    pdf.save()

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="ComicCraft_Comic.pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)