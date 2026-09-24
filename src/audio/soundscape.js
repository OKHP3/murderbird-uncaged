// Gesture-started Web Audio sketch. No final song or recorded effects are bundled.
export function createSoundscape() {
  let context, master, bed, timer, enabled = false, step = 0;
  function tone(frequency, duration, type = 'sine', volume = .08, destination = master, start = context.currentTime) {
    const oscillator = context.createOscillator();
    const envelope = context.createGain();
    oscillator.type = type;
    oscillator.frequency.setValueAtTime(frequency, start);
    envelope.gain.setValueAtTime(0, start);
    envelope.gain.linearRampToValueAtTime(volume, start + .012);
    envelope.gain.exponentialRampToValueAtTime(.001, start + duration);
    oscillator.connect(envelope).connect(destination);
    oscillator.start(start);
    oscillator.stop(start + duration + .02);
  }
  function startBed() {
    // A quiet workshop pulse, not a substitute for the planned theme song.
    bed = context.createGain();
    bed.gain.value = .55;
    bed.connect(master);
    const notes = [82.41, 98, 110, 98, 82.41, 73.42, 65.41, 73.42];
    function beat() {
      if (!enabled) return;
      const note = notes[step % notes.length];
      tone(note, .74, 'triangle', .065, bed);
      if (step % 2 === 0) tone(note * 2, .24, 'sine', .016, bed);
      step++;
    }
    beat();
    timer = window.setInterval(beat, 780);
  }
  return {
    async toggle() {
      if (!context) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return false;
        context = new AudioContext();
        master = context.createGain();
        master.gain.value = .6;
        master.connect(context.destination);
      }
      if (enabled) {
        enabled = false;
        window.clearInterval(timer);
        master.gain.setTargetAtTime(0, context.currentTime, .12);
      } else {
        await context.resume();
        enabled = true;
        master.gain.setTargetAtTime(.6, context.currentTime, .15);
        startBed();
        this.effect('chirp');
      }
      return enabled;
    },
    effect(name) {
      if (!enabled || !context) return;
      const now = context.currentTime;
      if (bed) {
        bed.gain.setTargetAtTime(.16, now, .015);
        bed.gain.setTargetAtTime(.55, now + .35, .22);
      }
      if (name === 'metal' || name === 'open') {
        tone(320, .55, 'triangle', .095);
        tone(475, .42, 'sine', .04, master, now + .04);
        tone(960, .22, 'sine', .02, master, now + .07);
      } else if (name === 'pulse') {
        tone(110, .55, 'sawtooth', .045);
        tone(220, .42, 'sine', .09, master, now + .1);
      } else if (name === 'chirp') {
        tone(620, .17, 'triangle', .06);
        tone(900, .24, 'triangle', .05, master, now + .11);
        tone(460, .24, 'sine', .04, master, now + .29);
      } else {
        tone(510, .12, 'triangle', .055);
        tone(215, .16, 'sine', .045, master, now + .06);
      }
    },
  };
}