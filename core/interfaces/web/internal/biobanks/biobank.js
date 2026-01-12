/* =========================================================
   BIOBANK PAGE JS
   Tags, Keywords, Smart Localization & Safe Delete
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
   KEYWORDS (LOCAL)
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
        chipContainer.appendChild(chip);

        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "keyword_pairs";
        input.value = `${key}:::${value}`;
        hiddenContainer.appendChild(input);

        bootstrap.Modal
            .getInstance(document.getElementById("addKeywordModal"))
            ?.hide();

        form.reset();
    });
}

/* =========================================================
   SMART LOCALIZATION (SEARCH + MAP)
========================================================= */
function initSmartLocation() {
    const mapEl = document.getElementById("map");
    const searchInput = document.querySelector("input[name='institution']");
    const latInput = document.querySelector("input[name='latitude']");
    const lngInput = document.querySelector("input[name='longitude']");
    const labelInput = document.querySelector("input[name='location_label']");

    if (!mapEl || !searchInput || typeof L === "undefined") return;

    const map = L.map("map").setView([0, 0], 2);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors"
    }).addTo(map);

    let marker = null;
    let debounce = null;

    function updateMarker(lat, lng) {
        if (marker) {
            marker.setLatLng([lat, lng]);
        } else {
            marker = L.marker([lat, lng]).addTo(map);
        }
        latInput.value = lat.toFixed(6);
        lngInput.value = lng.toFixed(6);
    }

    searchInput.addEventListener("input", () => {
        clearTimeout(debounce);

        debounce = setTimeout(() => {
            const query = searchInput.value.trim();
            if (!query) return;

            fetch(
                `https://nominatim.openstreetmap.org/search?format=json&addressdetails=1&q=${encodeURIComponent(query)}`
            )
            .then(r => r.json())
            .then(data => {
                if (!data.length) return;

                const place = data[0];
                const lat = parseFloat(place.lat);
                const lon = parseFloat(place.lon);

                map.setView([lat, lon], 15);
                updateMarker(lat, lon);

                labelInput.value = place.display_name;
            });
        }, 600);
    });

    map.on("click", e => {
        const lat = e.latlng.lat;
        const lng = e.latlng.lng;

        updateMarker(lat, lng);

        fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`
        )
        .then(r => r.json())
        .then(data => {
            if (data.display_name) {
                labelInput.value = data.display_name;
                searchInput.value = data.display_name;
            }
        });
    });
}

/* =========================================================
   DELETE BIOBANK CONFIRMATION
========================================================= */
function initDeleteBiobankConfirm() {
    const modalEl = document.getElementById("confirmDeleteBiobankModal");
    if (!modalEl) return;

    const nameEl = document.getElementById("deleteBiobankName");
    const idInput = document.getElementById("deleteBiobankId");

    document.querySelectorAll(".js-delete-biobank").forEach(btn => {
        btn.addEventListener("click", () => {
            nameEl.textContent = btn.dataset.biobankName;
            idInput.value = btn.dataset.biobankId;
            new bootstrap.Modal(modalEl).show();
        });
    });
}

/* =========================================================
   INIT
========================================================= */
document.addEventListener("DOMContentLoaded", () => {
    initTagSelector();
    initAddTagModal();
    initKeywordSelector();
    initSmartLocation();
    initDeleteBiobankConfirm();

    console.debug("Biobank JS initialized (all features enabled)");
});

