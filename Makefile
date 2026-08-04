.PHONY: all watch clean diagrams diagrams-clean shots stubs debt

MMD_SRC := $(wildcard figures/mermaid/*.mmd)
MMD_PDF := $(patsubst figures/mermaid/%.mmd,figures/diagrams/%.pdf,$(MMD_SRC))

# mermaid-cli drives a headless Chromium. The config below is written on first
# use and points at whatever browser is available; override BROWSER on the
# command line if yours lives somewhere else.
BROWSER ?= $(shell command -v chromium 2>/dev/null || command -v chromium-browser 2>/dev/null || command -v google-chrome 2>/dev/null || echo /opt/pw-browsers/chromium)

all: diagrams
	latexmk -pdf -interaction=nonstopmode main.tex

# Skip diagram rendering — useful when iterating on prose and mermaid-cli is
# slow or absent. Unrendered diagrams print their source, so the build is still
# readable.
text-only:
	latexmk -pdf -interaction=nonstopmode main.tex

watch:
	latexmk -pvc -pdf -interaction=nonstopmode main.tex

clean:
	latexmk -C
	rm -f *.shots *.dgm *.ilg *.ind *.idx

# ---------------------------------------------------------------------------
# Diagrams. Source of truth is figures/mermaid/*.mmd, which is committed.
# The rendered PDFs are build output and are gitignored, so a diagram change
# shows up in review as a readable text diff.
# ---------------------------------------------------------------------------
diagrams: $(MMD_PDF)

figures/diagrams/%.pdf: figures/mermaid/%.mmd figures/mermaid/.puppeteer.json figures/mermaid/config.json
	@mkdir -p figures/diagrams
	npx -y @mermaid-js/mermaid-cli@11 \
	  -i $< -o $@ \
	  -p figures/mermaid/.puppeteer.json \
	  -c figures/mermaid/config.json \
	  -b transparent --pdfFit

figures/mermaid/.puppeteer.json:
	@mkdir -p figures/mermaid
	@printf '{"executablePath":"%s","args":["--no-sandbox","--disable-dev-shm-usage"]}\n' "$(BROWSER)" > $@
	@echo "Wrote $@ pointing at $(BROWSER)"

diagrams-clean:
	rm -rf figures/diagrams

# ---------------------------------------------------------------------------
# Debt ledgers. Each of these is a promise made to a reader that has not yet
# been kept, so they are counted rather than remembered.
# ---------------------------------------------------------------------------
shots:
	@grep -rn '\\needscreenshot{' chapters appendices frontmatter 2>/dev/null \
	  | sed -E 's/.*needscreenshot\{([^}]*)\}.*/\1/' \
	  | sort -u \
	  | while read k; do \
	      [ -f "figures/screenshots/$$k.png" ] || echo "MISSING: $$k.png"; \
	    done

stubs:
	@grep -rln '\\chapterstub{' chapters appendices 2>/dev/null \
	  | sed 's/^/STUB: /' || true

debt:
	@echo "== Chapters not yet written =="; $(MAKE) -s stubs
	@echo
	@echo "== Screenshots outstanding =="; $(MAKE) -s shots
	@echo
	@printf "== verifybox blocks: "
	@# chapters and appendices only. The introduction contains one of each
	@# admonition as a specimen, and counting those as debt makes the ledger
	@# lie by a constant.
	@grep -rc 'begin{verifybox}' chapters appendices 2>/dev/null \
	  | awk -F: '{s+=$$2} END {print s+0}'
	@printf "== mermaid sources: "
	@ls figures/mermaid/*.mmd 2>/dev/null | wc -l
