// Render index.html frame by frame, build music + sfx from the page's cues, mux into an MP4.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');

const DIR = __dirname, FPS = 30, OUT = 'tactique-6-secondes-v2.mp4';
const only = process.argv[2]; // optional: comma-separated times -> preview stills

(async () => {
  const tl = JSON.parse(fs.readFileSync(path.join(DIR, 'timeline.json'), 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('console', m => { if (m.type() === 'warning' || m.type() === 'error') console.log('page:', m.text()); });
  await page.goto('file://' + path.join(DIR, 'index.html'));
  const cues = await page.evaluate(async tl => await window.init(tl), tl);
  fs.writeFileSync(path.join(DIR, 'cues.json'), JSON.stringify(cues));

  if (only) {
    for (const s of only.split(',')) {
      await page.evaluate(t => window.render(t), +s);
      await page.screenshot({ path: path.join(DIR, `still_${s}.png`) });
    }
    await browser.close(); return;
  }
  const frames = path.join(DIR, 'frames');
  fs.rmSync(frames, { recursive: true, force: true }); fs.mkdirSync(frames);
  const n = Math.ceil(tl.total * FPS);
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => window.render(t), i / FPS);
    await page.screenshot({ path: path.join(frames, `f${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 92 });
  }
  await browser.close();
  execFileSync('python3', ['-I', path.join(DIR, 'audio2.py')], { stdio: 'inherit' });
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(frames, 'f%05d.jpg'),
    '-i', path.join(DIR, 'mix.wav'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '20', '-preset', 'medium',
    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', path.join(DIR, OUT)]);
  console.log('done', OUT);
})();
