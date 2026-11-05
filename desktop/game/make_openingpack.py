"""openingpack.mp3 - the game's own pack song (1 Nov), made from the preview score.
Time 0 is the tap (the walkout's clock), so the game's beats line up: the rip 0.30 s, white-out
0.85, flag 2.0, position 3.5, crest 5.0, stadium 6.25, card 7.0. A swiped pack starts it at 0.30.
(was: a score for the walkout preview, built from scratch and locked to its beats.
Video time: the tap is at 1.2 s; walkout time w = t - 1.2. 120 BPM, so the reveals
(w = 2.0 flag, 3.5 position, 5.0 crest, 7.0 card) all fall on the beat."""
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100
END = 13.0
TAP = 0.0
N = int(END * SR)
L = np.zeros(N)
R = np.zeros(N)
rng = np.random.default_rng(7)


def at(w):
    """walkout time -> sample index"""
    return int((TAP + w) * SR)


def put(sig, start, gain=1.0, pan=0.0):
    """Mix a mono signal in at sample `start`, panned -1 (left) .. 1 (right)."""
    if start >= N:
        return
    s = sig[:max(0, N - start)] * gain
    lg, rg = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    L[start:start + len(s)] += s * lg
    R[start:start + len(s)] += s * rg


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def lp(x, hz, order=2):
    b, a = signal.butter(order, min(hz, SR * 0.45) / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def hp(x, hz, order=2):
    b, a = signal.butter(order, hz / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi, SR * 0.45) / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def saw(freq, dur, detune=0.0):
    t = tt(dur)
    out = np.zeros_like(t)
    for d in (-detune, 0.0, detune):                 # three slightly detuned saws: a wide synth
        ph = (freq * (1 + d)) * t
        out += 2 * (ph - np.floor(ph + 0.5))
    return out / 3.0


def env(dur, a=0.005, d=0.2, s=0.0, r=0.1):
    n = int(dur * SR)
    e = np.zeros(n)
    ia, id_ = int(a * SR), int(d * SR)
    e[:ia] = np.linspace(0, 1, max(1, ia))[:len(e[:ia])]
    seg = e[ia:ia + id_]
    e[ia:ia + id_] = np.linspace(1, s, max(1, id_))[:len(seg)]
    e[ia + id_:] = s
    ir = int(r * SR)
    if ir and n > ir:
        e[-ir:] *= np.linspace(1, 0, ir)
    return e


def kick(gain=1.0, dur=0.45, f0=150, f1=42):
    t = tt(dur)
    f = f1 + (f0 - f1) * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7.5) * gain + rng.standard_normal(len(t)) * np.exp(-t * 90) * 0.15 * gain


def boom(dur=2.2):
    """the big impact: a dropping sub, a noise slam, a long tail"""
    t = tt(dur)
    f = 30 + 110 * np.exp(-t * 6)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    slam = lp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 9) * 0.9
    tail = lp(rng.standard_normal(len(t)), 600) * np.exp(-t * 1.6) * 0.25
    return sub + slam + tail


def crash(dur=1.8):
    t = tt(dur)
    return hp(rng.standard_normal(len(t)), 5000) * np.exp(-t * 2.6) * 0.6


def hat(dur=0.06):
    t = tt(dur)
    return hp(rng.standard_normal(len(t)), 8000) * np.exp(-t * 70)


def clap():
    t = tt(0.25)
    e = np.zeros_like(t)
    for k in (0, 0.011, 0.023):                       # three quick slaps, then the room
        e += (t >= k) * np.exp(-(t - k).clip(0) * 60)
    return bp(rng.standard_normal(len(t)), 900, 4000) * (e * 0.6 + np.exp(-t * 14) * 0.3)


def riser(dur, f0=300, f1=7000, tone=(200, 900)):
    """noise swept up through a band, plus a rising tone - tension into the next hit"""
    n = int(dur * SR)
    x = rng.standard_normal(n)
    out = np.zeros(n)
    chunk = 1024
    for i in range(0, n, chunk):
        k = i / float(n)
        c = f0 * (f1 / f0) ** k
        seg = x[max(0, i - 2048):i + chunk]
        y = bp(seg, c * 0.7, c * 1.4)
        out[i:i + chunk] = y[-len(out[i:i + chunk]):]
    t = tt(dur)
    f = tone[0] * (tone[1] / tone[0]) ** (t / dur)
    sweep = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    return (out * 2.2 + sweep) * (t / dur) ** 2


def whoosh(dur, up=True):
    n = int(dur * SR)
    x = rng.standard_normal(n)
    out = np.zeros(n)
    for i in range(0, n, 1024):
        k = i / float(n)
        c = (400 * (6000 / 400) ** k) if up else (6000 * (300 / 6000) ** k)
        seg = x[max(0, i - 2048):i + 1024]
        y = bp(seg, c * 0.6, c * 1.6)
        out[i:i + 1024] = y[-len(out[i:i + 1024]):]
    t = tt(dur)
    shape = np.sin(np.pi * t / dur) ** 2
    return out * shape * 1.6


def stab(freqs, dur=0.6):
    """a brassy chord stab"""
    t = tt(dur)
    x = sum(saw(f, dur, 0.004) for f in freqs) / len(freqs)
    cut = 600 + 5000 * np.exp(-t * 6)
    y = np.zeros_like(x)
    for i in range(0, len(x), 1024):                  # the filter closes as it rings out
        seg = x[max(0, i - 2048):i + 1024]
        yy = lp(seg, cut[i])
        y[i:i + 1024] = yy[-len(y[i:i + 1024]):]
    return y * np.exp(-t * 3.2)


def pad(freqs, dur, cutoff=1400, attack=0.25):
    x = sum(saw(f, dur, 0.006) for f in freqs) / len(freqs)
    return lp(x, cutoff) * env(dur, a=attack, d=0.01, s=1.0, r=min(0.3, dur / 3))


def bells(freqs, dur=1.8):
    t = tt(dur)
    out = np.zeros_like(t)
    for j, f in enumerate(freqs):
        out += (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)) \
            * np.exp(-t * (2.0 + j * 0.4)) * ((t > j * 0.06))
    return out / len(freqs)


def crowd(dur, gain=1.0):
    """a stadium crowd: banded noise that swells and murmurs, different in each ear"""
    t = tt(dur)
    mod = 0.75 + 0.25 * np.sin(2 * np.pi * 0.37 * t) * np.sin(2 * np.pi * 0.11 * t + 1)
    a = bp(rng.standard_normal(len(t)), 250, 2600) * mod
    b = bp(rng.standard_normal(len(t)), 250, 2600) * mod
    return a * gain, b * gain


def pyro():
    """a crackling burst: thump, then a fizz of crackles"""
    t = tt(1.6)
    thump = kick(0.9, 0.5, 90, 35)
    crack = (rng.random(len(t)) < 0.012 * np.exp(-t * 2)) * rng.standard_normal(len(t)) * 3.0
    fizz = hp(rng.standard_normal(len(t)), 3000) * np.exp(-t * 3) * 0.25
    out = hp(crack, 1500) * 0.6 + fizz
    out[:len(thump)] += thump
    return out


def note(name):
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    n, o = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((names[n] + (o - 4) * 12) / 12.0)


def chord(*names):
    return [note(x) for x in names]


BEAT = 0.5
# ---------------------------------------------------------------- tap, flap opens, light, white
# the light zipping across the seam (0 - 0.3 s; a swiped pack starts the song after it)
zt = tt(0.3)
zf = 900 + 5000 * (zt / 0.3) ** 1.5
zip_ = bp(rng.standard_normal(len(zt)), 1200, 8000) * (0.4 + 0.6 * (np.sin(2 * np.pi * np.cumsum(zf / 40) / SR) > 0))
zip_ += np.sin(2 * np.pi * np.cumsum(zf * 0.25) / SR) * 0.25
put(zip_ * (0.3 + 0.7 * zt / 0.3), at(0.0), 0.42, -0.2)
put(riser(0.85, 300, 9000, (180, 1100)), at(0), 0.55)
# the RIP at w = 0.30: a ragged burst of torn foil, a thump, a crash of light
rt = tt(0.22)
rip = bp(rng.standard_normal(len(rt)), 1500, 9000) * (0.6 + 0.4 * (rng.random(len(rt)) < 0.08)) * np.exp(-rt * 14)
put(rip, at(0.30), 0.75, 0.15)
put(kick(0.9, 0.5, 120, 45), at(0.30), 0.6)
put(crash(1.0), at(0.30), 0.3)
put(boom(), at(0.85), 0.95)
put(crash(2.2), at(0.85), 0.45)
put(bells(chord("A5", "C#6", "E6", "A6")), at(0.9), 0.35, -0.2)
put(bells(chord("E6", "A6", "C#7")), at(1.15), 0.22, 0.3)
# ---------------------------------------------------------------- the groove: w 1.0 .. 6.0
SECTIONS = [(1.0, 2.0, chord("A3", "C4", "E4"), note("A1")),
            (2.0, 3.5, chord("F3", "A3", "C4"), note("F1")),
            (3.5, 5.0, chord("C4", "E4", "G4"), note("C2")),
            (5.0, 6.0, chord("G3", "B3", "D4"), note("G1"))]
for w0, w1, ch, root in SECTIONS:
    put(pad(ch, w1 - w0 + 0.05, 1600, 0.05), at(w0), 0.16)
    b = w0
    while b < w1 - 1e-6:                                  # 8th-note bass, pumping
        k = int(round((b - 1.0) / 0.25))
        f = root * (2 if k % 4 == 3 else 1)
        bs = lp(saw(f * 2, 0.24, 0.003), 500) * env(0.24, 0.004, 0.18, 0.2, 0.04)
        put(bs, at(b), 0.42)
        b += 0.25
w = 1.0
while w < 6.0 - 1e-6:
    put(kick(0.95), at(w), 0.8)
    put(hat(), at(w + 0.25), 0.22, 0.35)
    if int(round((w - 1.0) / BEAT)) % 2 == 1:
        put(clap(), at(w), 0.45, -0.1)
    w += BEAT
# whooshes into each reveal
put(whoosh(0.3, True), at(1.72), 0.55, -0.4)
put(whoosh(0.32, False), at(3.18), 0.7, 0.4)
put(whoosh(0.3, True), at(4.72), 0.55, -0.3)
# ---------------------------------------------------------------- the reveals
for w0, ch in ((2.0, chord("F3", "A3", "C4", "F4")), (3.5, chord("C4", "E4", "G4", "C5")),
               (5.0, chord("G3", "B3", "D4", "G4"))):
    put(boom(1.2), at(w0), 0.55)
    put(crash(1.4), at(w0), 0.35)
    put(stab(ch), at(w0), 0.55)
put(bells(chord("C6", "E6", "G6")), at(3.52), 0.25, 0.25)
for _ in range(46):                                    # confetti pops with the crest
    d = rng.uniform(0, 0.8)
    f = rng.uniform(2200, 6000)
    p = np.sin(2 * np.pi * f * tt(0.03)) * np.exp(-tt(0.03) * 160)
    put(p, at(5.0 + d), rng.uniform(0.06, 0.16), rng.uniform(-0.9, 0.9))
# ---------------------------------------------------------------- 6.0: dark. the stadium
put(riser(0.95, 120, 2500, (60, 180)) * 0.6, at(6.0), 0.35)
ca, cb = crowd(END - (TAP + 6.25))
fade = np.minimum(1, tt(len(ca) / SR) / 0.4)
L[at(6.25):at(6.25) + len(ca)] += ca[:N - at(6.25)] * fade[:N - at(6.25)] * 0.16
R[at(6.25):at(6.25) + len(cb)] += cb[:N - at(6.25)] * fade[:N - at(6.25)] * 0.16
put(riser(0.55, 400, 9000, (220, 1760)), at(6.45), 0.6)       # the pillar rising
# ---------------------------------------------------------------- 7.0: he walks out
put(boom(2.6), at(7.0), 1.0)
put(crash(2.6), at(7.0), 0.5)
put(stab(chord("A3", "C#4", "E4", "A4"), 1.0), at(7.0), 0.6)
put(bells(chord("A5", "C#6", "E6", "A6", "C#7")), at(7.02), 0.3)
for side in (-0.8, 0.8):
    put(pyro(), at(7.0), 0.55, side)
    put(pyro(), at(10.0), 0.5, side)
cheer_a, cheer_b = crowd(3.0, 1.0)
swell = np.minimum(1, tt(3.0) / 0.15) * np.exp(-tt(3.0) * 0.9)
L[at(7.0):at(7.0) + len(cheer_a)] += (cheer_a * swell)[:N - at(7.0)] * 0.55
R[at(7.0):at(7.0) + len(cheer_b)] += (cheer_b * swell)[:N - at(7.0)] * 0.55
# the anthem after: A - D - E - A, two beats each, over the kick
OUTRO = [(7.0, chord("A3", "C#4", "E4"), note("A1")), (8.0, chord("D4", "F#4", "A4"), note("D2")),
         (9.0, chord("E4", "G#4", "B4"), note("E2")), (10.0, chord("A3", "C#4", "E4"), note("A1")),
         (11.0, chord("D4", "F#4", "A4"), note("D2"))]
for w0, ch, root in OUTRO:
    put(pad(ch, 1.05, 2200, 0.02), at(w0), 0.2)
    for j in range(4):
        bs = lp(saw(root * 2, 0.24, 0.003), 600) * env(0.24, 0.004, 0.18, 0.2, 0.04)
        put(bs, at(w0 + j * 0.25), 0.4)
w = 7.0
while TAP + w < END:
    put(kick(0.9), at(w), 0.7)
    put(hat(), at(w + 0.25), 0.2, 0.35)
    if int(round((w - 7.0) / BEAT)) % 2 == 1:
        put(clap(), at(w), 0.4, -0.1)
    w += BEAT
# ---------------------------------------------------------------- master
st = np.stack([L, R], 1)
st = np.tanh(st * 1.4) / np.tanh(1.4)                      # gentle glue
st /= np.max(np.abs(st)) / 0.92
fo = int(0.6 * SR)
st[-fo:] *= np.linspace(1, 0, fo)[:, None]
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
wav = os.path.join(HERE, "openingpack.wav")
wavfile.write(wav,
              SR, (st * 32767).astype(np.int16))
print("score written", st.shape[0] / SR, "s")
try:                                                    # mp3 for the game (needs ffmpeg); else keep the wav
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-codec:a", "libmp3lame", "-b:a", "192k",
                    os.path.join(HERE, "openingpack.mp3")], check=True)
    os.remove(wav)
    print("openingpack.mp3 written")
except Exception as exc:
    print("no ffmpeg (%s): openingpack.wav written instead - the game plays that too" % exc)
