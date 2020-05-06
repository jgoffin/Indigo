// Initialize the model.
const music_vae = new mm.MusicVAE('https://storage.googleapis.com/magentadata/js/checkpoints/music_vae/mel_4bar_small_q2');
music_vae.initialize().then(() => {
  document.getElementById('loading').style.display = 'none';
  [...document.getElementsByTagName('button')].forEach(b => b.style = '');
});

// Create a player to play the sampled sequence.
const vaePlayer = new mm.Player();
const vae_temperature = 1.5

let upload1_quant;
let upload2_quant;
let note_seq1;
let note_seq2;

function interpolate(midi1, midi2) {
  
  //Quantize note sequences and pass note sequences to interpolate function of MusicVAE
  mm.urlToNoteSequence(midi1)
                  .then(ns_val1 => note_seq1 = ns_val1)
                  .then(vars => upload1_quant = mm.sequences.quantizeNoteSequence(note_seq1, 4))
                  .then(vars => mm.urlToNoteSequence(midi2))
                  .then(ns_val2 => note_seq2 = ns_val2)
                  .then(vars => upload2_quant = mm.sequences.quantizeNoteSequence(note_seq2, 4))
                  .then(vars => music_vae
                      .interpolate([upload1_quant, upload2_quant], 4)
                      .then((sample) => {
                        const concatenated = mm.sequences.concatenate(sample);
                        vaePlayer.start(concatenated);
                      }));
}

function stop(){
  if (vaePlayer.isPlaying()) {
    vaePlayer.stop();
  }
  else{
    vaePlayer.start();
  }
  return;
}