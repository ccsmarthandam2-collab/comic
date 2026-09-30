/* ComicCraft - real-time preview logic */

(function () {

    "use strict";

    var imageDataUrl = null;

    var storyPrompt = document.getElementById("story_prompt");
    var character   = document.getElementById("character");
    var setting     = document.getElementById("setting");
    var tone        = document.getElementById("tone");
    var artStyle    = document.getElementById("art_style");
    var panels      = document.getElementById("panels");
    var layout      = document.getElementById("layout");
    var imageInput  = document.getElementById("image");
    var randomBtn   = document.getElementById("random-btn");

    var previewGrid   = document.getElementById("preview-grid");
    var previewStatus = document.getElementById("preview-status");

    /* ---------- debounce ---------- */

    function debounce(fn, ms) {
        var t;
        return function () {
            clearTimeout(t);
            var args = arguments;
            t = setTimeout(function () {
                fn.apply(null, args);
            }, ms);
        };
    }

    /* ---------- build query params ---------- */

    function currentParams() {
        return new URLSearchParams({
            story_prompt: storyPrompt.value,
            character: character.value || "Hero",
            setting: setting.value || "Unknown World",
            tone: tone.value,
            art_style: artStyle.value,
            panels: panels.value
        });
    }

    /* ---------- fetch preview ---------- */

    function updatePreview() {

        previewStatus.textContent = "Updating preview...";

        fetch("/api/preview?" + currentParams().toString())
            .then(function (res) { return res.json(); })
            .then(function (data) {
                renderPreview(data);
                previewStatus.textContent =
                    data.scenes.length + " scenes · seed #" +
                    (data.seed % 1000);
            })
            .catch(function () {
                previewStatus.textContent =
                    "Preview unavailable — is the server running?";
            });
    }

    var updatePreviewDebounced = debounce(updatePreview, 350);

    /* ---------- render ---------- */

    function renderPreview(data) {

        previewGrid.className =
            "comic-grid layout-" + layout.value;

        var html = "";

        data.scenes.forEach(function (scene) {

            var imgHtml;

            if (imageDataUrl) {
                imgHtml =
                    '<img class="comic-image effect-' +
                    scene.effect + '" src="' +
                    imageDataUrl + '" alt="preview">';
            } else {
                imgHtml =
                    '<div class="image-placeholder">🎨</div>';
            }

            html +=
                '<div class="comic-panel preview-panel">' +
                    '<div class="panel-number" style="background:' +
                        data.theme + ';">SCENE ' +
                        scene.number + '</div>' +
                    imgHtml +
                    '<div class="panel-text">' +
                        '<h3>' + escapeHtml(data.character) + '</h3>' +
                        '<p>' + escapeHtml(scene.text) + '</p>' +
                        '<div class="speech-bubble">💬 "' +
                            escapeHtml(scene.dialogue) +
                        '"</div>' +
                    '</div>' +
                '</div>';
        });

        previewGrid.innerHTML = html;
    }

    function escapeHtml(str) {
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }

    /* ---------- image preview (client side) ---------- */

    if (imageInput) {
        imageInput.addEventListener("change", function () {

            var file = imageInput.files[0];

            if (!file) {
                imageDataUrl = null;
                updatePreview();
                return;
            }

            var reader = new FileReader();

            reader.onload = function (e) {
                imageDataUrl = e.target.result;
                updatePreview();
            };

            reader.readAsDataURL(file);
        });
    }

    /* ---------- surprise me ---------- */

    var RANDOM_CHARACTERS = [
        "Nova", "Kai", "Zara", "Pixel", "Blaze",
        "Luna", "Rex", "Mira", "Echo", "Titan"
    ];

    var RANDOM_SETTINGS = [
        "a cyberpunk megacity", "a floating sky island",
        "an underwater kingdom", "a haunted lighthouse",
        "a secret space station", "a magical forest",
        "a desert of glass", "a city inside a volcano",
        "a time-traveling train", "an abandoned mall"
    ];

    var RANDOM_PROMPTS = [
        "A lost robot learns what it means to dream",
        "Two rivals must team up to win a cooking contest",
        "A cat discovers it can freeze time",
        "The last library on Earth holds a dangerous secret",
        "A delivery driver accidentally becomes a legend",
        "A young inventor builds a machine that reads memories",
        "An old superhero comes out of retirement",
        "A gardener grows plants that whisper predictions"
    ];

    function randomItem(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    }

    if (randomBtn) {
        randomBtn.addEventListener("click", function () {

            character.value = randomItem(RANDOM_CHARACTERS);
            setting.value = randomItem(RANDOM_SETTINGS);
            storyPrompt.value = randomItem(RANDOM_PROMPTS);

            var toneOptions = tone.options;
            tone.selectedIndex =
                Math.floor(Math.random() * toneOptions.length);

            var styleOptions = artStyle.options;
            artStyle.selectedIndex =
                Math.floor(Math.random() * styleOptions.length);

            updatePreview();
        });
    }

    /* ---------- listeners ---------- */

    [
        storyPrompt, character, setting
    ].forEach(function (el) {
        if (el) {
            el.addEventListener("input", updatePreviewDebounced);
        }
    });

    [tone, artStyle, panels, layout].forEach(function (el) {
        if (el) {
            el.addEventListener("change", updatePreviewDebounced);
        }
    });

    /* initial render */
    updatePreview();

})();