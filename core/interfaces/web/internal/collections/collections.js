/* =========================================================
   COLLECTION PAGE JS
   Tags + Keywords (same pattern as Biobank)
========================================================= */

/* =========================================================
   UTIL
========================================================= */
function getCsrfToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]")?.value;
}

/* =========================================================
   TAG SELECTION (CHIPS)
========================================================= */
function toggleTagChip(chip) {
    const tagId = chip.dataset.tagId;
    const hiddenContainer = document.getElementById("tagHiddenInputs");
    if (!tagId || !hiddenContainer) return;

    chip.classList.toggle("chip-selected");

    const existing = hiddenContainer.querySelector(
        `input[value="${tagId}"]`
    );

    if (existing) {
        existing.remove();
    } else {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "tags";
        input.value = tagId;
        hiddenContainer.appendChild(input);
    }
}

function initTagSelector() {
    document.querySelectorAll(".selectable-tag").forEach(chip => {
        if (chip.dataset.bound === "1") return;

        chip.addEventListener("click", () => toggleTagChip(chip));
        chip.dataset.bound = "1";
    });
}

/* =========================================================
   ADD TAG (AJAX)
========================================================= */
function initAddTagModal() {
    const form = document.getElementById("addTagForm");
    if (!form) return;

    form.addEventListener("submit", e => {
        e.preventDefault();

        const fd = new FormData(form);

        fetch("/ajax/add_tag/", {
            method: "POST",
            body: fd,
            headers: {
                "X-CSRFToken": getCsrfToken()
            }
        })
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                alert(data.error || "Error creating tag");
                return;
            }

            const chipContainer = document.getElementById("tagChipContainer");
            const hiddenContainer = document.getElementById("tagHiddenInputs");

            const chip = document.createElement("span");
            chip.className = "tag-chip selectable-tag chip-selected";
            chip.dataset.tagId = data.id;
            chip.innerText = data.name;

            chipContainer.appendChild(chip);

            const input = document.createElement("input");
            input.type = "hidden";
            input.name = "tags";
            input.value = data.id;
            hiddenContainer.appendChild(input);

            initTagSelector();

            bootstrap.Modal
                .getInstance(document.getElementById("addTagModal"))
                ?.hide();

            form.reset();
        })
        .catch(() => alert("Unexpected error while creating tag"));
    });
}

/* =========================================================
   KEYWORDS (LOCAL, SAME AS BIOBANK)
========================================================= */
function initKeywordSelector() {
    const form = document.getElementById("addKeywordForm");
    if (!form) return;

    form.addEventListener("submit", e => {
        e.preventDefault();

        const key = form.key.value.trim();
        const value = form.value.value.trim();

        if (!key || !value) {
            alert("Both keyword and value are required.");
            return;
        }

        const chipContainer = document.getElementById("keywordChipContainer");
        const hiddenContainer = document.getElementById("keywordHiddenInputs");

        const chip = document.createElement("span");
        chip.className = "keyword-chip chip-selected";
        chip.innerText = `${key} → ${value}`;

        const hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = "keyword_pairs";
        hidden.value = `${key}:::${value}`;

        chip.addEventListener("click", () => {
            chip.remove();
            hidden.remove();
        });

        chipContainer.appendChild(chip);
        hiddenContainer.appendChild(hidden);

        bootstrap.Modal
            .getInstance(document.getElementById("addKeywordModal"))
            ?.hide();

        form.reset();
    });
}

/* =========================================================
   INIT
========================================================= */
document.addEventListener("DOMContentLoaded", () => {
    initTagSelector();
    initAddTagModal();
    initKeywordSelector();

    console.debug("Collection JS initialized (Biobank pattern)");
});

