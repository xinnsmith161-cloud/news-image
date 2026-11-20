// news-image-20261120 — "World News, 20 Nov 2026"
//
// This entry is a newspaper front page for Friday 20 November 2026: one
// image that sums up the day's world news. The image itself lives in
// entry.png next to this file (drawn by draw_news.py); all this program
// does is hand that exact file to the grader by placing it at
// $MAKEFUN_OUTPUT_DIR/entry.png ("/output" inside the grader container).
//
// Run it outside the container like this:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
//
// Node 22 standard library only — no dependencies, no network.

import { copyFileSync, existsSync, mkdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

// The PNG beside this file is the entry; resolve it relative to this
// source file rather than the working directory.
const here = dirname(fileURLToPath(import.meta.url));
const sourceImage = resolve(here, 'entry.png');

// Where the grader looks for the image. The environment overrides the
// default so the same code works locally and in the container.
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const destination = join(outputDir, 'entry.png');

if (!existsSync(sourceImage)) {
  throw new Error(`entry image missing: ${sourceImage}`);
}

// The output directory may not exist yet (e.g. a fresh /output mount).
mkdirSync(outputDir, { recursive: true });

copyFileSync(sourceImage, destination);
console.log(`wrote ${destination}`);
