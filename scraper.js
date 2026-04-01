/**
 * Dawson Timetable Scraper (Simplified)
 * 
 * INSTRUCTIONS:
 * 1. Go to https://timetable.dawsoncollege.qc.ca/
 * 2. Select ALL the options you want to see classes for (or use "Ctrl+A" to
 *    select everything in the Discipline dropdown).
 * 3. Click "Search" and wait for the results to fully load.
 * 4. Click the "+" expand buttons to reveal all hidden sections.
 * 5. Once all results are visible on the page, simply use your browser's
 *    File → "Save As..." (Ctrl+S) to save the page as
 *    "Timetable and Registration Guide.html"
 * 6. Move the saved HTML file into your "Classroom Finder" folder.
 * 7. Run `python app.py` — the parser will automatically detect and use the file!
 * 
 * ALTERNATIVE (automated expand + download):
 * If you have a large result set and want to auto-expand all "+" buttons and
 * save programmatically, paste this script into the browser console (F12):
 */

async function expandAndSave() {
    console.log("%c[Dawson Scraper] Expanding all sections...", "color: #00ff00; font-size: 14px; font-weight: bold;");
    
    // Click all expand/+ buttons
    let expandButtons = Array.from(document.querySelectorAll('a, button, span, div.expand, i.fa-plus, .expand-row')).filter(el =>
        (el.innerText && el.innerText.trim() === '+') ||
        (el.getAttribute('title') && el.getAttribute('title').toLowerCase().includes('expand')) ||
        (el.className && typeof el.className === 'string' && el.className.includes('expand'))
    );

    let clicked = 0;
    for (let btn of expandButtons) {
        try {
            if (btn.offsetParent !== null) {
                btn.click();
                clicked++;
            }
        } catch (e) {}
    }
    
    console.log(`[Dawson Scraper] Clicked ${clicked} expand buttons. Waiting for content to render...`);
    await new Promise(r => setTimeout(r, 2000));

    // Download the page
    let blob = new Blob([document.documentElement.outerHTML], { type: "text/html" });
    let a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "Timetable and Registration Guide.html";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    console.log("%c[Dawson Scraper] Done! Move the downloaded file to your Classroom Finder folder.", "color: #00ff00; font-size: 14px; font-weight: bold;");
    alert("Download complete! Move 'Timetable and Registration Guide.html' to your Classroom Finder folder, then run 'python app.py'.");
}

expandAndSave();
