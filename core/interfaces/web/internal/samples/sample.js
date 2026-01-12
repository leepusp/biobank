import { setupSelectableChips } from "./chips.js";

document.addEventListener("DOMContentLoaded", () => {

    /* ===============================================================
       TAGS
    =============================================================== */
    setupSelectableChips({
        chipSelector: ".selectable-tag",
        hiddenContainerId: "tagHiddenInputs",
        inputName: "tags",
        dataAttr: "tagId"
    });

    /* ===============================================================
       ADD TAG (AJAX)
    =============================================================== */
    const addTagForm = document.getElementById("addTagForm");

    if (addTagForm) {
        addTagForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const fd = new FormData(this);

            fetch("/ajax/add_tag/", {
                method: "POST",
                body: fd,
                headers: {
                    "X-CSRFToken": document.querySelector(
                        "[name=csrfmiddlewaretoken]"
                    )?.value
                }
            })
            .then(r => r.json())
            .then(data => {
                if (!data.success) {
                    alert(data.error || "Failed to create tag.");
                    return;
                }

                const chip = document.createElement("span");
                chip.className = "chip selectable-tag chip-selected";
                chip.dataset.tagId = data.id;
                chip.innerText = data.name;

                document.getElementById("tagChipContainer")
                        ?.appendChild(chip);

                const hidden = document.createElement("input");
                hidden.type = "hidden";
                hidden.name = "tags";
                hidden.value = data.id;

                document.getElementById("tagHiddenInputs")
                        ?.appendChild(hidden);

                setupSelectableChips({
                    chipSelector: ".selectable-tag",
                    hiddenContainerId: "tagHiddenInputs",
                    inputName: "tags",
                    dataAttr: "tagId"
                });

                bootstrap.Modal.getInstance(
                    document.getElementById("addTagModal")
                )?.hide();

                this.reset();
            })
            .catch(err => {
                console.error(err);
                alert("Error while creating tag.");
            });
        });
    }

    /* ===============================================================
       KEYWORDS
    =============================================================== */
    const addKeywordForm = document.getElementById("addKeywordForm");

    if (addKeywordForm) {
        addKeywordForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const key = this.key.value.trim();
            const val = this.value.value.trim();

            if (!key || !val) {
                alert("Both fields are required.");
                return;
            }

            const chip = document.createElement("span");
            chip.className = "chip chip-selected";
            chip.innerText = `${key} → ${val}`;

            document.getElementById("keywordChipContainer")
                    ?.appendChild(chip);

            const hidden = document.createElement("input");
            hidden.type = "hidden";
            hidden.name = "keyword_pairs";
            hidden.value = `${key}:::${val}`;

            document.getElementById("keywordHiddenInputs")
                    ?.appendChild(hidden);

            bootstrap.Modal.getInstance(
                document.getElementById("addKeywordModal")
            )?.hide();

            this.reset();
        });
    }

    /* ===============================================================
       FILE UPLOADS
    =============================================================== */
    let fileIndex = 0;

    const addFileBtn = document.getElementById("addFileBtn");
    const fileContainer = document.getElementById("fileContainer");

    if (addFileBtn && fileContainer) {
        addFileBtn.addEventListener("click", () => {

            const wrapper = document.createElement("div");
            wrapper.className = "file-row mb-3";

            wrapper.innerHTML = `
                <input type="file"
                       name="file"
                       class="form-control mb-1"
                       required>

                <input type="text"
                       name="file_type_${fileIndex}"
                       class="form-control mb-1"
                       placeholder="File type (optional)">

                <input type="text"
                       name="file_description_${fileIndex}"
                       class="form-control mb-1"
                       placeholder="Description (optional)">

                <button type="button"
                        class="btn btn-sm btn-outline-danger mt-1">
                    Remove
                </button>
            `;

            // remover linha
            wrapper.querySelector("button")
                   .addEventListener("click", () => {
                       wrapper.remove();
                   });

            fileContainer.appendChild(wrapper);
            fileIndex++;
        });
    }

});

